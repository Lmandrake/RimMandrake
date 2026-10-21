"""titan_events_live.py -- the live rows A2..A5 of TITAN_CAMPS_SCAVENGERS_EVENTS_1 (Huge Things corpse-site scavengers and
camps, the footfall-warned RM_TitanPassage, their toggles), on whatever Playing map is current. Drives the static hooks of
RimMandrake.TitanicCreatures.TitanValidationHooks (Source/Titanic/Events/TitanValidationHooks.cs) through jawa/static_call,
because DebugDailyStep / DebugArriveNow are instance methods static_call refuses.

  python.exe src/RimMandrake/HugeThings/northstar/titan_events_live.py [--site X,Z] [--t3 RM_Oommok] [--out FILE]

The map is DIRTIED (a T3 is killed into a corpse site, predators and visitors walk in, a titan crosses, a live T3 is spawned):
run it on a save you will reload WITHOUT saving. Settings it touches are snapshotted first and restored in `finally`.

Rows: {id, criterion, status PASS|FAIL|UNMEASURED, cls MOD|SITE|HARNESS, detail}. "Could not ask" is UNMEASURED.

Order matters (learned from the code, not the item): a site draws scavengers only while none of its last draw is spawned, and
makes a camp only while its camper list is empty, so the toggle rows run FIRST on the fresh site:
  T0 both toggles off, both chances 1   -> no scavenger, no camp            (A5 scavengers + camps)
  T1 scavengers off, camps on, 1 h camp -> camp > 0, scavengers 0           (A3 arrive, A5 scavengers)
     advance past the camp hours        -> every camper gone / exiting      (A3 leave)
  T2 scavengers on, camps off           -> scavengers > 0, camp 0           (A2 draw, A5 camps)
     advance until one is at the site, one more step -> eaten rises, meat falls by at least that   (A2 eat)
  P  titanEventsEnabled off -> canFire False; on -> fire, pending + tremor letter; arrive -> tier >= T2, not homed here,
     LordJob_ExitMapNear; a live T3 on the map -> no eligible kind is T3     (A4, A5 passage)
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

ITEM = "TITAN_CAMPS_SCAVENGERS_EVENTS_1"
HOOKS = "RimMandrake.TitanicCreatures.TitanValidationHooks"
SETTINGS = "RimMandrake.HugeThings.RM_HugeThingsSettings"
FIELDS = ["corpseSiteScavengersEnabled", "corpseSiteScavengerDailyChance", "corpseSiteCampsEnabled",
          "corpseSiteCampDailyChance", "corpseSiteCampHours", "titanEventsEnabled"]


class Run(object):
    def __init__(self, rb, out):
        self.rb, self.out, self.rows, self.log = rb, out, [], []

    def call(self, tool, **kw):
        try:
            r = self.rb.call(tool, kw) or {}
        except Exception as ex:  # noqa: BLE001
            r = {"success": False, "error": "call raised: %s" % ex}
        self.log.append((tool, kw, str(r)[:400]))
        return r

    def hook(self, method, args=""):
        r = self.call("jawa/static_call", type=HOOKS, method=method, args=args)
        txt = str(r.get("result") if r.get("result") is not None else r.get("error") or r.get("message") or r)
        print("    %s(%s) -> %s" % (method, args, txt[:600]), flush=True)
        return r.get("success") is True and not txt.startswith("FAIL"), txt

    def get(self, f):
        return self.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f).get("value")

    def put(self, f, v):
        return self.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v)).get("success")

    def ticks(self, n):
        done = 0
        while done < n:
            k = min(1000, n - done)
            self.call("rimworld/step_game_ticks", ticks=k)
            done += k

    def row(self, rid, crit, status, cls, detail):
        self.rows.append(dict(id=rid, item=ITEM, criterion=crit, status=status, cls=cls, detail=detail))
        print("  %-34s %-10s %-7s %s %s" % (rid, status, cls, crit, detail[:300]), flush=True)
        self.save()

    def save(self):
        with open(self.out, "w", encoding="utf-8") as f:
            json.dump(dict(script="titan_events_live.py", when=time.strftime("%Y-%m-%dT%H:%M:%S"), rows=self.rows,
                           calls=self.log), f, indent=1, default=str)


def parse_site(txt):
    """SiteReport text -> dict of the FIRST site (or None)."""
    parts = txt.split(" | ")
    if len(parts) < 2:
        return None
    s = parts[1]
    d = {"raw": s}
    for key in ("meat", "eaten", "scav", "camp"):
        try:
            d[key] = int(s.split(" %s=" % key, 1)[1].split()[0])
        except (IndexError, ValueError):
            d[key] = None
    d["S"] = [x.split("]")[0] for x in s.split(" S[")[1:]]
    d["C"] = [x.split("]")[0] for x in s.split(" C[")[1:]]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="", help="cell X,Z for the titan corpse (default: map centre, then offsets)")
    ap.add_argument("--t3", default="RM_Oommok")
    ap.add_argument("--passage-only", action="store_true", help="skip the corpse-site blocks (a site already stands)")
    ap.add_argument("--out", default=os.path.join(REPO, "src", "RimMandrake", "HugeThings", "northstar",
                                                  "titan_events_live_%s.json" % time.strftime("%Y%m%dT%H%M")))
    a = ap.parse_args()
    from rimbridge_client import RimBridge, discover_from_log
    host, port, token = discover_from_log()
    with RimBridge(host, port, token, timeout=180.0) as rb:
        R = Run(rb, a.out)
        snap = dict((f, R.get(f)) for f in FIELDS)
        if any(v is None for v in snap.values()):
            R.row("B0_settings_snapshot", "-", "UNMEASURED", "HARNESS", "could not read %r" % snap)
            return 2
        print("  snapshot %r" % snap, flush=True)
        try:
            passage(R, a) if a.passage_only else body(R, a)
        finally:
            for f, v in snap.items():
                R.put(f, v)
            print("  restored %r" % dict((f, R.get(f)) for f in FIELDS), flush=True)
            R.save()
    print("rows -> %s" % a.out)
    return 0


def body(R, a):
    mi = R.call("jawa/map_info")
    size = mi.get("size") or mi.get("mapSize") or {}
    print("  map_info %s" % str(mi)[:300], flush=True)
    # ---------- the site: kill a T3 into a corpse, let MapComponent_TitanicCorpseSites convert it
    cells = []
    if a.site:
        x, z = [int(v) for v in a.site.split(",")]
        cells = [(x, z)]
    else:
        try:
            cx, cz = int(size.get("x")) // 2, int(size.get("z")) // 2
        except (TypeError, ValueError, AttributeError):
            cx = cz = 125
        cells = [(cx + dx, cz + dz) for dx, dz in ((0, 0), (25, 0), (-25, 0), (0, 25), (0, -25), (25, 25), (-25, -25))]
    site = None
    for (x, z) in cells:
        ok, txt = R.hook("KillTitanAt", "%s|%d,%d" % (a.t3, x, z))
        if not ok or "tier=T3" not in txt:
            R.row("B0_t3_killed", "-", "UNMEASURED", "HARNESS", "KillTitanAt %s at %d,%d: %s" % (a.t3, x, z, txt[:200]))
            return
        R.ticks(300)
        ok, rep = R.hook("SiteReport")
        site = parse_site(rep) if ok else None
        if site:
            break
    if not site:
        R.row("B0_site_made", "-", "UNMEASURED", "SITE", "no corpse site appeared at any of %r" % cells)
        return
    R.row("B0_site_made", "-", "PASS", "MOD", site["raw"][:200])

    # ---------- T0: both toggles off
    R.put("corpseSiteScavengersEnabled", False); R.put("corpseSiteCampsEnabled", False)
    R.put("corpseSiteScavengerDailyChance", 1.0); R.put("corpseSiteCampDailyChance", 1.0)
    ok, rep = R.hook("SiteDailyStep")
    s = parse_site(rep) if ok else None
    if not s:
        R.row("A5_both_off", "A5", "UNMEASURED", "HARNESS", rep[:200])
    else:
        R.row("A5_both_off", "A5", "PASS" if (s["scav"], s["camp"]) == (0, 0) else "FAIL", "MOD",
              "scav=%s camp=%s at chance 1 with both toggles off" % (s["scav"], s["camp"]))

    # ---------- T1: camps only, 1 h
    R.put("corpseSiteCampsEnabled", True); R.put("corpseSiteCampHours", 1.0)
    ok, rep = R.hook("SiteDailyStep")
    s = parse_site(rep) if ok else None
    if not s:
        R.row("A3_camp_arrives", "A3", "UNMEASURED", "HARNESS", rep[:200])
    else:
        bad = [c for c in s["C"] if "hostile=True" in c or "lord=LordJob_VisitColony" not in c]
        if not s["camp"]:
            R.row("A3_camp_arrives", "A3", "FAIL", "MOD", "camp chance 1, camps on: CamperCount %s (%s)" % (s["camp"], s["raw"][:200]))
        else:
            R.row("A3_camp_arrives", "A3", "PASS" if not bad else "FAIL", "MOD",
                  "CamperCount=%d; %s" % (s["camp"], "; ".join(s["C"])[:300]))
        R.row("A5_scavengers_off", "A5", "PASS" if s["scav"] == 0 else "FAIL", "MOD",
              "scavengers off, chance 1: scav=%s (camps on in the same step: camp=%s)" % (s["scav"], s["camp"]))
        if s["camp"]:
            # 1 h = 2500 ticks; VisitColony leaves through its exit toil, then walking off the map takes a while
            left = None
            for _ in range(10):
                R.ticks(1000)
                ok, rep = R.hook("SiteReport")
                s2 = parse_site(rep) if ok else None
                if s2 is None:
                    break
                gone = all(("spawned=False" in c) or ("Exit" in c) or ("lord=none" in c) for c in s2["C"]) if s2["C"] else True
                if gone and _ >= 2:
                    left = s2
                    break
            R.row("A3_camp_leaves", "A3", "PASS" if left else "FAIL", "MOD",
                  ("after camp hours 1: %s" % "; ".join(left["C"])[:300]) if left else "campers still visiting 10000 ticks after a 1 h camp")
        R.put("corpseSiteCampsEnabled", False)
        R.ticks(5000)   # let leaving campers despawn so the camper list empties

    # ---------- T2: scavengers only
    R.put("corpseSiteScavengersEnabled", True)
    ok, rep = R.hook("SiteDailyStep")
    s = parse_site(rep) if ok else None
    if not s:
        R.row("A2_draw", "A2", "UNMEASURED", "HARNESS", rep[:200])
    else:
        R.row("A5_camps_off", "A5", "PASS" if s["camp"] == 0 or all("spawned=False" in c for c in s["C"]) else "FAIL", "MOD",
              "camps off, chance 1: camp=%s" % s["camp"])
        if not s["scav"]:
            R.row("A2_draw", "A2", "FAIL", "MOD", "scavenger chance 1, on: ScavengerCount 0 -- %s (a map biome with no "
                  "season-survivable untiered predator draws nothing: check ScavengerKinds before calling this MOD)" % s["raw"][:200])
            return passage(R, a)
        bad = [x for x in s["S"] if "tier=None" not in x or "pred=True" not in x or "homedHere=True" not in x]
        R.row("A2_draw", "A2", "PASS" if not bad else "FAIL", "MOD", "ScavengerCount=%d; %s" % (s["scav"], "; ".join(s["S"])[:300]))
        at = None
        for _ in range(12):
            R.ticks(1000)
            ok, rep = R.hook("SiteReport")
            s2 = parse_site(rep) if ok else None
            if s2 and any("atSite=True" in x for x in s2["S"]):
                at = s2
                break
        if not at:
            R.row("A2_eat", "A2", "UNMEASURED", "SITE", "no scavenger reached 10 cells of the site in 12000 ticks")
        else:
            ok, rep = R.hook("SiteDailyStep")
            s3 = parse_site(rep) if ok else None
            if not s3:
                R.row("A2_eat", "A2", "UNMEASURED", "HARNESS", rep[:200])
            else:
                de, dm = s3["eaten"] - at["eaten"], at["meat"] - s3["meat"]
                R.row("A2_eat", "A2", "PASS" if de > 0 and dm >= de else "FAIL", "MOD",
                      "eaten +%d, meat -%d (spoilage the rest) with %d at the site" %
                      (de, dm, sum(1 for x in at["S"] if "atSite=True" in x)))
    passage(R, a)


def passage(R, a):
    # IncidentWorker.CanFireNow caches its CanFireNowSub answer per game tick (lastCheckCanRunTick): on a paused game two asks
    # in one tick return the FIRST answer, so every toggle flip is followed by a tick before asking again (run 1, 2026-10-21,
    # read the off-answer back as "cannot fire" with events on).
    R.put("titanEventsEnabled", False)
    R.ticks(2)
    ok, txt = R.hook("PassageCanFire")
    R.row("A5_titan_events_off", "A5", "PASS" if ok and "canFire=False" in txt else ("FAIL" if ok else "UNMEASURED"), "MOD", txt[:200])
    R.put("titanEventsEnabled", True)
    R.ticks(2)
    ok, txt = R.hook("PassageCanFire")
    # the 2026-10-21 water law, read straight off the pool: on a land map no eligible kind is tagged :sea, on a sea map none
    # is tagged :land (run of 2026-10-21 on R3 Stillsand listed RM_Reefback, RM_Lanternwhale, RSW_ShadeWhale... on foot)
    if ok and " eligible=" in txt and "seaMap=" in txt:
        sea_map = "seaMap=True" in txt
        wrong = ":land" if sea_map else ":sea"
        R.row("A4_water_law", "A4", "FAIL" if wrong in txt else "PASS", "MOD", txt[:300])
    else:
        R.row("A4_water_law", "A4", "UNMEASURED", "HARNESS", "PassageCanFire carries no seaMap= (old DLL?): %s" % txt[:200])
    if not ok or "canFire=True" not in txt:
        R.row("A4_can_fire", "A4", "UNMEASURED", "SITE", "events on but cannot fire here: %s" % txt[:300])
        return
    before = len((R.call("jawa/letter_list") or {}).get("letters") or [])
    r = R.call("jawa/fire_incident", incidentDef="RM_TitanPassage", forced=True)
    ok, rep = R.hook("PassageReport")
    letters = (R.call("jawa/letter_list") or {}).get("letters") or []
    tremor = [l for l in letters[before:] + letters[-3:] if "remor" in str(l.get("label"))]
    R.row("A4_pending_and_letter", "A4", "PASS" if ok and "pending=True" in rep and tremor else "FAIL", "MOD",
          "%s; letter %s; fire %s" % (rep[:160], (tremor[-1] if tremor else letters[-1:]), str(r)[:80]))
    R.ticks(600)
    ok, rep = R.hook("PassageReport")
    R.row("A4_still_pending_through_tremors", "A4", "PASS" if "pending=True" in rep else "FAIL", "MOD", rep[:200])
    R.hook("PassageArriveNow")
    R.ticks(5)
    ok, rep = R.hook("PassageReport")
    # TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT (owner, by card 2026-10-21): the pool is the map biome's own hints (passage list,
    # else its own roster), so homedHere=True is now normal; the old "homedHere=False" bar encoded card #5's rule and is
    # gone. What must hold is the water law: a sea giant never walks a land map, a land giant never swims a sea map.
    good = ok and "pending=False" in rep and " arrived=" in rep and "spawned=True" in rep and "seaMatch=True" in rep \
        and "lord=LordJob_ExitMapNear" in rep and (" tier=T2" in rep or " tier=T3" in rep)
    R.row("A4_arrives", "A4", "PASS" if good else "FAIL", "MOD", rep[:300])
    # the one-T3-per-map law: a live T3 on the map leaves no T3 among the eligible kinds
    r = R.call("jawa/spawn_pawn", kindDef=a.t3, faction="none", count=1)
    R.ticks(2)
    ok, txt = R.hook("PassageCanFire")
    if not ok or "t3OnMap=True" not in txt:
        R.row("A4_no_second_t3", "A4", "UNMEASURED", "HARNESS", "spawn %s: %s; %s" % (a.t3, str(r)[:120], txt[:200]))
    else:
        R.row("A4_no_second_t3", "A4", "PASS" if ":T3" not in txt else "FAIL", "MOD", txt[:300])


if __name__ == "__main__":
    sys.exit(main())
