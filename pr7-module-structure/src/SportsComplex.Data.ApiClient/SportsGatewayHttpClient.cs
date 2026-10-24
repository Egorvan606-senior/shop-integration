using System.Net.Http.Json;
using SportsComplex.Core.BusinessLogic.Abstractions;
using SportsComplex.Shared.Contracts;
using SportsComplex.Shared.Contracts.Dto;

namespace SportsComplex.Data.ApiClient;

/// <summary>HTTP-реализация порта ISportsGatewayClient (адаптер к шлюзу).</summary>
public sealed class SportsGatewayHttpClient : ISportsGatewayClient
{
    private sealed record ScheduleEnvelope(IReadOnlyList<SectionSessionDto> Sessions);

    private readonly HttpClient _http;

    public SportsGatewayHttpClient(HttpClient http) => _http = http;

    public async Task<IReadOnlyList<SectionSessionDto>> GetScheduleAsync(DateOnly from, DateOnly to, CancellationToken ct = default)
    {
        var url = $"{ApiRoutes.SectionsSchedule}?dateFrom={from:yyyy-MM-dd}&dateTo={to:yyyy-MM-dd}";
        var envelope = await _http.GetFromJsonAsync<ScheduleEnvelope>(url, ct);
        return envelope?.Sessions ?? Array.Empty<SectionSessionDto>();
    }

    public async Task<EquipmentRentResponseDto> RentAsync(EquipmentRentRequestDto request, CancellationToken ct = default)
    {
        using var response = await _http.PostAsJsonAsync(ApiRoutes.EquipmentRent, request, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<EquipmentRentResponseDto>(ct))!;
    }
}
