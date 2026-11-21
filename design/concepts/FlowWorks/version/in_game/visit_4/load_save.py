"""load_save.py <saveName> [--ignore-missing-mods]: load a save on the live game through the bridge and wait for Playing
(visit 3 helper). exit 0 loaded, 2 not loaded (the cause printed).

--ignore-missing-mods passes ignoreModCompatibility: a save made with a mod the current tier forbids (SITTING_20261114_PIT_FIXES
holds mandrake.rut.pyrelandsmechanics, which the evening_20261113 tier now forbids) loads without that mod's content."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6, "src", "RimMandrake", "Utils"))
import validation_core as V  # noqa: E402

B = V.Bridge()
args = {"saveName": sys.argv[1]}
if "--ignore-missing-mods" in sys.argv:
    args["ignoreModCompatibility"] = True
ld = B.call("rimworld/load_game", **args) or {}
print("load_game:", str(ld)[:300])
got = V._wait_playing(B)
# _wait_playing returns (ok, state): the tuple itself is always truthy, so read its first element
ok = got[0] if isinstance(got, tuple) else bool(got)
print("playing:", got, "map:", str(B.call("jawa/map_info") or {})[:300])
sys.exit(0 if ok else 2)
