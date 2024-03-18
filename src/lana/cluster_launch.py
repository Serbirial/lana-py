from multiprocessing import Lock

from bot import LanaAR, config
from dis_command.discommand.sharding import collection
from ipc import IPCServer
from utils import db as database


def cluster_launch():
    startup_lock = Lock()

    config = config.BotConfig()
    db = database.DB(database.mariadb_pool(0))

    main_lana = LanaAR("lana_main", True, startup_lock, db)
    lana = LanaAR

    main_lana.ipc = IPCServer(main_lana, "localhost", 62435)
    main_lana.cluster = collection.ThreadedCluster(name="cluster_one", id=1, client=lana)

    cluster_schema = [[1, 2], [3, 4]]  # Thread 1 handles shards 0-1  # Thread 2 handles shards 2-3
    cluster_total = 5

    print("Creating threads...")

    for ids in cluster_schema:
        main_lana.cluster.add_thread(ids)

    print("Launching...")

    main_lana.cluster.launch(config.token, cluster_total, *(None, False, startup_lock, db))

    print("Launched threads.\nLaunching main bot on shard 0.")

    main_lana.shard_count = cluster_total
    main_lana.shard_ids = [0]

    # Lock the startup lock, and release it in the main instance when the instance is fully ready.
    startup_lock.acquire(False)

    main_lana.run(config.token)
