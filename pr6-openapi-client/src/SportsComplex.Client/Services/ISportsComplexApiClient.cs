using SportsComplex.Client.Models;

namespace SportsComplex.Client.Services;

/// <summary>
/// Абстракция сетевого слоя. UI зависит только от этого интерфейса,
/// поэтому реальный HTTP-клиент можно заменить заглушкой в тестах.
/// </summary>
public interface ISportsComplexApiClient
{
    /// <summary>GET /sections/schedule</summary>
    Task<SectionSchedule> GetScheduleAsync(
        DateOnly dateFrom,
        DateOnly dateTo,
        SectionType? sectionType = null,
        bool onlyAvailable = false,
        CancellationToken cancellationToken = default);

    /// <summary>POST /equipment/rent</summary>
    Task<EquipmentRentResponse> RentEquipmentAsync(
        EquipmentRentRequest request,
        CancellationToken cancellationToken = default);
}
