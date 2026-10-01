"""validation.py -- modcheck suite for RimStarWars: Bacta (mandrake.rsw.bacta).
Walk: design/validation_walks/RimStarWars/Bacta.md  (`## must be true`, every line arrowed to a component here).
First script, BACTA_FIRST_SCRIPT_1 (debug_process.md section 2). Dev tooling, never deployed.

Live (python.exe, bridge held, game up on the `bacta` modset_builder tier):
    python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Bacta \\
        --plan src/RimStarWars/Bacta/northstar_plan.py
Offline: same with --mock --mock-skip-site (the plan registers northstar_mock.py's in-memory Bacta game).

Grounded in the mod's source: `BactaMod.cs` (the 8 toggles and 8 tunables, all `public static`, read through
`jawa/mod_settings_field`), `CompBactaImmersion.cs` (one pass per 250 ticks: heal, drain, auto-eject),
`BactaHealingUtility.cs` (the two laws: a Hediff_MissingPart is never touched, a hediff on the
ConsciousnessSource part is never touched), `Building_BactaTank.cs` (power/fluid gates, needs hold, corpse
admission), `CompUseEffect_BactaHeal.cs` (field items), the patches (trader stock, doctor recipes).

Every state change is read back from the game. A component that cannot ask records UNMEASURED, never PASS.
Each check can fail: northstar_mock.py has a BACTA_MOCK_BREAK mode per mechanic and selftest_bacta_mock.py
proves each one flips exactly its component to FAIL (the worker note lists the live way to break each case).

Not expressible with current bridge tools (walk marks them UNCOVERED): the visible suspended pawn / glass shell /
fluid column (visual), the bacta spray and `RSW_Administer*` doctor-bill path, scarHealPerDay / immunityGainPerDay /
tendQuality tuning and the infection assist (`WoundInfection` at any severity is instantly lethal through
`jawa/pawn_health`, MEASURED 2026-09-24, skills/rimbridge/references/silent-failures.md), droid speed multiplier.
"""
import contextlib
import json
import re
import sys
import time

from modcheck import Suite, ExpectationFailed

suite = Suite("Bacta")
suite.toggles = ["healingEnabled", "scarErasureEnabled", "infectionAssistEnabled", "suspendNeedsEnabled",
                 "autoEjectEnabled", "revivalEnabled", "medicalDroidEnabled", "fieldItemsEnabled",
                 "woundHealPerDay", "fluidCostPerDay", "revivalWindowHours", "scarHealPerDay"]

SETTINGS = "RimMandrake.StarWars.Bacta.BactaSettings"
DEFAULTS = {"healingEnabled": True, "scarErasureEnabled": True, "infectionAssistEnabled": True,
            "suspendNeedsEnabled": True, "autoEjectEnabled": True, "revivalEnabled": False,
            "medicalDroidEnabled": True, "fieldItemsEnabled": True,
            "woundHealPerDay": 30.0, "scarHealPerDay": 2.4, "immunityGainPerDay": 0.30,
            "fluidCostPerDay": 5.0, "tendQuality": 0.85, "revivalWindowHours": 6.0,
            "medicalDroidHealMultiplier": 1.5, "fieldItemPotency": 1.0}
TANK, DROID, FLUID, PATCH, SPRAY = "RSW_BactaTank", "RSW_MedicalDroid", "RSW_Bacta", "RSW_BactaPatch", "RSW_BactaSpray"
PASS_TICKS = 250
SIZE = 40


# ------------------------------------------------------------------ helpers

def _live(t):
    """True only for a real/mock Session and an unfailed chain; False for the offline declaration probe."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


class _Unmeasured(Exception):
    pass


def _unmeasured(t, why):
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, **kw):
    """t.component() plus the UNMEASURED fix-up (verdict UNMEASURED, real reason in the detail, chain not poisoned)."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    why = getattr(t, "_why", None)
    if why and not before:
        t.components[-1].detail = "UNMEASURED: %s" % why
        t.upstream_failed = False
    t._why = None
    if t.session is not None and t.components:
        c = t.components[-1]
        print("[bacta] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
              file=sys.stderr, flush=True)


def _ok(r, label):
    if not isinstance(r, dict) or not r.get("success"):
        _fail("%s failed: %s" % (label, str(r)[:300]))
    return r


def _sget(t, field):
    r = _ok(t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field), "settings get " + field)
    return r.get("value")


