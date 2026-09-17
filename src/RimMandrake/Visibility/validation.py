"""validation.py -- modcheck suite for RimMandrake Colony Visibility
(mandrake.rm.visibility).

Grounded in the mod's actual, ENTIRE source, read whole:
`GameComponent_ColonyVisibility.cs` (the 0-100 dial, band ladder, Annex A
threat curve, tile-memory decay), `ColonyVisibilityRaidPatch.cs` (the five
Harmony hooks and their own choke-point reasoning), `RM_VisibilityMod.cs`
(the two Mod Settings: `enableRaidScaling`, `raidScalingStrength`,
`launchResetMultiplier` -- all `public static` on `RM_VisibilitySettings`,
same static-field shape as StructureInjections/RustChrome/Antiquities),
`DebugActions_Visibility.cs` (the one dev action this suite drives), and
`VisibilityModInit.cs`. Also read `design/validation_walks/RimMandrake/
Visibility.md`.

WHAT THIS SUITE DOES NOT RE-PROVE: `BandFor`/`ThreatFactor`/`SeasonsAway`/
`DecayedTileVisibility` are all PURE functions (no `Find.*`, no Harmony) by
this mod's own design specifically so they can run outside a game --
`python3 src/RimMandrake/Utils/selftest_colony_visibility.py` (a real net48
console app compiling the actual .cs file in, per that script's own header)
already covers every one of them offline. Duplicating that math here with
`jawa/*` round-trips would be strictly worse evidence for the same claim.
This suite exists for the ONE thing the walk doc itself calls out as
structurally unprovable offline (step 4): whether the live Harmony Prefix on
`IncidentWorker.TryExecute` actually multiplies a real firing incident's
`parms.points` by the expected factor, and whether the two Mod Settings
(`enableRaidScaling`, `raidScalingStrength`) actually gate that multiplication
in the running game, not just in the formula.

HOW THE LIVE PROOF WORKS: `Prefix_ScaleHostilePoints` logs its own before/
after/factor line in `Prefs.DevMode` ("[RimMandrake.Visibility] <Worker> "
"points {before} -> {after} (visibility {v}, factor {f})") -- this suite
reads THAT line back via `jawa/drain_log`, the same "the debug/patch's own
summary log line is the evidence" idiom StructureInjections and RustChrome
already use, rather than inferring the multiplier from a raid's eventual
pawn count (which vanilla's own wealth/pointsPerColonist terms would
confound). The live incident is fired via `jawa/storyteller_fire(incidentDef=
"RaidEnemy", points=100, dryRun=False)` -- NOT `jawa/fire_incident`, whose
own tool description says it calls `IncidentDef.Worker.TryExecute(parms)`
directly, which is exactly the method our Prefix sits on, so either tool
would reach the hook; `storyteller_fire` is used because Aftermath's own
suite already establishes it as a proven, gated (`#if JAWA_GM_TOOLS`) but
present tool on this build. `points=100` is chosen so every one of Annex A's
five anchor factors (0.55/0.80/1.00/1.25/1.60) lands on a whole number with
no `Mathf.Clamp` rounding ambiguity (55/80/100/125/160), all comfortably
above `StorytellerUtility.GlobalPointsMin()` and under the 10000 ceiling, so
the clamp never engages and the observed number is pure `points * factor`.

Setting `shipVisibility` to each anchor is done through the mod's OWN dev
action, `DebugActions_Visibility.SetVisibility` (category
"RimMandrake.Visibility", plain `DebugActionType.Action`, no ToolMap
click needed -- confirmed by the source: no `actionType` override means the
default `Action`, and the method itself takes no `IntVec3` argument) via
`rimworld/execute_debug_action` with a two-level path: "Actions\\Set Colony
Visibility (dev)\\<preset label>", following the SAME submenu-selection
idiom `load_session.py`'s "Wear apparel (selected)...\\<defName>" already
uses for a `Dialog_DebugOptionListLister` menu -- this action's own preset
labels are `v + " (" + BandFor(v) + ")"` (source line 30), so "0 (Hidden)"
and "100 (Exposed)" are the exact literal strings, not guessed.

Still not proven / likely first-live-run corrections:
  1. `ResetOnLaunch()` (the Ta'Baa launch-reset postfix on `GravshipUtility.
     GenerateGravship`) and the tile-memory decay pair (`RecordTileDeparture`
     prefix on the same method / `ApplyTileMemoryOnArrival` postfix on
     `ArriveExistingMap`/`ArriveNewMap`) are UNCOVERED -- all three need a
     real, complete gravship launch-and-arrive cycle (a built grav engine,
     `CompLaunchable.TryLaunch`, a destination tile, a second map), which is
     a heavier live rig than this smoke suite's single-map, no-launch shape
     affords. The pure decay MATH (`SeasonsAway`/`DecayedTileVisibility`) is
     covered by the offline selftest per the module docstring; only the
     Harmony wiring around the actual launch/arrival is untested here.
  2. `Postfix_AddInspectGizmo` (the `Building_GravEngine` gizmo showing the
     current band) is UNCOVERED -- no bridge tool was found that lists a
     specific Thing's live Gizmos to read a `Command_Action`'s label/desc
     back; this needs a real grav engine placed on the map plus such a tool.
  3. The five "not found by reflection" `Log.Error` guards in `Apply()`
     (walk doc step 3) are a NEGATIVE claim ("this string never appears") --
     this suite does not assert their absence, because a positive result
     from `raid_points_scale_with_visibility_band` below (the Prefix
     actually firing and producing the expected log line) is strictly
     stronger evidence that `AccessTools.Method(IncidentWorker.TryExecute)`
     resolved than a log-absence check would be, and re-asserting the
     absence of five specific error strings on top adds no coverage the
     positive path doesn't already imply for `TryExecute`. The other four
     reflected members (`GenerateGravship`/`ArriveExistingMap`/
     `ArriveNewMap`/`GetGizmos`) are NOT covered by anything below (see #1/2).
  4. `raidScalingStrength` is exercised only at its two mathematically clean
     endpoints (0 = no effect, 1 = default/unchanged curve) -- values between
     0 and 2 that double the deviation are asserted by formula reading, not
     independently fired live.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Visibility")
suite.toggles = ["enableRaidScaling", "raidScalingStrength"]

SETTINGS_TYPE = "RimMandrake.Visibility.RM_VisibilitySettings"
TAG = "[RimMandrake.Visibility]"
RAID_POINTS = 100.0
# Annex A anchors (module docstring): points=100 makes every factor a whole
# number, no Mathf.Clamp rounding ambiguity.
ANCHOR_LOW = ("0 (Hidden)", 0.55)
ANCHOR_HIGH = ("100 (Exposed)", 1.60)


def _set_visibility(t, preset_label):
    r = t.bridge_call("rimworld/execute_debug_action",
                      path="Actions\\Set Colony Visibility (dev)\\" + preset_label)
    return r


def _fire_raid_and_read_factor(t, worker_hint="IncidentWorker_RaidEnemy"):
    r = t.bridge_call("jawa/storyteller_fire", incidentDef="RaidEnemy",
                      points=RAID_POINTS, dryRun=False)
    if not (r or {}).get("success"):
        raise ExpectationFailed(
            "jawa/storyteller_fire(RaidEnemy, points=%.0f) did not report success "
            "(blocked by a dialog, or CanFireNow was false): %r" % (RAID_POINTS, r))
    log = t.bridge_call("jawa/drain_log", limit=200, contains=TAG)
    msgs = [m.get("text", "") for m in ((log or {}).get("messages") or [])]
    line = msgs[-1] if msgs else None
    return line


@suite.chain("raid_points_scale_with_visibility_band")
def raid_points_scale_with_visibility_band(t):
    """Two anchors, one chain: sets shipVisibility to the Hidden floor (0)
    and the Exposed ceiling (100) via the mod's own dev action, fires a real
    RaidEnemy incident at a controlled points=100 through each, and reads
    the Prefix's own before/after/factor log line back -- proving both that
    `IncidentWorker.TryExecute` is actually being intercepted on this build
    (module docstring #3) and that the Annex A curve's two extremes apply
    correctly to a LIVE firing incident, not just the pure function."""
    import re

    with t.component("raid_enemy_scales_by_annex_a_curve", beyond_toggle=True):
        t.set_setting(SETTINGS_TYPE, {"enableRaidScaling": True,
                                      "raidScalingStrength": 1.0})

        for label, expected_factor in (ANCHOR_LOW, ANCHOR_HIGH):
            vr = _set_visibility(t, label)
            if not vr:
                raise ExpectationFailed(
                    "rimworld/execute_debug_action for preset %r returned nothing "
                    "-- the debug action's own submenu path may not match the "
                    "current label format" % label)

            line = _fire_raid_and_read_factor(t)
            if line is None:
                raise ExpectationFailed(
                    "no %s log line found after firing RaidEnemy at preset %r -- "
                    "either enableRaidScaling was off or the Prefix never ran"
                    % (TAG, label))
            m = re.search(r"points (-?\d+) -> (-?\d+) \(visibility (-?[\d.]+), "
                          r"factor (-?[\d.]+)\)", line)
            if not m:
                raise ExpectationFailed(
                    "could not parse before/after/factor out of log line %r "
                    "(format may have drifted from ColonyVisibilityRaidPatch.cs's "
                    "Prefix_ScaleHostilePoints)" % line)
            before, after, vis, factor = (float(m.group(1)), float(m.group(2)),
                                          float(m.group(3)), float(m.group(4)))
            expected_after = RAID_POINTS * expected_factor
            if abs(factor - expected_factor) > 0.02:
                raise ExpectationFailed(
                    "preset %r: logged factor %.2f does not match Annex A's ruled "
                    "%.2f (line=%r)" % (label, factor, expected_factor, line))
            if abs(after - expected_after) > 1.0:
                raise ExpectationFailed(
                    "preset %r: points %g -> %g, expected -> %g (factor %.2f x "
                    "%.0f) (line=%r)"
                    % (label, before, after, expected_after, expected_factor,
                       RAID_POINTS, line))
        t.screenshot()


@suite.chain("settings_gate_the_multiplier_reversibly")
def settings_gate_the_multiplier_reversibly(t):
    """`enableRaidScaling=False` makes `Prefix_ScaleHostilePoints` return
    BEFORE its own dev-mode Log.Message call (source: the guard is the
    first line in the method), so the correct live proof of "off" is the
    ABSENCE of a new tag line after firing, not a factor of 1.0 -- a
    genuinely different assertion shape than the strength-slider case
    below, which still logs. Flips back on and re-fires in the same
    component to prove the gate is reversible mid-session, matching
    StructureInjections/RustChrome's own toggle round-trip precedent."""
    with t.component("enableRaidScaling_gate_reversible", toggle="enableRaidScaling"):
        _set_visibility(t, ANCHOR_HIGH[0])

        t.set_setting(SETTINGS_TYPE, {"enableRaidScaling": False})
        t.bridge_call("jawa/drain_log", limit=200, contains=TAG)  # clear the queue first
        off_line = _fire_raid_and_read_factor(t)
        if off_line is not None:
            raise ExpectationFailed(
                "a %s log line appeared with enableRaidScaling=False -- the "
                "master off switch did not suppress the Prefix: %r" % (TAG, off_line))

        t.set_setting(SETTINGS_TYPE, {"enableRaidScaling": True})
        on_line = _fire_raid_and_read_factor(t)
        if on_line is None:
            raise ExpectationFailed(
                "no %s log line after re-enabling enableRaidScaling -- the gate "
                "did not turn back on" % TAG)
        t.screenshot()


@suite.chain("strength_slider_zero_neutralises_the_curve")
def strength_slider_zero_neutralises_the_curve(t):
    """`RM_VisibilitySettings.ScaledThreatFactor`: `1 + (curveFactor - 1) *
    raidScalingStrength` -- at strength=0 this is exactly 1.0 regardless of
    visibility, i.e. the dial keeps tracking but stops affecting raid
    points, DIFFERENT from the master toggle (which suppresses the log line
    itself): here the Prefix still runs and still logs, just with factor
    1.00. Visibility held at the Exposed ceiling (curveFactor=1.60) so a
    slider bug that only shows at extremes is not masked."""
    import re

    with t.component("raidScalingStrength_zero_is_factor_one",
                      toggle="raidScalingStrength"):
        t.set_setting(SETTINGS_TYPE, {"enableRaidScaling": True,
                                      "raidScalingStrength": 0.0})
        _set_visibility(t, ANCHOR_HIGH[0])

        line = _fire_raid_and_read_factor(t)
        if line is None:
            raise ExpectationFailed(
                "no %s log line with raidScalingStrength=0 -- expected the Prefix "
                "to still run and log factor 1.00" % TAG)
        m = re.search(r"points (-?\d+) -> (-?\d+) \(visibility (-?[\d.]+), "
                      r"factor (-?[\d.]+)\)", line)
        if not m or abs(float(m.group(4)) - 1.0) > 0.02:
            raise ExpectationFailed(
                "raidScalingStrength=0 at visibility 100 did not log factor 1.00: "
                "%r" % line)
        if abs(float(m.group(1)) - float(m.group(2))) > 1.0:
            raise ExpectationFailed(
                "raidScalingStrength=0 changed the points despite factor 1.00: %r"
                % line)

        t.set_setting(SETTINGS_TYPE, {"raidScalingStrength": 1.0})
        t.screenshot()
