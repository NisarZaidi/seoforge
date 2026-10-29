---
name: seoforge
description: >-
  Audit websites with SeoForge's native crawler; produce evidence-based SEO, AEO,
  GEO, competitor, reputation and content plans. Use when the user asks for SEO
  audits, crawls, competitor analysis, reputation checks, or SeoForge workflows.
---

# SeoForge (project skill)

This workspace **is** the SeoForge repository. The full skill bundle lives at the repo root.

## Skill root

Resolve the canonical skill from:

- `SKILL.md` (repository root — full instructions)
- `docs/agent-installation.md` — host install notes
- `playbooks/` — specialist SEO/AEO/GEO workflows
- `references/` — crawler CLI and capability map

Personal copy (all projects): `~/.cursor/skills/seoforge/`

## Runtime

Prefer the installed CLI from this checkout:

```powershell
cd E:\persnal\seo\beyondseo
python -m pip install -e ".[browser,reports]"
seoforge doctor
seoforge audit https://example.com --max-pages 10 --out ..\runs\demo
```

Keep crawl/audit output **outside** this repo (for example `E:\persnal\seo\runs\...`).

## Rules

- Never invent rankings, traffic, backlink totals, or AI citations.
- Respect robots.txt unless the user explicitly authorizes an override; record it.
- Label coverage limits when a crawl is partial or blocked.
- Lead with evidence-backed findings and acceptance checks.

Read the root `SKILL.md` for the complete workflow (profile → competitors → reputation → 30/60/90 plan).
