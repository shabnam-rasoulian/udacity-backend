import jinja2
import os
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
months_abbvs = dict((m[:3].lower(), m) for m in months)
def valid_month(month):
    if month:
        return months_abbvs.get(month[:3].lower())

def valid_day(day):
    if day and day.isdigit():
        day = int(day)
        if day > 0 and day <= 31:
            return day

def valid_year(year):
    if year and year.isdigit():
        year = int(year)
        if year > 1900 and year < 2020:
            return year


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
        self.render("birthday.html")

    def post(self):
        month = self.request.get("month")
        day = self.request.get("day")
        year = self.request.get("year")

        if valid_month(month) and valid_day(day) and valid_year(year):
            self.redirect("/thanks")
        else:
            error = "That's not a valid date!"
            self.render("birthday.html", error = error, month = month, day = day, year = year)

class ThanksHandler(Handler):
    def get(self):
        self.write("That's totally a valid date. Thanks!")

app = webapp2.WSGIApplication([
    ("/", MainHandler),
    ("/thanks", ThanksHandler),
], debug=True)

