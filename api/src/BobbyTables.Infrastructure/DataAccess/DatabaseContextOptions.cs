using System.ComponentModel.DataAnnotations;
using Microsoft.EntityFrameworkCore;

namespace BobbyTables.Infrastructure.DataAccess;

public sealed class DatabaseContextOptions
{
    public const string SectionName = "DatabaseContext";

    [Required]
    public required string ConnectionString { get; init; }

    public QueryTrackingBehavior QueryTrackingBehavior { get; init; } = QueryTrackingBehavior.NoTracking;
    public bool EnableSensitiveDataLogging { get; init; }
}
