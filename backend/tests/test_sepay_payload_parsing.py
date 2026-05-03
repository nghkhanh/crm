from decimal import Decimal

from app.services.sepay import SePayService


def test_sepay_payload_parser_supports_production_style_payload():
    reference, amount, note, external_id, raw_payload = SePayService.parse_webhook_payload(
        {
            "id": 92704,
            "gateway": "BIDV",
            "transactionDate": "2024-01-07 14:02:37",
            "code": "ORD123456789",
            "transferAmount": 2277000,
            "description": "Thanh toan ORD123456789",
            "transferType": "in",
        }
    )

    assert reference == "ORD123456789"
    assert amount == Decimal("2277000")
    assert note == "Thanh toan ORD123456789"
    assert external_id == "92704"
    assert raw_payload["code"] == "ORD123456789"
