from interface import *
from user import User, Group
from alg import Network
from random import choice
from uuid import uuid1
from datetime import datetime as dt
from datetime import timedelta
from copy import deepcopy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import DataBase
from pandas import DataFrame as DF

config = {
    "avatars": {
        "people": [(f"avatars/male{i}.png", f"avatars/female{i}.png") for i in range(8)],
        "groups": [f"avatars/group{i}.png" for i in range(9)],
        "unknown": "avatars/unknown.png"
    },
    "icons": {
        "add-member": "icons/add-member.png",
        "edit-name": "icons/edit-name.png",
        "password": "icons/password.png",
        "logout": "icons/logout.png",
        "export": "icons/export.png"
    },
    "app": {
        "sidebar": {
            "home": ("icons/home.png", TOP),
            "groups": ("icons/groups.png", TOP),
            "people": ("icons/people.png", TOP),
            "invites": ("icons/invites.png", TOP),
            "setting": ("icons/setting.png", BOTTOM)
        },
        "sidepanels": {
            "home": {
                "height": 70,
                "font": ("Arial Bold", 25),
                "label": None,
                "button": None,
                "text": None
            },
            "groups": {
                "height": 70,
                "font": ("Arial Bold", 25),
                "label": "Groups",
                "button": ("New group", 80),
                "text": None
            },
            "people": {
                "height": 70,
                "font": ("Arial Bold", 25),
                "label": "Friends",
                "button": ("New friend", 80),
                "text": None,
            },
            "invites": {
                "height": 70,
                "font": ("Arial Bold", 25),
                "label": "Invites",
                "button": None,
                "text": None,
            },
            "setting": {
                "height": 70,
                "font": ("Arial Bold", 25),
                "label": "Setting",
                "button": None,
                "text": None,
            },
        }
    }
}


