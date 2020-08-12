import ed25519

import config
import src.provenance_db.models as provenance_models
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
    user_1 = provenance_models.User(id=0,
                                    username='ludwig_stage',
                                    private_key_sk=private_key_1.sk_s,
                                    private_key_vk=private_key_1.vk_s)
    private_key_2, public_key_2 = ed25519.create_keypair()
    user_2 = provenance_models.User(id=1,
                                    username='karlo_mirkovic',
                                    private_key_sk=private_key_2.sk_s,
                                    private_key_vk=private_key_2.vk_s)
    config.provenance_session.add(user_1)
    config.provenance_session.add(user_2)
    config.provenance_session.commit()

    # Fill with dummy data for testing
    util.fill_dummy(provenance_holder, user_1)
    search_entry_1 = Execution(provenance_hash=None,
                               choreography_instance_id=0,
                               choreography_version=None,
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

    search_entry_2 = Adaptation(provenance_hash=None,
                                name=None,
                                type='add',
                                identifier=None,
                                version=None,
                                change=None,
                                signature=None,
                                timestamp=None,
                                predecessor=None)

    adaptations = provenance_holder.providers[0].retrieve('adaptation')
    results = provenance_holder.controller.retrieve(search_entry_2, provenance_holder.providers, 'adaptation')

    for p in adaptations:
        print(p)
    # for r in results:
    #     for k in r:
    #         print(k)
