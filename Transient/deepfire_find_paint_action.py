import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r

roots = call("rimworld/list_debug_action_roots")
actions_path = None
for r in roots.get("roots", []):
    if r.get("label") == "Actions" or r.get("path", "").endswith("Actions"):
        actions_path = r.get("path")
        break
print("actions path:", actions_path)

ch = call("rimworld/list_debug_action_children", path=actions_path)
matches = [c for c in ch.get("children", []) if "Paint" in c.get("path", "")]
for m in matches:
    print(m.get("path"), "|", m.get("actionType"), "|", m.get("hasChildren"))
