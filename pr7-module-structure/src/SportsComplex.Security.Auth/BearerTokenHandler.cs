using System.Net.Http.Headers;

namespace SportsComplex.Security.Auth;

/// <summary>DelegatingHandler: подставляет заголовок Authorization: Bearer в каждый запрос.</summary>
public sealed class BearerTokenHandler : DelegatingHandler
{
    private readonly ITokenProvider _tokens;

    public BearerTokenHandler(ITokenProvider tokens) => _tokens = tokens;

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var token = await _tokens.GetAccessTokenAsync(cancellationToken);
        if (token is not null)
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        return await base.SendAsync(request, cancellationToken);
    }
}
