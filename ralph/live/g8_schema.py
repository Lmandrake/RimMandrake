"""g8_schema.py tool [tool...] : print the live schema + description of each named tool (debug helper for the g8_* scripts)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fwb  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = fwb.FW()
r = B.S.list_tools() if hasattr(B.S, "list_tools") else B.tools()
tl = r.get("tools") if isinstance(r, dict) else r
want = set(sys.argv[1:])
for t in tl or []:
    n = t.get("name") if isinstance(t, dict) else str(t)
    if n in want:
        print("==", n)
        print(json.dumps(t.get("inputSchema") or t.get("parameters") or {}, default=str)[:2500])
        print("   ", (t.get("description") or "")[:1500])
