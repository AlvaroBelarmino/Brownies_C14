"""Contratos HTTP da API."""

from pydantic import BaseModel, Field


class ItemPedidoIn(BaseModel):
    sku: str = Field(min_length=1)
    preco_unitario: float = Field(ge=0)
    quantidade: int = Field(gt=0)


class PedidoIn(BaseModel):
    itens: list[ItemPedidoIn]
    cupom: str | None = None
