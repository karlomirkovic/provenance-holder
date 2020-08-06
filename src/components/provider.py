import datetime

from metaclasses.providermeta import ProviderMeta
from ..config import provenance_session
from ..provenance_db.models import Execution, Adaptation


class Provider(ProviderMeta):
    # The retrieve method is overloaded and can be called with or without an entry
    # If called without and entry, it retrieves all the entries of the specified entry type
    def retrieve(self, entry_type, entry=None):
        result = None
        # If an entry is specified we query the database of the provider depending on the entry type
        if entry is not None:
            # In the case of a query for an execution there are two choices
            # One choice is a list of database entries with the same choreography instance id
            # The other choice is merely specifying a workflow instance id and receiving one entry
            if entry_type == 'execution':
                if entry.workflow_instance_id is not None:
                    result = provenance_session \
                        .query(Execution) \
                        .filter(Execution.workflow_instance_id == entry.workflow_instance_id) \
                        .first()
                elif entry.choreography_instance_id is not None:
                    result = provenance_session \
                        .query(Execution) \
                        .filter(Execution.choreography_instance_id == entry.choreography_instance_id)
            # In the case of a query for an adaptation the user receives one entry
            # The query is based on the identifier that is specified by the user
            elif entry_type == 'adaptation':
                result = provenance_session \
                    .query(Adaptation) \
                    .filter(Adaptation.identifier == entry.identifier) \
                    .first()
            else:
                print("The provenance holder doesn't support that entry type.")
        else:
            # The overloaded retrieve method has two trivial options
            # Querying all execution entries or querying all adaptation entries
            # The result is a list sorted by timestamp in decreasing order
            if entry_type == 'execution':
                result = provenance_session.query(Execution).order_by(Execution.timestamp.desc())
            elif entry_type == 'adaptation':
                result = provenance_session.query(Adaptation).order_by(Adaptation.timestamp.desc())
        return result

    def record(self, message):
        for entry in message:
            # If the entry type is an execution
            # The provider creates and instance of that object and fills it with data appropriately
            if entry.entry_type == 'execution':
                new_entry = Execution(provenance_hash=entry.provenance_hash,
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
            # If the entry type is an adaptation
            # The provider creates and instance of that object and fills it with data appropriately
            elif entry.entry_type == 'adaptation':
                new_entry = Adaptation(provenance_hash=entry.provenance_hash,
                                       name=entry.name,
                                       type=entry.type,
                                       identifier=entry.identifier,
                                       version=entry.version,
                                       change=entry.change,
                                       signature=entry.signature,
                                       timestamp=datetime.datetime.now(),
                                       predecessor=entry.predecessor)

                provenance_session.add(new_entry)

            else:
                print('You are attempting to record a type of entry not supported by the provenance holder.')
                break

        provenance_session.commit()

    def migrate(self):
        pass
