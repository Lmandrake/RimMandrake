import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

with rb() as b:
    roots = b.call("rimworld/list_debug_action_roots", {})
    print("ROOTS:", json.dumps(roots.get("roots") or roots.get("children"))[:600])
