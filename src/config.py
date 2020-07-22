from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .db.models import Base


engine = create_engine('postgres+psycopg2://postgres:password@localhost:5432/provenance', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


