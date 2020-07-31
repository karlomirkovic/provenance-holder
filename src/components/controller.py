from ed25519 import VerifyingKey

from config import controller_session, provenance_session
from controller_db.models import ExecutionUserRelationship, AdaptationUserRelationship
from metaclasses.controllermeta import ControllerMeta
from provenance_db.models import User


class Execution:
    def __init__(self):
        self.choreography_instance_id = None
        self.choreography_version = None
        self.choreography_identifier = None
        self.workflow_instance_id = None
        self.workflow_version = None
        self.workflow_identifier = None
        self.input = None
        self.invoke_signature = None
        self.output = None
        self.execute_signature = None
        self.timestamp = None
        self.predecessor = None
        self.entry_type = None


class Adaptation:
    def __init__(self):
        self.name = None
        self.type = None
        self.identifier = None
        self.version = None
        self.change = None
        self.signature = None
        self.predecessor = None
        self.entry_type = None


class Controller(ControllerMeta):
    def retrieve(self, search_id, search_type, provider, user, entry_type):
        result = provider.retrieve(search_id, search_type, entry_type)
        new_message = []
        if entry_type == 'execution':
            if search_type == 'workflow':
                temp = [result.choreography_instance_id,
                        result.choreography_version,
                        result.choreography_identifier,
                        result.workflow_instance_id,
                        result.workflow_version,
                        result.workflow_identifier,
                        result.input,
                        result.invoke_signature,
                        result.output,
                        result.execute_signature,
                        entry_type]
                eur = controller_session \
                    .query(ExecutionUserRelationship) \
                    .filter(ExecutionUserRelationship.workflow_instance_id == result.workflow_instance_id) \
                    .first()
                entry_user = provenance_session \
                    .query(User) \
                    .filter(User.id == eur.user_id) \
                    .first()
                new_message = self.validate([temp], entry_user)
            elif search_type == 'choreography':
                message = []
                for entry in result:
                    temp = [entry.choreography_instance_id,
                            entry.choreography_version,
                            entry.choreography_identifier,
                            entry.workflow_instance_id,
                            entry.workflow_version,
                            entry.workflow_identifier,
                            entry.input,
                            entry.invoke_signature,
                            entry.output,
                            entry.execute_signature,
                            entry_type]
                    message.append(temp)
                    eurs = controller_session \
                        .query(ExecutionUserRelationship) \
                        .filter(ExecutionUserRelationship.choreography_instance_id == entry.choreography_instance_id)
                    for eur in eurs:
                        entry_user = provenance_session \
                            .query(User) \
                            .filter(User.id == eur.user_id) \
                            .first()
                        new_message = self.validate(message, entry_user)

        elif entry_type == 'adaptation':
            temp = [result.name,
                    result.type,
                    result.identifier,
                    result.version,
                    result.change,
                    result.signature,
                    entry_type]
            eur = controller_session\
                .query(AdaptationUserRelationship)\
                .filter(AdaptationUserRelationship.identifier == result.identifier)\
                .first()
            entry_user = provenance_session\
                .query(User)\
                .filter(User.id == eur.user_id)\
                .first()
            new_message = self.validate([temp], entry_user)

        return new_message

    def validate(self, message, user):
        new_message = []
        # A Message is a list of Entries
        for entry in message:
            entry_type = entry[len(entry) - 1]
            if entry_type == 'execution':
                # entry[7] - invoke_signature
                # entry[9] - execute_signature
                invoke = str(entry[0]) + \
                         str(entry[1]) + \
                         str(entry[2]) + \
                         str(entry[3]) + \
                         str(entry[4]) + \
                         str(entry[5]) + \
                         str(entry[6])
                invoke = bytes(invoke, 'utf-8')
                execute = str(entry[7]) + entry[8]
                execute = bytes(execute, 'utf-8')

                # Reconstruct the public key using the ed25519 constructor
                public_key = VerifyingKey(user.private_key_vk)
                try:
                    public_key.verify(entry[7], invoke, encoding='hex')
                    public_key.verify(entry[9], execute, encoding='hex')
                    new_message.append(entry)
                    print("Validated")
                except:
                    print("Could not validate signature of user " + user.username)
            elif entry_type == 'adaptation':
                # (name, type, identifier, version, change, signature, entry_type)
                # entry[5] - signature
                sig_msg = entry[0] + str(entry[3]) + entry[4]
                sig_msg = bytes(sig_msg, 'utf-8')

                public_key = VerifyingKey(user.private_key_vk)
                try:
                    public_key.verify(entry[5], sig_msg, encoding='hex')
                    new_message.append(entry)
                    print("Validated")
                except:
                    print("Could not validate signature of user " + user.username)
            else:
                print("Cannot validate an entry of this type.")

        return new_message

    # When the record method is called, the controller converts the data
    # into data that can be used by the providers and calls them to store it
    def record(self, message, provider, user):
        message = self.validate(message, user)
        new_message = []

        # A Message is a list of Entries
        for entry in message:
            entry_type = entry[len(entry) - 1]
            if entry_type == 'execution':
                new_entry = Execution()
                new_entry.choreography_instance_id = entry[0]
                new_entry.choreography_version = entry[1]
                new_entry.choreography_identifier = entry[2]
                new_entry.workflow_instance_id = entry[3]
                new_entry.workflow_version = entry[4]
                new_entry.workflow_identifier = entry[5]
                new_entry.input = entry[6]
                new_entry.invoke_signature = entry[7]
                new_entry.output = entry[8]
                new_entry.execute_signature = entry[9]
                new_entry.entry_type = entry_type

                new_message.append(new_entry)

                # Link the user and the execution data in the controller database
                controller_entry = ExecutionUserRelationship(
                    choreography_instance_id=new_entry.choreography_instance_id,
                    workflow_instance_id=new_entry.workflow_instance_id,
                    user_id=user.id)
                controller_session.add(controller_entry)
                controller_session.commit()
            elif entry_type == 'adaptation':
                # (name, type, identifier, version, change, signature, predecessor, entry_type)
                new_entry = Adaptation()
                new_entry.name = entry[0]
                new_entry.type = entry[1]
                new_entry.identifier = entry[2]
                new_entry.version = entry[3]
                new_entry.change = entry[4]
                new_entry.signature = entry[5]
                new_entry.entry_type = entry_type

                new_message.append(new_entry)

                # Link the user and the adaptation data in the controller database
                controller_entry = AdaptationUserRelationship(identifier=new_entry.identifier, user_id=user.id)
                controller_session.add(controller_entry)
                controller_session.commit()

        provider.record(new_message)

    def migrate(self):
        pass
