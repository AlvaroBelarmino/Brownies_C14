from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


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
