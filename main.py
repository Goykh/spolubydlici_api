from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

users = [{"jmeno": "Petr",
          "dluzi": {
              "Pavel": 15.0,
              "Jiri": 1.0,
              "Dan": 4.5
          },
          "dluzi_mu": {
              "Jakub": 2.5,
              "Pavel": 6.75,
          },
          "suma": ""},
         {"jmeno": "Pavel",
          "dluzi": {
              "Petr": 6.75,
              "Dan": 1.0
          },
          "dluzi_mu": {
              'Petr': 15.0
          },
          "suma": ""}
         ]


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/users')
async def get_users(db: Session = Depends(get_db)):
    return {"uzivatele": crud.get_all_users_with_data(db)}


@app.post('/add')
async def add_new_user(new_user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name=new_user.user)
    if db_user:
        raise HTTPException(status_code=400, detail="Uživatel už existuje.")
    return crud.create_user(db, new_user)


@app.post('/transaction')
async def make_transaction(transaction: schemas.TransactionBase, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, transaction=transaction)
