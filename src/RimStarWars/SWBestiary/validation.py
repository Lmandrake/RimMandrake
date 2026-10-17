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
import fnmatch
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


def deploy_held(path):
    """True if src/DEPLOY_HOLD.txt holds this file back from the game (a held def is not live, so it cannot resolve)."""
    src = os.path.normpath(os.path.join(HERE, "..", ".."))
    rel = os.path.relpath(path, src).replace(os.sep, "/")
    try:
        lines = open(os.path.join(src, "DEPLOY_HOLD.txt"), encoding="utf-8").read().splitlines()
    except OSError:
        return False
    for ln in lines:
        glob = ln.split("#", 1)[0].strip()
        if glob and fnmatch.fnmatchcase(rel, glob):
            return True
    return False


def shipped_defs():
    """[(DefType, defName)] for every non-abstract, unconditional top-level def under Defs/ (a def carrying its own
    MayRequire is skipped: it legitimately stays out when its donor is absent; so is a file src/DEPLOY_HOLD.txt
    holds back from the game)."""
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml") and not deploy_held(os.path.join(dp, fn)):
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


DRAGONSNAKE = "RSW_Dragonsnake"
DRAGONSNAKE_ALBINO = "RSW_DragonsnakeAlbino"


def body_part_defs(body_def):
    """[part def name] of every part of the BodyDef named body_def anywhere under Defs/ (held files included);
    None if no such BodyDef parses."""
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            for el in ET.parse(os.path.join(dp, fn)).getroot():
                if el.tag == "BodyDef" and (el.findtext("defName") or "").strip() == body_def:
                    return [d.text.strip() for d in el.iter("def") if d.text]
    return None


def dragonsnake_body_plan_findings():
    """DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER: the canon dragonsnake is a quadruped (four Legs), the albino a
    limbless serpent (no Leg). Offline, deterministic: a body plan is a def fact, not a live one."""
    bad = []
    canon, albino = body_part_defs(DRAGONSNAKE), body_part_defs(DRAGONSNAKE_ALBINO)
    if canon is None or albino is None:
        return ["dragonsnake BodyDefs not found (canon %s, albino %s)" % (canon is not None, albino is not None)]
    if canon.count("Leg") != 4:
        bad.append("%s body has %d Legs, canon is a quadruped (4)" % (DRAGONSNAKE, canon.count("Leg")))
    if albino.count("Leg") != 0:
        bad.append("%s body has %d Legs, canon is limbless" % (DRAGONSNAKE_ALBINO, albino.count("Leg")))
    if "Hump" in albino:
        bad.append("%s body has a hood (Hump); the film creature has none" % DRAGONSNAKE_ALBINO)
    return bad


def static_checks():
    bad = list(dragonsnake_body_plan_findings())
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
    # TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE: the nest's on/off only works if the GenStepDef's gate key is the one the
    # Mod constructor registers (an unregistered key reads ENABLED, silently).
    nest = open(os.path.join(HERE, "Defs", "MapGeneration", "RSW_TaozinNest.xml"), encoding="utf-8").read()
    bm = open(os.path.join(HERE, "Source", "BeastMechanics", "RSW_BeastMechanicsSettings.cs"), encoding="utf-8").read()
    if "<gateKey>RSW.TaozinNest</gateKey>" not in nest:
        bad.append("RSW_TaozinNest.xml carries no RM_MechanicGateExtension gateKey RSW.TaozinNest")
    if 'RM_MechanicGates.Register("RSW.TaozinNest"' not in bm:
        bad.append("RSW_BeastMechanicsMod never registers gate RSW.TaozinNest")
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
    "innateAbilitiesEnabled", "scrapHoardingEnabled", "toxinDependenceEnabled",
    "albinoDragonsnakeEnabled",
    # scrapBirdBaseTheftEnabled / scrapThiefFlockEnabled were round-tripped below but missing here (static_checks
    # flagged both, 2026-10-17); the four taozin settings are TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE.
    "scrapBirdBaseTheftEnabled", "scrapThiefFlockEnabled",
    "taozinBrineTankEnabled", "taozinDaysPerJar", "taozinPaleDays", "taozinNestEnabled",
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
    "RSW_Tellurox",       # HelixTellurox (the PawnKindDef; RSW_TelluroxShell is its leather ITEM -- a spawn of it never lists as a pawn, load 13)
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


# ------------------------------------------------- beast mechanics behave (r28 left these as settings round-trips)
# RSW_BeastMechanicsProof (BeastMechanics DLL) spawns the real creature on the current map beside its scrap + nest
# and asks the SHIPPED job giver what it would do: on, and with the toggle off. Everything it spawns is destroyed
# before it returns. NOT proven: the job driver's carrying to completion (ticks). (Metal eating moved to
# CreatureBehaviors' metal_eater_seeks_its_metal with RM_Khorrak, KHORRAK_STEEL_DIET_TIER_1.)
_PROOF_TYPE = "RimMandrake.StarWars.SWBestiary.RSW_BeastMechanicsProof"


def _proof(t, method):
    r = t.bridge_call("jawa/static_call", type=_PROOF_TYPE, method=method, args="current")
    if not isinstance(r, dict):
        return {}, ""
    text = r.get("result")
    if text in (None, ""):
        text = "(static_call returned no result: success=%s message=%s)" % (r.get("success"), r.get("message") or r.get("error"))
    return dict(re.findall(r"(\w+)=(\S+)", str(text))), str(text)


