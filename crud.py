import sqlite3

from sqlalchemy.orm import Session

import models
import schemas


def get_user_by_name(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.name == user_name).first()


def get_all_users_with_data(db: Session):
    users = []
    for user in db.query(models.User.name).all():
        name = "".join([i for i in user])
        user_dict = {
            "jmeno": name,
            "dluzi": get_who_user_owns_to(user_name=name),
            "dluzi_mu": get_who_owns_to_user(user_name=name),
            "suma": get_sum(get_who_owns_to_user(user_name=name), get_who_user_owns_to(user_name=name))
        }
        users.append(user_dict)
    return {"uzivatele": users}


def get_user_data_by_name(db: Session, user_name: str):
    name = db.query(models.User).filter(models.User.name == user_name)
    user_dict = {
        "jmeno": name,
        "dluzi": get_who_user_owns_to(user_name=name),
        "dluzi_mu": get_who_owns_to_user(user_name=name),
        "suma": get_sum(get_who_owns_to_user(user_name=name), get_who_user_owns_to(user_name=name))
    }
    return user_dict


def create_user(db: Session, user: schemas.UserBase):
    db_user = models.User(name=user.user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"jmeno": db_user.name, "dluzi": {}, "dluzi_mu": {}, "suma": 0}


def create_transaction(db: Session, transaction: schemas.TransactionBase):
    # TODO: error handling
    db_debtor = db.query(models.User).filter(models.User.name == transaction.dluznik).first()
    db_creditor = db.query(models.User).filter(models.User.name == transaction.veritel).first()

    db_transaction = models.Transaction(debtor=db_debtor.id, creditor=db_creditor.id, amount=transaction.castka)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    filter_list = [db_debtor.name, db_creditor.name]
    users_dict = get_all_users_with_data(db)
    result = [d for d in users_dict if d["jmeno"] in filter_list]
    sorted_result = sorted(result, key=lambda key: key["jmeno"])
    return sorted_result


def get_who_owns_to_user(user_name: str):
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
    debt_sum = sum(debtors.values())
    credit_sum = sum(creditors.values())
    return debt_sum + credit_sum
