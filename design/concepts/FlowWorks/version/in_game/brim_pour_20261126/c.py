"""c.py TOOL JSON | c.py static TYPE METHOD ARGS  - one live bridge call, prints the reply's result text or JSON."""
import json, os, sys
sys.path.insert(0, os.path.join(os.environ["RM_REPO"], "src", "RimMandrake", "Utils"))
import rimbridge_client as R
h, p, t = R.discover_from_log() if hasattr(R, "discover_from_log") else (None, None, None)
h = os.environ.get("RIMBRIDGE_HOST", h or "127.0.0.1"); p = int(os.environ.get("GABP_SERVER_PORT", p)); t = os.environ.get("GABP_TOKEN", t)
with R.RimBridge(h, p, t) as rb:
    if sys.argv[1] == "static":
        r = rb.call("jawa/static_call", {"type": sys.argv[2], "method": sys.argv[3], "args": sys.argv[4] if len(sys.argv) > 4 else ""})
    else:
        r = rb.call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
    if isinstance(r, dict) and "result" in r and isinstance(r["result"], str):
        print(r["result"])
    else:
        if isinstance(r, dict): r.pop("operation", None); r.pop("state", None)
        print(json.dumps(r)[:4000])
