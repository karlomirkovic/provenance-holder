from metaclasses.adaptermeta import AdapterMeta


def parse_message(message, message_type):
    return []


# The read_message method reads the message from the bus and uses invokes
# the parse_message method to convert the data into data usable by the controller
def read_message(message, provenance_holder):
    file = open(message, "r+")
    lines = file.readlines()
    # The first line in a message from the bus is the message type
    message_type = lines[0]
    lines.remove(lines[0])
    if message_type == "collect\n":
        user_id = lines[0]
        lines.remove(lines[0])
        # Parse the rest of the message which contains the data
        new_message = parse_message(lines, message_type)
        provenance_holder.adapter.collect(new_message, provenance_holder, user_id)
    elif message_type == "retrieve\n":
        # Parse the rest of the message which contains the data
        new_message = parse_message(lines, message_type)
        provenance_holder.adapter.retrieve(new_message, provenance_holder, message_type)
    file.close()


class Adapter(AdapterMeta):

    def retrieve(self, entry, provenance_holder, entry_type):
        result = provenance_holder.controller.retrieve(entry, provenance_holder.providers, entry_type)
        return result

    def collect(self, message, provenance_holder, user_id):
        provenance_holder.controller.record(message, provenance_holder.providers, user_id)
