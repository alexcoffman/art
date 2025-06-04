import json
from unittest.mock import Mock

import pytest
import requests

from art import app, get_wb_goods


def test_get_wb_goods_success(monkeypatch):
    def mock_get(url, headers=None, params=None):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "data": {
                "listGoods": [{"nmID": 123, "sizes": []}]
            }
        }
        return mock_resp

    monkeypatch.setattr(requests, "get", mock_get)
    goods = get_wb_goods("key")
    assert goods == [{"nmID": 123, "sizes": []}]


def test_get_wb_goods_error(monkeypatch):
    def mock_get(url, headers=None, params=None):
        raise requests.exceptions.RequestException("fail")

    monkeypatch.setattr(requests, "get", mock_get)
    goods = get_wb_goods("key")
    assert "Ошибка запроса" in goods


def test_get_wb_goods_empty(monkeypatch):
    def mock_get(url, headers=None, params=None):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {}
        return mock_resp

    monkeypatch.setattr(requests, "get", mock_get)
    goods = get_wb_goods("key")
    assert goods == "Данные не найдены"


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_get_goods_success(client, monkeypatch):
    def mock_get_goods(api_key, limit=10, offset=0, filter_nm_id=None):
        return [{"nmID": 111, "sizes": [{"price": 100, "discountedPrice": 90}]}]

    monkeypatch.setattr("art.get_wb_goods", mock_get_goods)
    response = client.post("/get_goods", data={"api_key": "k", "article": "111"})
    assert response.status_code == 200
    assert response.get_json() == {"price": 100, "discounted_price": 90}


def test_get_goods_not_found(client, monkeypatch):
    monkeypatch.setattr("art.get_wb_goods", lambda *a, **k: [])
    response = client.post("/get_goods", data={"api_key": "k", "article": "111"})
    assert response.status_code == 200
    assert response.get_json() == {"error": "Товар не найден"}


def test_get_goods_api_failure(client, monkeypatch):
    monkeypatch.setattr("art.get_wb_goods", lambda *a, **k: "Ошибка запроса: fail")
    response = client.post("/get_goods", data={"api_key": "k", "article": "111"})
    assert response.status_code == 200
    assert response.get_json() == {"error": "Товар не найден"}
