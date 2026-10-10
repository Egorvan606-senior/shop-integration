"""Демонстрация правил маппинга ПР №3: показывает запись источника и результат в приёмнике.

Запуск из корня репозитория:  python scripts/run_mapping_demo.py
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.services.mapping.common import MappingError  # noqa: E402
from src.services.mapping.order_to_erp import map_order  # noqa: E402
from src.services.mapping.crm_to_billing import map_client  # noqa: E402
from src.services.mapping.logistics_to_erp import map_tracking_event  # noqa: E402
from src.services.mapping.accounting_to_bank import map_payment  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "pr3"
RATES = {(date(2026, 10, 10), "USD"): (1, "81.5432")}   # условный курс для демонстрации

CASES = [
    ("Кейс 1. Интернет-магазин -> Складская ERP", "case1_shop_order.json", map_order),
    ("Кейс 2. CRM -> Биллинговый контур", "case2_crm_client.json", map_client),
    ("Кейс 3. API логистического оператора -> ERP", "case3_carrier_event.json", map_tracking_event),
    ("Кейс 4. Бухгалтерия -> Банковский шлюз", "case4_payment.json", lambda d: map_payment(d, RATES)),
]


def show(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def main():
    for title, fixture, func in CASES:
        src = json.loads((FIX / fixture).read_text(encoding="utf-8"))
        print()
        print(title)
        print("Источник (Source):")
        print(show(src))
        print("Приёмник (Target):")
        print(show(func(src)))
    print()
    print("Проверка валидации: телефон '123-45' в кейсе 2")
    bad = json.loads((FIX / "case2_crm_client.json").read_text(encoding="utf-8"))
    bad["phone"] = "123-45"
    try:
        map_client(bad)
    except MappingError as e:
        print("[Отклонено Validation Guard]", e)


if __name__ == "__main__":
    main()
