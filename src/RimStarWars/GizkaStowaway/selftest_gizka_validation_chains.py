#!/usr/bin/env python3
"""selftest_gizka_validation_chains.py -- GIZKA_VALIDATION_FIX_LOST_REASON_DONOR_PICK: two harness faults in
validation.py, driven through modcheck's real TestContext on a fake bridge (no game):
  * harmony_wiring: hook 1 UNMEASURED, hook 2 a real FAIL -> every row after the FAIL must be UNMEASURED WITH a reason
    (the old _comp cleared upstream_reason to None, so the rows after a later FAIL carried no reason at all);
  * donor_patch: with both the donor `Gizka` and the port `RSW_Gizka` loaded, only RSW_Gizka is patched to 15
    (RSW_GizkaDonorPatches.xml; the donor block was deleted), so the row must read RSW_Gizka and PASS, not FAIL on the
    donor's untouched 100; with only the donor loaded it is UNMEASURED, never a FAIL.
GIZKA_STOWAWAY_UNMEASURED_ROWS_1: the five live mechanics chains run against Sim, a toy of the mod behind RSW_GizkaProbe:
every row PASSes on a right mod, each PLANTED defect FAILs its row, and a mutation pass proves every _fail in those
chains is load-bearing (replacing any one with `pass` lets some planted defect through, which turns this RED).
Offline.

    python3 src/RimStarWars/GizkaStowaway/selftest_gizka_validation_chains.py
"""
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402
from modcheck.suite import TestContext  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


class Fake(object):
    def __init__(self, loaded=("RSW_Gizka",), mv=None):
        self.loaded, self.mv, self.hook_n = set(loaded), mv or {}, 0

    def track(self, *a, **k):
        pass

    def call(self, tool, **p):
        if tool == "jawa/harmony_patches":
            self.hook_n += 1
            if self.hook_n == 1:
                return {"success": False, "message": "no such method"}
            return {"success": True, "methods": [{"prefixes": [{"owner": "someone.else"}]}]}
        if tool == "jawa/get_defs":
            d = p.get("defs", "")
            if d.startswith("PawnKindDef/"):
                return {"success": True, "foundCount": 1 if d.split("/", 1)[1] in self.loaded else 0}
            if d.startswith("ThingDef/") and p.get("fields") == "statBases":
                k = d.split("/", 1)[1]
                return {"success": True, "defs": [{"fields": {"statBases": [{"stat": "MarketValue", "value": self.mv[k]}]}}]}
        return {"success": True}


