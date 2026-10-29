"""Typer + Rich CLI for SeoForge."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel

from seoforge import __version__
from seoforge.cli.console import (
    brand_title,
    console,
    error,
    findings_table,
    status_table,
    success,
    warn,
)
from seoforge.cli.runners import (
    audit_findings,
    coverage_from_summary,
    default_run_dir,
    run_audit_from_crawl,
    run_crawl,
)
from seoforge.config import load_settings
from seoforge.exceptions import SeoForgeError

app = typer.Typer(
    name="seoforge",
    help="Evidence-first SEO, AEO & GEO toolkit with a native website crawler.",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)


@app.callback()
def _root(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show SeoForge version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        console.print(f"SeoForge {__version__}")
        raise typer.Exit(0)


@app.command("version")
def version_cmd() -> None:
    """Show the installed SeoForge version."""
    # Single plain line for scripts, launchers, and CI.
    console.print(f"SeoForge {__version__}", highlight=False)


@app.command("doctor")
def doctor_cmd(
    target: Optional[str] = typer.Option(
        None, "--target", help="Optional URL for a bounded live reachability probe."
    ),
    query: Optional[str] = typer.Option(
        None, "--query", help="Optional search discovery probe query."
    ),
    out: Optional[Path] = typer.Option(
        None, "--out", help="Optional directory for doctor JSON output."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Print machine-readable JSON instead of a Rich table."
    ),
) -> None:
    """Check Python, dependencies, filesystem, and optional target readiness."""
    from seoforge.crawl.doctor import check_environment

    if not json_output:
        console.print(Panel(brand_title("doctor"), border_style="cyan"))

    # Capture JSON that check_environment prints to stdout.
    import contextlib
    import io

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = check_environment(target, query, out)
    payload = buffer.getvalue().strip()
    report = json.loads(payload) if payload.startswith("{") else {}

    if json_output:
        if payload:
            console.print(payload)
        raise typer.Exit(code)

    rows = []
    for key, value in (report.get("runtime_checks") or {}).items():
        if isinstance(value, dict):
            rows.append(
                (
                    key,
                    str(value.get("status", "?")),
                    str(value.get("evidence", value.get("failure", "")))[:140],
                )
            )
    for key, value in (report.get("checks") or {}).items():
        if isinstance(value, dict) and "status" in value:
            rows.append((key, str(value.get("status")), str(value.get("evidence", ""))[:140]))
    console.print(status_table("Runtime readiness", rows[:24]))
    if report.get("browser_ready"):
        success("Browser JavaScript probe ready")
    else:
        warn("Browser rendering not ready (HTTP crawl still works)")
    if report.get("http_ready"):
        success("HTML parser dependency present")
    else:
        error("Install package deps: pip install -e .")
    raise typer.Exit(code)


@app.command("crawl")
def crawl_cmd(
    url: str = typer.Argument(..., help="Seed URL to crawl."),
    out: Optional[Path] = typer.Option(
        None, "--out", help="Output directory (default: seoforge-runs/crawl-<host>)."
    ),
    max_pages: Optional[int] = typer.Option(None, "--max-pages", help="Page attempt budget."),
    audit_depth: Optional[str] = typer.Option(
        None, "--audit-depth", help="quick | standard | deep (sets default page budget)."
    ),
    include_www: bool = typer.Option(
        True, "--include-www/--exact-host", help="Include www/non-www counterpart."
    ),
    mode: str = typer.Option("auto", "--mode", help="auto | http | browser"),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to seoforge.toml"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress crawl progress lines."),
    json_output: bool = typer.Option(False, "--json", help="Print summary JSON only."),
) -> None:
    """Crawl a website and write evidence to an output directory."""
    try:
        settings = load_settings(
            config_file=config,
            overrides={
                "max_pages": max_pages,
                "audit_depth": audit_depth,
                "include_www": include_www,
                "render_mode": mode,
                "quiet": quiet or None,
            },
        )
        dest = out or default_run_dir(settings, url, "crawl")
        if not json_output:
            console.print(Panel(brand_title(f"crawl -> {dest}"), border_style="cyan"))
        summary = run_crawl(
            url, dest, settings, max_pages=max_pages, include_www=include_www, quiet=quiet
        )
        coverage = coverage_from_summary(summary)
        if json_output:
            console.print_json(data=summary)
        else:
            success(f"Inspected HTML documents: {coverage.html_documents}")
            console.print(
                status_table(
                    "Coverage",
                    [
                        ("seed", "info", coverage.seed),
                        ("inspected", "PASS", str(coverage.inspected)),
                        ("partial", "NOT_TESTED", str(coverage.partial)),
                        ("failed", "FAIL" if coverage.failed else "PASS", str(coverage.failed)),
                        ("pending", "NOT_TESTED", str(coverage.pending)),
                        ("output", "info", str(dest)),
                    ],
                )
            )
        raise typer.Exit(0 if coverage.html_documents else 1)
    except SeoForgeError as exc:
        error(str(exc))
        raise typer.Exit(exc.exit_code) from exc
    except (OSError, ValueError, KeyError, TypeError) as exc:
        error(str(exc))
        raise typer.Exit(2) from exc


@app.command("audit")
def audit_cmd(
    url: str = typer.Argument(..., help="Website URL to audit."),
    out: Optional[Path] = typer.Option(
        None, "--out", help="Output directory (default: seoforge-runs/audit-<host>)."
    ),
    max_pages: Optional[int] = typer.Option(None, "--max-pages", help="Page attempt budget."),
    audit_depth: Optional[str] = typer.Option(
        None, "--audit-depth", help="quick | standard | deep"
    ),
    include_www: bool = typer.Option(True, "--include-www/--exact-host"),
    mode: str = typer.Option("auto", "--mode", help="auto | http | browser"),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to seoforge.toml"),
    quiet: bool = typer.Option(False, "--quiet"),
    json_output: bool = typer.Option(False, "--json", help="Print audit JSON to stdout."),
) -> None:
    """One-shot audit: crawl -> findings -> terminal summary (+ audit.json/md)."""
    try:
        settings = load_settings(
            config_file=config,
            overrides={
                "max_pages": max_pages,
                "audit_depth": audit_depth,
                "include_www": include_www,
                "render_mode": mode,
                "quiet": quiet or None,
            },
        )
        dest = out or default_run_dir(settings, url, "audit")
        crawl_dir = dest / "crawl"
        audit_dir = dest / "audit"
        if not json_output:
            console.print(Panel(brand_title(f"audit -> {dest}"), border_style="cyan"))
            console.print(f"[dim]Crawling[/dim] {url} ...")
        summary = run_crawl(
            url,
            crawl_dir,
            settings,
            max_pages=max_pages,
            include_www=include_www,
            quiet=quiet,
        )
        from seoforge.analyze.pipeline import export_analysis, merge_analyzer_findings
        from seoforge.crawl.engine import write_json

        audit = run_audit_from_crawl(crawl_dir, audit_dir)
        analysis = export_analysis(crawl_dir, dest / "analysis")
        audit = merge_analyzer_findings(audit, analysis)
        write_json(audit_dir / "audit.json", audit)
        findings = audit_findings(audit)
        coverage = coverage_from_summary(summary)
        if json_output:
            console.print_json(data={"audit": audit, "analysis": analysis})
        else:
            success(f"Crawl complete | {coverage.html_documents} HTML documents")
            composite = analysis.get("composite") or {}
            console.print(
                status_table(
                    "AEO / GEO / Entity scores",
                    [
                        ("aeo", "PASS", f"{composite.get('aeo', 0)} / 100"),
                        ("geo", "PASS", f"{composite.get('geo', 0)} / 100"),
                        ("entity", "PASS", f"{composite.get('entity', 0)} / 100"),
                    ],
                )
            )
            success(f"Findings written | {audit_dir / 'audit.json'}")
            if findings:
                console.print(findings_table([f.raw or f.to_dict() for f in findings]))
            else:
                warn("No material findings from automated checks - review coverage limits.")
            high = sum(1 for f in findings if f.priority == "high")
            console.print(
                Panel(
                    f"[bold]{len(findings)}[/bold] findings"
                    f" | [red]{high} high[/red]"
                    f" | output [cyan]{dest}[/cyan]",
                    title="Audit summary",
                    border_style="green",
                )
            )
        raise typer.Exit(0 if coverage.html_documents else 1)
    except SeoForgeError as exc:
        error(str(exc))
        raise typer.Exit(exc.exit_code) from exc
    except (OSError, ValueError, KeyError, TypeError) as exc:
        error(str(exc))
        raise typer.Exit(2) from exc


@app.command("compete")
def compete_cmd(
    target_crawl: Path = typer.Argument(..., help="Existing target crawl directory."),
    competitor_crawl: Optional[list[Path]] = typer.Option(
        None,
        "--competitor-crawl",
        help="Existing competitor crawl directory (repeatable).",
    ),
    out: Optional[Path] = typer.Option(
        None, "--out", help="Output directory for competitor-matrix.json."
    ),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Build a side-by-side competitor matrix from existing crawl folders."""
    try:
        from seoforge.research.compete import export_comparison

        if not competitor_crawl:
            raise SeoForgeError("Provide at least one --competitor-crawl directory.")
        dest = out or Path("seoforge-runs") / "compete"
        if not json_output:
            console.print(Panel(brand_title(f"compete -> {dest}"), border_style="cyan"))
        payload = export_comparison(target_crawl, list(competitor_crawl), dest)
        if json_output:
            console.print_json(data=payload)
        else:
            success(f"Matrix written | {dest / 'competitor-matrix.json'}")
            table = status_table(
                "Competitors",
                [
                    (
                        str(row.get("competitor", ""))[:48],
                        "PASS",
                        f"pages={row.get('pages')} schema={len(row.get('schema_types') or [])} gaps={len(row.get('title_gaps_vs_target') or [])}",
                    )
                    for row in payload.get("matrix") or []
                ],
            )
            console.print(table)
            if payload.get("gaps"):
                console.print(findings_table(payload["gaps"]))
        raise typer.Exit(0)
    except SeoForgeError as exc:
        error(str(exc))
        raise typer.Exit(exc.exit_code) from exc
    except (OSError, ValueError, KeyError, TypeError) as exc:
        error(str(exc))
        raise typer.Exit(2) from exc


