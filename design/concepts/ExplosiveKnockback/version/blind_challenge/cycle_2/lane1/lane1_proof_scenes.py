#!/usr/bin/env python3
"""Blind lane 1 rows for the offline bar inv_proof_scenes (ExplosiveKnockback 0.2.0, cycle 2), written from the bar:
"Live scenes RM_KnockbackProof (mortar 3 cells, wall, door, sandbags, too big, EMP, items, shelf, corpse, pits, cover,
caps, master off, config, guards) and the runner that drives them". Reads RM_KnockbackProof*.cs, RM_KnockbackMod.cs,
proof_build_gate.py, knockback_runner.py and the committed release DLL (through a metadata reader, never strings).
    python3 lane1_proof_scenes.py [--src <ExplosiveKnockback dir>]
Prints one JSON row per line. Exit 0 = no FAIL; 1 = a FAIL."""
import argparse, glob, importlib.util, io, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback")
STAGE = os.environ.get("KB_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c2_lane1") + "_meta"
BARS = ["inv_proof_scenes"]
rows = []


def row(id_, kind, verdict, cases, detail, bars=BARS):
    rows.append({"id": id_, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail})


def proof_sources(mod):
    return sorted(glob.glob(os.path.join(mod, "Source", "RM_KnockbackProof*.cs")))


# ── the bar's named scenes: each family has at least one scene in SceneNames, and every scene name is built ──
FAMILIES = {  # the bar's word -> scene names any one of which is that scene
    "mortar 3 cells": ["calibration"], "wall": ["wall_stop"], "door": ["door_stop"], "sandbags": ["over_sandbags"],
    "too big": ["heavy_skip"], "EMP": ["emp_no_throw"], "items": ["items"], "shelf": ["shelf"],
    "corpse": ["corpse_into_pit", "killed_by_blast"], "pits": ["pit_colonist", "pit_enemy", "no_cross"], "cover": ["cover_breaks"],
    "caps": ["all_fly_no_cap"], "master off": ["settings_off"], "config": ["lookup_projectile", "lookup_zero_wins", "impact_factor", "body_override"],
    "guards": ["immunity_window", "shield_counter", "in_pit_skip"],
}


def scene_names(text):
    m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", text, re.S)
    body = re.sub(r"//[^\n]*", "", m.group(1)) if m else ""
    return re.findall(r'"([a-z0-9_]+)"', body)


def check_names(mod):
    main = open(os.path.join(mod, "Source", "RM_KnockbackProof.cs"), encoding="utf-8").read()
    names = scene_names(main)
    allsrc = "\n".join(open(p, encoding="utf-8").read() for p in proof_sources(mod))
    labels = set(re.findall(r'case\s+"([a-z0-9_]+)"\s*:', allsrc))
    missing_fam = [f for f, alts in FAMILIES.items() if not any(a in names for a in alts)]
    unbuilt = [n for n in names if n not in labels]
    dup = sorted({n for n in names if names.count(n) > 1})
    ok = names and not missing_fam and not unbuilt and not dup
    row("L1_PROOF_SCENES_NAMED_AND_BUILT", "fixed", "PASS" if ok else "FAIL", len(names) + len(FAMILIES),
        "SceneNames %d; bar families missing: %s; names with no case label in any proof source: %s; duplicates: %s"
        % (len(names), missing_fam or "none", unbuilt or "none", dup or "none"))
    return names


# ── restore chains: a scene that changes a def, a setting or the map must leave it as it found it. A restore assignment
#    that does not chain the previous restore drops it; that is a leak when anything before it in the same scene set one. ──
FUNC_RX = re.compile(r"^\s*(?:private|public|internal)\s+static\s+[\w<>\[\],. ]+?\s+(\w+)\s*\(")


