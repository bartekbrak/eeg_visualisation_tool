# https://github.com/bokeh/bokeh/blob/master/examples/embed/embed_multiple.py
from collections import namedtuple
from collections import defaultdict
from operator import attrgetter
from bokeh.io import vform
from bokeh.models import ColumnDataSource, Range1d, HoverTool, TapTool, \
    Callback
from bokeh.embed import file_html
from bokeh.resources import INLINE
from bokeh.plotting import figure
import itertools
from jinja2 import Environment, PackageLoader
import numpy

from evt.constants import column_name_map, filters_columns
from evt.data_getter import get_from_csv
from evt.utils import get_random_colour, \
    average_yaxis_by_properties_separate
from experiments.js import hover_js, tap_js


def get_progress_bar(y_min, y_max):
    progress_bar_data = {'x': [0, 0], 'y': [y_min, y_max]}
    return ColumnDataSource(data=progress_bar_data, name='progress_bar')


def get_tools(hover_js_, tap_js_, progress_bar_name):
    return (
        HoverTool(tooltips=None, callback=Callback(code=hover_js_)),
        TapTool(action=Callback(code=tap_js_ % progress_bar_name))
    )


def get_figure(tools, video_len, **kwargs):
    f = figure(
        tools=tools,
        toolbar_location=None,
        width=640,
        height=200,
        x_range=Range1d(1, video_len),
        x_axis_type='datetime',
        **kwargs
    )
    f.ygrid.grid_line_alpha = 0.1
    f.xgrid.grid_line_alpha = 0.2
    f.yaxis.minor_tick_line_color = None
    f.yaxis.major_tick_line_color = None
    # f.yaxis.major_label_text_alpha = 0
    return f


def write_file(layout, **template_args):
    env = Environment(loader=PackageLoader('evt', 'templates'))
    template = env.get_template('mytemplate.html')
    html = file_html(layout, INLINE, 'my plot', template, template_args)
    with open('final.html', 'w') as textfile:
        textfile.write(html)


def get_video_data(filename):
    with open(filename) as f:
        return f.read().encode('base64')


def get_data_min_max(grouped_data, key='y_series'):
    list_of_lists = [one[key] for one in grouped_data.values()]
    flat = list(itertools.chain(*list_of_lists))
    return min(flat), max(flat)

Line = namedtuple('Line', 'data, source, description, color')


def main():
    video_len = 10100
    sampling_rate = 333
    video_filename = 'myvideo.mp4'
    no_of_plots = 2
    y_margin = 0.2
    filename = 'tomek.csv'

    data = get_from_csv(filename, column_name_map)
    line_groups = grouper(
        data,
        filters_columns,
        sampling_rate,
        average_yaxis_by_properties_separate
    )
    lines = list(itertools.chain(*line_groups.values()))
    sources = map(attrgetter('data'), lines)
    y_min, y_max = numpy.min(sources) - y_margin, numpy.max(sources) + y_margin
    progress_bar = get_progress_bar(y_min, y_max)

    figures = [
        get_figure(
            tools=get_tools(hover_js, tap_js, progress_bar.name),
            video_len=video_len,
            y_range=Range1d(y_min, y_max)
        )
        for _ in range(no_of_plots)
    ]

    mean = numpy.mean(sources)
    for f_ in figures:
        f_.line(
            'x', 'y', source=progress_bar, line_color='green')
        f_.line(
            range(0, video_len), mean, line_color='orange', line_dash=(3, 6))
        f_.quad(
            top=mean,
            bottom=y_min,
            left=0,
            right=video_len,
            alpha=0.1

        )

    for f_, line in itertools.product(figures, lines):
        f_.line(
            'x', 'y',
            source=line.source,
            color=line.color,
            line_width=2
        )
    layout = vform(*figures)
    template_args = {
        'progress_bar_id': progress_bar.ref['id'],
        'progress_bar_y': progress_bar.data['y'],
        'video_data': get_video_data(video_filename),
        'line_groups': line_groups,
        'default_groups': ('age', )
    }
    write_file(
        layout,
        **template_args
    )


def grouper(data, grouped_by, sampling_rate, grouper_f):
    line_groups = defaultdict(list)
    for description, y_series, filter_names in grouper_f(grouped_by, data):
        x_range = range(0, len(y_series) * sampling_rate, sampling_rate)
        source = ColumnDataSource(data=dict(x=x_range, y=y_series))
        key = ', '.join(filter_names)
        line_groups[key].append(
            Line(y_series, source, description, get_random_colour())
        )
    return line_groups


if __name__ == '__main__':
    main()
