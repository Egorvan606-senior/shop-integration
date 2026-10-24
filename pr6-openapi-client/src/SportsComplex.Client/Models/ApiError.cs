namespace SportsComplex.Client.Models;

/// <summary>Единый формат ошибки шлюза (components/schemas/ApiError).</summary>
public sealed record ApiError(string Code, string Message, string? TraceId = null);
