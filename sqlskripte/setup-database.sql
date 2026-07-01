-- =============================================
-- StateStatisticsDB - Kompletan Setup Script
-- Baza podataka za državnu statistiku i agencije
-- =============================================

-- Kreiranje baze podataka
IF DB_ID('StateStatisticsDB') IS NOT NULL
BEGIN
    ALTER DATABASE StateStatisticsDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE StateStatisticsDB;
END
GO

CREATE DATABASE StateStatisticsDB
ON 
(
    NAME = 'StateStatisticsDB_Data',
    FILENAME = 'C:\SQLData\StateStatisticsDB.mdf',
    SIZE = 100MB,
    MAXSIZE = 1GB,
    FILEGROWTH = 10MB
)
LOG ON 
(
    NAME = 'StateStatisticsDB_Log',
    FILENAME = 'C:\SQLData\StateStatisticsDB.ldf',
    SIZE = 10MB,
    MAXSIZE = 100MB,
    FILEGROWTH = 5MB
);
GO

USE StateStatisticsDB;
GO

-- =============================================
-- Kreiranje Schema-a
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Stats')
BEGIN
    EXEC('CREATE SCHEMA Stats');
END
GO

-- =============================================
-- 1. Regions - Regije/Općine
-- =============================================
CREATE TABLE Stats.Regions (
    RegionID INT PRIMARY KEY IDENTITY(1,1),
    RegionName NVARCHAR(100) NOT NULL,
    RegionCode NVARCHAR(10) NOT NULL UNIQUE,
    Population INT NOT NULL CHECK (Population >= 0),
    Area DECIMAL(10,2) NOT NULL CHECK (Area > 0), -- km²
    CreatedDate DATETIME2 DEFAULT SYSDATETIME(),
    ModifiedDate DATETIME2 DEFAULT SYSDATETIME()
);
GO

-- =============================================
-- 2. Departments - Odjeljenja/Ministarstva
-- =============================================
CREATE TABLE Stats.Departments (
    DepartmentID INT PRIMARY KEY IDENTITY(1,1),
    DepartmentName NVARCHAR(100) NOT NULL,
    DepartmentCode NVARCHAR(20) NOT NULL UNIQUE,
    Budget DECIMAL(15,2) NOT NULL DEFAULT 0 CHECK (Budget >= 0),
    ManagerID INT NULL, -- Self-referencing, postaviti nakon kreiranja Employees
    CreatedDate DATETIME2 DEFAULT SYSDATETIME(),
    ModifiedDate DATETIME2 DEFAULT SYSDATETIME()
);
GO

-- =============================================
-- 3. Employees - Zaposlenici
-- =============================================
CREATE TABLE Stats.Employees (
    EmployeeID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    JMBG NVARCHAR(13) NOT NULL UNIQUE, -- Jedinstveni matični broj
    DepartmentID INT NOT NULL,
    Position NVARCHAR(100) NOT NULL,
    Salary DECIMAL(10,2) NOT NULL CHECK (Salary >= 0),
    HireDate DATE NOT NULL,
    Email NVARCHAR(100) NULL,
    CreatedDate DATETIME2 DEFAULT SYSDATETIME(),
    ModifiedDate DATETIME2 DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Employees_Departments 
        FOREIGN KEY (DepartmentID) 
        REFERENCES Stats.Departments(DepartmentID)
        -- 
        -- 
);
GO

-- Dodavanje foreign key za ManagerID u Departments
ALTER TABLE Stats.Departments
ADD CONSTRAINT FK_Departments_Manager
    FOREIGN KEY (ManagerID) 
    REFERENCES Stats.Employees(EmployeeID)
    ON DELETE SET NULL
    ;
GO

-- =============================================
-- 4. Projects - Projekti
-- =============================================
CREATE TABLE Stats.Projects (
    ProjectID INT PRIMARY KEY IDENTITY(1,1),
    ProjectName NVARCHAR(200) NOT NULL,
    DepartmentID INT NOT NULL,
    Budget DECIMAL(15,2) NOT NULL CHECK (Budget >= 0),
    StartDate DATE NOT NULL,
    EndDate DATE NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Planned' 
        CHECK (Status IN ('Planned', 'InProgress', 'Completed', 'Cancelled')),
    Description NVARCHAR(MAX) NULL,
    CreatedDate DATETIME2 DEFAULT SYSDATETIME(),
    ModifiedDate DATETIME2 DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Projects_Departments 
        FOREIGN KEY (DepartmentID) 
        REFERENCES Stats.Departments(DepartmentID)
        
        ,
    CONSTRAINT CK_Projects_Dates 
        CHECK (EndDate IS NULL OR EndDate >= StartDate)
);
GO

