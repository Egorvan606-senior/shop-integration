namespace SportsComplex.Client.Models;

/// <summary>Запрос на бронирование инвентаря (components/schemas/EquipmentRentRequest).</summary>
public sealed record EquipmentRentRequest
{
    public required string StudentId { get; init; }
    public required string SessionId { get; init; }
    public required IReadOnlyList<RentItem> Items { get; init; }
}
