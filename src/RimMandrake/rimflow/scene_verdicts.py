#!/usr/bin/env python3
"""scene_verdicts.py -- the scene verdict ledger: the runs of one claim on one build -> the scene's verdict. A receipt is
not a verdict (Bridge v2 decision 12, design/specs/2026-11-23-bridge-v2/05_build_design.md).

One append-only file per mod version, design/concepts/<Mod>/version/scene_runs.jsonl. A `run` line is one run of a
scene, copied from its receipt; a `class` line classes or re-judges a run that is already there. Nothing is overwritten.
The rules of kinds A, B and C are live_kinds.py's (the Stage 6 exit's reader): this module decides which runs are
samples that may count for a bar, and hands only those to live_kinds.reading.

Page: design/specs/2026-11-23-scene-verdicts/boundary.md. Tests: selftest_scene_verdicts.py.

    python3 scene_verdicts.py show <Mod> <scene> [--claim H] [--build SHA]   one summary; exit code names its state
    python3 scene_verdicts.py add <Mod> '<run line as JSON>'
    python3 scene_verdicts.py class <Mod> <run> --outcome W --why "..." --by UNIT [--rejudged] [--spoiled-by "..."]"""
import argparse
import datetime
import fcntl
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import live_kinds as LK  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FILE = "version/scene_runs.jsonl"
IDENTITY = ("run", "scene", "claim", "build", "outcome", "receipt")     # a line without these is refused at add
REFERENCE = "reference"         # the arm (speed 1, camera on the station) that needs no comparison
ACCEPTED_MAPS = ("settlement",)  # the map kinds a bar accepts when its test names none (05_build_design.md: by default)
HUNT_PARTS = ("what", "why_it_matters", "next_step", "cost")    # hunt_open.py's FIELDS (standing_rulings.md §Live tests, 5)
# the four answers a summary gives besides a verdict; each has its own exit code
READ, ZERO, NONE, NO_LOOK, FAILED = "READ", "ZERO", "NONE", "COULD NOT LOOK", "FAILED"
EXIT = {READ: 0, ZERO: 3, NONE: 4, NO_LOOK: 5, FAILED: 6}
# a cluster of side-by-side copies is one sample; its word is the first of these that any copy reads
CLUSTER_ORDER = (LK.MOD_FAILURE, LK.UNRESOLVED, LK.REFUSED, LK.SUCCESS, LK.RANDOM_MISS, LK.ENVIRONMENT, LK.APPARATUS,
                 LK.NO_LOOK)


class Refused(Exception):
    """A line that cannot be written; the text names the repair."""


class Unreadable(Exception):
    """The ledger is there and cannot be read: no verdict can be known from it."""


def path(root, mod):
    return os.path.join(root, "design", "concepts", mod, FILE)


def read(root, mod):
    """-> (lines, there). there False: no ledger file (looked, none). Raises Unreadable for a file that is there and bad."""
    p = path(root, mod)
    if not os.path.exists(p):
        return [], False
    out = []
    try:
        with open(p, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if line.strip():
                    v = json.loads(line)
                    if not isinstance(v, dict):
                        raise ValueError("line %d is not an object" % i)
                    out.append(v)
    except (OSError, ValueError) as e:
        raise Unreadable("%s: %s" % (p, e)) from e
    return out, True


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(root, mod, line):
    p = path(root, mod)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(line, sort_keys=True) + "\n")
    return line


def check_run(line, have=()):
    """-> [why the run line cannot be written]; [] when it can. have: the run ids already in the ledger."""
    if not isinstance(line, dict):
        return ["a run line is a JSON object"]
    out = ["it lacks %s (the run's identity, from its receipt)" % k for k in IDENTITY
           if not isinstance(line.get(k), str) or not line[k].strip()]
    if LK.norm(line.get("outcome")) not in LK.OUTCOMES:
        out.append("its outcome %r is none of the seven (%s)" % (line.get("outcome"), ", ".join(LK.OUTCOMES)))
    if line.get("run") in have:
        out.append("run %s is already in the ledger: class or re-judge it with a class line, never a second run line"
                   % line.get("run"))
    if line.get("replay_of") is not None and line.get("replay_of") not in have:
        out.append("replay_of %r names no run in the ledger" % line.get("replay_of"))
    return out


