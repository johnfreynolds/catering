import webapp2, jinja2, os, re
from google.appengine.ext import db
from google.appengine.api import memcache
from models import Order, User
from caching import get_items, get_one_order
from webapp2_extras import sessions
import hashutils, sys, json, logging

### Jinja2 Configurations ###
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

### Configuration ###
config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key',}

class Handler(webapp2.RequestHandler):
    """ Utility class for gathering various useful methods that are used by
    most request handlers """

    def get_orders(self, limit, offset):
        """ Get all posts ordered by creation date (descending) """
        query = Order.all().order('-created')
        return query.fetch(limit=limit, offset=offset)

    def get_orders_by_user(self, user, limit, offset):
        """
            Get all posts by a specific user, ordered by creation date
            (descending). The user parameter will be a User object.
        """
        # TODO - filter the query so that only posts by the given user
        query = Order.all().filter("author", user).order('-created')
        return query.fetch(limit=limit, offset=offset)

    def get_user_by_name(self, username):
        """ Get a user object from the db, based on their username """
        user = db.GqlQuery("SELECT * FROM User WHERE username = '%s'" % username)
        if user:
            return user.get()

    def login_user(self, user):
        """ Login a user specified by a User object user """
        user_id = user.key().id()
        self.set_secure_cookie('user_id', str(user_id))

    def logout_user(self):
        """ Logout a user specified by a User object user """
        self.set_secure_cookie('user_id', '')

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        if cookie_val:
            return hashutils.check_secure_val(cookie_val)

    def set_secure_cookie(self, name, val):
        cookie_val = hashutils.make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', 'session=; %s=%s; Path=/' % (name, cookie_val))

    def initialize(self, *a, **kw):
        """
            A filter to restrict access to certain pages when not logged in.
            If the request path is in the global auth_paths list, then the user
            must be signed in to access the path/resource.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.get_by_id(int(uid))
        item_count = self.session.get(('item_count'),**kw)

        if not self.user and self.request.path in auth_paths:
            self.redirect('/login')

    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    def get_items_from_cart(self):
        """ Fetches items from sessions cart """
        item_list = []
        cart_count = self.session.get('add_to_cart_count')
        if not cart_count: return None;
        for i in range(1, cart_count+1):
            item = self.session.get(str(i))
            if item:
                item_list.append(item)
        return item_list



class MainPage(Handler):
    """ This is the main page which uses the server-side templating to display
    all items. Use this in an emergency by changing the route mappings. Its
    currently mapped to /index.html. (This could be used as an admin handler)"""
    def get(self):
        cater_order = get_items(update = True)
        users = User.all()
        t = jinja_env.get_template("mainpage.html")
        response = t.render(users = users, cater_order = cater_order)
        self.response.write(response)

class AnotherMainPage(Handler):
    """ This is the main page which uses the client-side handlebars for
    templating. Currently mapped to /"""
    def get(self):
        t = jinja_env.get_template("main2.html")
        response = t.render()
        self.response.write(response)

class JSONHandler(Handler):
    def get(self):
        cater_order = get_items(True)
        self.response.headers['Content-type'] = 'application/json'
        single_order_json = []
        for t in cater_order:
            single_order_json.append({"id": t.unq_id, "title": t.title})
        self.write(json.dumps(single_order_json))

class CartHandler(Handler):
    """ This will be a function to allow the user to see what they have ordered
    from their selections within the menu. """
    def get(self, username=""):
        # render the page
        item_list = self.get_items_from_cart()
        t = jinja_env.get_template("cart.html")
        response = t.render(item_list = item_list)
        self.response.out.write(response)

class OrderHandler(Handler):
    def render_form(self, unq_id="", name="", price="", qty="", body=""):
        """ Render the new post form with or without an error, based on parameters """
        t = jinja_env.get_template("menu.html")
        response = t.render(unq_id=unq_id, name=product_name, price=price, qty=qty, body=body)
        self.response.out.write(response)

    def get(self):
        user = get_user_by_name()
        if user:
            self.response.headers['Content-type'] = 'application/json'
            get_current_add_count = int(self.session.get('add_to_cart_count'))
            unq_id = self.request.get.unq_id
            name = self.request.get.product_name
            price = self.request.get.price
            qty = self.request.get.qty
            body = self.request.get.body
            get_current_add_count += 1
            self.session[get_current_add_count] = {"qty": int(qty),
                                                   "name": product_name,
                                                   "unq_id": unq_id,
                                                   "price": price,
                                                   "subtotal": price * qty}

            current_cart_items = int(self.session.get("item_count"))
            update_cart_items = current_cart_items + int(qty)
            self.session["item_count"] = updated_cart_items
            self.session["add_to_cart_count"] = get_current_add_count
            self.write(json.dumps({"status" : 1, "msg" : "Order added. <a href='/cart'><span class='label-success'>View Cart</span></a>"}))
        else:
            self.write(json.dumps({"status" : 0, "msg" : "Please <a href='/login'</span> <span class='label label-important'>Login</span> </a>to start your menu order!"}))
        self.render_form()

class CheckoutHandler(Handler):
    def get(self, id):
        """ Render a page with what the customer has ordered """
        item_list = self.get_items_from_cart()
        if item_list:
            for i in item_list:
                order = Order(qty = int(i["qty"]), user = user, unq_id = int(i["unq_id"]))
                order.put()
                logging.error("Attempting to put information into database")
        else:
            logging.error("Any updates to this order have been missed")
        logging.error("Order has been added for user: %s" % username)
        self.session["add_to_cart_count"] = 0
        t = jinja_env.get_template("completeorder.html")
        response = t.render(post=post)

class SignupHandler(Handler):
    def validate_username(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        if USER_RE.match(username):
            return username
        else:
            return ""

    def validate_password(self, password):
        PWD_RE = re.compile(r"^.{3,20}$")
        if PWD_RE.match(password):
            return password
        else:
            return ""

    def validate_verify(self, password, verify):
        if password == verify:
            return verify

    def validate_email(self, email):
        # allow empty email field
        if not email:
            return ""

        EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
        if EMAIL_RE.match(email):
            return email

    def get(self):
        t = jinja_env.get_template("signup.html")
        response = t.render(errors={})
        self.response.out.write(response)

    def post(self):
        """
            Validate submitted data, creating a new user if all fields are valid.
            If data doesn't validate, render the form again with an error.

            This code is essentially identical to the solution to the Signup portion
            of the Formation assignment. The main modification is that we are now
            able to create a new user object and store it when we have valid data.
        """

        submitted_username = self.request.get("username")
        submitted_password = self.request.get("password")
        submitted_verify = self.request.get("verify")
        submitted_email = self.request.get("email")
        addr1 = self.request.get("addr1")
        addr2 = self.request.get("addr2")
        city = self.request.get("city")
        state = self.request.get("state")
        zip = int(self.request.get("zip"))

        username = self.validate_username(submitted_username)
        password = self.validate_password(submitted_password)
        verify = self.validate_verify(submitted_password, submitted_verify)
        email = self.validate_email(submitted_email)

        errors = {}
        existing_user = self.get_user_by_name(username)
        has_error = False

        if existing_user:
            errors['username_error'] = "A user with that username already exists"
            has_error = True
        elif (username and password and verify and (email is not None) ):

            # create new user object and store it in the database
            pw_hash = hashutils.make_pw_hash(username, password)
            user = User(username=username, pw_hash=pw_hash, email=email, addr1=addr1, addr2=addr2, city=city, state=state, zip=zip)
            user.put()
            # login our new user
            self.login_user(user)
        else:
            has_error = True

            if not username:
                errors['username_error'] = "That's not a valid username"

            if not password:
                errors['password_error'] = "That's not a valid password"

            if not verify:
                errors['verify_error'] = "Passwords don't match"

            if email is None:
                errors['email_error'] = "That's not a valid email"

        if has_error:
            t = jinja_env.get_template("signup.html")
            response = t.render(username=username, email=email, addr1=addr1, addr2=addr2, city=city, state=state, zip=zip, errors=errors)
            self.response.out.write(response)
        else:
            self.redirect('/menu')

class LoginHandler(Handler):

    # TODO - The login code here is mostly set up for you, but there isn't a template to log in

    def render_login_form(self, username="", username_error="", password="", password_error="", error=""):
        """ Render the login form with or without an error, based on parameters """
        t = jinja_env.get_template("login.html")
        response = t.render(username=username, username_error=username_error, password=password, password_error=password_error, error=error)
        self.response.out.write(response)

    def get(self):
        self.render_login_form()

    def post(self):
        submitted_username = self.request.get("username")
        submitted_password = self.request.get("password")

        # get the user from the database
        user = self.get_user_by_name(submitted_username)

        if not user:
            self.render_login_form(username=submitted_username, password=submitted_password, username_error = "Invalid username")
            #self.redirect('/signup')
        elif hashutils.valid_pw(submitted_username, submitted_password, user.pw_hash):
            self.login_user(user)
            self.redirect('/menu')
        else:
            self.render_login_form(username=submitted_username, password=submitted_password, password_error = "Invalid password")

class LogoutHandler(Handler):
    def get(self):
        self.logout_user()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/mainpage', MainPage),
    ('/cart', CartHandler),
    ('/menu', OrderHandler),
    ('/all.json', JSONHandler),
    ('/checkout', CheckoutHandler),
    ('/signup', SignupHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler)
], debug=True, config=config)

# A list of paths that a user must be logged in to access
auth_paths = ['/menu', '/cart']
