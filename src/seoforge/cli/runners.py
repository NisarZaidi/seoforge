"""Shared runners used by Typer commands and the legacy argparse CLI."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from seoforge.analyze.findings import audit_report
from seoforge.config import SeoForgeSettings
from seoforge.crawl.engine import Crawler
from seoforge.crawl.network import Config
from seoforge.exceptions import ConfigError, CrawlError
from seoforge.models import CoverageReport, Finding


def default_run_dir(settings: SeoForgeSettings, url: str, label: str = "audit") -> Path:
    host = urlparse(url).hostname or "site"
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", host).strip("-") or "site"
    return Path(settings.output_dir) / f"{label}-{safe}"


def build_crawl_config(
    url: str,
    settings: SeoForgeSettings,
    *,
    max_pages: int | None = None,
    include_www: bool | None = None,
    render_mode: str | None = None,
    allow_private: bool | None = None,
    selected_urls: list[str] | None = None,
) -> Config:
    pages = max_pages if max_pages is not None else settings.page_budget()
    if pages < 1:
        raise ConfigError("max_pages must be at least 1.")
    return Config(
        url=url,
        selection="priority" if not selected_urls else "priority",
        selected_urls=selected_urls or [],
        max_pages=pages,
        max_depth=settings.max_depth,
        workers=settings.workers,
        delay=settings.delay,
        timeout=settings.timeout,
        retries=settings.retries,
        include_www=settings.include_www if include_www is None else include_www,
        allow_private=settings.allow_private if allow_private is None else allow_private,
        robots_policy="respect" if settings.respect_robots else "ignore",
        render_mode=render_mode or settings.render_mode,
    )


def run_crawl(
    url: str,
    out: Path,
    settings: SeoForgeSettings,
    *,
    max_pages: int | None = None,
    include_www: bool | None = None,
    render_mode: str | None = None,
    quiet: bool = False,
    log=None,
) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    config = build_crawl_config(
        url,
        settings,
        max_pages=max_pages,
        include_www=include_www,
        render_mode=render_mode,
    )
    crawler = Crawler(config, out)
    try:
        if quiet or settings.quiet:
            crawler.log = lambda _: None
        elif log is not None:
            crawler.log = log
        summary = crawler.run()
    finally:
        crawler.close()
    if not summary.get("html_documents"):
        raise CrawlError(
            "Crawl finished without usable HTML documents. Inspect access.json and coverage.json."
        )
    return summary


def run_audit_from_crawl(crawl_dir: Path, out: Path | None = None) -> dict:
    crawl_dir = Path(crawl_dir)
    dest = Path(out) if out else crawl_dir / "audit"
    return audit_report(crawl_dir, dest)


def audit_findings(audit: dict) -> list[Finding]:
    return [Finding.from_audit_row(row) for row in audit.get("findings") or []]


def coverage_from_summary(summary: dict) -> CoverageReport:
    return CoverageReport.from_summary(summary)
