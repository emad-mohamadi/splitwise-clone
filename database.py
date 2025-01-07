from supabase import Client, create_client
import json
from random import choice, randint

# Set up Supabase client
URL = "https://qrdbmqosjdulvsmdvwia.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFyZGJtcW9zamR1bHZzbWR2d2lhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU1NzA2MTUsImV4cCI6MjA1MTE0NjYxNX0.9JMjUwv75YA3NJTnd-j88CPJ540nCuTCh_LB-Cccmrc"


class DataBase(Client):
    def __init__(self, tables=["users", "groups", "transactions"], supabase_url=URL, supabase_key=KEY, options=None):
        super().__init__(supabase_url, supabase_key, options)
        self.status = True
        try:
            self.tables = {t: Table(self.get_all(t, key="*")) for t in tables}
        except:
            self.status = False

    def modify(self, table, id, key, value):
        self.table(table).update({key: value}).eq("id", id).execute()

    def insert(self, table, value):
        self.table(table).insert(value).execute()

    def delete(self, table, id):
        self.table(table).delete().eq("id", id).execute()

    def pop(self, table, id, key, value):
        response = self.table(table).select(key).eq("id", id).execute()
        updated = [item for item in response.data[0]
                   [key] if item != value]
        self.modify(table, id, key, updated)

    def add(self, table, id, key, value):
        response = self.table(table).select(key).eq("id", id).execute()
        updated = [item for item in response.data[0][key]] + [value]
        self.modify(table, id, key, updated)

    def get(self, table, id, key="*"):
        response = self.table(table).select(key).eq("id", id).execute()
        return response.data[0] if key == "*" else response.data[0][key]

    def get_all(self, table, key="id"):
        response = self.table(table).select(key).execute()
        return response.data if key == "*" else [record[key] for record in response.data]

    def reload(self):
        self.tables = {t: Table(self.get_all(t, key="*")) for t in self.tables}

    def init_user(self, id, name):
        new_user = {
            "id": id,
            "name": name,
            "avatar": "avatars/unknown.png",
            "groups": [],
            "invites": [],
            "people": {},
            "settings": {
                "default-currency": "USD",
            }
        }
        self.insert("users", [new_user])

    def reset(self, table):
        for id in self.tables[table].get:
            self.delete(table, id)

    def reset_all(self):
        for table in self.tables:
            self.reset(table)


class Table:
    def __init__(self, data):
        self.data = data
        self.get = {item["id"]: item for item in data}


# with open('sample.json') as f:
#     data = json.load(f)

# ref = DataBase()
# ref.reset_all()
# ref.init_user("emad")
# ref.init_user("danial")
# ref.init_user("melo")
# ref.insert("passwords", a)