class Sim(object):
    """A toy of the mod behind RSW_GizkaProbe (GIZKA_STOWAWAY_UNMEASURED_ROWS_1), right by default; `bug` plants one
    defect (or a "+"-joined set of them) so a row can be shown to FAIL. Every _fail in the live chains is reached by
    one planted defect in PLANTED: replacing any of them with `pass` turns this selftest RED."""
    def __init__(self, bug=None):
        self.bugs = frozenset((bug or "").split("+")) - {""}
        self.n, self.cool, self.mem, self.uid = 0, False, 0, 0
        self.s = {"stowawayEventsEnabled": "True", "discoveryFrequency": "1.0", "triggerGravship": "True",
                  "triggerSalvage": "True", "triggerTrade": "True", "triggerQuest": "True", "breedingRate": "1.0",
                  "populationCap": "22", "chewingEnabled": "True", "cullGuiltEnabled": "True", "globalBreedingRate": "1.0"}
        self.food, self.temp, self.pos = {}, {}, {}
        self.applied, self.power, self.broken, self.col, self.applies = 1.0, False, False, (0, 0), 0

    def has(self, bug):
        return bug in self.bugs

    def track(self, *a, **k):
        pass

    def on(self, k):
        return self.s[k].lower() == "true" or self.has("ignore_" + k)

    def kv(self, **d):
        return {"success": True, "result": ";".join("%s=%s" % (k, v) for k, v in d.items())}

    def deliver(self, toggle):
        freq = float(self.s["discoveryFrequency"]) > 0 or self.has("ignore_discoveryFrequency")
        if not (self.on("stowawayEventsEnabled") and self.on(toggle) and freq):
            return
        if self.cool and not self.has("no_cooldown"):
            return
        self.n += 2 if self.has("double_gravship") and toggle == "triggerGravship" else 1
        self.cool = True

    def probe(self, m, a):
        b = self.n
        if m == "ResetDiscoveryCooldown":
            self.cool = False
            return self.kv(ok=1)
        if m == "Count":
            return {"success": True, "result": str(self.n)}
        if m == "Fire":
            tog = {"gravship": "triggerGravship", "trade": "triggerTrade", "quest": "triggerQuest"}.get(a[0])
            if a[0] == "trade_unchanged" and self.has("empty_trade_delivers"):
                tog = "triggerTrade"
            if a[0] == "quest_fail" and self.has("quest_fail_delivers"):
                tog = "triggerQuest"
            if tog:
                self.deliver(tog)
            return self.kv(before=b, after=self.n)
        if m == "Deconstruct":
            if a[0].startswith("ShipChunk") or self.has("any_salvage_delivers"):
                self.deliver("triggerSalvage")
            return self.kv(def_=a[0], before=b, after=self.n)
        if m == "SpawnAdult":
            self.uid += 1
            self.n += 1
            gid = "Gizka%d" % self.uid
            self.food[gid], self.temp[gid] = 0.8, 20.0
            self.pos[gid] = tuple(int(v) for v in a[1].split(","))
            return self.kv(id=gid, lifeStage=2, stages=3)
        if m == "SetFood":
            self.food[a[0]] = float(a[1])
            return self.kv(food=a[1])
        if m == "SetRoomTemp":
            self.temp[a[0]] = float(a[1])
            return self.kv(temp=a[1])
        if m == "TickFecundity":
            g, fuse, delta = a[0], int(a[1]), int(a[2])
            warm = self.temp[g] >= 12 or self.has("cold_ignored")
            fed = self.food[g] >= 0.35 or self.has("hunger_ignored")
            cap = int(self.s["populationCap"])
            rate = 1.0 if self.has("rate_ignored") else float(self.s["breedingRate"])
            if not (warm and fed) or not self.on("stowawayEventsEnabled"):
                after = fuse
            elif fuse - delta > 0:
                after = fuse if self.has("fuse_frozen") else fuse - delta
            else:
                after = 0 if self.has("no_rearm") else int(V.replicate_interval_days(4, 8, self.n, cap, rate) * 60000)
                if (self.n < cap or self.has("breeds_at_cap")) and not self.has("no_replicate"):
                    self.n += 1
            return self.kv(temp=self.temp[g], food=self.food[g], minTemp=12, minFood=0.35, cap=cap, fuseBefore=fuse,
                           fuseAfter=after, before=b, after=self.n)
        if m == "ChewCheck":
            st = V.stage_for(V.load_srcs(), self.n, int(self.s["populationCap"]))
            powered = self.power or self.has("chew_unpowered")
            gate = 2 if self.has("chew_below_infestation") else 3
            if self.on("chewingEnabled") and powered and st >= gate and not self.has("chew_never"):
                self.broken = True
            broken, self.broken = self.broken, False           # each check reads a fresh heater
            shown = min(st + 1, 4) if self.has("stage_misreported") else st   # the probe's stage is not the gating one
            return self.kv(count=self.n, stage=["None", "Cute", "Underfoot", "Infestation", "Plague"][shown],
                           powerOn=self.power, brokenBefore=False, brokenAfter=broken)
        if m == "Kill":
            g = a[0]
            near = g in self.pos and abs(self.pos[g][0] - self.col[0]) + abs(self.pos[g][1] - self.col[1]) <= 12
            lineage = g.startswith("Gizka") or self.has("cull_any_lineage")
            if lineage and self.on("cullGuiltEnabled") and (near or self.has("cull_any_range")) and not self.has("cull_never"):
                self.mem += 1
            return self.kv(stowaway=g.startswith("Gizka"), dead=True)
        if m == "MemoryCount":
            return {"success": True, "result": str(self.mem)}
        if m == "DonorFields":
            return self.kv(egg=8.0 / self.applied, mate=12.0 / self.applied, global_=self.s["globalBreedingRate"])
        if m == "Apply":
            self.applies += 1
            if not self.has("apply_noop") and not (self.has("apply_sticky") and self.applies > 1):
                self.applied = float(self.s["globalBreedingRate"])
            return {"success": True, "result": "null"}
        return {"success": False, "message": "unknown " + m}

    def call(self, tool, **p):
        if tool == "jawa/mod_settings_field":
            if p["action"] == "set":
                self.s[p["field"]] = str(p["value"])
                return {"success": True}
            return {"success": True, "value": self.s[p["field"]]}
        if tool == "jawa/static_call":
            return self.probe(p["method"], p["args"].split("|") if p["args"] else [])
        if tool == "jawa/list_things":
            if self.has("no_heater"):
                return {"success": True, "things": []}
            return {"success": True, "things": [{"id": "%s%d" % (p["defName"], self.uid)}]}
        if tool == "jawa/power_net":
            self.power = bool(p["forcePowerOn"])
            return {"success": True, "powerOnAfter": self.power}
        if tool == "jawa/spawn_pawn":
            self.uid += 1
            if p["kindDef"] == "Colonist":
                self.col = (p["x"], p["z"])
                return {"success": True, "pawns": [{"id": "Colonist%d" % self.uid}]}
            self.pos["Wild%d" % self.uid] = (p["x"], p["z"])
            return {"success": True, "pawns": [{"id": "Wild%d" % self.uid}]}
        if tool == "jawa/get_defs":
            return {"success": True, "foundCount": 0 if self.has("no_gizka") else 1}
        return {"success": True}


