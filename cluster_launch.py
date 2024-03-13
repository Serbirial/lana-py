from bot import LanaAR, config
from multiprocessing import Queue
from dis_command.discommand.sharding import collection
from utils import db as database

queue = Queue()
config = config.BotConfig()
db = database.DB(database.mariadb_pool(0)) 
main_lana = LanaAR(True, db, queue)
lana = LanaAR

main_lana.cluster = collection.ThreadedCluster(name="cluster_one", id=1, client=lana)
cluster_schema = [
	[1,2], # Thread 1 handles shards 0-1 
	[3,4]  # Thread 2 handles shards 2-3
]
cluster_total = 5

print("Creating threads...")

for ids in cluster_schema:
	main_lana.cluster.add_thread(ids)

print("Launching...")

main_lana.cluster.launch(config.token, cluster_total, *(False, db, queue))

print("Launched threads.\nLaunching main bot on shard 0.")

main_lana.shard_count = cluster_total
main_lana.shard_ids = [0]
main_lana.run(config.token)