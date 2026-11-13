using BobbyTables.Infrastructure.DataAccess;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace BobbyTables.Infrastructure;

public static class InfrastructureExtensions
{
    extension(IServiceCollection services)
    {
        public IServiceCollection AddInfrastructure(IConfiguration configuration)
        {
            services.AddSingleton(TimeProvider.System);

            services.AddOptions<DatabaseContextOptions>()
                .Bind(configuration.GetSection(DatabaseContextOptions.SectionName))
                .ValidateDataAnnotations()
                .ValidateOnStart();

            services.AddDbContext<DatabaseContext>((provider, options) =>
                {
                    var contextOptions = provider.GetRequiredService<IOptions<DatabaseContextOptions>>().Value;

                    options.UseNpgsql(contextOptions.ConnectionString);
                    options.UseSnakeCaseNamingConvention();
                    options.UseQueryTrackingBehavior(contextOptions.QueryTrackingBehavior);
                    options.EnableSensitiveDataLogging(contextOptions.EnableSensitiveDataLogging);
                }
            );

            return services;
        }
    }
}