def _same(got, want):
    if isinstance(want, bool):
        return str(got).strip().lower() == str(want).lower()
    try:
        return abs(float(got) - float(want)) < 1e-3
    except (TypeError, ValueError):
        return False


def _sset(t, field, value):
    """Write a static settings field and read it back independently (never the setter's echo)."""
    _ok(t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=str(value)),
        "settings set %s=%s" % (field, value))
    got = _sget(t, field)
    if not _same(got, value):
        _fail("settings %s=%r did not take (read back %r)" % (field, value, got))


def _defaults(t):
    for k, v in DEFAULTS.items():
        _sset(t, k, v)


def _rect(t, size=SIZE):
    x, z = t.anchor
    return "%d,%d,%d,%d" % (x - size // 2, z - size // 2, size, size)


def _things(t, defs=None, group=None):
    if group:
        r = t.bridge_call("jawa/list_things", rect=_rect(t), limit=200, group=group)
    elif defs:
        r = t.bridge_call("jawa/list_things", rect=_rect(t), limit=200, defName=defs)
    else:
        r = t.bridge_call("jawa/list_things", rect=_rect(t), limit=200)
    _ok(r, "list_things")
    if r.get("isCompleteList") is False:
        _fail("list_things truncated: %s" % str(r)[:200])
    return r.get("things") or []


def _tid(t, d):
    rows = _things(t, d)
    return rows[0].get("id") if rows else None


def _pawn(t, pid):
    r = _ok(t.bridge_call("jawa/pawn_get", pawn=pid), "pawn_get " + str(pid))
    return (r.get("pawns") or [{}])[0]


def _sev(p, defname, part=None):
    v = [h.get("severity") for h in (p.get("hediffs") or [])
         if h.get("def") == defname and (part is None or h.get("part") == part)]
    return sum(v) if v else None


def _food(p):
    for n in (p.get("needs") or []):
        if n.get("need") == "Food":
            return n.get("level")
    return None


def _contained(p):
    return p.get("position") is None


def _inspect(t, tid):
    r = _ok(t.bridge_call("jawa/inspect_string", thingIds=tid), "inspect_string")
    rows = r.get("things") or r.get("results") or []
    out = []
    for row in rows:
        ins = row.get("inspect")
        out.extend(ins if isinstance(ins, list) else [str(ins)])
    return "\n".join(out)


def _fuel(t, tank):
    m = re.search(r"Bacta:\s*([\d.]+)\s*/\s*([\d.]+)", _inspect(t, tank))
    return float(m.group(1)) if m else None


def _add(t, pid, hediff, part=None, sev=-1.0):
    if part:
        r = t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff=hediff, bodyPart=part, severity=sev)
    else:
        r = t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff=hediff, severity=sev)
    _ok(r, "pawn_health add %s %s" % (hediff, part))


def _power(t, tank, on):
    r = _ok(t.bridge_call("jawa/power_net", thing=tank, forcePowerOn=on), "power_net")
    if r.get("powerOnAfter") is not on:
        _fail("power_net forcePowerOn=%s read back powerOnAfter=%r" % (on, r.get("powerOnAfter")))


def _build(t, ops):
    r = _ok(t.bridge_call("jawa/build_batch", ops=ops, faction="player", readBack=8), "build_batch " + ops)
    if r.get("survived") is not None and r.get("survived") != r.get("placed"):
        _fail("build_batch placed %r but only %r survived: %s" % (r.get("placed"), r.get("survived"), r.get("displaced")))
    t.bridge_call("jawa/map_commit")


def _site(t, S, droid=False):
    """Clean concrete site, tank (powered, empty), optional droid, shipped settings. Fills S."""
    _defaults(t)
    t.clear_area(size=SIZE)
    x, z = t.anchor
    h = SIZE // 2
    _ok(t.bridge_call("jawa/set_terrain_batch", ops="Concrete:%d,%d,%d,%d" % (x - h, z - h, SIZE, SIZE)), "terrain")
    t.bridge_call("jawa/log_autoopen_suppress")
    ops = "%s:%d,%d,2" % (TANK, x + 4, z)
    if droid:
        ops += ";%s:%d,%d" % (DROID, x + 4, z + 4)
    _build(t, ops)
    S["tank"] = _tid(t, TANK)
    if not S["tank"]:
        _fail("%s not on the map after build_batch" % TANK)
    _power(t, S["tank"], True)
    if droid:
        S["droid"] = _tid(t, DROID)
        if not S["droid"]:
            _fail("%s not on the map after build_batch" % DROID)
        _power(t, S["droid"], True)
    S["pawn"] = t.spawn_pawn("Colonist", hostile=False)
    if not S["pawn"]:
        _fail("spawn_pawn returned no pawn")
    t.bridge_call("jawa/set_draft", pawnId=S["pawn"], drafted=False)
    for need in ("Food", "Rest"):
        t.bridge_call("jawa/pawn_need", pawn=S["pawn"], action="need", need=need, level=1.0)


