from sqlalchemy import Column, Integer, Float, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String

provenance_base = declarative_base()


class Adaptation(provenance_base):
    __tablename__ = 'adaptation'
    # The Sha256 hash of everything below apart from the predecessor
    provenance_hash = Column(String(64), primary_key=True)

    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    identifier = Column(Integer, unique=True, nullable=False)
    version = Column(Float, nullable=False)
    change = Column(String, nullable=False)
    # Signature of name, version, and change
    signature = Column(LargeBinary, unique=True, nullable=False)
    timestamp = Column(DateTime)

    # The Sha256 provenance hash of it's predecessor object
    predecessor = Column(String(64))

    def __repr__(self):
        return "<Adaptation(provenance_hash='{}', " \
               " name='{}', " \
               " type={}, " \
               " identifier={}, " \
               " version={}, " \
               " change={}," \
               " signature='{}'," \
               " timestamp={}," \
               " predecessor='{}')>" \
            .format(self.provenance_hash,
                    self.name,
                    self.type,
                    self.identifier,
                    self.version,
                    self.change,
                    self.signature,
                    self.timestamp,
                    self.predecessor)


class Execution(provenance_base):
    __tablename__ = 'execution'

    # Sha256 hash of everything below apart from the predecessor
    provenance_hash = Column(String(64), primary_key=True)

    choreography_instance_id = Column(Integer, nullable=False)
    choreography_version = Column(Float, nullable=False)
    choreography_identifier = Column(Integer, unique=True, nullable=False)
    workflow_instance_id = Column(Integer, unique=True, nullable=False)
    workflow_version = Column(Float, nullable=False)
    workflow_identifier = Column(Integer, unique=True, nullable=False)
    input = Column(String, nullable=False)
    invoke_signature = Column(LargeBinary, nullable=False)

    output = Column(String, nullable=False)
    execute_signature = Column(LargeBinary, nullable=False)

    timestamp = Column(DateTime)

    # The Sha256 provenance hash of it's predecessor object
    predecessor = Column(String(64))

    def __repr__(self):
        return "<Execution(provenance_hash='{}', " \
               " choreography_instance_id={}, " \
               " choreography_version={}, " \
               " choreography_identifier={}, " \
               " workflow_instance_id={}, " \
               " workflow_version={}," \
               " workflow_identifier={}," \
               " input='{}', " \
               " invoke_signature='{}', " \
               " output='{}', " \
               " execute_signature='{}', " \
               " timestamp={}, " \
               " predecessor='{}')>" \
            .format(self.provenance_hash,
                    self.choreography_instance_id,
                    self.choreography_version,
                    self.choreography_identifier,
                    self.workflow_instance_id,
                    self.workflow_version,
                    self.workflow_identifier,
                    self.input,
                    self.invoke_signature,
                    self.output,
                    self.execute_signature,
                    self.timestamp,
                    self.predecessor)
