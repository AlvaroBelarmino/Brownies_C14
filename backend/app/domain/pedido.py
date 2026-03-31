"""
Domínio do pedido — ver REGRAS.md na raiz do repositório.
"""

from __future__ import annotations

from typing import Any, TypedDict


class ItemPedido(TypedDict):
    sku: str
    preco_unitario: float
    quantidade: int


def _moeda(valor: float) -> float:
    return round(float(valor), 2)


def _percentual_cupom(cupom: str | None) -> float:
    if cupom is None:
        return 0.0
    normalizado = cupom.strip().upper()
    if not normalizado:
        return 0.0
    if normalizado == "PROMO10":
        return 0.10
    if normalizado == "INATEL5":
        return 0.05
    return 0.0


def _validar_itens(itens: list[ItemPedido]) -> None:
    for item in itens:
        q = int(item["quantidade"])
        p = float(item["preco_unitario"])
        if q <= 0:
            raise ValueError("Cada item deve ter quantidade maior que zero.")
        if p < 0:
            raise ValueError("Preço unitário não pode ser negativo.")


def calcular_pedido(
    itens: list[dict[str, Any]] | list[ItemPedido],
    cupom: str | None = None,
) -> dict[str, Any]:
    """
    Retorna totais monetários com 2 casas (round Python).
    Pedido vazio: todos os valores zero e frete zero (carrinho vazio sem cobrança de frete).
    """
    if not itens:
        return {
            "subtotal_bruto": 0.0,
            "desconto_volume": 0.0,
            "subtotal_apos_volume": 0.0,
            "desconto_cupom": 0.0,
            "subtotal_apos_descontos": 0.0,
            "frete": 0.0,
            "imposto": 0.0,
            "total": 0.0,
            "quantidade_total": 0,
        }

    lista: list[ItemPedido] = [
        {
            "sku": str(i["sku"]),
            "preco_unitario": float(i["preco_unitario"]),
            "quantidade": int(i["quantidade"]),
        }
        for i in itens
    ]
    _validar_itens(lista)

    subtotal_bruto = _moeda(
        sum(i["preco_unitario"] * i["quantidade"] for i in lista)
    )
    quantidade_total = sum(i["quantidade"] for i in lista)

    if quantidade_total >= 12:
        desconto_volume = _moeda(subtotal_bruto * 0.05)
        subtotal_apos_volume = _moeda(subtotal_bruto - desconto_volume)
    else:
        desconto_volume = 0.0
        subtotal_apos_volume = subtotal_bruto

    pct_cupom = _percentual_cupom(cupom)
    desconto_cupom = _moeda(subtotal_apos_volume * pct_cupom)
    subtotal_apos_descontos = _moeda(subtotal_apos_volume - desconto_cupom)

    # Frete grátis quando subtotal após descontos (já em 2 casas) >= 80
    frete = 0.0 if subtotal_apos_descontos >= 80.0 else 10.0
    frete = _moeda(frete)

    base_imposto = _moeda(subtotal_apos_descontos + frete)
    imposto = _moeda(base_imposto * 0.12)
    total = _moeda(subtotal_apos_descontos + frete + imposto)

    return {
        "subtotal_bruto": subtotal_bruto,
        "desconto_volume": desconto_volume,
        "subtotal_apos_volume": subtotal_apos_volume,
        "desconto_cupom": desconto_cupom,
        "subtotal_apos_descontos": subtotal_apos_descontos,
        "frete": frete,
        "imposto": imposto,
        "total": total,
        "quantidade_total": quantidade_total,
    }
