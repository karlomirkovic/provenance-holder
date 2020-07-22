from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime

Base = declarative_base()


class ProvenanceEntry(Base):
    __tablename__ = 'provenance'

    # Sha256 hash of everything below.
    provenance_hash = Column(String(64), primary_key=True)

    choreography_instance_id = Column(Integer, nullable=False)
    choreography_version = Column(Integer, nullable=False)
    workflow_instance_id = Column(Integer, unique=True, nullable=False)
    workflow_version = Column(Float, nullable=False)
    input = Column(String, nullable=False)
    # The signed choreography_instance_id, workflow_instance_id, workflow_version and input.
    invoke_signature = Column(String, nullable=False)

    output = Column(String, nullable=False)
    # The signed invoke_signature and output.
    execute_signature = Column(String, nullable=False)

    timestamp = Column(DateTime)
    # The Sha256 provenance hash of it's predecessor object
    predecessor = Column(String(64))

    def __repr__(self):
        return "<ProvenanceEntry(provenance_hash={}, " \
               "choreography_instance_id={}, " \
               "choreography_version={}, " \
               "workflow_instance_id={}, " \
               "workflow_version={}, " \
               "input='{}', " \
               "invoke_signature='{}', " \
               "output='{}', " \
               "execute_signature='{}', " \
               "timestamp={}, " \
               "predecessor='{}')>" \
            .format(self.provenance_hash,
                    self.choreography_instance_id,
                    self.choreography_version,
                    self.workflow_instance_id,
                    self.workflow_version,
                    self.input,
                    self.invoke_signature,
                    self.output,
                    self.execute_signature,
                    self.timestamp,
                    self.predecessor)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    private_key = Column(String, nullable=False, unique=True)
    public_key = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return "<User(id={}, " \
               "username='{}', " \
               "private_key='{}', " \
               "public_key='{}')>"\
            .format(self.id,
                    self.username,
                    self.private_key,
                    self.public_key)