"""validation.py -- modcheck suite for RimUtinni UtinniPatches
(mandrake.rut.patches). list: full (walk doc's own line -- "this mod's
whole purpose is patching third-party defs across ~20 loadAfter mods; the
minimal list cannot exercise it").

THIS MOD IS ENORMOUS (300+ files under Defs/Patches/Textures) and the walk
doc (`design/validation_walks/RimUtinni/UtinniPatches.md`) already itemizes
its own flagship def read-backs in full (## must be true / the walk, steps
1-13) -- this suite does NOT re-walk all ~150 defs as chains, matching
every other suite in this backfill's convention (StructureInjections/
RustChrome/Antiquities/AshkarrWeatherSuite): validation.py chains prove
BEHAVIOR a bridge session can exercise; raw def-existence/log-cleanliness
is that separate walk-doc checklist's own job. What this suite DOES cover
is the mod's actual C# surface -- `Source/AmbientShrineGuardians.cs`,
`Source/GeothermalDensityField.cs`, `Source/PatchOperationSettingGate.cs`,
`Source/TwinkleFloraSpike.cs`, `Source/UtinniPatchesSettings.cs` -- every
one read whole before writing this, plus a small, representative sample of
the walk doc's own flagship defs (not all ~150).

WHAT THE C# ACTUALLY DOES, and why two of its four mechanisms are
UNCOVERED here rather than faked:

  * `SymbolResolver_Interior_AncientTemple_AmbientDoctrine` (Ambient Shrine
    Guardians) swaps an ancient-temple's mechanoid/fleshbeast/hive guardian
    for a sealed cryptosleep watch, ONLY on 8 named biomes, ONLY during
    real BaseGen map generation of a NEW ancient-temple map. The file's OWN
    header says it outright: "⛔ NOT PROVEN YET. A 0W/0E build proves the
    subclass compiles... it proves NOTHING about this resolver actually
    being picked at map generation... owes a quicktest map on one
    candidate biome... before this may be called done." This suite agrees
    and does not fake that proof: `modcheck.suite.TestContext` has no verb
    that generates a NEW map with a chosen biome (every verb here acts on
    `Find.CurrentMap`, already generated before the chain runs) -- the
    tooling this needs does not exist yet on this bridge.
  * `GenStep_ScatterGeysersDensityField` (Geothermal Density Field) scales
    steam-geyser count by `GeothermalDensityUtility.ComputeDensity`, a pure
    static function of world position -- but `ComputeDensity`/
    `CalculateFinalCount` are ONLY ever called from inside real map
    generation too, and neither is exposed by any bridge tool for a direct
    call. Same gap, same reason -- UNCOVERED here, not faked.
  * `PatchOperationSettingGate` (the `utinniWorldIconEnabled` gate on
    `Patches/UtinniWorldIcon.xml`) only ever runs at PATCH-APPLY time,
    which is over long before any bridge session starts (the class's own
    header: "LoadedModManager.LoadAllActiveMods... CreateModClasses()...
    BEFORE LoadModXML()/ApplyPatches()... A settings change therefore
    takes effect on the NEXT game start, not immediately"). Flipping
    `utinniWorldIconEnabled` mid-session via `t.set_setting` changes the
    static field but the def is already built either way -- so this is the
    same "worldgen/boot-time-only toggle" shape StructureInjections'
    `enabled` and RustChrome's `themeEnabled`(false-path) already document,
    and gets the same repo-level (not live) proof: `repo_checks` below
    confirms the XML actually wires `PatchOperationSettingGate` with
    `setting=utinniWorldIconEnabled` and a real `<match>` branch, which is
    everything a live session COULD prove about wiring that already ran.
  * `CompGlowPulse`/`RUT_PlantTwinkle` (Twinkle Flora Spike) is the one
    mechanism that IS live-drivable -- it is a timeboxed feasibility spike
    "not wired into any live biome or shipped plant" (its own header) but
    spawnable by hand, exactly as that header invites. No bridge tool
    reads a Thing's live rendered colour back, so this suite proves only
    that the comp survives real ticking across multiple `CompTickRare`
    (every 250 ticks) cycles without throwing or despawning the plant --
    not the actual colour-pulse math, which needs either a colour-read
    tool or the timeboxed item's own console measurement, neither of which
    exists here.

Still not proven / real gaps:
  1. Ambient Shrine Guardians and Geothermal Density Field: see above --
     both need a "generate a new map with a chosen biome" bridge tool that
     does not exist. Not a smoke-suite gap to paper over; it is this test
     harness's own missing capability.
  2. Walk doc step 6 ("jawa/world_info_get on the frozen Ash'karr worldfile
     ... never a freshly generated world") is NOT what
     `planet_name_patch_on_quicktest_world` below does -- a modcheck
     session's quicktest map necessarily sits on ITS OWN throwaway dev
     world (every suite in this backfill relies on that structurally), not
     the frozen campaign save. This chain proves the `NamerWorld`
     `rulesStrings` patch (walk step 5's def content) actually renames
     WHATEVER world gets generated, which is a stronger live claim than a
     def read-back but still not step 6's specific ask. Confirming the
     FROZEN save's own world.name is a full-campaign-load check, out of
     this suite's quicktest shape (see `rimworld-debug-testing` skill: a
     quicktest is not evidence about the real campaign).
  3. The Conditional-guarded third-party reflavors (`GalacticEmpire.xml`,
     `ForgottenArsenal.xml`, and every other `MayRequire`-guarded patch
     among the ~150 in `Patches/`) are NOT swept here -- whether
     `Neronix17.OuterRim.GalacticEmpire` etc. are actually active on
     whatever "full" list a given run uses is itself runtime-variable, and
     auditing every soft-dependent patch's both branches is the walk doc's
     own job (steps 8-9), not duplicated as ~20 more chains here.
"""
import os
import re

