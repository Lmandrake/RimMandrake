"""validation.py -- modcheck suite for RimUtinni: Weather Suite (Ash'karr)
(mandrake.rut.weathersuite).

Pure-Defs + patch content mod: no Source/, no Assemblies/, no ModSettings
class -- `src/RimUtinni/AshkarrWeatherSuite/` holds only About/About.xml,
one geometry Defs file (`Defs/WeatherGeometryDefs/
WeatherGeometryDefs_Ashkarr.xml`) and one flavor-text patch
(`Patches/AshkarrWeather_FolkSigns.xml`), both read in full before writing
this. `suite.toggles = []`, every component `beyond_toggle=True`. The two
Mod Options toggles that actually gate behaviour here
(`WeatherSuiteSettings.terminatorFrontEnabled`,
`.nightsideAuroraEnabled`/`.auroraMaxBrightnessEnabled`) live on the ENGINE
mod's own `WeatherSuiteSettings` class in `mandrake.rm.weathersuite`
(`WeatherSuiteHook.cs`, read in full before writing this) -- this companion
carries none of its own.

WHAT THIS MOD IS: wires `mandrake.rm.weathersuite`'s generic terminator-
band/nightside-band engine (`WeatherGeometryUtility.ArcFromSubstellar`,
a great-circle arc test off ONE loaded `PlanetGeometryDef` -- `Ambient
Geometry.ActiveGeometry` takes `AllDefsListForReading.FirstOrDefault()`, so
this mod being the only one shipping that def type is load-bearing, not
incidental) onto Ash'karr's real, frozen substellar point and band arcs,
plus folk-sign flavor text appended to five vanilla `WeatherDef`
descriptions. A HARD `modDependency` on `mandrake.rm.weathersuite` (both the
`PlanetGeometryDef` type itself and `WeatherGeometryUtility` live there) --
this suite's environment is minimal+mandrake.rm.weathersuite, per the walk
doc's own line.

Exact facts, read directly from the two Defs/Patch files, not guessed:
  - Exactly one `PlanetGeometryDef`: `RUT_WS_AshkarrGeometry`
    (substellarLat=0, substellarLon=0, terminatorBandMinArc=63,
    terminatorBandMaxArc=117, nightsideBandMinArc=117). The file's own
    header cites the exact provenance for every number (the_one_map.md's
    reconciliation, ASHKARR_WORLDMAP_tiles.csv row 0 cross-check,
    WeatherSuiteHook.cs's own comment on why nightsideBandMinArc sits at
    the terminator band's own outer edge) -- none of these five numbers are
    computed by this suite; they are asserted as shipped.
  - Exactly 5 `PatchOperationConditional`-wrapped `Replace`s on
    `WeatherDef.description`: Clear, Fog, DryThunderstorm, SnowGentle,
    SnowHard -- confirmed by direct grep of the patch file (5 `<xpath>`
    pairs, one Conditional wrapper + one Replace each). Each Replace only
    fires if the target `description` node already exists (true for all
    five, being vanilla Core WeatherDefs, always loaded) -- so on THIS
    mod's own environment these are not expected to no-op, unlike
    AshkarrFlora's genuinely-inert defensive patch.
  - The patch file's own header explicitly proves no collision with
    FIRE_ECOLOGY_LOOP_1's `BiomeDef[defName="ZBiome_Grasslands"]/
    baseWeatherCommonalities` patch -- confirmed directly (not merely
    copied from the header): `grep -n "ZBiome_Grasslands\\|
    baseWeatherCommonalities" AshkarrWeather_FolkSigns.xml` finds both
    strings ONLY inside the file's own explanatory `<!-- -->` comment
    (lines 23/26), never inside an actual `<xpath>` element (the ten real
    `<xpath>` lines all target `WeatherDef[defName=...]/description`).
    `no_biome_collision` below asserts this distinction directly rather
    than trusting the comment's own claim.
  - The five folk-sign sentences are deliberately silent about "static
    seasons" or "glass storms" (the deep design doc's v2 system, not yet
    built) -- `no_v2_mechanic_promised` below greps for those exact phrases
    and fails if either ever appears, since promising a mechanic that does
    not exist would be a lie the flavor text tells the player, per the
    patch file's own header.

WHY MOST COMPONENTS ARE DEF READ-BACK / LOG-FREE REPO CHECKS: this mod
carries zero C# of its own -- the actual terminator-band GameCondition,
nightside aurora gating and forecaster comp all live in
`mandrake.rm.weathersuite`. This suite's job is the same as every other
Defs-only RimUtinni companion in this backfill: prove the DATA is exactly
what was authored and wired to the right engine type, not that the engine
mechanism itself works (that belongs to `mandrake.rm.weathersuite`'s own
validation.py, not yet written as of this pass -- check before assuming it
exists).

Still not proven / real gaps:
  1. No live map is spawned in the terminator or nightside band here -- the
     actual `GameCondition_Flashstorm`/`GameCondition_DarkAuroraMax`
     behaviour and `MapComponent_TerminatorBand`'s one-per-map letter are
     entirely the engine mod's mechanism to prove, not this Defs-only
     companion's.
  2. `jawa/weather_get` (walk doc step 10, confirming the WeatherDecider
     pathway is healthy with the new geometry def present) is included
     below, but only as a smoke check that the call succeeds -- it cannot
     independently prove the geometry def specifically is what keeps that
     pathway healthy, only that nothing about this mod's presence broke it.
  3. No pixel/visual check of the terminator storm-wall or dark-side aurora
     rendering at the correct band is attempted -- the walk doc's own final
     line defers this to a human pass (MOD_HUMAN_EXPLORATION_PASS_1), and
     this suite agrees: none of the bridge tools found here can inspect
     sky-rendering appearance.
"""
import os

