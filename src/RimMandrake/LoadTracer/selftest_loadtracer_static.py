#!/usr/bin/env python3
"""L0 acceptance for LoadTracer (mandrake.rm.loadtracer): no game, no build, no bridge.

LoadTracer has no tunable logic - it replaces one engine loop with a copy that logs. So the whole risk is DRIFT: the copy stops
being equivalent to the engine's CallAll, or a patch target is renamed by a game update and the tracer silently arms nothing.
This test pins, against the decompiled engine tree and the mod source:
  - the copied loop does what CallAll does (same enumeration, same RunClassConstructor, same error text, sets coreStaticAssetsLoaded
    last, returns false so the original does not run twice) and falls back to the ORIGINAL (returns true) if enumeration fails
  - all three patch targets exist in the engine as public static parameterless methods, and the two bracketed stages really run inside
    PlayDataLoader after CallAll (the stall bracket claim in the file's header)
  - every Harmony HarmonyMethod names a public static method that exists on LoadTracerPatches
  - per-type lines use UnityEngine.Debug.Log, never Verse.Log (the 1000-message cap is the reason this mod exists)
  - About/csproj/DLL agree (packageId, harmony id, Compile list, shipped assembly)
It then PLANTS each break in memory and proves it is caught. Nothing on disk is written.

    python3 src/RimMandrake/LoadTracer/selftest_loadtracer_static.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.environ.get("RIMWORLD_DECOMPILED", "/mnt/d/Luke/dev/reference/rimworld-decompiled")


def rd(*p):
    with open(os.path.join(*p), encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def findings(cs, ctor_util, loader, atlas, floatmenu, about, csproj, dll_present):
    out = []
    code = strip_comments(cs)
    eng = strip_comments(ctor_util)
    # --- engine side: the thing we copy
    m = re.search(r"public static void CallAll\(\)\s*\{(.*?)\n\t\}", eng, re.S)
    if not m:
        return ["engine: StaticConstructorOnStartupUtility.CallAll() not found (renamed or no longer parameterless static)"]
    eng_body = m.group(1)
    for needle, why in (("GenTypes.AllTypesWithAttribute<StaticConstructorOnStartup>()", "enumeration source"),
                        ("RuntimeHelpers.RunClassConstructor(item.TypeHandle)", "per-type call"),
                        ('"Error in static constructor of "', "error text"),
                        ("coreStaticAssetsLoaded = true", "completion flag")):
        if needle not in eng_body:
            out.append("engine CallAll no longer contains %s (%s): the tracer's copy has drifted" % (needle, why))
    # --- mod side: the copy
    m = re.search(r"public static bool CallAllPrefix\(\)\s*\{(.*?)\n        \}", code, re.S)
    if not m:
        return out + ["mod: LoadTracerPatches.CallAllPrefix() not found"]
    body = m.group(1)
    for needle, why in (("GenTypes.AllTypesWithAttribute<StaticConstructorOnStartup>()", "enumeration source"),
                        ("RuntimeHelpers.RunClassConstructor(item.TypeHandle)", "per-type call"),
                        ('"Error in static constructor of "', "error text"),
                        ("StaticConstructorOnStartupUtility.coreStaticAssetsLoaded = true", "completion flag")):
        if needle not in body:
            out.append("mod CallAllPrefix lost %s (%s): not equivalent to the engine loop" % (needle, why))
    if not re.search(r"return false;\s*\}\s*$", body.strip() + "}") and "return false;" not in body:
        out.append("mod CallAllPrefix never returns false: the original CallAll would run a second time")
    if body.rfind("return false;") < body.rfind("coreStaticAssetsLoaded"):
        out.append("mod CallAllPrefix sets coreStaticAssetsLoaded after returning false (flag never set)")
    catch_part = body.split("catch (Exception ex)", 1)
    if len(catch_part) < 2 or "return true;" not in catch_part[1].split("int i = 0;")[0]:
        out.append("mod CallAllPrefix does not fall back to the original (return true) when type enumeration throws")
    if re.search(r"\bLog\.Message\([^;]*(ctor|CallAll)", body):
        out.append("mod CallAllPrefix traces through Verse.Log: it stops logging at 1000 messages, which is why this mod exists")
    if "UnityEngine.Debug.Log(\"[LoadTracer] ctor \"" not in body:
        out.append("mod CallAllPrefix no longer logs one line per type through UnityEngine.Debug.Log")
    # --- patch targets exist in the engine
    targets = (("StaticConstructorOnStartupUtility", "CallAll", eng_has(ctor_util, "CallAll")),
               ("FloatMenuMakerMap", "Init", eng_has(floatmenu, "Init")),
               ("GlobalTextureAtlasManager", "BakeStaticAtlases", eng_has(atlas, "BakeStaticAtlases")))
    for cls, meth, ok in targets:
        if not ok:
            out.append("engine %s.%s() is gone or not public static parameterless: Harmony would throw at arm time" % (cls, meth))
        if cls == "StaticConstructorOnStartupUtility":
            continue
        if not re.search(r'AccessTools\.Method\(typeof\(%s\),\s*(?:nameof\(%s\.%s\)|"%s")' % (cls, cls, meth, meth), code):
            out.append("mod no longer patches %s.%s" % (cls, meth))
    if not re.search(r"AccessTools\.Method\(typeof\(StaticConstructorOnStartupUtility\),\s*nameof\(StaticConstructorOnStartupUtility\.CallAll\)\)", code):
        out.append("mod no longer patches StaticConstructorOnStartupUtility.CallAll")
    # the two brackets really run after CallAll inside PlayDataLoader
    ld = strip_comments(loader)
    pos = [ld.find(x) for x in ("StaticConstructorOnStartupUtility.CallAll();", "FloatMenuMakerMap.Init();", "GlobalTextureAtlasManager.BakeStaticAtlases();")]
    if min(pos) < 0 or not (pos[0] < pos[1] < pos[2]):
        out.append("engine PlayDataLoader no longer runs CallAll -> FloatMenuMakerMap.Init -> BakeStaticAtlases in that order: the header's bracket claim is false")
    # --- every HarmonyMethod names a real patch method
    declared = set(re.findall(r"public static \w+ (\w+)\(", code))
    named = re.findall(r"nameof\(LoadTracerPatches\.(\w+)\)", code)
    for n in named:
        if n not in declared:
            out.append("HarmonyMethod names LoadTracerPatches.%s which is not a public static method" % n)
    if len(named) != 5:
        out.append("expected 5 patch hooks (CallAll prefix, FloatMenu pre/post, Bake pre/post), found %d" % len(named))
    # --- metadata agreement
    try:
        pid = ET.fromstring(about.encode("utf-8")).findtext("packageId")
    except ET.ParseError as e:
        return out + ["About.xml does not parse: %s" % e]
    hid = re.search(r'new Harmony\("([^"]+)"\)', code)
    if pid != "mandrake.rm.loadtracer":
        out.append("About packageId %r is not mandrake.rm.loadtracer" % pid)
    if not hid or hid.group(1) != pid:
        out.append("Harmony id %r differs from packageId %r" % (hid.group(1) if hid else None, pid))
    if '<Compile Include="LoadTracer.cs" />' not in csproj:
        out.append("csproj does not compile LoadTracer.cs (EnableDefaultCompileItems is false: it would build nothing)")
    if not dll_present:
        out.append("Assemblies/LoadTracer.dll is not shipped")
    return out


def eng_has(text, name):
    return re.search(r"public static void %s\(\)" % name, text) is not None


def main():
    if not os.path.isfile(os.path.join(ENGINE, "Verse", "StaticConstructorOnStartupUtility.cs")):
        print("UNMEASURED, not a pass or a fail: decompiled engine tree not reachable at %s" % ENGINE)
        return 2
    cs = rd(HERE, "Source", "LoadTracer.cs")
    inputs = dict(cs=cs, ctor_util=rd(ENGINE, "Verse", "StaticConstructorOnStartupUtility.cs"), loader=rd(ENGINE, "Verse", "PlayDataLoader.cs"),
                  atlas=rd(ENGINE, "Verse", "GlobalTextureAtlasManager.cs"), floatmenu=rd(ENGINE, "RimWorld", "FloatMenuMakerMap.cs"),
                  about=rd(HERE, "About", "About.xml"), csproj=rd(HERE, "Source", "LoadTracer.csproj"),
                  dll_present=os.path.isfile(os.path.join(HERE, "Assemblies", "LoadTracer.dll")))
    fails = []

    def check(name, cond, detail=""):
        print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
        if not cond:
            fails.append(name)

    check("sanity probe: sources non-trivial", all(len(v) > 200 for k, v in inputs.items() if isinstance(v, str)), {k: len(v) for k, v in inputs.items() if isinstance(v, str)})
    base = findings(**inputs)
    check("shipped mod + engine: clean", base == [], base)

    def brk(tag, key, old, new, must):
        assert old in inputs[key], "planted break target missing: %r" % old       # a break that matches nothing proves nothing
        got = findings(**dict(inputs, **{key: inputs[key].replace(old, new, 1)}))
        check("break %-46s" % tag, any(must in g for g in got), got)

    brk("error text changed", "cs", '"Error in static constructor of "', '"Error in ctor of "', "error text")
    brk("prefix never returns false", "cs", "return false;", "return true;", "returns false")
    brk("completion flag dropped", "cs", "StaticConstructorOnStartupUtility.coreStaticAssetsLoaded = true;", "", "completion flag")
    brk("enumeration failure no longer falls back", "cs", "return true; // run the original", "return false; // run the original", "fall back")
    brk("per-type line moved to Verse.Log", "cs", 'UnityEngine.Debug.Log("[LoadTracer] ctor "', 'Log.Message("[LoadTracer] ctor "', "Debug.Log")
    brk("RunClassConstructor replaced", "cs", "RuntimeHelpers.RunClassConstructor(item.TypeHandle)", "item.TypeInitializer?.Invoke(null, null)", "per-type call")
    brk("Bake patch target renamed", "cs", "nameof(GlobalTextureAtlasManager.BakeStaticAtlases)", "nameof(GlobalTextureAtlasManager.BakeAtlases)", "no longer patches")
    brk("hook name typo", "cs", "nameof(LoadTracerPatches.BakePostfix)", "nameof(LoadTracerPatches.BakePostfx)", "not a public static")
    brk("Harmony id drifts from packageId", "cs", '"mandrake.rm.loadtracer"', '"mandrake.rm.loadtracr"', "Harmony id")
    brk("csproj drops the source", "csproj", '<Compile Include="LoadTracer.cs" />', "", "csproj")
    brk("packageId changed", "about", "<packageId>mandrake.rm.loadtracer</packageId>", "<packageId>mandrake.rm.tracer</packageId>", "packageId")
    brk("engine renames Init", "floatmenu", "public static void Init()", "public static void Initialize()", "FloatMenuMakerMap.Init")
    brk("engine renames BakeStaticAtlases", "atlas", "public static void BakeStaticAtlases()", "public static void Bake()", "BakeStaticAtlases")
    brk("engine CallAll gains a new error text", "ctor_util", '"Error in static constructor of "', '"Static ctor failed: "', "error text")
    brk("engine drops the Init stage", "loader", "FloatMenuMakerMap.Init();", "", "bracket claim")
    got = findings(**dict(inputs, dll_present=False))
    check("break shipped DLL missing", any("not shipped" in g for g in got), got)
    print("selftest_loadtracer_static: %s" % ("FAIL (%d)" % len(fails) if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
