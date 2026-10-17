#!/usr/bin/env python3
"""stage_extra.py -- the three walk stagings that had no tool (review walk 2026-10-17). Bridge must be HELD; python.exe only.

  python.exe Transient/review_walk_2026-10-17/stage_extra.py sprinklers --origin 40,60 [--spray-ticks 2800] [--save NAME]
  python.exe Transient/review_walk_2026-10-17/stage_extra.py weirs [--run 6] [--save NAME]     # current map = river_site.py's
  python.exe Transient/review_walk_2026-10-17/stage_extra.py human --at X,Z                    # same --at stage_review.py used
  add --dry to print the plan with a recording bridge (no game); `| tr -d '\\r'` on the output.

Nothing here is a new tool: every bridge call below is copied from a script that already runs it. Calls relied on, and where:
  jawa/destroy_batch rects= category= ................ Utils/stage_review.py clear(); FlowWorks/review_map_rivers.py build() (categories=)
  jawa/build_batch ops="Def:x,z[,rot]" faction=player wipeExisting=False .... FlowWorks/review_map.py (build op), review_map_rivers.py build()
  jawa/list_things defName= rect= limit= ............ review_map.py (style op), review_map_rivers.py (hp op)
  jawa/set_thing_props thing=<id> style=<StyleDef> .. review_map.py "style" op (Choose style's write)
  jawa/static_call type=RimMandrake.FlowWorks.RM_NorthstarProofs method=ProofTank args="x,z;Store;<Liquid>;<units>" ... review_map.py stage()
  jawa/gss_stage ops="kind=gss_charge|x=|z=" ........ review_map.py stage() (a built battery holds 0 Wd)
  jawa/get_terrain_batch (via review_map_rivers.read_terrain), review_map_rivers.river_anchors / ROT ... review_map_rivers.py
  jawa/map_info, jawa/spawn_pawn kindDef= x= z= count= faction= ..... review_map_rivers.py, Utils/stage_review.py prep_worker()
  jawa/set_fog action=unfog rect=, jawa/clear_ui, rimworld/jump_camera_to_cell, rimworld/frame_cell_rect, rimworld/take_screenshot
        ........ Utils/stage_review.py shoot()
  rimworld/step_game_ticks ticks= pauseFirst= timeoutMs= ... modcheck/reviewmap.py LiveBridge.ticks (the <=2000-tick chunk rule from rimworld-live-review)
  rimworld/save_game saveName= ...................... Utils/stage_review.py save_game() (only when --save is given)
  The 'RM_Liquid_FreshWater' liquid key and 'RM_LiquidTank/RM_LiquidPump/RM_UniversalPipe/Battery/PowerConduit'
  def names are from review_map.py station carry_tanks / pump_pour / pipes.
MEASURED on the 2026-10-17 walk: the sprinkler layout (LAYOUT G below; a pump needs no adjacent water) and the joined weir wall
(sections laid INTO the river along the crossing; side by side along the bank qualified 1-2 of 6, none joined). Still assumed: the
cells a 2x2 tank occupies (origin..+1).
"""
import argparse, os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FW = os.path.join(REPO, "src", "RimMandrake", "FlowWorks")
for p in (FW, os.path.join(FW, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")):
    sys.path.insert(0, p)

LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")


class Dry(object):
    def __init__(self):
        self.log = []
    def call(self, tool, **kw):
        self.log.append((tool, kw)); print("DRY", tool, json.dumps(kw)[:160])
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 250, "sizeZ": 250}
        return {"success": True, "survived": 1, "things": [{"id": 1}]}
    def ticks(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n)


def bridge(dry):
    if dry:
        return Dry()
    from modcheck import reviewmap as RM
    return RM.LiveBridge()


def say(m):
    print("%s %s" % (time.strftime("%H:%M:%S"), m), flush=True)


def shoot(B, x, z, w, h, name):
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (max(0, x - 4), max(0, z - 4), w + 8, h + 8))
    B.call("jawa/clear_ui")
    B.call("rimworld/jump_camera_to_cell", x=x + w // 2, z=z + h // 2)
    B.call("rimworld/frame_cell_rect", x=x, z=z, width=w, height=h, paddingCells=3)
    time.sleep(1.0)
    r = B.call("rimworld/take_screenshot", fileName=name, suppressMessage=True)   # appends .png itself
    say("screenshot %s -> %s" % (name, r.get("path")))


def build(B, d, x, z, rot=None):
    r = B.call("jawa/build_batch", ops="%s:%d,%d" % (d, x, z) + ("" if rot is None else ",%d" % rot), faction="player", wipeExisting=False)
    if r.get("survived") == 0:
        say("NOT BUILT %s at %d,%d: %s" % (d, x, z, (r.get("failed") or [])[:1]))
    return r.get("survived") != 0


def style(B, d, x, z, st):
    th = B.call("jawa/list_things", defName=d, rect="%d,%d,1,1" % (x, z), limit=3).get("things") or []
    if not th:
        say("style: no %s at %d,%d" % (d, x, z)); return False
    r = B.call("jawa/set_thing_props", thing=str(th[0].get("id") or th[0].get("thingId")), style=st)
    ok = "style" in (r.get("changed") or []) or isinstance(B, Dry)
    if not ok:
        say("style %s on %s at %d,%d NOT applied: %s" % (st, d, x, z, json.dumps(r)[:140]))
    return ok


def save(B, name):
    r = B.call("rimworld/save_game", saveName=name)
    say("save %s: %s (stat the Saves folder yourself; save_game has written the CURRENT slot before)" % (name, r.get("path")))


def sprinklers(B, a):
    ox, oz = [int(v) for v in a.origin.split(",")]
    # one mini network per look, rows 8 cells apart in z. Per row (x from ox): tank 2x2 at ox..ox+1; pipe ox+2; pump ox+3 (on the
    # run, powered through a conduit+battery above it); pipes ox+4..ox+5; head on the last pipe (ox+5).
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (ox - 2, oz - 6, 12, 8 * len(LOOKS) + 8), categories="Building,Item,Filth")
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (ox - 2, oz - 6, 12, 8 * len(LOOKS) + 8), categories="Plant")
    for i, look in enumerate(LOOKS):
        z = oz + 8 * i
        # LAYOUT G (measured live 2026-10-17, northstar/sprinkler_live.py): one unbroken pipe run ox+2..ox+5, the pump built
        # OVER pipe ox+3, power SOUTH of the pump. The old layout (pump in the run with no pipe under it) split the run and
        # every head read "Dry: nothing in the tanks on this network".
        build(B, "RM_LiquidTank", ox, z)
        for x in (ox + 2, ox + 3, ox + 4, ox + 5):
            build(B, "RM_UniversalPipe", x, z)
        build(B, "RM_LiquidPump", ox + 3, z)
        build(B, "PowerConduit", ox + 3, z - 1)
        build(B, "PowerConduit", ox + 3, z - 2)
        build(B, "Battery", ox + 3, z - 4, 0)
        build(B, "RM_SprinklerHead", ox + 5, z)
        style(B, "RM_SprinklerHead", ox + 5, z, "RM_SprinklerHead_" + look)
        B.call("jawa/gss_stage", ops="kind=gss_charge|x=%d|z=%d" % (ox + 3, z - 4))
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
               args="%d,%d;Store;RM_Liquid_FreshWater;%d" % (ox, z, 1000 * 10 * 10))   # 1,000 L = 10,000 units (UNITS_PER_LITRE 10)
        say("sprinkler row %s staged at z=%d" % (look, z))
    rect = (ox - 6, oz - 4, 22, 8 * len(LOOKS) + 8)
    shoot(B, rect[0], rect[1], rect[2], rect[3], "extra_sprinklers_p0")
    done = 0
    while done < a.spray_ticks:                      # <=2000 per chunk (rimworld-live-review), then it re-pauses via pauseFirst
        n = min(2000, a.spray_ticks - done)
        B.ticks(n); done += n
    shoot(B, rect[0], rect[1], rect[2], rect[3], "extra_sprinklers_spraying")
    say("read each head's inspect line for 'Spraying water' (select it; or jawa/list_things); one pulse is hourly, spray lasts pulse+250 ticks")
    if a.save:
        save(B, a.save)


