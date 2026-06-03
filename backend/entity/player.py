class Player:
    handTile = []
    bonus = []

    def __init__(self, tai: int = 0):
        self.tai = tai

    def __str__(self):
        return (
            f"Tai: {self.tai}"
            + "\nBonus tiles: "
            + ", ".join([str(t) for t in self.bonus])
            + "\nHand: "
            + ", ".join([str(t) for t in self.handTile])
        )

    def addTai(self, increment: int = 1):
        self.tai += increment

    def addBonusTile(self, bonus: list):
        self.bonus = bonus

    def assignHand(self, handTile):
        self.handTile = handTile