from modcheck import Suite, ExpectationFailed

suite = Suite("AshkarrWeatherSuite")
suite.toggles = []   # no Source/, no ModSettings of its own -- every component beyond_toggle

GEOMETRY_DEF = "RUT_WS_AshkarrGeometry"

GEOMETRY_EXPECT = {
    "substellarLat": "0", "substellarLon": "0",
    "terminatorBandMinArc": "63", "terminatorBandMaxArc": "117",
    "nightsideBandMinArc": "117",
}

# Verbatim substrings from AshkarrWeather_FolkSigns.xml, not guessed.
FOLK_SIGN_EXPECT = {
    "Clear": "Folk sign: a still, colorless sky",
    "Fog": "Folk sign: fog this thick",
    "DryThunderstorm": "Folk sign: count the gap",
    "SnowGentle": "Folk sign: snow this gentle",
    "SnowHard": "Folk sign: when hard snow comes on fast",
}

FORBIDDEN_V2_PHRASES = ["static season", "glass storm"]

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
_PATCH_PATH = os.path.join(_MOD_DIR, "Patches", "AshkarrWeather_FolkSigns.xml")


def _live(t):
    """Distinguishes a real chain run from the offline declaration probe."""
    return t.session is not None and not t.upstream_failed


@suite.chain("repo_checks")
def repo_checks(t):
    """Pure repo checks against the patch file's own text, no bridge call --
    run even under the offline declaration probe."""
    t.clear_area(size=8)
    with open(_PATCH_PATH, "r", encoding="utf-8") as f:
        xml = f.read()

    with t.component("no_biome_collision", beyond_toggle=True):
        import re
        xpath_lines = re.findall(r"<xpath>([^<]*)</xpath>", xml)
        bad = [x for x in xpath_lines
              if "ZBiome_Grasslands" in x or "BiomeDef" in x
              or "baseWeatherCommonalities" in x]
        if bad:
            raise ExpectationFailed(
                "AshkarrWeather_FolkSigns.xml has an <xpath> targeting the "
                "Grasslands biome or baseWeatherCommonalities -- collides "
                "with FIRE_ECOLOGY_LOOP_1's own patch: %r" % bad)
        if not xpath_lines:
            raise ExpectationFailed("no <xpath> elements found at all -- patch file empty?")

    with t.component("no_v2_mechanic_promised", beyond_toggle=True):
        lowered = xml.lower()
        found = [p for p in FORBIDDEN_V2_PHRASES if p in lowered]
        if found:
            raise ExpectationFailed(
                "folk-sign flavor text mentions v2-only mechanic(s) %r that "
                "do not exist yet -- the patch file's own header calls this "
                "a lie the flavor text would tell the player" % found)

    with t.component("exactly_five_weather_defs_patched", beyond_toggle=True):
        import re
        targets = sorted(set(re.findall(
            r'WeatherDef\[defName="([^"]+)"\]/description', xml)))
        expected = sorted(FOLK_SIGN_EXPECT)
        if targets != expected:
            raise ExpectationFailed(
                "expected exactly the 5 WeatherDefs %r patched, found %r"
                % (expected, targets))


