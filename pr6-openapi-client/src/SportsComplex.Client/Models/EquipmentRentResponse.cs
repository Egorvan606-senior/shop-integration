namespace SportsComplex.Client.Models;

/// <summary>Ответ шлюза о созданной брони (components/schemas/EquipmentRentResponse).</summary>
public sealed record EquipmentRentResponse
{
    public required string RentId { get; init; }
    public required string SessionId { get; init; }
    public required RentStatus Status { get; init; }
    public string? PickupPoint { get; init; }
    public DateTimeOffset? ReturnDeadline { get; init; }
    public required IReadOnlyList<RentItem> Items { get; init; }
}
