namespace SportsComplex.Shared.Contracts.Dto;

/// <summary>DTO занятия секции — соответствует schemas/SectionSession из openapi.yaml (ПР6).</summary>
public sealed record SectionSessionDto(
    string SessionId,
    string SectionType,
    string Title,
    string Hall,
    DateTimeOffset StartsAt,
    DateTimeOffset EndsAt,
    int Capacity,
    int FreeSlots,
    bool EquipmentAvailable);
