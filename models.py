from sqlalchemy import Column, Integer, String, Float

from database import Base


class User(Base):
    """
    Main table, store unique names of users and an id.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class Transaction(Base):
    """
    Stores all transactions.
    Each row has the id of the creditor
    and the debtor.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    debtor = Column(Integer)
    creditor = Column(Integer)
    amount = Column(Float)
