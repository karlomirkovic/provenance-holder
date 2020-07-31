import datetime
import hashlib

from metaclasses.providermeta import ProviderMeta
from ..config import provenance_session
from ..provenance_db.models import Execution, Adaptation


class Provider(ProviderMeta):
    def retrieve(self, search_id, search_type, entry_type):
        result = None
        if entry_type == 'execution':
            if search_type == 'workflow':
                result = provenance_session \
                    .query(Execution) \
                    .filter(Execution.workflow_instance_id == search_id) \
                    .first()
            elif search_type == 'choreography':
                result = provenance_session \
                    .query(Execution) \
                    .filter(Execution.choreography_instance_id == search_id)
        elif entry_type == 'adaptation':
                result = provenance_session\
                    .query(Adaptation)\
                    .filter(Adaptation.identifier == search_id)
        else:
            print("The provenance holder doesn't support that entry type.")

        return result

    def record(self, message):
        for entry in message:
            if entry.entry_type == 'execution':
                predecessor = provenance_session. \
                    query(Execution). \
                    filter(Execution.choreography_instance_id == entry.choreography_instance_id) \
                    .first()

                if predecessor is not None:
                    entry.predecessor = predecessor.provenance_hash
                else:
                    entry.predecessor = None

                provenance_session.commit()

                # Concatenate column values into a string in order to hash
                provenance = str(entry.choreography_instance_id) + \
                             str(entry.choreography_version) + \
                             str(entry.choreography_identifier) + \
                             str(entry.workflow_instance_id) + \
                             str(entry.workflow_version) + \
                             str(entry.workflow_identifier) + \
                             entry.input + \
                             str(entry.invoke_signature) + \
                             entry.output + \
                             str(entry.execute_signature) + \
                             str(entry.timestamp) + \
                             str(entry.predecessor)

                provenance_hash = str(hashlib.sha256(provenance.encode('utf-8')))
                new_entry = Execution(provenance_hash=provenance_hash,
                                      choreography_instance_id=entry.choreography_instance_id,
                                      choreography_version=entry.choreography_version,
                                      choreography_identifier=entry.choreography_identifier,
                                      workflow_instance_id=entry.workflow_instance_id,
                                      workflow_version=entry.workflow_version,
                                      workflow_identifier=entry.workflow_identifier,
                                      input=entry.input,
                                      invoke_signature=entry.invoke_signature,
                                      output=entry.output,
                                      execute_signature=entry.execute_signature,
                                      timestamp=datetime.datetime.now(),
                                      predecessor=entry.predecessor)

                provenance_session.add(new_entry)
                provenance_session.commit()

            elif entry.entry_type == 'adaptation':
                predecessor = provenance_session. \
                    query(Adaptation)\
                    .order_by(Adaptation.timestamp.desc())\
                    .first()

                if not predecessor:
                    entry.predecessor = None
                else:
                    entry.predecessor = predecessor.provenance_hash

                provenance_session.commit()
                # Concatenate column values into string in order to hash
                adaptation_provenance = entry.name + \
                                        entry.type + \
                                        str(entry.identifier) + \
                                        str(entry.version) + \
                                        entry.change + \
                                        str(entry.signature)
                provenance_hash = str(hashlib.sha256(adaptation_provenance.encode('utf-8')))
                new_entry = Adaptation(provenance_hash=provenance_hash,
                                       name=entry.name,
                                       type=entry.type,
                                       identifier=entry.identifier,
                                       version=entry.version,
                                       change=entry.change,
                                       signature=entry.signature,
                                       timestamp=datetime.datetime.now(),
                                       predecessor=entry.predecessor)

                provenance_session.add(new_entry)
                provenance_session.commit()

            else:
                print('You are attempting to record a type of entry not supported by the provenance holder.')
                break
