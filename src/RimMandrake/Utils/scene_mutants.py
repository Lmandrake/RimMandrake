#!/usr/bin/env python3
"""scene_mutants - each mod's list of mutants, the seeded draw, and a scene shown both ways (green run, red run).

Item RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE (05_build_design.md §Decision 13). Promises, limits and what is not
promised: design/specs/2026-11-23-bridge-v2/boundary.md §MUTANTS AND SHOWN BOTH WAYS. Each promise has a test of its name in
selftest_scene_mutants.py.

    python3 scene_mutants.py lint <Mod>                 the mod's mutants.json against the rules; exit 0 clean, 1 refused, 2 could not read
    python3 scene_mutants.py draw <Mod> <scene> <build> the mutant that the program draws for this scene and build
    python3 scene_mutants.py history <Mod> [--killed]   each bar's mutants and their latest both-ways verdict;
                                                        --killed: exit 0 when one recorded mutant was killed, 1 when none was
    python.exe scene.py both-ways <script>              the live part (the game is the script's own): the green run, then the red run under the drawn mutant

The core (everything above `run_live`) is pure: it reads a list, verdicts and traces, and writes only through `record`.
The mod keeps the list; the program draws; the session overlay (a settings field), the patch switch or the scene's own plant
applies the mutant. The scene's author does not choose which mutant runs.
"""
import ast
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(HERE, "..", "rimflow")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import scene_compare as SC  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FILE = "version/mutants.json"
SCHEMA = "mutants_v1"
KINDS = ("live", "compiled")
# what a mutant changes. "value" is a wrong number; every other change is of a branch, an order, a target or a life cycle
CHANGES = ("value", "branch", "order", "target", "patch_off", "cache", "lifecycle", "timing")
APPLIES = ("setting", "patch", "plant")          # how a live mutant is applied: session overlay, patch switch, the scene's plant
BREAKS = ("success", "forbidden")                # the judge's roles that a red run can fail on (scene_judge.ROLES)
OFF_VALUES = ("false", "0", "off", "none", "")
# names that a scene script would use to set its own draw: refused (the author does not choose)
DRAW_NAMES = ("MUTANT", "MUTANTS", "SEED", "DRAW", "PLANT", "PLANTS")

KILLED, NOT_KILLED, NOT_USED, NO_EXPOSURE = "KILLED", "NOT_KILLED", "NOT_USED", "NO_EXPOSURE"
OTHER_CONDITION, NOT_ONE_FIXTURE, GREEN_NOT_SUCCESS = "OTHER_CONDITION", "NOT_ONE_FIXTURE", "GREEN_NOT_SUCCESS"
NEEDS_BUILD, WITNESS_UNREAD, RED_UNDECIDED, RED_COUNTED = "NEEDS_BUILD", "WITNESS_UNREAD", "RED_UNDECIDED", "RED_COUNTED"
WORDS = {
    KILLED: "mutant killed: the red run failed on the condition that the mutant names",
    NOT_KILLED: "mutant not killed: the red run ended SUCCESS under the mutant (this scene did not catch it; it does not mean "
                "the scene cannot fail)",
    NOT_USED: "mutant not used: its witness reads the same in the green and the red run, so the mutant did not act",
    NO_EXPOSURE: "proves nothing: the exposure condition did not hold in the red run as in the green run",
    OTHER_CONDITION: "the red run failed, but on another condition than the one the mutant names",
    NOT_ONE_FIXTURE: "not shown: the two runs did not start from one fixture save with one hash",
    GREEN_NOT_SUCCESS: "not shown: the green run did not end SUCCESS, so a red run shows nothing",
    NEEDS_BUILD: "needs build: a compiled mutant runs only on a build with its flag, never as a live overlay",
    WITNESS_UNREAD: "could not look: the witness is not in one of the two traces",
    RED_UNDECIDED: "not shown: the red run ended neither SUCCESS nor MOD FAILURE",
    RED_COUNTED: "DEFECT: the red run's receipt counts for a bar; a red run never counts",
}


