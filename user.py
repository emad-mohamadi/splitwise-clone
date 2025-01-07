from currencyconvert import Conversions
from datetime import datetime, timedelta
from uuid import uuid1
from copy import deepcopy
from database import DataBase


class User:
    def __init__(self, id, ref: DataBase):
        data = ref.tables["users"].get[id]
        self.id = id
        self.name = data["name"]
        self.avatar = data["avatar"]
        self.groups = data["groups"]
        self.people = data["people"]
        self.invites = data["invites"]
        self.settings = data["settings"]
        self.currency = Conversions(self.settings["default-currency"])
        self.scheduled = []

        return


class Group:
    def __init__(self, id, ref: DataBase):
        data = ref.tables["groups"].get[id]
        self.total = 0
        self.id = id
        self.name = data["name"]
        self.avatar = data["avatar"]
        self.members = data["members"]
        self.transactions = data["transactions"]
        self.scheduled = []
        self.passed = []
        self.balance = None
        self.passed, self.scheduled = [], []
        now = datetime.now()
        for tr_id in deepcopy(self.transactions):
            tr = ref.tables["transactions"].get[tr_id]
            temp = deepcopy(tr)
            temp.pop("nid")
            if datetime.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f') < now:
                freq = temp["repeat"]
                temp["repeat"] = ""
                self.passed.append(deepcopy(temp))
                if freq:
                    ref.tables["transactions"].get[tr_id]["repeat"] = ""
                    ref.modify("transactions", tr_id, "repeat", "")
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
                        freq = ""
                    ref.insert("transactions", [temp])
                    ref.tables["transactions"].get[temp["id"]] = deepcopy(temp)
                    self.transactions.append(deepcopy(temp["id"]))

            else:
                self.scheduled.append(deepcopy(temp))

            ref.modify("groups", id, "transactions", self.transactions)

            self.passed.sort(key=lambda tr: datetime.strptime(
                tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
            self.scheduled.sort(key=lambda tr: datetime.strptime(
                tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)

        return
