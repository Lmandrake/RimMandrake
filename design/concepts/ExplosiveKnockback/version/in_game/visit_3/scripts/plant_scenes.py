#!/usr/bin/env python3
"""Run blind cycle 2's PF_SCENE_* plants one by one on ArchBig (release build), each in script mode (a planted reading
counts for no bar), and write one row per plant to visit_3/planted_scene_rows.jsonl.

    python.exe design\\concepts\\ExplosiveKnockback\\version\\in_game\\visit_3\\scripts\\plant_scenes.py [--only ID,..]

Per plant: the file must hold `old` exactly once; it is replaced by `new`, the scene runs through
scene.LAUNCH["game"] = "ArchBig" (scene.py accept refuses a changed tree), and the file is restored in a
finally block and on SIGTERM/SIGINT. Two lines are read, because `scene.py accept` decides from the first only: the
scene's own last verdict line with the exit code (the deciding line) and the library judge's Verdict(outcome=...) line
(advisory, counts_for_bar False; it decides only a script that prints no line of its own, such as scene_storeroom_pit.py). outcome: SEEN when the deciding line is not PASS or the script crashed with no verdict;
SEEN BY JUDGE ONLY when the deciding line reads PASS and the judge's does not read SUCCESS; NOT SEEN when both pass;
COULD NOT LOOK when scene.open refused (WRONG_BUILD and the like) or the run timed out: the plant was never exercised.
A plant that changes only a comment is not run: it is an equivalent mutant, and no test can see it.
    --reread rewrites planted_scene_rows.jsonl from the evidence files of the plants it already holds (no game)."""
import argparse, datetime, json, os, re, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
VISIT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(VISIT, *[".."] * 6))
FAULTS = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_2/lane2/planted_faults.json")
SAVED = {}

RUNNER = r'''
import os, runpy, sys
repo = %r
sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "Utils"))
import scene
scene.LAUNCH["game"] = "ArchBig"
script = sys.argv[1]
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
sys.argv = [script]
runpy.run_path(script, run_name="__main__")
'''


def restore():
    for p, b in list(SAVED.items()):
        open(p, "wb").write(b)
        SAVED.pop(p, None)


def on_sig(sig, _):
    restore()
    sys.exit(128 + sig)


def code_part(line):
    return line.split("#", 1)[0].rstrip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--timeout", type=int, default=1500, help="hang guard: the slowest real run of these scenes took 147 s")
    ap.add_argument("--reread", action="store_true")
    a = ap.parse_args()
    if a.reread:
        return reread()
    signal.signal(signal.SIGTERM, on_sig)
    signal.signal(signal.SIGINT, on_sig)
    plants = [p for p in json.load(open(FAULTS, encoding="utf-8")) if p["id"].startswith("PF_SCENE_")]
    if a.only:
        plants = [p for p in plants if p["id"] in a.only.split(",")]
    runner = RUNNER % REPO
    out_rows = os.path.join(VISIT, "planted_scene_rows.jsonl")
    try:
        for p in plants:
            path = os.path.join(REPO, p["file"])
            text = open(path, encoding="utf-8").read()
            row = {"plant": p["id"], "file": p["file"], "old": p["old"], "new": p["new"], "bars": p.get("bars"),
                   "game": "archmagi (ArchBig)", "build": "release DLL of source 5e43516ec8", "counts_for_bar": False,
                   "at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S PST")}
            if text.count(p["old"]) != 1:
                row.update(seen=None, outcome="COULD NOT LOOK", why="the file holds `old` %d times, not once" % text.count(p["old"]))
            elif code_part(p["old"]) == code_part(p["new"]):
                row.update(seen=False, outcome="NOT RUN", why="equivalent mutant: the plant changes only a comment, so no test can see it")
            else:
                SAVED[path] = open(path, "rb").read()
                open(path, "w", encoding="utf-8").write(text.replace(p["old"], p["new"]))
                t0 = time.time()
                try:
                    r = subprocess.run([sys.executable, "-c", runner, path], cwd=REPO, capture_output=True, text=True, timeout=a.timeout)
                    rc, out = r.returncode, r.stdout + "\n--- stderr ---\n" + r.stderr[-4000:]
                except subprocess.TimeoutExpired as e:
                    rc, out = -9, "TIMEOUT after %d s\n%s" % (a.timeout, (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""))
                finally:
                    restore()
                ev = os.path.join(VISIT, "evidence", "plant_%s.txt" % p["id"])
                open(ev, "w", encoding="utf-8").write(out.replace("\r", ""))
                row.update(rc=rc, wall_s=round(time.time() - t0, 1), evidence=os.path.relpath(ev, REPO).replace("\\", "/"))
                row.update(read_out(out, rc))
            with open(out_rows, "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
            print("%-46s %-20s %s | judge %s" % (p["id"], row["outcome"], row.get("verdict_line"), row.get("judge")), flush=True)
    finally:
        restore()


def read_out(out, rc):
    """-> the reading fields of one plant run's output (see the module doc)."""
    vs = re.findall(r"^(PASS|FAIL|UNMEASURED|INVALID)\s+sc_\S+", out, re.M)
    last = vs[-1] if vs else None
    j = re.findall(r"^Verdict\(outcome='([A-Z ]+)'", out, re.M)
    judge = j[-1] if j else None
    refused = re.search(r"^\S*Refused: ([A-Z_]+)", out, re.M)
    if rc == -9 or (refused and last is None):
        o = "COULD NOT LOOK"
    elif (last is not None and last != "PASS") or (last is None and rc != 0) or (last is None and judge not in (None, "SUCCESS")):
        o = "SEEN"
    elif judge is not None and judge != "SUCCESS":
        o = "SEEN BY JUDGE ONLY"
    else:
        o = "NOT SEEN"
    return {"verdict_line": last, "judge": judge, "refused": refused.group(1) if refused else None,
            "seen": {"COULD NOT LOOK": None, "SEEN": True}.get(o, False), "outcome": o}


def reread():
    path = os.path.join(VISIT, "planted_scene_rows.jsonl")
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    for r in rows:
        if r.get("evidence"):
            r.update(read_out(open(os.path.join(REPO, r["evidence"]), encoding="utf-8").read(), r.get("rc", 0)))
    open(path, "w", encoding="utf-8").write("".join(json.dumps(r) + "\n" for r in rows))
    for r in rows:
        print("%-46s %-20s %s | judge %s" % (r["plant"], r["outcome"], r.get("verdict_line"), r.get("judge")))


if __name__ == "__main__":
    main()
