

from sanic import Blueprint

from web.blueprints.dashboard import blueprint as dashboard
from web.blueprints.api import blueprint as api

# All of the Dash blueprints
dash = Blueprint.group(
    dashboard
)

api = Blueprint.group(
    api
)