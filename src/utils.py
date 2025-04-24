from pydantic import BaseModel
from typing import List, Optional
import re


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


def sanitize_company_name(company_name: Optional[str]):
    if company_name is None:
        return None
    company_name = company_name.strip()
    suffixes = r"\s+((Pvt\.?|Private)?\s*Ltd\.?|LLC|Inc\.?|Limited|Corp\.?|Corporation|Co\.?|Company|LLP|LP|PLC|SA|S\.A\.?|GmbH|AG|KG|SE|SRL|Pty\.?|Pvt\.?|Pte\.?|NV|BV|CV|SAS|SPA|OY|AS|AB|JSC|PJSC|ULC|PC)\.?$"
    standardized = re.sub(suffixes, "", company_name, flags=re.IGNORECASE)
    standardized = re.sub(r",?\s*$", "", standardized)
    print(f"Standardized company name: {standardized}")
    return standardized.strip()
