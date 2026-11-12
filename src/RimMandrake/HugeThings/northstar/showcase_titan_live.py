"""showcase_titan_live.py -- the TITAN promise of HugeThings, one demonstration in the owner's order (ANSWERS_OWNER.md
answers 1-2, 2026-11-11): CONTROL, CROSSING, then DEATH, then the CROWD at the remains. Gated: a phase that does not PASS stops
the run and every later phase is UNMEASURED (never reordered, never run out of order). Each phase carries start/end
tick stamps in the output JSON.

  CONTROL   the scene's one control, before the titan: a same-mass UNTIERED RM_TestTitanT2Control on the same staged
            lane gets the titan's Goto GOAL (sealed by the ring), then a Goto to the open cell touching the ring. The ring
            must stay whole (broken -> FAIL MOD: walls break without a tier); a control that never reaches the ring or
            gets inside it is UNMEASURED SITE. It is vanished afterwards; CROSSING re-stages the lane.
  CROSSING  a real RM_TestTitanT3Adult (HugeThingsTestRaces, faction none) walks a staged lane on the registered calm
            site: a player WoodLog wall column, a row of grown Plant_TreeOak, a grown RM_Nogtyl giant. Census of the
            staged things and Filth_RubbleRock before vs after; the walk is sampled every 120 ticks (no step longer
            than MAX_STEP cells -> it walked, it did not teleport). STAGED: the spawn and the Goto order (a wild animal
            has no reason of its own to cross this lane); ORDINARY: the path, the wake and the wall breaking.
  DEATH     ordinary damage first: jawa/damage (Thing.TakeDamage, Bullet) until the titan dies -- the cause is staged,
            the death path is the game's. Fallback: TitanValidationHooks.KillTitanAt at its cell, labelled STAGED.
            The corpse must become a Building_TitanicCorpseSite (a NEW site in SiteReport near the death cell).
  CROWD     scavengers and campers arrive through TitanValidationHooks.SiteDailyStep (the site's own daily step,
            chances forced to 1 and restored); they must target the site (SiteReport S[... atSite=True]).

The scene runs on a scene-begin snapshot of the registered calm site and is restored in `finally` (settings first,
then the snapshot reload). LIVE: needs the game and the bridge; offline proof is selftest_showcases.py.
Exit 0 every required row PASS, 1 a MOD FAIL, 2 UNMEASURED (could not ask) -- the Lightspeed proof contract.
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import showcase_common as SC  # noqa: E402

ITEM = "RIMMANDRAKE_SPLIT_HUGETHINGS_PLANT_AND_TITAN_PROMISES"
HOOKS = "RimMandrake.TitanicCreatures.TitanValidationHooks"
KIND = "RM_TestTitanT3Adult"
SNAP_PREFIX = "CODEX_ShowcaseTitan_"
SITE_KEY = "calm"
LANE = (20, 155, 101, 21)            # x, z, w, h -- away from the workshop rect 90,90,96,30 of trunk_doors_live
START, GOAL = (26, 165), (114, 165)
WALL_X, TREE_X, GIANT = 50, 70, (92, 165)
STAGED_Z = range(159, 172)
# The goal is SEALED by a wall ring: titan clearing (Patch_StartPath_TitanClearing) acts only when the destination is
# unreachable, so an open lane would let the titan walk round the line wall and test nothing but the wake.
RING_R = 3
RING = [(GOAL[0] + dx, GOAL[1] + dz) for dx in range(-RING_R, RING_R + 1) for dz in range(-RING_R, RING_R + 1)
        if max(abs(dx), abs(dz)) == RING_R]
ARRIVE = 2                            # inside the ring: within 2 cells of the goal
CHUNK, BUDGET, MAX_STEP, STALL = 120, 12000, 12, 1800   # a re-order mid-clearing would interrupt the clearing job
NEAR = 12
FIELDS = ("giantAnimalsEnabled", "wakeEnabled", "titanClearingEnabled", "titanEventsEnabled",
          "corpseSiteEnabled", "corpseSiteScavengersEnabled", "corpseSiteScavengerDailyChance", "corpseSiteCampsEnabled",
          "corpseSiteCampDailyChance", "giantPlantsEnabled")
PACKAGES = ("mandrake.rm.hugethings", "mandrake.rm.hugethingstestraces")
CONTROL_KIND = "RM_TestTitanT2Control"   # bodySize 8, forceEnabled=false: same mass, NO tier (HugeThingsTestRaces)
CONTROL_TICKS, CONTROL_SWITCH, CONTROL_DWELL = 3600, 600, 600   # the titan's own order (Goto GOAL, sealed) first;
OUTSIDE = (GOAL[0] - RING_R - 1, GOAL[1])  # then Goto the open cell touching the ring, and stand there DWELL ticks
ROWS = dict(PRE=["PRE_ready"], CONTROL=["CONTROL_untiered_leaves_ring"], CROSSING=["CROSSING_walked", "CROSSING_destroys"],
            DEATH=["DEATH_titan_dies", "DEATH_corpse_site"], CROWD=["CROWD_arrives", "CROWD_targets_site"])
PHASES = ("PRE", "CONTROL", "CROSSING", "DEATH", "CROWD")
REQUIRED = [r for k in PHASES for r in ROWS[k]]


def arrived(cell):
    return None not in cell and max(abs(cell[0] - GOAL[0]), abs(cell[1] - GOAL[1])) <= ARRIVE


def rect(x, z, w, h):
    return "%d,%d,%d,%d" % (x, z, w, h)


def sites(txt):
    """SiteReport text -> [site dicts] (titan_events_live.parse_site on every ' | ' segment) with at=(x,z)."""
    from titan_events_live import parse_site
    out = []
    for seg in str(txt).split(" | ")[1:]:
        d = parse_site("sites | " + seg)
        if not d:
            continue
        head = seg.split()
        d["id"] = head[0] if head else None
        try:
            x, z = seg.split(" at ", 1)[1].split()[0].split(",")
            d["at"] = (int(x), int(z))
        except (IndexError, ValueError):
            d["at"] = None
        out.append(d)
    return out


class TitanShowcase(object):
    def __init__(self, sc, settings):
        self.sc, self.st = sc, settings
        self.pid, self.death_cell, self.site, self.sites_before = None, None, None, set()
        self.census0 = {}

    # ------------------------------------------------------------ helpers
    def census(self):
        x, z, w, h = LANE
        rows = self.sc.things(rect(x, z, w, h))
        if rows is None:
            return None
        c = dict(wall=0, ring=0, tree=0, giant=0, rubble=0, blocker=0)
        ring = set(RING)
        for t in rows:
            d = t.get("def")
            if d == "Wall":
                c["ring" if (t.get("x"), t.get("z")) in ring else "wall"] += 1
            elif d == "Plant_TreeOak":
                c["tree"] += 1
            elif d == "RM_Nogtyl":
                c["giant"] += 1
            elif d == "Filth_RubbleRock":
                c["rubble"] += 1
            elif d == "RM_HugeTrunkBlocker":
                c["blocker"] += 1
        return c

    def stage_lane(self):
        x, z, w, h = LANE
        call = self.sc.call
        call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % (x, z, w, h))
        call("jawa/destroy_batch", categories="All", rects=rect(x, z, w, h))
        call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % (x, z, w, h))
        walls = [(WALL_X, zz) for zz in STAGED_Z] + RING
        call("jawa/build_batch", ops=";".join("Wall:%d,%d" % c for c in walls), stuff="WoodLog",
             faction="player", wipeExisting=True, readBack=0)
        ops = ["id=t%d|kind=plant|x=%d|z=%d|def=Plant_TreeOak|growth=1" % (zz, TREE_X, zz) for zz in STAGED_Z[::3]]
        ops.append("id=g|kind=plant|x=%d|z=%d|def=RM_Nogtyl|growth=1" % GIANT)
        call("jawa/artboard_stage", phase="subjects", pause=False, killHostiles=True, ops="\n".join(ops))
        self.sc.ticks(120)

    # ------------------------------------------------------------ phases
    def pre(self, sc):
        okp, why = SC.preflight(sc, PACKAGES)
        if not okp:
            return sc.row("PRE_ready", "the loaded build is this clone's, with test races", "UNMEASURED", "HARNESS", why)
        bad = [f for f, v in (("giantAnimalsEnabled", True), ("wakeEnabled", True), ("titanClearingEnabled", True),
                              ("titanEventsEnabled", True), ("giantPlantsEnabled", True),
                              ("corpseSiteEnabled", True)) if not self.st.put(f, v)]
        x, z, w, h = LANE
        there = [p.get("id") for p in sc.call("jawa/list_pawns", rect=rect(x, z, w, h), limit=200).get("pawns") or []]
        if bad or there:
            return sc.row("PRE_ready", "settings on and the lane empty of pawns", "UNMEASURED", "SITE",
                          "settings not written %s; pawns already in the lane %s" % (bad, there[:8]))
        return sc.row("PRE_ready", "build, settings and an empty lane", "PASS", "HARNESS", why)

    def control(self, sc):
        """The scene's shared control: the same lane, the same Goto GOAL, a same-mass UNTIERED walker. If the ring
        breaks anyway, CROSSING_destroys could not tell the titan's passage from anything else that breaks walls."""
        rid, crit = "CONTROL_untiered_leaves_ring", "an untiered same-mass walker sent to the sealed goal leaves the ring whole"
        self.stage_lane()
        c0 = self.census()
        if not c0 or c0.get("ring", 0) != len(RING):
            return sc.row(rid, crit, "UNMEASURED", "SITE", "the ring was not built whole: %s" % c0)
        r = sc.call("jawa/spawn_pawn", kindDef=CONTROL_KIND, x=START[0], z=START[1], faction="none", count=1)
        ps = r.get("pawns") or []
        cid = ps[0].get("id") if ps else None
        if not cid:
            return sc.row(rid, crit, "UNMEASURED", "HARNESS", "spawn_pawn %s: %s" % (CONTROL_KIND, str(r)[:200]))
        sc.rec.setdefault("staged", []).append("control: spawn %s at %s faction none; Goto %s then %s" % (
            CONTROL_KIND, START, GOAL, OUTSIDE))
        sc.call("jawa/pawn_need", pawn=cid, action="need", need="Food", level=1.0)
        sc.call("jawa/ordered_job", pawnId=cid, jobDef="Goto", targetAX=GOAL[0], targetAZ=GOAL[1], waitTicks=1)
        spent, nearest, inside, p, second, dwell = 0, None, False, None, False, 0
        while spent < CONTROL_TICKS and dwell < CONTROL_DWELL:
            if not second and spent >= CONTROL_SWITCH:
                sc.call("jawa/ordered_job", pawnId=cid, jobDef="Goto", targetAX=OUTSIDE[0], targetAZ=OUTSIDE[1], waitTicks=1)
                second = True
            d = sc.ticks(CHUNK)
            spent += d if d else CHUNK
            p = sc.pawn(cid)
            if not p or p.get("dead") or not p.get("spawned"):
                break
            cell = (p.get("x"), p.get("z"))
            if None not in cell:
                gap = max(abs(cell[0] - GOAL[0]), abs(cell[1] - GOAL[1]))
                nearest = gap if nearest is None else min(nearest, gap)
                inside = inside or gap < RING_R
                dwell = dwell + (d if d else CHUNK) if gap <= RING_R + 1 else 0
        c1 = self.census()
        alive = bool(p and not p.get("dead") and p.get("spawned"))
        gone = sc.call("jawa/pawn_force_incapacitate", pawn=cid, action="vanish")
        sc.rec["control_vanished"] = gone.get("destroyedAfter")
        dd = "ring %s -> %s of %d; %d ticks; nearest approach %s cells from goal; alive %s; vanished %s" % (
            c0.get("ring"), (c1 or {}).get("ring"), len(RING), spent, nearest, alive, gone.get("destroyedAfter"))
        if not c1:
            return sc.row(rid, crit, "UNMEASURED", "HARNESS", "after-census unreadable; " + dd)
        if c1.get("ring", 0) < len(RING):
            return sc.row(rid, crit, "FAIL", "MOD", "an UNTIERED walker broke the ring: " + dd)
        if inside:
            return sc.row(rid, crit, "UNMEASURED", "SITE", "the control got inside a whole ring (the ring leaks): " + dd)
        if nearest is None or nearest > RING_R + 1:
            return sc.row(rid, crit, "UNMEASURED", "SITE", "the control never reached the ring, so it tested nothing: " + dd)
        if not alive or gone.get("destroyedAfter") is not True:
            return sc.row(rid, crit, "UNMEASURED", "HARNESS", "control died/despawned or was not removed: " + dd)
        return sc.row(rid, crit, "PASS", "MOD", dd)

    def crossing(self, sc):
        self.stage_lane()
        c0 = self.census()
        self.census0 = c0 or {}
        if not c0 or not c0["wall"] or not c0["tree"] or not c0["giant"]:
            sc.row("CROSSING_walked", "titan walks the staged lane", "UNMEASURED", "HARNESS", "staging read back %s" % c0)
            return sc.row("CROSSING_destroys", "the crossing destroys what it passes", "UNMEASURED", "HARNESS",
                          "the lane was not staged (walls/trees/giant): %s" % c0)
        r = sc.call("jawa/spawn_pawn", kindDef=KIND, x=START[0], z=START[1], faction="none", count=1)
        ps = r.get("pawns") or []
        self.pid = ps[0].get("id") if ps else None
        if not self.pid:
            sc.row("CROSSING_walked", "titan walks the staged lane", "UNMEASURED", "HARNESS", "spawn_pawn: %s" % str(r)[:200])
            return sc.row("CROSSING_destroys", "the crossing destroys what it passes", "UNMEASURED", "HARNESS", "no titan")
        sc.rec.setdefault("staged", []).append("spawn %s at %s faction none; Goto %s (STAGED order)" % (KIND, START, GOAL))
        sc.call("jawa/pawn_need", pawn=self.pid, action="need", need="Food", level=1.0)
        sc.call("jawa/ordered_job", pawnId=self.pid, jobDef="Goto", targetAX=GOAL[0], targetAZ=GOAL[1], waitTicks=1)
        path, worst, spent, stall_at, reorders = [], 0.0, 0, 0, 0
        p = sc.pawn(self.pid)
        if p:
            path.append((p.get("x"), p.get("z")))
        while spent < BUDGET:
            d = sc.ticks(CHUNK)
            spent += d if d else CHUNK
            p = sc.pawn(self.pid)
            if not p or p.get("dead") or not p.get("spawned"):
                break
            cell = (p.get("x"), p.get("z"))
            if path and None not in cell and None not in path[-1]:
                step = ((cell[0] - path[-1][0]) ** 2 + (cell[1] - path[-1][1]) ** 2) ** 0.5
                worst = max(worst, step)
                stall_at = stall_at + CHUNK if step < 1 else 0
            path.append(cell)
            if arrived(cell):
                break
            if stall_at >= STALL:
                sc.call("jawa/ordered_job", pawnId=self.pid, jobDef="Goto", targetAX=GOAL[0], targetAZ=GOAL[1], waitTicks=1)
                reorders, stall_at = reorders + 1, 0
        c1 = self.census() or {}
        alive = bool(p and not p.get("dead") and p.get("spawned"))
        reached = bool(path and arrived(path[-1]))
        detail = "path %d samples %s..%s, max step %.1f cells/%d ticks, %d ticks, re-orders %d" % (
            len(path), path[:1], path[-1:], worst, CHUNK, spent, reorders)
        if not alive:
            sc.row("CROSSING_walked", "titan walks the staged lane", "UNMEASURED", "HARNESS",
                   "titan gone mid-crossing (dead/despawned): " + detail)
        elif not reached:
            sc.row("CROSSING_walked", "titan walks the staged lane end to end", "FAIL", "MOD", "did not reach the goal: " + detail)
        elif len(path) < 3 or worst > MAX_STEP:
            sc.row("CROSSING_walked", "titan WALKS (no jump)", "FAIL", "MOD", "teleport-like or unsampled: " + detail)
        else:
            sc.row("CROSSING_walked", "titan walks the staged lane end to end", "PASS", "MOD", detail)
        lost = dict((k, c0.get(k, 0) - c1.get(k, 0)) for k in ("wall", "ring", "tree", "giant"))
        dd = "before %s after %s destroyed %s rubble +%d" % (c0, c1, lost, c1.get("rubble", 0) - c0.get("rubble", 0))
        if not c1:
            return sc.row("CROSSING_destroys", "the crossing destroys what it passes", "UNMEASURED", "HARNESS",
                          "after-census unreadable; " + dd)
        if not reached:
            return sc.row("CROSSING_destroys", "the crossing destroys what it passes", "UNMEASURED", "HARNESS",
                          "no full crossing to judge; " + dd)
        if c0.get("ring", 0) != len(RING):
            return sc.row("CROSSING_destroys", "the crossing breaks through the wall ring sealing its goal", "UNMEASURED",
                          "SITE", "the ring was not built whole (%d/%d walls); %s" % (c0.get("ring", 0), len(RING), dd))
        ok = lost["ring"] > 0
        return sc.row("CROSSING_destroys", "the crossing breaks through the wall ring sealing its goal (and what else it passes)",
                      "PASS" if ok else "FAIL", "MOD", dd)

    def death(self, sc):
        _, txt = sc.hook(HOOKS, "SiteReport")
        self.sites_before = set(s["id"] for s in sites(txt))
        p = sc.pawn(self.pid)
        if not p:
            sc.row("DEATH_titan_dies", "the titan dies", "UNMEASURED", "HARNESS", "titan not on the map")
            return sc.row("DEATH_corpse_site", "its corpse becomes a site", "UNMEASURED", "HARNESS", "no titan")
        self.death_cell = (p.get("x"), p.get("z"))
        how, hits = None, 0
        for hits in range(1, 41):
            sc.call("jawa/damage", thingId=self.pid, damageDef="Bullet", amount=400, armorPenetration=1, allowColonists=False)
            q = sc.pawn(self.pid)
            if not q or q.get("dead"):
                how = "ORDINARY death path: %d x jawa/damage Bullet 400 (Thing.TakeDamage; the cause is staged)" % hits
                break
            self.death_cell = (q.get("x"), q.get("z"))
        if how is None:
            ok, t = sc.hook(HOOKS, "KillTitanAt", "%s|%d,%d" % (KIND, self.death_cell[0], self.death_cell[1]))
            if not ok or "tier=T3" not in t:
                sc.row("DEATH_titan_dies", "the titan dies", "UNMEASURED", "HARNESS", "damage did not kill; KillTitanAt: %s" % t)
                return sc.row("DEATH_corpse_site", "its corpse becomes a site", "UNMEASURED", "HARNESS", "no death")
            how = "STAGED: damage did not kill in 40 hits; KillTitanAt %s (a second, generated adult; the walker stays)" % t[:120]
        sc.rec.setdefault("staged", []).append("death: " + how)
        sc.row("DEATH_titan_dies", "the titan dies", "PASS", "MOD" if how.startswith("ORDINARY") else "HARNESS", how)
        sc.ticks(300)
        ok, txt = sc.hook(HOOKS, "SiteReport")
        new = [s for s in sites(txt) if s["id"] not in self.sites_before]
        near = [s for s in new if s.get("at") and abs(s["at"][0] - self.death_cell[0]) <= NEAR
                and abs(s["at"][1] - self.death_cell[1]) <= NEAR]
        if not ok:
            return sc.row("DEATH_corpse_site", "its corpse becomes a Building_TitanicCorpseSite", "UNMEASURED", "HARNESS", txt[:200])
        self.site = near[0] if near else None
        return sc.row("DEATH_corpse_site", "its corpse becomes a Building_TitanicCorpseSite", "PASS" if near else "FAIL", "MOD",
                      "death cell %s; new sites %s" % (self.death_cell, [(s["id"], s.get("at")) for s in new]))

    def crowd(self, sc):
        bad = [f for f, v in (("corpseSiteScavengersEnabled", True), ("corpseSiteScavengerDailyChance", 1),
                              ("corpseSiteCampsEnabled", True), ("corpseSiteCampDailyChance", 1)) if not self.st.put(f, v)]
        if bad or not self.site:
            sc.row("CROWD_arrives", "a crowd comes to the remains", "UNMEASURED", "HARNESS", "settings %s site %s" % (bad, self.site))
            return sc.row("CROWD_targets_site", "the crowd targets the site", "UNMEASURED", "HARNESS", "not staged")
        sid = self.site["id"]
        ok, t = sc.hook(HOOKS, "SiteDailyStep")
        sc.rec.setdefault("staged", []).append("crowd: SiteDailyStep called with chances 1 (the site's own daily step)")
        mine, waited, at = None, 0, False
        while True:
            _, txt = sc.hook(HOOKS, "SiteReport")
            mine = next((s for s in sites(txt) if s["id"] == sid), None)
            at = bool(mine and any("atSite=True" in s for s in mine["S"]))
            if at or waited >= 12000 or not mine:
                break
            d = sc.ticks(1000)
            waited += d if d else 1000
        came = bool(mine and ((mine.get("scav") or 0) + (mine.get("camp") or 0)) > 0)
        sc.row("CROWD_arrives", "scavengers/campers arrive through the site's daily step", "PASS" if came else "FAIL", "MOD",
               "SiteDailyStep %s; site %s" % (t[:120], (mine or {}).get("raw", "gone")[:400]))
        if not came:
            return sc.row("CROWD_targets_site", "the crowd targets the site", "UNMEASURED", "HARNESS", "nobody came")
        if at:
            return sc.row("CROWD_targets_site", "the crowd targets the site", "PASS", "MOD",
                          "a scavenger atSite=True after %d ticks: %s" % (waited, mine["S"][:4]))
        if not mine["S"]:
            return sc.row("CROWD_targets_site", "the crowd targets the site", "UNMEASURED", "HARNESS",
                          "campers only (no atSite reading for camps): %s" % mine["C"][:3])
        return sc.row("CROWD_targets_site", "the crowd targets the site", "FAIL", "MOD",
                      "no scavenger at the site after %d ticks: %s" % (waited, mine["S"][:4]))


