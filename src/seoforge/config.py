"""SeoForge configuration: defaults, TOML files, and environment overrides."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Literal

from seoforge.exceptions import ConfigError

AuditDepth = Literal["quick", "standard", "deep"]
RenderMode = Literal["auto", "http", "browser"]

DEPTH_PAGES = {"quick": 1, "standard": 15, "deep": 50}


@dataclass
class SeoForgeSettings:
    """User-facing settings loaded from defaults, TOML, and env."""

    output_dir: Path = Path("seoforge-runs")
    audit_depth: AuditDepth = "standard"
    max_pages: int | None = None
    max_depth: int = 6
    workers: int = 4
    delay: float = 0.5
    timeout: float = 20.0
    retries: int = 2
    include_www: bool = True
    respect_robots: bool = True
    render_mode: RenderMode = "auto"
    user_agent: str = "SeoForge/0.2 (+https://github.com/NisarZaidi/seoforge)"
    allow_private: bool = False
    quiet: bool = False
    no_color: bool = False

    def page_budget(self) -> int:
        if self.max_pages is not None:
            return self.max_pages
        return DEPTH_PAGES[self.audit_depth]


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _coerce(name: str, value: Any) -> Any:
    if name in {"output_dir"} and not isinstance(value, Path):
        return Path(str(value))
    if name in {"max_pages", "max_depth", "workers", "retries"} and value is not None:
        return int(value)
    if name in {"delay", "timeout"}:
        return float(value)
    if name in {"include_www", "respect_robots", "allow_private", "quiet", "no_color"}:
        if isinstance(value, bool):
            return value
        return _parse_bool(str(value))
    return value


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - py<3.11
        import tomli as tomllib  # type: ignore

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"Cannot read config file {path}: {exc}") from exc
    except Exception as exc:  # tomllib.TOMLDecodeError
        raise ConfigError(f"Invalid TOML in {path}: {exc}") from exc
    section = data.get("seoforge", data)
    if not isinstance(section, dict):
        raise ConfigError(f"Config root in {path} must be a table.")
    return section


def find_config_file(start: Path | None = None) -> Path | None:
    start = (start or Path.cwd()).resolve()
    names = ("seoforge.toml", ".seoforge.toml")
    for directory in [start, *start.parents]:
        for name in names:
            candidate = directory / name
            if candidate.is_file():
                return candidate
        if (directory / ".git").exists():
            break
    return None


def load_settings(
    *,
    config_file: Path | None = None,
    overrides: dict[str, Any] | None = None,
) -> SeoForgeSettings:
    """Merge defaults ← TOML ← SEOFORGE_* env ← explicit overrides."""
    data: dict[str, Any] = {}
    path = config_file or find_config_file()
    if path:
        data.update(_read_toml(path))

    env_map = {
        "SEOFORGE_OUTPUT_DIR": "output_dir",
        "SEOFORGE_AUDIT_DEPTH": "audit_depth",
        "SEOFORGE_MAX_PAGES": "max_pages",
        "SEOFORGE_MAX_DEPTH": "max_depth",
        "SEOFORGE_WORKERS": "workers",
        "SEOFORGE_DELAY": "delay",
        "SEOFORGE_TIMEOUT": "timeout",
        "SEOFORGE_RETRIES": "retries",
        "SEOFORGE_INCLUDE_WWW": "include_www",
        "SEOFORGE_RESPECT_ROBOTS": "respect_robots",
        "SEOFORGE_RENDER_MODE": "render_mode",
        "SEOFORGE_USER_AGENT": "user_agent",
        "SEOFORGE_ALLOW_PRIVATE": "allow_private",
        "SEOFORGE_QUIET": "quiet",
        "NO_COLOR": "no_color",
    }
    for env_name, field_name in env_map.items():
        if env_name in os.environ and os.environ[env_name] != "":
            raw = os.environ[env_name]
            data[field_name] = True if env_name == "NO_COLOR" else raw

    if overrides:
        for key, value in overrides.items():
            if value is not None:
                data[key] = value

    known = {f.name for f in fields(SeoForgeSettings)}
    unknown = sorted(set(data) - known)
    if unknown:
        raise ConfigError("Unknown config keys: " + ", ".join(unknown))

    cleaned = {k: _coerce(k, v) for k, v in data.items()}
    settings = SeoForgeSettings(**cleaned)
    if settings.audit_depth not in DEPTH_PAGES:
        raise ConfigError("audit_depth must be quick, standard, or deep.")
    if settings.render_mode not in {"auto", "http", "browser"}:
        raise ConfigError("render_mode must be auto, http, or browser.")
    if settings.workers < 1 or settings.max_depth < 0:
        raise ConfigError("workers must be >= 1 and max_depth >= 0.")
    return settings


def settings_dict(settings: SeoForgeSettings) -> dict[str, Any]:
    payload = asdict(settings)
    payload["output_dir"] = str(settings.output_dir)
    payload["page_budget"] = settings.page_budget()
    return payload
