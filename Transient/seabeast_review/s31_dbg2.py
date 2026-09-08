import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

with rb() as b:
    ch = b.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    hits = [c["path"] for c in ch if any(k in c["label"].lower() for k in ("fog", "reveal", "regenerate", "redraw", "light", "glow"))]
    print("HITS:", hits)
