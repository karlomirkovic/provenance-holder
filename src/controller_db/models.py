from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

controller_base = declarative_base()


class ExecutionUserRelationship(controller_base):
    __tablename__ = 'executionuserrelationship'

    choreography_instance_id = Column(Integer)
    workflow_instance_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    def __repr__(self):
        return "<ExecutionUserRelationship(" \
               "choreography_instance_id={}," \
               " workflow_instance_id={}," \
               " user_id='{}')>" \
            .format(self.choreography_instance_id,
                    self.workflow_instance_id,
                    self.user_id)


class AdaptationUserRelationship(controller_base):
    __tablename__ = 'adaptationuserrelationship'

    identifier = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    def __repr__(self):
        return "<ExecutionUserRelationship(" \
               "identifier={}," \
               " user_id='{}')>" \
            .format(self.identifier,
                    self.user_id)
