"""Pre-alpha CLI: source inventory and evidence requests, never a release approval."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evidence import image_evidence, review_template
from .pbir import report_context


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vqs", description="Visual Quality System pre-alpha tools")
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory", help="Read PBIR definition and bindings, without design approval")
    inventory.add_argument("report", type=Path, help="An enhanced-format *.Report folder")
    review = commands.add_parser("request-review", help="Validate a capture manifest and prepare review questions")
    review.add_argument("report", type=Path)
    review.add_argument("renders", type=Path)
    review.add_argument("--surface", choices=["report"], default="report")
    review.add_argument("--fixer-id", required=True)
    args = parser.parse_args(argv)
    try:
        info = report_context(args.report)
        if args.command == "inventory":
            print(json.dumps(info, indent=2, ensure_ascii=False))
            return 0
        manifest_path = args.renders / "capture-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        names = list(manifest.get("files", {}))
        pages, issues = image_evidence(args.renders, info["source_sha256"], names)
        if issues or len(pages) != len(info["pages"]):
            print(json.dumps({"status": "blocked", "findings": issues,
                              "reason": "Fresh complete source-bound page renders required"}, indent=2))
            return 2
        draft = review_template(args.surface, info["source_sha256"], pages, args.fixer_id)
        print(json.dumps(draft, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": f"{type(exc).__name__}: {exc}"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
