using SportsComplex.Core.BusinessLogic.Services;
using SportsComplex.Shared.Contracts.Dto;

namespace SportsComplex.UI.Desktop.Forms;

/// <summary>Главная форма: расписание секций и бронирование инвентаря.</summary>
public sealed class ScheduleForm : Form
{
    private readonly ScheduleService _schedule;
    private readonly RentalService _rental;
    private readonly DataGridView _grid = new() { Dock = DockStyle.Fill, ReadOnly = true, AutoGenerateColumns = true };
    private readonly Button _refresh = new() { Text = "Обновить расписание", Dock = DockStyle.Top, Height = 36 };
    private readonly Button _rent = new() { Text = "Забронировать мяч к занятию", Dock = DockStyle.Bottom, Height = 36 };

    public ScheduleForm(ScheduleService schedule, RentalService rental)
    {
        _schedule = schedule;
        _rental = rental;
        Text = "АИС «Спортивный комплекс и секции»";
        Width = 900;
        Height = 520;
        Controls.Add(_grid);
        Controls.Add(_refresh);
        Controls.Add(_rent);
        _refresh.Click += async (_, _) => await LoadAsync();
        _rent.Click += async (_, _) => await RentSelectedAsync();
    }

    private async Task LoadAsync()
    {
        try
        {
            _grid.DataSource = (await _schedule.GetAvailableThisWeekAsync(DateOnly.FromDateTime(DateTime.Today))).ToList();
        }
        catch (HttpRequestException ex)
        {
            MessageBox.Show($"Шлюз недоступен: {ex.Message}", Text);
        }
    }

    private async Task RentSelectedAsync()
    {
        if (_grid.CurrentRow?.DataBoundItem is not SectionSessionDto session) return;
        try
        {
            var result = await _rental.RentAsync("I14-23-9-010", session,
                new[] { new RentItemDto("BALL-VOLLEY", 1) }, DateTimeOffset.Now);
            MessageBox.Show($"Бронь {result.RentId}: {result.Status}", Text);
        }
        catch (Exception ex) when (ex is InvalidOperationException or HttpRequestException)
        {
            MessageBox.Show(ex.Message, Text);
        }
    }
}