class Refused(Exception):
    def __init__(self, name, repair):
        super().__init__("%s: %s" % (name, repair))
        self.name, self.repair = name, repair


class Unreadable(Exception):
    pass


# ---------------------------------------------------------------------------------------------------- the list
def path(root, mod):
    return os.path.join(root, "design", "concepts", mod, FILE)


def load(root, mod):
    """-> the list, or None when the mod has no list (looked, none). Raises Unreadable for a file that is there and bad."""
    p = path(root, mod)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        raise Unreadable("%s: %s" % (p, e)) from e
    if not isinstance(d, dict):
        raise Unreadable("%s is not an object" % p)
    return d


def known_bars(root, mod):
    """-> (the set of the mod's locked bar ids, None), or (None, why the locked list could not be read): then a bar is not
    checked against it, and lint says why."""
    p = os.path.join(root, "design", "concepts", mod, "version", "locked_bars.json")
    try:
        with open(p, encoding="utf-8") as f:
            ids = json.load(f).get("ids")
    except (OSError, ValueError, AttributeError) as e:
        return None, "%s could not be read: %s" % (p, e)
    return (set(ids), None) if isinstance(ids, list) else (None, "%s has no \"ids\" list" % p)


def _feature_switches(lst):
    return {str(x) for x in (lst.get("feature_switches") or []) if isinstance(x, str)}


