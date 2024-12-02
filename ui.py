
import customtkinter as CTK
from tkinter import Tk


class Dashboard(Tk):
    def __init__(self):
        super().__init__()

        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure((0, 1), weight=1)

        self.frame = CTK.CTkFrame(self, width=100, fg_color="gray25")
        self.frame.place(x=0, y=0, relheight=1)
        self.frame.grid_propagate(False)

        self.button = CTK.CTkButton(self.frame, text='≡', width=70, font=(
            "roboto", 40), hover_color='#242424', fg_color='#2B2B2B', corner_radius=0, command=self.expand_side_bar)
        self.button.place(relx=1, rely=0, anchor="ne")

        self.text = CTK.CTkLabel(
            self, text='Hello ,World!', font=("roboto", 40))
        self.text.place(x=100, y=50)
        self.text.lower()

    def expand_side_bar(self):
        if self.frame["width"] != 500:
            self.frame.configure(width=500)
            return
        self.frame.configure(width=70)


app = Dashboard()
app.mainloop()
