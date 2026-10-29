"""Run SeoForge analyzers over crawl evidence and merge findings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from seoforge.analyze import aeo, entity, geo
from seoforge.analyze.review import read_pages
from seoforge.crawl.engine import write_json
from seoforge.models import AnalyzerScore


def run_analyzers(crawl_dir: Path) -> dict[str, AnalyzerScore]:
    pages = read_pages(crawl_dir)
    return {
        "aeo": aeo.analyze_pages(pages),
        "geo": geo.analyze_pages(pages),
        "entity": entity.analyze_pages(pages),
    }


def export_analysis(crawl_dir: Path, out: Path) -> dict[str, Any]:
    scores = run_analyzers(crawl_dir)
    payload = {
        "crawl": str(crawl_dir),
        "scores": {name: score.to_dict() for name, score in scores.items()},
        "composite": {
            "aeo": scores["aeo"].score,
            "geo": scores["geo"].score,
            "entity": scores["entity"].score,
            "note": "Composite values are independent heuristics, not a ranking prediction.",
        },
    }
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "analysis.json", payload)
    return payload


def merge_analyzer_findings(audit: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    extra = []
    for score in (analysis.get("scores") or {}).values():
        for finding in score.get("findings") or []:
            extra.append(
                {
                    **finding,
                    "priority": finding.get("priority", "medium"),
                    "claim_type": finding.get("claim_type", "inference"),
                    "why_it_matters": finding.get("why_it_matters", ""),
                    "acceptance_check": finding.get("acceptance_check", ""),
                    "uncertainty": finding.get("uncertainty", ""),
                    "recommended_action": finding.get("recommended_action", ""),
                    "evidence_refs": [],
                    "captured_at": [],
                }
            )
    audit = dict(audit)
    audit["findings"] = list(audit.get("findings") or []) + extra
    audit["analysis"] = analysis.get("composite")
    return audit
