-- ============================================================
-- Stored Procedures for StateStatisticsDB
-- Run this script against StateStatisticsDB after setup-database.sql
-- ============================================================

USE StateStatisticsDB;
GO

-- ------------------------------------------------------------
-- SP 1: Stats.sp_GetAllEmployees
-- Returns all employee rows — used with SqlQuery<Employee>
-- ------------------------------------------------------------
IF OBJECT_ID('Stats.sp_GetAllEmployees', 'P') IS NOT NULL
    DROP PROCEDURE Stats.sp_GetAllEmployees;
GO

CREATE PROCEDURE Stats.sp_GetAllEmployees
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        EmployeeID,
        FirstName,
        LastName,
        JMBG,
        DepartmentID,
        Position,
        Salary,
        HireDate,
        Email,
        CreatedDate,
        ModifiedDate
    FROM Stats.Employees
    ORDER BY LastName, FirstName;
END
GO

-- ------------------------------------------------------------
-- SP 2: Stats.sp_GetEmployeesByDepartment
-- Returns employees filtered by department — SqlQuery<Employee>
-- ------------------------------------------------------------
IF OBJECT_ID('Stats.sp_GetEmployeesByDepartment', 'P') IS NOT NULL
    DROP PROCEDURE Stats.sp_GetEmployeesByDepartment;
GO

CREATE PROCEDURE Stats.sp_GetEmployeesByDepartment
    @DepartmentID INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        EmployeeID,
        FirstName,
        LastName,
        JMBG,
        DepartmentID,
        Position,
        Salary,
        HireDate,
        Email,
        CreatedDate,
        ModifiedDate
    FROM Stats.Employees
    WHERE DepartmentID = @DepartmentID
    ORDER BY LastName, FirstName;
END
GO

-- ------------------------------------------------------------
-- SP 3: Stats.sp_SearchEmployees
-- Returns employees filtered by optional params — SqlQuery<Employee>
-- @DepartmentID  INT     = NULL  (omit to search all departments)
-- @MinSalary     DECIMAL = NULL  (omit for no lower bound)
-- @MaxSalary     DECIMAL = NULL  (omit for no upper bound)
-- ------------------------------------------------------------
IF OBJECT_ID('Stats.sp_SearchEmployees', 'P') IS NOT NULL
    DROP PROCEDURE Stats.sp_SearchEmployees;
GO

CREATE PROCEDURE Stats.sp_SearchEmployees
    @DepartmentID  INT             = NULL,
    @MinSalary     DECIMAL(18, 2)  = NULL,
    @MaxSalary     DECIMAL(18, 2)  = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        EmployeeID,
        FirstName,
        LastName,
        JMBG,
        DepartmentID,
        Position,
        Salary,
        HireDate,
        Email,
        CreatedDate,
        ModifiedDate
    FROM Stats.Employees
    WHERE
        (@DepartmentID IS NULL OR DepartmentID = @DepartmentID)
        AND (@MinSalary IS NULL OR Salary >= @MinSalary)
        AND (@MaxSalary IS NULL OR Salary <= @MaxSalary)
    ORDER BY LastName, FirstName;
END
GO

-- ------------------------------------------------------------
-- SP 4: Stats.sp_GetDepartmentSummary
-- Returns a CUSTOM shape (JOIN + GROUP BY aggregates)
-- Used with SqlQuery<DepartmentSummaryViewModel>
-- Columns: DepartmentID, DepartmentName, DepartmentCode, Budget,
--          ManagerFullName, EmployeeCount, AverageSalary,
--          TotalSalaryBill, TotalProjectCount, ActiveProjectCount,
--          TotalProjectBudget
-- ------------------------------------------------------------
IF OBJECT_ID('Stats.sp_GetDepartmentSummary', 'P') IS NOT NULL
    DROP PROCEDURE Stats.sp_GetDepartmentSummary;
GO

