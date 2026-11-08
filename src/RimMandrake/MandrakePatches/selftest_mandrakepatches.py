"""selftest_mandrakepatches.py -- every_fix_is_guarded_static is green on the shipped Patches/ and reddens on
each break it exists to catch (planted in a temp copy, never the shipped files)."""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def anima_check():
    """AnimaTree_NoRandomSpawn.xml: the two removals leave no random anima-tree route in Core's own XML
    (skipped, not failed, where the game install is not readable)."""
    try:
        from lxml import etree
    except ImportError:
        print("skip  anima: lxml missing")
        return
    core = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs"
    pairs = [("MapGeneration/BasePlayerMapGenerator.xml", "/Defs/MapGeneratorDef[defName='Base_Player']/genSteps/li[text()='AnimaTrees']"),
             ("Storyteller/Storytellers.xml", "/Defs/StorytellerDef/comps/li[incident='AnimaTreeSpawn']")]
    patch = etree.parse(os.path.join(HERE, "Patches", "AnimaTree_NoRandomSpawn.xml"))
    xps = [x.text.replace('"', "'") for x in patch.iterfind(".//match/xpath")]
    check("anima patch carries both removals", xps == [p[1] for p in pairs], xps)
    for fn, xp in pairs:
        path = os.path.join(core, fn)
        if not os.path.exists(path):
            print("skip  anima: %s not readable" % fn)
            continue
        doc = etree.parse(path)
        before = doc.xpath(xp)
        for n in before:
            n.getparent().remove(n)
        check("anima: %s has the route before and none after" % fn, len(before) >= 1 and doc.xpath(xp) == [], len(before))


def ghost_target_ops(patch_dir):
    """[(file, xpath)] for leaf ops aimed at a MOD-namespaced def class (/Defs/Ns.Class[...]) that are NOT under a
    FindMod ancestor. A Conditional alone does not guard a nomatch Add: the target def is absent when the mod is,
    so the Add matches nothing and logs a red failure on every load (FACE_PATCH_FIX_ADDS_TO_A_GHOST)."""
    import re
    import xml.etree.ElementTree as ET
    out = []

    def walk(e, fn, under_findmod):
        c = (e.get("Class") or "").replace("PatchOperation", "")
        if c in ("Add", "Replace", "Remove", "AddModExtension", "Insert", "SetName"):
            xp = (e.findtext("xpath") or "").strip()
            if re.match(r"^/?Defs/[A-Za-z_]\w*\.\w+", xp) and not under_findmod:
                out.append((fn, xp))
            return
        guard = under_findmod or c == "FindMod"
        for k in ("match", "nomatch"):
            for x in e.findall(k):
                walk(x, fn, guard)
        for li in e.findall("operations/li"):
            walk(li, fn, guard)

    for fn in sorted(os.listdir(patch_dir)):
        if fn.endswith(".xml"):
            for op in ET.parse(os.path.join(patch_dir, fn)).getroot().findall("Operation"):
                walk(op, fn, False)
    return out


# CAI_FOG_SILENCE_FORCED_OFF_BY_US: every CAI 5000 member CaiFogOff.cs binds by name (const name -> member string).
CAI_MEMBERS = {"FinderType": "CombatAI.Finder", "ModType": "CombatAI.CombatAIMod", "FinderSettingsField": "Settings",
               "FinderModField": "Mod", "FogField": "FogOfWar_Enabled", "SightField": "NewSightSystem_Enabled",
               "PrevFogField": "prevFogEnabled", "WriteSettingsMethod": "WriteSettings"}
CAI_DLL = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3673768803/1.6/Assemblies/CombatAI.dll"


# Force()'s if-conditions, in order. Pinned exactly: a flipped guard (e.g. the toggle polarity) keeps every
# SetValue text in place yet stops the forcing, so text presence alone cannot see it.
FORCE_IFS = ["!bound",
             "!RM_PatchesSettings.caiFogForcedOff",
             "settings == null",
             "sight != null && sight.FieldType == typeof(bool)",
             'why != "CAI settings saved" && prevFog != null && prevFog.FieldType == typeof(bool) && Current.Game == null',
             "mod != null",
             "was"]


def force_flow_problems(src):
    """[problem] for the body of CaiFogOff.Force: exact guard list, early returns, and the write after the toggle guard."""
    import re
    m = re.search(r"public static bool Force\(string why\)\s*\{", src)
    if not m:
        return ["no `public static bool Force(string why)`"]
    depth, i = 1, m.end()
    while depth and i < len(src):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        i += 1
    body = src[m.end():i - 1]
    code = re.sub(r"//[^\n]*", "", body)
    out = []
    ifs = [c.strip() for c in re.findall(r"\bif \((.*)\)\s*(?:\{|[A-Za-z_])", code)]
    if ifs != FORCE_IFS:
        out.append("Force() if-conditions %r != FORCE_IFS" % ifs)
    if not re.search(r"if \(!bound\) return false;", code):
        out.append("Force(): `if (!bound) return false;` changed")
    g = re.search(r"if \(!RM_PatchesSettings\.caiFogForcedOff\)\s*\{[^{}]*return false;\s*\}", code)
    if not g:
        out.append("Force(): the toggle guard is not `if (!RM_PatchesSettings.caiFogForcedOff) { ... return false; }`")
    w = code.find("fog.SetValue(settings, false);")
    if w < 0 or (g and w < g.end()):
        out.append("Force(): fog.SetValue(settings, false) is missing or not after the toggle guard")
    elif code[:w].rsplit("\n", 1)[-1].strip() or re.search(r"\{[^{}]*$", code[g.end() if g else 0:w]):
        out.append("Force(): fog.SetValue(settings, false) sits inside a conditional")
    if not re.search(r"fog\.SetValue\(settings, false\);[\s\S]*return true;\s*$", code):
        out.append("Force() does not end `return true;` after the write")
    return out


# Install()'s if-conditions, in order. Pinned like FORCE_IFS: a flipped guard or a dropped `bound = true;` disables the
# forcer while every Patch/SetValue text stays in place.
INSTALL_IFS = ["installed",
               "finderT == null",
               "fog == null || fog.FieldType != typeof(bool) || write == null"]


def method_body(src, sig):
    """Comment-stripped body of the method whose header matches regex `sig` (ending at its `{`), or None."""
    import re
    m = re.search(sig, src)
    if not m:
        return None
    depth, i = 1, m.end()
    while depth and i < len(src):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        i += 1
    return re.sub(r"//[^\n]*", "", src[m.end():i - 1])


