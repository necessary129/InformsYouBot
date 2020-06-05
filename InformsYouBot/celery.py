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


def patch_http_connection_pool(**constructor_kwargs):
    """
    This allows to override the default parameters of the 
    HTTPConnectionPool constructor.
    For example, to increase the poolsize to fix problems 
    with "HttpConnectionPool is full, discarding connection"
    call this function with maxsize=16 (or whatever size 
    you want to give to the connection pool)
    """
    from urllib3 import connectionpool, poolmanager

    class MyHTTPConnectionPool(connectionpool.HTTPConnectionPool):
        def __init__(self, *args, **kwargs):
            kwargs.update(constructor_kwargs)
            super(MyHTTPConnectionPool, self).__init__(*args, **kwargs)

    poolmanager.pool_classes_by_scheme["http"] = MyHTTPConnectionPool

    class MyHTTPSConnectionPool(connectionpool.HTTPSConnectionPool):
        def __init__(self, *args, **kwargs):
            kwargs.update(constructor_kwargs)
            super(MyHTTPSConnectionPool, self).__init__(*args, **kwargs)

    poolmanager.pool_classes_by_scheme["https"] = MyHTTPSConnectionPool


patch_http_connection_pool(maxsize=500)

import celery
from .database import session


class Task(celery.Task):
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = True
    #    max_retries = 50
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
