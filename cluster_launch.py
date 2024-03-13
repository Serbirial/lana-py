from bot import LanaAR
from dis_command.discommand.sharding import collection
from dis_command.discommand.entry.inject import inject_into_bot
from utils import db

def cluster_launch(): 
	cluster = collection.ThreadedCluster(name="cluster_one", id=1)
	cluster_schema = [
		[0,1], # Thread 1 handles shards 0-1 
		[2,3]  # Thread 2 handles shards 2-3
	]

	_db = db.DB(db.mariadb_pool(0))

	lana = LanaAR(db)
	try:
		lana.panel = db.DB(db.mariadb_pool(1, "private/config/private_db.json"))
	except FileNotFoundError:
		pass
	inject_into_bot(lana)

	for ids in cluster_schema:
		cluster.add_thread(ids)
	
	cluster.launch(lana.config.token, len(cluster_schema))