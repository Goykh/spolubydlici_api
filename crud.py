import sqlite3

from sqlalchemy.orm import Session

import models
import schemas


def get_user_by_name(db: Session, user_name: str):
    """
    Looks for the name in the db.
    """
    return db.query(models.User).filter(models.User.name == user_name).first()


def get_all_users_with_data(db: Session, user_name: str | None = None):
    """
    Gets all the users with all their data,
    or only one user if user_name param has been provided.
    """
    users = []
    if user_name:
        creditors = get_who_user_owns_to(user_name=user_name)
        debtors = get_who_owns_to_user(user_name=user_name)
        user_dict = {
            "jmeno": user_name,
            "dluzi": creditors,
            "dluzi_mu": debtors,
            "suma": get_sum(debtors, creditors)
        }
        return user_dict
    for user in db.query(models.User.name).all():
        name = "".join([i for i in user])
        creditors = get_who_user_owns_to(user_name=name)
        debtors = get_who_owns_to_user(user_name=name)
        user_dict = {
            "jmeno": name,
            "dluzi": creditors,
            "dluzi_mu": debtors,
            "suma": get_sum(debtors, creditors)
        }
        users.append(user_dict)
    return users


def create_user(db: Session, user: schemas.UserBase):
    """
    Creates user for db.
    """
    db_user = models.User(name=user.user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"jmeno": db_user.name, "dluzi": {}, "dluzi_mu": {}, "suma": 0}


def create_transaction(db: Session, transaction: schemas.TransactionBase):
    """
    Creates a transaction.
    Returns a both objects ordered by "jmeno".
    """
    db_debtor = db.query(models.User).filter(models.User.name == transaction.dluznik).first()
    db_creditor = db.query(models.User).filter(models.User.name == transaction.veritel).first()

    db_transaction = models.Transaction(debtor=db_debtor.id, creditor=db_creditor.id, amount=transaction.castka)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    filter_list = [db_debtor.name, db_creditor.name]
    users_dict = get_all_users_with_data(db)
    result = []
    for i, j in enumerate(users_dict):
        if j["jmeno"] in filter_list:
            result.append(j)
    sorted_result = sorted(result, key=lambda key: key["jmeno"])
    return sorted_result


def get_who_owns_to_user(user_name: str):
    """
    Gets a dictionary of names that own to a user and the amount.
    I couldn't get this query work with sqalchemy so I had to use sqlite3.
    """
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(f"""SELECT u2.name, sum(t.amount) FROM transactions t
                         INNER JOIN users u1 ON u1.id = t.creditor
                         INNER JOIN users u2 ON u2.id = t.debtor
                         WHERE u1.name = '{user_name}' GROUP BY u2.name""")
    result = cur.fetchall()
    debtors = {}
    for i, j in result:
        debtors[i] = j
    return debtors


def get_who_user_owns_to(user_name: str):
    """
    Gets a dictionary of names that user owns to and the amount.
    I couldn't get this query work with sqalchemy so I had to use sqlite3.
    """
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(f"""SELECT u2.name, sum(t.amount) FROM transactions t
                         INNER JOIN users u1 ON u1.id = t.debtor
                         INNER JOIN users u2 ON u2.id = t.creditor
                         WHERE u1.name = '{user_name}' GROUP BY u2.name""")
    result = cur.fetchall()
    creditors = {}
    for i, j in result:
        creditors[i] = j
    return creditors


def get_sum(debtors: dict, creditors: dict):
    """
    Gets the sum of total debt + total credit.
    """
    debt_sum = sum(debtors.values())
    credit_sum = sum(creditors.values())
    return debt_sum + credit_sum