@suite.chain("scrap_hoarder_carries_to_its_nest")
def scrap_hoarder_carries_to_its_nest(t):
    with t.component("a_rested_hoarder_takes_scrap_to_its_nest", toggle="scrapHoardingEnabled"):
        kv, text = _proof(t, "ProofHoard")
        if t.session is not None and not t.upstream_failed:
            if text.startswith("ERROR") or "hoarder" not in kv:
                raise ExpectationFailed("ProofHoard: %s" % text)
            want = "RSW_HoardScrap|target=%s|targetB=%s" % (kv.get("scrap"), kv.get("nest"))
            if kv.get("on") != want:
                raise ExpectationFailed("%s with %s near its %s got %s (want %s)"
                                        % (kv.get("hoarder"), kv.get("scrap"), kv.get("nest"), kv.get("on"), want))
            if kv.get("off") != "none":
                raise ExpectationFailed("scrapHoardingEnabled off still hoards: %s" % kv.get("off"))


@suite.chain("taozin_brine_tank_infuses_and_whitens")
def taozin_brine_tank_infuses_and_whitens(t):
    # TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE. RSW_BeastMechanicsProof.ProofBrineTank drives the shipped tank's own
    # TryAcceptThing + TickRare for 1.1 days twice (switch off, then on at 0.5 day/jar and 1 day to white) with 3 brine.
    # Expect: off moves nothing; on drops 2 jars, leaves 1 brine, whitens the grub, and vanilla TryGetAlternate answers 0.
    # NOT proven: the colonist carry job (needs ticks and a colonist), the white texture itself (art not installed yet).
    kv, text = {}, ""
    with t.component("tank_switch_off_does_nothing", toggle="taozinBrineTankEnabled"):
        kv, text = _proof(t, "ProofBrineTank")
        if t.session is not None and not t.upstream_failed:
            if text.startswith("ERROR") or kv.get("accepted") != "True":
                raise ExpectationFailed("ProofBrineTank: %s" % text)
            if (kv.get("off_jars"), kv.get("off_brine"), kv.get("off_pale")) != ("0", "3", "False"):
                raise ExpectationFailed("switched-off tank still worked: %s" % text)
    with t.component("tank_fills_jars_and_whitens_grub", toggle="taozinPaleDays"):
        if t.session is not None and not t.upstream_failed:
            want = {"jars": "2", "brine": "1", "pale": "True", "alternate": "0"}
            got = {k: kv.get(k) for k in want}
            if got != want:
                raise ExpectationFailed("brine tank got %s, want %s (%s)" % (got, want, text))


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


# ------------------------------------------------- DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER (2026-10-17)
# The canon dragonsnake (crocodilian quadruped) and its rare pale variant the albino dragonsnake (limbless serpent).
# Body plans are proven OFFLINE (dragonsnake_body_plan_findings, in static_checks). Live: both spawn, and the Greentide
# roster carries the albino exactly when its def is live and albinoDragonsnakeEnabled is on. The toggle is read once
# at startup (RSW_DragonsnakeAlbinoToggle), so a live flip proves nothing until restart: this reads the CURRENT value
# and checks the roster agrees with it. While the albino's def is held from deploy (no art yet) its rows read
# UNMEASURED, never PASS.
GREENTIDE = "RM_Greentide"


@suite.chain("dragonsnake_pair")
def dragonsnake_pair(t):
    t.clear_area(size=30)
    r = t.bridge_call("jawa/get_defs", defs="PawnKindDef/" + DRAGONSNAKE_ALBINO, fields="defName", limit=2)
    albino_live = isinstance(r, dict) and int(r.get("foundCount", 0)) == 1
    with t.component("canon_dragonsnake_spawns", beyond_toggle=True):
        t.spawn_pawn(DRAGONSNAKE, hostile=False)
        if t._guard() and DRAGONSNAKE not in _races_present(t):
            raise ExpectationFailed("%s spawned but is not listed afterwards" % DRAGONSNAKE)
    with t.component("albino_roster_follows_toggle", toggle="albinoDragonsnakeEnabled"):
        if t.session is None:
            return
        if not albino_live:
            _unmeasured(t, "%s is not live (held in src/DEPLOY_HOLD.txt until its art is installed)" % DRAGONSNAKE_ALBINO)
            return
        rs = t.bridge_call("jawa/mod_settings_field", typeName=BEAST_SETTINGS, action="get", field="albinoDragonsnakeEnabled")
        on = (rs or {}).get("value") if isinstance(rs, dict) else None
        if on is None:
            _unmeasured(t, "mod_settings_field could not read albinoDragonsnakeEnabled: %s" % str(rs)[:120])
            return
        on = str(on).lower() == "true"
        pr = t.bridge_call("jawa/biome_probe", biomes=GREENTIDE, animals=True, limit=200,
                           find=DRAGONSNAKE + "," + DRAGONSNAKE_ALBINO)
        rows = (((pr or {}).get("biomes") or [{}])[0].get("animals") or []) if isinstance(pr, dict) else []
        names = set(a.get("defName") for a in rows)
        if DRAGONSNAKE not in names:
            _unmeasured(t, "biome_probe %s does not list %s (control): cannot see the roster" % (GREENTIDE, DRAGONSNAKE))
            return
        if on and DRAGONSNAKE_ALBINO not in names:
            raise ExpectationFailed("albino toggle on but %s is not on the %s roster" % (DRAGONSNAKE_ALBINO, GREENTIDE))
        if not on and DRAGONSNAKE_ALBINO in names:
            raise ExpectationFailed("albino toggle off but %s is still on the %s roster" % (DRAGONSNAKE_ALBINO, GREENTIDE))
        if on:
            t.spawn_pawn(DRAGONSNAKE_ALBINO, hostile=False)
            if DRAGONSNAKE_ALBINO not in _races_present(t):
                raise ExpectationFailed("%s spawned but is not listed afterwards" % DRAGONSNAKE_ALBINO)
        t.screenshot()


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
