#!/usr/bin/env python3
"""The barrage frame bar is the 99th-percentile frame inside the barrage-and-gas-chain window, at most 50 ms
(RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO; owner 2026-11-15 ~7:28 PM PST, "1 agree.", to the
99th-percentile-in-the-window proposal: the mod-off control's single worst frame broke 50 ms on random list stalls).

Feeds the PRODUCTION decider (KbFrameStats in Source/RM_KnockbackMath.cs, through Source/SelfTest --frame-fixtures) the
nine probe files visit 2 wrote (criterion_repairs/sc_barrage_perf_2026-11-15/probe_csv: selfcheck, mod off, mod on, three
runs) and four planted files made from a mod-on run, and checks it against this file's own reading of the same rows:
  W  the decider's window rows, p99 and verdict equal the Python reference on every file (nearest-rank p99 of the unpaused
     rows whose probe time, the running sum of ms, lies in 0.9-8.25 s)
  O  the three mod-on runs PASS (the agreed reading of the recorded runs); a FAIL here is a STOP, not a reason to loosen
  S  a planted sustained stall FAILS: 1.5 s of 75 ms frames, and 2 s of 55 ms frames, inside the window
  P  a planted single 200 ms stall inside the window PASSES, and is still the reported worst frame
  E  a probe that stopped before the window closed FAILS (it never saw the chain)
  T  the bar's text (tree.json barrage_frame_budget, scenes.json sc_barrage_perf) and the scene's code name the statistic
     and the window, and the old single-worst-frame wording is gone. The tree and sheet words may instead be HELD as
     criterion_repairs/sc_barrage_perf_2026-11-15/tree_sheet_rewording.patch (his coverage certificate is bound to the
     tree hash): then the patch must apply to today's tree and sheet, and the patched tree is what is checked

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_barrage_p99.py
"""
# selftest-timeout: 300
import csv
import json
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONCEPT = os.path.join(REPO, "design", "concepts", "ExplosiveKnockback")
PROBES = os.path.join(CONCEPT, "version", "criterion_repairs", "sc_barrage_perf_2026-11-15", "probe_csv")
sys.path.insert(0, HERE)
import selftest_explosiveknockback_kernel as kernel  # noqa: E402  (stages Source/ and runs dotnet)

LO, HI, BUDGET = 0.9, 8.25, 50.0
ON_RUNS = ["172152", "172345", "172520"]      # barrage_perf, mod on, visit-2 runs first / settled / third
OFF_RUNS = ["172127", "172320", "172455"]     # barrage_perf_off, the control
SELF_RUNS = ["172102", "172255", "172430"]    # frame_probe_selfcheck

fails = []


def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + " " + what)
    if not ok:
        fails.append(code + " " + what)


def read(path):
    with open(path) as f:
        return [(float(r["ms"]), r["paused"] == "1", int(r["in_air"])) for r in csv.DictReader(f)]


def write(path, rows):
    with open(path, "w", newline="\n") as f:
        f.write("row,ms,paused,in_air\n")
        for i, (ms, p, a) in enumerate(rows):
            f.write("%d,%s,%d,%d\n" % (i, ("%.3f" % ms).rstrip("0").rstrip("."), 1 if p else 0, a))


def reference(rows):
    """(windowRows, p99, worst, probeSeconds, verdict) by the bar's words, independent of the C#."""
    t, live = 0.0, []
    for ms, p, _ in rows:
        t += ms
        if LO * 1000 <= t <= HI * 1000 and not p:
            live.append(ms)
    live.sort()
    p99 = live[max(0, math.ceil(0.99 * len(live)) - 1)] if live else 0.0
    worst = max((ms for ms, p, _ in rows if not p), default=0.0)
    paused = sum(1 for _, p, _ in rows if p)
    ok = bool(rows) and len(rows) - paused >= 0.9 * len(rows) and t >= HI * 1000 and bool(live) and p99 <= BUDGET
    return len(live), p99, worst, t / 1000.0, ok


def plant(rows, at_s, frame_ms, seconds):
    """Replace the frames from at_s with a stall of `seconds` of frame_ms frames (the window keeps its real length)."""
    t, out, i = 0.0, [], 0
    while i < len(rows) and t + rows[i][0] <= at_s * 1000:
        out.append(rows[i])
        t += rows[i][0]
        i += 1
    n = int(round(seconds * 1000 / frame_ms))
    out += [(frame_ms, False, rows[min(i, len(rows) - 1)][2])] * n
    skipped = 0.0
    while i < len(rows) and skipped < seconds * 1000:
        skipped += rows[i][0]
        i += 1
    return out + rows[i:]


