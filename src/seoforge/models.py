"""Typed public models for SeoForge observations and reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Priority = Literal["high", "medium", "low"]
ClaimType = Literal["verified_fact", "inference", "hypothesis"]


@dataclass
class CoverageReport:
    inspected: int = 0
    partial: int = 0
    failed: int = 0
    pending: int = 0
    html_documents: int = 0
    seed: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_summary(cls, summary: dict[str, Any]) -> CoverageReport:
        coverage = summary.get("coverage") or {}
        return cls(
            inspected=int(coverage.get("inspected", summary.get("html_documents", 0) or 0)),
            partial=int(coverage.get("partial", 0) or 0),
            failed=int(coverage.get("failed", 0) or 0),
            pending=int(coverage.get("pending", 0) or 0),
            html_documents=int(summary.get("html_documents", 0) or 0),
            seed=str(summary.get("seed", "")),
            raw=summary,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Finding:
    code: str
    priority: Priority | str
    observation: str
    affected_urls: list[str] = field(default_factory=list)
    recommended_action: str = ""
    acceptance_check: str = ""
    claim_type: ClaimType | str = "inference"
    why_it_matters: str = ""
    uncertainty: str = ""
    score_component: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_audit_row(cls, row: dict[str, Any]) -> Finding:
        return cls(
            code=str(row.get("code", "finding")),
            priority=row.get("priority", "medium"),
            observation=str(row.get("observation", "")),
            affected_urls=list(row.get("affected_urls") or []),
            recommended_action=str(row.get("recommended_action", "")),
            acceptance_check=str(row.get("acceptance_check", "")),
            claim_type=row.get("claim_type", "inference"),
            why_it_matters=str(row.get("why_it_matters", "")),
            uncertainty=str(row.get("uncertainty", "")),
            raw=row,
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("raw", None)
        return data


@dataclass
class PageObservation:
    url: str
    status: int = 0
    title: str = ""
    word_count: int = 0
    h1: list[str] = field(default_factory=list)
    schema_types: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("raw", None)
        return data


@dataclass
class AnalyzerScore:
    name: str
    score: float
    max_score: float = 100.0
    confidence: str = "heuristic"
    signals: dict[str, Any] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "max_score": self.max_score,
            "confidence": self.confidence,
            "signals": self.signals,
            "findings": [f.to_dict() for f in self.findings],
            "notes": self.notes,
        }


@dataclass
class CompetitorComparison:
    target: str
    competitors: list[str] = field(default_factory=list)
    matrix: list[dict[str, Any]] = field(default_factory=list)
    gaps: list[Finding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "competitors": self.competitors,
            "matrix": self.matrix,
            "gaps": [f.to_dict() for f in self.gaps],
            "notes": self.notes,
        }
