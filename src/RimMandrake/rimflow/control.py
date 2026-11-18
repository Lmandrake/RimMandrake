#!/usr/bin/env python3
"""control: the ONE control store of the Maturation Pipeline, and `pipe`, its one-line command surface.

Item RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS; design
design/specs/2026-11-18-pipeline-control-surface/03-merged.md (option M: SQLite, a library, no daemon).

The owner, 2026-11-18 ~10:40 AM PST: "This should be a one-line bash command, ok? Build that immediately. No more wasting
time and tokens on trivial pipeline commanding. ... Individual items should be trivially switchable on and off."
~11:02 AM PST: "we are going to have. System that is instantly responsive by the time we are done here. This is not
beyond our technology to achieve."
By card, 2026-11-18 (asked 11:04 AM PST, answered by 11:25 AM PST): a void run's spend does not count toward the stage
ceiling; stopping is three explicit commands: "Stop work immediately and write where you are." "Stop work at the next
easy spot and write where you are." "STOP NOW without write." (the at-easy-spot one is the default, but "we shouldn't
rely on defaults. The agent should be precise in its instruction and use the right option.") ~11:28 AM PST: "there
should even be an option just to force kill the agent, period. Not just send it a nudge to die swiftly."

The store is one SQLite file (WAL) on ext4, outside every clone: ~/.local/state/rimmandrake/control/control.db
(RM_CONTROL_DB overrides; a selftest process that names none gets its own empty file). Control state never needs a
publish, a clone or git: an act binds the moment its transaction commits, because every launch reads the store at the
moment of launch (admit) and again when the unit itself starts (its ExecCondition, the `condition` verb).

  switches      one row per (scope, layer). scope: all | mod:<M> | stage:<S> | item:<ID> | family:<F> | role:<R>.
                layer: control (`pipe off`, `pipe stop`, `maturation_dispatch.py pause`) or owner (his hold, imported
                from mod_owner_hold.json with his words). Any live row on one of a run's scopes refuses it. `pipe on`
                lifts the control row only: his owner row stays (`mod_owner_hold.py lift` lifts it, with his words).
  runs          every admitted launch: the unit name fixed BEFORE systemd-run, family, mod, item, stage, role, model.
                state: admitted -> started (its ExecCondition passed) -> ended | killed; or cancelled (a `pipe off`
                committed first), refused (the condition found it no longer authorised), fail_launch (systemd-run said
                no), abandoned (reconcile: it never started and its launcher is gone).
  reservations  a consumable held for a run: held -> charged at VALIDATED settlement, or released; charged -> voided.
  grants        more of a consumable for a mod in one accounting window (`pipe grant <Mod> look +N`).
  voids         one row per voided run; voiding twice changes nothing. A void never moves a stage.
  faults        the system-fault meter: every fail_system settlement (its own alarm, FAULT_LIMIT a day per mod). A void
                or a system fault charges nothing and its spend is not the mod's (card, 2026-11-18).
  stops         a stop order for a live run (`pipe stop --write-now | --at-easy-spot`), delivered INTO the running agent
                by its Claude Code PostToolUse hook (`hook` verb: one indexed lookup, silent when there is none).
  acts          the append-only audit: id, revision, who, UTC and Pacific time, why, his words, before, after.

The pause ordering contract (critique 2 of 02-gpt.md): `pipe off` commits a new revision AND cancels every
admitted-but-unstarted run in its scope in ONE transaction; every unit launch_unit starts carries
`ExecCondition=control.py condition <run>`, which in one transaction either marks the run started (still admitted, no
switch blocks it) or marks it refused and releases its reservations. So after `pipe off` returns, nothing that had not
already passed its condition can begin; one that had is reported live, and `pipe stop` stops it.

An unreadable, missing, corrupt or locked store: admit refuses everything (CONTROL UNREADABLE: <cause>), the condition
skips the unit, `pipe show` prints `CONTROL UNREADABLE: <cause>` (never "nothing is off"), and `pipe doctor` names the
fix. `pipe init --import` is the only thing that creates the production store. `pipe stop <unit> --kill` still kills by
unit name when the store cannot be read (emergency stopping never waits on it).

  pipe on|off <all|Mod|stage|item|family:F|role:R> --why ... [--owner-said ...]
  pipe stop <scope|unit> --write-now|--at-easy-spot|--kill --why ... [--deadline 5m]
  pipe show [Mod] [--json]   pipe why <Mod>   pipe log [-n N]
  pipe void <run> --why ...   pipe grant <Mod> look +N --why ... --owner-said ...|--per-ruling ...
  pipe set|add|reset|limit|queue|undo ...   (consumable counts, limits and the queue: pipeline_control.py)
  pipe init [--import]   pipe doctor
Exit codes: 0 done, 2 refused, 3 could not look (the store is unreadable), 4 failed (an error that is neither).
Every write prints at most 3 lines (before -> after; act id + revision; the undo command). Selftest: selftest_control.py.
"""
import argparse
import datetime as dt
import difflib
import json
import os
import signal
import socket
import sqlite3
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCHEMA_VERSION = 1
DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".local", "state", "rimmandrake", "control", "control.db")
TICK_UNIT = "rm-maturation-dispatch.service"
OK, REFUSED, UNREADABLE, FAILED = 0, 2, 3, 4
LAUNCH_REFUSED_RC = 75              # the rc launch_unit returns for a refused launch (systemd-run was never called)
FAULT_LIMIT = 3                     # fail_system settlements per mod in 24 h before the system-fault alarm
LAYERS = ("control", "owner")
FAMILIES = {                        # the 7 launch families of the re-measure (02m-remeasure.md), plus the test probe
    "detached": "detached_helper.launch (rm-detached-*): builders, stewards, fixers, holders, judges",
    "role": "role_launch.launch (rm-role-*): the Dispatcher's scheduled roles and the Designer chain",
    "relentless": "relentless*.py (retired by the owner 2026-11-13): OFF from the import on",
    "designer_cleanse": "designer_cleanse.py fleet unit",
    "cert_rerun": "maturation_dispatch.cert_rerun_unit",
    "stop_resume": "stop_resume.py sweep unit",
    "testq": "testq/steward.py wake unit",
    "probe": "selftest probes (rm-probe-*)",
}
STAGES = ("intake", "designer", "preflight", "offline_build", "blind_challenge", "in_game", "pre_human", "his_walk",
          "passed")
STOP_MODES = ("write_now", "at_easy_spot", "kill")
DEFAULT_STOP_MODE = "at_easy_spot"  # his default (card 2026-11-18); `pipe` always prints which mode it used
WRITE_NOW_DEADLINE_S = 300
KILL_WAIT_S = 1.0
UNM = "UNMEASURED"
LIVE_STATES = ("admitted", "started")
NEVER_RAN = ("fail_launch", "refused")    # its unit ended without its payload (a cancelled or abandoned one may still start: fenced)
SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS acts (id TEXT PRIMARY KEY, rev INTEGER NOT NULL UNIQUE, ts REAL NOT NULL, at TEXT,
  at_pacific TEXT, who TEXT, kind TEXT NOT NULL, scope TEXT, before TEXT, after TEXT, why TEXT NOT NULL, owner_said TEXT,
  per_ruling TEXT, idem TEXT UNIQUE, undoes TEXT);
CREATE TABLE IF NOT EXISTS switches (scope TEXT NOT NULL, layer TEXT NOT NULL, why TEXT NOT NULL, said TEXT, date TEXT,
  until REAL, act TEXT, at_pacific TEXT, who TEXT, extra TEXT, PRIMARY KEY (scope, layer));
CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, unit TEXT NOT NULL UNIQUE, family TEXT NOT NULL, mod TEXT,
  item TEXT, stage TEXT, role TEXT, model TEXT, state TEXT NOT NULL, rev INTEGER, admitted_at REAL, started_at REAL,
  ended_at REAL, result TEXT, why TEXT, pid INTEGER, host TEXT, spec TEXT);
CREATE TABLE IF NOT EXISTS reservations (id INTEGER PRIMARY KEY AUTOINCREMENT, run TEXT NOT NULL, mod TEXT NOT NULL,
  resource TEXT NOT NULL, win TEXT NOT NULL DEFAULT '', qty INTEGER NOT NULL, state TEXT NOT NULL, at REAL,
  settled_at REAL, why TEXT, pid INTEGER, host TEXT, UNIQUE (run, mod, resource, win));
CREATE TABLE IF NOT EXISTS grants (id INTEGER PRIMARY KEY AUTOINCREMENT, mod TEXT NOT NULL, resource TEXT NOT NULL,
  win TEXT NOT NULL DEFAULT '', qty INTEGER NOT NULL, act TEXT, why TEXT, owner_said TEXT, at REAL);
CREATE TABLE IF NOT EXISTS voids (run TEXT PRIMARY KEY, mod TEXT, act TEXT, why TEXT, owner_said TEXT, at REAL);
CREATE TABLE IF NOT EXISTS faults (id INTEGER PRIMARY KEY AUTOINCREMENT, run TEXT, mod TEXT, resource TEXT, why TEXT,
  at REAL);
CREATE TABLE IF NOT EXISTS refusals (id INTEGER PRIMARY KEY AUTOINCREMENT, at REAL, unit TEXT, family TEXT, mod TEXT,
  why TEXT);
CREATE TABLE IF NOT EXISTS stops (id INTEGER PRIMARY KEY AUTOINCREMENT, unit TEXT NOT NULL, run TEXT, mode TEXT NOT NULL,
  act TEXT, why TEXT, at REAL, deadline REAL, state TEXT NOT NULL, seen_at REAL, seen_n INTEGER DEFAULT 0,
  ended_at REAL, said TEXT);
