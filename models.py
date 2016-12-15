from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()
    addr1 = db.StringProperty()
    addr2 = db.StringProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    zip = db.IntegerProperty()

class Order(db.Model):
    time_of_order = db.DateTimeProperty(auto_now_add = True)
    unq_id = db.StringProperty(required = True)
    product_name = db.TextProperty()
    price = db.TextProperty()
    qty = db.IntegerProperty()
    body = db.TextProperty()