-- =============================================
-- 5. EconomicData - Ekonomski podaci po regijama
-- =============================================
CREATE TABLE Stats.EconomicData (
    DataID INT PRIMARY KEY IDENTITY(1,1),
    RegionID INT NOT NULL,
    Year INT NOT NULL CHECK (Year >= 2000 AND Year <= 2100),
    GDP DECIMAL(18,2) NULL CHECK (GDP >= 0),
    UnemploymentRate DECIMAL(5,2) NULL CHECK (UnemploymentRate >= 0 AND UnemploymentRate <= 100),
    AverageSalary DECIMAL(10,2) NULL CHECK (AverageSalary >= 0),
    InflationRate DECIMAL(5,2) NULL,
    RecordedDate DATETIME2 DEFAULT SYSDATETIME(),
    CONSTRAINT FK_EconomicData_Regions 
        FOREIGN KEY (RegionID) 
        REFERENCES Stats.Regions(RegionID)
        ON DELETE CASCADE
        ,
    CONSTRAINT UQ_EconomicData_Region_Year 
        UNIQUE (RegionID, Year)
);
GO

-- =============================================
-- 6. Reports - Izvještaji
-- =============================================
CREATE TABLE Stats.Reports (
    ReportID INT PRIMARY KEY IDENTITY(1,1),
    ReportName NVARCHAR(200) NOT NULL,
    DepartmentID INT NOT NULL,
    CreatedBy INT NOT NULL,
    CreatedDate DATETIME2 DEFAULT SYSDATETIME(),
    Status NVARCHAR(50) NOT NULL DEFAULT 'Draft'
        CHECK (Status IN ('Draft', 'Review', 'Approved', 'Published', 'Archived')),
    ReportType NVARCHAR(50) NOT NULL,
    Description NVARCHAR(MAX) NULL,
    CONSTRAINT FK_Reports_Departments 
        FOREIGN KEY (DepartmentID) 
        REFERENCES Stats.Departments(DepartmentID)
        
        ,
    CONSTRAINT FK_Reports_CreatedBy 
        FOREIGN KEY (CreatedBy) 
        REFERENCES Stats.Employees(EmployeeID)
        
        
);
GO

-- =============================================
-- 7. ReportData - Podaci u izvještajima
-- =============================================
CREATE TABLE Stats.ReportData (
    ReportDataID INT PRIMARY KEY IDENTITY(1,1),
    ReportID INT NOT NULL,
    DataType NVARCHAR(50) NOT NULL,
    Value DECIMAL(18,2) NULL,
    TextValue NVARCHAR(MAX) NULL,
    RegionID INT NULL,
    Year INT NULL,
    CreatedDate DATETIME2 DEFAULT SYSDATETIME(),
    CONSTRAINT FK_ReportData_Reports 
        FOREIGN KEY (ReportID) 
        REFERENCES Stats.Reports(ReportID)
        ON DELETE CASCADE
        ,
    CONSTRAINT FK_ReportData_Regions 
        FOREIGN KEY (RegionID) 
        REFERENCES Stats.Regions(RegionID)
        ON DELETE SET NULL
        
);
GO

-- =============================================
-- Kreiranje Indeksa
-- =============================================

-- Indeksi za Regions
CREATE NONCLUSTERED INDEX IX_Regions_RegionCode 
    ON Stats.Regions(RegionCode);
GO

-- Indeksi za Employees
CREATE NONCLUSTERED INDEX IX_Employees_DepartmentID 
    ON Stats.Employees(DepartmentID);
GO

CREATE NONCLUSTERED INDEX IX_Employees_JMBG 
    ON Stats.Employees(JMBG);
GO

CREATE NONCLUSTERED INDEX IX_Employees_HireDate 
    ON Stats.Employees(HireDate);
GO

-- Indeksi za Projects
CREATE NONCLUSTERED INDEX IX_Projects_DepartmentID 
    ON Stats.Projects(DepartmentID);
GO

CREATE NONCLUSTERED INDEX IX_Projects_Status 
    ON Stats.Projects(Status);
GO

-- Indeksi za EconomicData
CREATE NONCLUSTERED INDEX IX_EconomicData_RegionID 
    ON Stats.EconomicData(RegionID);
GO

