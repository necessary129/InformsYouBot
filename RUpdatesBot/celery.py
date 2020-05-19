import celery
from .database import session


class Task(celery.Task):
    retry_backoff = True
    retry_backoff_max = 360
    retry_jitter = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        session.remove()


app = celery.Celery(
    "RUpdatesBot",
    broker="amqp://",
    # backend='rpc://',
    task_cls="RUpdatesBot.celery:Task",
    include=["RUpdatesBot.tasks"],
)

if __name__ == "__main__":
    app.start()