from modcheck import Suite, ExpectationFailed

suite = Suite("UtinniPatches")
suite.toggles = ["ambientShrineDoctrineEnabled", "geothermalDensityFieldEnabled",
                 "utinniWorldIconEnabled"]

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
_WORLDICON_PATCH = os.path.join(_MOD_DIR, "Patches", "UtinniWorldIcon.xml")
_TWINKLE_DEF = os.path.join(_MOD_DIR, "Defs", "ThingDefs_Plants",
                            "RUT_TwinkleSpikeTestPlant.xml")

TWINKLE_PLANT = "RUT_TwinkleSpikeTestPlant"


def _live(t):
    """Distinguishes a real chain run from the offline declaration probe --
    same idiom as AshkarrWeatherSuite/validation.py."""
    return t.session is not None and not t.upstream_failed


@suite.chain("repo_checks")
def repo_checks(t):
    """Pure repo checks against the XML/Defs text itself -- no bridge call,
    runs even under the offline declaration probe. Covers the two
    boot/patch-time-only mechanisms (module docstring) that a live session
    cannot re-observe after the fact."""
    t.clear_area(size=8)

    with t.component("world_icon_gate_wired_correctly", beyond_toggle=True):
        with open(_WORLDICON_PATCH, "r", encoding="utf-8") as f:
            xml = f.read()
        if 'Class="RimMandrake.Utinni.UtinniPatches.PatchOperationSettingGate"' not in xml:
            raise ExpectationFailed(
                "UtinniWorldIcon.xml no longer wires PatchOperationSettingGate")
        if "<setting>utinniWorldIconEnabled</setting>" not in xml:
            raise ExpectationFailed(
                "UtinniWorldIcon.xml's PatchOperationSettingGate is missing "
                "<setting>utinniWorldIconEnabled</setting> -- PatchOperationSettingGate.ApplyWorker "
                "only recognises that exact string (named-switch, not reflection, by design)")
        if "<match" not in xml:
            raise ExpectationFailed(
                "UtinniWorldIcon.xml's gate has no <match> branch -- nothing would "
                "apply even with the setting on")

    with t.component("twinkle_flora_spike_only_wired_to_its_own_test_plant",
                      beyond_toggle=True):
        # The comp's own header claims RUT_TwinkleSpikeTestPlant.xml is the
        # ONLY def referencing CompProperties_GlowPulse -- confirmed by
        # grepping every Defs/ThingDefs_Plants file, not trusted from the
        # comment alone.
        plants_dir = os.path.join(_MOD_DIR, "Defs", "ThingDefs_Plants")
        referencing = []
        for name in os.listdir(plants_dir):
            if not name.endswith(".xml"):
                continue
            with open(os.path.join(plants_dir, name), "r", encoding="utf-8") as f:
                if "CompProperties_GlowPulse" in f.read():
                    referencing.append(name)
        if referencing != ["RUT_TwinkleSpikeTestPlant.xml"]:
            raise ExpectationFailed(
                "expected exactly RUT_TwinkleSpikeTestPlant.xml to reference "
                "CompProperties_GlowPulse, found %r -- either the spike got wired "
                "into a real plant (update this suite's live coverage) or the "
                "test def was renamed/removed" % referencing)


