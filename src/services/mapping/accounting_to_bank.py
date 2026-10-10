"""Кейс 4. Бухгалтерия -> Банковский шлюз.

Валютный платёж пересчитывается в рубли по курсу ЦБ РФ на дату платежа
с округлением до копеек. Курс ЦБ публикуется «за номинал»: например,
за 100 японских иен, поэтому курс за 1 единицу = Value / Nominal.

Курсы передаются в функцию снаружи (таблица rates), а не запрашиваются
внутри: так правило можно проверить тестом без доступа к сайту ЦБ.
"""
import re
from decimal import Decimal

from .common import MappingError, require, to_decimal, round_money, parse_ru_date

# ISO 4217: буквенный код -> цифровой код
CURRENCY_NUMERIC = {"RUB": "643", "USD": "840", "EUR": "978", "CNY": "156", "JPY": "392"}
ACCOUNT_RE = re.compile(r"^\d{20}$")
PURPOSE_MAX = 210


def rate_per_unit(rates, currency, pay_date):
    """rates: {(дата, 'USD'): (Nominal, Value)} -> курс за 1 единицу валюты."""
    if currency == "RUB":
        return Decimal("1")
    key = (pay_date, currency)
    if key not in rates:
        raise MappingError("rate", f"нет курса ЦБ для {currency} на {pay_date.isoformat()}")
    nominal, value = rates[key]
    return Decimal(str(value)) / Decimal(nominal)


def map_payment(doc, rates):
    currency = str(require(doc, "currency")).strip().upper()
    if currency not in CURRENCY_NUMERIC:
        raise MappingError("currency", f"валюта {currency!r} не поддерживается")

    amount = to_decimal(require(doc, "amount"), "amount")
    if amount <= 0:
        raise MappingError("amount", "сумма платежа должна быть больше нуля")

    pay_date = parse_ru_date(require(doc, "payment_date"), "payment_date")
    rate = rate_per_unit(rates, currency, pay_date)

    account = str(require(doc, "payer_account")).replace(" ", "")
    if not ACCOUNT_RE.match(account):
        raise MappingError("payer_account", "номер счёта должен состоять из 20 цифр")

    purpose = " ".join(str(require(doc, "purpose")).split())
    if len(purpose) > PURPOSE_MAX:
        raise MappingError("purpose", f"назначение платежа длиннее {PURPOSE_MAX} символов")

    return {
        "DocNumber": str(require(doc, "doc_number")).strip(),           # 1-к-1
        "PaymentDate": pay_date.isoformat(),                             # ДД.ММ.ГГГГ -> ГГГГ-ММ-ДД
        "CurrencyNumCode": CURRENCY_NUMERIC[currency],                   # USD -> 840
        "AmountCurrency": str(amount),
        "CbrRate": str(rate),
        "AmountRub": str(round_money(amount * rate)),                    # пересчёт + округление
        "PayerAccount": account,
        "Purpose": purpose,
    }
