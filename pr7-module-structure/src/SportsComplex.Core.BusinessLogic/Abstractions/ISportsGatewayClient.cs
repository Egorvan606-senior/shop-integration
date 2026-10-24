using SportsComplex.Shared.Contracts.Dto;

namespace SportsComplex.Core.BusinessLogic.Abstractions;

/// <summary>
/// Порт к интеграционному шлюзу. Объявлен в ядре, реализован в Data.ApiClient
/// (инверсия зависимостей: ядро не знает про HTTP).
/// </summary>
public interface ISportsGatewayClient
{
    Task<IReadOnlyList<SectionSessionDto>> GetScheduleAsync(DateOnly from, DateOnly to, CancellationToken ct = default);
    Task<EquipmentRentResponseDto> RentAsync(EquipmentRentRequestDto request, CancellationToken ct = default);
}
