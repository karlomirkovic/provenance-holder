from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from controller_db.models import controller_base
from provenance_db.models import provenance_base


# Drop all and recreate all tables
def migrate_database():
    provenance_base.metadata.drop_all(bind=provenance_engine)
    controller_base.metadata.drop_all(bind=controller_engine)
    provenance_base.metadata.create_all(bind=provenance_engine)
    controller_base.metadata.create_all(bind=controller_engine)


# Create the engines and connect to the provenance and controller databases respectively
provenance_engine = create_engine('postgres+psycopg2://postgres:postgres@localhost:5432/provenance')
provenance_session = sessionmaker(bind=provenance_engine)()
controller_engine = create_engine('postgres+psycopg2://postgres:postgres@localhost:5432/controller')
controller_session = sessionmaker(bind=controller_engine)()
