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
    "InformsYouBot",
    broker="pyamqp://",
    # backend='rpc://',
    task_cls="InformsYouBot.celery:Task",
    include=["InformsYouBot.tasks"],
)

app.conf.update(task_serializer="pickle", accept_content=["pickle"])

if __name__ == "__main__":
    app.start()
