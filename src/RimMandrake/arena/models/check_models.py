#!/usr/bin/env python3
"""Run TLC on LiveHandoff.tla and check that every configuration gets the outcome it should.

The proof for ARENA_HANDOFF_PROVE_MODEL_FINDS_KNOWN_RACE (architecture_switch_harness_2026-10-29.md
section 6 step 11, section 7). A model is trusted only if it can fail, so this runs three kinds of case:

  unfixed     Unfixed.cfg: the goodbye restart as it was before the 2026-10-29 blind reviews.  TLC
              must report S5 violated by the known interleaving: Goodbye, a Send during the
              close-out, CloseOut, ... Relaunch.
  fixed       FixedSafety.cfg (S1-S6, L2Bound, two messages) and FixedLiveness.cfg (L1, L2, one
              message): no error.
  mutations   one guard removed per run (the spec's `Bugs` constant), each checked against ONLY the
              property that guard exists for.  Each must be violated, or that property has no teeth.

Usage:  check_models.py [--only CASE ...] [--list] [--workers N]
Exit 0 = every case got its expected outcome; 1 = some did not; 2 = TLC/Java is not installed
(UNMEASURED, not a pass or a fail).

Java and tla2tools.jar: $RM_TLA_JAVA / $RM_TLA_JAR, else <rm data root>/build/tla/{jre/bin/java,
dl/tla2tools.jar} (rmpaths -> agent_storage; D:\\ClaudeWork\\rimmandrake\\build\\tla on the desktop).
TLC's state directory goes to a local temp dir, never the D: drive: over drvfs the liveness check
ran ~60 s per 32k states and never finished; on the local disk the whole liveness case takes ~40 s.
Each case's TLC output is kept at <rm data root>/build/tla/runs/<case>/out.txt.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "LiveHandoff.tla"
sys.path.insert(0, str(HERE.parents[1] / "Utils"))

UNMEASURED = "UNMEASURED, not a pass or a fail"
# The seat's memory cgroup OOM-killed TLC at ~5.5 GB of heap (2026-10-29); stay well under it.
XMX = os.environ.get("RM_TLA_XMX", "3500m")

BASE = {"Msgs": "{m1}", "Bugs": "{}", "RC_DROPS_TO_DEAD": "FALSE", "MaxGoodbyes": "2",
        "MaxReloads": "3", "MaxCrashes": "1", "YieldBound": "2"}

# The known goodbye race, in order (other actions may sit between them).
KNOWN_RACE = ["Goodbye", "Send", "CloseOut", "Check", "KillOk", "Relaunch"]


def _cfg(*, bugs=(), invariants=(), properties=(), **consts) -> str:
    c = dict(BASE, **{k: str(v) for k, v in consts.items()})
    if bugs:
        c["Bugs"] = "{" + ", ".join(f'"{b}"' for b in bugs) + "}"
    lines = ["SPECIFICATION Spec", "CHECK_DEADLOCK FALSE", "CONSTANTS"]
    lines += [f"  {k} = {v}" for k, v in c.items()]
    if invariants:
        lines.append("INVARIANTS " + " ".join(invariants))
    if properties:
        lines.append("PROPERTIES " + " ".join(properties))
    return "\n".join(lines) + "\n"


# name -> (cfg text, expected).  expected: "ok", "invariant:<name>" or "temporal:<name>".
def cases() -> dict[str, tuple[str, str]]:
    out = {
        "unfixed": ((HERE / "Unfixed.cfg").read_text(), "invariant:S5"),
        "fixed_safety": ((HERE / "FixedSafety.cfg").read_text(), "ok"),
        "fixed_liveness": ((HERE / "FixedLiveness.cfg").read_text(), "ok"),
    }
    mut = {  # guard removed -> the property it exists for
        "relaunch_after_survive": "S1",   # wake a new window although the kill failed
        "verdict_stale": "S2",            # record a verdict without re-reading the loaded sha
        "deploy_live": "S3",              # deploy C# while the game process lives
        "silent_reload": "S4",            # reload with no logged rule
        "queue_in_memory": "S5",          # the pilot's queue dies with its context
        "switch_early": "S6",             # write `switch` before the old arm has stopped
        "ignore_owner": "L2Bound",        # keep testing after he comes home
        "closeout_skips_queue": "S5",     # A2 off: a message before the goodbye never gets its turn
    }
    for bug, inv in mut.items():
        out[f"mut_{bug}"] = (_cfg(bugs=[bug], invariants=[inv]), f"invariant:{inv}")
    # Remote Control delivering to a dead window: the owner's accepted risk, not a protocol bug.
    out["risk_rc_drops_to_dead"] = (_cfg(RC_DROPS_TO_DEAD="TRUE", invariants=["S5"]), "invariant:S5")
    out["mut_no_park"] = (_cfg(bugs=["no_park"], properties=["L1"]), "temporal:L1")
    out["mut_ignore_owner_L2"] = (_cfg(bugs=["ignore_owner"], properties=["L2"]), "temporal:L2")
    return out


def tools() -> tuple[Path, Path] | None:
    java = os.environ.get("RM_TLA_JAVA")
    jar = os.environ.get("RM_TLA_JAR")
    if not (java and jar):
        try:
            import rmpaths
            tla = rmpaths.rm_path("build", "tla")
        except Exception as e:  # no data root on this machine
            print(f"no rm data root ({e})", file=sys.stderr)
            return None
        java = java or str(tla / "jre" / "bin" / ("java.exe" if os.name == "nt" else "java"))
        jar = jar or str(tla / "dl" / "tla2tools.jar")
    java_p, jar_p = Path(java), Path(jar)
    if not (java_p.is_file() and jar_p.is_file()):
        print(f"missing {java_p if not java_p.is_file() else jar_p}", file=sys.stderr)
        return None
    return java_p, jar_p


def run_tlc(java: Path, jar: Path, cfg: str, logdir: Path, workers: int, timeout: int) -> str:
    logdir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="tlc_"))
    try:
        shutil.copy(SPEC, work / SPEC.name)
        (work / "run.cfg").write_text(cfg)
        cmd = [str(java), f"-Xmx{XMX}", "-XX:+UseParallelGC", "-cp", str(jar), "tlc2.TLC",
               "-workers", str(workers), "-noGenerateSpecTE", "-metadir", str(work / "st"),
               "-config", "run.cfg", SPEC.name]
        try:
            p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=timeout)
            text = p.stdout + p.stderr + f"\n[check_models] returncode={p.returncode}\n"
        except subprocess.TimeoutExpired as e:
            text = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
            text += f"\n[check_models] TIMEOUT after {timeout}s\n"
        (logdir / "out.txt").write_text(text)
        (logdir / "run.cfg").write_text(cfg)
        return text
    finally:
        shutil.rmtree(work, ignore_errors=True)


def outcome(text: str) -> str:
    """What TLC said: ok | invariant:<name> | temporal:<name> | broken:<why>."""
    if "[check_models] TIMEOUT" in text:
        return "broken:timeout"
    rc = re.search(r"^\[check_models\] returncode=(-?\d+)", text, re.M)
    rc = int(rc.group(1)) if rc else None
    got = _verdict(text)
    # TLC's own exit status must agree with its verdict line (0 clean, 12 safety, 13 liveness),
    # so a matching line followed by a crash, or a clean line from a killed run, is never accepted.
    want_rc = {"ok": 0, "invariant": 12, "temporal": 13}.get(got.split(":")[0])
    if want_rc is not None and rc != want_rc:
        return f"broken:{got} but exit {rc}"
    return got


def _verdict(text: str) -> str:
    m = re.search(r"^Error: Invariant (\w+) is violated", text, re.M)
    if m:
        return f"invariant:{m.group(1)}"
    m = re.search(r"^Error: Temporal property (\w+) was violated", text, re.M)
    if m:
        return f"temporal:{m.group(1)}"
    if "Model checking completed. No error has been found." in text:
        return "ok"
    m = re.search(r"^(Error:.*|.*(?:Semantic|Parse|Assumption).*error.*)$", text, re.M | re.I)
    return "broken:" + (m.group(1)[:80] if m else "no verdict line (killed? see out.txt)")


def trace_actions(text: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r"^State \d+: <(\w+)", text, re.M)]


def has_known_race(actions: list[str]) -> bool:
    it = iter(actions)
    return all(any(a == want for a in it) for want in KNOWN_RACE)


def stats(text: str) -> str:
    m = re.search(r"^(\d+) states generated, (\d+) distinct states found", text, re.M)
    return f"{int(m.group(2)):,} distinct" if m else ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", nargs="+", metavar="CASE")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--workers", type=int, default=max(1, min(10, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--timeout", type=int, default=480, help="seconds per case")
    a = ap.parse_args(argv)
    cs = cases()
    if a.list:
        for k, (_, exp) in cs.items():
            print(f"{k:28s} expect {exp}")
        return 0
    if a.only:
        bad = [k for k in a.only if k not in cs]
        if bad:
            ap.error(f"unknown case(s) {bad}; --list shows them")
        cs = {k: cs[k] for k in a.only}
    t = tools()
    if t is None:
        print(f"TLC not installed: {UNMEASURED}")
        return 2
    import rmpaths
    runs = Path(os.environ.get("RM_TLA_RUNS") or rmpaths.rm_path("build", "tla", "runs"))
    fails = 0
    for name, (cfg, expected) in cs.items():
        t0 = time.monotonic()
        text = run_tlc(*t, cfg, runs / name, a.workers, a.timeout)
        got = outcome(text)
        ok = got == expected
        extra = ""
        if name == "unfixed" and ok:
            acts = trace_actions(text)
            ok = has_known_race(acts)
            extra = " trace " + ">".join(acts[1:])
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name:26s} expect {expected:18s} got {got:18s} "
              f"{stats(text):>18s} {time.monotonic() - t0:5.0f}s{extra}", flush=True)
    print(f"{len(cs) - fails}/{len(cs)} cases as expected; logs under {runs}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
