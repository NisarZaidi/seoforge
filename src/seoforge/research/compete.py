"""Competitor matrix helpers from crawled inventories."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from seoforge.analyze.review import read_pages
from seoforge.crawl.engine import write_json
from seoforge.models import CompetitorComparison, Finding


def _inventory(pages: list[dict[str, Any]]) -> dict[str, Any]:
    titles = []
    schema = set()
    words = 0
    internal = 0
    for page in pages:
        if page.get("error") or int(page.get("status") or 0) >= 400:
            continue
        data = page.get("data") or {}
        titles.append(data.get("title") or page.get("url"))
        words += int(data.get("word_count") or 0)
        for block in data.get("jsonld") or []:
            if isinstance(block, dict):
                t = block.get("@type")
                if isinstance(t, list):
                    schema.update(str(x) for x in t)
                elif t:
                    schema.add(str(t))
        links = data.get("links") or []
        internal += sum(1 for _ in links)
    return {
        "pages": len(pages),
        "titles": [t for t in titles if t][:40],
        "schema_types": sorted(schema),
        "word_count_total": words,
        "link_mentions": internal,
    }


def build_matrix(target_crawl: Path, competitor_crawls: list[Path]) -> CompetitorComparison:
    target_pages = read_pages(target_crawl)
    target_inv = _inventory(target_pages)
    seed = ""
    summary_path = Path(target_crawl) / "summary.json"
    if summary_path.is_file():
        import json

        seed = json.loads(summary_path.read_text(encoding="utf-8")).get("seed", "")
    rows = []
    gaps: list[Finding] = []
    competitor_hosts = []
    target_titles = {str(t).lower() for t in target_inv["titles"]}
    target_schema = set(target_inv["schema_types"])

    for crawl in competitor_crawls:
        pages = read_pages(crawl)
        inv = _inventory(pages)
        summary = Path(crawl) / "summary.json"
        competitor_seed = str(crawl)
        if summary.is_file():
            import json

            competitor_seed = json.loads(summary.read_text(encoding="utf-8")).get("seed", str(crawl))
        competitor_hosts.append(competitor_seed)
        missing_titles = [
            t for t in inv["titles"] if t and str(t).lower() not in target_titles
        ][:8]
        missing_schema = sorted(set(inv["schema_types"]) - target_schema)
        rows.append(
            {
                "competitor": competitor_seed,
                "pages": inv["pages"],
                "word_count_total": inv["word_count_total"],
                "schema_types": inv["schema_types"],
                "title_gaps_vs_target": missing_titles,
                "schema_gaps_vs_target": missing_schema,
                "link_mentions": inv["link_mentions"],
            }
        )
        if missing_titles:
            gaps.append(
                Finding(
                    code="competitor_content_gap",
                    priority="medium",
                    observation=f"Competitor exposes titles/topics not seen on target: {missing_titles[:3]}",
                    affected_urls=[seed] if seed else [],
                    recommended_action="Review whether equivalent service/support pages are needed on the target site.",
                    acceptance_check="Map each gap to keep/skip with business rationale after manual review.",
                    claim_type="hypothesis",
                    why_it_matters="Content gaps can explain missing query coverage.",
                    uncertainty="Title overlap is a coarse proxy; intent matching needs human review.",
                )
            )
        if missing_schema:
            gaps.append(
                Finding(
                    code="competitor_schema_gap",
                    priority="low",
                    observation=f"Competitor declares schema types absent on target: {missing_schema[:6]}",
                    affected_urls=[seed] if seed else [],
                    recommended_action="Only add schema that matches visible content on the target site.",
                    acceptance_check="Validate new JSON-LD against visible entities.",
                    claim_type="inference",
                    why_it_matters="Structured data gaps can limit entity clarity.",
                    uncertainty="Schema volume is not a quality ranking signal by itself.",
                )
            )
    return CompetitorComparison(
        target=seed or str(target_crawl),
        competitors=competitor_hosts,
        matrix=rows,
        gaps=gaps,
        notes=[
            "Matrix compares crawled inventories only; rankings and traffic are not inferred.",
            f"Target inventory pages={target_inv['pages']} words={target_inv['word_count_total']}",
        ],
    )


def export_comparison(target_crawl: Path, competitor_crawls: list[Path], out: Path) -> dict:
    comparison = build_matrix(target_crawl, competitor_crawls)
    payload = comparison.to_dict()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "competitor-matrix.json", payload)
    return payload
