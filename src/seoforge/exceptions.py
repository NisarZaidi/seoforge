"""SeoForge exception hierarchy."""

from __future__ import annotations


class SeoForgeError(Exception):
    """Base error for user-facing SeoForge failures."""

    exit_code = 2


class ConfigError(SeoForgeError):
    """Invalid configuration, missing files, or bad options."""


class CrawlError(SeoForgeError):
    """Crawl could not complete usefully."""


class AnalysisError(SeoForgeError):
    """Analysis or scoring failed on available evidence."""


class ReportError(SeoForgeError):
    """Report export or presentation failed."""


class DependencyError(SeoForgeError):
    """A required optional dependency or runtime probe failed."""

    exit_code = 1
