"""Entity SEO signals: Organization/Person consistency from JSON-LD and visible cues."""

from __future__ import annotations

import re
from typing import Any

from seoforge.models import AnalyzerScore, Finding

NAP_PHONE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
NAP_EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
SAME_AS_HINT = re.compile(
    r"sameAs|linkedin\.com|facebook\.com|twitter\.com|x\.com|instagram\.com", re.I
)


def _jsonld_entities(page: dict[str, Any]) -> list[dict[str, Any]]:
    data = page.get("data") or {}
    blocks = data.get("jsonld") or data.get("schema") or []
    entities: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if not isinstance(node, dict):
            return
        types = node.get("@type", [])
        if isinstance(types, str):
            types = [types]
        if any(
            str(t).lower() in {"organization", "localbusiness", "person", "corporation"}
            for t in types
        ):
            entities.append(node)
        for value in node.values():
            if isinstance(value, (dict, list)):
                walk(value)

    for block in blocks:
        walk(block)
    return entities


def analyze_pages(pages: list[dict[str, Any]]) -> AnalyzerScore:
    findings: list[Finding] = []
    usable = 0
    org_pages = 0
    person_pages = 0
    same_as_pages = 0
    nap_pages = 0
    names: set[str] = set()
    phones: set[str] = set()

    for page in pages:
        if page.get("error") or int(page.get("status") or 0) >= 400:
            continue
        usable += 1
        text = str((page.get("data") or {}).get("text") or "")
        entities = _jsonld_entities(page)
        types = []
        for entity in entities:
            t = entity.get("@type")
            types.extend([t] if isinstance(t, str) else list(t or []))
            name = entity.get("name")
            if isinstance(name, str) and name.strip():
                names.add(name.strip())
            if entity.get("sameAs"):
                same_as_pages += 1
            phone = entity.get("telephone")
            if isinstance(phone, str):
                phones.add(re.sub(r"\s+", " ", phone.strip()))
        lower_types = {str(t).lower() for t in types}
        if lower_types & {"organization", "localbusiness", "corporation"}:
            org_pages += 1
        if "person" in lower_types:
            person_pages += 1
        if NAP_PHONE.search(text) or NAP_EMAIL.search(text):
            nap_pages += 1
            for match in NAP_PHONE.findall(text):
                phones.add(re.sub(r"\s+", " ", match.strip()))
        if SAME_AS_HINT.search(text) or same_as_pages:
            pass

    if usable == 0:
        return AnalyzerScore(
            name="entity",
            score=0.0,
            confidence="insufficient_evidence",
            notes=["No usable HTML pages to score for entity consistency."],
        )

    score = round(
        100
        * (
            0.35 * min(1.0, (org_pages / usable) * 3)
            + 0.20 * min(1.0, (person_pages / usable) * 4)
            + 0.25 * min(1.0, (nap_pages / usable) * 2)
            + 0.20 * (1.0 if len(names) <= 2 else 0.4)
        ),
        1,
    )

    if org_pages == 0:
        findings.append(
            Finding(
                code="entity_missing_organization",
                priority="medium",
                observation="No Organization/LocalBusiness JSON-LD entity was detected in this sample.",
                affected_urls=[p.get("url", "") for p in pages if p.get("url")][:3],
                recommended_action="Publish consistent Organization markup with name, url, and contact points.",
                acceptance_check="Recrawl homepage/about and confirm Organization @type in JSON-LD.",
                claim_type="inference",
                why_it_matters="Clear entity identity helps search and answer systems ground the brand.",
                uncertainty="Absence claims require complete captures of intended identity pages.",
                score_component="entity",
            )
        )
    if len(names) > 2:
        findings.append(
            Finding(
                code="entity_name_inconsistency",
                priority="low",
                observation=f"Multiple organization/person names observed in structured data: {sorted(names)[:5]}",
                affected_urls=[p.get("url", "") for p in pages if p.get("url")][:3],
                recommended_action="Align legal/brand names across Organization markup and visible NAP.",
                acceptance_check="Confirm a single preferred name across homepage, about, and schema.",
                claim_type="inference",
                why_it_matters="Conflicting names weaken entity resolution.",
                uncertainty="Abbreviations and product names can be legitimate variants.",
                score_component="entity",
            )
        )

    return AnalyzerScore(
        name="entity",
        score=score,
        confidence="heuristic",
        signals={
            "usable_pages": usable,
            "pages_with_organization_schema": org_pages,
            "pages_with_person_schema": person_pages,
            "pages_with_nap_cues": nap_pages,
            "pages_with_sameAs": same_as_pages,
            "distinct_names": sorted(names)[:10],
            "distinct_phones_sampled": sorted(phones)[:8],
        },
        findings=findings,
        notes=["Entity score reflects consistency cues in this crawl sample only."],
    )
