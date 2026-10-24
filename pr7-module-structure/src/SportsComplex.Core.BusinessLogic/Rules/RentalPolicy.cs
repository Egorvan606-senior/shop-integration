using SportsComplex.Shared.Contracts.Dto;

namespace SportsComplex.Core.BusinessLogic.Rules;

/// <summary>Бизнес-правила аренды инвентаря спорткомплекса.</summary>
public static class RentalPolicy
{
    public const int MaxQuantityPerItem = 3;
    public const int MaxPositions = 5;
    public static readonly TimeSpan BookingClosesBeforeStart = TimeSpan.FromMinutes(30);

    public static IReadOnlyList<string> Validate(SectionSessionDto session, IReadOnlyList<RentItemDto> items, DateTimeOffset now)
    {
        var errors = new List<string>();
        if (!session.EquipmentAvailable)
            errors.Add("К этому занятию инвентарь не выдаётся.");
        if (session.StartsAt - now < BookingClosesBeforeStart)
            errors.Add("Бронь закрывается за 30 минут до начала занятия.");
        if (items.Count is 0 or > MaxPositions)
            errors.Add($"В брони должно быть от 1 до {MaxPositions} позиций.");
        if (items.Any(i => i.Quantity is < 1 or > MaxQuantityPerItem))
            errors.Add($"Количество одной позиции — от 1 до {MaxQuantityPerItem}.");
        return errors;
    }
}
