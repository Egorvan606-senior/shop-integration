using SportsComplex.Core.BusinessLogic.Services;
using SportsComplex.Data.ApiClient;
using SportsComplex.Security.Auth;
using SportsComplex.UI.Desktop.Forms;

namespace SportsComplex.UI.Desktop;

internal static class Program
{
    /// <summary>Composition Root: здесь собираются модули приложения.</summary>
    [STAThread]
    private static void Main()
    {
        ApplicationConfiguration.Initialize();

        var tokens = new InMemoryTokenProvider();
        var http = new HttpClient(new BearerTokenHandler(tokens) { InnerHandler = new HttpClientHandler() })
        {
            BaseAddress = new Uri("https://api.sport.spbiem.local/v1/")
        };
        var gateway = new SportsGatewayHttpClient(http);

        Application.Run(new ScheduleForm(new ScheduleService(gateway), new RentalService(gateway)));
    }
}