def split_units(text):
    """(name, start line, lines) per static function; Build is split further at each case label."""
    lines = text.split("\n")
    units, cur, start = [], None, 0
    for i, l in enumerate(lines):
        m = FUNC_RX.match(l)
        if m:
            if cur:
                units.append((cur, start, lines[start:i]))
            cur, start = m.group(1), i
    if cur:
        units.append((cur, start, lines[start:]))
    out = []
    for name, st, ls in units:
        if name != "Build":
            out.append((name, st, ls))
            continue
        cs, cst = "Build:<head>", st
        buf = []
        for j, l in enumerate(ls):
            m = re.match(r'\s*case\s+"([a-z0-9_]+)"\s*:', l)
            if m and buf and not re.match(r'\s*case\s+"', ls[j - 1]):
                out.append((cs, cst, buf))
                buf, cst = [], st + j
                cs = "Build:" + m.group(1)
            elif m:
                cs = cs if cs != "Build:<head>" else "Build:" + m.group(1)
            buf.append(l)
        out.append((cs, cst, buf))
    return out


def restore_leaks(texts, extra_setters=()):
    """texts: {file: text}. Returns (leaks, n_sites, setters)."""
    units = []
    for f, t in texts.items():
        for name, st, ls in split_units(t):
            units.append((f, name, st, ls))
    setters = {n.split(":")[0] for f, n, st, ls in units if not n.startswith("Build") and any(re.search(r"\b\w+\.restore\s*=", l) for l in ls)}
    setters |= {"FlightRestore"} | set(extra_setters)
    setters.discard("RunRestore")
    leaks, n = [], 0
    for f, name, st, ls in units:
        if name == "RunRestore":
            continue
        for j, l in enumerate(ls):
            if not re.search(r"\bs\.restore\s*=", l):
                continue
            n += 1
            stmt = " ".join(x.strip() for x in ls[j:j + 12])
            stmt = stmt[:stmt.find("};") + 2] if "};" in stmt else stmt
            chains = re.search(r"\bprev\w*\s*\?\.\s*Invoke|FlightRestore\(s\)|prev\w*\(\)", stmt) is not None
            if chains:
                continue
            before = "\n".join(ls[1:j])   # the function's own header line is not a call
            prior = [m.group(1) for m in re.finditer(r"\b(%s)\s*\(" % "|".join(sorted(setters)), before)]
            prior_assign = re.search(r"\bs\.restore\s*=", before)
            if prior or prior_assign:
                leaks.append("%s:%d [%s] overwrites the restore set before by %s" % (os.path.basename(f), st + j + 1, name,
                             ", ".join(sorted(set(prior))) or "an earlier s.restore"))
    return leaks, n, setters


def settings_writes_unrestored(texts):
    """A direct write to a Mod Setting in a scene, with no restore before it in that scene that names that field (or a
    whole-settings snapshot), leaves the player's value changed."""
    out, n = [], 0
    for f, t in texts.items():
        for name, st, ls in split_units(t):
            if name in ("FlightRestore", "RunRestore"):
                continue
            for j, l in enumerate(ls):
                m = re.search(r"RimMandrakeExplosiveKnockbackSettings\.(\w+)\s*=(?!=)", l)
                if not m or re.search(r"=>|restore|was\b|\bfg\b|\bsp\b|\brb\b", l):
                    continue
                n += 1
                field = m.group(1)
                before = "\n".join(ls[:j])
                flight = field in ("flyingGoods", "goodsFlightSpeed", "goodsRebound") and "FlightRestore(s)" in before
                snap = "SetValue(null, saved[i])" in before or "fields[i].SetValue" in before
                named = re.search(r"restore\s*=.*%s" % field, before, re.S) is not None
                if not (flight or snap or named):
                    out.append("%s:%d [%s] writes %s with no restore before it" % (os.path.basename(f), st + j + 1, name, field))
    return out, n


