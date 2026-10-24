# ПР №6. Клиентская архитектура и OpenAPI-спецификация интеграционного шлюза

Вариант 10 — АИС «Спортивный комплекс и секции», шлюз записи в секции, тренажёрный зал и аренду инвентаря.

- `openapi/openapi.yaml` — контракт OpenAPI 3.0.3 (Contract-First): `GET /sections/schedule`, `POST /equipment/rent`, модели в `components/schemas`.
- `src/SportsComplex.Client` — клиент .NET 8 с разделением ответственности: `UI/`, `Services/` (класс-клиент `SportsComplexApiClient`), `Models/`.
- `tests/SportsComplex.Client.Tests` — xUnit-тесты (десериализация ответа и др.), 5/5 пройдено.

Запуск тестов: `dotnet test SportsComplexGateway.sln`

Отчёт: `Отчёт_ПР6_Иванов_И14-23-9.pdf`. Студент: Иванов Е.М., группа И14-23-9.
