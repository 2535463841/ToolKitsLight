import flask

from flask import views
from flask import current_app


INDEX_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>FLuent Http Server</title>
    </head>
    <body>
        <h3>Fluent Http Server</h3>
        <p>Please set your rules</p>
    </body>
</html>
"""

class IndexView(views.MethodView):

    def get(self):
        return INDEX_HTML
