"""validation.py -- modcheck suite for RimMandrake Inhabited (mandrake.rm.inhabited).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Inhabited

Grounded in the mod's actual source: `RM_InhabitedMod.cs` for the three real
Mod Settings fields (`fateEnabled`, `robbedFraction`, `beggarsFromPoolEnabled`
-- all `public static`, same shape as `PitsSettings`); `DebugActions_Inhabited.cs`
for the exact debug-action labels and the plain `Log.Message` lines each one
emits (this mod's read-back channel -- most are prose, not `field=value`
pairs, unlike Pits' purpose-built `REPORT_PIT` line, so several components
below can only assert a tag's PRESENCE, not a specific value; noted per
component); `InhabitedFateWorker.cs` and `MapComponent_InhabitedWatch.cs` for
where `fateEnabled` and `robbedFraction` actually gate something; and
`Defs/PlaceDefs/Places_Inhabited.xml` for the one fact that makes fate
testable offline: `RM_InhabitedPlace_Scrapyard` (fate `FleeIfThreatened`) is
the FIRST `InhabitedPlaceDef` the XML loader resolves, and
`DebugActions_Inhabited.CreatePlaceHere` assigns
`DefDatabase<InhabitedPlaceDef>.AllDefsListForReading.FirstOrDefault()` with
no picker -- so "Create place at current tile" always seeds a
`FleeIfThreatened` place, never one of the three `Resident` archetypes, with
no dialog to drive.

TWO STRUCTURAL GAPS, both flagged rather than worked around:

  1. **All of this mod's debug actions target `Find.CurrentMap.Tile` /
     `Find.CurrentMap.Center` / `FindPlace()`'s first `WorldObject_Inhabited`
     -- never a `t.anchor` cell.** `t.clear_area`/`t.spawn` operate on a rect
     around `t.anchor` (500,500 by default), which has no relationship to
     where a place's stock actually lands (`place.stockSpot` is
     `map.Center` or a random non-edge cell). `clear_area(size=20)` below is
     boilerplate per spec 1b (every chain opens on a cleared area) but does
     NOT clear the cell the mod's own mechanics touch. A component that needs
     to destroy or inspect Things at `stockSpot` specifically cannot do so
     with the current verb vocabulary -- this is why `robbed_threshold`'s
     actual 0.5 boundary (destroy SOME but not all dumped stock, expect
     "robbed") is not exercised here; only the "nothing spurious once
     collected" side is.
  2. **`RM_InhabitedSettings`'s three fields are `public static`.** Per the
     Pits pilot (MOD_VALIDATION_PIT_PILOT_1's own validation.py, its
     "NOT a chain" note): `rimworld/update_mod_settings` reflects INSTANCE
     fields on the ModSettings object and refuses a static one with
     "Could not resolve field ... on ...". `t.set_setting` is therefore not
     used anywhere below; every `toggle=` component tests the toggle's
     SHIPPED DEFAULT (all three default `true`/0.5f), never a flip. This is
     the identical, already-known gap -- not rediscovered here, just hit
     again.

suite.toggles = ["fateEnabled", "robbedFraction", "beggarsFromPoolEnabled"]
(RM_InhabitedSettings' only three fields -- the GenSteps that place a cast/
stock on a map are explicitly NOT exposed as settings, per RM_InhabitedMod.cs's
own comment, so they are not toggles this suite owes a component to).

Still not proven / likely first-live-run corrections:
  - The `_debug()` helper assumes Inhabited's plain (non-ToolMap) `Action`-type
    debug actions resolve at path `Actions\\T: <label>` with no `x`/`z`
    params, by ANALOGY to Pits' MEASURED finding for its ToolMap actions
    (category is UI metadata there too) -- never independently confirmed for
    a non-targeted action. If the path or the no-coordinate call shape is
    wrong, every component in this file fails identically on first run,
    which at least localises the fix to `_debug()` itself.
  - `robbed_threshold_not_spurious` only proves Menace()'s stock branch is
    silent once `stockSpawnedCount == 0`; the actual fraction threshold is
    unproven (see gap 1 above).
  - `fate_detects_when_enabled` proves `InhabitedFateWorker.DetectCause`'s
    default-on behavior; it does NOT prove `fateEnabled=false` suppresses
    anything, because that gate lives in `MapComponent_InhabitedWatch`'s
    background tick (a 250-tick-interval poll), not in `DetectCause` itself,
    and the toggle can't be flipped live (gap 2).
  - `pool_ready_for_beggars_substitution` proves the PRECONDITION
    (`DisplacedPool` holds a humanlike candidate); the actual Harmony
    substitution in `Patch_BeggarsFromPool.cs` needs a live, Ideology-gated
    Beggars quest (`QuestNode_Root_Beggars`) to call
    `QuestGen_Pawns.GeneratePawn` at all, and nothing here triggers one -- no
    debug action exists for it and no bridge quest-generation verb is
    documented.
  - Everything settlement-shaped (`WorldObject_InhabitedSettlement`,
    `GenStep_ComposeSettlementDistrict`, `SettlementCasing`,
    `GateSearchHook`, `Patch_SettlementDeparture`, the visit/re-entry/
    departure loop `DebugActions_Inhabited` itself calls "test harness, needs
    one already created") is UNTESTED here. `CreateSettlementHere`'s own
    picker (`Dialog_DebugOptionListLister` over `SettlementManifestDef`) has
    no scripted way to choose an item without a live menu, and the source's
    own comments confirm nothing in ordinary play constructs an
    `Inhabited_Settlement` yet -- there is no producer, so this is authored-
    but-unreachable exactly the way `DebugActions_Inhabited.cs` says the
    wilderness `GenStep_InhabitedCast`/`GenStep_InhabitedStock` route is too
    (no `TileMutatorDef` names `Inhabited_Cast` in the current build set).
  - `CharacterApplier`/`CharacterDef`-driven "Spawn authored character" is
    untested: it depends on `CharacterDef`s existing in the deployed build
    (generated by an external `cast_to_xml.py` script per its own error
    message), which this suite has not confirmed are present.
"""
from modcheck import Suite

