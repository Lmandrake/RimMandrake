#!/usr/bin/env python3
"""Offline proof of two planet looks: The Chill stays unlit, and the Twilight Sea carries its stained glass.

Items SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT and TWILIGHT_GLASS_WIRE_INTO_SWIRL_LAYER. The owner approved both looks on the
round-3 sheet (WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP, 2026-10-25); the prefill picks ship: Chill abyss with no sea films,
Twilight glass "panes v3". Page: design/specs/2026-11-26-world-sea-lists/boundary.md.

  1. EXECUTION: Source/RM_WorldLookLists.cs itself is compiled (dotnet.exe, net8.0 console) and run on the shipped
     defaults and on hand cases. Named mutants of that file must each turn a case red, or the cases are blind.
  2. WIRING: BuildSea scales both films by FilmScale under worldChillUnlit; the glass list is drawn under
     worldTwilightGlass with water biomes allowed, the swirl list with water excluded; both toggles are declared on,
     scribed, reset, drawn as checkboxes and part of the redraw key.
  3. TEXTURE: World/RM_Swirls/TwilightGlass.png is installed in TerminalBiomes and is byte-for-byte the pixels the
     sheet generator makes for the picked look (world_water_variants PANES3).
  4. SHIPPED: the committed RimMandrake.Biomes.dll is the one its .srchash stamped, built from these sources.
Each promise is a t_<name> function below (code_review_status.py reads them by name).

    python3 selftest_world_sea_lists.py [--part chill|glass]     one item's promises only (its outcome check)
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RM, "..", ".."))
sys.path.insert(0, os.path.join(RM, "Utils"))
sys.path.insert(0, os.path.join(RM, "Utils", "art"))

SRC = os.path.join(HERE, "Source")
LISTS_CS = os.path.join(SRC, "RM_WorldLookLists.cs")
LOOK_CS = os.path.join(SRC, "RM_WorldLook.cs")
MOD_CS = os.path.join(SRC, "RM_BiomesMod.cs")
DLL = os.path.join(HERE, "Assemblies", "RimMandrake.Biomes.dll")
GLASS_PNG = os.path.join(RM, "TerminalBiomes", "Textures", "World", "RM_Swirls", "TwilightGlass.png")
SEAS = ("RM_TheScald", "RM_GreySea", "RM_TwilightSea", "RM_TheChill")
# dotnet.exe needs a Windows drive (as selftest_world_paths_drawn.py)
EXEC_SCRATCH = os.environ.get("RM_SELFTEST_EXEC_SCRATCH", "/mnt/d/ClaudeWork/rimmandrake/selftest_tmp")

HARNESS = r'''
using System;
using System.Globalization;
using System.IO;
using RimMandrake.Biomes;
static class Harness
{
    static string F(float f) => f.ToString("R", CultureInfo.InvariantCulture);
    static void Main(string[] a)
    {
        foreach (string raw in File.ReadAllLines(a[0]))
        {
            string[] p = raw.Split('\t');
            if (p[0] == "F") Console.WriteLine("F\t" + p[1] + "\t" + p[2] + "\t" + F(RM_WorldLookLists.FilmScale(p[1], p[2])));
            else if (p[0] == "E")
            {
                var es = RM_WorldLookLists.Entries(p[1]);
                var parts = new System.Collections.Generic.List<string>();
                foreach (var e in es) parts.Add(e.biome + "|" + e.texture + "|" + F(e.widthsPerRepeat));
                Console.WriteLine("E\t" + p[1] + "\t" + string.Join(";", parts));
            }
            else if (p[0] == "U")
                Console.WriteLine("U\t" + p[1] + "\t" + p[2] + "\t" + p[3] + "\t" + F(RM_WorldLookLists.UvScale(
                    float.Parse(p[1], CultureInfo.InvariantCulture), float.Parse(p[2], CultureInfo.InvariantCulture),
                    float.Parse(p[3], CultureInfo.InvariantCulture))));
        }
    }
}
'''
CSPROJ = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><Nullable>disable</Nullable>
  <EnableDefaultCompileItems>false</EnableDefaultCompileItems><ImplicitUsings>disable</ImplicitUsings></PropertyGroup>
  <ItemGroup><Compile Include="Harness.cs" /><Compile Include="RM_WorldLookLists.cs" /></ItemGroup>
</Project>
'''


def read(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read()


def default_of(text, name):
    m = re.search(r'public static string %s = "([^"]*)";' % name, text)
    return m.group(1) if m else None


def cases(look):
    """(line sent, the answer that must come back). The shipped defaults are read from RM_WorldLook.cs."""
    films = default_of(look, "seaFilmOverrides") or ""
    glass = default_of(look, "glassBiomes") or ""
    swirl = default_of(look, "swirlBiomes") or ""
    out = []
    # the shipped film list: the Chill unlit, every other sea keeps its films
    for sea in SEAS:
        out.append((("F", films, sea), "0" if sea == "RM_TheChill" else "1"))
    # the grammar
    for ov, b, want in (("A=off", "A", "0"), ("A=0.5", "A", "0.5"), (" A = off ", "A", "0"), ("A=off", "B", "1"),
                        ("A=bogus", "A", "1"), ("A=-1", "A", "1"), ("", "A", "1"), ("A=off,B=0.25", "B", "0.25"),
                        ("A=2", "A", "2"), ("A", "A", "1"), ("A=off,A=0.5", "A", "0.5")):
        out.append((("F", ov, b), want))
    # the shipped glass list: the Twilight Sea, the picked texture, 40 tile widths per repeat (GLASS_PERIOD)
    out.append((("E", glass), "RM_TwilightSea|TwilightGlass|40"))
    # the shipped swirl list keeps its two land entries on the global scale
    out.append((("E", swirl), "RM_Abyss|Abyss|0;RM_TheRot|TheRot|0"))
    for lst, want in (("A=t@40", "A|t|40"), ("A=t", "A|t|0"), ("A=t@x", "A|t|0"), ("A=t@-3", "A|t|0"),
                      (" A = t @ 12.5 ,B=u", "A|t|12.5;B|u|0"), ("=t,A=,A", ""), ("", "")):
        out.append((("E", lst), want))
    for w, tile, fb, want in (("40", "0.5", "0.035", "0.05"), ("0", "0.5", "0.035", "0.035"), ("40", "0", "0.035", "0.035")):
        out.append((("U", w, tile, fb), want))
    return out


def run_lists(source, sent):
    """Compile `source` as RM_WorldLookLists.cs with the harness; feed the lines; -> {line: answer} or an error string."""
    os.makedirs(EXEC_SCRATCH, exist_ok=True)
    import winbuild
    where = tempfile.mkdtemp(prefix="sealists_", dir=EXEC_SCRATCH)
    try:
        for name, text in (("RM_WorldLookLists.cs", source), ("Harness.cs", HARNESS), ("SeaListsExec.csproj", CSPROJ),
                           ("in.txt", "\n".join("\t".join(s) for s in sent) + "\n")):
            with open(os.path.join(where, name), "w", encoding="utf-8") as f:
                f.write(text)
        dotnet = winbuild.dotnet_exe()
        built = None
        for _ in range(2):   # one retry, as selftest_world_paths_drawn.py (a fresh temp dir build once failed silently)
            built = winbuild.run_interop_captured([dotnet, "build", winbuild.win(os.path.join(where, "SeaListsExec.csproj")),
                                                   "-c", "Release", "--nologo", "-v", "quiet"], cwd=where,
                                                  capture_output=True, text=True, timeout=300)
            if built.returncode == 0:
                break
        if built.returncode != 0:
            return "build failed: " + (built.stdout + built.stderr)[-1200:]
        ran = winbuild.run_interop_captured([dotnet, winbuild.win(os.path.join(where, "bin", "Release", "net8.0", "SeaListsExec.dll")),
                                             winbuild.win(os.path.join(where, "in.txt"))], cwd=where, capture_output=True,
                                            text=True, timeout=200)
        if ran.returncode != 0:
            return "harness exited %d: %s" % (ran.returncode, (ran.stdout + ran.stderr)[-600:])
        got = {}
        for line in ran.stdout.replace("\r", "").splitlines():
            p = line.split("\t")
            got[tuple(p[:-1])] = p[-1]
        return got
    finally:
        shutil.rmtree(where, ignore_errors=True)


def same(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-6
    except ValueError:
        return a == b


def wrong(got, todo):
    if isinstance(got, str):
        return [got]
    return ["%s -> %r, want %r" % (" | ".join(s), got.get(s), w) for s, w in todo if got.get(s) is None or not same(got[s], w)]


MUTANTS = {   # each must turn a case red
    "off ignored": ('if (v == "off") scale = 0f;', 'if (v == "never") scale = 0f;'),
    "factor ignored": ("scale = f;", "scale = 1f;"),
    "negative accepted": ("f >= 0f &&", ""),
    "scale dropped": ("widthsPerRepeat = widths", "widthsPerRepeat = 0f"),
    "uv inverted": ("return 1f / (widthsPerRepeat * tileWidth);", "return widthsPerRepeat * tileWidth;"),
    "no fallback": ("if (widthsPerRepeat <= 0f || tileWidth <= 0f) return fallback;", "if (tileWidth < 0f) return fallback;"),
}


def t_chill_unlit_by_default(results):
    return results["shipped films"]


def t_film_override_grammar(results):
    return results["film grammar"]


def t_twilight_glass_listed(results):
    return results["glass list"]


def t_glass_scale_per_biome(results):
    return results["uv scale"]


def t_glass_draws_on_water(look):
    bad = []
    if not re.search(r'BuildSwirls\(layer, mine, glassBiomes, true, "glass"\)', look):
        bad.append("Wrap does not draw glassBiomes with water allowed")
    if not re.search(r'BuildSwirls\(layer, mine, swirlBiomes, false, "swirls"\)', look):
        bad.append("Wrap does not draw swirlBiomes with water excluded")
    if not re.search(r"if \(RM_BiomesSettings\.worldTwilightGlass\) sb\.Append", look):
        bad.append("the glass layer is not gated on worldTwilightGlass")
    if "RM_WorldLookLists.UvScale(" not in look:
        bad.append("BuildSwirls does not take a per-entry scale (RM_WorldLookLists.UvScale)")
    if not re.search(r"allowWater \|\| !b\.isWaterBiome", look):
        bad.append("SwirlMap does not let a listed water biome through when water is allowed")
    return bad


def t_chill_films_skipped(look):
    bad = []
    if not re.search(r"RM_BiomesSettings\.worldChillUnlit \? RM_WorldLookLists\.FilmScale\(seaFilmOverrides, ", look):
        bad.append("BuildSea does not read FilmScale under worldChillUnlit")
    if not re.search(r"if \(filmScale <= 0f\) (\{[^}]*)?continue;", look):
        bad.append("BuildSea does not skip a tile whose films are off")
    if look.count("filmScale * sea") < 2:
        bad.append("BuildSea does not scale both film alphas by filmScale")
    return bad


def t_toggles_scribed_and_drawn(mod):
    bad = []
    for field, label in (("worldChillUnlit", "Planet: The Chill stays unlit (no sea films) [now]"),
                         ("worldTwilightGlass", "Planet: Twilight Sea glass [now]")):
        for pin in ("public static bool %s = true;" % field, "%s = true;" % field,
                    'Scribe_Values.Look(ref %s, "%s", true);' % (field, field),
                    '"%s", ref RM_BiomesSettings.%s' % (label, field)):
            if pin not in mod:
                bad.append("RM_BiomesMod.cs has no %s" % pin)
        m = re.search(r"static string WorldLookKey\(\) => ([^;]+);", mod)
        if not m or ("RM_BiomesSettings." + field) not in m.group(1):
            bad.append("WorldLookKey leaves out %s (the planet would not redraw when it changes)" % field)
    return bad


def t_glass_texture_is_the_pick():
    if not os.path.exists(GLASS_PNG):
        return ["%s is not installed" % os.path.relpath(GLASS_PNG, REPO)]
    try:
        import numpy as np
        from PIL import Image
        import world_water_variants as WWV
        import biome_worldfaces as BW
    except Exception as e:   # numpy/PIL missing: cannot look
        return ["UNMEASURED: cannot import the sheet generator (%s)" % e]
    rgb, a = WWV.glass_tex("panes", WWV.hsv_shift(BW.F["TwilightSea"][0], *WWV.COLOURS["deep"]), **WWV.PANES3)
    want = np.dstack([np.clip(np.rint(rgb), 0, 255), np.rint(a * 255)]).astype(np.uint8)
    have = np.asarray(Image.open(GLASS_PNG).convert("RGBA"))
    if have.shape != want.shape:
        return ["TwilightGlass.png is %s, the pick is %s" % (have.shape, want.shape)]
    if not np.array_equal(have, want):
        return ["TwilightGlass.png differs from world_water_variants PANES3 (%d pixels)" % int((have != want).any(axis=2).sum())]
    return []


def t_dll_built_from_source():
    bad = []
    with open(DLL + ".srchash", encoding="utf-8") as f:
        lines = [l.split() for l in f if l.strip()]
    with open(DLL, "rb") as f:
        binary = f.read()
    if [l[2] for l in lines if l[:2] == ["#", "dll:"]] != [hashlib.sha256(binary).hexdigest()]:
        bad.append("the committed DLL is not the one its .srchash stamped")
    sources = [l for l in lines if l[0] != "#"]
    listed = {os.path.basename(l[1]) for l in sources}
    for needed in ("RM_WorldLookLists.cs", "RM_WorldLook.cs", "RM_BiomesMod.cs"):
        if needed not in listed:
            bad.append("the .srchash does not list %s" % needed)
    for digest, rel in sources:
        with open(os.path.join(SRC, rel), "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != digest:
                bad.append("the DLL was not built from this %s: rebuild it (winbuild.py BiomesShell)" % rel)
    for name in (b"RM_WorldLookLists", b"FilmScale", b"worldTwilightGlass", b"worldChillUnlit"):
        if name + b"\0" not in binary:
            bad.append("the committed DLL has no %s" % name.decode())
    return bad


PARTS = {"chill": {"chill_unlit_by_default", "film_override_grammar", "chill_films_skipped", "toggles_scribed_and_drawn",
                   "dll_built_from_source", "mutants"},
         "glass": {"twilight_glass_listed", "glass_scale_per_biome", "glass_draws_on_water", "toggles_scribed_and_drawn",
                   "glass_texture_is_the_pick", "dll_built_from_source", "mutants"}}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    part = argv[argv.index("--part") + 1] if "--part" in argv else None
    if part is not None and part not in PARTS:
        print("usage: selftest_world_sea_lists.py [--part chill|glass]")
        return 2
    look, mod = read(LOOK_CS), read(MOD_CS)
    bad = {}
    if not os.path.exists(LISTS_CS):
        got = "Source/RM_WorldLookLists.cs does not exist"
        source = None
    else:
        source = read(LISTS_CS)
    todo = cases(look)
    groups = {"shipped films": [c for c in todo if c[0][0] == "F" and c[0][2] in SEAS],
              "film grammar": [c for c in todo if c[0][0] == "F" and c[0][2] not in SEAS],
              "glass list": [c for c in todo if c[0][0] == "E" and c[0][1] in (default_of(look, "glassBiomes") or "\0",
                                                                               default_of(look, "swirlBiomes") or "\0")],
              "uv scale": [c for c in todo if c[0][0] == "U"]}
    groups["glass list"] += [c for c in todo if c[0][0] == "E" and c not in groups["glass list"]]
    if default_of(look, "seaFilmOverrides") is None:
        bad["chill_unlit_by_default"] = ["RM_WorldLook.cs has no public static string seaFilmOverrides"]
    if default_of(look, "glassBiomes") is None:
        bad["twilight_glass_listed"] = ["RM_WorldLook.cs has no public static string glassBiomes"]
    if source is not None:
        got = run_lists(source, [s for s, _ in todo])
    results = {k: wrong(got, v) for k, v in groups.items()}
    for name, fn, arg in (("chill_unlit_by_default", t_chill_unlit_by_default, results),
                          ("film_override_grammar", t_film_override_grammar, results),
                          ("twilight_glass_listed", t_twilight_glass_listed, results),
                          ("glass_scale_per_biome", t_glass_scale_per_biome, results),
                          ("glass_draws_on_water", t_glass_draws_on_water, look),
                          ("chill_films_skipped", t_chill_films_skipped, look),
                          ("toggles_scribed_and_drawn", t_toggles_scribed_and_drawn, mod),
                          ("glass_texture_is_the_pick", lambda _: t_glass_texture_is_the_pick(), None),
                          ("dll_built_from_source", lambda _: t_dll_built_from_source(), None)):
        found = fn(arg)
        if found:
            bad.setdefault(name, []).extend(found)
    # mutants: only worth running on a source that passes
    if source is not None and not any(k in bad for k in ("chill_unlit_by_default", "film_override_grammar",
                                                         "twilight_glass_listed", "glass_scale_per_biome")):
        for mname, (old, new) in MUTANTS.items():
            if old not in source:
                bad.setdefault("mutants", []).append("mutant '%s' did not apply (the source moved; update it)" % mname)
                continue
            mgot = run_lists(source.replace(old, new, 1), [s for s, _ in todo])
            if isinstance(mgot, str) or not wrong(mgot, todo):
                bad.setdefault("mutants", []).append("mutant '%s' stayed green: the cases are blind" % mname)
    if part is not None:   # the shared toggle and DLL checks keep only the lines about this item's own field
        other = {"chill": "Glass", "glass": "Chill"}[part]
        bad = {k: [e for e in v if k != "toggles_scribed_and_drawn" or other not in e]
               for k, v in bad.items() if k in PARTS[part]}
        bad = {k: v for k, v in bad.items() if v}
    for k, v in bad.items():
        for e in v:
            print("FAIL %s: %s" % (k, e))
    if bad:
        print("RESULT: FAIL")
        return 1
    print("ran RM_WorldLookLists.cs on %d cases; %d mutants all caught; glass texture = the pick; DLL fresh" % (len(todo), len(MUTANTS)))
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
