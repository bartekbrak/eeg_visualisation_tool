from base64 import b64encode
from tempfile import NamedTemporaryFile
from ffprobe import FFProbe
from flask import Flask, request, url_for, jsonify
from evt import template_env
from evt.data_getter import get_from_excel
from evt.forms import ServerForm
from evt.standalone import the_meat, render_template

app = Flask(__name__, static_url_path='/evt/templates')


def get_resource_as_string(name, charset='utf-8'):
    # used for in-lining js and css
    with app.open_resource(name) as f:
        return f.read().decode(charset)
template_env.globals['get_resource_as_string'] = get_resource_as_string


@app.route('/')
def server():
    form = ServerForm()
    kwargs = {
        'get_end_user_file_url': url_for('.get_end_user_file'),
        'filesaver': url_for('static', filename='FileSaver.min.js')
    }
    return template_env.get_template('server.html').render(form=form, **kwargs)


def get_video_len(video_data):
    with NamedTemporaryFile() as f:
        f.write(video_data)
        ffropbe = FFProbe(f.name)
        video_length = int(float(ffropbe.video[0].duration) * 1000)
    return video_length


@app.route('/get_end_user_file', methods=('POST',))
def get_end_user_file():
    data_file = request.files['data_file']
    video_content = request.files['clip'].read()
    video_encoded = b64encode(video_content)
    form = ServerForm(request.form)
    video_len = get_video_len(video_content)
    plots = [int(_) for _ in form.data['no_of_plots'].split(',')]
    sheets = get_from_excel(data_file)
    tp = []
    # will truncate sheets if no_of_plots is smaller
    for no_of_plots, sheet in zip(plots, sheets):
        tp.append(dict(no_of_plots=no_of_plots, **sheet))

    layout, template_args = the_meat(
        tp, form.data['sampling_rate'], video_encoded,
        video_len, form.data['y_margin']
    )
    template_args.update(**form.data)
    content = render_template(
        layout,
        template=template_env.get_template('result.html'),
        **template_args
    )

    return jsonify({
        'status': 'ok',
        'content': content
    })


def main():
    app.run(debug=True, port=5002)