def lint(lst, bars=None):
    """-> [(name, why, repair)] for each fault of the list; [] when it is clean. bars: the mod's locked bar ids, or None.
    A list that names no feature switch is refused: then a mutant that only turns the feature off cannot be told apart."""
    out = []

    def no(name, why, repair):
        out.append((name, why, repair))

    if lst.get("schema") != SCHEMA:
        no("SCHEMA", "schema %r" % lst.get("schema"), "set \"schema\": \"%s\"" % SCHEMA)
    switches = lst.get("feature_switches")
    if not isinstance(switches, list) or not all(isinstance(x, str) for x in switches):
        no("NO_FEATURE_SWITCHES", "the list does not name the mod's whole-feature switches",
           "list each master switch as \"<settings type>.<field>\" in \"feature_switches\" ([] only for a mod with none)")
    switches = _feature_switches(lst)
    bar_rows = lst.get("bars") if isinstance(lst.get("bars"), dict) else {}
    if not isinstance(lst.get("bars"), dict):
        no("NO_BARS", "the list has no \"bars\" object", "add \"bars\": {<bar id>: {scenes, written_by, reviewed_by, review}}")
    muts = lst.get("mutants") if isinstance(lst.get("mutants"), list) else []
    if not isinstance(lst.get("mutants"), list):
        no("NO_MUTANTS", "the list has no \"mutants\" array", "add \"mutants\": [...]")
    seen, per_bar = set(), {}
    for i, m in enumerate(muts):
        if not isinstance(m, dict):
            no("BAD_MUTANT", "mutant %d is not an object" % i, "write it as an object")
            continue
        name = m.get("name")
        tag = name if isinstance(name, str) and name else "mutant %d" % i
        if not isinstance(name, str) or not name.strip():
            no("NO_NAME", "%s has no name" % tag, "give it a name")
        elif name in seen:
            no("NAME_TWICE", "%s is in the list twice" % name, "give each mutant its own name")
        seen.add(name)
        bar = m.get("bar")
        if not isinstance(bar, str) or not bar.strip():
            no("NO_BAR", "%s names no bar" % tag, "name the bar it should break (\"bar\": <a locked bar id>)")
        elif bars is not None and bar not in bars:
            no("UNKNOWN_BAR", "%s names bar %r, which is not a locked bar of the mod" % (tag, bar), "name a bar id of locked_bars.json")
        elif bar not in bar_rows:
            no("BAR_NOT_LISTED", "%s names bar %r, which has no row in \"bars\"" % (tag, bar), "add the bar's row: its scenes and review")
        else:
            per_bar.setdefault(bar, []).append(m)
        kind, change, apply = m.get("kind"), m.get("change"), m.get("apply")
        if kind not in KINDS:
            no("BAD_KIND", "%s kind %r" % (tag, kind), "kind is one of %s" % ", ".join(KINDS))
        if change not in CHANGES:
            no("BAD_CHANGE", "%s change %r" % (tag, change), "change is one of %s" % ", ".join(CHANGES))
        if m.get("breaks") not in BREAKS:
            no("NO_BREAKS", "%s names no condition that the red run must fail on" % tag, "\"breaks\" is one of %s" % ", ".join(BREAKS))
        w = m.get("witness")
        if not isinstance(w, dict) or not witness_tracks(w):
            no("NO_WITNESS", "%s names no witness" % tag,
               "\"witness\": {\"track\": <a value the scene records, which differs because of the mutant>} or {\"tracks\": [...]}; "
               "a read-back is not a witness")
        if kind == "compiled":
            if not isinstance(m.get("flag"), str) or not m["flag"].strip():
                no("NO_FLAG", "%s is compiled but names no build flag" % tag, "\"flag\": <the define in the mod's source>")
            if apply is not None:
                no("COMPILED_APPLY", "%s is compiled but has a live apply" % tag, "a compiled mutant has a flag only")
            continue
        if kind != "live":
            continue
        if not isinstance(apply, dict) or len([k for k in APPLIES if k in apply]) != 1:
            no("BAD_APPLY", "%s: a live mutant has exactly one of %s in \"apply\"" % (tag, ", ".join(APPLIES)),
               "\"apply\": {\"setting\": \"<type>.<field>\", \"value\": \"<str>\"} | {\"patch\": \"<type>.<method>\"} | {\"plant\": \"<name>\"}")
            continue
        if "setting" in apply:
            if not isinstance(apply.get("value"), str) or "." not in str(apply.get("setting")):
                no("BAD_APPLY", "%s: a setting mutant takes \"<type>.<field>\" and a string value" % tag, "write both")
            elif apply["setting"] in switches and apply["value"].strip().lower() in OFF_VALUES:
                no("FEATURE_OFF", "%s only switches the whole feature off (%s = %s)" % (tag, apply["setting"], apply["value"]),
                   "plant a wrong value, branch, order or target inside the feature, not the master switch")
        if "patch" in apply and apply.get("patch") in switches:
            no("FEATURE_OFF", "%s takes off the patch that is the whole feature (%s)" % (tag, apply["patch"]),
               "take off a patch that does one part of the feature")
        if "plant" in apply and apply["plant"] != name:
            no("BAD_APPLY", "%s: a plant mutant's plant name is its own name, not %r" % (tag, apply["plant"]),
               "set \"plant\": \"%s\"" % name)
        if m.get("feature_off") is True:
            no("FEATURE_OFF", "%s says it switches the feature off" % tag, "a mutant breaks a part, not the whole")
    for bar, row in sorted(bar_rows.items()):
        if not isinstance(row, dict):
            no("BAD_BAR_ROW", "bar %s's row is not an object" % bar, "write it as an object")
            continue
        n = len(per_bar.get(bar, []))
        if n < 2:
            no("ONE_MUTANT", "bar %s has %d mutant(s); the draw is no draw with fewer than 2" % (bar, n), "add another mutant for it")
        scenes = row.get("scenes")
        if not isinstance(scenes, list) or not scenes or not all(isinstance(s, str) and s for s in scenes):
            no("NO_SCENE", "bar %s names no scene" % bar, "\"scenes\": [<the scene file's name without .py>]")
        wb, rb = str(row.get("written_by") or "").strip(), str(row.get("reviewed_by") or "").strip()
        if not wb:
            no("NO_WRITER", "bar %s does not name who wrote its scene" % bar, "\"written_by\": <the unit or item that wrote it>")
        if not rb or rb == wb or not str(row.get("review") or "").strip():
            no("NOT_REVIEWED", "bar %s's mutants are not reviewed by an agent that did not write the scene" % bar,
               "an agent that did not write the scene reads the list and writes \"reviewed_by\" and \"review\"")
    return out


