class User:
    def __init__(self, id, data=None):
        self.id = id
        self.name = data["users"][id]["name"]
        self.groups = data["users"][id]["groups"]
        self.people = data["users"][id]["people"]
        self.invites = data["users"][id]["invites"]
        return


class Group:
    def __init__(self, id, data):
        self.id = id
        self.name = data["groups"][id]["name"]
        self.members = data["groups"][id]["members"]
        self.transactions = data["groups"][id]["transactions"]
        return
