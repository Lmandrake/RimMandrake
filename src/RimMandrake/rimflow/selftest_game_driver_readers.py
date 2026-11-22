#!/usr/bin/env python3
"""selftest_game_driver_readers.py - the equivalence run of RIMMANDRAKE_MOVE_GAME_DRIVER_READERS_OFF_BRIDGE_FILE_TWO_LEFT.

The two last readers of the BRIDGE glance file (`preflight_bridge.c_bridge_lease`, `running_now.collect_bridge`) now
read each game's driver lock through `game_lock.query`. This runs the OLD readers (frozen copies of their code at
88fccbe8d6, below) and the NEW ones on the same lock states and compares their verdicts:

  old path: the lock -> the glance file `rimflow bridge who` prints from it (`cli._mirror_bridge`, the real printer)
            -> the old reader of that file; and the old reader with no glance file at all (a helper clone has none)
  new path: the lock -> `preflight_bridge.c_bridge_lease` / `running_now.collect_bridge`, and `game_lock.py query all`

Every difference is classed in the table `KNOWN_OLD_WRONG` (the old reader was wrong; the new verdict stands). An
unclassed difference, or a new reader that disagrees with `game_lock.py query all`, is a FAIL.

    python3 selftest_game_driver_readers.py              the fixture cases (offline, throwaway locks): exit 0/1
    python3 selftest_game_driver_readers.py --recorded   also every driver lock kept on this machine (read only, copied)
                                                         and every BRIDGE glance file of a clone here, against the lock

Page: design/specs/2026-11-21-one-game-lock/boundary.md (the-two-last-glance-file-readers-read-every-game-from-the-lock).
"""
import glob
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

TMP = tempfile.mkdtemp(prefix="st_game_driver_readers_")
HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
for _k in ("RM_GAME_INSTANCE", "RM_HOST_GUARD_GEN", "RM_DRIVER_PID", "RM_ROLE_UNIT", "RIMFLOW_BRIDGE_SEAT",
           "AGENT_SEAT", "CLAUDE_SESSION_ID"):
    os.environ.pop(_k, None)
A_LOCK = os.path.join(TMP, "DRIVER_LOCK.json")
INST = os.path.join(TMP, "instances")
B_LOCK = os.path.join(INST, "b", "DRIVER_LOCK.json")
os.makedirs(os.path.join(INST, "b"))
os.makedirs(os.path.join(TMP, "items"))
CONTROL = os.path.join(TMP, "control.db")
os.environ.update(RIMFLOW_DRIVER_LOCK=A_LOCK, RM_INSTANCES_ROOT=INST, RIMFLOW_LEDGER=os.path.join(TMP, "events.jsonl"),
                  RIMFLOW_ITEMS=os.path.join(TMP, "items"), RM_CONTROL_DB=CONTROL, RIMFLOW_SEAT="BENCH",
                  RIMFLOW_OWNER_ACT_STAMP=os.path.join(TMP, "stamp.json"), RIMFLOW_PROBE="no-reading",
                  RIMFLOW_BRIDGE_LOCK=os.path.join(TMP, "bridge.lock"), RM_HOST="archmagi")
GLANCE = os.path.join(TMP, "BRIDGE")          # where the printer writes under this RIMFLOW_LEDGER (model.bridge_mirror_path)
for _p in (HERE, UTILS):
    sys.path.insert(0, _p)
import cli  # noqa: E402
import control  # noqa: E402
import driver_lock  # noqa: E402
import game_lock  # noqa: E402
import preflight_bridge  # noqa: E402
import running_now  # noqa: E402
import bridge_holder  # noqa: E402

FAILS, SLEEPERS = [], []
TALLY = {"compared": 0, "same": 0, "old_wrong": {}}


def check(cond, msg, detail=""):
    print(("ok   " if cond else "FAIL ") + msg + ("" if cond else "  %s" % (detail,))[:900])
    if not cond:
        FAILS.append(msg)
    return bool(cond)


