#!/usr/bin/env python3
"""V&V pilot 1: FlowWorks (and EmpirePursuit) fuzz/property families at the SHIPPED settings, honest failure rates.

    python3 src/RimMandrake/Utils/vv_shipped_matrix.py [--quick] [--skip-ep] [--skip-control] [--skip-suites]
    python3 src/RimMandrake/Utils/vv_shipped_matrix.py --lint-only

Report: design/RimMandrake/vv_methods/pilot1_shipped_matrix_2026-10-16.md (method, results, classification).

WHAT "SHIPPED" MEANS HERE. The kernel configuration is DERIVED, not typed in: the defaults of
RimMandrakeFlowWorksSettings (RimMandrakeFlowWorksMod.cs field initialisers, cross-checked against the Scribe default of
the same field) are pushed through the adapter lines that copy settings into RM_FlowKernel every pulse
(RM_MapComponent_Excavation.DoPulse, `flowKernel.<field> = <expr>;`). Each single-flag-off configuration flips ONE
player-facing bool setting that an adapter line reads and re-evaluates the adapter (so viscosity off also turns creep off,
exactly as the game does). The owner's saved settings file is read and its differences listed, never used.

HOW. Stages FlowWorks/Source (+ Defs, _Shared) on D:\\Luke\\dev\\_rmbuild\\VV_PILOT1_<clone hash>, deletes the probe
bin/obj (stale-stage lesson 2026-10-16), inserts one line into the STAGED ArrayWorld.Pulse
(`VV.MatrixFlags.Apply(k);` just before `k.Pulse`) and one into the staged Program.Case (case name), builds
SelfTest/VV/ShippedMatrixProbe.cs with the whole SelfTest compile list, and runs it with Windows dotnet.exe.
Nothing in the clone is modified.

PRE-DECLARED PASS CRITERION (written before the first run, 2026-10-16):
  PASS iff (1) at SHIPPED every randomised family completes its fixed n with 0 failures, 0 exceptions, no timeout;
  (2) every kernel family's pulses went through the hook (kernel_pulses_hooked > 0);
  (3) the negative control reproduces: on the pre-fix kernel (c82dd1c08^) fills_from_limitless at base seed 1000,
      n=2000 is RED at SHIPPED and 0 at AUTHORED (stage 2 measured 194/2000 on its HEAD then);
  (4) the AUTHORED full suite run through the probe passes (the staging and hook change nothing by themselves).
  Anything else exits 1. A red at a single-flag-off configuration does not fail the run; it is classified in the report.
STOPPING RULE: fixed n per family, chosen before running (below); never extended or cut on results. The only early stop
  is the per-family wall cap (--cap-seconds, default 1200), recorded as TIMEOUT = NOT EVIDENCED, never a pass.
BOUNDS: 0 failures in n -> rule-of-three 95% upper bound 3/n; k > 0 -> Wilson 95% interval. Both describe THIS
  generator's scene distribution, not a player's failure rate.
"""
import argparse
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

FW = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks")
SRC = os.path.join(FW, "Source")
SELFTEST = os.path.join(SRC, "SelfTest")
SETTINGS_CS = os.path.join(SRC, "RimMandrakeFlowWorksMod.cs")
ADAPTER_CS = os.path.join(SRC, "RM_MapComponent_Excavation.cs")
KERNEL_CS = os.path.join(SRC, "RM_FlowKernel.cs")
EP = os.path.join(ROOT, "src", "RimUtinni", "EmpirePursuit", "Source")
OWNER_SETTINGS = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/"
                  "Mod_FlowWorks_RimMandrakeFlowWorksMod.xml")
CONTROL_REV = "c82dd1c08^"
TAG = hashlib.sha1(os.path.realpath(ROOT).encode()).hexdigest()[:8]
STAGE = os.path.join(winbuild.BUILD_ROOT, "VV_PILOT1_" + TAG)

