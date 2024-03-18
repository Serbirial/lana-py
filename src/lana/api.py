from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import HTTPResponse, empty

from lana.utils import db
from lana.web import context
from lana.web.blueprints.blueprints import api


async def catch_everything(request, exception):
    if not isinstance(exception, NotFound):
        return empty()
    return HTTPResponse("URL not found.", 404)


def main(host="localhost", port=4004, prefix_limit=25, db_config=None):
    _db = db.DB(db.mariadb_pool(0, db_config))
    app = Sanic("LanaDashboard")
    app.ctx = context.CustomContext(_db)
    app.ctx.prefix_limit = prefix_limit
    app.blueprint(api)
    app.exception(Exception)(catch_everything)
    app.run(host, port, debug=False)


if __name__ == "__main__":
    main()
