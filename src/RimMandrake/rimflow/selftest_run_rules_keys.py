#!/usr/bin/env python3
"""Selftest: every key in run_rules.json is one some live tool still reads (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES).

run_rules.json was the retired Relentless tick's rules file; the tick's own keys went with it (2026-11-18). A key
is LIVE when a non-test file under rimflow/, Utils/ or .claude/hooks/ quotes its name ("key" or 'key'). Checked: the
top level and the live and walls blocks. A `_x` comment key needs its sibling `x` (or is the file's `_`).
Static on purpose: a common word ("enabled", "seat") passes by another file's use of it, so this catches a key
nothing names at all, not every dead one. A planted dead key and an orphaned comment must both be refused.

    python3 src/RimMandrake/rimflow/selftest_run_rules_keys.py
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RULES = os.path.join(HERE, "run_rules.json")
BLOCKS = ("live", "walls")


def live_sources():
    pats = ("src/RimMandrake/rimflow/*.py", "src/RimMandrake/Utils/*.py", "src/RimMandrake/Utils/*/*.py",
            ".claude/hooks/*.py")
    files = [f for p in pats for f in glob.glob(os.path.join(ROOT, p)) if not os.path.basename(f).startswith("selftest")]
    out = []
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as fh:
            out.append(fh.read())
    if len(out) < 50:
        raise SystemExit("UNMEASURED: only %d source files found under %s; the scan cannot see" % (len(out), ROOT))
    return "\n".join(out)


def problems(rules, text):
    out = []

    def scan(d, where):
        for k in d:
            if k == "_":
                continue
            if k.startswith("_"):
                if k[1:] not in d:
                    out.append("%s%s: a comment whose key is gone" % (where, k))
            elif not re.search(r"""["']%s["']""" % re.escape(k), text):
                out.append("%s%s: no live file reads it" % (where, k))
    scan(rules, "")
    for b in BLOCKS:
        if isinstance(rules.get(b), dict):
            scan(rules[b], b + ".")
    return out


def main():
    with open(RULES, encoding="utf-8") as f:
        rules = json.load(f)
    text = live_sources()
    fails = 0
    probs = problems(rules, text)
    print(("PASS" if not probs else "FAIL") + " every run_rules.json key is read by live code" +
          ("" if not probs else ": %d dead\n  " % len(probs) + "\n  ".join(probs)))
    fails += bool(probs)
    planted = problems(dict(rules, zz_never_read_key=1), text)
    ok = any("zz_never_read_key" in p for p in planted)
    print(("PASS" if ok else "FAIL") + " a planted dead key is refused")
    fails += not ok
    orphan = problems(dict(rules, _zz_gone="a comment"), text)
    ok = any("_zz_gone" in p for p in orphan)
    print(("PASS" if ok else "FAIL") + " a comment whose key is gone is refused")
    fails += not ok
    print("FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
