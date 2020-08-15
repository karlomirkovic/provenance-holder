import hashlib

import ed25519

from config import controller_session, provenance_session
from controller_db.models import ExecutionUserRelationship, AdaptationUserRelationship
from metaclasses.controllermeta import ControllerMeta
from controller_db.models import User


# The Execution and Adaptation classes are only used within the controller for two purposes
# Converting the data from the message into a format that can be used by the providers
# Comparing the retrieval results from each provider
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

    # Overload the equality operator in order to compare executions
    def __eq__(self, other):
        if not isinstance(other, Execution):
            # Don't attempt to compare against unrelated types
            return NotImplemented

        return self.provenance_hash == other.provenance_hash and \
               self.choreography_instance_id == other.choreography_instance_id and \
               self.choreography_version == other.choreography_version and \
               self.choreography_identifier == other.choreography_identifier and \
               self.workflow_instance_id == other.workflow_instance_id and \
               self.workflow_version == other.workflow_version and \
               self.input == other.input and \
               self.invoke_signature == other.invoke_signature and \
               self.output == other.output and \
               self.execute_signature == other.execute_signature and \
               self.timestamp == other.timestamp and \
               self.predecessor == other.predecessor


class Adaptation:
    def __init__(self):
        self.provenance_hash = None
        self.name = None
        self.type = None
        self.identifier = None
        self.version = None
        self.change = None
        self.signature = None
        self.timestamp = None
        self.predecessor = None
        self.entry_type = None

    # Overload the equality operator in order to compare adaptations
    def __eq__(self, other):
        if not isinstance(other, Adaptation):
            # Don't attempt to compare against unrelated types
            return NotImplemented

        return self.provenance_hash == other.provenance_hash and \
               self.name == other.name and \
               self.type == other.type and \
               self.identifier == other.identifier and \
               self.version == other.version and \
               self.change == other.change and \
               self.signature == other.signature and \
               self.timestamp == other.timestamp and \
               self.predecessor == other.predecessor


def compare_results(message, entry_type):
    # In the case that there is only one provider, there is no need for comparison
    if len(message) == 1:
        return 1

    # The message is a list of lists
    # It consists of data retrieval from the different providers
    # Iterate through the matrix column-wise and compare entries
    if entry_type == 'execution':
        for i in range(len(message)):
            entry_1 = Execution()
            entry_1.provenance_hash = message[i][0]
            entry_1.choreography_instance_id = message[i][1]
            entry_1.choreography_version = message[i][2]
            entry_1.choreography_identifier = message[i][3]
            entry_1.workflow_instance_id = message[i][4]
            entry_1.workflow_version = message[i][5]
            entry_1.workflow_identifier = message[i][6]
            entry_1.input = message[i][7]
            entry_1.invoke_signature = message[i][8]
            entry_1.output = message[i][9]
            entry_1.execute_signature = message[i][10]
            entry_1.timestamp = message[i][11]
            entry_1.predecessor = message[i][12]
            for j in range(len(message[i])):
                compare_entry = Execution()
                compare_entry.provenance_hash = message[j][0]
                compare_entry.choreography_instance_id = message[j][1]
                compare_entry.choreography_version = message[j][2]
                compare_entry.choreography_identifier = message[j][3]
                compare_entry.workflow_instance_id = message[j][4]
                compare_entry.workflow_version = message[j][5]
                compare_entry.workflow_identifier = message[j][6]
                compare_entry.input = message[j][7]
                compare_entry.invoke_signature = message[j][8]
                compare_entry.output = message[j][9]
                compare_entry.execute_signature = message[j][10]
                compare_entry.timestamp = message[j][11]
                compare_entry.predecessor = message[j][12]
                if entry_1 == compare_entry:
                    pass
                else:
                    print("Execution with provenance hash "
                          + str(compare_entry.provenance_hash)
                          + " from provider "
                          + str(i)
                          + " differs to the respective execution from provider 1.")
                    return 0
    elif entry_type == 'adaptation':
        for i in range(len(message)):
            entry_1 = Adaptation()
            entry_1.provenance_hash = message[0][i].provenance_hash
            entry_1.name = message[0][i].name
            entry_1.type = message[0][i].type
            entry_1.identifier = message[0][i].identifier
            entry_1.version = message[0][i].version
            entry_1.change = message[0][i].change
            entry_1.signature = message[0][i].signature
            entry_1.timestamp = message[0][i].timestamp
            entry_1.predecessor = message[0][i].predecessor
            for j in range(len(message[0])):
                print(message[j][i])
                compare_entry = Adaptation()
                compare_entry.provenance_hash = message[j][i].provenance_hash
                compare_entry.name = message[j][i].name
                compare_entry.type = message[j][i].type
                compare_entry.identifier = message[j][i].identifier
                compare_entry.version = message[j][i].version
                compare_entry.change = message[j][i].change
                compare_entry.signature = message[j][i].signature
                compare_entry.timestamp = message[j][i].timestamp
                compare_entry.predecessor = message[j][i].predecessor
                if entry_1 == compare_entry:
                    pass
                else:
                    print("Adaptation with provenance hash "
                          + str(compare_entry.provenance_hash)
                          + " from provider "
                          + str(i)
                          + " differs to the respective adaptation from provider 1.")
                    return 0
    else:
        print("The controller can not compare data of the entry type '" + entry_type + "'.")
    return 1


