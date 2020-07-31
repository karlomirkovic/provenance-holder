from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from provenance_db.models import provenance_base
from controller_db.models import controller_base


def migrate_database():
    provenance_base.metadata.drop_all(bind=provenance_engine)
    controller_base.metadata.drop_all(bind=controller_engine)
    provenance_base.metadata.create_all(bind=provenance_engine)
    controller_base.metadata.create_all(bind=controller_engine)


provenance_engine = create_engine('postgres+psycopg2://postgres:password@localhost:5432/provenance')
provenance_session = sessionmaker(bind=provenance_engine)()
controller_engine = create_engine('postgres+psycopg2://postgres:password@localhost:5432/controller')
controller_session = sessionmaker(bind=controller_engine)()



