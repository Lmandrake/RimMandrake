#!/usr/bin/env python3
"""selftest_game_driver_readers.py - the equivalence run of the readers moved off the BRIDGE glance file.

Items RIMMANDRAKE_MOVE_GAME_DRIVER_READERS_OFF_BRIDGE_FILE_TWO_LEFT (`preflight_bridge.c_bridge_lease`) and RIMMANDRAKE_MOVE_TWO_MORE_GLANCE_READERS_CENSUS_MISSED (`handoff.bridge_lines`, the
handoff's "- Bridge:" lines, and FlowWorks's `preflight_flowworks.p_b1`, row P-B1). Each now reads each game's driver
lock through `game_lock.query`, and the glance file and its printer are deleted. This runs the OLD readers (frozen
copies of their code at 88fccbe8d6 and 2d45788d5c, below) and the NEW ones on the same lock states and compares their
verdicts:

  old path: the lock -> the glance file the printer wrote from it (a frozen copy of `cli._mirror_bridge` and
            `model.bridge_body`, both deleted) -> the old reader of that file; and the old reader with no glance file
            at all (a helper clone has none; the old P-B1 then asked `rimflow bridge who`)
  new path: the lock -> the three readers above, and `game_lock.py query all`

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
import bridge_holder  # noqa: E402
import handoff  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "FlowWorks", "northstar"))
import preflight_flowworks as PF  # noqa: E402

# RIMFLOW_LEDGER alone redirects nothing for an imported cli: only cli.main() calls _bind_paths. Unbound, the frozen
# printer's ledger fallback (cli.load, cli._bridge_who) read the clone's REAL ledger, so P-B1 for ArchSmall turned
# red whenever the live ledger's last ArchBig take was BENCH's (2026-11-22, RIMMANDRAKE_MEND_GLANCE_READER_ARCHSMALL_
# LOCK_READS_WRONG). Every verdict here is a reading of the throwaway locks and this empty throwaway ledger only.
cli._bind_paths()

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


def old_handoff_bridge(text):
    """handoff.py's "- Bridge:" value as it was (2d45788d5c): the LAST non-comment line of its clone's glance file, or
    "unknown" when the clone had none. text: the file's text, or None for no file."""
    if text is None:
        return "unknown"
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    return (lines[-1] if lines else "") or "unknown"


def old_p_b1(text, who_out, seat):
    """preflight_flowworks.p_b1 as it was (2d45788d5c), past its tools check: its clone's glance file when one existed,
    else `rimflow bridge who`'s output (who_out: (rc, text))."""
    if text is not None:
        holder = text.strip()
    else:
        rc, out = who_out
        holder = out.strip() if rc == 0 else None
    if holder is None:
        return "UNMEASURED"
    return "PASS" if bridge_holder.held_by(holder) == bridge_holder.identity(seat) else "FAIL"


# the printer, frozen at 2d45788d5c (cli._mirror_bridge + model.bridge_body, both deleted with the glance file)
OLD_HEADER = (
    "# WHO IS DRIVING THE LIVE RIMWORLD BRIDGE.\n"
    "# A print of each game's driver lock (game_lock.py). Written by `rimflow bridge`, never by hand.\n"
    "#   free?  ->  rimflow bridge take --for \"<what for>\"\n"
    "#   held?  ->  do offline work. Nobody will come and tell you it freed; look again.\n"
    "#   wrong? ->  rimflow bridge who   (prints this again from the lock)\n")


def old_bridge_body(holder, actor, purpose=None, since=None, note=None, others=None):
    if holder:
        line = "HELD    %s    since %s" % (holder, since or "now")
        if purpose:
            line += "\nfor     %s" % purpose
    else:
        line = "FREE    since %s" % (since or "now")
        if actor:
            line += "    (released by %s)" % actor
    if note:
        line += "\nnote    %s" % note
    for key, ent in sorted((others or {}).items()):
        line += "\nother   %s  %s  since %s%s" % (game_lock.game_names.show_key(key), ent["holder"],
                                               ent.get("since") or "?",
                                               "  for: %s" % ent["purpose"] if ent.get("purpose") else "")
    return OLD_HEADER + line + "\n"