def _refuel(t, S, n):
    """Spawn n bacta and have the pawn fuel the tank through the REAL vanilla Refuel job."""
    x, z = t.anchor
    _ok(t.bridge_call("rimworld/spawn_thing", defName=FLUID, stackCount=n, x=x + 1, z=z + 1), "spawn bacta")
    stack = _tid(t, FLUID)
    if not stack:
        _unmeasured(t, "spawned bacta stack not found on the map (harness: spawn_thing)")
    r = t.bridge_call("jawa/ordered_job", pawnId=S["pawn"], jobDef="Refuel", targetAId=S["tank"], targetBId=stack,
              count=n, waitTicks=60, timeoutSeconds=60)
    t.wait_ticks(700)
    fuel = _fuel(t, S["tank"])
    if fuel is None:
        _unmeasured(t, "no 'Bacta: n / m' line in the tank's inspect string")
    if fuel < 0.5:
        if not (r or {}).get("accepted"):
            _unmeasured(t, "Refuel job was not accepted (site/harness): %s" % str(r)[:200])
        _fail("Refuel job accepted and run but the tank holds %s bacta (fuelFilter / CompRefuelable wiring)" % fuel)
    return fuel


def _enter(t, S):
    r = t.bridge_call("jawa/ordered_job", pawnId=S["pawn"], jobDef="EnterBuilding", targetAId=S["tank"],
              waitTicks=60, timeoutSeconds=60)
    t.wait_ticks(700)
    p = _pawn(t, S["pawn"])
    if not _contained(p):
        if not (r or {}).get("accepted"):
            _unmeasured(t, "EnterBuilding not accepted (site/harness): %s" % str(r)[:200])
        _fail("pawn is still on the map after EnterBuilding on a powered, fuelled tank (CanAcceptPawn refused?): "
              "tank says %r" % _inspect(t, S["tank"])[:200])
    return p


# ------------------------------------------------------------------ chain 1: content

