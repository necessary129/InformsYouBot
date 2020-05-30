#  Copyright (C) 2020 Shamil K Muhammed

# This file is part of InformsYouBot.

# InformsYouBot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    InformsYouBot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with InformsYouBot.  If not, see <http://www.gnu.org/licenses/>.
from .utils import CONFIG, message_url
from urllib.parse import quote

NEW_SUBMISSION_MESSAGE = r"""Click [here](/message/compose/?to={c.USERNAME}&subject=Subscribe&message={c.SAFE_TRIGGER}subscribe%20u/{author}%20r/{subreddit}) to get a new notification everytime /u/{author} posts on /r/{subreddit}

"""

USERNAME = CONFIG["reddit_accounts"][0]["username"]
OWNER_USERNAME = CONFIG["owner_account"].lower()

UPDATE_MESSAGE = r"""/u/{author} has posted a submission to /r/{subreddit}.

[Check it out]({url})
"""

TRIGGER = "!"
SAFE_TRIGGER = quote(TRIGGER)

SUBSCRIPTION_SUCCESS = (
    r"""I will message you everytime when /u/{author} posts to /r/{subreddit}"""
)


TABLES = (
    ("My subscriptions", message_url(USERNAME, "Updates", "!mysubscriptions")),
    (
        "Message maintainer",
        message_url(OWNER_USERNAME, f"Message about /u/{USERNAME}", ""),
    ),
)
