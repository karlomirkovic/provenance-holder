import sqlalchemy

class Entry:
    def __init__(self):
        self.choreography_instance_id = None
        self.choreography_version = None
        self.workflow_instance_id = None
        self.workflow_version = None
        self.input = None
        self.invoke_signature = None
        self.output = None
        self.execute_signature = None


class Controller:
    def retrieve(self):
        pass

    def validate(self, message, user):
        new_message = []
        # A Message is a list of Entries
        # Entries from ESB look like this (chorid, chorver, workid, workver, input, b'invokesig, output, b'execsig)
        for entry in message:
            # entry[5] - invoke_signature
            # entry[7] - execute_signature
            invoke = str(entry[0]) + str(entry[1]) + str(entry[2]) + str(entry[3]) + str(entry[4])
            invoke = bytes(invoke, 'utf-8')
            try:
                user.public_key.verify(entry[5], invoke, encoding='hex')
                print("Invoke signature of user " + user.username + " is valid")
            except:
                print("Could not verify invoke signature of user " + user.username)
                print("Entry in message is ignored")

            execute = str(entry[5]) + entry[6]
            execute = bytes(execute, 'utf-8')

            try:
                user.public_key.verify(entry[7], execute, encoding='hex')
                print("Execute signature of user " + user.username + " is valid")
                new_message.append(entry)
            except:
                print("Could not verify execute signature of user " + user.username)
                print("Entry in message is ignored")

        return new_message

    # When the record method is called, the controller converts the data
    # into data that can be used by the providers and calls them to store it
    def record(self, message, provider):
        # A Message is a list of Entries
        # Entries from ESB look like this (chorid, chorver, workid, workver, input, invokesig, output, execsig)
        new_message = []
        for entry in message:
            new_entry = Entry()
            new_entry.choreography_instance_id = entry[0]
            new_entry.choreography_version = entry[1]
            new_entry.workflow_instance_id = entry[2]
            new_entry.workflow_version = entry[3]
            new_entry.input = entry[4]
            new_entry.invoke_signature = entry[5]
            new_entry.output = entry[6]
            new_entry.execute_signature = entry[7]
            new_entry.timestamp = None
            new_entry.predecessor = None

            new_message.append(new_entry)

        provider.record(new_message)

    def migrate(self):
        pass