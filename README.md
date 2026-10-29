# SeoForge

**Evidence-first SEO, AEO & GEO** with a native website crawler — no paid SEO API required.

Crawl sites, score answer/citation/entity readiness, compare competitors, verify reputation samples, and export actionable reports. Works as a Python CLI/library and as a skill for **Cursor**, **Claude**, and **ChatGPT**.

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-0D9488?style=flat-square" alt="MIT"></a>
  <a href="docs/setup.md"><img src="https://img.shields.io/badge/python-3.10%2B-0F172A?style=flat-square" alt="Python 3.10+"></a>
  <a href="#quick-start"><img src="https://img.shields.io/badge/APIs-none_required-0F172A?style=flat-square" alt="No API keys"></a>
  <a href="#agent-skills"><img src="https://img.shields.io/badge/skills-Cursor_|_Claude_|_ChatGPT-0D9488?style=flat-square" alt="Multi-agent"></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-0.2.1-0D9488?style=flat-square" alt="0.2.1"></a>
</p>

> **Before publishing:** search the repo for `NisarZaidi` and replace it with your GitHub username (clone URLs, badges, `pyproject.toml`, docs).

---

## Features

| Area | What you get |
|---|---|
| **Native crawler** | Robots/sitemaps, priority sampling, resume via SQLite, HTTP + optional Playwright |
| **SEO audit** | Technical/on-page findings with evidence, impact, and acceptance checks |
| **AEO** | Question/FAQ detection, answer-first cues, FAQ schema signals — scored in code |
| **GEO** | Citation-readiness: claims, proof, freshness, quotable statements |
| **Entity SEO** | Organization/Person JSON-LD + NAP consistency signals |
| **Competitors** | Side-by-side matrix from crawl inventories (content & schema gaps) |
| **Reputation** | Verify source pages for links/mentions; conservative evidence-based scoring |
| **Reports** | Rich terminal summaries + branded HTML (optional PDF) |
| **Agent skills** | Cursor, Claude, and ChatGPT-friendly `SKILL.md` + playbooks |

Honest limits: no invented rankings, traffic, or AI citations. Coverage gaps are always reported.

---

## Quick start

Requires **Python 3.10+** (3.12 recommended).

```sh
git clone https://github.com/NisarZaidi/seoforge.git
cd seoforge
python -m pip install -e ".[reports]"

seoforge doctor
seoforge audit https://example.com --max-pages 10
```

Windows (PowerShell):

```powershell
git clone https://github.com/NisarZaidi/seoforge.git
cd seoforge
py -3 -m pip install -e ".[reports]"
seoforge doctor
seoforge audit https://example.com --max-pages 10
```

### Install options

| Method | Command |
|---|---|
| pip editable | `python -m pip install -e ".[browser,reports]"` |
| uv | `uv pip install -e ".[browser,reports]"` |
| extras | `browser` (Playwright), `reports` (PDF), `sftp`, `dev` |

### Library usage

```python
from seoforge import Config, Crawler

config = Config(url="https://example.com", max_pages=10, render_mode="auto")
crawler = Crawler(config, "runs/python-example")
try:
    print(crawler.run()["html_documents"])
finally:
    crawler.close()
```

---

## CLI overview

```text
seoforge version
seoforge doctor [--target URL]
seoforge audit URL [--out DIR] [--max-pages N] [--audit-depth quick|standard|deep]
seoforge crawl URL [--out DIR]
seoforge compete TARGET_CRAWL --competitor-crawl DIR [--competitor-crawl DIR...]
seoforge discover --query "..." --out DIR
seoforge reputation --target URL --brand NAME --sources CSV --out DIR
seoforge report --audit PATH --out DIR          # HTML/PDF present
```

One-shot star path:

```sh
seoforge audit https://example.com --audit-depth standard --out ./seoforge-runs/demo
```

Writes crawl evidence, `audit/audit.json`, and AEO/GEO/Entity scores under `analysis/`.

Legacy argparse commands (`watch`, `profile`, `project`, `onsite`, …) remain available for advanced workflows — run `seoforge --help` for the note.

Full reference: [references/crawler.md](references/crawler.md).

---

## Configuration

Copy [`seoforge.toml.example`](seoforge.toml.example) to `seoforge.toml` or `.seoforge.toml`:

```toml
[seoforge]
output_dir = "seoforge-runs"
audit_depth = "standard"
workers = 4
render_mode = "auto"
include_www = true
respect_robots = true
```

Environment overrides use the `SEOFORGE_*` prefix (for example `SEOFORGE_MAX_PAGES=20`). Local `seoforge.toml` files are gitignored by default.

---

## Agent skills

| Platform | Guide |
|---|---|
| **Cursor** | [docs/agent-installation.md#cursor](docs/agent-installation.md#cursor) |
| **Claude** (web / Claude Code) | [docs/agent-installation.md#claude](docs/agent-installation.md#claude) |
| **ChatGPT** | [docs/agent-installation.md#chatgpt](docs/agent-installation.md#chatgpt) |

Skill entrypoint: [`SKILL.md`](SKILL.md). Validate a Claude-sized bundle with:

```sh
python scripts/validate_skill.py
```

---

## Docker

```sh
docker build -t seoforge .
docker run --rm seoforge doctor
docker run --rm -v "%cd%/out:/out" seoforge audit https://example.com --max-pages 5 --out /out
```

(Linux/macOS: `-v "$PWD/out:/out"`.)

---

## Project layout

```text
src/seoforge/     crawl, extract, analyze, research, reputation, report, cli
docs/            setup, architecture, agent installation
playbooks/       SEO / AEO / GEO specialist workflows
references/      capabilities, crawler CLI, measurement boundaries
tests/           unit + regression fixtures
assets/          brand mark
Dockerfile
seoforge.toml.example
SKILL.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and `CODE_OF_CONDUCT.md` in the git checkout.

```sh
python -m pip install -e ".[dev,browser,reports]"
ruff check .
python -m pytest tests/test_phase3_core.py -q
python -m unittest discover -s tests -v
python scripts/validate_skill.py
```

## License

[MIT](LICENSE) © SeoForge Contributors

## Status

**0.2.1** — public-ready polish on the 0.2 Typer/analyzer line. Beta: respect robots.txt and site terms; results are evidence samples, not ranking guarantees.
