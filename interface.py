from customtkinter import *
from PIL import Image


class Frame(CTkFrame):
    def __init__(self, master, width=200, height=200, corner_radius=None, border_width=None, bg_color="transparent", fg_color=None, border_color=None, background_corner_colors=None, overwrite_preferred_drawing_method=None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color,
                         border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        return

    @staticmethod
    def picture(file_path, size=(35, 35)):
        file = Image.open(file_path)
        return CTkImage(file, size=size)


class SideBar:
    def __init__(self, root, options, color="gray40", hover_color="gray65", click_color="gray81", size=40):
        self.color = color
        self.click_color = click_color
        self.side_bar = Frame(
            root, width=size, corner_radius=0, fg_color=color)
        self.side_bar.pack(side=LEFT, fill="y")
        self.buttons = {name: None for name in options}
        self.panels = {name: None for name in options}
        for name, (pic, side) in options.items():
            self.panels[name] = Frame(root, width=300, corner_radius=0)
            icon = Frame.picture(pic, size=(size, size))
            self.buttons[name] = CTkButton(
                self.side_bar,
                image=icon,
                text="",
                fg_color="transparent",
                width=30,
                height=30,
                hover_color=hover_color,
                command=self.button_handler(name),
                corner_radius=0
            )
            self.buttons[name].pack(fill="both", side=side)
        self.button_handler("home")()
        return

    def button_handler(self, button_name):
        def f():
            for name, button in self.buttons.items():
                if name == button_name:
                    button.configure(fg_color=self.click_color)
                    self.panels[name].pack(side=LEFT, fill="y")
                else:
                    self.panels[name].pack_forget()
                    button.configure(fg_color=self.color)
        return f


class FrameList:
    links = {}

    def __init__(self, root, header, objects, command=None, width=280, height=150, corner_radius=15, font=("Calibry", 18), title_color="gray40", color=None):
        self.items = {name: None for name in objects["name"]}
        self.title = Frame(
            root, height=header["height"], width=width, fg_color="transparent")
        self.title.pack(side=TOP, padx=10, pady=5, fill="x")
        widget = CTkLabel(
            self.title, text=header["label"], font=header["font"], fg_color="transparent", wraplength=280, justify="left", text_color=title_color)
        widget.place(x=5, y=5)

        if header["button"]:
            widget = CTkButton(self.title, width=header["button"][1], height=30, command=command,
                               corner_radius=corner_radius, text=header["button"][0])
            widget.place(x=width-header["button"][1]-10, y=7)
        if header["text"]:
            widget = CTkLabel(
                self.title, text=header["text"], font=(font[0], font[1]-4), fg_color="transparent", wraplength=280, justify="left")
            widget.place(x=6, y=15+header["font"][1])

        for name in self.items:
            i = objects["name"].index(name)
            self.items[name] = Frame(
                root, height=height, width=width, corner_radius=corner_radius, fg_color=color)
            self.items[name].pack(side=TOP, padx=10, pady=5, fill="x")

            widget = CTkLabel(
                self.items[name], text=objects["label"][i], font=font, fg_color="transparent")
            widget.place(x=10, y=5)

            if objects["button"][i]:
                widget = CTkButton(self.items[name], width=objects["button"][i][1], height=30,
                                   corner_radius=corner_radius-5, text=objects["button"][i][0], command=self.button_handler(name))
                widget.place(x=width-objects["button"][i][1]-10, y=5)

            textbox = Frame(
                self.items[name], fg_color="transparent", width=10, height=10)
            textbox.place(x=10, y=12+font[1])
            for j in range(len(objects["text"][i])):
                widget = CTkLabel(
                    textbox, text=objects["text"][i][j][0], height=1, font=(font[0], font[1]-5), fg_color="transparent", wraplength=220, justify="left", text_color=objects["text"][i][j][1])
                widget.pack(padx=1, pady=0, anchor="nw")

    def add_link(self, links):
        for name, link in links.items():
            self.links[name] = link
        return

    def button_handler(self, button_name):
        def f():
            for name, link in self.links.items():
                if name == button_name:
                    link.pack(side=RIGHT, fill="both", expand=True)
                elif link:
                    link.pack_forget()

        return f


class MainPanel(Frame):
    def __init__(self, master, width=200, height=200, corner_radius=0, border_width=None, bg_color="transparent", fg_color="transparent", border_color=None, background_corner_colors=None, overwrite_preferred_drawing_method=None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color,
                         border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.pack(side=RIGHT, fill="both", expand=True)
        return

    def add_title(self, text, font=("Arial Bold", 25), wraplength=400, color="black", not_placed=False):
        self.title = CTkLabel(self, text=text, fg_color="transparent",
                              wraplength=wraplength, font=font, justify="left", text_color=color)
        if not_placed:
            return
        self.title.place(x=15, y=10)
        return

    def add_options(self, options, corner_radius=20, hover_color="gray70"):
        frame = Frame(self, fg_color="transparent", height=10)
        frame.place(y=40, x=15)
        for i in range(len(options["label"])):
            if options["label"][i]:
                widget = CTkButton(
                    frame, corner_radius=corner_radius, text=options["label"][i], width=20, height=20, font=("Arial Bold", 12), fg_color=options["color"][i], hover_color=hover_color)
            else:
                widget = CTkButton(
                    frame, image=options["color"][i], text="", corner_radius=corner_radius, width=10, height=10, font=("Arial Bold", 10), fg_color="transparent", hover_color=hover_color)
            widget.pack(side=LEFT, padx=1, pady=0)
        return

    def add_button(self, buttons, corner_radius=20):
        frame = Frame(self, width=10, height=10)
        frame.pack(pady=9, anchor="ne")
        for i in range(len(buttons["label"])):
            widget = CTkButton(frame, text=buttons["label"][i], width=20, height=25, corner_radius=corner_radius,
                               fg_color=buttons["color"][i][0], hover_color=buttons["color"][i][1], font=("Arial", 12, "bold"))
            widget.pack(anchor="ne", pady=2, padx=15)
        return

    def set_body(self, color="transparent", corner_raduis=15):
        self.body = Frame(self, fg_color=color, corner_radius=corner_raduis)
        self.body.pack(padx=15, pady=5, fill="both", side=BOTTOM, expand=True)
        return

    def add_text(self, text, font=("Arial", 14), wraplength=400, color="black"):
        frame = Frame(self, fg_color="transparent", height=10)
        frame.place(y=40, x=15)
        widget = CTkLabel(frame, text=text, text_color=color, width=20, height=25,
                          fg_color="transparent", font=font, justify="left", wraplength=wraplength)
        widget.pack(anchor="nw", padx=1)
        return
