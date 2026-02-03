from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from typing import List

# Импортируем всё необходимое из наших новых модулей
from database import engine, SessionLocal, get_db, Base
import models
from schemas import Ticket, TicketCreate, UserCreate

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


# 5. Удалить тикет
@app.delete("/tickets/{ticket_id}", tags=["5 Delete Single Ticket"])
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.TicketDB).filter(models.TicketDB.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted successfully"}


# ⚠️ Danger Zone: Удалить всё
@app.delete("/tickets", tags=["⚠️ Danger Zone"])
def delete_all_tickets(db: Session = Depends(get_db)):
    db.query(models.TicketDB).delete()
    db.commit()
    return {"message": "All tickets deleted"}


# Подключаем фронтенд (папка frontend должна быть в корне проекта)
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)