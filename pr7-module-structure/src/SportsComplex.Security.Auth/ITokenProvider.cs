namespace SportsComplex.Security.Auth;

/// <summary>Выдаёт JWT текущего пользователя (студента) для запросов к шлюзу.</summary>
public interface ITokenProvider
{
    Task<string?> GetAccessTokenAsync(CancellationToken cancellationToken = default);
}