def install_flow_problems(src):
    """[problem] for CaiFogOff.Install: exact guard list, each guard returns, and the tail Patch -> bound -> Force."""
    import re
    code = method_body(src, r"public static void Install\(\)\s*\{")
    if code is None:
        return ["no `public static void Install()`"]
    out = []
    ifs = [c.strip() for c in re.findall(r"\bif \((.*)\)\s*(?:\{|[A-Za-z_])", code)]
    if ifs != INSTALL_IFS:
        out.append("Install() if-conditions %r != INSTALL_IFS" % ifs)
    if not re.match(r"\s*if \(installed\) return;\s*installed = true;", code):
        out.append("Install(): does not open `if (installed) return; installed = true;`")
    if not re.search(r"if \(finderT == null\) return;", code):
        out.append("Install(): `if (finderT == null) return;` changed")
    g = re.search(r"if \(fog == null \|\| fog\.FieldType != typeof\(bool\) \|\| write == null\)\s*\{[^{}]*return;\s*\}", code)
    if not g:
        out.append("Install(): the missing-member guard is not `if (fog == null || ... || write == null) { ... return; }`")
    tail = re.search(r"\n\s*new Harmony\(\"mandrake\.rm\.patches\.caifogoff\"\)\.Patch\(write,\s*"
                     r"prefix: new HarmonyMethod\(typeof\(CaiFogOff\), nameof\(Prefix_WriteSettings\)\)\);\s*"
                     r"bound = true;\s*Force\(\"constructor\"\);\s*$", code)
    if not tail or (g and tail.start() < g.end()):
        out.append("Install() does not end, after the guards and outside any block, with Patch(write, prefix) then "
                   "`bound = true;` then Force(\"constructor\")")
    elif re.search(r"\{[^{}]*$", code[g.end() if g else 0:tail.start()]):
        out.append("Install(): the Patch/bound/Force tail sits inside a conditional")
    if code.count("bound = true;") != 1 or re.search(r"\bbound = false;", code):
        out.append("Install(): `bound = true;` must be set exactly once and never cleared")
    return out


# Every assignment statement in Install(), in order, whitespace-normalised. Pinned exactly: binding `fog` to SightField,
# `finderSettings` to FinderModField or `write` to another method keeps every guard and Patch text in place yet stops
# the fog write landing on CombatAI.Settings.FogOfWar_Enabled (or the save-time prefix hooking WriteSettings).
INSTALL_BINDS = ["installed = true;",
                 "Type finderT = AccessTools.TypeByName(FinderType);",
                 "Type modT = AccessTools.TypeByName(ModType);",
                 "finderSettings = AccessTools.Field(finderT, FinderSettingsField);",
                 "finderMod = AccessTools.Field(finderT, FinderModField);",
                 "Type settingsT = finderSettings?.FieldType;",
                 "fog = settingsT == null ? null : AccessTools.Field(settingsT, FogField);",
                 "sight = settingsT == null ? null : AccessTools.Field(settingsT, SightField);",
                 "prevFog = modT == null ? null : AccessTools.Field(modT, PrevFogField);",
                 "MethodInfo write = modT == null ? null : AccessTools.Method(modT, WriteSettingsMethod, Type.EmptyTypes);",
                 'Status = "CAI 5000 is loaded but its fog setting was not found (CAI changed): fog NOT forced off.";',
                 "bound = true;"]
# Every reflective GetValue/SetValue statement in Force(), in order: which object each read and write goes through.
FORCE_REFLECT = ["object settings = finderSettings.GetValue(null);",
                 "bool was = (bool)fog.GetValue(settings);",
                 "fog.SetValue(settings, false);",
                 "if (sight != null && sight.FieldType == typeof(bool)) sight.SetValue(settings, false);",
                 "object mod = finderMod?.GetValue(null);",
                 "if (mod != null) prevFog.SetValue(mod, false);"]


def binding_problems(src):
    """[problem] when Install()'s assignments or Force()'s reflective reads/writes differ from the pinned lists."""
    import re
    norm = lambda c: [" ".join(l.split()) for l in re.findall(r"[^;{}]*;", c)]
    out = []
    code = method_body(src, r"public static void Install\(\)\s*\{")
    binds = [l for l in norm(code or "") if re.search(r"(?<![=!<>])=(?!=)", l)
             and not l.startswith(("if ", "Log.")) and "Log.Warning" not in l]
    if binds != INSTALL_BINDS:
        out.append("Install() assignments %r != INSTALL_BINDS" % binds)
    code = method_body(src, r"public static bool Force\(string why\)\s*\{")
    refl = [l for l in norm(code or "") if re.search(r"\.(?:Get|Set)Value\(", l)]
    if refl != FORCE_REFLECT:
        out.append("Force() reflective reads/writes %r != FORCE_REFLECT" % refl)
    return out


# The two places that reach Install(), each body pinned exactly (comment-stripped, whitespace-normalised): an `if (false)`
# wrapped around a call, or a call moved behind a return, keeps every substring in place yet never installs the forcer.
CALL_SITES = [("RM_PatchesMod's constructor", r"public class RM_PatchesMod : Mod\s*\{\s*"
               r"public RM_PatchesMod\(ModContentPack content\) : base\(content\)\s*\{",
               "GetSettings<RM_PatchesSettings>(); CaiFogOff.Install();"),
              ("CaiFogOffStartup's static constructor", r"\[StaticConstructorOnStartup\]\s*public static class CaiFogOffStartup"
               r"\s*\{\s*(?://[^\n]*\s*)*static CaiFogOffStartup\(\)\s*\{",
               'CaiFogOff.Install(); CaiFogOff.Force("startup");')]


def call_site_problems(src, mod_src):
    """[problem] when the Mod constructor or the startup class body is not exactly the pinned unconditional calls."""
    out = []
    for (name, sig, want), text in zip(CALL_SITES, (mod_src, src)):
        body = method_body(text, sig)
        if body is None:
            out.append("%s: header not found (class, attribute or signature changed)" % name)
        elif " ".join(body.split()) != want:
            out.append("%s body %r != %r" % (name, " ".join(body.split()), want))
    for fname, text in (("CaiFogOff.cs", src), ("RM_PatchesMod.cs", mod_src)):
        if "#if" in text:
            out.append("%s: a preprocessor conditional could compile the call sites out" % fname)
    return out


