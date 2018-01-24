import hashlib, hmac
import jinja2
import os
import re
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

SECRET = "imsosecret"
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split("|")[0]
    if h == make_secure_val(val):
        return val

# Main page handler
class Main(Handler):
    def get(self):
        self.response.headers["Content-Type"] = "text/html"
        visits = 0
        visits_cookie_val = self.request.cookies.get("visits")
        if visits_cookie_val:
            visits_val = check_secure_val(visits_cookie_val)
            if visits_val:
                visits = int(visits_val)
            else:
                visits = 0

        visits += 1
        self.response.headers.add_header("Set-Cookie", "visits=%s" % make_secure_val(str(visits)))
        if visits > 10000:
            self.write("You are the best ever!")
        else:
            self.write("You've been here %s times!" % visits)

app = webapp2.WSGIApplication([
    ("/", Main),
], debug=True)

