#!/usr/bin/env python3
"""The criteria ledger — how the art-eval pipeline learns (skill `rimworld-art-evaluation`,
references/criteria_ledger.md).

Owner, 2026-10-23: *"If Human live walk notices a problem, look back and improve evaluation criteria or process
that generated the issue."* Every owner override on a shadow sheet, every live-walk finding about art the pipeline
passed, and every disagreement with a past owner verdict becomes ONE entry: what was missed, then (when fixed)
which check / prompt line / policy row changed, the prompt versions before and after, and the regression example
added so the miss can never silently return.

    python3 ledger.py add --subject RM_X --template creature --source owner_override \
        --owner-said "<his words>" --missed "<what the pipeline got wrong>" --decision REGEN [--run <run id>]
    python3 ledger.py fix CL-001 --change "<what changed, where>" --files <paths> \
        --regression RM_X:B --expect ACCEPT
    python3 ledger.py list [--open]

Files: infrastructure/state/art_eval/criteria_ledger.jsonl (append-only events) and regression.jsonl (one row per
regression example; `runner.py regress` re-runs them all on the current prompt versions).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy as P  # noqa: E402

STATE = P.ROOT / "infrastructure/state/art_eval"
SOURCES = ("owner_override", "live_walk", "owner_key", "agent_review")


def _now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def events(path: Path | None = None) -> list:
    p = path or STATE / "criteria_ledger.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.is_file() else []


def entries(path: Path | None = None) -> dict:
    """Fold the event log into one entry per id."""
    out = {}
    for e in events(path):
        if e["event"] == "add":
            out[e["id"]] = dict(e, status="open", fixes=[])
        elif e["event"] == "fix" and e["id"] in out:
            out[e["id"]]["fixes"].append(e)
            out[e["id"]]["status"] = "fixed"
        elif e["event"] == "note" and e["id"] in out:
            out[e["id"]].setdefault("notes", []).append(e)
    return out


def _append(e: dict, path: Path | None = None):
    p = path or STATE / "criteria_ledger.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as fh:
        fh.write(json.dumps(e) + "\n")


def add(subject, template, source, missed, decision, owner_said=None, run=None, path=None) -> str:
    if source not in SOURCES:
        raise SystemExit(f"--source must be one of {SOURCES}")
    if source in ("owner_override", "live_walk") and not owner_said:
        raise SystemExit("an owner override or live-walk finding carries his words (--owner-said)")
    n = 1 + max([int(i.split("-")[1]) for i in entries(path)] or [0])
    cid = f"CL-{n:03d}"
    _append({"event": "add", "id": cid, "at": _now(), "subject": subject, "template": template, "source": source,
             "owner_said": owner_said, "missed": missed, "pipeline_decision": decision, "run": run}, path)
    return cid


def fix(cid, change, files, regression=None, expect=None, why=None, path=None, reg_path=None):
    if cid not in entries(path):
        raise SystemExit(f"{cid} is not in the ledger")
    v = {n: P.prompt_version(P.REFS / "prompts" / f"{n}.md")["tag"] for n in
         ("preamble", "opus_first_pass", "gpt_targeted_second_look", "regen_prompt_edit", "departures_brief")}
    for t in P.TEMPLATES:
        v[t] = P.prompt_version(P.REFS / "templates" / f"{t}.md")["tag"]
    v["severity"] = P.prompt_version(P.REFS / "severity_policy.md")["tag"]
    _append({"event": "fix", "id": cid, "at": _now(), "change": change, "files": files, "versions_after": v,
             "regression": regression, "expect": expect}, path)
    if regression:
        if expect not in ("ACCEPT", "NOT_ACCEPT"):
            raise SystemExit("--expect ACCEPT|NOT_ACCEPT with --regression")
        rp = reg_path or STATE / "regression.jsonl"
        with rp.open("a") as fh:
            fh.write(json.dumps({"pilot": regression, "expect": expect, "from": cid, "why": why or change}) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--subject", required=True); a.add_argument("--template", required=True, choices=P.TEMPLATES)
    a.add_argument("--source", required=True, choices=SOURCES); a.add_argument("--missed", required=True)
    a.add_argument("--decision", required=True); a.add_argument("--owner-said"); a.add_argument("--run")
    f = sub.add_parser("fix")
    f.add_argument("id"); f.add_argument("--change", required=True); f.add_argument("--files", nargs="+", required=True)
    f.add_argument("--regression"); f.add_argument("--expect", choices=("ACCEPT", "NOT_ACCEPT")); f.add_argument("--why")
    l = sub.add_parser("list"); l.add_argument("--open", action="store_true")
    o = ap.parse_args(argv)
    if o.cmd == "add":
        print(add(o.subject, o.template, o.source, o.missed, o.decision, o.owner_said, o.run))
    elif o.cmd == "fix":
        fix(o.id, o.change, o.files, o.regression, o.expect, o.why)
        print(f"{o.id} fixed")
    else:
        for e in entries().values():
            if o.open and e["status"] != "open":
                continue
            print(f"{e['id']} {e['status']:5} {e['subject']:18} {e['source']:14} {e['missed'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