def naboo_fish_checks():
    """NABOO_FISH_TO_TWILIGHT_1 (offline, XML parsed): mee/faa are off the Scald and on the Twilight
    Sea as floor residents (wildAnimals node names, no <li>) with their catches in fishTypes.
    Live spawn/catch is UNMEASURED here (needs the seabed floor generator; SEABED_PER_SEA_FLOORS_1)."""
    import xml.etree.ElementTree as ET
    bad = []
    pdir = os.path.join(_MOD_DIR, "Patches")

    def ops(fn):
        return ET.parse(os.path.join(pdir, fn)).getroot().findall("Operation")

    def added(fn, biome, sub):
        out = []
        for op in ops(fn):
            for o in [op] + list(op.iter("match")):
                xp = o.findtext("xpath") or ""
                if 'defName="%s"]/%s' % (biome, sub) in xp.replace("Defs/", "/Defs/", 1) or xp.endswith('"%s"]/%s' % (biome, sub)):
                    v = o.find("value")
                    if v is not None:
                        out += [(c.tag, c.text) for c in v]
        return out

    # Owner, Scald sheet 2026-10-05: the sando aqua monster left the Scald too, so the Scald's
    # Utinni wildAnimals patch is gone; nothing Star Wars may ride onto RM_TheScald any more.
    if os.path.exists(os.path.join(pdir, "WildAnimals_TheScald.xml")):
        bad.append("WildAnimals_TheScald.xml is back (the Scald carries no Star Wars resident)")
    tw = dict(added("WildAnimals_TwilightSea.xml", "RM_TwilightSea", "wildAnimals"))
    for n in ("RSW_Mee", "RSW_Faa", "RSW_SandoAquaMonster"):
        if n not in tw:
            bad.append("%s missing from RM_TwilightSea wildAnimals" % n)
    # only a <li> inside a <value> discards a roster entry; <mods><li> is FindMod's own syntax
    if any(True for op in ops("WildAnimals_TwilightSea.xml") for v in op.iter("value") for _ in v.iter("li")):
        bad.append("<li> in WildAnimals_TwilightSea.xml (discards the entry)")
    c1 = dict(added("WildAnimals_TwilightSea.xml", "RM_TwilightSea", "fishTypes/saltwater_Common"))
    c2 = dict(added("WildAnimals_TwilightSea.xml", "RM_TwilightSea", "fishTypes/saltwater_Uncommon"))
    if "RSW_MeeCatch" not in c1:
        bad.append("RSW_MeeCatch not added to Twilight saltwater_Common")
    if "RSW_FaaCatch" not in c2:
        bad.append("RSW_FaaCatch not added to Twilight saltwater_Uncommon")
    return bad


@suite.chain("naboo_fish_in_twilight")
def naboo_fish_in_twilight(t):
    bad = naboo_fish_checks()
    if bad:
        raise ExpectationFailed("; ".join(bad))


