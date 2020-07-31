from metaclasses.adaptermeta import AdapterMeta


class Adapter(AdapterMeta):
    def retrieve(self, search_id, search_type, provenance_holder, user):
        result = provenance_holder.controller.retrieve(search_id, search_type, provenance_holder.providers[0], user)

    def collect(self, message, provenance_holder, user):
        provenance_holder.controller.record(message, provenance_holder.providers[0], user)
