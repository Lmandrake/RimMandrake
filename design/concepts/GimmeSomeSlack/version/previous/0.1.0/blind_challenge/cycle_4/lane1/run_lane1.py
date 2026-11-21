#!/usr/bin/env python3
"""Blind lane 1, GimmeSomeSlack 0.1.0 cycle 4. One command:
    python3 run_lane1.py [--kernel <AerialMath.cs>] [--mod <mod dir>] [--out <rows.jsonl>]
Rows from three sources, written from the bars alone (tree.json, sheet.md, plan.md) and the shipped settings:
  * BlindLane1.cs against the production kernel AerialMath.cs (+ ConduitPlacementGate.cs), built with the per-user Windows
    dotnet under <agent storage>/scratch/gimmesomeslack_blind_c4_lane1 (dotnet.exe cannot build from a WSL path);
  * the no-hose scan (bars no_hose, no_hose_in_gss): defs, patches, textures, C# declarations and literals, and the shipped
    DLL's type table read with a metadata reader (BlindLane1 --types), never a string scan;
  * the shipped settings: field default == Scribe default == ResetToDefaults == inside the slider range;
  * not_kernel rows for the bars whose logic is game-side (UNSETTLED, owed to Stage 6).
Exit 0 = every decided row PASS; 1 = a FAIL."""
import argparse, glob, json, os, re, shutil, subprocess, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""
rows = []


def row(id, bars, kind, verdict, cases, detail):
    rows.append({"id": id, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail})


