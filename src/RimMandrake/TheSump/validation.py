"""validation.py -- modcheck suite for RimMandrake: the Sump (mandrake.rm.thesump).

First north-star script (THE_SUMP_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/TheSump.md (DRAFT).
The planet's oil sump: a dusky tar basin biome (RM_TheSump) with its own flora and fauna rosters, a poured tar moat and fuse post,
the dig-shaft stratum lottery, the Deep Black mere gen step, the tar-pit belch incident and a permanent-dusk weather lock.
TEN FILES ARE HELD FROM DEPLOY by src/DEPLOY_HOLD.txt (flora, fauna, flora items, the tar-beast bulge and its registration,
moat fuse post, mouse filth, and the BiomeDef itself). The script reads that list: held defs are never expected live.

CHAINS
  defs_resolve       every def parsed from the mod's own XML that actually DEPLOYS resolves live; a control name reads
                     notFound; held defs are reported UNMEASURED-by-hold, never as failures.
  settings_roundtrip every `public static` bool/float of RM_TheSumpSettings: default / write / restore (numerics compared numerically).
  biome_wiring       UNMEASURED-by-hold: the BiomeDef is held (a live read would describe the stale game copy).
  map_mechanics      Deep Black mere, tar vault, moat/fuse post, dig lottery, tar beast, mouse trail, wick garden, dusk lock: UNMEASURED,
                     each naming whether the cause is the hold or a map/event the bridge cannot generate.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game. Nothing here has been run live.
"""
import fnmatch
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = "TheSump"
SETTINGS = "RimMandrake.TheSump.RM_TheSumpSettings"
BIOME = "RM_TheSump"
CONTROL_ABSENT = "ThingDef/TheSumpNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float|string)\s+(\w+)\s*=\s*([^;]+);")
_HOLD_FILE = os.path.join(HERE, "..", "..", "DEPLOY_HOLD.txt")


def held_globs():
    """Globs from src/DEPLOY_HOLD.txt that name this mod (relative to custom_patches/, '*' crosses '/')."""
    out = []
    if not os.path.isfile(_HOLD_FILE):
        return out
    for line in open(_HOLD_FILE, encoding="utf-8"):
        g = line.split("#", 1)[0].strip()
        if g.startswith(MOD + "/"):
            out.append(g)
    return out


HELD = held_globs()


def is_held(rel):
    return any(fnmatch.fnmatchcase(MOD + "/" + rel.replace(os.sep, "/"), g) for g in HELD)


def parse_defs():
    """([(DefType, defName)] deployed, [(DefType, defName, file)] held) from every non-abstract top-level def under Defs/."""
    deployed, held = [], []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, HERE)
            for el in ET.parse(full).getroot():
                nm = el.find("defName") if isinstance(el.tag, str) else None
                if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                    (held if is_held(rel) else deployed).append((el.tag, nm.text.strip(), rel) if is_held(rel) else (el.tag, nm.text.strip()))
    return sorted(set(deployed)), sorted(set(held))


SHIPPED, HELD_DEFS = parse_defs()


