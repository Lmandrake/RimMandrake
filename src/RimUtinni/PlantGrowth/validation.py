"""validation.py -- modcheck suite for RimUtinni Jawa Plant Growth
(mandrake.rut.plantgrowth).

Read whole before writing this: `Patch_Plant_GrowthRate.cs`,
`PlantGrowthConfig.cs`, `PlantGrowthMod.cs` (settings), `PlantGrowthSettingsDef.cs`,
`Defs/JawaPlantGrowthSettings.xml`, `About.xml` and the walk doc.

ONE MOD SETTINGS TOGGLE, real boolean checkbox: `growthEnabled`
(`PlantGrowthSettings.growthEnabled`, default `true`). The four numeric
bands (`defaultMultiplier`/`treeMultiplier`/`terminatorMultiplier`/
`minGrowDaysToBoost`) are SLIDERS, not toggles, per the briefing's own rule
for what goes in `suite.toggles`. All five are `public static` fields
(same declaration shape as Pits/RimProperty, which `BRIDGE_STATIC_
SETTINGS_FIELDS_1` already fixed `jawa/mod_settings_field` for), so
`t.set_setting` reaches them.

A REAL, WALK-DOC-IS-STALE FINDING, same family as RustChrome's and
Oracle's tonight: the walk doc's "must be true" bullet #1 and step 3 say
the def read-back for `PlantGrowthSettingsDef.defaultMultiplier` etc.
should read `4.0`/`2.5`/`0.4`/`1.0` and treats that as proof of the live
values. Reading `PlantGrowthConfig.Rebuild()` and its own header comment
in `PlantGrowthConfig.cs` ("MOD_OPTIONS_RETROFIT_1: the four numeric bands
are owned by the in-game Mod Settings screen ... Rebuild() no longer
reads them"): those four def fields are DEAD as of that retrofit -- the
XML values are still there (kept "for anyone hand-editing the file for
reference", About.xml's own words) but `Rebuild()` reads
`PlantGrowthSettings.defaultMultiplier` etc. instead, which HAPPEN to
default to the same numbers today. A def read-back of those four fields
would therefore keep "passing" even if someone changed the Mod Settings
defaults and left the XML untouched, or vice versa -- it proves nothing
about the LIVE multiplier. This suite proves the live values instead, by
observing the actual growth-rate effect through the toggle (see below),
never by reading the def's now-inert numeric fields. `terminatorBiomes`
and `exemptPlants` are UNAFFECTED by this retrofit -- `Rebuild()` still
reads those two lists from the def -- so the def read-back for THOSE two
fields is still meaningful proof, and is used below.

A SECOND REAL FINDING, this one about the terminator biome roster itself,
not the walk doc: `PlantGrowthConfig.cs`'s own comment says the sole
confirmed terminator biome, `"PoisonForest"`, comes from "Advanced Biomes
(Continued)". This repo also ships its OWN biome of a very similar name --
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PoisonForest.xml` -- but
its `defName` is `RUT_PoisonForest`, confirmed by direct read, NOT
`PoisonForest`. Different string, no fuzzy match in
`DefDatabase<BiomeDef>.GetNamedSilentFail`. Neither `UtinniPatches`
(`mandrake.rut.patches`) nor any packageId recognisable as "Advanced
Biomes (Continued)" appears in the minimal list (grepped directly against
`infrastructure/state/modlists/ModsConfig.MINIMAL.xml`) -- so on the
environment `modcheck run PlantGrowth` actually composes, the terminator
biome name `"PoisonForest"` resolves to NOTHING, `TerminatorBiomeCount`
should be exactly 0, and `Rebuild()`'s own warning line
(`"terminator biome 'PoisonForest' is not loaded; skipping it."`) should
fire. That absence is asserted below as the correct signal for this
environment, not treated as a bug.

WHY THE GROWTH-RATE PROOF IS A SAME-SPECIES ON/OFF COMPARISON, not a
cross-species one: `Plant_Potato` and `Plant_TreeOak` (both confirmed real
vanilla Core defNames -- found already targeted by
`src/RimStarWars/StarWarsPatches/Patches/PlantNames_CanonSW.xml`'s own
patches, not guessed here) have very different intrinsic `growDays`, so a
raw side-by-side growth-percentage comparison between two different
species would confound "the multiplier" with "the species' own base
rate". Instead, each component below measures the SAME species TWICE,
once with `growthEnabled=True` and once with `growthEnabled=False`,
replanted fresh both times (`jawa/set_plants`'s own `clearFirst=true`
default wipes the rect before replanting, so a re-run is idempotent, per
that tool's own description) -- isolating exactly the toggle's effect.
`Plant_Potato` (non-exempt, default band) should show a clearly bigger
delta with the toggle ON; `Plant_Ambrosia` (one of the three named exempt
plants, also confirmed real via its use in
`src/RimUtinni/UtinniPatches/Patches/BiomeFlora_Ashkarr.xml`) should show
almost no difference either way, proving the exempt list actually holds
against the toggle rather than merely existing in a list nothing reads.

REAL, UNMEASURED RESPONSE-SHAPE RISK: `jawa/inspect_string`'s own
`outputSchema` only documents the PER-THING shape (id/defName/label/
position/inspect-as-lines/lowPriority/error), not the top-level container
key. `_plant_growth_percent()` below guesses `things` as that key (the
same noun `jawa/list_things` uses) -- UNVERIFIED, the single most likely
first-live-run correction in this file. Whether vanilla's own inspect
string renders `"Growth: 45%"` as a bare integer or with a decimal
(`"45.2%"`) is also unverified; the regex below accepts either.

Still not proven / likely first-live-run corrections:
  1. `wait_ticks` budgets (20000 for both growth-delta components) are a
     rough estimate from `growDays`/`GenDate.TicksPerDay` arithmetic, not
     measured against a real quicktest map's actual tick rate or starting
     time-of-day -- if the map starts at night or in a cold snap, vanilla
     growth (and therefore the whole delta) could sit near zero for a
     stretch regardless of the multiplier, since the environmental
     factors are folded into the composite rate BEFORE this mod's postfix
     multiplies it. First-live-run correction candidate if either
     growth-delta component reads implausibly small numbers on both
     passes.
  2. The terminator-biome multiplier (x0.4, "genuinely slower than
     vanilla") has NO live component at all -- there is no bridge route
     found to force a quicktest map's own biome to a terminator one (only
     `jawa/world_*` planet-level tools were found, nothing that reassigns
     an already-generated map's `Biome`), and the one biome this mod's
     own default roster names does not resolve on the minimal list anyway
     (see the terminator-biome finding above). Left undone rather than
     faked.
  3. The inspect string reading the boosted rate live (About.xml's own
     "verify from the inspect string ... it reads the boosted rate")
     is exactly what the growth-delta components exercise, but the exact
     wording/format of that line is read defensively via regex, not
     asserted to match a specific transcribed string.
"""
import re

