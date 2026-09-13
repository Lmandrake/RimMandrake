"""validation.py -- modcheck suite for RimUtinni ShipMemory (mandrake.rut.shipmemory).

Grounded in `Source/GameComponent_ShipMemory.cs` (the one GameComponent,
its three reveal triggers, and the `Find.HiddenItemsManager.Hidden(Gate)`
guard shared by all of them), `Source/ShipMemorySettings.cs` (the two real
Mod Settings fields), `Defs/ThingDefs_Items/RUT_ShipMemory.xml` (the
never-spawned gate def), and `Patches/RUT_ShipMemory_ContainmentGate.xml`
(the seven researchPrerequisites -> discoveryPrerequisites swaps).
Requires the Anomaly DLC (`About.xml`'s own `modDependencies`) -- every
mechanism below is itself gated on `ModsConfig.AnomalyActive`, so this
suite assumes the runner's environment has Anomaly active, same as it
assumes the "mod under test" itself is active.

SAME STATIC-FIELD GAP AS Pits/Pyrelands: `ShipMemorySettings`'
`shipMemoryEnabled`/`bioferriteThreshold` are `public static`, so
`t.set_setting` is not attempted (see Pits' and Pyrelands' own
validation.py for the grounded reason). Both components below exercise
the mechanism at its SHIPPED DEFAULT (enabled, threshold 50).

**Chain order matters and is deliberate, not incidental**: `Find.
HiddenItemsManager.Hidden(Gate)` is checked by BOTH
`GameComponentTick` and `Notify_SignalReceived` before either will act,
and `SetDiscovered` is a one-shot, save-scoped flip with no reset call
anywhere in this mod. Since a modcheck run keeps ONE game session across
every chain for a mod (only the test AREA is cleared/swept between
chains -- design/RimMandrake/mod_validation_runner_spec.md's teardown
is scoped to what a chain spawned, not the save), the gate can only be
revealed FRESH once per run. So:
  1. `bioferrite_stockpile_reveal` runs FIRST and proves the tick-based
     stockpile trigger, which needs the gate genuinely still hidden.
  2. `assailant_signal_after_reveal` runs SECOND, deliberately reusing
     the now-revealed gate to prove the OTHER trigger's own guard --
     `if (!Find.HiddenItemsManager.Hidden(Gate)) return;` -- suppresses a
     second reveal/second letter rather than double-firing. This is a
     real assertion about the code, not a workaround for the ordering
     constraint: the two chains together prove both "it reveals" and
     "it does not re-reveal," which a single fresh-gate-per-chain design
     could not have shown at all.

Still not proven / likely first-live-run corrections:
  1. The THIRD trigger route -- `Building_HoldingPlatform` holding a live
     pawn (`HeldPawn != null`) -- is not exercised: no bridge tool for
     "capture a creature into a HoldingPlatform" was found in a tool
     search (`--list-tools` for "holdingplatform"/"capture"/"contain"
     turned up nothing suited to entities specifically), and building
     one, spawning a capturable creature, and running the vanilla capture
     job to completion is a heavier live-colony scenario than this
     mod's own mechanism warrants scripting from scratch here. Left as a
     genuine gap, not a guess.
  2. `letter_list`'s `label` field is the read-back channel because the
     letter's own `LetterDef` (`LetterDefOf.PositiveEvent`) is a shared
     vanilla def, not something unique to this mod -- filtering by label
     text is deliberate, not an oversight, but it is a soft string match
     against `Languages/English/Keyed/RUT_ShipMemory.xml` and would
     silently stop matching if that Keyed string is ever reworded without
     updating this file.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("ShipMemory")
suite.toggles = ["shipMemoryEnabled"]

GATE_DEF = "RUT_ShipMemory_Containment"
REVEAL_LABEL = "She remembers the chains"   # RUT_ShipMemory_Containment_Label
PATCHED_THINGS = ["HoldingPlatform", "ElectricInhibitor", "ShardInhibitor",
                  "BioferriteHarvester", "Electroharvester", "BioferriteGenerator"]
PATCHED_TERRAIN = "BioferritePlate"


def _live(t):
    """See Pyrelands/validation.py's identical helper -- offline-probe
    guard, not a game-state check."""
    return t.session is not None and not t.upstream_failed


def _reveal_letters(t):
    r = t.bridge_call("jawa/letter_list")
    letters = (r or {}).get("letters") or []
    return [l for l in letters if l.get("label") == REVEAL_LABEL]


@suite.chain("bioferrite_stockpile_reveal")
def bioferrite_stockpile_reveal(t):
    """Runs FIRST in this suite -- see module docstring on chain order.
    Stockpiles exactly the shipped default threshold (50) of Bioferrite on
    a player-home map cell; `map.resourceCounter.GetCount` sums quantity
    across every stack on the map regardless of how spawn_batch happened
    to lay them out, so 50 separate 1-count spawns satisfy the
    `>= threshold` check exactly as a single stack of 50 would."""
    t.clear_area(size=12)
    x, z = t.anchor
    t.spawn("Bioferrite", count=50, at="pile")   # same cell each call -> one pile
    t.wait_ticks(700)   # >= one 600-tick GameComponentTick check boundary

    with t.component("reveals_on_stockpile", toggle="shipMemoryEnabled"):
        found = _reveal_letters(t)
        if _live(t) and len(found) < 1:
            raise ExpectationFailed(
                "expected a '%s' letter after stockpiling 50 Bioferrite and "
                "waiting past the 600-tick check interval; letter_list had none "
                "matching" % REVEAL_LABEL)
        t.screenshot()


@suite.chain("assailant_signal_after_reveal")
def assailant_signal_after_reveal(t):
    """Runs SECOND, deliberately after the gate is already revealed (see
    module docstring). Fires the Assailant dungeon's own signal shape
    (`Notify_SignalReceived` matches by `EndsWith`, per the C#'s own
    comment citing spec §3) and proves the ALREADY-discovered guard
    suppresses a second letter, rather than proving a fresh reveal (which
    chain 1 already owns)."""
    t.clear_area(size=12)
    before = _reveal_letters(t)

    with t.component("no_duplicate_reveal_once_discovered", toggle="shipMemoryEnabled"):
        t.bridge_call("jawa/signal_send", tag="RUT_ShipMemory_ContainmentTestSignal.RUT_ShipMemory_Containment")
        after = _reveal_letters(t)
        if _live(t) and len(after) != len(before):
            raise ExpectationFailed(
                "firing the Assailant-shaped signal after the gate was already "
                "discovered produced %d matching letters where %d existed before -- "
                "Notify_SignalReceived's Hidden(Gate) guard did not suppress it"
                % (len(after), len(before)))
        t.screenshot()


@suite.chain("containment_gate_patch_wiring")
def containment_gate_patch_wiring(t):
    """Pure def-state check, unconditional (no ModSettings governs whether
    `RUT_ShipMemory_ContainmentGate.xml` applies at all -- only
    `PatchOperationFindMod`'s Anomaly-active gate does, matching this
    suite's own Anomaly-active assumption). Confirms all seven patched
    defs actually lost `researchPrerequisites` and gained the
    `discoveryPrerequisites` pointing at the gate -- the item spec's own
    "why the removal patch is mandatory" note (IsResearchFinished is
    checked before discoveryPrerequisites, so a dangling reference would
    hide these forever)."""
    t.clear_area(size=8)

    with t.component("seven_defs_gated_on_containment", beyond_toggle=True):
        pairs = ";".join("ThingDef/%s" % n for n in PATCHED_THINGS)
        pairs += ";TerrainDef/%s" % PATCHED_TERRAIN
        r = t.bridge_call("jawa/get_defs", defs=pairs,
                          fields="researchPrerequisites,discoveryPrerequisites")
        if _live(t):
            rows = {row.get("defName"): row for row in (r or {}).get("defs") or []}
            not_found = (r or {}).get("notFound") or []
            bad = []
            if not_found:
                bad.append("not found (Anomaly not active in this environment?): %r" % not_found)
            for name in PATCHED_THINGS + [PATCHED_TERRAIN]:
                row = rows.get(name)
                if row is None:
                    continue
                fields = row.get("fields") or {}
                research = fields.get("researchPrerequisites")
                if research not in (None, "(no such field)", [], ""):
                    bad.append("%s still has researchPrerequisites=%r" % (name, research))
                discover = fields.get("discoveryPrerequisites")
                discover_list = discover if isinstance(discover, list) else ([discover] if discover else [])
                if GATE_DEF not in discover_list:
                    bad.append("%s.discoveryPrerequisites does not include %s: got %r"
                               % (name, GATE_DEF, discover))
            if bad:
                raise ExpectationFailed(
                    "containment-gate patch did not apply as authored: %s" % "; ".join(bad))
        t.screenshot()