def main():
    stage = os.path.join(kernel.STAGE, "frame_fixtures")
    if not os.path.isdir(os.path.dirname(kernel.STAGE)):
        print("UNMEASURED: no D: staging root on this machine")
        return 1
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    files = {}
    for stamp in SELF_RUNS + OFF_RUNS + ON_RUNS:
        name = "RM_FrameProbe_20261115T%s.csv" % stamp
        shutil.copy2(os.path.join(PROBES, name), os.path.join(stage, name))
        files[name] = read(os.path.join(PROBES, name))
    on = read(os.path.join(PROBES, "RM_FrameProbe_20261115T%s.csv" % ON_RUNS[1]))
    planted = {
        "planted_sustained_75ms_1.5s.csv": plant(on, 3.0, 75.0, 1.5),
        "planted_sustained_55ms_2s.csv": plant(on, 4.0, 55.0, 2.0),
        "planted_single_200ms.csv": plant(on, 5.0, 200.0, 0.2),
        "planted_stopped_at_6s.csv": [r for r, t in zip(on, _cum(on)) if t <= 6000.0],
    }
    for name, rows in planted.items():
        write(os.path.join(stage, name), rows)
        files[name] = rows

    rc, out = kernel.main(extra=["--frame-fixtures", kernel.win(stage)])
    got = {}
    for line in out.splitlines():
        m = re.match(r"FIXTURE (\S+) windowRows=(\d+) p99=([\d.]+) worst=([\d.]+) probeS=([\d.]+) verdict=(PASS|FAIL)(.*)", line)
        if m:
            got[m.group(1)] = (int(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), m.group(6) == "PASS", m.group(7))
    check("W0", len(got) == len(files), "the decider read every fixture (%d of %d; dotnet exit %s)" % (len(got), len(files), rc))
    print("file                                   windowRows  p99(ms)  worst(ms)  verdict")
    for name, rows in files.items():
        n, p99, worst, secs, ok = reference(rows)
        print("%-38s %10d %8.1f %10.1f  %s" % (name, n, p99, worst, "PASS" if ok else "FAIL"))
        g = got.get(name)
        check("W", g is not None and g[0] == n and abs(g[1] - p99) < 0.05 and abs(g[2] - worst) < 0.05 and g[4] == ok,
              "%s decider %s equals reference (%d, %.1f, %.1f, %s)" % (name, g and g[:5], n, p99, worst, ok))
    for stamp in ON_RUNS:
        g = got.get("RM_FrameProbe_20261115T%s.csv" % stamp)
        check("O", bool(g and g[4]), "mod-on run %s passes the p99-in-window bar (p99 %s ms)" % (stamp, g and g[1]))
    for name in ("planted_sustained_75ms_1.5s.csv", "planted_sustained_55ms_2s.csv"):
        g = got.get(name)
        check("S", bool(g and not g[4]), "%s fails (p99 %s ms; %s)" % (name, g and g[1], g and g[5].strip()))
    g = got.get("planted_single_200ms.csv")
    check("P", bool(g and g[4] and g[2] >= 199.9), "one 200 ms stall in the window passes and is the reported worst (%s)" % (g and g[:5],))
    g = got.get("planted_stopped_at_6s.csv")
    check("E", bool(g and not g[4] and "before the window closed" in g[5]), "a probe stopped at 6 s fails (%s)" % (g and g[5].strip(),))

    tree = json.load(open(os.path.join(CONCEPT, "tree.json")))
    held = "today's tree"
    if "99th-percentile" not in json.dumps(_leaf(tree)):
        tree, held = _patched_tree()
    node = _leaf(tree) or {"experience": ""}
    scene = next(s for s in json.load(open(os.path.join(CONCEPT, "scenes.json")))["scenes"] if s["id"] == "sc_barrage_perf")
    stat = re.compile(r"99th-percentile frame .*0\.9.8\.25 s.*at most 50 ms", re.S)
    check("T1", bool(stat.search(node["experience"])), "tree.json barrage_frame_budget experience (%s) names the p99, the window and 50 ms" % held)
    check("T2", bool(stat.search(scene["expect"])), "scenes.json sc_barrage_perf expect names the p99, the window and 50 ms")
    check("T3", "99th-percentile" in scene["control"]["expect"], "the control reports its own p99 in the same window")
    old = re.compile(r"worst frame across both events|read the worst frame\.|one frame stalls")
    check("T4", "NOT" not in held and not old.search(json.dumps(node) + json.dumps(scene)),
          "the single-worst-frame wording is gone from the bar and the scene (%s)" % held)
    src = open(os.path.join(HERE, "Source", "RM_KnockbackProof_StageThree.cs")).read()
    check("T5", "BarrageWindowLoS = 0.9f" in src and "BarrageWindowHiS = 8.25f" in src
          and "RM_FrameProbe.Stop(BarrageWindowLoS, BarrageWindowHiS)" in src, "BarragePerf stops the probe with the 0.9-8.25 s window")
    print("%d failed" % len(fails) if fails else "ALL PASS")
    return 1 if fails else 0


def _leaf(tree):
    return next((n for n in tree.get("leaves", []) if isinstance(n, dict) and n.get("id") == "barrage_frame_budget"), {})


def _patched_tree():
    """Today's tree.json and sheet.md with the held rewording patch applied, in a scratch folder (git apply outside a repo)."""
    import subprocess
    import tempfile
    patch = os.path.join(PROBES, "..", "tree_sheet_rewording.patch")
    with tempfile.TemporaryDirectory() as tmp:
        rel = os.path.join("design", "concepts", "ExplosiveKnockback")
        os.makedirs(os.path.join(tmp, rel))
        for f in ("tree.json", "sheet.md"):
            shutil.copy2(os.path.join(CONCEPT, f), os.path.join(tmp, rel, f))
        r = subprocess.run(["git", "apply", os.path.abspath(patch)], cwd=tmp, capture_output=True, text=True)
        if r.returncode != 0:
            return {}, "held patch does NOT apply: " + (r.stderr or "").strip()[:200]
        sheet = open(os.path.join(tmp, rel, "sheet.md")).read()
        ok = "99th-percentile frame inside the barrage-and-chain window" in sheet and "no frame over 50 ms" not in sheet
        return json.load(open(os.path.join(tmp, rel, "tree.json"))), "held patch applied%s" % ("" if ok else ", sheet line NOT reworded")


def _cum(rows):
    t, out = 0.0, []
    for ms, _, _ in rows:
        t += ms
        out.append(t)
    return out


if __name__ == "__main__":
    sys.exit(main())