CREATE INDEX IF NOT EXISTS runs_state ON runs (state);
CREATE INDEX IF NOT EXISTS res_acct ON reservations (mod, resource, win, state);
CREATE INDEX IF NOT EXISTS stops_unit ON stops (unit, state);
"""


class Unreadable(Exception):
    """The store cannot be consulted: nothing launches on it ("could not look", never "nothing is off")."""


class Refused(Exception):
    pass


# ---------------------------------------------------------------- the store

def db_path():
    """RM_CONTROL_DB, else (a test process: RM_UNDER_SELFTEST, or a test that pointed the owner hold at its own file) a
    store of its own, empty and initialised, so a test never reads or writes the live one; else the live store."""
    p = os.environ.get("RM_CONTROL_DB")
    if p:
        return p
    if test_process():
        import tempfile
        d = os.path.join(tempfile.gettempdir(), "rm-control-selftest")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "control-%d.db" % os.getpid())
        if not os.path.exists(p):
            init(p)
        os.environ["RM_CONTROL_DB"] = p     # its children read and write the same test store
        return p
    return DEFAULT_DB


def test_process():
    """True in a test: the selftest harness (RM_UNDER_SELFTEST), a test that pointed the owner hold at its own file, a
    selftest_* script run directly, or a process whose dispatcher state is not the live one. A test never reaches the
    live store."""
    if os.environ.get("RM_UNDER_SELFTEST") or os.environ.get("RM_OWNER_HOLD_FILE"):
        return True
    if os.path.basename(sys.argv[0] if sys.argv else "").startswith("selftest"):
        return True
    st = os.environ.get("RM_DISPATCHER_STATE")
    if st:
        try:
            sys.path.insert(0, HERE) if HERE not in sys.path else None
            import doorbell
            return os.path.abspath(st) != os.path.abspath(doorbell.DEFAULT_STATE)
        except Exception:       # noqa: BLE001  cannot tell: treat it as a test (never write the live store blind)
            return True
    return False


def is_live(p=None):
    return os.path.abspath(p or db_path()) == os.path.abspath(DEFAULT_DB)


def _err(e):
    s = str(e)
    if "locked" in s or "busy" in s:
        return "locked (another writer holds it past the timeout): %s" % s
    if "not a database" in s or "malformed" in s or "corrupt" in s:
        return "corrupt: %s" % s
    if "disk" in s and ("full" in s or "I/O" in s):
        return "disk: %s" % s
    return "%s: %s" % (type(e).__name__, s)


def connect(p=None, timeout=3.0):
    """-> an open connection to an initialised store. Raises Unreadable (with its cause) on anything else."""
    p = p or db_path()
    if not os.path.exists(p):
        raise Unreadable("not initialised: %s does not exist (create it with `pipe init --import`)" % p)
    if not os.access(p, os.R_OK | os.W_OK):
        raise Unreadable("permission denied on %s" % p)
    try:
        c = sqlite3.connect(p, timeout=timeout, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA busy_timeout=%d" % int(timeout * 1000))
        row = c.execute("SELECT v FROM meta WHERE k='schema'").fetchone()
    except sqlite3.Error as e:
        raise Unreadable("%s: %s" % (p, _err(e)))
    if not row or row[0] != str(SCHEMA_VERSION):
        c.close()
        raise Unreadable("%s: schema %s, this code reads %d" % (p, row[0] if row else "absent", SCHEMA_VERSION))
    return c


def init(p=None):
    """Create the store (idempotent). -> path."""
    p = p or db_path()
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    c = sqlite3.connect(p, timeout=5, isolation_level=None)
    try:
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript(SCHEMA)
        c.execute("INSERT OR IGNORE INTO meta VALUES ('schema', ?)", (str(SCHEMA_VERSION),))
        c.execute("INSERT OR IGNORE INTO meta VALUES ('rev', '0')")
        c.execute("INSERT OR IGNORE INTO meta VALUES ('initialised', ?)", (pac(time.time()),))
    finally:
        c.close()
    return p


class txn:
    """BEGIN IMMEDIATE ... COMMIT on a fresh connection: every write is one serialised transaction."""

    def __init__(self, p=None, timeout=3.0):
        self.p, self.timeout = p, timeout

    def __enter__(self):
        self.c = connect(self.p, self.timeout)
        try:
            self.c.execute("BEGIN IMMEDIATE")
        except sqlite3.Error as e:
            self.c.close()
            raise Unreadable("%s: %s" % (self.p or db_path(), _err(e)))
        return self.c

    def __exit__(self, et, ev, tb):
        try:
            if et is None:
                try:
                    self.c.execute("COMMIT")
                except sqlite3.Error as e:
                    self.c.execute("ROLLBACK")
                    raise Unreadable("commit failed: %s" % _err(e))
            else:
                self.c.execute("ROLLBACK")
        finally:
            self.c.close()
        if isinstance(ev, sqlite3.Error):
            raise Unreadable(_err(ev))
        return False


def read(p=None, timeout=1.5):
    """A connection for reads (WAL: a reader never waits on a writer)."""
    return connect(p, timeout)


def _q(sql, args=(), p=None, one=False):
    c = read(p)
    try:
        cur = c.execute(sql, args)
        r = cur.fetchone() if one else cur.fetchall()
        return (dict(r) if r else None) if one else [dict(x) for x in r]
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()


def who():
    seat = (os.environ.get("AGENT_SEAT") or os.environ.get("RIMFLOW_SEAT") or os.environ.get("USER") or "?").strip()
    return "%s@%s" % (seat, socket.gethostname())


def pac(t):
    try:
        from zoneinfo import ZoneInfo
        z = ZoneInfo("America/Los_Angeles")
    except Exception:       # noqa: BLE001  no tz database: say so rather than print UTC as Pacific
        return UNM
    return dt.datetime.fromtimestamp(t, z).strftime("%Y-%m-%d %I:%M:%S %p %Z")


def utc(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rev(c):
    return int(c.execute("SELECT v FROM meta WHERE k='rev'").fetchone()[0])


def _act(c, kind, scope, before, after, why, owner_said=None, per_ruling=None, idem=None, undoes=None, now=None):
    """Write one act inside the caller's transaction (bumps the revision). -> the act row as a dict."""
    if not (isinstance(why, str) and why.strip()):
        raise Refused("--why is required")
    now = time.time() if now is None else now
    r = rev(c) + 1
    c.execute("UPDATE meta SET v=? WHERE k='rev'", (str(r),))
    aid = "ct_%06d" % r
    row = {"id": aid, "rev": r, "ts": now, "at": utc(now), "at_pacific": pac(now), "who": who(), "kind": kind,
           "scope": scope, "before": json.dumps(before, sort_keys=True, default=str),
           "after": json.dumps(after, sort_keys=True, default=str), "why": why.strip(), "owner_said": owner_said,
           "per_ruling": per_ruling, "idem": idem, "undoes": undoes}
    c.execute("INSERT INTO acts (%s) VALUES (%s)" % (",".join(row), ",".join("?" * len(row))), list(row.values()))
    return row


def _idem_hit(c, idem):
    if not idem:
        return None
    r = c.execute("SELECT * FROM acts WHERE idem=?", (idem,)).fetchone()
    return dict(r) if r else None


# ---------------------------------------------------------------- scopes and switches

def key(name):
    return os.path.basename(os.path.normpath(str(name or "")))


def concepts_dir():
    return os.environ.get("RM_CONTROL_CONCEPTS") or os.path.join(REPO, "design", "concepts")


def known_mods(advancing_only=False):
    """-> the pipeline's mods: maturation_dispatch.json's advancing list, then (unless advancing_only) every concept
    folder (this tree's). RM_CONTROL_MODS="A,B" names them for a test."""
    env = os.environ.get("RM_CONTROL_MODS")
    if env is not None:
        return [m for m in env.split(",") if m]
    out = []
    try:
        with open(os.path.join(HERE, "maturation_dispatch.json"), encoding="utf-8") as f:
            out = [key(m) for m in json.load(f).get("advancing") or []]
    except (OSError, ValueError):
        pass
    if advancing_only:
        return out
    d = concepts_dir()
    try:
        out += sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)) and x not in out
                      and not x.startswith(("_", ".")))
    except OSError:
        pass
    return out


def scope_of(t, strict=True):
    """'all' | 'Mod' | 'mod:M' | 'stage:S' | 'item:ID' | a RIMMANDRAKE_/RIMMASTER_ id | 'family:F' | a family name |
    'role:R' -> the canonical scope. Raises Refused with the nearest names."""
    t = str(t or "").strip()
    if t == "all":
        return "all"
    kind, _, name = t.partition(":")
    if not name:
        kind, name = None, t
    if kind == "item" or (kind is None and (name.startswith("RIMMANDRAKE_") or name.startswith("RIMMASTER_"))):
        return "item:" + name
    if kind == "stage" or (kind is None and name in STAGES):
        if name not in STAGES:
            raise Refused("no stage %r; stages: %s" % (name, ", ".join(difflib.get_close_matches(name, STAGES, 3, .3)
                                                                       or STAGES)))
        return "stage:" + name
    if kind == "family" or (kind is None and name in FAMILIES):
        if name not in FAMILIES:
            raise Refused("no launch family %r; families: %s" % (name, ", ".join(FAMILIES)))
        return "family:" + name
    if kind == "role":
        return "role:" + name
    if kind not in (None, "mod"):
        raise Refused("no scope kind %r (all, mod:, stage:, item:, family:, role:)" % kind)
    m = key(name)
    if strict:
        mods = known_mods()
        if m not in mods:
            near = difflib.get_close_matches(m, mods, 4, .3)
            raise Refused("no mod %r in the pipeline; nearest: %s" % (m, ", ".join(near) or ", ".join(mods[:6])))
    return "mod:" + m


def run_scopes(spec):
    """The scopes a run lives in: a live switch on any of them refuses it."""
    out = ["all", "family:" + str(spec.get("family"))]
    if spec.get("mod"):
        out.append("mod:" + key(spec["mod"]))
    for m in spec.get("mods") or []:    # a fleet over several mods: any one held or off refuses it
        out.append("mod:" + key(m))
    if spec.get("stage"):
        out.append("stage:" + spec["stage"])
    if spec.get("item"):
        out.append("item:" + spec["item"])
    if spec.get("role"):
        out.append("role:" + spec["role"])
    return out


def _live(row, now):
    return row["until"] is None or now < float(row["until"])


def blocking(c, scopes, now=None):
    """-> the live switch rows on any of `scopes` (owner first, then control; the narrowest scope last)."""
    now = time.time() if now is None else now
    q = "SELECT * FROM switches WHERE scope IN (%s)" % ",".join("?" * len(scopes))
    rows = [r for r in c.execute(q, scopes).fetchall() if _live(r, now)]
    return sorted(rows, key=lambda r: (0 if r["layer"] == "owner" else 1, scopes.index(r["scope"])))


def describe(r):
    if r["layer"] == "owner":
        return "HELD BY OWNER (%s, %s): %s" % (r["scope"], r["date"] or "?", r["said"] or r["why"])
    until = " until %s" % pac(r["until"]) if r["until"] else ""
    return "OFF (%s, act %s at %s%s): %s" % (r["scope"], r["act"], r["at_pacific"], until, r["why"])


def _release(c, where, args, why, now, fault=False):
    """Release every held reservation matching `where` (and meter it as a system fault). -> count."""
    rows = c.execute("SELECT * FROM reservations WHERE state='held' AND " + where, args).fetchall()
    for r in rows:
        c.execute("UPDATE reservations SET state='released', settled_at=?, why=? WHERE id=?", (now, why, r["id"]))
        if fault:
            c.execute("INSERT INTO faults (run, mod, resource, why, at) VALUES (?,?,?,?,?)",
                      (r["run"], r["mod"], r["resource"], why, now))
    return len(rows)


def _in_scope(r, scope):
    try:
        spec = json.loads(r["spec"] or "{}") or dict(r)
    except ValueError:
        spec = dict(r)
    return scope == "unit:" + r["unit"] or scope in run_scopes(spec)


def _cancel_in_scope(c, scope, why, now):
    """Cancel every admitted (unstarted) run in `scope`, releasing its reservations. -> [unit]."""
    out = []
    for r in c.execute("SELECT * FROM runs WHERE state='admitted'").fetchall():
        if _in_scope(r, scope):
            c.execute("UPDATE runs SET state='cancelled', ended_at=?, why=? WHERE id=?", (now, why, r["id"]))
            _release(c, "run=?", (r["id"],), "cancelled before start: " + why, now)
            out.append(r["unit"])
    return out


def switch(scope, off, why, layer="control", until=None, said=None, owner_said=None, per_ruling=None, idem=None,
           p=None, now=None, date=None, extra=None):
    """Write one switch. off=True: the row is written and every unstarted run in scope is cancelled, in ONE
    transaction. off=False: the row of that layer is removed (`on all` never lifts a mod's owner row). -> dict."""
    now = time.time() if now is None else now
    if layer not in LAYERS:
        raise Refused("no layer %r" % layer)
    if layer == "owner" and not (said or owner_said):
        raise Refused("his hold carries his words (--owner-said)")
    with txn(p) as c:
        hit = _idem_hit(c, idem)
        if hit:
            return {"act": hit, "replayed": True, "cancelled": [], "before": None, "still": [], "had": True}
        old = c.execute("SELECT * FROM switches WHERE scope=? AND layer=?", (scope, layer)).fetchone()
        before = "OFF" if old and _live(old, now) else "ON"
        cancelled = []
        if off:
            a = _act(c, "off" if layer == "control" else "hold", scope, dict(old) if old else None,
                     {"layer": layer, "why": why, "until": until}, why, owner_said, per_ruling, idem, now=now)
            c.execute("INSERT OR REPLACE INTO switches (scope, layer, why, said, date, until, act, at_pacific, who, "
                      "extra) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (scope, layer, why.strip(), said or owner_said, date or utc(now)[:10], until, a["id"],
                       a["at_pacific"], a["who"], json.dumps(extra) if extra else None))
            cancelled = _cancel_in_scope(c, scope, why, now)
        else:
            if not old:
                still = [describe(r) for r in blocking(c, [scope], now)]
                return {"act": None, "before": "ON" if not still else "OFF", "cancelled": [], "still": still,
                        "replayed": False, "had": False}
            a = _act(c, "on" if layer == "control" else "lift", scope, dict(old), None, why, owner_said, per_ruling,
                     idem, now=now)
            c.execute("DELETE FROM switches WHERE scope=? AND layer=?", (scope, layer))
        still = [describe(r) for r in blocking(c, [scope], now)]
        return {"act": a, "before": before, "cancelled": cancelled, "still": still, "replayed": False,
                "had": bool(old)}


def switches(p=None, now=None):
    """-> every live switch row. Raises Unreadable."""
    now = time.time() if now is None else now
    return [r for r in _q("SELECT * FROM switches ORDER BY scope, layer", p=p) if _live(r, now)]


