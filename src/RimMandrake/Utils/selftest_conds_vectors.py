#!/usr/bin/env python3
# selftest-timeout: 600   (lost WSL launches winbuild.run_interop repeats: up to 3 at ~2 min each, INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT)
"""Selftest: the bridge condition evaluator's two twins agree byte for byte (CONDCORE_BUILD_THREE_VALUED_TREES).

Spec: design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 row T1. The C# core
(bridgetools/JawaBench.BridgeTools/JawaBenchCondCore.cs, compiled into the companion and into bridgetools/CondSelfTest)
and the Python twin (Utils/conds.py) both run Utils/conds_vectors.json. Checks:
  1. every vector's `expect` holds as a subset of the Python result (the semantics, not just parity);
  2. the vectors carry every required case tag and a refusal vector for every name in conds.REFUSALS, and the C# core
     emits exactly that set of refusal names;
  3. the committed C# output Utils/conds_vectors.cs_out.txt is stamped with the sha256 of the current C# core,
     CondSelfTest/Program.cs and the vectors (a stale golden fails), and its body is byte-identical to the Python output;
  4. when dotnet.exe runs here, CondSelfTest is built (winbuild staging) and its live output must equal both.
     Where no Windows program runs (the walled checker) step 4 says SKIPPED and steps 1-3 carry the proof;
     --require-cs makes its absence a FAIL. --regen rewrites the golden from a live C# run (never from Python).

Run: python3 src/RimMandrake/Utils/selftest_conds_vectors.py [--require-cs] [--regen]
"""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import conds  # noqa: E402

BT = os.path.join(REPO, "src", "RimMandrake", "bridgetools")
CORE = os.path.join(BT, "JawaBench.BridgeTools", "JawaBenchCondCore.cs")
PROG = os.path.join(BT, "CondSelfTest", "Program.cs")
PROJ = os.path.join(BT, "CondSelfTest", "CondSelfTest.csproj")
VECTORS = os.path.join(HERE, "conds_vectors.json")
GOLDEN = os.path.join(HERE, "conds_vectors.cs_out.txt")

REQUIRED_TAGS = ("true_at_arm", "max_ticks_0", "hit_on_deadline", "unknown_mid_streak", "unknown_gap_before_edge",
                 "empty_rect_refused", "stateful_child_under_any_true", "shared_probe_independent_baselines",
                 "epoch_change_under_stays")

_fails = []


def check(ok, name, why=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else " -- " + why))
    if not ok:
        _fails.append(name)


def subset(want, got, path="$"):
    """None when want is a subset of got, else the first difference."""
    if isinstance(want, dict):
        if not isinstance(got, dict):
            return "%s: want object, got %s" % (path, conds.canon(got)[:80])
        for k in sorted(want):
            if k not in got:
                return "%s.%s missing" % (path, k)
            d = subset(want[k], got[k], path + "." + k)
            if d:
                return d
        return None
    if isinstance(want, list):
        if not isinstance(got, list) or len(want) != len(got):
            return "%s: want %s, got %s" % (path, conds.canon(want)[:80], conds.canon(got)[:80])
        for i, (w, g) in enumerate(zip(want, got)):
            d = subset(w, g, "%s[%d]" % (path, i))
            if d:
                return d
        return None
    return None if conds.canon(want) == conds.canon(got) else "%s: want %s, got %s" % (
        path, conds.canon(want)[:80], conds.canon(got)[:80])


def stamp():
    h = hashlib.sha256()
    for p in (CORE, PROG, VECTORS):
        with open(p, "rb") as fh:
            h.update(fh.read())
        h.update(b"\0")
    return h.hexdigest()


def dotnet_runs():
    try:
        import winbuild
        exe = winbuild.dotnet_exe()
    except Exception:
        return None
    if not exe or not os.path.exists(exe):
        return None
    try:
        p = winbuild.run_interop_captured([exe, "--version"], capture_output=True, text=True, timeout=60, cwd="/mnt/d/Luke/dev")
    except (OSError, subprocess.SubprocessError):
        return None
    return exe if p.returncode == 0 else None


def run_cs(exe, vectors_text):
    import winbuild
    proj = os.path.dirname(PROJ)
    rc, rec = winbuild.stage_build(PROJ, stage_name="CondSelfTest")
    if rc:
        return None, "build FAILED (rc %s)" % rc
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\CondSelfTest.dll"
    p = winbuild.run_interop_captured([exe, dll], input=vectors_text.encode("utf-8"), capture_output=True, timeout=300,
                       cwd="/mnt/d/Luke/dev")
    if p.returncode:
        return None, "CondSelfTest exit %d: %s" % (p.returncode, p.stderr.decode("utf-8", "replace")[-400:])
    return p.stdout.decode("utf-8"), ""


