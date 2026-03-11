Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Python da venv nao encontrado em $python"
}

$runStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$historyPath = "docs/etapas/smoke_etapa2_baseline_history.md"
$runStatus = "SUCCESS"
$stepResults = New-Object System.Collections.Generic.List[string]

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    Write-Host "==> $Name"
    & $Action
    if ($LASTEXITCODE -ne 0) {
        $script:stepResults.Add("- ${Name}: FAIL (codigo $LASTEXITCODE)")
        throw "Falha na etapa '$Name' com codigo $LASTEXITCODE"
    }
    $script:stepResults.Add("- ${Name}: OK")
    Write-Host "<== OK: $Name"
}

try {
    Invoke-Step -Name "Django check" -Action {
        & $python manage.py check
    }

    Invoke-Step -Name "Regressao dirigida Etapa 2/3/4" -Action {
        & $python -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q
    }

    Invoke-Step -Name "Smoke HTTP local (GET + POST controlado)" -Action {
        $code = @'
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from accounts.models import UserType
from eventos.models import Evento, InscricaoEvento
from nucleos.models import Nucleo
from pagamentos.models import Transacao
from pagamentos.services.pagamento import PagamentoService

User = get_user_model()
user = User.objects.filter(
    user_type__in=[UserType.ADMIN.value, UserType.OPERADOR.value],
    organizacao__isnull=False,
    is_active=True,
).order_by("id").first()
if not user:
    raise SystemExit("SMOKE_ERROR: sem usuario de negocio valido (admin/operador).")

client = Client()
client.force_login(user)
org = user.organizacao

paths = {
    "conexoes": reverse("conexoes:perfil_sections_conexoes"),
    "pix_get": reverse("pagamentos:pix-checkout"),
    "faturamento_get": reverse("pagamentos:faturamento-checkout"),
}

for label, path in paths.items():
    resp = client.get(path)
    if resp.status_code != 200:
        raise SystemExit(f"SMOKE_ERROR: {label} retornou {resp.status_code} em {path}")
    print(f"SMOKE_{label.upper()}:{path}|{resp.status_code}")

# POST controlado de membros: cenário inválido esperado (coordenação sem papel)
target = User.objects.filter(organizacao=org, is_active=True).exclude(id=user.id).order_by("id").first()
if not target:
    target = User.objects.create_user(
        username=f"smoke_target_{user.id}",
        email=f"smoke_target_{user.id}@hubx.local",
        password="Smoke@123",
        user_type=UserType.CONVIDADO.value,
        organizacao=org,
    )
nucleo = Nucleo.objects.filter(organizacao=org).order_by("id").first()
if not nucleo:
    nucleo = Nucleo.objects.create(organizacao=org, nome=f"Smoke Nucleo {str(org.id)[:8]}")

membros_path = reverse("membros:membro_promover_form", kwargs={"pk": target.pk})
membros_invalid = client.post(membros_path, data={"coordenador_nucleos": [str(nucleo.id)]})
if membros_invalid.status_code != 400:
    raise SystemExit(
        f"SMOKE_ERROR: membros POST invalido esperava 400 e retornou {membros_invalid.status_code}"
    )
print(f"SMOKE_MEMBROS_POST_INVALID:{membros_path}|{membros_invalid.status_code}")

# POST controlado de pagamentos (Pix com stub local de provider/service)
evento = Evento.objects.filter(organizacao=org).order_by("id").first() or Evento.objects.order_by("id").first()
if not evento:
    raise SystemExit("SMOKE_ERROR: sem evento disponivel para checkout/faturamento.")
inscricao, _ = InscricaoEvento.all_objects.get_or_create(user=user, evento=evento)
if inscricao.deleted:
    inscricao.deleted = False
    inscricao.deleted_at = None
    inscricao.save(update_fields=["deleted", "deleted_at", "updated_at"])

orig_iniciar = PagamentoService.iniciar_pagamento
def _fake_iniciar_pagamento(self, pedido, metodo, dados_pagamento):
    return Transacao.objects.create(
        pedido=pedido,
        valor=pedido.valor,
        status=Transacao.Status.APROVADA,
        metodo=metodo,
        detalhes={"status": "approved", "baseline_script": True},
    )

PagamentoService.iniciar_pagamento = _fake_iniciar_pagamento
try:
    pix_post = client.post(
        reverse("pagamentos:pix-checkout"),
        data={
            "valor": "120.00",
            "metodo": Transacao.Metodo.PIX,
            "email": user.email or "baseline@example.com",
            "nome": user.get_full_name() or user.username,
            "documento": "12345678909",
            "inscricao_uuid": str(inscricao.uuid),
            "organizacao_id": str(org.id),
        },
    )
finally:
    PagamentoService.iniciar_pagamento = orig_iniciar
if pix_post.status_code != 302:
    raise SystemExit(f"SMOKE_ERROR: pix POST esperava 302 e retornou {pix_post.status_code}")
print(f"SMOKE_PIX_POST:{reverse('pagamentos:pix-checkout')}|{pix_post.status_code}")

# POST controlado de faturamento
fat_post = client.post(
    reverse("pagamentos:faturamento-checkout"),
    data={
        "valor": "120.00",
        "condicao_faturamento": "2x",
        "inscricao_uuid": str(inscricao.uuid),
        "organizacao_id": str(org.id),
    },
)
if fat_post.status_code != 302:
    raise SystemExit(
        f"SMOKE_ERROR: faturamento POST esperava 302 e retornou {fat_post.status_code}"
    )
print(f"SMOKE_FAT_POST:{reverse('pagamentos:faturamento-checkout')}|{fat_post.status_code}")
'@
        $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($tempFile, $code, $utf8NoBom)
        try {
            & $python manage.py shell -c "exec(open(r'$tempFile', encoding='utf-8').read())"
        }
        finally {
            if (Test-Path $tempFile) {
                Remove-Item $tempFile -Force
            }
        }
    }
}
catch {
    $runStatus = "FAIL"
    Write-Error $_
}
finally {
    if (-not (Test-Path $historyPath)) {
        "# Historico Smoke Etapa 2 Baseline`n" | Out-File -FilePath $historyPath -Encoding utf8
    }
    $entry = @()
    $entry += "## $runStamp"
    $entry += "- status: $runStatus"
    $entry += "- script: scripts/smoke_etapa2_baseline.ps1"
    $entry += "- etapas:"
    $entry += $stepResults
    $entry += ""
    Add-Content -Path $historyPath -Value ($entry -join "`n")

    if ($runStatus -eq "SUCCESS") {
        Write-Host "Smoke baseline da Etapa 2 concluido com sucesso."
    }
    else {
        Write-Error "Smoke baseline da Etapa 2 finalizou com falha."
        exit 1
    }
}
