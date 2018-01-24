import cgi
import os
import webapp2

form = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shopping List</title>
    </head>
    <body>
        <form method="post">
            <h2>Add a food</h2>
            <input type="text" name="food" value="">
            %s
            <input type="submit" value="Add">
        </form>
    </body>
</html>
"""

hidden_html = """
    <input type="hidden" name="food" value="%s">
"""

item_html = """
    <li>%s</li>
"""

shopping_html = """
    <br><br>
    <h2>Shopping list:</h2>
    <ul>
    %s
    </ul>
"""

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(form % "")

    def post(self):
        items = self.request.get_all("food")
        output = form
        hiddens = ""
        shopping = ""
        if items:
            for item in items:
                item = cgi.escape(item, quote = True)
                hiddens += hidden_html % item
                shopping += item_html % item
            
            output = form % hiddens
            shopping_list = shopping_html % shopping
            output += shopping_list

        self.response.write(output)


app = webapp2.WSGIApplication([
    ("/", MainPage),
], debug=True)

