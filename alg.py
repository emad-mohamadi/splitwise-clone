import pandas as pd
import numpy as np


class Network:
    def __init__(self, people: list[str], currency="USD"):
        self.currency = currency
        self.people = people
        self.balance = {id: 0 for id in people}
        self.size = len(people)
        self.adjacency = pd.DataFrame(
            np.zeros((self.size, self.size), int), index=people, columns=people
        )
        return

    def add_debt(self, debtor, creditor, amount):
        self.adjacency.at[debtor, creditor] += amount
        self.adjacency.at[creditor, debtor] -= amount
        self.calculate_balance()
        return

    def add_person(self, id):
        self.people.add(id)
        self.adjacency.loc[id] = [0] * self.size
        self.adjacency[id] = 0
        self.balance[id] = 0
        self.size += 1
        return

    def calculate_balance(self):
        self.balance = {id: round(self.adjacency[id].sum(), 2)
                        for id in self.people}
        return

    def settled_up(self):
        transactions = []
        queue = sorted(self.balance.items(), key=lambda item: item[1])
        queue = [item for item in queue if item[1]]
        while queue:
            debtor, debt = queue[0]
            debt = -debt
            match = None
            for i in range(-1, -len(queue), -1):
                if queue[i][1] == debt:
                    match = i
                    break
                elif queue[i][1] < debt:
                    match = -1
                    break
            creditor, credit = queue[match]

            del queue[match], queue[0]
            if debt < credit:
                queue.append((creditor, credit-debt))
            elif debt > credit:
                queue.append((debtor, credit-debt))
            transactions.append(
                (debtor, creditor, round(min(debt, credit), 2)))
            queue.sort(key=lambda item: item[1])
        return transactions

    def __repr__(self):
        phrases = []
        for creditor in self.people:
            for debtor in self.people:
                if self.adjacency[creditor][debtor] > 0:
                    phrases.append(f"{debtor} owes {creditor} ${
                                   self.adjacency[creditor][debtor]}")
        return "\n".join(phrases)


# group = Network(["Alice", "Bob", "Charlie", "David"])
# group.add_debt("Alice", "Bob", 10.3)
# group.add_debt("Bob", "Charlie", 30)
# group.add_debt("Charlie", "Alice", 20)
# group.add_debt("Alice", "David", 40)
# group.add_debt("David", "Charlie", 10)

# print(group.balance)
# print(group.adjacency)
# print(group.settled_up())
# -------
# Alice owes Bob $50
# Bob owes Charlie $30
# Charlie owes Alice $20
# Alice owes David $40
# David owes Charlie $10
