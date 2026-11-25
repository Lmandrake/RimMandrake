#!/usr/bin/env python3
"""Run blind lane 1 (ExplosiveKnockback 0.2.0, cycle 1) against the shipped kernel, or a substitute kernel file.

    python3 run_lane1.py [--kernel <path to an RM_KnockbackMath.cs>] [--src <ExplosiveKnockback dir>] [--out <rows.jsonl>]
                         [--no-proof-build]

The C# rows (BlindLane1.cs) compile against the kernel RM_KnockbackMath.cs; the shipped settings defaults go to the test
in EK_* variables read from RM_KnockbackMod.cs by regex (never hand-copied; WSLENV carries them to dotnet.exe). The
Python rows test proof_build_gate.py by behaviour, the settings file's three default lists (initializer, Scribe, Reset)
against each other, the proof scenes' dispatch, and the proof build itself (winbuild with -p:RmProofs=true under a private
WINBUILD_ROOT; the clone's Assemblies/ are restored after). One not_kernel row per game-side bar.
Stage: /mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c1_lane1/ (dotnet.exe cannot build from a WSL path).
Exit 0 = no FAIL row; 1 = a FAIL row; 2 = build or run failure (no rows written)."""
import argparse, glob, importlib.util, io, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback")
CONCEPT = os.path.join(REPO, "design/concepts/ExplosiveKnockback")
STAGE = "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c1_lane1"
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0162;CS0168;CS0219</NoWarn></PropertyGroup></Project>"""
FIELD_RX = re.compile(r"public static (bool|float|int) (\w+) = ([^;]+);")


def settings_fields(src):
    text = open(os.path.join(src, "Source/RM_KnockbackMod.cs"), encoding="utf-8").read()
    cls = text[text.index("class RimMandrakeExplosiveKnockbackSettings"):]
    cls = cls[:cls.index("public static KbSettings Kernel(")]
    return {n: (t, v.strip()) for t, n, v in FIELD_RX.findall(cls)}, text


def norm(t, v):
    v = v.strip()
    if t == "bool":
        return v
    return float(v.rstrip("f")) if re.fullmatch(r"-?[\d.]+f?", v) else v


def row(rows, id_, bars, kind, verdict, cases, detail):
    rows.append({"id": id_, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail})


def py_rows(src, rows, proof_build):
    fields, text = settings_fields(src)
    # ── settings: initializer == Scribe default == Reset value, every field in all three ──
    scribe = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "\w+", ([^)]+)\);', text))
    keys = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', text))
    reset = dict(re.findall(r"RimMandrakeExplosiveKnockbackSettings\.(\w+) = ([^;]+);", text[text.index("public static void Reset()"):]))
    bad = []
    for n, (t, v) in fields.items():
        if n not in scribe:
            bad.append(n + " not saved")
            continue
        if keys.get(n) != n:
            bad.append(n + " saved under key " + str(keys.get(n)))
        if norm(t, scribe[n]) != norm(t, v):
            bad.append("%s: initializer %s, Scribe default %s" % (n, v, scribe[n]))
        if n not in reset:
            bad.append(n + " not reset")
        elif norm(t, reset[n]) != norm(t, v):
            bad.append("%s: initializer %s, Reset %s" % (n, v, reset[n]))
    extra = sorted(set(scribe) - set(fields)) + sorted(set(reset) - set(fields))
    if extra:
        bad.append("saved or reset but no field: " + ",".join(extra))
    row(rows, "L1_FIXED_SETTINGS_DEFAULTS_AGREE", ["inv_proof_scenes", "settings_scale_and_switch"], "fixed", "FAIL" if bad else "PASS",
        len(fields), ("; ".join(bad[:12])) if bad else "%d settings: each field's initializer, Scribe default and Reset value agree, each saved under its own name (the proof's restore and a fresh install give the shipped behaviour)" % len(fields))

    # ── proof_build_gate by behaviour ──
    spec = importlib.util.spec_from_file_location("ek_gate", os.path.join(src, "proof_build_gate.py"))
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    cases, fails = 0, []

    def expect_exit(resp, what):
        nonlocal cases
        cases += 1
        buf = io.StringIO()
        try:
            gate.require_proof_build(resp, out=buf)
            fails.append(what + ": no exit")
        except SystemExit as e:
            if e.code != 3 or "PROOF BUILD REQUIRED" not in buf.getvalue() or "RmProofs=true" not in buf.getvalue():
                fails.append(what + ": exit %r, message %r" % (e.code, buf.getvalue()[:80]))

    def expect_pass(resp, what):
        nonlocal cases
        cases += 1
        buf = io.StringIO()
        try:
            out = gate.require_proof_build(resp, out=buf)
            if out is not resp or buf.getvalue():
                fails.append(what + ": changed or printed")
        except SystemExit as e:
            fails.append(what + ": exit %r" % e.code)

    expect_exit({"error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}, "release answer (dict)")
    expect_exit("Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof", "release answer (text)")
    expect_exit({"result": {"isError": True, "content": [{"text": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}]}}, "release answer (nested)")
    expect_pass({"result": "STAGED calibration at 10,10"}, "a proof build answer")
    expect_pass({"result": "FAIL calibration RM_KnockbackProof journal empty"}, "a FAIL verdict from a proof build")
    expect_pass(None, "no answer")
    expect_pass("", "an empty answer")
    row(rows, "L1_FIXED_PROOF_BUILD_GATE", ["inv_proof_scenes"], "fixed", "FAIL" if fails else "PASS", cases,
        "; ".join(fails) if fails else "the release answer (text, dict or nested) exits 3 with the build-and-deploy lines; a proof build's STAGED or FAIL answer and an empty answer pass through unchanged and print nothing")

    # ── every named proof scene has a handler; the bar's named scenes exist ──
    proof_files = sorted(glob.glob(os.path.join(src, "Source/RM_KnockbackProof*.cs")))
    ptext = "\n".join(open(p, encoding="utf-8").read() for p in proof_files)
    m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", ptext, re.S)
    names = re.findall(r'"(\w+)"', re.sub(r"//[^\n]*", "", m.group(1))) if m else []
    handled = set(re.findall(r'case "(\w+)"', ptext))
    missing = [n for n in names if n not in handled]
    dup = sorted({n for n in names if names.count(n) > 1})
    want = {"mortar 3 cells": ["calibration"], "wall": ["wall_stop"], "door": ["door_stop"], "sandbags": ["over_sandbags"],
            "too big": ["heavy_skip", "spared_states"], "EMP": ["emp_no_throw"], "items": ["items"], "shelf": ["shelf", "open_storage"],
            "corpse": ["corpse_into_pit"], "pits": ["pit_colonist", "pit_enemy"], "cover": ["cover_breaks"], "caps": ["all_fly_no_cap"],
            "master off": ["settings_off"], "config": ["lookup_projectile", "lookup_zero_wins"], "guards": ["immunity_window", "shield_counter"]}
    absent = [k for k, v in want.items() if not all(x in names and x in handled for x in v)]
    bad = (["no SceneNames list"] if not names else []) + ["no handler: " + ",".join(missing)] * bool(missing) + ["listed twice: " + ",".join(dup)] * bool(dup) + ["bar scene absent: " + ",".join(absent)] * bool(absent)
    row(rows, "L1_FIXED_PROOF_SCENES_DISPATCH", ["inv_proof_scenes"], "fixed", "FAIL" if bad else "PASS", len(names) + len(want),
        "; ".join(bad) if bad else "%d named scenes, each with a case in the proof sources, none twice; every scene the bar names (mortar, wall, door, sandbags, too big, EMP, items, shelf, corpse, pits, cover, caps, master off, config, guards) is named and handled" % len(names))

    # ── the release DLL has no proof type; the proof build compiles ──
    dlls = glob.glob(os.path.join(src, "Assemblies/*.dll"))
    rel = [d for d in dlls if "ExplosiveKnockback" in os.path.basename(d)]
    if rel:
        blob = open(rel[0], "rb").read()
        ok = b"RM_KnockbackProof" not in blob and b"RM_KnockbackMath" in blob
        row(rows, "L1_FIXED_RELEASE_DLL_HAS_NO_PROOF_TYPE", ["inv_proof_scenes"], "fixed", "PASS" if ok else "FAIL", 1,
            "%s: RM_KnockbackProof %s, RM_KnockbackMath %s in its metadata strings (the gate's premise)" % (os.path.relpath(rel[0], REPO), "absent" if b"RM_KnockbackProof" not in blob else "PRESENT", "present" if b"RM_KnockbackMath" in blob else "ABSENT"))
    else:
        row(rows, "L1_FIXED_RELEASE_DLL_HAS_NO_PROOF_TYPE", ["inv_proof_scenes"], "fixed", "FAIL", 0, "no committed ExplosiveKnockback DLL under Assemblies/")
    if proof_build:
        env = dict(os.environ, WINBUILD_ROOT="/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c1_lane1_proofbuild")
        try:
            b = subprocess.run(["python3", os.path.join(REPO, "src/RimMandrake/Utils/winbuild.py"), "ExplosiveKnockback", "--", "-p:RmProofs=true"],
                               cwd=REPO, capture_output=True, text=True, env=env, timeout=530)
            rc, out = b.returncode, (b.stdout + b.stderr)
        except subprocess.TimeoutExpired:
            rc, out = None, "timed out at 530 s (a hang guard: one build measured ~1-2 min)"
        finally:
            subprocess.run(["git", "-C", REPO, "checkout", "--", "src/RimMandrake/ExplosiveKnockback/Assemblies"], capture_output=True)
        built = re.findall(r"BUILT (\S+)", out)
        errs = re.findall(r"error CS\d+[^\n]*", out)
        staged = os.path.join(env["WINBUILD_ROOT"], "ExplosiveKnockback/src/RimMandrake/ExplosiveKnockback/Assemblies/RimMandrakeExplosiveKnockback.dll")
        has_proof = os.path.exists(staged) and b"RM_KnockbackProof" in open(staged, "rb").read()
        verdict = "PASS" if rc == 0 and built and has_proof else ("UNSETTLED" if rc is None else "FAIL")
        built = [x + (" (carries RM_KnockbackProof)" if has_proof else " (NO RM_KnockbackProof in it)") for x in built]
        row(rows, "L1_FIXED_PROOF_BUILD_COMPILES", ["inv_proof_scenes"], "fixed", verdict, 1,
            ("the proof build (-p:RmProofs=true) compiles: " + ", ".join(built)) if verdict == "PASS" else
            ("rc %s; %s; %s" % (rc, "; ".join(errs[:5]), out[-600:])))
    else:
        row(rows, "L1_FIXED_PROOF_BUILD_COMPILES", ["inv_proof_scenes"], "fixed", "UNSETTLED", 0, "skipped (--no-proof-build); settle it with run_lane1.py without the flag")


def not_kernel_rows(rows):
    ids = json.load(open(os.path.join(CONCEPT, "version/locked_bars.json")))["ids"]
    covered = {}
    for r in rows:
        for b in r["bars"]:
            covered.setdefault(b, []).append(r["id"])
    for b in ids:
        if b in ("inv_kernel", "inv_proof_scenes"):
            continue
        k = covered.get(b, [])
        row(rows, "L1_NOT_KERNEL_" + b.upper(), [b], "not_kernel", "UNSETTLED", 0,
            "game-side: what the player sees is decided by the bar's in-game scene (Stage 6 or the walk), not by RM_KnockbackMath.cs. "
            + ("Its kernel half is tested in " + ", ".join(k) + "." if k else "No kernel function carries its logic.")
            + " Settled by: that scene's run on a game, on this build.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=None)
    ap.add_argument("--src", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    ap.add_argument("--no-proof-build", action="store_true")
    a = ap.parse_args()
    os.makedirs(STAGE, exist_ok=True)
    for f in glob.glob(os.path.join(STAGE, "*.cs")):
        os.remove(f)
    shutil.copy(a.kernel or os.path.join(a.src, "Source/RM_KnockbackMath.cs"), os.path.join(STAGE, "RM_KnockbackMath.cs"))
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), STAGE)
    open(os.path.join(STAGE, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=400)  # a hang guard: a build measured well under a minute
    if b.returncode:
        print("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
        sys.exit(2)
    fields, _ = settings_fields(a.src)
    senv = {"EK_" + n: str(norm(t, v)).lower() if t == "bool" else str(norm(t, v)) for n, (t, v) in fields.items()}
    env = dict(os.environ, **senv)
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", "")] + list(senv)))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=400)  # a hang guard: a run measured a few seconds
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not rows:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
        sys.exit(2)
    py_rows(a.src, rows, not a.no_proof_build)
    not_kernel_rows(rows)
    with open(a.out, "w") as f:
        for row_ in rows:
            f.write(json.dumps(row_) + "\n")
    c = {}
    for row_ in rows:
        c[row_["verdict"]] = c.get(row_["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row_ in rows:
        if row_["verdict"] == "FAIL":
            print("FAIL", row_["id"], row_["detail"][:600])
    sys.exit(1 if c.get("FAIL") else 0)


main()
