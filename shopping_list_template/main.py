import jinja2
import os
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))


class MainHandler(Handler):
    def get(self):
        items = self.request.get_all("food")
        self.render("shopping.html", items = items)


class FizzBuzzHandler(Handler):
    def get(self):
        n = self.request.get("n")
        if n and n.isdigit():
            n = int(n)
        self.render("fizzbuzz.html", n = n)

app = webapp2.WSGIApplication([
    ("/", MainHandler),
    ("/fizzbuzz", FizzBuzzHandler),
], debug=True)
