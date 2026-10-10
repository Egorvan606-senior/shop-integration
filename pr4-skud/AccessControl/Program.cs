// ПР №4. Контракты данных и валидация для подсистемы контроля доступа (СКУД).
// Задание 3: десериализация JSON-события прохода и проверка бизнес-правил.
// Дополнительно: проверка XML-заявки на гостевой пропуск по XSD (задание 2).
using System;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;
using System.Xml;
using System.Xml.Schema;

namespace AccessControl;

// Объектная модель события. Имена в JSON — snake_case, как в badge_event_schema.json,
// поэтому каждому свойству явно задано имя JSON через JsonPropertyName.
public record BadgeEventDto(
    [property: JsonPropertyName("badge_id")] string? BadgeId,
    [property: JsonPropertyName("checkpoint_id")] int CheckpointId,
    [property: JsonPropertyName("event_type")] string? EventType,
    [property: JsonPropertyName("timestamp")] DateTime Timestamp
);

public static class AccessControlHandler
{
    private static readonly Regex BadgePattern = new("^[0-9A-Fa-f]{8}$");

    private static readonly JsonSerializerOptions Options = new()
    {
        PropertyNameCaseInsensitive = true,                          // требование задания
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow // лишние поля -> ошибка (как additionalProperties: false)
    };

    public static void ProcessBadgeScan(string rawJson)
    {
        try
        {
            BadgeEventDto? badgeEvent = JsonSerializer.Deserialize<BadgeEventDto>(rawJson, Options);

            if (badgeEvent == null)
            {
                Print(ConsoleColor.Yellow, "[Ошибка]: Пустой пакет данных от считывателя.");
                return;
            }

            if (badgeEvent.CheckpointId <= 0)
            {
                Print(ConsoleColor.Red, $"[Тревога]: Некорректный ID точки прохода #{badgeEvent.CheckpointId}!");
                return;
            }

            if (badgeEvent.BadgeId == null || !BadgePattern.IsMatch(badgeEvent.BadgeId))
            {
                Print(ConsoleColor.Red, $"[Тревога]: Недопустимый идентификатор карты '{badgeEvent.BadgeId}' (нужно 8 hex-символов).");
                return;
            }

            if (badgeEvent.EventType is not ("ENTRY" or "EXIT"))
            {
                Print(ConsoleColor.Yellow, $"[Ошибка]: Неизвестный тип события '{badgeEvent.EventType}' (допустимо ENTRY или EXIT).");
                return;
            }

            if (badgeEvent.Timestamp == default)
            {
                Print(ConsoleColor.Yellow, "[Ошибка]: В событии нет времени прохода (timestamp).");
                return;
            }

            Print(ConsoleColor.Green,
                $"[Доступ разрешен]: Карта {badgeEvent.BadgeId} зафиксирована на точке {badgeEvent.CheckpointId} " +
                $"({badgeEvent.EventType}) в {badgeEvent.Timestamp:yyyy-MM-dd HH:mm:ss} UTC");
        }
        catch (JsonException ex)
        {
            Print(ConsoleColor.Magenta, $"[Критическая ошибка десериализации]: Поврежден формат сообщения. Детали: {ex.Message}");
        }
    }

    // Проверка XML-заявки на гостевой пропуск по XSD-схеме средствами .NET
    public static void ValidateVisitorPass(string xmlPath, string xsdPath)
    {
        var settings = new XmlReaderSettings { ValidationType = ValidationType.Schema };
        settings.Schemas.Add(null, xsdPath);
        int errors = 0;
        settings.ValidationEventHandler += (_, e) =>
        {
            errors++;
            Print(ConsoleColor.Red, $"    строка {e.Exception.LineNumber}: {e.Message}");
        };
        using (var reader = XmlReader.Create(xmlPath, settings))
        {
            while (reader.Read()) { }
        }
        if (errors == 0)
            Print(ConsoleColor.Green, $"[XSD]: {Path.GetFileName(xmlPath)} — заявка соответствует схеме.");
        else
            Print(ConsoleColor.Yellow, $"[XSD]: {Path.GetFileName(xmlPath)} — найдено ошибок: {errors}.");
    }

