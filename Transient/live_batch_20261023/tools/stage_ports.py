"""stage_ports.py -- map C (save d in memory): one 2x2 tank per look with a reel+hose to each side (W lower, E upper, S, N),
plus a Scrapper cargo tank with W/E upper hoses and one side-arriving hose, plus a Repaired pumping station south port.
Prints each hose's coupling and writes Transient/live_batch_20261023/r3b/ports_stage.json."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\FlowWorks\northstar")
from rimbridge_client import RimBridge, resolve_endpoint
import joint_check as J
H, P, T = resolve_endpoint()
OUT = {"tanks": [], "hoses": []}
with RimBridge(H, P, T) as B:
    B.call("jawa/set_current_map", {"mapId": 0}); time.sleep(0.5)
    B.call("rimworld/set_god_mode", {"enabled": True})
    print("clear", json.dumps(B.call("jawa/destroy_batch", {"rects": "150,35,95,70", "categories": "All"}), default=str)[:200])
    def occ(x0, z0, x1, z1, d):
        cells = []
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                th = (B.call("rimworld/get_cell_info", {"x": x, "z": z}).get("cell") or {}).get("things") or []
                if any(t.get("defName") == d for t in th): cells.append((x, z))
        return cells
    def tank(d, x, z, style):
        r = B.call("jawa/build_batch", {"ops": "%s:%d,%d,0" % (d, x, z), "wipeExisting": False})
        c = occ(x - 2, z - 2, x + 2, z + 2, d)
        th = B.call("jawa/list_things", {"defName": d, "rect": "%d,%d,1,1" % c[0]}).get("things") or []
        st = B.call("jawa/set_thing_props", {"thing": str(th[0]["id"]), "style": style}) if th and style else None
        mx, mz = min(a for a, b in c), min(b for a, b in c)
        OUT["tanks"].append(dict(d=d, style=style, min=[mx, mz], cells=c, styled=(st or {}).get("success")))
        return mx, mz
    def hose(reel, target, label, rot=0):
        B.call("jawa/build_batch", {"ops": "RM_HoseReel:%d,%d,%d" % (reel[0], reel[1], rot), "wipeExisting": False})
        B.call("jawa/safe_advance", {"ticks": 2, "stopOn": "cancel", "timeoutMs": 30000})
        lay = J._probe(B, "lay:%d,%d,%d,%d" % (reel + target))
        OUT["hoses"].append(dict(label=label, reel=list(reel), target=list(target), lay=lay))
    looks = ["Scrapper", "Industrial", "Futuristic", "Modern"]
    for i, lk in enumerate(looks):
        x, z = 160 + i * 24, 60
        mx, mz = tank("RM_LiquidTankTall", x, z, "RM_LiquidTankTall_" + lk)
        hose((mx - 8, mz), (mx - 1, mz), lk + " tall W lower", 1)
        hose((mx + 9, mz + 1), (mx + 2, mz + 1), lk + " tall E upper", 3)
        hose((mx, mz - 9), (mx, mz - 1), lk + " tall S", 0)
        hose((mx + 1, mz + 10), (mx + 1, mz + 2), lk + " tall N", 2)
    mx, mz = tank("RM_UniversalCargoTank", 175, 85, "RM_UniversalCargoTank_Scrapper")
    tmx, tmz = OUT["tanks"][3]["min"]
    hose((mx - 8, mz + 1), (mx - 1, mz + 1), "Scrapper cargo W upper", 1)
    hose((mx + 9, mz + 1), (mx + 2, mz + 1), "Scrapper cargo E upper", 3)
    hose((mx - 4, mz - 9), (mx - 1, mz), "Scrapper cargo W lower from the SIDE (south)", 0)
    B.call("jawa/build_batch", {"ops": "RM_PumpingStation_Repaired:205,88,0", "wipeExisting": False})
    pc = occ(202, 85, 208, 91, "RM_PumpingStation_Repaired")
    OUT["station"] = pc
    B.call("jawa/safe_advance", {"ticks": 5, "stopOn": "cancel", "timeoutMs": 30000})
    cen = J._probe(B, "census")
    for h in OUT["hoses"]:
        m = [c for c in (cen.get("hoses") or []) if list(c.get("reel") or [])[:2] == h["reel"]]
        h["coupled"] = ((m[0].get("freeEnd") or {}).get("describe") if m else None)
        print("%-45s lay=%s -> %s" % (h["label"], (h["lay"] or {}).get("success"), h["coupled"]))
    print("tanks", [(t["d"], t["style"], t["min"], t["styled"]) for t in OUT["tanks"]])
    print("station cells", pc)
json.dump(OUT, open(r"Transient\live_batch_20261023\r3b\ports_stage.json", "w"), indent=1, default=str)
