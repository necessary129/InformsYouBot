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
from .utils import get_an_instance, get_main_instance
from prawcore.exceptions import ResponseException


def get_id_from_subs(subs):
    for sub in subs:
        try:
            if sub.id:
                return sub.id
        except:
            pass


def get_submissions_newer_than(subreddits, sid=None):
    reddit = get_main_instance()
    subreddits = "+".join(subreddits)
    submissions = []
    generator = reddit.subreddit(subreddits).new(limit=None)
    if not sid:
        submissions.append(next(generator))
        return submissions
    for submission in generator:
        if submission.id == sid:
            break
        submissions.append(submission)
    return submissions


def user_exists(user):
    reddit = get_an_instance()
    try:
        reddit.redditor(user).id
        return True
    except ResponseException:
        return False


def subreddit_exists(subreddit):
    reddit = get_an_instance()
    try:
        reddit.subreddit(subreddit).id
        return True
    except ResponseException:
        return False
