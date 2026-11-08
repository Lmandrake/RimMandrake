"""g8_site.py -- build the pass-8 gallery map ONCE and save it, so later sittings load it instead of re-staging.

  python.exe ralph/live/g8_site.py probe [--site calm]
        load the calm site, report colonists + a terrain/rock census of candidate gallery origins, overview shots.
  python.exe ralph/live/g8_site.py build [--origin X,Z] [--save RM_FW_Gallery8] [--replace] [--hour 11] [--no-verify]
        load the calm site (RM_TestSite_calm_v3), quiet it (Phoebe/Peaceful, threat 0, Clear locked, queue cleared),
        set the clock to `hour` (a declared time exception: the site has colonists), clear + unroof + paint Soil over
        the gallery rect, dig every fixture (jawa/flowworks_excavation_drive, dry), place the ladders, portables,
        bridge and climbing gear, read every fixture back, shoot an overview, SAVE (test_site_saves.save_site: stat
        before/after, never overwrites unless --replace, which first moves the old file to the run folder), then load
        the save again and read the fixtures back from it (unless --no-verify).
  python.exe ralph/live/g8_site.py verify [--save NAME]
        load the save and read every fixture back (depths, ladders, portables, deck, gear, wearer).

The layout is g8_common.layout(ORIGIN); GALLERY8.md lists every fixture's cells.
"""
import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g8_common as C  # noqa: E402
from g8_common import j, safe, scall  # noqa: E402

BAD_TERRAIN = ("Water", "Marsh", "Mud", "_Rough", "_Smooth", "Ice", "Lava", "Bridge", "Sand")
ROCKS = ("Granite,Sandstone,Limestone,Slate,Marble,MineableSteel,MineableComponentsIndustrial,MineableSilver,"
         "MineableGold,MineableUranium,MineablePlasteel,MineableJade,CollapsedRocks,RaisedRocks")


def load_base(B, R, site):
    import test_site_saves as TS
    t = time.time()
    rec = TS.load_site(B.loose_call, site)
    R.log("LOAD base", site, "%.0f s" % (time.time() - t), j({k: rec.get(k) for k in ("save", "verified", "problems")}, 500))
    if not rec.get("verified"):
        R.harness_error("base site %s did not verify: %s" % (site, rec.get("problems")))
    C.pause(B, R)
    C.quiet(B, R)
    return rec


