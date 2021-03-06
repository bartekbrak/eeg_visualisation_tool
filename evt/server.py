import itertools
import json
import os
import pickle
import traceback
from argparse import ArgumentParser
from base64 import b64encode
from itertools import chain
from operator import attrgetter
from tempfile import NamedTemporaryFile

import numpy
import pkg_resources
from bokeh.embed import file_html, components
from bokeh.io import vform
from bokeh.models import Callback, ColumnDataSource, HoverTool, Range1d
from bokeh.plotting import figure
from bokeh.resources import Resources
from ffprobe import FFProbe
from flask import Flask, jsonify, request, url_for
from markdown import markdown

from evt import memory, template_env
from evt.constants import palette_pickle, gauges_pickle
from evt.data_getter import continuous_array, get_from_excel, get_mean, grouper
from evt.forms import ServerForm, GaugeColors
from evt.models import Line
from evt.utils import (
    average_yaxis_by_properties_separate,
    distinct_colors,
    get_pickled_colors,
    color_pairs, uniform_list, SetEncoder)
from collections import defaultdict

app = Flask(__name__, static_url_path='/evt/templates')


def get_resource_as_string(name, charset='utf-8'):
    # used for in-lining js and css
    with app.open_resource(name) as f:
        return f.read().decode(charset)


template_env.globals['get_resource_as_string'] = get_resource_as_string


@app.route('/')
def server():
    form = ServerForm(
        colors=get_pickled_colors(palette_pickle, distinct_colors[:20]),
        no_of_plots=[
            GaugeColors(colors=get_pickled_colors(gauges_pickle, color_pairs[:2])),
        ]
    )
    kwargs = {
        'get_end_user_file_url': url_for('.get_end_user_file'),
        'filesaver': url_for('static', filename='FileSaver.min.js'),
        'color_picker': url_for('static', filename='jqColorPicker.min.js'),
        'pkg_version': pkg_resources.get_distribution('evt').version
    }
    return template_env.get_template('producer.html').render(form=form,
                                                             **kwargs)


@memory.cache
def get_video_len(video_data):
    print 'running get_video_len'
    with NamedTemporaryFile() as f:
        f.write(video_data)
        ffprobe = FFProbe(f.name)
        durations = [_.duration for _ in chain(ffprobe.audio, ffprobe.streams)]

        durations = [float(_) * 1000 for _ in durations]
    return max(durations), durations


@app.route('/get_end_user_file', methods=('POST',))
def get_end_user_file():
    logger = []
    try:
        data_file = request.files['data_file']
        video_content = request.files['clip'].read()
        logger += ['Video length in bytes: %s\n' % len(video_content)]
        video_encoded = b64encode(video_content)
        form = ServerForm(request.form)

        pickle.dump(form.data['colors'], open(palette_pickle, 'w'))
        # pickle.dump(form.data['no_of_plots'][0], open(gauges_pickle, 'w'))
        video_len, all_video_lens = get_video_len(video_content)
        logger += ['duration: %s out of %s\n' % (video_len, all_video_lens)]
        # plots = [int(_) for _ in form.data['no_of_plots'].split(',')]
        sheets = get_from_excel(data_file)
        logger += ['sheets: %s' % [
            [_['filter_column_names'], _['title']]
            for _ in sheets
            ]]
        plots = []
        # will truncate sheets if no_of_plots is smaller
        for no_of_plots, sheet in zip(form.data['no_of_plots'], sheets):
            plots.append(dict(no_of_plots=no_of_plots, **sheet))
        _validate_data_length(form.data['sampling_rate'], sheets, video_len)

        validate_sheets_uniformity(plots, logger)

        layout, template_args = the_meat(
            plots=plots,
            sampling_rate=form.data['sampling_rate'],
            video_data=video_encoded,
            y_margin=form.data['y_margin'],
            colors=form.data['colors'],
        )
        template_args.update(**form.data)
        client_info = markdown(form.data['client_info_markdown'].replace(
            '\r', '\n').replace('\n', '\n\n'))
        content = render_template(
            layout,
            template=template_env.get_template('evt/evt.jinja2'),
            client_info=client_info,
            **template_args
        )
        return jsonify(status='ok', content=content, traceback=logger)
    except Exception as e:
        return jsonify(
            status='error',
            traceback=str('\n'.join(logger)) + '\n' + traceback.format_exc(),
            message=e.message
        )


def main():
    app.run(debug=True, port=5002)


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
        ),
        names=['total'],
        line_policy='interp',
        # debug
        # tooltips=[
        #     ("index", "$index $data_x, $data_y $vx--$vy"),
        #     ("data_y", "$data_y"),
        # ]
    ),