# fixed n per family (the stopping rule); --quick divides by 10 for a smoke run (never a verdict)
SHIPPED_N = {"kernel_fuzz": 10000, "fills_from_limitless": 10000, "surface_random": 1000,
             "seq_sequences": 20000, "seq_orders": 200000, "seq_conversion": 5000, "seq_pitwidth": 20000,
             "hose": 1500, "trail": 1500}
AUTHORED_N = {"kernel_fuzz": 10000, "fills_from_limitless": 10000, "fills_from_limitless_shippedarg": 10000,
              "surface_random": 1000, "surface_random_levelset": 1000}
SINGLE_OFF_N = {"kernel_fuzz": 2000, "fills_from_limitless": 2000, "surface_random": 1000}
EP_N = {"ladder": 8000, "timers": 3000, "math": 5000}
BASE_SEED = 500000          # fresh seeds: Program.cs uses 1, 7, 11, 13, 101, 202, 1000


# ───────────────────────────── shipped configuration, derived ─────────────────────────────

def _num(v):
    v = v.strip().rstrip("fF")
    return float(v) if "." in v else int(v)


def settings_defaults(text):
    """Field initialisers of every public static bool/int/float setting, and the Scribe default of each."""
    init = {}
    for m in re.finditer(r"public static (bool|int|float) (\w+) = ([^;]+);", text):
        typ, name, val = m.groups()
        val = val.split("//")[0].strip()
        if typ == "bool":
            if val in ("true", "false"):
                init[name] = val == "true"
        else:
            try:
                init[name] = _num(val)
            except ValueError:
                pass
    scribe = {}
    for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([^)]+)\)', text):
        name, _, val = m.groups()
        val = val.strip()
        scribe[name] = (val == "true") if val in ("true", "false") else (_num(val) if re.fullmatch(r"-?[\d.]+f?", val) else val)
    props = {m.group(1): m.group(2) for m in re.finditer(r"public static (?:int|float|bool) (\w+) => ([^;]+);", text)}
    return init, scribe, props


def adapter_lines(text):
    """`flowKernel.<field> = <expr>;` assignments inside DoPulse (one-line ones; multi-line = scene-dependent)."""
    i = text.index("private void DoPulse()")
    j = text.index("flowKernel.Pulse(", i)
    body = text[i:j]
    out, scene = [], []
    for m in re.finditer(r"flowKernel\.(\w+) = ([^;]*?)(;|\n)", body):
        field, expr, end = m.groups()
        if field in ("depth", "fill"):
            continue
        # a line that reads no setting (sealedCell's door lambda) or spans lines (externalInput's driver set) is scene state
        settings_driven = end == ";" and "RimMandrakeFlowWorksSettings." in expr
        (out if settings_driven else scene).append((field, expr.strip()))
    return out, scene


def _py(expr):
    e = expr.replace("RimMandrakeFlowWorksSettings.", "")
    e = e.replace("MapControls.RM_MapControls.AnyDrainEdge(map)", "SCENE_DRAIN_EDGE")
    e = e.replace("Mathf.Clamp", "clamp").replace("Mathf.RoundToInt", "round")
    e = re.sub(r"(\d+(?:\.\d+)?)f\b", r"\1", e)
    e = e.replace("&&", " and ").replace("||", " or ")
    e = re.sub(r"!(?!=)", " not ", e)
    return e


class _Env(dict):
    def __init__(self, settings, props):
        super().__init__()
        self.s, self.p = settings, props

    def __missing__(self, k):
        if k == "clamp":
            return lambda v, lo, hi: max(lo, min(hi, v))
        if k == "round":
            return lambda v: int(round(v))
        if k == "SCENE_DRAIN_EDGE":
            return False            # a map with no dev drain edge (the default map)
        if k in self.s:
            return self.s[k]
        if k in self.p:
            return eval(_py(self.p[k]), {"__builtins__": {}}, self)
        raise KeyError("adapter expression names %r, which is not a parsed setting" % k)


