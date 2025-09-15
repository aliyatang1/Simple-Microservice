from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, date
from pydantic import BaseModel, Field, AnyUrl

class CompanyBase(BaseModel):
    name: str = Field(
        ...,
        description="Registered name of the company.",
        example="Acme Corp"
    )
    website: Optional[AnyUrl] = Field(
        None,
        description="Company website.",
        example="https://acme.com"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry sector.",
        example="Banking"
    )
    founded: Optional[date] = Field(
        None,
        description="Date the company was founded.",
        example="1999-04-01"
    )
    size: Optional[str] = Field(
        None,
        description="Company size category.",
        example="51-200 employees"
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Acme Corp",
                    "website": "https://acme.com",
                    "industry": "Banking",
                    "founded": "1999-04-01",
                    "size": "51-200 employees"
                }
            ]
        }
    }



class CompanyCreate(CompanyBase):
    """Payload to create a new company."""
    model_config = CompanyBase.model_config


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        description="Registered name of the company.",
        example="Acme Corp"
    )
    website: Optional[AnyUrl] = Field(
        None,
        description="Company website.",
        example="https://acme.com"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry sector.",
        example="Banking"
    )
    founded: Optional[date] = Field(
        None,
        description="Date the company was founded.",
        example="1999-04-01"
    )
    size: Optional[str] = Field(
        None,
        description="Company size category.",
        example="51-200 employees"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Acme Corp",
                    "industry": "Fintech",
                    "website": "https://acme.com",
                    "founded": "2000-01-01",
                    "size": "51-200 employees"
                },
                {
                    "name": "Globex Inc.",
                    "size": "500+ employees"
                }
            ]
        }
    }


class CompanyRead(CompanyBase):
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique company identifier.",
        json_schema_extra={"example": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "name": "Acme Corp",
                "website": "https://acme.com",
                "industry": "Banking",
                "founded": "1999-04-01",
                "size": "51-200 employees",
                "created_at": "2025-01-01T10:00:00Z",
                "updated_at": "2025-09-01T12:00:00Z"
            }
        }
    }