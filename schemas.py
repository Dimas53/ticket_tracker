from pydantic import BaseModel
from typing import Literal, Optional

class TicketBase(BaseModel):
    title: str
    description: str
    status: Literal["open", "in_progress", "done"]
    priority: Literal["low", "normal", "high"]
    assignee: str

class TicketCreate(TicketBase):
    owner_id: Optional[int] = None

class Ticket(TicketBase):
    id: int
    owner_id: Optional[int] = None
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["user", "admin"] = "user"