def blocked(spec, p=None, now=None):
    """-> why a run with this spec would be refused by a switch now, or None. Raises Unreadable."""
    c = read(p)
    try:
        rows = blocking(c, run_scopes(spec), now)
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()
    return describe(rows[0]) if rows else None


def mod_holds(p=None, now=None):
    """-> {mod: hold-shaped row} for every live switch on a mod scope (mod_owner_hold.load merges it, so every hold
    reader honours it). His owner rows carry his words and date; `pipe off <Mod>` rows read control=True."""
    out = {}
    for s in switches(p, now):
        if not s["scope"].startswith("mod:"):
            continue
        m = s["scope"][4:]
        if s["layer"] == "owner":
            row = {"mod": m, "date": s["date"] or "", "said": s["said"] or s["why"], "store": True, "act": s["act"]}
            try:
                row.update(json.loads(s["extra"]) if s["extra"] else {})
            except ValueError:
                pass
            out[m] = row
        else:
            out.setdefault(m, {"mod": m, "date": (s["date"] or ""), "said": s["why"], "control": True, "act": s["act"],
                               "at_pacific": s["at_pacific"], "until": s["until"]})
    return out


def heartbeat(name, p=None):
    """The live store was read just now by `name` (the tick): touch <store dir>/<name>, the reading the item's --live
    promise and the deadman check. A test store writes none. Never raises."""
    p = p or db_path()
    if not is_live(p):
        return None
    f = os.path.join(os.path.dirname(os.path.abspath(p)), name)
    try:
        with open(f, "w", encoding="ascii") as fh:
            fh.write("%s\n" % utc(time.time()))
        return f
    except OSError:
        return None


def note(kind, scope, why, after=None, p=None, now=None):
    """One act that records without switching (a stop-live list, say). -> the act."""
    with txn(p) as c:
        return _act(c, kind, scope, None, after, why, now=now)


def lift_owner(mod, said, date=None, p=None, now=None, held_said=None):
    """Lift his hold on `mod` in the store (his words required), and remember the lifted (mod, date), so the file
    mirror's row stops holding at once. -> the store row lifted, or None when the store held no row for it."""
    if not (isinstance(said, str) and said.strip()):
        raise Refused("lifting his hold takes his words (--said)")
    now = time.time() if now is None else now
    with txn(p) as c:
        old = c.execute("SELECT * FROM switches WHERE scope=? AND layer='owner'", ("mod:" + key(mod),)).fetchone()
        d = date or (old["date"] if old else "") or ""
        w = held_said if held_said is not None else (old["said"] if old else "") or ""
        _act(c, "lift", "mod:" + key(mod), dict(old) if old else None, {"lifted": [key(mod), d, w]},
             "his hold lifted: %s" % said.strip(), owner_said=said.strip(), idem="lift:owner:%s:%s:%d" % (
                 key(mod), d, int(now * 1000)), now=now)
        c.execute("DELETE FROM switches WHERE scope=? AND layer='owner'", ("mod:" + key(mod),))
        return dict(old) if old else None


def lifted_owner(p=None):
    """-> {(mod, date, his words)} of his holds lifted through the store: a file row that is exactly one of them stops
    holding at once; a new hold (other words or another day) holds."""
    out = set()
    for a in _q("SELECT after FROM acts WHERE kind='lift' ORDER BY rev", p=p):
        try:
            m, d, w = json.loads(a["after"])["lifted"]
            out.add((m, d, w))
        except (ValueError, KeyError, TypeError):
            continue
    return out


# ---------------------------------------------------------------- accounts (reserve, settle, void, grant)

def _account(c, mod, resource, win, base, exclude_run=None, used=None):
    """-> {base, granted, charged, voided, held, available} for one typed account. `used` (when the caller's own
    records count the validated results, as the coverage judge's rounds do) stands in for the store's charges."""
    g = c.execute("SELECT COALESCE(SUM(qty),0) FROM grants WHERE mod=? AND resource=? AND win=?",
                  (mod, resource, win)).fetchone()[0]
    rows = c.execute("SELECT state, run, qty FROM reservations WHERE mod=? AND resource=? AND win=?",
                     (mod, resource, win)).fetchall()
    charged = sum(r["qty"] for r in rows if r["state"] == "charged")
    voided = sum(r["qty"] for r in rows if r["state"] == "voided")
    held = sum(r["qty"] for r in rows if r["state"] == "held" and r["run"] != exclude_run)
    if used is not None:    # the caller's own validated count, or the store's charges where it holds more (a look
        charged = max(used, charged)    # charged on a covered verdict counts though no refusal round shows it)
    return {"base": base, "granted": g, "charged": charged, "voided": voided, "held": held,
            "available": base + g - charged - held}


def account(mod, resource, win="", base=0, p=None, used=None):
    c = read(p)
    try:
        return _account(c, key(mod), resource, win, base, used=used)
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()


def _reap(c, now):
    """Release held reservations whose holder process is gone (same host; fenced by /proc): a crashed judge never
    keeps its look. -> count."""
    n = 0
    host = socket.gethostname()
    for r in c.execute("SELECT * FROM reservations WHERE state='held' AND pid IS NOT NULL AND host=?",
                       (host,)).fetchall():
        if not os.path.exists("/proc/%d" % r["pid"]):
            n += _release(c, "id=?", (r["id"],), "fail_system: its holder (pid %d) died before settling" % r["pid"],
                          now, True)
    return n


def reserve(mod, resource, run, win="", base=0, qty=1, p=None, now=None, pid=None, used=None):
    """Hold `qty` of one account for `run`, in one transaction: exactly one of two callers racing for the last unit
    gets it. -> (True, account) or (False, why). Raises Unreadable (fail closed: the caller runs nothing)."""
    now = time.time() if now is None else now
    mod = key(mod)
    with txn(p) as c:
        _reap(c, now)
        mine = c.execute("SELECT state FROM reservations WHERE run=? AND mod=? AND resource=? AND win=?",
                         (run, mod, resource, win)).fetchone()
        if mine:
            if mine["state"] == "held":
                return True, _account(c, mod, resource, win, base, used=used)
            return False, "%s %s: run %s already settled this reservation (%s)" % (mod, resource, run, mine["state"])
        acc = _account(c, mod, resource, win, base, used=used)
        if acc["available"] < qty:
            return False, "%s %s: none available (%s)" % (mod, resource, fmt_acct(acc))
        c.execute("INSERT INTO reservations (run, mod, resource, win, qty, state, at, pid, host) VALUES "
                  "(?,?,?,?,?, 'held', ?,?,?)", (run, mod, resource, win, qty, now, pid or os.getpid(),
                                                  socket.gethostname()))
        return True, _account(c, mod, resource, win, base, used=used)


def settle(run, valid, why, p=None, now=None):
    """Settle every reservation of `run` exactly once: valid -> charged (the run ended and its result counts on the
    mod's merits); otherwise released and metered as a system fault. A second settle changes nothing. -> count."""
    now = time.time() if now is None else now
    with txn(p) as c:
        if valid:
            if c.execute("SELECT 1 FROM voids WHERE run=?", (run,)).fetchone():
                return 0        # a voided run is never charged afterwards
            return c.execute("UPDATE reservations SET state='charged', settled_at=?, why=? WHERE run=? AND "
                             "state='held'", (now, why, run)).rowcount
        n = _release(c, "run=?", (run,), "fail_system: " + why, now, fault=True)
    if n:
        _fault_alarm(run, p)
    return n


def faults(mod, since_s=86400, p=None, now=None):
    now = time.time() if now is None else now
    r = _q("SELECT COUNT(DISTINCT run) n FROM faults WHERE mod=? AND at>=?", (key(mod), now - since_s), p, one=True)
    return r["n"]


def _fault_alarm(run, p=None):
    """The system-fault meter's own alarm: FAULT_LIMIT fail_system runs on one mod in a day raise
    control:system_faults:<mod> (refusal_contract's alarm store), so a relaunch loop that never charges is still seen.
    Only the live store raises it (a test store's faults are its own)."""
    try:
        mods = [r["mod"] for r in _q("SELECT DISTINCT mod FROM faults WHERE run=?", (run,), p)]
        for m in mods:
            n = faults(m, p=p)
            if n >= FAULT_LIMIT and is_live(p):
                sys.path.insert(0, HERE) if HERE not in sys.path else None
                import refusal_contract as RC
                RC.alarm("control:system_faults:%s" % m, "%d runs on %s ended as system faults in 24 h (limit %d): they "
                         "charge nothing, so find the fault (pipe log; pipe show %s)" % (n, m, FAULT_LIMIT, m),
                         family="control")
    except Exception as e:      # noqa: BLE001  the alarm is the meter's voice; a dead one is said, never fatal
        print("control: the system-fault alarm could not be raised: %s" % e, file=sys.stderr)


def void(run, why, mod=None, owner_said=None, per_ruling=None, idem=None, p=None, now=None):
    """Void one run: its charges are given back and its held reservations released, exactly once. A void never moves a
    stage (`pipe show` flags a stage advanced on a voided run). -> dict."""
    now = time.time() if now is None else now
    with txn(p) as c:
        old = c.execute("SELECT * FROM voids WHERE run=?", (run,)).fetchone()
        if old:
            a = c.execute("SELECT * FROM acts WHERE id=?", (old["act"],)).fetchone()
            return {"replayed": True, "act": dict(a) if a else {"id": old["act"], "rev": "?"}, "given": 0,
                    "mod": old["mod"]}
        rr = c.execute("SELECT * FROM runs WHERE id=? OR unit=?", (run, run)).fetchone()
        rids = {run} | ({rr["id"], rr["unit"]} if rr else set())
        q = "SELECT * FROM reservations WHERE run IN (%s) AND state IN ('held','charged')" % ",".join("?" * len(rids))
        res = c.execute(q, list(rids)).fetchall()
        mod = key(mod) if mod else (rr["mod"] if rr else (res[0]["mod"] if res else None))
        a = _act(c, "void", "run:" + run, {"charged": sum(r["qty"] for r in res if r["state"] == "charged"),
                                           "held": sum(r["qty"] for r in res if r["state"] == "held")},
                 {"void": True}, why, owner_said, per_ruling, idem, now=now)
        for x in rids:
            c.execute("INSERT OR IGNORE INTO voids VALUES (?,?,?,?,?,?)", (x, mod, a["id"], why.strip(), owner_said,
                                                                           now))
        given = 0
        for x in rids:
            given += c.execute("UPDATE reservations SET state='voided', settled_at=? WHERE run=? AND state='charged'",
                               (now, x)).rowcount
            given += _release(c, "run=?", (x,), "voided: " + why, now)
        # the dispatch books key runs by unit: a void by run id books the unit (RIMMANDRAKE_BOOK_PIPE_VOID_BY_UNIT_NOT_RUN_ID)
        return {"replayed": False, "act": a, "given": given, "mod": mod, "unit": rr["unit"] if rr else run}


def voided(runs=None, p=None):
    """-> the set of voided run ids (of `runs`, when given). Raises Unreadable."""
    allv = {r["run"] for r in _q("SELECT run FROM voids", p=p)}
    return allv if runs is None else allv & set(runs)


def grant(mod, resource, n, why, win="", owner_said=None, per_ruling=None, idem=None, p=None, now=None, base=0,
          used=None):
    now = time.time() if now is None else now
    mod = key(mod)
    with txn(p) as c:
        hit = _idem_hit(c, idem)
        if hit:
            return {"replayed": True, "act": hit, "before": None, "after": _account(c, mod, resource, win, base, used=used)}
        before = _account(c, mod, resource, win, base, used=used)
        a = _act(c, "grant", "mod:%s/%s@%s" % (mod, resource, win), before, {"grant": n}, why, owner_said,
                 per_ruling, idem, now=now)
        c.execute("INSERT INTO grants (mod, resource, win, qty, act, why, owner_said, at) VALUES (?,?,?,?,?,?,?,?)",
                  (mod, resource, win, n, a["id"], why.strip(), owner_said, now))
        return {"replayed": False, "act": a, "before": before, "after": _account(c, mod, resource, win, base, used=used)}


def fmt_acct(a):
    return "available %d = %d base + %d granted - %d charged - %d held%s" % (
        a["available"], a["base"], a["granted"], a["charged"], a["held"],
        ", %d voided" % a["voided"] if a["voided"] else "")


# ---------------------------------------------------------------- the granted coverage look

