import datetime

from metaclasses.providermeta import ProviderMeta
from ..config import provenance_session
from ..provenance_db.models import Execution, Adaptation


class Provider(ProviderMeta):
    # The retrieve method is overloaded and can be called with or without an entry
    # If called without and entry, it retrieves all the entries of the specified entry type
    def retrieve(self, entry_type, entry=None):
        results = []
        # If an entry is specified we query the database of the provider depending on the query attributes
        if entry is not None:
            query_column_keys = []
            if entry_type == 'execution':
                entries = provenance_session.query(Execution).order_by(Execution.timestamp.desc())
                for col in Execution.__table__.columns:
                    column_value = getattr(entry, str(col.key))
                    if column_value is not None:
                        query_column_keys.append(col.key)
            elif entry_type == 'adaptation':
                entries = provenance_session.query(Adaptation).order_by(Adaptation.timestamp.desc())
                for col in Adaptation.__table__.columns:
                    column_value = getattr(entry, str(col.key))
                    if column_value is not None:
                        query_column_keys.append(col.key)
            else:
                print("The provenance holder doesn't support that entry type.")
                return []

            for e in entries:
                for query_column_key in query_column_keys:
                    a_value = getattr(e, str(query_column_key))
                    s_value = getattr(entry, str(query_column_key))
                    if a_value == s_value:
                        if e not in results:
                            results.append(e)

            for r in results:
                for query_column_key in query_column_keys:
                    a_value = getattr(r, str(query_column_key))
                    s_value = getattr(entry, str(query_column_key))
                    if a_value != s_value:
                        results.remove(r)

        else:
            # The overloaded retrieve method has two trivial options
            # Querying all execution entries or querying all adaptation entries
            # The result is a list sorted by timestamp in decreasing order
            if entry_type == 'execution':
                results = provenance_session.query(Execution).order_by(Execution.timestamp.desc())
            elif entry_type == 'adaptation':
                results = provenance_session.query(Adaptation).order_by(Adaptation.timestamp.desc())
        return results

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
