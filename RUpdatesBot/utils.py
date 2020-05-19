import yaml
import random
from itertools import cycle

from praw import Reddit


CONFIG = {}
INSTANCES = []


def _load_config():
    global CONFIG
    with open("settings.yaml", mode="r") as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)


def _create_instance_getter():
    global INSTANCE_CYCLE
    INSTANCE_CYCLE = cycle(INSTANCES)


def _load_instances():
    global CONFIG, INSTANCES
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
    random.shuffle(INSTANCES)
    _create_instance_getter()


def get_an_instance():
    global INSTANCE_CYCLE
    return next(INSTANCE_CYCLE)


_load_config()
_load_instances()