def add_run(root, mod, line):
    lines, _ = read(root, mod)
    have = {x.get("run") for x in lines if x.get("rec") == "run"}
    line = dict(line, rec="run", outcome=LK.norm((line or {}).get("outcome")) if isinstance(line, dict) else None)
    bad = check_run(line, have)
    if bad:
        raise Refused("; ".join(bad))
    return _append(root, mod, dict(line, at=line.get("at") or _now()))


def add_class(root, mod, run, outcome, why, by, rejudged=False, spoiled_by=None):
    """Class an UNRESOLVED run, or record a re-judgement of any run. The run line and every earlier class stay."""
    lines, _ = read(root, mod)
    if run not in {x.get("run") for x in lines if x.get("rec") == "run"}:
        raise Refused("run %s is not in %s: add its run line first" % (run, FILE))
    word = LK.norm(outcome)
    bad = []
    if word not in LK.OUTCOMES:
        bad.append("outcome %r is none of the seven" % outcome)
    if len(str(why or "").split()) < LK.WHY_WORDS:
        bad.append("the why needs %d words at least: the evidence that classes the run" % LK.WHY_WORDS)
    if not str(by or "").strip():
        bad.append("--by names the unit that classes it")
    if bad:
        raise Refused("; ".join(bad))
    line = {"rec": "class", "run": run, "outcome": word, "why": " ".join(str(why).split()), "by": by,
            "how": "rejudged" if rejudged else "classed", "at": _now()}
    if spoiled_by:
        line["spoiled_by"] = spoiled_by
    return _append(root, mod, line)


def bar_refusal(line, spec=None):
    """-> None when the run may count for a bar, else why it counts for nothing (it reads TUNED when the receipt is
    stamped or tainted). A mark that the receipt does not establish counts for nothing: unknown is never clean."""
    ov = line.get("overlay")
    if not isinstance(ov, str) or not ov.strip():
        return "NOT COUNTED: the receipt does not establish its overlay stamp"
    if ov.strip().lower() != "none":
        return "TUNED: overlay stamp %s" % ov
    if line.get("tainted") is not False:
        return "TUNED: taint mark %s (an overlay was written in this process before the run)" % (
            "set" if line.get("tainted") is True else "not established")
    arm = line.get("arm")
    if not isinstance(arm, str) or not arm.strip():
        return "NOT COUNTED: the receipt does not name its arm"
    if arm != REFERENCE and line.get("compared") is not True:
        return "NOT COUNTED: arm %s, not compared with the reference" % arm
    if str(line.get("build_kind") or "").upper() != "RELEASE":
        return "NOT COUNTED: %s build" % (line.get("build_kind") or "an unnamed")
    maps = (spec or {}).get("map_kinds")
    maps = ACCEPTED_MAPS if maps is None else maps if isinstance(maps, (list, tuple)) else ()
    if line.get("map_kind") not in maps:
        return "NOT COUNTED: map kind %s, the bar accepts %s" % (line.get("map_kind"), ", ".join(maps))
    return None


def history(lines):
    """-> {run id: {"line": the run line, "outcomes": [{outcome, how, by, why, at}], "now": the latest outcome}}."""
    out = {}
    for x in lines:
        if x.get("rec") == "run" and x.get("run") not in out:
            out[x["run"]] = {"line": x, "now": LK.norm(x.get("outcome")),
                             "outcomes": [{"outcome": LK.norm(x.get("outcome")), "how": "judged", "at": x.get("at")}]}
        elif x.get("rec") == "class" and x.get("run") in out:
            h = out[x["run"]]
            h["outcomes"].append({k: x.get(k) for k in ("outcome", "how", "by", "why", "at", "spoiled_by")})
            h["now"] = LK.norm(x.get("outcome"))
            if x.get("spoiled_by"):
                h["spoiled_by"] = x["spoiled_by"]
    return out


