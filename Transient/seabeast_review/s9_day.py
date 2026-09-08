import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

with rb() as b:
    gi = b.call("rimworld/get_game_info", {})
    print("GAMEINFO:", json.dumps({k: v for k, v in gi.items() if k != "operation"})[:900])
    cs = b.call("rimworld/get_camera_state", {})
    print("CAM:", json.dumps({k: v for k, v in cs.items() if k != "operation"})[:500])