def settings_fields():
    """{name: type} for every scalar `public static` field of the settings class, read from the C# ({} when none)."""
    src = open(os.path.join(HERE, "Source", "RM_TheSumpMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_TheSumpSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if len(SHIPPED) + len(HELD_DEFS) < 20:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % (len(SHIPPED) + len(HELD_DEFS))]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    src = open(os.path.join(HERE, "Source", "RM_TheSumpMod.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RM_TheSump.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    kinds = set(ty for ty, _n in SHIPPED) | set(h[0] for h in HELD_DEFS)
    for need in ("BiomeDef", "ThingDef", "TerrainDef", "WeatherDef", "GameConditionDef", "IncidentDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    if not any(n == BIOME for _t, n in SHIPPED) and not any(h[1] == BIOME for h in HELD_DEFS):
        bad.append("BiomeDef %s missing" % BIOME)
    if not HELD:
        bad.append("DEPLOY_HOLD.txt names no TheSump file (hold parser sanity probe failed; ten files were held on 2026-10-03)")
    if not HELD_DEFS:
        bad.append("no held def parsed (hold parser or def parser is blind)")
    # SUMP_KETHREL_BUILD_1: defs, art, code seams (parsed from the source; no game needed)
    names = set(n for _t, n in SHIPPED) | set(h[1] for h in HELD_DEFS)
    for need in ("RM_Kethrel", "RM_KethrelShell", "RM_KethrelTree"):
        if need not in names:
            bad.append("%s is not defined" % need)
    for stg in range(4):
        for fc in ("south", "east", "north"):
            if not os.path.isfile(os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "RM_Kethrel", "RM_Kethrel_Stage%d_%s.png" % (stg, fc))):
                bad.append("kethrel stage %d %s sprite missing" % (stg, fc))
    kcs = open(os.path.join(HERE, "Source", "RM_Kethrel.cs"), encoding="utf-8").read()
    for cls in ("RM_CompKethrelShell", "RM_PawnRenderNode_KethrelBody", "RM_ITab_KethrelShell", "RM_CompProperties_KethrelShell"):
        if "class %s" % cls not in kcs:
            bad.append("class %s not found in RM_Kethrel.cs" % cls)
    kx = open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Kethrel.xml"), encoding="utf-8").read()
    for ref in ("RimMandrake.TheSump.RM_PawnRenderNode_KethrelBody", "RimMandrake.TheSump.RM_ITab_KethrelShell", "RimMandrake.TheSump.RM_CompProperties_KethrelShell"):
        if ref not in kx:
            bad.append("RM_Kethrel.xml does not reference %s" % ref)
    if "HarmonyLib" in kcs:
        bad.append("RM_Kethrel.cs uses Harmony: this assembly has no Harmony reference by design (the render tree names the node class)")
    if "class RM_BiomeWorker_TheSump" not in open(os.path.join(HERE, "Source", "RM_TheSumpBiome.cs"), encoding="utf-8").read():
        bad.append("biome worker class RM_BiomeWorker_TheSump not found")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", MOD + ".md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite(MOD)
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        if ty == "string":
            return str(a) == str(b)
        try:
            return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
        except (TypeError, ValueError):
            return False

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_deployed_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            missing, ok = [], 0
            for i in range(0, len(names), 40):      # batches: a long defs string risks the 30 s reply timeout
                chunk = names[i:i + 40]
                r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=60)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                missing.extend(r.get("notFound") or [])
                ok += int(r.get("foundCount", 0))
            if _live(t) and (missing or ok != len(names)):
                raise ExpectationFailed("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))

        with t.component("held_defs_are_unmeasured_by_hold", beyond_toggle=True):
            if HELD_DEFS and _live(t):
                _unmeasured(t, "%d defs in %d files are held from deploy by DEPLOY_HOLD.txt and cannot be in the live game "
                               "(e.g. %s); their absence is the hold, not a failure"
                            % (len(HELD_DEFS), len(set(h[2] for h in HELD_DEFS)), ", ".join(h[1] for h in HELD_DEFS[:4])))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                raise ExpectationFailed("settings probe found no field (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
                elif ty == "string":
                    new = "zz_probe" if str(old) != "zz_probe" else "zz_probe2"
                else:
                    new = str(float(old) + 1.0)
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("biome_wiring")
    def biome_wiring(t):
        with t.component("biome_densities_positive", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "BiomeDef %s is held from deploy by DEPLOY_HOLD.txt (LOAD_ERRORS_DEF_FIELDS_1: 'game copy left as-is'), "
                               "so any live read describes a stale game copy, not this repo's def" % BIOME)

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        with t.component("deep_black_mere_generated", toggle="deepBlackMereEnabled"):
            if _live(t):
                _unmeasured(t, 'a once-per-map unbroken tar expanse exists only on a map GENERATED as RM_TheSump with the toggle on (none with it off); the bridge cannot generate a map. Its gen step def (RUT_GenStep_DeepBlackMere) resolves in defs_resolve')
        with t.component("kethrel_wears_shell_and_steps_stage", toggle="kethrelShellEnabled"):
            if _live(t):
                _unmeasured(t, "needs a spawned RM_Kethrel beside tar with a dropped weapon, then a read of RM_CompKethrelShell stage and the RM_KethrelShell severity; no bridge tool reads the comp yet (a [Tool] returning Stage/LoadKg is the first thing to add)")
        with t.component("kethrel_molt_drops_everything", toggle="kethrelMoltLoadKg"):
            if _live(t):
                _unmeasured(t, "needs a loaded kethrel and a molt; the same missing [Tool] as the stage read")
        with t.component("kethrel_ignores_home_area_unless_allowed", toggle="kethrelTakeColonyProperty"):
            if _live(t):
                _unmeasured(t, "needs a home area, a weapon inside it and a kethrel beside it, with the toggle off then on")
        with t.component("tar_vault_seals_contents", toggle="tarVaultEnabled"):
            if _live(t):
                _unmeasured(t, "RM_Comp_TarVaultSeal lives in this assembly but the vault def RUT_TarVault ships in UtinniPatches, not in this mod's Defs/ (MEASURED: no def of this mod names the comp), so a read needs the campaign tier loaded plus a vault with a stored item and ticks")
        with t.component("biome_rarity_worldgen", toggle="biomeRarityFactor"):
            if _live(t):
                _unmeasured(t, 'rarity changes only planets generated afterwards; the world is frozen and the bridge cannot generate one')
        with t.component("poured_tar_moat_and_fuse_post", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'the moat ignition needs RUT_MoatFusePost, which is HELD from deploy (no art, DEPLOY_HOLD.txt) so it is UNMEASURED-by-hold, plus a poured moat and a fire')
        with t.component("dig_shaft_stratum_lottery", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_DigShaft and RUT_DigStratumTable deploy and resolve, but the lottery draw needs a built shaft, a worker and ticks on a Sump map')
        with t.component("tar_beast_bulge_set_piece", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_BeastBulge, its gen step and its registration patches are all HELD from deploy (DEPLOY_HOLD.txt): UNMEASURED-by-hold')
        with t.component("sump_mouse_filth_trail", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_Filth_MouseTrack is HELD from deploy (no art): UNMEASURED-by-hold')
        with t.component("wick_garden_crop", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_Plant_Wick resolves in defs_resolve; growth, glow and harvest need a sown plant and game days on a Sump map')
        with t.component("permanent_dusk_lock", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_SumpDuskLock/RUT_SumpWeather resolve, but their wiring patch targets the held BiomeDef; the lock holding the sky at dusk needs an RM_TheSump map')

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
