from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base_Model_Mapper


# creating classes that inherit from it
class User(Base_Model_Mapper):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    password = Column(String)
    is_online = Column(Boolean, default=False)
    contacts = relationship("Contact", back_populates="sender")


class Contact(Base_Model_Mapper):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    contact_name = Column(String)
    is_online = Column(Boolean, default=False)
    contact_id = Column(Integer, ForeignKey("users.id"))
    sender = relationship("User", back_populates="contacts")
    messages = relationship("Message", back_populates="receiver")


class Message(Base_Model_Mapper):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("contacts.id"))
    message_description = Column(String)
    receiver = relationship("Contact", back_populates="messages")
