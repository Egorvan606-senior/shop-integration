using SportsComplex.Client.Models;
using SportsComplex.Client.Services;

namespace SportsComplex.Client.UI;

/// <summary>
/// Главное меню клиента. Работает только через ISportsComplexApiClient
/// и ничего не знает об HTTP, URL и JSON — это ответственность слоя Services.
/// </summary>
public sealed class MainMenu
{
    private readonly ISportsComplexApiClient _api;

    public MainMenu(ISportsComplexApiClient api) => _api = api;

    public async Task RunAsync()
    {
        while (true)
        {
            Console.WriteLine();
            Console.WriteLine("АИС «Спортивный комплекс и секции»");
            Console.WriteLine("1 — расписание секций на неделю");
            Console.WriteLine("2 — забронировать инвентарь к занятию");
            Console.WriteLine("0 — выход");
            Console.Write("> ");

            switch (Console.ReadLine())
            {
                case "1": await ShowScheduleAsync(); break;
                case "2": await RentAsync(); break;
                case "0": return;
                default: Console.WriteLine("Неизвестная команда"); break;
            }
        }
    }

    private async Task ShowScheduleAsync()
    {
        var today = DateOnly.FromDateTime(DateTime.Today);
        try
        {
            var schedule = await _api.GetScheduleAsync(today, today.AddDays(6), onlyAvailable: true);
            ScheduleView.Render(schedule);
        }
        catch (Exception ex) when (ex is SportsComplexApiException or HttpRequestException)
        {
            Console.WriteLine($"Не удалось получить расписание: {ex.Message}");
        }
    }

    private async Task RentAsync()
    {
        Console.Write("ID занятия: ");
        var sessionId = Console.ReadLine()?.Trim() ?? "";
        Console.Write("Код инвентаря (например BALL-VOLLEY): ");
        var code = Console.ReadLine()?.Trim().ToUpperInvariant() ?? "";

        var request = new EquipmentRentRequest
        {
            StudentId = "I14-23-9-010",
            SessionId = sessionId,
            Items = new[] { new RentItem(code, 1) }
        };

        try
        {
            RentEquipmentView.Render(await _api.RentEquipmentAsync(request));
        }
        catch (SportsComplexApiException ex)
        {
            Console.WriteLine($"Ошибка {(int)ex.StatusCode} {ex.Error?.Code}: {ex.Message}");
        }
        catch (HttpRequestException ex)
        {
            Console.WriteLine($"Шлюз недоступен: {ex.Message}");
        }
    }
}