LOOK = "granted_look"


def look_window(st):
    """-> the accounting window of a concept's granted look: the grant's time (a release applied from a grant keeps
    its granted_at; a plain release its own time; a grant still waiting on its fixes its time), or None."""
    rel = [x for x in (st or {}).get("coverage_releases") or [] if isinstance(x, dict)]
    if rel:     # keyed by kind, so a plain release and a grant in the same second are two windows
        r = rel[-1]
        return "grant:%s" % r["granted_at"] if r.get("granted_at") else "release:%s#%d" % (r.get("at") or "", len(rel))
    g = (st or {}).get("coverage_release_granted")
    return "grant:%s" % (g.get("at") or "") if isinstance(g, dict) else None


# ---------------------------------------------------------------- admission and the launch primitive

def admit(spec, p=None, now=None):
    """The one admission point. In ONE transaction: refuse on any live switch in the run's scopes, on a unit already
    admitted, or on any account without enough; else reserve every resource and write the run (state admitted) with
    its launch intent. -> {"ok", "run", "why", "rev"}. A refusal consumes nothing. Raises Unreadable."""
    now = time.time() if now is None else now
    spec = dict(spec)
    if spec.get("family") not in FAMILIES or not spec.get("unit"):
        raise Refused("a launch spec names its family (%s) and its unit: %r" % (", ".join(FAMILIES), spec))
    if spec.get("mod"):
        spec["mod"] = key(spec["mod"])
    with txn(p) as c:
        rows = blocking(c, run_scopes(spec), now)
        why = describe(rows[0]) if rows else None
        if not why:
            old = c.execute("SELECT state, pid, host FROM runs WHERE unit=?", (spec["unit"],)).fetchone()
            mine = old is not None and old["state"] == "admitted" and old["host"] == socket.gethostname() and (
                old["pid"] == os.getpid() or not os.path.exists("/proc/%d" % (old["pid"] or 0)))
            if old and (old["state"] in NEVER_RAN or mine):
                # that name never ran a payload, or its admission is this process's own earlier try (or a dead
                # launcher's) whose unit never reached its start check: it may be admitted again
                c.execute("DELETE FROM runs WHERE unit=?", (spec["unit"],))
                c.execute("DELETE FROM reservations WHERE run=? AND state='held'", ("run_" + spec["unit"],))
            elif old:
                why = ("DUPLICATE: unit %s is already admitted (state %s): an ambiguous start is investigated, never "
                       "relaunched under the same name" % (spec["unit"], old["state"]))
        if not why:
            _reap(c, now)
            for res in spec.get("resources") or []:
                acc = _account(c, key(res.get("mod") or spec.get("mod")), res["resource"], res.get("win", ""),
                               int(res.get("base", 0)), used=res.get("used"))
                if acc["available"] < int(res.get("qty", 1)):
                    why = "%s: none available (%s)" % (res["resource"], fmt_acct(acc))
                    break
        if why:
            c.execute("INSERT INTO refusals (at, unit, family, mod, why) VALUES (?,?,?,?,?)",
                      (now, spec["unit"], spec["family"], spec.get("mod"), why))
            c.execute("DELETE FROM refusals WHERE id <= (SELECT MAX(id) FROM refusals) - 2000")
            return {"ok": False, "run": None, "why": why, "rev": rev(c)}
        rid = "run_%s" % spec["unit"]
        r = rev(c)
        c.execute("INSERT INTO runs (id, unit, family, mod, item, stage, role, model, state, rev, admitted_at, pid, host, "
                  "spec) VALUES (?,?,?,?,?,?,?,?, 'admitted', ?,?,?,?,?)",
                  (rid, spec["unit"], spec["family"], spec.get("mod"), spec.get("item"), spec.get("stage"),
                   spec.get("role"), spec.get("model"), r, now, os.getpid(), socket.gethostname(),
                   json.dumps(spec, sort_keys=True, default=str)))
        for res in spec.get("resources") or []:
            c.execute("INSERT INTO reservations (run, mod, resource, win, qty, state, at) VALUES (?,?,?,?,?, 'held', ?)",
                      (rid, key(res.get("mod") or spec.get("mod")), res["resource"], res.get("win", ""),
                       int(res.get("qty", 1)), now))
        return {"ok": True, "run": rid, "why": None, "rev": r}


def condition(run, p=None, now=None):
    """The unit's ExecCondition: -> (exit code, line). 0 = start (marked started, in one transaction with the check);
    1 = REFUSED (cancelled, already started once, or a switch now blocks it: reservations released); 2 = the store
    cannot be read (skipped: fail closed). systemd skips the unit on any of 1-254."""
    now = time.time() if now is None else now
    try:
        with txn(p) as c:
            r = c.execute("SELECT * FROM runs WHERE id=?", (run,)).fetchone()
            if not r:
                return 1, "REFUSED %s: no admission for this run" % run
            if r["state"] != "admitted":
                return 1, "REFUSED %s: its intent is %s (%s), not admitted" % (run, r["state"], r["why"] or "-")
            rows = blocking(c, run_scopes(json.loads(r["spec"] or "{}")), now)
            if rows:
                why = describe(rows[0])
                c.execute("UPDATE runs SET state='refused', ended_at=?, why=? WHERE id=?", (now, why, run))
                _release(c, "run=?", (run,), "refused at start: " + why, now)
                return 1, "REFUSED %s at start: %s" % (run, why)
            c.execute("UPDATE runs SET state='started', started_at=? WHERE id=?", (now, run))
            return 0, "START %s (rev %d)" % (run, rev(c))
    except Unreadable as e:
        return 2, "CONTROL UNREADABLE: %s (unit skipped)" % e


def ended(run, result=None, p=None, now=None):
    """The unit's ExecStopPost: the run ends; a reservation nobody settled is released as a system fault (no result is
    never a charge); its stop order, if any, is done. -> line."""
    now = time.time() if now is None else now
    result = result or "%s/%s/%s" % (os.environ.get("SERVICE_RESULT", "?"), os.environ.get("EXIT_CODE", "?"),
                                     os.environ.get("EXIT_STATUS", "?"))
    with txn(p) as c:
        r = c.execute("SELECT * FROM runs WHERE id=?", (run,)).fetchone()
        if not r:
            return "no run %s" % run
        if r["state"] == "started":
            c.execute("UPDATE runs SET state='ended', ended_at=?, result=? WHERE id=?", (now, result, run))
        c.execute("UPDATE stops SET state='done', ended_at=? WHERE run=? AND state IN ('pending','seen')", (now, run))
        n = _release(c, "run=?", (run,), "ended (%s) with no validated settlement" % result, now,
                     fault=r["state"] == "started")
    if n:
        _fault_alarm(run, p)
    return "ENDED %s %s" % (run, result)


def run_state(run, p=None):
    return _q("SELECT * FROM runs WHERE id=? OR unit=?", (run, run), p, one=True)


def _mark(run, state, why, p=None, now=None, fault=False, frm=("admitted",)):
    """frm -> state (fail_launch / abandoned / killed), releasing its reservations. -> True if it moved."""
    now = time.time() if now is None else now
    with txn(p) as c:
        n = c.execute("UPDATE runs SET state=?, ended_at=?, why=? WHERE id=? AND state IN (%s)" % ",".join("?" * len(frm)),
                      (state, now, why, run) + tuple(frm)).rowcount
        if n:
            _release(c, "run=?", (run,), "%s: %s" % (state, why), now, fault)
        return bool(n)


class Launch(subprocess.CompletedProcess):
    """systemd-run's CompletedProcess, plus .refused (True: control refused it; systemd-run never ran, or the unit's
    condition skipped it), .unreadable, .run (the control run id) and .why."""
    refused = False
    unreadable = False
    run = None
    why = None


def _refusal(argv, why, unreadable=False, run=None):
    text = ("CONTROL UNREADABLE: %s" if unreadable else "REFUSED by control: %s") % why
    r = Launch(argv, LAUNCH_REFUSED_RC, "", text)
    r.refused, r.unreadable, r.why, r.run = True, unreadable, why, run
    return r


def hook_cmd(verb, run, p):
    py = "/usr/bin/python3" if os.path.exists("/usr/bin/python3") else sys.executable
    return "%s %s %s %s --db %s" % (py, os.path.abspath(__file__), verb, run, os.path.abspath(p))


def unit_of(argv):
    for n, a in enumerate(argv):
        if a == "--unit" and n + 1 < len(argv):
            return argv[n + 1]
        if a.startswith("--unit="):
            return a.split("=", 1)[1]
    return None


