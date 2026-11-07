"""Print every death letter's label and text from game B. Run on Steve through ralph/steve.sh run 'python.exe ralph/live/deaths.py'."""
import json, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint()
s = rb.RimBridge(host=h, port=p, token=t, timeout=120.0)
s.connect()
r = s.call("rimworld/list_letters", {}) or {}
if isinstance(r, dict) and r.get("content"):
    r = json.loads(r["content"][0]["text"])
for l in r.get("letters", []):
    txt = " ".join(str(l.get(k) or "") for k in ("text", "description", "body"))
    if "Death" in str(l.get("label")) or "died" in txt or "killed" in txt:
        print(l.get("label"), "|", txt.replace("\n", " ")[:500])