    private static void Print(ConsoleColor color, string text)
    {
        Console.ForegroundColor = color;
        Console.WriteLine(text);
        Console.ResetColor();
    }

    public static void Main(string[] args)
    {
        Console.OutputEncoding = Encoding.UTF8;
        string baseDir = AppContext.BaseDirectory;

        // Режим 1: путь к JSON-файлу в аргументах -> обработать только его
        if (args.Length > 0)
        {
            foreach (var path in args)
            {
                Console.WriteLine($"> Файл: {path}");
                ProcessBadgeScan(File.ReadAllText(path));
            }
            return;
        }

        // Режим 2 (по умолчанию): демонстрация на корректных и ошибочных запросах
        var tests = new (string Title, string Json)[]
        {
            ("1. Корректное событие",
             "{\"badge_id\": \"A1B2C3D4\", \"checkpoint_id\": 3, \"event_type\": \"ENTRY\", \"timestamp\": \"2026-09-27T13:00:00Z\"}"),
            ("2. Регистр имён полей другой (PropertyNameCaseInsensitive)",
             "{\"BADGE_ID\": \"0F0F0F0F\", \"Checkpoint_Id\": 12, \"Event_Type\": \"EXIT\", \"TimeStamp\": \"2026-09-27T18:05:00Z\"}"),
            ("3. checkpoint_id = 0",
             "{\"badge_id\": \"A1B2C3D4\", \"checkpoint_id\": 0, \"event_type\": \"ENTRY\", \"timestamp\": \"2026-09-27T13:00:00Z\"}"),
            ("4. checkpoint_id отрицательный",
             "{\"badge_id\": \"A1B2C3D4\", \"checkpoint_id\": -7, \"event_type\": \"EXIT\", \"timestamp\": \"2026-09-27T13:00:00Z\"}"),
            ("5. Битый синтаксис JSON (нет закрывающей скобки)",
             "{\"badge_id\": \"A1B2C3D4\", \"checkpoint_id\": 3, \"event_type\": \"ENTRY\""),
            ("6. Неверный тип: checkpoint_id строкой",
             "{\"badge_id\": \"A1B2C3D4\", \"checkpoint_id\": \"три\", \"event_type\": \"ENTRY\", \"timestamp\": \"2026-09-27T13:00:00Z\"}"),
            ("7. Лишнее поле в сообщении",
             "{\"badge_id\": \"A1B2C3D4\", \"checkpoint_id\": 3, \"event_type\": \"ENTRY\", \"timestamp\": \"2026-09-27T13:00:00Z\", \"door\": \"main\"}"),
            ("8. Неверный формат карты",
             "{\"badge_id\": \"XYZ-0001\", \"checkpoint_id\": 3, \"event_type\": \"ENTRY\", \"timestamp\": \"2026-09-27T13:00:00Z\"}"),
            ("9. Неизвестный тип события",
             "{\"badge_id\": \"A1B2C3D4\", \"checkpoint_id\": 3, \"event_type\": \"IN\", \"timestamp\": \"2026-09-27T13:00:00Z\"}"),
            ("10. Пустой пакет (null)", "null"),
            ("11. Строка из шаблона задания (смешанные стили имён)",
             "{\"badgeId\": \"A1B2C3D4\", \"checkpoint_id\": 3, \"eventType\": \"ENTRY\", \"timestamp\": \"2026-09-27T13:00:00Z\"}"),
        };

        Console.WriteLine("=== СКУД: обработка событий прохода (JSON) ===");
        foreach (var (title, json) in tests)
        {
            Console.WriteLine();
            Console.WriteLine($"--- {title}");
            Console.WriteLine($"    {json}");
            ProcessBadgeScan(json);
        }

        Console.WriteLine();
        Console.WriteLine("=== Бюро пропусков: проверка заявок (XML по XSD) ===");
        string xsd = Path.Combine(baseDir, "schemas", "visitor_pass.xsd");
        ValidateVisitorPass(Path.Combine(baseDir, "samples", "visitor_pass.xml"), xsd);
        ValidateVisitorPass(Path.Combine(baseDir, "samples", "visitor_pass_invalid.xml"), xsd);
    }
}