def launch_unit(argv, spec, runner=None, p=None, **kw):
    """THE launch primitive: every `systemd-run` that starts pipeline work goes through here (selftest_control
    enumerates the call sites; an unrouted one fails it). admit(spec) first; a refusal returns a Launch with .refused
    (rc LAUNCH_REFUSED_RC) and never runs systemd-run. An admitted run's unit carries ExecCondition (the start-time
    re-check) and ExecStopPost (its end receipt). After systemd-run returns, the run's state decides: refused or
    cancelled at start -> .refused, never "running". -> Launch. Raises what the runner raises (a timeout leaves the run
    admitted for reconcile: an ambiguous start is investigated, never relaunched under the same name)."""
    runner = runner or subprocess.run
    p = p or db_path()
    i = 1 if argv and os.path.basename(str(argv[0])) == "systemd-run" else None
    if i is None:       # not a unit (a test seam's stand-in command): admitted the same, run, and closed at once
        try:
            adm = admit(dict(spec, unit=spec.get("unit") or "rm-%s-%d" % (spec.get("family"), time.time_ns() // 1000)),
                        p)
        except Unreadable as e:
            return _refusal(argv, str(e), unreadable=True)
        if not adm["ok"]:
            return _refusal(argv, adm["why"])
        r = runner(argv, **kw)
        _mark(adm["run"], "ended" if r.returncode == 0 else "fail_launch", "no unit: ran in the caller", p)
        return r
    if not (spec.get("unit") or unit_of(argv)):     # the unit name is fixed BEFORE launch, so admission can key it
        argv = list(argv[:i]) + ["--unit", "rm-%s-%d-%04x" % (spec.get("family"), time.time_ns() // 1000,
                                                             os.getpid() & 0xffff)] + list(argv[i:])
    spec = dict(spec, unit=spec.get("unit") or unit_of(argv))
    try:
        adm = admit(spec, p)
    except Unreadable as e:
        return _refusal(argv, str(e), unreadable=True)
    if not adm["ok"]:
        return _refusal(argv, adm["why"])
    rid = adm["run"]
    # the two receipts go right after `--unit <name>` (the options before it stay where callers expect them)
    j = next((n + 2 for n, a in enumerate(argv) if a == "--unit"), None) or \
        next((n + 1 for n, a in enumerate(argv) if str(a).startswith("--unit=")), i)
    full = list(argv[:j]) + ["-p", "ExecCondition=" + hook_cmd("condition", rid, p),
                             "-p", "ExecStopPost=-" + hook_cmd("ended", rid, p)] + list(argv[j:])
    try:
        r = runner(full, **kw)
    except OSError as e:
        _mark(rid, "fail_launch", "systemd-run could not start: %s" % e, p, fault=True)
        raise
    try:    # the runner's own result, marked (a caller's fake runner may return any object)
        out = r
        out.refused, out.unreadable, out.why, out.run = False, False, None, rid
    except AttributeError:
        out = Launch(getattr(r, "args", full), r.returncode, getattr(r, "stdout", None), getattr(r, "stderr", None))
        out.run = rid
    try:
        st = run_state(rid, p)
    except Unreadable as e:
        out.why = "the run's state cannot be read after launch: %s" % e
        return out
    if st and st["state"] in ("refused", "cancelled"):
        return _refusal(argv, "%s at start: %s" % (st["state"], st["why"]), run=rid)
    if st and st["state"] == "admitted" and r.returncode != 0:
        _mark(rid, "fail_launch", "systemd-run exit %d" % r.returncode, p, fault=True)
    return out


def reconcile(p=None, now=None, min_age_s=300, unit_loaded=None):
    """Close admitted runs whose unit never started and whose launcher is gone: abandoned, reservations released. The
    condition fences them (an abandoned run's unit, if it ever starts, is refused). -> [unit]."""
    now = time.time() if now is None else now
    unit_loaded = unit_loaded or _unit_loaded
    rows = _q("SELECT * FROM runs WHERE state='admitted' AND admitted_at < ?", (now - min_age_s,), p)
    out = []
    for r in rows:
        alive = r["host"] == socket.gethostname() and r["pid"] and os.path.exists("/proc/%d" % r["pid"])
        if not alive and unit_loaded(r["unit"]) is False:
            if _mark(r["id"], "abandoned", "never started; its launcher (pid %s) is gone" % r["pid"], p, now, True):
                out.append(r["unit"])
    return out


def _unit_loaded(unit):
    """True / False, or None when systemd cannot be read (never abandon on a blind read)."""
    try:
        r = subprocess.run(["systemctl", "--user", "show", "-p", "LoadState,ActiveState", "--value", unit],
                           capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode:
        return None
    v = r.stdout.split()
    return bool(v) and v[0] == "loaded" and (len(v) < 2 or v[1] not in ("inactive", "failed"))


# ---------------------------------------------------------------- stopping live runs (three explicit commands)

STOP_TEXT = {
    "write_now": "STOP ORDER, write now (pipe stop --write-now, act {act} at {at}, by {who}: {why}). Stop what you are "
                 "doing NOW and start no new work. Write where you are: commit and ./publish only units that are "
                 "finished; put a short handoff note on your item ({item}) with `python3 src/RimMandrake/rimflow/cli.py "
                 "note {item} --text \"STOPPED (write-now): done: ...; half-done: ...; next: ...\" --why \"pipe stop\"` "
                 "and publish its shard; then end your turn. At {deadline} the run is killed.",
    "at_easy_spot": "STOP ORDER, at the next easy spot (pipe stop --at-easy-spot, act {act} at {at}, by {who}: {why}). "
                    "Finish the unit of work in hand, start no other, then write where you are: commit and ./publish "
                    "what is finished; put a short handoff note on your item ({item}) with `python3 "
                    "src/RimMandrake/rimflow/cli.py note {item} --text \"STOPPED (at-easy-spot): done: ...; half-done: "
                    "...; next: ...\" --why \"pipe stop\"` and publish its shard; then end your turn.{deadline_text}",
}


def _systemctl(args, timeout=10):
    try:
        r = subprocess.run(["systemctl", "--user"] + args, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return -1, "%s: %s" % (type(e).__name__, e)


def _cgroup_pids(unit):
    """-> (pids now in the unit's cgroup, or None when it cannot be read; the cgroup path)."""
    rc, out = _systemctl(["show", "-p", "ControlGroup", "--value", unit], 5)
    cg = out.strip() if rc == 0 else ""
    if not cg:
        return [], ""
    procs = os.path.join("/sys/fs/cgroup", cg.lstrip("/"), "cgroup.procs")
    try:
        with open(procs, encoding="ascii") as f:
            return [int(x) for x in f.read().split()], cg
    except FileNotFoundError:
        return [], cg
    except (OSError, ValueError):
        return None, cg


def _alive(pid):
    try:
        with open("/proc/%d/stat" % pid, encoding="ascii", errors="replace") as f:
            return f.read().rsplit(")", 1)[-1].split()[0] not in ("Z", "X")
    except (FileNotFoundError, ProcessLookupError, IndexError):
        return False
    except OSError:
        return True


def kill_units(units, wait_s=KILL_WAIT_S):
    """FORCE KILL: SIGKILL to each unit's WHOLE cgroup at once (every child included; `systemctl --user kill
    --signal=SIGKILL --kill-whom=all`), then `stop` to clear it, and verify every process that was in it is gone.
    -> [{"unit", "dead" (True/False/None: nothing was running), "ms", "survivors", "said"}]. Never raises."""
    out = []
    for u in units:
        pids, cg = _cgroup_pids(u)
        t0 = time.monotonic()
        rc, said = _systemctl(["kill", "--signal=SIGKILL", "--kill-whom=all", u], 10)
        if pids:        # belt and braces: the pids seen in the cgroup get SIGKILL too (a unit systemd no longer lists)
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
        left = list(pids or [])
        while left and time.monotonic() - t0 < wait_s:
            left = [x for x in left if _alive(x)]
            if left:
                time.sleep(0.01)
        left = [x for x in left if _alive(x)]
        ms = int((time.monotonic() - t0) * 1000)
        _systemctl(["stop", "--no-block", u], 10)
        _systemctl(["reset-failed", u], 5)
        if pids is None:
            out.append({"unit": u, "dead": None, "ms": ms, "survivors": [],
                        "said": "its cgroup could not be read (%s): death UNVERIFIED" % cg})
        elif not pids:
            out.append({"unit": u, "dead": None, "ms": ms, "survivors": [], "said": "nothing was running in it"})
        else:
            out.append({"unit": u, "dead": not left, "ms": ms, "survivors": left,
                        "said": "%d process(es) killed" % len(pids) if not left else "SURVIVED: pids %s" % left})
    return out


def _live_runs(c, scope):
    return [dict(r) for r in c.execute("SELECT * FROM runs WHERE state='started' ORDER BY started_at").fetchall()
            if _in_scope(r, scope)]


def _extra_units(run):
    try:
        spec = json.loads(run.get("spec") or "{}")
    except ValueError:
        spec = {}
    return [x for x in spec.get("extra_units") or [] if isinstance(x, str)]


def stop(target, mode, why, deadline_s=None, owner_said=None, per_ruling=None, p=None, now=None, killer=None,
         reaper=None, escalator=None):
    """`pipe stop`: block new launches on the scope at once (a control switch, every unstarted run cancelled, in one
    transaction), release the live runs' trials (void, fail_system), and per live run: write_now / at_easy_spot write a
    stop order its hook delivers; kill SIGKILLs its whole cgroup (and its claude scope) and verifies it dead. -> dict."""
    now = time.time() if now is None else now
    if mode not in STOP_MODES:
        raise Refused("no stop mode %r (%s)" % (mode, ", ".join(STOP_MODES)))
    killer = killer or kill_units
    t = str(target or "").strip()
    unit_target = t.startswith("unit:") or t.startswith("rm-")
    scope = ("unit:" + t[5:] if t.startswith("unit:") else "unit:" + t) if unit_target else scope_of(t)
    if deadline_s is None and mode == "write_now":
        deadline_s = WRITE_NOW_DEADLINE_S
    try:
        with txn(p) as c:
            act = None
            cancelled = []
            if not unit_target:
                old = c.execute("SELECT * FROM switches WHERE scope=? AND layer='control'", (scope,)).fetchone()
                act = _act(c, "stop", scope, dict(old) if old else None, {"mode": mode, "deadline_s": deadline_s}, why,
                           owner_said, per_ruling, now=now)
                c.execute("INSERT OR REPLACE INTO switches (scope, layer, why, said, date, until, act, at_pacific, who)"
                          " VALUES (?,?,?,?,?,?,?,?,?)", (scope, "control", "stopped (%s): %s" % (mode, why.strip()),
                                                          owner_said, utc(now)[:10], None, act["id"],
                                                          act["at_pacific"], act["who"]))
                cancelled = _cancel_in_scope(c, scope, "stopped: " + why, now)
            runs = _live_runs(c, scope)
            if unit_target and not runs:
                runs = [{"id": None, "unit": scope[5:], "spec": "{}", "item": None, "mod": None, "family": "?"}]
            if unit_target:
                act = _act(c, "stop", scope, None, {"mode": mode, "deadline_s": deadline_s}, why, owner_said,
                           per_ruling, now=now)
            for r in runs:
                if r["id"]:     # its trials released: a stopped run is void and charges nothing (fail_system)
                    c.execute("INSERT OR IGNORE INTO voids VALUES (?,?,?,?,?,?)",
                              (r["id"], r["mod"], act["id"], "stopped (%s): %s" % (mode, why.strip()), owner_said, now))
                    _release(c, "run=?", (r["id"],), "fail_system: stopped (%s): %s" % (mode, why), now, True)
                    c.execute("UPDATE reservations SET state='voided', settled_at=? WHERE run=? AND state='charged'",
                              (now, r["id"]))
                if mode != "kill":
                    c.execute("INSERT INTO stops (unit, run, mode, act, why, at, deadline, state) VALUES "
                              "(?,?,?,?,?,?,?, 'pending')", (r["unit"], r["id"], mode, act["id"], why.strip(), now,
                                                             now + deadline_s if deadline_s else None))
            store = True
    except Unreadable as e:
        if not (unit_target and mode == "kill"):
            raise
        act, cancelled, store = None, [], False
        runs = [{"id": None, "unit": scope[5:], "spec": "{}", "item": None, "mod": None, "family": "?"}]
        store_err = str(e)
    out = {"scope": scope, "mode": mode, "act": act, "cancelled": cancelled, "units": [], "store": store}
    for r in runs:      # a stopped run spends no trial in the dispatch books either (run_void.py; card 2026-11-18)
        if store and r.get("id"):
            r["books"] = void_books(r["unit"], r.get("mod"), "stopped (%s): %s" % (mode, why), owner_said,
                                    act["id"], p, per_ruling=per_ruling)
    if not store:
        out["store_err"] = store_err
    if mode == "kill":
        for r in runs:
            res = killer([r["unit"]] + _extra_units(r))
            # dead: every process that was in the unit (and its claude scope) is gone; a unit with nothing running is
            # fine; a cgroup that could not be read is UNVERIFIED, and a survivor is a failure
            bad = [x for x in res if x["dead"] is False or (x["dead"] is None and "nothing was running" not in x["said"])]
            row = {"unit": r["unit"], "dead": not bad and any(x["dead"] for x in res),
                   "ms": max(x["ms"] for x in res), "said": "; ".join("%s: %s" % (x["unit"], x["said"]) for x in res),
                   "ok": not bad}
            if not row["ok"]:   # something survived or death is unverified: never recorded killed, the clone kept
                row["bookkeeping"] = "NOT recorded killed and its clone kept: %s" % row["said"]
                out["units"].append(row)
                continue
            if store and r["id"]:
                _mark(r["id"], "killed", "pipe stop --kill (%s): %s" % (act["id"], why), p, frm=("started", "admitted"))
            row["bookkeeping"] = (reaper or reap_detached)(r, act, why) if r.get("family") == "detached" or \
                str(r["unit"]).startswith("rm-detached-") else "no bookkeeping owed (family %s)" % r.get("family")
            row["bookkeeping"] += r.get("books", "")
            out["units"].append(row)
    else:
        for r in runs:
            esc = (escalator or schedule_escalation)(r["unit"], deadline_s, p) if deadline_s else None
            out["units"].append({"unit": r["unit"], "ok": True, "said": "stop order written (%s)%s%s" % (
                mode, "; escalates to --kill at %s (%s)" % (pac(now + deadline_s), esc) if deadline_s else
                "; no deadline", r.get("books", ""))})
    return out


def schedule_escalation(unit, deadline_s, p=None):
    """A transient timer (bookkeeping, not pipeline work): at the deadline, `escalate` kills the run if it has not
    ended. -> line."""
    name = "rm-control-escalate-%s" % unit[-60:]
    py = "/usr/bin/python3" if os.path.exists("/usr/bin/python3") else sys.executable
    try:
        r = subprocess.run(["systemd-run", "--user", "--quiet", "--collect", "--unit", name,
                            "--on-active=%d" % int(deadline_s), "--timer-property=AccuracySec=1s", py,
                            os.path.abspath(__file__), "escalate", unit, "--db", os.path.abspath(p or db_path())],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError) as e:
        return "escalation timer NOT set (%s)" % e
    return "timer %s" % name if r.returncode == 0 else "escalation timer NOT set (exit %d: %s)" % (
        r.returncode, (r.stderr or "").strip()[:80])


def escalate(unit, p=None, now=None, killer=None, reaper=None):
    """The deadline of a stop order passed: kill the run if it has not ended, and say so (an act). -> line."""
    now = time.time() if now is None else now
    with txn(p) as c:
        s = c.execute("SELECT * FROM stops WHERE unit=? AND state IN ('pending','seen') ORDER BY id DESC",
                      (unit,)).fetchone()
        if not s:
            return "ESCALATE %s: nothing to do (its stop order is done or absent)" % unit
        a = _act(c, "escalate", "unit:" + unit, {"mode": s["mode"]}, {"mode": "kill"},
                 "the %s stop order's deadline passed (%s) and the run had not ended: escalated to --kill" % (
                     s["mode"], pac(s["deadline"] or now)), now=now)
        c.execute("UPDATE stops SET state='escalated', ended_at=? WHERE id=?", (now, s["id"]))
        r = c.execute("SELECT * FROM runs WHERE unit=?", (unit,)).fetchone()
    r = dict(r) if r else {"id": None, "unit": unit, "spec": "{}", "family": "?"}
    res = (killer or kill_units)([unit] + _extra_units(r))
    bad = [x for x in res if x["dead"] is False or (x["dead"] is None and "nothing was running" not in x["said"])]
    if bad:
        return "ESCALATION FAILED %s (%s): %s; NOT recorded killed" % (unit, a["id"], "; ".join(x["said"] for x in bad))
    if r.get("id"):
        _mark(r["id"], "killed", "escalated to --kill (%s)" % a["id"], p, frm=("started", "admitted"))
    book = (reaper or reap_detached)(r, a, "escalated") if str(unit).startswith("rm-detached-") else ""
    return "ESCALATED %s to --kill (%s): %s %s" % (unit, a["id"], "; ".join(x["said"] for x in res), book)


def reap_detached(run, act, why):
    """A killed detached run's bookkeeping, so a relaunch needs no hand step (measured 2026-11-18 11:30 AM PST by the
    Conductor: a SIGKILL left the record `running` and the clone held, because the cgroup kill also kills the unit's
    own ExecStopPost steps). The record is marked finished/killed at once (so a relaunch waits instead of refusing),
    then a `<unit>-return` unit runs finish's ledger note and the clone's return. -> line."""
    unit = run["unit"]
    try:
        import detached_helper as DH
        msg = DH.mark_killed(unit, "killed by pipe stop --kill (%s): %s" % ((act or {}).get("id", "-"), why))
    except Exception as e:      # noqa: BLE001
        return "bookkeeping FAILED: the record could not be marked killed (%s: %s); by hand: detached_helper.py " \
               "finish --unit %s; return --unit %s" % (type(e).__name__, e, unit, unit)
    if msg.startswith("no record"):
        return msg
    _systemctl(["stop", unit + "-return"], 10)
    _systemctl(["reset-failed", unit + "-return"], 5)
    py = "/usr/bin/python3" if os.path.exists("/usr/bin/python3") else sys.executable
    rec = DH.read_record(unit) or {}
    env = ["--setenv", "RM_DISPATCHER_STATE=" + str(rec.get("state") or DH.state_dir())]
    for k in ("RIMFLOW_SEAT", "AGENT_SEAT"):
        env += ["--setenv", "%s=%s" % (k, rec.get("seat") or "BENCH")]
    for k in ("RM_DETACHED_POOL", "RM_CONDUCTOR_LOG", "RELENTLESS_ROOT", "RM_CONTROL_DB", "PATH"):
        if os.environ.get(k):
            env += ["--setenv", "%s=%s" % (k, os.environ[k])]
    try:
        r = subprocess.run(["systemd-run", "--user", "--quiet", "--collect", "--no-block", "--unit", unit + "-return",
                            "-p", "RuntimeMaxSec=1800"] + env + [py, os.path.abspath(__file__), "reap", unit],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError) as e:
        return "%s; the finish+return unit could NOT start (%s): by hand: detached_helper.py finish --unit %s; " \
               "return --unit %s" % (msg, e, unit, unit)
    if r.returncode:
        return "%s; the finish+return unit could NOT start (exit %d: %s)" % (msg, r.returncode, (r.stderr or "")[:80])
    return "%s; %s-return runs finish + return" % (msg, unit)


def reap(unit):
    """The `<unit>-return` unit of a killed detached run: finish's note and log line, then the clone's return."""
    import detached_helper as DH
    rc1, t1 = DH.finish(unit)
    rc2, t2 = DH.return_clone(unit)
    print(t1)
    print(t2)
    return rc1 or rc2


# ---------------------------------------------------------------- the stop channel into a running agent (the hook)

def hook(p=None, unit=None, now=None, stdin=None):
    """The run's Claude Code PostToolUse hook. -> (exit code, text for the agent). One indexed lookup; silent (0, "")
    when there is no stop order, no unit, or no store (a hook never stops an agent because the store is unreadable;
    the switches and the kill still do). Exit 2 hands the text to the agent after its tool call."""
    unit = unit or os.environ.get("RM_ROLE_UNIT") or os.environ.get("RM_DETACHED_UNIT")
    if not unit:
        return 0, ""
    p = p or db_path()
    if not os.path.exists(p):
        return 0, ""
    now = time.time() if now is None else now
    try:
        c = sqlite3.connect(p, timeout=0.5, isolation_level=None)
        try:
            c.row_factory = sqlite3.Row
            s = c.execute("SELECT * FROM stops WHERE unit=? AND state IN ('pending','seen') ORDER BY id DESC LIMIT 1",
                          (unit,)).fetchone()
            if not s:
                return 0, ""
            c.execute("UPDATE stops SET state='seen', seen_at=COALESCE(seen_at, ?), seen_n=seen_n+1 WHERE id=?",
                      (now, s["id"]))
            a = c.execute("SELECT * FROM acts WHERE id=?", (s["act"],)).fetchone()
            r = c.execute("SELECT item FROM runs WHERE unit=?", (unit,)).fetchone()
        finally:
            c.close()
    except sqlite3.Error:
        return 0, ""
    item = (r["item"] if r else None) or os.environ.get("RM_CONTROL_ITEM") or "<your item>"
    dl = s["deadline"]
    text = STOP_TEXT[s["mode"]].format(act=s["act"], at=(a["at_pacific"] if a else "?"), who=(a["who"] if a else "?"),
                                       why=s["why"], item=item, deadline=pac(dl) if dl else "no deadline",
                                       deadline_text=" At %s the run is killed." % pac(dl) if dl else "")
    return 2, text


def claude_settings(p=None):
    """-> the `--settings` JSON a run's claude carries: its PostToolUse hook reads the stop channel (`hook`)."""
    py = "/usr/bin/python3" if os.path.exists("/usr/bin/python3") else sys.executable
    cmd = "%s %s hook --db %s" % (py, os.path.abspath(__file__), os.path.abspath(p or db_path()))
    return json.dumps({"hooks": {"PostToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": cmd,
                                                                              "timeout": 5}]}]}})


