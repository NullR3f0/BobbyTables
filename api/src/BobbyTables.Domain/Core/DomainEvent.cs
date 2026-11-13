namespace BobbyTables.Domain.Core;

public interface IDomainEvent
{
    public Guid EventId { get; init; }
    public DateTimeOffset OccurredOn { get; init; }
    public string EventType => GetType().AssemblyQualifiedName!;
}