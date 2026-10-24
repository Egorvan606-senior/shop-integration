using System.Net;
using SportsComplex.Client.Models;

namespace SportsComplex.Client.Services;

/// <summary>Ошибка, которую вернул шлюз (4xx/5xx), в виде, удобном для UI.</summary>
public sealed class SportsComplexApiException : Exception
{
    public HttpStatusCode StatusCode { get; }
    public ApiError? Error { get; }

    public SportsComplexApiException(HttpStatusCode statusCode, ApiError? error)
        : base(error?.Message ?? $"Шлюз вернул код {(int)statusCode}")
    {
        StatusCode = statusCode;
        Error = error;
    }
}