def kernel_config(settings, props, lines):
    env = _Env(settings, props)
    return {f: eval(_py(e), {"__builtins__": {}}, env) for f, e in lines}


def settings_read_by(expr):
    return set(re.findall(r"RimMandrakeFlowWorksSettings\.(\w+)", expr))


def kernel_defaults(text):
    out = {}
    for m in re.finditer(r"public (bool|int) (\w+)( = ([^;]+))?;", text):
        typ, name, _, val = m.groups()
        out[name] = (val.strip() == "true") if typ == "bool" and val else (False if typ == "bool" else int(val or 0))
    return out


def derive():
    st = open(SETTINGS_CS, encoding="utf-8").read()
    init, scribe, props = settings_defaults(st)
    lines, scene = adapter_lines(open(ADAPTER_CS, encoding="utf-8").read())
    # a symbolic Scribe default (a named constant) is not parsed: only literal-vs-literal disagreements count as drift
    drift = [(k, init[k], scribe[k]) for k in scribe if k in init and not isinstance(scribe[k], str) and scribe[k] != init[k]]
    shipped = kernel_config(init, props, lines)
    read = sorted(set().union(*[settings_read_by(e) for _, e in lines]) | set().union(*[settings_read_by(e) for _, e in scene]))
    bools = [s for s in read if isinstance(init.get(s), bool)]
    variants = []
    for s in bools:
        flipped = dict(init)
        flipped[s] = not init[s]
        cfg = kernel_config(flipped, props, lines)
        diff = {k: v for k, v in cfg.items() if v != shipped[k]}
        variants.append({"setting": s, "shipped": init[s], "kernel": cfg, "diff": diff,
                         "scene_only": not diff and any(s in settings_read_by(e) for _, e in scene)})
    owner, owner_seen = {}, 0
    if os.path.isfile(OWNER_SETTINGS):
        try:
            ms = ET.parse(OWNER_SETTINGS).getroot().find("ModSettings")
            for k in read:
                el = ms.find(k) if ms is not None else None
                if el is not None:
                    owner_seen += 1
                    raw = el.text.strip()
                    v = (raw.lower() == "true") if isinstance(init.get(k), bool) else _num(raw)
                    if v != init.get(k):
                        owner[k] = {"shipped": init.get(k), "owner_saved": v}
        except ET.ParseError as e:
            owner = {"_error": str(e)}
    return {"settings_read": read, "scribe_drift": drift, "adapter": lines, "adapter_scene": scene,
            "shipped": shipped, "variants": variants, "owner_diff": owner, "owner_keys_seen": owner_seen,
            "kernel_defaults": kernel_defaults(open(KERNEL_CS, encoding="utf-8").read())}


# ───────────────────────────── static flag lint ─────────────────────────────

def static_lint(d):
    """For each adapter-set kernel field: does any SelfTest file assign it the shipped value (literally), via an
    expression only, or never (then it runs at the C# default)?"""
    files = [p for p in glob.glob(os.path.join(SELFTEST, "*.cs"))]
    rows = []
    for field, _ in d["adapter"]:
        want = d["shipped"][field]
        lit, expr, other = [], [], []
        pat = re.compile(r"(?:\.k\.|\b(?:k|w\.k|a\.k|b\.k|c\.k|s\.k)\.)%s\s*=\s*([^;]+);|[{,]\s*%s\s*=\s*([^,}]+)" % (field, field))
        for p in files:
            for ln, line in enumerate(open(p, encoding="utf-8"), 1):
                for m in pat.finditer(line):
                    rhs = (m.group(1) or m.group(2) or "").strip()
                    where = "%s:%d" % (os.path.basename(p), ln)
                    val = {"true": True, "false": False}.get(rhs)
                    if val is None and re.fullmatch(r"\d+", rhs):
                        val = int(rhs)
                    if val is None:
                        expr.append(where)
                    elif val == want:
                        lit.append(where)
                    else:
                        other.append(where)
        dflt = d["kernel_defaults"].get(field)
        status = ("literal-shipped" if lit else "default-is-shipped" if dflt == want else
                  "expression-only" if expr else "GAP-never-shipped")
        rows.append({"field": field, "shipped": want, "csharp_default": dflt, "status": status,
                     "literal_shipped": len(lit), "expression": len(expr), "literal_other": len(other),
                     "first": (lit or expr or other or ["-"])[0]})
    return rows