@suite.chain("twinkle_flora_spike_survives_ticking")
def twinkle_flora_spike_survives_ticking(t):
    """The one live-drivable mechanism (module docstring). Spawns the
    timeboxed test plant and steps past several `CompTickRare` cycles
    (every 250 ticks) -- proves the comp does not throw/despawn the plant
    across real ticking, NOT the actual colour-pulse math (no bridge tool
    reads a Thing's rendered colour back). `t.screenshot()` at the end is
    the best available evidence for a human glance at the pulse itself."""
    t.clear_area(size=10)
    t.spawn(TWINKLE_PLANT, count=1, at="point")

    with t.component("plant_survives_multiple_glow_pulse_ticks", beyond_toggle=True):
        r = t.bridge_call("jawa/list_things", defName=TWINKLE_PLANT)
        rows = (r or {}).get("things") or []
        if _live(t) and not rows:
            raise ExpectationFailed(
                "no %s found via jawa/list_things right after spawning it"
                % TWINKLE_PLANT)

        t.wait_ticks(1200)  # ~5 CompTickRare cycles (250 ticks each)

        r2 = t.bridge_call("jawa/list_things", defName=TWINKLE_PLANT)
        rows2 = (r2 or {}).get("things") or []
        if _live(t) and not rows2:
            raise ExpectationFailed(
                "%s is gone after 1200 ticks of CompTickRare pulsing -- "
                "CompGlowPulse or RUT_PlantTwinkle.Graphic may be throwing "
                "and getting the plant destroyed/de-registered" % TWINKLE_PLANT)
        t.screenshot()


@suite.chain("planet_name_patch_on_quicktest_world")
def planet_name_patch_on_quicktest_world(t):
    """`JawaWorld_Name.xml` replaces RulePackDef `NamerWorld`'s
    `rulesStrings` unconditionally (walk doc bullet 2) -- this proves the
    LIVE EFFECT on whatever world this modcheck session's own quicktest map
    sits on, not the frozen campaign save (module docstring gap #2: that is
    a full-campaign-load check, out of a quicktest's scope per the
    `rimworld-debug-testing` skill)."""
    with t.component("namer_world_patch_renames_the_live_world", beyond_toggle=True):
        r = t.bridge_call("jawa/world_info_get")
        if _live(t):
            info = (r or {}).get("info") or {}
            name = info.get("name")
            if name != "Ash'karr":
                raise ExpectationFailed(
                    "jawa/world_info_get's world name is %r, expected exactly "
                    "\"Ash'karr\" (U+0027 apostrophe) from JawaWorld_Name.xml's "
                    "unconditional NamerWorld patch: %r" % (name, r))


@suite.chain("mindstone_gallery")
def mindstone_gallery(t):
    """LANTERNDEEPS_MINDSTONE_GALLERY_BUILD_1: run on a LANTERN DEEP map that has a Shard-mind. The gallery
    placement threads mindstone veins into the rock face around it. Not proven here: that a freshly generated
    Deep carries it (the genSteps patch) -- enter a new Deep and count RUT_MindstoneVein; and that mining one
    yields RUT_Mindstone (vanilla mineableThing)."""
    with t.component("mindstone_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RUT_Mindstone", "ThingDef/RUT_MindstoneVein", "GenStepDef/RUT_LanternDeepMindstoneGallery"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    with t.component("gallery_veins_placed", toggle="mindstoneGalleryEnabled"):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Utinni.UtinniPatches.RUT_MindstoneGalleryProof",
                          method="ProofGallery", args="")
        res = str((r or {}).get("result", ""))
        if t._guard() and (not res.startswith("veins=") or res.startswith("veins=0")):
            raise ExpectationFailed("no mindstone veins placed: %r" % (r,))


# ---- UTINNIPATCHES_COVERAGE_GAPS_1 static bars (no bridge) -------------------------------------------------
_GATE_CLASS = "RimMandrake.Utinni.UtinniPatches.PatchOperationSettingGate"
_CORE_DEFS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs"


