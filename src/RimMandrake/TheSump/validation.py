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
    def names_pre():
        return set(n for _t, n in SHIPPED) | set(h[1] for h in HELD_DEFS)
    kinds = set(ty for ty, _n in SHIPPED) | set(h[0] for h in HELD_DEFS)
    for need in ("BiomeDef", "ThingDef", "TerrainDef", "WeatherDef", "GameConditionDef", "IncidentDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    if not any(n == BIOME for _t, n in SHIPPED) and not any(h[1] == BIOME for h in HELD_DEFS):
        bad.append("BiomeDef %s missing" % BIOME)
    # The 2026-10-03 hold was lifted (art existed); an empty hold list is now the correct state.
    if not SHIPPED:
        bad.append("no shipped def parsed (def parser is blind)")
    # SUMP_TAR_BEAST_BUILD_1: defs, art, code seams (EnvironmentalHazards owns the C#)
    for need in ("RM_TarBeast", "RM_TarBeastPace", "RM_ThinkTree_TarBeast"):
        if need not in names_pre():
            bad.append("%s is not defined" % need)
    for fc in ("south", "east", "north"):
        if not os.path.isfile(os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "RM_TarBeast", "RM_TarBeast_%s.png" % fc)):
            bad.append("tar beast %s sprite missing" % fc)
    ehsrc = os.path.join(HERE, "..", "EnvironmentalHazards", "Source", "RM_CompTarBeast.cs")
    if os.path.isfile(ehsrc):
        ehs = open(ehsrc, encoding="utf-8").read()
        for cls in ("RM_CompTarBeast", "RM_JobGiver_TarBeastEat", "RM_CompBulgePumpWake"):
            if "class %s" % cls not in ehs:
                bad.append("class %s not found in RM_CompTarBeast.cs" % cls)
    else:
        bad.append("EnvironmentalHazards/Source/RM_CompTarBeast.cs missing")
    bx = open(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RUT_BeastBulge.xml"), encoding="utf-8").read()
    if "<li>RM_TarBeast</li>" not in bx or "Thrumbo</li>" in bx:
        bad.append("RUT_BeastBulge does not emerge RM_TarBeast (placeholder Thrumbo still wired?)")
    # SUMP_SOLVENT_WAKE_BUILD_1: the pour order's seams (the C# lives in EnvironmentalHazards)
    pour_src = os.path.join(HERE, "..", "EnvironmentalHazards", "Source", "RM_TarSolventPour.cs")
    if os.path.isfile(pour_src):
        ps = open(pour_src, encoding="utf-8").read()
        for cls in ("RM_CompBulgeSolventPour", "RM_MapComponent_TarSolventWake", "FloatMenuOptionProvider_PourSolvent", "JobDriver_RM_PourSolvent"):
            if "class %s" % cls not in ps:
                bad.append("class %s not found in RM_TarSolventPour.cs" % cls)
        if '"Shkaar"' not in ps or '"Zizzik"' not in ps:
            bad.append("solvent pour no longer applies both god deltas (Shkaar + Zizzik)")
    else:
        bad.append("EnvironmentalHazards/Source/RM_TarSolventPour.cs missing")
    if "CompProperties_BulgeSolventPour" not in bx:
        bad.append("RUT_BeastBulge carries no CompProperties_BulgeSolventPour")
    else:
        for sd in re.findall(r"<li>(RM_\w*TarSolvent)</li>", bx):
            found = False
            for dp, _dn, fs in os.walk(os.path.join(HERE, "..", "..")):
                if any(f.endswith(".xml") and "<defName>%s</defName>" % sd in open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read() for f in fs):
                    found = True
                    break
            if not found:
                bad.append("solvent %s named on the bulge is defined nowhere in src/" % sd)
    jd = os.path.join(HERE, "..", "EnvironmentalHazards", "Defs", "JobDefs", "RM_JobDefs_StationEater.xml")
    if "<defName>RM_PourSolvent</defName>" not in open(jd, encoding="utf-8").read():
        bad.append("JobDef RM_PourSolvent missing")
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
    # SUMP_CAPSTAN_TURRET_BUILD_1: the turret def, its two-part art, the class and its proof
    cap = os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_CapstanTurret.xml")
    if not os.path.isfile(cap) or "RimMandrake.TheSump.RM_CapstanTurret" not in open(cap, encoding="utf-8").read():
        bad.append("RM_CapstanTurret def missing or not on its class")
    for part in ("Base", "Top"):
        if not os.path.isfile(os.path.join(HERE, "Textures", "Things", "Building", "CapstanTurret", "RM_CapstanTurret_%s.png" % part)):
            bad.append("capstan %s art missing" % part)
    ccs = open(os.path.join(HERE, "Source", "RM_CapstanTurret.cs"), encoding="utf-8").read()
    for need in ("class RM_CapstanTurret", "class RM_CapstanTurretProof", "RM_CompTetherPull", "IRM_TetherPullHost", "capstanMaxMass"):
        if need not in ccs:
            bad.append("RM_CapstanTurret.cs lacks %s" % need)
    if "HarmonyLib" in ccs:
        bad.append("RM_CapstanTurret.cs uses Harmony: this assembly has no Harmony reference")
    # SUMP_CAPSTAN_LOCAL_RECIPE_1: two defs on one abstract parent, the local one paid in Sump bitumen and seepwax
    cx = ET.parse(cap).getroot()
    caps = {d.findtext("defName"): d for d in cx.iter("ThingDef") if d.findtext("defName")}
    pr = caps.get("RM_CapstanTurret_PitRigged")
    if "RM_CapstanTurret" not in caps or pr is None:
        bad.append("capstan needs both RM_CapstanTurret and RM_CapstanTurret_PitRigged")
    elif pr.find("costList/RM_Bitumen") is None or pr.find("costList/RM_Seepwax") is None:
        bad.append("RM_CapstanTurret_PitRigged must cost RM_Bitumen (tar-glass bearings) and RM_Seepwax (cable packing)")
    # SUMP_CAPSTAN_DRAWJOINT_RESEARCH_1: the row is locked behind studying two draw-joints found in the dig strata
    rp = open(os.path.join(HERE, "Defs", "ResearchProjectDefs", "RM_CapstanTurret.xml"), encoding="utf-8").read()
    if "<li>RUT_PreservedDrawJoint</li>" not in rp.split("<requiredAnalyzed>")[-1].split("</requiredAnalyzed>")[0]:
        bad.append("RM_CapstanTurret research does not require studying RUT_PreservedDrawJoint")
    dj = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Items", "RUT_PreservedDrawJoint.xml")).getroot()
    # WEBWORK_TRACTION_LANCE_BUILD_1: the comp is now the vanilla analyzable's grant-research subclass.
    ana = dj.find(".//li[@Class='RimMandrake.CreatureBehaviors.RM_CompProperties_AnalyzableGrantResearch']")
    if ana is not None and "RM_Research_TractionLance" not in [x.text for x in ana.iter("li")]:
        bad.append("RUT_PreservedDrawJoint no longer grants RM_Research_TractionLance (the Sump door to the lance)")
    if ana is None or ana.findtext("analysisRequiredRange") != "2~2" or ana.findtext("destroyedOnAnalyzed") != "true":
        bad.append("RUT_PreservedDrawJoint must be analyzable twice and consumed (spec: two preserved draw-joints)")
    lot = ET.parse(os.path.join(HERE, "Defs", "LotteryTableDefs", "RUT_DigStratumTable.xml")).getroot()
    if not any(r.findtext("thingDef") == "RUT_PreservedDrawJoint" for r in lot.iter("li")):
        bad.append("RUT_DigStratumTable never yields RUT_PreservedDrawJoint")
    # SUMP_FREE_TIER_MOVE_BUILD_1: the tar kit ships in this free mod, never in the campaign tier
    moved = ("RM_Tarred", "RM_TarredThought", "RM_WeakTarSolvent", "RM_StrongTarSolvent", "RM_ThrummelSeepwax",
             "RM_TarRuinedGoods", "RM_TarVault", "RM_GaslightLamp", "RM_TarGas", "RM_Duckboards", "RM_Glasswalk",
             "RM_GaslightChemistry", "RM_TarRendering", "RM_ScrubTarred", "RM_Bitumen")
    for need in moved:
        if need not in names:
            bad.append("moved tar-kit def %s is not defined in this mod" % need)
    alltext = ""
    for dp, _dn, fs in os.walk(os.path.join(HERE, "Defs")):
        for f in fs:
            if f.endswith(".xml"):
                alltext += open(os.path.join(dp, f), encoding="utf-8").read()
    for dp, _dn, fs in os.walk(os.path.join(HERE, "Patches")):
        for f in fs:
            if f.endswith(".xml"):
                alltext += open(os.path.join(dp, f), encoding="utf-8").read()
    body = re.sub(r"<from>\w+</from>", "", re.sub(r"<!--.*?-->", "", alltext, flags=re.S))
    for leak in sorted(set(re.findall(r">(RUT_(?:Tarred|Sumpgas|TarVault|GaslightLamp|Duckboards|Glasswalk|Bitumen|\w*TarSolvent|ThrummelSeepwax|TarRuinedGoods|GaslightChemistry|TarRendering|ScrubTarred)\w*)<", body))):
        bad.append("free mod still references campaign def %s" % leak)
    if re.search(r'MayRequire="mandrake\.rut', body):
        bad.append("free mod carries a campaign-tier MayRequire")
    if "<hediffDef>RM_Tarred</hediffDef>" not in body:
        bad.append("RM_TheSump's carried-filth extension does not name RM_Tarred")
    if "RimMandrake.TheSump.CompProperties_TarVaultSeal" not in body:
        bad.append("no def carries the tar vault seal comp")
    for tex in ("Building/RM_TarVault/RM_TarVault", "Building/Furniture/RM_GaslightLamp/RM_GaslightLamp",
                "Item/Resource/RM_TarGas/RM_TarGas", "Item/Resource/RM_Bitumen/RM_Bitumen",
                "Item/Resource/RM_WeakTarSolvent/RM_WeakTarSolvent", "Item/Resource/RM_StrongTarSolvent/RM_StrongTarSolvent",
                "Item/Resource/RM_ThrummelSeepwax/RM_ThrummelSeepwax", "Item/Resource/RM_TarRuinedGoods/RM_TarRuinedGoods"):
        if not os.path.isfile(os.path.join(HERE, "Textures", "Things", tex + ".png")):
            bad.append("moved texture Things/%s.png missing" % tex)
    ab = open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read()
    deps = re.search(r"<modDependencies>(.*?)</modDependencies>", ab, re.S)
    if deps and "helixien" in deps.group(1).lower():
        bad.append("TheSump About.xml depends on Helixien (unioned into all of Baroque Biomes)")
    alias = os.path.join(HERE, "Defs", "Misc", "RM_SumpTierMove_Aliases.xml")
    if not os.path.isfile(alias):
        bad.append("back-compat alias def missing")
    else:
        al = open(alias, encoding="utf-8").read()
        for old in ("RUT_Tarred", "RUT_TarVault", "RUT_GaslightLamp", "RUT_Sumpgas", "RUT_Glasswalk", "RUT_Duckboards", "RUT_Bitumen"):
            if "<from>%s</from>" % old not in al:
                bad.append("no back-compat alias from %s" % old)
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
                _unmeasured(t, "BiomeDef %s has 0 tiles until the one terminal repaint (BIOME_PAINT_ONCE_AT_THE_END_1), so densities are not exercised on a real map" % BIOME)

    def _proof(t, method):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.TheSump.RM_TheSumpProof", method=method, args="current")
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    def _kv(text):
        return dict(m.groups() for m in re.finditer(r"(\w+)=(\S+)", text))

    @suite.chain("tar_vault")
    def tar_vault(t):
        """THESUMP_COVERAGE_GAPS_1: RM_TheSumpProof.ProofVault on the current map drives the real seal comp
        (ScanNow = what CompTick runs every scanIntervalTicks) and ExtractOne. Not proven: the tarVaultEnabled off
        arm (CompTick returns before Scan; needs ticks with the toggle off, then a rot read)."""
        state = {}
        with t.component("stored_goods_sealed_rot_frozen_forbidden", toggle="tarVaultEnabled"):
            if not _live(t):
                return
            text = _proof(t, "ProofVault")
            if text.startswith("UNMEASURED"):
                _unmeasured(t, text)
                return
            state.update(_kv(text))
            for want in ("sealed=True", "rotFrozen=True", "forbidden=True"):
                if want not in text:
                    raise ExpectationFailed("vault proof missing %s: %s" % (want, text[:200]))
        with t.component("no_solvent_comes_out_ruined", toggle="tarVaultEnabled"):
            if not _live(t):
                return
            if state.get("ruinedOut") != "True":
                raise ExpectationFailed("extracting with no solvent did not leave RM_TarRuinedGoods: %s" % state)
        with t.component("solvent_extracts_clean_and_is_spent", toggle="tarVaultEnabled"):
            if not _live(t):
                return
            if state.get("cleanOut") != "True" or state.get("solventLeft") != "1":
                raise ExpectationFailed("with 2 solvent on the map, want a clean unforbidden thawed meal and 1 solvent left: %s" % state)

    @suite.chain("kethrel_shell")
    def kethrel_shell(t):
        """THESUMP_COVERAGE_GAPS_1: RM_TheSumpProof.ProofKethrel on the current map: PickUp (what the rare tick does
        on finding metal) steps the shell stage by load (stageLoadKg 3/10/22) and sets RM_KethrelShell; Molt drops it
        all. Not proven: the seek/pickup AI itself and the home-area rule (kethrelTakeColonyProperty), which need a
        weapon on tar beside a wild kethrel over rare ticks."""
        state = {}
        with t.component("load_steps_shell_stage", toggle="kethrelShellEnabled"):
            if not _live(t):
                return
            text = _proof(t, "ProofKethrel")
            if text.startswith("UNMEASURED"):
                _unmeasured(t, text)
                return
            state.update(_kv(text))
            if state.get("s0") != "0" or state.get("s1") != "2" or state.get("s2") != "3" or state.get("hediff1", "none") == "none":
                raise ExpectationFailed("want stage 0 -> 2 at 15 kg (with the shell hediff) -> 3 at 30 kg: %s" % text[:220])
        with t.component("molt_drops_everything", toggle="kethrelMoltLoadKg"):
            if not _live(t):
                return
            if state.get("sAfter") != "0" or state.get("hediffGone") != "True" or state.get("steelOnMap") != "60":
                raise ExpectationFailed("a molt must drop all 60 steel and return to stage 0 with no shell hediff: %s" % state)
        with t.component("kethrel_ignores_home_area_unless_allowed", toggle="kethrelTakeColonyProperty"):
            if _live(t):
                _unmeasured(t, "needs a home area, a weapon inside it and a wild kethrel beside it over rare ticks, toggle off then on")

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        with t.component("deep_black_mere_generated", toggle="deepBlackMereEnabled"):
            if _live(t):
                _unmeasured(t, 'a once-per-map unbroken tar expanse exists only on a map GENERATED as RM_TheSump with the toggle on (none with it off); the bridge cannot generate a map. Its gen step def (RUT_GenStep_DeepBlackMere) resolves in defs_resolve')
        with t.component("biome_rarity_worldgen", toggle="biomeRarityFactor"):
            if _live(t):
                _unmeasured(t, 'rarity changes only planets generated afterwards; the world is frozen and the bridge cannot generate one')
        with t.component("poured_tar_moat_and_fuse_post", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'the moat ignition needs RUT_MoatFusePost, which needs a built post, a poured moat and a fire (not yet measured live)')
        with t.component("dig_shaft_stratum_lottery", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_DigShaft and RUT_DigStratumTable deploy and resolve, but the lottery draw needs a built shaft, a worker and ticks on a Sump map')
        with t.component("tar_beast_bulge_set_piece", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'bulge -> wake (damage, construction, dig shaft, running deep drill) -> RM_TarBeast crawls to the densest building cluster, swallows one (mound + letter), lays tar, sinks into a new bulge: needs a Sump map and a wake; FIRST LIVE POKE: hit the bulge, step ticks, read RM_CompTarBeast/RM_CompStationEater via jawa/comp_read')
        with t.component("tar_solvent_pour_wakes_beast", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'pour order on a dormant bulge: carry RM_WeakTarSolvent (min count in settings) to the edge, pour -> bulge gone, one RM_TarBeast spawned in ManhunterPermanent, solvent consumed, Shkaar+Zizzik delta tagged "the tar woken by solvent"; control: no order offered without solvent; manhunter setting off -> ordinary eating beast. FIRST LIVE POKE: spawn bulge + solvent on a Sump map, issue the pour job, step ticks, read mental state (jawa/comp_read RM_CompTarBeast) and Ninefold satiation'.replace(chr(39), chr(34)))
        with t.component("sump_mouse_filth_trail", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_Filth_MouseTrack needs a sump mouse walking on tar (not yet measured live)')
        with t.component("wick_garden_crop", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_Plant_Wick resolves in defs_resolve; growth, glow and harvest need a sown plant and game days on a Sump map')
        with t.component("permanent_dusk_lock", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, 'RUT_SumpDuskLock/RUT_SumpWeather resolve, but their wiring patch targets the held BiomeDef; the lock holding the sky at dusk needs an RM_TheSump map')

    @suite.chain("capstan_turret")
    def capstan_turret(t):
        """SUMP_CAPSTAN_TURRET_BUILD_1. RM_CapstanTurretProof.ProofPull builds a turret and a target 9 cells off on
        any map's open ground, ropes it and reels step by step; "heavy" is a thrumbo (over the mass cap: snaps)."""
        def proof(kind):
            if t.session is None:
                _unmeasured(t, "no bridge session for ProofPull")
                return None
            r = t.bridge_call("jawa/static_call", type="RimMandrake.TheSump.RM_CapstanTurretProof", method="ProofPull", args=kind)
            text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
            if text.startswith("UNMEASURED"):
                _unmeasured(t, text)
                return None
            return text

        with t.component("reels_an_enemy_toward_the_turret", toggle="capstanEnabled"):
            text = proof("Villager")
            if text is not None:
                m = re.search(r"roped=True start=([\d.]+) end=([\d.]+)", text)
                if not m or float(m.group(2)) >= float(m.group(1)) - 2:
                    raise ExpectationFailed("the target was not pulled several cells in: %s" % text[:200])
        with t.component("over_mass_target_snaps_the_line", toggle="capstanMaxMass"):
            text = proof("heavy")
            if text is not None and ("roped=False" not in text or "snaps=1" not in text):
                raise ExpectationFailed("a thrumbo did not snap the line: %s" % text[:200])

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
