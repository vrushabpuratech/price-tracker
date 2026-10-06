from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserResponse

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    new_user = User(email=user.email)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
