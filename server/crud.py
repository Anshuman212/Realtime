from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import schema
from . import models


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def create_user(db: Session, user: schema.CreateUser):
    hash_password = pwd_context.hash(user.password) 
    db_user = models.User(user_name=user.user_name, hashed_password=hash_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.user_name == user_name).first()


def create_contact(db: Session, contact: schema.CreateContact, user_id: int):
    db_contact = models.Contact(**contact.dict(), contact_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts_of_user(db: Session, user_id: int):
    return db.query(models.Contact).filter(models.Contact.contact_id == user_id).all()


def create_message(db: Session, message: schema.CreateMessage, contact_id: int):
    db_message = models.Message(**message.dict(), message_id=contact_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_message_of_contact(db: Session, contact_id: int):
    return (
        db.query(models.Message).filter(models.Message.message_id == contact_id).all()
    )
