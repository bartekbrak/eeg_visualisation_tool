from jinja2 import Environment, PackageLoader

template_env = Environment(loader=PackageLoader('evt', 'templates'))
