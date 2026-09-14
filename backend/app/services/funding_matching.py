from dataclasses import dataclass

from app.models.funding_opportunity import FundingOpportunity
from app.models.project import Project, ProjectStatus

PROJECT_TYPE_POINTS = 40
COUNTRY_POINTS = 35
STAGE_POINTS = 25

_STAGE_BY_STATUS: dict[ProjectStatus, str] = {
    ProjectStatus.IDEA: "DEVELOPMENT",
    ProjectStatus.DEVELOPMENT: "DEVELOPMENT",
    ProjectStatus.WRITING: "DEVELOPMENT",
    ProjectStatus.PRE_PRODUCTION: "PRODUCTION",
    ProjectStatus.PRODUCTION: "PRODUCTION",
    ProjectStatus.POST_PRODUCTION: "POST_PRODUCTION",
    ProjectStatus.COMPLETED: "DISTRIBUTION",
}


def project_funding_stage(project: Project) -> str:
    return _STAGE_BY_STATUS[project.status]


@dataclass
class MatchResult:
    score: int
    project_type_match: bool
    country_match: bool
    stage_match: bool


def score_match(project: Project, opportunity: FundingOpportunity) -> MatchResult:
    """Deterministic, rule-based score — no AI involved. Every point is
    tied to a criterion the UI can display, per the project's "score
    explicable" requirement. An empty eligibility list on the
    opportunity means "no known restriction", which always matches; an
    unset project field (e.g. no country) never matches a restricted
    list, since we can't verify a fit we don't have data for.
    """
    project_type_match = (
        not opportunity.eligible_project_types
        or project.project_type.value in opportunity.eligible_project_types
    )
    country_match = not opportunity.eligible_countries or (
        bool(project.country)
        and project.country.strip().casefold()
        in {c.casefold() for c in opportunity.eligible_countries}
    )
    stage_match = (
        not opportunity.eligible_stages
        or project_funding_stage(project) in opportunity.eligible_stages
    )

    score = (
        (PROJECT_TYPE_POINTS if project_type_match else 0)
        + (COUNTRY_POINTS if country_match else 0)
        + (STAGE_POINTS if stage_match else 0)
    )
    return MatchResult(
        score=score,
        project_type_match=project_type_match,
        country_match=country_match,
        stage_match=stage_match,
    )
