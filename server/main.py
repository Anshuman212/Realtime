from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from datetime import datetime,timedelta
from typing import List,Union
from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import models
from .schema import schema
from .crud import crud
from .database import SessionLocal, Database_Connection_Creater
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
SECRET_KEY= dotenv_values("SECRET_KEY")
ALGORITHM = dotenv_values("ALGORITHM")
ACCESS_TOKEN_EXPIRY_MINUTES=30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
models.Base.metadata.create_all(bind=Database_Connection_Creater)
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class multiple_connection_manager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


connect_control = multiple_connection_manager()

def verify_pwd(password, hash_password):
    return pwd_context.verify(password,hash_password)

def get_user(db,username:str):
    if username in db:
        user_dict = db[username]
        return  CreateUser(**user_dict)
    

def authentiacting_user(db, username:str, password:str):
    user = get_user(db,username)
    if not user:
        raise HTTPException(status_code=401,detail="not authorized user")
    if not verify_pwd(password,user.hash_password):
        raise HTTPException(status_code=401,detail="invalid password")
    return user

def create_access_token(data:dict, expire_delta:Union[timedelta,None]=None):
    t_encode=data.copy()
    if expire_delta:
        expire= datetime.utcnow()+expire_delta
    else:
        expire_delta =datetime.utcnow+timedelta(minutes=15)
    t_encode.update({"expire":expire})
    encode_jwt= jwt.encode(t_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt
async def get_user_data(token:Annotated[str,Depends(oauth2_scheme)]):
    credential_exceptions= HTTPException(
        status_code=401,
        detail="credentials do not match"
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms={ALGORITHM})
        username:str = payload.get("user")
        if username is None:
            raise credential_exceptions
        token_data=TokenData(username=username)
    except JWTError:
        raise credential_exceptions
    user =get_user(db,username=token_data.username)
    if user is None:
        raise credential_exceptions
    return user


@app.post("/token",response_model=Token)
async def login_tokens(form_data:Annotated[OAuth2PasswordRequestForm,Depends()]):
    user=authentiacting_user(db,form_data.username,form_data.password):
    if user is None:
        raise HTTPException(status_code=401,detail= "unauthorized user")
    access_token_expire= timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    acess_token = create_access_token(data={"user":user.username},expire_delta=access_token_expire)
    return {"access_token":access_token,"token_type":bearer}



@app.post("/api/testing/user/", response_model=schema.User)
def create_user(user: schema.CreateUser, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name=user.user_name)
    if db_user:
        raise HTTPException(status_code=400, detail="user already exists")
    return crud.create_user(db=db, user=user)


@app.post("/api/testing/user/{user_id}/contact/", response_model=schema.Contact)
def create_contact(
    user_id: int, contact: schema.CreateContact, db: Session = Depends(get_db)
):
    db_contact = crud.get_contacts_of_user(db=db, contact=contact, user_id=user_id)
    if db_contact:
        raise HTTPException(status_code=400, detail="contact already exists")
    return crud.create_contact(db=db, contact=contact, user_id=user_id)


@app.get("/api/testing/user/{user_id}/contact/", response_model=schema.Contact)
def get_user_contact(
    user_id: int, contact: schema.Contact, db: Session = Depends(get_db)
):
    db_contact = crud.get_contacts_of_user(db=db, contact=contact, user_id=user_id)
    if db_contact:
        return db_contact
    raise HTTPException(status_code=400, detail="user not found")


@app.post(
    "/api/testing/user/{user_id}/contact/{contact_id}/message",
    response_model=schema.Message,
)
def create_message(
    user_id: int,
    contact_id: int,
    contact=schema.Contact,
    message=schema.CreateMessage,
    db: Session = Depends(get_db),
):
    db_contact = crud.get_contacts_of_user(db=db, contact=contact, user_id=user_id)
    if db_contact:
        return crud.create_message(db=db, message=message, contact_id=contact_id)
    raise HTTPException(401, detail="unauthorized contact cannot message")


@app.get(
    "/api/testing/user/{user_id}/contact/{contact_id}/message",
    response_model=schema.Message,
)
def get_user_message(
    user_id: int,
    contact_id: int,
    contact: schema.Contact,
    message: schema.Message,
    db: Session = Depends(get_db),
):
    db_contact = crud.get_contacts_of_user(db=db, contact=contact, user_id=user_id)
    if db_contact:
        contact_message = crud.get_message_of_contact(db=db, contact_id=contact_id)
        if contact_message:
            return contact_message
        raise HTTPException(
            status_code=400, detail="no message found with this contact"
        )
    raise HTTPException(status_code=400, detail="no contact found")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await connect_control.connect(websocket)
    current_datetime = datetime.now()
    current_time = current_datetime.strftime("%H : %M")
    try:
        while True:
            incomming_message = await websocket.receive_text()
            message = {
                "time": current_time,
                "clientId": client_id,
                "message": incomming_message,
            }
            await connect_control.broadcast(json.dumps(message))
    except WebSocketDisconnect:
        connect_control.disconnect(websocket)
        message = {
            "time": current_time,
            "clientId": client_id,
            "message": "now offline",
        }
        await connect_control.broadcast(json.dumps(message))
