import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

data = json.loads(open(r"D:\Luke\dev\Rimworld\Transient\desert_build_calls.json", encoding="utf-8").read())

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for name, entry in data.items():
        print(f"=== {name}: {len(entry['calls'])} calls (rect {entry['rect']}) ===")
        for note in entry["notes"]:
            print("  NOTE:", note)
        for c in entry["calls"]:
            res = rb.call(c["tool"], c["params"])
            ok = res.get("success")
            if not ok:
                print("  FAIL", c["tool"], json.dumps(c["params"])[:200], "->", res.get("message"))
        print(f"  done {name}")