def words(ident):
    """camelCase / snake / path identifier -> lower-case words (RM_HoseReel -> rm, hose, reel)."""
    out = []
    for part in re.split(r"[^A-Za-z0-9]+", ident):
        out += [w.lower() for w in re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+", part)]
    return out


HOSE = {"hose", "hoses", "reel", "reels"}
PIPE = {"pipe", "pipes"}


def strip_cs_comments(src):
    # one pass, strings kept whole, so a "//" inside a literal is not a comment
    return re.sub(r'"(?:[^"\\\n]|\\.)*"|//[^\n]*|/\*.*?\*/', lambda m: m.group(0) if m.group(0).startswith('"') else "", src, flags=re.S)


def no_hose_rows(mod, dotnet, dll_run):
    bars = ["no_hose", "no_hose_in_gss"]
    # defs + patches: every tag, attribute value and element text that is not prose (description/label are prose)
    PROSE = {"description", "label", "labelShort", "jobString", "reportString", "text", "letterText", "letterLabel", "tooltip"}
    hits, pipe_hits, n = [], [], 0
    for f in sorted(glob.glob(os.path.join(mod, "Defs/**/*.xml"), recursive=True) + glob.glob(os.path.join(mod, "Patches/**/*.xml"), recursive=True)):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as e:
            hits.append("%s unparseable: %s" % (os.path.relpath(f, mod), e)); continue
        for el in root.iter():
            n += 1
            vals = [el.tag] + list(el.attrib.values()) + ([] if el.tag in PROSE else [(el.text or "").strip()])
            for v in vals:
                if not v or len(v) > 300: continue
                w = set(words(v))
                if w & HOSE: hits.append("%s <%s> %r" % (os.path.relpath(f, mod), el.tag, v[:80]))
                elif w & PIPE: pipe_hits.append("%s <%s> %r" % (os.path.relpath(f, mod), el.tag, v[:80]))
    row("nohose_defs_patches", bars, "fixed", "FAIL" if hits else "PASS", n,
        ("hose/reel in def or patch fields: " + "; ".join(hits[:8])) if hits else
        "no def, patch, class, comp or texPath field under Defs/ or Patches/ names a hose or reel (%d elements; prose fields skipped)" % n)

    # textures: every file under Textures/ (the false pass the bar names: a scan of def names only misses a texture folder)
    tex = [os.path.relpath(p, mod) for p in glob.glob(os.path.join(mod, "Textures/**/*"), recursive=True) if os.path.isfile(p)]
    th = [t for t in tex if set(words(t)) & HOSE]
    tp = [t for t in tex if set(words(t)) & PIPE]
    row("nohose_textures", bars, "fixed", "FAIL" if th else "PASS", len(tex),
        ("hose/reel textures: " + "; ".join(th[:8])) if th else "no texture path under Textures/ names a hose or reel (%d files; pipe-named: %d)" % (len(tex), len(tp)))

    # C#: declared type names and string literals (texture paths, defNames) outside SelfTest, comments stripped
    decl, lits, files, exempt = [], [], 0, []
    for f in sorted(glob.glob(os.path.join(mod, "Source/**/*.cs"), recursive=True)):
        if "/SelfTest/" in f or "/obj/" in f or "/bin/" in f: continue
        files += 1
        src = strip_cs_comments(open(f, encoding="utf-8", errors="replace").read())
        for m in re.finditer(r"\b(class|struct|enum|interface|record)\s+([A-Za-z_][A-Za-z0-9_]*)", src):
            if set(words(m.group(2))) & HOSE: decl.append("%s %s" % (os.path.relpath(f, mod), m.group(2)))
        if f.endswith("/Core/LegacyName.cs"):
            # the settings-file rename table: "FireHosesMod" names the OLD settings file FlowWorks imports once; no def,
            # texture or class of GSS. Exempted by name so the exemption is visible.
            exempt.append("Core/LegacyName.cs (settings-file migration table)"); continue
        for m in re.finditer(r'"((?:[^"\\\n]|\\.)*)"', src):
            s = m.group(1)
            # only identifier-like literals (defNames, texture paths, type names); UI sentences are prose
            if " " in s.strip(): continue
            if set(words(s)) & HOSE: lits.append("%s %r" % (os.path.relpath(f, mod), s[:80]))
    bad = decl + lits
    row("nohose_csharp", bars, "fixed", "FAIL" if bad else "PASS", files,
        ("hose/reel types or literals: " + "; ".join(bad[:8])) if bad else
        "no type declared, and no defName or texture-path literal, names a hose or reel in %d C# files outside SelfTest (comments and UI prose skipped; literals exempt: %s)" % (files, ", ".join(exempt) or "none"))

    # the shipped DLL: its TypeDefinition table and resources (a stale assembly could ship a type the source lost)
    dlls = sorted(glob.glob(os.path.join(mod, "Assemblies/*.dll")))
    types, dbad = 0, []
    for d in dlls:
        out = dll_run(d)
        if out is None: dbad.append("could not read " + os.path.basename(d)); continue
        for t in out:
            types += 1
            if set(words(t)) & HOSE: dbad.append(os.path.basename(d) + ":" + t)
    v = "UNSETTLED" if not dlls or any(b.startswith("could not") for b in dbad) else ("FAIL" if dbad else "PASS")
    row("nohose_shipped_dll_types", bars, "fixed", v, types,
        ("hose/reel types in the shipped DLL: " + "; ".join(dbad[:8])) if dbad else
        "the shipped assembl%s %s declare%s no hose or reel type (%d types and resources, metadata reader)" %
        ("y" if len(dlls) == 1 else "ies", ", ".join(os.path.basename(d) for d in dlls), "s" if len(dlls) == 1 else "", types))

    # pipe drawing: the bar's words say "no hose, reel or pipe is drawn"; its oracle and red name hoses and reels only.
    # GSS draws the overhead span between two FlowWorks pipe poles (AerialLineKind.Pipe) with the pipe def's art.
    pipe_code = []
    for f in sorted(glob.glob(os.path.join(mod, "Source/**/*.cs"), recursive=True)):
        if "/SelfTest/" in f: continue
        src = strip_cs_comments(open(f, encoding="utf-8", errors="replace").read())
        k = len(re.findall(r"\bAerialLineKind\.Pipe\b|\bPipeMats\b", src))
        if k: pipe_code.append("%s x%d" % (os.path.relpath(f, mod), k))
    row("nohose_pipe_span_drawing", bars, "info", "INFO", len(pipe_code),
        "the bar's words say no pipe is drawn by this mod, but its oracle and red name hoses and reels only; GSS code draws the "
        "overhead span of FlowWorks pipe poles (AerialLineKind.Pipe / PipeMats) in: " + "; ".join(pipe_code) +
        (" | pipe-named def fields: " + "; ".join(pipe_hits[:4]) if pipe_hits else "") +
        ". Not a hose or reel; the pipe-pole span is required by another bar (settings_switch_cleanly: pipe poles have their own switch). Read in lane 2.")


def settings_rows(mod):
    """Shipped defaults: the field initialiser, the Scribe default, ResetToDefaults and the slider range agree."""
    bad, n = [], 0
    for rel in ("Source/Aerial/AerialSettings.cs", "Source/GimmeSomeSlackMod.cs"):
        src = open(os.path.join(mod, rel), encoding="utf-8").read()
        init = {m.group(2): m.group(3).strip() for m in re.finditer(r"public static (bool|int|float|double|[A-Z][A-Za-z.]+) ([a-zA-Z]+) = ([^;]+);", src)}
        scribe = {m.group(1): m.group(3).strip() for m in re.finditer(r'Scribe_Values\.Look\(ref ([a-zA-Z]+), "([A-Za-z]+)", ([^)]+)\)', src)}
        reset_m = re.search(r"void ResetToDefaults\(\)\s*\{(.*?)\n        \}", src, re.S)
        reset = {m.group(1): m.group(2).strip() for m in re.finditer(r"^\s*([a-zA-Z]+) = ([^;]+);", reset_m.group(1), re.M)} if reset_m else {}
        slider = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r"([a-zA-Z]+) = [^;]*?Slider\(\1, ([^,]+), ([^)]+?)\)", src)}
        def num(s):
            s = s.strip().rstrip("fFdD")
            try: return float(s)
            except ValueError: return None
        for name, v in scribe.items():
            n += 1
            if name in ("loopBudget", "legacy"): continue          # a legacy-migration sentinel (LegacyName.Unset), not a default
            if name in init and init[name] != v: bad.append("%s %s: field %s, Scribe %s" % (rel, name, init[name], v))
            if reset and name in reset and reset[name] != v: bad.append("%s %s: Scribe %s, Reset %s" % (rel, name, v, reset[name]))
            if name in slider:
                lo, hi, dv = num(slider[name][0]), num(slider[name][1]), num(v)
                if lo is not None and hi is not None and dv is not None and not (lo <= dv <= hi):
                    bad.append("%s %s: default %s outside slider %s..%s" % (rel, name, v, lo, hi))
        if reset_m is None: bad.append(rel + ": no ResetToDefaults found")
    row("settings_defaults_agree", ["settings_switch_cleanly", "mod_settings"], "sweep", "FAIL" if bad else "PASS", n,
        ("; ".join(bad[:10])) if bad else
        "%d saved settings: field default = Scribe default = ResetToDefaults, every slider default inside its range" % n)


