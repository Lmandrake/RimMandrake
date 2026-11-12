#!/usr/bin/env python3
"""regrade.py - a small independent regrade of closed items, with the owner's noise guard.

Spec: design/RimMandrake/relentless_improvement_loop_2026-11-03.md (loop step 5 and "Regrade noise guard"); item
REGRADE_SAMPLE_BUILD_NOISE_GUARDED. Owner, 2026-11-03: "there's a lot of noise in these regradings, and I'd hate this to
turn into a rabbit hole chasing noise." So:

  - a handful a day at most: `draw` takes at most CAP closed items per UTC day, never one regraded before;
  - a disagreement is RECORDED, never chased alone: one grader's VIOLATED is listed as "recorded, not acted on";
  - act only when two independent graders (distinct --by) call the same item VIOLATED, or the same kind of
    disagreement (the plain --tag sentence) is VIOLATED on two or more items;
  - if two weeks after the first draw nothing has held up (nothing actionable), it is STOPPED: `draw` refuses.

The record is delivery_metrics' audit record (infrastructure/state/close_audits.jsonl): a regrade sample is a `draw`
named R<YYYYMMDD> in the `random` stratum, a grade is an `audit` row plus a `tag`. So every regrade also counts in the
false-close metric there. The daily caller is the findings judge (src/RimMandrake/Utils/findings_judge_prompt.md).

    python3 src/RimMandrake/rimflow/regrade.py draw [--n 3]
    python3 src/RimMandrake/rimflow/regrade.py grade <SAMPLE> <ITEM> HOLDS|VIOLATED|UNMEASURED --by WHO \
        --how "what the grader ran or read" --evidence "what it showed" [--tag "one plain sentence: what was wrong"]
    python3 src/RimMandrake/rimflow/regrade.py report [--json]      # exit 0 running, 3 stopped, 2 damaged record

A tag reads cold to a human (spec, "Tags must be plain"): e.g. "The test checked the file, not the running game."
Acting on an ACT line is filing an item (rimflow namecheck/file); this tool never files, reopens or closes anything.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import delivery_metrics as dm                     # noqa: E402

CAP = 3                     # closed items regraded per UTC day, at most ("a handful of items a day, at most")
STOP_DAYS = 14              # "if after two weeks it has found nothing that held up, stop it"
PREFIX = "R"                # regrade samples are R<YYYYMMDD>; delivery_metrics' own samples are S<...>
_SAMPLE = re.compile(r"^R\d{8}$")


def _day(t):
    return dm.iso(t)[:10].replace("-", "")


def regrade_rows(audits):
    """Rows of the audit record that belong to the regrade (samples named R<YYYYMMDD>)."""
    return [r for r in audits if _SAMPLE.match(str(r.get("sample") or ""))]


def pick(snap, audits, now, n=CAP):
    """-> draw rows for today's regrade sample: at most CAP minus what today already drew, seeded by the date, over every
    close no regrade drew before. Refuses (SystemExit) when stopped."""
    st = status(audits, now)
    if st["state"] == "STOPPED":
        raise SystemExit("STOPPED: %s" % st["why"])
    if snap["states"] is None:
        raise SystemExit("UNMEASURED: no item states in %s" % snap["store"])
    name = PREFIX + _day(now)
    rg = regrade_rows(audits)
    today = sum(1 for r in rg if r["kind"] == "draw" and r["sample"] == name)
    room = max(0, min(n, CAP - today))
    if today >= CAP:
        raise SystemExit("CAP: %s already holds %d of %d regrades for today" % (name, today, CAP))
    seen = {r["item"] for r in rg if r["kind"] == "draw"}
    cl = dm.closes(snap["states"])
    pool = sorted(set(cl) - seen)
    seed = int(_day(now))
    picks = sorted(random.Random(seed + today).sample(pool, min(room, len(pool))))
    pool_sha = hashlib.sha1("\n".join(pool).encode()).hexdigest()
    rows = []
    for i in picks:
        s = snap["states"].get(i) or {}
        at, verdict, _ = cl[i]
        rows.append({"kind": "draw", "sample": name, "stratum": "random", "item": i, "at": dm.iso(now), "seed": seed,
                     "population": len(pool), "population_sha1": pool_sha, "closed_at": dm.iso(at) if at else None,
                     "sha": s.get("last_sha"), "verdict": verdict, "proof": ((s.get("contract") or {}).get("proof") or ""),
                     "source": "store", "reasons": None, "regrade": True})
    return rows


def grade_row(audits, sample, item, verdict, by, how, evidence, tag, now):
    """-> one audit row with its tag. A VIOLATED needs a plain tag; a grader grades an item once (independence)."""
    if not _SAMPLE.match(sample):
        raise SystemExit("%s is not a regrade sample (R<YYYYMMDD>)" % sample)
    tag = " ".join((tag or "").split())
    if verdict == "VIOLATED" and not tag:
        raise SystemExit("a VIOLATED regrade names its kind: --tag \"one plain sentence: what was wrong\"")
    if any(r["kind"] == "audit" and r["item"] == item and r["by"].strip().lower() == by.strip().lower()
           for r in regrade_rows(audits)):
        raise SystemExit("%s already graded %s; a second grade must come from a different grader" % (by, item))
    row = dm.audit_row(audits, sample, item, verdict, by, how, evidence, now)
    if tag:
        row["tag"] = tag
    return row


def _norm(tag):
    return re.sub(r"[^a-z0-9 ]", "", tag.lower()).strip()


def findings(audits):
    """-> {"act": [...], "recorded": [...]}: the noise guard. ACT rows are an item two distinct graders call VIOLATED, or a
    tag VIOLATED on two or more items; every other VIOLATED is recorded, not acted on."""
    grades = [r for r in regrade_rows(audits) if r["kind"] == "audit"]
    by_item, by_tag = {}, {}
    for r in grades:
        if r["verdict"] != "VIOLATED":
            continue
        by_item.setdefault(r["item"], {})[r["by"].strip().lower()] = r
        if r.get("tag"):
            by_tag.setdefault(_norm(r["tag"]), {"tag": r["tag"], "items": {}})["items"].setdefault(r["item"], r)
    act, acted = [], set()
    for i, graders in sorted(by_item.items()):
        if len(graders) >= 2:
            act.append({"why": "two graders agree", "item": i, "by": sorted(r["by"] for r in graders.values()),
                        "tags": sorted({r.get("tag") or "" for r in graders.values()} - {""})})
            acted.add(i)
    for k, t in sorted(by_tag.items()):
        if len(t["items"]) >= 2:
            act.append({"why": "the same kind repeats", "tag": t["tag"], "items": sorted(t["items"])})
            acted.update(t["items"])
    recorded = [{"item": i, "by": r["by"], "tag": r.get("tag"), "at": r["at"]}
                for i, graders in sorted(by_item.items()) if i not in acted for r in graders.values()]
    return {"act": act, "recorded": recorded}


def status(audits, now):
    """-> {"state": NOT_STARTED|RUNNING|STOPPED, ...}. STOPPED once STOP_DAYS have passed since the first regrade draw
    with nothing actionable; anything actionable keeps it running."""
    draws = [r for r in regrade_rows(audits) if r["kind"] == "draw"]
    if not draws:
        return {"state": "NOT_STARTED", "why": "no regrade drawn yet"}
    first = min(dm.ep(r["at"]) for r in draws)
    days = (now - first) / 86400.0
    held = findings(audits)["act"]
    base = {"first_draw": dm.iso(first), "days": round(days, 1), "drawn": len(draws),
            "graded": sum(1 for r in regrade_rows(audits) if r["kind"] == "audit"), "actionable": len(held)}
    if days >= STOP_DAYS and not held:
        return dict(base, state="STOPPED", why="%d days since the first regrade (%s) and nothing held up: stopped, as the "
                    "owner asked; filing an item to restart it is a Conductor call" % (int(days), dm.iso(first)[:10]))
    return dict(base, state="RUNNING", why="%s; %d actionable" % ("%.1f of %d days" % (days, STOP_DAYS), len(held)))


def render(st, f, today_left):
    out = ["REGRADE %s - %s" % (st["state"], st["why"])]
    if st["state"] == "RUNNING":
        out.append("today: %d of %d draws left" % (today_left, CAP))
    for a in f["act"]:
        if a["why"] == "two graders agree":
            out.append("ACT %s: two graders agree it is wrong (%s)%s" % (a["item"], ", ".join(a["by"]),
                       (" - " + " / ".join(a["tags"])) if a["tags"] else ""))
        else:
            out.append("ACT kind repeats on %d items: \"%s\" (%s)" % (len(a["items"]), a["tag"], ", ".join(a["items"])))
    for r in f["recorded"]:
        out.append("recorded, not acted on: %s by %s - %s" % (r["item"], r["by"], r.get("tag") or "(no tag)"))
    return "\n".join(out)


def main(argv=None, now=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--store", default=dm.STORE)
    ap.add_argument("--audits", default=dm.AUDITS)
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("report")
    r.add_argument("--json", action="store_true")
    d = sub.add_parser("draw")
    d.add_argument("--n", type=int, default=CAP)
    g = sub.add_parser("grade")
    g.add_argument("sample")
    g.add_argument("item")
    g.add_argument("verdict")
    g.add_argument("--by", required=True)
    g.add_argument("--how", required=True)
    g.add_argument("--evidence", required=True)
    g.add_argument("--tag")
    args = ap.parse_args(argv)
    now = now if now is not None else dt.datetime.now(dt.timezone.utc).timestamp()
    bad = {}
    audits = dm._jsonl(args.audits, bad)
    hurt = dm.damaged(audits)
    if bad or hurt:
        sys.stderr.write("DAMAGED: %s: %s - repair it before trusting a regrade\n"
                         % (args.audits, "; ".join(hurt[:5]) or "%d unparsed line(s)" % sum(bad.values())))
        if args.cmd in ("draw", "grade"):
            return 2
        audits = [x for x in audits if not dm.damaged([x], refs=False)]
    if args.cmd == "draw":
        rows = pick(dm.load(args.store), audits, now, args.n)
        dm.append(rows, args.audits)
        for x in rows:
            print(x["sample"], x["item"], x["sha"] or "-")
        if not rows:
            print("nothing to draw: every close has been regraded")
        return 0
    if args.cmd == "grade":
        dm.append([grade_row(audits, args.sample, args.item, args.verdict.upper(), args.by, args.how, args.evidence,
                             args.tag, now)], args.audits)
        return 0
    st, f = status(audits, now), findings(audits)
    today = sum(1 for x in regrade_rows(audits) if x["kind"] == "draw" and x["sample"] == PREFIX + _day(now))
    if getattr(args, "json", False):
        print(json.dumps({"status": st, "findings": f, "today_left": max(0, CAP - today)}, indent=1, sort_keys=True))
    else:
        print(render(st, f, max(0, CAP - today)))
    if bad or hurt:
        return 2
    return 3 if st["state"] == "STOPPED" else 0


if __name__ == "__main__":
    sys.exit(main())