def cai_fog_problems(src, mod_src, about, srchash, cs_bytes):
    """[problem] for the CAI fog forcer: constants, the forcing writes, the default-on setting, About, and the DLL stamp.
    Pure function of the texts so the break checks can plant each defect."""
    import hashlib
    import re
    import xml.etree.ElementTree as ET
    out = []
    consts = dict(re.findall(r'public const string (\w+) = "([^"]*)";', src))
    if consts != CAI_MEMBERS:
        out.append("CaiFogOff constants %r != CAI_MEMBERS" % consts)
    if "fog.SetValue(settings, false);" not in src:
        out.append("Force() no longer writes FogOfWar_Enabled=false")
    out += force_flow_problems(src)
    out += install_flow_problems(src)
    out += binding_problems(src)
    out += call_site_problems(src, mod_src)
    if not re.search(r"Patch\(write,\s*prefix: new HarmonyMethod\(typeof\(CaiFogOff\), nameof\(Prefix_WriteSettings\)\)\)", src):
        out.append("no Harmony prefix on CombatAIMod.WriteSettings")
    if "public static void Prefix_WriteSettings() => Force(" not in src:
        out.append("the WriteSettings prefix does not force")
    if not re.search(r"\[StaticConstructorOnStartup\]\s*public static class CaiFogOffStartup", src) or 'CaiFogOff.Force("startup")' not in src:
        out.append("no startup force")
    if "public static bool caiFogForcedOff = true;" not in mod_src or 'Scribe_Values.Look(ref caiFogForcedOff, "caiFogForcedOff", true);' not in mod_src:
        out.append("the setting is not default-on in both the field and the Scribe default")
    if "CaiFogOff.Install();" not in mod_src:
        out.append("the Mod constructor does not install the forcer")
    root = ET.fromstring(about)
    if "brrainz.harmony" not in [e.text for e in root.iterfind("modDependencies/li/packageId")]:
        out.append("About: no Harmony modDependency")
    if "Krkr.rule56" not in [(e.text or "").strip() for e in root.iterfind("loadAfter/li")]:
        out.append("About: no loadAfter Krkr.rule56")
    want = {hashlib.sha256(b).hexdigest() + " " + name for name, b in cs_bytes.items()}
    have = {l.strip() for l in srchash.splitlines() if l.strip() and not l.startswith("#")}
    if want != have:
        out.append("Assemblies/RimMandrakePatches.dll.srchash does not match Source/*/*.cs (rebuild): %s" % sorted(want ^ have))
    return out


def cai_fog_check():
    import glob
    rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read()
    src, mod_src, about = rd("Source", "CaiFogOff", "CaiFogOff.cs"), rd("Source", "CaiFogOff", "RM_PatchesMod.cs"), rd("About", "About.xml")
    srchash = rd("Assemblies", "RimMandrakePatches.dll.srchash")
    cs = {os.path.relpath(f, os.path.join(HERE, "Source")).replace(os.sep, "/"): open(f, "rb").read()
          for f in sorted(glob.glob(os.path.join(HERE, "Source", "*", "*.cs")))}
    check("CAI fog forcer: shipped source, About and DLL stamp", cai_fog_problems(src, mod_src, about, srchash, cs) == [],
          cai_fog_problems(src, mod_src, about, srchash, cs))
    check("CAI fog forcer: RimMandrakePatches.dll is shipped", os.path.getsize(os.path.join(HERE, "Assemblies", "RimMandrakePatches.dll")) > 0)
    breaks = [("a renamed CAI member", src.replace('"FogOfWar_Enabled"', '"FogOfWar_On"'), mod_src, about, srchash),
              ("Force stops writing false", src.replace("fog.SetValue(settings, false);", "fog.SetValue(settings, was);"), mod_src, about, srchash),
              ("the WriteSettings prefix is dropped", src.replace("prefix: new HarmonyMethod", "postfix: new HarmonyMethod"), mod_src, about, srchash),
              ("the setting defaults off", src, mod_src.replace("caiFogForcedOff = true;", "caiFogForcedOff = false;"), about, srchash),
              ("loadAfter Krkr.rule56 removed", src, mod_src, about.replace("<li>Krkr.rule56</li>", ""), srchash),
              ("stale DLL stamp", src, mod_src, about, srchash.replace(srchash.splitlines()[-1][:8], "00000000")),
              ("the toggle guard is inverted", src.replace("if (!RM_PatchesSettings.caiFogForcedOff)",
                                                           "if (RM_PatchesSettings.caiFogForcedOff)"), mod_src, about, srchash),
              ("the bound guard is inverted", src.replace("if (!bound) return false;", "if (bound) return false;"),
               mod_src, about, srchash),
              ("the write is made conditional on fog already on", src.replace("fog.SetValue(settings, false);",
                                                                              "if (!was) fog.SetValue(settings, false);"),
               mod_src, about, srchash),
              ("the toggle guard stops returning", src.replace(
                  'its fog is left to CAI\'s own checkbox.";\n                return false;',
                  'its fog is left to CAI\'s own checkbox.";'), mod_src, about, srchash),
              ("Install drops `bound = true;`", src.replace("bound = true;", ""), mod_src, about, srchash),
              ("Install's missing-member guard is inverted", src.replace(
                  "if (fog == null || fog.FieldType != typeof(bool) || write == null)", "if (fog != null)"),
               mod_src, about, srchash),
              ("Install's CAI-absent guard is inverted", src.replace("if (finderT == null) return;",
                                                                     "if (finderT != null) return;"), mod_src, about, srchash),
              ("Install's missing-member guard stops returning", src.replace(
                  "fog of war is NOT being forced off.\");\n                return;", "fog of war is NOT being forced off.\");"),
               mod_src, about, srchash),
              ("Install sets bound before patching", src.replace(
                  "            new Harmony(\"mandrake.rm.patches.caifogoff\")", "            bound = true;\n            new Harmony(\"mandrake.rm.patches.caifogoff\")"
              ).replace("prefix: new HarmonyMethod(typeof(CaiFogOff), nameof(Prefix_WriteSettings)));\n            bound = true;",
                        "prefix: new HarmonyMethod(typeof(CaiFogOff), nameof(Prefix_WriteSettings)));"), mod_src, about, srchash),
              ("the startup class no longer forces", src.replace('CaiFogOff.Force("startup");', ""), mod_src, about, srchash),
              ("Install binds fog to SightField", src.replace("AccessTools.Field(settingsT, FogField)",
                                                              "AccessTools.Field(settingsT, SightField)"), mod_src, about, srchash),
              ("Install binds finderSettings to FinderModField", src.replace(
                  "AccessTools.Field(finderT, FinderSettingsField)", "AccessTools.Field(finderT, FinderModField)"),
               mod_src, about, srchash),
              ("Install hooks the wrong CAI method", src.replace(
                  "AccessTools.Method(modT, WriteSettingsMethod, Type.EmptyTypes)",
                  'AccessTools.Method(modT, "DoSettingsWindowContents")'), mod_src, about, srchash),
              ("Force reads settings through finderMod", src.replace("object settings = finderSettings.GetValue(null);",
                                                                     "object settings = finderMod.GetValue(null);"),
               mod_src, about, srchash),
              ("Force writes fog on a different object", src.replace("fog.SetValue(settings, false);",
                                                                     "fog.SetValue(null, false);"), mod_src, about, srchash),
              ("the Mod constructor's Install is behind `if (false)`", src,
               mod_src.replace("            CaiFogOff.Install();", "            if (false) CaiFogOff.Install();"), about, srchash),
              ("the startup pair is wrapped in `if (false) { }`", src.replace(
                  'CaiFogOff.Install();\n            CaiFogOff.Force("startup");',
                  'if (false) { CaiFogOff.Install();\n            CaiFogOff.Force("startup"); }'), mod_src, about, srchash),
              ("the startup class loses [StaticConstructorOnStartup]", src.replace(
                  "[StaticConstructorOnStartup]\n    public static class CaiFogOffStartup", "public static class CaiFogOffStartup"),
               mod_src, about, srchash),
              ("the Mod constructor returns before Install", src,
               mod_src.replace("            CaiFogOff.Install();", "            return;\n            CaiFogOff.Install();"), about, srchash),
              ("the Mod constructor's Install is compiled out", src,
               mod_src.replace("            CaiFogOff.Install();", "#if NEVER\n            CaiFogOff.Install();\n#endif"),
               about, srchash)]
    for name, a, *_ in breaks[-20:-5]:
        check("break: planted %s actually changed the source" % name, a != src)
    for name, a, b, *_ in breaks[-5:]:
        check("break: planted %s actually changed the source" % name, (a, b) != (src, mod_src))
    for name, a, b, c, d in breaks:
        check("break: %s is reported" % name, len(cai_fog_problems(a, b, c, d, cs)) >= 1)
    if not os.path.exists(CAI_DLL):
        print("skip  CAI members vs installed CombatAI.dll: %s not readable (UNMEASURED)" % CAI_DLL)
        return
    try:
        import lint_harmony_targets as lht       # ECMA-335 tables via dnfile, never a string grep
        index = {"types": lht.index_dll(CAI_DLL)}
    except ImportError:
        print("skip  CAI members vs installed CombatAI.dll: dnfile missing (UNMEASURED)")
        return
    m = CAI_MEMBERS
    want = [(m["FinderType"], "field", m["FinderSettingsField"]), (m["FinderType"], "field", m["FinderModField"]),
            ("CombatAI.Settings", "field", m["FogField"]), ("CombatAI.Settings", "field", m["SightField"]),
            (m["ModType"], "field", m["PrevFogField"]), (m["ModType"], "method", m["WriteSettingsMethod"])]
    bad = [(w, lht.has_member(index, *w)) for w in want if lht.has_member(index, *w)[0] != "OK"]
    check("CAI members still exist in the installed CombatAI.dll", bad == [], bad)
    check("sanity: the CombatAI.dll probe can miss a member",
          lht.has_member(index, "CombatAI.Settings", "field", "FogOfWar_NoSuchName")[0] == "MISSING_MEMBER")


