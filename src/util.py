from db.models import Base
from sqlalchemy.engine import create_engine


def fill_dummy(provenance_holder, user):
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
                "10"]
        invoke = str(temp[0]) + str(temp[1]) + str(temp[2]) + str(temp[3]) + temp[4]
        invoke = bytes(invoke, 'utf-8')
        invoke_signature = user.private_key.sign(invoke, encoding='hex')
        temp.append(invoke_signature)
        temp.append("20")
        execute = str(invoke_signature) + temp[6]
        execute = bytes(execute, 'utf-8')
        execute_signature = user.private_key.sign(execute, encoding='hex')
        temp.append(execute_signature)

        message.append(temp)

    new_message = provenance_holder.controller.validate(message, user)
    provenance_holder.controller.record(new_message, provenance_holder.providers[0])
