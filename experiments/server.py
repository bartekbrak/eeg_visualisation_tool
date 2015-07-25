from flask import Flask, request
from evt.constants import column_name_map
from evt.data_getter import get_from_f

app = Flask(__name__)
html = '''
<form action="" method="POST" enctype="multipart/form-data">
    <input type="file" name="csv"><br>
    <input type="submit">
</form>
'''


@app.route('/', methods=("GET", "POST"))
def main():
    if request.method == "POST":
        f = request.files['csv']
        data = get_from_f(f, column_name_map)
        print data
        return "blaaa"
    return html
app.run(debug=True)