def scene_sets_draw(src):
    """-> the names by which a scene script tries to set its own draw ([] when none). The draw reads only the list, the
    scene's name and the build, so a scene that names one of DRAW_NAMES at its top level, or calls scene.accept with a
    plant, is refused: the author does not choose."""
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return ["the script does not parse: %s" % e]
    out = []
    for n in tree.body:
        targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, (ast.AnnAssign, ast.AugAssign)) else []
        for t in targets:
            if isinstance(t, ast.Name) and t.id.upper() in DRAW_NAMES:
                out.append(t.id)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("accept", "both_ways"):
            if len(n.args) > 1 or any(k.arg in ("plant_", "plant", "mutant") for k in n.keywords):
                out.append("a call of %s with a plant" % n.func.attr)
    return out


def candidates(lst, scene):
    """-> the mutants of every bar whose row names this scene, in name order."""
    rows = lst.get("bars") or {}
    bars = {b for b, r in rows.items() if isinstance(r, dict) and scene in (r.get("scenes") or [])}
    return sorted((m for m in lst.get("mutants") or [] if isinstance(m, dict) and m.get("bar") in bars), key=lambda m: str(m.get("name")))


def draw(lst, mod, scene, build, scene_src=None):
    """-> the mutant drawn for this scene on this build. The seed is the hash of the mod, the scene and the build: the same
    scene and build always draw the same mutant, and nothing in the scene can set it. Compiled mutants are in the draw, so
    the author cannot steer it by kind; one that is drawn is NEEDS_BUILD and is not run live."""
    if scene_src is not None:
        bad = scene_sets_draw(scene_src)
        if bad:
            raise Refused("SCENE_SETS_DRAW", "the scene sets its own draw (%s); remove it: the program draws" % ", ".join(bad))
    if not isinstance(build, str) or not build.strip():
        raise Refused("NO_BUILD", "the draw needs the build (the commit that the runs are made on)")
    pool = candidates(lst, scene)
    if not pool:
        raise Refused("NO_MUTANTS_FOR_SCENE", "no bar of %s's mutants.json names scene %s; add the bar's row" % (mod, scene))
    seed = int(hashlib.sha256(("%s\0%s\0%s" % (mod, scene, build)).encode("utf-8")).hexdigest(), 16)
    return pool[seed % len(pool)]


def launch_for(mutant):
    """-> what the red run's launch carries for this mutant: the plant name (stamped PLANTED on every receipt), and for a
    setting mutant the session overlay entry. NEEDS_BUILD for a compiled mutant."""
    if mutant.get("kind") == "compiled":
        raise Refused(NEEDS_BUILD, "%s is compiled (flag %s): build the mod with the flag; it is not run live" % (mutant.get("name"), mutant.get("flag")))
    apply = mutant.get("apply") or {}
    out = {"plant": mutant["name"]}
    if "setting" in apply:
        typ, _, field = apply["setting"].rpartition(".")
        out["overlay"] = {"name": "mutant %s" % mutant["name"], "entries": [{"typeName": typ, "field": field, "value": apply["value"]}]}
    if "patch" in apply:
        out["patch_off"] = apply["patch"]
    return out


# ---------------------------------------------------------------------------------------------------- shown both ways
def witness_tracks(witness):
    """-> the track names of a witness: {"track": name} or {"tracks": [names]} (any one of them that differs is the witness)."""
    w = witness or {}
    names_ = w.get("tracks") if isinstance(w.get("tracks"), list) else [w.get("track")]
    return [n for n in names_ if isinstance(n, str) and n.strip()]


def witness_changed(green_rows, red_rows, witness):
    """-> True when a witness track's course differs between the two traces (by offset from each run's open tick), False
    when every witness track is in both traces and reads the same, None when no track differs and one is missing from a
    trace (could not look)."""
    names_ = witness_tracks(witness)
    if not names_ or SC._open(green_rows or []) is None or SC._open(red_rows or []) is None:
        return None
    tg, tr = SC.timeline(green_rows), SC.timeline(red_rows)
    missing = False
    for name in names_:
        a, b = tg["tracks"].get(name), tr["tracks"].get(name)
        if not a or not b:
            missing = True
        elif a != b:
            return True
    return None if missing else False


