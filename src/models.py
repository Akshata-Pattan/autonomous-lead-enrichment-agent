from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    name: str
    role: str
    linkedin_url: str | None = None


class CompanyIntelligence(BaseModel):
    domain: str
    company_overview: str
    target_audience: str
    contact_points: list[str] = Field(default_factory=list)
    leadership: list[TeamMember] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)