def setting_gate_problems(mod_dir=None):
    """(problems, gates_seen). Every PatchOperationSettingGate in Patches/ (any depth) names a <setting> the
    C# switch handles (an unknown name logs Log.Error and returns false = a red 'Patch operation failed'),
    carries a match or nomatch branch, and the case reads a public static bool on UtinniPatchesSettings
    that ExposeData Scribes under the same key (else the toggle never persists)."""
    import re
    import xml.etree.ElementTree as ET
    mod_dir = mod_dir or _MOD_DIR
    src = open(os.path.join(mod_dir, "Source", "PatchOperationSettingGate.cs"), encoding="utf-8").read()
    cases = dict(re.findall(r'case\s+"(\w+)"\s*:\s*on\s*=\s*UtinniPatchesSettings\.(\w+)\s*;', src))
    st = open(os.path.join(mod_dir, "Source", "UtinniPatchesSettings.cs"), encoding="utf-8").read()
    bad, seen = [], 0
    if not cases:
        return ["blind parse: no switch cases read from PatchOperationSettingGate.cs"], 0
    for root, _d, files in os.walk(os.path.join(mod_dir, "Patches")):
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            p = os.path.join(root, fn)
            for el in ET.parse(p).getroot().iter():
                if el.get("Class") != _GATE_CLASS:
                    continue
                seen += 1
                s = (el.findtext("setting") or "").strip()
                where = "%s gate '%s'" % (fn, s)
                if s not in cases:
                    bad.append("%s: not a case of the C# switch (red 'unknown setting' + patch failed)" % where)
                    continue
                if el.find("match") is None and el.find("nomatch") is None:
                    bad.append("%s: no match/nomatch branch -- gates nothing" % where)
                field = cases[s]
                if not re.search(r"public\s+static\s+bool\s+%s\b" % field, st):
                    bad.append("%s: UtinniPatchesSettings.%s is not a public static bool" % (where, field))
                if not re.search(r'Scribe_Values\.Look\(ref\s+%s\s*,\s*"%s"' % (field, field), st):
                    bad.append("%s: %s is not Scribed under its own key -- the toggle never persists" % (where, field))
    if seen == 0:
        bad.append("blind parse: no PatchOperationSettingGate found under Patches/")
    return bad, seen


def infestation_ban_problems(core_defs=_CORE_DEFS, mod_dir=None):
    """None if Core is unreachable (UNMEASURED), else problems. The planet-wide ban is a bare
    PatchOperationReplace on Core IncidentDef Infestation/baseChance: Core must still carry that node (a
    Replace that matches nothing logs red), must not carry baseChanceWithRoyalty (which would win over
    baseChance), and our value must be 0 with no other src patch touching that incident's chance."""
    import glob
    import xml.etree.ElementTree as ET
    mod_dir = mod_dir or _MOD_DIR
    if not os.path.isdir(core_defs):
        return None
    inc = None
    for p in glob.glob(os.path.join(core_defs, "**", "*.xml"), recursive=True):
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in r.findall("IncidentDef"):
            if (d.findtext("defName") or "").strip() == "Infestation":
                inc = d
    bad = []
    if inc is None:
        return ["sanity: Core IncidentDef Infestation not found under %s" % core_defs]
    if inc.find("baseChance") is None:
        bad.append("Core Infestation has no <baseChance>: the Replace matches nothing (red patch error)")
    if inc.find("baseChanceWithRoyalty") is not None:
        bad.append("Core Infestation now carries baseChanceWithRoyalty: zeroing baseChance no longer bans it")
    ops = ET.parse(os.path.join(mod_dir, "Patches", "Infestation_PlanetwideBan.xml")).getroot().findall("Operation")
    vals = [(o.get("Class"), o.findtext("xpath"), o.findtext("value/baseChance")) for o in ops]
    if vals != [("PatchOperationReplace", 'Defs/IncidentDef[defName="Infestation"]/baseChance', "0")]:
        bad.append("Infestation_PlanetwideBan.xml is not the single Replace baseChance=0: %r" % (vals,))
    src_root = os.path.abspath(os.path.join(mod_dir, "..", ".."))
    for p in glob.glob(os.path.join(src_root, "**", "Patches", "**", "*.xml"), recursive=True):
        if os.path.basename(p) == "Infestation_PlanetwideBan.xml":
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        if 'IncidentDef[defName="Infestation"]' in txt:
            bad.append("another patch touches Core Infestation: %s" % os.path.relpath(p, src_root))
    return bad


# ---- UTINNIPATCHES_COVERAGE_GAPS_1 (offline half, round 41) -----------------------------------------------------
# Every non-held, non-inactive def this mod ships is IN the load-14 def dump and carries the label its XML authors.
# (The greatbole ladder chain moved to src/RimMandrake/Greentide/validation.py with its comp, GREENTIDE_BASE_PORT_BUILD_1.)
import json as _json


