from database import Base
from sqlalchemy import Column
from sqlalchemy.types import Integer, Boolean, Float, String, TIMESTAMP, DateTime
from datetime import datetime
from pydantic import BaseModel


class User(Base):
    __tablename__ = "User"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True)
    phone_no = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    
    
class APIKey(Base):
    __tablename__ = "apikey"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String)
    user_id = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
class ChatRequest(BaseModel):
    message : str
    model : str
    
    
class UsageLog(Base):
    __tablename__ = "UsageLog"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    api_key_id = Column(Integer)
    request = Column(String)
    response = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)