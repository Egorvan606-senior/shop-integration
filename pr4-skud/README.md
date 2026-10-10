# ПР №4. Контракты данных и валидация для СКУД

Отчёт: `docs/пр4_Иванов.pdf`

| Файл | Задание |
|---|---|
| `schemas/badge_event_schema.json` | 1 — JSON Schema события прохода (`additionalProperties: false`) |
| `samples/badge_event_valid.json`, `badge_event_invalid.json`, `badge_event_broken.json` | 1, 3 — тестовые события |
| `samples/visitor_pass.xml`, `schemas/visitor_pass.xsd` | 2 — заявка на гостевой пропуск и её XSD (имя ≥ 2 символов) |
| `samples/visitor_pass_invalid.xml` | 2 — ошибочная заявка для проверки XSD |
| `AccessControl.sln`, `AccessControl/Program.cs` | 3 — консольное приложение C# (.NET 8, без NuGet-пакетов) |
| `validate_schemas.py` | проверка схем на корректных и ошибочных примерах |

## Запуск C#-приложения

**Visual Studio:** открыть `AccessControl.sln` → `Ctrl+F5` (запуск без отладки — окно консоли не закроется).

**Консоль:**

```bash
cd pr4-skud/AccessControl
dotnet run                                        # демонстрация: 11 JSON-сообщений + 2 XML-заявки
dotnet run -- ../samples/badge_event_valid.json   # обработать свой файл
```

Ожидаемый результат: «[Доступ разрешен]» для корректных событий, «[Тревога]» при `checkpoint_id ≤ 0` и неверной карте,
«[Критическая ошибка десериализации]» (перехват `JsonException`) для битого JSON, неверного типа и лишнего поля.

## Проверка схем (Python)

```bash
pip install jsonschema rfc3339-validator lxml
python validate_schemas.py      # ИТОГ: все проверки дали ожидаемый результат
```

## Отличия от шаблона из задания

- убран лишний символ `5` после `if (badgeEvent.CheckpointId <= 0)` — с ним код не компилируется;
- имена JSON заданы через `[JsonPropertyName("badge_id")]` и т. д.: `PropertyNameCaseInsensitive` не учитывает подчёркивания, поэтому `checkpoint_id` из шаблонной строки не попадал в `CheckpointId`;
- `UnmappedMemberHandling = Disallow` — лишние поля отклоняются, как `additionalProperties: false` в схеме;
- добавлены проверки формата карты, типа события и наличия времени.
