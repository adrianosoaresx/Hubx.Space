#!/usr/bin/env python
"""
Script para popular a base de dados com dados iniciais para testes.

Este script cria duas organizações (CDL Florianópolis e CDL Blumenau),
um usuário root, dois usuários administradores (um por organização) e
cinquenta usuários associados para cada organização. Para cada organização
são criados também dois núcleos ("Núcleo da Mulher" e "Núcleo de Tecnologia")
e cada núcleo recebe quarenta participantes. Por fim, para cada
usuário associado é criada uma empresa ligada à mesma organização.

Execute este script com o ambiente Django configurado. Por exemplo:

```
python populate_data.py
```

O script utiliza o Faker para gerar nomes e descrições e a biblioteca
validate_docbr para gerar CPFs e CNPJs válidos.
"""

import os
import sys
import random
from typing import List

import django


def setup_django() -> None:
    """Configura o ambiente Django a partir da variável de ambiente padrão.

    Se `DJANGO_SETTINGS_MODULE` não estiver definido, assume
    ``Hubx.settings`` como padrão. Após definir, chama ``django.setup()``.
    """
    # Adiciona o diretório raiz do projeto ao sys.path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
    django.setup()

    # Configura o Celery para rodar tasks de forma síncrona (modo eager) durante o populate
    try:
        from celery import current_app
        current_app.conf.task_always_eager = True
    except ImportError:
        pass  # Celery não está instalado, ignora


def generate_unique_numbers(generator, count: int) -> List[str]:
    """Gera uma lista de números únicos usando o gerador fornecido.

    ``generator`` deve ser uma função sem argumentos que retorna
    uma string com um número (CPF ou CNPJ) válido. O algoritmo
    repete a geração até obter ``count`` números distintos.

    Args:
        generator: callable que retorna uma string representando
            um número válido (CPF ou CNPJ).
        count: quantidade de números distintos desejada.

    Returns:
        Lista de strings com números distintos.
    """
    seen = set()
    result: List[str] = []
    while len(result) < count:
        num = generator()
        # Garante unicidade na lista; evita números repetidos.
        if num not in seen:
            seen.add(num)
            result.append(num)
    return result


