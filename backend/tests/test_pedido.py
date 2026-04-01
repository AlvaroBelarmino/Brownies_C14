from itertools import product

import pytest

from app.domain.pedido import calcular_pedido


def _item(sku: str, preco: float, qtd: int) -> dict:
    return {"sku": sku, "preco_unitario": preco, "quantidade": qtd}


# Fluxo normal


def test_t1_um_item_sem_cupom_com_frete_cobrado() -> None:
    resultado = calcular_pedido([_item("B001", 8.0, 1)], None)

    assert resultado["subtotal_bruto"] == 8.0
    assert resultado["desconto_volume"] == 0.0
    assert resultado["desconto_cupom"] == 0.0
    assert resultado["subtotal_apos_descontos"] == 8.0
    assert resultado["frete"] == 10.0
    assert resultado["imposto"] == 2.16
    assert resultado["total"] == 20.16
    assert resultado["quantidade_total"] == 1


def test_t2_varios_itens_sem_cupom_abaixo_do_frete_gratis() -> None:
    resultado = calcular_pedido([_item("B001", 8.0, 2), _item("B004", 10.0, 1)], None)

    assert resultado["subtotal_bruto"] == 26.0
    assert resultado["frete"] == 10.0
    assert resultado["imposto"] == 4.32
    assert resultado["total"] == 40.32


def test_t3_subtotal_apos_descontos_atinge_frete_gratis() -> None:
    resultado = calcular_pedido([_item("B002", 12.0, 10)], None)

    assert resultado["subtotal_bruto"] == 120.0
    assert resultado["subtotal_apos_descontos"] == 120.0
    assert resultado["frete"] == 0.0
    assert resultado["imposto"] == 14.4
    assert resultado["total"] == 134.4


def test_t4_desconto_volume_aplicado_antes_de_cupom() -> None:
    resultado = calcular_pedido([_item("B001", 8.0, 12)], None)

    assert resultado["subtotal_bruto"] == 96.0
    assert resultado["desconto_volume"] == 4.8
    assert resultado["subtotal_apos_volume"] == 91.2
    assert resultado["quantidade_total"] == 12


def test_t5_cupom_promo10_sem_desconto_por_volume() -> None:
    resultado = calcular_pedido([_item("B002", 12.0, 1)], "PROMO10")

    assert resultado["subtotal_bruto"] == 12.0
    assert resultado["desconto_volume"] == 0.0
    assert resultado["desconto_cupom"] == 1.2
    assert resultado["subtotal_apos_descontos"] == 10.8
    assert resultado["frete"] == 10.0
    assert resultado["imposto"] == 2.5
    assert resultado["total"] == 23.3


def test_t6_cupom_inatel5_com_desconto_por_volume() -> None:
    resultado = calcular_pedido([_item("B001", 8.0, 12)], "INATEL5")

    assert resultado["subtotal_apos_volume"] == 91.2
    assert resultado["desconto_cupom"] == 4.56
    assert resultado["subtotal_apos_descontos"] == 86.64
    assert resultado["frete"] == 0.0
    assert resultado["imposto"] == 10.4
    assert resultado["total"] == 97.04


def test_t7_um_unico_sku_com_quantidade_alta() -> None:
    resultado = calcular_pedido([_item("B001", 8.0, 15)], None)

    assert resultado["quantidade_total"] == 15
    assert resultado["desconto_volume"] == 6.0
    assert resultado["subtotal_apos_descontos"] == 114.0
    assert resultado["frete"] == 0.0
    assert resultado["imposto"] == 13.68
    assert resultado["total"] == 127.68


def test_t8_precos_com_centavos_mantem_arredondamento_estavel() -> None:
    resultado = calcular_pedido([_item("B001", 8.99, 1)], None)

    assert resultado["subtotal_bruto"] == 8.99
    assert resultado["frete"] == 10.0
    assert resultado["imposto"] == 2.28
    assert resultado["total"] == 21.27


