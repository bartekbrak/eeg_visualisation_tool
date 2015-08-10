from base64 import b64encode
from flask import Flask, request, url_for, jsonify
from evt import template_env
from evt.constants import column_name_map
from evt.data_getter import get_from_excel
from evt.forms import ServerForm
from evt.standalone import the_meat, render_template

app = Flask(__name__, static_url_path='/evt/templates')


@app.route('/')
def server():
    form = ServerForm()
    kwargs = {
        'get_end_user_file_url': url_for('.get_end_user_file'),
        'filesaver': url_for('static', filename='FileSaver.min.js')
    }
    return template_env.get_template('server.html').render(form=form, **kwargs)


@app.route('/get_end_user_file', methods=('POST',))
def get_end_user_file():
    data_file = request.files['data_file']
    video_data = b64encode(request.files['clip'].read())
    data = get_from_excel(data_file, column_name_map)
    form = ServerForm(request.form)
    video_len = 10100

    layout, template_args = the_meat(
        data, form.data['no_of_plots'], form.data['sampling_rate'], video_data,
        video_len, form.data['y_margin']
    )
    template_args.update(**form.data)
    content = render_template(
        layout,
        form.data['plot_title'],
        template=template_env.get_template('mytemplate.html'),
        **template_args
    )

    return jsonify({
        'status': 'ok',
        'content': content
    })


def main():
    app.run(debug=True, port=5002)
