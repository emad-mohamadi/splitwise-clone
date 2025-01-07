import requests
from datetime import datetime, timedelta
from json import load, dump

API_KEY = 'ed7f3aadc0d3e6b32b52d9ce'
URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"
PATH = "exchangerates.json"


class Conversions:
    def __init__(self, default="USD"):
        with open(PATH, "r") as file:
            data = load(file)
        self.default = default
        self.status = "online"
        self.rates = data["conversion-rates"]
        self.currencies = list(self.rates.keys())
        self.last_update = datetime.strptime(
            data["update"], '%Y-%m-%d %H:%M:%S.%f')

        self.check_for_update()
        return

    def update(self, std_currency="USD"):
        try:
            response = requests.get(URL+std_currency)
            data = response.json()
            if response.status_code != 200:
                print(f"Error: {data['error-type']}")
                return "offline"
        except:
            print("No network, Failed to update conversion rates.")
            return "offline"

        self.rates = data['conversion_rates']
        self.last_update = str(datetime.now())
        with open(PATH, "w") as file:
            dump({"conversion-rates": self.rates,
                 "update": self.last_update}, file, indent=4)
        return "online"

    def rate(self, base, target):
        with open(PATH, "r") as file:
            data = load(file)
        rates = data["conversion-rates"]
        return rates[target] / rates[base]

    def convert(self, amount, base, target=None):
        if not target:
            target = self.default
        return round(float(amount) * self.rate(base, target), 2)

    def check_for_update(self):
        if datetime.now() - self.last_update > timedelta(days=1):
            self.status = self.update()
        return
