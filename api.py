from sanic import Sanic

from sanic.response import HTTPResponse, empty
from sanic.exceptions import NotFound


from utils import db

from web.blueprints.blueprints import api
from web import context


_db = db.DB(db.mariadb_pool(0))

app = Sanic("LanaDashboard")
app.ctx = context.CustomContext(_db)
app.blueprint(api)

@app.exception(Exception)
async def catch_everything(request, exception):
	if not isinstance(exception, NotFound):
		return empty()
	return HTTPResponse("URL not found.", 404)


def main():
	app.run("localhost", 4004, debug=False)

if __name__ == '__main__':
	main()