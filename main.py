from app import App


app = App()
if app.ref.status:
    app.login()
app.mainloop()
