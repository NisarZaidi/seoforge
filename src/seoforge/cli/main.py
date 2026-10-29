"""SeoForge CLI entrypoint: Typer for modern commands, argparse legacy for the rest."""

from __future__ import annotations

import sys

# Commands implemented on the Typer + Rich app.
# `crawl` stays on legacy argparse so full crawl flags (--delay, --only-url,
# --resume, --next-pages, …) keep working for scripts and the test suite.
MODERN = {
    "version",
    "doctor",
    "audit",
    "compete",
    "discover",
    "reputation",
    "report",
}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if args in (["--version"], ["-V"]):
        from seoforge.cli.app import run

        return run(["version"])

    if not args or args[0] in ("-h", "--help"):
        from seoforge.cli.app import run

        code = run(["--help"])
        print(
            "\nAlso available (legacy argparse):\n"
            "  crawl, scrape, watch, present, readiness, compare, backlinks,\n"
            "  search-plan, search-import, profile, competitors,\n"
            "  research-plan, compare-reputation, browser-setup, edit,\n"
            "  project, onsite\n"
            "Prefer: seoforge report --audit …  (modern) over present when possible.",
            file=sys.stderr,
        )
        return code

    if args[0] in MODERN:
        from seoforge.cli.app import run

        return run(args)

    from seoforge.cli.legacy import legacy_main

    return legacy_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
