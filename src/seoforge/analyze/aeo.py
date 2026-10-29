"""Answer Engine Optimization (AEO) signals from crawled page evidence."""

from __future__ import annotations

import re
from typing import Any

from seoforge.models import AnalyzerScore, Finding

QUESTION_RE = re.compile(
    r"\b(what|why|how|when|where|who|which|can|does|do|is|are|should)\b.+\?",
    re.I,
)
FAQ_HINTS = re.compile(r"\b(faq|frequently asked|common questions|q\s*&\s*a)\b", re.I)
ANSWER_FIRST = re.compile(
    r"^(is |are |yes[,.]|no[,.]|it is|they are|we |our |the [a-z]+ is )",
    re.I,
)


def _text_blobs(page: dict[str, Any]) -> str:
    data = page.get("data") or page.get("rendered", {}).get("data") or {}
    parts = [
        data.get("title") or "",
        " ".join(data.get("h1") or []),
        " ".join(data.get("h2") or []),
        data.get("text") or data.get("main_text") or "",
    ]
    return "\n".join(str(p) for p in parts if p)


def _schema_types(page: dict[str, Any]) -> list[str]:
    data = page.get("data") or {}
    types: list[str] = []
    for block in data.get("jsonld") or data.get("schema") or []:
        if isinstance(block, dict):
            value = block.get("@type")
            if isinstance(value, list):
                types.extend(str(v) for v in value)
            elif value:
                types.append(str(value))
    return types


def analyze_pages(pages: list[dict[str, Any]]) -> AnalyzerScore:
    """Score answer-readiness across successfully captured pages."""
    findings: list[Finding] = []
    question_pages = 0
    faq_pages = 0
    answer_first_pages = 0
    faq_schema_pages = 0
    usable = 0
    questions: list[str] = []

    for page in pages:
        if page.get("error") or int(page.get("status") or 0) >= 400:
            continue
        usable += 1
        text = _text_blobs(page)
        url = page.get("url") or ""
        page_questions = [m.group(0).strip() for m in re.finditer(QUESTION_RE, text)]
        if page_questions:
            question_pages += 1
            questions.extend(page_questions[:5])
        if FAQ_HINTS.search(text) or any("faq" in (u or "").lower() for u in [url]):
            faq_pages += 1
        # answer-first: short paragraph after an H2 question, or opening sentence pattern
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if any(ANSWER_FIRST.search(ln) and len(ln.split()) <= 40 for ln in lines[:12]):
            answer_first_pages += 1
        types = {t.lower() for t in _schema_types(page)}
        if "faqpage" in types or "question" in types:
            faq_schema_pages += 1

    if usable == 0:
        return AnalyzerScore(
            name="aeo",
            score=0.0,
            confidence="insufficient_evidence",
            notes=["No usable HTML pages to score for AEO."],
        )

    # Weighted heuristic score (transparent, not a ranking claim).
    ratio_q = question_pages / usable
    ratio_faq = faq_pages / usable
    ratio_answer = answer_first_pages / usable
    ratio_schema = faq_schema_pages / usable
    score = round(
        100
        * (0.30 * min(1.0, ratio_q * 2)
           + 0.25 * min(1.0, ratio_faq * 3)
           + 0.25 * min(1.0, ratio_answer * 2)
           + 0.20 * min(1.0, ratio_schema * 4)),
        1,
    )

    if ratio_q < 0.2:
        findings.append(
            Finding(
                code="aeo_low_question_coverage",
                priority="medium",
                observation="Few pages expose clear customer questions in headings or body copy.",
                affected_urls=[p.get("url", "") for p in pages if p.get("url")][:5],
                recommended_action="Add FAQ or Q&A sections that match real buyer questions.",
                acceptance_check="Recrawl and confirm questions appear as H2/H3 or FAQ blocks.",
                claim_type="inference",
                why_it_matters="Answer engines favour pages that state and answer explicit questions.",
                uncertainty="Question detection is regex-based on captured text only.",
                score_component="aeo",
            )
        )
    if faq_schema_pages == 0 and faq_pages > 0:
        findings.append(
            Finding(
                code="aeo_missing_faq_schema",
                priority="low",
                observation="FAQ-like content was detected without FAQPage/Question JSON-LD.",
                affected_urls=[p.get("url", "") for p in pages if p.get("url")][:3],
                recommended_action="Add valid FAQPage structured data that matches visible Q&A.",
                acceptance_check="Validate JSON-LD and confirm visible questions match markup.",
                claim_type="inference",
                why_it_matters="Structured Q&A can help machines locate concise answers.",
                uncertainty="Schema presence is not proof of rich-result eligibility.",
                score_component="aeo",
            )
        )

    return AnalyzerScore(
        name="aeo",
        score=score,
        confidence="heuristic",
        signals={
            "usable_pages": usable,
            "pages_with_questions": question_pages,
            "pages_with_faq_hints": faq_pages,
            "pages_with_answer_first": answer_first_pages,
            "pages_with_faq_schema": faq_schema_pages,
            "sample_questions": questions[:12],
        },
        findings=findings,
        notes=[
            "AEO score is a local readiness heuristic from crawled text/schema — not AI citation proof."
        ],
    )
