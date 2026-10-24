# ПР №7. Диаграмма модулей и структура проекта для АИС

Вариант 10 — АИС «Спортивный комплекс и секции».

- `docs/diagrams/components.puml` / `.png` — UML Component Diagram.
- `docs/diagrams/c4-containers.puml` / `.png` — C4 Model, Level 2 (Containers).
- `src/` — модули: `UI.Desktop`, `Core.BusinessLogic`, `Data.ApiClient`, `Security.Auth`, `Shared.Contracts`, `Gateway.Api`.
- `tests/SportsComplex.Core.Tests` — xUnit-тесты правил аренды, 5/5 пройдено.

Сборка: `dotnet build SportsComplex.AIS.sln` (7 проектов, без ошибок).

Отчёт: `Отчёт_ПР7_Иванов_И14-23-9.pdf`. Студент: Иванов Е.М., группа И14-23-9.
