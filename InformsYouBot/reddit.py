from .utils import get_an_instance, get_main_instance
from prawcore import NotFound


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
    except NotFound:
        return False


def subreddit_exists(subreddit):
    reddit = get_an_instance()
    try:
        reddit.subreddit(subreddit).id
        return True
    except NotFound:
        return False
