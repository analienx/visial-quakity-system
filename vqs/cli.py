"""Pre-alpha CLI: source inventory and evidence requests, never release approval."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evidence import image_evidence, review_template
from .pbir import report_context


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vqs", description="Visual Quality System pre-alpha tools")
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory", help="Read PBIR definition and bindings; not design approval")
    inventory.add_argument("report", type=Path, help="Enhanced-format *.Report folder")
    review = commands.add_parser("request-review", help="Require complete source-bound page images")
    review.add_argument("report", type=Path)
    review.add_argument("renders", type=Path)
    review.add_argument("--fixer-id", required=True)
    args = parser.parse_args(argv)
    try:
        info = report_context(args.report)
        if args.command == "inventory":
            print(json.dumps(info, indent=2, ensure_ascii=False))
            return 0
        manifest = json.loads((args.renders / "capture-manifest.json").read_text(encoding="utf-8-sig"))
        mapping = manifest.get("page_images")
        expected = [page["id"] for page in info["pages"]]
        if (not isinstance(mapping, dict) or set(mapping) != set(expected) or
                any(not isinstance(name, str) or Path(name).name != name or
                    not name.endswith(".png") for name in mapping.values()) or
                len(set(mapping.values())) != len(expected)):
            raise ValueError("Manifest requires a unique page_images entry for every PBIR page ID")
        ordered_files = [mapping[page_id] for page_id in expected]
        pages, issues = image_evidence(args.renders, info["source_sha256"], ordered_files)
        if issues or len(pages) != len(expected):
            print(json.dumps({"status": "blocked", "findings": issues,
                              "reason": "Fresh complete source-bound page renders required"}, indent=2))
            return 2
        for page, page_id in zip(pages, expected, strict=True):
            page["id"] = page_id
            page["visual_inventory"] = [{"id": visual["visual_id"]} for visual in
                                        next(p for p in info["pages"] if p["id"] == page_id)["visuals"]]
        print(json.dumps(review_template("report", info["source_sha256"], pages, args.fixer_id),
                         indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "reason": f"{type(exc).__name__}: {exc}"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
