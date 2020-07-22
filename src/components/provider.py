from src.components.component import Component
from ..db.models import ProvenanceEntry
from ..config import session
import datetime
import hashlib


class Provider(Component):
    def retrieve(self):
        pass

    def validate(self):
        pass

    def record(self, message):
        entries = []
        for entry in message:
            # Concatenate column values into a string in order to hash
            provenance = str(entry.choreography_instance_id) + \
                         str(entry.choreography_version) + \
                         str(entry.workflow_instance_id) + \
                         str(entry.workflow_version) + \
                         entry.input + \
                         str(entry.invoke_signature) + \
                         entry.output + \
                         str(entry.execute_signature)

            provenance_hash = str(hashlib.sha256(provenance.encode('utf-8')))
            temp_entry = ProvenanceEntry(provenance_hash=provenance_hash,
                                         choreography_instance_id=entry.choreography_instance_id,
                                         choreography_version=entry.choreography_version,
                                         workflow_instance_id=entry.workflow_instance_id,
                                         workflow_version=entry.workflow_version,
                                         input=entry.input,
                                         invoke_signature=entry.invoke_signature,
                                         output=entry.output,
                                         execute_signature=entry.execute_signature,
                                         timestamp=datetime.datetime.now(),
                                         predecessor=entry.predecessor)
            entries.append(temp_entry)

        # Set the predecessor object
        for i in range(len(entries)):
            if i+1 <= len(entries):
                for j in range(i+1, len(entries)):
                    if entries[i].choreography_instance_id == entries[j].choreography_instance_id:
                        entries[j].predecessor = entries[i].provenance_hash

        # Add it to the database
        for entry in entries:
            session.add(entry)
            session.commit()




