"""Rich console helpers for SeoForge CLI output."""

from __future__ import annotations

import os
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

_NO_COLOR = os.getenv("NO_COLOR") is not None
# legacy_windows=False avoids cp1252 crashes on styled help output.
console = Console(
    stderr=False, highlight=False, soft_wrap=True, no_color=_NO_COLOR, legacy_windows=False
)
err_console = Console(
    stderr=True, highlight=False, soft_wrap=True, no_color=_NO_COLOR, legacy_windows=False
)


def brand_title(subtitle: str = "") -> Text:
    text = Text()
    text.append("SeoForge", style="bold cyan")
    if subtitle:
        text.append(" | ", style="dim")
        text.append(subtitle, style="white")
    return text


def success(message: str) -> None:
    console.print(f"[green]OK[/green] {message}")


def warn(message: str) -> None:
    err_console.print(f"[yellow]![/yellow] {message}")


def error(message: str) -> None:
    err_console.print(f"[red]X[/red] {message}")


def status_table(title: str, rows: list[tuple[str, str, str]]) -> Table:
    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Detail", overflow="fold")
    for name, status, detail in rows:
        style = {
            "PASS": "green",
            "ready": "green",
            "dependencies_present": "green",
            "FAIL": "red",
            "BLOCKED": "red",
            "missing_dependency": "red",
            "NOT_TESTED": "dim",
            "not_tested": "dim",
            "unknown": "dim",
        }.get(status, "yellow")
        table.add_row(name, f"[{style}]{status}[/{style}]", detail)
    return table


def findings_table(findings: list[dict[str, Any]], limit: int = 12) -> Table:
    table = Table(title="Top findings", show_header=True, header_style="bold")
    table.add_column("Priority", width=8)
    table.add_column("Code", style="cyan")
    table.add_column("URLs", overflow="fold")
    table.add_column("Observation", overflow="fold")
    priority_style = {"high": "red", "medium": "yellow", "low": "green"}
    for row in findings[:limit]:
        priority = str(row.get("priority", "?"))
        urls = ", ".join(row.get("affected_urls") or [])
        table.add_row(
            f"[{priority_style.get(priority, 'white')}]{priority}[/]",
            str(row.get("code", "finding")),
            urls,
            str(row.get("observation", ""))[:160],
        )
    return table


def panel(message: str, title: str = "SeoForge") -> None:
    console.print(Panel(message, title=title, border_style="cyan"))
