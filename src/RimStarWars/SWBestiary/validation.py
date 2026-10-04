"""validation.py -- modcheck suite for RimStarWars: SW Bestiary
(mandrake.rsw.swbestiary).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run SWBestiary

(environment: minimal + this mod's own HARD `<modDependencies>` --
`Ludeon.RimWorld.Odyssey`, `sarg.alphaanimals`, `mlie.starwarsanimalcollection`
-- the mod cannot even load without them, per its own About.xml.)

THE WALK DOC (`design/validation_walks/RimStarWars/SWBestiary.md`) IS
SEVERELY STALE -- confirmed by reading `About.xml` whole, not guessed. Its
header says "deps: none (Ludeon.RimWorld only) -- content-only, no
assemblies, no patches" and only describes the ORIGINAL absorption (Bantha,
Jerba, 8 ex-Jurassic dinosaurs, 589 SoundDefs). The CURRENT mod has since
absorbed FIVE MORE sibling mods into this same folder (About.xml's own
"MECHANICAL_FAUNA_MERGE_WAVE_A" section): SeaBeasts (18 creatures),
Livestock (Karrask/Onnik/Moornak + live ThingComps),
HelixTellurox, JawaIkee (a live ThingComp + ModSettings), BeastNorm/
SeasWaterline patches -- plus SAND_SWIMMERS_MOD_1 and
LIVESTOCK_STARTER_TRIO_1 afterward. It now ships `Patches/` (four
subfolders), TWO live `Assemblies/*.dll` (`JawaIkee.dll`,
`RimMandrakeLivestockRSW.dll`) with TWO `ModSettings` classes, and three
real hard `modDependencies` beyond vanilla. This suite therefore covers (a)
the walk's own original scope (still valid, re-verified against
`ThingDefs_Karrask.xml`/`PawnKindDefs_*.xml` etc.) and (b) the two
ModSettings-gated mechanisms the walk never mentions at all
(`RSW_JawaIkeeSettings`, `RSW_LivestockSettings` -- both read whole from
`Source/JawaIkee/` and `Source/Livestock/`). It does NOT attempt to spawn or
mechanism-test every absorbed species from the other waves (SeaBeasts'
18, HelixTellurox, ShipVermin, the sand-swimmer trio) -- that needs the walk
doc itself rewritten first (a BENCH/owner-facing job, not this backfill
pass's), and `newly_absorbed_species_spawn_cleanly` below only spot-checks
that a representative one from each wave still spawns, as a floor above
the walk's own scope, not a rewrite of it.

Grounded in the mod's actual source, read whole before writing this:
`Source/JawaIkee/RSW_JawaIkeeSettings.cs` (one toggle, `ikeeThoughtEnabled`)
and `Source/JawaIkee/ThoughtWorker_IkeeNearby.cs` (`RSW_Jawa_IkeeWatching`:
stage 0/comforted if the pawn's xenotype is in `IkeeToleranceExtension.
tolerantXenotypes`, stage 1/unsettled otherwise, checked against any
"AA_Eyeling" pawn within `radius` cells -- `AA_Eyeling` confirmed as BOTH
the ThingDef defName the C# compares against AND a real PawnKindDef defName
via `RimUtinni/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml`'s own
`<animalKind>AA_Eyeling</animalKind>`, not guessed); `Source/Livestock/
RSW_LivestockSettings.cs` (`kilnBellyEnabled`/`kilnCooldownMultiplier` for
`CompKilnBelly`, plus the moornak fields) and `Source/Livestock/CompKilnBelly.cs`.
(The skarnix's light-aversion comp and its two settings moved to the Abyss mod.)

A REAL, CONFIRMED ENVIRONMENT GAP in the Ikee mechanism: every entry in
`IkeeToleranceExtension.tolerantXenotypes` (`Thought_IkeeWatching.xml`) is
`MayRequire="mandrake.rsw.starwarsraces"`, which is only a `loadAfter` on
this mod, never a hard dependency -- so on this suite's minimal environment
the tolerant list is EMPTY. Stage 0 (comforted) is therefore structurally
UNREACHABLE here regardless of which pawn is tested; `ikee_mood_thought_
toggle` below asserts stage 1 (unsettled, -5) for a plain Colonist and
documents why stage 0 cannot be proven on this environment, rather than
silently only testing the reachable half.

WHAT THIS SUITE CANNOT PROVE, and why -- `CompKilnBelly.cs` carries the comment in its own source,
"NOT live-verified this pass (offline build only)", which this suite
inherits rather than overriding with an invented pass:
  - `kilnBellyEnabled`/`kilnCooldownMultiplier`: the real cycle needs THREE
    correctly-spaced feedings of `RSW_KilnClay` across up to a full in-game
    day (`doseWindowTicks` = 60,000 ticks) with a 4-day (`fireCooldownTicks`
    = 240,000 ticks) cooldown between batches -- `doseTicks`/
    `nextFireReadyTick` are private fields with no getter, no debug action
    and no log line anywhere in this comp, so there is no read-back channel
    to confirm a dose registered even if this suite fed the animal and
    waited. Settings-only coverage (write + independent read-back).
  - Nothing exercises `Patches/BeastNorm` (targets the
    `mlie.starwarsanimalcollection` donor's own defNames, not this mod's)
    or `Patches/SeasWaterline`/`ProximityHatch` -- these are `PatchOperation`
    wiring with no runtime mechanism of their own to test beyond "did the
    mod load clean", which a successful suite run already demonstrates.

Still not proven / likely first-live-run corrections:
  1. Whether `jawa/spawn_pawn` can place a pawn of a PawnKindDef whose race
     ThingDef sets `wildBiomes` far outside the quicktest map's own biome
     (e.g. `RSW_Reefback`/SeaBeasts are aquatic) without a legality refusal
     -- not measured; if any of `newly_absorbed_species_spawn_cleanly`'s
     seven spawns fails for a biome/terrain reason rather than a load
     defect, that is the likely cause and is a spawn-tool limitation, not
     a mod defect.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CONTROL_ABSENT = "ThingDef/RSW_BestiaryNoSuchDef_ZZ"
BEAST_SETTINGS = "RimMandrake.StarWars.SWBestiary.RSW_BeastMechanicsSettings"
# SWBESTIARY_COVERAGE_GAPS_1: every Mod Settings class this assembly ships, and its source file.
SETTINGS_SOURCES = (
    ("RimMandrake.StarWars.JawaIkee.RSW_JawaIkeeSettings", "JawaIkee/RSW_JawaIkeeSettings.cs"),
    ("RimMandrake.StarWars.Livestock.RSW_LivestockSettings", "Livestock/RSW_LivestockSettings.cs"),
    (BEAST_SETTINGS, "BeastMechanics/RSW_BeastMechanicsSettings.cs"),
)
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def shipped_defs():
    """[(DefType, defName)] for every non-abstract, unconditional top-level def under Defs/ (a def carrying its own
    MayRequire is skipped: it legitimately stays out when its donor is absent)."""
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if (nm is not None and nm.text and el.get("Abstract", "").lower() != "true"
                            and not el.get("MayRequire") and not el.get("MayRequireAnyOf")):
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


def settings_fields():
    """{(class, field): (type, default)} for every scalar public static field of every settings class."""
    out = {}
    for cls, rel in SETTINGS_SOURCES:
        src = open(os.path.join(HERE, "Source", rel), encoding="utf-8").read()
        body = re.sub(r"//[^\n]*", "", src.split("ExposeData", 1)[0])
        for m in _FIELD.finditer(body):
            out[(cls, m.group(2))] = (m.group(1), m.group(3).strip())
    return out


SHIPPED = shipped_defs()
PLAIN = [p for p in SHIPPED if "." not in p[0]]


def static_checks():
    bad = []
    if len(SHIPPED) < 200:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if len(fields) < 9:
        return ["only %d settings fields parsed (sanity probe failed)" % len(fields)]
    for cls, rel in SETTINGS_SOURCES:
        src = open(os.path.join(HERE, "Source", rel), encoding="utf-8").read()
        after = src.split("ExposeData", 1)[1] if "ExposeData" in src else ""
        for (c, f), _v in fields.items():
            if c != cls:
                continue
            if '"%s"' % f not in after:
                bad.append("%s.%s is not Scribed" % (cls.rsplit(".", 1)[1], f))
            ui = src.split("void DoWindowContents", 1)[-1] if "void DoWindowContents" in src else ""
            if not re.search(r"\b%s\b" % f, ui):
                bad.append("%s.%s has no settings-window control" % (cls.rsplit(".", 1)[1], f))
    toggled = set(suite.toggles) if "suite" in globals() and suite is not None else set()
    if toggled:
        for (_c, f) in fields:
            if f not in toggled:
                bad.append("settings field %s is not in suite.toggles (never asserted)" % f)
    return bad


try:
    from modcheck import Suite, ExpectationFailed
except ImportError:
    sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
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

suite = Suite("SWBestiary")
suite.toggles = [
    "ikeeThoughtEnabled",
    "kilnBellyEnabled", "kilnCooldownMultiplier",
    "moornakGriefEnabled", "moornakReleaseDelayMultiplier",
    "metalEatingEnabled", "innateAbilitiesEnabled", "scrapHoardingEnabled", "toxinDependenceEnabled",
]

IKEE_SETTINGS = "RimMandrake.StarWars.JawaIkee.RSW_JawaIkeeSettings"
LIVESTOCK_SETTINGS = "RimMandrake.StarWars.Livestock.RSW_LivestockSettings"

# Walk's own original scope (still valid, re-read against the shipped Defs).
CORE_SPECIES = ["RSW_Bantha", "RSW_Jerba", "RSW_Baseopsis"]

# One representative species per absorption wave the walk doc never covers.
NEWLY_ABSORBED_SPECIES = [
    "RSW_Karrask",        # Livestock
    "RSW_Onnik",          # LIVESTOCK_STARTER_TRIO_1 -- CompKilnBelly
    "RSW_Reefback",       # SeaBeasts / Colossi
    "RSW_TelluroxShell",  # HelixTellurox
    "RSW_Mynock",         # ShipVermin
    "RSW_Blarth",         # MIASMA_ROUND2_IMPORTS_1 (live: UNMEASURED)
    "RSW_Blixus",
    "RSW_Bogwing",        # flyer: flight verified by state read only, never a live flight hunt
    "RSW_MarshHaunt",
]


def _races_present(t):
    r = t.bridge_call("jawa/list_pawns", limit=500)
    rows = (r or {}).get("pawns") or []
    return [p.get("kind") or p.get("def") for p in rows]


@suite.chain("core_species_spawn")
def core_species_spawn(t):
    """Walk steps 9-12, unchanged: Bantha (herd/pack), Jerba (new content,
    desert pack/milk beast) and Baseopsis (spot-checks the absorbed
    ex-Jurassic wave actually generates, not just parses)."""
    t.clear_area(size=30)
    with t.component("core_species_spawn_and_present", beyond_toggle=True):
        for kind in CORE_SPECIES:
            t.spawn_pawn(kind, hostile=False)
        present = _races_present(t)
        if t._guard():
            missing = [k for k in CORE_SPECIES if k not in present]
            if missing:
                raise ExpectationFailed(
                    "spawned %r but jawa/list_pawns is missing %r afterward "
                    "(present: %r)" % (CORE_SPECIES, missing, present))
        t.screenshot()


@suite.chain("newly_absorbed_species_spawn_cleanly")
def newly_absorbed_species_spawn_cleanly(t):
    """A floor ABOVE the walk doc's own scope (see module docstring on how
    stale it is) -- one species per wave the walk never mentions, spot-
    checking that the absorption did not silently break loading/spawning
    for any of them. Not a mechanism test of any of their own comps."""
    t.clear_area(size=40)
    with t.component("newly_absorbed_species_present", beyond_toggle=True):
        for kind in NEWLY_ABSORBED_SPECIES:
            t.spawn_pawn(kind, hostile=False)
        present = _races_present(t)
        if t._guard():
            missing = [k for k in NEWLY_ABSORBED_SPECIES if k not in present]
            if missing:
                raise ExpectationFailed(
                    "spawned %r but jawa/list_pawns is missing %r afterward "
                    "(present: %r) -- see module docstring's note on possible "
                    "biome/legality refusals for aquatic SeaBeasts species"
                    % (NEWLY_ABSORBED_SPECIES, missing, present))
        t.screenshot()


@suite.chain("ikee_mood_thought_toggle")
def ikee_mood_thought_toggle(t):
    """Behavioral proof of `ikeeThoughtEnabled` -- the only mechanism this
    mod's Ikee settings gate. See module docstring: stage 0 (comforted) is
    structurally unreachable on this environment (the tolerant xenotype
    list is entirely MayRequire-gated on a mod not in the minimal+deps
    set), so this only proves stage 1 (unsettled) appears when enabled and
    disappears when the toggle is off -- which is exactly what
    `ikeeThoughtEnabled=false`'s own tooltip promises ("the ikee has no
    mood effect on anyone")."""
    t.clear_area(size=20)
    x, z = t.anchor
    t.spawn_pawn("AA_Eyeling", hostile=False)
    colonist = t.spawn_pawn("Colonist", hostile=False, beyond=[(x, z)])

    with t.component("ikee_thought_present_when_enabled", toggle="ikeeThoughtEnabled"):
        t.set_setting(IKEE_SETTINGS, {"ikeeThoughtEnabled": True})
        r = t.bridge_call("jawa/pawn_thoughts", pawn=colonist)
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed("jawa/pawn_thoughts failed: %r" % r)
            thoughts = r.get("thoughts") or []
            mine = next((th for th in thoughts if th.get("def") == "RSW_Jawa_IkeeWatching"), None)
            if mine is None:
                raise ExpectationFailed(
                    "RSW_Jawa_IkeeWatching not among the colonist's thoughts with "
                    "ikeeThoughtEnabled=true and an AA_Eyeling nearby: %r" % thoughts)
            if mine.get("stage") != 1:
                raise ExpectationFailed(
                    "RSW_Jawa_IkeeWatching fired at stage %r, expected stage 1 "
                    "(unsettled) -- a plain Colonist cannot be on the tolerant "
                    "xenotype list even when it is populated, and it is empty "
                    "on this environment regardless (see module docstring): %r"
                    % (mine.get("stage"), mine))
        t.screenshot()

    with t.component("ikee_thought_absent_when_disabled", toggle="ikeeThoughtEnabled"):
        t.set_setting(IKEE_SETTINGS, {"ikeeThoughtEnabled": False})
        r = t.bridge_call("jawa/pawn_thoughts", pawn=colonist)
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed("jawa/pawn_thoughts failed: %r" % r)
            thoughts = r.get("thoughts") or []
            mine = next((th for th in thoughts if th.get("def") == "RSW_Jawa_IkeeWatching"), None)
            if mine is not None:
                raise ExpectationFailed(
                    "RSW_Jawa_IkeeWatching still present with ikeeThoughtEnabled=false: %r"
                    % mine)
        t.set_setting(IKEE_SETTINGS, {"ikeeThoughtEnabled": True})