class Controller(ControllerMeta):
    # The retrieve method of the controller takes an entry for querying as a parameter
    # Together with the providers and entry type
    def retrieve(self, entry, providers, entry_type):
        # retrieve_results is the list of all provider entry lists
        retrieve_results = []
        for provider in providers:
            # The list of entries from each individual provider is stored in provider_results
            provider_results = []
            results = provider.retrieve(entry_type, entry)
            # If the entry type is an execution
            # A temporary list is created in order for the data to be in a format where it can be validated
            if entry_type == 'execution':
                # The retrieval of database entries is done by passing an entry with all attributes set to None
                # The only attribute that isn't None is the attribute that the user wants to query by
                for result in results:
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
                    entry_user = controller_session \
                        .query(User) \
                        .filter(User.id == eur.user_id) \
                        .first()
                    # The message is validated
                    new_message = self.validate([temp], entry_user)
                    if new_message:
                        new_message = result
                    else:
                        new_message = []
                        print("The message could not be fully validate. Returning empty list.")
                    provider_results.append(new_message)
                retrieve_results.append(provider_results)
            elif entry_type == 'adaptation':
                for result in results:
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
                    entry_user = controller_session \
                        .query(User) \
                        .filter(User.id == aur.user_id) \
                        .first()
                    # Validate the entry
                    new_message = self.validate([temp], entry_user)
                    # If the adaptation is validated, return it.
                    if new_message:
                        new_message = result
                    else:
                        new_message = []
                        print("The message could not be fully validate. Empty list returned.")
                    provider_results.append(new_message)
                retrieve_results.append(provider_results)
        if compare_results(retrieve_results, entry_type):
            print("The retrieve results match upon comparison.")
        else:
            print("The retrieve results do not match upon comparison. Empty list returned.")
            return []
        return retrieve_results[0]

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
                public_key = ed25519.VerifyingKey(ed25519.from_ascii(user.public_key, encoding='hex'))
                try:
                    public_key.verify(entry[7], invoke, encoding='hex')
                    public_key.verify(entry[9], execute, encoding='hex')
                    new_message.append(entry)
                    print("Validated signature of execution with workflow_id: " + str(entry[3]))
                except:
                    print("Could not validate signature of user " + user.username)
            # If the entry is an adaptation validate accordingly
            elif entry_type == 'adaptation':
                # The piece of data at entry[5] is the signature
                # Concatenate the data in order to recreate the original data that was signed
                sig_msg = entry[0] + str(entry[3]) + entry[4]
                sig_msg = bytes(sig_msg, 'utf-8')

                # Reconstruct the public key using the ed25519 constructor and validate
                public_key = ed25519.VerifyingKey(ed25519.from_ascii(user.public_key, encoding='hex'))
                try:
                    public_key.verify(entry[5], sig_msg, encoding='hex')
                    new_message.append(entry)
                    print("Validated signature of adaptation with identifier: " + str(entry[2]))
                except:
                    print("Could not validate signature of user " + user.username)
            else:
                print("Cannot validate an entry of the type: " + entry_type)
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
                db_entries = providers[0].retrieve('execution', temp)

                # Iterate over the list of executions in order to find an entry that has the same
                # choreography instance id as the entry being recorded
                for execution in executions:
                    for db_entry in db_entries:
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

                # Retrieve the entry from the database in order to set its predecessor correctly
                temp = Adaptation()
                temp.identifier = new_entry.identifier
                db_entries = providers[0].retrieve('adaptation', temp)
                for db_entry in db_entries:
                    if adaptations.count() > 1:
                        db_entry.predecessor = adaptations[1].provenance_hash
                    provenance_session.commit()

    def migrate(self):
        pass