def get_figure(x_axis_len, **kwargs):
    f = figure(
        toolbar_location=None,
        plot_width=680,
        plot_height=151,
        # FIXME: this really should be 0, causes 0/1 to be displayed on axis
        x_range=Range1d(1, x_axis_len),
        x_axis_type='datetime',
        logo=None,
        **kwargs
    )
    f.yaxis.minor_tick_line_color = None
    f.yaxis.major_tick_line_color = None
    f.yaxis.axis_line_color = None
    f.yaxis.major_label_text_font_style = 'bold'
    f.yaxis.major_label_text_color = '#e2bad5'

    f.xaxis.axis_line_color = None
    f.xaxis.major_tick_line_color = None
    f.xaxis.axis_label_text_font_size = '12px'
    f.xaxis.major_label_text_font_style = 'bold'
    f.xaxis.major_label_text_color = '#e2bad5'
    f.h_symmetry = False
    f.v_symmetry = False
    f.min_border_left = 40
    f.min_border_top = 18
    f.min_border_bottom = 10
    f.min_border_right = 0
    f.outline_line_alpha = 0
    f.xgrid.grid_line_color = '#dddddd'
    f.xgrid.grid_line_width = 1
    f.ygrid.grid_line_color = '#dddddd'
    f.ygrid.grid_line_width = 1
    return f


def render_template(layout, plot_title, template, **template_args):
    return file_html(layout, Resources(mode="inline", minified=False),
                     plot_title, template, template_args)


def write_file(html, out_filename):
    with open(out_filename, 'w') as textfile:
        textfile.write(html)


def parse_args():
    here = os.path.dirname(os.path.realpath(__file__))
    parser = ArgumentParser()
    parser.add_argument(
        '-d',
        '--data',
        default=os.path.join(here, '..', 'data/data.xlsx')
    )
    parser.add_argument(
        '-v',
        '--video',
        default=os.path.join(here, '..', 'data/video.mp4')
    )
    parser.add_argument(
        '-c',
        '--clean',
        action='store_true'
    )
    return parser.parse_args()


def standalone():
    args = parse_args()
    if args.clean:
        print 'wiping cache'
        memory.clear()

    video_content = open(args.video).read()
    video_encoded = b64encode(video_content)
    video_len, all_video_lens = get_video_len(video_content)
    print 'duration: %s out of %s' % (video_len, all_video_lens)
    plots_ = [
        {
            'colors': ['#e8536b', '#bbc171',]
        },
        {
            'colors': ['#97d3db', '#f0e27c']
        },
    ]
    sheets = get_from_excel(args.data)

    plots = []
    # will truncate sheets if no_of_plots is smaller
    for no_of_plots, sheet in zip(plots_, sheets):
        plots.append(dict(no_of_plots=no_of_plots, **sheet))

    rate = 100
    y_margin = 0.2

    _validate_data_length(rate, sheets, video_len)
    validate_sheets_uniformity(plots, '')
    layout, template_args = the_meat(plots, rate, video_encoded, y_margin)
    content = render_template(
        layout,
        '',
        template=template_env.get_template('evt/evt.jinja2'),
        client_info=markdown(
            u'Nazwa Klienta:  \n**Nazwa Klienta**\n\n'
            u'Nazwa Badania:  \n**Nazwa Badania**\n\n'
            u'Data:  \n**2015-08-08**\n\n'
            u'Proba:  \n**100**'),
        **template_args
    )
    outfile_filename = 'data/out.html'
    write_file(content, outfile_filename)
    print(outfile_filename + ' written')


def _validate_data_length(rate, sheets, video_len):
    for sheet in sheets:
        data_covers = len(sheet['data'][0]['as']) * rate
        # notice addition of one rate
        assert_complaint = 'More data than video: %s > %s' % (
            data_covers, video_len)
        assert data_covers < video_len + rate, assert_complaint


