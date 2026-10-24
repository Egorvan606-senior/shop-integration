using System.Net;
using SportsComplex.Client.Models;
using SportsComplex.Client.Services;

namespace SportsComplex.Client.Tests;

public class SportsComplexApiClientTests
{
    private const string BaseUrl = "https://api.sport.spbiem.local/v1/";

    // Пример ответа взят из openapi.yaml (GET /sections/schedule → 200)
    private const string ScheduleJson = """
    {
      "dateFrom": "2026-10-26",
      "dateTo": "2026-11-01",
      "totalSessions": 2,
      "sessions": [
        {
          "sessionId": "SES-2026-1026-01",
          "sectionType": "VOLLEYBALL",
          "title": "Волейбол (сборная института)",
          "coachName": "Петров А.В.",
          "hall": "Игровой зал №1",
          "startsAt": "2026-10-26T18:00:00+03:00",
          "endsAt": "2026-10-26T19:30:00+03:00",
          "capacity": 20,
          "freeSlots": 6,
          "equipmentAvailable": true
        },
        {
          "sessionId": "SES-2026-1027-02",
          "sectionType": "TABLE_TENNIS",
          "title": "Настольный теннис",
          "hall": "Малый зал",
          "startsAt": "2026-10-27T17:00:00+03:00",
          "endsAt": "2026-10-27T18:30:00+03:00",
          "capacity": 8,
          "freeSlots": 0,
          "equipmentAvailable": false
        }
      ]
    }
    """;

    private static (SportsComplexApiClient client, FakeHttpMessageHandler handler) Create(
        HttpStatusCode status, string json)
    {
        var handler = new FakeHttpMessageHandler(status, json);
        var http = new HttpClient(handler) { BaseAddress = new Uri(BaseUrl) };
        return (new SportsComplexApiClient(http, "test-token"), handler);
    }

    [Fact]
    public async Task GetScheduleAsync_DeserializesResponseAccordingToContract()
    {
        var (client, _) = Create(HttpStatusCode.OK, ScheduleJson);

        var schedule = await client.GetScheduleAsync(new DateOnly(2026, 10, 26), new DateOnly(2026, 11, 1));

        Assert.Equal(new DateOnly(2026, 10, 26), schedule.DateFrom);
        Assert.Equal(2, schedule.TotalSessions);
        Assert.Equal(2, schedule.Sessions.Count);

        var volleyball = schedule.Sessions[0];
        Assert.Equal("SES-2026-1026-01", volleyball.SessionId);
        Assert.Equal(SectionType.Volleyball, volleyball.SectionType);
        Assert.Equal("Петров А.В.", volleyball.CoachName);
        Assert.Equal(new DateTimeOffset(2026, 10, 26, 18, 0, 0, TimeSpan.FromHours(3)), volleyball.StartsAt);
        Assert.True(volleyball.HasFreeSlots);

        var tennis = schedule.Sessions[1];
        Assert.Equal(SectionType.TableTennis, tennis.SectionType);   // "TABLE_TENNIS" → enum
        Assert.Null(tennis.CoachName);                               // необязательное поле
        Assert.False(tennis.HasFreeSlots);
        Assert.False(tennis.EquipmentAvailable);
    }

    [Fact]
    public async Task GetScheduleAsync_BuildsQueryAndSendsBearerToken()
    {
        var (client, handler) = Create(HttpStatusCode.OK, ScheduleJson);

        await client.GetScheduleAsync(new DateOnly(2026, 10, 26), new DateOnly(2026, 11, 1),
            SectionType.TableTennis, onlyAvailable: true);

        Assert.NotNull(handler.LastRequest);
        Assert.Equal(HttpMethod.Get, handler.LastRequest!.Method);
        Assert.Equal(
            BaseUrl + "sections/schedule?dateFrom=2026-10-26&dateTo=2026-11-01&sectionType=TABLE_TENNIS&onlyAvailable=true",
            handler.LastRequest.RequestUri!.ToString());
        Assert.Equal("Bearer", handler.LastRequest.Headers.Authorization?.Scheme);
    }

    [Fact]
    public async Task RentEquipmentAsync_SerializesRequestAndDeserializesResponse()
    {
        const string rentJson = """
        {
          "rentId": "RENT-000452",
          "sessionId": "SES-2026-1026-01",
          "status": "CONFIRMED",
          "pickupPoint": "Пункт выдачи инвентаря, 1 этаж",
          "returnDeadline": "2026-10-26T20:00:00+03:00",
          "items": [ { "equipmentCode": "BALL-VOLLEY", "quantity": 1 } ]
        }
        """;
        var (client, handler) = Create(HttpStatusCode.Created, rentJson);

        var rent = await client.RentEquipmentAsync(new EquipmentRentRequest
        {
            StudentId = "I14-23-9-010",
            SessionId = "SES-2026-1026-01",
            Items = new[] { new RentItem("BALL-VOLLEY", 1) }
        });

        Assert.Equal(HttpMethod.Post, handler.LastRequest!.Method);
        Assert.Contains("\"sessionId\":\"SES-2026-1026-01\"", handler.LastRequestBody);
        Assert.Contains("\"equipmentCode\":\"BALL-VOLLEY\"", handler.LastRequestBody);

        Assert.Equal("RENT-000452", rent.RentId);
        Assert.Equal(RentStatus.Confirmed, rent.Status);
        Assert.Single(rent.Items);
    }

    [Fact]
    public async Task RentEquipmentAsync_Conflict_ThrowsApiExceptionWithContractError()
    {
        const string errorJson = """
        { "code": "EQUIPMENT_NOT_AVAILABLE", "message": "Нет свободных наколенников", "traceId": "c0a8012e-7f31-4b4e-9d1a-2f6c0e9a1b77" }
        """;
        var (client, _) = Create(HttpStatusCode.Conflict, errorJson);

        var ex = await Assert.ThrowsAsync<SportsComplexApiException>(() =>
            client.RentEquipmentAsync(new EquipmentRentRequest
            {
                StudentId = "I14-23-9-010",
                SessionId = "SES-2026-1026-01",
                Items = new[] { new RentItem("KNEE-PADS", 2) }
            }));

        Assert.Equal(HttpStatusCode.Conflict, ex.StatusCode);
        Assert.Equal("EQUIPMENT_NOT_AVAILABLE", ex.Error?.Code);
    }

    [Fact]
    public async Task GetScheduleAsync_PeriodLongerThan14Days_ThrowsBeforeSendingRequest()
    {
        var (client, handler) = Create(HttpStatusCode.OK, ScheduleJson);

        await Assert.ThrowsAsync<ArgumentException>(() =>
            client.GetScheduleAsync(new DateOnly(2026, 10, 1), new DateOnly(2026, 10, 31)));

        Assert.Null(handler.LastRequest);
    }
}
