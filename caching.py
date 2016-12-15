import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from models import Order, User

def get_items(update = False):
    key = "food"
    cater_order = memcache.get("key")
    if cater_order is None or update:
        logging.error("DB QUERY FOR CATERING ORDER")
        cater_order = db.GqlQuery("SELECT * FROM Order ORDER BY time_of_order")
        cater_order = list(cater_order)
        memcache.set(key, cater_order)
    return cater_order

def get_one_order(item_id, update = False):
    key = item_id
    single_order = memcache.get(key)
    if single_order is None or update:
        logging.error("DB QUERY FOR A SINGLE ORDER")
        single_order = Order.all().filter("cater_order_id =", int(item_id)).get()
        memcache.set(key, single_order)
    return single_order