CREATE NONCLUSTERED INDEX IX_EconomicData_Year 
    ON Stats.EconomicData(Year);
GO

-- Indeksi za Reports
CREATE NONCLUSTERED INDEX IX_Reports_DepartmentID 
    ON Stats.Reports(DepartmentID);
GO

CREATE NONCLUSTERED INDEX IX_Reports_CreatedBy 
    ON Stats.Reports(CreatedBy);
GO

CREATE NONCLUSTERED INDEX IX_Reports_Status 
    ON Stats.Reports(Status);
GO

-- Indeksi za ReportData
CREATE NONCLUSTERED INDEX IX_ReportData_ReportID 
    ON Stats.ReportData(ReportID);
GO

CREATE NONCLUSTERED INDEX IX_ReportData_RegionID 
    ON Stats.ReportData(RegionID);
GO

-- =============================================
-- INSERT Sample Data - Regions
-- =============================================
INSERT INTO Stats.Regions (RegionName, RegionCode, Population, Area)
VALUES
    ('Federacija Bosne i Hercegovine', 'FBIH', 2200000, 26395.00),
    ('Republika Srpska', 'RS', 1200000, 24857.00),
    ('Brčko Distrikt', 'BD', 83000, 402.00),
    ('Sarajevo', 'SA', 275000, 1415.00),
    ('Banja Luka', 'BL', 185000, 1239.00),
    ('Tuzla', 'TZ', 110000, 302.00),
    ('Mostar', 'MO', 105000, 1175.00),
    ('Zenica', 'ZE', 115000, 558.00);
GO

-- =============================================
-- INSERT Sample Data - Departments
-- =============================================
INSERT INTO Stats.Departments (DepartmentName, DepartmentCode, Budget)
VALUES
    ('Ministarstvo Finansija', 'MF', 50000000.00),
    ('Ministarstvo Obrazovanja', 'MO', 30000000.00),
    ('Ministarstvo Zdravstva', 'MZ', 40000000.00),
    ('Agencija za Statistiku', 'AS', 5000000.00),
    ('Ministarstvo Privrede', 'MP', 20000000.00),
    ('Ministarstvo Poljoprivrede', 'MPP', 15000000.00);
GO

-- =============================================
-- INSERT Sample Data - Employees
-- =============================================
INSERT INTO Stats.Employees (FirstName, LastName, JMBG, DepartmentID, Position, Salary, HireDate, Email)
VALUES
    ('Ahmed', 'Hodžić', '0101950123456', 1, 'Ministar', 5000.00, '2020-01-15', 'ahmed.hodzic@mf.gov.ba'),
    ('Marko', 'Petrović', '1502870234567', 2, 'Ministar', 5000.00, '2019-03-01', 'marko.petrovic@mo.gov.ba'),
    ('Amra', 'Kovačević', '2003900345678', 3, 'Ministar', 5000.00, '2021-06-10', 'amra.kovacevic@mz.gov.ba'),
    ('Nedžad', 'Džananović', '0501850456789', 4, 'Direktor', 4500.00, '2018-01-20', 'nedzad.dzananovic@as.gov.ba'),
    ('Jelena', 'Stojanović', '1202900567890', 4, 'Statističar', 2500.00, '2020-09-01', 'jelena.stojanovic@as.gov.ba'),
    ('Dženan', 'Malić', '0803850678901', 4, 'Statističar', 2500.00, '2021-02-15', 'dzenan.malic@as.gov.ba'),
    ('Marija', 'Nikolić', '2504900789012', 1, 'Finansijski analitičar', 3000.00, '2019-11-05', 'marija.nikolic@mf.gov.ba'),
    ('Haris', 'Bešić', '3001850890123', 1, 'Računovodja', 2200.00, '2022-01-10', 'haris.besic@mf.gov.ba'),
    ('Sanja', 'Jovanović', '1802900901234', 2, 'Koordinator projekata', 2800.00, '2020-05-20', 'sanja.jovanovic@mo.gov.ba'),
    ('Adnan', 'Kurtić', '2203850012345', 3, 'Zdravstveni analitičar', 2700.00, '2021-08-12', 'adnan.kurtic@mz.gov.ba'),
    ('Milica', 'Popović', '1004900123456', 5, 'Ekonomski savjetnik', 3200.00, '2019-04-03', 'milica.popovic@mp.gov.ba'),
    ('Emir', 'Hasanović', '2802850234567', 6, 'Poljoprivredni ekspert', 2600.00, '2020-07-18', 'emir.hasanovic@mpp.gov.ba');
