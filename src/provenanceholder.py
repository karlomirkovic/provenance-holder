from src.components import adapter as a, provider as p, controller as c
import src.provenance_db.models as provenance_models
import src.controller_db.models as controller_models
import ed25519
import util
import config


class ProvenanceHolder:
    def __init__(self):
        self.adapter = a.Adapter()
        self.controller = c.Controller()
        self.providers = [p.Provider()]


if __name__ == '__main__':
    # Wipe the database before starting
    config.migrate_database()

    provenance_holder = ProvenanceHolder()
    private_key_1, public_key_1 = ed25519.create_keypair()
    user_1 = provenance_models.User(id=0,
                                    username='john_wayne',
                                    private_key_sk=private_key_1.sk_s,
                                    private_key_vk=private_key_1.vk_s)
    private_key_2, public_key_2 = ed25519.create_keypair()
    user_2 = provenance_models.User(id=1,
                                    username='karlo_mirkovic',
                                    private_key_sk=private_key_2.sk_s,
                                    private_key_vk=private_key_2.vk_s
                                    )

    pk_1 = controller_models.PublicKey(public_key_vk=public_key_1.vk_s,
                                       user_id=user_1.id)
    pk_2 = controller_models.PublicKey(public_key_vk=public_key_2.vk_s,
                                       user_id=user_2.id)
    config.provenance_session.add(user_1)
    config.provenance_session.add(user_2)
    config.provenance_session.commit()
    config.controller_session.add(pk_1)
    config.controller_session.add(pk_2)
    config.controller_session.commit()

    # Fill with dummy data for testing
    util.fill_dummy(provenance_holder, user_1)

    workflow = provenance_holder.adapter.retrieve(1, 'workflow', provenance_holder, user_2)
