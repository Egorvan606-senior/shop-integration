using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using SportsComplex.Client.Models;

namespace SportsComplex.Client.Services;

/// <summary>
/// Класс-клиент интеграционного шлюза спорткомплекса.
/// Инкапсулирует построение URL, авторизацию, сериализацию и обработку ошибок.
/// </summary>
public sealed class SportsComplexApiClient : ISportsComplexApiClient
{
    private const int MaxPeriodDays = 14;
    private readonly HttpClient _http;

    public SportsComplexApiClient(HttpClient http, string? accessToken = null)
    {
        _http = http ?? throw new ArgumentNullException(nameof(http));
        if (!string.IsNullOrWhiteSpace(accessToken))
        {
            _http.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", accessToken);
        }
    }

    public async Task<SectionSchedule> GetScheduleAsync(
        DateOnly dateFrom,
        DateOnly dateTo,
        SectionType? sectionType = null,
        bool onlyAvailable = false,
        CancellationToken cancellationToken = default)
    {
        if (dateTo < dateFrom)
            throw new ArgumentException("dateTo не может быть раньше dateFrom.");
        if (dateTo.DayNumber - dateFrom.DayNumber > MaxPeriodDays)
            throw new ArgumentException($"Период не может превышать {MaxPeriodDays} дней.");

        var query = new List<string>
        {
            $"dateFrom={dateFrom:yyyy-MM-dd}",
            $"dateTo={dateTo:yyyy-MM-dd}"
        };
        if (sectionType is not null)
            query.Add($"sectionType={ToContractName(sectionType.Value)}");
        if (onlyAvailable)
            query.Add("onlyAvailable=true");

        using var response = await _http.GetAsync(
            "sections/schedule?" + string.Join('&', query), cancellationToken);

        return await ReadAsync<SectionSchedule>(response, cancellationToken);
    }

    public async Task<EquipmentRentResponse> RentEquipmentAsync(
        EquipmentRentRequest request,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (request.Items.Count == 0)
            throw new ArgumentException("Нужно выбрать хотя бы одну позицию инвентаря.");
        if (request.Items.Any(i => i.Quantity is < 1 or > 3))
            throw new ArgumentException("Количество одной позиции — от 1 до 3.");

        using var response = await _http.PostAsJsonAsync(
            "equipment/rent", request, ApiJson.Options, cancellationToken);

        return await ReadAsync<EquipmentRentResponse>(response, cancellationToken);
    }

    /// <summary>Перевод значения enum в имя из контракта (TableTennis → TABLE_TENNIS).</summary>
    public static string ToContractName<TEnum>(TEnum value) where TEnum : struct, Enum =>
        JsonNamingPolicy.SnakeCaseUpper.ConvertName(value.ToString());

    private static async Task<T> ReadAsync<T>(HttpResponseMessage response, CancellationToken ct)
    {
        if (!response.IsSuccessStatusCode)
        {
            ApiError? error = null;
            try
            {
                error = await response.Content.ReadFromJsonAsync<ApiError>(ApiJson.Options, ct);
            }
            catch (JsonException)
            {
                // тело ошибки не соответствует контракту — оставляем только код
            }
            throw new SportsComplexApiException(response.StatusCode, error);
        }

        var body = await response.Content.ReadFromJsonAsync<T>(ApiJson.Options, ct);
        return body ?? throw new JsonException("Шлюз вернул пустой ответ.");
    }
}
