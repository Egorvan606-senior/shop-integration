"""Проверка схем ПР №4 на корректных и ошибочных примерах.

Запуск (из папки pr4-skud):
    pip install jsonschema rfc3339-validator lxml
    python validate_schemas.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from lxml import etree

HERE = Path(__file__).resolve().parent
SCHEMAS, SAMPLES = HERE / "schemas", HERE / "samples"


def check_json_schema():
    schema = json.loads((SCHEMAS / "badge_event_schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)            # сама схема корректна
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    print("=== JSON Schema: badge_event_schema.json ===")
    ok = True
    for name, expect_valid in [("badge_event_valid.json", True), ("badge_event_invalid.json", False)]:
        data = json.loads((SAMPLES / name).read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        print(f"\n{name}: {'VALID' if not errors else 'INVALID'} (ожидалось {'VALID' if expect_valid else 'INVALID'})")
        for e in errors:
            where = "/".join(str(p) for p in e.path) or "(корень)"
            print(f"  - {where}: {e.message}")
        ok &= (not errors) == expect_valid
    return ok


def check_xsd():
    schema = etree.XMLSchema(etree.parse(str(SCHEMAS / "visitor_pass.xsd")))
    print("\n=== XSD: visitor_pass.xsd ===")
    ok = True
    for name, expect_valid in [("visitor_pass.xml", True), ("visitor_pass_invalid.xml", False)]:
        valid = schema.validate(etree.parse(str(SAMPLES / name)))
        print(f"\n{name}: {'VALID' if valid else 'INVALID'} (ожидалось {'VALID' if expect_valid else 'INVALID'})")
        for err in schema.error_log:
            print(f"  - строка {err.line}: {err.message}")
        ok &= valid == expect_valid
    return ok


if __name__ == "__main__":
    result = check_json_schema() & check_xsd()
    print("\nИТОГ:", "все проверки дали ожидаемый результат" if result else "ЕСТЬ РАСХОЖДЕНИЯ")
    sys.exit(0 if result else 1)
