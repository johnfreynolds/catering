class Item: 
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def getPrice(self):
        return self.price

    def getName(self):
        return self.name

class Cart:
    def __init__(self, list):
        self.list = []

    def addItem(self, item):
        self.list.append(self.list)

    def getTotal(self):
        total = 0
        for item in self.list:
            name, price = item # or price = item[1]
            total = total + price

    def getNumItems(self):
        count = 0
        for c in range(self.list):
            count = self.list + 1
            return count

    def removeItem(self, item)
        #removes the item from the cart's item list

def main():
    item1 = Item("Banana", .69)
    item2 = Item("Eggs", 2.39)
    item3 = Item("Donut", .99)
    c = Cart()
    c.addItem(item1)
    c.addItem(item2)
    c.addItem(item3)
    print "You have %i items in your cart for a total of $%.02f" %(c.getNumItems(), c.getTotal())
    c.removeItem(item3)
    print "You have %i items in your cart for a total of $%.02f" % (c.getNumItems(), c.getTotal())
main()  