def census_rect(B, rect):
    x, z, w, h = rect
    ex = B.call("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=h, onlyNonZero=False, includeTerrain=True) or {}
    rows = ex.get("cells") or ex.get("rows") or []
    terr = {}
    dug = 0
    for c in rows:
        t = c.get("terrain") or "?"
        terr[t] = terr.get(t, 0) + 1
        if c.get("d"):
            dug += 1
    bad = sum(n for t, n in terr.items() if any(b in t for b in BAD_TERRAIN))
    th = B.call("jawa/list_things", defName=ROCKS, rect="%d,%d,%d,%d" % rect, limit=5000) or {}
    rocks = len(th.get("things") or th.get("rows") or [])
    return {"cells": len(rows), "bad": bad, "rocks": rocks, "dug": dug,
            "top": sorted(terr.items(), key=lambda kv: -kv[1])[:5]}


def probe(B, R, a):
    load_base(B, R, a.site)
    mi = B.call("jawa/map_info") or {}
    R.log("map", j({k: mi.get(k) for k in ("tile", "biome", "mapBiome", "sizeX", "sizeZ", "hilliness", "temperature")
                    if k in mi}, 400))
    cols = C.colonists(B)
    R.log("colonists", [(p.get("id"), p.get("x"), p.get("z")) for p in cols])
    R.log("hour", C.local_hour(B), "tick", C.tick(B))
    sx, sz = int(mi.get("sizeX") or 250), int(mi.get("sizeZ") or 250)
    best = []
    for ox in range(15, sx - 70, 25):
        for oz in range(10, sz - 40, 25):
            L = C.layout((ox, oz))
            x, z, w, h = L["site_rect"]
            if x < 2 or z < 2 or x + w > sx - 2 or z + h > sz - 2:
                continue
            near = [p for p in cols if x - 6 <= p["x"] <= x + w + 6 and z - 6 <= p["z"] <= z + h + 6]
            c = census_rect(B, L["site_rect"])
            score = c["bad"] + 3 * c["rocks"] + 50 * len(near) + 20 * c["dug"]
            best.append((score, (ox, oz), c, len(near)))
    best.sort(key=lambda b: b[0])
    for b in best[:8]:
        R.log("CANDIDATE origin=%s score=%d %s colonistsNear=%d" % (b[1], b[0], j(b[2], 300), b[3]))
        R.result("candidate", {"origin": b[1], "score": b[0], "census": b[2]}, source="probe")
    C.shot(B, R, "map_overview", (0, 0, sx, sz), 130, wait=2.0)
    if best:
        L = C.layout(best[0][1])
        C.shot(B, R, "best_candidate", L["site_rect"], 40, wait=2.0)


# ------------------------------------------------------------------------------------------------------ the build
def expected_depths(B, R, L):
    """{cell: levels} for every dug cell of the gallery (B2's deep pit at the live portable reach + 1)."""
    reach = C.setting(B, "portableLadderMaxLevels")
    try:
        reach = int(float(reach))
    except (TypeError, ValueError):
        R.harness_error("portableLadderMaxLevels unreadable (%r): assuming 6" % reach)
        reach = 6
    R.result("portable_reach_levels", reach, source="portableLadderMaxLevels")
    want = {}
    for h in L["A1"]:
        for c in h["cells"]:
            want[c] = h["levels"]
    for h in L["A2"]:
        for c in h["cells"]:
            want[c] = h["levels"]
    for r in L["A3"]["rows"]:
        for i in range(L["A3"]["w"]):
            want[(L["A3"]["x0"] + i, r["z"])] = r["levels"]
    for col in L["A4"]["cols"]:
        for k in range(L["A4"]["h"]):
            want[(col["x"], L["A4"]["z0"] + k)] = col["levels"]
    for c in L["B1"]["cells"]:
        want[c] = L["B1"]["levels"]
    for p in L["B2"]:
        lv = reach + 1 if p["tag"] == "deep" else p["levels"]
        p["levels"] = lv
        for c in p["cells"]:
            want[c] = lv
    for c in L["B3"]["cells"]:
        want[c] = L["B3"]["levels"]
    return {c: d for c, d in want.items() if d}, reach


def prepare_ground(B, R, L):
    x, z, w, h = L["site_rect"]
    rect = "%d,%d,%d,%d" % (x, z, w, h)
    # colonists out of the way first: clear_area destroys pawns standing in the rect
    for p in C.colonists(B):
        if x - 2 <= p["x"] <= x + w + 2 and z - 2 <= p["z"] <= z + h + 2:
            dest = (x - 6, z + h // 2)
            ok, at = C.walk_to(B, R, p["id"], dest, wait_ticks=600, tries=3)
            R.log("moved colonist", p["id"], "out of the site ->", at, ok)
            if not ok:
                R.harness_error("colonist %s still near the site at %s" % (p["id"], at))
    C.draft_all(B, R)
    r = safe(B, R, "jawa/clear_area", rect=rect, dryRun=False)
    R.log("clear_area", j({k: r.get(k) for k in ("success", "destroyed", "count", "message") if k in r}, 300))
    r = safe(B, R, "jawa/set_roof_batch", ops="None:%s" % rect, refresh=True)
    R.log("unroof", r.get("success"), j(r.get("message"), 120))
    r = safe(B, R, "jawa/set_terrain_batch", ops="Soil:%s" % rect, layer="top", refresh=True, clearOverlays=True)
    R.log("soil", r.get("success"), j({k: r.get(k) for k in ("cellsPainted", "cellsFailedVerify", "message") if k in r}, 200))
    r = safe(B, R, "jawa/set_fog", action="unfog", rect=rect)
    R.log("unfog", r.get("success"))
    c = census_rect(B, L["site_rect"])
    R.result("site_ground", c, expected="no bad terrain, no rock, nothing dug",
             ok=(c["bad"] == 0 and c["rocks"] == 0 and c["dug"] == 0), source="excavation_rect+list_things")


def dig_all(B, R, want):
    t = time.time()
    fails = 0
    for c, d in sorted(want.items()):
        r = safe(B, R, "jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=int(d), setFill=-1)
        if not C.ok_(r) or int(r.get("depth") or -1) != int(d):
            fails += 1
            if fails <= 6:
                R.harness_error("dig %s to %d -> %s" % (c, d, j(r, 200)))
    R.log("dug %d cells in %.1f s, %d short" % (len(want), time.time() - t, fails))


def check_depths(B, R, L, want, tag):
    x, z, w, h = L["site_rect"]
    got = C.depths(B, x, z, w, h)
    bad = [(c, d, got.get(c, 0)) for c, d in want.items() if (got.get(c, 0) or 0) != d]
    extra = [(c, v) for c, v in got.items() if v and c not in want]
    R.result("depths_%s" % tag, {"cells": len(want), "wrong": bad[:10], "extraDug": extra[:10]},
             expected="every fixture cell at its level, nothing else dug", ok=not bad and not extra,
             source="flowworks_excavation_rect")
    return not bad and not extra


def things_in(B, defname, rect):
    r = B.call("jawa/list_things", defName=defname, rect="%d,%d,%d,%d" % tuple(rect), limit=200) or {}
    return r.get("things") or r.get("rows") or []


def rot_of(t):
    for k in ("rot", "rotation", "rotInt"):
        if t.get(k) is not None:
            return t.get(k)
    return None


def place_kit(B, R, L):
    b1 = L["B1"]
    ops = ";".join("RM_Ladder:%d,%d,%d" % (c[0], c[1], r) for r, c in sorted(b1["ladders"].items()))
    r = safe(B, R, "jawa/build_batch", ops=ops, stuff="WoodLog", faction="player")
    R.log("B1 ladders", j({k: r.get(k) for k in ("success", "placed", "survived", "failed", "message") if k in r}, 300))
    ops = []
    for p in L["B2"]:
        ops += ["RM_LadderPortable:%d,%d,%d" % (c[0], c[1], rr) for rr, c in sorted(p["portables"].items())]
    r = safe(B, R, "jawa/build_batch", ops=";".join(ops), faction="player")
    R.log("B2 portables", j({k: r.get(k) for k in ("success", "placed", "survived", "failed", "message") if k in r}, 300))
    a, b = L["B3"]["anchors"]
    st, txt = scall(B, C.SUSP, "ProofBuild", "%d,%d;%d,%d;timber;god" % (a[0], a[1], b[0], b[1]))
    R.log("B3 bridge", st, txt[:300])
    b4 = L["B4"]
    r = safe(B, R, "jawa/spawn_batch", ops="RM_ClimbingGear:%d,%d;%s:%d,%d" % (b4["gear"][0], b4["gear"][1],
                                                                           b4["vanillaDef"], b4["vanilla"][0],
                                                                           b4["vanilla"][1]))
    R.log("B4 items", j({k: r.get(k) for k in ("success", "spawned", "message") if k in r}, 300))
    pid = C.subject(B, R, b4["wearer"], "B4 wearer")
    if pid:
        g = safe(B, R, "jawa/pawn_gear", pawn=pid, action="wear", **{"def": "RM_ClimbingGear"})
        R.log("B4 wear", g.get("success"), j(g.get("message") or g.get("worn"), 200))
    C.redraw(B, R)
    return pid


def check_kit(B, R, L, tag):
    ok_all = True
    b1 = L["B1"]
    lad = things_in(B, "RM_Ladder", (b1["x0"], b1["z0"], 5, 5))
    got = sorted(((t.get("x"), t.get("z")), rot_of(t)) for t in lad)
    want = sorted((c, r) for r, c in b1["ladders"].items())
    good = len(lad) == 4 and sorted(g[0] for g in got) == sorted(w[0] for w in want)
    R.result("B1_ladders_%s" % tag, got, expected=want, ok=good, source="list_things")
    ok_all &= good
    for p in L["B2"]:
        th = things_in(B, "RM_LadderPortable", (p["x0"], p["z0"], 3, 3))
        g2 = sorted(((t.get("x"), t.get("z")), rot_of(t)) for t in th)
        w2 = sorted((c, r) for r, c in p["portables"].items())
        good = sorted(g[0] for g in g2) == sorted(w[0] for w in w2)
        R.result("B2_%s_portables_%s" % (p["tag"], tag), g2, expected=w2, ok=good, source="list_things")
        ok_all &= good
    b3 = L["B3"]
    r = B.call("jawa/list_things", rect="%d,%d,%d,1" % (b3["x0"] - 1, b3["deck_z"], b3["w"] + 2), limit=200) or {}
    names = {}
    for t in r.get("things") or r.get("rows") or []:
        dn = str(t.get("def") or t.get("defName"))
        if "Suspension" in dn:
            names[dn] = names.get(dn, 0) + 1
    st, txt = scall(B, C.SUSP, "ProofSpan", "%d,%d" % (b3["x0"] + 2, b3["deck_z"]))
    R.result("B3_bridge_%s" % tag, {"things": names, "span": txt[:200]}, expected="anchors at both ends, deck over the hole",
             ok=None, source="list_things+ProofSpan")
    b4 = L["B4"]
    gear = things_in(B, "RM_ClimbingGear", (b4["gear"][0], b4["gear"][1], 1, 1))
    van = things_in(B, b4["vanillaDef"], (b4["vanilla"][0], b4["vanilla"][1], 1, 1))
    good = bool(gear) and bool(van)
    R.result("B4_items_%s" % tag, {"gear": len(gear), "vanilla": len(van)}, expected={"gear": 1, "vanilla": 1}, ok=good,
             source="list_things")
    ok_all &= good
    wearer = None
    for p in C.colonists(B):
        if (p.get("x"), p.get("z")) == tuple(b4["wearer"]):
            wearer = p.get("id")
    worn = None
    if wearer:
        pg = B.call("jawa/pawn_get", pawn=wearer) or {}
        ap = pg.get("apparel") or (pg.get("pawn") or {}).get("apparel") or ((pg.get("pawns") or [{}])[0]).get("apparel")
        worn = [a.get("def") or a.get("defName") if isinstance(a, dict) else a for a in ap or []]
    good = bool(wearer) and any("RM_ClimbingGear" in str(w) for w in worn or [])
    R.result("B4_wearer_%s" % tag, {"id": wearer, "apparel": worn}, expected="a colonist on the wearer cell in RM_ClimbingGear",
             ok=good, source="pawn_census+pawn_get")
    ok_all &= good
    return ok_all


def overview(B, R, L, tag):
    C.shot(B, R, "%s_overview" % tag, L["overview"], 36, wait=2.0)
    ox, oz = L["origin"]
    C.shot(B, R, "%s_rowA" % tag, (ox - 6, oz - 2, 40, 22), 20, wait=1.5)
    C.shot(B, R, "%s_rowB" % tag, (ox - 3, oz + 17, 62, 13), 20, wait=1.5)


def set_hour(B, R, hour):
    h = C.local_hour(B)
    t = C.tick(B)
    if h is None or t is None:
        R.harness_error("cannot read the hour (%s) or tick (%s)" % (h, t))
        return
    dt = int(round(((hour - h) % 24) * 2500))
    if dt:
        r = safe(B, R, "jawa/time_set_ticks", ticks=int(t) + dt, timeException=True,
                 why="Artisan pass 8 gallery site: midday light for the depth and kit shots (fixture build)")
        R.log("time_set", r.get("success"), j(r.get("message") or r.get("after"), 150))
    R.result("hour", round(C.local_hour(B) or -1, 2), expected=hour, ok=abs((C.local_hour(B) or -99) - hour) < 0.6,
             source="time_date_at")


def save(B, R, name, replace):
    import test_site_saves as TS
    sd = C.saves_dir()
    path = os.path.join(sd, name + ".rws")
    if os.path.exists(path):
        if not replace:
            R.harness_error("%s exists; pass --replace to move it aside and save again" % path)
            return False
        bak = os.path.join(R.dir, name + ".previous.rws")
        shutil.move(path, bak)
        R.log("moved the previous", name, "to", bak)
    C.pause(B, R)
    try:
        rec = TS.save_site(B.loose_call, name, sd)
    except Exception as e:  # noqa: BLE001
        R.harness_error("save_site raised %s: %s" % (type(e).__name__, str(e)[:300]))
        return False
    R.result("save", {"name": name, "bytes": rec.get("bytes"), "expanded": (rec.get("expanded") or {}).get("cells")},
             expected="a new %s.rws, no other save touched" % name, ok=True, source="save_site stat")
    return True


def build(B, R, a):
    L = C.layout(a.origin)
    R.log("origin", L["origin"], "site_rect", L["site_rect"])
    load_base(B, R, a.site)
    set_hour(B, R, a.hour)
    prepare_ground(B, R, L)
    want, reach = expected_depths(B, R, L)
    dig_all(B, R, want)
    C.step(B, 5)
    check_depths(B, R, L, want, "built")
    place_kit(B, R, L)
    C.step(B, 5)
    check_kit(B, R, L, "built")
    C.draft_all(B, R)
    C.settle(B, 300)
    overview(B, R, L, "built")
    if not save(B, R, a.save, a.replace):
        return
    if not a.no_verify:
        verify(B, R, a, L, want)


def verify(B, R, a, L=None, want=None):
    L = L or C.layout(a.origin)
    if not C.load_gallery(B, R, a.save):
        return
    if want is None:
        want, _ = expected_depths(B, R, L)
    d_ok = check_depths(B, R, L, want, "loaded")
    k_ok = check_kit(B, R, L, "loaded")
    R.result("save_loads", a.save, expected="the save loads and every fixture reads back", ok=bool(d_ok and k_ok),
             source="load_site+readback")
    overview(B, R, L, "loaded")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("probe", "build", "verify"))
    ap.add_argument("--site", default=C.BASE_SITE)
    ap.add_argument("--origin", default=None, help="X,Z (default g8_common.ORIGIN)")
    ap.add_argument("--save", default=C.SAVE)
    ap.add_argument("--replace", action="store_true")
    ap.add_argument("--hour", type=float, default=11.0)
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--tag", default="site")
    a = ap.parse_args()
    a.origin = tuple(int(v) for v in a.origin.split(",")) if a.origin else C.ORIGIN
    B = C.bridge()
    R = C.Run("site", "%s_%s" % (a.cmd, a.tag))
    try:
        if a.cmd == "probe":
            probe(B, R, a)
        elif a.cmd == "build":
            build(B, R, a)
        else:
            verify(B, R, a)
        C.finish_shots(R)
    except Exception as e:  # noqa: BLE001
        import traceback
        R.harness_error("UNCAUGHT %s: %s | %s" % (type(e).__name__, e, traceback.format_exc()[-800:]))
    finally:
        try:
            C.pause(B)
        except Exception:  # noqa: BLE001
            pass
        R.close()


if __name__ == "__main__":
    main()
