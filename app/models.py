# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    encrypted_user_key = Column(String, nullable=False)  # Fernet ключ (зашифрованный или в открытом виде)

    password_records = relationship("PasswordRecord", back_populates="owner")


class PasswordRecord(Base):
    __tablename__ = "password_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    login = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    url = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="password_records")