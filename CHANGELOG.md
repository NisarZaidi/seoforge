# Changelog

All notable changes to SeoForge are documented in this file.

## 0.2.1 — 2026-10-29

### Added

- Typer ports: `discover`, `reputation`, `report`
- Public-release README, SECURITY, `.gitignore`, placeholder convention `NisarZaidi`

### Changed

- Docs index cleaned for 0.2.x; agent-install URLs use the searchable placeholder

## 0.2.0 — 2026-10-29

### Added

- Typer + Rich CLI: `version`, `doctor`, `crawl`, `audit`, `compete`
- One-shot `seoforge audit <url>` (crawl + findings + AEO/GEO/Entity scores)
- Config system: `seoforge.toml` / `.seoforge.toml` + `SEOFORGE_*` env overrides
- Typed models (`Finding`, `CoverageReport`, `AnalyzerScore`, …) and exception hierarchy
- Code analyzers for AEO, GEO/citation readiness, and Entity SEO
- Competitor matrix export from existing crawl folders
- Dockerfile and pytest coverage for Phase 3 core modules

## 0.1.0 — 2026-10-29

### Added

- Independent **SeoForge** project identity (CLI `seoforge`, package `seoforge`)
- Modular package layout: `crawl`, `extract`, `analyze`, `research`, `reputation`, `report`, `cli`
- Multi-agent skill docs for **Cursor**, **Claude**, and **ChatGPT**
- Fresh MIT packaging metadata and brand assets (slate / teal)

### Changed

- Complete rebrand from the prior upstream clone; original author and product names removed
- Report palette and PDF font family renamed for SeoForge
- Version baseline reset to `0.1.0` for the new public lineage

### Notes

- Feature upscaling (richer AEO/GEO analyzers, Typer/Rich CLI, config files, Docker) is planned for subsequent releases
