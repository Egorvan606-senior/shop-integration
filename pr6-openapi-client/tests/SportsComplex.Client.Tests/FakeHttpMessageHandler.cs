using System.Net;
using System.Text;

namespace SportsComplex.Client.Tests;

/// <summary>
/// Подменяет сеть: возвращает заранее заданный JSON и запоминает последний запрос,
/// чтобы тест не зависел от доступности реального шлюза.
/// </summary>
internal sealed class FakeHttpMessageHandler : HttpMessageHandler
{
    private readonly HttpStatusCode _status;
    private readonly string _json;

    public HttpRequestMessage? LastRequest { get; private set; }
    public string? LastRequestBody { get; private set; }

    public FakeHttpMessageHandler(HttpStatusCode status, string json)
    {
        _status = status;
        _json = json;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        LastRequest = request;
        if (request.Content is not null)
            LastRequestBody = await request.Content.ReadAsStringAsync(cancellationToken);

        return new HttpResponseMessage(_status)
        {
            Content = new StringContent(_json, Encoding.UTF8, "application/json")
        };
    }
}
