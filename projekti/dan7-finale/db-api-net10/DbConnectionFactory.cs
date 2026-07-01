using Microsoft.Data.SqlClient;

/// <summary>
/// Fabrika za kreiranje SQL konekcija. Čita konekcijski string iz konfiguracije.
/// Ekvivalent funkciji get_db_connection() iz Python verzije.
/// </summary>
public class DbConnectionFactory
{
    private readonly string _connectionString;

    public DbConnectionFactory(IConfiguration config)
    {
        // Pokušaj učitati gotov konekcijski string, ili ga izgradi iz komponenti
        var cs = config.GetConnectionString("DefaultConnection");

        if (!string.IsNullOrWhiteSpace(cs))
        {
            _connectionString = cs;
        }
        else
        {
            // Fallback: gradi konekcijski string iz individualnih postavki (kao Python .env)
            var server   = config["DB_SERVER"]   ?? @"localhost\SQLEXPRESS";
            var database = config["DB_NAME"]     ?? "StateStatisticsDB";
            var trusted  = config["DB_TRUSTED_CONNECTION"] ?? "yes";

            var builder = new SqlConnectionStringBuilder
            {
                DataSource         = server,
                InitialCatalog     = database,
                TrustServerCertificate = true
            };

            if (trusted.Equals("yes", StringComparison.OrdinalIgnoreCase) ||
                trusted.Equals("true", StringComparison.OrdinalIgnoreCase) ||
                trusted == "1")
            {
                builder.IntegratedSecurity = true;
            }
            else
            {
                builder.UserID   = config["DB_USER"]     ?? "";
                builder.Password = config["DB_PASSWORD"] ?? "";
            }

            _connectionString = builder.ConnectionString;
        }
    }

    /// <summary>Kreira novu SQL konekciju (pozivalac je odgovoran za dispose).</summary>
    public SqlConnection CreateConnection() => new SqlConnection(_connectionString);
}