# --- the OLD readers, frozen at 88fccbe8d6 (their glance-file input passed in, not read from a fixed path) --------
def old_c_bridge_lease(text, seat, live):
    """preflight_bridge.c_bridge_lease as it was: the first status line of its own clone's BRIDGE file."""
    if text is None:
        return "UNMEASURED", "cannot read BRIDGE"
    try:
        line = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith('#')][0].strip()
    except IndexError:
        return "UNMEASURED", "cannot read BRIDGE"
    if line.startswith('FREE'):
        return "PASS", line
    parts = line.split()
    holder = parts[1] if parts[0].upper() == 'HELD' and len(parts) > 1 else parts[0]
    if holder.upper().startswith(bridge_holder.identity(seat.upper())):
        return "PASS", 'held by this seat: ' + line
    return "FAIL", 'held by another seat: %s' % line


def old_collect_bridge(texts):
    """running_now.collect_bridge as it was: the newest of the dispatch and bench clones' BRIDGE files, ArchBig only.
    texts: [(text or None, mtime)]."""
    last = None
    for txt, mt in texts:
        if txt is None:
            continue
        body = "\n".join(l for l in txt.splitlines() if not l.startswith("#"))
        m = re.search(r"^(HELD|FREE)\b[ \t]*(?!since\b)(\S*)[ \t]*(?:since\s+(\S+))?", body, re.M)
        if m and (last is None or mt > last["mt"]):
            last = {"state": m.group(1), "who": m.group(2), "mt": mt}
    return last        # None: the old reader raised Unmeasured


# --- worlds -------------------------------------------------------------------------------------------------------
def sleeper():
    p = subprocess.Popen(["sleep", "300"])
    SLEEPERS.append(p)
    time.sleep(0.05)
    return p


def ident_of(pid):
    return {"pid": pid, "start": driver_lock._proc_start(pid), "boot_id": driver_lock.current_boot_id(),
            "platform": "wsl", "host": socket.gethostname()}


def lock_body(seat, pid=None, purpose="planted", ago=0):
    t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - ago))
    ident = ident_of(pid) if pid else {"pid": 999999, "start": 1.0, "boot_id": "gone", "platform": "wsl",
                                        "host": socket.gethostname()}
    return {"seat": seat, "purpose": purpose, "identity": ident, "acquired": t, "heartbeat": t, "generation": 3}


def stage(a=None, b=None, pipe_a=None, control_bad=False):
    """Plant game a's and game b's locks (a dict, raw text, or None for no lock) and his pipe hold on game a."""
    for path, body in ((A_LOCK, a), (B_LOCK, b)):
        for p in (path, path + ".gen"):
            if os.path.exists(p):
                os.remove(p)
        if body is not None:
            with open(path, "w", encoding="utf-8") as f:
                f.write(body if isinstance(body, str) else json.dumps(body))
    for p in glob.glob(CONTROL + "*") + [GLANCE]:
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    if control_bad:
        os.makedirs(CONTROL)        # a store that exists and cannot be read
    elif pipe_a:
        control.init(CONTROL)
        control.switch("game:a", True, pipe_a, p=CONTROL)


def printed_glance():
    """The glance file the old system would hold for these locks: the real printer (`rimflow bridge who`'s)."""
    cli._mirror_bridge(None)
    with open(GLANCE, encoding="utf-8") as f:
        return f.read()


def query_all_cli():
    r = subprocess.run([sys.executable, os.path.join(HERE, "game_lock.py"), "query", "all"], capture_output=True,
                       text=True, timeout=60)
    return [ln for ln in r.stdout.splitlines() if ln.startswith(("ArchBig:", "ArchSmall:"))]


class LiveEnv(running_now.Env):
    pass


def norm_old_rn(o):
    return None if o is None else (o["state"], o["who"] or "")


def norm_new_rn_a(rows):
    """New running_now row of ArchBig, in the old reader's terms: (HELD|FREE, who) or None for UNMEASURED."""
    a = [r for r in rows if r["game"] == "ArchBig"][0]
    if a["state"] == "UNKNOWN":
        return None
    if a["state"] == "HELD" or (a["state"] == "HIS_HOLD" and a["who"]):
        return ("HELD", a["who"])
    if a["state"] == "HIS_HOLD":
        return ("HIS_HOLD", "")
    return ("FREE", "")


