from json import load, dump
from interface import *
from user import User, Group
from alg import Network
from server import Data
from uuid import uuid1, uuid4
from datetime import datetime as dt
from datetime import timedelta
from copy import deepcopy
from io import BytesIO
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

config = {
    "avatars": {
        "people": [(f"avatars/male{i}.png", f"avatars/female{i}.png") for i in range(8)],
        "unknown": "avatars/unknown.png"
    },
    "icons": {
        "add-member": "icons/add-member.png",
        "edit-name": "icons/edit-name.png",
        "password": "icons/password.png",
        "logout": "icons/logout.png"
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
        self.req = Data()
        self.status_code = True
        self.popup_stack = []
        return

    def load(self, id, data):
        self.req.id = id
        self.data = data
        self.user = User(id, data)
        config["app"]["sidepanels"]["home"]["label"] = f"Welcome, {
            self.user.name}"
        data["users"][self.user.id]["name"] = "You"
        groups_list = [Group(id, data) for id in self.user.groups]
        people_list = [User(id, data) for id in self.user.people]

        self.root = Frame(self)
        self.side_bar = SideBar(
            self.root, config["app"]["sidebar"], default_tab=self.last_tab)

        objects = {
            "name": ["1", "2"],
            "label": ["Title1", "Title2"],
            "button": [("View", 45, (None, None), None), ("View", 45, (None, None), None)],
            "text": [[], []],
        }
        self.home = FrameList(self.side_bar.panels["home"], config["app"]
                              ["sidepanels"]["home"], objects, height=80, width=320)

        balances = {}
        for gr in groups_list:
            balances[gr.id] = self.simplify(gr)
        objects = {
            "name": [group.id for group in groups_list],
            "label": [group.name for group in groups_list],
            "button": [("View", 45, (None, None), None) for _ in groups_list],
            "text": [[(f"Net balance: {gr.balance}", "red3" if gr.balance < 0 else "green" if gr.balance > 0 else "blue")] for gr in groups_list]
        }
        self.groups = FrameList(self.side_bar.panels["groups"], config["app"]
                                ["sidepanels"]["groups"], objects, height=80, command=self.new_group, width=320)

        objects = {
            "name": [user.id for user in people_list],
            "label": [user.name for user in people_list],
            "button": [("View", 45, (None, None), None) for _ in people_list],
            "text": [(("You are owed 0.2$", "green"), ("And you owe 0.8$", "red3"), ("Net balance: -0.6$", "blue")), (("You are owed 1.3$", "green"), ("And you owe 0.9$", "red3"), ("Net balance: +0.4$", "blue"))],
        }
        self.people = FrameList(self.side_bar.panels["people"], config["app"]
                                ["sidepanels"]["people"], objects, height=80, command=self.new_friend, width=320)

        i = len(self.user.invites)
        while i:
            i -= 1
            if self.user.invites[i][0] not in self.data["groups"]:
                self.user.invites.pop(i)

        objects = {
            "name": [invite[0]+str(invite[2]) for invite in self.user.invites],
            "label": [f"{self.data["users"][self.data["groups"][invite[0]]["members"][0]]["name"]} invited {"you" if not invite[2] else self.data["users"][invite[2]]["name"]} to {self.data["groups"][invite[0]]["name"]}" for invite in self.user.invites],
            "button": [("Delete", 53, ("red3", "red4"), self.invite_action(invite, False)) if invite[2] else ("Accept", 56, (None, None), self.invite_action(invite, True)) for invite in self.user.invites],
            "text": [((invite[1][:16], "gray50"),) for invite in self.user.invites]
        }
        self.invites = FrameList(self.side_bar.panels["invites"], config["app"]
                                 ["sidepanels"]["invites"], objects, height=50, font=("Arial", 14), font_dif=2, width=320)

        self.settings = Frame(
            self.side_bar.panels["setting"], height=1000, width=330, fg_color="transparent")
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
                  font=("Arial", 18), text_color="black", fg_color="transparent", hover=False).place(x=15, y=100)
        CTkButton(self.settings, image=Frame.picture(config["icons"]["logout"], (20, 20)), text="Logout", compound=RIGHT, width=10, height=10,
                  font=("Arial", 18), text_color="black", fg_color="transparent", hover=False).place(x=220, y=100)
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
            self.data["groups"][gr.id]["transactions"] = gr.passed + \
                gr.scheduled

            options = {
                "label": [data["users"][id]["name"] for id in gr.members],
                "color": ["gray60" if i else "gray30" for i in range(len(gr.members))],
                "command": [None] * len(gr.members),
            }
            if gr.members[0] == self.user.id:
                options["label"].append(None)
                options["color"].append(Frame.picture(
                    config["icons"]["add-member"], (20, 20)))
                options["command"].append(self.new_invite(gr))
            buttons = {
                "label": ["New expense", "Stats"],
                "color": [(None, None), (None, None)],
                "command": [self.new_group_expense(gr), self.manage_group(gr)],
            }
            main_panel = MainPanel(self.root)
            main_panel.add_title(text=gr.name, avatar=gr.avatar)
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
                "label": "Expenses" if gr.transactions else "No expenses yet",
                "button": None,
                "text": None,
            }
            objects = {
                "name": [tr["id"] for tr in gr.passed],
                "label": [tr["name"] for tr in gr.passed],
                "button": [(f"{sum([float(amnt) for amnt in tr["amounts"]])} {tr["currency"]}", 45, ("gray50", "gray60"), None) for tr in gr.passed],
                "text": [[(f"{data["users"][tr["creditor"]]["name"]} lent {App.sentence("group", [self.data["users"][debtor]["name"] for debtor in tr["debtors"]])}", "black"), (tr["date"][:16], "gray50")] for tr in gr.passed],
            }
            commands = {
                tr["id"]: self.new_group_expense(gr, tr) for tr in gr.passed}
            FrameList(recent, header, objects, commands, width=10,
                      height=70, title_color="gray50")

            simlified = balances[gr.id]
            header = {
                "height": 30,
                "font": ("Arial Bold", 18),
                "label": " Summary",
                "button": None,
                "text": None,
            }
            objects = {
                "name": [str(i) for i in range(len(simlified))],
                "label": [f"{data["users"][debtor]["name"]} {"owes" if debtor != self.user.id else "owe"} {data["users"][creditor]["name"]} {amount} {self.user.currency.default}" for debtor, creditor, amount in simlified],
                "button": [("Settle-up", 10, ("gray50", "gray60"), None) if debtor == self.user.id else None for debtor, _, _ in simlified],
                "text": [[]]*len(simlified),
                "color": ["red3" if self.user.id == debtor else "green" if self.user.id == creditor else "black" for debtor, creditor, _ in simlified]
            }
            settled = {str(i): self.new_group_expense(gr, {"id": None, "name": "Settled up", "amounts": [str(simlified[i][2])], "creditor": self.user.id, "debtors": [
                simlified[i][1]], "currency": self.user.currency.default, "date": None, "repeat": False}) for i in range(len(simlified)) if simlified[i][0] == self.user.id}
            FrameList(summary, header, objects, width=30, min_height=True, commands=settled,
                      height=25, title_color="gray50", font=("Arial", 14))
            recent.pack(side=LEFT, fill="both", expand=True)
            summary.pack(side=RIGHT, fill="both", expand=True)

        self.groups.add_link(links)

        links = {"empty": empty}
        for us in people_list:
            passed, us.scheduled = [], []
            now = dt.now()
            for tr in self.user.people[us.id]["transactions"]:
                temp = deepcopy(tr)
                if dt.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f') < now:
                    freq = temp["repeat"]
                    temp["repeat"] = False
                    passed.append(deepcopy(temp))
                    while freq:
                        temp["id"] = str(uuid1())
                        new_date = dt.strptime(
                            temp["date"], '%Y-%m-%d %H:%M:%S.%f')
                        new_date += timedelta(days=1) if freq == "daily" else timedelta(
                            days=7) if freq == "weekly" else timedelta(days=30) if freq == "monthly" else timedelta(days=365)
                        temp["date"] = new_date.strftime(
                            '%Y-%m-%d %H:%M:%S.%f')
                        if new_date < now:
                            passed.append(deepcopy(temp))
                        else:
                            temp["repeat"] = freq
                            us.scheduled.append(deepcopy(temp))
                            freq = False
                else:
                    us.scheduled.append(deepcopy(temp))

            passed.sort(key=lambda tr: dt.strptime(
                tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
            us.scheduled.sort(key=lambda tr: dt.strptime(
                tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
            self.data["users"][self.user.id]["people"][us.id]["transactions"] = passed + us.scheduled
            self.data["users"][us.id]["people"][self.user.id]["transactions"] = passed + us.scheduled

            buttons = {
                "label": ["New Expense", f"Delete {us.name}"],
                "color": [(None, None), ("red3", "red4")],
                "command": [self.new_personal_expense(us), None]
            }
            balance = 0
            for expense in passed:
                if us.id == expense["creditor"]:
                    balance -= self.user.currency.convert(
                        expense["amounts"][0], expense["currency"])
                else:
                    balance += self.user.currency.convert(
                        expense["amounts"][0], expense["currency"])
            debtor = balance < 0
            options = {
                "label": [f"{"You" if debtor else us.name} {"owe" if debtor else "owes"} {"You" if not debtor else us.name} {abs(balance)} {self.user.currency.default}"],
                "color": ["gray60"],
                "command": [None],
            }
            main_panel = MainPanel(self.root)
            main_panel.add_title(text=us.name, avatar=us.avatar)
            main_panel.add_button(buttons)
            if balance:
                main_panel.add_options(
                    options, color="red3" if debtor else "green")
            main_panel.set_body()
            links[us.id] = main_panel
            hist = Frame(main_panel.body,
                         fg_color="gray83", corner_radius=15)
            header = {
                "height": 30,
                "font": ("Arial Bold", 18),
                "label": "Expenses" if passed else "No expenses yet",
                "button": None,
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
            FrameList(hist, header, objects, width=10, commands=commands,
                      height=70, title_color="gray50")
            hist.pack(side=LEFT, fill="both", expand=True)

        self.people.add_link(links)
        self.groups.button_handler("empty")()

        self.root.pack(fill="both", expand=True)
        return

    def set_sefault_currency(self, choice):
        self.user.currency.default = choice
        self.data["users"][self.user.id]["settings"]["default-currency"] = choice
        self.refresh(self.groups.button_handler("empty"))

    def choose_avatar(self, id, owner_type):
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

            def select_avatar(avatar):
                def f():
                    if owner_type == "user":
                        self.data["users"][id]["avatar"] = avatar
                        self.close_popups()
                        self.refresh(self.people.button_handler("empty"))
                return f

            frame = Frame(win, width=300, height=400, corner_radius=20)
            CTkLabel(frame, text="Choose your preferred avatar", font=(
                "Arial", 18, "bold"), text_color="gray50").pack(pady=10)
            for i in range(4):
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
                CTkLabel(item, height=30, text=self.data["users"][id]["name"], font=(
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
                CTkLabel(item, height=30, text=self.data["users"][id]["name"], font=(
                    "Arial", 16)).pack(side=LEFT, padx=15)
                CTkButton(item, height=20, width=20, corner_radius=10, text=f"{total} {self.user.currency.default}", border_width=0,
                          hover_color="gray80", fg_color="transparent", font=("Arial", 12, "bold"), text_color="gray40").pack(side=RIGHT, padx=5, pady=5)
                item.pack(side=TOP, fill="x", padx=5, pady=5)

            if total:
                fig = network.visualize(
                    {member: User(
                        member, self.data).avatar for member in group.members},
                    {member: User(
                        member, self.data).name for member in group.members},
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
            for id in group.members:
                self.data["users"][id]["groups"].remove(group.id)
            del self.data["groups"][group.id]
            self.close_popups()
            self.refresh(self.groups.button_handler("empty"))

        return f

    def rename_group(self, group: Group, new_name_entry):
        def f():
            new_name = new_name_entry.get()
            if not new_name:
                print("Enter group name")
                return
            group.name = new_name
            self.data["groups"][group.id]["name"] = group.name
            self.close_popups()
            self.refresh(self.groups.button_handler(group.id))

        return f

    def rename_user(self, new_name_entry, new_id_entry):
        def f():
            new_name = new_name_entry.get()
            new_id = new_id_entry.get()
            if not new_name:
                print("Enter name.")
                return
            if not new_id.startswith("@"):
                print("Add @ befor your username.")
                return
            new_id = new_id[1:].strip()
            if len(new_id) < 4:
                print("Username is too short.")
                return

            if not self.user.id == new_id or not self.user.name == new_name:
                self.user.name = new_name

                for group in self.user.groups:
                    self.data["groups"][group]["members"].insert(
                        self.data["groups"][group]["members"].index(self.user.id), new_id)
                    self.data["groups"][group]["members"].remove(self.user.id)
                    for tr in self.data["groups"][group]["transactions"]:
                        if tr["creditor"] == self.user.id:
                            tr["creditor"] = new_id
                        if self.user.id in tr["debtors"]:
                            tr["debtors"].insert(
                                tr["debtors"].index(self.user.id), new_id)
                            tr["debtors"].remove(self.user.id)

                for invite in self.user.invites:
                    if self.user.id in invite:
                        invite.insert(invite.index(self.user.id), new_id)
                        invite.remove(self.uder.id)

                for fr in self.user.people:
                    for tr in self.user.people[fr]["transactions"]:
                        if tr["creditor"] == self.user.id:
                            tr["creditor"] = new_id
                        if self.user.id in tr["debtors"]:
                            tr["debtors"].insert(
                                tr["debtors"].index(self.user.id), new_id)
                            tr["debtors"].remove(
                                self.user.id)

                for user in self.data["users"]:
                    if self.user.id in self.data["users"][user]["people"]:
                        for tr in self.data["users"][user]["people"][self.user.id]["transactions"]:
                            if tr["creditor"] == self.user.id:
                                tr["creditor"] = new_id
                            if self.user.id in tr["debtors"]:
                                tr["debtors"].insert(
                                    tr["debtors"].index(self.user.id), new_id)
                                tr["debtors"].remove(self.user.id)
                        self.data["users"][user]["people"][self.user.id]["name"] = new_name
                        self.data["users"][user]["people"][new_id] = self.data["users"][user]["people"].pop(
                            self.user.id)
                    for inv in self.data["users"][user]["invites"]:
                        if self.user.id in inv:
                            inv.insert(inv.index(self.user.id), new_id)
                            inv.remove(self.uder.id)

                self.data["users"][new_id] = self.data["users"].pop(
                    self.user.id)
                self.user.id = new_id
            self.close_popups()
            self.refresh(self.groups.button_handler("empty"))

        return f

    def remove_member(self, group: Group, id):
        def f():
            self.data["groups"][group.id]["members"].remove(id)
            self.data["users"][id]["groups"].remove(group.id)
            self.close_popups()
            self.refresh(self.groups.button_handler(group.id))
        return f

    def check_status(self):
        if self.status_code:
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
                "repeat": False,
            }
        if not default_values["id"]:
            edit = False
            default_values["id"] = str(uuid1())

        def f():
            self.close_popups()
            win = CTkToplevel(self)
            win.title("NewExpense")
            win.geometry(f"{self.scr_w//4}x{int(0.5*self.scr_h)
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
            CTkLabel(schedule, width=10, text="Date", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            date = CTkEntry(schedule, height=30, width=80, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            date.pack(side=LEFT, padx=5, fill="x", expand=True)
            date.insert(0, default_values["date"][2:10].replace("-", "."))
            repeat = CTkComboBox(schedule, height=25, width=100, values=["none", "weekly", "daily", "monthly", "yearly"],
                                 font=("Arial", 16, "bold"))
            repeat.pack(side=RIGHT, padx=5)
            repeat.set(default_values["repeat"]
                       if default_values["repeat"] else "none")
            CTkLabel(schedule, width=10, text="repeat", font=(
                "Arial", 18)).pack(side=RIGHT, padx=5)

            def toggle():
                if checkbox.get():
                    schedule.pack(side=BOTTOM, padx=10, pady=5,
                                  fill="x")
                else:
                    schedule.pack_forget()

            checkbox = IntVar(value=bool(default_values["repeat"]))
            CTkButton(frame, height=30, width=10, text=f"{"Edit" if edit else "Add"} expense",
                      corner_radius=15, command=self.create_personal_expense(split, default_values["date"], default_values["id"], user, name, creditor, debtors, checkbox, date, repeat, currency, amounts, total)).pack(side=BOTTOM, pady=10)
            CTkCheckBox(frame, height=5, font=("Arial", 18), border_width=2, corner_radius=15, text="Schedule", variable=checkbox, command=toggle).pack(
                anchor="sw", pady=10, padx=15)
            split_options(default_values["debtors"][0] if len(
                default_values["debtors"]) == 1 else "both")
            split_types(default_split)
            toggle()

            frame.pack(expand=True, pady=20, padx=20)
        return f

    def create_personal_expense(self, split_type_entry, prev_date, unique_id, user: User, name_entry, creditor_entry, debtors_entry, schedule_entry, date_entry, repeat_entry, currency_entry, amount_entry, total_entry):
        def f():
            name = name_entry.get()
            if not name:
                print("Enter a desctription.")
                return
            currency = currency_entry.get()
            if currency not in self.user.currency.currencies:
                print("Invalid currency.")
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
                print("Invalid amount.")
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
                                print("Invalid ratio.")
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
                        print("Total amount can not be zero.")
                        return

            print(debtors, amounts)
            if creditor in debtors:
                if len(debtors) == 1:
                    print("Invalid input")
                    return
                amounts.pop(debtors.index(creditor))
                debtors.remove(creditor)

            debtors = [debtors[i]
                       for i in range(len(debtors)) if float(amounts[i])]
            amounts = [amnt for amnt in amounts if float(amnt)]

            if not debtors:
                print("Select debtor")
                return

            date, repeat = None, None
            if schedule_entry.get():
                try:
                    date = str(dt.strptime(
                        "20"+date_entry.get().replace(".", "-")+" 12:00:00.1", '%Y-%m-%d %H:%M:%S.%f'))
                except ValueError:
                    print("Invalid date")
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

            self.remove_expense(user, unique_id)

            self.data["users"][self.user.id]["people"][user.id]["transactions"].append(
                new_transaction)
            self.data["users"][self.user.id]["people"][user.id]["transactions"].sort(
                key=lambda tr: dt.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
            self.data["users"][user.id]["people"][self.user.id]["transactions"].append(
                new_transaction)
            self.data["users"][user.id]["people"][self.user.id]["transactions"].sort(
                key=lambda tr: dt.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
            self.close_popups()
            self.refresh(self.people.button_handler(user.id))

        return f

    def remove_expense(self, owner, id):
        if isinstance(owner, User):
            for i in range(len(self.data["users"][self.user.id]["people"][owner.id]["transactions"])):
                if self.data["users"][self.user.id]["people"][owner.id]["transactions"][i]["id"] == id:
                    del self.data["users"][self.user.id]["people"][owner.id]["transactions"][i]
                    break
            for i in range(len(self.data["users"][owner.id]["people"][self.user.id]["transactions"])):
                if self.data["users"][owner.id]["people"][self.user.id]["transactions"][i]["id"] == id:
                    del self.data["users"][owner.id]["people"][self.user.id]["transactions"][i]
                    break
            return True
        else:
            for i in range(len(self.data["groups"][owner.id]["transactions"])):
                if self.data["groups"][owner.id]["transactions"][i]["id"] == id:
                    del self.data["groups"][owner.id]["transactions"][i]
                    break
            return False

    def delete_expense(self, owner, id):
        def f():
            self.close_popups()
            if self.remove_expense(owner, id):
                self.refresh(self.people.button_handler(owner.id))
            else:
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
                "repeat": False,
            }
        if not default_values["id"]:
            edit = False
            default_values["id"] = str(uuid1())
        if not default_values["date"]:
            default_values["date"] = str(dt.now())

        def f():
            if n < 2:
                print("There's no other members in this group.")
                return
            self.close_popups()
            win = CTkToplevel(self)
            win.title("NewExpense")
            win.geometry(f"{self.scr_w//4}x{int(0.75*self.scr_h)
                                            }+{int(0.4*self.scr_w)}+{self.scr_h//7}")
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
            creditor = CTkOptionMenu(entry, height=25, width=70, values=[f"{self.data["users"][id]["name"]} ({id})" for id in group.members],
                                     font=("Arial", 16, "bold"))
            creditor.pack(side=LEFT, padx=5)
            creditor.set(f"{self.data["users"][default_values["creditor"]]["name"]} ({
                         default_values["creditor"]})")
            widget = CTkLabel(entry, text="in", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)
            currency = CTkComboBox(entry, height=25, width=70, values=self.user.currency.currencies,
                                   font=("Arial", 16))
            currency.pack(side=LEFT, padx=5)
            currency.set(default_values["currency"])

            schedule = Frame(frame, height=10, fg_color="transparent")
            CTkLabel(schedule, width=10, text="Date", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            date = CTkEntry(schedule, height=30, width=80, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            date.pack(side=LEFT, padx=5, fill="x", expand=True)
            date.insert(0, default_values["date"][2:10].replace("-", "."))
            repeat = CTkOptionMenu(schedule, height=25, width=100, values=["none", "weekly", "daily", "monthly", "yearly"],
                                   font=("Arial", 16, "bold"))
            repeat.pack(side=RIGHT, padx=5)
            repeat.set(default_values["repeat"]
                       if default_values["repeat"] else "none")
            CTkLabel(schedule, width=10, text="repeat", font=(
                "Arial", 18)).pack(side=RIGHT, padx=5)

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
                CTkCheckBox(eq, height=5, font=("Arial", 16), border_width=2, corner_radius=15, text=f"{self.data["users"][id]["name"]} ({id})", variable=debtors[id], onvalue=id, offvalue="").pack(
                    anchor="nw", pady=5)
            CTkButton(tabs.tab("Equally"), height=30, width=10, text=f"{"Edit" if edit else "Add"} expense", command=self.create_group_expense("eq", default_values["date"], default_values["id"], group, name, creditor, debtors, checkbox, date, repeat, currency, amount),
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
                    "Arial", 16), text=f"{self.data["users"][id]["name"]} ({id})").pack(side=LEFT, padx=0)
                debtors[id] = CTkEntry(widget, height=25, border_width=0, width=50,
                                       fg_color="gray70", font=("Arial", 14))
                debtors[id].pack(side=RIGHT, fill="x")
            CTkButton(tabs.tab("By ratio"), height=30, width=10, text=f"{"Edit" if edit else "Add"} expense", command=self.create_group_expense("br", default_values["date"], default_values["id"], group, name, creditor, debtors, checkbox, date, repeat, currency, amount),
                      corner_radius=15).pack(side=BOTTOM, pady=0)
            br.pack(fill="both", padx=0, pady=0)

            # Unequally
            debtors = {id: None for id in group.members}
            for id in group.members:
                widget = Frame(uneq, fg_color="transparent")
                widget.pack(side=TOP, fill="x", pady=2)
                CTkLabel(widget, width=10, font=(
                    "Arial", 16), text=f"{self.data["users"][id]["name"]} ({id})").pack(side=LEFT, padx=0)
                debtors[id] = CTkEntry(widget, height=25, border_width=0, width=80,
                                       fg_color="gray70", font=("Arial", 14))
                debtors[id].pack(side=RIGHT, fill="x")
                debtors[id].insert(0, default_values["amounts"]
                                   [default_values["debtors"].index(id)] if id in default_values["debtors"] else "")

            CTkButton(tabs.tab("Unequally"), height=30, width=10, text=f"{"Edit" if edit else "Add"} expense", command=self.create_group_expense("uneq", default_values["date"], default_values["id"], group, name, creditor, debtors, checkbox, date, repeat, currency),
                      corner_radius=15).pack(side=BOTTOM, pady=0)
            uneq.pack(fill="both", padx=0, pady=0)

            frame.pack(expand=True, pady=20, padx=20)

        return f

    def create_group_expense(self, split_type, prev_date, unique_id, group: Group, name_entry, creditor_entry, debtors_entry, schedule_entry, date_entry, repeat_entry, currency_entry, amount_entry=None):
        def f():
            name = name_entry.get()
            if not name:
                print("Enter a desctription.")
                return
            try:
                amount = float(amount_entry.get()) if amount_entry else 0.0
            except ValueError:
                print("Invalid amount.")
                return
            currency = currency_entry.get()
            if currency not in self.user.currency.currencies:
                print("Invalid currency.")
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
                    print("Invalid input")
                    return
                amounts.pop(debtors.index(creditor))
                debtors.remove(creditor)

            debtors = [debtors[i]
                       for i in range(len(debtors)) if float(amounts[i])]
            amounts = [amnt for amnt in amounts if float(amnt)]

            if not debtors:
                print("Select debtors")
                return

            date, repeat = None, None
            if schedule_entry.get():
                try:
                    date = str(dt.strptime(
                        "20"+date_entry.get().replace(".", "-")+" 12:00:00.1", '%Y-%m-%d %H:%M:%S.%f'))
                except ValueError:
                    print("Invalid date")
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

            self.remove_expense(group, unique_id)

            self.data["groups"][group.id]["transactions"].append(
                new_transaction)
            self.data["groups"][group.id]["transactions"].sort(
                key=lambda tr: dt.strptime(tr["date"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
            self.close_popups()
            self.refresh(self.groups.button_handler(group.id))

        return f

    def simplify(self, group: Group):
        network = Network(group.members.copy())
        for expense in group.passed:
            for i in range(len(expense["debtors"])):
                amount = self.user.currency.convert(
                    float(expense["amounts"][i]), expense["currency"])
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
                self.data["groups"][invite[0]]["members"].append(self.user.id)
                self.data["users"][self.user.id]["groups"].append(invite[0])
                self.data["users"][self.data["groups"]
                                   [invite[0]]["members"][0]]["invites"].remove([invite[0], invite[1], self.user.id])
            else:
                self.data["users"][invite[2]]["invites"].remove(
                    [invite[0], invite[1], None])
            self.data["users"][self.user.id]["invites"].remove(invite)

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
                if id not in self.data["users"] or id in group_members or id == self.user.id:
                    continue
                group_members.append(id)

            if not group_name:
                print("Enter group name.")
                return

            group_id = str(uuid1())
            self.data["groups"][group_id] = {
                "name": group_name,
                "avatar": "avatars/group1.png",
                "members": [self.user.id],
                "transactions": []
            }
            self.data["users"][self.user.id]["groups"].append(group_id)
            self.invite(group_id, group_members)
            self.refresh(call=self.groups.button_handler(group_id))

        return f

    def new_friend(self):
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
                if id not in self.data["users"] or id in new_friends or id in self.user.people or id == self.user.id:
                    continue
                new_friends.insert(0, id)
            me = {
                "name": self.user.name,
                "transactions": [],
            }
            for fr in new_friends:
                person = {
                    "name": self.data["users"][fr]["name"],
                    "transactions": [],
                }
                self.data["users"][self.user.id]["people"][fr] = person
                self.data["users"][fr]["people"][self.user.id] = me
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
                if id not in self.data["users"] or id in group.members or id in new_members:
                    continue
                new_members.append(id)
            self.invite(group.id, new_members)
            self.refresh(call=self.groups.button_handler(group.id))

        return f

    def invite(self, group_id, group_members):
        for user_id in group_members:
            self.data["users"][user_id]["invites"].insert(0,
                                                          [group_id, str(dt.now()), None])
            self.data["users"][self.user.id]["invites"].insert(0,
                                                               [group_id, str(dt.now()), user_id])
            self.side_bar.default_tab = "invites"
        self.close_popups()

    def refresh(self, call=None):
        self.root.destroy()
        self.data["users"][self.user.id]["name"] = self.user.name
        self.last_tab = self.side_bar.default_tab
        self.load(self.user.id, self.data)
        if call:
            call()

    def save(self):
        self.data["users"][self.user.id]["name"] = self.user.name
        with open("local.json", "w") as file:
            dump(self.data, file, indent=4)

    @ staticmethod
    def sentence(task, input):
        if task == "group":
            output = []
            for item in input[:-1]:
                output.append(item)
            return (", ".join(output) + f" and {input[-1]}") if output else input[-1]


me = "user1"
data = None
app = App()
app.req.id = me
app.status_code = app.req.read_global_data()
if app.status_code:
    data = app.req.global_data
else:
    app.req.read_local_data()
    data = app.req.local_data
app.load(me, data)
app.mainloop()
