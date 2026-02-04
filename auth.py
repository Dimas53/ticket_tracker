import datetime
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Импортируем наши настройки из соседних файлов
from database import get_db
from models import UserDB

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 1. Конфигурация безопасности
SECRET_KEY = "SCHOOL_PROJECT_SECRET_KEY" # Ключ для подписи токенов
ALGORITHM = "HS256" # Алгоритм шифрования
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Время жизни токена (1 час)

# Инструмент для работы с паролями (хеширование bcrypt)
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

# Инструмент, который будет искать токен в заголовке Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- ЛОГИКА ПАРОЛЕЙ ---

def verify_password(plain_password: str, hashed_password: str):
    """Сверяет введенный пароль с хешем из базы"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """Создает безопасный хеш из обычного пароля"""
    return pwd_context.hash(password)

# --- ЛОГИКА ТОКЕНОВ (JWT) ---

def create_access_token(data: dict):
    """Генерирует JWT токен (цифровой пропуск)"""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- ЗАЩИТНИК (Dependency) ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Эта функция — 'охранник'. Она проверяет токен,
    документирует кто зашел и возвращает объект пользователя.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Расшифровываем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Ищем пользователя в базе по имени из токена
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user