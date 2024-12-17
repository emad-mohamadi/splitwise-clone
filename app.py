from json import load
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
        self.geometry(f"{self.scr_w}x{self.scr_h}+{self.scr_w //
                      2}+{self.scr_h//2}")  # Initial window size
        self.title(title)  # seting window title
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
        self.root.pack(fill="both", expand=True)
        side_bar = SideBar(self.root, config["app"]["sidebar"])

        objects = {
            "name": ["1", "2"],
            "label": ["Title1", "Title2"],
            "button": [("View", 45), ("View", 45)],
            "text": [[], []],
        }
        home = FrameList(side_bar.panels["home"], config["app"]
                         ["sidepanels"]["home"], objects, height=80)

        objects = {
            "name": [group.id for group in groups_list],
            "label": [group.name for group in groups_list],
            "button": [("View", 45) for _ in groups_list],
            "text": [[] for _ in groups_list]
        }
        groups = FrameList(side_bar.panels["groups"], config["app"]
                           ["sidepanels"]["groups"], objects, height=80, command=self.new_group)
        # connection_status = CTkLabel(
        #     side_bar.panels["groups"], text="You're Offline", height=25, font=("Arial Bold", 12), corner_radius=0, bg_color="DarkGoldenrod1")
        # connection_status.pack(side=BOTTOM, padx=0, pady=0, fill="x")

        objects = {
            "name": [user.id for user in people_list],
            "label": [user.name for user in people_list],
            "button": [("View", 45), ("View", 45)],
            "text": [(("You are owed 0.2$", "green"), ("And you owe 0.8$", "red"), ("Net balance: -0.6$", "blue")), (("You are owed 1.3$", "green"), ("And you owe 0.9$", "red"), ("Net balance: +0.4$", "blue"))],
        }
        people = FrameList(side_bar.panels["people"], config["app"]
                           ["sidepanels"]["people"], objects, height=80, command=self.refresh)

        objects = {
            "name": [invite[0]+str(invite[2]) for invite in self.user.invites],
            "label": [f"{self.data["users"][self.data["groups"][invite[0]]["members"][0]]["name"]} invited {"you" if not invite[2] else self.data["users"][invite[2]]["name"]} to {self.data["groups"][invite[0]]["name"]}." for invite in self.user.invites],
            "button": [None]*len(self.user.invites),
            "text": [((invite[1][:16], "gray50"),) for invite in self.user.invites],
        }
        invites = FrameList(side_bar.panels["invites"], config["app"]
                            ["sidepanels"]["invites"], objects, height=50, font=("Arial", 16))

        empty = MainPanel(self.root)
        empty.add_title(text="There's nothing to show.",
                        font=("Arial", 18), color="gray60", not_placed=True)
        empty.title.place(relx=0.5, rely=0.5, anchor=CENTER)
        links = {"empty": empty}
        for gr in groups_list:
            options = {
                "label": [data["users"][id]["name"] for id in gr.members] + [None],
                "color": ["gray60" if i else "gray30" for i in range(len(gr.members))] + [Frame.picture(config["icons"]["add-member"], (20, 20))],
                "command": [None] * (len(gr.members)+1),
            }
            buttons = {
                "label": ["New Expense", "Delete Group"],
                "color": [(None, None), ("red3", "red4")],
                "comand": [None, None],
            }
            main_panel = MainPanel(self.root)
            main_panel.add_title(text=gr.name)
            main_panel.add_options(options)
            main_panel.add_button(buttons)
            main_panel.set_body()
            links[gr.id] = main_panel
            recent = Frame(main_panel.body, fg_color="gray83",
                           height=500, corner_radius=15)
            recent.pack(side=LEFT, fill="both", expand=True)
            summary = Frame(main_panel.body,
                            fg_color="transparent", corner_radius=15)
            summary.pack(side=RIGHT, fill="both", expand=True)
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
                "text": [[(f"{data["users"][tr["creditor"]]["name"]} lent {tr["amount"]} {tr["currency"]} to {", ".join(data["users"][debtor]["name"] for debtor in tr["debtors"])}", "black")] for tr in gr.transactions],
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
                "label": [f"{data["users"][debtor]["name"]} owe {data["users"][creditor]["name"]} {amount}" for debtor, creditor, amount in simlified],
                "button": [None]*len(simlified),
                "text": [[]*len(simlified)],
            }
            widget = FrameList(summary, header, objects, width=30,
                               height=30, title_color="gray50", font=("Arial", 14))

        groups.add_link(links)

        links = {"empty": empty}
        for us in people_list:
            buttons = {
                "label": ["New Expense", f"Delete {us.name}"],
                "color": [(None, None), ("red3", "red4")],
                "comand": [None, None]
            }
            main_panel = MainPanel(self.root)
            main_panel.add_title(text=us.name)
            main_panel.add_button(buttons)
            main_panel.add_text("Sample text")
            main_panel.set_body()
            links[us.id] = main_panel

        people.add_link(links)
        groups.button_handler("empty")()

        return

    def simplify(self, group: Group):
        network = Network(group.members)
        for expense in group.transactions:
            amount = round(expense["amount"]/len(expense["debtors"]), 2)
            for debtor in expense["debtors"]:
                network.add_debt(debtor, expense["creditor"], amount)
        return network.settled_up()

    def button_handler(self, button_name):
        def f():
            win = CTkToplevel(self)
            W = self.winfo_screenwidth()//2
            H = self.winfo_screenheight()//2
            win.title(button_name)
            win.geometry(f"{W//2}x{H}+{int(0.75*W)}+{H//2}")
            win.lift()
            win.focus()
            win.attributes("-topmost", True)
            Frame(win, corner_radius=20).pack(padx=20, pady=20, fill="both")

        return f

    def new_group(self):
        self.win = CTkToplevel(self)
        self.win.title("Create New Group")
        self.win.geometry(f"{self.scr_w//2}x{int(0.75*self.scr_h)
                                             }+{int(0.75*self.scr_w)}+{self.scr_h//2}")
        self.win.lift()
        self.win.focus()
        self.win.attributes("-topmost", True)
        frame = Frame(self.win, corner_radius=20, width=500, height=6000)
        frame.pack(expand=True, pady=20, padx=20)

        widget = CTkLabel(frame, text="New Group", font=(
            "Arial Bold", 25), text_color="gray40")
        widget.pack(padx=15, pady=10, anchor="nw")

        entry = Frame(frame, height=50, fg_color="transparent")
        entry.pack(anchor="nw", padx=10, pady=15, fill="x")
        widget = CTkLabel(entry, text="Group Name", font=("Arial", 18))
        widget.pack(side=LEFT, padx=5)
        name = CTkEntry(entry, height=30, border_width=0,
                        fg_color="gray90", font=("Arial", 16, "bold"))
        name.pack(side=RIGHT, padx=5, fill="x")

        entry = Frame(frame, height=100, fg_color="transparent")
        entry.pack(anchor="nw", padx=10, pady=0, fill="x")
        widget = CTkLabel(entry, text="Members", font=("Arial", 18))
        widget.pack(side=LEFT, padx=5)
        members = CTkEntry(entry, height=30, border_width=0,
                           fg_color="gray90", font=("Arial", 16, "bold"))
        members.pack(side=BOTTOM, padx=5, fill="x")

        widget = Frame(frame, height=100, fg_color="transparent")
        widget.pack(anchor="nw", padx=10, pady=0, fill="x")
        CTkLabel(widget, text="Use comma to seperate usernames.\nYou can invite members later.\n\n", font=(
            "Arial", 12, "bold"), text_color="gray60", justify="left", wraplength=250).pack(anchor="sw", padx=6, pady=5)
        CTkButton(frame, text="Creat Group", width=80, font=("Arial", 18, "bold"),
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

            for user_id in group_members:
                self.data["users"][user_id]["invites"].append(
                    [group_id, str(dt.now()), None])
                self.data["users"][self.user.id]["invites"].append(
                    [group_id, str(dt.now()), user_id])
            self.win.destroy()
            self.refresh()

        return f

    def refresh(self):
        self.root.destroy()
        self.data["users"][self.user.id]["name"] = self.user.name
        self.load(self.user.id, self.data)


me = "user3"
data = Data(me)
data.read_local_data()
app = App()
app.load(me, data.local_data)
app.mainloop()
