from metaclasses.controllermeta import ControllerMeta
from config import controller_session, provenance_session
from controller_db.models import EntryUserRelationship
from provenance_db.models import User
from ed25519 import VerifyingKey


class Entry:
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


class Controller(ControllerMeta):
    def retrieve(self, search_id, search_type, provider, user):
        result = provider.retrieve(search_id, search_type)
        message = []
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
                    result.execute_signature]
            message.append(temp)
            print(temp)
            eur = controller_session\
                .query(EntryUserRelationship)\
                .filter(EntryUserRelationship.workflow_instance_id == result.workflow_instance_id)\
                .first()
            entry_user = provenance_session\
                .query(User)\
                .filter(User.id == eur.user_id)\
                .first()
            new_message = self.validate(message, entry_user)

        return new_message

    def validate(self, message, user):
        new_message = []
        # A Message is a list of Entries
        # (chorid, chorver, choriden, workid, workver, workiden, input, b'invokesig, output, b'execsig)
        for entry in message:
            # entry[7] - invoke_signature
            # entry[9] - execute_signature
            invoke = str(entry[0]) +\
                     str(entry[1]) +\
                     str(entry[2]) +\
                     str(entry[3]) +\
                     str(entry[4]) +\
                     str(entry[5]) +\
                     str(entry[6])
            invoke = bytes(invoke, 'utf-8')
            execute = str(entry[7]) + entry[8]
            execute = bytes(execute, 'utf-8')

            # Reconstruct the public key using the ed25519 constructor
            public_key = VerifyingKey(user.private_key_vk)
            public_key.verify(entry[7], invoke, encoding='hex')
            try:
                public_key.verify(entry[7], invoke, encoding='hex')
                public_key.verify(entry[9], execute, encoding='hex')
                new_message.append(entry)
                print("Verified")
            except:
                print("Could not verify signature of user " + user.username)

        return new_message

    # When the record method is called, the controller converts the data
    # into data that can be used by the providers and calls them to store it
    def record(self, message, provider, user):
        message = self.validate(message, user)
        # A Message is a list of Entries
        # (chorid, chorver, choriden, workid, workver, workiden, input, b'invokesig, output, b'execsig)
        new_message = []
        for entry in message:
            new_entry = Entry()
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

            new_message.append(new_entry)
            controller_entry = EntryUserRelationship(choreography_instance_id=new_entry.choreography_instance_id,
                                                     workflow_instance_id=new_entry.workflow_instance_id,
                                                     user_id=user.id)
            controller_session.add(controller_entry)
            controller_session.commit()
        provider.record(new_message)

    def migrate(self):
        pass
