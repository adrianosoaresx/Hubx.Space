# Instruções para o Codex – ProjetoHubx (Lite DEV)

## 🧭 Contexto
Você atua no repositório `Hubx.Space` (Hubx.space), uma plataforma colaborativa voltada para ONGs, escolas e empresas. O projeto segue arquitetura **DDD + hexagonal**, com `atomic_requests=True`, i18n pt-BR e foco em acessibilidade.

---

## ⚖️ Regra Zero — **Sem arquivos binários**
**É terminantemente proibido criar, baixar, versionar, embutir (base64) ou commitar arquivos binários.**  
Inclui (exemplos): imagens (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`…), fontes (`.ttf`, `.otf`, `.woff`…), vídeos (`.mp4`, `.webm`…), áudios (`.mp3`, `.wav`…), documentos (`.pdf`, `.docx`, `.xlsx`…), compactados (`.zip`, `.rar`…), executáveis/compilados (`.exe`, `.dll`, `.so`, `.pyc`), bancos de dados (`.sqlite`, `.db`), modelos de IA (`.bin`, `.pth`, `.onnx`) e **qualquer blob base64**.

**Em vez disso, faça:**
- Use **placeholders textuais** (`src="__TODO_LOGO__"`), caminhos simulados e descrições em Markdown.
- Para ícones/ilustrações simples, é permitido **SVG textual inline pequeno** (sem base64, legível no diff).
- Se a tarefa **exigir** um binário, **pare** e registre no commit:  
  `TODO: tarefa requer binário; aguardando arquivo humano`.

> **Proibições explícitas**  
> - Não embutir `data:*;base64,` em nenhum arquivo.  
> - Não adicionar nem modificar binários já presentes.

---

## 📌 Stack
- **Backend**: Python 3.12 · Django 5 (DRF, SimpleJWT) · PostgreSQL · Celery  
- **Frontend**: HTML5 semântico · Tailwind CSS 3 · HTMX  

---

## 📂 Organização mínima
- `domain/`, `application/`, `infrastructure/` conforme DDD  
- `Serializers` em `application`, não em `domain`  
- `Model.clean()` para validações simples; regras em **Services**  
- Templates com HTML semântico (`<main>`, `<section>`, `aria-*`)

---

## ✅ Qualidade e segurança
- **Sanitizar entradas** e **validar permissões** sempre  
- Nunca expor dados sensíveis reais  
- **Acessibilidade** e **i18n pt-BR** obrigatórios  

*(Testes, cobertura e linters ficam desativados nesta fase DEV)*

---

## 🧪 Commits
- Use **Conventional Commits** (`feat:`, `fix:`, `refactor:`, `docs:`…)  
- Título ≤ 72 caracteres; corpo descrevendo **o que mudou** e **por quê**  
- **Commits direto em `main`** (fase DEV)  
- Se precisar de binários, deixe apenas `TODO`

**Exemplo**
```
feat(users): cria UserCreateSerializer (texto-apenas)

- Implementa serializer e validações simples em Model.clean()
- Mantém DDD: regras de negócio em services (application)
- TODO: avatar real será fornecido externamente (não versionar binários)
```

---

## 📄 Fontes de Verdade


---

## 📜 Checklist rápido
1. Verificar se envolve binários → se sim, parar e deixar `TODO`.  
2. Produzir apenas artefatos textuais (código, configs, docs).  
3. Para assets, usar placeholders (`/static/...`).  
4. Atualizar docs curtas em `docs/`.  
5. Comitar em `main` com Conventional Commit, sem binários/base64.

---

## ✅ Arquivos permitidos
Arquivos **permitidos**: `.py`, `.md`, `.html`, `.css`, `.js`, `.json`, `.yaml/.yml`, `.toml`, `.ini`, `.env.example`, `.sql`, `.sh`, `Dockerfile`, `.editorconfig`, `.pre-commit-config.yaml`, **`.svg` textual pequeno** (sem base64).

**Exemplo de placeholder em HTML**
```html
<img src="/static/img/__TODO_LOGO__.svg" alt="Logo do ProjetoHubx" width="144" height="48">
<!-- Arquivo real fornecido por humano; não versionar binários -->
```

**Exemplo de SVG textual mínimo**
```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" role="img" aria-label="ícone">
  <circle cx="12" cy="12" r="10" stroke="currentColor" fill="none"/>
  <path d="M8 12h8" stroke="currentColor" fill="none"/>
</svg>
```
## cobertura de testes 
- NÃO criar testes automatizados
- NÃO criar arquivos de test (pytest, unittest, jest, etc.)
- NÃO alterar ou adicionar cobertura de testes
- Focar exclusivamente no código solicitado