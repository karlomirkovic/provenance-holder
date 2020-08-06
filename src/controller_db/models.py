from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

controller_base = declarative_base()


# An ExecutionUserRelationship stored in the controller database
# in order to be able to identify the user of an execution entry prior to validation
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


# An ExecutionUserRelationship stored in the controller database
# in order to be able to identify the user of an adaptation entry prior to validation
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