from modcheck import Suite, ExpectationFailed

suite = Suite("PlantGrowth")
suite.toggles = ["growthEnabled"]

SETTINGS_TYPE = "RimMandrake.Utinni.PlantGrowth.PlantGrowthSettings"
BOOT_LOG_TAG = "[RimMandrake.Utinni.PlantGrowth] scaling"
WARNING_LOG_TAG = "[RimMandrake.Utinni.PlantGrowth] terminator biome"

DEFAULT_BAND_PLANT = "Plant_Potato"   # non-exempt, default (x4) band
EXEMPT_PLANT = "Plant_Ambrosia"       # named in DEFAULT_EXEMPT_PLANTS
GROWTH_TICKS = 20000                  # ~1/3 in-game day -- see docstring item 1


def _plant_growth_percent(t, defName, rect):
    r = t.bridge_call("jawa/inspect_string", defName=defName, rect=rect)
    rows = (r or {}).get("things") or (r or {}).get("results") or []
    row = rows[0] if rows else None
    lines = (row or {}).get("inspect") or []
    joined = "\n".join(lines) if isinstance(lines, list) else str(lines)
    m = re.search(r"Growth:\s*([\d.]+)%", joined)
    return float(m.group(1)) if m else None


def _measure_growth_delta(t, defName, x, z, ticks):
    rect = "%d,%d,1,1" % (x, z)
    ops = "%s:%d,%d,1,1" % (defName, x, z)

    t.set_setting(SETTINGS_TYPE, {"growthEnabled": True})
    t.bridge_call("jawa/set_plants", ops=ops, growth=0.05, density=1.0)
    t.wait_ticks(ticks)
    on_pct = _plant_growth_percent(t, defName, rect)

    t.set_setting(SETTINGS_TYPE, {"growthEnabled": False})
    t.bridge_call("jawa/set_plants", ops=ops, growth=0.05, density=1.0)
    t.wait_ticks(ticks)
    off_pct = _plant_growth_percent(t, defName, rect)

    return on_pct, off_pct


