from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(settings.SYNC_SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()









