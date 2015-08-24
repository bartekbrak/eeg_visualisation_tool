from jinja2 import Environment, PackageLoader
from joblib import Memory

template_env = Environment(loader=PackageLoader('evt', 'templates'))
cachedir = '/tmp/evt_cache'
memory = Memory(cachedir=cachedir, verbose=0)
# uncomment to disable caching
# memory.clear()

