using SportsComplex.Core.BusinessLogic.Abstractions;
using SportsComplex.Shared.Contracts.Dto;

namespace SportsComplex.Core.BusinessLogic.Services;

public sealed class ScheduleService
{
    private readonly ISportsGatewayClient _gateway;

    public ScheduleService(ISportsGatewayClient gateway) => _gateway = gateway;

    /// <summary>Занятия недели со свободными местами, отсортированные по времени.</summary>
    public async Task<IReadOnlyList<SectionSessionDto>> GetAvailableThisWeekAsync(DateOnly today, CancellationToken ct = default)
    {
        var sessions = await _gateway.GetScheduleAsync(today, today.AddDays(6), ct);
        return sessions.Where(s => s.FreeSlots > 0).OrderBy(s => s.StartsAt).ToList();
    }
}
