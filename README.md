# Brownie da Turma

Aplicacao web para montagem de pedidos e calculo de orcamento de uma doceria. O projeto possui frontend em React e backend em FastAPI, com regras de negocio para subtotal, desconto por volume, cupons, frete e imposto.

## Tecnologias

- Backend: Python, FastAPI e Pydantic
- Frontend: React, TypeScript e Vite
- Testes: Pytest
- CI: GitHub Actions

## Estrutura

- `backend/`: API, dominio do pedido e testes automatizados
- `frontend/`: interface web do cliente
- `.github/workflows/`: pipeline de CI
- `REGRAS.md`: regras de negocio do calculo

## Backend

O backend expoe a API de calculo de pedidos e concentra a logica principal do projeto.

### Estrutura do backend

- `backend/app/main.py`: inicializacao da API, rotas e CORS
- `backend/app/schemas.py`: contratos HTTP de entrada
- `backend/app/domain/pedido.py`: regras de negocio do calculo do pedido
- `backend/tests/`: testes unitarios do dominio e da API

### Como executar o backend

No Windows:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

No Linux ou macOS:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Com a API em execucao:

- Swagger: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`
- Healthcheck: `http://127.0.0.1:8000/health`

### Endpoint principal do backend

`POST /api/pedido/calcular`

Exemplo de requisicao:

```json
{
  "itens": [
    {
      "sku": "B001",
      "preco_unitario": 8.0,
      "quantidade": 2
    },
    {
      "sku": "B004",
      "preco_unitario": 10.0,
      "quantidade": 1
    }
  ],
  "cupom": "PROMO10"
}
```

### Testes do backend

Para rodar os testes:

```powershell
cd backend
.\.venv\Scripts\python -m pytest -v
```

Os testes cobrem:

- fluxo normal do calculo do pedido
- casos de borda e validacoes
- comportamento da API em sucesso, erro 400 e erro 422
- configuracao de CORS

### Variavel de ambiente do backend

`CORS_ORIGINS`

Exemplo:

```env
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

## Frontend

O frontend oferece a interface para selecionar produtos, informar cupom e consultar o resumo do pedido em tempo real.

### Como executar o frontend

```bash
cd frontend
npm ci
npm run dev
```

Aplicacao local:

- `http://127.0.0.1:5173`

### Variavel de ambiente do frontend

`VITE_API_BASE`

Essa variavel permite apontar o frontend para uma URL diferente da API.

Exemplo:

```env
VITE_API_BASE=http://127.0.0.1:8000
```

O arquivo de exemplo esta em `frontend/.env.example`.

## Regras de negocio

As regras completas de precificacao, descontos, frete e imposto estao documentadas em [REGRAS.md](./REGRAS.md).

## Integracao continua

O pipeline do GitHub Actions fica em `.github/workflows/ci.yml` e atualmente executa:

- testes unitarios do backend
- lint do frontend
- build do frontend
- notificacao por e-mail ao final da execucao

## Observacao

O projeto foi organizado com separacao clara entre frontend, backend, regras de negocio e testes automatizados, facilitando manutencao e evolucao.
