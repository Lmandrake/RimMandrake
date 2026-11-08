"""g8_paramcheck.py -- dump the live schema (declared parameter names) of every tool the g8 scripts call, as JSON lines,
so the call sites can be checked offline (python.exe ralph/live/g8_paramcheck.py > Transient/ralph_fw/g8_params.jsonl)."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fwb  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
here = os.path.dirname(os.path.abspath(__file__))
used = set()
for f in os.listdir(here):
    if f.startswith("g8_") and f.endswith(".py"):
        used |= set(re.findall(r'"((?:jawa|rimworld)/[a-z_]+)"', open(os.path.join(here, f), encoding="utf-8").read()))
B = fwb.FW()
tl = B.S.list_tools()
names = set()
for t in tl:
    n = t.get("name")
    names.add(n)
    if n in used:
        props = (t.get("inputSchema") or t.get("parameters") or {}).get("properties") or {}
        print(json.dumps({"tool": n, "params": sorted(props)}))
for n in sorted(used - names):
    print(json.dumps({"tool": n, "missing": True}))
