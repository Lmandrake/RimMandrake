#!/usr/bin/env python3
"""pipe_off_end.py: a `pipe off` carries its end condition, and the Maturation tick lifts the off when it reads true.

Page design/specs/2026-11-26-pipe-off-end/boundary.md; selftest selftest_pipe_off_end.py. Item
RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX, part 5. His answer by card, 2026-11-26: "Program lifts it
(Recommended)".

    ./pipe off <target> --why "..." --end "closed:<ITEM>" | "ready:<Mod>" | "cmd:<command>"
    python3 src/RimMandrake/rimflow/pipe_off_end.py show          every off: reason, age, end condition, its reading
    python3 src/RimMandrake/rimflow/pipe_off_end.py sweep [--apply]   what the tick does (dry without --apply)

His holds are never lifted here: an owner-layer row, or a control row that carries his words (`--owner-said`).
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

CONCEPTS = os.path.join(REPO, "design", "concepts")
CLOSED = ("done", "dropped", "superseded")
RULING = "RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX"     # his card answer "Program lifts it" is on this item's study
FORMS = "closed:<ITEM>, ready:<Mod> or cmd:<command>"
READY_RX = re.compile(r"^\s*\**READY\b", re.M)
VISIT_RX = re.compile(r"readiness_visit_(\d+)_")
import time_budget  # noqa: E402
# budget: danger=a condition command that never returns would hold the Maturation tick; the shared call class
# budget: (time_budget.CALL_S); a hang reads could not look and the off stays
CMD_DEADLINE_S = time_budget.CALL_S


class Refused(Exception):
    pass


def parse(text):
    """'closed:<ITEM>' | 'ready:<Mod>' | 'cmd:<command>' -> the condition dict. Raises Refused."""
    kind, _c, rest = str(text or "").strip().partition(":")
    rest = rest.strip()
    if kind == "closed" and re.match(r"^[A-Z0-9_]+$", rest):
        return {"kind": "closed", "item": rest}
    if kind == "ready" and re.match(r"^[A-Za-z0-9_]+$", rest):
        return {"kind": "ready", "mod": rest}
    if kind == "cmd" and rest:
        return {"kind": "cmd", "cmd": rest}
    raise Refused("--end %r is not %s; nothing was written" % (text, FORMS))


def text_of(end):
    if not isinstance(end, dict):
        return "none set"
    return "%s:%s" % (end.get("kind"), end.get("item") or end.get("mod") or end.get("cmd"))


def check(end, root=CONCEPTS, items=None, runner=None):
    """-> (True | False | None, reading). None: could not look, with the cause."""
    k = (end or {}).get("kind")
    if k == "closed":
        if items is None:
            return None, "could not look: the ledger could not be read"
        it = items.get(end["item"])
        if it is None:
            return None, "could not look: %s is not on the ledger" % end["item"]
        st = getattr(it, "state", None)
        return (st in CLOSED), "%s: %s is %s" % ("true" if st in CLOSED else "false", end["item"], st)
    if k == "ready":
        files = glob.glob(os.path.join(root, end["mod"], "version", "in_game", "readiness_*.md"))
        if not files:
            return None, "could not look: no readiness list for %s" % end["mod"]
        newest = max(files, key=lambda p: (int((VISIT_RX.search(p) or [0, 0])[1]), os.path.basename(p)))
        try:
            with open(newest, encoding="utf-8") as f:
                ok = bool(READY_RX.search(f.read()))
        except OSError as e:
            return None, "could not look: %s (%s)" % (os.path.basename(newest), type(e).__name__)
        return ok, "%s: %s %s" % ("true" if ok else "false", os.path.basename(newest), "reads READY" if ok else
                                  "does not read READY")
    if k == "cmd":
        run = runner or (lambda c: subprocess.run(c, shell=True, cwd=REPO, capture_output=True,
                                                  timeout=CMD_DEADLINE_S).returncode)
        try:
            rc = run(end["cmd"])
        except subprocess.TimeoutExpired:
            return None, "could not look: the command did not end inside %d s" % CMD_DEADLINE_S
        if rc in (0, 1):
            return rc == 0, "%s: exit %d" % ("true" if rc == 0 else "false", rc)
        return None, "could not look: exit %s" % rc
    if k == "unreadable":
        return None, "could not look: %s" % end.get("cause")
    return None, "none set"


def _end_of(row):
    try:
        ex = json.loads(row["extra"]) if row["extra"] else {}
    except (ValueError, TypeError) as e:     # an off whose condition cannot be read is never "none set"
        return {"kind": "unreadable", "cause": "its extra field is not JSON (%s)" % type(e).__name__}
    return ex.get("end") if isinstance(ex, dict) else None


def _age(t, now):
    if not isinstance(t, (int, float)):
        return "age?"
    s = max(0, now - t)
    return "%dm" % (s // 60) if s < 3600 else "%dh" % (s // 3600) if s < 86400 * 2 else "%dd" % (s // 86400)


def _his(row):
    return row["layer"] == "owner" or bool(row["said"])


def rows(now=None, root=CONCEPTS, items=None, runner=None):
    """-> one row per live switch: scope, layer, why, age, end, end_text, reading, his. Reads conditions; acts on nothing."""
    import control as C
    now = time.time() if now is None else now
    out = []
    for s in C.switches(now=now):
        a = C._q("SELECT ts FROM acts WHERE id=?", (s["act"],), one=True) if s["act"] else None
        end = _end_of(s)
        his = _his(s)
        if his:
            reading = "his: the program never lifts it"
        elif end is None:
            reading = "none set: the Conductor sets one"
        else:
            reading = check(end, root, items, runner)[1]
        out.append({"scope": s["scope"], "layer": s["layer"], "why": s["why"], "age": _age(a["ts"] if a else None, now),
                    "end": end, "end_text": text_of(end), "reading": reading, "his": his})
    return out


def sweep(apply, now=None, root=CONCEPTS, items=None, runner=None):
    """Lift each control-layer off (not his) whose condition reads true. -> the rows, a lifted one with "lifted" and
    "undo". apply False: reads only."""
    import control as C
    now = time.time() if now is None else now
    out = []
    for s in C.switches(now=now):
        end = _end_of(s)
        r = {"scope": s["scope"], "end": end, "end_text": text_of(end), "why": s["why"]}
        if _his(s):
            r["reading"] = "his: the program never lifts it"
        elif end is None:
            r["reading"] = "none set"
        else:
            ok, r["reading"] = check(end, root, items, runner)
            if ok and apply and s["layer"] == "control":
                C.switch(s["scope"], False, "program lift: its end condition %s read %s (the off's reason was: %s)"
                         % (text_of(end), r["reading"], s["why"]), per_ruling=RULING, now=now)
                r["lifted"] = True
                r["undo"] = "undo: pipe off %s --why %s --end %s" % (s["scope"], json.dumps(s["why"]),
                                                                     json.dumps(text_of(end)))
        out.append(r)
    return out


def safe_sweep(apply, now=None):
    """The tick's call: never raises. -> (rows, None) or (None, cause)."""
    try:
        try:
            import fleet_mods
            _, w = fleet_mods.ledger()
            items = w.items
        except Exception:       # noqa: BLE001 - a closed: condition then reads could not look; nothing is lifted on it
            items = None
        return sweep(apply, now, items=items), None
    except Exception as e:      # noqa: BLE001
        return None, "could not look: %s: %s" % (type(e).__name__, e)


def page_lines(rs):
    """-> his page's lines: each off with its reason, age, end condition and its reading."""
    if rs is None or isinstance(rs, dict):
        return ["- Switched off: could not look (%s)" % ((rs or {}).get("could_not_look") or "the control store could not be read")]
    if not rs:
        return ["- Nothing is switched off."]
    return ["- `%s` off %s: %s · ends on: %s (%s)" % (r["scope"], r["age"], " ".join(str(r["why"]).split())[:140],  # cut-ok: page line
                                                     r["end_text"], r["reading"]) for r in rs]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    s = sub.add_parser("sweep")
    s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    try:
        import fleet_mods
        _, w = fleet_mods.ledger()
        items = w.items
    except Exception:       # noqa: BLE001
        items = None
    if a.cmd == "show":
        print("\n".join(page_lines(rows(items=items))))
        return 0
    for r in sweep(a.apply, items=items):
        print("%s  %s  %s%s" % (r["scope"], r["end_text"], r["reading"], ("  LIFTED; " + r["undo"]) if r.get("lifted") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
