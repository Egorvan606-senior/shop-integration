using SportsComplex.Client.Models;

namespace SportsComplex.Client.UI;

/// <summary>Компонент UI: вывод расписания секций в виде таблицы в консоли.</summary>
public static class ScheduleView
{
    public static void Render(SectionSchedule schedule)
    {
        Console.WriteLine($"Расписание секций {schedule.DateFrom:dd.MM} – {schedule.DateTo:dd.MM}, занятий: {schedule.TotalSessions}");
        Console.WriteLine(new string('-', 92));
        Console.WriteLine($"{"ID занятия",-18}{"Секция",-30}{"Зал",-18}{"Начало",-14}{"Мест",-6}{"Инв.",-4}");
        Console.WriteLine(new string('-', 92));
        foreach (var s in schedule.Sessions)
        {
            Console.WriteLine(
                $"{s.SessionId,-18}{Trim(s.Title, 29),-30}{Trim(s.Hall, 17),-18}" +
                $"{s.StartsAt:dd.MM HH:mm}{"",-3}{s.FreeSlots + "/" + s.Capacity,-6}{(s.EquipmentAvailable ? "да" : "нет"),-4}");
        }
    }

    private static string Trim(string text, int max) =>
        text.Length <= max ? text : text[..(max - 1)] + "…";
}