CREATE PROCEDURE Stats.sp_GetDepartmentSummary
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        d.DepartmentID,
        d.DepartmentName,
        d.DepartmentCode,
        d.Budget,
        ISNULL(m.LastName + ' ' + m.FirstName, 'N/A')  AS ManagerFullName,
        COUNT(DISTINCT e.EmployeeID)                    AS EmployeeCount,
        ISNULL(AVG(e.Salary), 0)                        AS AverageSalary,
        ISNULL(SUM(e.Salary), 0)                        AS TotalSalaryBill,
        COUNT(DISTINCT p.ProjectID)                     AS TotalProjectCount,
        SUM(CASE WHEN p.Status = 'InProgress' THEN 1 ELSE 0 END)
                                                        AS ActiveProjectCount,
        ISNULL(SUM(p.Budget), 0)                        AS TotalProjectBudget
    FROM Stats.Departments d
    LEFT JOIN Stats.Employees  m ON d.ManagerID    = m.EmployeeID
    LEFT JOIN Stats.Employees  e ON e.DepartmentID = d.DepartmentID
    LEFT JOIN Stats.Projects   p ON p.DepartmentID = d.DepartmentID
    GROUP BY
        d.DepartmentID,
        d.DepartmentName,
        d.DepartmentCode,
        d.Budget,
        m.LastName,
        m.FirstName
    ORDER BY d.DepartmentName;
END
GO

-- ------------------------------------------------------------
-- SP 5: Stats.sp_GetRegionalStatsByYear
-- Returns a CUSTOM shape with a computed GDPPerCapita column
-- Used with SqlQuery<RegionalStatsViewModel>
-- Columns: RegionID, RegionName, RegionCode, Population, Year,
--          GDP, UnemploymentRate, AverageSalary, InflationRate,
--          GDPPerCapita
-- ------------------------------------------------------------
IF OBJECT_ID('Stats.sp_GetRegionalStatsByYear', 'P') IS NOT NULL
    DROP PROCEDURE Stats.sp_GetRegionalStatsByYear;
GO

CREATE PROCEDURE Stats.sp_GetRegionalStatsByYear
    @Year INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        r.RegionID,
        r.RegionName,
        r.RegionCode,
        r.Population,
        ed.Year,
        ed.GDP,
        ed.UnemploymentRate,
        ed.AverageSalary,
        ed.InflationRate,
        CASE
            WHEN r.Population > 0 AND ed.GDP IS NOT NULL
            THEN ed.GDP / r.Population
            ELSE NULL
        END AS GDPPerCapita
    FROM Stats.Regions r
    INNER JOIN Stats.EconomicData ed ON ed.RegionID = r.RegionID
    WHERE ed.Year = @Year
    ORDER BY r.RegionName;
END
GO

-- ------------------------------------------------------------
-- SP 6: Stats.sp_GiveSalaryRaise
-- UPDATE — no SELECT; returns rows-affected via ExecuteSqlCommand
-- @DepartmentID        INT
-- @PercentageIncrease  DECIMAL  (e.g. 10 = 10%)
-- ------------------------------------------------------------
IF OBJECT_ID('Stats.sp_GiveSalaryRaise', 'P') IS NOT NULL
    DROP PROCEDURE Stats.sp_GiveSalaryRaise;
GO

CREATE PROCEDURE Stats.sp_GiveSalaryRaise
    @DepartmentID       INT,
    @PercentageIncrease DECIMAL(5, 2)
AS
BEGIN
    SET NOCOUNT OFF;   -- OFF so @@ROWCOUNT / rows-affected is returned to the caller

    UPDATE Stats.Employees
    SET
        Salary       = Salary * (1 + @PercentageIncrease / 100.0),
        ModifiedDate = GETDATE()
    WHERE DepartmentID = @DepartmentID;
END
GO

-- ------------------------------------------------------------
-- SP 7: Stats.sp_UpdateProjectStatus
-- UPDATE — no SELECT; returns rows-affected via ExecuteSqlCommand
-- @ProjectID   INT
-- @NewStatus   NVARCHAR(50)  (Planned | InProgress | Completed | Cancelled)
-- ------------------------------------------------------------
IF OBJECT_ID('Stats.sp_UpdateProjectStatus', 'P') IS NOT NULL
    DROP PROCEDURE Stats.sp_UpdateProjectStatus;
GO

CREATE PROCEDURE Stats.sp_UpdateProjectStatus
    @ProjectID  INT,
    @NewStatus  NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT OFF;   -- OFF so rows-affected is returned to the caller

    UPDATE Stats.Projects
    SET Status = @NewStatus
    WHERE ProjectID = @ProjectID;
END
GO

-- ============================================================
-- Verification — run after creation to confirm SPs exist
-- ============================================================
SELECT
    name        AS StoredProcedure,
    create_date AS Created,
    modify_date AS Modified
FROM sys.procedures
WHERE schema_id = SCHEMA_ID('Stats')
ORDER BY name;
GO
