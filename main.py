from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

# 1. База и модели
from database import engine, SessionLocal, get_db, Base
import models

# 2. Схемы (импортируем и модуль целиком, и классы по отдельности)
import schemas
from schemas import Ticket, TicketCreate, UserCreate

# 3. Авторизация (импортируем модуль целиком для auth.hash и функции отдельно)
import auth
from auth import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)


# Автоматически создаем таблицы в базе данных при запуске
# (SQLAlchemy проверит models.py через импорт выше)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ticket Tracker API",
    version="1.0",
    openapi_tags=[
        {"name": "🔐 Auth"},
        {"name": "1 Create Ticket"},
        {"name": "2 List All Tickets"},
        {"name": "3 Get Single Ticket"},
        {"name": "4 Update Ticket"},
        {"name": "5 Delete Single Ticket"},
        {"name": "⚠️ Danger Zone"},
    ],
)


# --- 🔐 AUTH ENDPOINTS (Мы их добавим чуть позже в auth.py, пока оставим место) ---

# РЕГИСТРАЦИЯ: Создаем нового пользователя

@app.post("/register", tags=["🔐 Auth"])  # Вернул тег с замком, чтобы не терялся
def create_new_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, нет ли такого юзера
    db_user = db.query(models.UserDB).filter(models.UserDB.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pwd = get_password_hash(user_data.password)
    user_role = "admin" if user_data.username.startswith("admin_") else "user"

    new_user = models.UserDB(
        username=user_data.username,
        password_hash=hashed_pwd,  # Проверь, что в models.py именно password_hash!
        role=user_role
    )

    db.add(new_user)
    try:
        db.commit()  # Пробуем записать
        db.refresh(new_user)
    except Exception as e:
        db.rollback()  # ЕСЛИ ОШИБКА — СНИМАЕМ БЛОКИРОВКУ
        print(f"DATABASE ERROR: {e}")  # Увидишь ошибку в консоли
        raise HTTPException(status_code=500, detail="Database is busy or error occurred")

    return {"message": "User created", "username": new_user.username, "role": new_user.role}


# Проверка Юзеров
@app.get("/users", tags=["🔐 Auth"])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.UserDB).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]





# Удаление одного пользователя по ID (Только для Админа)
@app.delete("/users/{user_id}", tags=["🔐 Auth"])
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: models.UserDB = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Nur Admins können Benutzer löschen!")

    user = db.query(models.UserDB).filter(models.UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    # Не даем админу удалить самого себя (опционально, но полезно)
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Du kannst dich nicht selbst löschen!")

    db.delete(user)
    db.commit()
    return {"message": f"Benutzer {user.username} wurde gelöscht"}

# ЛОГИН: Выдаем токен (пропуск)
@app.post("/token", tags=["🔐 Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Ищем юзера
    user = db.query(models.UserDB).filter(models.UserDB.username == form_data.username).first()

    # 2. Проверяем пароль (сравниваем чистый пароль с хешем в БД)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Генерируем токен
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Очистка ВСЕХ пользователей (Danger Zone)
@app.delete("/users", tags=["⚠️ Danger Zone"])
def delete_all_users(
        db: Session = Depends(get_db),
        current_user: models.UserDB = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Nur Admins können die Benutzerliste leeren!")

    # Оставляем только текущего админа, чтобы не вылететь из системы
    db.query(models.UserDB).filter(models.UserDB.id != current_user.id).delete()
    db.commit()
    return {"message": "Alle Benutzer außer dem aktuellen Admin wurden gelöscht"}



# --- 🎫 TICKET ENDPOINTS ---

# 1. Создать тикет
@app.post("/tickets", response_model=Ticket, tags=["1 Create Ticket"])
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    db_ticket = models.TicketDB(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


# 2. Получить все тикеты
@app.get("/tickets", response_model=List[Ticket], tags=["2 List All Tickets"])
def get_all_tickets(db: Session = Depends(get_db)):
    return db.query(models.TicketDB).all()


# 3. Получить один тикет
@app.get("/tickets/{ticket_id}", response_model=Ticket, tags=["3 Get Single Ticket"])
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.TicketDB).filter(models.TicketDB.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


# 4. Обновить тикет
@app.put("/tickets/{ticket_id}", response_model=Ticket, tags=["4 Update Ticket"])
def update_ticket(ticket_id: int, ticket_data: Ticket, db: Session = Depends(get_db)):
    db_ticket = db.query(models.TicketDB).filter(models.TicketDB.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Обновляем поля из пришедших данных
    for key, value in ticket_data.model_dump(exclude={"id"}).items():
        setattr(db_ticket, key, value)

    db.commit()
    db.refresh(db_ticket)
    return db_ticket


# 5. Удаление ОДНОГО тикета (теперь только для тех, кто вошел в систему)
@app.delete("/tickets/{ticket_id}", tags=["5 Delete Single Ticket"])
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_user)  # <--- ВОТ ЗАМОК
):
    ticket = db.query(models.TicketDB).filter(models.TicketDB.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    # Обрати внимание: теперь мы можем даже написать, КТО удалил
    return {"message": f"Ticket deleted by user: {current_user.username}"}


# 6. Danger Zone (Удаление всего — только для залогиненных админов)
@app.delete("/tickets", tags=["⚠️ Danger Zone"])
def delete_all_tickets(
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_user)  # <--- ВОТ ЗАМОК
):
    # Дополнительная проверка на роль
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can wipe the database!")

    db.query(models.TicketDB).delete()
    db.commit()
    return {"message": "All tickets deleted by admin"}


# Подключаем фронтенд (папка frontend должна быть в корне проекта)
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)


#
# # 5. Удаление ОДНОГО тикета
# # ⚠️ АВТОРИЗАЦИЯ ВРЕМЕННО ОТКЛЮЧЕНА для тестирования фронта
# @app.delete("/tickets/{ticket_id}", tags=["5 Delete Single Ticket"])
# def delete_ticket(
#     ticket_id: int,
#     db: Session = Depends(get_db),
#     # current_user: models.UserDB = Depends(get_current_user)  # ← ЗАКОММЕНТИРОВАНО
# ):
#     ticket = db.query(models.TicketDB).filter(models.TicketDB.id == ticket_id).first()
#     if not ticket:
#         raise HTTPException(status_code=404, detail="Ticket not found")
#
#     db.delete(ticket)
#     db.commit()
#     return {"message": "Ticket deleted"}
#
#
# # 6. Danger Zone (Удаление всего)
# # ⚠️ АВТОРИЗАЦИЯ ВРЕМЕННО ОТКЛЮЧЕНА для тестирования фронта
# @app.delete("/tickets", tags=["⚠️ Danger Zone"])
# def delete_all_tickets(
#     db: Session = Depends(get_db),
#     # current_user: models.UserDB = Depends(get_current_user)  # ← ЗАКОММЕНТИРОВАНО
# ):
#     # Проверка на роль ОТКЛЮЧЕНА
#     # if current_user.role != "admin":
#     #     raise HTTPException(status_code=403, detail="Only admins can wipe the database!")
#
#     db.query(models.TicketDB).delete()
#     db.commit()
#     return {"message": "All tickets deleted"}
#
#
# # Подключаем фронтенд (папка frontend должна быть в корне проекта)
# app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)