def compare(case, a=None, b=None, pipe_a=None, control_bad=False, seat="BENCH", why_differs=None, quiet=False):
    """Run the old and new readers on one world. why_differs: {reader: reason} for the differences the old reader is
    known to get wrong; any other difference fails."""
    why_differs = why_differs or {}
    stage(a, b, pipe_a, control_bad)
    glance = printed_glance()
    os.remove(GLANCE)
    ctx = {"seat": seat, "live": False}
    new_pf = preflight_bridge.c_bridge_lease(ctx).status
    new_rows = running_now.collect_bridge(LiveEnv())
    lines = query_all_cli()
    same = [r["line"] for r in new_rows] == lines
    if not (same and quiet):
        check(same, "%s: running_now reads every game as `game_lock.py query all`" % case,
              ([r["line"] for r in new_rows], lines))
    rows = {
        "preflight, glance printed": (old_c_bridge_lease(glance, seat, False)[0], new_pf),
        "preflight, no glance file": (old_c_bridge_lease(None, seat, False)[0], new_pf),
        "running_now, glance printed": (norm_old_rn(old_collect_bridge([(glance, 1.0)])), norm_new_rn_a(new_rows)),
        "running_now, no glance file": (norm_old_rn(old_collect_bridge([(None, 0)])), norm_new_rn_a(new_rows)),
    }
    for reader, (old, new) in rows.items():
        TALLY["compared"] += 1
        if old == new:
            TALLY["same"] += 1
            if reader in why_differs:
                check(False, "%s / %s: a difference was expected (%s) and none came" % (case, reader,
                                                                                         why_differs[reader]))
            continue
        why = why_differs.get(reader) or why_differs.get(reader.split(",")[1].strip())
        if why:
            TALLY["old_wrong"][why] = TALLY["old_wrong"].get(why, 0) + 1
            if not quiet:
                print("     differs, old wrong: %s / %s: old %s, new %s (%s)" % (case, reader, old, new, why))
        else:
            check(False, "%s / %s: unclassed difference" % (case, reader), "old %s, new %s" % (old, new))
    return new_pf, new_rows


NO_GLANCE = "a helper clone has no glance file: the old reader could not look"
NO_GLANCE_RN = "the dispatch and bench clones' glance files were absent: the old page could not look"


def blind(extra=None):
    d = {"preflight, no glance file": NO_GLANCE, "running_now, no glance file": NO_GLANCE_RN}
    d.update(extra or {})
    return d


