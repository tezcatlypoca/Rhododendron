from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    roles = Column(String)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)

    # Relations
    projets = relationship("Projet", back_populates="compte")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)
    role = Column(String, nullable=False, default="assistant")
    is_active = Column(Boolean, default=True)
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    last_used = Column(DateTime, default=func.now())
    projet_id = Column(String, ForeignKey("projets.id"), nullable=True)

    # Relations
    conversations = relationship("Conversation", back_populates="agent")
    projet = relationship("Projet", back_populates="agents")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    conversation_metadata = Column(JSON, default={})

    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    message_metadata = Column(JSON, default={})

    conversation = relationship("Conversation", back_populates="messages")
    agent = relationship("Agent")

class Projet(Base):
    __tablename__ = "projets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = Column(String, nullable=False)
    description = Column(String)
    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())
    compte_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Relations
    compte = relationship("User", back_populates="projets")
    agents = relationship("Agent", back_populates="projet", cascade="all, delete-orphan") 