# https://github.com/bokeh/bokeh/blob/master/examples/embed/embed_multiple.py
from collections import namedtuple, defaultdict
from datetime import datetime
from operator import attrgetter
from bokeh.io import vform
from bokeh.models import ColumnDataSource, Range1d, HoverTool, Callback
from bokeh.embed import file_html
from bokeh.resources import INLINE
from bokeh.plotting import figure
import itertools
import numpy
from evt import template_env

from evt.constants import column_name_map, filters_columns, data_column_name
from evt.data_getter import get_from_csv
from evt.utils import get_random_colour, average_yaxis_by_properties_separate


def get_progress_bar():
    progress_bar_y = [-10, 10]
    progress_bar_data = {'x': [0, 0], 'y': progress_bar_y}
    return (
        progress_bar_y,
        ColumnDataSource(data=progress_bar_data, name='progress_bar')
    )


def get_tools():
    return HoverTool(
        tooltips=None,
        callback=Callback(
            code="evt.hover_position=cb_data['geometry']['x'] / 1000;"
        )
    ),


def get_figure(tools, video_len, **kwargs):
    f = figure(
        y_axis_label=u'Skala motywacji',
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
    f.yaxis.axis_label_text_font_size = '12px'
    # f.yaxis.major_label_text_alpha = 0
    return f


def render_template(layout, plot_title, template, **template_args):
    return file_html(layout, INLINE, plot_title, template, template_args)


def write_file(html, out_filename):
    with open(out_filename, 'w') as textfile:
        textfile.write(html)


def get_video_data(filename):
    with open(filename) as f:
        return f.read().encode('base64')


Line = namedtuple('Line', 'data, source, description, color')


def standalone():
    video_len = 10100
    sampling_rate = 333
    video_filename = 'myvideo.mp4'
    no_of_plots = 2
    plot_title = 'Prototype {date}, plots: {no}'.format(
        date=datetime.now().strftime('%Y.%m.%d'),
        no=no_of_plots
    )
    out_filename = 'evt_3plots.html'
    y_margin = 0.2
    filename = 'tomek.csv'

    # simple calculations
    data = get_from_csv(filename, column_name_map)
    video_data = get_video_data(video_filename)
    layout, template_args = the_meat(
        data, no_of_plots, sampling_rate, video_data, video_len, y_margin
    )
    content = render_template(
        layout,
        plot_title,
        template=template_env.get_template('mytemplate.html'),
        **template_args
    )
    write_file(content, out_filename)


def the_meat(
        data, no_of_plots, sampling_rate, video_data, video_len, y_margin):
    mean = get_mean(data)
    line_groups_per_plot = []
    figures = []
    progress_bar_y, progress_bar = get_progress_bar()
    for _ in range(no_of_plots):
        line_groups = grouper(
            data,
            filters_columns,
            sampling_rate,
            average_yaxis_by_properties_separate
        )
        line_groups_per_plot.append(line_groups)
        lines = list(itertools.chain(*line_groups.values()))
        sources = map(attrgetter('data'), lines)
        y_min, y_max = \
            numpy.min(sources) - y_margin, numpy.max(sources) + y_margin

        f = get_figure(
            tools=get_tools(),
            video_len=video_len,
            y_range=Range1d(y_min, y_max)
        )
        figures.append(f)
        draw_secondary_elements(f, mean, progress_bar, video_len, y_min)
        for line in lines:
            f.line(
                'x', 'y',
                source=line.source,
                color=line.color,
                line_width=2
            )
    layout = vform(*figures)
    template_args = {
        'progress_bar_id': progress_bar.ref['id'],
        'progress_bar_y': progress_bar_y,
        'video_data': video_data,
        'line_groups_per_plot': line_groups_per_plot,
    }
    return layout, template_args


def get_mean(data):
    return numpy.mean([row[data_column_name] for row in data])


def draw_secondary_elements(f, mean, progress_bar, video_len, y_min):
    f.line('x', 'y', source=progress_bar, line_color='green')
    f.line(range(0, video_len), mean, line_color='orange', line_dash=(3, 6))
    f.quad(
        top=mean,
        bottom=y_min,
        left=0,
        right=video_len,
        alpha=0.1

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
    standalone()