def main(argv):
    with open(VECTORS, encoding="utf-8") as fh:
        text = fh.read()
    doc = conds.parse_json(text)
    vecs = doc["vectors"]
    py_out = conds.run_vectors_text(text)

    # 1. semantics: each expect is a subset of the result
    bad = []
    for v in vecs:
        d = subset(v.get("expect", {}), conds.run_vector(v))
        if d:
            bad.append("%s: %s" % (v["name"], d))
    check(not bad, "expect holds on %d vectors" % len(vecs), "; ".join(bad[:5]))
    check(all(v.get("expect") for v in vecs), "every vector states an expect",
          ",".join(v["name"] for v in vecs if not v.get("expect")))

    # 2. coverage of required cases and of every refusal name, in both twins
    tags = set(t for v in vecs for t in v.get("tags", []))
    miss = [t for t in REQUIRED_TAGS if t not in tags]
    check(not miss, "required case tags present", ",".join(miss))
    refused = set(conds.run_vector(v).get("refused") for v in vecs) - {None}
    miss = [n for n in conds.REFUSALS if n not in refused]
    check(not miss, "a vector refuses with each of %d names" % len(conds.REFUSALS), ",".join(miss))
    with open(CORE, encoding="utf-8") as fh:
        cs = fh.read()
    cs_names = set(re.findall(r'\bRefuse\("([a-z_0-9]+)"', cs)) | set(re.findall(r'R_[A-Za-z]+ = "([a-z_0-9]+)"', cs))
    check(cs_names == set(conds.REFUSALS), "C# core emits the same refusal names",
          "only C#: %s; only Python: %s" % (sorted(cs_names - set(conds.REFUSALS)), sorted(set(conds.REFUSALS) - cs_names)))
    impure = re.findall(r"(?m)^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", cs)
    check(not impure, "C# core is pure (no Verse/RimWorld/Unity/Harmony using)", ",".join(impure))

    # 3. the committed C# output: current stamp, and byte-identical to Python
    want_stamp = stamp()
    regen = "--regen" in argv
    golden = None
    if os.path.exists(GOLDEN):
        with open(GOLDEN, encoding="utf-8", newline="") as fh:
            golden = fh.read()
    exe = dotnet_runs()
    cs_live = None
    if exe and "--no-cs" not in argv:
        cs_live, why = run_cs(exe, text)
        check(cs_live is not None, "CondSelfTest builds and runs", why)
    if regen:
        if cs_live is None:
            check(False, "--regen needs a live C# run", "no dotnet or the run failed")
        else:
            golden = "# stamp " + want_stamp + "\n" + cs_live
            with open(GOLDEN, "w", encoding="utf-8", newline="") as fh:
                fh.write(golden)
            print("wrote " + GOLDEN)
    if golden is None:
        check(False, "committed C# output present", GOLDEN)
    else:
        head, _, body = golden.partition("\n")
        check(head == "# stamp " + want_stamp, "C# golden stamp is current",
              "golden %s, sources %s: rerun with --regen where dotnet runs" % (head[8:20], want_stamp[:12]))
        check(body == py_out, "C# golden is byte-identical to the Python twin",
              first_diff(body, py_out))
    if cs_live is not None:
        check(cs_live == py_out, "live C# output is byte-identical to the Python twin", first_diff(cs_live, py_out))
    elif exe is None:
        if "--require-cs" in argv:
            check(False, "live C# run", "no runnable dotnet.exe and --require-cs")
        else:
            print("SKIPPED live C# run: no runnable dotnet.exe here; the stamped golden binds the C# output")
    print("conds vectors: %d vectors, %s" % (len(vecs), "FAIL %d" % len(_fails) if _fails else "all checks passed"))
    return 1 if _fails else 0


def first_diff(a, b):
    al, bl = a.splitlines(), b.splitlines()
    for i, (x, y) in enumerate(zip(al, bl)):
        if x != y:
            j = next((k for k in range(min(len(x), len(y))) if x[k] != y[k]), min(len(x), len(y)))
            return "line %d (%s) at col %d: C# ...%s | py ...%s" % (i + 1, x.split("\t")[0], j, x[max(0, j - 30):j + 50],
                                                                   y[max(0, j - 30):j + 50])
    return "line counts %d vs %d" % (len(al), len(bl))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
