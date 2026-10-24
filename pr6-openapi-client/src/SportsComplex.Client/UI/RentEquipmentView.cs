using SportsComplex.Client.Models;

namespace SportsComplex.Client.UI;

/// <summary>Компонент UI: результат бронирования инвентаря.</summary>
public static class RentEquipmentView
{
    public static void Render(EquipmentRentResponse rent)
    {
        Console.WriteLine($"Бронь {rent.RentId}: {rent.Status}");
        foreach (var item in rent.Items)
            Console.WriteLine($"  • {item.EquipmentCode} × {item.Quantity}");
        if (rent.PickupPoint is not null)
            Console.WriteLine($"  Получить: {rent.PickupPoint}");
        if (rent.ReturnDeadline is not null)
            Console.WriteLine($"  Вернуть до: {rent.ReturnDeadline:dd.MM.yyyy HH:mm}");
    }
}
