import celery
from .database import session


class Task(celery.Task):
    retry_backoff = True
    retry_backoff_max = 360
    retry_jitter = True
    autoretry_for = (Exception,)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        session.remove()


app = celery.Celery(
    "RUpdatesBot",
    broker="pyamqp://",
    # backend='rpc://',
    task_cls="RUpdatesBot.celery:Task",
    include=["RUpdatesBot.tasks"],
)

app.conf.update(task_serializer="pickle", accept_content=["pickle"])

if __name__ == "__main__":
    app.start()
