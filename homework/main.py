import hashlib, hmac
import jinja2
import os
import re
import random, string
import webapp2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

# Main class to implement required functions
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

# Main page handler
class Main(Handler):
    def get(self):
        self.write("Hello Udacity!")

#####################################
# Encode the text to rot13
class Rot13(Handler):
    def get(self):
        self.render("rot13.html")

    def post(self):
        text = self.request.get("text")
        if text:
            text = text.encode("rot13")
        self.render("rot13.html", text = text)

####################################
# Sign up page
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    return EMAIL_RE.match(email)


class SignupHandler(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")
        
        have_error = False
        params = {"username": self.username, "email": self.email}

        if not valid_username(self.username):
            have_error = True
            params["username_error"] = "That's not a valid username."

        if not valid_password(self.password):
            have_error = True
            params["password_error"] = "That wasn't a valid password."

        if self.verify != self.password:
            have_error = True
            params["verify_error"] = "Your passwords didn't match."

        if self.email and not valid_email(self.email):
            have_error = True
            params["email_error"] = "That's not a valid email."

        if have_error:
            self.render("signup.html", **params)
        else:
            self.done()

    def done(self):
        raise NoErrorImplement

class SignUp(SignupHandler):
    def done(self):
        self.redirect("/unit2/welcome?username=" + self.username)

class Unit2Welcome(Handler):
    def get(self):
        username = self.request.get("username")
        self.render("welcome.html", username = username)

################################
# The login app
SECRET = "aQaGwNszBTxX0EKA929FX1aj74XwfNcq"
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split("|")[0]
    if h == make_secure_val(val):
        return val

def make_salt():
    return "".join(random.choice(string.letters) for i in range(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s,%s" % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(",")[1]
    return h == make_pw_hash(name, pw, salt) 

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

class Register(SignupHandler):
    def done(self):
        u = User.all().filter("name = ", self.username).get()
        if not u:
            user = User(name = self.username, pw_hash = make_pw_hash(self.username, self.password), email = self.email)
            user.put()
            self.response.headers.add_header("Set-Cookie", "user_id=%s; path=/" % make_secure_val(str(user.key().id())))
            self.redirect("/unit3/welcome")
        else:
            params = {"username": self.username, "email": self.email, "username_error": "That user already exists."}
            self.render("signup.html", **params)

class Login(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        user = User.all().filter("name = ", username).get()
        if user and valid_pw(username, password, user.pw_hash):
            self.response.headers.add_header("Set-Cookie", "user_id=%s; path=/" % make_secure_val(str(user.key().id())))
            self.redirect("/unit3/welcome")
        else:
            error = "Invalid login"
            self.render("login.html", error = error)

class Logout(Handler):
    def get(self):
        self.response.headers.add_header("Set-Cookie", "user_id= ; path=/")
        self.redirect("/signup")

class Unit3Welcome(Handler):
    def get(self):
        cookie_val = self.request.cookies.get("user_id")
        if cookie_val:
            val = check_secure_val(cookie_val)
            if val:
                key = db.Key.from_path("User", int(val))
                user = db.get(key) 
                self.render("welcome.html", username = user.name)
            else:
                self.redirect("/signup")

################################
#The blog app
class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        self.render("blog.html", posts = posts)

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Blog(subject = subject, content = content)
            p.put() 
            self.redirect("/blog/" + str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", error = error, subject = subject, content = content)

class Post(Handler):
    def get(self, id):
        key = db.Key.from_path("Blog", int(id))
        post = db.get(key)
        self.render("post.html", post = post)

app = webapp2.WSGIApplication([
    ("/", Main),
    ("/unit2/rot13", Rot13),
    ("/unit2/signup", SignUp),
    ("/unit2/welcome", Unit2Welcome),
    ("/blog", BlogHandler),
    ("/blog/newpost", NewPost),
    ("/blog/([0-9]+)", Post),
    ("/signup", Register),
    ("/login", Login),
    ("/logout", Logout),
    ("/unit3/welcome", Unit3Welcome),
], debug=True)

