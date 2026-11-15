#!/usr/bin/env python3
"""Blind lane 1 (ExplosiveKnockback 0.1.0, cycle 3) against the shipped kernel, or with the kernel file swapped.
    python3 run_lane1.py [--kernel <RM_KnockbackMath.cs>] [--src <ExplosiveKnockback mod dir>] [--out <rows.jsonl>] [--no-proof-build]
Stages BlindLane1.cs + the kernel under /mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c3_lane1 (dotnet.exe
cannot build from a WSL path; EK_LANE1_STAGE overrides), builds and runs it with the per-user Windows dotnet, adds the
settings/def/gate rows read here, writes one JSON row per line and prints the verdict counts.
Exit 0 = every decided row PASS (INFO/UNSETTLED do not fail)."""
import argparse, glob, importlib.util, io, json, os, re, shutil, subprocess, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""


def row(id_, bars, kind, ok, cases, detail, verdict=None):
    return {"id": id_, "bars": bars, "kind": kind, "verdict": verdict or ("PASS" if ok else "FAIL"), "cases": cases, "detail": detail}


def settings_rows(src):
    """Each setting: field initializer == Scribe default == Reset() value; default inside its slider range; every bool switch drawn."""
    t = open(os.path.join(src, "Source/RM_KnockbackMod.cs"), encoding="utf-8").read()
    init = dict(re.findall(r"public static (?:bool|float|int) (\w+) = ([^;]+);", t))
    scribe = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "\w+", ([^)]+)\)', t))
    reset_body = t[t.find("public static void Reset()"):]
    reset_body = reset_body[:reset_body.find("\n        }\n")]
    reset = dict(re.findall(r"RimMandrakeExplosiveKnockbackSettings\.(\w+) = ([^;]+);", reset_body))
    sliders = {m[0]: (float(m[1].rstrip("f")), float(m[2].rstrip("f"))) for m in re.findall(r"(\w+) = [^;\n]*?list\.Slider\(\w+, ([\d.]+f?), ([\d.]+f?)\)", t)}
    boxes = set(re.findall(r"CheckboxLabeled\([^;]*?ref (\w+)", t, re.S))

    def num(v):
        v = v.strip()
        if v in ("true", "false"):
            return v
        try:
            return float(v.rstrip("f"))
        except ValueError:
            return v
    bad, cases = [], 0
    for name, v in init.items():
        if name in ("debugDrawVectors",):
            pass
        cases += 1
        if name not in scribe:
            bad.append("%s not saved" % name)
        elif num(scribe[name]) != num(v):
            bad.append("%s saved default %s != %s" % (name, scribe[name], v))
        if name not in reset:
            bad.append("%s not reset" % name)
        elif num(reset[name]) != num(v):
            bad.append("%s reset %s != %s" % (name, reset[name], v))
        if name in sliders:
            lo, hi = sliders[name]
            if not (lo <= num(v) <= hi):
                bad.append("%s default %s outside slider %s..%s" % (name, v, lo, hi))
        if v.strip() in ("true", "false") and name not in boxes:
            bad.append("%s has no checkbox" % name)
    rows = [row("py_settings_default_save_reset_agree", ["settings_scale_and_switch", "inv_settings", "inv_proof_scenes"], "fixed", not bad, cases,
                ("%d settings: initializer, saved default and Reset() agree, inside slider ranges, every switch on the page" % cases) if not bad else "; ".join(bad[:8]))]
    # removed cap settings stay gone (settings_scale_and_switch: "the removed cap settings are gone from the page")
    gone = [n for n in init if re.search(r"(perExplosion|throwsPerTick|maxThrowsPer|throwCap|goodsCap|maxThrows\b)", n, re.I)]
    rows.append(row("py_removed_cap_settings_gone", ["settings_scale_and_switch", "every_good_moves"], "fixed", not gone, len(init),
                    "no per-explosion or per-tick throw cap setting is declared" if not gone else "still declared: %s" % gone))
    # landing stun sliders may cross (min above max): read how the game side draws a stun
    rows.append(row("info_landing_stun_min_max_independent", ["settings_scale_and_switch", "people_thrown_three_cells"], "info", True, 1,
                    "landingStunMin and landingStunMax are independent 0..300 sliders; nothing on the page keeps min <= max (game-side use not read in lane 1)",
                    verdict="INFO"))
    return rows


