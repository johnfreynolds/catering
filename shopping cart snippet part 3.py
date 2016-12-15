class Item(object):
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Cart(dict):
    def add_item(self, item, amount):
        try:
            self[item.name][1] += amount
        except IndexError:
            self.update({
                item.name: [item.price, amount]
            })

class User(object):
    def __init__(self, name):    
        self.name = name
        self.carts = [Cart()]

    def add_cart(self):
        self.carts.append(Cart())

    def add_item(self, item, amount, cart_index=0):
        self.carts[cart_index].add_item(item, amount)

def main():
    apple = Item('apple', 7.8)

    john = User('John')

    # I would choose `john.add_item(apple, 5, 1)`
    # or `john.carts[0].add_item(apple, 5)`
    # Not both.
    john.add_item(apple, 5)
    print("John's first cart has: {}".format(john.carts[0]))

    john.carts[0].add_item(Item('pear', 5), 6)
    print("John's first cart has: {}".format(john.carts[0]))

    john.add_cart()
    john.add_item(apple, 5, 1)
    print("John's second cart has: {}".format(john.carts[1]))

if __name__ == '__main__':
    main()