@suite.chain("content")
def content(t):
    with _comp(t, "defs_resolve"):
        if _live(t):
            want = ["ThingDef/RSW_BactaTank", "ThingDef/RSW_Bacta", "ThingDef/RSW_BactaPatch", "ThingDef/RSW_BactaSpray",
                    "ThingDef/RSW_MedicalDroid", "ResearchProjectDef/RSW_BactaImmersion",
                    "JobDef/RSW_CarryCorpseToBactaTank", "WorkGiverDef/RSW_CarryToBactaTank",
                    "WorkGiverDef/RSW_CarryCorpseToBactaTank", "RecipeDef/RSW_AdministerBactaPatch",
                    "RecipeDef/RSW_AdministerBactaSpray"]
            r = t.bridge_call("jawa/get_defs", defs=";".join(want), fields="defName", limit=50)
            _ok(r, "get_defs")
            if r.get("notFound") or r.get("foundCount") != len(want):
                _fail("defs missing: notFound=%r foundCount=%r of %d" % (r.get("notFound"), r.get("foundCount"), len(want)))

    with _comp(t, "tank_def_wiring"):
        if _live(t):
            r = _ok(t.bridge_call("jawa/get_def", defName=TANK, defType="ThingDef"), "get_def tank")
            ex = r.get("extra") or {}
            if ex.get("thingClass") != "Building_BactaTank":
                _fail("tank thingClass %r, expected Building_BactaTank" % ex.get("thingClass"))
            if ex.get("tickerType") != "Normal":
                _fail("tank tickerType %r; CompBactaImmersion.CompTick needs Normal" % ex.get("tickerType"))
            classes = [c.get("compClass") or c.get("class") for c in (r.get("comps") or [])]
            for need in ("CompBactaImmersion", "CompBactaShell", "CompRefuelable", "CompPowerTrader",
                         "CompAffectedByFacilities"):
                if need not in classes:
                    _fail("tank has no %s comp (has %s)" % (need, classes))
            fuel = [c for c in r["comps"] if (c.get("compClass") or c.get("class")) == "CompRefuelable"][0]
            if float((fuel.get("fields") or {}).get("fuelCapacity", -1)) != 30.0:
                _fail("tank fuelCapacity %r, expected 30" % (fuel.get("fields") or {}).get("fuelCapacity"))
            d = _ok(t.bridge_call("jawa/get_def", defName=DROID, defType="ThingDef"), "get_def droid")
            if "CompFacility" not in [c.get("compClass") or c.get("class") for c in (d.get("comps") or [])]:
                _fail("medical droid has no CompFacility")

    with _comp(t, "fluid_and_items_trade"):
        if _live(t):
            for dn in (FLUID, PATCH, SPRAY):
                ex = _ok(t.bridge_call("jawa/get_def", defName=dn, defType="ThingDef"), "get_def " + dn).get("extra") or {}
                if "ExoticMisc" not in (ex.get("tradeTags") or []):
                    _fail("%s tradeTags %r lacks ExoticMisc" % (dn, ex.get("tradeTags")))
                if ex.get("tradeability") != "All":
                    _fail("%s tradeability %r, expected All" % (dn, ex.get("tradeability")))

    with _comp(t, "trader_stock_patch_landed"):
        if _live(t):
            kinds = ["Orbital_Exotic", "Caravan_Outlander_Exotic", "Base_Outlander_Standard"]
            r = t.bridge_call("jawa/get_defs", defs=";".join("TraderKindDef/" + k for k in kinds),
                      fields="stockGenerators", deep=True)
            _ok(r, "get_defs traders")
            if r.get("notFound"):
                _fail("trader kinds not found: %r" % r.get("notFound"))
            for row in r.get("defs") or []:
                sg = (row.get("fields") or {}).get("stockGenerators")
                if not isinstance(sg, list) or all(isinstance(i, str) for i in sg):
                    _unmeasured(t, "get_defs cannot show stockGenerators contents for %s: %r" % (row.get("defName"), str(sg)[:120]))
                if '"%s"' % FLUID not in json.dumps(sg):
                    _fail("%s stockGenerators carry no %s row: the patch matched nothing" % (row.get("defName"), FLUID))

    with _comp(t, "doctor_recipes_patch_landed"):
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/Human;ThingDef/Muffalo", fields="recipes", deep=False)
            _ok(r, "get_defs recipes")
            rows = dict((d.get("defName"), (d.get("fields") or {}).get("recipes")) for d in r.get("defs") or [])
            hum = rows.get("Human")
            if not isinstance(hum, list):
                _unmeasured(t, "Human.recipes unreadable: %r" % (hum,))
            for rc in ("RSW_AdministerBactaPatch", "RSW_AdministerBactaSpray"):
                if rc not in hum:
                    _fail("Human.recipes lacks %s: the recipe patch matched nothing" % rc)
            ani = rows.get("Muffalo")
            if not isinstance(ani, list) or "AdministerMechSerumHealer" not in ani:
                _unmeasured(t, "control failed: Muffalo.recipes %r has no vanilla AdministerMechSerumHealer" % (ani,))
            for rc in ("RSW_AdministerBactaPatch", "RSW_AdministerBactaSpray"):
                if rc not in ani:
                    _fail("animal recipes lack %s: the AnimalThingBase patch matched nothing" % rc)

    with _comp(t, "settings_ship_defaults"):
        if _live(t):
            bad = dict((k, _sget(t, k)) for k, v in DEFAULTS.items() if not _same(_sget(t, k), v))
            if bad:
                _fail("not at shipped defaults (a prior run's leftovers or a changed ship value): %s" % bad)

    with _comp(t, "no_bacta_errors_in_log"):
        if _live(t):
            r = _ok(t.bridge_call("jawa/drain_log", contains="Bacta", errorsOnly=True, limit=50), "drain_log")
            errs = [m for m in (r.get("messages") or []) if m.get("type") == "Error"]
            if errs:
                _fail("%d Error log line(s) mention Bacta: %s" % (len(errs), str(errs[0].get("text"))[:300]))


# ------------------------------------------------------------------ chain 2: the core healing loop

