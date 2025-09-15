from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Path

from models.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from models.company import CompanyCreate, CompanyRead, CompanyUpdate
from models.health import Health

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
employees: Dict[UUID, EmployeeRead] = {}
companies: Dict[UUID, CompanyRead] = {}

app = FastAPI(
    title="Employee/Company API",
    description="Demo FastAPI app using Pydantic v2 models for Employee and Company",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Company endpoints
# -----------------------------------------------------------------------------

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/companies", response_model=CompanyRead, status_code=201)
def create_company(company: CompanyCreate):
    company_read = CompanyRead(**company.model_dump())
    if company_read.id in companies:
        raise HTTPException(status_code=400, detail="Company with this ID already exists")
    companies[company_read.id] = company_read
    return company_read

@app.get("/companies", response_model=List[CompanyRead])
def list_companies(
    name: Optional[str] = Query(None, description="Filter by company name"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    size: Optional[str] = Query(None, description="Filter by company size"),
):
    results = list(companies.values())
    if name is not None:
        results = [c for c in results if c.name == name]
    if industry is not None:
        results = [c for c in results if c.industry == industry]
    if size is not None:
        results = [c for c in results if c.size == size]
    return results

@app.get("/companies/{company_id}", response_model=CompanyRead)
def get_company(company_id: UUID):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")
    return companies[company_id]

@app.patch("/companies/{company_id}", response_model=CompanyRead)
def update_company(company_id: UUID, update: CompanyUpdate):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")
    stored = companies[company_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    companies[company_id] = CompanyRead(**stored)
    return companies[company_id]

@app.put("/companies/{company_id}", response_model=CompanyRead)
def replace_company(company_id: UUID, company: CompanyCreate):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    # Ensure the ID from path is used, ignoring any ID in the body if present
    company_data = company.model_dump()
    company_data["id"] = company_id

    company_read = CompanyRead(**company_data)
    companies[company_id] = company_read

    return company_read

@app.delete("/companies/{company_id}", status_code=204)
def delete_company(company_id: UUID):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")
    # Remove company from any employees' companies list
    for emp_id, emp in employees.items():
        updated_companies = [c for c in emp.companies if c.id != company_id]
        if len(updated_companies) != len(emp.companies):
            emp_dict = emp.model_dump()
            emp_dict["companies"] = updated_companies
            employees[emp_id] = EmployeeRead(**emp_dict)
    del companies[company_id]
    return


# -----------------------------------------------------------------------------
# Employee endpoints
# -----------------------------------------------------------------------------
@app.post("/employees", response_model=EmployeeRead, status_code=201)
def create_employee(employee: EmployeeCreate):
    # Validate company_ids exist before creating employee
    for company_id in employee.company_ids:
        if company_id not in companies:
            raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    # Prepare list of CompanyRead objects for this employee
    linked_companies = [companies[cid] for cid in employee.company_ids]

    # Safely get the dict, and remove "companies" if present
    employee_data = employee.model_dump(exclude={"company_ids"})
    employee_data.pop("companies", None) 

    employee_read = EmployeeRead(**employee_data, companies=linked_companies)

    if employee_read.id in employees:
        raise HTTPException(status_code=400, detail="Employee with this ID already exists")

    employees[employee_read.id] = employee_read
    return employee_read

@app.get("/employees", response_model=List[EmployeeRead])
def list_employees(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    department: Optional[str] = Query(None, description="Filter by department"),
    team: Optional[str] = Query(None, description="Filter by team"),
    min_years_of_exp: Optional[int] = Query(None, description="Filter by minimum years of experience"),
    company_name: Optional[str] = Query(None, description="Filter by company name associated with employee"),
):
    results = list(employees.values())

    if employee_id is not None:
        results = [e for e in results if e.employee_id == employee_id]
    if first_name is not None:
        results = [e for e in results if e.first_name == first_name]
    if last_name is not None:
        results = [e for e in results if e.last_name == last_name]
    if email is not None:
        results = [e for e in results if e.email == email]
    if phone is not None:
        results = [e for e in results if e.phone == phone]
    if department is not None:
        results = [e for e in results if e.department == department]
    if team is not None:
        results = [e for e in results if e.team == team]
    if min_years_of_exp is not None:
        results = [e for e in results if e.yearsofexp >= min_years_of_exp]
    if company_name is not None:
        results = [e for e in results if any(c.name == company_name for c in e.companies)]

    return results

@app.get("/employees/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: UUID):
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employees[employee_id]

@app.patch("/employees/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: UUID, update: EmployeeUpdate):
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")

    stored = employees[employee_id].model_dump()

    update_data = update.model_dump(exclude_unset=True)

    # If company_ids are updated, validate and update linked companies
    if "company_ids" in update_data:
        new_company_ids = update_data.pop("company_ids")
        for cid in new_company_ids:
            if cid not in companies:
                raise HTTPException(status_code=404, detail=f"Company {cid} not found")
        linked_companies = [companies[cid] for cid in new_company_ids]
        stored["companies"] = linked_companies

    stored.update(update_data)
    employees[employee_id] = EmployeeRead(**stored)
    return employees[employee_id]

@app.put("/employees/{employee_id}", response_model=EmployeeRead)
def replace_employee(employee_id: UUID, employee: EmployeeCreate):
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")

    for company_id in employee.company_ids:
        if company_id not in companies:
            raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    linked_companies = [companies[cid] for cid in employee.company_ids]

    # Dump data and remove keys that will be passed explicitly
    employee_data = employee.model_dump(exclude={"company_ids"})
    employee_data.pop("id", None)         # Remove if it exists
    employee_data.pop("companies", None)  # Just in case

    # Reconstruct with new id and linked companies
    employee_read = EmployeeRead(id=employee_id, **employee_data, companies=linked_companies)

    employees[employee_id] = employee_read
    return employee_read

@app.delete("/employees/{employee_id}", status_code=204)
def delete_employee(employee_id: UUID):
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    del employees[employee_id]
    return

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Person/Address API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
