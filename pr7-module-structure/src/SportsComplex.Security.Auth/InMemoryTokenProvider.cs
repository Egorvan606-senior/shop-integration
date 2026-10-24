namespace SportsComplex.Security.Auth;

/// <summary>Хранит токен, полученный при входе через SSO вуза, в памяти процесса.</summary>
public sealed class InMemoryTokenProvider : ITokenProvider
{
    private string? _token;
    private DateTimeOffset _expiresAt;

    public void SetToken(string token, DateTimeOffset expiresAt)
    {
        _token = token;
        _expiresAt = expiresAt;
    }

    public Task<string?> GetAccessTokenAsync(CancellationToken cancellationToken = default) =>
        Task.FromResult(_token is not null && _expiresAt > DateTimeOffset.UtcNow ? _token : null);
}
