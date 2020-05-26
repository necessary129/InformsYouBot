from jinja2 import Environment, PackageLoader, select_autoescape
from . import constants as c

env = Environment(
    loader=PackageLoader("RUpdatesBot", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def get_template(template):
    return env.get_template(template, globals=(c,))
