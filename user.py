from currencyconvert import Conversions
from datetime import datetime, timedelta
from uuid import uuid1
from copy import deepcopy


class User:
    def __init__(self, id, data=None):
        self.id = id
        self.name = data["users"][id]["name"]
        self.avatar = data["users"][id]["avatar"]
        self.groups = data["users"][id]["groups"]
        self.people = data["users"][id]["people"]
        self.invites = data["users"][id]["invites"]
        self.settings = data["users"][id]["settings"]
        self.currency = Conversions(self.settings["default-currency"])
        self.scheduled = []
        return


class Group:
    def __init__(self, id, data):
        self.id = id
        self.name = data["groups"][id]["name"]
        self.avatar = data["groups"][id]["avatar"]
        self.members = data["groups"][id]["members"]
        self.transactions = data["groups"][id]["transactions"]
        self.scheduled = []
        self.passed = []
        self.balance = None
        self.passed, self.scheduled = [], []
        now = datetime.now()
        for tr in self.transactions:
            temp = deepcopy(tr)
            if datetime.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f') < now:
                freq = temp["repeat"]
                temp["repeat"] = False
                self.passed.append(deepcopy(temp))
                while freq:
                    temp["id"] = str(uuid1())
                    new_date = datetime.strptime(
                        temp["date"], '%Y-%m-%d %H:%M:%S.%f')
                    new_date += timedelta(days=1) if freq == "daily" else timedelta(
                        days=7) if freq == "weekly" else timedelta(days=30) if freq == "monthly" else timedelta(days=365)
                    temp["date"] = new_date.strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    if new_date < now:
                        self.passed.append(deepcopy(temp))
                    else:
                        temp["repeat"] = freq
                        self.scheduled.append(deepcopy(temp))
                        freq = False
            else:
                self.scheduled.append(deepcopy(temp))

            self.passed.sort(key=lambda tr: datetime.strptime(
                tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
            self.scheduled.sort(key=lambda tr: datetime.strptime(
                tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)

        return
