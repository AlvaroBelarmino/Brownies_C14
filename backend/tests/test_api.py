from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import _cors_origins, app


def test_api_retorna_200_com_resultado_do_dominio() -> None:
    client = TestClient(app)
    esperado = {
        "subtotal_bruto": 24.0,
        "desconto_volume": 0.0,
        "subtotal_apos_volume": 24.0,
        "desconto_cupom": 2.4,
        "subtotal_apos_descontos": 21.6,
        "frete": 10.0,
        "imposto": 3.79,
        "total": 35.39,
        "quantidade_total": 2,
    }

    with patch("app.main.calcular_pedido", return_value=esperado) as calcular_pedido_mock:
        response = client.post(
            "/api/pedido/calcular",
            json={
                "itens": [
                    {"sku": "B002", "preco_unitario": 12.0, "quantidade": 2},
                ],
                "cupom": "PROMO10",
            },
        )

    assert response.status_code == 200
    assert response.json() == esperado
    calcular_pedido_mock.assert_called_once_with(
        [{"sku": "B002", "preco_unitario": 12.0, "quantidade": 2}],
        "PROMO10",
    )


def test_api_retorna_400_quando_dominio_lanca_value_error() -> None:
    client = TestClient(app)

    with patch(
        "app.main.calcular_pedido",
        side_effect=ValueError("Erro de regra de negocio"),
    ) as calcular_pedido_mock:
        response = client.post(
            "/api/pedido/calcular",
            json={
                "itens": [
                    {"sku": "B001", "preco_unitario": 8.0, "quantidade": 1},
                ],
                "cupom": "PROMO10",
            },
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "Erro de regra de negocio"}
    calcular_pedido_mock.assert_called_once_with(
        [{"sku": "B001", "preco_unitario": 8.0, "quantidade": 1}],
        "PROMO10",
    )


def test_api_retorna_422_para_payload_invalido_sem_chamar_dominio() -> None:
    client = TestClient(app)

    with patch("app.main.calcular_pedido") as calcular_pedido_mock:
        response = client.post(
            "/api/pedido/calcular",
            json={
                "itens": [
                    {"sku": "B001", "preco_unitario": 8.0, "quantidade": 0},
                ],
            },
        )

    assert response.status_code == 422
    calcular_pedido_mock.assert_not_called()


def test_cors_origins_remove_espacos_e_ignora_entradas_vazias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        " http://localhost:3000 , , http://127.0.0.1:5173 ,, ",
    )

    assert _cors_origins() == [
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
