#!/usr/bin/env python3
"""shortfall.py -- a stochastic scene that ends short of its X of Y escalates to the Conductor (owner, 2026-11-23,
design/RimMandrake/standing_rulings.md §Live tests have three kinds). live_kinds.py reads the shortfall; this file asks
(the Maturation tick calls `observe`) and records the Conductor's call on the scene in the mod's test table.

  python3 src/RimMandrake/rimflow/shortfall.py call <Mod> <scene> needed --item ID --why "..."
      the mod's function needs X of Y: the scene reads MOD FAILURE and takes the road back
  python3 src/RimMandrake/rimflow/shortfall.py call <Mod> <scene> guess --x N [--y M] --item ID --why "..."
      X was a guess against environmental fluctuation: N of Y (or of M) stands on the scene, and the scene is judged again;
      the opportunities already run on the same build count

The Conductor window only. Exit 0 recorded and landed; 2 refused, nothing written; 3 could not look; 4 the table is written
and its landing or the note failed, named. Page: design/specs/2026-11-23-live-kinds-exit-reader/boundary.md."""
import argparse
import copy
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import live_kinds as LK  # noqa: E402

NOTE_RETRY_S = 600
QUESTION = ("Does the mod REQUIRE X of Y to be true, or was X of Y a guess and (X-1) of Y is just as good? Does the mod's "
            "function need X of Y, or did X guard against environmental fluctuation?")


# ---- the question: the tick's half -----------------------------------------------------------------------------------

def key_of(mod, s):
    return "%s|%s|%s of %s|%s" % (mod, s["test"], s["x_of_y"][0], s["x_of_y"][1], s.get("mod_sha"))


def item_of(f):
    """-> the item of the mod's newest in-game run in the tick's facts, or None."""
    import maturation_dispatch as MD
    runs = [r for r in (f or {}).get("runs_seen") or [] if isinstance(r, dict) and MD._is_ingame_item(r.get("item"))]
    return max(runs, key=lambda r: r.get("at") or 0)["item"] if runs else None


def text_of(mod, s, item):
    x, y = s["x_of_y"]
    cmd = "python3 src/RimMandrake/rimflow/shortfall.py call %s %s %%s --item %s --why \"...\"" % (mod, s["test"], item or "ID")
    return ("%s scene %s ended short of its X of Y: it reached %d of the %d it needs (%d of %d), in %d valid opportunity(ies) "
            "on build %s; %d of %d budgeted run(s) spent. Tag evidence: %s. %s The scene's pass is held until your call is "
            "recorded: `%s` (the scene reads MOD FAILURE and takes the road back), or `%s` (X was a guess; N stands on the "
            "scene and it is judged again)." % (
                mod, s["test"], s["got"], x, x, y, s["valid"], s.get("mod_sha"), s["spent"], s["budget"],
                s.get("tag_evidence"), QUESTION, cmd % "needed", cmd % "guess --x N"))


def seen(st, key):
    """-> what was written for this shortfall on an earlier tick."""
    return st.setdefault("shortfalls", {}).setdefault(key, {})


def _note(item, text):
    """The note on the mod's item, as the tick files its items (RUNNER, under the clone's ingest lock). -> (ok, text)."""
    import dispatcher as D
    import maturation_dispatch as MD
    lk = D.git_lock()
    if lk is None:
        return False, "ingest.lock stayed busy"
    try:
        ing = MD._ingest()
        rc, out = ing.rimflow("note", item, "--text", text, "--why", "a scene ended short of its X of Y")
        if rc:
            return False, "note refused: %s" % out
        return True, "noted; publish: %s" % ing.publish(1, message="ledger: a scene short of its X of Y, noted on %s" % item)
    finally:
        lk.close()


def observe(facts, st, now, rd, fx=None):
    """The tick's pass: ask the Conductor once for each shortfall whose call is owed. -> rd with rd['shortfalls']."""
    fx = fx or {}
    import detached_helper as DH
    out = rd["shortfalls"] = []
    for mod, f in sorted((facts or {}).items()):
        for s in ((f or {}).get("exit") or {}).get("shortfalls") or [] if mod not in (fx.get("holds") or ()) else []:
            item, k = item_of(f), key_of(mod, s)
            b, text, said = seen(st, k), text_of(mod, s, item), []
            if not b.get("log"):
                try:
                    DH.conductor_line(text, now, path=fx.get("conductor_log"), head="SHORT OF X OF Y (RAISE FIRST)")
                    b["log"] = now
                except (OSError, RuntimeError, ValueError, KeyError) as e:
                    said.append("the Conductor log line was not written (%s: %s)" % (type(e).__name__, e))
            if not b.get("note"):
                if not item:
                    said.append("no in-game run item is known for %s: the note is owed" % mod)
                elif now - float(b.get("tried") or 0) >= NOTE_RETRY_S or not b.get("tried"):
                    b["tried"] = now
                    try:
                        ok, why = (fx.get("note") or _note)(item, "SHORT OF X OF Y: " + text)
                    except Exception as e:      # noqa: BLE001  a failed note is named and tried again
                        ok, why = False, "%s: %s" % (type(e).__name__, e)
                    if ok:
                        b.update(note=now, item=item)
                    else:
                        b["note_failed"] = why
                if item and not b.get("note"):
                    said.append("the note on %s is owed (%s)" % (item, b.get("note_failed")))
            out.append({"key": k, "item": b.get("item") or item, "written": [w for w in ("log", "note") if b.get(w)],
                        "owed": said})
            rd.setdefault("needs_conductor", []).append(text + "".join(" [%s]" % x for x in said))
    return rd


