from unittest.mock import Mock, mock_open, patch

import pytest

from src.utils import convert_to_rub, load_transactions


def test_load_transactions_valid_file() -> None:
    json_data = '[{"id": 1, "amount": 100}]'
    with patch("builtins.open", mock_open(read_data=json_data)):
        result = load_transactions("dummy_path.json")
    assert result == [{"id": 1, "amount": 100}]


def test_load_transactions_empty_file() -> None:
    with patch("builtins.open", mock_open(read_data="")):
        result = load_transactions("empty.json")
    assert result == []

@patch("src.utils.requests.get")
def test_convert_to_rub_usd(mock_get: Mock) -> None:
    mock_response = {
        "success": True,
        "result": 905.0  # 10 USD * 90.5 RUB/USD
    }
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        transaction = {"amount": 10, "currency": "USD"}
        result = convert_to_rub(transaction)

        assert result == 905.0
        mock_get.assert_called_once()

def test_convert_to_rub_rub() -> None:
    transaction = {"amount": 1000, "currency": "RUB"}
    assert convert_to_rub(transaction) == 1000.0