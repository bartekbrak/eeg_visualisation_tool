from src.data_getter import get_from_f
from src.utils import group_by, get_random_colour, get_figure
from src.widgets import get_file_widget
from src.constants import column_name_map
from bokeh.plotting import output_notebook, show
from bokeh.io import vform, output_file
from bokeh.models import Callback, ColumnDataSource, Button, Range1d
registry = {}
# get_file_widget(registry)

def prepare():
    # from src.prototype import before_do, do, output_notebook, get_file_widget
    # global registry
    output_notebook()
    # registry = {}
    return get_file_widget(registry)

_data = None
def get_data():
    global _data
    if _data:
        return _data
    else:
        _data = get_from_f(registry['csv'], column_name_map)
        return _data


def show_figure(*grouped_by):
    data = get_data()

    print 'columns avaialable:', column_name_map
    # grouped_by = ('age', 'sex', 'favourite_brand')
    print 'grouped by:', grouped_by
    grouped = group_by(grouped_by, data)
    video_len = 33000
    figure = get_figure(
        video_len, width=800, height=400,
        y_range=Range1d(-1, 1)
    )
    x_range = range(0, video_len, 1000)

    buttons = get_buttons(figure, grouped, x_range, grouped_by)

    layout = vform(figure, *buttons)
    output_file('bokeh.html')
    show(layout)


def make_callback(callback_args, line_name, source_name):
    return Callback(args=callback_args, code="""
    if ({line_name}.get('data')['x'][0] == null) {{
        {line_name}.set('data', {source_name}.get('data')).trigger('change');
    }} else {{
        {line_name}.set('data', empty.get('data')).trigger('change');
    }}
    """.format(**locals()))

def get_buttons(figure, grouped, x_range, grouped_by):
    buttons = []
    for group_description, group in grouped.iteritems():
        y_data = group['grouped']
        y_ds = ColumnDataSource(data=dict(x=x_range, y=y_data))
        y_ds2 = ColumnDataSource(data=dict(x=x_range, y=y_data))
        figure.line(
            'x', 'y',
            source=y_ds,
            # legend=group_description,
            color=get_random_colour()
        )
        line_name = '%s_line' % group_description
        source_name = '%s_source' % group_description
        this_args = {
            'empty': ColumnDataSource(data=dict(x=[], y=[])),
            line_name: y_ds,
            source_name: y_ds2,

        }
        this_callback = make_callback(this_args, line_name, source_name)
        label = ', '.join([group['description'][key] for key in grouped_by])
        # TODO: rewrite to from bokeh.models.widgets import Toggle
        buttons.append(
            Button(label=label, callback=this_callback,
                   type='success')
        )
    return buttons