def _row(h, scene, build, word=None):
    """-> the live_kinds row of one run (or of a cluster, with its folded word)."""
    line = h["line"]
    word = word or h["now"]
    return {"test": scene, "outcome": word, "verdict": "PASS" if word == LK.SUCCESS else "FAIL", "mod_sha": build,
            "spoiled_by": h.get("spoiled_by") or line.get("spoiled_by"), "forbidden": line.get("forbidden"),
            "run": line["run"]}


def _fold(members, scene, build, spec):
    """-> the live_kinds row of a cluster: each copy is read as live_kinds reads it (a forbidden effect is a MOD FAILURE,
    an ENVIRONMENT FAULT without its record is UNRESOLVED), and the cluster takes the first word of CLUSTER_ORDER."""
    read = [(LK.outcome(_row(m, scene, build), spec)[0], m) for m in members]
    words = [w for w, _ in read]
    word = next(w for w in CLUSTER_ORDER + tuple(words) if w in words)
    h = next(m for w, m in read if w == word)
    return dict(_row(h, scene, build, word), forbidden=None)


def hunts(runs):
    """-> [notice]: a hunt opens on an UNRESOLVED run that is serious (one sighting is enough) or whose symptom is seen
    again. A notice names the four parts the policy asks (a part the run did not write is named missing) and the
    hunt_open.py command that tells the Conductor; this module writes no log and no note."""
    open_ = [h for h in runs if h["now"] == LK.UNRESOLVED]
    seen = {}
    for h in open_:
        s = str(h["line"].get("symptom") or "").strip()
        if s:
            seen.setdefault(s, []).append(h)
    out = []
    for h in open_:
        line, s = h["line"], str(h["line"].get("symptom") or "").strip()
        again = len(seen.get(s, ())) >= 2
        if line.get("serious") is not True and not again:
            continue
        if again and seen[s][0] is not h and line.get("serious") is not True:
            continue        # one notice for a symptom seen again, on its first run
        parts = line.get("hunt") if isinstance(line.get("hunt"), dict) else {}
        n = {"run": line["run"], "scene": line.get("scene"), "opened": "serious" if line.get("serious") is True else
             "seen again (%d runs, symptom: %s)" % (len(seen[s]), s)}
        n.update({k: parts.get(k) for k in HUNT_PARTS})
        n["missing"] = [k for k in HUNT_PARTS if not str(parts.get(k) or "").strip()]
        n["text"] = "FOR THE CONDUCTOR: a hunt opens on scene %s, run %s (%s). %s" % (
            line.get("scene"), line["run"], n["opened"], " ".join("%s: %s." % (k.replace("_", " "), parts.get(k) or
                                                                               "MISSING, the run's writer owes it")
                                                                   for k in HUNT_PARTS))
        n["command"] = ["python3", "src/RimMandrake/rimflow/hunt_open.py", "<the mod's item>"] + [
            a for k in HUNT_PARTS for a in ("--" + k.replace("_", "-"), str(parts.get(k) or ""))]
        out.append(n)
    return out


