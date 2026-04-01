from itertools import product

from app.domain.pedido import calcular_pedido


def _item(sku: str, preco: float, qtd: int) -> dict:
    return {"sku": sku, "preco_unitario": preco, "quantidade": qtd}


def test_t9_cupom_aceita_todas_as_combinacoes_de_maiusculas_e_minusculas() -> None:
    item = [_item("B001", 8.0, 1)]
    esperado = calcular_pedido(item, "PROMO10")

    opcoes_por_caractere = [
        (caractere.lower(), caractere.upper()) if caractere.isalpha() else (caractere,)
        for caractere in "PROMO10"
    ]

    for combinacao in product(*opcoes_por_caractere):
        cupom = "".join(combinacao)
        resultado = calcular_pedido(item, cupom)
        assert resultado == esperado


def test_t18_fronteira_exatamente_80_aplica_frete_gratis() -> None:
    resultado = calcular_pedido([_item("B001", 8.0, 10)], None)

    assert resultado["subtotal_bruto"] == 80.0
    assert resultado["subtotal_apos_descontos"] == 80.0
    assert resultado["frete"] == 0.0
    assert resultado["imposto"] == 9.6
    assert resultado["total"] == 89.6