def held_globs(hold_file=None):
    """Globs of UtinniPatches/... paths in src/DEPLOY_HOLD.txt (undeployed ON PURPOSE, so absent from any dump)."""
    hold_file = hold_file or os.path.join(_MOD_DIR, "..", "..", "DEPLOY_HOLD.txt")
    out = []
    for ln in open(hold_file, encoding="utf-8"):
        body = ln.split("#", 1)[0].strip()
        if body.startswith("UtinniPatches/"):
            out.append(body[len("UtinniPatches/"):])
    return out


def shipped_def_rows(mod_dir=None):
    """[(defType, defName, label-or-None, guard-pkgs, relpath)] for every non-abstract top-level def under Defs/."""
    import fnmatch  # noqa: F401
    import xml.etree.ElementTree as ET
    from modcheck import shipped_defs as SD
    mod_dir = mod_dir or _MOD_DIR
    out = []
    for root, dirs, files in os.walk(os.path.join(mod_dir, "Defs")):
        dirs.sort()
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            rel = os.path.relpath(os.path.join(root, fn), mod_dir).replace(os.sep, "/")
            for el in ET.parse(os.path.join(root, fn)).getroot():
                if not isinstance(el.tag, str) or el.get("Abstract", "").lower() == "true":
                    continue
                name = (el.findtext("defName") or "").strip()
                if name:
                    g = SD.guard_of(el)
                    pk = [x for x in g.replace("anyof:", "").replace(";", ",").split(",") if x]
                    out.append((el.tag, name, (el.findtext("label") or "").strip() or None, pk, rel, g.startswith("anyof:") or ";anyof:" in g))
    return out


def dump_presence_findings(rows_defs, dump_by_type, active_pkgs, held):
    """(checked, skipped dict, findings). A def is LOST when it is not held, its type is dumped, every non-DLC guard
    package is active (an anyOf guard needs one), and it is absent from the dump. Label drift is a finding too."""
    import fnmatch
    checked, skipped, bad = 0, {"held": 0, "guard inactive": 0, "type not dumped": 0}, []
    for ty, name, label, pk, rel, is_any in rows_defs:
        if any(fnmatch.fnmatch(rel, g) for g in held):
            skipped["held"] += 1
            continue
        d = dump_by_type.get(ty)
        if d is None:
            skipped["type not dumped"] += 1
            continue
        satisfied = (any(p in active_pkgs for p in pk) if is_any else all(p in active_pkgs for p in pk)) if pk else True
        if not satisfied:
            skipped["guard inactive"] += 1
            continue
        checked += 1
        row = d.get(name)
        if row is None:
            bad.append("%s %s (%s) is not in the dump" % (ty, name, rel))
        elif label is not None and str(row.get("label")) != label:
            bad.append("%s %s label %r in the dump, %r in the XML" % (ty, name, row.get("label"), label))
    return checked, skipped, bad


def _dump_inputs():
    import game_paths as GP
    base = GP.DEF_DUMP
    man = _json.load(open(os.path.join(base, "manifest.json")))
    active = set((m.get("packageId") or "").lower() for m in man.get("mods", []))
    return base, active


def _dump_types(base, wanted):
    out = {}
    for ty in wanted:
        p = os.path.join(base, "defs", ty + ".json")
        out[ty] = dict((r["defName"], r) for r in _json.load(open(p))["defs"]) if os.path.isfile(p) else None
    return out




