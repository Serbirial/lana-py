import logging
from multiprocessing import Lock

from dis_command.discommand.sharding import collection

from lana.bot import LanaAR
from lana.ipc import IPCServer
from lana.utils import db as database

logger = logging.getLogger(__name__)


def cluster_launch(token, db_config):
    startup_lock = Lock()

    db = database.DB(database.mariadb_pool(0, db_config))

    main_lana = LanaAR("lana_main", True, startup_lock, db)
    lana = LanaAR

    main_lana.ipc = IPCServer(main_lana, "localhost", 62435)
    main_lana.cluster = collection.ThreadedCluster(name="cluster_one", id=1, client=lana)

    cluster_schema = [[1, 2], [3, 4]]  # Thread 1 handles shards 0-1  # Thread 2 handles shards 2-3
    cluster_total = 5

    logger.info("Creating threads...")

    for ids in cluster_schema:
        main_lana.cluster.add_thread(ids)

    logger.info("Launching...")

    main_lana.cluster.launch(token, cluster_total, *(None, False, startup_lock, db))

    logger.info("Launched threads.\nLaunching main bot on shard 0.")

    main_lana.shard_count = cluster_total
    main_lana.shard_ids = [0]

    # Lock the startup lock, and release it in the main instance when the instance is fully ready.
    startup_lock.acquire(False)

    main_lana.run(token)
