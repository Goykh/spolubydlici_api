from fastapi import FastAPI, HTTPException, Depends, Path
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/users')
async def get_users(db: Session = Depends(get_db)):
    """
    Calls for all users.
    """
    return {"uzivatele": crud.get_all_users_with_data(db)}


@app.get('/users/{user_name}')
async def get_user_by_name(db: Session = Depends(get_db), user_name: str = Path(title="what")):
    """
    Calls for user by name. If name is not found in db,
    it returns a 400 exception.
    """
    db_user = crud.get_user_by_name(db, user_name=user_name)
    if db_user:
        return {"uzivatel": crud.get_all_users_with_data(db, user_name=user_name)}
    raise HTTPException(status_code=400, detail="Uživatel neexistuje.")


@app.post('/add')
async def add_new_user(new_user: schemas.UserBase, db: Session = Depends(get_db)):
    """
    First looks if user exist, if it does, raises 400 exception.
    Else adds user to the db and returns its object
    """
    db_user = crud.get_user_by_name(db, user_name=new_user.user)
    if db_user:
        raise HTTPException(status_code=400, detail="Uživatel už existuje.")
    return crud.create_user(db, new_user)


@app.post('/transaction')
async def make_transaction(transaction: schemas.TransactionBase, db: Session = Depends(get_db)):
    """
    First checks if both names are provided correctly.
    If yes, calls for the function to create the transaction.
    It returns the objects of both names.
    """
    db_debtor = crud.get_user_by_name(db, user_name=transaction.dluznik)
    db_creditor = crud.get_user_by_name(db, user_name=transaction.veritel)
    if not db_debtor or not db_creditor:
        raise HTTPException(status_code=400, detail="Zadaný uživatel neexistuje.")
    return crud.create_transaction(db=db, transaction=transaction)
