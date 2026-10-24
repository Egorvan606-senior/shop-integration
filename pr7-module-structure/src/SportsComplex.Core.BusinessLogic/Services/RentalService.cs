using SportsComplex.Core.BusinessLogic.Abstractions;
using SportsComplex.Core.BusinessLogic.Rules;
using SportsComplex.Shared.Contracts.Dto;

namespace SportsComplex.Core.BusinessLogic.Services;

public sealed class RentalService
{
    private readonly ISportsGatewayClient _gateway;

    public RentalService(ISportsGatewayClient gateway) => _gateway = gateway;

    public async Task<EquipmentRentResponseDto> RentAsync(
        string studentId, SectionSessionDto session, IReadOnlyList<RentItemDto> items, DateTimeOffset now, CancellationToken ct = default)
    {
        var errors = RentalPolicy.Validate(session, items, now);
        if (errors.Count > 0)
            throw new InvalidOperationException(string.Join(Environment.NewLine, errors));

        return await _gateway.RentAsync(new EquipmentRentRequestDto(studentId, session.SessionId, items), ct);
    }
}
