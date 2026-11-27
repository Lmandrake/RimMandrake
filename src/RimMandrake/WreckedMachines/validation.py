"""validation.py -- modcheck suite for RimMandrake Wrecked Machines
(mandrake.rm.wreckedmachines).

Grounded in this mod's actual Defs. The mod carries C# and a settings class
(`Source/WreckedMachinesMod.cs`, SETTINGS below). Each setting that Apply reads is
driven by its chain setting_<field>_drives_def (set, re-run WreckedMachinesPatcher.Apply,
read the def it rewrites, restore); the tier shapes (process counts, canOverclock,
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
That list is `modcheck_env.py` beside this file (MODCHECK_DONOR_ENVIRONMENTS_1),
composed by `modcheck run` through TIERS["wreckedmachines"]; it says why no
other VE mod is needed.
`petetimessix.researchreinvented` is MayRequire-guarded (the Analyse
special-opportunity def) and is NOT required for anything this suite
exercises.

THE SCENES (item RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL): one chain scene_<x> per acceptance
and interaction scene of design/concepts/WreckedMachines/scenes.json, each asserting its row's start, then its action and
expect, then its control. They read the mechanisms of the 0.1.0 design (machine lines, the repair on the machine, study,
placement) through the mod's proof type, whose contract is written above the scenes; until the build ships a method, the
scenes that need it fail at their start and name it. selftest_wm_scenes.py checks the start, the control and the acts that
no scene may make after its start, on a fake game. They replace the three spawn-and-inspect chains and the four UNMEASURED
play-time rows of the build before this design.

Still not proven by this suite:
  1. The replaceTags build-over of the current build (tier_shapes_static/replace_tags_build_over_live stays UNMEASURED):
     the 0.1.0 design removes that ladder for a repair on the machine (plan.md), so no live check is written for it.
  2. `RM_WM_AnalyseWreckedSmelter` (the ResearchReinvented Analyse opportunity) is not exercised; its file header records
     it as "NOT VERIFIED AT RUNTIME".
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
            "requireLowerGradeUnderneath", "enableSalvagedEmanators",
            "alloyForgeProgressiveGate", "plasteelAlloyEnabled",
            "smeltersFollowSalvageRule", "cremateWithoutStripping")
# Settings read at play time rather than by Apply (PlaceWorker / ThoughtWorker).
RUNTIME_SETTINGS = ("requireLowerGradeUnderneath", "enableSalvagedEmanators")
# Read at play time by the workers in Source/WreckedMachinesSalvage.cs.
SALVAGE_SETTINGS = ("smeltersFollowSalvageRule", "cremateWithoutStripping")
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


def _alloy_forge_checks(bad):
    """SHIP_ALLOY_FORGE_1: the forge is gated by the early restoration project, which follows the smelter
    restoration; the plasteel process is gated by the late project, which follows the forge's and
    AdvancedFabrication. Read from the shipped research XML and the gate patch."""
    rroot = ET.parse(os.path.join(HERE, "Defs", "ResearchProjectDefs", "ResearchProjects_WreckedMachines.xml")).getroot()
    rp = {d.findtext("defName"): [li.text for li in d.findall("prerequisites/li")] for d in rroot.findall("ResearchProjectDef")}
    if rp.get("RM_WM_AlloyForgeRestoration") != ["RM_WM_AutomatedSmelterRestoration"]:
        bad.append("RM_WM_AlloyForgeRestoration must follow only the smelter restoration, has %r" % rp.get("RM_WM_AlloyForgeRestoration"))
    if sorted(rp.get("RM_WM_PlasteelAlloying") or []) != ["AdvancedFabrication", "RM_WM_AlloyForgeRestoration"]:
        bad.append("RM_WM_PlasteelAlloying must follow the forge restoration and AdvancedFabrication, has %r" % rp.get("RM_WM_PlasteelAlloying"))
    ops = ET.parse(os.path.join(HERE, "Patches", "WreckedMachines_AlloyForgeGates.xml")).getroot()
    xp = [(x.text or "") for x in ops.iter("xpath")]
    vals = " ".join(ET.tostring(v, encoding="unicode") for v in ops.iter("value"))
    if not any('VFEFactory_AutomatedAlloyForge"]/researchPrerequisites' in x for x in xp) or "RM_WM_AlloyForgeRestoration" not in vals:
        bad.append("the gate patch does not replace the alloy forge's research with RM_WM_AlloyForgeRestoration")
    if not any('VFEFactory_AlloyPlasteel"]' in x for x in xp) or "RM_WM_PlasteelAlloying" not in vals:
        bad.append("the gate patch does not gate VFEFactory_AlloyPlasteel with RM_WM_PlasteelAlloying")
    cs = open(os.path.join(HERE, "Source", "WreckedMachinesMod.cs"), encoding="utf-8").read()
    if "if (gated) AlloyForge.costList = EarlyForgeCost(StockForgeCost);" not in cs:
        bad.append("the progressive gate does not swap the forge's advanced components for industrial ones")
    if "plasteelAlloyEnabled, PlasteelProcessNext)" not in cs:
        bad.append("re-enabling plasteel does not put it back before its loaded neighbour (it would jump ahead of durasteel)")
    if "if (!forgeCostApplied && AlloyForge != null" not in cs:
        bad.append("the forge cost is not set once at startup (a live change alters deconstruct refunds)")
    tab = open(os.path.join(HERE, "..", "..", "RimUtinni", "ResearchRetag", "Patches", "RUT_ResearchTabAssign.xml"),
               encoding="utf-8").read()
    for n in ("RM_WM_AutomatedSmelterRestoration", "RM_WM_AlloyForgeRestoration", "RM_WM_PlasteelAlloying"):
        if 'ResearchProjectDef[defName="%s"]/tab' % n not in tab:
            bad.append("%s is not retabbed beside the smelter (RUT_ResearchTabAssign.xml)" % n)


def static_checks():
    """Offline: the grades are the shapes the mod promises, and every setting is wired."""
    bad = []
    _alloy_forge_checks(bad)
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
    salvage = open(os.path.join(HERE, "Source", "WreckedMachinesSalvage.cs"), encoding="utf-8").read()
    apply = src.split("public static void Apply", 1)[-1] + ladder  # LadderPatcher.Apply reads ratios via RatioFor
    for f in fields:
        if '"%s"' % f not in scribed:
            bad.append("%s is not Scribed" % f)
        if not re.search(r"\b%s\b" % f, ui):
            bad.append("%s has no control in DoWindowContents" % f)
        reader = salvage if f in SALVAGE_SETTINGS else ladder if f in RUNTIME_SETTINGS else apply
        # The three ratios are read through the normalised WreckedMachinesSettings.Ladder property, which is
        # itself built from the raw fields (src, the settings class) - so a read of .Ladder is a read of each.
        via_ladder = (f in ("wreckedRatio", "kludgedRatio", "refurbishedRatio")
                      and re.search(r"Ladder\s*=>[^;]*\b%s\b" % f, src) is not None
                      and "WreckedMachinesSettings.Ladder" in reader)
        if "WreckedMachinesSettings.%s" % f not in reader and not via_ladder:
            bad.append("%s is never read (a dead setting)" % f)
    return bad


try:
    from modcheck import Suite, ExpectationFailed, RowDone
except ImportError:
    _UTILS = os.path.join(HERE, "..", "Utils")
    sys.path.insert(0, _UTILS)
    try:
        from modcheck import Suite, ExpectationFailed, RowDone
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
    if t._guard() and not (r or {}).get("success"):
        raise ExpectationFailed("UNMEASURED: jawa/drain_log did not answer: %r" % (r,))   # unreadable != clean
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
    # SHIP_ALLOY_FORGE_1. Off restores VFE's stock gate on the forge.
    ("alloyForgeProgressiveGate", False, "ThingDef/VFEFactory_AutomatedAlloyForge", "researchPrerequisites",
     lambda b, a: None if "RM_WM_AlloyForgeRestoration" in str(b) and "VFE_ComplexFactories" in str(a)
     and "RM_WM_AlloyForgeRestoration" not in str(a) else "forge gate did not swap to VFE_ComplexFactories"),
    # Off drops VFEFactory_AlloyPlasteel from the forge's processor list (read deep through comps).
    ("plasteelAlloyEnabled", False, "ThingDef/VFEFactory_AutomatedAlloyForge", "comps",
     lambda b, a: None if "VFEFactory_AlloyPlasteel" in str(b) and "VFEFactory_AlloyPlasteel" not in str(a)
     else "plasteel process still on the forge (or never readable in comps)"),
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
                raise RowDone
            before, raw = read(t)
            if before is None:
                _unmeasured(t, "could not read %s %s: %s" % (defpath, defield, str(raw)[:160]))
                raise RowDone
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


import re as _re_forge
_FORGE_PROC = _re_forge.compile(r"\b(RSW_Alloy\w+|VFEFactory_(?:Alloy|Create)\w+)\b")


def _forge_process_order(v):
    """The forge's process defNames in list order, read from the comps value (first occurrence of each)."""
    seen = []
    for m in _FORGE_PROC.findall(str(v) if v is not None else ""):
        if m not in seen:
            seen.append(m)
    return seen


def _require_gate_on(t):
    """The forge's research gate and early cost are the SHIPPED behaviour (alloyForgeProgressiveGate on); a session
    with it off says so instead of failing."""
    on = _setting(t, "get", "alloyForgeProgressiveGate").get("value")
    if on is None:
        _unmeasured(t, "mod_settings_field could not read alloyForgeProgressiveGate")
        raise RowDone
    if str(on).lower() == "false":
        _unmeasured(t, "alloyForgeProgressiveGate is off in this session: the shipped gate is not what loads")
        raise RowDone


@suite.chain("alloy_forge_gated")
def alloy_forge_gated(t):
    """SHIP_ALLOY_FORGE_1 on a load: the forge needs RM_WM_AlloyForgeRestoration and costs no advanced components,
    the plasteel process needs RM_WM_PlasteelAlloying, durasteel is the forge's first recipe, the forge's research
    sits on the smelter's tab, and no def logged an error."""
    with t.component("forge_needs_alloy_forge_restoration", toggle="alloyForgeProgressiveGate"):
        if t.session is None:
            raise RowDone
        _require_gate_on(t)
        v, raw = _def_field(t, "ThingDef/VFEFactory_AutomatedAlloyForge", "researchPrerequisites")
        if v is None:
            _unmeasured(t, "could not read the forge's researchPrerequisites: %s" % str(raw)[:160])
            raise RowDone
        if "RM_WM_AlloyForgeRestoration" not in str(v):
            raise ExpectationFailed("forge researchPrerequisites %r lack RM_WM_AlloyForgeRestoration" % v)
    with t.component("plasteel_process_needs_plasteel_alloying"):
        if t.session is None:
            raise RowDone
        v, raw = _def_field(t, "PipeSystem.ProcessDef/VFEFactory_AlloyPlasteel", "researchPrerequisites")
        if v is None:
            _unmeasured(t, "get_defs could not read a PipeSystem.ProcessDef: %s" % str(raw)[:160])
            raise RowDone
        if "RM_WM_PlasteelAlloying" not in str(v):
            raise ExpectationFailed("VFEFactory_AlloyPlasteel researchPrerequisites %r lack RM_WM_PlasteelAlloying" % v)
    with t.component("forge_costs_no_advanced_components", toggle="alloyForgeProgressiveGate"):
        # The stock cost (4 ComponentSpacer) needs plasteel + AdvancedFabrication: the early forge would be a late one.
        if t.session is None:
            raise RowDone
        _require_gate_on(t)
        v, raw = _def_field(t, "ThingDef/VFEFactory_AutomatedAlloyForge", "costList")
        if v is None:
            _unmeasured(t, "could not read the forge's costList: %s" % str(raw)[:160])
            raise RowDone
        if "ComponentSpacer" in str(v) or "ComponentIndustrial" not in str(v):
            raise ExpectationFailed("forge costList %r still needs advanced components (or no industrial ones)" % v)
    with t.component("durasteel_is_the_forges_first_recipe"):
        if t.session is None:
            raise RowDone
        v, raw = _def_field(t, "ThingDef/VFEFactory_AutomatedAlloyForge", "comps")
        order = _forge_process_order(v)
        if not order:
            _unmeasured(t, "could not read the forge's processes through comps: %s" % str(raw)[:160])
            raise RowDone
        if "RSW_AlloyDurasteel" not in order:
            _unmeasured(t, "RSW_AlloyDurasteel is not on the forge (mandrake.rsw.armoury absent, or durasteelAlloyEnabled "
                           "off): %s" % order)
            raise RowDone
        if order[0] != "RSW_AlloyDurasteel":
            raise ExpectationFailed("durasteel is not the forge's first recipe: %s" % order)
    with t.component("forge_research_on_the_workshop_tab"):
        # ResearchRetag (mandrake.rut.researchretag) puts the smelter restoration on RUT_Tree_Workshop; the two forge
        # projects that follow it must sit beside it, not alone on Main.
        if t.session is None:
            raise RowDone
        tabs = {}
        for n in ("RM_WM_AutomatedSmelterRestoration", "RM_WM_AlloyForgeRestoration", "RM_WM_PlasteelAlloying"):
            v, raw = _def_field(t, "ResearchProjectDef/" + n, "tab")
            if v is None:
                _unmeasured(t, "could not read %s's tab: %s" % (n, str(raw)[:160]))
                raise RowDone
            tabs[n] = str(v)
        if "RUT_Tree_Workshop" not in tabs["RM_WM_AutomatedSmelterRestoration"]:
            _unmeasured(t, "the smelter restoration is not on RUT_Tree_Workshop (ResearchRetag absent?): %r" % tabs)
            raise RowDone
        off = [n for n, v in tabs.items() if "RUT_Tree_Workshop" not in v]
        if off:
            raise ExpectationFailed("forge research not on the smelter's tab: %r" % tabs)
    with t.component("alloy_forge_loads_clean"):
        if t.session is None:
            return
        r = t.bridge_call("jawa/drain_log", limit=200, errorsOnly=True)
        if not (r or {}).get("success"):
            raise ExpectationFailed("UNMEASURED: jawa/drain_log did not answer: %r" % (r,))
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        hit = [m for m in msgs if any(n in m for n in ("RM_WM_AlloyForge", "RM_WM_PlasteelAlloying", "AlloyForgeGates"))]
        if hit:
            raise ExpectationFailed("log errors name the alloy forge gates: %r" % hit)


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


# =========================================================================== scenes.json entry points
# Item RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL. One chain per acceptance and interaction scene of
# design/concepts/WreckedMachines/scenes.json, named scene_<id without sc_>. Each follows its row: the first component asserts
# the row's start, the action and the expect are the components that follow, and the control (the foil: a machine that must
# stay unrepaired, locked or refused) runs in the same pass. The bar each scene decides is in tree.json. A reset is the
# harness's job: these chains clean only what they spawned, and leave the map to the runner (the item's words).
#
# THE PROOF CONTRACT. Almost every mechanism the scenes read (machine lines, levels, repair records, placement) is built by
# the mod's 0.1.0 build in the order of plan.md, after this script. The scenes read it through one static type of the mod,
# PROOF below, through jawa/static_call; each method returns text, one entry per line, "VERB word | key value | key value".
# Until the mod ships a method, the scene that needs it fails at its start with "the mod's proof type does not answer
# <method>": an unbuilt bar is red, never skipped. The methods and the line each one returns:
#   Loaded()                 "LOADED version <v> | lines <n>"
#   Machines()               "MACHINE <line> | on <true|false> | wrecked <def> | kludged <def> | refurbished <def> | original <def>"
#                            one per ancient machine, the 18 factory machines, the power cell and the emanator
#   Settings()               "SETTING <field> | value <v> | shipped <v>"   every Mod Settings field
#   Projects()               "PROJECT <defName> | line <line> | step <1|2>"  the two restoration projects of each machine
#   Level(<thingId>)         "LEVEL <Wrecked|Kludged|Refurbished|none> | line <line> | def <def>"
#   Repair(<thingId>)        "REPAIR <none|ordered|working> | next <level> | delivered <def>:<n>,... | work <done>/<total>"
#   SignalLog()              "SIGNAL <thingId> | from <level> | to <level> | tick <t>"  every level-changed signal since load
#   Placement()              "PLACE <def> | where <ruin|ordinary>"  what map generation may place, read from the switches now
#   InRuinRoom(<x>,<z>)      "ROOM <true|false>"
#   Speed(<thingId>)         "SPEED <factor>"   the applied work speed of a level (1 = the Original's)
#   Onboarding(<line>)       "ROW <line> | kludged <processDef>,... | refurbished <processDef>,..."  the onboarding table's row
#   LineLabels()             "LABEL <line> | label <the Mod Settings label text>"
#   TextureIds()             "TEX <def> | hash <hash of the texture loaded>"   the art of the build under test
#   PlantLighterWrecked(<line>)  stages the planted row of sc_three_looks_rows (Kludged drawn as Wrecked, lighter); "PLANTED <def>"
# The repair order is read the way the player reads it: the machine is selected and its gizmos listed (rimworld/
# list_selected_gizmos); REPAIR_GIZMO names the label words of the order.
PROOF = "RimMandrake.WreckedMachines.RM_WreckedMachinesProof"
SCENE_ITEM = "RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL"
LINES_FIELD = "machineLines"            # the Mod Settings dictionary line -> on (tree.json, inv_mod_settings)
RUIN_SWITCH, ORDINARY_SWITCH = "placeInRuins", "placeOnOrdinaryMaps"    # the two placement switches (plan.md, order step 5)
REPAIR_GIZMO = ("repair", "restore")    # words of the repair order's label, lower case
COMPONENT = "RM_WM_AncientComponent"
FACTORY_FLOOR = "VFEF_FactoryFloor"     # VFE Factory 1.6 Defs/TerrainDefs (read 2026-11-27)
PLAIN_FLOOR = "WoodPlankFloor"
FACTORY_RESEARCH = ("VFE_BasicFactories", "VFE_ComplexFactories")
FACTORY_PARTS = ("VFEFactory_Conveyor", "VFEFactory_FactoryHopper", "VFEFactory_Booster", "VFEFactory_Heatsink")
CONDUIT = "PowerConduit"
LAMPS_PER_NET = 8                       # "more lamps than the Kludged cell can light" (sc_cell_and_emanator)
TAKE_APART_REPEATS = 3                  # sc_no_handouts: take-aparts of each level, written before the first run
RR_PACKAGE = "petetimessix.researchreinvented"
VCE_PACKAGE = "vanillaexpanded.vcooke"   # Vanilla Cooking Expanded; the cannery tier adds it (read as the loaded list says)
# The originals, measured: VFE Factory 1.6 ThingDefs_Buildings, and the base game's defs through RimSage (2026-11-27).
ORIGINAL = {"smelter": "VFEFactory_AutomatedSmelter", "autoloom": "VFEFactory_Autoloom", "alloyforge": "VFEFactory_AutomatedAlloyForge",
            "drill": "VFEFactory_AutomatedDrillPlatform", "powercell": "VanometricPowerCell", "emanator": "PsychicEmanator"}
