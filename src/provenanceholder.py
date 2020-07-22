from src.components import adapter as a, provider as p, controller as c
from src.db import models
import ed25519
import util


class ProvenanceHolder:
    def __init__(self):
        self.adapter = a.Adapter()
        self.controller = c.Controller()
        self.providers = [p.Provider()]


if __name__ == '__main__':
    provenance_holder = ProvenanceHolder()
    private_key, public_key = ed25519.create_keypair()
    user = models.User(id=0,
                       username='john_wayne',
                       private_key=private_key,
                       public_key=public_key)

    # Fill with dummy data for testing
    util.fill_dummy(provenance_holder, user)




