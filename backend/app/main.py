"""API FastAPI — doceria."""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.domain.pedido import calcular_pedido
from app.schemas import PedidoIn


# Origens padrão: dev local + front em produção no Railway (sobrescreva com CORS_ORIGINS se precisar).
_DEFAULT_CORS = (
    "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:4173,http://localhost:4173,"
    "https://browniesc14.up.railway.app"
)


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", _DEFAULT_CORS)
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(title="Brownie da Turma API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/pedido/calcular")
def calcular_pedido_api(pedido: PedidoIn) -> dict:
    try:
        itens = [item.model_dump() for item in pedido.itens]
        return calcular_pedido(itens, pedido.cupom)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