# ---------------------------------------------------------------- the call-site census (no launch bypasses admit)

# Files whose `systemd-run` starts no pipeline work (paths under src/RimMandrake), each with why. Every other site must
# be routed: its function calls launch_unit, or it is a BUILDER whose every caller calls launch_unit.
NOT_PIPELINE = {
    "Utils/timers_guard.py": "re-arms a paused timer (no model)",
    "Utils/clone_mem_probe.py": "a memory-probe scope (no model)",
    "Utils/run_selftests.py": "the selftest harness scope (no model)",
    "Utils/mutation/run_mutation.py": "mutation-test workers (no model)",
    "rimflow/login_watch.py": "the account login switch (no model)",
    "rimflow/seat_restart.py": "a seat restart timer (no model)",
    "rimflow/control.py": "the primitive itself, its escalation timer and its killed-run bookkeeping unit",
}
BOOKKEEPING = {
    "rimflow/detached_helper.py:return_argv": "a finished run's clone-return step (starts no model)",
    "rimflow/role_launch.py:stoppost_handoff": "a finished run's wrap-up step, an ExecStopPost (starts no model)",
}
BUILDERS = {    # functions that only BUILD a systemd-run argv; every call of one must sit in a launch_unit caller
    "rimflow/detached_helper.py:launch_argv",
    "rimflow/role_launch.py:launch_argv",
    "rimflow/designer_cleanse.py:fleet_unit_argv",
}


def _sr_list(node):
    if isinstance(node, (ast_mod().List, ast_mod().Tuple)) and node.elts:
        e = node.elts[0]
        return isinstance(e, ast_mod().Constant) and isinstance(e.value, str) and \
            os.path.basename(e.value) == "systemd-run"
    return False


def ast_mod():
    import ast
    return ast


def _calls(fn, name):
    ast = ast_mod()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            if (isinstance(f, ast.Name) and f.id == name) or (isinstance(f, ast.Attribute) and f.attr == name):
                yield n


def call_sites(root=None):
    """-> [{"file", "func", "line", "routed" (bool), "why"}] for every list literal whose first element is systemd-run in
    every non-test .py under `root` (src/RimMandrake). The selftest fails on any routed=False."""
    ast = ast_mod()
    root = root or os.path.join(REPO, "src", "RimMandrake")
    funcs = {}      # "rel:func" -> FunctionDef
    sites = []
    trees = {}
    for d, _dirs, files in os.walk(root):
        parts = os.path.relpath(d, root).split(os.sep)
        if any(x.startswith(".") and x != "." for x in parts) or "__pycache__" in parts:
            continue
        for f in files:
            if not f.endswith(".py") or f.startswith("selftest") or f.startswith("test_"):
                continue
            path = os.path.join(d, f)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            try:
                import warnings
                with open(path, encoding="utf-8") as fh, warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    tree = ast.parse(fh.read())
            except (OSError, SyntaxError, ValueError):
                continue
            trees[rel] = tree

            def visit(node, stack):
                for ch in ast.iter_child_nodes(node):
                    if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        funcs["%s:%s" % (rel, ch.name)] = ch
                        visit(ch, stack + [ch])
                    else:
                        if _sr_list(ch):
                            sites.append((rel, stack[-1] if stack else None, ch.lineno))
                        visit(ch, stack)
            visit(tree, [])
    callers = {}    # builder "rel:name" -> [(rel, enclosing FunctionDef or None)]
    by_name = {}
    for b in BUILDERS:
        by_name.setdefault(b.split(":")[1], []).append(b)
    for rel, tree in trees.items():
        def walk(node, fn):
            for ch in ast.iter_child_nodes(node):
                if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    walk(ch, ch)
                    continue
                if isinstance(ch, ast.Call):
                    f = ch.func
                    # a bare name calls the builder of its own file; X.name calls a builder of that name elsewhere
                    for b in by_name.get(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute)
                                         else None, []):
                        if (b.split(":")[0] == rel) == isinstance(f, ast.Name):
                            callers.setdefault(b, []).append((rel, fn))
                walk(ch, fn)
        walk(tree, None)
    out = []
    for rel, fn, line in sites:
        name = fn.name if fn else "<module>"
        k = "%s:%s" % (rel, name)
        if rel in NOT_PIPELINE:
            out.append({"file": rel, "func": name, "line": line, "routed": True, "why": "not pipeline: " + NOT_PIPELINE[rel]})
        elif k in BOOKKEEPING:
            out.append({"file": rel, "func": name, "line": line, "routed": True, "why": "bookkeeping: " + BOOKKEEPING[k]})
        elif fn is not None and any(True for _ in _calls(fn, "launch_unit")):
            out.append({"file": rel, "func": name, "line": line, "routed": True, "why": "calls launch_unit"})
        elif k in BUILDERS:
            cs = callers.get(k) or []
            bad = [(r, f.name if f else "<module>") for r, f in cs
                   if f is None or not (any(True for _ in _calls(f, "launch_unit")) or "%s:%s" % (r, f.name) in BUILDERS)]
            out.append({"file": rel, "func": name, "line": line, "routed": bool(cs) and not bad,
                        "why": ("builder; every caller launches through launch_unit (%d)" % len(cs)) if cs and not bad
                        else "builder called OUTSIDE launch_unit: %s" % ", ".join("%s:%s" % b for b in bad) if bad
                        else "builder with no caller"})
        else:
            out.append({"file": rel, "func": name, "line": line, "routed": False,
                        "why": "UNROUTED: starts a unit without control.launch_unit"})
    return out


# ---------------------------------------------------------------- the import (cutover)

