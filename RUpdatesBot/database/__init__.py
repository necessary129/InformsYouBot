from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from ..utils import CONFIG

engine = create_engine(CONFIG["db_url"])
session = scoped_session(sessionmaker(bind=engine))

from .models import *
