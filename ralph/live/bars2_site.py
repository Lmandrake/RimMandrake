"""bars2_site.py -- one wide look at the candidate staging ground east of the story compound, plus the game state."""
import sys
from bars2_common import bridge, shot, log, j

B = bridge()
gi = B.call("rimworld/get_game_info") or {}
log("game", j(gi.get("state"), 400))
cen = B.call("jawa/pawn_census", faction="player") or {}
log("player pawns", [(p.get("id"), p.get("kindDef"), p.get("x"), p.get("z"), p.get("downed")) for p in cen.get("pawns") or []])
x, z, w, h = (int(v) for v in (sys.argv[1:5] if len(sys.argv) > 4 else (150, 85, 80, 80)))
shot(B, "site_%d_%d" % (x, z), (x, z, w, h), root=max(w, h) * 0.55)
