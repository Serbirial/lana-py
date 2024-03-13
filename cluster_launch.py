from bot import LanaAR, config
from dis_command.discommand.sharding import collection
from utils import db

lana = LanaAR
config = config.BotConfig()
_db = db.DB(db.mariadb_pool(0)) 



cluster = collection.ThreadedCluster(name="cluster_one", id=1)
cluster_schema = [
	[0,1], # Thread 1 handles shards 0-1 
	[2,3]  # Thread 2 handles shards 2-3
]
cluster_total = 4

cluster.set_client(lana)

for ids in cluster_schema:
	cluster.add_thread(ids)

cluster.launch(config.token, cluster_total, *(_db,))