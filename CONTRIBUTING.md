# Contributing to SeoForge

Thanks for helping improve SeoForge. Good contributions make crawls clearer, findings more actionable, or the docs easier to follow.

## Setup

```sh
python -m pip install -e ".[dev,browser,reports]"
# or
python scripts/setup.py --dev
```

## Checks

```sh
ruff check .
ruff format --check .
python -m pytest tests/test_phase3_core.py -q
python -m unittest discover -s tests -v
python scripts/validate_skill.py
```

Keep fixes focused. Prefer small fixtures over live websites. Do not commit crawl databases, credentials, client reports, or personal paths.

Preserve the distinction between raw HTTP captures and rendered pages. When changing CLI flags or output fields, update [references/crawler.md](references/crawler.md) and tests.

Before a PR, run the checks above. CI runs on Linux, Windows, and macOS ([workflow](https://github.com/NisarZaidi/seoforge/actions/workflows/tests.yml)). Contributions are under the MIT license.

## Release hygiene

Keep live-client research outside the repository. Use fictional names and example domains in fixtures. Before publishing:

```sh
python scripts/check_release.py
git diff --check
```

Before the first public push, search the repo for `NisarZaidi` and replace it (see `PLACEHOLDERS.md` in the git checkout).