@suite.chain("tank_heals")
def tank_heals(t):
    S = {}
    with _comp(t, "site_ready_heals"):
        if _live(t):
            _site(t, S)

    with _comp(t, "tank_refuels_via_vanilla_job"):
        if _live(t):
            S["fuel0"] = _refuel(t, S, 25)
            if abs(S["fuel0"] - 25.0) > 0.5:
                _fail("tank holds %s after fuelling 25 bacta" % S["fuel0"])

    with _comp(t, "enters_and_reports_off", toggle="healingEnabled"):
        if _live(t):
            _sset(t, "healingEnabled", False)
            _enter(t, S)
            txt = _inspect(t, S["tank"])
            if "disabled" not in txt.lower():
                _fail("healing off, occupied, powered, fuelled: inspect should say healing is disabled, got %r" % txt[:200])
            _add(t, S["pawn"], "Cut", "Torso", 4.0)
            _add(t, S["pawn"], "MissingBodyPart", "Kidney")
            _add(t, S["pawn"], "Bruise", "Brain", 2.0)
            p = _pawn(t, S["pawn"])
            S["cut0"], S["brain0"] = _sev(p, "Cut", "Torso"), _sev(p, "Bruise", "Brain")
            if S["cut0"] is None or S["brain0"] is None or _sev(p, "MissingBodyPart", "Kidney") is None:
                _unmeasured(t, "fixture hediffs not present after pawn_health add: %s" % p.get("hediffs"))
            S["fuel1"] = _fuel(t, S["tank"])
            t.wait_ticks(2500)
            p = _pawn(t, S["pawn"])
            cut = _sev(p, "Cut", "Torso")
            if cut is None or S["cut0"] - cut > 0.3:
                _fail("healing is OFF yet the cut fell %s -> %s in 2500 ticks" % (S["cut0"], cut))
            if _fuel(t, S["tank"]) < S["fuel1"] - 1e-3:
                _fail("healing OFF yet bacta drained %s -> %s" % (S["fuel1"], _fuel(t, S["tank"])))
            S["cut_off"] = cut

    with _comp(t, "heals_fresh_wound_at_tuned_rate", toggle="woundHealPerDay"):
        if _live(t):
            _sset(t, "healingEnabled", True)
            t.wait_ticks(2500)
            p = _pawn(t, S["pawn"])
            cut = _sev(p, "Cut", "Torso")
            drop = S["cut_off"] - (cut if cut is not None else 0.0)
            S["cut_on"], S["brain_on"] = cut, _sev(p, "Bruise", "Brain")
            # 30/day * 250/60000 = 0.125 per pass, 10 passes = 1.25
            if not 0.6 <= drop <= 2.0:
                _fail("woundHealPerDay=30: the cut fell %.3f in 2500 ticks, expected about 1.25 (0.6..2.0)" % drop)

    with _comp(t, "drains_bacta_while_healing", toggle="fluidCostPerDay"):
        if _live(t):
            now = _fuel(t, S["tank"])
            used = S["fuel1"] - now
            # 5/day * 2500/60000 = 0.208; healing-off phase must have used 0, so all of it is this phase
            if not 0.05 <= used <= 1.0:
                _fail("fluidCostPerDay=5: used %.3f bacta in a 2500-tick healing phase, expected about 0.21" % used)

    with _comp(t, "never_regrows_never_touches_brain"):
        if _live(t):
            p = _pawn(t, S["pawn"])
            if _sev(p, "MissingBodyPart", "Kidney") is None:
                _fail("the missing kidney is gone after healing: bacta regrew a part")
            br = _sev(p, "Bruise", "Brain")
            if br is None or S["brain0"] - br > 0.3:
                _fail("brain bruise changed %s -> %s while the cut healed %s -> %s: bacta touched the brain"
                      % (S["brain0"], br, S["cut_off"], S["cut_on"]))
            if S["cut_off"] - S["cut_on"] < 0.6:
                _unmeasured(t, "control failed: the tank did not heal the cut in this window, so the brain/part "
                               "guards were not exercised")

    with _comp(t, "ejects_when_nothing_left", toggle="autoEjectEnabled"):
        if _live(t):
            _sset(t, "woundHealPerDay", 120)
            t.wait_ticks(3000)
            p = _pawn(t, S["pawn"])
            if _contained(p):
                _fail("only a missing kidney and a brain bruise remain (both off limits) yet the occupant was not "
                      "ejected; hediffs=%s" % p.get("hediffs"))
            if _sev(p, "Cut", "Torso") is not None:
                _fail("occupant ejected with the cut unhealed: %s" % p.get("hediffs"))
            if _sev(p, "MissingBodyPart", "Kidney") is None or _sev(p, "Bruise", "Brain") is None:
                _fail("the off-limits hediffs are gone after the full immersion: %s" % p.get("hediffs"))

    with _comp(t, "no_bacta_errors_after_ticking"):
        if _live(t):
            r = _ok(t.bridge_call("jawa/drain_log", contains="Bacta", errorsOnly=True, limit=50), "drain_log")
            errs = [m for m in (r.get("messages") or []) if m.get("type") == "Error"]
            if errs:
                _fail("Error log line(s) mention Bacta after the tank ticked: %s" % str(errs[0].get("text"))[:300])


