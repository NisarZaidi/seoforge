"""Pytest-friendly coverage for Phase 3 config, models, and analyzers."""

from __future__ import annotations

from pathlib import Path

import pytest

from seoforge.analyze import aeo, entity, geo
from seoforge.config import load_settings
from seoforge.models import CoverageReport, Finding


def test_load_settings_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    settings = load_settings()
    assert settings.audit_depth == "standard"
    assert settings.page_budget() == 15


def test_load_settings_toml_and_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "seoforge.toml"
    cfg.write_text(
        '[seoforge]\naudit_depth = "quick"\nworkers = 2\noutput_dir = "runs"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SEOFORGE_WORKERS", "3")
    settings = load_settings()
    assert settings.audit_depth == "quick"
    assert settings.workers == 3
    assert settings.output_dir == Path("runs")
    assert settings.page_budget() == 1


def test_aeo_geo_entity_analyzers_on_fixture_page() -> None:
    pages = [
        {
            "url": "https://example.com/",
            "status": 200,
            "data": {
                "title": "What is managed SEO?",
                "h1": ["What is managed SEO?"],
                "h2": ["How does pricing work?"],
                "text": (
                    "What is managed SEO? It is an ongoing service.\n"
                    "According to research shows teams need proof. Updated 2026.\n"
                    "Contact us at hello@example.com or +1 555 0100."
                ),
                "word_count": 40,
                "jsonld": [
                    {
                        "@type": "Organization",
                        "name": "Example Co",
                        "telephone": "+1 555 0100",
                        "sameAs": ["https://linkedin.com/company/example"],
                    },
                    {"@type": "FAQPage"},
                ],
            },
        }
    ]
    aeo_score = aeo.analyze_pages(pages)
    geo_score = geo.analyze_pages(pages)
    entity_score = entity.analyze_pages(pages)
    assert aeo_score.score > 0
    assert geo_score.score > 0
    assert entity_score.score > 0
    assert aeo_score.name == "aeo"


def test_finding_and_coverage_models() -> None:
    finding = Finding.from_audit_row(
        {
            "code": "missing_title",
            "priority": "high",
            "observation": "No title",
            "affected_urls": ["https://example.com"],
            "recommended_action": "Add title",
            "acceptance_check": "Recrawl",
            "claim_type": "verified_fact",
            "why_it_matters": "Clarity",
            "uncertainty": "None",
        }
    )
    assert finding.code == "missing_title"
    coverage = CoverageReport.from_summary({"seed": "https://example.com", "html_documents": 3})
    assert coverage.html_documents == 3
