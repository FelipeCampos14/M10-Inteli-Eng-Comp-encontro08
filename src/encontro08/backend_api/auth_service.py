from fastapi import Form, Depends, Request, HTTPException, Response, FastAPI, Body
from sqlalchemy.orm import Session
from database.models import User, ToDoList
from database.database import SessionLocal
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import uvicorn
from database.database import db, engine
from database.models import User, ToDoList
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from pydantic import BaseModel

class UserInfo(BaseModel):
    username: str
    password: str

templates = Jinja2Templates(directory="templates")

app = FastAPI()

SECRET_KEY = "pokemon"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_async_db():
    db = SessionLocal()
    async with db as session:
        yield session



def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.name == username).first()
    userpass = db.query(User).filter(User.password == password).first()
    if not user:
        return False
    if not userpass:
        return False
    return user

# Update /login endpoint to use OAuth2PasswordRequestForm
@app.post("/login")
async def login(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"status": "Login Success"}

# Add dependencies to CRUD user endpoints to get current user
@app.get("/users")
async def get_users(db: Session = Depends(get_async_db)):
    async with db as session:

        users = select(User)
        result = await session.execute(users)
        users = result.scalars().all()
    return users

@app.get("/users/{id}")
async def get_user(id: int, db: Session = Depends(get_async_db)):
    async with db as session:
        stmt = select(User).filter(User.id == id)
        try:
            result = await session.execute(stmt)
            user = result.scalars().one()
            return user
        except NoResultFound:
            raise HTTPException(status_code=404, detail="User not found")

@app.post("/users")
async def create_user(user_data: UserInfo, db: Session = Depends(get_async_db)):
    async with db as session:
        db_user = User(name=user_data.username, password=user_data.password)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
    return {"status": f"User [{user_data.username}] created with id {db_user.id}"}
        
@app.put("/users/{id}")
async def update_user(id: int, user_data: UserInfo, db: Session = Depends(get_async_db)):
    async with db as session:
        db_user = await session.get(User, id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        db_user.name = user_data.username
        db_user.password = user_data.password
        await session.commit()
        return {"status": f"User [{user_data.username}] updated"}

@app.delete("/users/{id}")
async def delete_user(id: int, db: Session = Depends(get_async_db)):
    async with db as session:
        db_user = await session.get(User, id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        await session.delete(db_user)
        await session.commit()
        return {"status": f"User with id [{id}] deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
