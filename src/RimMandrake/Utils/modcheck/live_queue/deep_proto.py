"""deep_proto: UNPROVEN prototype for DEEP_LAYER_BELT_HARNESS_1 -- reach a real Lantern Deep pocket map from the bland map.

    python.exe src/RimMandrake/Utils/modcheck/live_queue/deep_proto.py        (game up on a bland map, bridge held)

Why: LanternDeeps' creep / aurora / hydrocarbon / hush proofs read 'no map, comp or kind (comp only on a Deep)' because
RM_LanternDeepGenerator.customMapComponents (RM_MapComponent_Creep, _DeepAurora, _DeepCollapse...) are attached only to a
pocket map generated from that MapGeneratorDef; they are never auto-added to the bland map.
The route a PLAYER takes: the 5x5 MapPortal RM_LanternDeepMineshaft (isTargetable false) -> a colonist enters -> the pocket map is
generated. This script tries exactly that through the bridge: spawn the portal beside the colony, order a colonist to EnterPortal
(jobDef from vanilla JobDefOf.EnterPortal), then walk set_current_map over map ids and print each map's biome/tile so the Deep can
be found. NOTHING HERE HAS RUN: first live reading goes in the LanternDeeps script, then this becomes bland_world.enter_deep()
(restore: jawa/map_drop on the pocket map, set_current_map back to the bland map).
"""
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
for p in (_HERE, os.path.join(_HERE, "..", "..", "rimbench"), os.path.join(_HERE, "..", "..")):
    sys.path.insert(0, p)
from common import call, open_session   # noqa: E402


def j(x, n=700):
    return json.dumps(x, default=str)[:n]


def main():
    with open_session(False) as s:
        info = call(s, "jawa/map_info")
        print("map", j(info, 400))
        cx, cz = int(info.get("sizeX", 250)) // 2, int(info.get("sizeZ", 250)) // 2
        print("spawn", j(call(s, "jawa/spawn_batch", ops="RM_LanternDeepMineshaft:%d,%d" % (cx + 20, cz + 20))))
        t = call(s, "jawa/list_things", defName="RM_LanternDeepMineshaft", limit=5)
        pid = ((t.get("things") or [{}])[0]).get("id")
        cols = [q for q in (call(s, "jawa/list_pawns", limit=20).get("pawns") or [])
                if q.get("isPlayer") and q.get("intelligence") == "Humanlike"]
        print("portal", pid, "colonists", [c["id"] for c in cols][:3])
        if not (pid and cols):
            return 1
        print("job", j(call(s, "jawa/ordered_job", pawnId=cols[0]["id"], jobDef="EnterPortal", targetAId=pid,
                            waitTicks=600, timeoutSeconds=60), 900))
        time.sleep(3)
        for mid in range(0, 5):
            print("map", mid, j(call(s, "jawa/set_current_map", mapId=mid), 160))
            mi = call(s, "jawa/map_info")
            print("   ", j({k: mi.get(k) for k in ("mapBiome", "tile", "sizeX", "mapIndex")}, 300))
        return 0


if __name__ == "__main__":
    sys.exit(main())