# ------------------------------------------------------------------ chain 3: scar erasure

def _find_permanent_action(t):
    r = t.bridge_call("rimworld/search_debug_actions", query="Make injuries permanent", limit=10)
    if not isinstance(r, dict) or not r.get("success"):
        _unmeasured(t, "search_debug_actions failed: %s" % str(r)[:200])
    stack = [r]
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            if isinstance(o.get("path"), str) and "permanent" in o["path"].lower():
                return o["path"]
            stack.extend(o.values())
        elif isinstance(o, list):
            stack.extend(o)
    _unmeasured(t, "no 'Make injuries permanent' debug action found")


@suite.chain("tank_scar")
def tank_scar(t):
    S = {}
    with _comp(t, "site_ready_scar"):
        if _live(t):
            _site(t, S)
            _refuel(t, S, 10)
            _sset(t, "scarErasureEnabled", False)
            _sset(t, "autoEjectEnabled", False)   # nothing heals with scars off, so the tank would release the pawn
            _sset(t, "scarHealPerDay", 20)
            _add(t, S["pawn"], "Cut", "Torso", 0.3)
            path = _find_permanent_action(t)
            x, z = t.anchor
            pos = _pawn(t, S["pawn"]).get("position") or {}
            _ok(t.bridge_call("rimworld/execute_debug_action", path=path, pawnId=S["pawn"],
                      x=pos.get("x", x), z=pos.get("z", z)), "execute_debug_action permanent")
            S["scar0"] = _sev(_pawn(t, S["pawn"]), "Cut", "Torso")
            if S["scar0"] is None:
                _unmeasured(t, "the cut vanished when made permanent (fixture)")
            _enter(t, S)

    with _comp(t, "scar_erasure_off_keeps_the_scar", toggle="scarErasureEnabled"):
        if _live(t):
            t.wait_ticks(1500)
            s = _sev(_pawn(t, S["pawn"]), "Cut", "Torso")
            # a NON-permanent 0.3 cut would be gone in 3 passes at 30/day: a surviving, unchanged injury proves
            # both that it is permanent and that the scar branch honours the toggle
            if s is None or S["scar0"] - s > 0.05:
                _fail("scarErasureEnabled=false but the permanent injury went %s -> %s" % (S["scar0"], s))

    with _comp(t, "scar_erasure_on_removes_the_scar", toggle="scarHealPerDay"):
        if _live(t):
            _sset(t, "scarErasureEnabled", True)
            t.wait_ticks(2000)
            p = _pawn(t, S["pawn"])
            if _sev(p, "Cut", "Torso") is not None:
                _fail("scarErasureEnabled=true, scarHealPerDay=20: a 0.3 permanent injury survived 2000 ticks: %s"
                      % p.get("hediffs"))


# ------------------------------------------------------------------ chain 4: power gate

@suite.chain("tank_power")
def tank_power(t):
    S = {}
    with _comp(t, "site_ready_power"):
        if _live(t):
            _site(t, S)
            _refuel(t, S, 10)
            _add(t, S["pawn"], "Cut", "Torso", 4.0)
            S["cut0"] = _sev(_pawn(t, S["pawn"]), "Cut", "Torso")
            _enter(t, S)

    with _comp(t, "unpowered_tank_does_not_heal"):
        if _live(t):
            _power(t, S["tank"], False)
            if "unpowered" not in _inspect(t, S["tank"]).lower():
                _fail("tank powered off but inspect does not say unpowered: %r" % _inspect(t, S["tank"])[:200])
            f0 = _fuel(t, S["tank"])
            t.wait_ticks(1500)
            cut = _sev(_pawn(t, S["pawn"]), "Cut", "Torso")
            if cut is None or S["cut0"] - cut > 0.3:
                _fail("tank has no power yet the cut fell %s -> %s" % (S["cut0"], cut))
            if _fuel(t, S["tank"]) < f0 - 1e-3:
                _fail("tank has no power yet it drained bacta")
            S["cut_off"] = cut

    with _comp(t, "powered_tank_heals_again"):
        if _live(t):
            _power(t, S["tank"], True)
            t.wait_ticks(1500)
            cut = _sev(_pawn(t, S["pawn"]), "Cut", "Torso")
            if cut is None or S["cut_off"] - cut < 0.3:
                _fail("power restored but the cut stayed %s -> %s" % (S["cut_off"], cut))


