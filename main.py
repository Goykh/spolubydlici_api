from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel

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


class User(BaseModel):
    user: str


class Transaction(BaseModel):
    dluznik: str
    veritel: str
    suma: float


class UserList(BaseModel):
    uzivatele: list[str] = Query()
def get_sum_of_amounts():
    for i, j in enumerate(users):
        amount = sum(users[i]['dluzi'].values()) + sum(users[i]['dluzi_mu'].values())
        users[i]['suma'] = amount


@app.get('/users')
async def get_users(uzivatele: dict = Body()):
    get_sum_of_amounts()
    if uzivatele:
        result = []
        for i, j in enumerate(users):
            if users[i]['jmeno'] in uzivatele:
                result.append(users[i])
        return result.sort()
    else:
        return users


@app.post('/add')
async def add_new_user(user: User):
    for i, j in enumerate(users):
        if j['jmeno'] == user.user:
            raise HTTPException(status_code=400, detail="Jméno už je v seznamu.")
    new_user = {
        'jmeno': user.user,
        'dluzi': {},
        'dluzi_mu': {},
        'suma': ""
    }
    users.append(new_user)
    return new_user


@app.post('/transaction')
async def make_transaction(transaction: Transaction):
    # adding data to debtor
    names_of_users = [i['jmeno'] for i in users]
    if transaction.dluznik not in names_of_users or transaction.veritel not in names_of_users:
        raise HTTPException(status_code=400, detail="Zadali jste jméno, které se v seznamu nenachází.")
    for i, j in enumerate(users):
        if users[i]['jmeno'] == transaction.dluznik:
            if transaction.veritel in users[i]['dluzi']:
                users[i]['dluzi'][transaction.veritel] += transaction.suma
            else:
                users[i]['dluzi'][transaction.veritel] = transaction.suma

    # adding data to creditor
    for i, j in enumerate(users):
        if users[i]['jmeno'] == transaction.veritel:
            if transaction.dluznik in users[i]['dluzi_mu']:
                users[i]['dluzi_mu'][transaction.dluznik] += transaction.suma
            else:
                users[i]['dluzi_mu'][transaction.dluznik] = transaction.suma
    get_sum_of_amounts()
    result = []
    for i, j in enumerate(users):
        if users[i]['jmeno'] in [transaction.dluznik, transaction.veritel]:
            result.append(users[i])

    return result