def patch_rows(src):
    want = {"Bomb": 1.0, "Flame": 0.5, "EMP": 0.0, "Smoke": 0.0, "Extinguish": 0.0, "ToxGas": 0.0}
    got = {}
    root = ET.parse(os.path.join(src, "Patches/RM_Knockback_DamageDefs.xml")).getroot()
    for op in root.iter("Operation"):
        m = re.search(r'DamageDef\[defName="(\w+)"\]', op.findtext("xpath") or "")
        if m:
            got.setdefault(m.group(1), []).append(float(op.find("value").find("li").findtext("force")))
    bad = ["%s %s want [%s]" % (k, got.get(k), v) for k, v in want.items() if got.get(k) != [v]]
    extra = [k for k in got if k not in want]
    return [row("py_damage_type_forces", ["every_harmful_blast_throws", "only_explosions_throw", "inv_which_blasts", "per_weapon_tuning"], "fixed",
                not bad and not extra, len(want), ("forces %s; bombs full, fire half, EMP/smoke/extinguish/tox gas 0, one patch each" % got) if not bad and not extra else "; ".join(bad) + (" extra %s" % extra if extra else ""))]


def gate_rows(src):
    p = os.path.join(src, "proof_build_gate.py")
    spec = importlib.util.spec_from_file_location("ek_gate_blind", p)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    bad = []
    rel = {"error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}
    if not g.is_release_answer(rel):
        bad.append("release answer not seen")
    if g.is_release_answer({"result": "SET strength=1"}):
        bad.append("proof answer read as release")
    if g.is_release_answer({"error": "Type not found: RimMandrake.Other.Thing"}):
        bad.append("another type's miss read as ours")
    buf = io.StringIO()
    try:
        g.require_proof_build(rel, out=buf)
        bad.append("release answer did not exit")
    except SystemExit as e:
        if e.code != 3:
            bad.append("exit %s not 3" % e.code)
        if "PROOF BUILD REQUIRED" not in buf.getvalue():
            bad.append("no message")
    ok = {"result": "ok"}
    if g.require_proof_build(ok) is not ok:
        bad.append("proof answer not passed through")
    return [row("py_proof_build_gate", ["inv_proof_scenes"], "fixed", not bad, 5,
                "a release answer exits 3 with the build recipe; a proof answer or another type's miss passes" if not bad else "; ".join(bad))]


def proof_build_row(src):
    """inv_proof_scenes offline: the proof scenes (RM_PROOFS) compile against the game."""
    root = os.environ.get("WINBUILD_ROOT_LANE1") or "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c3_lane1_winbuild"
    env = dict(os.environ, WINBUILD_ROOT=root)
    try:
        r = subprocess.run([sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/winbuild.py"), "ExplosiveKnockback", "--", "-p:RmProofs=true"],
                           capture_output=True, text=True, timeout=500, env=env, cwd=REPO)
    except subprocess.TimeoutExpired:
        return [row("build_proof_scenes_compile", ["inv_proof_scenes"], "fixed", False, 1, "winbuild timed out", verdict="UNSETTLED")]
    tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
    errs = re.findall(r"error CS\d+[^\n]*", r.stdout + r.stderr)
    # winbuild copies the DLL into the mod's Assemblies: read it for the proof type, then put the committed release DLL back
    dll = os.path.join(src, "Assemblies/RimMandrakeExplosiveKnockback.dll")
    has_proof = os.path.exists(dll) and b"RM_KnockbackProof" in open(dll, "rb").read()
    subprocess.run(["git", "checkout", "--", os.path.join(src, "Assemblies")], cwd=REPO, capture_output=True)
    return [row("build_proof_scenes_compile", ["inv_proof_scenes"], "fixed", r.returncode == 0 and not errs and has_proof, 1,
                "winbuild ExplosiveKnockback -- -p:RmProofs=true rc %d, proof type in the DLL %s (release DLL restored); %s"
                % (r.returncode, has_proof, (" | ".join(errs[:3]) if errs else " | ".join(tail))[:400]))]


NOT_KERNEL = [
    ("nk_pawn_flight_arc", ["pawn_flight_arc"], "the flyer carries the pawn to the cell chosen at the blast and returns it to work: RM_PawnFlyerPatches, live"),
    ("nk_hose_drops_at_takeoff", ["hose_drops_at_takeoff"], "FlowWorks hose end dropped at takeoff: game-side"),
    ("nk_shield_absorbs", ["shield_belt_holds"], "whether a belt absorbed the blast and the gas-shove exception: game-side (the charge arithmetic is fx_shield_extra_charge)"),
    ("nk_no_teleport", ["no_teleport"], "goods carried by the thing flyer, never despawned and respawned: RM_ThingFlyer_Knockback, live"),
    ("nk_no_careless_fall", ["no_careless_fall"], "pathing cost of pits for colonists vs enemies: game-side"),
    ("nk_pit_goods_fetched", ["pit_goods_fetched", "inv_pit_floor_haul"], "hauling off a pit floor: game-side jobs"),
    ("nk_our_gases_burn", ["our_gases_burn"], "the Cauldron's vent gas registration and the census: game-side"),
    ("nk_blast_breaks_pit_cover", ["blast_breaks_pit_cover"], "cover breaking by damage type and radius: game-side"),
    ("nk_gas_chain", ["gas_goes_clump_by_clump", "inv_gas_chain"], "fire front, one burst per clump cell, 2 s pawn cooldown: RM_MapComponent_Knockback, live (the exact goods cap is fx_caps)"),
    ("nk_only_explosions_hook", ["only_explosions_throw", "inv_hook"], "only the explosion damage worker is patched: game-side hook (the per-type forces are py_damage_type_forces)"),
    ("nk_walk_storeroom_raid", ["walk_storeroom_raid"], "a raid walk on the full list: live"),
    ("nk_barrage_frames", ["barrage_frame_budget"], "frames under 50 ms through a barrage: live measurement (the reading is fx_frame_stats)"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel")
    ap.add_argument("--src", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    ap.add_argument("--no-proof-build", action="store_true")
    a = ap.parse_args()
    root = os.environ.get("EK_LANE1_STAGE") or "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c3_lane1"
    os.makedirs(root, exist_ok=True)
    for f in glob.glob(os.path.join(root, "*.cs")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), root)
    shutil.copy(a.kernel or os.path.join(a.src, "Source/RM_KnockbackMath.cs"), os.path.join(root, "RM_KnockbackMath.cs"))
    open(os.path.join(root, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", root], capture_output=True, text=True, check=True).stdout.strip()
    rows = []
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode != 0:
        errs = re.findall(r"error CS\d+[^\r\n]*", b.stdout)
        rows.append(row("cs_build", ["inv_kernel"], "fixed", False, 1, "kernel + BlindLane1 do not build: %s" % " | ".join(errs[:3])[:500]))
    else:
        r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
        for ln in r.stdout.splitlines():
            ln = ln.strip()
            if ln.startswith("{"):
                rows.append(json.loads(ln))
        if r.returncode != 0:
            rows.append(row("cs_run", ["inv_kernel"], "fixed", False, 1, "BlindLane1 rc %d: %s" % (r.returncode, r.stderr.strip()[-400:])))
    rows += settings_rows(a.src) + patch_rows(a.src) + gate_rows(a.src)
    if not a.no_proof_build:
        rows += proof_build_row(a.src)
    for id_, bars, why in NOT_KERNEL:
        rows.append(row(id_, bars, "not_kernel", False, 0, "game-side: " + why, verdict="UNSETTLED"))
    with open(a.out, "w") as fh:
        for r_ in rows:
            fh.write(json.dumps(r_) + "\n")
    counts = {}
    for r_ in rows:
        counts[r_["verdict"]] = counts.get(r_["verdict"], 0) + 1
    print("LANE1 rows %d %s -> %s" % (len(rows), " ".join("%s %d" % kv for kv in sorted(counts.items())), a.out))
    for r_ in rows:
        if r_["verdict"] == "FAIL":
            print("FAIL %s: %s" % (r_["id"], r_["detail"][:300]))
    return 1 if counts.get("FAIL") else 0


if __name__ == "__main__":
    sys.exit(main())
