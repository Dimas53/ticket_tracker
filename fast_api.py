from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey # Добавь ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship # Добавь relationship

from fastapi.staticfiles import StaticFiles

# FastAPI application
# app = FastAPI(title="Ticket Tracker API", version="1.0")
app = FastAPI(
    title="Ticket Tracker API",
    version="1.0",
    openapi_tags=[
        {"name": "1 Create Ticket"},
        {"name": "2 List All Tickets"},
        {"name": "3 Get Single Ticket"},
        {"name": "4 Update Ticket"},
        {"name": "5 Delete Single Ticket"},
        {"name": "⚠️ Danger Zone"},  # this block will be the very last one
    ],
)

# app.mount("/ui", StaticFiles(directory=".", html=True), name="ui")



# SQLite database configuration
DATABASE_URL = "sqlite:///./tickets.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



# Database user model
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False) # Unique username to prevent duplicates
    password_hash = Column(String, nullable=False)        # Store hashed passwords only
    role = Column(String, default="user")                # Access levels: 'user' or 'admin'

    # Relationship: links a user to their multiple tickets
    # 'owner' refers to the attribute we will add to TicketDB in the next step
    tickets = relationship("TicketDB", back_populates="owner")


# Database table model
class TicketDB(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    assignee = Column(String, nullable=False)

    # 1. Add a foreign key to link a ticket to a specific user
    owner_id = Column(Integer, ForeignKey("users.id"))

    # 2. Define the relationship to access the User object
    owner = relationship("UserDB", back_populates="tickets")


# Create tables in the database
Base.metadata.create_all(bind=engine)


# Pydantic model for the API
# class Ticket(BaseModel):
#     # id: int
#     id: Optional[int] = None  # Теперь можно не передавать при создании
#     title: str
#     description: str
#     status: Literal["open", "in_progress", "done"]
#     priority: Literal["low", "normal", "high"]
#     assignee: str
#
#     class Config:
#         from_attributes = True

# Pydantic model for the API
# --- USER SCHEMAS ---

class UserBase(BaseModel):
    username: str
    role: str = "user"

class UserCreate(UserBase):
    password: str  # We'll use this for registration in the next stage

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# --- TICKET SCHEMAS ---

class TicketBase(BaseModel):
    title: str
    description: str
    status: Literal["open", "in_progress", "done"]
    priority: Literal["low", "normal", "high"]
    assignee: str

# Use this for POST (it doesn't have an 'id' field)
class TicketCreate(TicketBase):
    owner_id: Optional[int] = None

# Use this for GET (it has the 'id' field from the database)
class Ticket(TicketBase):
    id: int
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True


# Function to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#
# # 1. Create a ticket
# @app.post("/tickets", status_code=200, tags=["1 Create Ticket"])
# def create_ticket(ticket: Ticket):
#     db = SessionLocal()
#
#     # Existence check
#     # existing = db.query(TicketDB).filter(TicketDB.id == ticket.id).first()
#     # if existing:
#     #     db.close()
#     #     raise HTTPException(status_code=409, detail="Ticket already exists")
#
#     # Creating a new ticket
#     db_ticket = TicketDB(
#         # id=ticket.id,
#         title=ticket.title,
#         description=ticket.description,
#         status=ticket.status,
#         priority=ticket.priority,
#         assignee=ticket.assignee
#     )
#     db.add(db_ticket)
#     db.commit()
#     db.refresh(db_ticket)
#     db.close()
#
#     return ticket
#
#
# # 2. Get the list of all tickets
# @app.get("/tickets", tags=["2 List All Tickets"]
# )
# def get_all_tickets():
#     db = SessionLocal()
#     tickets = db.query(TicketDB).all()
#     db.close()
#     return tickets
#

# 1. Create a ticket
@app.post("/tickets", response_model=Ticket, status_code=200, tags=["1 Create Ticket"])
def create_ticket(ticket: TicketCreate):  # Using TicketCreate (no ID required)
    db = SessionLocal()

    # Create a new ticket object from the incoming data
    # **ticket.model_dump() is a shortcut to unpack all fields at once
    db_ticket = TicketDB(**ticket.model_dump())

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    db.close()

    return db_ticket  # Returns the created ticket with its new ID from DB


# 2. Get the list of all tickets
@app.get("/tickets", response_model=list[Ticket], tags=["2 List All Tickets"])
def get_all_tickets():
    db = SessionLocal()
    # Fetch all tickets from the database
    tickets = db.query(TicketDB).all()
    db.close()
    return tickets

# 3. Get a single ticket by ID
@app.get("/tickets/{ticket_id}", tags=["3 Get Single Ticket"])
def get_ticket(ticket_id: int):
    db = SessionLocal()
    ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
    db.close()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


# 4. Update a ticket
@app.put("/tickets/{ticket_id}", tags=["4 Update Ticket"])
def update_ticket(ticket_id: int, ticket: Ticket):
    db = SessionLocal()

    db_ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
    if not db_ticket:
        db.close()
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.id != ticket_id:
        db.close()
        raise HTTPException(status_code=422, detail="ID in URL and body must match")

    # Updating fields
    db_ticket.title = ticket.title
    db_ticket.description = ticket.description
    db_ticket.status = ticket.status
    db_ticket.priority = ticket.priority
    db_ticket.assignee = ticket.assignee

    db.commit()
    db.refresh(db_ticket)
    db.close()

    return ticket


# 5. Delete a ticket
@app.delete("/tickets/{ticket_id}", tags=["5 Delete Single Ticket"])
def delete_ticket(ticket_id: int):
    db = SessionLocal()

    ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
    if not ticket:
        db.close()
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    db.close()

    return {"message": "Ticket deleted successfully"}


# Delete all tickets (for development)
@app.delete("/tickets", tags=["⚠️ Danger Zone"]
)
def delete_all_tickets():
    db = SessionLocal()
    db.query(TicketDB).delete()
    db.commit()
    db.close()
    return {"message": "All tickets deleted"}



# Монтируем текущую папку, чтобы файлы styles.css и app.js были доступны
app.mount("/ui", StaticFiles(directory=".", html=True), name="ui")

# To run via python fast_api.py

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)




