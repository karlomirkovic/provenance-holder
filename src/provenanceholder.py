from src.components import adapter as a, provider as p, controller as c
import util


class ProvenanceHolder:
    def __init__(self):
        self.adapter = a.Adapter()
        self.controller = c.Controller()
        self.providers = [p.Provider()]


if __name__ == '__main__':
    provenance_holder = ProvenanceHolder()
    util.fill_dummy(provenance_holder)




