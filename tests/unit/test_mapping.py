"""Модульные тесты правил сопоставления данных (ПР №3).

Запуск из корня репозитория:  python -m pytest -v tests/unit/test_mapping.py
Для каждого кейса проверяется корректная запись и ошибочные записи
(валидация должна останавливать неверные данные).
"""
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from src.services.mapping.common import MappingError
from src.services.mapping.order_to_erp import map_order
from src.services.mapping.crm_to_billing import map_client, normalize_phone
from src.services.mapping.logistics_to_erp import map_tracking_event
from src.services.mapping.accounting_to_bank import map_payment

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "pr3"


def load(name):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


# ---------------- Кейс 1: Интернет-магазин -> ERP ----------------
def test_case1_order_mapping():
    doc = map_order(load("case1_shop_order.json"))
    assert doc["DocNumber"] == "ORD-2026-000123"               # trim + верхний регистр
    assert doc["DocDateUtc"] == "2026-10-10 11:30:00"          # +03:00 -> UTC
    assert doc["CustomerEmail"] == "ivan.petrov@example.ru"
    assert doc["PaymentStatusCode"] == 2                       # 'PAID' -> 2
    assert doc["DeliveryCode"] == "CUR"
    tea, mug = doc["Lines"]
    assert (tea["ItemCode"], tea["PackQty"], tea["LooseQty"]) == ("000145", 2, 6)   # 30 шт = 2 уп. по 12 + 6 шт
    assert (mug["PackQty"], mug["LooseQty"]) == (1, 0)                              # 6 шт = 1 уп. по 6
    assert tea["PriceKop"] == 24990 and mug["PriceKop"] == 39950                    # '399,5' -> 39950
    assert doc["DocTotalKop"] == 24990 * 30 + 39950 * 6


@pytest.mark.parametrize("patch, field", [
    ({"items": [{"sku": "UNKNOWN", "quantity": 1, "price": 10}]}, "items[0].sku"),
    ({"items": [{"sku": "SPOON-ST", "quantity": 0, "price": 10}]}, "items[0].quantity"),
    ({"items": [{"sku": "SPOON-ST", "quantity": 1, "price": -5}]}, "items[0].price"),
    ({"payment_status": "chargeback"}, "payment_status"),
    ({"created_at": "10.10.2026 14:30"}, "created_at"),
    ({"items": []}, "items"),
])
def test_case1_invalid(patch, field):
    order = load("case1_shop_order.json"); order.update(patch)
    with pytest.raises(MappingError) as e:
        map_order(order)
    assert e.value.field == field


# ---------------- Кейс 2: CRM -> Биллинг ----------------
def test_case2_client_mapping():
    c = map_client(load("case2_crm_client.json"))
    assert c["FullName"] == "Петров Иван Сергеевич"
    assert c["PhoneE164"] == "+79111234567"
    assert c["BirthDate"] == "1990-03-15"
    assert c["ClientTypeCode"] == 1
    assert c["Email"] == "ivan.p@example.ru"
    assert c["BalanceKop"] == 150050
    assert c["IsActive"] is True


def test_case2_without_middle_name_and_double_surname():
    rec = load("case2_crm_client.json")
    rec.update({"last_name": "римский-корсаков", "middle_name": None})
    assert map_client(rec)["FullName"] == "Римский-Корсаков Иван"


@pytest.mark.parametrize("raw", ["+7 911 123-45-67", "89111234567", "9111234567", "7(911)1234567"])
def test_case2_phone_formats(raw):
    assert normalize_phone(raw) == "+79111234567"


@pytest.mark.parametrize("patch, field", [
    ({"phone": "123-45"}, "phone"),
    ({"inn": "7802123"}, "inn"),
    ({"client_type": "Юрлицо", "inn": "780212345678"}, "inn"),   # у юрлица ИНН 10 цифр
    ({"birth_date": "1990-03-15"}, "birth_date"),
    ({"is_active": "может быть"}, "is_active"),
])
def test_case2_invalid(patch, field):
    rec = load("case2_crm_client.json"); rec.update(patch)
    with pytest.raises(MappingError) as e:
        map_client(rec)
    assert e.value.field == field


# ---------------- Кейс 3: Логистика -> ERP ----------------
def test_case3_event_mapping():
    ev = map_tracking_event(load("case3_carrier_event.json"))
    assert ev["TrackNo"] == "RP123456789RU"
    assert ev["OrderId"] == "2026-000123"
    assert ev["StatusCode"] == 30
    assert ev["NeedsReview"] is False
    assert ev["EventTimeMsk"] == "2026-10-10 12:15:00"         # 09:15 UTC = 12:15 МСК
    assert ev["WeightKg"] == Decimal("1.250")
    assert ev["DeliveryCostKop"] == 35000


@pytest.mark.parametrize("text, code", [("DELIVERED", 40), ("вручен", 40), ("In Transit", 20),
                                        ("Прибыл в сортировочный центр", 20), ("Lost", 90)])
def test_case3_status_synonyms(text, code):
    rec = load("case3_carrier_event.json"); rec["status"] = text
    assert map_tracking_event(rec)["StatusCode"] == code


def test_case3_unknown_status_goes_to_review():
    rec = load("case3_carrier_event.json"); rec["status"] = "Задержан на таможне"
    ev = map_tracking_event(rec)
    assert ev["StatusCode"] == 0 and ev["NeedsReview"] is True


@pytest.mark.parametrize("patch, field", [
    ({"order_ref": "2026-000123"}, "order_ref"),
    ({"weight_g": -1}, "weight_g"),
    ({"event_time": "2026-10-10T09:15:00"}, "event_time"),    # нет часового пояса
])
def test_case3_invalid(patch, field):
    rec = load("case3_carrier_event.json"); rec.update(patch)
    with pytest.raises(MappingError) as e:
        map_tracking_event(rec)
    assert e.value.field == field


# ---------------- Кейс 4: Бухгалтерия -> Банк ----------------
# Условные курсы для теста (не реальные курсы ЦБ): (номинал, значение)
RATES = {
    (date(2026, 10, 10), "USD"): (1, "81.5432"),
    (date(2026, 10, 10), "JPY"): (100, "54.3210"),
}


def test_case4_usd_payment():
    p = map_payment(load("case4_payment.json"), RATES)
    assert p["CurrencyNumCode"] == "840"
    assert p["PaymentDate"] == "2026-10-10"
    assert p["AmountRub"] == "101973.85"                       # 1250.55 * 81.5432 = 101973.84876
    assert p["PayerAccount"] == "40702810300000012345"
    assert "  " not in p["Purpose"]


def test_case4_nominal_100_jpy():
    doc = load("case4_payment.json"); doc.update({"currency": "JPY", "amount": "10000"})
    assert map_payment(doc, RATES)["AmountRub"] == "5432.10"   # курс за 100 иен -> за 1 иену


def test_case4_round_half_up():
    doc = load("case4_payment.json"); doc.update({"currency": "RUB", "amount": "10.005"})
    assert map_payment(doc, RATES)["AmountRub"] == "10.01"     # банковское округление дало бы 10.00


@pytest.mark.parametrize("patch, field", [
    ({"currency": "XYZ"}, "currency"),
    ({"amount": "0"}, "amount"),
    ({"payment_date": "11.10.2026"}, "rate"),                  # нет курса на эту дату
    ({"payer_account": "4070281030"}, "payer_account"),
    ({"purpose": "x" * 211}, "purpose"),
])
def test_case4_invalid(patch, field):
    doc = load("case4_payment.json"); doc.update(patch)
    with pytest.raises(MappingError) as e:
        map_payment(doc, RATES)
    assert e.value.field == field