class App(CTk):
    def __init__(self, title="Splitwise", appearance_mode="light"):
        super().__init__()
        self.ref = DataBase()
        set_appearance_mode(appearance_mode)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.scr_w = self.winfo_screenwidth()
        self.scr_h = self.winfo_screenheight()
        self.geometry(f"{int(0.7*self.scr_w)}x{self.scr_h//2}+{self.scr_w //
                      4}+{self.scr_h//4}")  # Initial window size
        self.title(title)  # seting window title
        self.last_tab = "home"
        self.last_panel = "empty"
        self.status = {panel: None for panel in config["app"]["sidebar"]}
        self.popup_stack = []
        return

    def singup(self):
        self.root = Frame(self, corner_radius=20)

        CTkLabel(self.root, text="Sing-up", font=("Arial Bold", 25),
                 text_color="gray50").pack(side=TOP, pady=15)

        widget = Frame(self.root, fg_color="transparent")
        CTkLabel(widget, text="Name                          ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        name = CTkEntry(widget, fg_color="gray90",
                        corner_radius=15, border_width=0)
        name.pack(side=LEFT, padx=10)
        widget.pack(side=TOP, pady=10, padx=2)

        widget = Frame(self.root, fg_color="transparent")
        CTkLabel(widget, text="Username                   ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        username = CTkEntry(widget, fg_color="gray90",
                            corner_radius=15, border_width=0)
        username.pack(side=LEFT, padx=10)
        widget.pack(side=TOP, pady=10, padx=2)

        widget = Frame(self.root, fg_color="transparent")
        CTkLabel(widget, text="Create password       ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        pass1 = CTkEntry(widget, fg_color="gray90", corner_radius=15,
                         border_width=0)
        pass1.configure(show="●")
        pass1.pack(side=LEFT, padx=10)
        widget.pack(side=TOP, pady=10, padx=2)

        widget = Frame(self.root, fg_color="transparent")
        CTkLabel(widget, text="Confirm password     ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        pass2 = CTkEntry(widget, fg_color="gray90", corner_radius=15,
                         border_width=0)
        pass2.configure(show="●")
        pass2.pack(side=LEFT, padx=10)
        widget.pack(side=TOP, pady=10, padx=2)

        widget = Frame(self.root, fg_color="transparent")
        CTkButton(widget, width=10, corner_radius=15, command=self.signup_action(name, username, pass1, pass2),
                  fg_color="steel blue", text="Sign-up").pack(side=RIGHT, padx=2)
        widget.pack(fill="x", side=BOTTOM, pady=10, padx=10)
        CTkButton(widget, width=10, hover=False, fg_color="transparent", font=CTkFont(family="Arial", size=14, underline=True),
                  text="Login", text_color="royal blue", command=self.switch("login")).pack(side=RIGHT, padx=5)
        CTkLabel(widget, text="Already have an account?", font=(
            "Arial", 14), text_color="gray50").pack(side=RIGHT, padx=0)
        widget.pack(fill="x", side=BOTTOM, pady=10, padx=10)

        self.root.pack(expand=True)

    def login(self):
        self.root = Frame(self, corner_radius=20)

        CTkLabel(self.root, text="Login", font=("Arial Bold", 25),
                 text_color="gray50").pack(side=TOP, pady=15)

        widget = Frame(self.root, fg_color="transparent")
        CTkLabel(widget, text="Username                  ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        username = CTkEntry(widget, fg_color="gray90",
                            corner_radius=15, border_width=0)
        username.pack(side=LEFT, padx=10)
        widget.pack(side=TOP, pady=10, padx=2)

        widget = Frame(self.root, fg_color="transparent")
        CTkLabel(widget, text="Password                  ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        password = CTkEntry(widget, fg_color="gray90", corner_radius=15,
                            border_width=0)
        password.configure(show="●")
        password.pack(side=LEFT, padx=10)
        widget.pack(side=TOP, pady=10, padx=2)

        widget = Frame(self.root, fg_color="transparent")
        CTkButton(widget, width=10, corner_radius=15, command=self.login_action(username, password),
                  fg_color="steel blue", text="Login").pack(side=RIGHT, padx=2)
        widget.pack(fill="x", side=BOTTOM, pady=10, padx=10)
        CTkButton(widget, width=10, hover=False, fg_color="transparent", font=CTkFont(family="Arial", size=14, underline=True),
                  text="Sign-up", text_color="royal blue", command=self.switch("signup")).pack(side=RIGHT, padx=5)
        CTkLabel(widget, text="Don't have an account?", font=(
            "Arial", 14), text_color="gray50").pack(side=RIGHT, padx=0)
        widget.pack(fill="x", side=BOTTOM, pady=10, padx=10)

        self.root.pack(expand=True)

    def switch(self, action):
        def f():
            self.root.destroy()
            if action == "login":
                self.login()
            else:
                self.singup()
        return f

    def signup_action(self, name_entry, username_entry, pass1_entry, pass2_entry):
        def f():
            name = name_entry.get()
            username = username_entry.get()
            pass1 = pass1_entry.get()
            pass2 = pass2_entry.get()

            if not name:
                self.show_message("Enter your name.")
                return
            if username in self.ref.tables["users"].get:
                self.show_message("Username is not available")
                return
            if len(pass1) < 8:
                self.show_message("Password is too short.")
                return
            if pass1 != pass2:
                self.show_message("Password not confirmed.")
                return

            self.ref.init_user(username, name)
            self.ref.insert("passwords", [{"id": username, "password": pass1}])
            self.ref.reload()
            self.root.destroy()
            self.load(username)
            self.side_bar.button_handler("setting")()
            self.choose_avatar(username, "user")()

        return f

    def login_action(self, username_entry, password_entry):
        def f():
            username = username_entry.get()
            password = password_entry.get()

            if username in self.ref.tables["users"].get and password == self.ref.get("passwords", username, "password"):
                self.root.destroy()
                self.load(username)
            else:
                self.show_message("Invalid username or password.")
                return

        return f

    def logout(self):
        self.ref.reload()
        self.root.destroy()
        self.login()

    def change_password(self):
        self.close_popups()
        win = CTkToplevel(self)
        win.title("ChooseAvatar")
        win.geometry(f"{self.scr_w//4}x{int(0.5*self.scr_h)
                                        }+{int(0.4*self.scr_w)}+{self.scr_h//5}")
        win.lift()
        win.focus()
        win.attributes("-topmost", True)
        self.popup_stack.append(win)

        frame = Frame(win, width=300, height=400, corner_radius=20)

        CTkLabel(frame, text="Change password", font=("Arial Bold", 25),
                 text_color="gray50").pack(side=TOP, pady=15)

        widget = Frame(frame, fg_color="transparent")
        CTkLabel(widget, text="Old password             ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        old = CTkEntry(widget, fg_color="gray90",
                       corner_radius=15, border_width=0)
        old.pack(side=LEFT, padx=10)
        old.configure(show="●")
        widget.pack(side=TOP, pady=10, padx=2)

        widget = Frame(frame, fg_color="transparent")
        CTkLabel(widget, text="New password           ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        pass1 = CTkEntry(widget, fg_color="gray90", corner_radius=15,
                         border_width=0)
        pass1.configure(show="●")
        pass1.pack(side=LEFT, padx=10)
        widget.pack(side=TOP, pady=10, padx=2)

        widget = Frame(frame, fg_color="transparent")
        CTkLabel(widget, text="Confirm password     ", font=(
            "Arial Bold", 14)).pack(side=LEFT, padx=15)
        pass2 = CTkEntry(widget, fg_color="gray90", corner_radius=15,
                         border_width=0)
        pass2.configure(show="●")
        pass2.pack(side=LEFT, padx=10)
        widget.pack(side=TOP, pady=10, padx=2)

        CTkButton(frame, width=10, corner_radius=15, command=self.change_password_action(old, pass1, pass2),
                  fg_color="steel blue", text="Change").pack(side=BOTTOM, pady=10)

        frame.pack(expand=True)

    def change_password_action(self, old_entry, new1_entry, new2_entry):
        def f():
            old = old_entry.get()
            new1 = new1_entry.get()
            new2 = new2_entry.get()

            if old != self.ref.get("passwords", self.user.id, "password"):
                self.show_message("Wrong password.")
                return
            if len(new1) < 8:
                self.show_message("Password is too short.")
                return
            if new1 != new2:
                self.show_message("Password not confirmed.")
                return

            self.ref.modify("passwords", self.user.id, "password", new1)
            self.close_popups()
            self.refresh()
        return f

    def load(self, id):
        self.user = User(id, self.ref)
        config["app"]["sidepanels"]["home"]["label"] = f"Welcome, {
            self.user.name}"
        self.ref.tables["users"].get[id]["name"] = "You"
        groups_list = [Group(id, self.ref) for id in self.user.groups]
        people_list = [User(id, self.ref) for id in self.user.people]

        last_groups_trs = {gr.id: self.last_tr(
            gr.transactions) for gr in groups_list}
        last_people_trs = {fr.id: self.last_tr(
            fr.people[self.user.id]["transactions"]) for fr in people_list}

        people_list.sort(key=lambda x: dt.strptime(
            last_people_trs[x.id]["date"] if last_people_trs[x.id] else "0001-01-01 00:00:00.1", '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
        groups_list.sort(key=lambda x: dt.strptime(
            last_groups_trs[x.id]["date"] if last_groups_trs[x.id] else "0001-01-01 00:00:00.1", '%Y-%m-%d %H:%M:%S.%f'), reverse=True)

        self.root = Frame(self)
        self.side_bar = SideBar(
            self.root, config["app"]["sidebar"], default_tab=self.last_tab)

        total_group_expenses = {gr.id: gr.total for gr in groups_list}
        balances = {}
        for gr in groups_list:
            balances[gr.id] = self.simplify(gr)

        people_balances = {fr.id: 0.0 for fr in people_list}
        total_friend_expenses = {fr.id: 0.0 for fr in people_list}
        for fr in people_list:
            for tr_id in fr.people[self.user.id]["transactions"]:
                tr = self.ref.tables["transactions"].get[tr_id]
                if dt.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f') <= dt.now():
                    if self.user.id == tr["creditor"]:
                        people_balances[fr.id] += float(tr["amounts"][0])
                    else:
                        people_balances[fr.id] -= float(tr["amounts"][0])
                    total_friend_expenses[fr.id] += float(tr["amounts"][0])

        total_net_balance = sum(people_balances.values()
                                ) + sum([gr.balance for gr in groups_list])
        objects = {
            "name": ["1", "2"],
            "label": [f"Total expense {sum(total_friend_expenses.values())+sum(total_group_expenses.values())} {self.user.currency.default}", "Most expensers"],
            "button": [None, None],
            "text": [[(f"{sum(total_group_expenses.values())} {self.user.currency.default} in groups", None), (f"{sum(total_friend_expenses.values())} {self.user.currency.default} in friends", None)], [(f"in groups: {self.ref.tables["groups"].get[max(total_group_expenses, key=lambda x: total_group_expenses[x])]["name"]} {total_group_expenses[max(total_group_expenses, key=lambda x: total_group_expenses[x])]} {self.user.currency.default}" if total_group_expenses else "No groups yet", None), (f"in friends: {self.ref.tables["users"].get[max(total_friend_expenses, key=lambda x: total_friend_expenses[x])]["name"]} {total_friend_expenses[max(total_friend_expenses, key=lambda x: total_friend_expenses[x])]} {self.user.currency.default}" if total_friend_expenses else "No friends yet", None)]],
        }
        config["app"]["sidepanels"]["home"]["text"] = f"Total net balance {
            total_net_balance} {self.user.currency.default}"
        self.home = FrameList(self.side_bar.panels["home"], config["app"]
                              ["sidepanels"]["home"], objects, height=70, width=320)

        objects = {
            "name": [group.id for group in groups_list],
            "label": [group.name for group in groups_list],
            "button": [("View", 45, (None, None), None) for _ in groups_list],
            "text": [[(f"Net balance: {gr.balance}", "red3" if gr.balance < 0 else "green" if gr.balance > 0 else "midnight blue"), (f"{last_groups_trs[gr.id]["name"]} {sum([float(amnt) for amnt in last_groups_trs[gr.id]["amounts"]])} {last_groups_trs[gr.id]["currency"]}" if last_groups_trs[gr.id] else "No expenses yet", None if last_groups_trs[gr.id] else "gray50"), (last_groups_trs[gr.id]["date"][:16] if last_groups_trs[gr.id] else "", "gray50")] for gr in groups_list]
        }

        if not groups_list:
            config["app"]["sidepanels"]["groups"]["label"] = "No groups yet"
        self.groups = FrameList(self.side_bar.panels["groups"], config["app"]
                                ["sidepanels"]["groups"], objects, height=80, command=self.new_group, width=320)

        objects = {
            "name": [user.id for user in people_list],
            "label": [user.name for user in people_list],
            "button": [("View", 45, (None, None), None) for _ in people_list],
            "text": [[(f"Net balance: {people_balances[fr.id]}", "red3" if people_balances[fr.id] < 0 else "green" if people_balances[fr.id] > 0 else "midnight blue"), (f"{last_people_trs[fr.id]["name"]} {last_people_trs[fr.id]["amounts"][0]} {last_people_trs[fr.id]["currency"]}" if last_people_trs[fr.id] else "No expenses yet", None if last_people_trs[fr.id] else "gray50"), (last_people_trs[fr.id]["date"][:16] if last_people_trs[fr.id] else "", "gray50")] for fr in people_list],
        }
        if not people_list:
            config["app"]["sidepanels"]["people"]["label"] = "No friends yet"
        self.people = FrameList(self.side_bar.panels["people"], config["app"]
                                ["sidepanels"]["people"], objects, height=80, command=self.new_friend, width=320)

        i = len(self.user.invites)
        while i:
            i -= 1
            if self.user.invites[i][0] not in self.ref.tables["groups"].get:
                self.ref.pop("users", self.user.id,
                             "invites", self.user.invites[i])
                self.ref.tables["users"].get[self.user.id]["invites"].remove(
                    self.user.invites[i])
                self.user.invites.pop(i)

        objects = {
            "name": [invite[0]+str(invite[2]) for invite in self.user.invites],
            "label": [f"{self.ref.tables["users"].get[self.ref.tables["groups"].get[invite[0]]["members"][0]]["name"]} invited {"you" if not invite[2] else self.ref.tables["users"].get[invite[2]]["name"]} to {self.ref.tables["groups"].get[invite[0]]["name"]}" for invite in self.user.invites],
            "button": [("Delete", 53, ("red3", "red4"), self.invite_action(invite, False)) if invite[2] else ("Accept", 56, (None, None), self.invite_action(invite, True)) for invite in self.user.invites],
            "text": [((invite[1][:16], "gray50"),) for invite in self.user.invites]
        }
        if not self.user.invites:
            config["app"]["sidepanels"]["invites"]["label"] = "No invites yet"
        self.invites = FrameList(self.side_bar.panels["invites"], config["app"]
                                 ["sidepanels"]["invites"], objects, height=50, font=("Arial", 14), font_dif=2, width=320)

        self.settings = Frame(
            self.side_bar.panels["setting"], height=1000, width=335, fg_color="transparent")
        CTkButton(self.settings, text="", width=10, height=10, command=self.choose_avatar(self.user.id, "user"), image=Frame.picture(
            self.user.avatar, (75, 75)), fg_color="transparent", hover=False).place(x=10, y=13)
        name = CTkEntry(self.settings, height=40, width=170, corner_radius=10, text_color="gray40", border_width=0,
                        fg_color="transparent", font=("Arial Bold", 35))
        name.insert(0, self.user.name)
        name.place(x=100, y=20)
        id = CTkEntry(self.settings, height=40, width=170, corner_radius=10, text_color="gray40", border_width=0,
                      fg_color="transparent", font=("Jetbrains Mono", 18))
        id.insert(0, "@"+self.user.id)
        id.place(x=100, y=55)
        CTkButton(self.settings, image=Frame.picture(config["icons"]["edit-name"], (30, 30)), text="", corner_radius=0, width=10, height=10,
                  fg_color="transparent", hover_color="gray60", command=self.rename_user(name, id)).place(x=280, y=20)
        CTkButton(self.settings, image=Frame.picture(config["icons"]["password"], (20, 20)), text="Change password", compound=RIGHT, width=10, height=10,
                  font=("Arial", 18), text_color="black", fg_color="transparent", hover=False, command=self.change_password).place(x=15, y=100)
        CTkButton(self.settings, image=Frame.picture(config["icons"]["logout"], (20, 20)), text="Logout", compound=RIGHT, width=10, height=10,
                  font=("Arial", 18), text_color="red4", fg_color="transparent", hover=False, command=self.logout).place(x=220, y=100)
        CTkLabel(self.settings, text="Default currency", font=("Arial", 18),
                 text_color="black", fg_color="transparent").place(x=21, y=160)
        CTkOptionMenu(self.settings, width=25, values=[self.user.currency.default]+[item for item in self.user.currency.currencies if item != self.user.currency.default], command=self.set_sefault_currency).place(
            x=245, y=162)
        self.settings.pack(fill="y", padx=5, pady=5)

        for panel in self.side_bar.panels:
            self.status[panel] = CTkLabel(
                self.side_bar.panels[panel], text="You're offline", height=30, font=("Arial Bold", 16), corner_radius=0, bg_color="DarkGoldenrod1")
        self.check_status()

        empty = MainPanel(self.root)
        empty.add_title(text="There's nothing to show.",
                        font=("Arial", 18), color="gray60", not_placed=True)
        empty.title.pack(expand=True)
        links = {"empty": empty}
        self.status = {}
        for gr in groups_list:
            owner = gr.members[0] == self.user.id
            options = {
                "label": [self.ref.tables["users"].get[id]["name"] for id in gr.members],
                "color": ["gray60" if i else "gray30" for i in range(len(gr.members))],
                "command": [self.select_member(id) for id in gr.members],
            }
            if owner:
                options["label"].append(None)
                options["color"].append(Frame.picture(
                    config["icons"]["add-member"], (20, 20)))
                options["command"].append(self.new_invite(gr))
            buttons = {
                "label": ["New expense", "Group info"],
                "color": [(None, None), (None, None)],
                "command": [self.new_group_expense(gr), self.manage_group(gr)],
            }
            main_panel = MainPanel(self.root)
            main_panel.add_title(text=gr.name, avatar=gr.avatar, command=self.choose_avatar(
                gr.id, "group") if owner else None)
            main_panel.add_options(options)
            main_panel.add_button(buttons)
            main_panel.set_body()
            links[gr.id] = main_panel
            recent = Frame(main_panel.body, fg_color="gray83",
                           height=500, corner_radius=15)
            summary = Frame(main_panel.body,
                            fg_color="transparent", corner_radius=15)
            header = {
                "height": 30,
                "font": ("Arial Bold", 18),
                "label": "Expenses" if gr.passed else "No expenses yet",
                "button": ("Filter", 0) if gr.passed else None,
                "text": None,
            }
            objects = {
                "name": [tr["id"] for tr in gr.passed],
                "label": [tr["name"] for tr in gr.passed],
                "button": [(f"{sum([float(amnt) for amnt in tr["amounts"]])} {tr["currency"]}", 45, ("gray50", "gray60"), None) for tr in gr.passed],
                "text": [[(f"{self.ref.tables["users"].get[tr["creditor"]]["name"]} lent {App.sentence("group", [self.ref.tables["users"].get[debtor]["name"] for debtor in tr["debtors"]])}", "black"), (tr["date"][:16], "gray50")] for tr in gr.passed],
            }
            commands = {
                tr["id"]: self.new_group_expense(gr, tr) for tr in gr.passed}
            FrameList(recent, header, objects, commands, width=10, header_min_height=True, command=self.filter_expenses(gr.name, self.ref.tables["groups"].get[gr.id]["transactions"], gr.members),
                      height=70, title_color="gray50")

            simlified = balances[gr.id]
            header = {
                "height": 30,
                "font": ("Arial Bold", 18),
                "label": " Summary" if simlified else "All settled up",
                "button": None,
                "text": None,
            }
            objects = {
                "name": [str(i) for i in range(len(simlified))],
                "label": [f"{self.ref.tables["users"].get[debtor]["name"]} {"owes" if debtor != self.user.id else "owe"} {self.ref.tables["users"].get[creditor]["name"]} {amount} {self.user.currency.default}" for debtor, creditor, amount in simlified],
                "button": [("Settle-up", 10, ("gray50", "gray60"), None) if creditor == self.user.id else None for _, creditor, _ in simlified],
                "text": [[]]*len(simlified),
                "color": ["red3" if self.user.id == debtor else "green" if self.user.id == creditor else "black" for debtor, creditor, _ in simlified]
            }
            settled = {str(i): self.new_group_expense(gr, {"id": None, "name": "Settled up", "amounts": [str(simlified[i][2])], "creditor": simlified[i][0], "debtors": [
                simlified[i][1]], "currency": self.user.currency.default, "date": None, "repeat": False}) for i in range(len(simlified)) if simlified[i][1] == self.user.id}
            FrameList(summary, header, objects, width=30, min_height=True, commands=settled,
                      height=25, title_color="gray50", font=("Arial", 14))
            recent.pack(side=LEFT, fill="both", expand=True)
            summary.pack(side=RIGHT, fill="both", expand=True)

        self.groups.add_link(links)

        links = {"empty": empty}
        for us in people_list:
            passed, us.scheduled = [], []
            now = dt.now()
            for tr_id in deepcopy(self.user.people[us.id]["transactions"]):
                tr = self.ref.tables["transactions"].get[tr_id]
                temp = deepcopy(tr)
                if "nid" in temp:
                    temp.pop("nid")
                if dt.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f') < now:
                    freq = temp["repeat"]
                    passed.append(deepcopy(temp))
                    while freq:
                        temp["id"] = str(uuid1())
                        new_date = dt.strptime(
                            temp["date"], '%Y-%m-%d %H:%M:%S.%f')
                        new_date += timedelta(days=1) if freq == "daily" else timedelta(
                            days=7) if freq == "weekly" else timedelta(days=30) if freq == "monthly" else timedelta(days=365)
                        temp["date"] = new_date.strftime(
                            '%Y-%m-%d %H:%M:%S.%f')
                        self.user.people[us.id]["transactions"].append(
                            temp["id"])
                        us.people[self.user.id]["transactions"].append(
                            temp["id"])
                        self.ref.insert("transactions", [temp])
                        self.ref.tables["transactions"].get[temp["id"]] = deepcopy(
                            temp)
                        self.ref.modify("users", us.id, "people", us.people)
                        self.ref.tables["users"].get[us.id]["people"][self.user.id]["transactions"]
                        self.ref.modify("users", self.user.id,
                                        "people", self.user.people)
                        if new_date < now:
                            passed.append(deepcopy(temp))
                        else:
                            temp["repeat"] = freq
                            us.scheduled.append(deepcopy(temp))
                            break
                else:
                    us.scheduled.append(deepcopy(temp))

            passed.sort(key=lambda tr: dt.strptime(
                tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
            us.scheduled.sort(key=lambda tr: dt.strptime(
                tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)

            buttons = {
                "label": ["New expense", f"Remove friend"],
                "color": [(None, None), ("red3", "red4")],
                "command": [self.new_personal_expense(us), self.remove_friend(us)]
            }
            total_lent, total_borrowed = 0, 0
            for expense in passed:
                if us.id == expense["creditor"]:
                    total_borrowed += self.user.currency.convert(
                        expense["amounts"][0], expense["currency"])
                else:
                    total_lent += self.user.currency.convert(
                        expense["amounts"][0], expense["currency"])
            balance = total_lent - total_borrowed
            debtor = balance < 0
            options = {
                "label": [f"{"You" if debtor else us.name} {"owe" if debtor else "owes"} {"You" if not debtor else us.name} {abs(balance)} {self.user.currency.default}" if balance else "All settled up"],
                "color": ["gray60"],
                "command": [self.new_personal_expense(us, {"id": None, "name": "Settled up", "amounts": [str(balance)], "creditor": [us.id], "debtors": self.user.id, "currency": self.user.currency.default, "date": None, "repeat": False}) if balance > 0 else None],
            }
            main_panel = MainPanel(self.root)
            main_panel.add_title(text=us.name, avatar=us.avatar)
            main_panel.add_button(buttons)
            main_panel.add_options(
                options, color="red3" if debtor else "green" if balance else "gray50")
            main_panel.set_body()
            links[us.id] = main_panel
            hist = Frame(main_panel.body,
                         fg_color="gray83", corner_radius=15)
            summary = Frame(main_panel.body,
                            fg_color="transparent", corner_radius=15)
            header = {
                "height": 30,
                "font": ("Arial Bold", 18),
                "label": "Expenses" if passed else "No expenses yet",
                "button": ("Filter", 0) if passed else None,
                "text": None,
            }
            objects = {
                "name": [tr["id"] for tr in passed],
                "label": [tr["name"] for tr in passed],
                "button": [(f"{tr["amounts"][0]} {tr["currency"]}", 45, ("gray50", "gray60"), None) for tr in passed],
                "text": [[(f"You {"lent" if tr["creditor"] == self.user.id else "borrowed"}", "black"), (tr["date"][:16], "gray50")] for tr in passed],
            }
            commands = {tr["id"]: self.new_personal_expense(
                us, tr) for tr in passed}
            FrameList(hist, header, objects, width=10, commands=commands, command=self.filter_expenses(us.name, self.user.people[us.id]["transactions"], [self.user.id, us.id]),
                      header_min_height=True, height=70, title_color="gray50")

            header = {
                "height": 30,
                "font": ("Arial Bold", 18),
                "label": " Summary",
                "button": None,
                "text": None,
            }
            objects = {
                "name": ["1"],
                "label": [f"Total expensed: {total_borrowed+total_lent} {self.user.currency.default}"],
                "button": [None],
                "text": [[(f"You expensed {total_lent} {self.user.currency.default}", "gray40"), (f"{us.name} expensed {total_borrowed} {self.user.currency.default}", "gray40")]],
                "color": [None]
            }
            body = FrameList(summary, header, objects, width=30,
                             height=70, title_color="gray50", font=("Arial", 18), font_dif=4)

            CTkLabel(body.scroll, text=f" {"S" if us.scheduled else "No s"}cheduled expenses", font=(
                "Arial", 18), text_color="gray50").pack(anchor="nw", padx=10, pady=5)
            widget = Frame(body.scroll, height=10, corner_radius=0)
            widget.pack(padx=5, fill="x", anchor="nw")
            for tr in us.scheduled:
                item = Frame(widget, height=10,
                             corner_radius=15, fg_color="gray80")
                label = Frame(item, height=10, width=10,
                              fg_color="transparent")
                label.pack(side=LEFT, padx=15, pady=5)
                CTkLabel(label, height=20, text=tr["name"], font=(
                    "Arial", 16)).pack(anchor="nw")
                total_amount = sum([float(amnt) for amnt in tr["amounts"]])
                CTkButton(item, height=35, width=30, corner_radius=10, text=f"{total_amount} {tr["currency"]}", border_width=2,
                          border_color="gray50", fg_color="transparent", hover_color="gray70", text_color="black", command=self.new_personal_expense(us, tr)).pack(side=RIGHT, padx=5, pady=5)
                item.pack(side=TOP, fill="x", padx=5, pady=5)
                CTkLabel(label, height=10, text=f"{tr["date"][:10]}   ({tr["repeat"] if tr["repeat"] else "no repeat"})", font=(
                    "Arial", 13, "bold"), text_color="gray50").pack(anchor="nw")
                item.pack(side=TOP, fill="x", padx=5, pady=5)
            hist.pack(side=LEFT, fill="both", expand=True)
            summary.pack(side=RIGHT, fill="both", expand=True)

        self.people.add_link(links)
        self.groups.button_handler("empty")()

        self.root.pack(fill="both", expand=True)
        return

    def last_tr(self, tr_ids):
        if not tr_ids:
            return 0
        temp = [deepcopy(self.ref.tables["transactions"].get[tr_id])
                for tr_id in tr_ids]
        temp = [t for t in temp if dt.strptime(
            t["date"], '%Y-%m-%d %H:%M:%S.%f') <= dt.now()]
        temp.sort(key=lambda x: x["date"], reverse=True)
        return temp[0]

    def remove_friend(self, user: User):
        def f():
            self.user.people.pop(user.id)
            user.people.pop(self.user.id)
            self.ref.modify("users", self.user.id, "people", self.user.people)
            self.ref.modify("users", user.id, "people", user.people)
            self.refresh(self.people.button_handler("empty"))
        return f

    def apply_filters(self, owner_name, tr_ids, us_ids, name_entry, creditor_entry, debtor_entry, date_from_entry, date_to_entry, amount_from_entry, amount_to_entry, sort_by_entry, convert_entry):

        def f():
            name = name_entry.get().strip()
            creditor = creditor_entry.get()
            debtor = debtor_entry.get()
            date_from = date_from_entry.get().strip()
            date_to = date_to_entry.get().strip()
            amount_from = amount_from_entry.get().strip()
            amount_to = amount_to_entry.get().strip()
            sort_by = sort_by_entry.get()
            convert = convert_entry.get()
            last_filter = {
                "name": name,
                "creditor": creditor,
                "debtor": debtor,
                "date-from": date_from,
                "date-to": date_to,
                "amount-from": amount_from,
                "amount-to": amount_to,
                "sort-by": sort_by,
                "convert": convert
            }

            us_names = {item["id"]: item["name"]
                        for item in self.ref.tables["users"].get.values()}
            trs = [self.ref.tables["transactions"].get[id] for id in tr_ids]

            def sort_tr(item):
                match sort_by.split()[0]:
                    case "date":
                        return dt.strptime(item["date"], '%Y-%m-%d %H:%M:%S.%f')
                    case "amount":
                        return sum([float(amnt) for amnt in item["amounts"]])

            trs.sort(key=sort_tr, reverse=(sort_by[-1] == "↑"))
            mask = []

            for tr in trs:
                name_check = True
                if name:
                    name_check = name.lower() in tr["name"].lower().split()

                creditor_check = True
                if creditor:
                    creditor_check = creditor.lower() in [
                        tr["creditor"].lower(), us_names[tr["creditor"]].lower()]

                debtor_check = True
                if debtor:
                    debtor_check = False
                    for id in tr["debtors"]:
                        if debtor.lower() in [id.lower(), us_names[id].lower()]:
                            debtor_check = True
                            break

                tr_date = dt.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f')
                date_from_check = True
                if date_from:
                    try:
                        date_from_check = dt.strptime(
                            f"{date_from} 00:00:00", '%Y.%m.%d %H:%M:%S') <= tr_date
                    except:
                        self.show_message("Invalid date.")
                        return
                date_to_check = True
                if date_to:
                    try:
                        date_to_check = tr_date <= dt.strptime(
                            f"{date_to} 23:59:59", '%Y.%m.%d %H:%M:%S')
                    except:
                        self.show_message("Invalid date.")
                        return

                tr_amount = sum([float(amnt) for amnt in tr["amounts"]])
                if convert != "off":
                    tr_amount = self.user.currency.convert(
                        tr_amount, tr["currency"], convert)
                amount_from_check = True
                if amount_from:
                    amount_from_check = float(amount_from) <= tr_amount
                amount_to_check = True
                if amount_to:
                    amount_to_check = tr_amount <= float(amount_to)

                check = name_check and creditor_check and debtor_check and date_from_check and date_to_check and amount_from_check and amount_to_check
                mask.append(check)

            self.filter_expenses(owner_name, [tr["id"]
                                 for tr in trs], us_ids, mask, last_filter)()

            pass
        return f

    def filter_expenses(self, owner_name, tr_ids, us_ids, mask=None, prefilled=None):
        if not prefilled:
            prefilled = {
                "name": "",
                "creditor": "",
                "debtor": "",
                "date-from": "",
                "date-to": "",
                "amount-from": "",
                "amount-to": "",
                "sort-by": "date ↑",
                "convert": "off"
            }
        if not mask:
            mask = [True for _ in tr_ids]
        tr_ids, us_ids = deepcopy(tr_ids), deepcopy(us_ids)

        def f():
            self.close_popups()
            win = CTkToplevel(self)
            win.title("ExpenseFilter")
            win.geometry(f"{int(0.3*self.scr_w)}x{int(0.6*self.scr_h)}+{self.scr_w //
                                                                        4}+{self.scr_h//4}")
            win.lift()
            win.focus()
            win.attributes("-topmost", True)
            self.popup_stack.append(win)

            frame = Frame(win, width=400, height=400, corner_radius=20)

            widget = Frame(frame, height=50, width=10, fg_color="transparent")
            widget.pack(fill="x", side=TOP, padx=10, pady=10)
            CTkLabel(widget, text="Description", font=(
                "Arial", 16, "bold"), text_color="gray50").pack(side=LEFT, padx=5)
            name = CTkEntry(widget, border_width=0, width=90, font=(
                "Arial", 14), fg_color="gray80")
            name.pack(side=LEFT, padx=5)
            CTkLabel(widget, text="sort by", font=(
                "Arial", 14)).pack(side=LEFT, padx=5)
            sort_by = CTkOptionMenu(widget, width=50, values=[
                                    "date ↑", "date ↓", "amount ↑", "amount ↓"], font=("Arial", 14))
            sort_by.pack(side=LEFT, padx=5)
            sort_by.set(prefilled["sort-by"])

            widget = Frame(frame, height=50, width=10, fg_color="transparent")
            widget.pack(fill="x", side=TOP, padx=10, pady=5)
            CTkLabel(widget, text="Creditor", font=("Arial", 16, "bold"),
                     text_color="gray50").pack(side=LEFT, padx=5)
            creditor = CTkComboBox(widget, width=100, values=[""] + [id for id in us_ids],
                                   font=("Arial", 14), fg_color="gray80")
            creditor.set(prefilled["creditor"])
            creditor.pack(side=LEFT, padx=5)
            CTkLabel(widget, text=" Debtor", font=("Arial", 16, "bold"),
                     text_color="gray50").pack(side=LEFT, padx=5)
            debtor = CTkComboBox(widget, width=100, values=[""] + [id for id in us_ids],
                                 font=("Arial", 14), fg_color="gray80")
            debtor.set(prefilled["debtor"])
            debtor.pack(side=LEFT, padx=5)

            widget = Frame(frame, height=50, width=10, fg_color="transparent")
            widget.pack(fill="x", side=TOP, padx=10, pady=5)
            CTkLabel(widget, text="Date     ", text_color="gray50", font=(
                "Arial", 16, "bold")).pack(side=LEFT, padx=5)
            CTkLabel(widget, text="from", width=40, font=(
                "Arial", 14)).pack(side=LEFT, padx=0)
            date_from = CTkEntry(widget, border_width=0, width=105, font=(
                "Arial", 14), fg_color="gray80")
            date_from.insert(0, prefilled["date-from"])
            date_from.pack(side=LEFT, padx=5)
            CTkLabel(widget, text="to", width=20, font=(
                "Arial", 14)).pack(side=LEFT, padx=0)
            date_to = CTkEntry(widget, border_width=0, width=105, font=(
                "Arial", 14), fg_color="gray80")
            date_to.insert(0, prefilled["date-to"])
            date_to.pack(side=LEFT, padx=5)

            widget = Frame(frame, height=50, width=10, fg_color="transparent")
            widget.pack(fill="x", side=TOP, padx=10, pady=5)
            CTkLabel(widget, text="Amount", text_color="gray50", font=(
                "Arial", 16, "bold")).pack(side=LEFT, padx=5)
            CTkLabel(widget, text="from", width=40, font=(
                "Arial", 14)).pack(side=LEFT, padx=0)
            amount_from = CTkEntry(widget, border_width=0, width=105, font=(
                "Arial", 14), fg_color="gray80")
            amount_from.insert(0, prefilled["amount-from"])
            amount_from.pack(side=LEFT, padx=5)
            CTkLabel(widget, text="to", width=20, font=(
                "Arial", 14)).pack(side=LEFT, padx=0)
            amount_to = CTkEntry(widget, border_width=0, width=105, font=(
                "Arial", 14), fg_color="gray80")
            amount_to.insert(0, prefilled["amount-to"])
            amount_to.pack(side=LEFT, padx=5)

            widget = Frame(frame, height=50, width=10, fg_color="transparent")
            widget.pack(fill="x", side=TOP, padx=10, pady=5)
            CTkLabel(widget, text="Convert currency", font=(
                "Arial", 14)).pack(side=LEFT, padx=5)
            currency = CTkOptionMenu(widget, width=50, values=[
                                     "off"]+self.user.currency.currencies, font=("Arial", 14))
            currency.set(prefilled["convert"])
            currency.pack(side=LEFT, padx=5)
            CTkButton(widget, width=10, height=25, corner_radius=10, text="Apply filter", command=self.apply_filters(owner_name, tr_ids, us_ids, name, creditor, debtor, date_from, date_to, amount_from, amount_to, sort_by, currency),
                      font=("Arial Bold", 14)).pack(side=LEFT, padx=5)

            us_names = {item["id"]: item["name"]
                        for item in self.ref.tables["users"].get.values()}
            filtered = [deepcopy(self.ref.tables["transactions"].get[tr_ids[i]])
                        for i in range(len(tr_ids)) if mask[i]]
            tr_list = CTkScrollableFrame(frame, corner_radius=15)
            for tr in filtered:
                item = Frame(tr_list, height=10,
                             corner_radius=15, fg_color="gray70")
                label = Frame(item, height=10, width=10,
                              fg_color="transparent")
                label.pack(side=LEFT, padx=15, pady=5)
                CTkLabel(label, height=20, text=tr["name"], font=(
                    "Arial", 16)).pack(anchor="nw")
                total_amount = sum([float(amnt) for amnt in tr["amounts"]])
                CTkButton(item, height=35, width=30, corner_radius=10, text=f"{total_amount} {tr["currency"]}", border_width=2,
                          border_color="gray50", fg_color="transparent", hover_color="gray70", text_color="black").pack(side=RIGHT, padx=5, pady=5)
                item.pack(side=TOP, fill="x", padx=5, pady=5)
                CTkLabel(label, height=10, text=f"{us_names[tr["creditor"]]} to {App.sentence("group", [us_names[id] for id in tr["debtors"]])} - {tr["date"][2:10]}", font=(
                    "Arial", 13, "bold"), text_color="gray50").pack(anchor="nw")
                item.pack(side=TOP, fill="x", padx=5, pady=5)

            CTkButton(tr_list, width=30, image=Frame.picture(config["icons"]["export"], (20, 20)), compound=RIGHT, height=25, corner_radius=15, text="Export", command=self.export_expenses(filtered, owner_name),
                      fg_color="transparent", hover=False, text_color="black", font=("Arial Bold", 14), border_width=2, border_color="gray70").pack(side=BOTTOM, pady=15)

            tr_list.pack(pady=10, padx=10, fill="x")

            frame.pack(expand=True)
            pass
        return f

    def export_expenses(self, trs, owner):
        trs = deepcopy(trs)
        for tr in trs:
            tr.pop("nid")
            tr.pop("id")

        def f():
            self.close_popups()
            export = filedialog.asksaveasfile(
                initialfile=f"exported-{self.user.id}({owner})-{str(dt.now())
                                                                [:16].replace(" ", "-").replace(":", ".")}.csv",
                defaultextension=".csv",
                filetypes=[("CSV file", "*.csv")]
            )
            if export.name:
                DF(trs).to_csv(export.name)

        return f

    def show_message(self, text):
        win = CTkToplevel(self)
        win.title("Message")
        win.geometry(f"{self.scr_w//5}x60+{int(0.5*self.scr_w)
                                           }+{int(0.4*self.scr_h)}")
        win.lift()
        win.focus()
        win.attributes("-topmost", True)
        self.popup_stack.append(win)
        CTkLabel(win, text=text, justify=CENTER,
                 wraplength=250).pack(expand=True)

    def set_sefault_currency(self, choice):
        self.user.currency.default = choice
        temp = self.user.settings
        temp["default-currency"] = choice
        self.ref.modify("users", self.user.id, "settings", temp)
        self.ref.tables["users"].get[self.user.id]["settings"]["default-currency"] = choice
        self.refresh(self.groups.button_handler("empty"))

    def select_member(self, member):
        def f():
            if member in self.user.people:
                self.people.button_handler(member)()
            elif member == self.user.id:
                self.side_bar.button_handler("setting")()
            else:
                self.new_friend(preset=member)

        return f

    def choose_avatar(self, id, owner_type):
        def f():
            self.close_popups()
            win = CTkToplevel(self)
            win.title("ChooseAvatar")
            win.geometry(f"{self.scr_w//4}x{int(0.5*self.scr_h)
                                            }+{int(0.4*self.scr_w)}+{self.scr_h//5}")
            win.lift()
            win.focus()
            win.attributes("-topmost", True)
            self.popup_stack.append(win)

            def select_avatar(avatar):
                def f():
                    if owner_type == "user":
                        self.ref.modify("users", self.user.id,
                                        "avatar", avatar)
                        self.ref.tables["users"].get[self.user.id]["avatar"] = avatar
                        self.close_popups()
                        self.refresh(self.people.button_handler("empty"))
                    else:
                        self.ref.modify("groups", id,
                                        "avatar", avatar)
                        self.ref.tables["groups"].get[id]["avatar"] = avatar
                        self.close_popups()
                        self.refresh(self.groups.button_handler(id))

                return f

            frame = Frame(win, width=300, height=400, corner_radius=20)
            CTkLabel(frame, text="Choose your preferred avatar", font=(
                "Arial", 18, "bold"), text_color="gray50").pack(pady=10)
            if owner_type == "user":
                for i in [0, 1, 2, 3]:
                    row = Frame(frame, fg_color="transparent", height=70)
                    CTkButton(row, height=75, width=75, command=select_avatar(config["avatars"]["people"][i][i % 2]), image=Frame.picture(
                        config["avatars"]["people"][i][i % 2], (70, 70)), text="", fg_color="transparent", hover=False).pack(side=LEFT, padx=2)
                    CTkButton(row, height=75, width=75, command=select_avatar(config["avatars"]["people"][i][not (i % 2)]), image=Frame.picture(
                        config["avatars"]["people"][i][not (i % 2)], (70, 70)), text="", fg_color="transparent", hover=False).pack(side=LEFT, padx=2)
                    CTkButton(row, height=75, width=75, command=select_avatar(config["avatars"]["people"][i+4][i % 2]), image=Frame.picture(
                        config["avatars"]["people"][i+4][i % 2], (70, 70)), text="", fg_color="transparent", hover=False).pack(side=LEFT, padx=2)
                    CTkButton(row, height=75, width=75, command=select_avatar(config["avatars"]["people"][i+4][not (i % 2)]), image=Frame.picture(
                        config["avatars"]["people"][i+4][not (i % 2)], (70, 70)), text="", fg_color="transparent", hover=False).pack(side=LEFT, padx=2)
                    row.pack(fill="x", side=TOP, pady=6, padx=5)
            else:
                for i in [0, 3, 6]:
                    row = Frame(frame, fg_color="transparent", height=70)
                    CTkButton(row, height=100, width=100, command=select_avatar(config["avatars"]["groups"][i]), image=Frame.picture(
                        config["avatars"]["groups"][i], (100, 100)), text="", fg_color="transparent", hover=False).pack(side=LEFT, padx=2)
                    CTkButton(row, height=100, width=100, command=select_avatar(config["avatars"]["groups"][i+1]), image=Frame.picture(
                        config["avatars"]["groups"][i+1], (100, 100)), text="", fg_color="transparent", hover=False).pack(side=LEFT, padx=2)
                    CTkButton(row, height=100, width=100, command=select_avatar(config["avatars"]["groups"][i+2]), image=Frame.picture(
                        config["avatars"]["groups"][i+2], (100, 100)), text="", fg_color="transparent", hover=False).pack(side=LEFT, padx=2)
                    row.pack(fill="x", side=TOP, pady=6, padx=5)

            frame.pack(expand=True)

            pass
        return f

    def manage_group(self, group: Group):
        owner = self.user.id == group.members[0]

        def f():
            self.close_popups()
            win = CTkToplevel(self)
            win.title("GroupInfo")
            win.geometry(f"{self.scr_w//4}x{int(0.5*self.scr_h)
                                            }+{int(0.4*self.scr_w)}+{self.scr_h//5}")
            win.lift()
            win.focus()
            win.attributes("-topmost", True)
            self.popup_stack.append(win)
            frame = CTkScrollableFrame(
                win, corner_radius=20, width=300)

            widget = Frame(frame, height=10, width=200, fg_color="transparent")
            widget.pack(pady=0, padx=0, fill="x", anchor="nw")
            if owner:
                name = CTkEntry(widget, height=40, width=150, corner_radius=10, text_color="gray40", border_width=0,
                                fg_color="transparent", font=("Arial Bold", 25))
                name.insert(0, group.name)
                name.pack(side=LEFT)
                CTkButton(widget, image=Frame.picture(config["icons"]["edit-name"], (30, 30)), text="", corner_radius=0, width=10, height=10,
                          font=("Arial Bold", 10), fg_color="transparent", hover_color="gray60", command=self.rename_group(group, name)).pack(side=RIGHT, padx=15)
            else:
                CTkLabel(widget, text=group.name, font=(
                    "Arial Bold", 25), text_color="gray40").pack(side=LEFT, padx=10, pady=5)

            widget = Frame(frame, height=10, corner_radius=0)
            widget.pack(padx=5, fill="x", anchor="nw")
            network = Network(group.members.copy())
            for expense in group.passed:
                for i in range(len(expense["debtors"])):
                    amount = self.user.currency.convert(
                        float(expense["amounts"][i]), expense["currency"])
                    network.add_debt(
                        expense["debtors"][i], expense["creditor"], amount)
            for id in group.members:
                item = Frame(widget, height=70,
                             corner_radius=15, fg_color="gray80")
                CTkLabel(item, height=30, text=self.ref.tables["users"].get[id]["name"], font=(
                    "Arial", 16)).pack(side=LEFT, padx=15)
                if id == group.members[0]:
                    CTkButton(item, height=20, width=20, corner_radius=10, text="Owner", border_width=0,
                              hover_color="gray80", fg_color="transparent", font=("Arial", 12, "bold"), text_color="gray40").pack(side=RIGHT, padx=5, pady=5)
                elif owner:
                    CTkButton(item, height=20, width=30, corner_radius=10, text="Remove", border_width=2, command=self.remove_member(group, id),
                              border_color="red4", fg_color="transparent", hover=False, text_color="red4").pack(side=RIGHT, padx=5, pady=5)
                amnt = network.balance[id]
                CTkLabel(item, height=30, text='{0:{1}}'.format(amnt, '+' if amnt else '')+f" {self.user.currency.default}", font=(
                    "Arial", 13), text_color="green" if amnt > 0 else "red3").pack(side=LEFT, padx=10)
                item.pack(side=TOP, fill="x", padx=5, pady=5)
            if owner:
                CTkButton(frame, image=Frame.picture(
                    config["icons"]["add-member"], (25, 25)), corner_radius=15, text="Invite people", text_color="gray40", font=("Arial", 16), fg_color="transparent", hover_color="gray80", command=self.new_invite(group)).pack(anchor="nw", padx=10, pady=5)

            CTkLabel(frame, text=f"{"S" if group.scheduled else "No s"}cheduled expenses", font=(
                "Arial", 18), text_color="gray50").pack(anchor="nw", padx=10, pady=5)
            widget = Frame(frame, height=10, corner_radius=0)
            widget.pack(padx=5, fill="x", anchor="nw")
            for tr in group.scheduled:
                item = Frame(widget, height=10,
                             corner_radius=15, fg_color="gray80")
                label = Frame(item, height=10, width=10,
                              fg_color="transparent")
                label.pack(side=LEFT, padx=15, pady=5)
                CTkLabel(label, height=20, text=tr["name"], font=(
                    "Arial", 16)).pack(anchor="nw")
                total_amount = sum([float(amnt) for amnt in tr["amounts"]])
                CTkButton(item, height=35, width=30, corner_radius=10, text=f"{total_amount} {tr["currency"]}", border_width=2,
                          border_color="gray50", fg_color="transparent", hover_color="gray70", text_color="black", command=self.new_group_expense(group, tr)).pack(side=RIGHT, padx=5, pady=5)
                item.pack(side=TOP, fill="x", padx=5, pady=5)
                CTkLabel(label, height=10, text=f"{tr["date"][:10]}   ({tr["repeat"] if tr["repeat"] else "no repeat"})", font=(
                    "Arial", 13, "bold"), text_color="gray50").pack(anchor="nw")
                item.pack(side=TOP, fill="x", padx=5, pady=5)

            total = network.total_expensed
            CTkLabel(frame, text=f"{"Total" if total else "No"} expense{f": {total} {self.user.currency.default}" if total else "s yet"}", font=(
                "Arial", 18), text_color="gray50").pack(anchor="nw", padx=10, pady=5)
            widget = Frame(frame, height=10, corner_radius=0)
            widget.pack(padx=5, fill="x", anchor="nw")
            for id, total in sorted([(i, j) for i, j in network.expensed.items() if j], key=lambda i: i[1], reverse=True):
                item = Frame(widget, height=70,
                             corner_radius=15, fg_color="gray80")
                CTkLabel(item, height=30, text=self.ref.tables["users"].get[id]["name"], font=(
                    "Arial", 16)).pack(side=LEFT, padx=15)
                CTkButton(item, height=20, width=20, corner_radius=10, text=f"{total} {self.user.currency.default}", border_width=0,
                          hover_color="gray80", fg_color="transparent", font=("Arial", 12, "bold"), text_color="gray40").pack(side=RIGHT, padx=5, pady=5)
                item.pack(side=TOP, fill="x", padx=5, pady=5)

            if total:
                fig = network.visualize(
                    {member: self.ref.tables["users"].get[member]
                        ["avatar"] for member in group.members},
                    {member: self.ref.tables["users"].get[member]["name"]
                        for member in group.members},
                    config["avatars"]["unknown"]
                )
                graph = FigureCanvasTkAgg(fig, master=frame)
                graph.draw()
                graph.get_tk_widget().pack(padx=10, pady=10)

            CTkButton(frame, height=25, width=30, corner_radius=15, text=f"{"Delete" if owner else "Leave"} group",
                      fg_color="red3", hover_color="red4", command=self.delete_group(group) if owner else self.remove_member(group, self.user.id)).pack(side=BOTTOM, pady=10)

            frame.pack(expand=True, fill="y", pady=40)
        return f

    def delete_group(self, group: Group):
        def f():
            confirmation = CTkInputDialog(
                title="Confirm", text="Type in your password to confirm", button_fg_color="gray60", button_hover_color="gray50")
            if confirmation.get_input() != self.ref.get("passwords", self.user.id, "password"):
                self.show_message("Wrong password, Confirmation failed")
                return
            for id in group.members:
                self.ref.pop("users", id, "groups", group.id)
                self.ref.tables["users"].get[id]["groups"].remove(group.id)
            self.ref.delete("groups", group.id)
            self.ref.tables["groups"].get.pop(group.id)
            self.close_popups()
            self.refresh(self.groups.button_handler("empty"))

        return f

    def rename_group(self, group: Group, new_name_entry):
        def f():
            new_name = new_name_entry.get()
            if not new_name:
                self.show_message("Enter group name")
                return
            group.name = new_name
            self.ref.modify("groups", group.id, "name", new_name)
            self.ref.tables["groups"].get[group.id]["name"] = new_name
            self.close_popups()
            self.refresh(self.groups.button_handler(group.id))

        return f

    def rename_user(self, new_name_entry, new_id_entry):
        def f():
            new_name = new_name_entry.get()
            new_id = new_id_entry.get()
            if not new_name:
                self.show_message("Enter name.")
                return
            if not new_id.startswith("@"):
                self.show_message("Add @ befor your username.")
                return
            new_id = new_id[1:].strip()
            # if new_id.find(""):
            #     self.show_message("Invalid username")
            if len(new_id) < 4:
                self.show_message("Username is too short.")
                return
            if new_id != self.user.id and new_id in self.ref.tables["users"].get:
                self.show_message("Username not available.")
                return

            if not self.user.id == new_id or not self.user.name == new_name:
                self.user.name = new_name

                for group in self.user.groups:
                    members = self.ref.tables["groups"].get[group]["members"]
                    members[members.index(self.user.id)] = new_id
                    self.ref.modify("groups", group, "members", members)

                for tr_id in self.ref.tables["transactions"].get:
                    tr = self.ref.tables["transactions"].get[tr_id]
                    if tr["creditor"] == self.user.id:
                        self.ref.modify(
                            "transactions", tr["id"], "creditor", new_id)
                    if self.user.id in tr["debtors"]:
                        tr["debtors"].insert(
                            tr["debtors"].index(self.user.id), new_id)
                        tr["debtors"].remove(self.user.id)
                        self.ref.modify(
                            "transactions", tr["id"], "debtors", tr["debtors"])

                for invite in self.user.invites:
                    if self.user.id in invite:
                        invite.insert(invite.index(self.user.id), new_id)
                        invite.remove(self.user.id)
                self.ref.modify("users", self.user.id,
                                "invites", self.user.invites)
                self.ref.tables["users"].get[self.user.id]["invites"] = self.user.invites

                for us_id in self.ref.tables["users"].get:
                    user = self.ref.tables["users"].get[us_id]
                    if self.user.id in user["people"]:
                        user["people"][self.user.id]["name"] = new_name
                        user["people"][new_id] = user["people"].pop(
                            self.user.id)
                        self.ref.modify(
                            "users", user["id"], "people", user["people"])

                    for inv in user["invites"]:
                        if self.user.id in inv:
                            inv.insert(inv.index(self.user.id), new_id)
                            inv.remove(self.user.id)
                    self.ref.modify("users", user["id"],
                                    "invites", user["invites"])

                self.ref.modify("users", self.user.id, "id", new_id)
                self.ref.modify("users", new_id, "name", new_name)
                self.ref.tables["users"].get[new_id] = self.ref.tables["users"].get.pop(
                    self.user.id)
                self.ref.tables["users"].get[new_id]["id"] = new_id
                self.ref.tables["users"].get[new_id]["name"] = new_name
                self.ref.modify("passwords", self.user.id, "id", new_id)
                self.user.id = new_id
            self.close_popups()
            self.refresh(self.groups.button_handler("empty"))

        return f

    def remove_member(self, group: Group, id):
        def f():
            self.ref.pop("groups", group.id, "members", id)
            self.ref.pop("users", id, "groups", group.id)
            self.ref.tables["groups"].get[group.id]["members"].remove(id)
            self.ref.tables["users"].get[id]["groups"].remove(group.id)
            self.close_popups()
            self.refresh(self.groups.button_handler(group.id))
        return f

    def check_status(self):
        if self.ref.status:
            for panel in self.side_bar.panels:
                self.status[panel].pack_forget()
        else:
            for panel in self.side_bar.panels:
                self.status[panel].pack(side=BOTTOM, padx=0, pady=0, fill="x")

    def new_personal_expense(self, user: User, prefilled=False):
        default_split = "unequally"
        default_values = prefilled
        edit = True
        if not default_values:
            edit = False
            default_split = "equally"
            default_values = {
                "id": str(uuid1()),
                "name": "",
                "amounts": [""],
                "debtors": [user.id],
                "creditor": self.user.id,
                "currency": self.user.currency.default,
                "date": str(dt.now()),
                "repeat": "",
            }
        if not default_values["id"]:
            edit = False
            default_values["id"] = str(uuid1())
        if not default_values["date"]:
            default_values["date"] = str(dt.now())

        def f():
            self.close_popups()
            win = CTkToplevel(self)
            win.title("NewExpense")
            win.geometry(f"{self.scr_w//4}x{int(0.7*self.scr_h)
                                            }+{int(0.4*self.scr_w)}+{self.scr_h//5}")
            win.lift()
            win.focus()
            win.attributes("-topmost", True)
            self.popup_stack.append(win)
            frame = Frame(win, corner_radius=20)

            widget = Frame(frame, height=10, fg_color="transparent")
            widget.pack(pady=10, padx=15, fill="x")
            CTkLabel(widget, text=f"{"Edit" if edit else "Add"} expense", font=(
                "Arial Bold", 25), text_color="gray40").pack(side=LEFT)
            if edit:
                CTkButton(widget, text="Delete", text_color="red3", fg_color="transparent", height=20, hover_color="gray70",
                          width=35, border_width=2, border_color="red3", corner_radius=10, command=self.delete_expense(user, default_values["id"])).pack(side=RIGHT)

            entry = Frame(frame, height=50, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=15, fill="x")
            CTkLabel(entry, width=10, text="Description", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            name = CTkEntry(entry, height=30, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            name.pack(padx=5, fill="x")
            name.insert(0, default_values["name"])

            entry = Frame(frame, height=10, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=5, fill="x")
            widget = CTkLabel(entry, text="Paid by", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)
            creditor = CTkOptionMenu(entry, height=25, width=70, values=["You", user.name],
                                     font=("Arial", 16, "bold"))
            creditor.pack(side=LEFT, padx=5)
            creditor.set(
                "You" if default_values["creditor"] == self.user.id else user.name)
            widget = CTkLabel(entry, text="in", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)
            currency = CTkComboBox(entry, height=25, width=70, values=self.user.currency.currencies,
                                   font=("Arial", 16))
            currency.pack(side=LEFT, padx=5)
            currency.set(default_values["currency"])

            def split_options(debtor):
                if debtor == "both":
                    split_label.pack(side=LEFT, padx=5)
                    split.pack(side=LEFT, padx=5)
                    split_types(default_split)
                else:
                    split_label.pack_forget()
                    split.pack_forget()
                    uneq.pack_forget()

            def split_types(selected):
                if selected == "equally" or debtors.get() != "both":
                    uneq.pack_forget()
                    amount_frame.pack(fill="x", expand=True, padx=10, side=TOP)
                elif debtors.get() == "both":
                    if selected == "by ratio":
                        amount_frame.pack(
                            fill="x", expand=True, padx=10, side=TOP)
                    else:
                        amount_frame.pack_forget()
                    uneq.pack(fill="x", expand=True, padx=10, side=TOP)

            entry = Frame(frame, height=10, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=5, fill="x")
            widget = CTkLabel(entry, text="to", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)
            debtors = CTkOptionMenu(entry, height=25, width=70, values=["both", "You", user.name],
                                    font=("Arial", 16, "bold"), command=split_options)
            debtors.pack(side=LEFT, padx=5)
            debtors.set("both" if len(
                default_values["debtors"]) == 2 else user.name if default_values["debtors"][0] == user.id else "You")
            split_label = CTkLabel(
                entry, text="& splitted", font=("Arial", 18))
            split = CTkOptionMenu(entry, height=25, width=60, values=["equally", "by ratio", "unequally"],
                                  font=("Arial", 16, "bold"), command=split_types)
            split.set(default_split)

            widget = Frame(frame, height=10, fg_color="transparent")
            widget.pack(fill="x", expand=True, padx=0, side=TOP)
            uneq = Frame(widget, height=10, fg_color="transparent")
            amount_frame = Frame(widget, height=10, fg_color="transparent")
            you = Frame(uneq, height=10, fg_color="transparent")
            you.pack(side=LEFT, fill="x", expand=True, pady=5, padx=5)
            him = Frame(uneq, height=10, fg_color="transparent")
            him.pack(side=RIGHT, fill="x", expand=True, pady=5, padx=5)
            CTkLabel(amount_frame, width=10, font=(
                "Arial", 16), text="Total amount").pack(side=LEFT, padx=5)
            total = CTkEntry(amount_frame, height=25, border_width=0, width=120,
                             fg_color="gray70", font=("Arial", 14))
            total.pack(side=RIGHT, fill="x", padx=5)
            total.insert(0, default_values["amounts"][0])
            amounts = [None, None]
            CTkLabel(you, width=10, font=(
                "Arial", 16), text="You").pack(side=LEFT, padx=0)
            amounts[0] = CTkEntry(you, height=25, border_width=0, width=80,
                                  fg_color="gray70", font=("Arial", 14))
            amounts[0].pack(side=LEFT, fill="x", padx=10)
            amounts[0].insert(0, default_values["amounts"][default_values["debtors"].index(
                self.user.id)] if len(default_values["amounts"]) == 2 else "")
            CTkLabel(him, width=10, font=(
                "Arial", 16), text=user.name).pack(side=LEFT, padx=0)
            amounts[1] = CTkEntry(him, height=25, border_width=0, width=80,
                                  fg_color="gray70", font=("Arial", 14))
            amounts[1].pack(side=LEFT, fill="x", padx=10)
            amounts[1].insert(0, default_values["amounts"][default_values["debtors"].index(
                user.id)] if len(default_values["amounts"]) == 2 else "")

            schedule = Frame(frame, height=10, fg_color="transparent")
            widget = Frame(schedule, height=10, width=10,
                           fg_color="transparent")
            widget.pack(anchor="nw")
            CTkLabel(widget, width=10, text="Date", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            date = CTkEntry(widget, height=30, width=100, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            date.pack(side=LEFT, padx=5, fill="x", expand=True)
            date.insert(0, default_values["date"][:10].replace("-", "."))
            CTkLabel(widget, width=10, text="Time", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            time = CTkEntry(widget, height=30, width=60, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            time.pack(side=LEFT, padx=5, fill="x", expand=True)
            time.insert(0, default_values["date"][11:16])
            widget = Frame(schedule, height=10, width=10,
                           fg_color="transparent")
            widget.pack(anchor="nw", pady=5)
            repeat = CTkComboBox(widget, height=25, width=100, values=["none", "weekly", "daily", "monthly", "yearly"],
                                 font=("Arial", 16, "bold"))
            CTkLabel(widget, width=10, text="Repeat", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            repeat.pack(side=LEFT, padx=5)
            repeat.set(default_values["repeat"]
                       if default_values["repeat"] else "none")

            def toggle():
                if checkbox.get():
                    schedule.pack(side=BOTTOM, padx=10, pady=5,
                                  fill="x")
                else:
                    schedule.pack_forget()

            checkbox = IntVar(value=bool(default_values["repeat"]))
            CTkButton(frame, height=30, width=10, text=f"{"Edit" if edit else "Add"} expense",
                      corner_radius=15, command=self.create_personal_expense(split, edit, default_values["date"], default_values["id"], user, name, creditor, debtors, checkbox, date, time, repeat, currency, amounts, total)).pack(side=BOTTOM, pady=10)
            CTkCheckBox(frame, height=5, font=("Arial", 18), border_width=2, corner_radius=15, text="Schedule", variable=checkbox, command=toggle).pack(
                anchor="sw", pady=10, padx=15)
            split_options(default_values["debtors"][0] if len(
                default_values["debtors"]) == 1 else "both")
            split_types(default_split)
            toggle()

            frame.pack(expand=True, pady=20, padx=20)
        return f

    def create_personal_expense(self, split_type_entry, edit, prev_date, unique_id, user: User, name_entry, creditor_entry, debtors_entry, schedule_entry, date_entry, time_entry, repeat_entry, currency_entry, amount_entry, total_entry):
        def f():
            name = name_entry.get()
            if not name:
                self.show_message("Enter a desctription.")
                return
            currency = currency_entry.get()
            if currency not in self.user.currency.currencies:
                self.show_message("Invalid currency.")
                return
            debtors = None
            amounts = None
            total = None
            creditor = self.user.id if creditor_entry.get() == "You" else user.id
            try:
                amounts = [float(entry.get()) if entry.get()
                           else 0.0 for entry in amount_entry]
                total = float(total_entry.get()) if total_entry.get() else 0.0
            except ValueError:
                self.show_message("Invalid amount.")
                return
            match debtors_entry.get():
                case "You":
                    debtors = [self.user.id]
                    amounts = [str(round(total, 2))]
                case "both":
                    debtors = [self.user.id, user.id]
                    match split_type_entry.get():
                        case "equally":
                            amounts = [str(round(total/2, 2))] * 2
                        case "by ratio":
                            s = sum(amounts)
                            if not s:
                                self.show_message("Invalid ratio.")
                                return
                            amounts = [str(round(r*total/s, 2))
                                       for r in amounts]
                        case _:
                            amounts = [str(round(amnt, 2)) for amnt in amounts]
                case _:
                    debtors = [user.id]
                    try:
                        amounts = [str(float(total_entry.get()))]
                    except ValueError:
                        self.show_message("Total amount can not be zero.")
                        return

            if creditor in debtors:
                if len(debtors) == 1:
                    self.show_message("Invalid input")
                    return
                amounts.pop(debtors.index(creditor))
                debtors.remove(creditor)

            debtors = [debtors[i]
                       for i in range(len(debtors)) if float(amounts[i])]
            amounts = [amnt for amnt in amounts if float(amnt)]

            if not debtors:
                self.show_message("Select debtor")
                return

            date, repeat = None, None
            if schedule_entry.get():
                d = date_entry.get().replace(".", "-")
                t = time_entry.get()
                d = "20"[:10-len(d)] + d
                t += "12:00:00.100000"[len(t):]
                try:
                    date = str(dt.strptime(f"{d} {t}", '%Y-%m-%d %H:%M:%S.%f'))
                except ValueError:
                    self.show_message("Invalid date")
                    return
                repeat = repeat_entry.get() if repeat_entry.get() != "none" else None
            else:
                date = prev_date
                repeat = None

            new_transaction = {
                "id": unique_id,
                "name": name,
                "amounts": amounts,
                "debtors": debtors,
                "creditor": creditor,
                "currency": currency,
                "date": date,
                "repeat": repeat
            }

            if edit:
                self.ref.delete("transactions", new_transaction["id"])
            else:
                self.user.people[user.id]["transactions"].append(
                    new_transaction["id"])
                user.people[self.user.id]["transactions"].append(
                    new_transaction["id"])
                self.ref.modify("users", self.user.id,
                                "people", self.user.people)
                self.ref.modify("users", user.id, "people", user.people)
            self.ref.insert("transactions", [new_transaction])

            self.ref.tables["transactions"].get[new_transaction["id"]
                                                ] = new_transaction

            self.close_popups()
            self.refresh(self.people.button_handler(user.id))

        return f

    def delete_expense(self, owner, id):
        def f():
            self.close_popups()
            self.ref.delete("transactions", id)
            self.ref.tables["transactions"].get.pop(id)
            if isinstance(owner, User):
                self.ref.tables["users"].get[owner.id]["people"][self.user.id]["transactions"].remove(
                    id)
                self.ref.tables["users"].get[self.user.id]["people"][owner.id]["transactions"].remove(
                    id)
                self.ref.modify("users", owner.id, "people",
                                self.ref.tables["users"].get[owner.id]["people"])
                self.ref.modify("users", self.user.id, "people",
                                self.ref.tables["users"].get[self.user.id]["people"])
                self.refresh(self.people.button_handler(owner.id))
            else:
                self.ref.tables["groups"].get[owner.id]["transactions"].remove(
                    id)
                self.ref.modify("groups", owner.id, "transactions",
                                self.ref.tables["groups"].get[owner.id]["transactions"])
                self.refresh(self.groups.button_handler(owner.id))
        return f

    def new_group_expense(self, group: Group, prefilled=False):
        n = len(group.members)
        default_values = prefilled
        default_tab = "Unequally"
        edit = True
        if not default_values:
            edit = False
            default_tab = "Equally"
            default_values = {
                "id": str(uuid1()),
                "name": "",
                "amounts": [""] * n,
                "debtors": group.members,
                "creditor": self.user.id,
                "currency": self.user.currency.default,
                "date": str(dt.now()),
                "repeat": "",
            }
        if not default_values["id"]:
            edit = False
            default_values["id"] = str(uuid1())
        if not default_values["date"]:
            default_values["date"] = str(dt.now())

        def f():
            if n < 2:
                self.show_message("There's no other members in this group.")
                return
            self.close_popups()
            win = CTkToplevel(self)
            win.title("NewExpense")
            win.geometry(f"{self.scr_w//4}x{int(0.8*self.scr_h)
                                            }+{int(0.4*self.scr_w)}+{self.scr_h//8}")
            win.lift()
            win.focus()
            win.attributes("-topmost", True)
            self.popup_stack.append(win)
            frame = Frame(win, corner_radius=20)

            widget = Frame(frame, height=10, fg_color="transparent")
            widget.pack(pady=10, padx=15, fill="x")
            CTkLabel(widget, text=f"{"Edit" if edit else "Add"} expense", font=(
                "Arial Bold", 25), text_color="gray40").pack(side=LEFT)
            if edit:
                CTkButton(widget, text="Delete", text_color="red3", fg_color="transparent", height=20, hover_color="gray70",
                          width=35, border_width=2, border_color="red3", corner_radius=10, command=self.delete_expense(group, default_values["id"])).pack(side=RIGHT)

            entry = Frame(frame, height=50, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=15, fill="x")
            CTkLabel(entry, width=10, text="Description", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            name = CTkEntry(entry, height=30, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            name.pack(padx=5, fill="x")
            name.insert(0, default_values["name"])

            entry = Frame(frame, height=10, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=5, fill="x")
            widget = CTkLabel(entry, text="Paid by", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)
            us_names = {item["id"]: item["name"]
                        for item in self.ref.tables["users"].get.values()}
            creditor = CTkOptionMenu(entry, height=25, width=70, values=[f"{us_names[id]} ({id})" for id in group.members],
                                     font=("Arial", 16, "bold"))
            creditor.pack(side=LEFT, padx=5)
            creditor.set(f"{us_names[default_values["creditor"]]} ({
                         default_values["creditor"]})")
            widget = CTkLabel(entry, text="in", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)
            currency = CTkComboBox(entry, height=25, width=70, values=self.user.currency.currencies,
                                   font=("Arial", 16))
            currency.pack(side=LEFT, padx=5)
            currency.set(default_values["currency"])

            schedule = Frame(frame, height=10, fg_color="transparent")
            widget = Frame(schedule, height=10, width=10,
                           fg_color="transparent")
            widget.pack(anchor="nw")
            CTkLabel(widget, width=10, text="Date", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            date = CTkEntry(widget, height=30, width=100, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            date.pack(side=LEFT, padx=5, fill="x", expand=True)
            date.insert(0, default_values["date"][:10].replace("-", "."))
            CTkLabel(widget, width=10, text="Time", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            time = CTkEntry(widget, height=30, width=60, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            time.pack(side=LEFT, padx=5, fill="x", expand=True)
            time.insert(0, default_values["date"][11:16])
            widget = Frame(schedule, height=10, width=10,
                           fg_color="transparent")
            widget.pack(anchor="nw", pady=5)
            repeat = CTkComboBox(widget, height=25, width=100, values=["none", "weekly", "daily", "monthly", "yearly"],
                                 font=("Arial", 16, "bold"))
            CTkLabel(widget, width=10, text="Repeat", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            repeat.pack(side=LEFT, padx=5)
            repeat.set(default_values["repeat"]
                       if default_values["repeat"] else "none")

            def toggle():
                if checkbox.get():
                    schedule.pack(anchor="nw", padx=10, pady=5,
                                  fill="x", side=TOP)
                else:
                    schedule.pack_forget()

            checkbox = IntVar(value=bool(default_values["repeat"]))
            CTkCheckBox(frame, height=5, font=("Arial", 18), border_width=2, corner_radius=15, text="Schedule", variable=checkbox, command=toggle).pack(
                anchor="nw", pady=10, padx=15)
            toggle()

            tabs = CTkTabview(frame, height=100, width=100, corner_radius=10)
            tabs.pack(fill="x", side=BOTTOM, padx=10, pady=10)

            tabs.add("Equally")
            tabs.add("Unequally")
            tabs.add("By ratio")

            tabs.set(default_tab)

            eq = CTkScrollableFrame(tabs.tab("Equally"), fg_color="transparent",
                                    scrollbar_button_color="gray70", scrollbar_button_hover_color="gray75")
            uneq = CTkScrollableFrame(tabs.tab("Unequally"), fg_color="transparent",
                                      scrollbar_button_color="gray70", scrollbar_button_hover_color="gray75")
            br = CTkScrollableFrame(tabs.tab("By ratio"), fg_color="transparent",
                                    scrollbar_button_color="gray70", scrollbar_button_hover_color="gray75")

            # Equally
            widget = Frame(tabs.tab("Equally"), fg_color="transparent")
            widget.pack(side=TOP, fill="x")
            CTkLabel(widget, width=10, font=(
                "Arial", 16), text="Total amount", text_color="gray50").pack(side=LEFT, padx=5)
            amount = CTkEntry(widget, height=25, border_width=0, width=100,
                              fg_color="gray70", font=("Arial", 14))
            amount.pack(side=RIGHT, fill="x", padx=3)
            debtors = {id: StringVar(value="") for id in group.members}
            for id in group.members:
                CTkCheckBox(eq, height=5, font=("Arial", 16), border_width=2, corner_radius=15, text=f"{us_names[id]} ({id})", variable=debtors[id], onvalue=id, offvalue="").pack(
                    anchor="nw", pady=5)
            CTkButton(tabs.tab("Equally"), height=30, width=10, text=f"{"Edit" if edit else "Add"} expense", command=self.create_group_expense("eq", edit, default_values["date"], default_values["id"], group, name, creditor, debtors, checkbox, date, time, repeat, currency, amount),
                      corner_radius=15).pack(side=BOTTOM, pady=0)
            eq.pack(fill="both", padx=0, pady=0)

            # By ratio
            widget = Frame(tabs.tab("By ratio"), fg_color="transparent")
            widget.pack(side=TOP, fill="x")
            CTkLabel(widget, width=10, font=(
                "Arial", 16), text="Total amount", text_color="gray50").pack(side=LEFT, padx=5)
            amount = CTkEntry(widget, height=25, border_width=0, width=100,
                              fg_color="gray70", font=("Arial", 14))
            amount.pack(side=RIGHT, fill="x", padx=3)
            debtors = {id: None for id in group.members}
            for id in group.members:
                widget = Frame(br, fg_color="transparent")
                widget.pack(side=TOP, fill="x", pady=2)
                CTkLabel(widget, width=10, font=(
                    "Arial", 16), text=f"{us_names[id]} ({id})").pack(side=LEFT, padx=0)
                debtors[id] = CTkEntry(widget, height=25, border_width=0, width=50,
                                       fg_color="gray70", font=("Arial", 14))
                debtors[id].pack(side=RIGHT, fill="x")
            CTkButton(tabs.tab("By ratio"), height=30, width=10, text=f"{"Edit" if edit else "Add"} expense", command=self.create_group_expense("br", edit, default_values["date"], default_values["id"], group, name, creditor, debtors, checkbox, date, time, repeat, currency, amount),
                      corner_radius=15).pack(side=BOTTOM, pady=0)
            br.pack(fill="both", padx=0, pady=0)

            # Unequally
            debtors = {id: None for id in group.members}
            for id in group.members:
                widget = Frame(uneq, fg_color="transparent")
                widget.pack(side=TOP, fill="x", pady=2)
                CTkLabel(widget, width=10, font=(
                    "Arial", 16), text=f"{us_names[id]} ({id})").pack(side=LEFT, padx=0)
                debtors[id] = CTkEntry(widget, height=25, border_width=0, width=80,
                                       fg_color="gray70", font=("Arial", 14))
                debtors[id].pack(side=RIGHT, fill="x")
                debtors[id].insert(0, default_values["amounts"]
                                   [default_values["debtors"].index(id)] if id in default_values["debtors"] else "")

            CTkButton(tabs.tab("Unequally"), height=30, width=10, text=f"{"Edit" if edit else "Add"} expense", command=self.create_group_expense("uneq", edit, default_values["date"], default_values["id"], group, name, creditor, debtors, checkbox, date, time, repeat, currency),
                      corner_radius=15).pack(side=BOTTOM, pady=0)
            uneq.pack(fill="both", padx=0, pady=0)

            frame.pack(expand=True, pady=20, padx=20)

        return f

    def create_group_expense(self, split_type, edit, prev_date, unique_id, group: Group, name_entry, creditor_entry, debtors_entry, schedule_entry, date_entry, time_entry, repeat_entry, currency_entry, amount_entry=None):
        def f():
            name = name_entry.get()
            if not name:
                self.show_message("Enter a desctription.")
                return
            try:
                amount = float(amount_entry.get()) if amount_entry else 0.0
            except ValueError:
                self.show_message("Invalid amount.")
                return
            currency = currency_entry.get()
            if currency not in self.user.currency.currencies:
                self.show_message("Invalid currency.")
                return
            creditor = creditor_entry.get().split()[1][1:-1]
            debtors = [id for id, entry in debtors_entry.items()
                       if entry.get()]
            amounts = None

            match split_type:
                case "eq":
                    amounts = [str(round(amount/len(debtors), 2))
                               for _ in debtors]
                case "br":
                    ratio = [float(entry.get())
                             for _, entry in debtors_entry.items() if entry.get()]
                    s = sum(ratio)
                    amounts = [str(round(amount*(r/s), 2)) for r in ratio]
                case _:
                    amounts = [str(round(float(entry.get()), 2))
                               for _, entry in debtors_entry.items() if entry.get()]
            if creditor in debtors:
                if len(debtors) == 1:
                    self.show_message("Invalid input")
                    return
                amounts.pop(debtors.index(creditor))
                debtors.remove(creditor)

            debtors = [debtors[i]
                       for i in range(len(debtors)) if float(amounts[i])]
            amounts = [amnt for amnt in amounts if float(amnt)]

            if not debtors:
                self.show_message("Select debtors")
                return

            date, repeat = None, None
            if schedule_entry.get():
                d = date_entry.get().replace(".", "-")
                t = time_entry.get()
                d = "20"[:10-len(d)] + d
                t += "12:00:00.100000"[len(t):]
                try:
                    date = str(dt.strptime(f"{d} {t}", '%Y-%m-%d %H:%M:%S.%f'))
                except ValueError:
                    self.show_message("Invalid date")
                    return
                repeat = repeat_entry.get() if repeat_entry.get() != "none" else None
            else:
                date = prev_date
                repeat = None

            new_transaction = {
                "id": unique_id,
                "name": name,
                "amounts": amounts,
                "debtors": debtors,
                "creditor": creditor,
                "currency": currency,
                "date": date,
                "repeat": repeat
            }

            if edit:
                self.ref.delete("transactions", new_transaction["id"])
            else:
                self.ref.add("groups", group.id, "transactions",
                             new_transaction["id"])
            self.ref.insert("transactions", [new_transaction])

            self.ref.tables["transactions"].get[new_transaction["id"]
                                                ] = new_transaction

            self.close_popups()
            self.refresh(self.groups.button_handler(group.id))

        return f

    def simplify(self, group: Group):
        network = Network(group.members.copy())
        for expense in group.passed:
            for i in range(len(expense["debtors"])):
                amount = self.user.currency.convert(
                    float(expense["amounts"][i]), expense["currency"])
                group.total += amount
                network.add_debt(
                    expense["debtors"][i], expense["creditor"], amount)
        group.balance = network.balance[self.user.id]
        return network.settled_up()

    def close_popups(self):
        for win in self.popup_stack:
            win.destroy()
        self.popup_stack = []

    def invite_action(self, invite, accept):
        def f():
            if accept:
                self.ref.add("groups", invite[0], "members", self.user.id)
                self.ref.tables["groups"].get[invite[0]
                                              ]["members"].append(self.user.id)
                self.ref.add("users", self.user.id, "groups", invite[0])
                self.ref.tables["users"].get[self.user.id]["groups"].append(
                    invite[0])
                self.ref.pop("users", self.ref.tables["groups"].get[invite[0]]["members"][
                             0], "invites", [invite[0], invite[1], self.user.id])
                self.ref.tables["users"].get[self.ref.tables["groups"].get[invite[0]]
                                             ["members"][0]]["invites"].remove([invite[0], invite[1], self.user.id])
            else:
                self.ref.pop("users", invite[2], "invites", [
                             invite[0], invite[1], None])
                self.ref.tables["users"].get[invite[2]]["invites"].remove(
                    [invite[0], invite[1], None])

            self.ref.pop("users", self.user.id, "invites", invite)
            self.ref.tables["users"].get[self.user.id]["invites"].remove(
                invite)

            self.refresh(call=self.groups.button_handler(
                invite[0]) if accept else None)
        return f

    def new_group(self):
        self.close_popups()
        win = CTkToplevel(self)
        win.title("NewGroup")
        win.geometry(f"{self.scr_w//4}x{int(0.4*self.scr_h)
                                        }+{int(0.4*self.scr_w)}+{self.scr_h//4}")
        win.lift()
        win.focus()
        win.attributes("-topmost", True)
        self.popup_stack.append(win)
        frame = Frame(win, corner_radius=20, width=500, height=6000)
        frame.pack(expand=True, pady=20, padx=20)

        widget = CTkLabel(frame, text="New group", font=(
            "Arial Bold", 25), text_color="gray40")
        widget.pack(padx=15, pady=10, anchor="nw")

        entry = Frame(frame, height=50, fg_color="transparent")
        entry.pack(anchor="nw", padx=10, pady=15, fill="x")
        widget = CTkLabel(entry, text="Group name", font=("Arial", 18))
        widget.pack(side=LEFT, padx=5)
        name = CTkEntry(entry, height=30, border_width=0,
                        fg_color="gray90", font=("Arial", 16, "bold"))
        name.pack(side=RIGHT, padx=5, fill="x")

        entry = Frame(frame, height=100, fg_color="transparent")
        entry.pack(anchor="nw", padx=10, pady=0, fill="x")
        widget = CTkLabel(entry, text="Members", font=("Arial", 18))
        widget.pack(side=LEFT, padx=5)
        members = CTkEntry(entry, height=30, border_width=0,
                           fg_color="gray90", font=("Arial", 16))
        members.pack(side=BOTTOM, padx=5, fill="x")

        widget = Frame(frame, height=100, fg_color="transparent")
        widget.pack(anchor="nw", padx=10, pady=0, fill="x")
        CTkLabel(widget, text="Use comma to seperate usernames.\nYou can invite members later.\n\n", font=(
            "Arial", 12, "bold"), text_color="gray60", justify="left", wraplength=250).pack(anchor="sw", padx=6, pady=5)
        CTkButton(frame, text="Creat group", width=80, font=("Arial", 18, "bold"),
                  height=30, corner_radius=15, command=self.create_group(name, members)).pack(side=BOTTOM, pady=10)

    def create_group(self, name, members):
        def f():
            group_name = name.get()
            group_members = []

            for id in members.get().split(","):
                id = id.strip()
                if id not in self.ref.tables["users"].get or id in group_members or id == self.user.id:
                    continue
                group_members.append(id)

            if not group_name:
                self.show_message("Enter group name.")
                return

            group_id = str(uuid1())
            new_group = {
                "id": group_id,
                "name": group_name,
                "avatar": choice(config["avatars"]["groups"]),
                "members": [self.user.id],
                "transactions": []
            }
            self.ref.insert("groups", [new_group])
            self.ref.add("users", self.user.id, "groups", group_id)
            self.ref.tables["groups"].get[group_id] = new_group
            self.ref.tables["users"].get[self.user.id]["groups"].append(
                group_id)
            self.invite(group_id, group_members)
            self.refresh(call=self.groups.button_handler(group_id))

        return f

    def new_friend(self, preset=""):
        self.close_popups()
        win = CTkToplevel(self)
        win.title("NewFriends")
        win.geometry(f"{self.scr_w//4}x{int(0.4*self.scr_h)
                                        }+{int(0.4*self.scr_w)}+{self.scr_h//4}")
        win.lift()
        win.focus()
        win.attributes("-topmost", True)
        self.popup_stack.append(win)
        frame = Frame(win, corner_radius=20, width=500, height=6000)
        frame.pack(expand=True, pady=20, padx=20)

        widget = CTkLabel(frame, text=f"Add friends", font=(
            "Arial Bold", 25), text_color="gray40")
        widget.pack(padx=15, pady=10, anchor="nw")

        entry = Frame(frame, height=100, fg_color="transparent")
        entry.pack(anchor="nw", padx=10, pady=2, fill="x")
        widget = CTkLabel(
            entry, text="Usernames", font=("Arial", 18))
        widget.pack(side=LEFT, padx=5)

        entry = Frame(frame, height=100, fg_color="transparent")
        entry.pack(anchor="nw", padx=10, pady=0, fill="x")
        new_friends = CTkEntry(entry, height=30, border_width=0,
                               fg_color="gray90", font=("Arial", 16))
        new_friends.pack(side=BOTTOM, padx=5, fill="x")
        new_friends.insert(0, preset)

        widget = Frame(frame, height=100, fg_color="transparent")
        widget.pack(anchor="nw", padx=10, pady=0, fill="x")
        CTkLabel(widget, text="Use comma to seperate usernames.\n\n", font=(
            "Arial", 12, "bold"), text_color="gray60", justify="left", wraplength=250).pack(anchor="sw", padx=6, pady=5)
        CTkButton(frame, text="Add friends", width=80, font=("Arial", 18, "bold"),
                  height=30, corner_radius=15, command=self.create_friends(new_friends)).pack(side=BOTTOM, pady=10)

    def create_friends(self, entry):
        def f():
            new_friends = []
            for id in entry.get().split(","):
                id = id.strip()
                if id not in self.ref.tables["users"].get or id in new_friends or id in self.user.people or id == self.user.id:
                    continue
                new_friends.insert(0, id)
            me = {
                "name": self.user.name,
                "transactions": [],
            }

            for fr in new_friends:
                self.ref.tables["users"].get[self.user.id]["people"][fr] = {
                    "name": self.ref.tables["users"].get[fr]["name"],
                    "transactions": [],
                }
                self.ref.tables["users"].get[fr]["people"][self.user.id] = me
                self.ref.modify("users", fr, "people",
                                self.ref.tables["users"].get[fr]["people"])
            self.ref.modify("users", self.user.id, "people",
                            self.ref.tables["users"].get[self.user.id]["people"])

            self.close_popups()
            self.refresh()
        return f

    def new_invite(self, group: Group):
        def f():
            self.close_popups()
            win = CTkToplevel(self)
            win.title("InviteUsers")
            win.geometry(f"{self.scr_w//4}x{int(0.4*self.scr_h)
                                            }+{int(0.4*self.scr_w)}+{self.scr_h//4}")
            win.lift()
            win.focus()
            win.attributes("-topmost", True)
            self.popup_stack.append(win)
            frame = Frame(win, corner_radius=20, width=500, height=6000)
            frame.pack(expand=True, pady=20, padx=20)

            widget = CTkLabel(frame, text=f"Invite to {group.name}", font=(
                "Arial Bold", 25), text_color="gray40")
            widget.pack(padx=15, pady=10, anchor="nw")

            entry = Frame(frame, height=100, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=2, fill="x")
            widget = CTkLabel(
                entry, text="Usernames", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)

            entry = Frame(frame, height=100, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=0, fill="x")
            members = CTkEntry(entry, height=30, border_width=0,
                               fg_color="gray90", font=("Arial", 16))
            members.pack(side=BOTTOM, padx=5, fill="x")

            widget = Frame(frame, height=100, fg_color="transparent")
            widget.pack(anchor="nw", padx=10, pady=0, fill="x")
            CTkLabel(widget, text="Use comma to seperate usernames.\n\n", font=(
                "Arial", 12, "bold"), text_color="gray60", justify="left", wraplength=250).pack(anchor="sw", padx=6, pady=5)
            CTkButton(frame, text="Invite", width=80, font=("Arial", 18, "bold"),
                      height=30, corner_radius=15, command=self.create_inivte(group, members)).pack(side=BOTTOM, pady=10)

        return f

    def create_inivte(self, group: Group, entry):
        def f():
            new_members = []
            for id in entry.get().split(","):
                id = id.strip()
                if id not in self.ref.tables["users"].get or id in group.members or id in new_members:
                    continue
                new_members.append(id)
            self.invite(group.id, new_members)
            self.refresh(call=self.groups.button_handler(group.id))

        return f

    def invite(self, group_id, group_members):
        for user_id in group_members:
            now = str(dt.now())
            self.ref.add("users", self.user.id, "invites", [
                group_id, now, user_id])
            self.ref.tables["users"].get[self.user.id]["invites"].append(
                [group_id, now, user_id])
            self.ref.add("users", user_id, "invites", [
                group_id, now, None])
            self.ref.tables["users"].get[user_id]["invites"].append(
                [group_id, now, None])

            self.side_bar.default_tab = "invites"
        self.close_popups()

    def refresh(self, call=None):
        self.ref.reload()
        self.root.destroy()
        self.last_tab = self.side_bar.default_tab
        self.load(self.user.id)
        if call:
            call()

    @ staticmethod
    def sentence(task, input):
        if task == "group":
            output = []
            for item in input[:-1]:
                output.append(item)
            return (", ".join(output) + f" and {input[-1]}") if output else input[-1]
