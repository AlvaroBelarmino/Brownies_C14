# Brownie da Turma

Aplicação web para montagem de pedidos e cálculo de orçamento de uma doceria. O sistema separa **backend** (API e regras de negócio em Python/FastAPI) e **frontend** (interface em React/TypeScript/Vite), com integração contínua no GitHub Actions.

### Aplicação em produção (Railway)

A interface está publicada em:

**[https://browniesc14.up.railway.app](https://browniesc14.up.railway.app)**

Assim dá para testar o fluxo (cardápio, cupom e orçamento) **sem rodar o projeto na máquina local**. A API em produção já deve estar configurada no build do front (`VITE_API_BASE`) e o CORS no backend para essa origem.

## Tecnologias

| Camada | Stack |
|--------|--------|
| Backend | Python 3.12+, FastAPI, Pydantic |
| Frontend | React 19, TypeScript, Vite 8 |
| Testes | pytest |
| CI/CD | GitHub Actions |

## Estrutura do repositório

```
├── backend/           # API REST e domínio do pedido
├── frontend/          # SPA do cliente (Vite + React)
├── .github/           # Workflows e scripts do pipeline
├── REGRAS.md          # Especificação de negócio (preços, descontos, frete, imposto)
├── EQUIPE.md          # Integrantes do grupo
└── README.md          # Este arquivo
```

---

## Backend

Concentra a lógica de cálculo (subtotal, desconto por volume, cupons, frete e imposto) e expõe endpoints HTTP.

### Organização principal

| Caminho | Função |
|---------|--------|
| `backend/app/main.py` | Aplicação FastAPI, CORS, rotas |
| `backend/app/schemas.py` | Modelos de entrada da API (Pydantic) |
| `backend/app/domain/pedido.py` | Regras de negócio do pedido |
| `backend/tests/` | Testes unitários e de API |

### Executar localmente

**Windows (PowerShell):**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Linux / macOS:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Com a API no ar:

- Documentação interativa (Swagger): `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`
- Healthcheck: `GET http://127.0.0.1:8000/health`

### Endpoint principal

`POST /api/pedido/calcular`

Exemplo de corpo JSON:

```json
{
  "itens": [
    { "sku": "B001", "preco_unitario": 8.0, "quantidade": 2 },
    { "sku": "B004", "preco_unitario": 10.0, "quantidade": 1 }
  ],
  "cupom": "PROMO10"
}
```

### Variáveis de ambiente (backend)

| Variável | Descrição |
|----------|-----------|
| `CORS_ORIGINS` | Lista separada por vírgulas das origens permitidas (ex.: `http://127.0.0.1:5173` para o Vite em desenvolvimento). |

### Testes

```bash
cd backend
python -m pytest -v
```

Relatório JUnit (útil no CI): `python -m pytest --junitxml=test-results.xml tests/`

---

## Frontend

Interface para escolher produtos, informar cupom e exibir o resumo do orçamento. Consome a API via `fetch` (JSON).

### Organização principal

| Caminho | Função |
|---------|--------|
| `frontend/src/App.tsx` | Páginas, layout e fluxo de pedido |
| `frontend/src/cardapio.ts` | Itens, preços e nomes dos arquivos de imagem |
| `frontend/src/ProductImage.tsx` | Exibição de foto com fallback quando a imagem não existe |
| `frontend/public/images/` | Imagens estáticas dos produtos (`b001.png` … `b004.png`) |
| `frontend/.env.example` | Modelo de variável `VITE_API_BASE` |

### Scripts npm

| Comando | Descrição |
|---------|-----------|
| `npm run dev` | Servidor de desenvolvimento (Vite, HMR) |
| `npm run build` | Typecheck (`tsc`) + build de produção em `frontend/dist` |
| `npm run preview` | Serve a pasta `dist` localmente |
| `npm run lint` | ESLint no código TypeScript/React |

### Executar localmente

```bash
cd frontend
npm ci
npm run dev
```

Abrir no navegador: `http://127.0.0.1:5173`

### Variáveis de ambiente (frontend)

| Variável | Descrição |
|----------|-----------|
| `VITE_API_BASE` | URL base da API (sem barra no final). Ex.: `http://127.0.0.1:8000`. Em produção, apontar para a URL pública do backend. |

Copie `frontend/.env.example` para `frontend/.env` e ajuste os valores.

### Build de produção

```bash
cd frontend
npm ci
npm run build
```

Saída em `frontend/dist/`, pronta para hospedagem estática ou servida pelo pipeline.

---

## Regras de negócio

As regras completas (cardápio, cupons, frete grátis, imposto, arredondamento e cenários de validação) estão em **[REGRAS.md](./REGRAS.md)**.

---

## Integração contínua e deploy

O workflow em [`.github/workflows/ci.yml`](.github/workflows/ci.yml) executa, em sequência:

1. **test-backend** — instala dependências Python, roda `pytest` com relatório JUnit e publica artefato.
2. **lint-frontend** — em paralelo com o job de testes do backend — `npm ci` e `npm run lint`.
3. **build** — depende dos dois anteriores; gera o build do frontend e empacota `dist` em ZIP (artefato).
4. **deploy** — apenas em push à `main`/`master`; dispara webhooks (Railway) via secrets.
5. **notify** — sempre ao final (`if: always()`); envia notificação por e-mail com script Python, usando secrets para SMTP e destinatários (sem credenciais no código).

Secrets necessários no repositório (GitHub → Settings → Secrets and variables → Actions) devem ser configurados pela equipe (webhooks Railway, SMTP, e-mails, etc.).

### Produção: Railway

O deploy em **produção** é feito na [Railway](https://railway.app): serviços separados para **API** (Python/Uvicorn) e **interface** (build estático do Vite ou serviço Node, conforme a configuração do grupo).

| Item | Observação |
|------|------------|
| **Disparo automático** | Push na `main`/`master` executa o workflow; o job `deploy` chama os **Deploy Hooks** configurados nos secrets `RAILWAY_WEBHOOK_BACK` e `RAILWAY_WEBHOOK_FRONT`. |
| **URL da API** | Defina no painel do Railway (variáveis do serviço backend). Use essa URL como **`VITE_API_BASE`** no **build** do frontend em produção, para o navegador chamar o backend correto. |
| **CORS** | No backend, `CORS_ORIGINS` deve incluir a **origem HTTPS** do front no Railway (ex.: `https://seu-front.up.railway.app`), além das URLs de desenvolvimento se ainda forem usadas. |

**URLs públicas (preencher com as do projeto):**

- API: `https://` *(colocar aqui a URL do serviço backend no Railway)*  
- Front: `https://` *(colocar aqui a URL do serviço frontend no Railway)*  

---

## Equipe

Integrantes e papéis: ver **[EQUIPE.md](./EQUIPE.md)**.

---

## Uso de ferramentas de IA

Conforme orientação da disciplina, registramos abaixo **quais prompts** foram utilizados e se o **resultado foi satisfatório** para cada integrante que fez uso de assistentes (ChatGPT, Copilot, Cursor, etc.).

### Guilherme da Silva Fernandes Almeida

**Prompts (exemplos):**

- Ajuda para montar pipeline de CI no GitHub Actions (testes, lint, build).
- Boas práticas para workflows com múltiplos jobs e paralelismo.
- Uso de variáveis de ambiente e secrets sem hardcode.
- Definição de pontos críticos para testes unitários (fluxo normal e extremos).
- Cenários de teste (fluxo normal vs. casos extremos) e cobertura de falhas.

**Resultado satisfatório?** Sim — auxiliou na organização do CI e na clareza dos cenários de teste.

---

### Eduardo Melo Bertozzi

**Prompts (exemplos):**

- Estruturação de job de deploy no GitHub Actions para Railway após build, lint e testes.
- Separação de serviços front (React/Vite) e back (Python/Uvicorn) no mesmo monorepo no Railway.
- Integração de webhooks de deploy com secrets do GitHub.
- Fluxo de Git/GitHub Actions para alterar `ci.yml` e abrir PR com segurança.
- Permissões e vinculação de plataformas de infraestrutura ao repositório.
- Redação de repasse técnico para configuração de infra e chaves de API.

**Resultado satisfatório?** Sim — contribuiu para o desenho do deploy e da integração com Railway.

---

### Álvaro Júlio César Belarmino

**Prompts utilizados (temas principais):**

- Leitura e interpretação do enunciço da disciplina (pipeline CI/CD, testes, deploy, artefatos) e alinhamento com uma ideia de projeto (doceria / brownies, stack FastAPI + React).
- Definição de arquitetura em monorepo, regras de negócio em `REGRAS.md` e roteiro de tarefas (backend, front, CI).
- Apoio na documentação inicial (`EQUIPE.md`, estrutura de pastas, `.gitignore`)
- Implementação do núcleo do backend (domínio do pedido, API, CORS) e do frontend (layout, integração com a API, imagens em `public/images/`); prompts para prompts de imagem e ajuste de nomes de arquivo.
- Revisão do README para ficar claro para correção (sem metadados inadequados), consolidação de tudo na raiz e seção de IA; inclusão da URL de produção no Railway.

**Resultado foi satisfatório?** Sim. Ajudou a organizar requisitos, estrutura do código e a documentação; a parte de deploy, CI avançado, testes unitários completos e integração com Railway ficou a cargo do grupo e foi ajustada em conjunto com os colegas após o merge no repositório.

---

## Licença e contexto

Projeto acadêmico desenvolvido para a disciplina de Engenharia de Software, com foco em qualidade de software, testes automatizados e pipeline CI/CD.
