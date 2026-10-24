using SportsComplex.Client.Services;
using SportsComplex.Client.UI;

Console.OutputEncoding = System.Text.Encoding.UTF8;

// Точка сборки зависимостей: UI получает сетевой слой через интерфейс.
var http = new HttpClient
{
    BaseAddress = new Uri("https://api.sport.spbiem.local/v1/"),
    Timeout = TimeSpan.FromSeconds(10)
};
ISportsComplexApiClient api = new SportsComplexApiClient(http, Environment.GetEnvironmentVariable("SPORT_API_TOKEN"));

await new MainMenu(api).RunAsync();
