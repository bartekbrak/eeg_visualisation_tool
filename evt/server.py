from flask import Flask, request
from evt import template_env
from evt.constants import column_name_map
from evt.data_getter import get_from_f
from evt.forms import ServerForm

app = Flask(__name__)


@app.route('/', methods=("GET", "POST"))
def server():
    form = ServerForm(request.form)
    if request.method == "POST":
        f = request.files['csv']
        data = get_from_f(f, column_name_map)
        print data
        return "blaaa"
    return template_env.get_template('server.html').render(form=form)

def main():
    app.run(debug=True)
