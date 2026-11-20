"""load_save.py <saveName>: load a save on the live game through the bridge and wait for Playing (visit 2 helper).
exit 0 loaded, 2 not loaded (the cause printed)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6, "src", "RimMandrake", "Utils"))
import validation_core as V  # noqa: E402

B = V.Bridge()
ld = B.call("rimworld/load_game", saveName=sys.argv[1]) or {}
print("load_game:", str(ld)[:300])
ok = V._wait_playing(B)
print("playing:", ok, "map:", str(B.call("jawa/map_info") or {})[:300])
sys.exit(0 if ok else 2)