NTC_TARGET = ("RimWorld.ReadingPolicyDatabase", "method", "GenerateStartingPolicies")
RW_DLL = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll"
RW_DECOMP = "/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/RimWorld/ReadingPolicyDatabase.cs"


def null_guard_problems(src, mod_src):
    """[problem] for the null-thingClass guard (QUICKTEST_POLICY_NRE_FULLLIST_1): it prefixes the vanilla method that NREs,
    also runs at startup, repairs every null thingClass ThingDef, names def + mod + file in Log.Error, and is default-on."""
    import re
    out = []
    consts = dict(re.findall(r'public const string (\w+) = "([^"]*)";', src))
    if (consts.get("TargetType"), consts.get("TargetMethod")) != (NTC_TARGET[0], NTC_TARGET[2]):
        out.append("guard target constants %r != %r" % (consts, NTC_TARGET))
    if not re.search(r"AccessTools\.Method\(typeof\(ReadingPolicyDatabase\), TargetMethod\)", src):
        out.append("Install() does not resolve ReadingPolicyDatabase.TargetMethod")
    if not re.search(r"Patch\(target,\s*prefix: new HarmonyMethod\(typeof\(NullThingClassGuard\), nameof\(Prefix\)\)\)", src):
        out.append("no Harmony PREFIX on GenerateStartingPolicies")
    if 'public static void Prefix() => Repair(' not in src:
        out.append("the prefix does not repair")
    if not re.search(r"\[StaticConstructorOnStartup\]\s*public static class NullThingClassGuardStartup", src) or 'NullThingClassGuard.Repair("startup")' not in src:
        out.append("no startup repair")
    if "DefDatabase<ThingDef>.AllDefsListForReading" not in src or "def.thingClass != null)" not in src:
        out.append("Repair() does not walk every ThingDef skipping only non-null thingClass")
    if not re.search(r"def\.thingClass = FallbackClass\(", src):
        out.append("Repair() does not assign a fallback class")
    if "Log.Error(LogTag" not in src or "def.modContentPack?.PackageId" not in src or "def.fileName" not in src:
        out.append("the error does not name the def's mod (packageId) and file")
    if "if (!RM_PatchesSettings.nullThingClassGuard)\n                return;" not in src:
        out.append("Repair() ignores the toggle")
    if "public static bool nullThingClassGuard = true;" not in mod_src or 'Scribe_Values.Look(ref nullThingClassGuard, "nullThingClassGuard", true);' not in mod_src:
        out.append("the guard setting is not default-on in both the field and the Scribe default")
    if "ref RM_PatchesSettings.nullThingClassGuard" not in mod_src:
        out.append("no settings checkbox for the guard")
    return out