# (planted defect, chain, the row that must FAIL); one per _fail in the live chains (GIZKA_STOWAWAY_UNMEASURED_ROWS_1)
PLANTED = (
    ("double_gravship", "discovery_triggers", "gravship_landing_delivers_one_tame_gizka"),
    ("no_cooldown", "discovery_triggers", "cooldown_blocks_a_second_discovery"),
    ("empty_trade_delivers", "discovery_triggers", "trade_delivers_one_and_an_empty_trade_none"),
    ("quest_fail_delivers", "discovery_triggers", "quest_success_delivers_one_and_failure_none"),
    ("any_salvage_delivers", "discovery_triggers", "salvage_deconstruction_delivers_one_and_other_things_none"),
    ("ignore_triggerGravship", "discovery_triggers", "every_off_switch_silences_its_trigger"),
    ("ignore_triggerTrade", "discovery_triggers", "every_off_switch_silences_its_trigger"),
    ("ignore_triggerQuest", "discovery_triggers", "every_off_switch_silences_its_trigger"),
    ("ignore_discoveryFrequency", "discovery_triggers", "every_off_switch_silences_its_trigger"),
    ("ignore_triggerSalvage", "discovery_triggers", "every_off_switch_silences_its_trigger"),
    ("fuse_frozen", "fecundity_live", "fecundity_replicates_while_fed_and_warm"),
    ("no_replicate", "fecundity_live", "fecundity_replicates_while_fed_and_warm"),
    ("no_rearm", "fecundity_live", "fecundity_replicates_while_fed_and_warm"),
    ("hunger_ignored", "fecundity_live", "hunger_stalls_the_fuse"),
    ("cold_ignored", "fecundity_live", "cold_below_breeding_gate_stalls_replication"),
    ("breeds_at_cap", "fecundity_live", "population_cap_stops_breeding"),
    ("rate_ignored", "fecundity_live", "breeding_rate_divides_the_interval"),
    ("no_heater", "chewing_live", "site_ready"),
    ("ignore_chewingEnabled", "chewing_live", "chewing_off_spares_a_powered_building"),
    ("chew_unpowered", "chewing_live", "unpowered_building_is_not_chewed"),
    ("chew_below_infestation", "chewing_live", "below_infestation_nothing_is_chewed"),
    ("chew_never", "chewing_live", "infestation_stage_chews_powered_buildings"),
    ("stage_misreported", "chewing_live", "infestation_stage_chews_powered_buildings"),
    ("ignore_cullGuiltEnabled", "cull_guilt_live", "cull_guilt_off_weighs_nothing"),
    ("cull_any_range", "cull_guilt_live", "unwatched_or_wild_kills_weigh_nothing"),
    ("cull_any_lineage", "cull_guilt_live", "unwatched_or_wild_kills_weigh_nothing"),
    ("cull_never", "cull_guilt_live", "cull_weighs_on_watching_colonists"),
    ("apply_noop", "global_breeding_slider", "global_breeding_slider_rescales_donor_fields"),
    ("apply_sticky", "global_breeding_slider", "global_breeding_slider_rescales_donor_fields"),
)


LIVE_CHAINS = ("discovery_triggers", "fecundity_live", "chewing_live", "cull_guilt_live", "global_breeding_slider")


