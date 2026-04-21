from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String)
    interaction_type = Column(String)
    date = Column(String)
    time = Column(String)
    topics = Column(JSON)
    materials_shared = Column(JSON)
    sentiment = Column(String)
    attendees = Column(JSON)


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialty = Column(String)
    last_interaction = Column(String)


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    reminder_date = Column(String)
    note = Column(String)
    created_at = Column(String)