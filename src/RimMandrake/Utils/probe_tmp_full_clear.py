#!/usr/bin/env python3
"""Proof probe for OPS_TMP_DRAIN_RESTORE_JVCO: is the HOST /tmp under every TMP_FULL line right now?

A walled checker's own /tmp is a private bind (findmnt shows the box's ext4, not the host tmpfs), so
shutil.disk_usage('/tmp') inside the box proves nothing about the alarm. This reads the alarm's own
instrument instead: the newest row of ops_watch's disk series ($RM_OPS_WATCH_DIR/series/disk.jsonl,
default D:\\ClaudeWork\\rimmandrake\\ops_watch), and every rule tagged TMP_FULL in ops_watch_rules.json
(the lines are read, never typed here).

exit 0  every TMP_FULL key is MEASURED in the newest row, the row is fresh, and none crosses its line
exit 1  a TMP_FULL line is crossed
exit 2  UNMEASURED: no series, stale row (older than --max-age-h, default 3), a key missing or not MEASURED
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPS = {">": lambda v, x: v > x, "<": lambda v, x: v < x, ">=": lambda v, x: v >= x, "<=": lambda v, x: v <= x}


def unmeasured(why: str) -> None:
    print("UNMEASURED: " + why)
    sys.exit(2)


def last_line(p: Path) -> str:
    with open(p, "rb") as f:
        f.seek(0, 2)
        n = f.tell()
        f.seek(max(0, n - 65536))
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    if not lines:
        unmeasured("%s is empty" % p)
    return lines[-1].decode("utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age-h", type=float, default=3.0)
    ap.add_argument("--rules", default=str(HERE / "ops_watch_rules.json"))
    a = ap.parse_args()
    rules = []

    def walk(o):  # the rules sit nested under several sections; collect every TMP_FULL rule wherever it is
        if isinstance(o, dict):
            if o.get("tag") == "TMP_FULL" and o.get("op") in OPS and "key" in o and "value" in o:
                rules.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(json.load(open(a.rules, encoding="utf-8")))
    if not rules:
        unmeasured("no TMP_FULL rule in %s" % a.rules)
    store = Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))
    series = store / "series" / "disk.jsonl"
    if not series.is_file():
        unmeasured("no disk series at %s" % series)
    row = json.loads(last_line(series))
    at = datetime.strptime(row["at"], "%Y-%m-%dT%H:%M:%SZ")
    age_h = (time.time() - (at - datetime(1970, 1, 1)).total_seconds()) / 3600
    if age_h > a.max_age_h:
        unmeasured("newest disk row %s is %.1f h old (max %.1f h)" % (row["at"], age_h, a.max_age_h))
    crossed = []
    for r in rules:
        pt = row.get("points", {}).get(r["key"])
        if not isinstance(pt, dict) or pt.get("m") != "MEASURED" or not isinstance(pt.get("v"), (int, float)):
            unmeasured("%s not MEASURED in the row at %s: %r" % (r["key"], row["at"], pt))
        hit = OPS[r["op"]](pt["v"], r["value"])
        print("%s %s = %s (alarm when %s %s) at %s" % ("CROSSED" if hit else "ok", r["key"], pt["v"], r["op"],
                                                      r["value"], row["at"]))
        if hit:
            crossed.append(r["key"])
    if crossed:
        print("FAIL: host /tmp crosses TMP_FULL: " + ", ".join(crossed))
        sys.exit(1)
    print("PASS: host /tmp under every TMP_FULL line (%d rules)" % len(rules))


if __name__ == "__main__":
    main()
