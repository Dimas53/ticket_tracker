from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base # Импортируем из database

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    tickets = relationship("TicketDB", back_populates="owner")

class TicketDB(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="open")
    priority = Column(String, default="normal")
    assignee = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserDB", back_populates="tickets")