import yaml
import random
from itertools import cycle
from functools import wraps
import redis

REDIS_CLIENT = redis.Redis()


def only_one(function=None, key=None, timeout=None, block=False):
    """Enforce only one celery task at a time."""

    def _dec(run_func):
        """Decorator."""
        mkey = key if key else run_func.__name__

        @wraps(run_func)
        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            lock = REDIS_CLIENT.lock(mkey, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=block)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()

            return ret_value

        return _caller

    return _dec(function) if function is not None else _dec


from praw import Reddit


CONFIG = {}
INSTANCES = []
MAIN_INSTANCE = None


def _load_config():
    global CONFIG
    with open("settings.yaml", mode="r") as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)


def _create_instance_getter():
    global INSTANCE_CYCLE
    INSTANCE_CYCLE = cycle(INSTANCES)


def _load_instances():
    global CONFIG, INSTANCES, MAIN_INSTANCE
    cid = CONFIG["reddit_client_id"]
    csecret = CONFIG["reddit_client_secret"]
    ua = CONFIG["reddit_ua"]
    for account in CONFIG["reddit_accounts"]:
        INSTANCES.append(
            Reddit(
                client_id=cid,
                client_secret=csecret,
                user_agent=ua,
                username=account["username"],
                password=account["password"],
            )
        )
    MAIN_INSTANCE = INSTANCES[0]
    random.shuffle(INSTANCES)
    _create_instance_getter()


def get_main_instance():
    global MAIN_INSTANCE
    return MAIN_INSTANCE


def get_an_instance():
    global INSTANCE_CYCLE
    return next(INSTANCE_CYCLE)


_load_config()
_load_instances()
