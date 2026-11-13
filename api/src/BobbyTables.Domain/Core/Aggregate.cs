namespace BobbyTables.Domain.Core;

public abstract class Aggregate<TId> : Entity<TId>
{
    private readonly List<IDomainEvent> _domainEvents = [];

    public IReadOnlyList<IDomainEvent> DomainEvents => _domainEvents;

    public void AddDomainEvent(IDomainEvent @event) => _domainEvents.Add(@event);

    public List<IDomainEvent> ClearDomainEvents()
    {
        var dequeued = _domainEvents.ToList();

        _domainEvents.Clear();

        return dequeued;
    }
}
