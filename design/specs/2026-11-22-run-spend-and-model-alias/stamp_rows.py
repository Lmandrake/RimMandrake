#!/usr/bin/env python3
"""One-time repair (2026-11-22): stamp each committed spend row that has no token_unit, so that
role_launch.stored_unit (stamp, else weighted_v1) reads every row right and the time switch can go.

The unit of a row is its own run record's unit (role_launch.stored_unit of the detached record that its `unit` names).
A row with no run record takes the verdict of the old time rule (weighted_v1 before 2026-11-16 23:05 PST, or with no
`at`; weighted_v2 after). Usage: python3 stamp_rows.py [--apply]. Without --apply it prints the plan and writes nothing.
"""
import datetime as dt
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "src", "RimMandrake", "rimflow"), os.path.join(ROOT, "src", "RimMandrake", "Utils")]
import role_launch as RL  # noqa: E402
import maturation as M  # noqa: E402

DETACHED = "/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached"
SWITCH = dt.datetime(2026, 11, 16, 23, 5, tzinfo=dt.timezone(dt.timedelta(hours=-8))).timestamp()


def by_time(row):
    t = M._instant(row.get("at")) if row.get("at") is not None else None
    return RL.TOKEN_UNIT if t is not None and t >= SWITCH else RL.V1_UNIT


def main(argv):
    apply = "--apply" in argv
    if not os.path.isdir(DETACHED):
        print("could not look: %s" % DETACHED)
        return 2
    runs = {}
    for f in glob.glob(os.path.join(DETACHED, "*.json")):
        try:
            r = json.load(open(f))
        except (OSError, ValueError):
            continue
        if isinstance(r, dict) and r.get("unit"):
            runs[r["unit"]] = r
    tally = {}

    def stamp(row):
        if isinstance(row.get("token_unit"), str) and row["token_unit"].strip():
            return False
        run = runs.get(M._unit_of(row))
        u = RL.stored_unit(run) if run is not None else by_time(row)
        how = "its run record" if run is not None else "the time rule (no run record)"
        k = (u, how, "time rule agrees" if u == by_time(row) else "TIME RULE DIFFERS")
        tally[k] = tally.get(k, 0) + 1
        row["token_unit"] = u
        return True

    files = subprocess.run(["git", "-C", ROOT, "ls-files", "*version/run_spend.jsonl", "*version/stage_record.json"],
                           capture_output=True, text=True).stdout.split()
    changed = []
    for f in files:
        p = os.path.join(ROOT, f)
        mod = f.split("/")[-3]
        if f.endswith(".jsonl"):
            rows = [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]
            if any([stamp(x) for x in rows]):
                changed.append(f)
                if apply:
                    M.write_text(ROOT, mod, M.RUN_SPEND, "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows))
        else:
            lk = M._mod_lock(ROOT, mod)
            try:
                rec = M.load(ROOT, mod)
                if any([stamp(x) for x in rec.get("spend") or []]):
                    changed.append(f)
                    if apply:
                        M.write_text(ROOT, mod, M.RECORD, M.dump(rec))
            finally:
                lk.close()
    for k, n in sorted(tally.items()):
        print("  stamped %-12s from %-30s %-18s %4d" % (k + (n,)))
    print("%s %d rows in %d files" % ("STAMPED" if apply else "PLAN (no --apply):", sum(tally.values()), len(changed)))
    for f in changed:
        print("  " + f)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