def run(chain, bridge, mod=None):
    t = TestContext(bridge)
    dict((mod or V).suite.chains)[chain](t)
    return t.components


def fail_mutants():
    """validation.py with ONE _fail(...) line of the live chains replaced by `pass`, built in memory (the file on disk is
    never touched). Yields (line number, line, module)."""
    path = os.path.join(HERE, "validation.py")
    lines = open(path, encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if '@suite.chain("%s")' % LIVE_CHAINS[0] in l)
    for i in range(start, len(lines)):
        m = re.match(r"^(\s*)_fail\(.*\)\s*$", lines[i])
        if not m:
            continue
        mod = types.ModuleType("validation_mutant_%d" % (i + 1))
        mod.__file__ = path
        src = "\n".join(lines[:i] + [m.group(1) + "pass"] + lines[i + 1:])
        exec(compile(src, path, "exec"), mod.__dict__)
        yield i + 1, lines[i].strip(), mod


def main():
    if V.suite is None:
        check("modcheck importable", False)
        return 1
    rows = run("harmony_wiring", Fake())
    verdicts = [c.verdict for c in rows]
    check("sanity: hook 1 UNMEASURED, hook 2 FAIL", verdicts[:2] == ["UNMEASURED", "FAIL"] and len(rows) >= 3, repr(verdicts))
    after = rows[2:]
    check("rows after the FAIL are UNMEASURED", after and all(c.verdict == "UNMEASURED" for c in after), repr(verdicts))
    check("rows after the FAIL carry a reason", after and all(c.detail for c in after),
          repr([(c.name, c.detail) for c in after][:3]))

    both = run("donor_patch", Fake(loaded=("Gizka", "RSW_Gizka"), mv={"Gizka": 100.0, "RSW_Gizka": 15.0}))
    check("donor and port loaded: the patched RSW_Gizka is read -> PASS", [c.verdict for c in both] == ["PASS"],
          repr([(c.verdict, str(c.detail)[:120]) for c in both]))
    port = run("donor_patch", Fake(loaded=("RSW_Gizka",), mv={"RSW_Gizka": 100.0}))
    check("control: an unpatched RSW_Gizka still FAILs", [c.verdict for c in port] == ["FAIL"], repr([c.verdict for c in port]))
    donor = run("donor_patch", Fake(loaded=("Gizka",), mv={"Gizka": 100.0}))
    check("donor only: UNMEASURED, not FAIL (nothing patches the donor)", [c.verdict for c in donor] == ["UNMEASURED"],
          repr([(c.verdict, str(c.detail)[:120]) for c in donor]))
    # GIZKA_STOWAWAY_UNMEASURED_ROWS_1: the live mechanics rows PASS on a right mod and each planted defect FAILs its row
    for chain in LIVE_CHAINS:
        rows = run(chain, Sim())
        check("right mod: %s all PASS" % chain, rows and all(c.verdict == "PASS" for c in rows),
              repr([(c.name, c.verdict, str(c.detail)[:140]) for c in rows if c.verdict != "PASS"]))
    for bug, chain, row in PLANTED:
        rows = {c.name: c.verdict for c in run(chain, Sim(bug))}
        check("planted %s: %s FAILs" % (bug, row), rows.get(row) == "FAIL", repr(rows))
    # mutation pass: every _fail of the live chains must be load-bearing -- with it replaced by `pass`, some planted
    # defect must stop reading FAIL on its row (else that check could be deleted and every proof would stay green)
    n_mut = 0
    for lineno, line, mod in fail_mutants():
        n_mut += 1
        caught = [bug for bug, chain, row in PLANTED
                  if {c.name: c.verdict for c in run(chain, Sim(bug), mod)}.get(row) != "FAIL"]
        check("mutant validation.py:%d (_fail -> pass) is caught by a planted defect" % lineno, caught, line[:120])
    check("sanity: the mutation pass found the live chains' _fail lines", n_mut >= 13, "found %d" % n_mut)
    for chain in LIVE_CHAINS:
        rows = run(chain, Sim("no_gizka"))
        check("no gizka creature loaded: %s reads UNMEASURED, never FAIL" % chain,
              rows and all(c.verdict == "UNMEASURED" for c in rows), repr([(c.name, c.verdict) for c in rows]))
    print("gizka validation chains: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
