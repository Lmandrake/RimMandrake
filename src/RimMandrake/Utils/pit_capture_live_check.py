#!/usr/bin/env python3
"""PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP live verdict: read pit-walk result.json files (one per run dir given) and exit 0
only when every run's PSW_capture_down_from_lip row is PASS with no governor stop (a hurt warden stops the governor:
the row reads UNMEASURED with detail.why). Usage: pit_capture_live_check.py <run dir>..."""
import json
import os
import sys


def verdict(d):
    p = os.path.join(d, "result.json")
    if not os.path.exists(p):
        return "missing"
    rows = [r for r in json.load(open(p, encoding="utf-8")).get("rows", []) if r.get("id") == "PSW_capture_down_from_lip"]
    if not rows:
        return "absent"
    r = rows[0]
    return r.get("status", "?") + ("/stopped:" + str(r["detail"]["why"])[:80] if (r.get("detail") or {}).get("why") else "")


def main(dirs):
    if not dirs:
        print("usage: pit_capture_live_check.py <run dir>...")
        return 2
    got = [verdict(d) for d in dirs]
    print("PSW_capture_down_from_lip:", got)
    return 0 if got == ["PASS"] * len(dirs) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