@suite.chain("livestock_settings_are_live_flippable")
def livestock_settings_are_live_flippable(t):
    """No behavioral proof beyond write + independent read-back -- see
    module docstring's "WHAT THIS SUITE CANNOT PROVE" section for exactly
    why (both comps' OWN source comments already say "NOT live-verified
    this pass", and neither has any bridge/log read-back channel at all)."""

    with t.component("kiln_belly_enabled_flips", toggle="kilnBellyEnabled"):
        t.set_setting(LIVESTOCK_SETTINGS, {"kilnBellyEnabled": False})
        t.set_setting(LIVESTOCK_SETTINGS, {"kilnBellyEnabled": True})

    with t.component("kiln_cooldown_multiplier_flips", toggle="kilnCooldownMultiplier"):
        t.set_setting(LIVESTOCK_SETTINGS, {"kilnCooldownMultiplier": 2.0})
        t.set_setting(LIVESTOCK_SETTINGS, {"kilnCooldownMultiplier": 1.0})


def _unmeasured(t, why):
    t.upstream_reason = "UNMEASURED: " + why
    t.upstream_failed = True


@suite.chain("defs_resolve")
def defs_resolve(t):
    """SWBESTIARY_COVERAGE_GAPS_1: every unconditional def parsed from Defs/ survives the loader live (a def can
    parse and still be discarded: a missing type, an inactive donor class). A control name must read notFound."""
    with t.component("control_probe_can_say_absent", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
        if t.session is not None:
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
            if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                raise ExpectationFailed("control def reads as present: %r" % r)
    with t.component("every_shipped_def_resolves", beyond_toggle=True):
        names = ["%s/%s" % p for p in PLAIN]
        missing, ok = [], 0
        for i in range(0, len(names), 20):
            chunk = names[i:i + 20]
            r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=40)
            if t.session is None:
                continue
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("get_defs failed: %r" % r)
            missing.extend(r.get("notFound") or [])
            ok += int(r.get("foundCount", 0))
        if t.session is not None and (missing or ok != len(names)):
            raise ExpectationFailed("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))


def _make_roundtrip(cls, field, ty, default):
    def chain(t):
        with t.component("%s_round_trips" % field, toggle=field):
            if t.session is None:
                return
            r = t.bridge_call("jawa/mod_settings_field", typeName=cls, action="get", field=field)
            old = (r or {}).get("value") if isinstance(r, dict) else None
            if old is None:
                _unmeasured(t, "mod_settings_field could not read %s: %s" % (field, str(r)[:120]))
                return
            if ty == "bool":
                new = "False" if str(old).lower() == "true" else "True"
            else:
                new = str(float(old) + 1.0)
            try:
                t.set_setting(cls, {field: new})   # set_setting verifies by an independent read-back
            finally:
                t.set_setting(cls, {field: old})
    chain.__name__ = "settings_%s" % field
    return chain


# The five toggles the audit found never touched (the three older ones keep their own chains above).
for (_cls, _f), (_ty, _dv) in sorted(settings_fields().items()):
    if _f in ("ikeeThoughtEnabled", "kilnBellyEnabled", "kilnCooldownMultiplier"):
        continue
    suite.chain("settings_%s_round_trips" % _f)(_make_roundtrip(_cls, _f, _ty, _dv))


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