LAMP, WALL, BENCH, RUBBLE, SLAG = "StandingLamp", "Wall", "HiTechResearchBench", "Filth_RubbleBuilding", "ChunkSlagSteel"
# The old names that must leave the game when the forge is onboarded (plan.md, "Leaves the mod when the forge is onboarded").
OLD_FORGE_PROJECTS = ("RM_WM_AlloyForgeRestoration", "RM_WM_PlasteelAlloying")
OLD_FORGE_SETTINGS = ("alloyForgeProgressiveGate", "plasteelAlloyEnabled")
# Counts the row says the tester writes before the first run (scenes.json: "the number is written in the test table before the
# first run"). Not tuning numbers of the mod: how much of the game's own randomness one run looks at.
GENERATOR_RUNS = 200                    # runs per generator, sc_no_handouts (the hang guard of jawa/thing_set_sample is 2000)
RUIN_MAPS = 6                           # ruin maps, sc_ruin_holds_wrecks
ORDINARY_MAPS, ORDINARY_WANT = 20, 1    # Y ordinary maps and X of them with a wreck, sc_rare_wreck_ordinary_map (kind B)
FLOOD = 12                              # "no map is flooded": more of this mod's things than this on one ruin map
STUDY_DAYS = 6                          # days of clock a study scene gives the researcher
# Every word the player must not read (sc_text_names_no_setting); the Star Wars names come from biome_rulings.md.
SETTING_WORDS = ("ship", "Kolyska", "Rakatan", "Utinni", "Jawa", "clan", "god", "favour", "the crash")

# Acts that a scene may not make after its asserted start (the item's criteria): finish research, finish a study, set a level,
# spawn a machine. The selftest reads every scene's calls against this, with ALLOWED_AFTER_START for the rows that say so.
FORBIDDEN_AFTER_START = ("jawa/research_finish_project", "jawa/research_bulk", "jawa/research_progress")
FORBIDDEN_PROOF_METHODS = ("SetLevel", "FinishStudy", "CompleteRepair")
ALLOWED_AFTER_START = {
    "sc_menu_and_research": ("jawa/research_bulk",),          # its action: "finish every research project"
    "sc_cannery_tier": ("jawa/research_bulk",),               # its action: "finish every research project"
    "sc_component_gate": ("jawa/research_bulk",),             # its action: "with every research project finished"
    "sc_every_machine_onboarded": ("_finish_first(",),        # its action: "finish that machine's first project by command"
    "sc_levels_do_their_work": ("place",),                  # it places the machines it compares (its start)
}


def START_MARK(t, sid):
    """The point after which a scene acts only by orders, clock and reads; the selftest swaps in a recorder."""
    return None


def _live(t):
    return t.session is not None and t._guard()


def _fields(line):
    """'LEVEL Kludged | line smelter | def X' -> {'_verb': 'LEVEL', '_word': 'Kludged', 'line': 'smelter', 'def': 'X'}."""
    parts = [p.strip() for p in str(line).split("|")]
    head = parts[0].split(None, 1)
    out = {"_verb": head[0] if head else "", "_word": head[1].strip() if len(head) > 1 else ""}
    for p in parts[1:]:
        k, _, v = p.partition(" ")
        if k:
            out[k] = v.strip()
    return out


def _proof(t, method, args=""):
    """The mod's proof type: a list of parsed lines; a refusal fails the component and names the method."""
    r = t.bridge_call("jawa/static_call", type=PROOF, method=method, args=args)
    if not t._guard():
        return []
    text = str((r or {}).get("result") or "")
    if not (r or {}).get("success") or text.startswith("REFUSED") or text.startswith("error="):
        raise ExpectationFailed("the mod's proof type does not answer %s(%s): %s" % (method, args, str(r)[:200]))
    return [_fields(ln) for ln in text.splitlines() if ln.strip()]


def _machines(t):
    return {m["_word"]: m for m in _proof(t, "Machines") if m["_verb"] == "MACHINE"}


def _level(t, tid):
    rows = _proof(t, "Level", tid)
    return rows[0]["_word"] if rows else None


def _start(t, sid, lines_on=True):
    """The start every row names first: the proof type answers, every setting at its shipped value, every line on. Returns the
    machines. A scene whose row switches lines off says so (lines_on=False) and asserts its own state after."""
    loaded = _proof(t, "Loaded")
    if not loaded or loaded[0]["_verb"] != "LOADED":
        raise ExpectationFailed("start of %s: the proof type answered %r, not LOADED" % (sid, loaded))
    off_shipped = ["%s=%s (shipped %s)" % (s["_word"], s.get("value"), s.get("shipped"))
                   for s in _proof(t, "Settings") if s["_verb"] == "SETTING" and s.get("value") != s.get("shipped")]
    ms = _machines(t)
    if off_shipped and lines_on:
        raise ExpectationFailed("start of %s: settings not at their shipped values: %s" % (sid, off_shipped))
    if not ms:
        raise ExpectationFailed("start of %s: the proof type lists no ancient machine" % sid)
    off = sorted(k for k, m in ms.items() if m.get("on") != "true")
    if lines_on and off:
        raise ExpectationFailed("start of %s: machine lines off at the start: %s" % (sid, off))
    return ms


def _line(t, ms, key):
    m = ms.get(key)
    if m is None:
        raise ExpectationFailed("the proof type lists no machine line %r (has %s)" % (key, sorted(ms)))
    return m


def _set_line(t, key, on):
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=LINES_FIELD, key=key,
                      value="true" if on else "false")
    if t._guard() and not ((r or {}).get("success") and _apply(t)):
        raise ExpectationFailed("could not set the %s line %s and apply: %s" % (key, "on" if on else "off", str(r)[:200]))


def _set_switch(t, field, on):
    r = _setting(t, "set", field, "true" if on else "false")
    if t._guard() and not (r.get("success") and _apply(t)):
        raise ExpectationFailed("could not set %s=%s and apply: %s" % (field, on, str(r)[:200]))


def _build(t, defname, x, z, rot="south", faction="player"):
    """Place one finished building (scene staging, before START_MARK) and return its id, read back from the map."""
    r = t.bridge_call("jawa/build_batch", ops="%s:%d,%d,%s" % (defname, x, z, rot), faction=faction)
    if not t._guard():
        return None
    rows = (t.bridge_call("jawa/list_things", defName=defname, rect="%d,%d,7,7" % (x - 3, z - 3)) or {}).get("things") or []
    if not rows:
        raise ExpectationFailed("staging: %s did not stand at (%d,%d) after build_batch: %s" % (defname, x, z, str(r)[:160]))
    t.__dict__.setdefault("_wm_pos", {})[rows[0]["id"]] = (x, z)
    return rows[0]["id"]


def _many(t, ops):
    """Staging of plain buildings (walls, conduits, lamps) in one call: [(def, x, z)]."""
    if ops:
        t.bridge_call("jawa/build_batch", ops=";".join("%s:%d,%d" % o for o in ops), faction="player")


def _designate(t, desig, tid, at=None):
    """A player's order on one thing (Uninstall, Deconstruct, Haul): jawa/designate_batch on the thing's cell. Returns the reply:
    `added` 0 with the thing in skippedWrongType is the game refusing the order for that thing."""
    x, z = at or t.__dict__.get("_wm_pos", {}).get(tid, (None, None))
    if x is None:
        raise ExpectationFailed("no known cell for %s to designate %s on" % (tid, desig))
    return t.bridge_call("jawa/designate_batch", action="add", designation=desig, rect="%d,%d,1,1" % (int(x), int(z))) or {}


def _items(t, defname, x, z, count):
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,%d" % (defname, x, z, count))


def _floor(t, terrain, x, z, w, h):
    ops = ";".join("%d,%d" % (x + i, z + j) for i in range(w) for j in range(h))
    t.bridge_call("jawa/set_terrain_batch", terrainDef=terrain, ops=ops)


def _colonist(t, x, z, research=True):
    r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=x, z=z)
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if _live(t) and not pid:
        raise ExpectationFailed("staging: no colonist spawned: %s" % str(r)[:160])
    if pid and not research:
        t.bridge_call("jawa/set_work_priority", pawnId=pid, workType="Research", priority=0)
    return pid


def _job(t, pid):
    g = t.bridge_call("jawa/pawn_get", pawn=pid) or {}
    return str(g.get("job") or g.get("curJob") or g)


def _count(t, defname, rect=None):
    rows = (t.bridge_call("jawa/list_things", defName=defname, rect=rect or _site(t), limit=2000) or {}).get("things") or []
    return sum(int(r.get("stackCount") or 1) for r in rows)


