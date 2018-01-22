import cgi
import os
import webapp2

form = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Birthday</title>
    </head>
    <body>
        <form method="post">
            <h1>What is your birthday?</h1>
            <label> Month
                <input type="text" name="month" value="%(month)s">
            </label>
            <label> Day
                <input type="text" name="day" value="%(day)s">
            </label>
            <label> Year
                <input type="text" name="year" value="%(year)s">
            </label>
            <br><br>
            <div style="color: red">%(error)s</div>
            <br>
            <input type="submit" value="Submit">
        </form>
    </body>
</html>
"""

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

def escape_html(s):
    return cgi.escape(s, quote = True)

class MainPage(webapp2.RequestHandler):
    def write_form(self, error="", month="", day="", year=""):
        self.response.write(form % {"error": error, "month": month, "day": day, "year": year})

    def get(self):
        self.write_form()

    def post(self):
        month = self.request.get("month")
        day = self.request.get("day")
        year = self.request.get("year")

        if valid_month(month) and valid_day(day) and valid_year(year):
            self.redirect("/thanks")
        else:
            error = "That's not a valid date!"
            self.write_form(error = error, month = escape_html(month), day = escape_html(day), year = escape_html(year))

class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("That's totally a valid date. Thanks!")

app = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/thanks", ThanksHandler),
], debug=True)