# ───────────────────────────── stage, patch, build ─────────────────────────────

PULSE_ANCHOR = "public void Pulse(IEnumerable<int> seeds) { pulse++; k.Pulse(seeds, pulse); Sync(); }"
PULSE_HOOK = "public void Pulse(IEnumerable<int> seeds) { pulse++; VV.MatrixFlags.Apply(k); k.Pulse(seeds, pulse); Sync(); }"
CASE_ANCHOR = "        private static void Case(string name, Action fn)\n        {\n"
CASE_HOOK = CASE_ANCHOR + "            VV.MatrixFlags.CurrentCase = name;\n"


def _patch(path, anchor, repl):
    t = open(path, encoding="utf-8").read()
    if t.count(anchor) != 1:
        sys.exit("VV: anchor found %d times in %s (want exactly 1): the test file changed; update the hook" % (t.count(anchor), path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(t.replace(anchor, repl))


def _rsync(rels, dest):
    excl = sum((["--exclude", e] for e in winbuild.RSYNC_EXCLUDES + ["__pycache__/", "art_source/"]), [])
    r = subprocess.run(["rsync", "-rtR", "--delete", "--no-perms", "--no-owner", "--no-group", "--modify-window=2",
                        "--checksum", *excl, *rels, dest + "/"], cwd=ROOT)
    if r.returncode:
        sys.exit("VV: rsync failed (%d)" % r.returncode)


def _probe_csproj(src_csproj, extra, startup, defines, assembly):
    t = open(src_csproj, encoding="utf-8").read()
    t = re.sub(r'<Compile Include="([^"]+)"', lambda m: '<Compile Include="..\\%s"' % m.group(1), t)
    t = t.replace("<ItemGroup>", "<ItemGroup>\n" + "".join('    <Compile Include="%s" />\n' % e for e in extra), 1)
    t = re.sub(r"<AssemblyName>[^<]*</AssemblyName>", "<AssemblyName>%s</AssemblyName>" % assembly, t)
    t = t.replace("</PropertyGroup>", "  <StartupObject>%s</StartupObject>\n    <DefineConstants>$(DefineConstants);%s</DefineConstants>\n"
                  "    <NoWarn>$(NoWarn);CS8981;CS0168;CS0219;CS0162</NoWarn>\n  </PropertyGroup>" % (startup, defines), 1)
    return t


def _build(csproj_path):
    d = os.path.dirname(csproj_path)
    for sub in ("bin", "obj"):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)     # stale-stage lesson: never trust a warm bin/obj
    rc = winbuild.run_dotnet(winbuild.win(csproj_path), d, "Release", [])
    if rc:
        sys.exit("VV: build failed for %s (env/build failure, not a verdict)" % csproj_path)
    dll = glob.glob(os.path.join(d, "bin", "Release", "net8.0", "*.dll"))
    return d


def stage_flowworks(control=False):
    """control=True: the same stage with RM_FlowKernel.cs replaced by CONTROL_REV's, and a minimal compile list."""
    dest = STAGE + ("_control" if control else "")
    os.makedirs(dest, exist_ok=True)
    # the selftests read the mod's shipped Defs/, Patches/ and Tools/ (call-site and data pins), so they are staged
    rels = ["src/RimMandrake/FlowWorks/Source/", "src/RimMandrake/FlowWorks/Defs/", "src/RimMandrake/FlowWorks/Patches/",
            "src/RimMandrake/FlowWorks/Tools/", "src/RimMandrake/_Shared/",
            "src/Directory.Build.targets", "src/Directory.Build.props"]
    _rsync(rels, dest)
    st = os.path.join(dest, "src", "RimMandrake", "FlowWorks", "Source", "SelfTest")
    _patch(os.path.join(st, "FlowKernelFuzz.cs"), PULSE_ANCHOR, PULSE_HOOK)
    vv = os.path.join(st, "VV")
    if control:
        # the pre-fix kernel AND the fuzz file of the same revision (HEAD's fuzz file calls kernel members added later)
        old_fuzz = subprocess.run(["git", "show", "%s:src/RimMandrake/FlowWorks/Source/SelfTest/FlowKernelFuzz.cs" % CONTROL_REV],
                                  cwd=ROOT, capture_output=True, text=True, check=True).stdout
        with open(os.path.join(st, "FlowKernelFuzz.cs"), "w", encoding="utf-8") as f:
            f.write(old_fuzz)
        _patch(os.path.join(st, "FlowKernelFuzz.cs"), PULSE_ANCHOR, PULSE_HOOK)
        old = subprocess.run(["git", "show", "%s:src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs" % CONTROL_REV],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
        with open(os.path.join(dest, "src", "RimMandrake", "FlowWorks", "Source", "RM_FlowKernel.cs"), "w", encoding="utf-8") as f:
            f.write(old)
        proj = ('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>'
                '<LangVersion>latest</LangVersion><ImplicitUsings>enable</ImplicitUsings><Nullable>disable</Nullable>'
                '<EnableDefaultCompileItems>false</EnableDefaultCompileItems><AssemblyName>VVControl</AssemblyName>'
                '<StartupObject>RimMandrake.FlowWorks.SelfTest.VV.ShippedMatrixProbe</StartupObject>'
                '<NoWarn>CS8981;CS0168;CS0219;CS0162</NoWarn></PropertyGroup><ItemGroup>'
                + "".join('<Compile Include="%s" />' % c for c in [
                    "..\\..\\RM_StockMath.cs", "..\\..\\RM_FlowKernel.cs", "..\\..\\RM_PumpMath.cs", "..\\..\\RM_FireMath.cs",
                    "..\\..\\RM_PitTrapMath.cs", "..\\..\\RM_RelativeRulesMath.cs", "..\\..\\Machinery\\RM_ConversionMath.cs", "..\\..\\RM_Volume.cs",
                    "..\\FlowKernelFuzz.cs", "..\\SequenceFuzz.cs", "ShippedMatrixProbe.cs"])
                + '</ItemGroup></Project>')
        path = os.path.join(vv, "VVControl.csproj")
    else:
        _patch(os.path.join(st, "Program.cs"), CASE_ANCHOR, CASE_HOOK)
        proj = _probe_csproj(os.path.join(st, "RimMandrakeFlowWorks.SelfTest.csproj"), ["ShippedMatrixProbe.cs"],
                             "RimMandrake.FlowWorks.SelfTest.VV.ShippedMatrixProbe", "VV_HOSE", "VVProbe")
        path = os.path.join(vv, "VVProbe.csproj")
    with open(path, "w", encoding="utf-8") as f:
        f.write(proj)
    _build(path)
    return os.path.join(vv, "bin", "Release", "net8.0", os.path.splitext(os.path.basename(path))[0] + ".dll")


def stage_ep():
    dest = STAGE + "_ep"
    os.makedirs(dest, exist_ok=True)
    _rsync(["src/RimUtinni/EmpirePursuit/Source/", "src/Directory.Build.targets", "src/Directory.Build.props"], dest)
    fz = os.path.join(dest, "src", "RimUtinni", "EmpirePursuit", "Source", "SelfTest", "Fuzz")
    vv = os.path.join(dest, "src", "RimUtinni", "EmpirePursuit", "Source", "SelfTest", "VV")
    proj = _probe_csproj(os.path.join(fz, "EmpirePursuitFuzz.csproj"), ["EpRatesProbe.cs"],
                         "RuthlessPursuingMechanoids.Fuzz.VV.EpRatesProbe", "VV_EP", "VVEp")
    proj = proj.replace('Include="..\\..\\..\\', 'Include="..\\..\\').replace('Include="..\\EmpirePursuitFuzz.cs"', 'Include="..\\Fuzz\\EmpirePursuitFuzz.cs"').replace('Include="..\\Program.cs"', 'Include="..\\Fuzz\\Program.cs"')
    path = os.path.join(vv, "VVEp.csproj")
    with open(path, "w", encoding="utf-8") as f:
        f.write(proj)
    _build(path)
    return os.path.join(vv, "bin", "Release", "net8.0", "VVEp.dll")


# ───────────────────────────── run ─────────────────────────────

def _run(dll, args, timeout=7200):
    cmd = [winbuild.dotnet_exe(), winbuild.win(dll), *args]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=os.path.dirname(dll), capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr, time.time() - t0


def setstr(cfg):
    return ";".join("%s=%s" % (k, (1 if v else 0) if isinstance(v, bool) else v) for k, v in sorted(cfg.items()))


def rates(dll, out, config, cfg, ns, cap, scale):
    for fam, n in ns.items():
        n = max(1, n // scale)
        args = ["rates", "--config", config, "--set", setstr(cfg) if cfg else "", "--families", fam, "--n", str(n),
                "--base", str(BASE_SEED), "--cap-seconds", str(cap), "--out", winbuild.win(out)]
        rc, so, se, dt = _run(dll, args)
        sys.stdout.write(so)
        if rc:
            print("VV: probe rc=%d for %s/%s: %s" % (rc, config, fam, (se or so)[-800:]))


def bound(k, n):
    if n <= 0:
        return "n=0"
    if k == 0:
        return "0 (rule of three: < %.3g%%)" % (300.0 / n)
    z = 1.96
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return "%.3g%% (Wilson 95%%: %.3g-%.3g%%)" % (100 * p, 100 * (c - h), 100 * (c + h))


def suite(dll, out, cfg, record, track):
    args = ["suite", "--out", winbuild.win(out), "--track", ",".join(track)]
    if cfg:
        args += ["--set", setstr(cfg)]
    if record:
        args.append("--record")
    rc, so, se, dt = _run(dll, args)
    with open(out[:-5] + ".stdout.txt", "w") as f:
        f.write(so)
    fails = re.findall(r"^FAIL  (\S+)", so, re.M)
    hose_fail = re.findall(r"^\s*FAIL\b(?!  )(.*)$", so, re.M)
    summary = re.findall(r"^(\d+)/(\d+) passed", so, re.M)
    rec = json.load(open(out)) if os.path.isfile(out) else {}
    return {"rc": rec.get("rc"), "fails": fails, "passed": summary[-1] if summary else None, "seconds": round(dt, 1),
            "hook_calls": rec.get("hook_calls"), "tail": so[-1500:] if not summary else "", "rec": rec}


def dynamic_lint(rec, shipped):
    per_field = {}
    for line in rec.get("field_tally", []):
        case, field, val, cnt = line.split("\t")
        per_field.setdefault(field, {}).setdefault(val, set()).add(case)
    rows = []
    for field, want in shipped.items():
        w = str(want) if not isinstance(want, bool) else ("True" if want else "False")
        vals = per_field.get(field, {})
        rows.append({"field": field, "shipped": want, "cases_at_shipped": len(vals.get(w, set())),
                     "values_seen": {k: len(v) for k, v in vals.items()}})
    want_tuple = "".join("%s=%s;" % (f, ("True" if v else "False") if isinstance(v, bool) else v) for f, v in shipped.items())
    full = sorted({l.split("\t")[0] for l in rec.get("tuple_tally", []) if l.split("\t")[1] == want_tuple})
    kernel_cases = sorted({l.split("\t")[0] for l in rec.get("tuple_tally", [])})
    return rows, full, kernel_cases


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="n/10 smoke run (never a verdict)")
    ap.add_argument("--lint-only", action="store_true")
    ap.add_argument("--skip-ep", action="store_true")
    ap.add_argument("--skip-control", action="store_true")
    ap.add_argument("--skip-suites", action="store_true")
    ap.add_argument("--cap-seconds", type=int, default=1200)
    a = ap.parse_args(argv)
    scale = 10 if a.quick else 1

    d = derive()
    print("== shipped kernel configuration (settings defaults -> adapter) ==")
    for f, e in d["adapter"]:
        print("  %-22s = %-6s  <- %s" % (f, d["shipped"][f], e))
    for f, e in d["adapter_scene"]:
        print("  %-22s = (scene)  <- %s ..." % (f, e))
    print("  scribe drift:", d["scribe_drift"] or "none")
    print("  owner's saved settings (%d of the %d adapter-read keys present in the file) differ on:" % (d["owner_keys_seen"], len(d["settings_read"])), d["owner_diff"] or "none")
    lint = static_lint(d)
    print("== static flag lint ==")
    for r in lint:
        print("  %-22s shipped=%-5s default=%-5s %-20s (literal-shipped %d, expression %d, other %d; first %s)" % (
            r["field"], r["shipped"], r["csharp_default"], r["status"], r["literal_shipped"], r["expression"], r["literal_other"], r["first"]))
    if a.lint_only:
        return 0

    run_dir = os.path.join(STAGE + "_results", time.strftime("%Y%m%dT%H%M%S"))
    os.makedirs(run_dir, exist_ok=True)
    json.dump({k: v for k, v in d.items()}, open(os.path.join(run_dir, "derived.json"), "w"), indent=1, default=str)
    out = os.path.join(run_dir, "rates.jsonl")
    track = [f for f, _ in d["adapter"]]
    shipped = d["shipped"]
    verdict = []

    dll = stage_flowworks()
    print("== suites (one run each) ==")
    suites = {}
    if not a.skip_suites:
        suites["AUTHORED"] = suite(dll, os.path.join(run_dir, "suite_AUTHORED.json"), None, True, track)
        suites["SHIPPED"] = suite(dll, os.path.join(run_dir, "suite_SHIPPED.json"), shipped, False, track)
        for v in d["variants"]:
            if v["diff"]:
                suites["OFF_" + v["setting"]] = suite(dll, os.path.join(run_dir, "suite_OFF_%s.json" % v["setting"]), v["kernel"], False, track)
        for k, s in suites.items():
            print("  %-36s passed %s  fails %d  hook %s  %.0fs %s" % (k, s["passed"], len(s["fails"]), s["hook_calls"], s["seconds"], s["tail"][-300:]))
        if suites["AUTHORED"]["fails"] or not suites["AUTHORED"]["passed"]:
            verdict.append("AUTHORED suite through the probe is not clean: %s" % suites["AUTHORED"]["fails"])
        rows, full, kcases = dynamic_lint(suites["AUTHORED"]["rec"], shipped)
        print("== dynamic flag lint (AUTHORED suite, pulses through the hook) ==")
        for r in rows:
            print("  %-22s shipped=%-5s cases at shipped %3d   values seen (cases) %s" % (r["field"], r["shipped"], r["cases_at_shipped"], r["values_seen"]))
        print("  cases that pulse a kernel: %d; cases that ever ran the FULL shipped tuple: %d %s" % (len(kcases), len(full), full[:12]))
        json.dump({"rows": rows, "full_shipped_cases": full, "kernel_cases": kcases,
                   "suites": {k: {kk: vv for kk, vv in s.items() if kk != "rec"} for k, s in suites.items()}},
                  open(os.path.join(run_dir, "suites.json"), "w"), indent=1)

    print("== rates ==")
    rates(dll, out, "SHIPPED", shipped, SHIPPED_N, a.cap_seconds, scale)
    rates(dll, out, "AUTHORED", None, AUTHORED_N, a.cap_seconds, scale)
    for v in d["variants"]:
        if v["diff"]:
            rates(dll, out, "OFF_" + v["setting"], v["kernel"], SINGLE_OFF_N, a.cap_seconds, scale)
    if not a.skip_control:
        cdll = stage_flowworks(control=True)
        cout = os.path.join(run_dir, "control.jsonl")
        global BASE_SEED
        keep, BASE_SEED = BASE_SEED, 1000
        # the pre-fix kernel has none of the fields added after it (levelExactEnabled, WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES):
        # MatrixFlags refuses an unknown field, so the control forces only the shipped fields that kernel declares
        old_kernel = subprocess.run(["git", "show", "%s:src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs" % CONTROL_REV],
                                    cwd=ROOT, capture_output=True, text=True, check=True).stdout
        old_fields = set(kernel_defaults(old_kernel))
        control_cfg = {k: v for k, v in shipped.items() if k in old_fields}
        print("  control forces %d of %d shipped fields (absent from %s: %s)" % (
            len(control_cfg), len(shipped), CONTROL_REV, sorted(set(shipped) - old_fields) or "none"))
        rates(cdll, cout, "CONTROL_prefix_SHIPPED", control_cfg, {"fills_from_limitless": 2000}, a.cap_seconds, 1)
        rates(cdll, cout, "CONTROL_prefix_AUTHORED", None, {"fills_from_limitless": 2000}, a.cap_seconds, 1)
        BASE_SEED = keep
        cr = {r["config"]: r for r in map(json.loads, open(cout))}
        cs, ca = cr.get("CONTROL_prefix_SHIPPED", {}), cr.get("CONTROL_prefix_AUTHORED", {})
        print("  control: pre-fix kernel %s, shipped %s/%s, authored %s/%s" % (CONTROL_REV, cs.get("failures"), cs.get("completed"), ca.get("failures"), ca.get("completed")))
        if not (cs.get("failures", 0) > 0 and ca.get("failures", 1) == 0):
            verdict.append("negative control did not reproduce (the matrix cannot see the bug it exists for)")
    if not a.skip_ep:
        edll = stage_ep()
        for fam, n in EP_N.items():
            rc, so, se, dt = _run(edll, ["rates", "--families", fam, "--n", str(max(1, n // scale)), "--base", str(BASE_SEED),
                                         "--cap-seconds", str(a.cap_seconds), "--out", winbuild.win(out)])
            sys.stdout.write(so)

    print("== summary ==")
    recs = [json.loads(l) for l in open(out)]
    for r in recs:
        print("  %-28s %-32s %6d/%-7d %s%s" % (r["config"], r["family"], r["failures"], r["completed"], bound(r["failures"], r["completed"]),
                                               " TIMEOUT" if r["timed_out"] else ""))
        if r["config"] == "SHIPPED" or r["config"].startswith("SHIPPED_GATES"):
            if r["failures"] or r["exceptions"] or r["timed_out"]:
                verdict.append("%s red at shipped: %d/%d" % (r["family"], r["failures"], r["completed"]))
            if r["family"] in ("kernel_fuzz", "fills_from_limitless", "surface_random") and r.get("kernel_pulses_hooked", 0) <= 0:
                verdict.append("%s: no kernel pulse went through the hook" % r["family"])
    if a.quick:
        verdict.append("--quick: a smoke run, never a verdict")
    print("results:", winbuild.win(run_dir))
    print("VERDICT:", "PASS" if not verdict else "FAIL\n  " + "\n  ".join(verdict))
    return 0 if not verdict else 1


if __name__ == "__main__":
    sys.exit(main())