GO

-- Ažuriranje ManagerID u Departments
UPDATE Stats.Departments SET ManagerID = 1 WHERE DepartmentID = 1; -- Ministarstvo Finansija
UPDATE Stats.Departments SET ManagerID = 2 WHERE DepartmentID = 2; -- Ministarstvo Obrazovanja
UPDATE Stats.Departments SET ManagerID = 3 WHERE DepartmentID = 3; -- Ministarstvo Zdravstva
UPDATE Stats.Departments SET ManagerID = 4 WHERE DepartmentID = 4; -- Agencija za Statistiku
UPDATE Stats.Departments SET ManagerID = 11 WHERE DepartmentID = 5; -- Ministarstvo Privrede
UPDATE Stats.Departments SET ManagerID = 12 WHERE DepartmentID = 6; -- Ministarstvo Poljoprivrede
GO

-- =============================================
-- INSERT Sample Data - Projects
-- =============================================
INSERT INTO Stats.Projects (ProjectName, DepartmentID, Budget, StartDate, EndDate, Status, Description)
VALUES
    ('Digitalizacija državne statistike', 4, 2000000.00, '2023-01-01', '2024-12-31', 'InProgress', 'Projekat modernizacije sistema za prikupljanje i obradu statistike'),
    ('Popis stanovništva 2024', 4, 5000000.00, '2024-01-01', '2024-12-31', 'InProgress', 'Nacionalni popis stanovništva'),
    ('Elektronsko zdravstveno kartiranje', 3, 3000000.00, '2023-06-01', '2025-05-31', 'InProgress', 'Digitalizacija zdravstvenih kartona'),
    ('Reforma obrazovnog sistema', 2, 10000000.00, '2022-09-01', '2025-08-31', 'InProgress', 'Kompleksna reforma obrazovnog sistema'),
    ('Poboljšanje fiskalne politike', 1, 5000000.00, '2023-03-01', '2024-02-28', 'Completed', 'Analiza i poboljšanje fiskalnih mehanizama'),
    ('Ruralni razvoj', 6, 8000000.00, '2023-01-15', '2025-01-14', 'InProgress', 'Podrška ruralnom razvoju i poljoprivredi'),
    ('Ekonomski monitoring', 5, 1500000.00, '2024-01-01', '2024-12-31', 'InProgress', 'Praćenje ekonomskih pokazatelja');
GO

-- =============================================
-- INSERT Sample Data - EconomicData
-- =============================================
INSERT INTO Stats.EconomicData (RegionID, Year, GDP, UnemploymentRate, AverageSalary, InflationRate)
VALUES
    -- Federacija BiH
    (1, 2020, 8500000000.00, 18.5, 950.00, 1.2),
    (1, 2021, 9200000000.00, 17.2, 980.00, 2.1),
    (1, 2022, 9800000000.00, 16.8, 1020.00, 14.5),
    (1, 2023, 10500000000.00, 15.5, 1080.00, 5.2),
    -- Republika Srpska
    (2, 2020, 4500000000.00, 19.2, 920.00, 1.5),
    (2, 2021, 4800000000.00, 18.0, 950.00, 2.3),
    (2, 2022, 5100000000.00, 17.5, 1000.00, 15.2),
    (2, 2023, 5400000000.00, 16.8, 1050.00, 5.8),
    -- Brčko Distrikt
    (3, 2020, 320000000.00, 16.8, 1000.00, 1.0),
    (3, 2021, 340000000.00, 15.5, 1020.00, 1.8),
    (3, 2022, 360000000.00, 15.0, 1050.00, 13.5),
    (3, 2023, 380000000.00, 14.5, 1100.00, 4.5),
    -- Sarajevo
    (4, 2020, 2800000000.00, 12.5, 1200.00, 1.2),
    (4, 2021, 3000000000.00, 11.8, 1250.00, 2.0),
    (4, 2022, 3200000000.00, 11.2, 1300.00, 14.0),
    (4, 2023, 3400000000.00, 10.5, 1350.00, 4.8),
    -- Banja Luka
    (5, 2020, 1800000000.00, 14.2, 1100.00, 1.3),
    (5, 2021, 1950000000.00, 13.5, 1150.00, 2.1),
    (5, 2022, 2100000000.00, 13.0, 1200.00, 14.8),
    (5, 2023, 2250000000.00, 12.5, 1250.00, 5.5);
GO

