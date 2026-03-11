from __future__ import annotations


class AccountsDomainError(Exception):
    """Base para erros de dominio do modulo de contas."""


class ProfileManagementPermissionDeniedError(AccountsDomainError):
    """Usuario autenticado sem permissao de gerenciamento para o alvo."""


class UserAlreadyActiveError(AccountsDomainError):
    """Tentativa de ativar um usuario que ja esta ativo."""


class UserAlreadyInactiveError(AccountsDomainError):
    """Tentativa de desativar um usuario que ja esta inativo."""


class InvalidProfileSectionError(AccountsDomainError):
    """Secao de perfil invalida para renderizacao parcial."""