# ---- the answer: the Conductor's command -----------------------------------------------------------------------------

def may(why, env):
    import conductor_acts as CA
    ok, text = CA.check("x of y call", why, env)
    if ok and len(str(why).split()) < LK.WHY_WORDS:
        return False, "refused: the why has fewer than %d words" % LK.WHY_WORDS
    return ok, text


def stays_short(spec, runs):
    k = LK.reading(spec, runs)
    return bool(k and k["short"])


def _answer(a, spec, runs):
    """-> (the scene with the call on it, the entry) or (None, why refused)."""
    k = LK.reading(spec, runs)
    if not k or not k["short"] or k["count"] in ("unresolved", "refused", "tag"):
        return None, "%s reads no shortfall here (%s); if the rows are newer than this clone, run ./sync" % (
            a.scene, "; ".join((k or {}).get("why") or []) or "no X of Y ended short")
    s, (x, y) = k["short"], k["short"]["x_of_y"]
    e = {"call": a.call, "x_of_y": [x, y], "got": s["got"], "valid": s["valid"], "mod_sha": s["mod_sha"],
         "why": " ".join(a.why.split()), "by": "BENCH", "at": datetime.datetime.now(datetime.timezone.utc).strftime(
             "%Y-%m-%dT%H:%M:%SZ")}
    new = copy.deepcopy(spec)
    if a.call == LK.NEEDED:
        if a.x is not None or a.y is not None:
            return None, "`needed` takes no --x or --y: X of Y stays %d of %d" % (x, y)
    else:
        n, m = a.x, a.y if a.y is not None else y
        if n is None or not 1 <= n <= x or m < y or [n, m] == [x, y]:
            return None, "`guess` needs --x N with 1 <= N <= %d, and --y M (optional) at least %d, not both as they are" % (x, y)
        new["x_of_y"] = e["to"] = [n, m]
        if m > y:
            new["budget"] = max(s["budget"], s["spent"] + m - s["valid"])
        if stays_short(new, runs):
            return None, "%d of %d leaves the scene short on the runs it has (%d success(es) in %d valid): give a smaller --x, " \
                         "or more opportunities with --y" % (n, m, s["got"], s["valid"])
    old = new.get("x_of_y_calls")
    new["x_of_y_calls"] = (old if isinstance(old, list) else []) + [e]
    return new, e


def _run(runner, argv, root):
    """-> (ok, last line)."""
    try:
        r = runner(argv, cwd=root, capture_output=True, text=True)
    except OSError as e:
        return False, str(e)
    return r.returncode == 0, "".join(((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-1:])


def dump_like(was, tt):
    """-> tt as JSON text in the file's own shape, so that the landing holds the call and nothing else."""
    d = json.loads(was)
    for ind in (1, 2, None):
        for asc in (True, False):
            for end in ("\n", ""):
                if json.dumps(d, indent=ind, ensure_ascii=asc) + end == was:
                    return json.dumps(tt, indent=ind, ensure_ascii=asc) + end
    return json.dumps(tt, indent=1, ensure_ascii=False) + "\n"


def main(argv=None, root=REPO, runner=subprocess.run, env=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("call", help="record the Conductor's call on a scene short of its X of Y")
    c.add_argument("mod")
    c.add_argument("scene")
    c.add_argument("call", choices=LK.CALLS)
    c.add_argument("--x", type=int)
    c.add_argument("--y", type=int)
    c.add_argument("--item", required=True)
    c.add_argument("--why", required=True)
    a = ap.parse_args(argv)
    ok, text = may(a.why, env)
    if not ok:
        print(text)
        return 2
    import build_match as BM
    import conductor_acts as CA
    import maturation as M
    rel = "design/concepts/%s/version/test_table.json" % a.mod
    p = os.path.join(root, rel)
    try:
        with open(p, encoding="utf-8") as f:
            was = f.read()
        tt = json.loads(was)
        spec = dict(M.ingame_tests(tt)).get(a.scene)
        runs = BM.check_runs(root, a.mod).get(a.scene)
    except (OSError, ValueError, AttributeError) as e:
        print("COULD NOT LOOK: %s; nothing was written" % e)
        return 3
    new, e = _answer(a, spec, runs) if spec else (None, "%s is no stage-6 in-game check of %s" % (a.scene, rel))
    if new is None:
        print("REFUSED: %s; nothing was written" % e)
        return 2
    tt["tests"][a.scene] = new
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        f.write(dump_like(was, tt))
    os.replace(p + ".tmp", p)
    said = "%s scene %s, %d of %d (%d reached): the Conductor's call is %s" % (
        a.mod, a.scene, e["x_of_y"][0], e["x_of_y"][1], e["got"], "that the mod needs X of Y" if a.call == LK.NEEDED else
        "that X was a guess; now %d of %d" % tuple(e["to"]))
    ok, line = _run(runner, [os.path.join(root, "publish"), "-m", said, rel], root)
    if not ok:
        print("WRITTEN, NOT LANDED: %s (%s). Land it: ./publish -m \"%s\" %s ; then write the note by hand: cli.py note %s" % (
            rel, line, said, rel, a.item))
        return 4
    print("%s: %s" % (said, line))
    ok, line = _run(runner, [sys.executable, os.path.join(HERE, "cli.py"), "note", a.item, "--per-ruling", CA.RULING, "--text",
                             said + ". Why: " + e["why"], "--why", CA.tagged(a.why, "x of y call"), "--publish"], root)
    if not ok:
        print("NOTE NOT WRITTEN on %s (%s): the call stands and is landed; write the note by hand" % (a.item, line))
        return 4
    print("note on %s: %s" % (a.item, line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