def weirs(B, a):
    import review_map_rivers as RV
    mi = B.call("jawa/map_info")
    size = (int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or mi.get("sizeY") or 0))
    prof = B.call("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofGrid", args="-")
    if not isinstance(B, Dry) and ("current=" not in str(prof.get("result", "")) or "current=0" in str(prof.get("result", ""))):
        raise SystemExit("needs the river site with a current (run northstar/river_site.py first): %s" % str(prof)[:200])
    terr = RV.read_terrain(B, size)
    anchors = RV.river_anchors(terr, size, k=len(LOOKS), spacing=RV.SPACING)
    if len(anchors) < len(LOOKS):
        raise SystemExit("only %d crossings on this river; need %d" % (len(anchors), len(LOOKS)))
    for look, cr in zip(LOOKS, anchors):
        (bx, bz), d, n, e = cr
        rot = RV.ROT[d]
        # The joined wall (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS; RM_RiverWorksProofWorks.ProofWeirJoin): a 1x2 weir faces the
        # water, so the next section of the wall starts 2 cells further INTO the river along d, same rotation, and so on
        # toward the far bank. (The first version laid weirs side by side ALONG the bank: 1-2 of 6 qualified, none joined.)
        cells = [(bx + d[0] * 2 * k, bz + d[1] * 2 * k) for k in range(a.run) if 2 * k < max(2, n)]
        say("%s: crossing bank %s dir %s, %d moving cells: %d wall sections planned" % (look, (bx, bz), d, n, len(cells)))
        xs = [c[0] for c in cells] + [c[0] + d[0] for c in cells]
        zs = [c[1] for c in cells] + [c[1] + d[1] for c in cells]
        B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (min(xs) - 2, min(zs) - 2, max(xs) - min(xs) + 5, max(zs) - min(zs) + 5), categories="Plant")   # categories=, as above (review 2026-10-17: category= was the wrong name)
        got = 0
        for c in cells:
            if build(B, "RM_BankWeir", c[0], c[1], rot):
                got += 1
                style(B, "RM_BankWeir", c[0], c[1], "RM_BankWeir_" + look)
        say("%s: %d weirs built and styled" % (look, got))
        if cells:
            shoot(B, min(xs) - 6, min(zs) - 6, max(xs) - min(xs) + 13, max(zs) - min(zs) + 13, "extra_weirs_%s" % look.lower())
    say("unpause a few hours (<=2000-tick steps) for slack pools; re-pause before looking")
    if a.save:
        save(B, a.save)


def human(B, a):
    x, z = [int(v) for v in a.at.split(",")]
    # stage_review.py's grid puts the FIRST kind on --at, so a colonist 3 cells west stands at the head of the line, same row.
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=x - 3, z=z, count=1, faction="PlayerColony")
    say("human at %d,%d: %s" % (x - 3, z, json.dumps(r)[:120]))
    say("re-shoot the line with stage_review.py --frame including that cell, or: shoot below")
    shoot(B, x - 6, z - 4, a.width, 9, "extra_creature_line_with_human")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=("sprinklers", "weirs", "human"))
    ap.add_argument("--origin", default="40,60"); ap.add_argument("--spray-ticks", type=int, default=2800)
    ap.add_argument("--run", type=int, default=6); ap.add_argument("--at", default="40,100"); ap.add_argument("--width", type=int, default=70)
    ap.add_argument("--save", default=""); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    B = bridge(a.dry)
    {"sprinklers": sprinklers, "weirs": weirs, "human": human}[a.what](B, a)


if __name__ == "__main__":
    main()
