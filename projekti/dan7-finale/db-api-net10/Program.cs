using Microsoft.Data.SqlClient;

var builder = WebApplication.CreateBuilder(args);

// Dodaj OpenAPI / Swagger podršku (ugrađena u .NET 10)
builder.Services.AddOpenApi();

// Registruj DbConnectionFactory kao singleton servis
builder.Services.AddSingleton<DbConnectionFactory>();

var app = builder.Build();

// .NET 10: MapOpenApi() i ugrađeni Swagger UI (bez Swashbuckle paketa)
app.MapOpenApi();

if (app.Environment.IsDevelopment())
{
    // Ugrađeni OpenAPI UI dostupan na /openapi/ui
    app.MapGet("/swagger", () => Results.Redirect("/openapi/ui")).ExcludeFromDescription();
}

app.UseHttpsRedirection();

// ─────────────────────────────────────────────
//  GET /api/departments
// ─────────────────────────────────────────────
app.MapGet("/api/departments", async (DbConnectionFactory factory) =>
{
    var results = new List<Department>();
    await using var conn = factory.CreateConnection();
    await conn.OpenAsync();
    await using var cmd = new SqlCommand(
        "SELECT DepartmentID, DepartmentName, DepartmentCode, Budget FROM Stats.Departments", conn);
    await using var reader = await cmd.ExecuteReaderAsync();
    while (await reader.ReadAsync())
    {
        results.Add(new Department(
            reader.GetInt32(0),
            reader.GetString(1),
            reader.GetString(2),
            reader.GetDecimal(3)
        ));
    }
    return Results.Ok(results);
})
.WithName("GetDepartments")
.WithSummary("Vraća sva odjeljenja/ministarstva");

// ─────────────────────────────────────────────
//  GET /api/employees
// ─────────────────────────────────────────────
app.MapGet("/api/employees", async (DbConnectionFactory factory) =>
{
    var results = new List<Employee>();
    await using var conn = factory.CreateConnection();
    await conn.OpenAsync();
    const string sql = """
        SELECT e.EmployeeID, e.FirstName, e.LastName, d.DepartmentName, e.Position
        FROM Stats.Employees e
        INNER JOIN Stats.Departments d ON e.DepartmentID = d.DepartmentID
        """;
    await using var cmd = new SqlCommand(sql, conn);
    await using var reader = await cmd.ExecuteReaderAsync();
    while (await reader.ReadAsync())
    {
        results.Add(new Employee(
            reader.GetInt32(0),
            reader.GetString(1),
            reader.GetString(2),
            reader.GetString(3),
            reader.GetString(4)
        ));
    }
    return Results.Ok(results);
})
.WithName("GetAllEmployees")
.WithSummary("Vraća sve zaposlenike u sistemu");

// ─────────────────────────────────────────────
//  GET /api/employees/search?name=...
// ─────────────────────────────────────────────
app.MapGet("/api/employees/search", async (string name, DbConnectionFactory factory) =>
{
    var results = new List<Employee>();
    await using var conn = factory.CreateConnection();
    await conn.OpenAsync();
    const string sql = """
        SELECT e.EmployeeID, e.FirstName, e.LastName, d.DepartmentName, e.Position
        FROM Stats.Employees e
        INNER JOIN Stats.Departments d ON e.DepartmentID = d.DepartmentID
        WHERE e.FirstName LIKE @term OR e.LastName LIKE @term
        """;
    await using var cmd = new SqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("@term", $"%{name}%");
    await using var reader = await cmd.ExecuteReaderAsync();
    while (await reader.ReadAsync())
    {
        results.Add(new Employee(
            reader.GetInt32(0),
            reader.GetString(1),
            reader.GetString(2),
            reader.GetString(3),
            reader.GetString(4)
        ));
    }
    return Results.Ok(results);
})
.WithName("SearchEmployees")
.WithSummary("Pretražuje zaposlenike po imenu ili prezimenu");

// ─────────────────────────────────────────────
//  GET /api/economic-data?year=2023
// ─────────────────────────────────────────────
app.MapGet("/api/economic-data", async (int year, DbConnectionFactory factory) =>
{
    var results = new List<EconomicData>();
    await using var conn = factory.CreateConnection();
    await conn.OpenAsync();
    const string sql = """
        SELECT r.RegionName, ed.Year, ed.GDP, ed.UnemploymentRate, ed.AverageSalary
        FROM Stats.EconomicData ed
        INNER JOIN Stats.Regions r ON ed.RegionID = r.RegionID
        WHERE ed.Year = @year
        """;
    await using var cmd = new SqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("@year", year);
    await using var reader = await cmd.ExecuteReaderAsync();
    while (await reader.ReadAsync())
    {
        results.Add(new EconomicData(
            reader.GetString(0),
            reader.GetInt32(1),
            reader.IsDBNull(2) ? null : reader.GetDecimal(2),
            reader.IsDBNull(3) ? null : reader.GetDecimal(3),
            reader.IsDBNull(4) ? null : reader.GetDecimal(4)
        ));
    }
    return Results.Ok(results);
})
.WithName("GetEconomicData")
.WithSummary("Vraća ekonomske podatke za traženu godinu po regijama");

// ─────────────────────────────────────────────
//  GET /api/projects/budget?department_code=MF
// ─────────────────────────────────────────────
app.MapGet("/api/projects/budget", async (string department_code, DbConnectionFactory factory) =>
{
    await using var conn = factory.CreateConnection();
    await conn.OpenAsync();
    const string sql = """
        SELECT SUM(p.Budget)
        FROM Stats.Projects p
        INNER JOIN Stats.Departments d ON p.DepartmentID = d.DepartmentID
        WHERE d.DepartmentCode = @code
        """;
    await using var cmd = new SqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("@code", department_code);
    var scalar = await cmd.ExecuteScalarAsync();
    var total = scalar == null || scalar == DBNull.Value ? 0m : Convert.ToDecimal(scalar);
    return Results.Ok(new { department_code, total_projects_budget = total });
})
.WithName("GetProjectBudget")
.WithSummary("Vraća ukupan budžet projekata za dati kod odjeljenja (npr. 'MF', 'MO')");

app.Run();

// ─────────────────────────────────────────────
//  Record modeli (ekvivalent Pydantic modelima)
// ─────────────────────────────────────────────
record Department(int DepartmentID, string DepartmentName, string DepartmentCode, decimal Budget);
record Employee(int EmployeeID, string FirstName, string LastName, string DepartmentName, string Position);
record EconomicData(string RegionName, int Year, decimal? GDP, decimal? UnemploymentRate, decimal? AverageSalary);