def judge_both_ways(mutant, green, red):
    """Pure. green and red: {"verdict": {outcome, failed, evidence, counts_for_bar}, "fixture": {"name", "sha256"},
    "rows": the judged run's trace rows}. -> {"verdict": one of WORDS, "why": its words, "change": the mutant's change}."""
    def out(word, more=""):
        return {"verdict": word, "why": WORDS[word] + (": " + more if more else ""), "mutant": mutant.get("name"),
                "change": mutant.get("change"), "kind": mutant.get("kind")}

    if mutant.get("kind") == "compiled" and red is None:
        return out(NEEDS_BUILD, "flag %s" % mutant.get("flag"))
    fg, fr = (green or {}).get("fixture") or {}, (red or {}).get("fixture") or {}
    if not fg.get("sha256") or fg != fr:
        return out(NOT_ONE_FIXTURE, "green %s, red %s" % (fg or "unknown", fr or "unknown"))
    gv, rv = green.get("verdict") or {}, red.get("verdict") or {}
    if gv.get("outcome") != "SUCCESS":
        return out(GREEN_NOT_SUCCESS, "green %s" % gv.get("outcome"))
    if rv.get("counts_for_bar") is not False:
        return out(RED_COUNTED, "counts_for_bar %r" % rv.get("counts_for_bar"))
    if (gv.get("evidence") or {}).get("exposure") is not True or (rv.get("evidence") or {}).get("exposure") is not True:
        return out(NO_EXPOSURE, "green exposure %s, red exposure %s" % ((gv.get("evidence") or {}).get("exposure"),
                                                                       (rv.get("evidence") or {}).get("exposure")))
    used = witness_changed(green.get("rows"), red.get("rows"), mutant.get("witness"))
    if used is None:
        return out(WITNESS_UNREAD, "track(s) %s" % ", ".join(witness_tracks(mutant.get("witness"))))
    if used is False:
        return out(NOT_USED, "track(s) %s" % ", ".join(witness_tracks(mutant.get("witness"))))
    word = rv.get("outcome")
    if word == "SUCCESS":
        return out(NOT_KILLED)
    if word == "MOD FAILURE":
        cond = (rv.get("failed") or {}).get("condition")
        if cond == mutant.get("breaks"):
            return out(KILLED, "on %s" % cond)
        return out(OTHER_CONDITION, "failed on %s; the mutant names %s" % (cond, mutant.get("breaks")))
    return out(RED_UNDECIDED, "red %s" % word)


def record(root, mod, scene, build, mutant, result, green, red):
    """Append the both-ways line to the mod's scene_runs.jsonl: both runs' ids, receipts and fixtures, and the verdict."""
    import scene_verdicts as SV

    def side(x):
        x = x or {}
        return {k: x.get(k) for k in ("run", "receipt", "fixture")} | {"outcome": (x.get("verdict") or {}).get("outcome")}
    line = {"rec": "both_ways", "scene": scene, "bar": mutant.get("bar"), "mutant": mutant.get("name"), "kind": mutant.get("kind"),
            "change": mutant.get("change"), "build": build, "green": side(green), "red": side(red) if red else None,
            "verdict": result["verdict"], "why": result["why"], "at": SV._now()}
    return SV._append(root, mod, line)


def bar_history(lst, lines):
    """-> {bar: {"mutants": {name: latest verdict or None}, "killed": [...], "note": str or None}} from both_ways lines."""
    latest = {}
    for x in lines:
        if x.get("rec") == "both_ways":
            latest[x.get("mutant")] = x
    out = {}
    for m in lst.get("mutants") or []:
        if not isinstance(m, dict):
            continue
        b = out.setdefault(m.get("bar"), {"mutants": {}, "killed": [], "note": None})
        v = (latest.get(m.get("name")) or {}).get("verdict")
        b["mutants"][m.get("name")] = v or (NEEDS_BUILD if m.get("kind") == "compiled" else None)
        if v == KILLED:
            b["killed"].append(m)
    for b in out.values():
        if b["killed"] and all(m.get("change") == "value" for m in b["killed"]):
            b["note"] = ("ONLY_VALUE_KILLS: every killed mutant of this bar is a value change, so a wrong branch, order or target "
                         "is not shown caught")
        b["killed"] = [m.get("name") for m in b["killed"]]
    return out


