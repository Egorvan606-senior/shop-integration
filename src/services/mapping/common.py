"""Общие функции для правил сопоставления данных (ПР №3).

Здесь собраны преобразования, которые повторяются в нескольких кейсах:
перевод денег в копейки, разбор дат, проверка обязательных полей.
Деньги считаются только через Decimal: float даёт ошибки округления
(0.1 + 0.2 != 0.3), а в денежных расчётах это недопустимо.
"""
from datetime import datetime, date, timezone
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


class MappingError(ValueError):
    """Ошибка трансформации: данные не прошли валидацию (Validation Guard)."""

    def __init__(self, field, message):
        super().__init__(f"{field}: {message}")
        self.field = field


def require(data, field):
    """Достаёт обязательное поле; пустое или отсутствующее — ошибка."""
    value = data.get(field)
    if value is None or (isinstance(value, str) and not value.strip()):
        raise MappingError(field, "обязательное поле отсутствует или пустое")
    return value


def to_decimal(value, field):
    """Строка или число -> Decimal. Принимает и запятую, и точку как разделитель."""
    try:
        return Decimal(str(value).replace(" ", "").replace(",", "."))
    except (InvalidOperation, ValueError):
        raise MappingError(field, f"не число: {value!r}")


def rub_to_kopecks(value, field):
    """Рубли (Float/строка) -> целые копейки (Long), арифметическое округление."""
    rub = to_decimal(value, field)
    if rub < 0:
        raise MappingError(field, "сумма не может быть отрицательной")
    return int((rub * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def round_money(value):
    """Округление до 2 знаков «как в школе» (0.005 -> 0.01), а не банковское."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_iso_datetime(value, field):
    """ISO 8601 ('2026-10-10T14:30:00+03:00' или '...Z') -> datetime с часовым поясом."""
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        raise MappingError(field, f"дата не в формате ISO 8601: {value!r}")
    if dt.tzinfo is None:
        raise MappingError(field, "в дате не указан часовой пояс")
    return dt


def to_db_datetime_utc(dt):
    """datetime -> строка формата СУБД 'YYYY-MM-DD HH:MM:SS' в UTC."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def parse_ru_date(value, field):
    """Дата в русском формате 'ДД.ММ.ГГГГ' -> date."""
    try:
        return datetime.strptime(str(value).strip(), "%d.%m.%Y").date()
    except ValueError:
        raise MappingError(field, f"дата не в формате ДД.ММ.ГГГГ: {value!r}")


def case_when(value, mapping, field, default=None):
    """Условный маппинг (CASE WHEN ... THEN ...). Регистр и пробелы не важны.

    Если значения нет в справочнике и default не задан — это ошибка:
    неизвестный статус лучше остановить, чем молча записать неверный код.
    """
    key = str(value).strip().lower()
    for src, dst in mapping.items():
        if key == src.lower():
            return dst
    if default is not None:
        return default
    raise MappingError(field, f"значение {value!r} отсутствует в справочнике")


__all__ = [
    "MappingError", "require", "to_decimal", "rub_to_kopecks", "round_money",
    "parse_iso_datetime", "to_db_datetime_utc", "parse_ru_date", "case_when", "date",
]