def summary(spec, lines, scene, claim=None, build=None, relation=None):
    """The scene's verdict from the ledger's lines. claim, build None: the scene's latest run's. relation(scene, old
    build, new build) -> True when the change does not touch what the scene reads, False when it does, None unknown: a
    run on an earlier build counts only on True. -> {state, verdict, why, runs, counted, hunts, claim, build}."""
    spec = spec or {}
    hist = history(lines)
    mine = [h for h in hist.values() if h["line"].get("scene") == scene]
    out = {"scene": scene, "state": NONE, "verdict": None, "why": [], "runs": [], "counted": 0, "hunts": hunts(mine),
           "claim": claim, "build": build}
    if not mine:
        out["why"].append("no run of scene %s is in the ledger" % scene)
        return out
    claim = out["claim"] = claim or mine[-1]["line"].get("claim")
    build = out["build"] = build or mine[-1]["line"].get("build")
    if LK.kind(spec) not in ("A", "B", "C") or LK.tag_flaws(spec):
        out.update(state=FAILED, why=["the scene's tag cannot be used: %s" % "; ".join(LK.tag_flaws(spec))])
        return out
    pool, clusters = [], {}
    first = {}      # receipt hash -> the run that first named it, over the whole file: a receipt is one sample
    for h in hist.values():
        first.setdefault(h["line"].get("receipt"), h["line"]["run"])
    for h in mine:
        line = h["line"]
        row = {"run": line["run"], "build": line.get("build"), "outcomes": h["outcomes"], "now": h["now"]}
        out["runs"].append(row)
        seen = first.get(line.get("receipt")) != line["run"]    # whatever scene or claim the first line named
        if line.get("claim") != claim:
            row["reads"] = "OTHER CLAIM %s" % line.get("claim")
            continue
        if line.get("replay_of") is not None or seen:
            row["reads"] = "REPLAY of %s: not a sample" % (line.get("replay_of") or "receipt " + line["receipt"])
            continue
        refusal = bar_refusal(line, spec)
        if refusal:
            row["reads"] = refusal
            continue
        if line.get("build") != build:
            rel = relation(scene, line.get("build"), build) if relation else None
            if rel is not True:
                row["reads"] = "OTHER BUILD %s: the change to %s %s" % (line.get("build"), build, "touches what the "
                                                                        "scene reads" if rel is False else
                                                                        "has no readable relation to the scene")
                continue
        row["reads"] = h["now"]
        c = line.get("cluster")
        if c is not None:
            if c in clusters:
                clusters[c].append(h)
                row["reads"] = "%s (in cluster %s, one sample)" % (h["now"], c)
                continue
            clusters[c] = [h]
        pool.append((c, h))
    if not pool:
        out.update(state=ZERO, why=["%d run(s) of scene %s, none counts for a bar on claim %s, build %s" % (
            len(mine), scene, claim, build)])
        return out
    rows = [(1, _fold(clusters[c], scene, build, spec) if c is not None else _row(h, scene, build)) for c, h in pool]
    out["counted"] = len(rows)
    out["state"] = READ
    if LK.kind(spec) == "C":
        out.update(verdict="HUNT", why=["kind C: a hunt is never part of the acceptance tests, so it counts for no bar"])
        return out
    k = LK.reading(spec, rows)
    out["why"] = list(k["why"])
    words = [LK.outcome(r, spec)[0] for _, r in rows]      # as live_kinds reads each: a forbidden effect is MOD FAILURE
    if LK.MOD_FAILURE in words or k["mod"]:
        out["verdict"] = "FAIL"
        out["why"].append("a run of this claim and build is a MOD FAILURE")
    elif k["count"] == "unresolved":
        out["verdict"] = "HELD"
    elif k["count"] in ("refused", "tag"):
        out.update(state=FAILED, verdict=None)
    elif k["count"] == "inconclusive":
        out["verdict"] = "SHORT" if k["short"] else "INCONCLUSIVE"
        out["short"] = k["short"]
    elif k["count"] == "spoiled":
        out["verdict"] = "NO VALID RUN"
    else:
        out["verdict"] = "PASS" if k["passes"] else "FAIL"
    return out


def read_summary(root, mod, spec, scene, **kw):
    """summary() over the mod's ledger; a ledger that cannot be read gives COULD NOT LOOK, never a verdict."""
    try:
        lines, _ = read(root, mod)
    except Unreadable as e:
        return {"scene": scene, "state": NO_LOOK, "verdict": None, "why": [str(e)], "runs": [], "counted": 0,
                "hunts": []}
    return summary(spec, lines, scene, **kw)