# ------------------------------------------------------------------ chain 5: needs hold, dry tank

@suite.chain("tank_needs_and_dry")
def tank_needs_and_dry(t):
    S = {}
    with _comp(t, "site_ready_dry"):
        if _live(t):
            _site(t, S)
            _refuel(t, S, 2)
            t.bridge_call("jawa/pawn_need", pawn=S["pawn"], action="need", need="Food", level=0.6)
            _add(t, S["pawn"], "Cut", "Torso", 4.0)
            _enter(t, S)
            S["food0"] = _food(_pawn(t, S["pawn"]))

    with _comp(t, "needs_held_while_immersed", toggle="suspendNeedsEnabled"):
        if _live(t):
            if S["food0"] is None:
                _unmeasured(t, "pawn has no Food need to read")
            t.wait_ticks(1500)
            f = _food(_pawn(t, S["pawn"]))
            if abs(f - S["food0"]) > 0.003:
                _fail("suspendNeedsEnabled=true but Food moved %s -> %s inside the tank" % (S["food0"], f))
            _sset(t, "suspendNeedsEnabled", False)
            t.wait_ticks(1000)
            f2 = _food(_pawn(t, S["pawn"]))
            if S["food0"] - f2 < 0.005:
                _unmeasured(t, "control failed: with the hold off Food still did not fall (%s -> %s)" % (S["food0"], f2))

    with _comp(t, "dry_tank_holds_occupant_when_autoeject_off", toggle="autoEjectEnabled"):
        if _live(t):
            _sset(t, "autoEjectEnabled", False)
            _sset(t, "fluidCostPerDay", 200)
            t.wait_ticks(2000)
            fuel = _fuel(t, S["tank"])
            if fuel is None or fuel > 0.001:
                _fail("fluidCostPerDay=200 for 2000 ticks should empty a 2-unit tank, it holds %s" % fuel)
            p = _pawn(t, S["pawn"])
            if not _contained(p):
                _fail("autoEjectEnabled=false yet the occupant left the dry tank")

    with _comp(t, "dry_tank_ejects_when_autoeject_on", toggle="fluidCostPerDay"):
        if _live(t):
            _sset(t, "autoEjectEnabled", True)
            t.wait_ticks(700)
            if _contained(_pawn(t, S["pawn"])):
                _fail("autoEjectEnabled=true and the tank is dry: the occupant was not released within 2 passes")


# ------------------------------------------------------------------ chain 6: medical droid facility

@suite.chain("tank_droid")
def tank_droid(t):
    S = {}
    with _comp(t, "site_ready_droid"):
        if _live(t):
            _site(t, S, droid=True)
            _refuel(t, S, 5)
            _add(t, S["pawn"], "Cut", "Torso", 4.0)
            _enter(t, S)
            t.wait_ticks(PASS_TICKS)

    with _comp(t, "linked_droid_is_reported_assisting", toggle="medicalDroidEnabled"):
        if _live(t):
            txt = _inspect(t, S["tank"])
            if "droid assisting" not in txt.lower():
                _fail("powered RSW_MedicalDroid 4 cells from an immersing tank: inspect lacks the assist line: %r" % txt[:250])

    with _comp(t, "droid_toggle_off_stops_the_assist", toggle="medicalDroidEnabled"):
        if _live(t):
            _sset(t, "medicalDroidEnabled", False)
            txt = _inspect(t, S["tank"])
            if "droid assisting" in txt.lower():
                _fail("medicalDroidEnabled=false but inspect still says the droid assists: %r" % txt[:250])


# ------------------------------------------------------------------ chain 7: field items