def main() -> None:
    """Função principal responsável por orquestrar a criação dos dados."""
    setup_django()

    # Importações tardias após django.setup()
    from django.contrib.auth import get_user_model
    from django.db import transaction
    from django.utils.text import slugify
    from faker import Faker
    from validate_docbr import CPF, CNPJ

    from accounts.models import UserType
    from empresas.models import Empresa
    from nucleos.models import Nucleo, ParticipacaoNucleo
    from organizacoes.models import Organizacao

    faker = Faker("pt_BR")

    User = get_user_model()

    # Cria organizações se ainda não existirem
    org_data = [
        {
            "nome": "CDL Florianópolis",
            "slug": slugify("CDL Florianópolis"),
            "tipo": "coletivo",
        },
        {
            "nome": "CDL Blumenau",
            "slug": slugify("CDL Blumenau"),
            "tipo": "coletivo",
        },
    ]

    # Gera CNPJs únicos para as organizações
    cnpj_generator = CNPJ()
    org_cnpjs = generate_unique_numbers(cnpj_generator.generate, len(org_data))

    organizacoes: List[Organizacao] = []
    for idx, org_info in enumerate(org_data):
        org, created = Organizacao.objects.get_or_create(
            slug=org_info["slug"],
            defaults={
                "nome": org_info["nome"],
                "cnpj": org_cnpjs[idx],
                "descricao": faker.sentence(),
                "tipo": org_info["tipo"],
                "rua": faker.street_name(),
                "cidade": faker.city(),
                "estado": faker.state_abbr(),
                "contato_nome": faker.name(),
                "contato_email": faker.email(),
                "contato_telefone": faker.phone_number(),
            },
        )
        organizacoes.append(org)

    # Cria usuário root se não existir
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            email="root@hubx.local",
            username="root",
            password="password123",
            first_name="Root",
            last_name="User",
        )

    # Função auxiliar para gerar CPFs únicos
    cpf_generator = CPF()

    @transaction.atomic
    def populate_for_org(org: Organizacao) -> None:
        """Popula dados específicos para uma organização.

        Cria um usuário admin, usuários associados, núcleos e empresas
        vinculadas a esta organização.

        Args:
            org: instância de ``Organizacao`` a ser populada.
        """
        # Cria admin se não existir para esta organização
        admin_email = f"admin_{slugify(org.nome)}@hubx.local"
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_user(
                email=admin_email,
                username=f"admin_{slugify(org.nome)}",
                password="password123",
                user_type=UserType.ADMIN,
                is_staff=True,
                first_name="Admin",
                last_name=org.nome.split()[1] if len(org.nome.split()) > 1 else "Admin",
                organizacao=org,
            )

        # Cria cinquenta associados para a organização
        # Gera CPFs únicos para estes usuários
        cpfs = generate_unique_numbers(cpf_generator.generate, 50)
        associados: List[User] = []
        for i in range(50):
            email = f"assoc_{slugify(org.nome)}_{i+1}@hubx.local"
            username = f"assoc_{slugify(org.nome)}_{i+1}"
            # Verifica se email já existe para evitar violação de unicidade
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                associados.append(user)
                continue
            user = User.objects.create_user(
                email=email,
                username=username,
                password="password123",
                user_type=UserType.ASSOCIADO,
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                organizacao=org,
                is_associado=True,
            )
            # Atribui CPF e dados opcionais
            user.cpf = cpfs[i]
            user.nome_completo = f"{user.first_name} {user.last_name}"
            user.address = faker.street_name()
            user.cidade = faker.city()
            user.estado = faker.state_abbr()
            user.save(update_fields=["cpf", "nome_completo", "address", "cidade", "estado"])
            associados.append(user)

        # Cria núcleos: Mulher e Tecnologia para a organização
        nucleos_data = [
            {
                "nome": "Núcleo da Mulher",
                "descricao": "Grupo dedicado às associadas mulheres.",
            },
            {
                "nome": "Núcleo de Tecnologia",
                "descricao": "Grupo dedicado a temas de tecnologia.",
            },
        ]
        created_nucleos: List[Nucleo] = []
        for nucleo_info in nucleos_data:
            nucleo, _ = Nucleo.objects.get_or_create(
                organizacao=org,
                slug=slugify(nucleo_info["nome"]),
                defaults={
                    "nome": nucleo_info["nome"],
                    "descricao": nucleo_info["descricao"],
                },
            )
            created_nucleos.append(nucleo)

        # Associa 40 usuários a cada núcleo (amostragem aleatória)
        if len(associados) >= 40:
            for nucleo in created_nucleos:
                membros = random.sample(associados, 40)
                for user in membros:
                    # Cria participação apenas se ainda não existir
                    ParticipacaoNucleo.objects.get_or_create(
                        user=user,
                        nucleo=nucleo,
                        defaults={
                            "papel": "membro",
                            "status": "ativo",
                        },
                    )
                    # Define o núcleo principal do usuário se ainda não tiver
                    if not user.nucleo:
                        user.nucleo = nucleo
                        user.save(update_fields=["nucleo"])

        # Cria uma empresa para cada usuário associado
        # Gera CNPJs únicos para as empresas desta organização
        empresa_cnpjs = generate_unique_numbers(cnpj_generator.generate, len(associados))
        for idx, user in enumerate(associados):
            empresa_nome = f"Empresa {user.first_name} {user.last_name}"
            Empresa.objects.create(
                usuario=user,
                organizacao=org,
                nome=empresa_nome,
                cnpj=empresa_cnpjs[idx],
                tipo=random.choice(["MEI", "LTDA", "SA"]),
                municipio=user.cidade or faker.city(),
                estado=user.estado or faker.state_abbr(),
                descricao=faker.sentence(),
                palavras_chave=faker.word(),
            )

    # Popula cada organização
    for org in organizacoes:
        populate_for_org(org)

    print("Dados de teste criados com sucesso!")


if __name__ == "__main__":
    main()