@app.command("discover")
def discover_cmd(
    query: Optional[list[str]] = typer.Option(
        None, "--query", "-q", help="Search query (repeatable)."
    ),
    queries: Optional[Path] = typer.Option(
        None, "--queries", help="JSON list of query objects from a profile/plan."
    ),
    out: Path = typer.Option(..., "--out", help="Output directory for discovery leads."),
    target: str = typer.Option("", "--target", help="Optional site being researched."),
    market: Optional[str] = typer.Option(None, "--market"),
    language: Optional[str] = typer.Option(None, "--language"),
    offline: bool = typer.Option(False, "--offline", help="Do not call live search providers."),
    max_queries: int = typer.Option(8, "--max-queries"),
    max_candidates: int = typer.Option(100, "--max-candidates"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Collect unverified search leads with bounded native fallbacks."""
    try:
        from seoforge.research.discovery import PROVIDERS, discover
        from seoforge.analyze.review import read_json

        query_rows = read_json(queries) if queries else []
        query_rows += [
            {"query": q, "market": market, "language": language} for q in (query or [])
        ]
        if not query_rows:
            raise SeoForgeError("Provide --query and/or --queries JSON.")
        if not json_output:
            console.print(Panel(brand_title(f"discover -> {out}"), border_style="cyan"))
        result = discover(
            query_rows,
            out,
            target,
            PROVIDERS,
            [],
            [],
            [],
            offline,
            16,
            max_queries,
            max_candidates,
            12,
            90,
            None,
        )
        if json_output:
            console.print_json(data=result)
        else:
            success(f"Discovery status: {result.get('status', 'done')}")
            success(f"Output: {out}")
        raise typer.Exit(0)
    except SeoForgeError as exc:
        error(str(exc))
        raise typer.Exit(exc.exit_code) from exc
    except (OSError, ValueError, KeyError, TypeError) as exc:
        error(str(exc))
        raise typer.Exit(2) from exc


@app.command("reputation")
def reputation_cmd(
    target: str = typer.Option(..., "--target", help="Website being scored."),
    brand: str = typer.Option(..., "--brand", help="Brand name for mention checks."),
    out: Path = typer.Option(..., "--out", help="Fresh empty output directory."),
    sources: Optional[Path] = typer.Option(
        None, "--sources", help="CSV of candidate source pages to verify."
    ),
    evidence: Optional[Path] = typer.Option(
        None, "--evidence", help="Reuse prior brand-aware backlinks.json."
    ),
    max_sources: int = typer.Option(50, "--max-sources"),
    search_pages: int = typer.Option(5, "--search-pages"),
    mode: str = typer.Option("auto", "--mode", help="http | auto | browser"),
    alias: Optional[list[str]] = typer.Option(None, "--alias", help="Brand alias (repeatable)."),
    related_host: Optional[list[str]] = typer.Option(
        None, "--related-host", help="Related host that cannot supply independent proof."
    ),
    allow_private: bool = typer.Option(False, "--allow-private"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Estimate reputation from verified source-page evidence (conservative)."""
    try:
        from seoforge.reputation.scoring import reputation

        if not sources and not evidence:
            raise SeoForgeError("Provide --sources CSV or --evidence backlinks.json.")
        if sources and evidence:
            raise SeoForgeError("Use either --sources or --evidence, not both.")
        if not json_output:
            console.print(Panel(brand_title(f"reputation -> {out}"), border_style="cyan"))
        result = reputation(
            sources,
            target,
            brand,
            out,
            max_sources,
            mode,
            allow_private,
            alias or (),
            related_host or (),
            search_pages,
            evidence,
        )
        if json_output:
            console.print_json(data=result)
        else:
            success(f"Reputation assessment written to {out}")
            if isinstance(result, dict):
                for key in (
                    "score",
                    "score_status",
                    "confidence",
                    "score_range",
                    "model_version",
                ):
                    if key in result:
                        console.print(f"  [cyan]{key}[/cyan]: {result[key]}")
        raise typer.Exit(0)
    except SeoForgeError as exc:
        error(str(exc))
        raise typer.Exit(exc.exit_code) from exc
    except (OSError, ValueError, KeyError, TypeError) as exc:
        error(str(exc))
        raise typer.Exit(2) from exc


@app.command("report")
def report_cmd(
    out: Path = typer.Option(..., "--out", help="Report output directory."),
    audit: Optional[Path] = typer.Option(
        None, "--audit", help="Native audit.json to present (findings preserved)."
    ),
    input_json: Optional[Path] = typer.Option(
        None, "--input", help="Reviewed report-content JSON."
    ),
    fmt: str = typer.Option("both", "--format", help="both | html | pdf"),
    overwrite: bool = typer.Option(False, "--overwrite"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Export a branded HTML/PDF client report from audit or content JSON."""
    try:
        from seoforge.report.present import export_report, from_audit

        if not audit and not input_json:
            raise SeoForgeError("Provide --audit or --input.")
        if audit and input_json:
            raise SeoForgeError("Use either --audit or --input, not both.")
        source = audit or input_json
        assert source is not None
        if not json_output:
            console.print(Panel(brand_title(f"report -> {out}"), border_style="cyan"))
        data = json.loads(source.read_text(encoding="utf-8"))
        if audit:
            data = from_audit(data)
        result = export_report(data, out, fmt, overwrite)
        if json_output:
            console.print_json(data=result)
        else:
            success(f"Report status: {result.get('status')}")
            for name, path in (result.get("files") or {}).items():
                console.print(f"  [cyan]{name}[/cyan]: {path}")
        raise typer.Exit(0 if result.get("status") in {"complete", "html_only"} else 1)
    except SeoForgeError as exc:
        error(str(exc))
        raise typer.Exit(exc.exit_code) from exc
    except (OSError, ValueError, KeyError, TypeError) as exc:
        error(str(exc))
        raise typer.Exit(2) from exc


def run(argv: list[str] | None = None) -> int:
    """Invoke the Typer app; return a process exit code."""
    try:
        app(args=argv, prog_name="seoforge", standalone_mode=False)
        return 0
    except typer.Exit as exc:
        return int(exc.exit_code) if exc.exit_code is not None else 0
    except typer.Abort:
        return 1