def null_guard_check():
    rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read()
    src, mod_src = rd("Source", "NullThingClassGuard", "NullThingClassGuard.cs"), rd("Source", "CaiFogOff", "RM_PatchesMod.cs")
    got = null_guard_problems(src, mod_src)
    check("null-thingClass guard: shipped source", got == [], got)
    breaks = [("the target renamed", src.replace('"GenerateStartingPolicies"', '"GenerateStartingPolicy"'), mod_src),
              ("prefix becomes postfix", src.replace("prefix: new HarmonyMethod(typeof(NullThingClassGuard)",
                                                     "postfix: new HarmonyMethod(typeof(NullThingClassGuard)"), mod_src),
              ("startup repair dropped", src.replace('NullThingClassGuard.Repair("startup");', ""), mod_src),
              ("the null test inverted", src.replace("def.thingClass != null)", "def.thingClass == null)"), mod_src),
              ("no assignment", src.replace("def.thingClass = FallbackClass(", "var unused = FallbackClass("), mod_src),
              ("mod not named", src.replace("def.modContentPack?.PackageId", "def.defName"), mod_src),
              ("toggle ignored", src.replace("if (!RM_PatchesSettings.nullThingClassGuard)\n                return;", ""), mod_src),
              ("defaults off", src, mod_src.replace("nullThingClassGuard = true;", "nullThingClassGuard = false;")),
              ("checkbox removed", src, mod_src.replace("ref RM_PatchesSettings.nullThingClassGuard", "ref RM_PatchesSettings.caiFogForcedOff"))]
    for name, a, b in breaks:
        check("break: planted '%s' changed the text" % name, (a, b) != (src, mod_src))
        check("break: null guard %s is reported" % name, len(null_guard_problems(a, b)) >= 1)
    if os.path.exists(RW_DECOMP):
        dec = open(RW_DECOMP, encoding="utf-8", errors="replace").read()
        check("vanilla still derefs thingClass unguarded (the guard is still needed)",
              "item.thingClass.SameOrSubclassOf<Book>()" in dec, RW_DECOMP)
    else:
        print("skip  vanilla decomp not readable (UNMEASURED): %s" % RW_DECOMP)
    if not os.path.exists(RW_DLL):
        print("skip  guard target vs Assembly-CSharp.dll: not readable (UNMEASURED)")
        return
    try:
        import lint_harmony_targets as lht
        index = {"types": lht.index_dll(RW_DLL)}
    except ImportError:
        print("skip  guard target vs Assembly-CSharp.dll: dnfile missing (UNMEASURED)")
        return
    check("guard target exists in the installed Assembly-CSharp.dll", lht.has_member(index, *NTC_TARGET)[0] == "OK",
          lht.has_member(index, *NTC_TARGET))
    check("ThingDef.thingClass field exists", lht.has_member(index, "Verse.ThingDef", "field", "thingClass")[0] == "OK")
    check("sanity: the Assembly-CSharp probe can miss a member",
          lht.has_member(index, "RimWorld.ReadingPolicyDatabase", "method", "NoSuchMethodHere")[0] != "OK")


CDG_DECOMP = "/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/RimWorld/DrugPolicy.cs"


def cut_drug_guard_problems(src, mod_src):
    """[problem] for the cut-drug policy repair (BEER_DIAGNOSE_NON_DRUG_3200_LOG_ERRORS): a Harmony postfix on
    DrugPolicy.ExposeData that, only at PostLoadInit and only with the default-on toggle, drops each entry whose drug
    is no longer a drug, keeps real drugs, and names each removal."""
    import re
    out = []
    if not re.search(r"AccessTools\.Method\(typeof\(DrugPolicy\), TargetMethod\)", src) or 'TargetMethod = "ExposeData"' not in src:
        out.append("Install() does not resolve DrugPolicy.ExposeData")
    if not re.search(r"Patch\(target,\s*postfix: new HarmonyMethod\(typeof\(CutDrugPolicyGuard\), nameof\(Postfix\)\)\)", src):
        out.append("no Harmony POSTFIX on ExposeData")
    if "if (Scribe.mode != LoadSaveMode.PostLoadInit)\n                return;" not in src:
        out.append("the postfix runs outside PostLoadInit (it would also edit on save)")
    if "if (!RM_PatchesSettings.cutDrugPolicyGuard)\n                return;" not in src:
        out.append("the postfix ignores the toggle")
    if 'EntriesField = "entriesInt"' not in src or ".Field(EntriesField).GetValue<List<DrugPolicyEntry>>()" not in src:
        out.append("the postfix does not read DrugPolicy.entriesInt")
    if "if (drug == null || drug.IsDrug)\n                    continue;" not in src:
        out.append("the postfix does not keep real drugs")
    if "entries.RemoveAt(i);" not in src or "i = entries.Count - 1; i >= 0; i--" not in src:
        out.append("the postfix does not remove while walking backwards")
    if 'Log.Message(LogTag + " " + drug.defName' not in src:
        out.append("a removal is not named in the log")
    if "public static bool cutDrugPolicyGuard = true;" not in mod_src or 'Scribe_Values.Look(ref cutDrugPolicyGuard, "cutDrugPolicyGuard", true);' not in mod_src:
        out.append("the setting is not default-on in both the field and the Scribe default")
    if "ref RM_PatchesSettings.cutDrugPolicyGuard" not in mod_src or "CutDrugPolicyGuard.Status" not in mod_src:
        out.append("no settings checkbox or status for the repair")
    return out


def cut_drug_guard_check():
    rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read()
    src, mod_src = rd("Source", "CutDrugPolicyGuard", "CutDrugPolicyGuard.cs"), rd("Source", "CaiFogOff", "RM_PatchesMod.cs")
    src, mod_src = src.replace("\r\n", "\n"), mod_src.replace("\r\n", "\n")
    got = cut_drug_guard_problems(src, mod_src)
    check("cut-drug repair: shipped source", got == [], got)
    breaks = [("the target renamed", src.replace('"ExposeData"', '"ExposeDataX"'), mod_src),
              ("postfix becomes prefix", src.replace("postfix: new HarmonyMethod", "prefix: new HarmonyMethod"), mod_src),
              ("runs at every scribe mode", src.replace("if (Scribe.mode != LoadSaveMode.PostLoadInit)\n                return;", ""), mod_src),
              ("toggle ignored", src.replace("if (!RM_PatchesSettings.cutDrugPolicyGuard)\n                return;", ""), mod_src),
              ("the drug test inverted", src.replace("drug == null || drug.IsDrug", "drug == null || !drug.IsDrug"), mod_src),
              ("nothing removed", src.replace("entries.RemoveAt(i);", ""), mod_src),
              ("removal unnamed", src.replace('Log.Message(LogTag + " " + drug.defName', 'Log.Message(LogTag + " "'), mod_src),
              ("defaults off", src, mod_src.replace("cutDrugPolicyGuard = true;", "cutDrugPolicyGuard = false;")),
              ("checkbox removed", src, mod_src.replace("ref RM_PatchesSettings.cutDrugPolicyGuard", "ref RM_PatchesSettings.caiFogForcedOff"))]
    for name, a, b in breaks:
        check("break: planted '%s' changed the text" % name, (a, b) != (src, mod_src))
        check("break: cut-drug repair %s is reported" % name, len(cut_drug_guard_problems(a, b)) >= 1)
    if os.path.exists(CDG_DECOMP):
        dec = open(CDG_DECOMP, encoding="utf-8", errors="replace").read()
        check("vanilla still prunes only a null drug (the repair is still needed)",
              "x == null || x.drug == null" in dec and "IsDrug)" not in dec.split("PostLoadInit", 1)[-1].split("InitializeIfNeeded", 1)[0], CDG_DECOMP)
    else:
        print("skip  vanilla decomp not readable (UNMEASURED): %s" % CDG_DECOMP)
    if not os.path.exists(RW_DLL):
        print("skip  repair target vs Assembly-CSharp.dll: not readable (UNMEASURED)")
        return
    try:
        import lint_harmony_targets as lht
        index = {"types": lht.index_dll(RW_DLL)}
    except ImportError:
        print("skip  repair target vs Assembly-CSharp.dll: dnfile missing (UNMEASURED)")
        return
    check("repair target exists in the installed Assembly-CSharp.dll",
          lht.has_member(index, "RimWorld.DrugPolicy", "method", "ExposeData")[0] == "OK")
    check("DrugPolicy.entriesInt exists", lht.has_member(index, "RimWorld.DrugPolicy", "field", "entriesInt")[0] == "OK")
    check("sanity: the DrugPolicy probe can miss a member",
          lht.has_member(index, "RimWorld.DrugPolicy", "field", "noSuchFieldHere")[0] != "OK")



# LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS: the third-party debug sinks LogSpamOff.cs binds by name.
def log_spam_problems(src, mod_src):
    out = []
    for const, member in (('IntimacyType = "LoveyDoveySexWithEuterpe.SexUtilities"', "Intimacy's type"),
                          ('IntimacySink = "HandNotesToEuterpe"', "Intimacy's log method"),
                          ('MoodChainType = "MoodChainReaction.Hediff_MCRMoodChain"', "Mood Chain's type"),
                          ('MoodChainSink = "DebugLog"', "Mood Chain's log method")):
        if const not in src:
            out.append("%s is not bound as %s" % (member, const))
    if "Bind(harmony, IntimacyType, IntimacySink, nameof(Prefix_Intimacy))" not in src:
        out.append("Intimacy's sink is not patched")
    if "Bind(harmony, MoodChainType, MoodChainSink, nameof(Prefix_MoodChain))" not in src:
        out.append("Mood Chain's sink is not patched")
    if "if (!RM_PatchesSettings.quietThirdPartyLogSpam)\n                return true;" not in src:
        out.append("the prefix ignores the toggle")
    if "first line dropped from" not in src or "return false;\n        }\n    }" not in src:
        out.append("the prefix does not skip the original or never reports its first drop")
    if "harmony.Patch(target, prefix: new HarmonyMethod(typeof(LogSpamOff), prefix));" not in src:
        out.append("no Harmony prefix")
    if "public static bool quietThirdPartyLogSpam = true;" not in mod_src or 'Scribe_Values.Look(ref quietThirdPartyLogSpam, "quietThirdPartyLogSpam", true);' not in mod_src:
        out.append("the setting is not default-on in both the field and the Scribe default")
    if "ref RM_PatchesSettings.quietThirdPartyLogSpam" not in mod_src or "LogSpamOff.Status" not in mod_src:
        out.append("no settings checkbox or status")
    return out


def log_spam_check():
    rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read().replace("\r\n", "\n")
    src, mod_src = rd("Source", "LogSpamOff", "LogSpamOff.cs"), rd("Source", "CaiFogOff", "RM_PatchesMod.cs")
    got = log_spam_problems(src, mod_src)
    check("log spam off: shipped source", got == [], got)
    breaks = [("Intimacy's method renamed", src.replace('"HandNotesToEuterpe"', '"HandNotes"'), mod_src),
              ("Mood Chain's type renamed", src.replace('"MoodChainReaction.Hediff_MCRMoodChain"', '"MoodChainReaction.X"'), mod_src),
              ("Mood Chain left out", src.replace("Bind(harmony, MoodChainType", "Bind(null, MoodChainType"), mod_src),
              ("toggle ignored", src.replace("if (!RM_PatchesSettings.quietThirdPartyLogSpam)\n                return true;", ""), mod_src),
              ("the original still runs", src.replace("return false;\n        }\n    }", "return true;\n        }\n    }"), mod_src),
              ("defaults off", src, mod_src.replace("quietThirdPartyLogSpam = true;", "quietThirdPartyLogSpam = false;")),
              ("checkbox removed", src, mod_src.replace("ref RM_PatchesSettings.quietThirdPartyLogSpam", "ref RM_PatchesSettings.caiFogForcedOff"))]
    for name, a, b in breaks:
        check("break: planted '%s' changed the text" % name, (a, b) != (src, mod_src))
        check("break: log spam off %s is reported" % name, len(log_spam_problems(a, b)) >= 1)

def metal_nonflammable_problems(src, mod_src):
    out = []
    for needle, why in (
            ('MineralCategories = { "Metallic", "Stony", "Gemstones" }', "the categories are not Metallic, Stony, Gemstones"),
            ('OrganicCategories = { "Woody", "Fabric", "Leathery" }', "Woody/Fabric/Leathery are not excluded"),
            ("c.defName == name", "categories are not matched by defName (a mod-free generic match)"),
            ("m.stat == StatDefOf.Flammability", "the Flammability stat is not the one edited"),
            ("sp.statFactors = factors;", "stuffProps.statFactors is not set"),
            ("def.statBases = bases;", "the stuff's own statBases is not set"),
            ("new List<StatModifier>(sp.statFactors)", "the shared statFactors list is edited in place"),
            ("value = 0f", "the value is not 0"),
            ("if (!RM_PatchesSettings.metalStoneNonFlammable)", "the toggle is ignored"),
            ("stuff def(s) changed (", "no startup count line"),
            ("[StaticConstructorOnStartup]", "no startup hook"),
            ("public static string Probe()", "no live probe")):
        if needle not in src:
            out.append(why)
    for banned in ("RSW_", "RUT_", "RM_Steel", "Steel\"") :
        # the generic code names no mod's def; the Probe list legitimately does, so look only above it
        if banned in src.split("public static string Probe()")[0].split("[StaticConstructorOnStartup]")[1]:
            out.append("Apply names a mod def (%s): it must stay generic" % banned)
    if "public static bool metalStoneNonFlammable = true;" not in mod_src or 'Scribe_Values.Look(ref metalStoneNonFlammable, "metalStoneNonFlammable", true);' not in mod_src:
        out.append("the setting is not default-on in both the field and the Scribe default")
    if "ref RM_PatchesSettings.metalStoneNonFlammable" not in mod_src or "MetalNonFlammable.Status" not in mod_src:
        out.append("no settings checkbox or status")
    if "Metal, stone and gem buildings don't burn" not in mod_src:
        out.append("the checkbox label is not the owner-ordered text")
    return out


