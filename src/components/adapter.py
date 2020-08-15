from metaclasses.adaptermeta import AdapterMeta


class Adapter(AdapterMeta):
    def retrieve(self, entry, provenance_holder, user, entry_type):
        result = provenance_holder.controller.retrieve(entry, provenance_holder.providers, entry_type)
        return result

    def collect(self, message, provenance_holder, user):
        provenance_holder.controller.record(message, provenance_holder.providers, user)
