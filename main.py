from fastapi import FastAPI

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


def get_sum_of_amounts():
    for i, j in enumerate(users):
        amount = sum(users[i]['dluzi'].values()) + sum(users[i]['dluzi_mu'].values())
        users[i]['suma'] = amount


@app.get('/users')
async def get_users(users_list: list[str] | None = None):
    get_sum_of_amounts()
    # TODO: dis no work, need to fix
    if users_list:
        result = []
        for i, j in enumerate(users):
            if users[i]['jmeno'] in users_list:
                result.append(users[i])
        return result.sort()
    else:
        return users


@app.post('/add')
async def add_new_user(user: str):
    #TODO: need to add if statement to stop duplicate names
    users.append({
        'jmeno': user,
        'dluzi': {},
        'dluzi_mu': {},
        'suma': ""
    })
    print(users)
    return {'user': user}


@app.post('/transaction')
async def make_transaction(creditor: str, debtor: str, amount: float):
    # adding data to debtor
    for i, j in enumerate(users):
        if users[i].get('jmeno') == debtor:
            if creditor in users[i].get('dluzi'):
                users[i]['dluzi'][creditor] += amount
            else:
                users[i]['dluzi'][creditor] = amount

    # adding data to creditor
    for i, j in enumerate(users):
        if users[i].get('jmeno') == creditor:
            if debtor in users[i].get('dluzi_mu'):
                users[i]['dluzi_mu'][debtor] += amount
            else:
                users[i]['dluzi_mu'][debtor] = amount
    get_sum_of_amounts()
    result = []
    for i, j in enumerate(users):
        if users[i]['jmeno'] in [debtor, creditor]:
            result.append(users[i])

    return result