def the_meat(plots, sampling_rate, video_data, y_margin, colors=distinct_colors):
    line_groups_per_plot = []
    totals = []
    # valency is misleading, this is just average
    valencies = []
    figures = []
    progress_bar_y, progress_bar = get_progress_bar()
    titles = []
    gauge_colours = []
    group_ids = defaultdict(lambda: defaultdict(list))
    for plot in plots:
        x_axis_len = len(plot['data'][0]['as']) * sampling_rate + sampling_rate
        for color_below, color_above in zip(*[iter(plot['no_of_plots']['colors'])] * 2):
            titles.append(plot['title'])
            gauge_colours.append({
                'color_above': color_above,
                'color_below': color_below
            })
            lines = []
            total = get_mean(plot['data'], axis=0)
            if plot['filter_column_names']:
                line_groups = grouper(
                    plot['data'],
                    plot['filter_column_names'],
                    sampling_rate,
                    average_yaxis_by_properties_separate,
                    itertools.cycle(colors)
                )
                for group_name, lines in line_groups.items():
                    for line in lines:
                        description = line.description[group_name]
                        group_ids[group_name][description].append(line.source._id)
                line_groups_per_plot.append(line_groups)
                lines = list(itertools.chain(*line_groups.values()))
                sources = map(attrgetter('data'), lines)
                y_min, y_max = \
                    numpy.min(sources) - y_margin, numpy.max(
                        sources) + y_margin
            else:
                y_min, y_max = \
                    numpy.min(total) - y_margin, numpy.max(total) + y_margin
                # FIXME: Smelly, find a better way

                line_groups_per_plot.append({})

            f = get_figure(
                tools=get_tools(),
                x_axis_len=x_axis_len,
                y_range=Range1d(y_min, y_max),

            )
            figures.append(f)

            x_range = range(0, len(total) * sampling_rate, sampling_rate)
            total_data = dict(x=x_range, y=total)
            total_cds = ColumnDataSource(data=total_data)
            valency = get_mean(plot['data'])
            # we want gauge to have zero in the middle
            gauge_boundary = abs(
                max(numpy.min(total), numpy.max(total), key=abs))
            total_line = Line(
                total,
                total_cds,
                'no description',
                'red',
                -gauge_boundary,
                gauge_boundary,
                0,  # or valency
                continuous_array(x_range, total)
            )
            totals.append(total_line)
            valency_data = dict(x=[0, x_axis_len], y=[valency, valency])
            valency_cds = ColumnDataSource(data=valency_data)
            valency_line = Line(
                data=valency_data,
                source=valency_cds,
                color='orange',
                mean=valency,
            )
            valencies.append(valency_line)

            draw_secondary_elements(
                f, valency_cds, total_cds, progress_bar, x_axis_len, y_min,
                y_max, color_above, color_below
            )
            if plot['filter_column_names']:
                for line in lines:
                    f.line(
                        'x', 'y',
                        source=line.source,
                        color=line.color,
                        line_width=2
                    )
    layout = vform(*figures)
    script, plots = components(figures)
    if not isinstance(plots, tuple):
        plots = tuple([plots])
    template_args = {
        'progress_bar_id': progress_bar.ref['id'],
        'progress_bar_y': progress_bar_y,
        'video_data': video_data,
        'line_groups_per_plot': line_groups_per_plot,
        'totals': totals,
        'totals_ids': [_.source._id for _ in totals],
        'valencies': valencies,
        'valencies_ids': [_.source._id for _ in valencies],
        'plots': plots,
        'script': script,
        'gauge_colours': gauge_colours,
        'titles': titles,
        'group_ids': group_ids
        # 'legend': 'vertical' if len(plots) == 1 else 'horizontal'
    }
    template_args.update(get_inline_statics())
    return layout, template_args


def validate_sheets_uniformity(plots, logger):
    # In order for legend to be able to control all plots at the same time
    # the sheets need to have same column names and the scope of these columns
    # need to be identical
    sheets_columns = [p['filter_column_names'] for p in plots]
    logger += [u'filter_column_names: ' + unicode(sheets_columns) + '\n']
    assert uniform_list(
        sheets_columns), 'All sheets must contain identical filter columns'
    scopes = []
    for plot in plots:
        scope = defaultdict(set)
        for line in plot['data']:
            for column_name, v in line.items():
                if column_name != 'as':
                    scope[column_name].add(v)
        scopes.append(scope)
    logger += [
        u'scopes: ' +
        json.dumps(scopes, cls=SetEncoder, ensure_ascii=True, indent=4) +
        '\n'
    ]
    assert uniform_list(
        scopes), 'The scopes of every filter should be the same across sheets'


def get_inline_statics():
    static_files = {
        'video_border_up': 'video_border_up.png',
        'video_border_back': 'video_border_back.png',
        'video_border_down': 'video_border_down.png',
        'back': 'back.png',
        'logo': 'logo.png',
        'brainvision': 'brainvision.png',
    }
    # dirty, huh? you think this piece is dirty, look around
    static_path = os.path.abspath(os.path.dirname(__file__)) + '/static/'
    return {
        var: b64encode(open(static_path + filename).read())
        for var, filename in static_files.items()
    }


def draw_secondary_elements(
        f, valency_cds, total_cds, progress_bar, x_axis_len, y_min, y_max,
        color_above, color_below
    ):
    f.quad(
        top=0,
        bottom=y_min,
        left=0,
        right=x_axis_len,
        alpha=0.3,
        fill_color=color_below,
        line_color=None,
        # line_width=2

    )
    f.quad(
        top=0,
        bottom=y_max,
        left=0,
        right=x_axis_len,
        alpha=0.3,
        fill_color=color_above,
        # line_color='blue',
        # line_width=2

    )
    f.line('x', 'y', source=progress_bar, line_color='green')
    f.line('x', 'y', source=valency_cds, line_color='orange', line_dash=(6, 6), line_width=2)
    f.line('x', 'y', source=total_cds, line_color='red', name='total', line_width=2)


if __name__ == '__main__':
    standalone()