# --- the fixture cases --------------------------------------------------------------------------------------------
def t_fixtures():
    s = sleeper()
    pf, rows = compare("both games free", why_differs=blind())
    check(pf == "PASS" and [r["state"] for r in rows] == ["FREE", "FREE"], "both free: PASS, two FREE rows")

    pf, rows = compare("held ArchBig (OPERATIONS, live), free ArchSmall", a=lock_body("OPERATIONS", s.pid),
                       why_differs=blind())
    check(pf == "FAIL" and rows[0]["state"] == "HELD" and rows[0]["who"] == "OPERATIONS" and rows[1]["state"] == "FREE",
          "held ArchBig, free ArchSmall: preflight FAIL; running_now reads both games", rows)

    pf, rows = compare("ArchBig held by this seat", a=lock_body("BENCH", s.pid), why_differs=blind())
    check(pf == "PASS", "a hold of this seat: PASS")

    pf, rows = compare("free ArchBig, held ArchSmall", b=lock_body("OPERATIONS", s.pid), why_differs=blind())
    check(rows[1]["state"] == "HELD" and rows[1]["who"] == "OPERATIONS",
          "running_now sees ArchSmall's holder (the old page never showed ArchSmall)", rows)
    os.environ["RM_GAME_INSTANCE"] = "b"
    try:
        # under RM_GAME_INSTANCE=b, RIMFLOW_DRIVER_LOCK names game b's lock (game_lock.lock_path, host_guard.instance_env)
        stage(a=lock_body("OPERATIONS", s.pid))
        glance = printed_glance()
        old, new = old_c_bridge_lease(glance, "BENCH", False)[0], preflight_bridge.c_bridge_lease(
            {"seat": "BENCH", "live": False}).status
        TALLY["compared"] += 1
        TALLY["old_wrong"]["a preflight for ArchSmall read ArchBig's glance line"] = 1
        check(old == "PASS" and new == "FAIL", "a preflight for ArchSmall reads ArchSmall's lock (old read ArchBig's: "
              "PASS beside a live ArchSmall holder)", (old, new))
    finally:
        os.environ.pop("RM_GAME_INSTANCE")

    pf, rows = compare("a dead holder", a=lock_body("OPERATIONS"), why_differs=blind())
    check(pf == "PASS" and rows[0]["state"] == "FREE", "a dead holder reads FREE at once")

    pf, rows = compare("his OWNER lock, process gone", a=lock_body("OWNER", purpose="his walk"), why_differs=blind())
    check(pf == "FAIL" and rows[0]["state"] == "HIS_HOLD", "his OWNER lock: FAIL, HIS_HOLD", rows)

    garbled = '{"seat": "BENCH", "identity": {"pid'
    pf, rows = compare("a garbled lock (planted fault)", a=garbled, why_differs={
        "preflight, glance printed": "a garbled lock printed FREE (the printer fell back to the empty ledger)",
        "running_now, glance printed": "a garbled lock printed FREE (the printer fell back to the empty ledger)",
    })
    check(pf == "UNMEASURED" and rows[0]["state"] == "UNKNOWN", "an unreadable lock is UNMEASURED, never FREE", rows)

    pf, rows = compare("pipe off game:ArchBig, game free", pipe_a="his walk", why_differs=blind({
        "preflight, glance printed": "his `pipe off game:ArchBig` was invisible to the glance file: PASS under his stop",
        "running_now, glance printed": "his `pipe off game:ArchBig` was invisible to the glance file: FREE under his stop",
    }))
    check(pf == "FAIL" and rows[0]["state"] == "HIS_HOLD", "a free game under his pipe hold: FAIL, HIS_HOLD", rows)

    pf, rows = compare("pipe off game:ArchBig, held by this seat", a=lock_body("BENCH", s.pid), pipe_a="his walk",
                       why_differs=blind())
    check(pf == "PASS", "the holder's own preflight under his pipe hold: PASS (the Conductor drives his walk)")

    pf, rows = compare("a control store that cannot be read, game free", control_bad=True, why_differs={
        "preflight, glance printed": "a store that cannot be read cannot rule out his pipe hold",
        "running_now, glance printed": "a store that cannot be read cannot rule out his pipe hold",
    })      # with no glance file both are blind: the same verdict, UNMEASURED
    check(pf == "UNMEASURED" and rows[0]["state"] == "UNKNOWN", "an unreadable control store: UNMEASURED", rows)

    # a stale glance file (the 2:25 AM release that left it saying HELD) against a free lock
    stage()
    stale = "# x\nHELD OPERATIONS since 2026-11-21T10:25:00Z\nfor a run that ended\n"
    old = old_c_bridge_lease(stale, "BENCH", False)[0]
    new = preflight_bridge.c_bridge_lease({"seat": "BENCH", "live": False}).status
    TALLY["compared"] += 1
    TALLY["old_wrong"]["a stale glance file named a holder that had gone"] = 1
    check(old == "FAIL" and new == "PASS", "a stale glance file no longer decides (old FAIL, new PASS)", (old, new))

    # no reader opens a glance file: a planted one that lies changes nothing
    with open(GLANCE, "w") as f:
        f.write(stale)
    saved = running_now.Env.read_text
    opened = []
    running_now.Env.read_text = lambda self, p: opened.append(p) or saved(self, p)
    try:
        rows = running_now.collect_bridge(LiveEnv())
    finally:
        running_now.Env.read_text = saved
    check(rows[0]["state"] == "FREE" and not opened, "a planted, lying glance file is never read", (rows, opened))


