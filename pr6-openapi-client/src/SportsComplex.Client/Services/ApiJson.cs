using System.Text.Json;
using System.Text.Json.Serialization;

namespace SportsComplex.Client.Services;

/// <summary>
/// Общие настройки сериализации, согласованные с контрактом openapi.yaml:
/// поля в camelCase, перечисления в UPPER_SNAKE_CASE (VOLLEYBALL, TABLE_TENNIS, WAITING_LIST).
/// </summary>
public static class ApiJson
{
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web)
    {
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        Converters = { new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseUpper) }
    };
}
