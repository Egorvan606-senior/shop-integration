# ПР №2. Уровни интеграции и схема взаимодействия модулей

Отчёт: [`docs/пр2_Иванов.pdf`](../пр2_Иванов.pdf)

## Файлы

| Файл | Что это |
|---|---|
| `modules_diagram.py` | Скрипт построения схемы модулей (Python, matplotlib; обозначения ГОСТ 19.701-90) |
| `modules.png` | Готовая схема (сборка: `python modules_diagram.py`) |

## Модули

| Модуль | Компоненты `src/` | Уровень интеграции |
|---|---|---|
| 1. Источник / Интерфейс | `connectors/sftp_client`, `webhooks/receiver`, `parsers/` | данные (SFTP, парсеры), API (вебхуки) |
| 2. Бизнес-логика | `models/`, `services/order_validator`, `stock_calculator`, `order_status_sync`, `catalog_sync` | бизнес-логика |
| 3. Приёмник / Хранилище | `connectors/db_repository`, `connectors/marketplace_client` | данные (SQL), API (REST) |

## Потоки на схеме

- **А** — остатки и цены: склад (SFTP, CSV/XML) → парсер → расчёт остатков → маркетплейс (HTTPS PUT, JSON)
- **Б** — заказы: интернет-магазин (вебхук HTTPS POST, JSON) → парсер → валидация → БД учётной системы (SQL INSERT)
- **В** — статусы и трек-номера: БД (SQL SELECT) → `order_status_sync` → маркетплейс
- **Г** — каталог: номенклатура → `catalog_sync` → маркетплейс

## Спецификация артефактов и протоколов

| Источник | Приёмник | Уровень | Протокол | Формат | Данные |
|---|---|---|---|---|---|
| Складская система (И1) | sftp_client | Данные | SFTP (SSH, 22) | CSV / XML | Остатки и цены |
| Интернет-магазин (И2) | webhooks/receiver | API | HTTPS (Webhooks) | JSON | Новый заказ |
| webhooks/receiver | Интернет-магазин | API | HTTPS (ответ) | HTTP 200/400/401 | Подтверждение приёма |
| parsers | services | Бизнес-логика | вызов в процессе | объекты моделей | Разобранные данные |
| order_validator | db_repository → БД (П2) | Данные | TCP (СУБД), SQL | записи orders, order_items | Проверенный заказ |
| БД (П2) | db_repository → order_status_sync | Данные | TCP (СУБД), SQL | результат SELECT | Отгрузки, трек-номера |
| stock_calculator | marketplace_client → П1 | API | HTTPS REST PUT | JSON | Остатки |
| order_status_sync | marketplace_client → П1 | API | HTTPS REST POST | JSON | Статусы, трек-номера |
| catalog_sync | marketplace_client → П1 | API | HTTPS REST POST/PUT | JSON | Карточки товаров |
| Маркетплейс (П1) | marketplace_client | API | HTTPS (ответ) | JSON, HTTP 2xx/4xx/5xx | Подтверждение / ошибка |
| config/, .env | все модули | — | локальный диск | YAML / .env | Параметры подключений |
