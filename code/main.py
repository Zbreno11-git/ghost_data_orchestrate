"""Ghost Data Still Exists — deletion-audit CLI.

  python code/main.py validate <output.csv> [--split targets|samples] [--dataset DIR]
  python code/main.py ingest [--report] [--dataset DIR]
  python code/main.py status
  python code/main.py run --engine deterministic --split samples|targets [--ownership strict|scored] [--out DIR]
  python code/main.py explain <case_id> --run DIR [--dataset DIR] [--md FILE]   (no model call)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ghostaudit.config import REPO_ROOT, load_config  # noqa: E402

REQUEST_FILES = {"targets": "deletion_requests.csv", "samples": "sample_deletion_requests.csv"}


def cmd_validate(args) -> int:
    from ghostaudit.ingest.manifest import evidence_times, read_csv
    from ghostaudit.validate import validate_file

    dataset = Path(args.dataset)
    requests = {r["case_id"]: r for r in read_csv(dataset / REQUEST_FILES[args.split])}
    violations = validate_file(Path(args.csv), requests, evidence_times(dataset))
    for x in violations:
        print(f"{x.code}\t{x.case_id}\t{x.detail}")
    print(f"{len(violations)} violations in {args.csv} against {len(requests)} {args.split} requests")
    return 1 if violations else 0


def cmd_ingest(args) -> int:
    from ghostaudit.ingest.pipeline import ingest_all, write_coverage

    store, coverage = ingest_all(Path(args.dataset), allow_paid=args.allow_paid)
    if args.report:
        md = write_coverage(coverage, REPO_ROOT / "runs" / "ingest")
        print(md.read_text())
    failed = [c for c in coverage.files if c.status == "failed"]
    print(f"{len(coverage.files)} files, {len(store)} observations, "
          f"{sum(c.status == 'processed' for c in coverage.files)} processed, "
          f"{sum(c.status == 'partial' for c in coverage.files)} partial, {len(failed)} failed")
    return 1 if failed else 0


def cmd_status(args) -> int:
    from ghostaudit.llm.ledger import Ledger

    cfg = load_config()
    led = Ledger(REPO_ROOT / cfg["budget"]["ledger_path"], cfg["budget"]["ceiling_usd"])
    t = led.totals()
    print(f"ledger: settled ${t['settled_usd']:.6f}  outstanding ${t['outstanding_usd']:.6f}  "
          f"ceiling ${cfg['budget']['ceiling_usd']:.2f}  rows {len(led.rows())}")
    runs = REPO_ROOT / "runs"
    if runs.exists():
        print("runs:", ", ".join(sorted(p.name for p in runs.iterdir() if p.is_dir())) or "none")
    return 0


def cmd_run(args) -> int:
    from datetime import datetime, timezone

    from ghostaudit.runner import run

    tag = "det" if args.engine == "deterministic" else f"agent-{args.mode}"
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{tag}-{args.split}-{args.ownership}"
    out = Path(args.out) if args.out else REPO_ROOT / "runs" / run_id
    cases = set(args.cases.split(",")) if args.cases else None
    from ghostaudit.config import load_config
    cfg = load_config()
    if args.agent_scope:
        cfg["agent"] = {**cfg["agent"], "scope": args.agent_scope}
    summary = run(Path(args.dataset), args.split, out, args.ownership, engine=args.engine, gateway_mode=args.mode,
                  model=args.model, cases=cases, run_id=run_id, config=cfg)
    print(f"{summary['rows']} rows → {out / 'output.csv'}")
    print(f"status {summary['status']}  support {summary['support']}")
    print(f"workflow assignment {summary['workflow_assignment']}  ambiguous {summary['workflow_ambiguous_requests']}")
    if summary["agent"]:
        print(f"agent {summary['agent']}  tools {summary['tool_use']}")
    if summary["ingest_failed_files"]:
        print("ingest failed:", summary["ingest_failed_files"])
        return 1
    return 0


def cmd_explain(args) -> int:
    from ghostaudit.explain import explain
    text = explain(Path(args.run), args.case_id, Path(args.dataset))
    if args.md:
        Path(args.md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md).write_text(text, encoding="utf-8")
        print(f"wrote {args.md}")
    else:
        print(text)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="main.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("validate")
    p.add_argument("csv")
    p.add_argument("--split", choices=sorted(REQUEST_FILES), default="targets")
    p.add_argument("--dataset", default=str(REPO_ROOT / "dataset"))
    p.set_defaults(fn=cmd_validate)
    p = sub.add_parser("ingest")
    p.add_argument("--report", action="store_true")
    p.add_argument("--dataset", default=str(REPO_ROOT / "dataset"))
    p.add_argument("--allow-paid", action="store_true", help="permit vision calls for PNGs missing from the cache")
    p.set_defaults(fn=cmd_ingest)
    p = sub.add_parser("run")
    p.add_argument("--engine", choices=["deterministic", "agent"], default="deterministic")
    p.add_argument("--mode", choices=["live", "replay"], default="live",
                   help="agent only: replay serves cached responses and never contacts the provider")
    p.add_argument("--model", help="agent model (default: [agent].model in config)")
    p.add_argument("--agent-scope", choices=["all", "non_resolved"],
                   help="agent reviews every authorized case or only weak/unresolved ones (default: [agent].scope)")
    p.add_argument("--cases", help="comma-separated case_ids to run (default: every case of the split)")
    p.add_argument("--split", choices=sorted(REQUEST_FILES), default="targets")
    p.add_argument("--ownership", choices=["strict", "scored"], default="strict")
    p.add_argument("--dataset", default=str(REPO_ROOT / "dataset"))
    p.add_argument("--out", help="output directory (default runs/<run_id>/)")
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("explain", help="explain one case from a run's decision trace; never calls a model")
    p.add_argument("case_id")
    p.add_argument("--run", required=True)
    p.add_argument("--dataset", default=str(REPO_ROOT / "dataset"))
    p.add_argument("--md", help="write the explanation to this Markdown file")
    p.set_defaults(fn=cmd_explain)
    p = sub.add_parser("status")
    p.set_defaults(fn=cmd_status)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
