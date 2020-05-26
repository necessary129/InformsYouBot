from .utils import CONFIG
from urllib.parse import quote

NEW_SUBMISSION_MESSAGE = r"""Click [here](/message/compose/?to={c.USERNAME}&subject=Subscribe&message={c.SAFE_TRIGGER}subscribe%20u/{author}%20r/{subreddit}) to get a new notification everytime /u/{author} posts on /r/{subreddit}

"""

USERNAME = CONFIG["reddit_accounts"][0]["username"]

UPDATE_MESSAGE = r"""/u/{author} has posted a submission to /r/{subreddit}.

[Check it out]({url})
"""

TRIGGER = "!"
SAFE_TRIGGER = quote(TRIGGER)

SUBSCRIPTION_SUCCESS = (
    r"""I will message you everytime when /u/{author} posts to /r/{subreddit}"""
)
