# Brownie da Turma

Aplicação web para montagem de pedidos e cálculo de orçamento (subtotais, descontos, frete e impostos). Regras de negócio em `REGRAS.md`.

## Tecnologias

- **Backend:** Python, FastAPI
- **Frontend:** React, TypeScript, Vite

## Estrutura

- `backend/` — API e domínio do pedido
- `frontend/` — interface do cliente

## Execução local

### Backend (porta 8000)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentação interativa: `http://127.0.0.1:8000/docs`

### Frontend (porta 5173)

```bash
cd frontend
npm ci
npm run dev
```

Variável opcional `VITE_API_BASE` (ver `frontend/.env.example`). No servidor, ajustar também `CORS_ORIGINS` na API.

## Documentação

As regras de precificação, descontos e impostos estão em **[REGRAS.md](./REGRAS.md)**.

## Integração contínua

Workflows em `.github/workflows/`.
