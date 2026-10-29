"""Generative Engine Optimization / citation-readiness signals."""

from __future__ import annotations

import re
from typing import Any

from seoforge.models import AnalyzerScore, Finding

CLAIM_RE = re.compile(
    r"\b(\d+%|\d{4}|according to|research shows|we (found|measured|tested)|studies? (show|suggest))\b",
    re.I,
)
PROOF_RE = re.compile(
    r"\b(case study|customer|client|testimonial|source|citation|published|updated|last (updated|reviewed))\b",
    re.I,
)
DATE_RE = re.compile(
    r"\b(20\d{2}|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b",
    re.I,
)
QUOTABLE_RE = re.compile(r"(^|\n)\s*([A-Z][^.!?\n]{40,160}[.!?])", re.M)


def _body(page: dict[str, Any]) -> str:
    data = page.get("data") or {}
    return str(data.get("text") or data.get("main_text") or "")


def analyze_pages(pages: list[dict[str, Any]]) -> AnalyzerScore:
    findings: list[Finding] = []
    usable = 0
    claim_pages = 0
    proof_pages = 0
    fresh_pages = 0
    quotable_count = 0
    external_link_pages = 0

    for page in pages:
        if page.get("error") or int(page.get("status") or 0) >= 400:
            continue
        usable += 1
        text = _body(page)
        data = page.get("data") or {}
        if CLAIM_RE.search(text):
            claim_pages += 1
        if PROOF_RE.search(text):
            proof_pages += 1
        if DATE_RE.search(text) or data.get("modified") or data.get("published"):
            fresh_pages += 1
        quotable_count += len(QUOTABLE_RE.findall(text)[:3])
        links = data.get("links") or []
        if any(
            isinstance(link, dict) and link.get("rel") != "internal" and str(link.get("href", "")).startswith("http")
            for link in links
        ) or any(isinstance(link, str) and link.startswith("http") for link in links):
            # Heuristic: outbound absolute links often present as strings or objects.
            external_link_pages += 1
        elif "http" in text and "://" in text:
            external_link_pages += 1

    if usable == 0:
        return AnalyzerScore(
            name="geo",
            score=0.0,
            confidence="insufficient_evidence",
            notes=["No usable HTML pages to score for GEO / citation readiness."],
        )

    score = round(
        100
        * (
            0.30 * min(1.0, (claim_pages / usable) * 2)
            + 0.30 * min(1.0, (proof_pages / usable) * 2)
            + 0.20 * min(1.0, (fresh_pages / usable) * 2)
            + 0.20 * min(1.0, (quotable_count / max(usable, 1)) / 2)
        ),
        1,
    )

    if proof_pages / usable < 0.25:
        findings.append(
            Finding(
                code="geo_weak_proof_signals",
                priority="medium",
                observation="Few pages show proof, sources, customers, or review/update cues.",
                affected_urls=[p.get("url", "") for p in pages if p.get("url")][:5],
                recommended_action="Add dated proof, named sources, and quotable summary statements.",
                acceptance_check="Recrawl and confirm proof/freshness language on core service pages.",
                claim_type="inference",
                why_it_matters="Generative systems prefer citable, attributable statements.",
                uncertainty="Keyword heuristics cannot verify claim truthfulness.",
                score_component="geo",
            )
        )

    return AnalyzerScore(
        name="geo",
        score=score,
        confidence="heuristic",
        signals={
            "usable_pages": usable,
            "pages_with_claim_cues": claim_pages,
            "pages_with_proof_cues": proof_pages,
            "pages_with_freshness_cues": fresh_pages,
            "quotable_statements_sampled": quotable_count,
            "pages_with_external_link_cues": external_link_pages,
        },
        findings=findings,
        notes=[
            "GEO score estimates citation readiness from on-page cues — not observed AI mentions."
        ],
    )
