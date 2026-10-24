namespace SportsComplex.Client.Models;

/// <summary>Сетка занятий за период (components/schemas/SectionSchedule).</summary>
public sealed record SectionSchedule
{
    public required DateOnly DateFrom { get; init; }
    public required DateOnly DateTo { get; init; }
    public required int TotalSessions { get; init; }
    public required IReadOnlyList<SectionSession> Sessions { get; init; }
}
