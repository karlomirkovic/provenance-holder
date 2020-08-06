import hashlib

from ed25519 import VerifyingKey

from config import controller_session, provenance_session
from controller_db.models import ExecutionUserRelationship, AdaptationUserRelationship
from metaclasses.controllermeta import ControllerMeta
from provenance_db.models import User


# The Execution and Adaptation classes are only used within the controller for the purpose of converting
# the data in a message into a format that can be used by the providers


class Execution:
    def __init__(self):
        self.provenance_hash = None
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
        self.provenance_hash = None
        self.name = None
        self.type = None
        self.identifier = None
        self.version = None
        self.change = None
        self.signature = None
        self.predecessor = None
        self.entry_type = None


class Controller(ControllerMeta):
    # The retrieve method of the controller takes an entry for querying as a parameter
    # Together with the provider, user, and entry type
    def retrieve(self, entry, provider, user, entry_type):
        result = provider.retrieve(entry_type, entry)
        new_message = []
        # If the entry type is an execution
        # A temporary list is created in order for the data to be in a format where it can be validated
        if entry_type == 'execution':
            # The retrieval of database entries is done by passing an entry with all attributes set to None
            # The only attribute that isn't None is the attribute that the user wants to query by
            # For executions, there are two options, namely the workflow instance id and the choreography instance id
            if entry.workflow_instance_id is not None:
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
                # We query the separate controller database
                # for an entry with the same workflow instance id as the querying entry given as a parameter
                eur = controller_session \
                    .query(ExecutionUserRelationship) \
                    .filter(ExecutionUserRelationship.workflow_instance_id == result.workflow_instance_id) \
                    .first()
                # Once we have the execution user relationship we query the database of users
                # in order to find the user that signed the data when it was being recorded
                entry_user = provenance_session \
                    .query(User) \
                    .filter(User.id == eur.user_id) \
                    .first()
                # The message is validated
                new_message = self.validate([temp], entry_user)

                # If the message was validated correctly, the 'new_message' list would not be empty
                # If it isn't empty then the initial query result from the provider has been fully validated
                if new_message:
                    new_message = result

            elif entry.choreography_instance_id is not None:
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
                    # We query the separate controller database
                    # for entries with the same choreography instance id as the querying entry given as a parameter
                    eurs = controller_session \
                        .query(ExecutionUserRelationship) \
                        .filter(ExecutionUserRelationship.choreography_instance_id == entry.choreography_instance_id)
                    # Once we have the list of execution user relationships we iterate over it
                    # and for each execution user relationship we find the user and validate the message
                    for eur in eurs:
                        entry_user = provenance_session \
                            .query(User) \
                            .filter(User.id == eur.user_id) \
                            .first()
                        new_message = self.validate(message, entry_user)

                        # Check if all the entries in the message were validated
                        # If not, return an empty list
                        if not len(new_message) == len(result):
                            new_message = []
                            print("All the entries of the message could not be validated.")

        elif entry_type == 'adaptation':
            # Convert the query result into a data format that can be validated.
            temp = [result.name,
                    result.type,
                    result.identifier,
                    result.version,
                    result.change,
                    result.signature,
                    entry_type]
            # We query the separate controller database
            # for an entry with the same identifier as the querying entry given as a parameter
            aur = controller_session \
                .query(AdaptationUserRelationship) \
                .filter(AdaptationUserRelationship.identifier == result.identifier) \
                .first()
            # Once we have the adaptation user relationship we query the database of users
            # in order to find the user that signed the data when it was being recorded
            entry_user = provenance_session \
                .query(User) \
                .filter(User.id == aur.user_id) \
                .first()
            # Validate the entry
            new_message = self.validate([temp], entry_user)

            # If the adaptation is validated, return it.
            if new_message:
                new_message = result

        return new_message

    # The validate method of the controller takes a message and a user as parameters
    # Since the message is a list of entries, the method iterates over the entries and validates the signatures
    def validate(self, message, user):
        new_message = []
        # A message is a list of entries
        for entry in message:
            # For every entry, the last piece of data is the entry_type
            entry_type = entry[len(entry) - 1]

            # If the entry is an execution validate accordingly
            if entry_type == 'execution':
                # The piece of data at entry[7] is the invoke_signature
                # The piece of data at entry[9] is the execute_signature
                # Concatenate the data in order to recreate the original data that was signed
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

                # Reconstruct the public key using the ed25519 constructor and validate
                public_key = VerifyingKey(user.private_key_vk)
                try:
                    public_key.verify(entry[7], invoke, encoding='hex')
                    public_key.verify(entry[9], execute, encoding='hex')
                    new_message.append(entry)
                    print("Validated")
                except:
                    print("Could not validate signature of user " + user.username)
            # If the entry is an adaptation validate accordingly
            elif entry_type == 'adaptation':
                # The piece of data at entry[5] is the signature
                # Concatenate the data in order to recreate the original data that was signed
                sig_msg = entry[0] + str(entry[3]) + entry[4]
                sig_msg = bytes(sig_msg, 'utf-8')

                # Reconstruct the public key using the ed25519 constructor and validate
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
    # The record method also calculates the provenance hash and the predecessor object for each entry
    # It does it once per entry so each provider doesn't have to do it repeatedly
    def record(self, message, providers, user):
        # Validate the entries in the message before proceeding to record
        message = self.validate(message, user)
        new_message = []
        # A message is a list of entries
        for entry in message:
            # For every entry, the last piece of data is the entry_type
            entry_type = entry[len(entry) - 1]

            # If the entry is an execution convert the data accordingly
            if entry_type == 'execution':
                # Concatenate the data into a string in order to hash.
                provenance = str(entry[0]) + \
                             str(entry[1]) + \
                             str(entry[2]) + \
                             str(entry[3]) + \
                             str(entry[4]) + \
                             str(entry[5]) + \
                             entry[6] + \
                             str(entry[7]) + \
                             entry[8] + \
                             str(entry[9])

                provenance_hash = hashlib.sha256(provenance.encode('utf-8')).hexdigest()

                new_entry = Execution()
                new_entry.provenance_hash = provenance_hash
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

                # Record the execution entry on all providers
                for provider in providers:
                    provider.record([new_entry])

                # Link the user and the execution data in the controller database.
                controller_entry = ExecutionUserRelationship(
                    choreography_instance_id=new_entry.choreography_instance_id,
                    workflow_instance_id=new_entry.workflow_instance_id,
                    user_id=user.id)
                controller_session.add(controller_entry)
                try:
                    controller_session.commit()
                except:
                    controller_session.rollback()

                # Use the overloaded retrieve method to retrieve all executions
                # The method returns a list of executions in decreasing order by timestamp
                # The first entry in the list with the same choreography id is the predecessor
                executions = providers[0].retrieve('execution')

                # Retrieve the entry from the database in order to set its predecessor correctly
                temp = Execution()
                temp.workflow_instance_id = new_entry.workflow_instance_id
                db_entry = providers[0].retrieve('execution', temp)

                # Iterate over the list of executions in order to find an entry that has the same
                # choreography instance id as the entry being recorded
                for execution in executions:
                    # Make sure that the provenance hashes don't match
                    # so we don't set an object as its own predecessor
                    if execution.choreography_instance_id == db_entry.choreography_instance_id \
                            and execution.provenance_hash != new_entry.provenance_hash:
                        db_entry.predecessor = execution.provenance_hash
                provenance_session.commit()

            # If the entry is an adaptation convert the data accordingly
            elif entry_type == 'adaptation':
                new_entry = Adaptation()
                # Concatenate column values into string in order to hash.
                adaptation_provenance = entry[0] + \
                                        entry[1] + \
                                        str(entry[2]) + \
                                        str(entry[3]) + \
                                        entry[4] + \
                                        str(entry[5])
                provenance_hash = hashlib.sha256(adaptation_provenance.encode('utf-8')).hexdigest()
                new_entry.provenance_hash = provenance_hash
                new_entry.name = entry[0]
                new_entry.type = entry[1]
                new_entry.identifier = entry[2]
                new_entry.version = entry[3]
                new_entry.change = entry[4]
                new_entry.signature = entry[5]
                new_entry.entry_type = entry_type

                new_message.append(new_entry)

                for provider in providers:
                    provider.record([new_entry])

                # Link the user and the adaptation data in the controller database.
                controller_entry = AdaptationUserRelationship(identifier=new_entry.identifier, user_id=user.id)
                controller_session.add(controller_entry)
                try:
                    controller_session.commit()
                except:
                    controller_session.rollback()

                # Use the overloaded retrieve method to retrieve all adaptations
                # The method returns a list of adaptations in decreasing order by timestamp
                # The first entry in the list is the predecessor
                adaptations = providers[0].retrieve('adaptation')
                predecessor = adaptations[0].provenance_hash

                # Retrieve the entry from the database in order to set its predecessor correctly
                temp = Adaptation()
                temp.identifier = new_entry.identifier
                db_entry = providers[0].retrieve('adaptation', temp)
                db_entry.predecessor = predecessor
                provenance_session.commit()

    def migrate(self):
        pass