def metal_nonflammable_check():
    rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read().replace("\r\n", "\n")
    src, mod_src = rd("Source", "MetalNonFlammable", "MetalNonFlammable.cs"), rd("Source", "CaiFogOff", "RM_PatchesMod.cs")
    got = metal_nonflammable_problems(src, mod_src)
    check("metal non-flammable: shipped source", got == [], got)
    srchash = rd("Assemblies", "RimMandrakePatches.dll.srchash")
    check("metal non-flammable: the built DLL's srchash lists the source", "MetalNonFlammable/MetalNonFlammable.cs" in srchash)
    breaks = [("Stony dropped", src.replace('"Stony", ', ""), mod_src),
              ("Woody no longer excluded", src.replace('"Woody", ', ""), mod_src),
              ("factor left alone", src.replace("sp.statFactors = factors;", ""), mod_src),
              ("own statBases left alone", src.replace("def.statBases = bases;", ""), mod_src),
              ("list edited in place", src.replace("new List<StatModifier>(sp.statFactors)", "sp.statFactors"), mod_src),
              ("toggle ignored", src.replace("if (!RM_PatchesSettings.metalStoneNonFlammable)", "if (false)"), mod_src),
              ("a mod def named in Apply", src.replace("public static void Apply()", "public static void Apply()\n{ var x = \"RSW_Durasteel\";"), mod_src),
              ("defaults off", src, mod_src.replace("metalStoneNonFlammable = true;", "metalStoneNonFlammable = false;")),
              ("checkbox removed", src, mod_src.replace("ref RM_PatchesSettings.metalStoneNonFlammable", "ref RM_PatchesSettings.caiFogForcedOff"))]
    for name, a, b in breaks:
        check("break: planted '%s' changed the text" % name, (a, b) != (src, mod_src))
        check("break: metal non-flammable %s is reported" % name, len(metal_nonflammable_problems(a, b)) >= 1)
    # The def-level rule, offline, on the real def dump: every shipped stuff the C# would touch (mineral category, no organic one).
    dump = os.path.join(os.environ.get("RM_DEF_DUMP", ""), "defs", "ThingDef.json")
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
        import game_paths
        dump = os.path.join(game_paths.DEF_DUMP, "defs", "ThingDef.json")
        import json
        with open(dump, encoding="utf-8") as f:
            defs = json.load(f)["defs"]
    except Exception as e:
        print("SKIP metal non-flammable: def dump unreadable (%s)" % str(e)[:80])
        return
    hit = []
    for t in defs:
        if not t.get("is", {}).get("stuff"):
            continue
        cats = (t["fields"].get("stuffProps") or {}).get("categories") or []
        if set(cats) & {"Metallic", "Stony", "Gemstones"} and not set(cats) & {"Woody", "Fabric", "Leathery"}:
            hit.append(t["defName"])
    check("metal non-flammable: the dump has Steel, an RSW metal, and a custom stone in the covered set",
          {"Steel", "RSW_Durasteel", "RM_Lanternstone"} <= set(hit) and len(hit) >= 40, "%d covered; sample %s" % (len(hit), hit[:5]))


