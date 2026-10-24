using SportsComplex.Core.BusinessLogic.Rules;
using SportsComplex.Shared.Contracts.Dto;

namespace SportsComplex.Core.Tests;

public class RentalPolicyTests
{
    private static readonly DateTimeOffset Now = new(2026, 10, 26, 12, 0, 0, TimeSpan.FromHours(3));

    private static SectionSessionDto Session(bool equipment = true, int hoursToStart = 6) =>
        new("SES-2026-1026-01", "VOLLEYBALL", "Волейбол", "Игровой зал №1",
            Now.AddHours(hoursToStart), Now.AddHours(hoursToStart + 1.5), 20, 6, equipment);

    [Fact]
    public void Validate_CorrectRequest_NoErrors() =>
        Assert.Empty(RentalPolicy.Validate(Session(), new[] { new RentItemDto("BALL-VOLLEY", 1) }, Now));

    [Theory]
    [InlineData(0)]
    [InlineData(4)]
    public void Validate_WrongQuantity_ReturnsError(int quantity) =>
        Assert.Single(RentalPolicy.Validate(Session(), new[] { new RentItemDto("KNEE-PADS", quantity) }, Now));

    [Fact]
    public void Validate_SessionWithoutEquipment_ReturnsError() =>
        Assert.Single(RentalPolicy.Validate(Session(equipment: false), new[] { new RentItemDto("BALL-VOLLEY", 1) }, Now));

    [Fact]
    public void Validate_LessThan30MinutesToStart_ReturnsError() =>
        Assert.Single(RentalPolicy.Validate(Session(hoursToStart: 0), new[] { new RentItemDto("BALL-VOLLEY", 1) }, Now));
}
