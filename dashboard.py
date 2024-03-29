from web import context

from sanic import Sanic

from sanic.response import text
from sanic_ext import render


from utils import db
from config import config

from web.blueprints.blueprints import dash
from oauth import Client

from os import walk


config = config.DashboardConfig()



_oauth_client = Client(config.client_id, secret=config.client_secret, redirect=config.callback_url)
_db = db.DB(db.mariadb_pool(0))

app = Sanic("LanaDashboard")
app.static('/static', './dashboard/static')
app.ctx = context.CustomContext(_db)
app.blueprint(dash)

html_data = {}

async def render_jinja_file(file_name: str, context: dict):
	return await render(
		template_source=html_data[file_name],
		context=context,
		app=app,
	)

for parent, subddirs, files in walk("./web/html/"):
	for file in files:
		html_data[file] = open(f"{parent}{file}").read()


@app.get("/")
async def hello_world(request):
	return text("Hello, world.")

# Inject everything needed.
@app.on_request
async def setup_connection(request):
	request.ctx.oauth = _oauth_client
	request.ctx.render = render_jinja_file

def main():
	app.run("localhost", 8080)

if __name__ == '__main__':
	main()