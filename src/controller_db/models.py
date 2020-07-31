from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, LargeBinary, String
controller_base = declarative_base()


class PublicKey(controller_base):
    __tablename__ = 'public_keys'

    public_key_vk = Column(LargeBinary, primary_key=True)
    user_id = Column(Integer, unique=True)

    def __repr__(self):
        return "<PublicKey(public_key_vk='{}', " \
               "user_id={},)>"\
            .format(self.public_key_vk,
                    self.user_id)


class EntryUserRelationship(controller_base):
    __tablename__ = 'enrtryuserrelationship'

    choreography_instance_id = Column(Integer)
    workflow_instance_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    def __repr__(self):
        return "<EntryUserRelationship(" \
               "choreography_instance_id={}," \
               " workflow_instance_id={}," \
               " user_id='{}')>"\
            .format(self.choreography_instance_id,
                    self.workflow_instance_id,
                    self.user_id)
