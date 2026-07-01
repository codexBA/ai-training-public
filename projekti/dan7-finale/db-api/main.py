from fastapi import FastAPI, HTTPException
from database import get_db_connection
from typing import List, Optional
from pydantic import BaseModel
import pyodbc

app = FastAPI(
    title="State Statistics DB API",
    description="API za pristup podacima državne statistike",
    version="1.0.0"
)

# Modeli za Pydantic
class Department(BaseModel):
    DepartmentID: int
    DepartmentName: str
    DepartmentCode: str
    Budget: float

class Employee(BaseModel):
    EmployeeID: int
    FirstName: str
    LastName: str
    DepartmentName: str
    Position: str

class EconomicData(BaseModel):
    RegionName: str
    Year: int
    GDP: Optional[float]
    UnemploymentRate: Optional[float]
    AverageSalary: Optional[float]

@app.get("/api/departments", response_model=List[Department])
def get_departments():
    """Vraća sva odjeljenja/ministarstva"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DepartmentID, DepartmentName, DepartmentCode, Budget FROM Stats.Departments")
    
    departments = []
    for row in cursor.fetchall():
        departments.append({
            "DepartmentID": row[0],
            "DepartmentName": row[1],
            "DepartmentCode": row[2],
            "Budget": float(row[3])
        })
    conn.close()
    return departments

@app.get("/api/employees/search", response_model=List[Employee])
def search_employees(name: str):
    """Pretražuje zaposlenike po imenu ili prezimenu i vraća gdje rade"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT e.EmployeeID, e.FirstName, e.LastName, d.DepartmentName, e.Position 
    FROM Stats.Employees e
    INNER JOIN Stats.Departments d ON e.DepartmentID = d.DepartmentID
    WHERE e.FirstName LIKE ? OR e.LastName LIKE ?
    """
    search_term = f"%{name}%"
    cursor.execute(query, (search_term, search_term))
    
    employees = []
    for row in cursor.fetchall():
        employees.append({
            "EmployeeID": row[0],
            "FirstName": row[1],
            "LastName": row[2],
            "DepartmentName": row[3],
            "Position": row[4]
        })
    conn.close()
    return employees

@app.get("/api/economic-data", response_model=List[EconomicData])
def get_economic_data(year: int):
    """Vraća ekonomske podatke za traženu godinu po regijama"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT r.RegionName, ed.Year, ed.GDP, ed.UnemploymentRate, ed.AverageSalary
    FROM Stats.EconomicData ed
    INNER JOIN Stats.Regions r ON ed.RegionID = r.RegionID
    WHERE ed.Year = ?
    """
    cursor.execute(query, (year,))
    
    data = []
    for row in cursor.fetchall():
        data.append({
            "RegionName": row[0],
            "Year": row[1],
            "GDP": float(row[2]) if row[2] else None,
            "UnemploymentRate": float(row[3]) if row[3] else None,
            "AverageSalary": float(row[4]) if row[4] else None
        })
    conn.close()
    return data

@app.get("/api/projects/budget")
def get_project_budget(department_code: str):
    """Vraća ukupan budžet svih projekata za određeni kod odjeljenja (npr. 'MF', 'MO')"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT SUM(p.Budget)
    FROM Stats.Projects p
    INNER JOIN Stats.Departments d ON p.DepartmentID = d.DepartmentID
    WHERE d.DepartmentCode = ?
    """
    cursor.execute(query, (department_code,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0]:
        return {"department_code": department_code, "total_projects_budget": float(row[0])}
    return {"department_code": department_code, "total_projects_budget": 0.0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
