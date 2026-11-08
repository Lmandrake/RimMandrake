"""jobwatch.py -- step N single ticks and print every job change of the hostile pawns (def, target, giver).
  python.exe ralph/live/jobwatch.py [ticks=520]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fwb, story1  # noqa: E402

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 520
    B = fwb.FW()
    last = {}
    first = True
    for t in range(n):
        r = B.call("jawa/pawn_census", faction="hostile", includeDead=False) or {}
        for p in r.get("pawns") or []:
            if first:
                print("FIELDS", sorted(p.keys())); print("JOB", json.dumps(p.get("job") or p.get("curJob"), default=str)[:600]); first = False
            j = p.get("job") or p.get("curJob")
            key = json.dumps(j, sort_keys=True, default=str)
            if last.get(p["id"]) != key:
                print(t, p.get("name"), p.get("x"), p.get("z"), key[:400], flush=True)
                last[p["id"]] = key
        B.step(1)
main()
