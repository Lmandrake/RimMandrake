"""Live proof of SHADE_LESSONS_BUILD_WATCH_THE_HERD_CROSS criterion A7: on a Long Shade quicktest map, a colonist studies
dewfringe and a herd crossing is counted.

    python3 src/RimMandrake/EnvironmentalHazards/prove_shade_lessons.py --offline
    python.exe "$(wslpath -w src/RimMandrake/EnvironmentalHazards/prove_shade_lessons.py)" --clause A7 < /dev/null

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game or bridge, probe not in the loaded DLL, staging refused).

Scene: an RM_LongShade map (tile 114480, size 150, the LongShade proofs' tile) -> Toggle true -> Stage (a studier sent
to the nearest RM_Dewfringe; a drafted watcher; a wild Hare sent on RM_ShadeDash to a landing cell 4-7 cells from the
watcher, in its line of sight) -> run 2500 ticks -> Read -> Cleanup, toggle put back, map dropped.
  A7 holds when: the colony's RM_ShadeIdea_DewOff points rose (a study interaction on dewfringe credited the idea), the
     staged hare's own crossing reached its landing cell (the probe's CrossingLanded listener saw it), the colony's
     RM_ShadeIdea_PortableShade points rose by at least 1, and the gate read on.
Probe: RimMandrake.EnvironmentalHazards.RM_ShadeLessonsProof (Source/RM_ShadeLessonsProof.cs) through jawa/static_call.
--offline: the probe is compiled into the csproj, every method the driver calls exists, and judge() passes a good record
and fails each broken one.
"""
from __future__ import annotations

import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PROBE = "RimMandrake.EnvironmentalHazards.RM_ShadeLessonsProof"
TILE, SIZE = 114480, 150
RUN_TICKS = 2500
METHODS = ("Toggle", "Stage", "Read", "Cleanup")


def kv(line):
    return dict(m.groups() for m in re.finditer(r"(\w+)=(\S+)", line or ""))


def _f(d, k):
    try:
        return float(d.get(k))
    except (TypeError, ValueError):
        return float("nan")


def judge(rec):
    if not str(rec.get("stage", "")).startswith("STAGED"):
        return False, "staging did not run: %s" % rec.get("stage")
    r = kv(rec.get("read", ""))
    dew0, dew, ps0, ps = _f(r, "dew0"), _f(r, "dew"), _f(r, "ps0"), _f(r, "ps")
    why = "dew %s->%s, portable shade %s->%s, hare crossings %s, gate %s" % (dew0, dew, ps0, ps, r.get("hareEvents"), r.get("gate"))
    if r.get("gate") != "True":
        return False, "gate off: " + why
    if not dew > dew0:
        return False, "no dewfringe study credited: " + why
    if not int(r.get("hareEvents", "0")) >= 1:
        return False, "the staged crossing never landed: " + why
    if not ps - ps0 >= 1:
        return False, "the crossing was not counted: " + why
    return True, why


def offline():
    fails = []
    src = open(os.path.join(HERE, "Source", "RM_ShadeLessonsProof.cs"), encoding="utf-8").read()
    proj = open(os.path.join(HERE, "Source", "RM_EnvironmentalHazards.csproj"), encoding="utf-8").read()
    if '<Compile Include="RM_ShadeLessonsProof.cs" />' not in proj:
        fails.append("probe not in the csproj")
    for m in METHODS:
        if not re.search(r"public static string %s\(string" % m, src):
            fails.append("probe lacks %s(string)" % m)
    good = {"stage": "STAGED plant=1,1", "read": "READ dew0=0 dew=0.87 ps0=0 ps=1 hareEvents=1 events=1 hareAt=True gate=True"}
    if not judge(good)[0]:
        fails.append("judge fails a good record")
    for broken in ("dew=0", "ps=0", "hareEvents=0", "gate=False"):
        k = broken.split("=")[0]
        bad = dict(good, read=re.sub(r"\b%s=\S+" % k, broken, good["read"]))
        if judge(bad)[0]:
            fails.append("judge passes a record with %s" % broken)
    if judge(dict(good, stage="REFUSED: x"))[0]:
        fails.append("judge passes a refused staging")
    for f in fails:
        print("FAIL " + f)
    print("RESULT %s" % ("PASS" if not fails else "FAIL"))
    return 1 if fails else 0


def _scene():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    from scenes import scenelib as S  # noqa: E402
    from await_lifecycle import await_lifecycle  # noqa: E402

    def static(method, arg=""):
        r = S.call("jawa/static_call", type=PROBE, method=method, args=arg)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else str(r)

    lc = await_lifecycle(S.call, "map_ready", deadline_s=400, start=True)
    if not lc.ok:
        return {"started": time.time(), "unmeasured": "no playing map: " + lc.reason}
    rec = {"started": time.time()}
    probe = static("Toggle", "probe")
    if not probe.startswith("REFUSED: want"):
        rec["unmeasured"] = "probe RM_ShadeLessonsProof absent (new EnvironmentalHazards DLL not loaded): " + probe
        return rec
    back = (S.call("jawa/map_info") or {}).get("mapIndex", 0)
    was = kv(static("Toggle", "true")).get("was")
    mid = None
    try:
        mid = S.biome_map(TILE, "RM_LongShade", size=SIZE)
        S.run(300)
        rec["stage"] = static("Stage")
        if not rec["stage"].startswith("STAGED"):
            rec["unmeasured"] = "staging refused: " + rec["stage"]
            return rec
        S.run(RUN_TICKS)
        rec["read"] = static("Read")
        rec["cleanup"] = static("Cleanup")
    finally:
        if was in ("True", "False"):
            static("Toggle", was.lower())
        if mid is not None:
            S.drop_map(mid, TILE, back)
    return rec


def live(clause):
    try:
        rec = _scene()
    except Exception as ex:   # no bridge, no game
        print("UNMEASURED: %r" % (ex,))
        return 2
    print("record: %r" % (rec,))
    if rec.get("unmeasured"):
        print("UNMEASURED: " + rec["unmeasured"])
        return 2
    ok, why = judge(rec)
    print("%s %s: %s" % ("PASS" if ok else "FAIL", clause, why))
    return 0 if ok else 1


def main(argv):
    if "--offline" in argv:
        return offline()
    if "--clause" in argv and argv[argv.index("--clause") + 1:argv.index("--clause") + 2] == ["A7"]:
        return live("A7")
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
