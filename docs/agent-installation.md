# Install SeoForge in your assistant

SeoForge is a **Python CLI + library** with a reusable **skill** (`SKILL.md` + playbooks + crawler). Pick your host below.

| Host | Start here |
|---|---|
| Cursor | [Cursor](#cursor) |
| Claude (web / desktop) | [Claude skills upload](#claude) |
| Claude Code | [Claude Code](#claude-code) |
| ChatGPT (Custom GPT / Skills) | [ChatGPT](#chatgpt) |

Also read [permissions.md](permissions.md) before granting network or filesystem access.

Saving a skill and preparing the crawler are **separate** steps. Report:

1. Skill registration  
2. HTTP / doctor readiness  
3. Browser (Playwright) readiness — only if JavaScript capture is needed  

---

## Cursor

### Option A — project skill (recommended)

1. Clone or copy this repository into your workspace (or add it as a submodule).
2. Ensure Cursor can see `SKILL.md` at the skill root (this repo root).
3. Install the engine in a venv your agent may use:

```sh
python -m pip install -e ".[browser,reports]"
seoforge doctor
```

4. In chat, ask: *“Use the SeoForge skill to audit https://example.com.”*

### Option B — paste install request

```text
Install SeoForge from https://github.com/NisarZaidi/seoforge for Cursor.
Follow docs/agent-installation.md#cursor.
Register the skill from SKILL.md, install the package with pip install -e ".[browser,reports]",
run seoforge doctor, and report skill registration vs HTTP vs browser readiness separately.
```

### Cursor tips

- Prefer `seoforge …` over ad-hoc scrape scripts.
- Keep client crawl output **outside** the skill repo (e.g. `../runs/…`).
- Optional Chromium: `python -m playwright install chromium`.

---

## Claude

### Claude.ai / desktop Skills upload

1. Build or download a skill ZIP whose top-level folder is `seoforge/` and contains `SKILL.md`, `src/`, `playbooks/`, `docs/`, `scripts/`, and `references/`.
2. Enable **Code execution and file creation** if available on your account.
3. **Customize → Skills → Add skill → Upload skill** (labels vary slightly by client).
4. Enable SeoForge, start a **new** chat, and ask it to explain capabilities and run a doctor check.

Helper scripts in this repo:

```sh
python scripts/build_skill.py    # produces a release-style skill ZIP when available
python scripts/validate_skill.py
```

### Claude Code

```sh
git clone https://github.com/NisarZaidi/seoforge.git
cd seoforge
python -m pip install -e ".[browser,reports]"
# Point Claude Code at this folder / SKILL.md per your Claude Code skill docs
seoforge doctor
```

Paste:

```text
Use SeoForge from this repo. Read SKILL.md and docs/agent-installation.md#claude-code.
Run seoforge doctor, then audit the URL I provide with evidence-backed findings.
```

---

## ChatGPT

### Custom GPT (knowledge + instructions)

1. Create a Custom GPT.
2. Upload this repository (or the skill ZIP) as **Knowledge**.
3. Paste the following into **Instructions** (edit the repo URL if needed):

```text
You are operating with the SeoForge skill. Follow SKILL.md.
Prefer the SeoForge CLI (seoforge) when a Code Interpreter / execution environment is available.
Never invent crawl results, rankings, backlinks, or AI citations.
Distinguish skill registration from crawler readiness.
For audits: crawl → profile → competitors → reputation sample → findings → 30/60/90 plan.
Respect robots.txt unless the user explicitly authorizes an override; record the override.
```

4. In chat: *“Using SeoForge, outline how you would audit example.com and what evidence you need.”*

### ChatGPT workspace / Skills (when available)

1. Use **Skills → Create / Upload** with `seoforge-<version>-skill.zip` when you publish releases.
2. Or ask Work / the workspace agent:

```text
Install SeoForge from https://github.com/NisarZaidi/seoforge as a reusable skill.
Follow docs/agent-installation.md#chatgpt and docs/permissions.md.
Use the complete skill bundle (SKILL.md, src/, playbooks/, scripts/).
Confirm it appears in my Skills list, then set up the crawler and run doctor.
Report skill registration, HTTP readiness, and browser readiness separately.
```

3. Open a **fresh** task after replace/update so the new mount is used.

### When ChatGPT cannot reach GitHub

Download the source or skill ZIP on a machine that can reach GitHub, then upload via the skill importer. Uploading does not fix workspace DNS, proxy, or live crawl permissions — check each separately.

---

## Shared doctor check

```sh
seoforge doctor
seoforge doctor --target https://example.com
```

Or:

```sh
python scripts/run.py doctor
python scripts/run.py doctor --target https://example.com
```

Interpret results honestly: installed Chromium ≠ successful page render; DNS failure ≠ robots disallow.

---

## Other assistants

Any agent that can read `SKILL.md`, run a Python 3.10+ environment, and call `seoforge` can use this project. Map its skill/import UI to the Cursor / Claude / ChatGPT patterns above.

---

## Check model access separately

A model that cannot answer without tools has **not** demonstrated a SeoForge failure. Keep host authentication, skill save, and crawler network checks as three separate diagnostics.
