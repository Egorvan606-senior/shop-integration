using SportsComplex.Shared.Contracts;
using SportsComplex.Shared.Contracts.Dto;

// Интеграционный шлюз спорткомплекса: реализует контракт openapi.yaml (ПР6).
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/v1/" + ApiRoutes.SectionsSchedule, (DateOnly dateFrom, DateOnly dateTo) =>
{
    var sessions = new[]
    {
        new SectionSessionDto("SES-2026-1026-01", "VOLLEYBALL", "Волейбол (сборная института)", "Игровой зал №1",
            new DateTimeOffset(2026, 10, 26, 18, 0, 0, TimeSpan.FromHours(3)),
            new DateTimeOffset(2026, 10, 26, 19, 30, 0, TimeSpan.FromHours(3)), 20, 6, true)
    };
    return Results.Ok(new { dateFrom, dateTo, totalSessions = sessions.Length, sessions });
});

app.MapPost("/v1/" + ApiRoutes.EquipmentRent, (EquipmentRentRequestDto request) =>
    Results.Created($"/v1/equipment/rent/RENT-000452",
        new EquipmentRentResponseDto("RENT-000452", request.SessionId, "CONFIRMED", request.Items)));

app.Run();
