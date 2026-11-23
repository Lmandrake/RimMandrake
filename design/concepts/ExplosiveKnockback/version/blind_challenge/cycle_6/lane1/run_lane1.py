#!/usr/bin/env python3
"""ExplosiveKnockback blind lane 1, cycle 6 (run judge-1795437145).
    python3 run_lane1.py [--kernel <path>]... [--src <ExplosiveKnockback dir>] [--out <rows.jsonl>]
A --kernel file replaces the shipped kernel of the same basename (RM_KnockbackMath.cs, RM_KnockbackPlan.cs, RM_KnockbackMod.cs,
proof_build_gate.py). Stages BlindLane1.cs and the two C# kernels under <agent storage>/rimmandrake/scratch/explosiveknockback_blind_c6_lane1
(dotnet.exe cannot build from a WSL path; LANE1_STAGE overrides it), builds with the per-user Windows dotnet, then adds the Python rows
(settings as shipped, the proof build gate, the proof scene list). Writes one JSON row per line and prints the verdict counts.
Exit 0 = no FAIL row; 1 = a FAIL row; 2 = build or run failure (no rows written)."""
import argparse, glob, importlib.util, io, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback")
KERNELS = ["Source/RM_KnockbackMath.cs", "Source/RM_KnockbackPlan.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings>
<AssemblyName>BlindLane1</AssemblyName></PropertyGroup></Project>"""


def row(rid, bars, kind, verdict, cases, detail):
    return {"id": rid, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail}


def py_rows(src, swap):
    rows = []
    mod_path = swap.get("RM_KnockbackMod.cs", os.path.join(src, "Source/RM_KnockbackMod.cs"))
    t = open(mod_path).read()
    # settings as shipped: initialiser == Scribe default == Reset() value, default inside its slider range, removed caps gone
    init = {m.group(2): m.group(3) for m in re.finditer(r"public static (bool|float|int) (\w+) = ([^;]+);", t)}
    scribe = {m.group(1): m.group(2) for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "\w+", ([^)]+)\);', t)}
    reset = {m.group(1): m.group(2) for m in re.finditer(r"RimMandrakeExplosiveKnockbackSettings\.(\w+) = ([^;]+);", t)}
    slider = {m.group(1): (m.group(3), m.group(4)) for m in re.finditer(r"(\w+) = (?:\(int\))?(?:Mathf\.Round\()?(?:Mathf\.Max\(\w+, Mathf\.Round\()?list\.Slider\((\w+), ([\d.]+)f, ([\d.]+)f\)", t)}

    def val(s):
        s = s.strip().rstrip("f")
        return {"true": 1.0, "false": 0.0}.get(s, None) if s in ("true", "false") else float(s)
    bad = []
    for name, v in init.items():
        if name == "debugDrawVectors":
            pass
        if name in scribe and val(scribe[name]) != val(v):
            bad.append("%s init %s scribe %s" % (name, v, scribe[name]))
        if name not in reset:
            bad.append("%s missing from Reset()" % name)
        elif val(reset[name]) != val(v):
            bad.append("%s init %s reset %s" % (name, v, reset[name]))
        if name not in scribe:
            bad.append("%s not saved" % name)
        if name in slider:
            lo, hi = float(slider[name][0]), float(slider[name][1])
            if not (lo <= val(v) <= hi):
                bad.append("%s default %s outside slider %s..%s" % (name, v, lo, hi))
    removed = [k for k in ("maxThrowsPerExplosion", "maxItemThrowsPerMapTick", "immuneBodySize") if re.search(r"\b%s\b" % k, t)]
    if removed:
        bad.append("removed settings still present: %s" % ", ".join(removed))
    rows.append(row("L1_SETTINGS_SHIPPED_DEFAULTS_COHERENT", ["settings_scale_and_switch", "inv_settings", "inv_proof_scenes"], "fixed",
                    "FAIL" if bad else "PASS", len(init),
                    ("; ".join(bad)) if bad else "%d settings: initialiser = saved default = Reset(); %d sliders hold their default; the removed cap and body-size settings are gone" % (len(init), len(slider))))
    # the proof build gate
    gate_path = swap.get("proof_build_gate.py", os.path.join(src, "proof_build_gate.py"))
    spec = importlib.util.spec_from_file_location("blind_gate", gate_path)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    bad = []
    rel = {"error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}
    other = {"error": "Type not found: RimMandrake.FlowWorks.RM_FlowProof"}
    good = {"result": "calibration,wall_stop flowworks=True"}
    buf = io.StringIO()
    try:
        g.require_proof_build(rel, out=buf)
        bad.append("release answer passed")
    except SystemExit as e:
        if e.code != 3:
            bad.append("release exit %r" % e.code)
        if "PROOF BUILD REQUIRED" not in buf.getvalue():
            bad.append("no PROOF BUILD REQUIRED line")
    for resp, name in ((good, "proof answer"), (other, "another type's miss")):
        try:
            if g.require_proof_build(resp, out=io.StringIO()) is not resp:
                bad.append(name + " not returned unchanged")
        except SystemExit:
            bad.append(name + " refused")
    rows.append(row("L1_PROOF_GATE_REFUSES_RELEASE_DLL", ["inv_proof_scenes"], "fixed", "FAIL" if bad else "PASS", 3,
                    "; ".join(bad) if bad else "release DLL answer exits 3 with PROOF BUILD REQUIRED; a proof answer and another type's miss pass unchanged"))
    # the proof scenes the bar names exist as entry points, and each named scene is handled (named again past the list)
    proof = "".join(open(p).read() for p in sorted(glob.glob(os.path.join(src, "Source/RM_KnockbackProof*.cs"))))
    m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", proof, re.S)
    names = re.findall(r'"(\w+)"', m.group(1)) if m else []
    want = {"mortar 3 cells": "calibration", "wall": "wall_stop", "door": "door_stop", "sandbags": "over_sandbags", "too big": "heavy_skip",
            "EMP": "emp_no_throw", "items": "items", "shelf": "shelf", "corpse": "corpse_into_pit", "pits": "pit_colonist", "cover": "cover_breaks",
            "caps": "all_fly_no_cap", "master off": "settings_off", "config": "lookup_projectile", "guards": "spared_states"}
    missing = ["%s (%s)" % (k, v) for k, v in want.items() if v not in names]
    unhandled = [n for n in names if proof.count('"%s"' % n) < 2 and not re.search(r'"%s[_"]|%s\b' % (n, n), proof.replace(m.group(0), "") if m else proof)]
    rows.append(row("L1_PROOF_SCENES_NAMED_BY_THE_BAR_EXIST", ["inv_proof_scenes"], "fixed", "FAIL" if missing else "PASS", len(want),
                    ("missing: " + ", ".join(missing)) if missing else "%d scene names; every scene the bar lists has an entry point; %d named once only (INFO, source text): %s" % (len(names), len(unhandled), ", ".join(unhandled[:12]))))
    rows.append(row("L1_NOT_KERNEL_GAME_SIDE", ["pawn_flight_arc", "hose_drops_at_takeoff", "pit_goods_fetched", "no_careless_fall", "our_gases_burn",
                                               "walk_storeroom_raid", "only_explosions_throw", "blast_breaks_pit_cover", "inv_hook", "inv_pawn_flyer",
                                               "inv_items_teleport", "inv_pit_floor_haul", "inv_hose_drop", "inv_gas_tags", "inv_killed_corpse"],
                    "not_kernel", "UNSETTLED", 0,
                    "game-side logic (flyers, Harmony hooks, pit hauling, pathing, gas census, the raid walk, cover breaking by blast radius): no kernel decides these; settled at Stage 6 by their live scenes"))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    swap = {os.path.basename(k): os.path.abspath(k) for k in a.kernel}
    stage = os.environ.get("LANE1_STAGE")
    if not stage:
        root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
        stage = os.path.join(root, "rimmandrake", "scratch", "explosiveknockback_blind_c6_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    for k in KERNELS:
        b = os.path.basename(k)
        shutil.copy(swap.get(b, os.path.join(a.src, k)), os.path.join(stage, b))
    unknown = set(swap) - {os.path.basename(k) for k in KERNELS} - {"RM_KnockbackMod.cs", "proof_build_gate.py"}
    if unknown:
        sys.exit("unknown kernel(s): %s" % ", ".join(sorted(unknown)))
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        print("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
        sys.exit(2)
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not rows:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
        sys.exit(2)
    try:
        rows += py_rows(a.src, swap)
    except Exception as e:  # a planted fault that breaks the Python half is a failing row, not a crash
        rows.append(row("L1_PY_HALF_RAN", ["inv_proof_scenes", "inv_settings"], "fixed", "FAIL", 0, "python half raised %s: %s" % (type(e).__name__, e)))
    with open(a.out, "w") as f:
        for rr in rows:
            f.write(json.dumps(rr) + "\n")
    c = {}
    for rr in rows:
        c[rr["verdict"]] = c.get(rr["verdict"], 0) + 1
    print("LANE1", json.dumps(c, sort_keys=True), "rows", len(rows), "->", a.out)
    for rr in rows:
        if rr["verdict"] in ("FAIL", "UNSETTLED"):
            print(rr["verdict"], rr["id"], rr["detail"][:500])
    sys.exit(1 if any(rr["verdict"] == "FAIL" for rr in rows) else 0)


main()