@suite.chain("defs_vs_dump_static")
def defs_vs_dump_static(t):
    """Offline: the ~430 defs this mod ships are in the load-14 def dump (held / guard-inactive ones named, not passed) and
    carry their XML label. UNMEASURED without a readable dump."""
    with t.component("shipped_defs_are_in_the_dump_with_their_labels", beyond_toggle=True):
        try:
            base, active = _dump_inputs()
            rows_defs = shipped_def_rows()
            dump = _dump_types(base, sorted(set(r[0] for r in rows_defs)))
        except Exception as e:
            t.upstream_failed = True
            t.upstream_reason = "UNMEASURED: no readable def dump (%s)" % e
            return
        held = held_globs()
        if len(rows_defs) < 300 or len(held) < 5 or "mandrake.rut.patches" not in active or not dump.get("ThingDef"):
            raise ExpectationFailed("blind parse: %d defs, %d hold globs, patches mod active=%s" % (len(rows_defs), len(held), "mandrake.rut.patches" in active))
        checked, skipped, bad = dump_presence_findings(rows_defs, dump, active, held)
        if checked < 300:
            raise ExpectationFailed("only %d defs were checkable (skipped %s)" % (checked, skipped))
        if bad:
            raise ExpectationFailed("%d of %d checked defs lost or drifted (skipped %s): %s" % (len(bad), checked, skipped, "; ".join(bad[:5])))





@suite.chain("settings_gates_static")
def settings_gates_static(t):
    """Static: settings-gated patch ops (PatchOperationSettingGate) all name a handled, Scribed toggle."""
    with t.component("every_setting_gate_names_a_handled_scribed_toggle", beyond_toggle=True):
        bad, seen = setting_gate_problems()
        if bad:
            raise ExpectationFailed("%d gate problem(s) over %d gate(s): %s" % (len(bad), seen, bad))


@suite.chain("infestation_ban_static")
def infestation_ban_static(t):
    """Static: the planet-wide Infestation ban lands on Core's current IncidentDef and is the only hand on it.
    Live readback (get_defs IncidentDef/Infestation baseChance == 0) is the deploy-side bar."""
    with t.component("infestation_ban_lands_on_core_baseChance", beyond_toggle=True):
        bad = infestation_ban_problems()
        if bad is None:
            t._why = "Core Defs unreachable from this machine (%s)" % _CORE_DEFS
            t.upstream_failed = True
            t.upstream_reason = "UNMEASURED: " + t._why
            return
        if bad:
            raise ExpectationFailed("; ".join(bad))


@suite.chain("mindstone_matrix_recipes")
def mindstone_matrix_recipes(t):
    """MINDSTONE_MATRIX_KINDLED_BUILD_1: RUT_Mindstone -> RUT_MindstoneMatrix -> RSW_DW_Head_Mindstone, both at
    RSW_DW_ReassemblyHarness. The XML half runs offline; the def read-back needs Droidworks loaded. Not proven
    here: a pawn completing both bills (needs a bill pipeline), and the assembly half, which is Droidworks'
    own mindstone_head_wiring chain."""
    import xml.etree.ElementTree as ET
    with t.component("matrix_recipes_shaped", beyond_toggle=True):
        root = ET.parse(os.path.join(_MOD_DIR, "Defs", "RecipeDefs", "RUT_MindstoneMatrix_Recipes.xml")).getroot()
        want = {"RUT_CutMindstoneMatrix": ("RUT_Mindstone", "RUT_MindstoneMatrix"),
                "RUT_CaseMindstoneHead": ("RUT_MindstoneMatrix", "RSW_DW_Head_Mindstone")}
        for rd in root.findall("RecipeDef"):
            name = rd.findtext("defName")
            if name not in want:
                continue
            ing, prod = want.pop(name)
            if rd.get("MayRequire") != "mandrake.rsw.droidworks":
                raise ExpectationFailed("%s lacks MayRequire=mandrake.rsw.droidworks on its root" % name)
            if [li.text for li in rd.find("recipeUsers")] != ["RSW_DW_ReassemblyHarness"]:
                raise ExpectationFailed("%s is not on RSW_DW_ReassemblyHarness" % name)
            firsts = [li.find("filter").find("thingDefs")[0].text for li in rd.find("ingredients")]
            if ing not in firsts or [p.tag for p in rd.find("products")] != [prod]:
                raise ExpectationFailed("%s: ingredients %r / products %r" % (name, firsts, [p.tag for p in rd.find("products")]))
        if want:
            raise ExpectationFailed("recipes missing: %r" % sorted(want))
    with t.component("matrix_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RUT_MindstoneMatrix", "RecipeDef/RUT_CutMindstoneMatrix", "RecipeDef/RUT_CaseMindstoneHead"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