-- =============================================
-- INSERT Sample Data - Reports
-- =============================================
INSERT INTO Stats.Reports (ReportName, DepartmentID, CreatedBy, CreatedDate, Status, ReportType, Description)
VALUES
    ('Godišnji izvještaj o stanovništvu 2023', 4, 4, '2024-01-15', 'Published', 'Annual', 'Kompletan godišnji izvještaj o demografskim pokazateljima'),
    ('Ekonomski pregled Q1 2024', 4, 5, '2024-04-10', 'Approved', 'Quarterly', 'Kvartalni pregled ekonomskih pokazatelja'),
    ('Analiza budžeta 2023', 1, 7, '2024-02-20', 'Published', 'Annual', 'Detaljna analiza izvršenja budžeta'),
    ('Zdravstveni statistički pregled', 3, 10, '2024-03-05', 'Review', 'Annual', 'Statistika zdravstvenih pokazatelja'),
    ('Obrazovni indikatori 2023', 2, 9, '2024-01-30', 'Published', 'Annual', 'Pregled obrazovnih postignuća i indikatora'),
    ('Poljoprivredna statistika', 6, 12, '2024-02-15', 'Approved', 'Annual', 'Godišnji pregled poljoprivredne proizvodnje');
GO

-- =============================================
-- INSERT Sample Data - ReportData
-- =============================================
INSERT INTO Stats.ReportData (ReportID, DataType, Value, TextValue, RegionID, Year)
VALUES
    (1, 'Population', 2200000, NULL, 1, 2023),
    (1, 'Population', 1200000, NULL, 2, 2023),
    (1, 'Population', 83000, NULL, 3, 2023),
    (2, 'GDP', 10500000000.00, NULL, 1, 2024),
    (2, 'GDP', 5400000000.00, NULL, 2, 2024),
    (2, 'UnemploymentRate', 15.5, NULL, 1, 2024),
    (2, 'UnemploymentRate', 16.8, NULL, 2, 2024),
    (3, 'BudgetExecution', 48500000.00, NULL, NULL, 2023),
    (3, 'BudgetVariance', 3.0, NULL, NULL, 2023),
    (4, 'HospitalBeds', 8500, NULL, NULL, 2023),
    (4, 'DoctorsPer1000', 2.1, NULL, NULL, 2023),
    (5, 'Students', 350000, NULL, NULL, 2023),
    (5, 'Schools', 2100, NULL, NULL, 2023),
    (6, 'AgriculturalProduction', 2500000.00, 'tons', NULL, 2023);
GO

-- =============================================
-- Osnovni SELECT Upiti za Verifikaciju
-- =============================================

-- Pregled svih regija
SELECT * FROM Stats.Regions;
GO

-- Pregled zaposlenika po odjeljenjima
SELECT 
    d.DepartmentName,
    e.FirstName + ' ' + e.LastName AS EmployeeName,
    e.Position,
    e.Salary
FROM Stats.Employees e
INNER JOIN Stats.Departments d ON e.DepartmentID = d.DepartmentID
ORDER BY d.DepartmentName, e.LastName;
GO

-- Ekonomski podaci po regijama za 2023
SELECT 
    r.RegionName,
    ed.Year,
    ed.GDP,
    ed.UnemploymentRate,
    ed.AverageSalary
FROM Stats.EconomicData ed
INNER JOIN Stats.Regions r ON ed.RegionID = r.RegionID
WHERE ed.Year = 2023
ORDER BY ed.GDP DESC;
GO

-- Projekti po odjeljenjima
SELECT 
    d.DepartmentName,
    p.ProjectName,
    p.Budget,
    p.Status,
    p.StartDate,
    p.EndDate
FROM Stats.Projects p
INNER JOIN Stats.Departments d ON p.DepartmentID = d.DepartmentID
ORDER BY d.DepartmentName, p.StartDate;
GO

-- Izvještaji sa informacijama o kreatoru
SELECT 
    r.ReportName,
    d.DepartmentName,
    e.FirstName + ' ' + e.LastName AS CreatedBy,
    r.CreatedDate,
    r.Status,
    r.ReportType
FROM Stats.Reports r
INNER JOIN Stats.Departments d ON r.DepartmentID = d.DepartmentID
INNER JOIN Stats.Employees e ON r.CreatedBy = e.EmployeeID
ORDER BY r.CreatedDate DESC;
GO

PRINT 'StateStatisticsDB je uspješno kreiran sa svim tabelama i podacima!';
GO
