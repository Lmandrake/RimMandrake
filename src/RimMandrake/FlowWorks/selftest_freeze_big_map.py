#!/usr/bin/env python3
"""LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP: offline proof that the 325-map staging->lay freeze is named by a profile, fixed
in the source, and that pipe_levelling_perf_proof completed on the 325 map. No game, no bridge, no dotnet.

  F1 the profile (in-tree copy of tprof_T3) names RM_MapComponent_Hoses:LayFrom with calls > 0 and a total over 10 s
  F2 the perf rows LEVEL_PERF_TICK_TIME and LEVEL_PERF_ALLOC read PASS and their LEVELPERF line has links=100 (all 100 rigs)
  F3 the evidence README ties both files to the 325 map
  F4 DrawAll asks for its lay with EnsureLay(r, true) and never lays itself: no LayFrom, LayAgain, PortLay,
     one-argument EnsureLay or EnsureLay(..., false) inside its body
  F5 EnsureLay hands a deferred ask to LayLater (when not FrameLegacy) BEFORE it can reach the synchronous LayAgain
  F6 LayLater lays only through the queue (layQueue.Ask) and never calls LayFrom, LayAgain or HoseMath.PortLay itself
  F7 the 250-tick recheck also asks deferred: EnsureLay(r, true) in TickRecheckBody
  F8 HoseLayQueue.cs exists, is compiled by the mod csproj, and its SelfTest suite is registered in Program.cs
  F9 the FlowWorks walk records the finding under this item id

Each check can fail: --root <dir> runs it against a copy (the mutants in the item's evidence README use it).
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ITEM = "LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP"
EV = "infrastructure/state/evidence/" + ITEM
HOSES = "src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs"
QUEUE = "src/RimMandrake/FlowWorks/Source/Hose/HoseLayQueue.cs"
CSPROJ = "src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj"
PROGRAM = "src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs"
WALK = "design/validation_walks/RimMandrake/FlowWorks.md"


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//[^\n]*", "", src)


def method_body(src, signature_re):
    """The brace-matched body of the first method whose header matches signature_re (comments already stripped)."""
    m = re.search(signature_re, src)
    if not m:
        return None
    i = src.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(src)):
        c = src[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return None


def run(root):
    rows = []

    def row(name, ok, detail):
        rows.append((name, bool(ok), detail))

    # F1
    prof = read(root, EV + "/tprof_T3.txt")
    m = re.search(r"RM_MapComponent_Hoses:LayFrom\s+calls=(\d+).*?totalMs=([\d.]+)", prof)
    row("F1", m and int(m.group(1)) > 0 and float(m.group(2)) > 10000.0,
        "LayFrom calls=%s totalMs=%s" % (m.group(1), m.group(2)) if m else "no LayFrom row in the profile")

    # F2
    perf = read(root, EV + "/perf_L0_timed.txt")
    for key in ("LEVEL_PERF_TICK_TIME", "LEVEL_PERF_ALLOC"):
        line = next((l for l in perf.splitlines() if l.split()[:1] == [key]), None)
        ok, detail = False, "row missing"
        if line:
            parts = line.split(None, 3)
            verdict = parts[1] if len(parts) > 1 else ""
            # the row's JSON payload is cut at 300 chars by the harness, so the LEVELPERF string is read, not parsed
            lm = re.search(r'"perf":\s*"LEVELPERF [^"]*?\blinks=(\d+)', parts[3]) if len(parts) > 3 else None
            links = int(lm.group(1)) if lm else None
            ok = verdict == "PASS" and links == 100
            detail = "verdict=%s links=%s" % (verdict, links)
        row("F2 " + key, ok, detail)

    # F3
    readme = read(root, EV + "/README.md")
    row("F3", "325 map" in readme and "tprof_T3.txt" in readme and "perf_L0_timed.txt" in readme,
        "README names the 325 map and both files")

    src = strip_comments(read(root, HOSES))

    # F4
    draw = method_body(src, r"\bvoid\s+DrawAll\s*\(\s*\)")
    if draw is None:
        row("F4", False, "DrawAll not found")
    else:
        asks = re.findall(r"\bEnsureLay\s*\(([^()]*)\)", draw)
        bad = [b for b in ("LayFrom", "LayAgain", "PortLay", "LayFromOn") if re.search(r"\b%s\s*\(" % b, draw)]
        nondeferred = [a for a in asks if a.replace(" ", "").split(",")[-1] != "true"]
        row("F4", asks and not nondeferred and not bad,
            "EnsureLay asks=%r nondeferred=%r direct lays=%r" % (asks, nondeferred, bad))

    # F5
    ens = method_body(src, r"\bHoseLay\s+EnsureLay\s*\(\s*CompHoseReel\s+\w+\s*,\s*bool\s+deferred\s*\)")
    if ens is None:
        row("F5", False, "EnsureLay(CompHoseReel, bool deferred) not found")
    else:
        dm = re.search(r"if\s*\(\s*deferred\s*&&\s*!\s*LegacyFrame\s*\)\s*return\s+LayLater\s*\(", ens)
        la = re.search(r"\bLayAgain\s*\(", ens)
        row("F5", dm and la and dm.start() < la.start(),
            "deferred->LayLater at %s, LayAgain at %s" % (dm.start() if dm else None, la.start() if la else None))

    # F6
    later = method_body(src, r"\bHoseLay\s+LayLater\s*\(")
    if later is None:
        row("F6", False, "LayLater not found")
    else:
        bad = [b for b in ("LayFrom", "LayAgain", "PortLay", "LayFromOn") if re.search(r"\b%s\s*\(" % b, later)]
        row("F6", re.search(r"\blayQueue\s*\.\s*Ask\s*\(", later) and not bad,
            "layQueue.Ask present=%s direct lays=%r" % (bool(re.search(r"layQueue\s*\.\s*Ask", later)), bad))

    # F7
    tick = method_body(src, r"\bvoid\s+TickRecheckBody\s*\(")
    asks = re.findall(r"\bEnsureLay\s*\(([^()]*)\)", tick or "")
    row("F7", tick is not None and asks and all(a.replace(" ", "").split(",")[-1] == "true" for a in asks),
        "TickRecheckBody EnsureLay asks=%r" % asks)

    # F8
    q_ok = os.path.isfile(os.path.join(root, QUEUE)) and re.search(r"\bclass\s+HoseLayQueue\b", strip_comments(read(root, QUEUE)))
    cs_ok = re.search(r'<Compile\s+Include="Hose\\HoseLayQueue\.cs"\s*/>', strip_xml_comments(read(root, CSPROJ)))
    pg_ok = re.search(r"\bHoseLayQueueChecks\s*\.\s*Run\s*\(", strip_comments(read(root, PROGRAM)))
    row("F8", q_ok and cs_ok and pg_ok, "queue class=%s compiled=%s selftest registered=%s" % (bool(q_ok), bool(cs_ok), bool(pg_ok)))

    # F9
    walk = read(root, WALK)
    row("F9", re.search(r"FOUND[^\n]*" + ITEM, walk), "FOUND line in the FlowWorks walk names the item")
    return rows


def strip_xml_comments(s):
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=REPO)
    a = ap.parse_args()
    rows = run(a.root)
    fails = 0
    for name, ok, detail in rows:
        print("%-28s %s  %s" % (name, "PASS" if ok else "FAIL", detail))
        fails += not ok
    print("%s: %d/%d PASS" % (ITEM, len(rows) - fails, len(rows)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