def import_live(p=None, now=None, hold_file=None, concepts=None, voids_file=None):
    """Seed the store from today's records, idempotently (each import act carries an idempotency key): his owner holds
    (mod_owner_hold.json, his words and date), the pipeline pause (pause.json), the retired Relentless family OFF, the
    granted coverage look of every concept with a standing release as an opening balance (charges = the refusing looks
    since that release), and run_void's standing voids (voids.jsonl). -> lines."""
    now = time.time() if now is None else now
    out = []
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import mod_owner_hold as OH
    holds = OH.load_file(hold_file or OH.PATH)
    for m, h in sorted(holds.items()):
        r = switch("mod:" + m, True, "his hold (mod_owner_hold.json): " + h["said"], layer="owner", said=h["said"],
                   date=h.get("date"), idem="import:owner:%s:%s" % (m, h.get("date")), p=p, now=now,
                   per_ruling="mod_owner_hold.json",
                   extra={k: v for k, v in h.items() if k == "design_allowed"} or None)
        out.append("owner hold %s %s" % (m, "already imported" if r["replayed"] else "imported (%s)" % r["act"]["id"]))
    r = switch("family:relentless", True, "Relentless is retired (owner 2026-11-13, design/RimMandrake/"
               "retired_loops_2026-11-13.md): its launch sites stay closed", idem="import:family:relentless", p=p,
               now=now, per_ruling="retired_loops_2026-11-13")
    out.append("family relentless OFF %s" % ("already imported" if r["replayed"] else r["act"]["id"]))
    try:
        import pipeline_pause as PP
        pz = PP.load_file() if hasattr(PP, "load_file") else PP.load()
    except Exception as e:      # noqa: BLE001
        pz = None
        out.append("pause.json: could not be read (%s): not imported" % e)
    if pz:
        for scope, e in ([("all", pz["all"])] if pz.get("all") else []) + sorted((pz.get("mods") or {}).items()):
            if not e or not PP.live(e, now):
                continue
            sc = "all" if scope == "all" else "mod:" + scope
            switch(sc, True, e["why"], until=e.get("until"), idem="import:pause:%s:%s" % (sc, e.get("at")), p=p,
                   now=now, per_ruling="pause.json")
            out.append("pause %s imported" % sc)
    for m, d, st in concepts if concepts is not None else _concepts():
        win = look_window(st)
        if win is None:
            continue
        import coverage_judge as CJ
        rs = CJ.rounds(st, d)
        rels = [x for x in st.get("coverage_releases") or [] if isinstance(x, dict)]
        spent = [r.get("judge") for r in CJ._looks(CJ.released_rounds(st, d, rs, rels[-1]))
                 if r.get("verdict") == "not_covered" and r.get("judge")] if rels else []     # a grant not yet applied
        with txn(p) as c:
            if _idem_hit(c, "import:look:%s:%s" % (m, win)):
                out.append("look %s already imported" % m)
                continue
            _act(c, "import", "mod:%s/%s@%s" % (m, LOOK, win), None, {"base": 1, "charged": spent},
                 "opening balance from %s coverage_releases (one look per release)" % m, per_ruling="import",
                 idem="import:look:%s:%s" % (m, win), now=now)
        out.append("look %s window %s: base 1, %d refusing look(s) since (counted from its rounds)" % (m, win,
                                                                                                    len(spent)))
    try:
        import run_void as RV
        act_v = RV.active(voids_file)
    except Exception as e:      # noqa: BLE001
        act_v = None
        out.append("voids.jsonl: could not be read (%s): not imported" % e)
    if act_v is not None:
        n = 0
        for u, v in sorted(act_v.items()):
            r = void(u, "imported from run_void (%s, %s): %s" % (v.get("id"), v.get("kind"), v.get("why")),
                     mod=v.get("mod"), owner_said=v.get("owner_said"), per_ruling="run_void",
                     idem="import:void:%s" % v.get("id"), p=p, now=now)
            n += 0 if r["replayed"] else 1
        out.append("voids: %d standing in voids.jsonl, %d newly imported" % (len(act_v), n))
    return out


def _concepts():
    d = concepts_dir()
    for m in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, m, "stage.json")
        try:
            with open(p, encoding="utf-8") as f:
                yield m, os.path.join(d, m), json.load(f)
        except (OSError, ValueError):
            continue


# ---------------------------------------------------------------- reads for people

