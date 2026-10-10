"""Кейс 3. API логистического оператора -> ERP.

Перевозчик сообщает статус доставки текстом (иногда по-разному для одного
и того же смысла), а ERP хранит статус числовым кодом. Неизвестный статус
не отбрасывается, а получает код 0 и уходит на ручной разбор: событие о посылке
терять нельзя.
"""
from datetime import timezone, timedelta
from decimal import Decimal

from .common import MappingError, require, rub_to_kopecks, parse_iso_datetime, case_when

MSK = timezone(timedelta(hours=3))
UNKNOWN_STATUS = 0

# Справочник «текст перевозчика -> код ERP». Несколько синонимов на один код.
STATUS_CODES = {
    "принят в отделении": 10, "accepted": 10,
    "в пути": 20, "in transit": 20, "прибыл в сортировочный центр": 20,
    "передан курьеру": 30, "out for delivery": 30,
    "вручен": 40, "delivered": 40,
    "возврат отправителю": 50, "returned": 50,
    "утерян": 90, "lost": 90,
}


def map_tracking_event(event):
    status_text = require(event, "status")
    code = case_when(status_text, STATUS_CODES, "status", default=UNKNOWN_STATUS)

    order_ref = str(require(event, "order_ref")).strip().upper()
    if not order_ref.startswith("ORD-"):
        raise MappingError("order_ref", "ссылка на заказ должна начинаться с 'ORD-'")

    weight_g = require(event, "weight_g")
    if not isinstance(weight_g, int) or weight_g <= 0:
        raise MappingError("weight_g", "вес должен быть целым числом граммов больше нуля")

    cost_text = str(require(event, "cost")).upper().replace("RUB", "").strip()   # '350,00 RUB'
    event_time = parse_iso_datetime(require(event, "event_time"), "event_time")

    return {
        "TrackNo": str(require(event, "tracking_number")).strip().upper(),          # 1-к-1
        "OrderId": order_ref[len("ORD-"):],                                          # отрезаем префикс
        "StatusCode": code,
        "StatusText": str(status_text).strip(),                                      # исходный текст для аудита
        "NeedsReview": code == UNKNOWN_STATUS,
        "EventTimeMsk": event_time.astimezone(MSK).strftime("%Y-%m-%d %H:%M:%S"),  # UTC -> МСК
        "WeightKg": (Decimal(weight_g) / 1000).quantize(Decimal("0.001")),          # г -> кг
        "DeliveryCostKop": rub_to_kopecks(cost_text, "cost"),
    }
