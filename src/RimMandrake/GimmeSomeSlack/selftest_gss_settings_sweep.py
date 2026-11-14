#!/usr/bin/env python3
"""T_SETTINGS_SWEEP_OFFLINE (GimmeSomeSlack 0.1.0, bars settings_switch_cleanly and mod_settings): the settings sweep, moved
out of the game as far as source can take it. No game, no build: a read of the mod's own source and scripts.

1. Every setting has an owner. For each key of the shipped floor table (validation.SHIPPED) and each AerialSettings field:
   an OFFLINE flip check (a SelfTest .cs compiled by the SelfTest csproj names it; T_CORE runs it and must be green), or the
   LIVE row that flips it (a live script sets it with set:<key>= or names it beside a probe set), with the reason it has no
   pure half: its read site is Verse-bound. A key with neither is refused.
2. Every setting is read. Each key has a production read site outside its settings class (GimmeSomeSlackSettings.<key> /
   AerialSettings.<key>, or the floor BuildOptions copy in GimmeSomeSlackMod.cs), so a flip reaches the game.
3. Every Harmony patch maps to exactly one switch. A [HarmonyPatch] class carries PatchFeature(label, settingsType, field)
   naming a real setting; or a label-only PatchFeature whose class body reads exactly the one setting BODY_GATED names; or
   it is an INFRA patch (save integrity, no switch by design: printed, see the journal's question); anything else is refused.

Planted (every run): a production read dropped (AerialSettings.maxStrands removed from the sources) and a [HarmonyPatch] class
with no gate must each be refused. Exit 0 PASS, 1 FAIL.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_settings_sweep.py [--list]
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
sys.path.insert(0, HERE)

# label-only PatchFeature classes gated inside their body by one setting: class -> (settings class, field)
BODY_GATED = {
    "Patch_Thing_Graphic_LampMasterOff": ("GimmeSomeSlackSettings", "enabled"),
    "RM_LiveWirePathCost": ("AerialSettings", "shockReach"),
}
# patches with no switch by design: class -> why (save integrity; a switch would break saves)
INFRA = {
    "Patch_GenTypes_LegacyTypeName": "loads saves written before the Messy Conduit rename; off would make those saves fail to load",
    "Patch_Map_ExposeComponents_SkipAerial": "keeps a save loadable without the mod; off would tie saves to the mod",
    "Patch_Game_ExposeSmallComponents_SkipSessionReset": "keeps the session-reset component out of saves (no state, no switch)",
    "Patch_Map_ExposeComponents_SkipCordGraph": "keeps the cord graph component out of saves, so a save loads without the mod",
    "Patch_Map_ExposeComponents_SkipConduitRuns": "keeps the conduit-runs component out of saves, so a save loads without the mod",
    "Patch_GameDataSaveLoader_SaveGame_DrainConduitRuns": "drains the unsaved style queue before any save, so a load never shows a second look",
    "Patch_MapDrawer_MapMeshDirty_MarkStale": "bookkeeping: marks a dirtied section stale for the cord layer; draws nothing, holds no state",
}
# derived values that are not settings
NOT_SETTINGS = {"fallenWireShock": "derived mirror of shockReach != None (AerialSettings.SyncDerived)", "Range": "a property: Clamp(maxSpan)"}


def read(p):
    return open(p, encoding="utf-8").read()


def nocomments(s):
    s = re.sub(r"//[^\n]*", "", s)
    return re.sub(r"/\*.*?\*/", "", s, flags=re.S)


def load():
    prod = {os.path.relpath(f, SRC).replace(os.sep, "/"): nocomments(read(f))
            for f in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)
            if "/SelfTest/" not in f.replace(os.sep, "/") and "/obj/" not in f.replace(os.sep, "/")}
    csproj = read(os.path.join(SRC, "SelfTest", "RimMandrakeGimmeSomeSlack.SelfTest.csproj"))
    compiled = set(re.findall(r'<Compile Include="([^"]+\.cs)"', csproj))
    st = {os.path.basename(f): nocomments(read(f)) for f in glob.glob(os.path.join(SRC, "SelfTest", "*.cs"))
          if os.path.basename(f) in compiled}
    live = {os.path.relpath(f, HERE): read(f) for f in glob.glob(os.path.join(HERE, "*.py")) + glob.glob(os.path.join(HERE, "northstar", "*.py"))
            if not os.path.basename(f).startswith("selftest")}
    return prod, st, live


def keys(prod):
    import validation as V
    aer = re.findall(r"public static (?:bool|float|int|string|WireSwayMode|ShockReach) (\w+) =", prod["Aerial/AerialSettings.cs"])
    return [("floor", "GimmeSomeSlackSettings", k) for k in V.SHIPPED] + \
           [("aerial", "AerialSettings", k) for k in aer if k not in NOT_SETTINGS]


def owners(prod, st, live):
    rows, faults = [], []
    for scope, cls, k in keys(prod):
        off = sorted(f for f, s in st.items() if re.search(r"\b%s\.%s\b|\b%s\s*[=:]|\"%s\b|\b%s\b(?=[^;\n]*(Check|==|!=))" % (cls, k, k, k, k), s))
        lv = sorted(f for f, s in live.items() if re.search(r"set:%s=|[\"']%s[\"']" % (k, k), s))
        reads = sorted(f for f, s in prod.items() if not f.endswith(("AerialSettings.cs",)) and
                       re.search(r"\b%s\.%s\b" % (cls, k), s) and not (f == "GimmeSomeSlackMod.cs" and cls == "AerialSettings"))
        if cls == "GimmeSomeSlackSettings" and not reads:   # the floor build options are filled in the settings file itself
            m = prod.get("GimmeSomeSlackMod.cs", "")
            region = m[m.find("new BuildOptions"):][:2500] if "new BuildOptions" in m else ""
            if re.search(r"\b%s\b" % k, region):
                reads = ["GimmeSomeSlackMod.cs (BuildOptions)"]
        owner = "offline" if off else "live" if lv else None
        rows.append((scope, k, owner, off or lv, reads))
        if not owner:
            faults.append("%s.%s: no offline flip check and no live row flips it" % (cls, k))
        if not reads:
            faults.append("%s.%s: no production read site: flipping it changes nothing" % (cls, k))
    return rows, faults


def patch_map(prod):
    rows, faults = [], []
    settings = {"GimmeSomeSlackSettings": prod.get("GimmeSomeSlackMod.cs", ""), "AerialSettings": prod.get("Aerial/AerialSettings.cs", "")}
    for f, s in prod.items():
        for m in re.finditer(r"((?:^[ \t]*\[[^\n]*\][ \t]*\n)+)[ \t]*(?:internal|public|private)?\s*(?:static\s+)?(?:sealed\s+)?class\s+(\w+)", s, re.M):
            attrs, name = m.group(1), m.group(2)
            if "HarmonyPatch" not in attrs:
                continue
            pf = re.search(r"PatchFeature\(\s*\"([^\"]+)\"(?:\s*,\s*typeof\((\w+)\)\s*,\s*\"(\w+)\")?\s*\)", attrs)
            if pf and pf.group(3):
                cls, field = pf.group(2), pf.group(3)
                ok = re.search(r"public static \w+ %s\b" % field, settings.get(cls, "")) is not None
                rows.append((name, "%s.%s" % (cls, field), "field"))
                if not ok:
                    faults.append("%s: PatchFeature names %s.%s, which is not a setting" % (name, cls, field))
            elif pf and name in BODY_GATED:
                cls, field = BODY_GATED[name]
                body = s[m.end():m.end() + 6000]
                body = body[:body.find("\n    }\n")] if "\n    }\n" in body else body
                got = set(re.findall(r"\b(GimmeSomeSlackSettings|AerialSettings)\.(\w+)\b", body))
                got = {g for g in got if g[1] not in ("Range",)}
                rows.append((name, "%s.%s" % (cls, field), "body"))
                if (cls, field) not in got:
                    faults.append("%s: label-only gate; its body does not read %s.%s" % (name, cls, field))
            elif name in INFRA:
                rows.append((name, "none (infra: %s)" % INFRA[name], "infra"))
            else:
                rows.append((name, None, "UNGATED"))
                faults.append("%s (%s): a Harmony patch no switch turns off" % (name, f))
    return rows, faults


def main(argv):
    prod, st, live = load()
    ok = True
    rows, f1 = owners(prod, st, live)
    prow, f2 = patch_map(prod)
    n_off = sum(1 for r in rows if r[2] == "offline")
    n_live = sum(1 for r in rows if r[2] == "live")
    print("settings: %d (%d floor, %d aerial): %d with an offline flip check, %d owned by a live row"
          % (len(rows), sum(r[0] == "floor" for r in rows), sum(r[0] == "aerial" for r in rows), n_off, n_live))
    print("patches: %d: %d by a settings field, %d gated in the body, %d infra (no switch by design)"
          % (len(prow), sum(r[2] == "field" for r in prow), sum(r[2] == "body" for r in prow), sum(r[2] == "infra" for r in prow)))
    if "--list" in argv:
        for r in rows:
            print("  %-6s %-22s %-7s %s | reads %s" % (r[0], r[1], r[2], ", ".join(r[3][:3]), ", ".join(r[4][:2])))
        for r in prow:
            print("  patch %-48s %s" % (r[0], r[1]))
    for f in f1 + f2:
        print("FAIL " + f)
        ok = False
    # planted: a dropped read site, an ungated patch
    p1 = {f: s.replace("AerialSettings.maxStrands", "3") for f, s in prod.items()}
    _, g1 = owners(p1, st, live)
    p2 = dict(prod)
    p2["Planted.cs"] = "    [HarmonyPatch(typeof(Pawn), \"Tick\")]\n    internal static class Patch_Planted_Ungated\n    {\n    }\n"
    _, g2 = patch_map(p2)
    planted = [any("maxStrands: no production read site" in x for x in g1), any("Patch_Planted_Ungated" in x for x in g2)]
    print("planted: a dropped AerialSettings.maxStrands read %s; an ungated patch %s"
          % tuple("refused" if p else "NOT CAUGHT" for p in planted))
    ok = ok and all(planted)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