def killed_proven(lines):
    """-> the both_ways lines with verdict KILLED whose green and red runs are run lines of the ledger, the green judged
    SUCCESS and the red MOD FAILURE. A line written by hand with no such runs is not counted."""
    runs = {x.get("run"): x for x in lines if x.get("rec") == "run"}
    out = []
    for x in lines:
        if x.get("rec") != "both_ways" or x.get("verdict") != KILLED:
            continue
        g, r = runs.get((x.get("green") or {}).get("run")), runs.get((x.get("red") or {}).get("run"))
        if g and r and g.get("outcome") == "SUCCESS" and r.get("outcome") == "MOD FAILURE" and g.get("receipt") == x["green"].get("receipt") \
                and r.get("receipt") == x["red"].get("receipt") and any(str(s).startswith("PLANTED ") for s in r.get("stamps") or []):
            out.append(x)
    return out


# ---------------------------------------------------------------------------------------------------- the live part
def _mod_of(script):
    s = os.path.relpath(os.path.abspath(script), REPO).replace("\\", "/")
    parts = s.split("/")
    if s.startswith("design/concepts/"):
        return parts[2]
    if s.startswith("src/RimMandrake/") and len(parts) > 3:
        return parts[2]
    raise Refused("NOT_A_MOD_SCENE", "%s is not under design/concepts/<Mod>/ or src/RimMandrake/<Mod>/" % s)


def _side(run_dir, verdict):
    with open(os.path.join(run_dir, "run.json")) as f:
        run = json.load(f)
    rows = []
    traces = sorted(n for n in os.listdir(run_dir) if n.startswith("trace_") and n.endswith(".jsonl"))
    req = (verdict.receipt or {}).get("entry", {}).get("request")
    pick = [n for n in traces if n == "trace_%s.jsonl" % req] or traces[-1:]
    for n in pick:
        with open(os.path.join(run_dir, n)) as f:
            rows = [json.loads(x) for x in f if x.strip()]
    rands = []
    for n in traces:
        with open(os.path.join(run_dir, n)) as f:
            o = SC._open([json.loads(x) for x in f if x.strip()])
        rands.append(str(o.get("rand")) if o and o.get("rand") is not None else None)
    return {"run": "%s:%s" % (run.get("session"), req), "fixture": run.get("fixture"), "rows": rows, "rands": rands,
            "verdict": {"outcome": verdict.outcome, "failed": verdict.first_failed, "evidence": verdict.evidence,
                        "counts_for_bar": verdict.counts_for_bar}}


