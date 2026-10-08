"""validation.py -- modcheck suite for RimMandrake Wrecked Machines
(mandrake.rm.wreckedmachines).

Grounded in this mod's actual Defs. The mod carries C# and a settings class
(`Source/WreckedMachinesMod.cs`: allowDonorSmelter, researchCostFactor,
materialCostFactor, skipRestorationResearch). Each one is driven by
`settings_drive_the_defs` (set, re-run WreckedMachinesPatcher.Apply, read the
def it rewrites, restore); the tier shapes (process counts, canOverclock,
shared replaceTags, research gate) are also asserted offline by
`static_checks()` (`python3 validation.py`).

WHAT THIS MOD ACTUALLY SHIPS (Buildings_WreckedMachines_AutomatedSmelter.xml,
ResearchProjects_WreckedMachines.xml, SpecialResearchOpportunities_
WreckedMachines.xml): three PARALLEL ThingDefs for one building --
RM_WM_AutomatedSmelter_Wrecked (inert rubble, no comps at all, `isInert`),
_Kludged (powered, VFEFactory/PipeSystem comps, a 3-process
AdvancedResourceProcessor with `canOverclock=false`), and _Repaired
(mechanically identical to the donor VFEFactory_AutomatedSmelter, all six
processes, `canOverclock=true`) -- sharing one `replaceTags` entry
("WM_AutomatedSmelter") so each can be built directly over the last, and the
Repaired tier gated behind this mod's OWN research project
(RM_WM_AutomatedSmelterRestoration) rather than VFE's vanilla one. The donor
building (VFEFactory_AutomatedSmelter) is left completely untouched --
About.xml's own description says both remain buildable side by side, on
purpose, for this v1 testing phase.

REAL DEPENDENCY, not a soft-hook: `<modDependencies>` names
VanillaExpanded.VFEFactory (not just loadAfter) -- the Kludged/Repaired
comps (`PipeSystem.CompPowerTrader_Overclocked`,
`PipeSystem.CompHeatPusherPowered_Overclocked`,
`PipeSystem.CompProperties_AdvancedResourceProcessor`) are that mod's
classes, and this mod cannot even load without it. VFEFactory (and its own
dependency, OskarPotocki.VanillaFactionsExpanded.Core) MUST be on this
mod's minimal test environment alongside `mandrake.rm.wreckedmachines`
itself, or every ThingDef below fails to load with a "type not found"
Config error rather than the failures these components are built to catch.
`petetimessix.researchreinvented` is MayRequire-guarded (the Analyse
special-opportunity def) and is NOT required for anything this suite
exercises.

WHAT THIS SUITE CANNOT PROVE, and why: `replaceTags`-driven build-over
(placing the Repaired blueprint directly on top of a standing Wrecked/
Kludged building) is a Designator_Build / blueprint-placement mechanic --
nothing on this bridge places a BLUEPRINT and lets construction resolve it
that way, and `jawa/spawn_batch` (the only spawn primitive this library's
`t.spawn()` uses) places a finished THING directly, which never touches the
replaceTags/CanReplace code path at all. This is therefore left
UNCOVERED rather than faked with a component that would not actually
exercise the mechanic; see "Still not proven" below.

Still not proven / likely first-live-run corrections:
  1. Every `jawa/inspect_string` assertion below only checks for the
     ABSENCE of a thrown `error` field and the PRESENCE of at least one
     inspect line -- it does not assert on any specific VFEFactory/
     PipeSystem inspect sentence (e.g. "needs power"), because that text
     was not measured live before writing this file and guessing it would
     make a brittle, likely-wrong assertion. Tightening this once the real
     text is seen is expected, not a sign this file was wrong to ship.
  2. The `replaceTags` build-over loop (see above) is entirely unproven by
     this suite -- it would need a live playtest or a bridge tool this
     roster does not have (something that resolves a blueprint through
     Designator_Build/GenConstruct rather than spawning a finished thing).
  3. `RM_WM_AnalyseWreckedSmelter` (the ResearchReinvented Analyse
     opportunity) is not exercised at all -- it is MayRequire-guarded on a
     mod not required for this suite's own minimal environment, and its own
     file header already records it as "NOT VERIFIED AT RUNTIME -- reserved
     for the owner's own quicktest."
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_TYPE = "RimMandrake.WreckedMachines.WreckedMachinesSettings"
PATCHER_TYPE = "RimMandrake.WreckedMachines.WreckedMachinesPatcher"
SETTINGS = ("allowDonorSmelter", "researchCostFactor", "materialCostFactor", "skipRestorationResearch",
            "wreckedRatio", "kludgedRatio", "refurbishedRatio", "allowFullRestoration",
            "requireLowerGradeUnderneath", "enableSalvagedEmanators")
# Settings read at play time rather than by Apply (PlaceWorker / ThoughtWorker).
RUNTIME_SETTINGS = ("requireLowerGradeUnderneath", "enableSalvagedEmanators")
GRADE_EXT = "RimMandrake.WreckedMachines.WreckedMachineGrade"
BUILD_OVER = "RimMandrake.WreckedMachines.PlaceWorker_BuildOverLowerGrade"


def _tiers():
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings",
                                 "Buildings_WreckedMachines_AutomatedSmelter.xml")).getroot()
    return {d.findtext("defName"): d for d in root.findall("ThingDef")}


def _mobile():
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings",
                                 "Buildings_WreckedMachines_Mobile.xml")).getroot()
    return {d.findtext("defName"): d for d in root.findall("ThingDef") if d.findtext("defName")}


def _ladder_checks(defs, bad):
    """Every grade def names its grade and line; the line equals its replaceTag (inherited
    from an abstract parent for the mobile lines, so read the def or report it); every grade
    above Wrecked carries the build-over PlaceWorker."""
    for dn, d in defs.items():
        ext = [li for li in d.findall("modExtensions/li") if li.get("Class") == GRADE_EXT]
        if len(ext) != 1:
            bad.append("%s carries %d WreckedMachineGrade extensions, want 1" % (dn, len(ext)))
            continue
        grade = (ext[0].findtext("grade") or "").strip()
        if grade not in ("Wrecked", "Kludged", "Refurbished", "Original"):
            bad.append("%s has unknown grade %r" % (dn, grade))
        pws = [li.text for li in d.findall("placeWorkers/li")]
        if grade != "Wrecked" and BUILD_OVER not in pws:
            bad.append("%s (grade %s) lacks %s" % (dn, grade, BUILD_OVER))
        if grade == "Refurbished" and "RM_WM_AncientComponent" not in [c.tag for c in d.findall("costList/*")]:
            bad.append("%s is Refurbished but does not cost RM_WM_AncientComponent" % dn)


def static_checks():
    """Offline: the grades are the shapes the mod promises, and every setting is wired."""
    bad = []
    tiers = _tiers()
    if len(tiers) < 4:
        return ["only %d ThingDefs parsed (sanity probe failed)" % len(tiers)]
    mobile = _mobile()
    if len(mobile) != 6:
        bad.append("mobile file parsed %d concrete ThingDefs, want 6 (3 power cell + 3 emanator)" % len(mobile))
    _ladder_checks(tiers, bad)
    _ladder_checks(mobile, bad)
    for dn, d in tiers.items():
        ext = d.find("modExtensions/li")
        if ext is not None and ext.findtext("line") != "WM_AutomatedSmelter":
            bad.append("%s line is not WM_AutomatedSmelter" % dn)
    for dn in ("RM_WM_AutomatedSmelter_Wrecked", "RM_WM_AutomatedSmelter_Kludged",
               "RM_WM_AutomatedSmelter_Refurbished", "RM_WM_AutomatedSmelter_Repaired"):
        d = tiers.get(dn)
        if d is None:
            bad.append("%s missing" % dn)
            continue
        if [li.text for li in d.findall("replaceTags/li")] != ["WM_AutomatedSmelter"]:
            bad.append("%s does not carry the shared replaceTags WM_AutomatedSmelter (build-over breaks)" % dn)
    w = tiers.get("RM_WM_AutomatedSmelter_Wrecked")
    if w is not None and (w.findtext("building/isInert") != "true" or w.find("comps") is not None or w.findtext("tickerType") != "Never"):
        bad.append("Wrecked tier is not inert (isInert true, no comps, tickerType Never)")
    for dn, nproc, oc in (("RM_WM_AutomatedSmelter_Kludged", 3, "false"),
                          ("RM_WM_AutomatedSmelter_Refurbished", 5, "false"),
                          ("RM_WM_AutomatedSmelter_Repaired", 6, "true")):
        d = tiers.get(dn)
        if d is None:
            continue
        proc = [li for li in d.findall("comps/li") if li.get("Class") == "PipeSystem.CompProperties_AdvancedResourceProcessor"]
        if len(proc) != 1:
            bad.append("%s has %d AdvancedResourceProcessor comps, want 1" % (dn, len(proc)))
            continue
        n = len(proc[0].findall("processes/li"))
        if n != nproc:
            bad.append("%s runs %d processes, want %d" % (dn, n, nproc))
        if (proc[0].findtext("canOverclock") or "").strip() != oc:
            bad.append("%s canOverclock is %r, want %s" % (dn, proc[0].findtext("canOverclock"), oc))
    for dn in ("RM_WM_AutomatedSmelter_Refurbished", "RM_WM_AutomatedSmelter_Repaired"):
        r = tiers.get(dn)
        if r is not None and "RM_WM_AutomatedSmelterRestoration" not in [li.text for li in r.findall("researchPrerequisites/li")]:
            bad.append("%s is not gated by RM_WM_AutomatedSmelterRestoration" % dn)
    src = open(os.path.join(HERE, "Source", "WreckedMachinesMod.cs"), encoding="utf-8").read()
    fields = re.findall(r"public\s+static\s+(?:bool|float)\s+(\w+)\s*=", src)
    if sorted(fields) != sorted(SETTINGS):
        bad.append("settings fields drifted: source has %s, suite drives %s" % (sorted(fields), sorted(SETTINGS)))
    scribed = src.split("void ExposeData", 1)[-1].split("DoWindowContents", 1)[0]
    ui = src.split("void DoWindowContents", 1)[-1].split("class WreckedMachinesMod", 1)[0]
    ladder = open(os.path.join(HERE, "Source", "WreckedMachinesLadder.cs"), encoding="utf-8").read()
    apply = src.split("public static void Apply", 1)[-1] + ladder  # LadderPatcher.Apply reads ratios via RatioFor
    for f in fields:
        if '"%s"' % f not in scribed:
            bad.append("%s is not Scribed" % f)
        if not re.search(r"\b%s\b" % f, ui):
            bad.append("%s has no control in DoWindowContents" % f)
        reader = ladder if f in RUNTIME_SETTINGS else apply
        # The three ratios are read through the normalised WreckedMachinesSettings.Ladder property, which is
        # itself built from the raw fields (src, the settings class) - so a read of .Ladder is a read of each.
        via_ladder = (f in ("wreckedRatio", "kludgedRatio", "refurbishedRatio")
                      and re.search(r"Ladder\s*=>[^;]*\b%s\b" % f, src) is not None
                      and "WreckedMachinesSettings.Ladder" in reader)
        if "WreckedMachinesSettings.%s" % f not in reader and not via_ladder:
            bad.append("%s is never read (a dead setting)" % f)
    return bad


try:
    from modcheck import Suite, ExpectationFailed
except ImportError:
    _UTILS = os.path.join(HERE, "..", "Utils")
    sys.path.insert(0, _UTILS)
    try:
        from modcheck import Suite, ExpectationFailed
    except ImportError:
        Suite = None

if Suite is None:
    if __name__ == "__main__":
        problems = static_checks()
        print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
        for p in problems:
            print("  - " + p)
        sys.exit(1 if problems else 0)
    raise SystemExit("modcheck not importable")

suite = Suite("WreckedMachines")
suite.toggles = list(SETTINGS)

WRECKED = "RM_WM_AutomatedSmelter_Wrecked"
KLUDGED = "RM_WM_AutomatedSmelter_Kludged"
REPAIRED = "RM_WM_AutomatedSmelter_Repaired"
RESTORATION_PROJECT = "RM_WM_AutomatedSmelterRestoration"

# Every Config-error / load-failure needle this mod's own defNames/namespace
# would show up under if a comp class or texture failed to resolve.
ERROR_NEEDLES = ["WreckedMachines", "RM_WM_", "AutomatedSmelter"]


def _assert_no_mod_errors(t):
    r = t.bridge_call("jawa/drain_log", limit=200, errorsOnly=True)
    msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
    hit = [m for m in msgs if any(n.lower() in m.lower() for n in ERROR_NEEDLES)]
    if hit:
        raise ExpectationFailed("error/warning-level log line(s) mention this mod: %r" % hit)


def _assert_inspects_cleanly(t, thing_id):
    r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
    rows = (r or {}).get("things") or []
    row = next((x for x in rows if x.get("id") == thing_id), None)
    if row is None:
        raise ExpectationFailed(
            "jawa/inspect_string(%r) returned no row for it: %r" % (thing_id, r))
    if row.get("error"):
        raise ExpectationFailed(
            "%s's comps threw building its inspect string: %r" % (thing_id, row.get("error")))
    return row


@suite.chain("wrecked_tier_loads_inert")
def wrecked_tier_loads_inert(t):
    """Beyond-toggle (no settings exist -- see module docstring): the
    dead-scenery tier loads with no comps and no Config/load errors. This is
    the tier with `isInert`/`tickerType Never` and NO CompProperties_Power --
    a texPath or comp-class typo here would otherwise only ever surface as a
    silent magenta box or a missed line in Player.log."""
    t.clear_area(size=20)
    cells = t.spawn(WRECKED, count=1, at="point")

    with t.component("spawns_and_inspects_clean", beyond_toggle=True):
        things = t.bridge_call("jawa/list_things", defName=WRECKED,
                               rect="%d,%d,20,20" % (cells[0][0] - 10, cells[0][1] - 10))
        rows = (things or {}).get("things") or []
        if not rows:
            raise ExpectationFailed("no %s found via jawa/list_things after spawning it." % WRECKED)
        _assert_inspects_cleanly(t, rows[0]["id"])
        _assert_no_mod_errors(t)
        t.screenshot()


@suite.chain("kludged_tier_has_power_and_processor_comps")
def kludged_tier_has_power_and_processor_comps(t):
    """Beyond-toggle: the powered, VFEFactory-dependent bodge tier -- proves
    its CompPowerTrader/CompPowerTrader_Overclocked,
    CompHeatPusherPowered_Overclocked and (3-process, canOverclock=false)
    AdvancedResourceProcessor comps all construct and report without
    throwing. This is the def that would break first, and loudest, if
    VanillaExpanded.VFEFactory were missing from the test environment or had
    renamed one of these PipeSystem classes (see module docstring's
    real-dependency note)."""
    t.clear_area(size=20)
    cells = t.spawn(KLUDGED, count=1, at="point")

    with t.component("spawns_and_inspects_clean", beyond_toggle=True):
        things = t.bridge_call("jawa/list_things", defName=KLUDGED,
                               rect="%d,%d,20,20" % (cells[0][0] - 10, cells[0][1] - 10))
        rows = (things or {}).get("things") or []
        if not rows:
            raise ExpectationFailed("no %s found via jawa/list_things after spawning it." % KLUDGED)
        row = _assert_inspects_cleanly(t, rows[0]["id"])
        if not row.get("inspect"):
            raise ExpectationFailed(
                "%s inspected with zero lines -- a powered building with a processor comp "
                "should print at least one status line: %r" % (KLUDGED, row))
        _assert_no_mod_errors(t)
        t.screenshot()


@suite.chain("repaired_tier_gated_by_own_research")
def repaired_tier_gated_by_own_research(t):
    """Beyond-toggle: RM_WM_AutomatedSmelterRestoration is this mod's OWN
    Ship-tree research project (WRECKED_MACHINES_RESURRECTION_1's re-point
    off VFE_BasicFactories) -- prove it exists, is finishable, and that the
    full-function Repaired tier (all six processes, canOverclock=true,
    mechanically identical to the donor per the def's own header) loads
    cleanly once it is. Does NOT prove the in-game build menu actually gates
    on it (that is Designator_Build's own researchPrerequisites check, not
    reachable via a direct spawn -- see module docstring)."""
    t.clear_area(size=20)

    with t.component("research_project_finishable", beyond_toggle=True):
        r = t.bridge_call("jawa/research_finish_project", project=RESTORATION_PROJECT)
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "could not finish %s: %r" % (RESTORATION_PROJECT, r))
        result = (r or {}).get("result") or {}
        if not result.get("isFinished"):
            raise ExpectationFailed(
                "%s reported success but isFinished is not true: %r" % (RESTORATION_PROJECT, r))
        t.screenshot()

    with t.component("repaired_tier_spawns_and_inspects_clean", beyond_toggle=True):
        cells = t.spawn(REPAIRED, count=1, at="point")
        things = t.bridge_call("jawa/list_things", defName=REPAIRED,
                               rect="%d,%d,20,20" % (cells[0][0] - 10, cells[0][1] - 10))
        rows = (things or {}).get("things") or []
        if not rows:
            raise ExpectationFailed("no %s found via jawa/list_things after spawning it." % REPAIRED)
        row = _assert_inspects_cleanly(t, rows[0]["id"])
        if not row.get("inspect"):
            raise ExpectationFailed(
                "%s inspected with zero lines -- expected at least one status line: %r"
                % (REPAIRED, row))
        _assert_no_mod_errors(t)
        t.screenshot()


def _setting(t, action, field, value=None):
    if value is not None:
        r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action=action, field=field, value=str(value))
    else:
        r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action=action, field=field)
    return r if isinstance(r, dict) else {}


def _def_field(t, defpath, field, null_ok=False):
    # deep=True is required for list fields: the default returns each non-scalar list item as its bare type name
    # (MEASURED live 2026-10-07: costList / stages / comps all read ['ThingDefCountClass', ...] before AND after a
    # rewrite, so every list-valued drive failed on a read that could not see values).
    r = t.bridge_call("jawa/get_defs", defs=defpath, fields=field, limit=2, deep=True)
    rows = (r or {}).get("defs") or [] if isinstance(r, dict) else []
    if not isinstance(r, dict) or r.get("success") is False or not rows:
        return None, r
    fields = rows[0].get("fields") or {}
    if null_ok and field not in fields:
        # MEASURED live 2026-10-07: jawa/get_defs OMITS a null field from `fields` (a requested field whose value is
        # null comes back as an empty dict). For a field that is legitimately null (a nulled designationCategory)
        # that means "null", not "unreadable" -- the same reading LuminousPigment `_designation` takes. A def that
        # did not resolve at all (no rows) is still unreadable, handled above.
        return "(null)", r
    return fields.get(field), r


def _apply(t):
    r = t.bridge_call("jawa/static_call", type=PATCHER_TYPE, method="Apply", args="")
    return isinstance(r, dict) and r.get("success") is True


def _unmeasured(t, why):
    t.upstream_reason = "UNMEASURED: " + why
    t.upstream_failed = True


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


POWERCELL_WRECKED = "RM_WM_PowerCell_Wrecked"


def _wrecked_power(t):
    """The REAL output of a spawned Wrecked power cell. wreckedRatio scales the private
    CompProperties_Power.basePowerConsumption (never serialised, so get_defs' idlePowerDraw is a vanilla -1.0
    default constant and cannot move). The spawned Thing's CompPowerTrader.EnergyOutputPerTick is what the mod's
    rewrite actually changes. Returns (energyOutputPerTick or None, raw)."""
    if getattr(t, "_wm_wrecked_cell", None) is None:
        cells = t.spawn(POWERCELL_WRECKED, count=1, at="point")
        rows = (t.bridge_call("jawa/list_things", defName=POWERCELL_WRECKED,
                              rect="%d,%d,20,20" % (cells[0][0] - 10, cells[0][1] - 10)) or {}).get("things") or []
        if not rows:
            return None, "no %s found after spawning it" % POWERCELL_WRECKED
        t._wm_wrecked_cell = rows[0]["id"]
    t.wait_ticks(250)
    r = t.bridge_call("jawa/power_net", thing=t._wm_wrecked_cell)
    if not isinstance(r, dict) or not r.get("success") or not r.get("isPowerTrader"):
        return None, r
    return r.get("energyOutputPerTick"), r


def _wrecked_power_check(b, a):
    # Default wreckedRatio 0.001 -> drive sets 0.01: a ten-fold change in output. Ratio of two reads, so the
    # original cell's wattage does not need to be hard-coded. Output is negative (a producer).
    bb, aa = _num(b), _num(a)
    if not bb or aa is None:
        return "Wrecked cell output unreadable (before %r, after %r)" % (b, a)
    return None if abs(aa / bb - 10.0) < 0.5 else "Wrecked cell output ratio %.3f, expected 10 (0.001 -> 0.01)" % (aa / bb)


# One chain per setting (a failure in one must not taint the others). Each: set the
# setting live, re-run WreckedMachinesPatcher.Apply (what closing the settings window
# runs), read the def it rewrites, restore; the restore read is the off arm.
DRIVES = (
    ("researchCostFactor", 2.0, "ResearchProjectDef/RM_WM_AutomatedSmelterRestoration", "baseCost",
     lambda b, a: None if _num(a) is not None and _num(b) and abs(_num(a) - 2 * _num(b)) < 1 else "baseCost did not double"),
    ("materialCostFactor", 2.0, "ThingDef/RM_WM_AutomatedSmelter_Kludged", "costList",
     lambda b, a: None if a != b and "240" in str(a) else "Kludged costList did not scale (Steel 120 -> 240)"),
    ("skipRestorationResearch", True, "ThingDef/RM_WM_AutomatedSmelter_Repaired", "researchPrerequisites",
     lambda b, a: None if "RM_WM_AutomatedSmelterRestoration" in str(b) and "RM_WM_AutomatedSmelterRestoration" not in str(a)
     else "Repaired still names the restoration research"),
    ("allowDonorSmelter", True, "ThingDef/VFEFactory_AutomatedSmelter", "designationCategory",
     lambda b, a: None if "VFEFactory_Factories" in str(a) and "VFEFactory_Factories" not in str(b)
     else "donor smelter did not reappear in the Factories category", "null_ok"),
    ("allowFullRestoration", True, "ThingDef/RM_WM_AutomatedSmelter_Repaired", "designationCategory",
     lambda b, a: None if "VFEFactory_Factories" in str(a) and "VFEFactory_Factories" not in str(b)
     else "the Original (Repaired) grade did not reappear in the Factories category", "null_ok"),
    ("refurbishedRatio", 0.5, "ThoughtDef/RM_WM_SalvagedEmanatorSoothe", "stages",
     lambda b, a: None if str(a) != str(b) else "Refurbished emanator mood did not change"),
    ("kludgedRatio", 0.1, "ThoughtDef/RM_WM_SalvagedEmanatorSoothe", "stages",
     lambda b, a: None if str(a) != str(b) else "Kludged emanator mood did not change"),
    ("wreckedRatio", 0.01, "ThingDef/RM_WM_PowerCell_Wrecked", "powerOutput", _wrecked_power_check, "power"),
)


def _make_drive(field, new, defpath, defield, check, mode=None):
    def read(t):
        if mode == "power":
            return _wrecked_power(t)
        return _def_field(t, defpath, defield, null_ok=(mode == "null_ok"))

    def chain(t):
        if t.session is None:
            with t.component("%s_rewrites_its_def" % field, toggle=field):
                pass
            with t.component("%s_restores_the_shipped_def" % field, toggle=field):
                pass
            return
        with t.component("%s_rewrites_its_def" % field, toggle=field):
            old = _setting(t, "get", field).get("value")
            if old is None:
                _unmeasured(t, "mod_settings_field could not read %s" % field)
                return
            before, raw = read(t)
            if before is None:
                _unmeasured(t, "could not read %s %s: %s" % (defpath, defield, str(raw)[:160]))
                return
            try:
                if not _setting(t, "set", field, new).get("success") or not _apply(t):
                    raise ExpectationFailed("could not set %s=%s and re-run Apply" % (field, new))
                after, _ = read(t)
                why = check(before, after)
                if why:
                    raise ExpectationFailed("%s=%s: %s (before %r, after %r)" % (field, new, why, before, after))
            finally:
                _setting(t, "set", field, old)
                _apply(t)
        with t.component("%s_restores_the_shipped_def" % field, toggle=field):
            back, _ = read(t)
            if str(back) != str(before):
                raise ExpectationFailed("%s restored but %s %s reads %r, was %r" % (field, defpath, defield, back, before))
    chain.__name__ = "setting_%s" % field
    return chain


for _d in DRIVES:
    suite.chain("setting_%s_drives_def" % _d[0])(_make_drive(*_d))


def _runtime_toggle(field):
    def chain(t):
        with t.component("%s_gates_play" % field, toggle=field):
            if t.session is not None:
                _unmeasured(t, "%s is read at play time (placement / thought), not by Apply; "
                               "needs a blueprint placed or a pawn near a powered emanator" % field)
    chain.__name__ = "runtime_%s" % field
    return chain


for _f in RUNTIME_SETTINGS:
    suite.chain("setting_%s_gates_play" % _f)(_runtime_toggle(_f))


@suite.chain("tier_shapes_static")
def tier_shapes_static(t):
    """Offline-provable halves of the tier contract (process counts, canOverclock, replaceTags
    build-over key, research gate, settings wiring), asserted from the shipped XML/C#.
    The live build-over through a blueprint is still UNMEASURED: no bridge tool resolves a
    blueprint through GenConstruct (jawa/spawn_batch places finished things)."""
    with t.component("tiers_have_the_promised_shapes", beyond_toggle=True):
        problems = static_checks()
        if problems:
            raise ExpectationFailed("; ".join(problems))
    with t.component("replace_tags_build_over_live", beyond_toggle=True):
        if t.session is not None:
            _unmeasured(t, "needs a blueprint placed over a standing tier and resolved by construction; "
                         "no bridge tool places a blueprint (jawa/spawn_batch spawns finished things)")


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
