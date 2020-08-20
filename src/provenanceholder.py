import ed25519

import config
import src.controller_db.models as controller_models
import util
from src.components import adapter as a, provider as p, controller as c
from provenance_db.models import Execution, Adaptation


class ProvenanceHolder:
    def __init__(self):
        self.adapter = a.Adapter()
        self.controller = c.Controller()
        self.providers = []


if __name__ == '__main__':
    # Wipe the database before starting
    config.migrate_database()

    provenance_holder = ProvenanceHolder()
    provenance_holder.providers.append(p.Provider(config.provenance_session))
    private_key_1, public_key_1 = ed25519.create_keypair()
    user_1 = controller_models.User(id=0,
                                    username='ludwig_stage',
                                    public_key=public_key_1.to_ascii(encoding='hex'),
                                    private_key=private_key_1.to_ascii(encoding='hex'))

    private_key_2, public_key_2 = ed25519.create_keypair()
    user_2 = controller_models.User(id=1,
                                    username='karlo_mirkovic',
                                    public_key=public_key_2.to_ascii(encoding='hex'),
                                    private_key=private_key_2.to_ascii(encoding='hex'))
    config.controller_session.add(user_1)
    config.controller_session.add(user_2)
    config.controller_session.commit()

    # Fill with dummy data for testing
    util.fill_dummy(provenance_holder, user_1)
    query_entry_1 = Execution(provenance_hash=None,
                              choreography_instance_id=0,
                              choreography_version=1.3,
                              choreography_identifier=None,
                              workflow_instance_id=None,
                              workflow_version=None,
                              workflow_identifier=None,
                              input=None,
                              invoke_signature=None,
                              output=None,
                              execute_signature=None,
                              timestamp=None,
                              predecessor=None)

    query_entry_2 = Adaptation(provenance_hash=None,
                               name=None,
                               type='add',
                               identifier=None,
                               version=1.0,
                               change=None,
                               signature=None,
                               timestamp=None,
                               predecessor=None)


    # Demo of retrieve operation
    retrieve_results_1 = provenance_holder.adapter.retrieve(query_entry_1, provenance_holder, 'execution')
    # retrieve_results_2 = provenance_holder.adapter.retrieve(query_entry_2, provenance_holder, 'adaptation')
    #
    for r in retrieve_results_1:
        print(r)

    # entries = provenance_holder.providers[0].retrieve('adaptation')
    # for a in adaptations:
    #     print(a)



