import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageDraw


class Network:
    def __init__(self, people: list[str], currency="USD"):
        self.currency = currency
        self.people = people
        self.total_expensed = 0
        self.expensed = {id: 0 for id in people}
        self.balance = {id: 0 for id in people}
        self.size = len(people)
        self.adjacency = pd.DataFrame(
            np.zeros((self.size, self.size), float), index=people, columns=people
        )
        return

    def add_debt(self, debtor, creditor, amount):
        if debtor not in self.people:
            self.add_person(debtor)
        if creditor not in self.people:
            self.add_person(creditor)
        self.total_expensed += abs(amount)
        self.expensed[creditor] += abs(amount)
        self.adjacency.at[debtor, creditor] += amount
        self.adjacency.at[creditor, debtor] -= amount
        self.calculate_balance()
        return

    def add_person(self, id):
        self.people.append(id)
        self.adjacency.loc[id] = [0] * self.size
        self.adjacency[id] = 0
        self.balance[id] = 0
        self.expensed[id] = 0
        self.size += 1
        return

    def calculate_balance(self):
        self.balance = {id: round(self.adjacency[id].sum(), 2)
                        for id in self.people}
        return

    def settled_up(self):
        transactions = []
        queue = sorted(self.balance.items(), key=lambda item: item[1])
        queue = [item for item in queue if abs(item[1]) >= 0.01]
        while queue:
            debtor, debt = queue[0]
            debt = -debt
            match = -1
            for i in range(-1, -len(queue), -1):
                if queue[i][1] == debt:
                    match = i
                    break
                elif queue[i][1] < debt:
                    break
            creditor, credit = queue[match]

            del queue[match], queue[0]
            if debt < credit:
                queue.append((creditor, credit-debt))
            elif debt > credit:
                queue.append((debtor, credit-debt))
            transactions.append(
                (debtor, creditor, round(min(debt, credit), 2)))
            queue = [item for item in queue if abs(item[1]) >= 0.01]
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

    def visualize(self, avatars, labels, unknown):
        G = nx.DiGraph()
        debts = self.settled_up()
        G.add_nodes_from(self.people)
        for debtor, creditor, amount in debts:
            G.add_edge(debtor, creditor, weight=amount)
        pos = nx.circular_layout(G)
        fig, ax = plt.subplots()

        for person, (x, y) in pos.items():
            img = Image.open(
                avatars[person] if person in avatars else unknown).convert("RGBA")
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            bigsize = (img.size[0] * 3, img.size[1] * 3)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(img.size, Image.Resampling.LANCZOS)
            img.putalpha(mask)
            imagebox = OffsetImage(img, zoom=0.5)
            ab = AnnotationBbox(imagebox, (x, y), frameon=False)
            ax.add_artist(ab)

        nx.draw_networkx_edges(G, pos, ax=ax, arrowstyle='->', connectionstyle='arc3,rad=0.2',
                               arrowsize=15, width=2, min_source_margin=30, min_target_margin=30)

        for person, (x, y) in pos.items():
            ax.text(x, y-0.3, labels[person] if person in labels else "Unknown", horizontalalignment='center',
                    fontsize=10, zorder=2)

        edge_labels = {(debtor, creditor): str(amount)
                       for debtor, creditor, amount in debts}
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_size=12, font_family="Arial")

        ax.axis('off')

        return fig


# group = Network(["Alice", "Bob", "Charlie", "David"])
# group.add_debt("Alice", "Bob", 10.3)
# group.add_debt("Bob", "Charlie", 30)
# group.add_debt("Charlie", "Alice", 20)
# group.add_debt("Alice", "David", 40)
# group.add_debt("David", "Charlie", 10)

# group.visualize(None)

# print(group.balance)
# print(group.adjacency)
# print(group.settled_up())
# -------
# Alice owes Bob $50
# Bob owes Charlie $30
# Charlie owes Alice $20
# Alice owes David $40
# David owes Charlie $10