def old_print_glance(actor=None, note=None):
    """The glance file's text as `rimflow bridge who` printed it from the locks (cli._mirror_bridge, frozen)."""
    _, w3 = cli.load()
    r = cli.lock_reading()
    others = {}
    for k in sorted(set(cli.model.BRIDGE_HOSTS) | set(w3.bridge_hosts)):
        if k == cli.model.DEFAULT_BRIDGE_HOST:
            continue
        rk = cli.lock_reading(k)
        if rk is not None:
            if cli.lock_holder(rk):
                others[k] = {"holder": cli.lock_holder(rk), "since": rk.get("since"), "purpose": rk.get("purpose")}
        elif (w3.bridge_hosts.get(k) or {}).get("holder"):
            others[k] = w3.bridge_hosts[k]
    if r is None:
        holder, purpose, since = w3.bridge_holder, w3.bridge_purpose, w3.bridge_since
    else:
        holder, purpose, since = cli.lock_holder(r), r.get("purpose"), r.get("since")
    return old_bridge_body(holder, actor, purpose if holder else None, since if holder else None, note=note,
                           others=others)


def bridge_who_out():
    """`rimflow bridge who`, run in this process on the throwaway locks: (rc, stdout)."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = cli._bridge_who()
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
    return rc or 0, buf.getvalue()


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
    """The glance file the old system would hold for these locks (the printer `rimflow bridge who` ran, frozen)."""
    return old_print_glance()


class _Tools(object):
    tools = ["jawa/map_info"]          # P-B1 checks only that the bridge answered with tools


def new_p_b1(seat):
    return PF.p_b1(_Tools(), PF.Paths(), None, seat).status


def new_handoff_lines():
    """handoff.bridge_lines(), or [] when the new reader is not there (a red run on the base)."""
    f = getattr(handoff, "bridge_lines", None)
    return f() if f else []


def norm_old_handoff(v):
    """The old handoff value in reader terms: (HELD, who) / (FREE, "") for a status line, else the line itself."""
    m = re.match(r"(HELD|FREE)\b\s*(?!since\b)(\S*)", v or "")
    return (m.group(1), m.group(2) or "") if m else ("NOT A STATUS", v)


def norm_new_handoff(lines):
    """ArchBig's handoff line in the old value's terms."""
    a = [ln for ln in lines if ln.startswith("ArchBig:")]
    if not a:
        return ("MISSING", "")
    m = re.match(r"ArchBig: (FREE|HELD by (\S+)|HIS HOLD: (?:his OWNER hold, (\S+)|HELD by (\S+))?|COULD NOT LOOK)", a[0])
    if not m:
        return ("NOT A STATUS", a[0])
    if m.group(1).startswith("HELD"):
        return ("HELD", m.group(2))
    if m.group(1).startswith("HIS HOLD"):
        who = m.group(3) or m.group(4)
        return ("HELD", who) if who else ("HIS_HOLD", "")
    return ("FREE", "") if m.group(1) == "FREE" else ("UNKNOWN", "")


def query_all_cli():
    r = subprocess.run([sys.executable, os.path.join(HERE, "game_lock.py"), "query", "all"], capture_output=True,
                       text=True, timeout=60)
    return [ln for ln in r.stdout.splitlines() if ln.startswith(("ArchBig:", "ArchSmall:"))]


def every_game():
    """One row per game of this machine, as MATURATION_NOW's games line reads them (game_lock.query_all)."""
    import game_names
    return [{"game": game_names.show(r.get("game")), "state": r.get("state"), "who": r.get("seat") or "", "line": r.get("line")}
            for r in game_lock.query_all()]