def main():
    spec = importlib.util.spec_from_file_location("mp_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    shipped = v.unguarded_ops()
    check("shipped Patches/: every top-level op guarded", shipped == [], shipped)
    anima_check()
    cai_fog_check()
    null_guard_check()
    cut_drug_guard_check()
    log_spam_check()
    metal_nonflammable_check()
    ghosts = ghost_target_ops(os.path.join(HERE, "Patches"))
    check("shipped Patches/: no op on a mod-namespaced def sits outside a FindMod", ghosts == [], ghosts)
    fa = open(os.path.join(HERE, "Patches", "HeadSetForFA_Revive.xml"), encoding="utf-8").read()
    check("FA revive is wrapped in FindMod on the Facial Animation Compatability Project",
          'PatchOperationFindMod' in fa and '<li>Facial Animation Compatability Project</li>' in fa)
    tmp0 = tempfile.mkdtemp()
    try:
        open(os.path.join(tmp0, "Ghost.xml"), "w").write(
            '<Patch><Operation Class="PatchOperationConditional"><xpath>/Defs/FA.D[defName="X"]/P</xpath>'
            '<nomatch Class="PatchOperationAdd"><xpath>/Defs/FA.D[defName="X"]</xpath><value><P></P></value></nomatch></Operation></Patch>')
        got = ghost_target_ops(tmp0)
        check("break: an unguarded Conditional/nomatch Add on a mod def is reported", len(got) == 1, got)
        open(os.path.join(tmp0, "Ghost.xml"), "w").write(
            '<Patch><Operation Class="PatchOperationFindMod"><mods><li>M</li></mods><match Class="PatchOperationConditional">'
            '<xpath>/Defs/FA.D[defName="X"]/P</xpath><nomatch Class="PatchOperationAdd"><xpath>/Defs/FA.D[defName="X"]</xpath>'
            '<value><P></P></value></nomatch></match></Operation></Patch>')
        check("the FindMod-wrapped form is clean", ghost_target_ops(tmp0) == [])
    finally:
        shutil.rmtree(tmp0, ignore_errors=True)
    tmp = tempfile.mkdtemp()
    try:
        pd = os.path.join(tmp, "Patches")
        shutil.copytree(os.path.join(HERE, "Patches"), pd)
        f = os.path.join(pd, "ThirdPartySignConfigErrors_Fix.xml")
        s = open(f, encoding="utf-8").read()
        brk = s.replace('<Operation Class="PatchOperationFindMod">', '<Operation Class="PatchOperationFindMod" MayRequire="Dark.Signs">', 1)
        open(f, "w", encoding="utf-8").write(brk)
        got = v.unguarded_ops(pd)
        check("break: top-level MayRequire is reported as inert", len(got) == 1 and "inert" in got[0][2], got)
        open(f, "w", encoding="utf-8").write(s)
        open(os.path.join(pd, "Bare.xml"), "w").write(
            '<Patch><Operation Class="PatchOperationReplace"><xpath>Defs/X</xpath><value><a/></value></Operation></Patch>')
        got = v.unguarded_ops(pd)
        check("break: a bare Replace is reported unguarded", got == [("Bare.xml", 0, "unguarded PatchOperationReplace")], got)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # ---- fix_effects_vs_dump_static (MANDRAKEPATCHES_COVERAGE_GAPS_1 offline half) ----
    import copy
    ops = v.leaf_ops()
    try:
        rows, active = v._dump_inputs(sorted(set(o["type"] for o in ops)))
        installed = v._installed_names()
    except Exception as e:
        rows = None
        print("UNMEASURED  fix effects vs dump: %s" % e)
    if rows:
        import collections
        kinds = collections.Counter(o["cls"] for o in ops)
        check("sanity probe: >= 15 leaf ops read (22 after the 2026-10-18 donor retirements) incl. Replace/Add/Remove", len(ops) >= 15 and all(kinds[k] for k in ("Replace", "Add", "Remove")), kinds)
        checked, skipped, bad = v.effect_findings(ops, rows, active, installed)
        # PATCHES_EFFECTFLOOR_FIX_FIVE_DONORS_NAPPING: the floor counts ops checked PLUS ops whose donor is inactive (named,
        # never passed: see the next check), so a smaller live list cannot redden a suite whose every op is accounted for.
        covered = checked + skipped.get("donor mod inactive", 0)
        check("shipped fixes vs the load-14 dump: %d checked, all show their effect (skipped %s)" % (checked, skipped),
              checked >= 1 and covered >= 15 and bad == [], (covered, bad[:3]))
        check("inactive donors are named, not passed", skipped["donor mod inactive"] >= 1, skipped)

        def fx(tag, mut, must, ops_=None, active_=None, installed_=None, expect_n=1):
            r2 = copy.deepcopy(rows)
            mut(r2)
            got = v.effect_findings(ops_ or ops, r2, active_ if active_ is not None else active, installed_ if installed_ is not None else installed)[2]
            check("break fix: %-52s -> %s" % (tag, must[:30]), any(must in g for g in got), got)

        def first(cls, ty):
            return next(o for o in ops if o["cls"] == cls and o["type"] == ty and all(any(g.lower() in active for g in grp) for grp in o["guards"]))
        try:
            wg = first("Replace", "WorkGiverDef")
        except StopIteration:
            # the dump's mod set decides which donors are active; with the DrillTurret donor absent from it none of the break
            # fixtures below can bite -- say so aloud (UNMEASURED), never crash and never pass.
            print("UNMEASURED  fix-effect breaks: no ACTIVE-donor WorkGiverDef Replace in the current dump's mod set (MiningCo. DrillTurret not in it)")
            wg = None
        if wg is None:
            print("\nUNMEASURED, not a pass or a fail" if not FAILS else "\n%d MandrakePatches selftest(s) FAILED" % len(FAILS))
            return 1 if FAILS else 0
        fx("turret job reverts to Mining", lambda r: r["WorkGiverDef"][wg["name"]]["fields"].__setitem__("workType", "Mining"), "workType")
        sg = first("Add", "ThingDef")
        fx("a sign loses its config-error field", lambda r: r["ThingDef"][sg["name"]]["fields"].__setitem__(sg["pairs"][0][0], False), sg["pairs"][0][0])
        wo = first("Replace", "WorldObjectDef")
        fx("settlement icon back to 1", lambda r: r["WorldObjectDef"][wo["name"]]["fields"].__setitem__("expandingIconDrawSize", 1.0), "expandingIconDrawSize")
        rm = first("Remove", "BiomeDef")
        last = rm["rest"].rstrip("/").split("/")[-1]
        fx("a removed animal reappears in the biome (%s)" % last, lambda r: r["BiomeDef"][rm["name"]]["fields"].__setitem__("wildAnimals", [{"animal": last, "commonality": 1}]), "still in the dump")
        rp = first("Replace", "RulePackDef")
        fx("the doubled apostrophe rule comes back", lambda r: r["RulePackDef"][rp["name"]]["fields"].__setitem__("rulePack", {"rulesStrings": ["maybeApostrophe->''"]}), "replaced-away")
        # GRiNDTerra's tex-path fixes were this break's fixture; they retired with that donor (2026-10-18). Any other active
        # PawnKindDef Replace with a `gone` texPath serves; none left means this break has nothing to bite, said aloud.
        pk = next((o for o in ops if o["cls"] == "Replace" and o["type"] == "PawnKindDef" and o["gone"] and all(any(g.lower() in active for g in grp) for grp in o["guards"])), None)
        if pk is not None:
            fx("an old texPath is still live (%s)" % pk["name"], lambda r: r["PawnKindDef"][pk["name"]]["fields"].__setitem__("lifeStages", [{"x": {"texPath": pk["gone"][0]}}]), "replaced-away")
        else:
            print("  skip break: no active PawnKindDef texPath Replace remains to break (UNMEASURED, not passed)")
        fx("an active donor's def vanishes (%s)" % wg["name"], lambda r: r["WorkGiverDef"].pop(wg["name"]), "not in the dump")
        fx("a FindMod name that no installed mod has", lambda r: None, "no installed mod is called", installed_=installed - {g.lower() for g in wg["guards"][0]})
        gone_names = {g.lower() for grp in wg["guards"] for g in grp}
        ck = v.effect_findings([wg], rows, active - gone_names, installed)
        check("break: the same op with its donor INACTIVE is skipped, not flagged", ck[0] == 0 and ck[1]["donor mod inactive"] == 1 and ck[2] == [], ck)
        ck = v.effect_findings([dict(wg, type="NoSuchDumpedType")], dict(rows, NoSuchDumpedType=None), active, installed)
        check("an undumped type is skipped and named", ck[0] == 0 and ck[1]["type not dumped"] == 1, ck)

        import runner
        from northstar_driver.session import FastSession
        from northstar_driver.transport import MockGame, MockTransport

        def chain(r_):
            saved = v._dump_inputs
            v._dump_inputs = lambda types: (r_, active)
            try:
                own = v.Suite("MandrakePatches")
                own.toggles = []
                own.chains = [(n, f) for n, f in v.suite.chains if n == "fix_effects_vs_dump_static"]
                with FastSession(transport=MockTransport(MockGame()), strict=False) as sess:
                    res = runner.run_suite(own, sess, anchor=None, mod=None)
            finally:
                v._dump_inputs = saved
            return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
        check("chain PASSes on the shipped patches", list(chain(rows).values()) == ["PASS"], chain(rows))
        r9 = copy.deepcopy(rows)
        r9["WorkGiverDef"][wg["name"]]["fields"]["workType"] = "Mining"
        check("chain reddens when a fix did not take", list(chain(r9).values()) == ["FAIL"], chain(r9))
    if FAILS:
        print("\n%d MandrakePatches selftest(s) FAILED" % len(FAILS))
        return 1
    if not rows:
        # the dump half never ran (unreadable dump, or an empty one): say so in the runner's own
        # phrase, never "all passed" - a skipped check is not a pass.
        print("\nUNMEASURED, not a pass or a fail (fix effects vs dump did not run)")
        return 0
    print("\nall MandrakePatches selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
