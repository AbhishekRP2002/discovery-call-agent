from pydantic import BaseModel
from typing import List, Optional


class ProspectContactInfo(BaseModel):
    first_name: str
    last_name: Optional[str]
    email: str
    phone: Optional[str]
    company_name: Optional[str]
    company_domain: str
    job_title: Optional[str]
    linkedin: Optional[str]


class ProspectAccountInfo(BaseModel):
    company_name: str
    company_domain: str
    company_summary: Optional[str]
    industry: Optional[str]
    pain_points: Optional[List[str]]


class SellerAccountInfo(BaseModel):
    company_name: str
    company_domain: str
    company_summary: Optional[str]
    industry: Optional[str]
    pain_points: Optional[List[str]]