def _site(t, size=60):
    x, z = t.anchor
    return "%d,%d,%d,%d" % (x - size // 2, z - size // 2, size, size)


def _gizmos(t, tid):
    """The selected thing's gizmos as the player sees them: (label, disabled, reason, id) rows."""
    t.bridge_call("rimworld/clear_selection")
    t.bridge_call("jawa/select_things", ids=tid)
    r = t.bridge_call("rimworld/list_selected_gizmos") or {}
    out = []
    for g in r.get("gizmos") or []:
        out.append((str(g.get("label") or ""), bool(g.get("disabled") or g.get("isDisabled")),
                    str(g.get("disabledReason") or g.get("disabledReasonText") or ""), g.get("gizmoId") or g.get("id")))
    return out


def _repair_order(t, tid):
    """(present, available, reason, gizmo id) of the machine's repair order."""
    for label, disabled, reason, gid in _gizmos(t, tid):
        if any(w in label.lower() for w in REPAIR_GIZMO):
            return True, not disabled, reason, gid
    return False, False, "", None


def _give_repair(t, tid):
    present, ok, reason, gid = _repair_order(t, tid)
    if not present or not ok:
        raise ExpectationFailed("the repair order on %s is %s: %s" % (tid, "missing" if not present else "unavailable", reason))
    r = t.bridge_call("rimworld/execute_gizmo", gizmoId=gid)
    if t._guard() and not (r or {}).get("success", True):
        raise ExpectationFailed("execute_gizmo(repair) refused on %s: %s" % (tid, str(r)[:160]))


def _researched(t, project):
    r = t.bridge_call("jawa/research_availability", project=project) or {}
    return bool((r.get("result") or {}).get("isFinished"))


def _research_row(t, project):
    return t.bridge_call("jawa/research_availability", project=project) or {}


def _projects(t, line):
    return sorted((p.get("step"), p["_word"]) for p in _proof(t, "Projects") if p["_verb"] == "PROJECT" and p.get("line") == line)


def _menu_visible(t, defname):
    """True when the build menu shows the def (jawa/architect_designator_visible), False when it does not, None unread."""
    r = t.bridge_call("jawa/architect_designator_visible", defName=defname) or {}
    if not r.get("success", False):
        return None
    return any(row.get("visible") for row in r.get("rows") or [])


def _wait_days(t, days, step=2500):
    for _ in range(int(days * 60000 // step)):
        t.wait_ticks(step)


def _study(t, defname):
    """jawa/study_record of a kind of thing: status no_study_comp | no_record | partial | complete, and its projects."""
    return t.bridge_call("jawa/study_record", **{"def": defname}) or {}


def _wait_level(t, tid, want, budget_days):
    """Advance in quarter days until the machine reads `want` (or the budget ends); returns the last level read."""
    lvl = None
    for _ in range(int(budget_days * 4)):
        t.wait_ticks(15000)
        lvl = _level(t, tid)
        if lvl == want:
            break
    return lvl


def _log_errors_naming_mod(t):
    r = t.bridge_call("jawa/drain_log", limit=500, errorsOnly=True) or {}
    if t._guard() and not r.get("success"):
        raise ExpectationFailed("UNMEASURED: jawa/drain_log did not answer: %r" % (r,))
    return [m.get("text", "") for m in r.get("messages") or [] if any(n.lower() in m.get("text", "").lower() for n in ERROR_NEEDLES)]



def _levels_of(m):
    return [m.get("wrecked"), m.get("kludged"), m.get("refurbished")]


# --------------------------------------------------------------------------- showcase 2: the Factory tab without its machines

@suite.chain("scene_menu_and_research")
def scene_menu_and_research(t):
    """sc_menu_and_research (only_by_repair): no level of any ancient machine is in the build menu before or after every project
    is finished; the factory's parts are; the base game's electric smelter is in its own tab. Control: the autoloom's line off
    puts the autoloom in the menu behind the factory mod's research, and every other machine reads as before."""
    st = {}
    with t.component("start_menu_and_research"):
        if _live(t):
            st["ms"] = _start(t, "sc_menu_and_research")
            done = [p for p in FACTORY_RESEARCH + tuple(p for _, p in _projects(t, "smelter")) if _researched(t, p)]
            if done:
                raise ExpectationFailed("start: research already finished: %s" % done)
            START_MARK(t, "sc_menu_and_research")

    def read(ms):
        return {d: _menu_visible(t, d) for m in ms.values() for d in _levels_of(m) if d}

    with t.component("no_level_in_menu_before_research"):
        if _live(t):
            st["before"] = read(st["ms"])
            shown = sorted(d for d, v in st["before"].items() if v)
            unread = sorted(d for d, v in st["before"].items() if v is None)
            if unread:
                raise ExpectationFailed("UNMEASURED: the build menu could not be read for %s" % unread)
            if shown:
                raise ExpectationFailed("levels of ancient machines in the build menu before research: %s" % shown)
    with t.component("no_level_in_menu_after_all_research"):
        if _live(t):
            t.bridge_call("jawa/research_bulk", mode="finish_all")
            st["after"] = read(st["ms"])
            shown = sorted(d for d, v in st["after"].items() if v)
            if shown:
                raise ExpectationFailed("levels of ancient machines in the build menu after every project: %s" % shown)
    with t.component("factory_parts_and_base_smelter_in_menu"):
        if _live(t):
            missing = [d for d in FACTORY_PARTS if not _menu_visible(t, d)]
            if not _menu_visible(t, "ElectricSmelter"):
                missing.append("ElectricSmelter")
            if missing:
                raise ExpectationFailed("not in the build menu after their research: %s" % missing)
    with t.component("control_autoloom_line_off"):
        if _live(t):
            loom = _line(t, st["ms"], "autoloom")
            try:
                _set_line(t, "autoloom", False)
                if not _menu_visible(t, loom.get("original") or ORIGINAL["autoloom"]):
                    raise ExpectationFailed("autoloom line off: the factory's autoloom is not in the build menu (instrument or tab hidden)")
                again = {d: v for d, v in read(st["ms"]).items() if d not in _levels_of(loom)}
                drift = sorted(d for d, v in again.items() if v != st["after"].get(d))
                if drift:
                    raise ExpectationFailed("the autoloom's line moved other machines in the menu: %s" % drift)
            finally:
                _set_line(t, "autoloom", True)


def _generators(t):
    r = t.bridge_call("jawa/thing_set_sample", kind="list") or {}
    return r.get("thingSetMakers") or [], r.get("traders") or []


def _sample(t, kind, name, runs=GENERATOR_RUNS):
    r = t.bridge_call("jawa/thing_set_sample", kind=kind, runs=runs, **{"def": name}) or {}
    if t._guard() and not r.get("success"):
        raise ExpectationFailed("UNMEASURED: thing_set_sample %s %s: %s" % (kind, name, str(r)[:160]))
    return {row["def"]: row for row in r.get("rows") or []}


def _all_outputs(t, sets, traders):
    seen = {}
    for g in sets:
        for d in _sample(t, "thingSetMaker", g["defName"]):
            seen.setdefault(d, []).append(g["defName"])
    for g in traders:
        for d in _sample(t, "trader", g["defName"]):
            seen.setdefault(d, []).append(g["defName"])
    return seen


@suite.chain("scene_no_handouts")
def scene_no_handouts(t):
    """sc_no_handouts (only_by_repair, last_repair_needs_component): no generator of the game hands out a working ancient
    machine or an Ancient Component, no recipe makes a component, a wreck taken apart leaves no component. Control: with the
    power cell's and the emanator's lines off, the same runs produce the base game's working cell and emanator."""
    st = {}
    with t.component("start_no_handouts"):
        if _live(t):
            st["ms"] = _start(t, "sc_no_handouts")
            sets, traders = _generators(t)
            mods = " ".join(str(g.get("mod")) for g in sets + traders).lower()
            lacking = [m for m in ("ludeon.rimworld", "ludeon.rimworld.ideology", "ludeon.rimworld.odyssey", "ludeon.rimworld.anomaly")
                       if m + " " not in mods + " "]
            if not sets or not traders or lacking:
                raise ExpectationFailed("start: generator list empty or missing %s (%d sets, %d traders)" % (lacking, len(sets), len(traders)))
            st["sets"], st["traders"] = sets, traders
            x, z = t.anchor
            _floor(t, FACTORY_FLOOR, x - 40, z - 44, 80, 88)
            st["parts"] = [[_build(t, m[lvl], x - 36 + (i % 6) * 12, z - 40 + r * 28 + (i // 6) * 7 + 2 * j)
                            for i, (key, m) in enumerate(sorted(st["ms"].items())) for j, lvl in enumerate(("wrecked", "kludged", "refurbished"))]
                           for r in range(TAKE_APART_REPEATS)]
            st["crew"] = [_colonist(t, x + k, z) for k in range(4)]
            START_MARK(t, "sc_no_handouts")
    with t.component("generators_give_no_ancient_machine"):
        if _live(t):
            working = set(d for m in st["ms"].values() for d in (m.get("kludged"), m.get("refurbished")) if d)
            working |= {ORIGINAL["powercell"], ORIGINAL["emanator"], COMPONENT}
            st["out"] = out = _all_outputs(t, st["sets"], st["traders"])
            hits = {d: out[d][:3] for d in working if d in out}
            if hits:
                raise ExpectationFailed("generators produced working ancient machines or the component: %s" % hits)
    with t.component("no_recipe_makes_a_component"):
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs="RecipeDef/*", fields="products", limit=5000) or {}
            if not r.get("defs"):
                raise ExpectationFailed("UNMEASURED: the recipe list could not be read: %s" % str(r)[:160])
            makers = [d.get("defName") for d in r["defs"] if COMPONENT in str((d.get("fields") or {}).get("products"))]
            if makers:
                raise ExpectationFailed("recipes make %s: %s" % (COMPONENT, makers))
    with t.component("machines_taken_apart_leave_no_component"):
        if _live(t):
            found = []
            for parts in st["parts"]:          # one staged set of every level per repeat, taken apart in turn
                for tid in parts:
                    _designate(t, "Deconstruct", tid)
                for _ in range(20):
                    _wait_days(t, 0.25)
                    if not any(_level(t, tid) not in (None, "none") for tid in parts):
                        break
                found.append(_count(t, COMPONENT))
            t._current.detail = "components after each take-apart: %s" % found
            if any(found):
                raise ExpectationFailed("Ancient Components lie on the map after machines were taken apart: %s" % found)
    with t.component("control_lines_off_give_base_machines"):
        if _live(t):
            try:
                _set_line(t, "powercell", False)
                _set_line(t, "emanator", False)
                out = _all_outputs(t, st["sets"], st["traders"])
                miss = [d for d in (ORIGINAL["powercell"], ORIGINAL["emanator"]) if d not in out]
                if miss:
                    raise ExpectationFailed("with their lines off no generator produced %s in %d runs each: the read cannot see "
                                            "these machines" % (miss, GENERATOR_RUNS))
            finally:
                _set_line(t, "powercell", True)
                _set_line(t, "emanator", True)


# --------------------------------------------------------------------------- placement

RUINS_MUTATOR = "AncientRuins"   # TileMutatorDef (RimSage, 2026-11-27); AncientRuins_Frozen is its cold twin


def _tiles(t, ruin):
    """Settleable world tiles that hold an ancient ruin (or hold none), read from the world as it is: the scene chooses a tile,
    it never paints one (Minimum Force; no worldgen)."""
    cache = getattr(t, "_wm_tiles", None)
    if cache is None:
        rows = (t.bridge_call("jawa/world_mutators_get", range="0-200000", limit=5000) or {}).get("tiles") or []
        ids = {True: [], False: []}
        for r in rows:
            tid = r.get("tile", r.get("id"))
            if tid is not None:
                ids[RUINS_MUTATOR in str(r.get("mutators"))].append(tid)
        cache = {}
        for k, v in ids.items():
            ok = t.bridge_call("jawa/tile_settleable", tiles=",".join(str(i) for i in v[:400])) or {}
            good = [r.get("tile") for r in ok.get("tiles") or [] if r.get("settleable")]
            cache[k] = good or v
        t._wm_tiles = cache
    return list(cache.get(ruin) or [])


def _gen_map(t, ruin):
    """A new map of the game's own generation on the next unused tile that holds (or lacks) an ancient ruin. The runner
    discards the maps (a reset is the harness's job)."""
    used = t.__dict__.setdefault("_wm_used", set())
    free = [x for x in _tiles(t, ruin) if x not in used]
    if t._guard() and not free:
        raise ExpectationFailed("UNMEASURED: no unused %s tile left in this world" % ("ruin" if ruin else "ruin-free"))
    tile = free[0] if free else -1
    used.add(tile)
    r = t.bridge_call("jawa/world_tile_map_generate", tile=tile)
    if t._guard() and not (r or {}).get("success"):
        raise ExpectationFailed("UNMEASURED: no map generated on tile %s: %s" % (tile, str(r)[:160]))
    _go_to_tile(t, tile)
    return r


def _go_to_tile(t, tile):
    """Make the loaded map on `tile` the current map (jawa/set_current_map takes a Map.uniqueID; its refusal lists the maps)."""
    listing = t.bridge_call("jawa/set_current_map", mapId=-1) or {}
    mid = next((m.get("mapId") for m in listing.get("loadedMaps") or [] if m.get("tile") == tile), None)
    if t._guard() and mid is None:
        raise ExpectationFailed("UNMEASURED: no loaded map on tile %s: %s" % (tile, str(listing)[:160]))
    t.bridge_call("jawa/set_current_map", mapId=mid)
    now = (t.bridge_call("jawa/map_info") or {}).get("tile")
    if t._guard() and now != tile:
        raise ExpectationFailed("UNMEASURED: the current map is on tile %s, not %s" % (now, tile))


def _mod_things(t, ms):
    rows = []
    defs = set(m.get("wrecked") for m in ms.values()) | {COMPONENT}
    for d in sorted(x for x in defs if x):
        for th in (t.bridge_call("jawa/list_things", defName=d, limit=500) or {}).get("things") or []:
            room = _proof(t, "InRuinRoom", "%s,%s" % (th.get("x"), th.get("z")))
            rows.append({"def": d, "id": th.get("id"), "x": th.get("x"), "z": th.get("z"),
                         "level": _level(t, th["id"]) if d != COMPONENT else None,
                         "ruin": bool(room and room[0]["_word"] == "true")})
    return rows


@suite.chain("scene_ruin_holds_wrecks")
def scene_ruin_holds_wrecks(t):
    """sc_ruin_holds_wrecks (wreck_is_found, last_repair_needs_component): over RUIN_MAPS ruin maps, wrecks of more than one
    machine lie in ruin rooms at the Wrecked level, at least one Ancient Component lies in a ruin room, none lies outside one, no
    map is flooded. Control: the same maps with ruin placement off hold none of either."""
    st = {}
    with t.component("start_ruin_holds_wrecks"):
        if _live(t):
            st["ms"] = ms = _start(t, "sc_ruin_holds_wrecks")
            if _mod_things(t, ms):
                raise ExpectationFailed("start: this mod's things already stand on the map")
            place = _proof(t, "Placement")
            ruin = {p["_word"] for p in place if p.get("where") == "ruin"}
            want = {m["wrecked"] for m in ms.values() if m.get("on") == "true"} | {COMPONENT}
            if want - ruin:
                raise ExpectationFailed("start: the placement list lacks %s" % sorted(want - ruin))
            START_MARK(t, "sc_ruin_holds_wrecks")
    with t.component("ruins_hold_wrecks_and_a_component"):
        if _live(t):
            maps = []
            for _ in range(RUIN_MAPS):
                _gen_map(t, ruin=True)
                maps.append(_mod_things(t, st["ms"]))
            allrows = [r for m in maps for r in m]
            outside = [r for r in allrows if not r["ruin"]]
            kinds = {r["def"] for r in allrows if r["def"] != COMPONENT}
            bad_level = [r for r in allrows if r["def"] != COMPONENT and r["level"] != "Wrecked"]
            comps = [r for r in allrows if r["def"] == COMPONENT]
            flooded = [len(m) for m in maps if len(m) > FLOOD]
            t._current.detail = "per map %s; kinds %s" % ([len(m) for m in maps], sorted(kinds))
            if outside or len(kinds) < 2 or bad_level or not comps or flooded:
                raise ExpectationFailed("outside rooms %d, kinds %d, not Wrecked %d, components %d, flooded maps %s" % (
                    len(outside), len(kinds), len(bad_level), len(comps), flooded))
    with t.component("control_ruin_placement_off"):
        if _live(t):
            try:
                _set_switch(t, RUIN_SWITCH, False)
                found = 0
                for _ in range(RUIN_MAPS):
                    _gen_map(t, ruin=True)
                    found += len(_mod_things(t, st["ms"]))
                if found:
                    raise ExpectationFailed("ruin placement off, still %d of this mod's things on the ruin maps" % found)
            finally:
                _set_switch(t, RUIN_SWITCH, True)


@suite.chain("scene_rare_wreck_ordinary_map")
def scene_rare_wreck_ordinary_map(t):
    """sc_rare_wreck_ordinary_map (wreck_is_found), kind B, X of Y = ORDINARY_WANT of ORDINARY_MAPS written before the first
    run: some ordinary maps hold exactly one wreck among rubble at the Wrecked level, many hold none, none holds several, none
    holds a component. Control: ordinary placement off, no map holds a wreck."""
    st = {}
    with t.component("start_rare_wreck_ordinary_map"):
        if _live(t):
            st["ms"] = _start(t, "sc_rare_wreck_ordinary_map")
            START_MARK(t, "sc_rare_wreck_ordinary_map")
    with t.component("one_wreck_now_and_then"):
        if _live(t):
            counts, several, comps, ruined = [], 0, 0, 0
            for _ in range(ORDINARY_MAPS):
                _gen_map(t, ruin=False)
                rows = _mod_things(t, st["ms"])
                if any(r["ruin"] for r in rows):
                    ruined += 1          # the start: a map kind with no ruin room, asserted after generation
                    continue
                wrecks = [r for r in rows if r["def"] != COMPONENT]
                comps += len(rows) - len(wrecks)
                counts.append(len(wrecks))
                if len(wrecks) > 1:
                    several += 1
                for w in wrecks:
                    if w["level"] != "Wrecked" or not _count(t, RUBBLE, "%d,%d,9,9" % (int(w["x"]) - 4, int(w["z"]) - 4)):
                        raise ExpectationFailed("a wreck on an ordinary map is not a Wrecked machine among rubble: %r" % w)
                    reach = ((t.bridge_call("jawa/reach_edge", cells="%s,%s" % (w["x"], w["z"]), mode="PassDoors") or {})
                             .get("cells") or [{}])[0]
                    if reach.get("canReachEdge") is not True:
                        raise ExpectationFailed("a wreck a colonist cannot walk to from the edge without mining: %r %r" % (w, reach))
                    if not any("uninstall" in g[0].lower() and not g[1] for g in _gizmos(t, w["id"])):
                        raise ExpectationFailed("the wreck at (%s,%s) offers no Uninstall order" % (w["x"], w["z"]))
            with_one = counts.count(1)
            t._current.detail = "wrecks per map %s (maps with a ruin room left out: %d)" % (counts, ruined)
            if several or comps:
                raise ExpectationFailed("maps with several wrecks %d, components on ordinary maps %d" % (several, comps))
            if with_one < ORDINARY_WANT or with_one == len(counts):
                raise ExpectationFailed("%d of %d maps held one wreck; want at least %d and not all" % (with_one, len(counts), ORDINARY_WANT))
    with t.component("control_ordinary_placement_off"):
        if _live(t):
            try:
                _set_switch(t, ORDINARY_SWITCH, False)
                found = 0
                for _ in range(ORDINARY_MAPS):
                    _gen_map(t, ruin=False)
                    found += len([r for r in _mod_things(t, st["ms"]) if not r["ruin"]])
                if found:
                    raise ExpectationFailed("ordinary placement off, still %d wrecks on ordinary maps" % found)
            finally:
                _set_switch(t, ORDINARY_SWITCH, True)


# --------------------------------------------------------------------------- showcase 1: the smelter comes home

@suite.chain("scene_carry_wreck_home")
def scene_carry_wreck_home(t):
    """sc_carry_wreck_home (wreck_comes_home): a colonist uninstalls, hauls and installs a wrecked smelter and a wrecked power cell
    on a plain floor twenty cells away by his own jobs; every wreck def has a carried form; each wreck's mass is recorded, not
    judged. Control: the same Uninstall order on a wall is refused."""
    st = {}
    x, z = t.anchor
    with t.component("start_carry_wreck_home"):
        if _live(t):
            ms = st["ms"] = _start(t, "sc_carry_wreck_home")
            st["w"] = [_build(t, _line(t, ms, "smelter")["wrecked"], x - 6, z, faction="none"),
                       _build(t, _line(t, ms, "powercell")["wrecked"], x - 1, z, faction="none")]
            st["wall"] = _build(t, WALL, x + 3, z)
            _floor(t, PLAIN_FLOOR, x + 14, z - 3, 8, 7)
            st["pid"] = _colonist(t, x, z - 4)
            terr = (t.bridge_call("jawa/get_terrain_batch", rects="%d,%d,1,1" % (x + 16, z)) or {})
            if FACTORY_FLOOR in str(terr):
                raise ExpectationFailed("start: the install cell has factory floor: %s" % str(terr)[:120])
            START_MARK(t, "sc_carry_wreck_home")
    with t.component("colonist_carries_each_wreck_home"):
        if _live(t):
            seen = set()
            for i, wid in enumerate(st["w"]):
                _designate(t, "Uninstall", wid)
                carried = None
                for _ in range(40):
                    t.wait_ticks(250)
                    seen.add(_job(t, st["pid"]).split("(")[0][:40])
                    rows = (t.bridge_call("jawa/list_things", defName="MinifiedThing", limit=50) or {}).get("things") or []
                    carried = next((r for r in rows if r.get("inner") == wid or str(wid) in str(r)), rows[0] if rows else None)
                    if carried:
                        break
                if not carried:
                    raise ExpectationFailed("wreck %s was not uninstalled into a carried form (jobs seen %s)" % (wid, sorted(seen)))
                r = t.bridge_call("jawa/install_blueprint", thing=carried["id"], x=x + 15 + 4 * i, z=z, rot="south")
                if not (r or {}).get("success"):
                    raise ExpectationFailed("install blueprint refused for %s: %s" % (carried["id"], str(r)[:200]))
                _wait_days(t, 0.5)
                lvl = (t.bridge_call("jawa/list_things", rect="%d,%d,5,5" % (x + 13 + 4 * i, z - 2), limit=20) or {}).get("things") or []
                if not any(_level(t, th["id"]) == "Wrecked" for th in lvl if th.get("id")):
                    raise ExpectationFailed("no Wrecked machine stands at the far cell after the install (jobs %s)" % sorted(seen))
            t._current.detail = "jobs seen: %s" % sorted(seen)
    with t.component("every_wreck_has_a_carried_form"):
        if _live(t):
            no_form, masses = [], {}
            for key, m in sorted(st["ms"].items()):
                v, raw = _def_field(t, "ThingDef/" + m["wrecked"], "minifiedDef")
                if not v or v == "(null)":
                    no_form.append(m["wrecked"])
                mass, _ = _def_field(t, "ThingDef/" + m["wrecked"], "statBases")
                masses[key] = re.findall(r"Mass[^0-9]*([0-9.]+)", str(mass))[:1]
            t._current.detail = "mass of each wreck (recorded, not judged): %s" % masses
            if no_form:
                raise ExpectationFailed("wreck defs with no carried form: %s" % no_form)
    with t.component("control_wall_uninstall_refused"):
        if _live(t):
            _designate(t, "Uninstall", st["wall"])
            r = _designate(t, "Uninstall", st["wall"])
            if r.get("added") or not r.get("skippedWrongType"):
                raise ExpectationFailed("a wall took an Uninstall designation, or the refusal was not seen: %s" % str(r)[:200])


def _staged_wreck(t, key, x, z, rot="south", terrain=None, faction="player"):
    ms = t._wm_ms
    if terrain:
        _floor(t, terrain, x - 3, z - 3, 7, 7)
    return _build(t, _line(t, ms, key)["wrecked"], x, z, rot=rot, faction=faction)


def _finish_first(t, key, step="1"):
    """Staging only (before START_MARK): finish the line's project of `step` as a save made by play would hold it."""
    for s, p in _projects(t, key):
        if s == step:
            t.bridge_call("jawa/research_finish_project", project=p, doCompletionDialog=False, doCompletionLetter=False)


def _study_stage(t, sid):
    """The start of the two first-study scenes: a wrecked smelter at home, a wrecked autoloom whose study is never turned on (the
    control), a second wrecked smelter, a bench, a researcher and a colonist who cannot research; nothing studied or finished."""
    x, z = t.anchor
    st = {}
    t._wm_ms = ms = _start(t, sid)
    sm = _line(t, ms, "smelter")
    st["w"] = _staged_wreck(t, "smelter", x - 8, z)
    st["ctl"] = _staged_wreck(t, "autoloom", x + 8, z)
    st["w2"] = _staged_wreck(t, "smelter", x - 8, z + 12)
    _build(t, BENCH, x, z + 6)
    st["r"], st["nr"] = _colonist(t, x, z - 4), _colonist(t, x + 2, z - 4, research=False)
    p = [pp for s_, pp in _projects(t, "smelter") if s_ == "1"]
    pc = [pp for s_, pp in _projects(t, "autoloom") if s_ == "1"]
    if not p or not pc:
        raise ExpectationFailed("start: no first project for the smelter or the autoloom")
    st["p"], st["pc"] = p[0], pc[0]
    rec = _study(t, sm["wrecked"])
    if _researched(t, st["p"]) or rec.get("status") not in ("no_record", "partial") or (rec.get("timesDone") or 0):
        raise ExpectationFailed("start: project finished or a study recorded: %s" % str(rec)[:200])
    return st


def _study_flow(t, st, second_needs_no_study=True):
    """The action, expect and control of the first-study scenes."""
    with t.component("project_locked_names_the_wreck"):
        if _live(t):
            r = _research_row(t, st["p"])
            if r.get("analyzedThingsRequirementsMet") is not False:
                raise ExpectationFailed("the first project is not locked by the study: %s" % str(r)[:200])
    with t.component("researcher_studies_by_himself"):
        if _live(t):
            study = [g for g in _gizmos(t, st["w"]) if "study" in g[0].lower()]
            if not study:
                raise ExpectationFailed("the wreck shows no study toggle")
            t.bridge_call("rimworld/execute_gizmo", gizmoId=study[0][3])
            jobs, steps, nr_jobs, rec = [], [], [], {}
            for _ in range(STUDY_DAYS * 4):
                t.wait_ticks(15000)
                jobs.append(_job(t, st["r"])[:60])
                nr_jobs.append(_job(t, st["nr"])[:60])
                rec = _study(t, _line(t, t._wm_ms, "smelter")["wrecked"])
                steps.append(rec.get("timesDone"))
                if rec.get("status") == "complete":
                    break
            t._current.detail = "study steps %s" % steps
            if rec.get("status") != "complete":
                raise ExpectationFailed("the study did not complete in %d days: steps %s, jobs %s" % (STUDY_DAYS, steps, jobs[-6:]))
            if any("Study" in j or "Analy" in j for j in nr_jobs):
                raise ExpectationFailed("the colonist who cannot research studied: %s" % nr_jobs)
            if len([s_ for s_ in steps if s_]) < 2 or sorted(s_ or 0 for s_ in steps) != [s_ or 0 for s_ in steps]:
                raise ExpectationFailed("the study did not rise over days: %s" % steps)
    with t.component("project_opens_and_is_finished_at_bench"):
        if _live(t):
            r = _research_row(t, st["p"])
            if not r.get("analyzedThingsRequirementsMet"):
                raise ExpectationFailed("study complete but the project is still locked: %s" % str(r)[:200])
            for _ in range(STUDY_DAYS * 4):
                t.wait_ticks(15000)
                if _researched(t, st["p"]):
                    break
            if not _researched(t, st["p"]):
                raise ExpectationFailed("the researcher did not finish the first project at the bench in %d days" % STUDY_DAYS)
            if second_needs_no_study:
                present, ok, reason, _ = _repair_order(t, st["w2"])
                if any("study" in g[0].lower() and not g[1] for g in _gizmos(t, st["w2"])) and not ok:
                    raise ExpectationFailed("a second wrecked smelter still asks for study: %s" % reason)
    with t.component("control_study_never_on"):
        if _live(t):
            if _researched(t, st["pc"]) or _research_row(t, st["pc"]).get("analyzedThingsRequirementsMet"):
                raise ExpectationFailed("the autoloom's first project opened with study never turned on (time or bench work alone)")


@suite.chain("scene_study_opens_first_project")
def scene_study_opens_first_project(t):
    """sc_study_opens_first_project (study_opens_research): with study turned on once, a researcher studies the wrecked smelter by
    himself over days, the colonist who cannot research never does, the study's progress rises on the wreck, the first project
    opens and is finished at the bench, and a second wreck needs no study. Control: study never turned on (the autoloom), a
    researcher at the bench for the same days: that project stays locked."""
    st = {}
    with t.component("start_study_opens_first_project"):
        if _live(t):
            st.update(_study_stage(t, "sc_study_opens_first_project"))
            kits = [r for r in (t.bridge_call("jawa/list_things", rect=_site(t, 120), limit=3000) or {}).get("things") or []
                    if re.search(r"FieldResearch|ResearchKit", str(r.get("def") or r.get("defName")))]
            if kits:
                raise ExpectationFailed("start: Research Reinvented's field kit lies on the map: %s" % kits[:3])
            START_MARK(t, "sc_study_opens_first_project")
    _study_flow(t, st)


@suite.chain("scene_second_study")
def scene_second_study(t):
    """sc_second_study (study_opens_research): the second project of the power cell is locked until the Kludged cell is studied,
    and the study's progress survives a save and reload. Control: a wrecked cell beside it, study never on for the Kludged one,
    the same days at the bench: the second project stays locked."""
    st = {}
    x, z = t.anchor
    with t.component("start_second_study"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_second_study")
            pc = _line(t, ms, "powercell")
            pr = dict(_projects(t, "powercell"))
            if not pr.get("1") or not pr.get("2"):
                raise ExpectationFailed("start: the power cell has not two projects: %s" % pr)
            st["p1"], st["p2"] = pr["1"], pr["2"]
            if not _researched(t, st["p1"]) or _researched(t, st["p2"]):
                raise ExpectationFailed("start: want the first project finished by play and the second not (a starting save of "
                                        "play is owed; the scene stages none)")
            st["k"] = _build(t, pc["kludged"], x - 4, z)
            st["w"] = _build(t, pc["wrecked"], x + 4, z)
            _build(t, BENCH, x, z + 6)
            st["r"] = _colonist(t, x, z - 4)
            if _research_row(t, st["p2"]).get("analyzedThingsRequirementsMet") is not False:
                raise ExpectationFailed("start: the second project is not locked by study")
            START_MARK(t, "sc_second_study")
    with t.component("control_no_study_keeps_second_locked"):
        if _live(t):
            _wait_days(t, 2)
            if _research_row(t, st["p2"]).get("analyzedThingsRequirementsMet") is not False:
                raise ExpectationFailed("the second project opened with no study of the Kludged cell (first study, wreck, time or bench)")
    with t.component("study_survives_reload"):
        if _live(t):
            study = [g for g in _gizmos(t, st["k"]) if "study" in g[0].lower()]
            if not study:
                raise ExpectationFailed("the Kludged cell shows no study toggle")
            t.bridge_call("rimworld/execute_gizmo", gizmoId=study[0][3])
            kdef = _line(t, t._wm_ms, "powercell")["kludged"]
            before = None
            for _ in range(STUDY_DAYS * 4):
                t.wait_ticks(15000)
                before = _study(t, kdef)
                if (before.get("timesDone") or 0) > 0:
                    break
            if not (before or {}).get("timesDone"):
                raise ExpectationFailed("the Kludged cell's study never started: %s" % str(before)[:200])
            name = "wm_second_study_mid"
            t.bridge_call("rimworld/save_game", saveName=name)
            t.bridge_call("rimworld/load_game_ready", saveName=name, timeoutMs=240000)
            after = _study(t, kdef)
            if after.get("timesDone") != before.get("timesDone"):
                raise ExpectationFailed("study progress %s before the reload, %s after" % (before.get("timesDone"), after.get("timesDone")))
    with t.component("second_project_opens_after_study"):
        if _live(t):
            kdef = _line(t, t._wm_ms, "powercell")["kludged"]
            for _ in range(STUDY_DAYS * 4):
                t.wait_ticks(15000)
                if _study(t, kdef).get("status") == "complete":
                    break
            if not _research_row(t, st["p2"]).get("analyzedThingsRequirementsMet"):
                raise ExpectationFailed("the Kludged cell's study did not open the second project")


def _ground_wreck(t, key, x, z, terrain=FACTORY_FLOOR, rot="south"):
    _floor(t, terrain, x - 3, z - 3, 7, 7)
    return _build(t, _line(t, t._wm_ms, key)["wrecked"], x, z, rot=rot)


@suite.chain("scene_repair_on_machine")
def scene_repair_on_machine(t):
    """sc_repair_on_machine (repair_on_the_machine): the repair is ordered on the wreck, a colonist hauls and works there, the
    wreck stands at its cell at every read, a Kludged smelter facing east stands there at the end, the repair goes on after a
    reload, and the level-changed signal fired once with Wrecked and Kludged. Control: a second wreck with no order stays
    Wrecked; the wrecked autoloom whose project is not finished shows the order unavailable, naming the research."""
    st = {}
    x, z = t.anchor
    with t.component("start_repair_on_machine"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_repair_on_machine")
            _finish_first(t, "smelter")
            st["w"] = _ground_wreck(t, "smelter", x - 8, z, rot="east")
            st["w2"] = _ground_wreck(t, "smelter", x, z)
            st["loom"] = _ground_wreck(t, "autoloom", x + 9, z)
            _items(t, "Steel", x - 8, z - 8, 400)
            _items(t, "ComponentIndustrial", x - 6, z - 8, 20)
            st["pid"] = _colonist(t, x, z - 6)
            st["sig0"] = len([s for s in _proof(t, "SignalLog") if s["_verb"] == "SIGNAL"])
            if _level(t, st["w"]) != "Wrecked" or not any(s == "1" and _researched(t, p) for s, p in _projects(t, "smelter")):
                raise ExpectationFailed("start: the first wreck is not Wrecked or its first project is not finished")
            if any(_researched(t, p) for s, p in _projects(t, "autoloom")):
                raise ExpectationFailed("start: the autoloom's project is finished; the foil needs it locked")
            if st["sig0"]:
                raise ExpectationFailed("start: %d level signals already logged" % st["sig0"])
            START_MARK(t, "sc_repair_on_machine")
    with t.component("order_given_on_the_machine"):
        if _live(t):
            smelter = _line(t, t._wm_ms, "smelter")
            if any(_menu_visible(t, d) for d in _levels_of(smelter) if d):
                raise ExpectationFailed("a level of the smelter is in the build menu: the order is not only on the machine")
            _give_repair(t, st["w"])
    with t.component("wreck_stands_while_repaired_and_after_reload"):
        if _live(t):
            reads, saved = [], False
            for i in range(32):
                t.wait_ticks(2500)
                here = (t.bridge_call("jawa/list_things", rect="%d,%d,3,3" % (x - 9, z - 1), limit=10) or {}).get("things") or []
                lvl = _level(t, st["w"])
                reads.append(lvl)
                if lvl not in ("Wrecked", "Kludged") or not here:
                    raise ExpectationFailed("read %d: the machine is not at its cell (level %r, things %d)" % (i, lvl, len(here)))
                rec = _proof(t, "Repair", st["w"])
                if not saved and rec and rec[0]["_word"] == "working":
                    t.bridge_call("rimworld/save_game", saveName="wm_repair_mid")
                    t.bridge_call("rimworld/load_game_ready", saveName="wm_repair_mid", timeoutMs=240000)
                    saved = True
                if lvl == "Kludged":
                    break
            if reads[-1] != "Kludged" or not saved:
                raise ExpectationFailed("the repair did not end Kludged after a reload mid-work: levels %s, reloaded %s" % (reads, saved))
    with t.component("kludged_faces_east_signal_once"):
        if _live(t):
            row = ((t.bridge_call("jawa/list_things", rect="%d,%d,3,3" % (x - 9, z - 1), limit=10) or {}).get("things") or [{}])[0]
            sigs = [s for s in _proof(t, "SignalLog") if s["_verb"] == "SIGNAL"]
            if str(row.get("rot") or row.get("rotation")) not in ("1", "east", "East"):
                raise ExpectationFailed("the Kludged smelter does not face east: %r" % row)
            if len(sigs) != 1 or sigs[0].get("from") != "Wrecked" or sigs[0].get("to") != "Kludged":
                raise ExpectationFailed("level signals: %r, want one Wrecked->Kludged" % sigs)
    with t.component("control_no_order_and_locked_order"):
        if _live(t):
            if _level(t, st["w2"]) != "Wrecked":
                raise ExpectationFailed("the second wreck, never ordered, is %r" % _level(t, st["w2"]))
            present, ok, reason, _ = _repair_order(t, st["loom"])
            if not present or ok or "research" not in reason.lower():
                raise ExpectationFailed("the autoloom's order: present %s, available %s, reason %r (want unavailable, naming research)"
                                        % (present, ok, reason))


@suite.chain("scene_repair_cancelled")
def scene_repair_cancelled(t):
    """sc_repair_cancelled (repair_on_the_machine): three repairs cancelled before delivery, after part of it and during the work
    each leave the wreck at its cell at Wrecked, every material back on the map, and a new order accepted. Control: a fourth
    repair not cancelled ends Kludged and uses its materials."""
    st = {}
    x, z = t.anchor
    with t.component("start_repair_cancelled"):
        if _live(t):
            t._wm_ms = _start(t, "sc_repair_cancelled")
            _finish_first(t, "smelter")
            st["w"] = [_ground_wreck(t, "smelter", x - 15 + 10 * i, z) for i in range(4)]
            _items(t, "Steel", x, z - 9, 800)
            _items(t, "ComponentIndustrial", x + 2, z - 9, 40)
            _colonist(t, x, z - 6)
            st["mat0"] = (_count(t, "Steel"), _count(t, "ComponentIndustrial"))
            if any(_level(t, w) != "Wrecked" for w in st["w"]):
                raise ExpectationFailed("start: not every wreck is Wrecked")
            START_MARK(t, "sc_repair_cancelled")

    def cancel(wid):
        g = [g for g in _gizmos(t, wid) if "cancel" in g[0].lower()]
        if not g:
            raise ExpectationFailed("no cancel order on %s under repair" % wid)
        t.bridge_call("rimworld/execute_gizmo", gizmoId=g[0][3])

    with t.component("cancel_never_loses_the_machine"):
        if _live(t):
            for w in st["w"]:
                _give_repair(t, w)
            cancel(st["w"][0])
            for want, wid in (("delivered", st["w"][1]), ("working", st["w"][2])):
                for _ in range(60):
                    t.wait_ticks(500)
                    rec = (_proof(t, "Repair", wid) or [{}])[0]
                    if (want == "delivered" and rec.get("delivered")) or rec.get("_word") == want:
                        break
                cancel(wid)
            t.wait_ticks(500)
            lv = [_level(t, w) for w in st["w"][:3]]
            mat = (_count(t, "Steel"), _count(t, "ComponentIndustrial"))
            if lv != ["Wrecked"] * 3:
                raise ExpectationFailed("after the cancels the levels are %s" % lv)
            # the fourth repair is still under way and holds its delivered share: compare what is on the map plus that share
            held = (_proof(t, "Repair", st["w"][3]) or [{}])[0].get("delivered", "")
            t._current.detail = "materials at start %s, after cancels %s, fourth holds %r" % (st["mat0"], mat, held)
            if mat[0] + sum(int(n) for d, n in re.findall(r"(Steel):(\d+)", held)) != st["mat0"][0]:
                raise ExpectationFailed("steel at start %d, after the cancels %d (+%s held by the uncancelled repair)" % (st["mat0"][0], mat[0], held))
            _give_repair(t, st["w"][0])
    with t.component("control_uncancelled_becomes_kludged"):
        if _live(t):
            lvl = _wait_level(t, st["w"][3], "Kludged", 3)
            if lvl != "Kludged":
                raise ExpectationFailed("the fourth, uncancelled repair ended %r: no repair could complete in this scene" % lvl)


def _proc_names(t, tid):
    r = t.bridge_call("jawa/processor_fill", thing=tid, dryRun=True) or {}
    return r.get("processes") or [], r


@suite.chain("scene_levels_do_their_work")
def scene_levels_do_their_work(t):
    """sc_levels_do_their_work (levels_of_function): Wrecked offers nothing and draws no power; Kludged offers a part of the
    smelter's jobs that is not empty; Refurbished offers every job of the Original and is slower; for the drill, Kludged is slower
    than Refurbished, slower than the Original. Control: the Refurbished machine's second run takes the same time, and the
    Original's def is unchanged."""
    st = {}
    x, z = t.anchor
    with t.component("start_levels_do_their_work"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_levels_do_their_work")
            _floor(t, FACTORY_FLOOR, x - 22, z - 14, 44, 28)
            st["ids"] = {}
            for row, key in enumerate(("smelter", "drill")):
                m = _line(t, ms, key)
                for col, lvl in enumerate(("wrecked", "kludged", "refurbished", "original")):
                    d = m.get(lvl) if lvl != "original" else (m.get("original") or ORIGINAL[key])
                    st["ids"][(key, lvl)] = _build(t, d, x - 18 + col * 10, z - 8 + row * 12)
            _build(t, "VanometricPowerCell", x + 20, z)   # one powered net for all eight (the cell is the base game's)
            st["origdef"], _ = _def_field(t, "ThingDef/" + ORIGINAL["smelter"], "comps")
            for k, tid in st["ids"].items():
                if k[1] != "wrecked":
                    pn = t.bridge_call("jawa/power_net", thing=tid) or {}
                    if not pn.get("powerOn", pn.get("isPowered", True)):
                        raise ExpectationFailed("start: %s is not powered: %s" % (k, str(pn)[:120]))
            START_MARK(t, "sc_levels_do_their_work")
    with t.component("wrecked_offers_nothing_draws_nothing"):
        if _live(t):
            for key in ("smelter", "drill"):
                procs, raw = _proc_names(t, st["ids"][(key, "wrecked")])
                pn = t.bridge_call("jawa/power_net", thing=st["ids"][(key, "wrecked")]) or {}
                if procs or pn.get("isPowerTrader"):
                    raise ExpectationFailed("the Wrecked %s offers %s or takes power (%s)" % (key, procs, str(pn)[:80]))
    with t.component("kludged_part_refurbished_whole"):
        if _live(t):
            k, _ = _proc_names(t, st["ids"][("smelter", "kludged")])
            r, _ = _proc_names(t, st["ids"][("smelter", "refurbished")])
            o, _ = _proc_names(t, st["ids"][("smelter", "original")])
            st["procs"] = (k, r, o)
            if not k or not set(k) < set(o) or set(r) != set(o):
                raise ExpectationFailed("processes: Kludged %s, Refurbished %s, Original %s" % (k, r, o))

    def run_ticks(tid, proc):
        f = t.bridge_call("jawa/processor_fill", thing=tid, process=proc, add=True) or {}
        if not f.get("allFull"):
            raise ExpectationFailed("the inputs of %s could not be placed in %s: %s" % (proc, tid, str(f)[:200]))
        for i in range(240):              # the clock is counted by the scene's own waits, 250 ticks a read
            t.wait_ticks(250)
            again = t.bridge_call("jawa/processor_fill", thing=tid, process=proc, dryRun=True) or {}
            if not again.get("allFull"):
                return (i + 1) * 250
        return None

    with t.component("slower_by_level"):
        if _live(t):
            k, r, o = st["procs"]
            shared = [p for p in k if p in o]
            if not shared:
                raise ExpectationFailed("no product the Kludged smelter and the Original share")
            p = shared[0]
            st["p"] = p
            times = {lvl: run_ticks(st["ids"][("smelter", lvl)], p) for lvl in ("refurbished", "original")}
            dk, _ = _proc_names(t, st["ids"][("drill", "kludged")])
            dp = dk[0] if dk else None
            dtimes = {lvl: run_ticks(st["ids"][("drill", lvl)], dp) for lvl in ("kludged", "refurbished", "original")} if dp else {}
            st["times"] = times
            t._current.detail = "smelter %s %s; drill %s %s" % (p, times, dp, dtimes)
            if None in list(times.values()) + list(dtimes.values()) or not dtimes:
                raise ExpectationFailed("a run did not finish: smelter %s, drill %s" % (times, dtimes))
            if not times["refurbished"] > times["original"] or not dtimes["kludged"] > dtimes["refurbished"] > dtimes["original"]:
                raise ExpectationFailed("the levels are not slower in order: smelter %s, drill %s" % (times, dtimes))
    with t.component("control_second_run_same_original_unchanged"):
        if _live(t):
            again = run_ticks(st["ids"][("smelter", "refurbished")], st["p"])
            first = st["times"]["refurbished"]
            if again is None or abs(again - first) > 250:     # "the same time", to the one read step of run_ticks
                raise ExpectationFailed("the Refurbished smelter's two runs: %s and %s ticks" % (first, again))
            now, _ = _def_field(t, "ThingDef/" + ORIGINAL["smelter"], "comps")
            if str(now) != str(st["origdef"]):
                raise ExpectationFailed("the Original smelter's def changed during the scene")


def _level_reading(t, key, tid):
    """The applied work of one machine: a power cell's output (W), else its first process's ticks from its def (read live)."""
    pn = t.bridge_call("jawa/power_net", thing=tid) or {}
    if key == "powercell":
        return pn.get("energyOutputPerTick")
    rows = _proof(t, "Speed", tid)
    return float(rows[0]["_word"]) if rows else None


@suite.chain("scene_levels_under_settings")
def scene_levels_under_settings(t):
    """sc_levels_under_settings (levels_of_function): at the lowest and the highest value of each level setting the order holds
    (Wrecked nothing, Kludged below Refurbished below the Original), and the Kludged and Refurbished readings move below and above
    their shipped readings. Control: the shipped readings read first and again after the settings are put back are equal."""
    st = {}
    x, z = t.anchor
    fields = ("kludgedRatio", "refurbishedRatio")
    with t.component("start_levels_under_settings"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_levels_under_settings")
            _floor(t, FACTORY_FLOOR, x - 22, z - 14, 44, 28)
            st["ids"] = {}
            for row, key in enumerate(("smelter", "powercell")):
                m = _line(t, ms, key)
                for col, lvl in enumerate(("wrecked", "kludged", "refurbished", "original")):
                    d = m.get(lvl) if lvl != "original" else (m.get("original") or ORIGINAL[key])
                    st["ids"][(key, lvl)] = _build(t, d, x - 18 + col * 10, z - 8 + row * 12)
            st["shipped"] = {k: _level_reading(t, k[0], v) for k, v in st["ids"].items()}
            st["old"] = {f: _setting(t, "get", f).get("value") for f in fields}
            START_MARK(t, "sc_levels_under_settings")

    def order_holds(read, key):
        w, k, r, o = (abs(read[(key, lvl)] or 0) for lvl in ("wrecked", "kludged", "refurbished", "original"))
        return w == 0 and k < r < o

    with t.component("order_holds_at_every_value"):
        if _live(t):
            bad = []
            try:
                for f in fields:
                    for v in ("0.01", "0.99"):
                        _setting(t, "set", f, v)
                        _apply(t)
                        read = {k: _level_reading(t, k[0], tid) for k, tid in st["ids"].items()}
                        for key in ("smelter", "powercell"):
                            if not order_holds(read, key):
                                bad.append("%s=%s %s: %s" % (f, v, key, [read[(key, l)] for l in ("wrecked", "kludged", "refurbished", "original")]))
                        lvl = "kludged" if f == "kludgedRatio" else "refurbished"
                        for key in ("smelter", "powercell"):
                            a, s = abs(read[(key, lvl)] or 0), abs(st["shipped"][(key, lvl)] or 0)
                            if (v == "0.01" and not a < s) or (v == "0.99" and not a > s):
                                bad.append("%s=%s: %s %s reads %s against shipped %s" % (f, v, key, lvl, a, s))
            finally:
                for f in fields:
                    _setting(t, "set", f, st["old"][f])
                _apply(t)
            if bad:
                raise ExpectationFailed("; ".join(bad[:6]))
    with t.component("control_shipped_reads_equal_after_restore"):
        if _live(t):
            back = {k: _level_reading(t, k[0], v) for k, v in st["ids"].items()}
            diff = {str(k): (st["shipped"][k], back[k]) for k in back if back[k] != st["shipped"][k]}
            if diff:
                raise ExpectationFailed("settings put back, readings differ: %s" % diff)


@suite.chain("scene_forge_plasteel")
def scene_forge_plasteel(t):
    """sc_forge_plasteel (levels_of_function): with every project finished, the Kludged forge offers obsidian and no plasteel or
    gravlite; the Refurbished forge offers plasteel and gravlite and makes plasteel; the old forge projects and settings are gone.
    Control: the factory mod's own forge, with the forge's line off, offers plasteel as the factory mod has it.
    This scene replaces the old chain alloy_forge_gated when the forge is onboarded (plan.md)."""
    st = {}
    x, z = t.anchor
    with t.component("start_forge_plasteel"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_forge_plasteel")
            t.bridge_call("jawa/research_bulk", mode="finish_all")
            m = _line(t, ms, "alloyforge")
            _floor(t, FACTORY_FLOOR, x - 16, z - 6, 32, 12)
            st["ids"] = {lvl: _build(t, m[lvl], x - 12 + 9 * i, z) for i, lvl in enumerate(("wrecked", "kludged", "refurbished"))}
            _build(t, "VanometricPowerCell", x + 16, z)
            if not all(_researched(t, p) for p in FACTORY_RESEARCH):
                raise ExpectationFailed("start: not every project finished")
            START_MARK(t, "sc_forge_plasteel")
    with t.component("kludged_forge_no_plasteel"):
        if _live(t):
            k, _ = _proc_names(t, st["ids"]["kludged"])
            st["k"] = k
            if not any("Obsidian" in p for p in k) or any("Plasteel" in p or "Gravlite" in p for p in k):
                raise ExpectationFailed("Kludged forge processes: %s" % k)
    with t.component("refurbished_forge_makes_plasteel"):
        if _live(t):
            r, _ = _proc_names(t, st["ids"]["refurbished"])
            pl = [p for p in r if "Plasteel" in p]
            if not pl or not any("Gravlite" in p for p in r):
                raise ExpectationFailed("Refurbished forge processes: %s" % r)
            before = _count(t, "Plasteel")
            f = t.bridge_call("jawa/processor_fill", thing=st["ids"]["refurbished"], process=pl[0], add=True) or {}
            if not f.get("allFull"):
                raise ExpectationFailed("plasteel's inputs could not be placed: %s" % str(f)[:200])
            _wait_days(t, 1)
            if _count(t, "Plasteel") <= before:
                raise ExpectationFailed("the Refurbished forge made no plasteel in a day")
    with t.component("old_forge_projects_and_settings_gone"):
        if _live(t):
            left = [p for p in OLD_FORGE_PROJECTS if (_research_row(t, p) or {}).get("success")]
            left += [s for s in OLD_FORGE_SETTINGS if _setting(t, "get", s).get("value") is not None]
            if left:
                raise ExpectationFailed("old forge names still in the game: %s" % left)
    with t.component("control_line_off_original_has_plasteel"):
        if _live(t):
            try:
                _set_line(t, "alloyforge", False)
                oid = _build(t, ORIGINAL["alloyforge"], x, z + 10)
                o, _ = _proc_names(t, oid)
                if not any("Plasteel" in p for p in o):
                    raise ExpectationFailed("the factory mod's own forge offers no plasteel (another cause): %s" % o)
            finally:
                _set_line(t, "alloyforge", True)


# --------------------------------------------------------------------------- showcase 3: relics in the house

@suite.chain("scene_cell_and_emanator")
def scene_cell_and_emanator(t):
    """sc_cell_and_emanator (levels_of_function): the wrecked cell gives no power and its lamps are dark; the Kludged cell gives
    less than the Refurbished one and lights fewer of the same row of lamps; both give less than the base game's cell. No thought
    beside the wrecked emanator; Kludged weaker than Refurbished, both weaker than the base game's. Control: a fifth room with no
    emanator and a fifth net with lamps and no cell give no thought and no light."""
    st = {}
    x, z = t.anchor
    with t.component("start_cell_and_emanator"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_cell_and_emanator")
            pc, em = _line(t, ms, "powercell"), _line(t, ms, "emanator")
            cells = [pc["wrecked"], pc["kludged"], pc["refurbished"], ORIGINAL["powercell"], None]
            ems = [em["wrecked"], em["kludged"], em["refurbished"], ORIGINAL["emanator"], None]
            st["cells"], st["lamps"], st["ems"], st["pawns"] = [], [], [], []
            for i, d in enumerate(cells):
                cx, cz = x - 30 + 13 * i, z - 12
                st["cells"].append(_build(t, d, cx, cz) if d else None)
                _many(t, [(CONDUIT, cx + 1 + k, cz) for k in range(LAMPS_PER_NET + 1)])
                _many(t, [(LAMP, cx + 1 + k, cz + 1) for k in range(LAMPS_PER_NET)])
                lamps = (t.bridge_call("jawa/list_things", defName=LAMP, rect="%d,%d,%d,1" % (cx + 1, cz + 1, LAMPS_PER_NET)) or {}).get("things") or []
                st["lamps"].append([l["id"] for l in lamps])
            for i, d in enumerate(ems):
                cx = x - 30 + 13 * i
                ring = [(WALL, wx, wz) for wx in range(cx - 4, cx + 5) for wz in (z + 2, z + 10)]
                ring += [(WALL, wx, wz) for wz in range(z + 3, z + 10) for wx in (cx - 4, cx + 4)]
                _many(t, ring)
                st["ems"].append(_build(t, d, cx, z + 6) if d else None)
                st["pawns"].append(_colonist(t, cx + 2, z + 4))
            nets = [str((t.bridge_call("jawa/power_net", thing=l[0]) or {}).get("netId")) if l else None for l in st["lamps"]]
            if None in nets or len(set(nets)) != len(nets) or any(len(l) != LAMPS_PER_NET for l in st["lamps"]):
                raise ExpectationFailed("start: lamp rows %s, nets %s (want %d lamps on each of 5 nets apart)"
                                        % ([len(l) for l in st["lamps"]], nets, LAMPS_PER_NET))
            START_MARK(t, "sc_cell_and_emanator")
    with t.component("cells_light_in_order"):
        if _live(t):
            t.wait_ticks(500)
            out = [abs((t.bridge_call("jawa/power_net", thing=c) or {}).get("energyOutputPerTick") or 0) if c else 0 for c in st["cells"]]
            lit = [sum(1 for l in ls if (t.bridge_call("jawa/power_net", thing=l) or {}).get("powerOn")) for ls in st["lamps"]]
            st["lit"] = lit
            t._current.detail = "output %s lamps lit %s of %d" % (out, lit, LAMPS_PER_NET)
            if out[0] or lit[0] or not out[1] < out[2] < out[3] or not lit[1] < lit[2] or lit[1] >= LAMPS_PER_NET:
                raise ExpectationFailed("cells: output %s, lamps lit %s of %d" % (out, lit, LAMPS_PER_NET))
    with t.component("emanators_calm_in_order"):
        if _live(t):
            _wait_days(t, 0.25)
            mood = []
            for p in st["pawns"]:
                th = t.bridge_call("jawa/pawn_thoughts", pawn=p) or {}
                mood.append(sum(float(x_.get("moodOffset") or 0) for x_ in th.get("thoughts") or []
                                if "Emanator" in str(x_.get("def")) or "Soothe" in str(x_.get("def"))))
            st["mood"] = mood
            t._current.detail = "emanator mood %s" % mood
            if mood[0] or not 0 < mood[1] < mood[2] < mood[3]:
                raise ExpectationFailed("emanator thoughts by level: %s" % mood)
    with t.component("control_empty_room_and_net"):
        if _live(t):
            if st["mood"][4] or st["lit"][4]:
                raise ExpectationFailed("no emanator gave a thought %s, or no cell lit %d lamps" % (st["mood"][4], st["lit"][4]))


@suite.chain("scene_component_gate")
def scene_component_gate(t):
    """sc_component_gate (last_repair_needs_component, repair_on_the_machine, only_by_repair): with no Ancient Component the
    Kludged smelter's last order is unavailable and names it; a delivered component comes back when the order is cancelled; given
    again, the smelter stays at its cell at every read with no frame or blueprint while a colonist works on it, ends Refurbished at
    the same cell and facing, and no component is left; the Refurbished smelter offers no further repair, with every project
    finished. Control: the power cell's order with a component in stock names the research, and the gizmo read that finds no
    order on the Refurbished smelter found one on the Kludged smelter."""
    st = {}
    x, z = t.anchor
    with t.component("start_component_gate"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_component_gate")
            for s_ in ("1", "2"):
                _finish_first(t, "smelter", s_)
            _finish_first(t, "powercell", "1")
            _floor(t, FACTORY_FLOOR, x - 10, z - 4, 9, 9)
            st["k"] = _build(t, _line(t, ms, "smelter")["kludged"], x - 6, z, rot="east")
            st["cell"] = _build(t, _line(t, ms, "powercell")["kludged"], x + 8, z)
            _items(t, "Steel", x, z - 8, 600)
            _items(t, "ComponentIndustrial", x + 2, z - 8, 40)
            _items(t, "Plasteel", x + 4, z - 8, 200)
            st["pid"] = _colonist(t, x, z - 6)
            if _count(t, COMPONENT):
                raise ExpectationFailed("start: an Ancient Component is on the map")
            if _level(t, st["k"]) != "Kludged":
                raise ExpectationFailed("start: the smelter is not Kludged")
            START_MARK(t, "sc_component_gate")
    with t.component("no_component_order_names_it"):
        if _live(t):
            present, ok, reason, _ = _repair_order(t, st["k"])
            st["kludged_order_seen"] = present
            if not present or ok or "component" not in reason.lower():
                raise ExpectationFailed("with no component: present %s, available %s, reason %r" % (present, ok, reason))
    with t.component("delivered_component_comes_back_on_cancel"):
        if _live(t):
            _items(t, COMPONENT, x + 6, z - 8, 1)
            _give_repair(t, st["k"])
            for _ in range(60):
                t.wait_ticks(500)
                if COMPONENT in str((_proof(t, "Repair", st["k"]) or [{}])[0].get("delivered")):
                    break
            g = [g_ for g_ in _gizmos(t, st["k"]) if "cancel" in g_[0].lower()]
            if not g:
                raise ExpectationFailed("no cancel order on the smelter under repair")
            t.bridge_call("rimworld/execute_gizmo", gizmoId=g[0][3])
            t.wait_ticks(500)
            if _level(t, st["k"]) != "Kludged" or _count(t, COMPONENT) != 1:
                raise ExpectationFailed("after the cancel: level %r, components on the map %d (want Kludged, 1)"
                                        % (_level(t, st["k"]), _count(t, COMPONENT)))
    with t.component("repair_on_the_machine_to_refurbished"):
        if _live(t):
            _give_repair(t, st["k"])
            cell = "%d,%d,3,3" % (x - 7, z - 1)
            reads = []
            for i in range(40):
                t.wait_ticks(2500)
                here = (t.bridge_call("jawa/list_things", rect=cell, limit=20) or {}).get("things") or []
                defs = [str(r_.get("def") or r_.get("defName") or "") for r_ in here]
                if any(d.startswith(("Frame_", "Blueprint_")) for d in defs):
                    raise ExpectationFailed("read %d: a frame or blueprint stands on the smelter's cell: %s" % (i, defs))
                lvl = _level(t, st["k"])
                reads.append((lvl, _job(t, st["pid"])[:30]))
                if lvl not in ("Kludged", "Refurbished") or not here:
                    raise ExpectationFailed("read %d: the smelter is not at its cell (level %r)" % (i, lvl))
                if lvl == "Refurbished":
                    break
            row = (here or [{}])[0]
            t._current.detail = "reads %s" % reads[-6:]
            if reads[-1][0] != "Refurbished" or str(row.get("rot") or row.get("rotation")) not in ("1", "east", "East") or _count(t, COMPONENT):
                raise ExpectationFailed("ended %r facing %r, %d components left" % (reads[-1][0], row.get("rot"), _count(t, COMPONENT)))
    with t.component("refurbished_offers_no_further_repair"):
        if _live(t):
            t.bridge_call("jawa/research_bulk", mode="finish_all")
            present, ok, reason, _ = _repair_order(t, st["k"])
            if present:
                raise ExpectationFailed("the Refurbished smelter still offers a repair order (%s, %r)" % (ok, reason))
    with t.component("control_cell_names_research_and_read_can_see"):
        if _live(t):
            if not st.get("kludged_order_seen"):
                raise ExpectationFailed("the gizmo read never saw the Kludged smelter's order: 'no further repair' proves nothing")
            present, ok, reason, _ = _repair_order(t, st["cell"])
            if not present or ok or "research" not in reason.lower():
                raise ExpectationFailed("the cell's last order: present %s, available %s, reason %r (want research)" % (present, ok, reason))


# --------------------------------------------------------------------------- telling the levels apart

@suite.chain("scene_three_looks_rows")
def scene_three_looks_rows(t):
    """sc_three_looks_rows (levels_told_apart), owner_review: rows of each machine's three levels in a shuffled, recorded order,
    one row per facing of a machine that turns, beside the base game's rubble, captured at play and near zoom with labels off.
    A fresh reader with the art judge's brief names each level (the reading is the judge's, recorded with the captures).
    Control: one planted row where Kludged is the Wrecked picture in a lighter shade; the reader must call it not told apart.
    The script captures and writes the key; it never judges its own pictures."""
    import random
    st = {}
    x, z = t.anchor
    with t.component("start_three_looks_rows"):
        if _live(t):
            ms = _start(t, "sc_three_looks_rows")
            tex = _proof(t, "TextureIds")
            if not tex:
                raise ExpectationFailed("start: the art of the build under test is not identified (TextureIds)")
            t.bridge_call("jawa/weather_set", weather="Clear")
            hour = (t.bridge_call("jawa/time_clock") or {}).get("hour")
            if hour is None or not 8 <= int(hour) <= 16:
                raise ExpectationFailed("start: not daylight (hour %r)" % hour)
            rng = random.Random(20261127)
            st["key"] = []
            for r, (k, m) in enumerate(sorted(ms.items())):
                order = ["wrecked", "kludged", "refurbished"]
                rng.shuffle(order)
                for c, lvl in enumerate(order):
                    _build(t, m[lvl], x - 30 + c * 8, z - 30 + r * 6)
                st["key"].append({"line": k, "order": order, "row": r})
            _items(t, SLAG, x + 2, z - 32, 3)
            _items(t, RUBBLE, x + 4, z - 32, 1)
            START_MARK(t, "sc_three_looks_rows")
    with t.component("rows_captured_for_the_reader"):
        if _live(t):
            t.bridge_call("jawa/screenshot_mode", enabled=True)
            for row in st["key"]:
                t.screenshot(name="wm_rows_%s" % row["line"], rect="%d,%d,24,5" % (x - 31, z - 31 + row["row"] * 6))
            t._current.detail = "key (owner_review; the reader names each level against it): %s" % st["key"]
    with t.component("control_planted_row_for_the_reader"):
        if _live(t):
            planted = _proof(t, "PlantLighterWrecked", st["key"][0]["line"]) if st.get("key") else []
            if not planted:
                raise ExpectationFailed("the planted row could not be made")
            t.screenshot(name="wm_rows_planted", rect="%d,%d,24,5" % (x - 31, z - 31))


@suite.chain("scene_marks_agree")
def scene_marks_agree(t):
    """sc_marks_agree (levels_told_apart): a powered Refurbished smelter and emanator show no no-power mark and read powered; a
    Kludged smelter broken down shows the breakdown mark and says so; the power cell shows no power mark. Control: the same
    smelter with its net cut shows the no-power mark and reads no power."""
    st = {}
    x, z = t.anchor
    with t.component("start_marks_agree"):
        if _live(t):
            ms = _start(t, "sc_marks_agree")
            _floor(t, FACTORY_FLOOR, x - 14, z - 6, 28, 12)
            st["s"] = _build(t, _line(t, ms, "smelter")["refurbished"], x - 10, z)
            st["e"] = _build(t, _line(t, ms, "emanator")["refurbished"], x - 4, z)
            st["k"] = _build(t, _line(t, ms, "smelter")["kludged"], x + 3, z)
            st["c"] = _build(t, _line(t, ms, "powercell")["refurbished"], x + 10, z)
            for d in ("VanometricPowerCell",):
                st["src"] = _build(t, d, x - 14, z + 4)
            t.bridge_call("jawa/comp_set", thing=st["k"], comp="Breakdownable", member="brokenDownInt", value="true")
            pn = t.bridge_call("jawa/power_net", thing=st["s"]) or {}
            if not pn.get("powerOn"):
                raise ExpectationFailed("start: the Refurbished smelter is not powered: %s" % str(pn)[:120])
            if "broken" not in str(t.bridge_call("jawa/inspect_string", thingIds=st["k"])).lower():
                raise ExpectationFailed("start: the Kludged smelter is not broken down")
            START_MARK(t, "sc_marks_agree")

    def text(tid):
        return str(t.bridge_call("jawa/inspect_string", thingIds=tid)).lower()

    with t.component("marks_match_power_state"):
        if _live(t):
            for k in ("s", "e", "k", "c"):
                t.screenshot(name="wm_marks_%s" % k)
            bad = []
            if "no power" in text(st["s"]) or "no power" in text(st["e"]):
                bad.append("a powered machine reads no power")
            if "broken" not in text(st["k"]):
                bad.append("the broken-down smelter does not say so")
            if "power" in text(st["c"]) and "output" not in text(st["c"]):
                bad.append("the power cell reads a power need")
            if bad:
                raise ExpectationFailed("; ".join(bad))
    with t.component("control_cut_net_shows_no_power"):
        if _live(t):
            t.bridge_call("jawa/power_net", thing=st["src"], forcePowerOn=False)
            t.bridge_call("jawa/destroy_batch", rects="%d,%d,1,1" % (x - 14, z + 4))
            t.wait_ticks(250)
            t.screenshot(name="wm_marks_cut")
            if "no power" not in text(st["s"]) and "unpowered" not in text(st["s"]):
                raise ExpectationFailed("the smelter on a cut net does not read no power: %s" % text(st["s"])[:200])


# --------------------------------------------------------------------------- Mod Settings

def _reads(t, keys):
    out = {}
    for k in keys:
        m = _line(t, _machines(t), k)
        out[k] = {"on": m.get("on"), "menu": _menu_visible(t, m.get("original") or ORIGINAL.get(k)),
                  "projects": [p for _, p in _projects(t, k)]}
    out["_gen"] = sorted(d for d in _sample(t, "thingSetMaker", "MapGen_AncientComplexRoomLoot_Default", 50)
                         if d in (ORIGINAL["powercell"],))
    out["_place"] = sorted(p["_word"] for p in _proof(t, "Placement") if p["_verb"] == "PLACE")
    return out


@suite.chain("scene_switch_machine_off")
def scene_switch_machine_off(t):
    """sc_switch_machine_off (switch_gives_machine_back): the autoloom's line off puts the factory's autoloom in the build menu
    and takes its projects away; the power cell's line off lets the generators produce the base game's cell; the machines on the
    map stand unchanged; the last read equals the first; each label says when it takes effect. Control: the smelter, never
    touched, reads the same in all four reads."""
    st = {}
    x, z = t.anchor
    keys = ("autoloom", "powercell", "smelter")
    with t.component("start_switch_machine_off"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_switch_machine_off")
            st["things"] = [_build(t, _line(t, ms, k)[lvl], x - 12 + 6 * i, z)
                            for i, (k, lvl) in enumerate((("autoloom", "wrecked"), ("autoloom", "kludged"),
                                                          ("powercell", "wrecked"), ("powercell", "kludged")))]
            st["r"] = [_reads(t, keys)]
            START_MARK(t, "sc_switch_machine_off")
    with t.component("lines_off_give_machines_back"):
        if _live(t):
            bad = []
            try:
                _set_line(t, "autoloom", False)
                st["r"].append(_reads(t, keys))
                if not st["r"][-1]["autoloom"]["menu"] or st["r"][-1]["autoloom"]["projects"]:
                    bad.append("autoloom off: menu %s, projects %s" % (st["r"][-1]["autoloom"]["menu"], st["r"][-1]["autoloom"]["projects"]))
                loom_w = _line(t, t._wm_ms, "autoloom")["wrecked"]
                if loom_w in st["r"][-1]["_place"]:
                    bad.append("autoloom off: its wreck is still in the placement list")
                _set_line(t, "powercell", False)
                st["r"].append(_reads(t, keys))
                if not st["r"][-1]["_gen"]:
                    bad.append("power cell off: no generator produced the base game's cell")
                if _line(t, t._wm_ms, "powercell")["wrecked"] in st["r"][-1]["_place"]:
                    bad.append("power cell off: its wreck is still in the placement list")
            finally:
                _set_line(t, "autoloom", True)
                _set_line(t, "powercell", True)
            st["r"].append(_reads(t, keys))
            if [_level(t, i) for i in st["things"]] != ["Wrecked", "Kludged", "Wrecked", "Kludged"]:
                bad.append("the machines on the map changed through the switches")
            if st["r"][-1] != st["r"][0]:
                bad.append("the last read differs from the first: %s / %s" % (st["r"][0], st["r"][-1]))
            labels = _proof(t, "LineLabels")
            if not labels or any("effect" not in (l.get("label") or "").lower() and "restart" not in (l.get("label") or "").lower()
                                 and "new map" not in (l.get("label") or "").lower() for l in labels):
                bad.append("a line's label does not say when it takes effect: %s" % labels)
            if bad:
                raise ExpectationFailed("; ".join(bad))
    with t.component("control_smelter_reads_the_same"):
        if _live(t):
            seen = [r["smelter"] for r in st["r"]]
            if any(s != seen[0] for s in seen):
                raise ExpectationFailed("the untouched smelter changed between reads: %s" % seen)


@suite.chain("scene_all_switches_off")
def scene_all_switches_off(t):
    """sc_all_switches_off (switch_gives_machine_back): every line off, every production machine is in the build menu as the
    factory mod has it, a ruin holds no wreck, the generators give the base game's cell and emanator, and the log holds no error
    of this mod. Control: one line on, that machine leaves the build menu and its wreck can be found in a ruin."""
    st = {}
    with t.component("start_all_switches_off"):
        if _live(t):
            ms = st["ms"] = _start(t, "sc_all_switches_off", lines_on=False)
            on = sorted(k for k, m in ms.items() if m.get("on") == "true")
            if on:
                raise ExpectationFailed("start: lines still on %s (the row starts from a load with every line off)" % on)
            t.mark_log()
            START_MARK(t, "sc_all_switches_off")
    with t.component("everything_back_to_the_factory_mod"):
        if _live(t):
            missing = [k for k, m in st["ms"].items() if m.get("original", "").startswith("VFEFactory_") and not _menu_visible(t, m["original"])]
            _gen_map(t, ruin=True)
            wrecks = [r for r in _mod_things(t, st["ms"]) if r["def"] != COMPONENT]
            sets, traders = _generators(t)
            out = _all_outputs(t, sets[:40], traders[:10])
            gave = [d for d in (ORIGINAL["powercell"], ORIGINAL["emanator"]) if d in out]
            errs = _log_errors_naming_mod(t)
            if missing or wrecks or len(gave) < 2 or errs:
                raise ExpectationFailed("not in menu %s; wrecks in the ruin %d; base machines given %s; log %s" % (missing, len(wrecks), gave, errs[:3]))
    with t.component("control_one_line_on"):
        if _live(t):
            try:
                _set_line(t, "smelter", True)
                m = _line(t, _machines(t), "smelter")
                if _menu_visible(t, m.get("original")):
                    raise ExpectationFailed("the smelter's line on, the factory's smelter is still in the build menu (the mod did not load?)")
                found = False
                for _ in range(RUIN_MAPS):
                    _gen_map(t, ruin=True)
                    if any(r["def"] == m["wrecked"] for r in _mod_things(t, st["ms"])):
                        found = True
                        break
                if not found:
                    raise ExpectationFailed("the smelter's line on, no wrecked smelter in %d ruins" % RUIN_MAPS)
            finally:
                _set_line(t, "smelter", False)


def _player_text_hits(root, words):
    """Every player-facing text field (label, description, jobString, reportString, letter text, keyed strings) of Defs, Patches,
    Languages and About.xml, and the C# string literals of Source that reach the screen, that holds one of `words` or names a
    level Repaired. -> [(file, line, word)]"""
    hits = []
    fields = re.compile(r"<(label|description|labelShort|jobString|reportString|text|letterText|letterLabel|tooltip|"
                        r"[A-Za-z_.]+)>([^<]*)</", re.S)
    pats = [(w, re.compile(r"\b%s\b" % re.escape(w), re.I)) for w in words] + [("Repaired", re.compile(r"\bRepaired\b"))]
    for dp, _, fs in os.walk(root):
        if os.sep + "art_source" in dp or os.sep + "obj" in dp or os.sep + "bin" in dp:
            continue
        for f in fs:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            if f.endswith(".xml") and (rel.startswith(("Defs", "Patches", "Languages", "About")) or "Defs" in rel or "Patches" in rel):
                txt = open(p, encoding="utf-8", errors="replace").read()
                txt = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), txt, flags=re.S)
                for m in fields.finditer(txt):
                    tag, val = m.group(1), m.group(2)
                    if tag in ("defName", "texPath", "li", "thingClass", "compClass", "workerClass") and tag != "li":
                        continue
                    if tag.endswith(("defName", "Class", "texPath", "xpath", "packageId")):
                        continue
                    for w, pat in pats:
                        if pat.search(val) and not (w == "Repaired" and tag not in ("label", "description", "labelShort")):
                            hits.append((rel, txt[:m.start()].count("\n") + 1, w))
            elif f.endswith(".cs") and "SelfTest" not in rel and "Kernel" not in rel:
                txt = open(p, encoding="utf-8", errors="replace").read()
                txt = re.sub(r"//[^\n]*", "", txt)
                for m in re.finditer(r'"((?:[^"\\\n]|\\.)*)"(?=\s*(?:\.Translate|\)|,|;|\+))', txt):
                    val = m.group(1)
                    if " " not in val:
                        continue              # an identifier, a def name or a key, not a sentence that reaches the screen
                    for w, pat in pats:
                        if pat.search(val):
                            hits.append((rel, txt[:m.start()].count("\n") + 1, w))
    return hits


def _star_wars_names():
    """The Star Wars names that design/RimMandrake/biome_rulings.md lists as real IP to keep out of RM_ text, read from its
    backticked names under the IP heading; empty when the file cannot be read (then the scene says so)."""
    p = os.path.join(HERE, "..", "..", "..", "design", "RimMandrake", "biome_rulings.md")
    try:
        txt = open(p, encoding="utf-8").read()
    except OSError:
        return None
    i = txt.find("NOT Star Wars IP")
    seg = txt[i:i + 6000] if i >= 0 else ""
    return sorted(set(n for n in re.findall(r"`([A-Z][a-z]{3,})`", seg)))


@suite.chain("scene_text_names_no_setting", offline=True)
def scene_text_names_no_setting(t):
    """sc_text_names_no_setting (no_setting_named), offline: no player-facing text of the mod names the setting, and no level is
    called Repaired. Control, run first so the read is shown able to see before it reports: a planted 'the ship's' in a
    FlowWorks-only patch and a planted C# string are both found."""
    import shutil
    import subprocess
    import tempfile
    st = {}
    with t.component("start_text_names_no_setting"):
        if t._guard():
            sha = subprocess.run(["git", "-C", HERE, "rev-parse", "--short=10", "HEAD"], capture_output=True, text=True).stdout.strip()
            names = _star_wars_names()
            if names is None:
                raise ExpectationFailed("start: design/RimMandrake/biome_rulings.md could not be read")
            st["words"] = SETTING_WORDS + tuple(names)
            t._current.detail = "commit %s, %d words" % (sha or "UNREAD", len(st["words"]))
            START_MARK(t, "sc_text_names_no_setting")
    with t.component("control_planted_texts_found"):
        if t._guard():
            d = tempfile.mkdtemp(prefix="wm_text_")
            try:
                os.makedirs(os.path.join(d, "Patches"))
                os.makedirs(os.path.join(d, "Source"))
                with open(os.path.join(d, "Patches", "FlowWorksOnly.xml"), "w") as f:
                    f.write('<Patch><Operation Class="PatchOperationFindMod"><mods><li>FlowWorks</li></mods><match Class="PatchOperationAdd">'
                            "<value><description>A pipe from the ship's hull.</description></value></match></Operation></Patch>")
                with open(os.path.join(d, "Source", "Planted.cs"), "w") as f:
                    f.write('class P { string s = Translate("A gift of the god of the clan"); }')
                got = {h[0].split(os.sep)[0] for h in _player_text_hits(d, st["words"])}
                if got != {"Patches", "Source"}:
                    raise ExpectationFailed("the planted texts were not both found: %s" % sorted(got))
            finally:
                shutil.rmtree(d, ignore_errors=True)
    with t.component("no_text_names_the_setting"):
        if t._guard():
            hits = _player_text_hits(HERE, st["words"])
            if hits:
                raise ExpectationFailed("%d hits, first %s" % (len(hits), hits[:6]))


# --------------------------------------------------------------------------- the whole run

WHOLE_START_SAVE = "wm_whole_journey_start"       # made by play at the first visit (the row: nothing placed by hand)
STATE_TOOLS_ALLOWED = ("jawa/designate_batch", "jawa/install_blueprint", "rimworld/execute_gizmo", "jawa/select_things",
                       "rimworld/clear_selection", "jawa/safe_advance", "rimworld/save_game", "rimworld/load_game_ready",
                       "jawa/set_terrain_designation", "rimworld/apply_architect_designator", "rimworld/select_architect_designator")


def _whole_start(t, sid):
    ld = t.bridge_call("rimworld/load_game_ready", saveName=WHOLE_START_SAVE, timeoutMs=240000)
    if t._guard() and not (ld or {}).get("success", False):
        raise ExpectationFailed("start: the starting save %s of play is not there (owed at the first visit): %s" % (WHOLE_START_SAVE, str(ld)[:120]))
    ms = _start(t, sid)
    started = [p for k in ms for _, p in _projects(t, k) if _researched(t, p)]
    if started:
        raise ExpectationFailed("start: projects of this mod already finished: %s" % started)
    found = {r["def"] for r in _mod_things(t, ms) if r["ruin"]}
    need = {_line(t, ms, "smelter")["wrecked"], _line(t, ms, "powercell")["wrecked"], COMPONENT}
    if need - found:
        raise ExpectationFailed("start: the ruin lacks %s" % sorted(need - found))
    t.mark_log()
    return ms


def _journey(t, sid, first, second):
    """By orders only: carry both wrecks home, factory floor and install, study, research, repair both to Kludged with a reload
    in the first repair, study again, research, fetch the component, repair `first` to Refurbished, read `second`'s last order.
    Returns {line: (level, last order reason)}."""
    ms = t._wm_ms
    x, z = t.anchor
    ends = {}
    things = {r["def"]: r for r in _mod_things(t, ms)}
    for i, key in enumerate((first, second)):
        row = things.get(_line(t, ms, key)["wrecked"]) or {}
        wid = row.get("id")
        _designate(t, "Uninstall", wid, at=(row.get("x"), row.get("z")))
        t.bridge_call("jawa/safe_advance", ticks=30000)
        mini = ((t.bridge_call("jawa/list_things", defName="MinifiedThing", limit=50) or {}).get("things") or [{}])[0].get("id")
        if key == "smelter":
            t.bridge_call("rimworld/select_architect_designator", designatorId=FACTORY_FLOOR)
            t.bridge_call("rimworld/apply_architect_designator", designatorId=FACTORY_FLOOR, x=x - 4, z=z - 4, width=8, height=8)
            t.bridge_call("jawa/safe_advance", ticks=30000)
        t.bridge_call("jawa/install_blueprint", thing=mini, x=x + 8 * i, z=z)
        t.bridge_call("jawa/safe_advance", ticks=30000)
    for step in ("1", "2"):
        for key in (first, second):
            mid = next((th["id"] for th in (t.bridge_call("jawa/list_things", rect=_site(t, 30), limit=200) or {}).get("things") or []
                        if _proof(t, "Level", th["id"]) and _level(t, th["id"]) not in (None, "none")
                        and _proof(t, "Level", th["id"])[0].get("line") == key), None)
            study = [g for g in _gizmos(t, mid) if "study" in g[0].lower()] if mid else []
            if study:
                t.bridge_call("rimworld/execute_gizmo", gizmoId=study[0][3])
            t.bridge_call("jawa/safe_advance", ticks=STUDY_DAYS * 60000)
            if step == "2" and key == first:
                comp = next((r for r in _mod_things(t, ms) if r["def"] == COMPONENT), None)
                if comp:
                    _designate(t, "Haul", comp["id"], at=(comp["x"], comp["z"]))
            present, ok, reason, gid = _repair_order(t, mid) if mid else (False, False, "", None)
            if ok:
                t.bridge_call("rimworld/execute_gizmo", gizmoId=gid)
                if step == "1" and key == first:
                    t.bridge_call("jawa/safe_advance", ticks=5000)
                    t.bridge_call("rimworld/save_game", saveName=sid + "_mid")
                    t.bridge_call("rimworld/load_game_ready", saveName=sid + "_mid", timeoutMs=240000)
                t.bridge_call("jawa/safe_advance", ticks=3 * 60000)
            t.screenshot(name="%s_%s_%s" % (sid, key, step))
            ends[key] = (_level(t, mid) if mid else None, reason if not ok else "")
    return ends


def _state_calls(t):
    rec = getattr(t.session, "calls", None)
    return [c for c in (rec or []) if c[0] not in STATE_TOOLS_ALLOWED and not c[0].endswith(("_get", "_read", "list_things", "static_call",
                                                                                              "availability", "inspect_string", "drain_log",
                                                                                              "study_record", "pawn_thoughts", "power_net",
                                                                                              "list_selected_gizmos", "get_game_info"))]


@suite.chain("scene_whole_journey", tick_cap=40 * 60000)
def scene_whole_journey(t):
    """sc_whole_journey (whole_journey), owner_review: from a starting save of play, by orders only, the smelter and the power
    cell are carried home, studied, researched and repaired to Kludged (a reload mid-repair), studied again, the component fetched,
    the smelter repaired to Refurbished; the cell's last order names the missing component; no error of this mod in the log; a
    capture at each change of level. Control: the state-changing calls after the start are orders, clock, saves and loads only."""
    st = {}
    with t.component("start_whole_journey"):
        if _live(t):
            t._wm_ms = _whole_start(t, "sc_whole_journey")
            START_MARK(t, "sc_whole_journey")
            st["mark"] = len(getattr(t.session, "calls", []) or [])
    with t.component("journey_ends_refurbished_and_named"):
        if _live(t):
            st["ends"] = ends = _journey(t, "sc_whole_journey", "smelter", "powercell")
            t._current.detail = "ends %s" % ends
            if ends.get("smelter", (None,))[0] != "Refurbished" or ends.get("powercell", (None,))[0] != "Kludged" \
                    or "component" not in ends.get("powercell", ("", ""))[1].lower():
                raise ExpectationFailed("journey ended %s" % ends)
            errs = _log_errors_naming_mod(t)
            if errs:
                raise ExpectationFailed("log errors of this mod: %s" % errs[:3])
    with t.component("control_orders_only"):
        if _live(t):
            bad = _state_calls(t)
            if bad:
                raise ExpectationFailed("state-changing calls that play could not make: %s" % bad[:6])


@suite.chain("scene_whole_second_order", tick_cap=40 * 60000)
def scene_whole_second_order(t):
    """sc_whole_second_order (whole_journey): from the same starting save, in a second order (study in the ruin, fetch the
    component first, the power cell before the smelter, a reload mid-study), the run ends with the machines swapped: the cell
    Refurbished, the smelter Kludged naming the missing component. Control: the two runs' end states differ only in which machine
    got the component."""
    st = {}
    with t.component("start_whole_second_order"):
        if _live(t):
            t._wm_ms = _whole_start(t, "sc_whole_second_order")
            START_MARK(t, "sc_whole_second_order")
    with t.component("second_order_ends_swapped"):
        if _live(t):
            st["ends"] = ends = _journey(t, "sc_whole_second_order", "powercell", "smelter")
            if ends.get("powercell", (None,))[0] != "Refurbished" or ends.get("smelter", (None,))[0] != "Kludged" \
                    or "component" not in ends.get("smelter", ("", ""))[1].lower():
                raise ExpectationFailed("second order ended %s" % ends)
    with t.component("control_end_states_differ_only_by_component"):
        if _live(t):
            first = {"smelter": "Refurbished", "powercell": "Kludged"}
            got = {k: v[0] for k, v in st["ends"].items()}
            if {k: first[k] for k in got} == got or set(got.values()) != set(first.values()):
                raise ExpectationFailed("end states %s against the first run's %s" % (got, first))


# --------------------------------------------------------------------------- interactions

@suite.chain("scene_uninstall_during_repair")
def scene_uninstall_during_repair(t):
    """sc_uninstall_during_repair (wreck_comes_home x repair_on_the_machine): Uninstall during a repair cancels it first, the
    delivered materials lie where the cell stood, the cell is carried Wrecked and installed, and a new order is accepted.
    Control: the same cell with its repair complete is carried Kludged and gives nothing back."""
    st = {}
    x, z = t.anchor
    with t.component("start_uninstall_during_repair"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_uninstall_during_repair")
            _finish_first(t, "powercell")
            st["c"] = _build(t, _line(t, ms, "powercell")["wrecked"], x - 6, z)
            st["c2"] = _build(t, _line(t, ms, "powercell")["wrecked"], x + 6, z)
            _items(t, "Steel", x, z - 8, 400)
            _items(t, "ComponentIndustrial", x + 2, z - 8, 20)
            _colonist(t, x, z - 6)
            _give_repair(t, st["c"])
            for _ in range(60):
                t.wait_ticks(500)
                if (_proof(t, "Repair", st["c"]) or [{}])[0].get("delivered"):
                    break
            if not (_proof(t, "Repair", st["c"]) or [{}])[0].get("delivered"):
                raise ExpectationFailed("start: no materials delivered to the cell's repair")
            st["deliv"] = (_proof(t, "Repair", st["c"]) or [{}])[0].get("delivered")
            START_MARK(t, "sc_uninstall_during_repair")
    with t.component("uninstall_cancels_and_gives_back"):
        if _live(t):
            _designate(t, "Uninstall", st["c"])
            t.wait_ticks(3000)
            near = {d: _count(t, d, "%d,%d,7,7" % (x - 9, z - 3)) for d in ("Steel", "ComponentIndustrial")}
            mini = ((t.bridge_call("jawa/list_things", defName="MinifiedThing", limit=20) or {}).get("things") or [{}])[0].get("id")
            if not mini:
                raise ExpectationFailed("the cell was not carried")
            r = t.bridge_call("jawa/install_blueprint", thing=mini, x=x - 6, z=z + 10) or {}
            t.wait_ticks(6000)
            stood = [th for th in (t.bridge_call("jawa/list_things", rect="%d,%d,5,5" % (x - 8, z + 8), limit=10) or {}).get("things") or []]
            lvl = _level(t, stood[0]["id"]) if stood else None
            if not any(near.values()) or lvl != "Wrecked":
                raise ExpectationFailed("delivered %s; near the old cell %s; installed level %r (%s)" % (st["deliv"], near, lvl, str(r)[:80]))
            present, ok, reason, _ = _repair_order(t, stood[0]["id"])
            if not ok:
                raise ExpectationFailed("a new repair order on the moved cell is unavailable: %s" % reason)
    with t.component("control_complete_repair_carried_kludged"):
        if _live(t):
            _give_repair(t, st["c2"])
            if _wait_level(t, st["c2"], "Kludged", 3) != "Kludged":
                raise ExpectationFailed("the control cell's repair did not complete")
            before = _count(t, "Steel")
            _designate(t, "Uninstall", st["c2"])
            t.wait_ticks(3000)
            rows = (t.bridge_call("jawa/list_things", defName="MinifiedThing", limit=20) or {}).get("things") or []
            if _count(t, "Steel") != before or not any("Kludged" in str(r) for r in rows):
                raise ExpectationFailed("a complete repair gave materials back or was not carried Kludged: %s" % str(rows)[:160])


@suite.chain("scene_repair_needs_ground")
def scene_repair_needs_ground(t):
    """sc_repair_needs_ground (wreck_comes_home x repair_on_the_machine), rule R_ground: on a plain floor the order is unavailable
    and names factory floor; on factory floor it is available; factory floor laid under a standing wreck by a colonist makes it
    available with the wreck unchanged; a wreck carried onto factory floor installs and its order is available. Control: a wrecked
    power cell on the plain floor has its order available."""
    st = {}
    x, z = t.anchor
    with t.component("start_repair_needs_ground"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_repair_needs_ground")
            if not _researched(t, FACTORY_RESEARCH[0]):
                raise ExpectationFailed("start: the factory mod's first research is not finished by play (a starting save is owed)")
            _finish_first(t, "smelter")
            _finish_first(t, "powercell")
            st["a"] = _ground_wreck(t, "smelter", x - 12, z, terrain=PLAIN_FLOOR)
            st["b"] = _ground_wreck(t, "smelter", x, z, terrain=FACTORY_FLOOR)
            st["c"] = _ground_wreck(t, "smelter", x + 12, z, terrain=PLAIN_FLOOR)
            st["cell"] = _ground_wreck(t, "powercell", x - 12, z + 12, terrain=PLAIN_FLOOR)
            _floor(t, FACTORY_FLOOR, x - 4, z + 10, 8, 8)
            _items(t, "Steel", x, z - 8, 600)
            _colonist(t, x, z - 6)
            START_MARK(t, "sc_repair_needs_ground")
    with t.component("plain_floor_refused_factory_floor_open"):
        if _live(t):
            a = _repair_order(t, st["a"])
            b = _repair_order(t, st["b"])
            if a[1] or "floor" not in a[2].lower() or not b[1]:
                raise ExpectationFailed("plain floor order %s, factory floor order %s" % (a[:3], b[:3]))
    with t.component("floor_laid_under_standing_wreck"):
        if _live(t):
            t.bridge_call("rimworld/select_architect_designator", designatorId=FACTORY_FLOOR)
            r = t.bridge_call("rimworld/apply_architect_designator", designatorId=FACTORY_FLOOR, x=x - 15, z=z - 3, width=7, height=7) or {}
            for _ in range(24):
                t.wait_ticks(2500)
                if _repair_order(t, st["a"])[1]:
                    break
            if _level(t, st["a"]) != "Wrecked" or not _repair_order(t, st["a"])[1]:
                raise ExpectationFailed("floor under the standing wreck: order %s, level %r (%s)" % (
                    _repair_order(t, st["a"])[:3], _level(t, st["a"]), str(r)[:100]))
    with t.component("carried_onto_factory_floor"):
        if _live(t):
            _designate(t, "Uninstall", st["c"])
            t.wait_ticks(4000)
            mini = ((t.bridge_call("jawa/list_things", defName="MinifiedThing", limit=20) or {}).get("things") or [{}])[0].get("id")
            r = t.bridge_call("jawa/install_blueprint", thing=mini, x=x, z=z + 14) or {}
            if not r.get("success"):
                raise ExpectationFailed("the wreck could not be placed on factory floor: %s" % str(r)[:200])
            t.wait_ticks(8000)
            stood = (t.bridge_call("jawa/list_things", rect="%d,%d,5,5" % (x - 2, z + 12), limit=10) or {}).get("things") or []
            if not stood or not _repair_order(t, stood[0]["id"])[1]:
                raise ExpectationFailed("the carried wreck did not install on factory floor with its order available")
    with t.component("control_cell_needs_no_floor"):
        if _live(t):
            c = _repair_order(t, st["cell"])
            if not c[1]:
                raise ExpectationFailed("the wrecked cell on a plain floor: order unavailable (%s): the ground rule refuses all" % c[2])


def _loaded(t, package):
    """True when `package` is in the loaded mod list, False when it is not, None when the list cannot be read."""
    r = t.bridge_call("jawa/running_mods") or {}
    mods = r.get("mods") or r.get("running") or []
    if not mods:
        return None
    return any(package.lower() == str(m.get("packageId") if isinstance(m, dict) else m).lower() for m in mods)


@suite.chain("scene_study_without_research_reinvented")
def scene_study_without_research_reinvented(t):
    """sc_study_without_research_reinvented (study_opens_research): on a tier of the small list without Research Reinvented, the
    wreck still offers the base game's study, the first project is locked naming the wreck, the researcher studies it by himself,
    and the project opens and is finished at the bench. Control: study never turned on, the bench alone opens nothing."""
    st = {}
    with t.component("start_study_without_research_reinvented"):
        if _live(t):
            _proof(t, "Loaded")                  # the row's start: the mod's proof type answers
            rr = _loaded(t, RR_PACKAGE)
            if rr is not False:
                raise ExpectationFailed("start: Research Reinvented is %s in the loaded list (this scene runs on a tier without it)"
                                        % ("loaded" if rr else "UNREAD"))
            st.update(_study_stage(t, "sc_study_without_research_reinvented"))
            START_MARK(t, "sc_study_without_research_reinvented")
    _study_flow(t, st, second_needs_no_study=False)


@suite.chain("scene_cannery_tier")
def scene_cannery_tier(t):
    """sc_cannery_tier (only_by_repair, levels_of_function, repair_on_the_machine): on the small list plus Vanilla Cooking
    Expanded, no level of the cannery is in the build menu before or after every project; the placement list holds its wreck; the
    Wrecked cannery offers nothing and has a carried form; Kludged offers a non-empty part of the donor's processes; Refurbished
    offers all of them and is slower than the factory mod's own; the wreck and the Kludged cannery offer their repair order.
    Control: the cannery's line off puts it in the build menu and takes its wreck off the placement list."""
    st = {}
    x, z = t.anchor
    with t.component("start_cannery_tier"):
        if _live(t):
            ms = t._wm_ms = _start(t, "sc_cannery_tier")
            can = _line(t, ms, "cannery")
            v, raw = _def_field(t, "ThingDef/" + can["original"], "defName")
            if not v:
                raise ExpectationFailed("start: the cannery's def %s is not loaded (Vanilla Cooking Expanded?): %s" % (can["original"], str(raw)[:120]))
            done = [p for p in FACTORY_RESEARCH if _researched(t, p)]
            if done:
                raise ExpectationFailed("start: research already finished: %s" % done)
            START_MARK(t, "sc_cannery_tier")
    with t.component("cannery_not_in_menu_before_or_after_research"):
        if _live(t):
            can = _line(t, t._wm_ms, "cannery")
            before = [d for d in _levels_of(can) if _menu_visible(t, d)]
            t.bridge_call("jawa/research_bulk", mode="finish_all")
            after = [d for d in _levels_of(can) if _menu_visible(t, d)]
            if before or after:
                raise ExpectationFailed("cannery levels in the build menu: before %s, after %s" % (before, after))
            if can["wrecked"] not in [p["_word"] for p in _proof(t, "Placement")]:
                raise ExpectationFailed("the cannery's wreck is not in the placement list")
    with t.component("cannery_levels_do_their_work"):
        if _live(t):
            can = _line(t, t._wm_ms, "cannery")
            _floor(t, FACTORY_FLOOR, x - 22, z - 6, 44, 12)
            ids = {lvl: _build(t, can[lvl] if lvl != "original" else can["original"], x - 18 + 10 * i, z)
                   for i, lvl in enumerate(("wrecked", "kludged", "refurbished", "original"))}
            w, _ = _proc_names(t, ids["wrecked"])
            k, _ = _proc_names(t, ids["kludged"])
            r, _ = _proc_names(t, ids["refurbished"])
            o, _ = _proc_names(t, ids["original"])
            form, _ = _def_field(t, "ThingDef/" + can["wrecked"], "minifiedDef")
            sp_r, sp_o = _proof(t, "Speed", ids["refurbished"]), _proof(t, "Speed", ids["original"])
            orders = [_repair_order(t, ids[l])[0] for l in ("wrecked", "kludged")]
            bad = []
            if w or not form or form == "(null)":
                bad.append("Wrecked offers %s, carried form %r" % (w, form))
            if not k or not set(k) < set(o) or set(r) != set(o):
                bad.append("processes Kludged %s, Refurbished %s, Original %s" % (k, r, o))
            if not (sp_r and sp_o and float(sp_r[0]["_word"]) < float(sp_o[0]["_word"])):
                bad.append("Refurbished speed %s against the Original's %s" % (sp_r, sp_o))
            if not all(orders):
                bad.append("repair orders on the wreck and the Kludged cannery: %s" % orders)
            if bad:
                raise ExpectationFailed("; ".join(bad))
    with t.component("control_cannery_line_off"):
        if _live(t):
            can = _line(t, t._wm_ms, "cannery")
            try:
                _set_line(t, "cannery", False)
                if not _menu_visible(t, can["original"]):
                    raise ExpectationFailed("cannery line off: the cannery is not in the build menu (did its patches apply?)")
                if can["wrecked"] in [p["_word"] for p in _proof(t, "Placement")]:
                    raise ExpectationFailed("cannery line off: its wreck is still in the placement list")
            finally:
                _set_line(t, "cannery", True)


def _row_disagrees(row, kludged, refurbished):
    """The onboarding row against what the loaded game offers: the differences, or [] when they agree."""
    out = []
    want_k = set(x for x in row.get("kludged", "").split(",") if x)
    want_r = set(x for x in row.get("refurbished", "").split(",") if x)
    if want_k != set(kludged):
        out.append("kludged row %s, game %s" % (sorted(want_k), sorted(kludged)))
    if want_r != set(refurbished):
        out.append("refurbished row %s, game %s" % (sorted(want_r), sorted(refurbished)))
    return out


@suite.chain("scene_every_machine_onboarded")
def scene_every_machine_onboarded(t):
    """sc_every_machine_onboarded (levels_of_function, repair_on_the_machine, study_opens_research): a state read for every machine
    on the list: the first project locked naming its wreck; the wreck offers study and a repair order unavailable for research
    and available after it; Kludged offers its order to Refurbished; Wrecked offers nothing and gives no power; Kludged is a
    non-empty strict part of the donor's processes, Refurbished equals them and is slower; the loaded game equals the onboarding
    row. Control: the base game's electric smelter shows no study and no repair order; a planted copy of one row with a process
    removed is reported as disagreeing."""
    st = {}
    x, z = t.anchor
    with t.component("start_every_machine_onboarded"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_every_machine_onboarded")
            _floor(t, FACTORY_FLOOR, x - 50, z - 50, 100, 100)
            _build(t, "VanometricPowerCell", x + 48, z + 48)
            st["ids"] = {}
            for i, (key, m) in enumerate(sorted(ms.items())):
                for j, lvl in enumerate(("wrecked", "kludged", "refurbished", "original")):
                    d = m.get(lvl) if lvl != "original" else m.get("original")
                    st["ids"][(key, lvl)] = _build(t, d, x - 46 + (i % 5) * 18 + j * 4, z - 46 + (i // 5) * 12)
            st["elec"] = _build(t, "ElectricSmelter", x + 40, z - 40)
            started = [p for k in ms for _, p in _projects(t, k) if _researched(t, p)]
            if started:
                raise ExpectationFailed("start: restoration projects already finished: %s" % started)
            START_MARK(t, "sc_every_machine_onboarded")
    with t.component("every_machine_reads_as_its_row"):
        if _live(t):
            bad, st["rows"] = [], {}
            for key, m in sorted(t._wm_ms.items()):
                ids = {lvl: st["ids"][(key, lvl)] for lvl in ("wrecked", "kludged", "refurbished", "original")}
                p1 = [p for s_, p in _projects(t, key) if s_ == "1"]
                lock = _research_row(t, p1[0]) if p1 else {}
                names = [pp.get("defName") for pp in _study(t, m["wrecked"]).get("projects") or []]
                if not p1 or lock.get("analyzedThingsRequirementsMet") is not False or p1[0] not in names:
                    bad.append("%s: first project not locked by its wreck (%s, %s)" % (key, p1, names))
                study = any("study" in g[0].lower() for g in _gizmos(t, ids["wrecked"]))
                pre = _repair_order(t, ids["wrecked"])
                _finish_first(t, key)
                post = _repair_order(t, ids["wrecked"])
                kl = _repair_order(t, ids["kludged"])
                if not study or not pre[0] or pre[1] or "research" not in pre[2].lower() or not post[1] or not kl[0]:
                    bad.append("%s: study %s, order before %s, after %s, Kludged order %s" % (key, study, pre[:3], post[:3], kl[:2]))
                w, _ = _proc_names(t, ids["wrecked"])
                pn = t.bridge_call("jawa/power_net", thing=ids["wrecked"]) or {}
                k, _ = _proc_names(t, ids["kludged"])
                r, _ = _proc_names(t, ids["refurbished"])
                o, _ = _proc_names(t, ids["original"])
                if w or abs(pn.get("energyOutputPerTick") or 0) > 0:
                    bad.append("%s: Wrecked offers %s or gives power" % (key, w))
                if o and (not k or not set(k) < set(o) or set(r) != set(o)):
                    bad.append("%s: processes Kludged %s, Refurbished %s, Original %s" % (key, k, r, o))
                sr, so = _proof(t, "Speed", ids["refurbished"]), _proof(t, "Speed", ids["original"])
                if not (sr and so and float(sr[0]["_word"]) < float(so[0]["_word"])):
                    bad.append("%s: Refurbished speed %s, Original %s" % (key, sr, so))
                row = (_proof(t, "Onboarding", key) or [{}])[0]
                st["rows"][key] = (row, k, r)
                bad += ["%s: %s" % (key, d) for d in _row_disagrees(row, k, r)]
            if bad:
                raise ExpectationFailed("%d machines off their rows: %s" % (len(bad), bad[:5]))
    with t.component("control_electric_smelter_and_planted_row"):
        if _live(t):
            g = [g_[0] for g_ in _gizmos(t, st["elec"]) if "study" in g_[0].lower() or any(w_ in g_[0].lower() for w_ in REPAIR_GIZMO)]
            if g:
                raise ExpectationFailed("the base game's electric smelter offers %s: the read reports study or repair anywhere" % g)
            key, (row, k, r) = next(iter(sorted(st["rows"].items())))
            planted = dict(row)
            planted["refurbished"] = ",".join(sorted(r)[1:])
            if not _row_disagrees(planted, k, r):
                raise ExpectationFailed("a planted row with %s removed was not reported as disagreeing" % (sorted(r)[:1],))


@suite.chain("scene_caravan_wreck_home")
def scene_caravan_wreck_home(t):
    """sc_caravan_wreck_home (wreck_comes_home): on a map on another world tile, a wrecked autoloom is uninstalled, a caravan of two
    colonists and a pack animal loads it by their own work, travels home and arrives with it, and colonists install the same Wrecked
    autoloom at the home cell. Control: the same load with the pack animal and one colonist left out reads over capacity."""
    st = {}
    x, z = t.anchor
    with t.component("start_caravan_wreck_home"):
        if _live(t):
            t._wm_ms = ms = _start(t, "sc_caravan_wreck_home")
            home = (t.bridge_call("jawa/map_info") or {})
            st["home_tile"] = home.get("tile")
            _floor(t, PLAIN_FLOOR, x + 10, z - 3, 8, 7)
            _gen_map(t, ruin=False)
            away = t.bridge_call("jawa/map_info") or {}
            if away.get("tile") == st["home_tile"] or st["home_tile"] is None:
                raise ExpectationFailed("start: no second map on another tile (home %r, now %r)" % (st["home_tile"], away.get("tile")))
            ax, az = int(away.get("sizeX") or 200) // 2, int(away.get("sizeZ") or 200) // 2
            st["w"] = _build(t, _line(t, ms, "autoloom")["wrecked"], ax, az, faction="none")
            st["crew"] = [_colonist(t, ax + 3, az + 3), _colonist(t, ax + 4, az + 3)]
            r = t.bridge_call("jawa/spawn_pawn", kindDef="Muffalo", faction="player", x=ax + 5, z=az + 3)
            st["pack"] = (((r or {}).get("pawns") or [{}])[0]).get("id")
            if not st["pack"] or None in st["crew"] or _level(t, st["w"]) != "Wrecked":
                raise ExpectationFailed("start: wreck %r, crew %s, pack animal %r" % (st["w"], st["crew"], st["pack"]))
            START_MARK(t, "sc_caravan_wreck_home")
    with t.component("caravan_brings_the_wreck_home"):
        if _live(t):
            _designate(t, "Uninstall", st["w"])
            mini = None
            for _ in range(40):
                t.wait_ticks(500)
                rows = (t.bridge_call("jawa/list_things", defName="MinifiedThing", limit=20) or {}).get("things") or []
                if rows:
                    mini = rows[0]
                    break
            if not mini:
                raise ExpectationFailed("the wreck was not uninstalled into a carried form")
            st["mini"] = mini["id"]
            st["one_carrier"] = t.bridge_call("jawa/caravan_mass", pawns=st["crew"][0], things=mini["id"]) or {}
            f = t.bridge_call("jawa/caravan_form_load", pawns=",".join(st["crew"] + [st["pack"]]), things=mini["id"], destTile=st["home_tile"]) or {}
            if not f.get("success") or f.get("over"):
                raise ExpectationFailed("the caravan did not start forming with the wreck: %s" % str(f)[:200])
            arrived, placed = False, {}
            for _ in range(40):
                t.bridge_call("jawa/safe_advance", ticks=15000)
                loaded = (t.bridge_call("jawa/set_current_map", mapId=-1) or {}).get("loadedMaps") or []
                if not any(m_.get("tile") == st["home_tile"] for m_ in loaded):
                    continue
                _go_to_tile(t, st["home_tile"])
                # the carried wreck is home once the engine accepts its install blueprint here (it is held on this map)
                placed = t.bridge_call("jawa/install_blueprint", thing=st["mini"], x=x + 13, z=z) or {}
                if placed.get("success"):
                    arrived = True
                    break
            if not arrived:
                raise ExpectationFailed("the caravan did not arrive home with the wreck: %s" % str(placed)[:160])
            t.bridge_call("jawa/safe_advance", ticks=30000)
            stood = (t.bridge_call("jawa/list_things", rect="%d,%d,6,6" % (x + 11, z - 2), limit=10) or {}).get("things") or []
            if not any(_level(t, r_["id"]) == "Wrecked" for r_ in stood):
                raise ExpectationFailed("no Wrecked autoloom stands at the home cell after the install")
    with t.component("control_too_few_carriers_read_over"):
        if _live(t):
            m = st.get("one_carrier") or {}       # read before the caravan formed, on the same carried wreck
            if not m.get("over"):
                raise ExpectationFailed("one colonist and the wreck read %s of %s: a carried form with no weight" % (m.get("usage"), m.get("capacity")))


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
