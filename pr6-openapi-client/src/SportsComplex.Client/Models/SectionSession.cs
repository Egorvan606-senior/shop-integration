namespace SportsComplex.Client.Models;

/// <summary>Одно занятие секции (components/schemas/SectionSession).</summary>
public sealed record SectionSession
{
    public required string SessionId { get; init; }
    public required SectionType SectionType { get; init; }
    public required string Title { get; init; }
    public string? CoachName { get; init; }
    public required string Hall { get; init; }
    public required DateTimeOffset StartsAt { get; init; }
    public required DateTimeOffset EndsAt { get; init; }
    public required int Capacity { get; init; }
    public required int FreeSlots { get; init; }
    public bool EquipmentAvailable { get; init; } = true;

    public bool HasFreeSlots => FreeSlots > 0;
}
