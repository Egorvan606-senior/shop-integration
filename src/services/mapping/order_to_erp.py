"""Кейс 1. Интернет-магазин -> Складская ERP.

Заказ из вебхука интернет-магазина (JSON) переводится в документ ERP.
Главное правило кейса: магазин продаёт ШТУКИ, а склад отгружает УПАКОВКИ,
поэтому количество пересчитывается по справочнику кратности упаковки.
"""
from .common import (MappingError, require, rub_to_kopecks, parse_iso_datetime,
                     to_db_datetime_utc, case_when)

# Справочник номенклатуры: артикул магазина -> (код товара в ERP, штук в упаковке)
NOMENCLATURE = {
    "TEA-GREEN-100": ("000145", 12),
    "MUG-CER-350": ("000231", 6),
    "SPOON-ST": ("000307", 1),
}

PAYMENT_STATUS = {"pending": 1, "paid": 2, "refunded": 3}       # CASE WHEN
DELIVERY_METHOD = {"courier": "CUR", "pickup": "PCK", "post": "PST"}


def map_line(item, index):
    sku = require(item, "sku")
    if sku not in NOMENCLATURE:
        raise MappingError(f"items[{index}].sku", f"артикул {sku!r} не найден в справочнике номенклатуры ERP")
    item_code, pack_size = NOMENCLATURE[sku]

    qty = require(item, "quantity")
    if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
        raise MappingError(f"items[{index}].quantity", "количество должно быть целым числом больше нуля")

    price_kop = rub_to_kopecks(require(item, "price"), f"items[{index}].price")
    return {
        "ItemCode": item_code,                    # подстановка по справочнику
        "PackQty": qty // pack_size,              # целые упаковки
        "LooseQty": qty % pack_size,              # остаток штуками (вскрытая упаковка)
        "PriceKop": price_kop,                    # Float руб -> Long коп.
        "LineSumKop": price_kop * qty,            # агрегация по строке
    }


def map_order(order):
    """Возвращает документ ERP; при ошибке выбрасывает MappingError."""
    items = require(order, "items")
    if not isinstance(items, list) or not items:
        raise MappingError("items", "в заказе нет позиций")
    lines = [map_line(it, i) for i, it in enumerate(items)]
    customer = require(order, "customer")
    delivery = require(order, "delivery")
    return {
        "DocNumber": str(require(order, "order_id")).strip().upper(),            # 1-к-1
        "DocDateUtc": to_db_datetime_utc(parse_iso_datetime(require(order, "created_at"), "created_at")),
        "CustomerEmail": str(require(customer, "email")).strip().lower(),
        "PaymentStatusCode": case_when(require(order, "payment_status"), PAYMENT_STATUS, "payment_status"),
        "DeliveryCode": case_when(require(delivery, "method"), DELIVERY_METHOD, "delivery.method"),
        "Lines": lines,
        "DocTotalKop": sum(l["LineSumKop"] for l in lines),                   # агрегация по документу
    }
