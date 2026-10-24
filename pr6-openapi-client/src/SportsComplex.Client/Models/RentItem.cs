namespace SportsComplex.Client.Models;

/// <summary>Позиция инвентаря в брони (components/schemas/RentItem).</summary>
public sealed record RentItem(string EquipmentCode, int Quantity);
