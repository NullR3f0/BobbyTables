namespace BobbyTables.Domain.Core;

public abstract class Entity<TId>
{
    public required TId Id { get; set; }
}