def test_t9_cupom_com_espacos_e_case_insensitive() -> None:
    item = [_item("B001", 8.0, 1)]
    esperado = calcular_pedido(item, "PROMO10")
    opcoes_por_caractere = [
        (caractere.lower(), caractere.upper()) if caractere.isalpha() else (caractere,)
        for caractere in "PROMO10"
    ]

    for combinacao in product(*opcoes_por_caractere):
        cupom = "".join(combinacao)
        assert calcular_pedido(item, cupom) == esperado
        assert calcular_pedido(item, f"  {cupom}  ") == esperado


def test_t10_varias_linhas_batem_com_soma_manual() -> None:
    resultado = calcular_pedido([_item("B001", 8.0, 2), _item("B002", 12.0, 1)], None)

    assert resultado["subtotal_bruto"] == 28.0


# Fluxo de extensão


def test_t11_lista_vazia_retorna_zeros_e_sem_frete() -> None:
    resultado = calcular_pedido([], None)

    assert resultado["subtotal_bruto"] == 0.0
    assert resultado["frete"] == 0.0
    assert resultado["imposto"] == 0.0
    assert resultado["total"] == 0.0
    assert resultado["quantidade_total"] == 0


def test_t12_quantidade_zero_rejeita_item() -> None:
    with pytest.raises(ValueError, match="quantidade"):
        calcular_pedido([_item("B001", 8.0, 0)], None)


def test_t13_quantidade_negativa_rejeita_item() -> None:
    with pytest.raises(ValueError, match="quantidade"):
        calcular_pedido([_item("B001", 8.0, -1)], None)


def test_t14_preco_zero_e_aceito_como_brinde() -> None:
    resultado = calcular_pedido([_item("B001", 0.0, 1)], None)

    assert resultado["subtotal_bruto"] == 0.0
    assert resultado["frete"] == 10.0
    assert resultado["imposto"] == 1.2
    assert resultado["total"] == 11.2


def test_t15_preco_negativo_rejeita_item() -> None:
    with pytest.raises(ValueError, match="negativo"):
        calcular_pedido([_item("B001", -1.0, 1)], None)


def test_t16_cupom_invalido_e_ignorado() -> None:
    com_cupom_invalido = calcular_pedido([_item("B001", 8.0, 1)], "INVALIDO")
    sem_cupom = calcular_pedido([_item("B001", 8.0, 1)], None)

    assert com_cupom_invalido == sem_cupom


def test_t17_none_string_vazia_e_espacos_equivalem_sem_cupom() -> None:
    itens = [_item("B001", 8.0, 2)]
    com_none = calcular_pedido(itens, None)
    com_string_vazia = calcular_pedido(itens, "")
    com_espacos = calcular_pedido(itens, "   ")

    assert com_none == com_string_vazia == com_espacos


def test_t18_fronteira_exatamente_80_aplica_frete_gratis() -> None:
    resultado = calcular_pedido([_item("B001", 8.0, 10)], None)

    assert resultado["subtotal_bruto"] == 80.0
    assert resultado["subtotal_apos_descontos"] == 80.0
    assert resultado["frete"] == 0.0
    assert resultado["imposto"] == 9.6
    assert resultado["total"] == 89.6


def test_t19_um_centavo_abaixo_do_frete_gratis_cobra_frete() -> None:
    resultado = calcular_pedido([_item("X", 79.99, 1)], None)

    assert resultado["subtotal_apos_descontos"] == 79.99
    assert resultado["frete"] == 10.0
    assert resultado["imposto"] == 10.8
    assert resultado["total"] == 100.79


def test_t20_limiar_de_volume_com_subtotal_pequeno() -> None:
    resultado = calcular_pedido([_item("X", 5.0, 12)], None)

    assert resultado["subtotal_bruto"] == 60.0
    assert resultado["desconto_volume"] == 3.0
    assert resultado["subtotal_apos_descontos"] == 57.0
    assert resultado["frete"] == 10.0
    assert resultado["imposto"] == 8.04
    assert resultado["total"] == 75.04