@suite.chain("field_patch")
def field_patch(t):
    S = {}
    with _comp(t, "site_ready_patch"):
        if _live(t):
            _site(t, S)
            _add(t, S["pawn"], "Cut", "Torso", 3.0)
            S["cut0"] = _sev(_pawn(t, S["pawn"]), "Cut", "Torso")
            x, z = t.anchor
            _ok(t.bridge_call("rimworld/spawn_thing", defName=PATCH, stackCount=1, x=x + 1, z=z + 1), "spawn patch")
            S["patch"] = _tid(t, PATCH)
            if not S["patch"] or S["cut0"] is None:
                _unmeasured(t, "fixture missing: patch=%r cut=%r" % (S.get("patch"), S.get("cut0")))

    def use(why):
        r = t.bridge_call("jawa/ordered_job", pawnId=S["pawn"], jobDef="UseItem", targetAId=S["patch"],
                  waitTicks=60, timeoutSeconds=60)
        t.wait_ticks(900)
        return r

    with _comp(t, "patch_unusable_when_field_items_off", toggle="fieldItemsEnabled"):
        if _live(t):
            _sset(t, "fieldItemsEnabled", False)
            use("off")
            cut = _sev(_pawn(t, S["pawn"]), "Cut", "Torso")
            if cut is None or S["cut0"] - cut > 0.5:
                _fail("fieldItemsEnabled=false yet the cut fell %s -> %s" % (S["cut0"], cut))
            if not _things(t, PATCH):
                _fail("fieldItemsEnabled=false yet the patch was consumed")

    with _comp(t, "patch_closes_a_fresh_wound", toggle="fieldItemsEnabled"):
        if _live(t):
            _sset(t, "fieldItemsEnabled", True)
            r = use("on")
            cut = _sev(_pawn(t, S["pawn"]), "Cut", "Torso")
            if cut is not None and S["cut0"] - cut < 1.0:
                if not (r or {}).get("accepted"):
                    _unmeasured(t, "UseItem not accepted (site/harness): %s" % str(r)[:200])
                _fail("bacta patch (woundHealAmount 6) used on a 3.0 cut: it is %s afterwards" % cut)
            if _things(t, PATCH):
                _fail("single-use bacta patch still on the map after use")


# ------------------------------------------------------------------ chain 8: revival of the recently dead

def _kill(t, pid):
    for _ in range(6):
        t.bridge_call("jawa/damage", thingId=pid, damageDef="Bomb", amount=500.0, allowColonists=True)
        rows = _things(t, group="Corpse")
        if rows:
            return rows[0].get("id")
    return None


@suite.chain("revival")
def revival(t):
    S = {}
    with _comp(t, "site_ready_revival"):
        if _live(t):
            _site(t, S)
            _refuel(t, S, 5)
            x, z = t.anchor
            r = _ok(t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x - 10, z=z + 8, faction="player", count=1),
                    "spawn victim")
            S["victim"] = ((r.get("pawns") or [{}])[0]).get("id")
            if not S["victim"]:
                _fail("no victim pawn spawned")
            t.session.track("pawn", S["victim"], x=x - 10, z=z + 8)
            S["corpse"] = _kill(t, S["victim"])
            if not S["corpse"]:
                _unmeasured(t, "could not kill the victim to make a corpse (jawa/damage)")

    def carry():
        r = t.bridge_call("jawa/ordered_job", pawnId=S["pawn"], jobDef="RSW_CarryCorpseToBactaTank",
                  targetAId=S["corpse"], targetBId=S["tank"], waitTicks=60, timeoutSeconds=60)
        t.wait_ticks(1500)
        return r

    with _comp(t, "revival_off_by_default_refuses_corpse", toggle="revivalEnabled"):
        if _live(t):
            if not _same(_sget(t, "revivalEnabled"), False):
                _fail("revivalEnabled must ship OFF")
            carry()
            if not _things(t, group="Corpse"):
                _fail("revivalEnabled=false but the corpse was taken into the tank")

    with _comp(t, "revival_window_refuses_old_corpse", toggle="revivalWindowHours"):
        if _live(t):
            _sset(t, "revivalEnabled", True)
            _sset(t, "revivalWindowHours", 0.001)
            carry()
            if not _things(t, group="Corpse"):
                _fail("revivalWindowHours=0.001 yet a corpse 1500+ ticks old was accepted")

    with _comp(t, "revival_on_revives_into_the_tank", toggle="revivalEnabled"):
        if _live(t):
            _sset(t, "revivalWindowHours", 6)
            carry()
            if _things(t, group="Corpse"):
                _fail("revivalEnabled=true, fresh corpse: it is still lying on the map")
            p = _pawn(t, S["victim"])
            if not _contained(p):
                # a revived pawn with nothing bacta can heal is released at the next 250-tick pass: then it must be
                # alive on the map instead
                r = _ok(t.bridge_call("jawa/list_pawns", limit=200), "list_pawns")
                row = [q for q in (r.get("pawns") or []) if q.get("id") == S["victim"]]
                if not row or row[0].get("dead"):
                    _fail("corpse gone but the victim is neither in the tank nor alive on the map: %s" % row)