def check_restores(mod):
    texts = {p: open(p, encoding="utf-8").read() for p in proof_sources(mod)}
    leaks, n, setters = restore_leaks(texts)
    unrest, m = settings_writes_unrestored(texts)
    # the instrument can see: a planted overwrite after AddExt, and a planted unrestored write, must both be flagged
    plant = {"plant.cs": "    private static string Build(Scene s)\n    {\n        switch (s.name)\n        {\n            case \"x\":\n"
             "                AddExt(s, d, e);\n                s.restore = () => Foo();\n"
             "                RimMandrakeExplosiveKnockbackSettings.strength = 2f;\n                return null;\n        }\n    }\n"}
    pl, _, _ = restore_leaks(plant, setters)
    pu, _ = settings_writes_unrestored(plant)
    seen = bool(pl) and bool(pu)
    ok = not leaks and not unrest and seen
    row("L1_PROOF_SCENES_RESTORE_CHAINS", "fixed", "PASS" if ok else ("FAIL" if seen else "UNSETTLED"), n + m + 2,
        "%d restore assignments, %d direct settings writes; restore setters %s; leaks: %s; unrestored writes: %s; planted overwrite and "
        "planted write flagged: %s" % (n, m, sorted(setters), leaks or "none", unrest or "none", seen))