def tick_reading():
    """-> (the live tick's last reading, or None, why not)."""
    try:
        d = os.environ.get("RM_MATURATION_DISPATCH_DIR")
        if not d:
            sys.path.insert(0, HERE) if HERE not in sys.path else None
            import doorbell
            d = os.path.join(doorbell.state_dir(), "maturation")
        with open(os.path.join(d, "reading.json"), encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "no reading.json yet"
    except (OSError, ValueError) as e:
        return None, "%s: %s" % (type(e).__name__, e)


def tick_rows(rd):
    """-> {mod: the tick's last row} from a reading (its `mods` is a dict by mod; an older one a list of rows)."""
    ms = (rd or {}).get("mods") or (rd or {}).get("rows") or {}
    if isinstance(ms, dict):
        return {key(m): r for m, r in ms.items() if isinstance(r, dict)}
    return {key(r.get("mod")): r for r in ms if isinstance(r, dict) and r.get("mod")}


def _stage_advanced_on_voided(c, mods=None):
    """-> lines: a voided run named in its concept's history after which the stage moved. The void never moves the
    stage back; the flag asks for the explicit decision (critique 17)."""
    out = []
    for v in c.execute("SELECT * FROM voids").fetchall():
        m = v["mod"]
        if not m or (mods and m not in mods):
            continue
        p = os.path.join(concepts_dir(), m, "stage.json")
        try:
            with open(p, encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            continue
        hs = [h for h in st.get("history") or [] if isinstance(h, dict)]
        if any(v["run"] in json.dumps(h) and (h.get("to") or h.get("stage") or h.get("what") in (
                "advance", "signed", "locked", "covered")) for h in hs) or any(
                isinstance(r, dict) and r.get("judge") == v["run"] and r.get("verdict") == "covered"
                for r in st.get("coverage_rounds") or []):
            out.append("FLAG %s: stage advanced on a voided run %s (the void moved nothing back; decide the stage "
                       "explicitly)" % (m, v["run"]))
    return out


def label(s):
    """A switch row's short cell: HELD BY OWNER / OFF, then its reason."""
    if s["layer"] == "owner":
        return "HELD BY OWNER: %s" % (s.get("said") or s["why"])
    return "OFF: %s" % s["why"]


def show(mod=None, p=None, now=None, as_json=False):
    """-> lines (one screen): every live switch, the live runs, the look accounts and the tick's last decision."""
    now = time.time() if now is None else now
    c = read(p)
    try:
        r0 = rev(c)
        sw = [dict(r) for r in c.execute("SELECT * FROM switches ORDER BY scope, layer").fetchall() if _live(r, now)]
        live = [dict(r) for r in c.execute("SELECT * FROM runs WHERE state IN ('admitted','started') ORDER BY "
                                           "admitted_at").fetchall()]
        looks = [dict(r) for r in c.execute("SELECT DISTINCT mod, win FROM reservations WHERE resource=? UNION "
                                            "SELECT DISTINCT mod, win FROM grants WHERE resource=?",
                                            (LOOK, LOOK)).fetchall()]
        accts = {(x["mod"], x["win"]): _account(c, x["mod"], LOOK, x["win"], 1) for x in looks}
        flags = _stage_advanced_on_voided(c, [key(mod)] if mod else None)
        nf = [dict(r) for r in c.execute("SELECT mod, COUNT(DISTINCT run) n FROM faults WHERE at>=? GROUP BY mod",
                                         (now - 86400,)).fetchall()]
        stops = [dict(r) for r in c.execute("SELECT * FROM stops WHERE state IN ('pending','seen')").fetchall()]
        lock = None
        try:        # WAL: a reader sees the last committed state; a writer holding the lock makes every act wait
            c.execute("PRAGMA busy_timeout=50")
            c.execute("BEGIN IMMEDIATE")
            c.execute("ROLLBACK")
        except sqlite3.Error as e:
            lock = _err(e)
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()
    rd, rd_why = tick_reading()
    tickmods = tick_rows(rd)
    if mod:
        mods = [key(mod)]
    else:   # the pipeline's mods: the tick's, the shipped advancing list, then any mod a switch names
        mods = list(tickmods)
        mods += [m for m in known_mods(advancing_only=True) if m not in mods]
        mods += sorted({s["scope"][4:] for s in sw if s["scope"].startswith("mod:")} - set(mods))
    if as_json:
        return [json.dumps({"rev": r0, "switches": sw, "live": live, "stops": stops,
                            "looks": {"%s@%s" % k: v for k, v in accts.items()}, "flags": flags,
                            "faults": {r["mod"]: r["n"] for r in nf}, "tick": rd.get("at_pac") if rd else None},
                           sort_keys=True, default=str)]
    out = ["STORE LOCKED: %s; this is the last committed state, and every launch and act waits up to 3 s then "
           "refuses (pipe doctor)" % lock] if lock else []
    glob = [s for s in sw if s["scope"] == "all"]
    out.append("control rev %d: ALL %s" % (r0, "; ".join(describe(s) for s in glob) if glob else "ON"))
    for s in sw:
        if not s["scope"].startswith("mod:") and s["scope"] != "all":
            out.append("%s %s" % (s["scope"], label(s)[:150]))
    for m in mods:
        ms = [s for s in sw if s["scope"] == "mod:" + m]
        state = "; ".join(label(s) for s in ms) or "ON"
        tr = tickmods.get(m) or {}
        look = [a for (am, _w), a in accts.items() if am == m]
        line = "%-18s %-15s %-40s tick: %s" % (m, str(tr.get("stage") or "-")[:15], state[:40],
                                                str(tr.get("decision") or "-") if rd else "UNMEASURED (%s)" % rd_why)
        if look:
            line += "  look %d left" % look[-1]["available"]
        out.append(line)
        if mod:
            out += ["  %s" % describe(s) for s in ms]
            out += ["  look window %s: %s" % (w, fmt_acct(a)) for (am, w), a in accts.items() if am == m]
            if tr.get("why"):
                out.append("  tick why: %s" % str(tr["why"])[:200])
            if tr.get("live"):
                out.append("  live (tick): %s" % ", ".join(str(x) for x in tr["live"])[:200])
            try:    # each consumable's count and limit (pipeline_control.py's census)
                sys.path.insert(0, HERE) if HERE not in sys.path else None
                import pipeline_control as PC
                out += [x for x in PC.do_show(PC.Ctx(), m) if x.startswith("  ")]
            except Exception as e:      # noqa: BLE001  a census that cannot read is UNMEASURED, never empty
                out.append("  consumables: UNMEASURED (%s: %s)" % (type(e).__name__, e))
    lv = [r for r in live if not mod or r["mod"] == key(mod)]
    out.append("runs in flight: %s" % (", ".join("%s %s(%s)" % (r["unit"], r["state"], r["mod"] or r["family"])
                                                 for r in lv[:6]) + (" +%d" % (len(lv) - 6) if len(lv) > 6 else "")
                                       if lv else "[] (none admitted or started through control)"))
    for s in stops:
        out.append("stop order %s on %s: %s (seen %s)" % (s["mode"], s["unit"], s["state"],
                                                           pac(s["seen_at"]) if s["seen_at"] else "not yet"))
    for r in nf:
        if not mod or r["mod"] == key(mod):
            out.append("system faults 24 h: %s %d (alarm at %d; void spend is not the mod's)" % (r["mod"], r["n"],
                                                                                                 FAULT_LIMIT))
    out += flags
    if rd:
        out.append("tick last read %s" % rd.get("at_pac", UNM))
    return out


def why(mod, p=None, now=None):
    """-> one line: what blocks this mod now, or what the tick last decided for it."""
    m = key(mod)
    b = blocked({"family": "detached", "unit": "-", "mod": m}, p, now)
    rd, rd_why = tick_reading()
    tr = tick_rows(rd).get(m) or {}
    tick = ("tick %s: %s %s" % (rd.get("at_pac", UNM), tr.get("decision") or "-", str(tr.get("why") or "")[:140])
            if rd else "tick reading UNMEASURED (%s)" % rd_why)
    return "%s: %s | %s" % (m, ("BLOCKED " + b) if b else "nothing in control blocks it", tick)


def log(n=10, p=None):
    rows = _q("SELECT * FROM acts ORDER BY rev DESC LIMIT ?", (n,), p)
    if not rows:
        return ["[] no acts yet (the store at %s is initialised and empty)" % (p or db_path())]
    return ["%s r%d %s %-5s %s: %s%s" % (r["id"], r["rev"], r["at_pacific"], r["kind"], r["scope"], r["why"][:120],
                                         " (his words: %s)" % r["owner_said"][:60] if r["owner_said"] else "")
            for r in reversed(rows)]


def tick_now():
    """An enabling act asks for a tick at once (non-blocking) instead of waiting up to 60 s. -> line or None (a test
    store asks for no tick unless RM_CONTROL_TICK_UNIT names one)."""
    unit = os.environ.get("RM_CONTROL_TICK_UNIT", TICK_UNIT if is_live() else "")
    if not unit:
        return None
    rc, said = _systemctl(["start", "--no-block", unit], 5)
    return ("tick started now: `pipe why <Mod>` in ~5 s says what it decided" if rc == 0
            else "tick NOT started (exit %d: %s); the timer runs it within 60 s" % (rc, said.strip()[:80]))


# ---------------------------------------------------------------- the command line

def _who_line(a):
    return "act %s rev %s at %s" % (a["id"], a["rev"], a.get("at_pacific"))


def cmd_switch(o, off):
    scope = scope_of(o.target)
    r = switch(scope, off, o.why, owner_said=o.owner_said, per_ruling=o.per_ruling, idem=o.idem)
    if r["replayed"]:
        return ["%s: already applied as %s (idempotency key %s): nothing changed" % (scope, r["act"]["id"], o.idem)]
    if not off and not r["had"]:
        if r["still"]:
            return ["%s: no `pipe off` switch to lift; still %s" % (scope, r["still"][0][:160])]
        return ["%s is already ON (the store holds no switch for it)" % scope]
    after = "OFF" if off else ("still " + r["still"][0][:120] if r["still"] else "ON")
    lines = ["%s %s -> %s%s" % (scope, r["before"], after,
                                "; cancelled before start: %s" % ", ".join(r["cancelled"]) if r["cancelled"] else "")]
    if off:
        try:
            live = [x for x in _q("SELECT * FROM runs WHERE state='started'") if _in_scope(x, scope)]
        except Unreadable:
            live = []
        tail = ("; %d run(s) live in it, untouched: stop with pipe stop %s --write-now | --at-easy-spot | --kill"
                % (len(live), o.target)) if live else "; new starts only (no run is live in it)"
        lines.append(_who_line(r["act"]) + tail)
    else:
        t = tick_now()
        lines.append(_who_line(r["act"]) + ("; " + t if t else ""))
    lines.append("undo: pipe %s %s --why \"...\"" % ("on" if off else "off", o.target))
    return lines


def cmd_stop(o):
    modes = [m for m, f in (("write_now", o.write_now), ("at_easy_spot", o.at_easy_spot), ("kill", o.kill)) if f]
    if len(modes) > 1:
        raise Refused("one stop mode, not %s" % ", ".join(modes))
    mode = modes[0] if modes else DEFAULT_STOP_MODE
    named = bool(modes)
    dl = parse_dur(o.deadline) if o.deadline else None
    r = stop(o.target, mode, o.why, deadline_s=dl, owner_said=o.owner_said, per_ruling=o.per_ruling)
    bad = [u for u in r["units"] if not u.get("ok")]
    head = "%s stop %s (%s%s): %s" % (r["scope"], "--" + mode.replace("_", "-"), "named" if named else
                                      "NO MODE GIVEN: the default; always name one", "" if r["store"] else
                                      "; STORE UNREADABLE: %s" % r.get("store_err"),
                                      "; ".join("%s %s" % (u["unit"], ("dead in %d ms" % u["ms"]) if u.get("dead")
                                                           else u["said"]) for u in r["units"]) or "[] no run live")
    l2 = ("%s%s" % (_who_line(r["act"]) if r["act"] else "no act written",
                    "; cancelled before start: %s" % ", ".join(r["cancelled"]) if r["cancelled"] else ""))
    if mode == "kill":
        l2 += "; " + "; ".join(u.get("bookkeeping", "") for u in r["units"])[:300]
    return (FAILED if bad else OK), [head[:400], l2[:400],
                                                             "undo: pipe on %s --why \"...\" (new starts again)" % (
                                                                 o.target if not r["scope"].startswith("unit:") else
                                                                 "<scope>")]


def parse_dur(s):
    s = str(s).strip().lower()
    mult = {"s": 1, "m": 60, "h": 3600}
    try:
        return int(float(s[:-1]) * mult[s[-1]]) if s[-1] in mult else int(float(s))
    except (ValueError, IndexError):
        raise Refused("a duration is N, Ns, Nm or Nh, got %r" % s)


def cmd_void(o):
    r = void(o.run, o.why, mod=o.mod, owner_said=o.owner_said, per_ruling=o.per_ruling, idem=o.idem)
    if r["replayed"]:
        return ["%s is already void (%s): nothing changed" % (o.run, r["act"]["id"])]
    extra = _void_books(o, r)
    return ["%s: void; %d reservation(s) given back%s; no stage moved%s" % (
        o.run, r["given"], " (mod %s)" % r["mod"] if r["mod"] else "", extra),
            _who_line(r["act"]),
            "undo: maturation_dispatch.py unvoid %s --why \"...\" (the dispatch books); the store's void stands" % o.run]


def _void_books(o, r):
    return void_books(r.get("unit") or o.run, r["mod"], o.why, o.owner_said, r["act"]["id"], per_ruling=getattr(o, "per_ruling", None))


def void_books(unit, mod, why, owner_said, act_id, p=None, per_ruling=None):
    """The dispatch books (run_void.py's voids.jsonl) learn the void too, so every counter reader there honours it at
    once (a test store tells no books: RM_RUN_VOIDS_FILE names a test's). -> "; <what happened>"."""
    if not (is_live(p) or os.environ.get("RM_RUN_VOIDS_FILE")):
        return ""
    try:
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import run_void as RV
        if unit in RV.active():
            return "; dispatch books: already void"
        rec = {"act": "void", "ts": utc(time.time()), "unit": unit, "mod": mod, "item": None, "why": why.strip(),
               "by": who(), "kind": "hand", "result": UNM, "cost_usd": UNM, "control_act": act_id}
        if owner_said:
            rec["owner_said"] = owner_said
        if per_ruling:      # the Conductor's route travels with it (selftest_conductor_authority)
            rec["per_ruling"] = per_ruling
        RV._append(rec)
        return "; dispatch books: voids.jsonl line written"
    except Exception as e:      # noqa: BLE001
        return "; dispatch books NOT told (%s: %s): maturation_dispatch.py void %s --why ..." % (type(e).__name__, e,
                                                                                                unit)


def cmd_grant(o):
    if o.resource not in ("look", LOOK):
        raise Refused("grant takes `look` in this slice (other consumables: pipe add <Mod> <res> <N>)")
    if not (o.owner_said or o.per_ruling):
        raise Refused("a granted look is his: pass --owner-said \"<his words>\" (or --per-ruling <id>)")
    try:
        n = int(o.n)
    except ValueError:
        raise Refused("grant needs +N, got %r" % o.n)
    m = scope_of(o.mod)[4:]
    st = None
    try:
        with open(os.path.join(concepts_dir(), m, "stage.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError):
        pass
    win = (look_window(st) if st else None) or ""
    r = grant(m, LOOK, n, o.why, win=win, owner_said=o.owner_said, per_ruling=o.per_ruling, idem=o.idem, base=1)
    if r["replayed"]:
        return ["%s look: already granted as %s (idempotency key %s): nothing changed" % (m, r["act"]["id"], o.idem)]
    t = tick_now()
    return ["%s look (window %s): granted %d -> %d" % (m, win or "none", r["before"]["granted"], r["after"]["granted"]),
            _who_line(r["act"]) + ("; " + t if t else ""),
            "undo: pipe grant %s look %+d --why \"...\" --per-ruling %s" % (m, -n, r["act"]["id"])]


def doctor():
    try:
        c = read()
        ok = c.execute("PRAGMA quick_check").fetchone()[0]
        lines = ["store %s: quick_check %s, rev %d" % (db_path(), ok, rev(c))]
        c.close()
        lines.append("reconcile: abandoned %s" % (reconcile() or "[] none"))
        return OK, lines
    except Unreadable as e:
        return UNREADABLE, ["CONTROL UNREADABLE: %s" % e,
                            "fix: missing -> `pipe init --import`; permission -> chmod u+rw; corrupt -> move it aside "
                            "(keep it) and `pipe init --import`; locked -> find the writer (fuser %s)" % db_path()]


def main(argv=None):
    av = list(sys.argv[1:] if argv is None else argv)
    if av[:1] in (["set"], ["add"], ["reset"], ["limit"], ["undo"], ["queue"]):
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import pipeline_control as PC
        return PC.main(av)
    if av[:1] == ["hook"]:      # the run's PostToolUse hook: as fast and as quiet as possible
        db = av[av.index("--db") + 1] if "--db" in av else None
        code, text = hook(db)
        if text:
            sys.stderr.write(text + "\n")
        return code
    ap = argparse.ArgumentParser(prog="pipe", description=__doc__.split("\n\n")[0])
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="verb", required=True)

    def w(p):
        p.add_argument("--why", required=True)
        p.add_argument("--owner-said")
        p.add_argument("--per-ruling")
        p.add_argument("--idem", help="idempotency key: a retried command with the same key changes nothing")
        return p
    for v in ("on", "off"):
        p = w(sub.add_parser(v))
        p.add_argument("target")
    p = w(sub.add_parser("stop"))
    p.add_argument("target")
    p.add_argument("--write-now", action="store_true", help="stop now, write where you are, end")
    p.add_argument("--at-easy-spot", action="store_true", help="finish the unit in hand, write where you are, end "
                                                               "(the default; name it anyway)")
    p.add_argument("--kill", action="store_true", help="FORCE KILL: SIGKILL the whole cgroup, no write")
    p.add_argument("--deadline", help="after it, a writing stop escalates to --kill (default 5m for --write-now)")
    p = sub.add_parser("show")
    p.add_argument("mod", nargs="?")
    p.add_argument("--json", action="store_true", dest="json2")
    p = sub.add_parser("why")
    p.add_argument("mod")
    p = sub.add_parser("log")
    p.add_argument("-n", type=int, default=10)
    p = w(sub.add_parser("void"))
    p.add_argument("run")
    p.add_argument("--mod")
    p = w(sub.add_parser("grant"))
    p.add_argument("mod")
    p.add_argument("resource")
    p.add_argument("n")
    p = sub.add_parser("init")
    p.add_argument("--import", action="store_true", dest="do_import")
    sub.add_parser("doctor")
    for v in ("condition", "ended", "escalate"):
        p = sub.add_parser(v)
        p.add_argument("run")
        p.add_argument("--db")
    p = sub.add_parser("reap")
    p.add_argument("unit")
    try:
        o = ap.parse_args(av)
    except SystemExit as e:
        return REFUSED if e.code else OK
    as_json = o.json or getattr(o, "json2", False)
    code = OK
    try:
        if o.verb in ("condition", "ended", "escalate"):
            if o.db:
                os.environ["RM_CONTROL_DB"] = o.db
            if o.verb == "condition":
                code, line = condition(o.run)
                print(line)
                return code
            print(ended(o.run) if o.verb == "ended" else escalate(o.run))
            return OK
        if o.verb == "reap":
            return reap(o.unit)
        if o.verb == "init":
            p = init(db_path())     # a test process gets its own store here too, never the live one
            c = read(p)
            lines = ["store %s initialised (rev %d)" % (p, rev(c))]
            c.close()
            if o.do_import:
                lines += import_live(p)
        elif o.verb == "doctor":
            code, lines = doctor()
        elif o.verb in ("on", "off"):
            lines = cmd_switch(o, o.verb == "off")
        elif o.verb == "stop":
            code, lines = cmd_stop(o)
        elif o.verb == "show":
            lines = show(o.mod, as_json=as_json)
        elif o.verb == "why":
            lines = [why(o.mod)]
        elif o.verb == "log":
            lines = log(o.n)
        elif o.verb == "void":
            lines = cmd_void(o)
        elif o.verb == "grant":
            lines = cmd_grant(o)
    except Refused as e:
        print("pipe: REFUSED: %s" % e)
        return REFUSED
    except Unreadable as e:
        print("CONTROL UNREADABLE: %s (nothing launches until it is repaired: pipe doctor)" % e)
        return UNREADABLE
    except Exception as e:      # noqa: BLE001  a failure is named, never a calm empty answer
        print("pipe: FAILED: %s: %s" % (type(e).__name__, e))
        return FAILED
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