@suite.chain("boot_config_and_terminator_roster")
def boot_config_and_terminator_roster(t):
    """The static ctor's own summary line, plus the terminator-biome
    absence this environment should produce (see module docstring's
    second finding). Asserts `ExemptCount >= 3` (the three named plants
    are always classified exempt regardless of what else is loaded) and
    `ScaledCount > 0`, never an exact total -- CLAUDE.md's own rule
    against guessing a count that depends on the full loaded plant
    roster."""
    t.clear_area(size=8)

    with t.component("boot_line_and_terminator_absence", beyond_toggle=True):
        t.expect_log_contains(BOOT_LOG_TAG, field=None, value=None)
        r = t.bridge_call("jawa/drain_log", limit=200, contains="[RimMandrake.Utinni.PlantGrowth]")
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        if t._guard():
            m = re.search(
                r"scaling (\d+) plant defs \(default x4, tree x2\.5\), "
                r"(\d+) exempt, (\d+) terminator biome\(s\) at x0\.4\.",
                joined)
            if not m:
                raise ExpectationFailed(
                    "no '%s ... default x4, tree x2.5 ... terminator "
                    "biome(s) at x0.4.' line found. Recent lines: %r"
                    % (BOOT_LOG_TAG, msgs))
            scaled, exempt, terminator = (int(x) for x in m.groups())
            if scaled <= 0:
                raise ExpectationFailed("ScaledCount = %d, expected > 0" % scaled)
            if exempt < 3:
                raise ExpectationFailed(
                    "ExemptCount = %d, expected >= 3 (the three named "
                    "DEFAULT_EXEMPT_PLANTS)" % exempt)
            if terminator != 0:
                raise ExpectationFailed(
                    "TerminatorBiomeCount = %d, expected 0 on this "
                    "environment -- 'PoisonForest' resolves to nothing "
                    "here (see module docstring: it is not the same "
                    "defName as our own RUT_PoisonForest, and neither "
                    "UtinniPatches nor its third-party namesake is in "
                    "the minimal list)" % terminator)
            if WARNING_LOG_TAG not in joined:
                raise ExpectationFailed(
                    "expected the 'terminator biome ... not loaded; "
                    "skipping it.' warning given TerminatorBiomeCount=0, "
                    "but it did not appear. Recent lines: %r" % msgs)
        t.screenshot()

    with t.component("terminator_and_exempt_lists_readback", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs="RimMandrake.Utinni.PlantGrowth.PlantGrowthSettingsDef/RUT_JawaPlantGrowth_Settings",
                          fields="terminatorBiomes,exemptPlants")
        if t._guard():
            rows = (r or {}).get("defs") or []
            row = rows[0] if rows else None
            fields = (row or {}).get("fields") or {}
            terminator_biomes = fields.get("terminatorBiomes")
            exempt_plants = fields.get("exemptPlants")
            if "PoisonForest" not in str(terminator_biomes):
                raise ExpectationFailed(
                    "RUT_JawaPlantGrowth_Settings.terminatorBiomes = %r, "
                    "expected to contain 'PoisonForest' (the def's own "
                    "authored list, unaffected by the numeric-bands "
                    "retrofit -- see module docstring)" % terminator_biomes)
            for name in ("Plant_TreeAnima", "Plant_TreeGauranlen", "Plant_Ambrosia"):
                if name not in str(exempt_plants):
                    raise ExpectationFailed(
                        "RUT_JawaPlantGrowth_Settings.exemptPlants = %r, "
                        "expected to contain %r" % (exempt_plants, name))
        t.screenshot()


@suite.chain("growth_toggle_and_exempt_list")
def growth_toggle_and_exempt_list(t):
    """Same-species on/off comparisons (see module docstring for why this
    design, not a cross-species one). Restores `growthEnabled=True`
    (default) at the end for any later suite in the same run."""
    t.clear_area(size=8)
    x, z = t.anchor

    with t.component("default_band_plant_grows_faster_enabled", toggle="growthEnabled"):
        on_pct, off_pct = _measure_growth_delta(t, DEFAULT_BAND_PLANT, x, z, GROWTH_TICKS)
        if t._guard():
            if on_pct is None or off_pct is None:
                raise ExpectationFailed(
                    "could not read a Growth%% line for %s -- on=%r off=%r"
                    % (DEFAULT_BAND_PLANT, on_pct, off_pct))
            if on_pct <= off_pct * 1.5:
                raise ExpectationFailed(
                    "%s grew %.2f%% enabled vs %.2f%% disabled over %d "
                    "ticks -- expected the enabled pass to be clearly "
                    "ahead (default band is x4)"
                    % (DEFAULT_BAND_PLANT, on_pct, off_pct, GROWTH_TICKS))
        t.screenshot()

    with t.component("exempt_plant_unaffected_by_toggle", beyond_toggle=True):
        on_pct, off_pct = _measure_growth_delta(t, EXEMPT_PLANT, x, z, GROWTH_TICKS)
        if t._guard():
            if on_pct is None or off_pct is None:
                raise ExpectationFailed(
                    "could not read a Growth%% line for %s -- on=%r off=%r"
                    % (EXEMPT_PLANT, on_pct, off_pct))
            baseline = max(on_pct, off_pct, 1.0)
            if abs(on_pct - off_pct) > 0.25 * baseline:
                raise ExpectationFailed(
                    "%s (exempt) grew %.2f%% enabled vs %.2f%% disabled -- "
                    "expected them close (exempt plants ignore the toggle "
                    "entirely); tolerance is loose to allow for time-of-"
                    "day/temperature drift between the two sequential "
                    "passes, see module docstring item 1"
                    % (EXEMPT_PLANT, on_pct, off_pct))
        t.screenshot()
        t.set_setting(SETTINGS_TYPE, {"growthEnabled": True})
