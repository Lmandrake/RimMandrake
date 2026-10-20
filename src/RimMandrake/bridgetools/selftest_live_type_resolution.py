#!/usr/bin/env python3
"""Offline guard: JawaBench resolves a mod type by NAME to the copy the game's code runs, never a stale twin.

RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD A3, LIVE 2026-10-20 (Transient/live_testing_2026-10-20a): on the 380 list
`jawa/mod_settings_field set rhossakBindEnabled=False` read back False while the rhossak's pane kept saying "Bound to
twisting thornwood" for 600 real ticks, twice. The deployed comp's IL reads that static and returns null when it is
False, so the bridge had written a DIFFERENT copy of the static. Prepatcher (zetrith.prepatcher; VEF, BigAndSmall,
yayoAni and CombatAI carry [PrepatcherField]s) reloads every patched assembly and all its dependants
(Reloader.PropagateNeedsReload) and leaves the pre-patch originals in the AppDomain, earlier in GetAssemblies() order;
the tool took the first FullName match there.

Checks, on the companion source:
  1. ResolveLiveType exists and asks GenTypes.GetTypeInAnyAssembly (the def loader's resolver, which walks
     LoadedModManager.RunningMods) BEFORE any AppDomain scan, and its fallback skips ReflectionOnly assemblies.
  2. mod_settings_field, static_call, and the shadegrid / cathedral / lore-stage lookups go through it.
  3. No file in the companion still resolves a type with the old "first FullName match in the AppDomain" shape.
  4. Every mod_settings_field reply (list / get / set) carries typeIdentity, so a run can see which copy it wrote.
Proven able to fail: each check is run against a mutated copy of the source that must make it go red.

    python3 src/RimMandrake/bridgetools/selftest_live_type_resolution.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "JawaBench.BridgeTools")

OLD_SHAPE = re.compile(
    r"AppDomain\.CurrentDomain\.GetAssemblies\(\)\s*"
    r"(?:\.SelectMany\([^;]*?GetTypes\(\)[^;]*?\)\s*\.FirstOrDefault\(\s*\w+\s*=>\s*\w+\.FullName\s*==|"
    r"\.Select\([^;]*?GetType\([^;]*?\)\s*\.FirstOrDefault\()", re.S)

USERS = {
    "JawaBenchModSettingsFieldTools.cs": "ResolveLiveType(typeName",
    "JawaBenchCompanionProbeTools.cs": "ResolveLiveType(type,",
    "JawaBenchShadeGridTools.cs": "ResolveLiveType(fullName",
    "JawaBenchCathedralAttitudeTools.cs": "ResolveLiveType(\"RimMandrake.RustCathedral",
    "JawaBenchLoreStageTools.cs": "ResolveLiveType(\"RimMandrake.LoreStages",
}


def load():
    files = {}
    for fn in sorted(os.listdir(SRC)):
        if fn.endswith(".cs"):
            with open(os.path.join(SRC, fn), encoding="utf-8-sig") as fh:
                files[fn] = fh.read()
    return files


def check(files):
    bad = []
    msf = files.get("JawaBenchModSettingsFieldTools.cs", "")
    m = re.search(r"internal static Type ResolveLiveType\(.*?\n        \}\n", msf, re.S)
    if not m:
        bad.append("ResolveLiveType is missing from JawaBenchModSettingsFieldTools.cs")
    else:
        body = m.group(0)
        g = body.find("GenTypes.GetTypeInAnyAssembly")
        # the copy COUNT may scan the AppDomain first; the RESOLUTION must not: the first `return` of a type
        # must come after the GenTypes call
        first_ret = body.find("return live;")
        if g < 0 or first_ret < 0 or first_ret < g:
            bad.append("ResolveLiveType does not resolve through GenTypes.GetTypeInAnyAssembly first")
        if "ReflectionOnly" not in body:
            bad.append("ResolveLiveType's AppDomain fallback does not skip ReflectionOnly assemblies")
    for fn, needle in USERS.items():
        if needle not in files.get(fn, ""):
            bad.append("%s no longer resolves its type through ResolveLiveType (%r)" % (fn, needle))
    for fn, text in files.items():
        if OLD_SHAPE.search(text):
            bad.append("%s resolves a type by the first FullName match in the AppDomain (a pre-Prepatcher twin)" % fn)
    for action in ("list", "get", "set"):
        if not re.search(r'action = "%s".{0,400}?typeIdentity' % action, msf, re.S):
            bad.append("mod_settings_field '%s' reply does not carry typeIdentity" % action)
    return bad


def mutations(files):
    """Each mutation must turn the check red; returns the ones that did not."""
    msf = "JawaBenchModSettingsFieldTools.cs"
    old_scan = ('AppDomain.CurrentDomain.GetAssemblies()\n                .SelectMany(a => { try { return a.GetTypes(); } '
                'catch { return Array.Empty<Type>(); } })\n                .FirstOrDefault(t => t.FullName == fullName);')
    muts = {
        "GenTypes call removed": (msf, lambda s: s.replace("GenTypes.GetTypeInAnyAssembly(typeName)", "null")),
        "ReflectionOnly filter removed": (msf, lambda s: s.replace("!a.ReflectionOnly", "true")),
        "typeIdentity dropped from get": (msf, lambda s: s.replace(
            "value = SafeFieldToString(fi.GetValue(target)), typeIdentity,", "value = SafeFieldToString(fi.GetValue(target)),")),
        "shadegrid back on the AppDomain": ("JawaBenchShadeGridTools.cs", lambda s: s.replace(
            "ResolveLiveType(fullName, out _, out _);", old_scan)),
    }
    survived = []
    for name, (fn, f) in muts.items():
        mutated = dict(files)
        mutated[fn] = f(files[fn])
        if mutated[fn] == files[fn] or not check(mutated):
            survived.append(name)
    return survived


def main():
    files = load()
    bad = check(files)
    survived = mutations(files)
    if survived:
        bad.append("mutations the check did not catch: %s" % survived)
    if bad:
        for b in bad:
            print("  BAD:", b)
        print("selftest live type resolution: FAIL (%d)" % len(bad))
        return 1
    print("selftest live type resolution: %d files, ResolveLiveType wired in %d, 4/4 mutations caught -> PASS"
          % (len(files), len(USERS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
