namespace SportsComplex.Shared.Contracts.Dto;

public sealed record EquipmentRentRequestDto(string StudentId, string SessionId, IReadOnlyList<RentItemDto> Items);