NOT_KERNEL = [
    ("conduit_invisible", "conduit draws no pipe and the power overlay works: rendering, game-side"),
    ("cords_lie_slack", "floor-cord lay lives in CordBuilder/CordSlacken, not in a named *Math/*Kernel file"),
    ("no_unforced_sharp_turn", "floor-cord curvature: CordBuilder, not a named kernel"),
    ("cords_meet_walls_at_face", "floor cords against walls: CordBuilder/CordGraph, not a named kernel"),
    ("strip_at_every_junction", "junction art per look: rendering"),
    ("dense_block_tangle", "an eye judgement on a dense block"),
    ("cord_shape_variation_probe", "the shape-distance instrument lives game-side (CordShapeAudit)"),
    ("cords_never_repeat", "shape distance across a room: instrument + judge"),
    ("cut_live_and_dead_ends", "which end sparks reads the live power net: game-side"),
    ("floor_end_shocks_crossers", "floor-end shock (FloorEndShock/ShockRule) is not a named kernel; the job test is game-side"),
    ("no_stall_on_rewire", "a frame-time bar: live only"),
    ("shock_reach_setting", "ShockRule is not a named kernel; the restart-free switch is live"),
    ("live_wire_lights_fuel", "fuel ignition: game-side"),
    ("statics_clear_between_games", "static reset between games: game-side"),
    ("owner_change_coils_wires", "the coil on a faction change is game-side (the link rule is in canlink_truth_table)"),
    ("walk_scavenger_base", "the walk: live with the owner's list"),
    ("cords_draw_under_things", "draw order: rendering"),
    ("wire_down_alert", "an Alert: game-side"),
    ("uninstall_clean", "removal of the mod: live"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=None, help="AerialMath.cs to test (default the mod's)")
    ap.add_argument("--mod", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    kernel = a.kernel or os.path.join(a.mod, "Source/Aerial/AerialMath.cs")
    stage = os.environ.get("LANE1_STAGE") or "/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c4_lane1"
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")): os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    shutil.copy(kernel, os.path.join(stage, "AerialMath.cs"))
    shutil.copy(os.path.join(a.mod, "Source/Core/ConduitPlacementGate.cs"), os.path.join(stage, "ConduitPlacementGate.cs"))
    # AerialMath reads two constants of Core/WallMount.cs, which pulls the shared cord geometry in; hand the two shipped values
    # over in a stub instead (read from the shipped file, so a change there still reaches the kernel)
    wm = open(os.path.join(a.mod, "Source/Core/WallMount.cs"), encoding="utf-8").read()
    sb = re.search(r"const double SouthBand = ([\d.]+);", wm).group(1); sv = re.search(r"const double SideBevel = ([\d.]+);", wm).group(1)
    open(os.path.join(stage, "WallMountStub.cs"), "w").write(
        "namespace RimMandrake.GimmeSomeSlack.Core { public static class WallMount { public const double SouthBand = %s, SideBevel = %s; } }\n" % (sb, sv))
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    exe = win + "\\bin\\Release\\net8.0\\BlindLane1.dll"
    if b.returncode:
        row("kernel_build", ["spans_above_everything"], "fixed", "FAIL", 1, "BlindLane1 + kernel did not compile: " + (b.stdout[-600:] + b.stderr[-300:]).replace("\n", " "))
        built = False
    else:
        built = True
        r = subprocess.run([dn, exe], capture_output=True, text=True, timeout=400)
        got = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        rows.extend(got)
        if r.returncode not in (0, 1) or not got:
            row("kernel_run", ["spans_above_everything"], "fixed", "FAIL", 1, "kernel run rc %s: %s" % (r.returncode, r.stderr[-400:]))

    def dll_run(path):
        if not built: return None
        tmp = os.path.join(stage, "scan_" + os.path.basename(path))
        shutil.copy(path, tmp)
        r = subprocess.run([dn, exe, "--types", subprocess.run(["wslpath", "-w", tmp], capture_output=True, text=True).stdout.strip()],
                           capture_output=True, text=True, timeout=120)
        return r.stdout.split() if r.returncode == 0 else None

    no_hose_rows(a.mod, dn, dll_run)
    settings_rows(a.mod)
    for bar, why in NOT_KERNEL:
        row("not_kernel_" + bar, [bar], "not_kernel", "UNSETTLED", 0, why + "; owed to Stage 6")

    with open(a.out, "w") as f:
        for r_ in rows: f.write(json.dumps(r_) + "\n")
    c = {}
    for r_ in rows: c[r_["verdict"]] = c.get(r_["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for r_ in rows:
        if r_["verdict"] == "FAIL": print("FAIL", r_["id"], r_["detail"][:400])
    sys.exit(1 if any(r_["verdict"] == "FAIL" for r_ in rows) else 0)


main()
