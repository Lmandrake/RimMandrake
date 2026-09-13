"""validation.py -- modcheck suite for RimMandrake Wrecked Machines
(mandrake.rm.wreckedmachines).

Grounded in this mod's actual Defs -- there is no C# here at all: `Source/`
holds only offline Python art tooling (fit_sprite.py, grab_source_art.py,
sheet.py, ...), no .csproj, no Assemblies folder, no ModSettings class. Per
this runner spec's own floor rule, "most mods have no settings yet ... zero
toggles is not a floor violation" -- `suite.toggles = []` and every
component below is `beyond_toggle=True`.

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
from modcheck import Suite, ExpectationFailed

suite = Suite("WreckedMachines")
suite.toggles = []

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
