#!/bin/bash
# Acceptance test for RIMMANDRAKE_SHARE_PYRELANDS_SITE_LOAD_BETWEEN_SHORT_CHAINS. Exit 0 pass, 1 fail, 2 could not look.
# Usage: bash <this file> [--day YYYY-MM-DD --from HH:MM --to HH:MM --port 5175 --limit 20]   |   bash <this file> --selftest
# Reads the bridge telemetry E:\telemetry\raw\bridge\<day>.jsonl.gz (/mnt/e/telemetry/raw/bridge/) and counts rimworld/load_game calls
# on the visit's port inside its window. Default = Pyrelands visit 7 (11-23 05:00 to 08:56, port 5175): reads 61 today.
# The study counted 48 "site reloads" by load ACTS (menu+load+poll groups); this reader counts the load_game call itself, so its number
# is higher and is its own yardstick, not the study's. Limit 20 = the study's target of about 20 loads [guess ~50%]: OUR OWN rule.
# Run it on the first Pyrelands visit after the change, with that visit's --day/--from/--to; it is red on visit 7 by construction.
cd "$(dirname "$0")/../../.." || exit 2
exec python3 -I - "$@" <<'PY'
import sys, json, gzip, os, tempfile, io, contextlib
def count(lines, port, a, b):
    n = rows = 0
    for l in lines:
        try: d = json.loads(l)
        except Exception: continue
        if d.get("ev") != "start" or not d.get("endpoint", "").endswith(":" + port): continue
        if not (a <= d["t"] < b): continue
        rows += 1
        if d.get("tool") == "rimworld/load_game": n += 1
    return n, rows
def judge(path, port, a, b, limit):
    try: n, rows = count(gzip.open(path, "rt", encoding="utf-8"), port, a, b)
    except Exception as e: print("could not look: %s" % e); return 2
    if rows == 0: print("could not look: no calls on port %s in the window (empty visit or wrong window)" % port); return 2
    print("calls in the window %d; rimworld/load_game calls %d (limit %d, our own rule)" % (rows, n, limit))
    return 0 if n <= limit else 1
if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
    d = tempfile.mkdtemp(); ok = True
    def mk(name, n_loads, other=5, port="127.0.0.1:5175"):
        p = os.path.join(d, name)
        with gzip.open(p, "wt") as f:
            for i in range(n_loads): f.write(json.dumps({"ev": "start", "endpoint": port, "t": "2026-11-23T06:%02d:00Z" % i, "tool": "rimworld/load_game"}) + "\n")
            for i in range(other): f.write(json.dumps({"ev": "start", "endpoint": port, "t": "2026-11-23T06:%02d:30Z" % i, "tool": "jawa/map_info"}) + "\n")
        return p
    cases = [("48 loads -> red", mk("a", 48), 1), ("12 loads -> green", mk("b", 12), 0), ("no costly act (0 loads) -> green", mk("c", 0), 0),
             ("empty visit -> could not look", mk("d", 0, 0), 2), ("other port only -> could not look", mk("e", 30, 5, "127.0.0.1:5174"), 2),
             ("unreadable -> could not look", os.path.join(d, "none.gz"), 2)]
    for name, p, want in cases:
        with contextlib.redirect_stdout(io.StringIO()): got = judge(p, "5175", "2026-11-23T05:00", "2026-11-23T08:57", 20)
        if got != want: ok = False; print("SELFTEST FAIL:", name, got, want)
    print("SELFTEST OK" if ok else "SELFTEST FAILED"); sys.exit(0 if ok else 1)
a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
day = a.get("--day", "2026-11-23")
sys.exit(judge("/mnt/e/telemetry/raw/bridge/%s.jsonl.gz" % day, a.get("--port", "5175"), "%sT%s" % (day, a.get("--from", "05:00")), "%sT%s" % (day, a.get("--to", "08:57")), int(a.get("--limit", 20))))
PY
