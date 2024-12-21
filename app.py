from json import load, dump
from interface import *
from user import User, Group
from alg import Network
from server import Data
from uuid import uuid1
from datetime import datetime as dt

config = {
    "icons": {
        "add-member": "icons/add-member.png"
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
                "button": ("New Group", 85),
                "text": None
            },
            "people": {
                "height": 70,
                "font": ("Arial Bold", 25),
                "label": "People",
                "button": ("New Expense", 98),
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
        self.scr_w = self.winfo_screenwidth()//2
        self.scr_h = self.winfo_screenheight()//2
        self.geometry(f"{int(1.3*self.scr_w)}x{self.scr_h}+{self.scr_w //
                      2}+{self.scr_h//2}")  # Initial window size
        self.title(title)  # seting window title
        self.last_tab = "home"
        self.last_panel = "empty"
        return

    def load(self, id, data):
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
        home = FrameList(self.side_bar.panels["home"], config["app"]
                         ["sidepanels"]["home"], objects, height=80, width=320)

        objects = {
            "name": [group.id for group in groups_list],
            "label": [group.name for group in groups_list],
            "button": [("View", 45, (None, None), None) for _ in groups_list],
            "text": [[] for _ in groups_list]
        }
        self.groups = FrameList(self.side_bar.panels["groups"], config["app"]
                                ["sidepanels"]["groups"], objects, height=80, command=self.new_group, width=320)

        # connection_status = CTkLabel(
        #     side_bar.panels["groups"], text="You're Offline", height=25, font=("Arial Bold", 12), corner_radius=0, bg_color="DarkGoldenrod1")
        # connection_status.pack(side=BOTTOM, padx=0, pady=0, fill="x")

        objects = {
            "name": [user.id for user in people_list],
            "label": [user.name for user in people_list],
            "button": [("View", 45, (None, None), None) for _ in people_list],
            "text": [(("You are owed 0.2$", "green"), ("And you owe 0.8$", "red"), ("Net balance: -0.6$", "blue")), (("You are owed 1.3$", "green"), ("And you owe 0.9$", "red"), ("Net balance: +0.4$", "blue"))],
        }
        people = FrameList(self.side_bar.panels["people"], config["app"]
                           ["sidepanels"]["people"], objects, height=80, command=self.save, width=320)

        objects = {
            "name": [invite[0]+str(invite[2]) for invite in self.user.invites],
            "label": [f"{self.data["users"][self.data["groups"][invite[0]]["members"][0]]["name"]} invited {"you" if not invite[2] else self.data["users"][invite[2]]["name"]} to {self.data["groups"][invite[0]]["name"]}" for invite in self.user.invites],
            "button": [("Delete", 53, ("red3", "red4"), self.invite_action(invite, False)) if invite[2] else ("Accept", 56, (None, None), self.invite_action(invite, True)) for invite in self.user.invites],
            "text": [((invite[1][:16], "gray50"),) for invite in self.user.invites]
        }
        invites = FrameList(self.side_bar.panels["invites"], config["app"]
                            ["sidepanels"]["invites"], objects, height=50, font=("Arial", 14), font_dif=2, width=320)

        empty = MainPanel(self.root)
        empty.add_title(text="There's nothing to show.",
                        font=("Arial", 18), color="gray60", not_placed=True)
        empty.title.pack(expand=True)
        links = {"empty": empty}
        for gr in groups_list:
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
                "label": ["New Expense", "Delete Group" if gr.members[0] == self.user.id else "Leave Group"],
                "color": [(None, None), ("red3", "red4")],
                "command": [self.new_group_expense(gr), None],
            }
            main_panel = MainPanel(self.root)
            main_panel.add_title(text=gr.name)
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
                "label": "Recent",
                "button": None,
                "text": None,
            }
            objects = {
                "name": [tr["date"] for tr in gr.transactions],
                "label": [tr["name"] for tr in gr.transactions],
                "button": [None]*len(gr.transactions),
                "text": [[(f"{data["users"][tr["creditor"]]["name"]} lent {sum([float(amnt) for amnt in tr["amounts"]])} {tr["currency"]} to {", ".join(data["users"][debtor]["name"] for debtor in tr["debtors"])}", "black")] for tr in gr.transactions],
            }
            widget = FrameList(recent, header, objects, width=10,
                               height=55, title_color="gray50")

            simlified = self.simplify(gr)
            header = {
                "height": 30,
                "font": ("Arial Bold", 18),
                "label": " Summary",
                "button": None,
                "text": None,
            }
            objects = {
                "name": [str(i) for i in range(len(simlified))],
                "label": [f"{data["users"][debtor]["name"]} owe{"s" if debtor != self.user.id else ""} {data["users"][creditor]["name"]} {amount} {self.user.currency.default}" for debtor, creditor, amount in simlified],
                "button": [None]*len(simlified),
                "text": [[]]*len(simlified),
            }
            widget = FrameList(summary, header, objects, width=30,
                               height=30, title_color="gray50", font=("Arial", 14))
            recent.pack(side=LEFT, fill="both", expand=True)
            summary.pack(side=RIGHT, fill="both", expand=True)

        self.groups.add_link(links)

        links = {"empty": empty}
        for us in people_list:
            buttons = {
                "label": ["New Expense", f"Delete {us.name}"],
                "color": [(None, None), ("red3", "red4")],
                "command": [None, None]
            }
            main_panel = MainPanel(self.root)
            main_panel.add_title(text=us.name)
            main_panel.add_button(buttons)
            main_panel.add_text("Sample text")
            main_panel.set_body()
            links[us.id] = main_panel

        people.add_link(links)
        self.groups.button_handler("empty")()

        self.root.pack(fill="both", expand=True)
        return

    def new_group_expense(self, group: Group):
        def f():
            if len(group.members) < 2:
                print("There's no other members in this group.")
                return
            self.win = CTkToplevel(self)
            self.win.title("NewExpense")
            self.win.geometry(f"{self.scr_w//2}x{self.scr_h
                                                 }+{int(0.75*self.scr_w)}+{self.scr_h//2}")
            self.win.lift()
            self.win.focus()
            self.win.attributes("-topmost", True)
            frame = Frame(self.win, corner_radius=20)

            CTkLabel(frame, text="Add expense", font=(
                "Arial Bold", 25), text_color="gray40").pack(padx=15, pady=10, anchor="nw")

            entry = Frame(frame, height=50, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=15, fill="x")
            CTkLabel(entry, text="Description", font=(
                "Arial", 18)).pack(side=LEFT, padx=5)
            name = CTkEntry(entry, height=30, border_width=0,
                            fg_color="gray90", font=("Arial", 16))
            name.pack(side=RIGHT, padx=5, fill="x")

            entry = Frame(frame, height=10, fg_color="transparent")
            entry.pack(anchor="nw", padx=10, pady=5, fill="x")
            widget = CTkLabel(entry, text="Paid by", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)
            creditor = CTkOptionMenu(entry, height=25, width=70, values=[f"{self.data["users"][id]["name"]} ({id})" for id in group.members],
                                     font=("Arial", 16, "bold"))
            creditor.pack(side=LEFT, padx=5)
            creditor.set(f"You ({self.user.id})")
            widget = CTkLabel(entry, text="in", font=("Arial", 18))
            widget.pack(side=LEFT, padx=5)
            currency = CTkComboBox(entry, height=25, width=70, values=self.user.currency.currencies,
                                   font=("Arial", 16))
            currency.pack(side=LEFT, padx=5)
            currency.set(self.user.currency.default)

            tabs = CTkTabview(frame, height=200, width=100,
                              corner_radius=10)
            tabs.pack(fill="both", side=BOTTOM, padx=10, pady=10, expand=True)

            tabs.add("Equally")
            tabs.add("Unequally")
            tabs.add("By ratio")

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
            CTkButton(tabs.tab("Equally"), height=30, width=10, text="Add expense", command=self.create_group_expense("eq", group, name, creditor, debtors, currency, amount),
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
            CTkButton(tabs.tab("By ratio"), height=30, width=10, text="Add expense", command=self.create_group_expense("br", group, name, creditor, debtors, currency, amount),
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
            CTkButton(tabs.tab("Unequally"), height=30, width=10, text="Add expense", command=self.create_group_expense("uneq", group, name, creditor, debtors, currency),
                      corner_radius=15).pack(side=BOTTOM, pady=0)
            uneq.pack(fill="both", padx=0, pady=0)

            frame.pack(expand=True, pady=20, padx=20)

        return f

    def create_group_expense(self, split_type, group: Group, name_entry, creditor_entry, debtors_entry, currency_entry=0, amount_entry=None):
        def f():
            name = name_entry.get()
            if not name:
                print("Enter a desctription.")
                return
            try:
                amount = float(amount_entry.get()) if amount_entry else None
                if not amount:
                    raise ValueError
            except ValueError:
                print("Total amount can not be zero.")
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
                       for i in range(len(debtors)) if amounts[i]]
            amounts = [amnt for amnt in amounts if amnt]

            if not debtors:
                print("Select debtors")
                return

            new_transaction = {
                "name": name,
                "amounts": amounts,
                "debtors": debtors,
                "creditor": creditor,
                "currency": currency,
                "date": str(dt.now())
            }

            self.data["groups"][group.id]["transactions"].insert(
                0, new_transaction)
            self.win.destroy()
            self.refresh(self.groups.button_handler(group.id))

        return f

    def simplify(self, group: Group):
        network = Network(group.members)
        for expense in group.transactions:
            for i in range(len(expense["debtors"])):
                amount = self.user.currency.convert(
                    float(expense["amounts"][i]), expense["currency"])
                network.add_debt(
                    expense["debtors"][i], expense["creditor"], amount)
        return network.settled_up()

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
        self.win = CTkToplevel(self)
        self.win.title("NewGroup")
        self.win.geometry(f"{self.scr_w//2}x{int(0.75*self.scr_h)
                                             }+{int(0.75*self.scr_w)}+{self.scr_h//2}")
        self.win.lift()
        self.win.focus()
        self.win.attributes("-topmost", True)
        frame = Frame(self.win, corner_radius=20, width=500, height=6000)
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

    def new_invite(self, group: Group):
        def f():
            self.win = CTkToplevel(self)
            self.win.title("InviteUsers")
            self.win.geometry(f"{self.scr_w//2}x{int(0.75*self.scr_h)
                                                 }+{int(0.75*self.scr_w)}+{self.scr_h//2}")
            self.win.lift()
            self.win.focus()
            self.win.attributes("-topmost", True)
            frame = Frame(self.win, corner_radius=20, width=500, height=6000)
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
        self.win.destroy()

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
            dump(self.data, file)

    @staticmethod
    def sentence(task, input):
        if task == "group":
            output = []
            for item in input[:-1]:
                output.append(item)
            return ", ".join(output) + f" and {input[-1]}"


me = "user1"
data = Data(me)
data.read_local_data()
app = App()
app.load(me, data.local_data)
app.mainloop()