suite = Suite("Inhabited")
suite.toggles = ["fateEnabled", "robbedFraction", "beggarsFromPoolEnabled"]

SCRAPYARD_DEF = "RM_InhabitedPlace_Scrapyard"


def _debug(t, label):
    """Execute one of DebugActions_Inhabited.cs's plain (non-ToolMap) debug
    actions: CreatePlaceHere/StuffRoster/AbsorbRoster/DrawFromPool/DumpStock/
    CollectStock/TestFate all resolve their own target (CurrentTile(),
    FindPlace(), Find.CurrentMap) rather than taking a cell argument, unlike
    Pits' ToolMap-targeted actions -- so no x/z is passed. By analogy to the
    Pits pilot's MEASURED finding, `category` ("RimMandrake.Inhabited") is UI
    metadata, not a path segment; the real path is `Actions\\T: <label>`.
    UNCONFIRMED for a non-targeted action -- see this file's own docstring."""
    return t.bridge_call("rimworld/execute_debug_action", path="Actions\\T: " + label)


@suite.chain("place_and_roster")
def place_and_roster(t):
    """The place/roster/pool lifecycle: create a place (always seeds
    RM_InhabitedPlace_Scrapyard, see module docstring), stuff its roster,
    absorb the roster into the world's displaced pool, then draw people back
    out. Each step's own Log.Message is the read-back -- these are prose
    lines, not `field=value` pairs (unlike Pits' purpose-built REPORT_PIT), so
    most assertions here are tag-presence only."""
    t.clear_area(size=20)

    with t.component("place_created", beyond_toggle=True):
        _debug(t, "Create place at current tile")
        t.expect_log_contains("[RimMandrake.Inhabited] created")
        t.screenshot()

    with t.component("roster_stuffed", beyond_toggle=True):
        _debug(t, "Stuff roster (3 pawns)")
        t.expect_log_contains("[RimMandrake.Inhabited] roster of")
        t.screenshot()

    with t.component("absorbed_into_pool", beyond_toggle=True):
        _debug(t, "Absorb roster into pool")
        t.expect_log_contains("[RimMandrake.Inhabited] moved")
        t.screenshot()

    with t.component("pool_ready_for_beggars_substitution", toggle="beggarsFromPoolEnabled"):
        # Proves the PRECONDITION Patch_BeggarsFromPool's DrawAnyInto relies
        # on (DisplacedPool holds >=1 humanlike pawn) via the SAME log line
        # "absorbed_into_pool" just captured -- the substitution itself is
        # not triggered here, see module docstring.
        t.expect_log_contains("[RimMandrake.Inhabited] moved")
        t.screenshot()

    with t.component("drawn_from_pool", beyond_toggle=True):
        _debug(t, "Draw 3 from pool")
        t.expect_log_contains("[RimMandrake.Inhabited] drew")
        t.screenshot()


@suite.chain("fate_and_stock")
def fate_and_stock(t):
    """A fresh place (again defaulting to Scrapyard/FleeIfThreatened): dump
    its larder onto the map, detect the fate cause, collect the stock back,
    then re-detect to prove the robbed check is silent once nothing is left
    out. See module docstring gap 1 for why the 0.5 threshold's actual
    boundary is not exercised."""
    t.clear_area(size=20)

    with t.component("place_created", beyond_toggle=True):
        _debug(t, "Create place at current tile")
        t.expect_log_contains("[RimMandrake.Inhabited] created")
        t.screenshot()

    with t.component("stock_dumped", beyond_toggle=True):
        _debug(t, "Stock: dump onto this map")
        t.expect_log_contains("[RimMandrake.Inhabited] dumped")
        t.screenshot()

    with t.component("fate_detects_when_enabled", toggle="fateEnabled"):
        # DetectCause is called directly here, bypassing
        # MapComponent_InhabitedWatch's own fateEnabled gate entirely
        # (InhabitedFateWorker.cs: "Master fate-detection toggle is gated at
        # the caller") -- this proves the default-ON detection mechanism the
        # toggle sits in front of, not the toggle's effect. See module
        # docstring gap 2.
        _debug(t, "Fate: test the cause now")
        t.expect_log_contains("[RimMandrake.Inhabited] fate=", field="fate",
                               value="FleeIfThreatened")
        t.screenshot()

    with t.component("stock_collected", beyond_toggle=True):
        _debug(t, "Stock: collect from this map")
        t.expect_log_contains("[RimMandrake.Inhabited] took back")
        t.screenshot()

    with t.component("robbed_threshold_not_spurious", toggle="robbedFraction"):
        # Weak coverage (flagged in the module docstring): Menace()'s
        # robbedFraction branch is guarded by `stockSpawnedCount > 0`, which
        # is false immediately after a full collect, so this only proves the
        # check does not fire spuriously on an empty larder -- not that the
        # 0.5 boundary itself is correct.
        _debug(t, "Fate: test the cause now")
        t.expect_log_contains("[RimMandrake.Inhabited] fate=", field="cause",
                               value="none")
        t.screenshot()
