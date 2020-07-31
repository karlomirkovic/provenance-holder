from metaclasses.providermeta import ProviderMeta
from ..provenance_db.models import ProvenanceEntry, Adaptation
from ..config import provenance_session
import datetime
import hashlib


class Provider(ProviderMeta):
    def retrieve(self, search_id, search_type):
        if search_type == 'workflow':
            workflow = provenance_session \
                .query(ProvenanceEntry) \
                .filter(ProvenanceEntry.workflow_instance_id == search_id) \
                .first()
            return workflow
        elif search_type == 'choreography':
            choreos = provenance_session \
                .query(ProvenanceEntry) \
                .filter(ProvenanceEntry.choreography_instance_id == search_id)
            return choreos
        else:
            adaptations = provenance_session\
                .query(Adaptation).filter(Adaptation.identifier == search_id)
            return adaptations

    def record(self, message):
        for entry in message:
            predecessor = provenance_session.\
                query(ProvenanceEntry).\
                filter(ProvenanceEntry.choreography_instance_id == entry.choreography_instance_id)\
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
            new_entry = ProvenanceEntry(provenance_hash=provenance_hash,
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
