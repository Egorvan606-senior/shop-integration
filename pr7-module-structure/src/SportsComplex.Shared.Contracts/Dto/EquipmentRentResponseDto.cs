namespace SportsComplex.Shared.Contracts.Dto;

public sealed record EquipmentRentResponseDto(string RentId, string SessionId, string Status, IReadOnlyList<RentItemDto> Items);
