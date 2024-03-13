from bot import LanaAR, config
from dis_command.discommand.sharding import collection
from utils import db

lana = LanaAR
config = config.BotConfig()
_db = db.DB(db.mariadb_pool(0)) 



cluster = collection.ThreadedCluster(name="cluster_one", id=1, client=lana)
cluster_schema = [
	[1,2], # Thread 1 handles shards 0-1 
	[3,4]  # Thread 2 handles shards 2-3
]
cluster_total = 5

print("Creating threads...")

for ids in cluster_schema:
	cluster.add_thread(ids)

print("Launching...")

cluster.launch(config.token, cluster_total, *(_db,))

print("Launched.")
main_lana = LanaAR(_db)
main_lana.shard_count = cluster_total
main_lana.shard_ids = [0]
main_lana.run()