def compare(case, a=None, b=None, pipe_a=None, control_bad=False, seat="BENCH", why_differs=None, quiet=False):
    """Run the old and new readers on one world. why_differs: {reader: reason} for the differences the old reader is
    known to get wrong; any other difference fails."""
    why_differs = why_differs or {}
    stage(a, b, pipe_a, control_bad)
    glance = printed_glance()
    ctx = {"seat": seat, "live": False}
    new_pf = preflight_bridge.c_bridge_lease(ctx).status
    new_rows = every_game()
    new_b1 = new_p_b1(seat)
    new_ho = new_handoff_lines()
    who = bridge_who_out()
    lines = query_all_cli()
    same_ho = new_ho == lines
    if not (same_ho and quiet):
        check(same_ho, "%s: the handoff's Bridge lines are `game_lock.py query all`'s" % case, (new_ho, lines))
    same = [r["line"] for r in new_rows] == lines
    if not (same and quiet):
        check(same, "%s: query_all reads every game as `game_lock.py query all`" % case,
              ([r["line"] for r in new_rows], lines))
    rows = {
        "preflight, glance printed": (old_c_bridge_lease(glance, seat, False)[0], new_pf),
        "preflight, no glance file": (old_c_bridge_lease(None, seat, False)[0], new_pf),
        "P-B1, glance printed": (old_p_b1(glance, who, seat), new_b1),
        "P-B1, no glance file": (old_p_b1(None, who, seat), new_b1),
        "handoff, glance printed": (norm_old_handoff(old_handoff_bridge(glance)), norm_new_handoff(new_ho)),
        "handoff, no glance file": (norm_old_handoff(old_handoff_bridge(None)), norm_new_handoff(new_ho)),
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
        if not why and reader == "handoff, glance printed" and old[0] == "NOT A STATUS" and \
                re.match(r"(for|note|other)\s", old[1] or ""):
            why = LAST_LINE
        if why:
            TALLY["old_wrong"][why] = TALLY["old_wrong"].get(why, 0) + 1
            if not quiet:
                print("     differs, old wrong: %s / %s: old %s, new %s (%s)" % (case, reader, old, new, why))
        else:
            check(False, "%s / %s: unclassed difference" % (case, reader), "old %s, new %s" % (old, new))
    return new_pf, new_rows


NO_GLANCE = "a helper clone has no glance file: the old reader could not look"


NO_GLANCE_HO = "a helper clone has no glance file: the handoff wrote 'Bridge: unknown'"
LAST_LINE = "the handoff took the glance file's LAST line: a for/note/other line, not the status line"
GARBLED = "a garbled lock printed FREE (the printer fell back to the empty ledger)"
PIPE_HIDDEN = "his `pipe off game:ArchBig` was invisible to the glance file"


def blind(extra=None):
    d = {"preflight, no glance file": NO_GLANCE,
         "handoff, no glance file": NO_GLANCE_HO}
    d.update(extra or {})
    return d


# --- the fixture cases --------------------------------------------------------------------------------------------
def t_fixtures():
    evs = cli.load()[0]
    check(os.path.realpath(cli.model.shard_dir()).startswith(os.path.realpath(TMP)) and not evs,
          "the readers read only this test's throwaway ledger (empty), never the clone's live one",
          (cli.model.EVENTS, len(evs)))
    s = sleeper()
    pf, rows = compare("both games free", why_differs=blind())
    check(pf == "PASS" and [r["state"] for r in rows] == ["FREE", "FREE"], "both free: PASS, two FREE rows")

    pf, rows = compare("held ArchBig (OPERATIONS, live), free ArchSmall", a=lock_body("OPERATIONS", s.pid),
                       why_differs=blind())
    check(pf == "FAIL" and rows[0]["state"] == "HELD" and rows[0]["who"] == "OPERATIONS" and rows[1]["state"] == "FREE",
          "held ArchBig, free ArchSmall: preflight FAIL; query_all reads both games", rows)

    pf, rows = compare("ArchBig held by this seat", a=lock_body("BENCH", s.pid), why_differs=blind())
    check(pf == "PASS", "a hold of this seat: PASS")

    pf, rows = compare("free ArchBig, held ArchSmall", b=lock_body("OPERATIONS", s.pid), why_differs=blind())
    check(rows[1]["state"] == "HELD" and rows[1]["who"] == "OPERATIONS",
          "query_all sees ArchSmall's holder", rows)
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
        stage(a=lock_body("BENCH", s.pid))           # the path ArchSmall's lock has under RM_GAME_INSTANCE=b
        glance = printed_glance()
        old, new = old_p_b1(glance, bridge_who_out(), "BENCH"), new_p_b1("BENCH")
        TALLY["compared"] += 1
        TALLY["old_wrong"]["P-B1 for ArchSmall read ArchBig's glance line"] = 1
        check(old == "FAIL" and new == "PASS", "P-B1 for ArchSmall reads ArchSmall's lock (old read ArchBig's: FAIL "
              "while this seat held ArchSmall)", (old, new))
    finally:
        os.environ.pop("RM_GAME_INSTANCE")

    pf, rows = compare("a dead holder", a=lock_body("OPERATIONS"), why_differs=blind())
    check(pf == "PASS" and rows[0]["state"] == "FREE", "a dead holder reads FREE at once")

    compare("a dead holder of this seat", a=lock_body("BENCH"), why_differs=blind())
    check(new_p_b1("BENCH") == "FAIL", "P-B1: a lock of this seat whose process is gone is not this seat's hold")

    compare("a live holder whose seat shares a first letter (BUILD)", a=lock_body("BUILD", s.pid), why_differs=blind())
    check(new_p_b1("BENCH") == "FAIL", "P-B1: another seat's hold (BUILD) is never this seat's (BENCH)")

    pf, rows = compare("his OWNER lock, process gone", a=lock_body("OWNER", purpose="his walk"), why_differs=blind())
    check(pf == "FAIL" and rows[0]["state"] == "HIS_HOLD", "his OWNER lock: FAIL, HIS_HOLD", rows)

    garbled = '{"seat": "BENCH", "identity": {"pid'
    pf, rows = compare("a garbled lock (planted fault)", a=garbled, why_differs={
        "preflight, glance printed": GARBLED, "P-B1, glance printed": GARBLED,
        "handoff, glance printed": GARBLED, "handoff, no glance file": NO_GLANCE_HO,
    })
    check(new_p_b1("BENCH") == "UNMEASURED" and new_handoff_lines()[:1] and
          new_handoff_lines()[0].startswith("ArchBig: COULD NOT LOOK"),
          "a garbled lock: P-B1 UNMEASURED and the handoff says COULD NOT LOOK, never FREE", new_handoff_lines())
    check(pf == "UNMEASURED" and rows[0]["state"] == "UNKNOWN", "an unreadable lock is UNMEASURED, never FREE", rows)

    pf, rows = compare("pipe off game:ArchBig, game free", pipe_a="his walk", why_differs=blind({
        "preflight, glance printed": "his `pipe off game:ArchBig` was invisible to the glance file: PASS under his stop",
        "handoff, glance printed": PIPE_HIDDEN + ": the handoff said FREE under his stop",
    }))
    check(pf == "FAIL" and rows[0]["state"] == "HIS_HOLD", "a free game under his pipe hold: FAIL, HIS_HOLD", rows)

    pf, rows = compare("pipe off game:ArchBig, held by this seat", a=lock_body("BENCH", s.pid), pipe_a="his walk",
                       why_differs=blind())
    check(pf == "PASS", "the holder's own preflight under his pipe hold: PASS (the Conductor drives his walk)")

    pf, rows = compare("a control store that cannot be read, game free", control_bad=True, why_differs={
        "preflight, glance printed": "a store that cannot be read cannot rule out his pipe hold",
        "handoff, glance printed": "a store that cannot be read cannot rule out his pipe hold",
        "handoff, no glance file": NO_GLANCE_HO,
    })      # with no glance file both are blind: the same verdict, UNMEASURED
    check(new_p_b1("BENCH") == "FAIL", "an unreadable control store: P-B1 still reads the lock (free: not this seat's)")
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
    # the handoff and P-B1 open no glance file (a clone's own, at infrastructure/state/BRIDGE, or any other)
    import builtins
    import io as _io
    real_open, real_io_open, seen = builtins.open, _io.open, []

    def spy(f, *a, **k):
        if os.path.basename(str(f)) == "BRIDGE":
            seen.append(f)
        return real_open(f, *a, **k)
    builtins.open = _io.open = spy
    try:
        b1, ho = new_p_b1("BENCH"), new_handoff_lines()
    finally:
        builtins.open, _io.open = real_open, real_io_open
    check(b1 == "FAIL" and ho[:1] and ho[0].startswith("ArchBig: FREE") and not seen,
          "the handoff and P-B1 never open a glance file", (b1, ho, seen))
    check(not hasattr(cli, "_mirror_bridge") and not hasattr(cli.model, "write_bridge_file") and
          not hasattr(cli.model, "bridge_mirror_path"), "the glance file's printer is gone (cli._mirror_bridge, "
          "model.write_bridge_file, model.bridge_mirror_path)")


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
                       glob.glob("/home/mandrake/rm/runs/clones/*/infrastructure/state/BRIDGE"))
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