def run(args, bridge, site, ticker=None):
    """One gated showcase. bridge: .call(tool, **kw) -> dict; site: .begin()/.restore() (LiveSite or a fake)."""
    sc = SC.Showcase(bridge, args.out, "showcase_titan_live.py", ITEM, REQUIRED, ticker=ticker)
    sc.rec.update(promise="titans", site_key=SITE_KEY, snapshot_prefix=SNAP_PREFIX, order=["CONTROL", "CROSSING", "DEATH", "CROWD"])
    st = SC.Settings(sc, FIELDS)
    show = TitanShowcase(sc, st)
    try:
        sc.rec["site"] = site.begin()
        if not st.snapshot():
            sc.row("PRE_ready", "settings readable", "UNMEASURED", "HARNESS", "settings snapshot unreadable %s" % st.prior)
        sc.run_phases([("PRE", show.pre, ROWS["PRE"]), ("CONTROL", show.control, ROWS["CONTROL"]),
                       ("CROSSING", show.crossing, ROWS["CROSSING"]),
                       ("DEATH", show.death, ROWS["DEATH"]), ("CROWD", show.crowd, ROWS["CROWD"])])
    except Exception as ex:  # noqa: BLE001
        sc.rec["error"] = repr(ex)
    finally:
        sc.rec["settings_restore_bad"] = st.restore()
        sc.rec["site_restore_errors"] = site.restore()
        sc.rec["finished"] = SC.utc()
        sc.save()
    return sc


def main(argv=None):
    ap = argparse.ArgumentParser(description="HugeThings TITAN promise: crossing, death, crowd (gated, on a restored site).")
    ap.add_argument("--out", default=os.path.join("/mnt/d/ClaudeWork/rimmandrake/showcases",
                                                  "showcase_titan_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    a = ap.parse_args(argv)
    try:
        b, ticker = SC.live_bridge()
    except Exception as ex:  # noqa: BLE001 -- no bridge is "could not ask", never a mod FAIL
        print("UNMEASURED HARNESS: no live bridge: %r" % ex)
        return 2
    sc = run(a, b, SC.LiveSite(b.call, SITE_KEY, SNAP_PREFIX), ticker)
    print("wrote %s  summary %s" % (a.out, sc.summary()))
    return sc.exit_code()


if __name__ == "__main__":
    sys.exit(main())
