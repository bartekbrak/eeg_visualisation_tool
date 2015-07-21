# https://github.com/bokeh/bokeh/blob/master/examples/embed/embed_multiple.py
from bokeh.io import vform
from bokeh.models import ColumnDataSource, Button, Range1d, HoverTool, TapTool, \
    Callback
from bokeh.embed import components, file_html
from bokeh.resources import INLINE
from bokeh.plotting import figure
from jinja2 import Environment, PackageLoader

from evt.constants import column_name_map
from evt.data_getter import get_from_csv
from evt.prototype import make_callback
from evt.utils import group_by, get_random_colour

env = Environment(loader=PackageLoader('evt', 'templates'))

data = get_from_csv('tomek.csv', column_name_map)

print 'columns avaialable:', column_name_map
grouped_by = ('age', 'sex', 'favourite_brand')
print 'grouped by:', grouped_by
grouped = group_by([], data)

hover = HoverTool(
    tooltips = [
        # ("index", "$index"),
        ("db", "$y")
    ]
)

hover2 = HoverTool(
    tooltips=None,
    point_policy='follow_mouse',
    callback=Callback(
        code="""
        if (hover_active) {
            var x = cb_data['geometry']['x'] / 1000;
            myvideo.currentTime = x;
        }
        """
    ),
)
tap= TapTool(action = Callback(code="""
    if (cb_obj.get('data')['x'].length == 2) {
    if (hover_active) {
        myvideo.play();
        hover_active = false;
        console.log('hover was active');
    } else {
        myvideo.pause();
        hover_active = true;
        console.log('hover was not active');
    }
    }
"""))

video_len = 10100
f = figure(
    # hover
    # tools='save, reset, ypan, resize, tap',
    tools= [hover2, tap],
    # tools='',
    # tools='tap',
    toolbar_location='right',
    width=800,
    height=200,
    x_range=Range1d(0, video_len),
    y_range=Range1d(-2, 2),
    x_axis_type='datetime',
    # lod_factor=10,
    # lod_interval=100,
    # lod_threshold=None,
    # lod_timeout=100
)


line = ColumnDataSource(data={'x': [0, 0], 'y': [-3, 3]})
f.line('x', 'y', source=line, line_color='green', line_width=3)

x_range = range(0, video_len, 333)

# empty = ColumnDataSource(data=dict(x=[], y=[]))

buttons = []
for group_description, group in grouped.iteritems():
    y_data = group['grouped']
    y_ds = ColumnDataSource(data=dict(x=x_range, y=y_data))
    # y_ds2 = ColumnDataSource(data=dict(x=x_range, y=y_data))
    f.line(
        'x', 'y',
        source=y_ds,
        #  legend=group_description,
        color=get_random_colour(),
        line_width=1,
        line_join='round',
        #         line_dash='dashed'
    )
    # line_name = '%s_line' % group_description
    # source_name = '%s_source' % group_description
    # this_args = {
    #     'empty': empty,
    #     line_name: y_ds,
    #     source_name: y_ds2,
    #
    # }
    # this_callback = make_callback(this_args, line_name, source_name)
    # buttons.append(
    #     Button(label=group_description, callback=this_callback)
    # )
# taptool = f.select(type=TapTool)
# taptool.action = Callback(code="""
#     alert('tap)
# """)
# taptool = f.select(type=TapTool)
# f.y_range.callback = Callback(code="""
#     console.log(cb_obj);
#     console.log(cb_data);
# """)

layout = vform(f, *buttons)

html_file = 'final.html'
kwargs = {
    'line_id': line._id,
    'line_y': line.data['y']
}
template = env.get_template('mytemplate.html')
html = file_html(layout, INLINE, "my plot", template, kwargs)
with open(html_file, 'w') as textfile:
    textfile.write(html)
# url = 'file:{}'.format(six.moves.urllib.request.pathname2url(os.path.abspath(html_file)))
# webbrowser.open(url)