# --- the recorded inputs (read only: each is copied into the throwaway lock) ---------------------------------------
def t_recorded():
    root = driver_lock.DEFAULT and os.path.dirname(os.path.dirname(driver_lock.DEFAULT))
    os.environ.pop("RIMFLOW_DRIVER_LOCK")      # only to find the live paths
    live_a = driver_lock.DEFAULT
    os.environ["RIMFLOW_DRIVER_LOCK"] = A_LOCK
    found = sorted(set(glob.glob(live_a + "*") + glob.glob(os.path.join(root, "instances", "*", "DRIVER_LOCK.json*"))))
    found = [p for p in found if not p.endswith(".gen") and os.path.isfile(p)]
    if not found:
        print("UNMEASURED recorded locks: none under %s" % root)
        return
    s = sleeper()
    seats, n0 = {}, TALLY["compared"]
    for p in found:
        with open(p, encoding="utf-8", errors="replace") as f:
            raw = f.read()
        try:
            body = json.loads(raw)
        except ValueError:
            body = raw
        seat = body.get("seat") if isinstance(body, dict) else "?"
        seats[seat] = seats.get(seat, 0) + 1
        compare("recorded %s, as kept" % os.path.basename(p), a=body, why_differs=blind(), quiet=True)
        if isinstance(body, dict):
            alive = dict(body, identity=ident_of(s.pid))
            compare("recorded %s, holder made live" % os.path.basename(p), a=alive, why_differs=blind(), quiet=True)
    print("recorded locks: %d files (%s), %d reader comparisons" % (
        len(found), ", ".join("%s %d" % kv for kv in sorted(seats.items(), key=str)), TALLY["compared"] - n0))

    # every BRIDGE glance file of a clone on this machine, against the live locks now
    stage()
    os.environ.pop("RIMFLOW_DRIVER_LOCK")
    os.environ.pop("RM_INSTANCES_ROOT")
    os.environ.pop("RIMFLOW_LEDGER")
    os.environ.pop("RM_CONTROL_DB")
    try:
        now_a = game_lock.query("a")
        files = sorted(glob.glob("/home/mandrake/rm/*/infrastructure/state/BRIDGE") +
                       glob.glob("/home/mandrake/rm/relentless/clones/*/infrastructure/state/BRIDGE"))
        agree = 0
        for p in files:
            with open(p, encoding="utf-8", errors="replace") as f:
                old = old_c_bridge_lease(f.read(), "BENCH", False)[0]
            new = preflight_bridge.c_bridge_lease({"seat": "BENCH", "live": False}).status
            agree += old == new
            print("     glance file %s: old %s, new %s (ArchBig's lock now: %s)" % (p, old, new, now_a["line"][:90]))
        TALLY["compared"] += len(files)
        TALLY["same"] += agree
        if len(files) - agree:
            TALLY["old_wrong"]["a clone's glance file disagreed with the lock now (stale, or blind to his pipe hold)"] = \
                len(files) - agree
        print("recorded glance files: %d, agree with the lock now %d" % (len(files), agree))
    finally:
        os.environ.update(RIMFLOW_DRIVER_LOCK=A_LOCK, RM_INSTANCES_ROOT=INST,
                          RIMFLOW_LEDGER=os.path.join(TMP, "events.jsonl"), RM_CONTROL_DB=CONTROL)


def main():
    try:
        t_fixtures()
        if "--recorded" in sys.argv:
            t_recorded()
    finally:
        for p in SLEEPERS:
            p.kill()
        shutil.rmtree(TMP, True)
    print("\ncompared %d reader verdicts: %d the same; old wrong: %s" % (
        TALLY["compared"], TALLY["same"], "; ".join("%s (%d)" % kv for kv in TALLY["old_wrong"].items()) or "none"))
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
