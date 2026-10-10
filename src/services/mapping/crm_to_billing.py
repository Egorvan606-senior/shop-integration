"""Кейс 2. CRM -> Биллинговый контур.

В CRM фамилия, имя и отчество хранятся раздельно, а биллинг ждёт одну строку
FullName (семантический разрыв). Телефон в CRM вводится как попало,
а биллинг принимает только международный формат E.164 (синтаксический разрыв).
"""
import re

from .common import MappingError, require, rub_to_kopecks, parse_ru_date, case_when

CLIENT_TYPE = {"физлицо": 1, "ип": 2, "юрлицо": 3}
YES_NO = {"да": True, "нет": False}
PHONE_E164 = re.compile(r"^\+7\d{10}$")


def _name_part(value):
    """'  иВАНОВ ' -> 'Иванов'; двойные фамилии через дефис сохраняются: 'римский-корсаков' -> 'Римский-Корсаков'."""
    value = " ".join(str(value).split())
    return "-".join(p[:1].upper() + p[1:].lower() for p in value.split("-"))


def full_name(record):
    last = _name_part(require(record, "last_name"))
    first = _name_part(require(record, "first_name"))
    middle = record.get("middle_name")                  # отчества может не быть
    parts = [last, first] + ([_name_part(middle)] if middle and str(middle).strip() else [])
    return " ".join(parts)


def normalize_phone(raw):
    """'8 (911) 123-45-67', '+7 911 1234567', '9111234567' -> '+79111234567'."""
    digits = re.sub(r"\D", "", str(raw))
    if len(digits) == 11 and digits[0] in "78":
        digits = "7" + digits[1:]
    elif len(digits) == 10 and digits[0] == "9":
        digits = "7" + digits
    phone = "+" + digits
    if not PHONE_E164.match(phone):
        raise MappingError("phone", f"телефон {raw!r} не приводится к формату +7XXXXXXXXXX")
    return phone


def validate_inn(inn, client_type_code):
    """ИНН: 12 цифр у физлица и ИП, 10 цифр у юрлица."""
    inn = str(inn).strip()
    need = 10 if client_type_code == 3 else 12
    if not inn.isdigit() or len(inn) != need:
        raise MappingError("inn", f"ИНН должен состоять из {need} цифр")
    return inn


def map_client(record):
    type_code = case_when(require(record, "client_type"), CLIENT_TYPE, "client_type")
    return {
        "FullName": full_name(record),                                              # объединение 3 полей
        "PhoneE164": normalize_phone(require(record, "phone")),
        "BirthDate": parse_ru_date(require(record, "birth_date"), "birth_date").isoformat() if type_code != 3 else None,
        "ClientTypeCode": type_code,
        "Inn": validate_inn(require(record, "inn"), type_code),
        "Email": str(require(record, "email")).strip().lower(),
        "BalanceKop": rub_to_kopecks(record.get("balance", 0), "balance"),
        "IsActive": case_when(require(record, "is_active"), YES_NO, "is_active"),
    }