@suite.chain("planet_geometry_readback")
def planet_geometry_readback(t):
    """The one PlanetGeometryDef, exact values copied verbatim from
    WeatherGeometryDefs_Ashkarr.xml. Also confirms it loaded from THIS mod
    and is not shadowed (walk doc step 9's own reasoning): since
    WeatherGeometryUtility.ActiveGeometry takes
    AllDefsListForReading.FirstOrDefault(), a SECOND PlanetGeometryDef
    anywhere in the loaded mod list would silently make this one
    unreachable depending on load order -- this component cannot detect
    that (jawa/get_def resolves by name, not "which one wins"), see gap."""
    t.clear_area(size=8)

    with t.component("geometry_def_matches_shipped_xml", beyond_toggle=True):
        # jawa/get_def (singular) only hand-models ThingDef/PawnKindDef/
        # BiomeDef under `extra` (GetDef, JawaBenchTerrainTools.cs) -- for a
        # custom Def subclass like PlanetGeometryDef it returns extra=null,
        # extraModelled=false, and there is no "resolved" or "fields" key on
        # its response at all, so the original call here always raised
        # ExpectationFailed regardless of the def's real content. jawa/get_defs
        # (plural)'s `fields=` parameter is the documented escape hatch for
        # reading an arbitrary def type's own scalar fields.
        r = t.bridge_call(
            "jawa/get_defs", defs="PlanetGeometryDef/%s" % GEOMETRY_DEF,
            fields=",".join(GEOMETRY_EXPECT))
        if _live(t):
            rows = (r or {}).get("defs") or []
            row = next((d for d in rows if d.get("defName") == GEOMETRY_DEF), None)
            fields = (row or {}).get("fields") or {}
            if not fields:
                raise ExpectationFailed(
                    "jawa/get_defs(PlanetGeometryDef/%s) returned no fields: %r"
                    % (GEOMETRY_DEF, r))
            bad = []
            for field, expect in GEOMETRY_EXPECT.items():
                got = fields.get(field)
                if str(got) != str(expect):
                    bad.append("%s: expected %r, got %r" % (field, expect, got))
            if bad:
                raise ExpectationFailed(
                    "RUT_WS_AshkarrGeometry field mismatch: %s" % "; ".join(bad))
        t.screenshot()


@suite.chain("folk_sign_descriptions_readback")
def folk_sign_descriptions_readback(t):
    """All 5 patched WeatherDefs' RESOLVED (post-patch) descriptions contain
    their expected folk-sign sentence -- the check a matched-nothing
    Conditional cannot fake (walk doc step 8's own reasoning): if the
    Replace never fired, the resolved description would still be vanilla's
    plain mechanical text with no "Folk sign:" substring at all."""
    t.clear_area(size=8)
    names = list(FOLK_SIGN_EXPECT)

    with t.component("all_five_folk_signs_present", beyond_toggle=True):
        pairs = ";".join("WeatherDef/%s" % n for n in names)
        r = t.bridge_call("jawa/get_defs", defs=pairs, fields="description")
        if _live(t):
            rows = {row.get("defName"): row for row in (r or {}).get("defs") or []}
            not_found = (r or {}).get("notFound") or []
            bad = []
            if not_found:
                bad.append("not found (vanilla WeatherDefs missing?): %r" % not_found)
            for name, expect_substr in FOLK_SIGN_EXPECT.items():
                row = rows.get(name)
                if row is None:
                    continue
                desc = str((row.get("fields") or {}).get("description") or "")
                if expect_substr not in desc:
                    bad.append("%s.description: expected %r in %r"
                              % (name, expect_substr, desc))
            if bad:
                raise ExpectationFailed(
                    "folk-sign patch mismatch: %s" % "; ".join(bad))
        t.screenshot()


@suite.chain("weather_pathway_healthy")
def weather_pathway_healthy(t):
    """Walk doc step 10: the WeatherDecider pathway these WeatherDefs feed
    reports a current weather/condition with no error. Smoke check only --
    see module docstring gap #2: this proves nothing about this mod's
    presence broke the pathway, not that the geometry def specifically
    keeps it healthy."""
    t.clear_area(size=8)

    with t.component("weather_get_succeeds", beyond_toggle=True):
        r = t.bridge_call("jawa/weather_get")
        if _live(t):
            row = r or {}
            # WeatherGet's own failure path returns Fail(), whose shared
            # helper (JawaBenchTerrainTools.cs) shapes a refusal as
            # {success=false, message, details} -- there is no "error" key
            # anywhere in this bridge's response family, so the original
            # `"error" in row` guard could never be true and this component
            # never actually failed on a genuine error.
            if not row.get("success", True):
                raise ExpectationFailed(
                    "jawa/weather_get reported an error: %r" % row)
        t.screenshot()
