class Item(object):
    def __init__(self,itemname,itemprice):
        self.__itemname = itemname
        self.__itemprice = itemprice

    def GetItemName(self):
        return self.__itemname

    def GetItemPrice(self):
        return self.__itemprice

    def ChangeItemPrice(self,newprcie):
        self.__itemprice = newprcie

class Cart(dict):      #cart dict format:  {itemname:[price,number]}
    def ShowCart(self):
        return self   

class User(object):
    def __init__(self, name):    
        self.name = name
        self.__cartlist = {}
        self.__cartlist[0] = Cart()

    def AddCart(self):
        self.__cartlist[len(self.__cartlist)] = Cart()

    def GetCart(self, cartindex = 0):
        return self.__cartlist[cartindex]

    def BuyItem(self, item, itemnum, cartindex = 0):
        try:
            self.__cartlist[cartindex][item.GetItemName()][1] += itemnum
        except:
            self.__cartlist[cartindex].update({item.GetItemName():[item.GetItemPrice(),itemnum]})

    def BuyCancle(self, itemname, itemnum, cartindex = 0):
        pass

if __name__ == '__main__': 

    item1 = Item('apple', 7.8)
    item2 = Item('pear', 5)   

    user1 = User('John')

    user1.BuyItem(item1, 5)
    print("user1 cart0 have: %s" % user1.GetCart(0).ShowCart())

    user1.BuyItem(item2, 6)
    print("user1 cart0 have: %s" % user1.GetCart(0).ShowCart())


    user1.AddCart()
    user1.BuyItem(item1, 5, 1)
    print("user1 cart1 have: %s" % user1.GetCart(1).ShowCart())