# ── the gate: a release DLL's 'Type not found' answer exits 3 with PROOF BUILD REQUIRED, anything else passes through ──
def check_gate(mod):
    spec = importlib.util.spec_from_file_location("pbg_lane1", os.path.join(mod, "proof_build_gate.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    cases, bad = 0, []
    release = [{"error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"},
               "ERROR Type not found RimMandrake.ExplosiveKnockback.RM_KnockbackProof"]
    passing = ["calibration,wall_stop flowworks=True hoses=True", {"result": "calibration,wall_stop"}, None, "",
               {"error": "Type not found: RimMandrake.FlowWorks.Something"}]
    for r in release:
        cases += 1
        buf = io.StringIO()
        try:
            g.require_proof_build(r, out=buf)
            bad.append("release answer %r passed" % (r,))
        except SystemExit as e:
            if e.code != 3 or "PROOF BUILD REQUIRED" not in buf.getvalue():
                bad.append("release answer %r exit %r msg %r" % (r, e.code, buf.getvalue()[:60]))
    for r in passing:
        cases += 1
        try:
            if g.require_proof_build(r, out=io.StringIO()) is not r:
                bad.append("answer %r not returned unchanged" % (r,))
        except SystemExit as e:
            bad.append("proof answer %r exited %r" % (r, e.code))
    row("L1_PROOF_GATE_RELEASE_EXITS_3", "fixed", "PASS" if not bad else "FAIL", cases,
        "; ".join(bad) or "a release 'Type not found ... RM_KnockbackProof' answer exits 3 with PROOF BUILD REQUIRED; proof answers, "
                         "empty answers and another type's error pass through unchanged")


# ── the runner: the gate on its first proof call, before any Stage; the player's settings restored in a finally ──
def check_runner(mod):
    t = open(os.path.join(mod, "knockback_runner.py"), encoding="utf-8").read()
    i_gate = t.find("require_proof_build(")
    i_names = t.find('call(b, "Names"')
    i_stage = t.find('call(b, "Stage"')
    i_finally = t.find("finally:")
    i_restore = t.find("restore_settings(b, snap)", i_finally)
    i_snap = t.find("snap = snapshot_settings(b)")
    ok = 0 <= i_names < i_gate < i_stage and 0 <= i_snap < i_stage < i_finally < i_restore
    row("L1_RUNNER_GATES_AND_RESTORES", "fixed", "PASS" if ok else "FAIL", 2,
        "Names %d < gate %d < first Stage %d; snapshot %d < Stage < finally %d < restore %d" % (i_names, i_gate, i_stage, i_snap, i_finally, i_restore))


# ── the release DLL: every proof file is wholly under RM_PROOFS, the csproj defines it only on RmProofs=true, and the
#    committed (release) DLL carries no proof type (a metadata reader lists its types) ──
META_CS = r"""using System; using System.IO; using System.Linq; using System.Reflection.Metadata; using System.Reflection.PortableExecutable;
class M { static void Main(string[] a) { using var fs = File.OpenRead(a[0]); using var pe = new PEReader(fs); var md = pe.GetMetadataReader();
foreach (var h in md.TypeDefinitions) { var t = md.GetTypeDefinition(h); Console.WriteLine("T " + md.GetString(t.Namespace) + "." + md.GetString(t.Name));
foreach (var mh in t.GetMethods()) Console.WriteLine("M " + md.GetString(t.Name) + "::" + md.GetString(md.GetMethodDefinition(mh).Name)); } } }"""
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""


def list_types(dll):
    os.makedirs(STAGE, exist_ok=True)
    open(os.path.join(STAGE, "Meta.cs"), "w").write(META_CS)
    open(os.path.join(STAGE, "Meta.csproj"), "w").write(CSPROJ)
    shutil.copy(dll, os.path.join(STAGE, "target.dll"))
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\Meta.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        return None, "metadata reader build failed: " + (b.stdout + b.stderr)[-300:]
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\Meta.dll", win + "\\target.dll"], capture_output=True, text=True, timeout=400)
    if r.returncode:
        return None, "metadata reader failed: " + r.stderr[-300:]
    return r.stdout.splitlines(), None


def check_release(mod):
    unguarded = []
    for p in proof_sources(mod) + [os.path.join(mod, "Source", "RM_PatchApplierProbe.cs")]:
        ls = [l for l in open(p, encoding="utf-8").read().split("\n") if l.strip()]
        if not (ls[0].strip() == "#if RM_PROOFS" and ls[-1].strip() == "#endif"):
            unguarded.append(os.path.basename(p))
    proj = open(os.path.join(mod, "Source", "RimMandrake_ExplosiveKnockback.csproj"), encoding="utf-8").read()
    proj_ok = re.search(r"<PropertyGroup Condition=\"'\$\(RmProofs\)' == 'true'\">\s*<DefineConstants>\$\(DefineConstants\);RM_PROOFS</DefineConstants>", proj) is not None \
        and len(re.findall(r"RM_PROOFS</DefineConstants>", proj)) == 1 and "<RmProofs Condition=\"'$(RmProofs)' == ''\">false</RmProofs>" in proj
    lines, err = list_types(os.path.join(mod, "Assemblies", "RimMandrakeExplosiveKnockback.dll"))
    if lines is None:
        row("L1_RELEASE_DLL_HAS_NO_PROOF_TYPE", "fixed", "UNSETTLED", 0, err + "; settle by running the metadata reader")
        return
    types = [l[2:] for l in lines if l.startswith("T ")]
    meths = [l[2:] for l in lines if l.startswith("M ")]
    proof_types = [t for t in types if re.search(r"RM_KnockbackProof|RM_PatchApplierProbe", t)]
    proof_meths = [m for m in meths if re.search(r"::(ProofSchedule|ForgetClosed|FillToSurface)$", m)]
    sane = any(t.endswith(".RM_KnockbackMath") for t in types) and len(types) > 10
    ok = not unguarded and proj_ok and not proof_types and not proof_meths and sane
    row("L1_RELEASE_DLL_HAS_NO_PROOF_TYPE", "fixed", "PASS" if ok else ("FAIL" if sane else "UNSETTLED"), len(types),
        "proof files not wholly under #if RM_PROOFS: %s; csproj defines RM_PROOFS only on RmProofs=true (default false): %s; committed DLL: "
        "%d types (reader sees RM_KnockbackMath: %s), proof types %s, proof methods %s" % (unguarded or "none", proj_ok, len(types), sane,
                                                                                         proof_types or "none", proof_meths or "none"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=MOD)
    a = ap.parse_args()
    check_names(a.src)
    check_restores(a.src)
    check_gate(a.src)
    check_runner(a.src)
    check_release(a.src)
    for r in rows:
        print(json.dumps(r))
    return 1 if any(r["verdict"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
