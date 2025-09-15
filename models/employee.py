from __future__ import annotations

from typing import Optional, List, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, StringConstraints

from .company import CompanyRead

# Custom Employee ID — 2–3 uppercase letters + 3–5 digits (e.g., AD123, JDS45678)
EmployeeIDType = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2,3}\d{3,5}$")]


class EmployeeBase(BaseModel):
    employee_id: EmployeeIDType = Field(
        ...,
        description="Unique employee ID (2–3 uppercase letters followed by 3–5 digits).",
        json_schema_extra={"example": "AD123"},
    )
    first_name: str = Field(
        ...,
        description="Given name.",
        json_schema_extra={"example": "Ada"},
    )
    last_name: str = Field(
        ...,
        description="Family name.",
        json_schema_extra={"example": "Lovelace"},
    )
    email: EmailStr = Field(
        ...,
        description="Primary email address.",
        json_schema_extra={"example": "ada@example.com"},
    )
    phone: str = Field(
        ...,
        description="Contact phone number in any reasonable format.",
        json_schema_extra={"example": "+1-212-555-0199"},
    )
    birth_date: Optional[date] = Field(
        None,
        description="Date of birth (YYYY-MM-DD).",
        json_schema_extra={"example": "1815-12-10"},
    )
    department: str = Field(
        ...,
        description="Employee's department.",
        json_schema_extra={"example": "Software Engineering"},
    )
    team: str = Field(
        ...,
        description="Employee's team.",
        json_schema_extra={"example": "Bill Automation"},
    )
    yearsofexp: int = Field(
        ...,
        description="Years of experience.",
        json_schema_extra={"example": 4},
    )
    companies: Optional[List[CompanyRead]] = Field(
        None,
        description="Companies linked to this employee.",
        json_schema_extra={
            "example": [
                {
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "name": "Acme Corp",
                    "website": "https://acme.com",
                    "industry": "Banking",
                    "founded": "1999-04-01",
                    "size": "51-200 employees",
                }
            ]
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "employee_id": "AD123",
                    "first_name": "Ada",
                    "last_name": "Lovelace",
                    "email": "ada@example.com",
                    "phone": "+1-212-555-0199",
                    "birth_date": "1815-12-10",
                    "department": "Software Engineering",
                    "team": "Bill Automation",
                    "yearsofexp": 4,
                    "companies": [
                        {
                            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "name": "Acme Corp",
                            "website": "https://acme.com",
                            "industry": "Banking",
                            "founded": "1999-04-01",
                            "size": "51-200 employees",
                        }
                    ],
                }
            ]
        }
    }


class EmployeeCreate(EmployeeBase):
    """Creation payload for an Employee."""
    company_ids: List[UUID] = Field(
        ..., description="List of company UUIDs this employee is associated with."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "employee_id": "JD567",
                    "first_name": "Grace",
                    "last_name": "Hopper",
                    "email": "grace.hopper@navy.mil",
                    "phone": "+1-202-555-0101",
                    "birth_date": "1906-12-09",
                    "department": "Human Resources",
                    "team": "University Recruiting",
                    "yearsofexp": 10,
                    "company_ids": [
                        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
                    ]
                }
            ]
        }
    }


class EmployeeUpdate(BaseModel):
    """Partial update for an Employee; supply only fields to change."""
    employee_id: Optional[EmployeeIDType] = Field(
        None, description="Employee ID.", json_schema_extra={"example": "JD567"}
    )
    first_name: Optional[str] = Field(None, json_schema_extra={"example": "Bill"})
    last_name: Optional[str] = Field(None, json_schema_extra={"example": "Chen"})
    email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "bill.chen@example.com"})
    phone: Optional[str] = Field(None, json_schema_extra={"example": "+1 212 323 1231"})
    birth_date: Optional[date] = Field(None, json_schema_extra={"example": "1990-01-01"})
    department: Optional[str] = Field(None, json_schema_extra={"example": "Engineering"})
    team: Optional[str] = Field(None, json_schema_extra={"example": "Core Infra"})
    yearsofexp: Optional[int] = Field(None, json_schema_extra={"example": 6})
    company_ids: Optional[List[UUID]] = Field(
        None,
        description="Updated list of company UUIDs.",
        json_schema_extra={"example": ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"]}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"first_name": "Alan", "last_name": "Turing"},
                {"email": "alan.turing@bletchley.gov.uk"},
                {"company_ids": ["bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"]}
            ]
        }
    }


class EmployeeRead(EmployeeBase):
    """Server representation of an Employee returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated employee UUID.",
        json_schema_extra={"example": "99999999-9999-4999-8999-999999999999"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )
    companies: List[CompanyRead] = Field(
        default_factory=list,
        description="Full company details associated with the employee.",
        json_schema_extra={
            "example": [
                {
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "name": "Acme Corp",
                    "website": "https://acme.com",
                    "industry": "Banking",
                    "founded": "1999-04-01",
                    "size": "51-200 employees",
                }
            ]
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "99999999-9999-4999-8999-999999999999",
                    "employee_id": "AD123",
                    "first_name": "Ada",
                    "last_name": "Lovelace",
                    "email": "ada@example.com",
                    "phone": "+1-212-555-0199",
                    "birth_date": "1815-12-10",
                    "department": "Software Engineering",
                    "team": "Bill Automation",
                    "yearsofexp": 4,
                    "companies": [
                        {
                            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "name": "Acme Corp",
                            "website": "https://acme.com",
                            "industry": "Banking",
                            "founded": "1999-04-01",
                            "size": "51-200 employees",
                        }
                    ],
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
