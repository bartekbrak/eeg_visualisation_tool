# https://github.com/bokeh/bokeh/blob/master/examples/embed/embed_multiple.py
from bokeh.io import vform
from bokeh.models import ColumnDataSource, Range1d, HoverTool, TapTool, \
    Callback
from bokeh.embed import file_html
from bokeh.resources import INLINE
from bokeh.plotting import figure
from jinja2 import Environment, PackageLoader

from evt.constants import column_name_map
from evt.data_getter import get_from_csv
from evt.utils import group_by, arithmetic_mean
from experiments.js import hover_js, tap_js


def get_progress_bar():
    progress_bar_data = {'x': [0, 0], 'y': [-3, 3]}
    return ColumnDataSource(data=progress_bar_data, name='progress_bar')


def get_tools(hover_js_, tap_js_, progress_bar_name):
    return (
        HoverTool(tooltips=None, callback=Callback(code=hover_js_)),
        TapTool(action=Callback(code=tap_js_ % progress_bar_name))
    )


def get_figure(tools, video_len):
    f = figure(
        tools=tools,
        toolbar_location=None,
        width=640,
        height=200,
        x_range=Range1d(1, video_len),
        y_range=Range1d(0, 1),
        x_axis_type='datetime',
    )
    f.ygrid.grid_line_alpha = 0.1
    f.xgrid.grid_line_alpha = 0.2
    f.yaxis.minor_tick_line_color = None
    f.yaxis.major_tick_line_color = None
    # f.yaxis.major_label_text_alpha = 0
    return f


def write_file(layout, progress_bar, grouped_plot_data):
    env = Environment(loader=PackageLoader('evt', 'templates'))
    template = env.get_template('mytemplate.html')
    kwargs = {
        'progress_bar_id': progress_bar.ref['id'],
        'progress_bar_y': progress_bar.data['y'],
        'video_data': open('myvideo.mp4', 'rb').read().encode('base64'),
        'grouped_plot_data': grouped_plot_data
    }
    html = file_html(layout, INLINE, 'my plot', template, kwargs)
    with open('final.html', 'w') as textfile:
        textfile.write(html)


def add_column_data_source(sampling_rate, grouped):
    for group_description, group in grouped.iteritems():
        y_series = group['y_series']
        x_range = [x * sampling_rate for x, _ in enumerate(y_series)]
        cds = ColumnDataSource(data=dict(x=x_range, y=y_series))
        group['source'] = cds


def get_mean(data):
    sub_means = [arithmetic_mean(*person['as']) for person in data]
    return arithmetic_mean(*sub_means)


def main():
    data = get_from_csv('tomek.csv', column_name_map)
    # grouped_by = ('age', 'sex', 'favourite_brand')
    grouped_plot_data = group_by(('age',), data)
    video_len = 10100
    sampling_rate = 333

    progress_bar = get_progress_bar()
    f = get_figure(
        tools=get_tools(hover_js, tap_js, progress_bar.name),
        video_len=video_len
    )
    f2 = get_figure(
        tools=get_tools(hover_js, tap_js, progress_bar.name),
        video_len=video_len
    )
    f.line('x', 'y', source=progress_bar, line_color='green')
    f2.line('x', 'y', source=progress_bar, line_color='green')
    # mean = ColumnDataSource(data=dict(x=range(0,video_len), y=get_mean(())))
    # f.line('x', 'y', source=mean, line_color='orange')
    f.line(range(0, video_len), get_mean(data), line_color='orange')
    f2.line(range(0, video_len), get_mean(data), line_color='orange')

    add_column_data_source(sampling_rate, grouped_plot_data)
    for v in grouped_plot_data.values():
        f.line(
            'x', 'y',
            source=v['source'],
            color=v['color'],
            line_width=1,
        )
    #
    # f2.line(
    #     'x', 'y',
    #     source=lines[1],
    #     color=get_random_colour(),
    #     line_width=1,
    # )

    layout = vform(f, f2)

    write_file(layout, progress_bar, grouped_plot_data)
