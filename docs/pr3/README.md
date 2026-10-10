# ПР №3. Правила сопоставления данных (Data Mapping)

Отчёт: `docs/пр3_Иванов.pdf` — матрицы сопоставления для всех четырёх кейсов методички.

| Кейс | Направление | Реализация |
|---|---|---|
| 1 | Интернет-магазин → Складская ERP (штуки → упаковки) | `src/services/mapping/order_to_erp.py` |
| 2 | CRM → Биллинг (ФИО в одну строку, телефон в E.164) | `src/services/mapping/crm_to_billing.py` |
| 3 | API логистического оператора → ERP (текстовые статусы → коды) | `src/services/mapping/logistics_to_erp.py` |
| 4 | Бухгалтерия → Банковский шлюз (валюта → рубли по курсу ЦБ) | `src/services/mapping/accounting_to_bank.py` |

Общие правила (копейки, округление ROUND_HALF_UP, даты, CASE WHEN) — `src/services/mapping/common.py`.

## Проверка

```bash
pip install -r requirements.txt
python -m pytest -v tests/unit/test_mapping.py   # 36 passed
python scripts/run_mapping_demo.py               # вывод источник -> приёмник
```

Курсы валют в тестах и демонстрации условные и нужны только для проверки формул.
