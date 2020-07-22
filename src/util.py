from db.models import Base
from sqlalchemy.engine import create_engine


def fill_dummy(provenance_holder):
    engine = create_engine('postgres+psycopg2://postgres:password@localhost:5432/provenance', echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    message = []
    # Fill a message with 5 provenance entries
    # Entries from ESB look like this (chorid, chorver, workid, workver, input, invokesig, output, execsig)
    for i in range(5):
        temp = [0,
                (1 + i/10),
                i,
                (1 + i/10),
                "10",
                bytes('invoke_signature', 'utf-8'),
                "20",
                bytes('execute_signature', 'utf-8')]
        message.append(temp)

    provenance_holder.controller.record(message, provenance_holder.providers[0])