def run_live(script):
    """scene.py both-ways: the green run, then the red run under the drawn mutant, each from the scene's fixture save loaded
    fresh, the red run with the green run's random state written back. -> exit code."""
    import scene
    import scene_verdicts as SV
    mod, name = _mod_of(script), os.path.splitext(os.path.basename(script))[0]
    lst = load(REPO, mod)
    if lst is None:
        raise Refused("NO_LIST", "%s has no %s" % (mod, FILE))
    bad = lint(lst, known_bars(REPO, mod)[0])
    if bad:
        raise Refused("LIST_REFUSED", "; ".join("%s %s (%s)" % b for b in bad))
    with open(script, encoding="utf-8") as f:
        src = f.read()
    rc, head = scene._world().git("rev-parse", "HEAD")
    build = head.strip()
    m = draw(lst, mod, name, build, src)
    print("BOTH WAYS %s on %s: drawn mutant %s (bar %s, %s %s)" % (name, build[:12], m["name"], m["bar"], m["kind"], m["change"]), flush=True)
    if m.get("kind") == "compiled":
        res = judge_both_ways(m, None, None)
        record(REPO, mod, name, build, m, res, None, None)
        print("BOTH WAYS %s: %s" % (name, res["why"]))
        return 4
    launch = launch_for(m)
    if "patch_off" in launch:
        raise Refused("PATCH_SWITCH_NOT_WIRED", "%s takes off patch %s; both-ways does not yet drive the patch switch hand (boundary.md "
                      "§THE PATCH SWITCH): wire it in scene.open's overlay first" % (m["name"], launch["patch_off"]))
    sides = []
    for arm in ("green", "red"):
        scene.LAUNCH["run_dirs"] = []
        extra = {} if arm == "green" else dict(launch, rands=sides[0]["rands"])
        rc = scene.accept(script, extra.get("plant"), extra=extra)
        dirs = scene.LAUNCH.get("run_dirs") or []
        if not dirs:
            print("BOTH WAYS %s: COULD NOT LOOK: the %s run kept no run folder (exit %s)" % (name, arm, rc))
            return 2
        v = scene.judge(dirs[-1])
        sides.append(_side(dirs[-1], v))
        print("BOTH WAYS %s %s run: %s (%s)" % (name, arm, v.outcome, dirs[-1]), flush=True)
    lines, _ = SV.read(REPO, mod)
    for sd in sides:
        line = next((x for x in lines if x.get("rec") == "run" and x.get("run") == sd["run"]), None)
        sd["receipt"] = line.get("receipt") if line else None
    res = judge_both_ways(m, sides[0], sides[1])
    record(REPO, mod, name, build, m, res, sides[0], sides[1])
    print("BOTH WAYS %s: %s %s" % (name, res["verdict"], res["why"]))
    return 0 if res["verdict"] in (KILLED, NOT_KILLED) else 1


# ---------------------------------------------------------------------------------------------------- the command line
def main(argv):
    if len(argv) >= 2 and argv[0] == "lint":
        try:
            lst = load(REPO, argv[1])
        except Unreadable as e:
            print("COULD NOT LOOK %s" % e)
            return 2
        if lst is None:
            print("%s: no %s (looked, none)" % (argv[1], FILE))
            return 1
        bars, why = known_bars(REPO, argv[1])
        bad = lint(lst, bars)
        for b in bad:
            print("REFUSED %s %s. Repair: %s" % b)
        note = "" if bars is not None else " (bar ids were not checked against the locked list: %s)" % why
        print("%s: %d mutant(s), %d fault(s)%s" % (argv[1], len(lst.get("mutants") or []), len(bad), note))
        return 1 if bad else 0
    if len(argv) == 4 and argv[0] == "draw":
        try:
            lst = load(REPO, argv[1])
            if lst is None:
                print("%s: no %s (looked, none)" % (argv[1], FILE))
                return 1
            m = draw(lst, argv[1], argv[2], argv[3])
        except Unreadable as e:
            print("COULD NOT LOOK %s" % e)
            return 2
        except Refused as e:
            print("REFUSED %s" % e)
            return 3
        print(json.dumps(m, sort_keys=True))
        return 0
    if len(argv) >= 2 and argv[0] == "history":
        import scene_verdicts as SV
        try:
            lst = load(REPO, argv[1])
            lines, _ = SV.read(REPO, argv[1])
        except (Unreadable, SV.Unreadable) as e:
            print("COULD NOT LOOK %s" % e)
            return 2
        if lst is None:
            print("%s: no %s (looked, none)" % (argv[1], FILE))
            return 1
        for bar, b in sorted(bar_history(lst, lines).items(), key=lambda i: str(i[0])):
            print("%s: %s%s" % (bar, ", ".join("%s=%s" % (k, v or "never run") for k, v in sorted(b["mutants"].items())),
                                "  " + b["note"] if b["note"] else ""))
        if "--killed" in argv:
            got = killed_proven(lines)
            print("%d mutant(s) killed with both runs in the ledger%s" % (len(got), ": " + ", ".join(x["mutant"] for x in got) if got else ""))
            return 0 if got else 1
        return 0
    print(__doc__)
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