EXIT_COUNT = {"FAIL": "mod", "HELD": "unresolved", "INCONCLUSIVE": "inconclusive", "SHORT": "inconclusive",
              "NO VALID RUN": "spoiled"}


def exit_veto(root, mod, checks, counts, builds=None, relation=None):
    """The Stage 6 exit's reading of the ledger. checks: [(test id, spec)]; counts: {test id: the exit's count}. -> ({test
    id: (count, why)} for a check that the exit counts `pass` and whose scene's ledger does not read PASS, [hunt notice]).
    A check whose scene has no line in the ledger is not touched: the ledger never turns any line into a pass."""
    try:
        lines, there = read(root, mod)
    except Unreadable as e:
        return {t: ("unresolved", "the scene verdict ledger could not be read (%s): an UNRESOLVED run may stand there" % e)
                for t, _ in checks if counts.get(t) == "pass"}, []
    if not there:
        return {}, []
    out, notices = {}, []
    for t, spec in checks:
        s = summary(spec, lines, t, build=(builds or {}).get(t), relation=relation)
        notices.extend(s["hunts"])
        if s["state"] == NONE or counts.get(t) != "pass" or s["verdict"] == "PASS":
            continue
        if s["state"] in (ZERO, FAILED):
            cnt = "spoiled" if s["state"] == ZERO else "refused"
        else:
            cnt = EXIT_COUNT.get(s["verdict"], "unresolved")
        out[t] = (cnt, "the scene verdict ledger reads %s (%s): a receipt is not a verdict" % (
            s["verdict"] or s["state"], "; ".join(s["why"]) or "no reason given"))
    return out, notices


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    s = sub.add_parser("show")
    s.add_argument("mod")
    s.add_argument("scene")
    s.add_argument("--claim")
    s.add_argument("--build")
    a = sub.add_parser("add")
    a.add_argument("mod")
    a.add_argument("line")
    c = sub.add_parser("class")
    c.add_argument("mod")
    c.add_argument("run")
    c.add_argument("--outcome", required=True)
    c.add_argument("--why", required=True)
    c.add_argument("--by", required=True)
    c.add_argument("--rejudged", action="store_true")
    c.add_argument("--spoiled-by")
    ap.add_argument("--root", default=REPO)
    args = ap.parse_args(argv)
    try:
        if args.verb == "show":
            tt_path = os.path.join(args.root, "design", "concepts", args.mod, "version", "test_table.json")
            try:
                with open(tt_path, encoding="utf-8") as f:
                    spec = ((json.load(f).get("tests") or {}).get(args.scene))
            except (OSError, ValueError) as e:
                print("COULD NOT LOOK: the test table %s could not be read (%s)" % (tt_path, e))
                return EXIT[NO_LOOK]
            if not isinstance(spec, dict):
                print("FAILED: the test table names no test %s" % args.scene)
                return EXIT[FAILED]
            r = read_summary(args.root, args.mod, spec, args.scene, claim=args.claim, build=args.build)
            print(json.dumps(r, sort_keys=True))
            print("%s %s" % (r["state"], r["verdict"] or ""))
            return EXIT[r["state"]]
        if args.verb == "add":
            add_run(args.root, args.mod, json.loads(args.line))
        else:
            add_class(args.root, args.mod, args.run, args.outcome, args.why, args.by, args.rejudged, args.spoiled_by)
        print("ADDED to %s" % path(args.root, args.mod))
        return 0
    except (Refused, ValueError) as e:
        print("REFUSED: %s" % e)
        return 2
    except Unreadable as e:
        print("COULD NOT LOOK: %s" % e)
        return EXIT[NO_LOOK]


if __name__ == "__main__":
    sys.exit(main())
