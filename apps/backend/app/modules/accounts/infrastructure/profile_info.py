from __future__ import annotations

from accounts.forms import InformacoesPessoaisForm


class DjangoProfileInfoFormGateway:
    def create_bound(self, *, data, files, instance) -> InformacoesPessoaisForm:
        return InformacoesPessoaisForm(data, files, instance=instance)

    def create_unbound(self, *, instance) -> InformacoesPessoaisForm:
        return InformacoesPessoaisForm(instance=instance)
