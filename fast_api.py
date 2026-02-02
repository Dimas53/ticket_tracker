from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

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

app.mount("/ui", StaticFiles(directory=".", html=True), name="ui")



# SQLite database configuration
DATABASE_URL = "sqlite:///./tickets.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database table model
class TicketDB(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    assignee = Column(String, nullable=False)


# Create tables in the database
Base.metadata.create_all(bind=engine)


# Pydantic model for the API
class Ticket(BaseModel):
    id: int
    title: str
    description: str
    status: Literal["open", "in_progress", "done"]
    priority: Literal["low", "normal", "high"]
    assignee: str

    class Config:
        from_attributes = True


# Function to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1. Create a ticket
@app.post("/tickets", status_code=200, tags=["1 Create Ticket"])
def create_ticket(ticket: Ticket):
    db = SessionLocal()

    # Existence check
    existing = db.query(TicketDB).filter(TicketDB.id == ticket.id).first()
    if existing:
        db.close()
        raise HTTPException(status_code=409, detail="Ticket already exists")

    # Creating a new ticket
    db_ticket = TicketDB(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        assignee=ticket.assignee
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    db.close()

    return ticket


# 2. Get the list of all tickets
@app.get("/tickets", tags=["2 List All Tickets"]
)
def get_all_tickets():
    db = SessionLocal()
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

# To run via python fast_api.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)