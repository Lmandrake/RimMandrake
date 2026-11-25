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

  switches      one row per (scope, layer). scope: all | mod:<M> | stage:<S> | item:<ID> | family:<F> | role:<R> |
                game:<G> (one game: an in-game run's spec names its game).
                layer: control (`pipe off`, `pipe stop`, `maturation_dispatch.py pause`) or owner (his hold, imported
                from mod_owner_hold.json with his words). Any live row on one of a run's scopes refuses it. `pipe on`
                lifts the control row only: his owner row stays (`mod_owner_hold.py lift` lifts it, with his words or as the
                Conductor's lift, CONDUCTOR_LIFT).
  runs          every admitted launch: the unit name fixed BEFORE systemd-run, family, mod, item, stage, role, model.
                state: admitted -> started (its ExecCondition passed) -> ended | killed; or cancelled (a `pipe off`
                committed first), refused (the condition found it no longer authorised), fail_launch (systemd-run said
                no), abandoned (reconcile: it never started and its launcher is gone).
  reservations  a consumable held for a run: held -> charged at VALIDATED settlement, or released; charged -> voided.
  grants        more of a consumable for a mod in one accounting window (`pipe grant <Mod> look +N`).
  queue         the advancing order (`pipe queue top|bottom|move|drop|add`): a position per mod and, apart from it, its
                membership (critique 23); the tick's advancing list reads it (queue_apply).
  mod_models    one mod's builder launches pinned to a model (`pipe model <Mod> fable|default`; mod_model.py).
  adjustments   the typed counts and limits (`pipe set|add|reset|limit`): a count's delta at a revision, a limit's
                value; `pipe undo <act>` is a compensating act, refused with the later acts it would break.
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

  pipe on|off <all|Mod|stage|item|family:F|role:R|game:G> --why ... [--owner-said ...]
                         game:ArchBig holds one game (any game name, any case; game:a still works): no run starts
                         on it; in-game runs go to the other game
  pipe stop <scope|unit> --write-now|--at-easy-spot|--kill --why ... [--deadline 5m]
  pipe show [Mod] [--json]   pipe why <Mod>   pipe log [-n N]
  pipe void <run> --why ...   pipe grant <Mod> look +N --why ... --owner-said ...|--per-ruling ...
  pipe set|add|reset|limit|queue|undo ...   (consumable counts, limits and the queue: pipeline_control.py)
  pipe model <Mod> <fable|default> --why ...   that mod's builders on that model, their caps scaled to its price
  pipe init [--import]   pipe doctor
Exit codes: 0 done, 2 refused, 3 could not look (the store is unreadable), 4 failed (an error that is neither).
Every write prints at most 3 lines (before -> after; act id + revision; the undo command). Selftest: selftest_control.py.
"""
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
sys.path.insert(0, HERE) if HERE not in sys.path else None
import probe_result as P  # noqa: E402  a read of systemd or a cgroup answers value, empty or could-not-look
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
    "game_deploy": "maturation_dispatch.game_deploy_unit (rm-game-deploy-*): a mod's game copy deployed, zero tokens",
    "stop_resume": "stop_resume.py sweep unit",
    "left_open_continue": "left_open_continue.py run unit (<run>-continue): a run that ended with work left",
    "testq": "testq/steward.py wake unit",
    "ops_held_filer": "ops_watch.start_held_filer (rm-ops-held-filer): files the alarms a sense pass held, outside the beat",
    "probe": "selftest probes (rm-probe-*)",
    "list_effect": "list_effect.py tick (rm-list-effect): runs list items' outcome checks, closes what holds; launches nothing",
    "list_dispatch": "list_dispatch.py tick (rm-list-dispatch): one detached helper per list item whose outcome check fails",
    "quiet_scan": "quiet_scan.py tick (rm-quiet-scan): one Sonnet run that reads quiet files while no mod step is live",
}
STAGES = ("intake", "designer", "preflight", "offline_build", "blind_challenge", "in_game", "pre_human", "his_walk",
          "passed")
STOP_MODES = ("write_now", "at_easy_spot", "kill")
# what a writing stop leaves behind: "continue" (the default) carries the run on in a fresh run once the cause of the
# stop is gone (its scope switch lifted, the account gate open to a new run: left_open_continue); "end" ends the work
# for good. A kill is never carried on (RIMMANDRAKE_CONTINUE_A_RUN_THE_CONDUCTOR_STOPPED_VOIDED_MEANS_NO_CARRY_ON)
STOP_THEN = ("continue", "end")
DEFAULT_STOP_MODE = "at_easy_spot"  # his default (card 2026-11-18); `pipe` always prints which mode it used
# budget: danger=a run that is told to write now never stops; evidence=3 of 15 write_now stops reached it and were escalated;
# budget: longest=599s (control.db stops, 14 days to 2026-11-24); stays=the owner's stop, and the deadline is part of the stop
# budget: he orders
WRITE_NOW_DEADLINE_S = 300
# budget: danger=a process that does not die, or a locked store, holds a kill; its reach leaves no record; no record of its run
KILL_WAIT_S = 1.0
# budget: danger=a process that does not die, or a locked store, holds a kill; its reach leaves no record; no record of its run
KILL_STORE_WAIT_S = 0.2           # a unit kill tries the store this long, then kills without it
ESCALATE_SLACK_S = 2.0              # a deadline timer may fire this early against the wall clock
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
CREATE TABLE IF NOT EXISTS adjustments (id INTEGER PRIMARY KEY AUTOINCREMENT, act TEXT NOT NULL, mod TEXT NOT NULL,
  res TEXT NOT NULL, kind TEXT NOT NULL, verb TEXT, delta INTEGER, value INTEGER, state TEXT NOT NULL DEFAULT 'live',
  undone_by TEXT, at REAL);
CREATE TABLE IF NOT EXISTS queue (mod TEXT PRIMARY KEY, pos REAL, member INTEGER NOT NULL DEFAULT 1, act TEXT, at REAL);
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
    """True in a test: a test process (test_process.under_test, the one definition), a test that pointed the owner hold
    at its own file, or a process whose dispatcher state is not the live one. A test never reaches the live store."""
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import test_process as _tp
    if _tp.under_test() or os.environ.get("RM_OWNER_HOLD_FILE"):
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


# budget: danger=a locked store holds its caller; its reach leaves no record; no record of its run
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
    # budget: danger=a locked store holds its caller; its reach leaves no record; no record of its run
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

    # budget: danger=a locked store holds its caller; its reach leaves no record; no record of its run
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


# budget: danger=a locked store holds its caller; its reach leaves no record; no record of its run
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


def mod_folders():
    """-> the mods with a shipping folder (src/RimMandrake|RimStarWars|RimUtinni/<Mod>/About/About.xml), seeded or
    not. RM_CONTROL_MOD_FOLDERS="A,B" names them for a test."""
    env = os.environ.get("RM_CONTROL_MOD_FOLDERS")
    if env is not None:
        return [m for m in env.split(",") if m]
    out = []
    for tier in ("RimMandrake", "RimStarWars", "RimUtinni"):
        d = os.path.join(REPO, "src", tier)
        try:
            out += sorted(x for x in os.listdir(d) if os.path.isfile(os.path.join(d, x, "About", "About.xml")))
        except OSError:
            pass
    return out


def scope_of(t, strict=True, unseeded=False):
    """'all' | 'Mod' | 'mod:M' | 'stage:S' | 'item:ID' | a RIMMANDRAKE_/RIMMASTER_ id | 'family:F' | a family name |
    'role:R' -> the canonical scope. Raises Refused with the nearest names. unseeded: a mod with a shipping folder
    and no place in the pipeline yet is a mod too (`pipe off|on`: an admitted mod is switched off before its seed;
    RIMMANDRAKE_HOLD_NEW_CONCEPT_DISABLED_DESIGNER_CHAINS)."""
    t = str(t or "").strip()
    if t == "all":
        return "all"
    kind, _, name = t.partition(":")
    if not name:
        kind, name = None, t
    if kind == "unit" or (kind is None and name.startswith("rm-")):
        # a run's unit, as `pipe stop` takes it: `on`/`off` accept every scope `stop` does
        # (RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT: `pipe on unit:<u>` was "no scope kind")
        return "unit:" + (name[:-len(".service")] if name.endswith(".service") else name)
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
    if kind == "game":
        import game_names               # ArchBig, archsmall, b, archmagi.b -> the store's key, game:<letter>
        try:
            return "game:" + game_names.letter(name)
        except game_names.GameNameError as e:
            raise Refused(str(e))
    if kind not in (None, "mod"):
        raise Refused("no scope kind %r (all, mod:, stage:, item:, family:, role:, game:, unit:)" % kind)
    m = key(name)
    if strict:
        mods = known_mods()
        folders = mod_folders() if unseeded else []
        if m not in mods and m not in folders:
            near = difflib.get_close_matches(m, mods + [f for f in folders if f not in mods], 4, .3)
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
    if spec.get("game"):                # the game an in-game run drives: `pipe off game:a` keeps every run off it
        import game_names               # a spec naming ArchSmall lives in the store's scope game:b
        try:
            out.append("game:" + game_names.letter(spec["game"]))
        except game_names.GameNameError:
            out.append("game:" + str(spec["game"]).strip().lower())     # unknown: its own scope, never another game's
    return out


def game_held(game, p=None, now=None):
    """-> why game `game` is held (a live `pipe off game:<g>` switch), or None. Raises Unreadable when the store cannot
    be read, so a reader can never take "could not look" for "not held". The per-game hold: the owner walks game a, and
    every run that can use game b goes there (RIMMANDRAKE_SPLIT_SECOND_GAME_MODS_FOLDER_SHARED_WITH_FIRST; his words,
    2026-11-20 3:40 PM PST: "You should not have been waiting for the game. there are two games")."""
    import game_names
    g = game_names.letter("a" if game is None or not str(game).strip() else game)
    c = read(p)
    try:
        rows = blocking(c, ["game:" + g], now)
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()
    return describe(rows[0]) if rows else None


def game_holds(p=None, now=None):
    """-> {game: why} for every live game switch. Raises Unreadable."""
    return {r["scope"][5:]: describe(r) for r in switches(p, now) if r["scope"].startswith("game:")}


def _live(row, now):
    return row["until"] is None or now < float(row["until"])


def blocking(c, scopes, now=None):
    """-> the live switch rows on any of `scopes` (owner first, then control; the narrowest scope last)."""
    now = time.time() if now is None else now
    q = "SELECT * FROM switches WHERE scope IN (%s)" % ",".join("?" * len(scopes))
    rows = [r for r in c.execute(q, scopes).fetchall() if _live(r, now)]
    return sorted(rows, key=lambda r: (0 if r["layer"] == "owner" else 1, scopes.index(r["scope"])))


def describe(r):
    import game_names                   # a game's scope reads by its name (game:ArchBig); the store keeps game:a
    sc = game_names.show_scope(r["scope"])
    if r["layer"] == "owner":
        return "HELD BY OWNER (%s, %s): %s" % (sc, r["date"] or "?", r["said"] or r["why"])
    until = " until %s" % pac(r["until"]) if r["until"] else ""
    return "OFF (%s, act %s at %s%s): %s" % (sc, r["act"], r["at_pacific"], until, r["why"])


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


def _withdraw_stops(c, rows, now):
    """Withdraw the stop orders in `rows` that their run has not yet obeyed. -> (withdrawn, obeyed): a pending order
    (not yet delivered) is withdrawn silently; a delivered one ('seen') becomes 'withdrawn_owed', and the run's hook
    tells it once that the order is withdrawn; an order whose run already ended ('done', 'escalated') is obeyed and is
    listed, never revived. Item RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT."""
    withdrawn, obeyed = [], []
    for r in rows:
        r = dict(r)
        if r["state"] in ("pending", "seen"):
            c.execute("UPDATE stops SET state=?, ended_at=? WHERE id=? AND state=?",
                      ("withdrawn" if r["state"] == "pending" else "withdrawn_owed", now, r["id"], r["state"]))
            withdrawn.append(r)
        elif r["state"] in ("done", "escalated"):
            obeyed.append(r)
    return withdrawn, obeyed


def _stop_rows_in(c, scope):
    """The stop orders a `pipe on <scope>` lifts: a unit's own, or those of a stop act on exactly that scope."""
    if scope.startswith("unit:"):
        return c.execute("SELECT * FROM stops WHERE unit=?", (scope[5:],)).fetchall()
    return c.execute("SELECT s.* FROM stops s JOIN acts a ON a.id=s.act WHERE a.kind='stop' AND a.scope=?",
                     (scope,)).fetchall()


def switch(scope, off, why, layer="control", until=None, said=None, owner_said=None, per_ruling=None, idem=None,
           p=None, now=None, date=None, extra=None):
    """Write one switch. off=True: the row is written and every unstarted run in scope is cancelled, in ONE
    transaction. off=False: the row of that layer is removed (`on all` never lifts a mod's owner row). -> dict."""
    now = time.time() if now is None else now
    if layer not in LAYERS:
        raise Refused("no layer %r" % layer)
    if layer == "owner" and not (said or owner_said):
        raise Refused("his hold carries his words (--owner-said)")
    try:
        return _switch(scope, off, why, layer, until, said, owner_said, per_ruling, idem, p, now, date, extra)
    finally:
        if scope == "all":      # the containment permit follows the all-switch from every caller, not only `pipe`
            permit_sync(p=p, now=now)


def _switch(scope, off, why, layer, until, said, owner_said, per_ruling, idem, p, now, date, extra):
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
            if layer == "control":      # `on` also withdraws the stop orders on the scope not yet obeyed
                pend = [r for r in _stop_rows_in(c, scope) if r["state"] in ("pending", "seen")]
                if pend:
                    a = _act(c, "on", scope, dict(old) if old else None, {"withdrawn": [r["id"] for r in pend]}, why,
                             owner_said, per_ruling, idem, now=now)
                    wd, _ = _withdraw_stops(c, pend, now)
                    if old:
                        c.execute("DELETE FROM switches WHERE scope=? AND layer=?", (scope, layer))
                    still = [describe(r) for r in blocking(c, [scope], now)]
                    return {"act": a, "before": before, "cancelled": [], "still": still, "replayed": False,
                            "had": True, "withdrawn": wd}
            if not old:
                still = [describe(r) for r in blocking(c, [scope], now)]
                return {"act": None, "before": "ON" if not still else "OFF", "cancelled": [], "still": still,
                        "replayed": False, "had": False}
            a = _act(c, "on" if layer == "control" else "lift", scope, dict(old), None, why, owner_said, per_ruling,
                     idem, now=now)
            c.execute("DELETE FROM switches WHERE scope=? AND layer=?", (scope, layer))
        still = [describe(r) for r in blocking(c, [scope], now)]
        return {"act": a, "before": before, "cancelled": cancelled, "still": still, "replayed": False,
                "had": bool(old), "replaced": dict(old) if off and old and _live(old, now) else None}


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


# The Conductor may lift his hold too (owner, by card 2026-11-19: "yes... but Conductor should also be able to lift a
# Hold. We work together, don't use me as a bottleneck alone."): cited by this item id, with the Conductor's reason.
CONDUCTOR_LIFT = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE"


def lift_owner(mod, said=None, date=None, p=None, now=None, held_said=None, per_ruling=None, why=None):
    """Lift his hold on `mod` in the store, and remember the lifted (mod, date), so the file mirror's row stops holding
    at once. The authority is his words (`said`) or the Conductor's lift (`per_ruling` CONDUCTOR_LIFT and its `why`,
    recorded as the Conductor's act: no owner_said), never both, never neither. -> the store row lifted, or None when
    the store held no row for it."""
    his = isinstance(said, str) and bool(said.strip())
    cond = (per_ruling or "").strip() == CONDUCTOR_LIFT and isinstance(why, str) and bool(why.strip())
    if his == bool(per_ruling):
        raise Refused("lifting his hold takes his words (--said) or the Conductor's lift (--per-ruling %s --why "
                      "\"...\"), one of them" % CONDUCTOR_LIFT)
    if not his and not cond:
        raise Refused("the Conductor's lift cites --per-ruling %s and carries --why" % CONDUCTOR_LIFT)
    now = time.time() if now is None else now
    with txn(p) as c:
        old = c.execute("SELECT * FROM switches WHERE scope=? AND layer='owner'", ("mod:" + key(mod),)).fetchone()
        d = date or (old["date"] if old else "") or ""
        w = held_said if held_said is not None else (old["said"] if old else "") or ""
        if his:
            text, kw = "his hold lifted: %s" % said.strip(), {"owner_said": said.strip()}
        else:
            text, kw = "the Conductor lifted his hold: %s" % why.strip(), {"per_ruling": CONDUCTOR_LIFT}
        _act(c, "lift", "mod:" + key(mod), dict(old) if old else None, {"lifted": [key(mod), d, w]}, text,
             idem="lift:owner:%s:%s:%d" % (key(mod), d, int(now * 1000)), now=now, **kw)
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


def owner_lifts(p=None):
    """-> [(mod, date, his held words, his lifting words, the Conductor's reason)] of every lift of his hold through
    the store, oldest first: the mirror's `lifted` record (mod_owner_hold.mirror). His lift has the Conductor's reason
    None; the Conductor's lift has his lifting words ""."""
    out = []
    for a in _q("SELECT after, owner_said, per_ruling, why FROM acts WHERE kind='lift' ORDER BY rev", p=p):
        try:
            m, d, w = json.loads(a["after"])["lifted"]
        except (ValueError, KeyError, TypeError):
            continue
        cw = None
        if a["per_ruling"] == CONDUCTOR_LIFT and not a["owner_said"]:
            cw = (a["why"] or "").split(": ", 1)[-1]
        out.append((m, d, w, a["owner_said"] or "", cw))
    return out


def hold_owner(mod, said, date=None, p=None, now=None, extra=None):
    """Write his hold on `mod` into the store, with his words (the one writer of his hold; mod_owner_hold.py hold, then
    its mirror). The same words held again change nothing. -> switch()'s dict."""
    if not (isinstance(said, str) and said.strip()):
        raise Refused("his hold carries his words (--said)")
    now = time.time() if now is None else now
    d = date or utc(now)[:10]
    if extra is None:       # a hold held again keeps the design pass he allowed on it
        da = mod_holds(p, now).get(key(mod), {})
        extra = {"design_allowed": da["design_allowed"]} if da.get("store") and da.get("design_allowed") else None
    import hashlib
    return switch("mod:" + key(mod), True, "his hold: " + said.strip(), layer="owner", said=said.strip(),
                  owner_said=said.strip(), date=d, extra=extra, p=p, now=now, idem="hold:owner:%s:%s:%s" % (
                      key(mod), d, hashlib.sha1(said.strip().encode("utf-8")).hexdigest()[:12]))


def allow_design_owner(mod, said, date, p=None, now=None):
    """Write his words allowing a design-only pass onto the store's row of his hold on `mod`. The hold stays. -> the
    allowance. Raises KeyError when the store holds no row for it."""
    if not (isinstance(said, str) and said.strip()):
        raise Refused("allow-design takes his words (--said)")
    now = time.time() if now is None else now
    with txn(p) as c:
        old = c.execute("SELECT * FROM switches WHERE scope=? AND layer='owner'", ("mod:" + key(mod),)).fetchone()
        if not old:
            raise KeyError("%s is not held" % mod)
        try:
            ex = json.loads(old["extra"]) if old["extra"] else {}
        except ValueError:
            ex = {}
        ex["design_allowed"] = {"said": said.strip(), "date": date}
        _act(c, "allow_design", "mod:" + key(mod), dict(old), {"design_allowed": ex["design_allowed"]},
             "design pass allowed on his hold: %s" % said.strip(), owner_said=said.strip(), now=now)
        c.execute("UPDATE switches SET extra=? WHERE scope=? AND layer='owner'", (json.dumps(ex), "mod:" + key(mod)))
        return ex["design_allowed"]


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
        # charged on a covered verdict counts though no refusal round shows it); the store's charges carry the same
        # typed adjustments as `used`, so a look `pipe set|add` gives back can be reserved (slice review 7)
        charged = max(used, _used(c, mod, resource, charged))
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
    keeps its look. -> [run] released (metered as faults: the caller sounds _fault_alarm after its commit)."""
    out = []
    host = socket.gethostname()
    for r in c.execute("SELECT * FROM reservations WHERE state='held' AND pid IS NOT NULL AND host=?",
                       (host,)).fetchall():
        if not os.path.exists("/proc/%d" % r["pid"]):
            if _release(c, "id=?", (r["id"],), "fail_system: its holder (pid %d) died before settling" % r["pid"],
                        now, True):
                out.append(r["run"])
    return out


def reserve(mod, resource, run, win="", base=0, qty=1, p=None, now=None, pid=None, used=None):
    """Hold `qty` of one account for `run`, in one transaction: exactly one of two callers racing for the last unit
    gets it. -> (True, account) or (False, why). Raises Unreadable (fail closed: the caller runs nothing)."""
    now = time.time() if now is None else now
    mod = key(mod)
    reaped = []
    out = _reserve(mod, resource, run, win, base, qty, p, now, pid, used, reaped)
    for x in dict.fromkeys(reaped):     # after the commit: a dead holder's look released is a metered fault
        _fault_alarm(x, p)
    return out


def _reserve(mod, resource, run, win, base, qty, p, now, pid, used, reaped):
    with txn(p) as c:
        reaped += _reap(c, now)
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


def carry_stop(unit, books=None, p=None):
    """-> the stop that voided `unit` and leaves it to be carried on ({act, mode, scope, then, why}), or None. Yes only
    when EVERY void of the unit (the store's, by unit or run id, and the dispatch books' standing line `books`, from
    run_void.active()) comes from a writing stop act (at_easy_spot or write_now) that does not end the work
    (stop_then). A kill, a hand void (`pipe void`, `maturation_dispatch.py void`) or a stop with --end is None: that
    run stays void and is not carried on. No void at all is None too. Raises Unreadable."""
    rr = _q("SELECT id FROM runs WHERE unit=? OR id=?", (unit, unit), p=p, one=True)
    ids = sorted({unit, "run_" + unit} | ({rr["id"]} if rr else set()))
    acts = {r["act"] for r in _q("SELECT act FROM voids WHERE run IN (%s)" % ",".join("?" * len(ids)), ids, p=p)}
    if books and books.get("act") == "void":
        if not books.get("control_act"):
            return None     # a void by hand in the books, with no act of the store behind it
        acts.add(books["control_act"])
    out = None
    for aid in sorted(acts):
        a = _q("SELECT * FROM acts WHERE id=?", (aid,), p=p, one=True)
        a = dict(a) if a else None
        if not a or a["kind"] != "stop":
            return None
        try:
            mode = json.loads(a["after"] or "{}").get("mode")
        except (TypeError, ValueError, AttributeError) as e:
            raise Unreadable("act %s: its after is not a JSON object (%s: %s)" % (aid, type(e).__name__, e))
        if mode not in ("at_easy_spot", "write_now") or stop_then(a) != "continue":
            return None
        out = {"act": a["id"], "mode": mode, "scope": a["scope"], "then": "continue", "why": a["why"]}
    return out


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


# ---------------------------------------------------------------- typed counts and limits (slice 2), and undo
# The consumables the pipeline counts from its own records (coverage looks, runs and verdicts, blind cycles) are typed
# accounts here: an adjustment row per `pipe set|add|reset` (a delta written at a revision, so a run that completes
# after a set still counts: critique 8) and per `pipe limit` (the latest live row binds; NULL = the pipeline's own
# default). `undo` is a compensating act, refused with the later acts it would break (critique 16). Item
# RIMMANDRAKE_TYPE_EVERY_CONSUMABLE_AS_ACCOUNT_OLD_COUNTERS_GO; readers: pipeline_control.used / .limit.

ADJ_SQL = ("CREATE TABLE IF NOT EXISTS adjustments (id INTEGER PRIMARY KEY AUTOINCREMENT, act TEXT NOT NULL, mod TEXT "
           "NOT NULL, res TEXT NOT NULL, kind TEXT NOT NULL, verb TEXT, delta INTEGER, value INTEGER, state TEXT NOT NULL "
           "DEFAULT 'live', undone_by TEXT, at REAL)")


def _has_adj(c):
    """A store initialised before slice 2 has no adjustments table: it has no adjustment (empty, not unreadable)."""
    return bool(c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='adjustments'").fetchone())


def _adj(c, mod, res, kind):
    if not _has_adj(c):
        return []
    return [dict(r) for r in c.execute("SELECT * FROM adjustments WHERE mod=? AND res=? AND kind=? AND state='live' "
                                       "ORDER BY id", (mod, res, kind)).fetchall()]


def _numeric(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _used(c, mod, res, measured):
    off = sum(r["delta"] or 0 for r in _adj(c, mod, res, "count"))
    return max(0, measured + off) if _numeric(measured) else measured


def _limit(c, mod, res, default):
    rows = _adj(c, mod, res, "limit")
    return default if not rows or rows[-1]["value"] is None else rows[-1]["value"]


def used(mod, res, measured, p=None):
    """The count a reader compares with its limit: the pipeline's own `measured` count plus every live adjustment,
    never below 0 (a non-number, e.g. UNMEASURED, is returned as it is). Raises Unreadable."""
    c = read(p)
    try:
        return _used(c, key(mod), res, measured)
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()


def limit(mod, res, default, p=None):
    """The most allowed: the latest live `pipe limit`, else `default` (the pipeline's own setting). Raises Unreadable."""
    c = read(p)
    try:
        return _limit(c, key(mod), res, default)
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()


def subjects(res, p=None):
    """-> {account key}: every subject holding a live adjustment (a count or a limit) of `res`. One read for a reader that
    judges many subjects (testpilot_route.routed: every open item), so a subject outside it reads its pipeline count and
    default limit unasked. Raises Unreadable."""
    c = read(p)
    try:
        if not _has_adj(c):
            return set()
        return {r[0] for r in c.execute("SELECT DISTINCT mod FROM adjustments WHERE res=? AND state='live'", (res,))}
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()


def set_account(mod, res, n, why, measured=None, verb="set", owner_said=None, per_ruling=None, idem=None, p=None,
                now=None):
    """`pipe set|add|reset <Mod> <res> <N>`: one adjustment at this revision. set/reset: the count reads N (0) now,
    given the pipeline's own `measured` count (None or UNMEASURED: the adjustment total is pinned to N); add: moves it
    by N. -> {"act", "before", "after", "replayed"}."""
    if verb not in ("set", "add", "reset"):
        raise Refused("a count is set, add or reset, not %r" % verb)
    if not str(res or "").strip():
        raise Refused("a count names its consumable")
    n = 0 if verb == "reset" else int(n)
    now = time.time() if now is None else now
    mod = key(mod)
    with txn(p) as c:
        hit = _idem_hit(c, idem)
        if hit:
            return {"act": hit, "before": None, "after": _used(c, mod, res, measured), "replayed": True}
        c.execute(ADJ_SQL)
        off = sum(r["delta"] or 0 for r in _adj(c, mod, res, "count"))
        raw = (measured + off) if _numeric(measured) else off
        if _numeric(measured):  # the count it reads lands exactly on the clamped target: no hidden debt below 0
            delta = max(0, (max(0, raw) + n) if verb == "add" else n) - raw
        else:
            delta = n if verb == "add" else n - raw
        before = _used(c, mod, res, measured)
        a = _act(c, verb, "mod:%s/%s" % (mod, res), {"used": before, "measured": measured},
                 {"delta": delta, "reads": None}, why, owner_said, per_ruling, idem, now=now)
        c.execute("INSERT INTO adjustments (act, mod, res, kind, verb, delta, at) VALUES (?,?,?, 'count', ?,?,?)",
                  (a["id"], mod, res, verb, delta, now))
        return {"act": a, "before": before, "after": _used(c, mod, res, measured), "replayed": False, "delta": delta}


def set_limit(mod, res, n, why, owner_said=None, per_ruling=None, idem=None, p=None, now=None):
    """`pipe limit <Mod> <res> <N|default>` (n None = the pipeline's own default). -> {"act", "before", "after"}."""
    now = time.time() if now is None else now
    mod = key(mod)
    n = None if n in (None, "default") else int(n)
    with txn(p) as c:
        hit = _idem_hit(c, idem)
        if hit:
            return {"act": hit, "before": None, "after": _limit(c, mod, res, None), "replayed": True}
        c.execute(ADJ_SQL)
        before = _limit(c, mod, res, None)
        a = _act(c, "limit", "mod:%s/%s" % (mod, res), {"limit": before}, {"limit": n}, why, owner_said, per_ruling,
                 idem, now=now)
        c.execute("INSERT INTO adjustments (act, mod, res, kind, verb, value, at) VALUES (?,?,?, 'limit', 'limit', ?,?)",
                  (a["id"], mod, res, n, now))
        return {"act": a, "before": before, "after": n, "replayed": False}


# One mod's builder launches on a pinned model (`pipe model <Mod> fable|default`; mod_model.py, its boundary page
# design/specs/2026-11-19-mod-model-pin/boundary.md). A row per pinned mod; lifting the pin deletes it. A store made before
# the table existed has no pin (empty, not unreadable), as with the adjustments above.
MODEL_SQL = "CREATE TABLE IF NOT EXISTS mod_models (mod TEXT PRIMARY KEY, model TEXT NOT NULL, act TEXT, at REAL)"


def _has_models(c):
    return bool(c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='mod_models'").fetchone())


def mod_models(p=None):
    """-> {mod: model alias} of every pinned mod ({} when none is). Raises Unreadable: could not look is never none."""
    c = read(p)
    try:
        if not _has_models(c):
            return {}
        return {r["mod"]: r["model"] for r in c.execute("SELECT mod, model FROM mod_models").fetchall()}
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()


def set_model(mod, model, why, owner_said=None, per_ruling=None, idem=None, p=None, now=None):
    """`pipe model <Mod> <alias|default>`: pin the mod's builder launches to `model` (default: lift the pin). Refused,
    naming it, for a model mod_model cannot pin or price. -> {"act", "before", "after", "replayed"}."""
    now = time.time() if now is None else now
    m = key(mod)
    if not m:
        raise Refused("pipe model names a mod")
    after = None if model in (None, "default") else str(model).strip()
    if after is not None:
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import mod_model as MM
        try:
            MM.pin_id(after)
            MM.cap_scale(after)
        except KeyError as e:   # role_launch.UnknownModel: named, nothing written
            raise Refused(str(e))
    with txn(p) as c:
        hit = _idem_hit(c, idem)
        if hit:
            return {"act": hit, "before": None, "after": after, "replayed": True}
        c.execute(MODEL_SQL)
        r = c.execute("SELECT model FROM mod_models WHERE mod=?", (m,)).fetchone()
        before = r["model"] if r else None
        a = _act(c, "model", "mod:%s/model" % m, {"model": before}, {"model": after}, why, owner_said, per_ruling, idem,
                 now=now)
        if after is None:
            c.execute("DELETE FROM mod_models WHERE mod=?", (m,))
        else:
            c.execute("INSERT OR REPLACE INTO mod_models (mod, model, act, at) VALUES (?,?,?,?)", (m, after, a["id"], now))
        return {"act": a, "before": before, "after": after, "replayed": False}


def cmd_model(o):
    sc = scope_of(o.mod, unseeded=True)     # a wrong name is refused with the nearest names, as `pipe off` does
    if not sc.startswith("mod:"):
        raise Refused("pipe model takes a mod, not %s" % sc)
    m = sc[4:]
    r = set_model(m, o.model, o.why, owner_said=o.owner_said, per_ruling=o.per_ruling, idem=o.idem)
    if r["replayed"]:
        return ["%s model: already applied as %s (idempotency key %s): nothing changed" % (m, r["act"]["id"], o.idem)]
    if r["after"]:
        import mod_model as MM
        now_ = "%s (%s), its builder caps x%g" % (r["after"], MM.pin_id(r["after"]), float(MM.cap_scale(r["after"])))
    else:
        now_ = "the shipped models and caps"
    return ["%s builder model: %s -> %s; judges and the in-game driver keep theirs" % (
                m, r["before"] or "the shipped models and caps", now_),
            _who_line(r["act"]) + "; binds at the next launch",
            "undo: pipe model %s %s --why \"...\"" % (m, r["before"] or "default")]


def undo(act_id, why, owner_said=None, per_ruling=None, p=None, now=None, base=0):
    """`pipe undo <act>`: a compensating act (critique 16). A count or limit adjustment stops counting; a grant gets
    its negative (a look already consumed shows as a deficit); an OFF is lifted only while it is still the switch's
    own act. Refused, naming why, when a later act depends on it, when it was already undone, or for an act no undo
    inverts (void, import, hold: their own commands). A stop is withdrawn while its run has not obeyed it; an obeyed one
    says so and names the resume command; his stop (--owner-said) is withdrawn only by his word. -> {"ok", "why", "act",
    "line", "after"}."""
    now = time.time() if now is None else now
    r = _undo(act_id, why, owner_said, per_ruling, p, now, base)
    if r["ok"] and r["act"]["scope"] == "all":   # the permit follows an undone all-switch too (permit-never-ghosts)
        permit_sync(p=p, now=now)
    for unit, order in r.pop("timers", ()):   # after withdrawal commits, even an already-fired timer sees it
        warning = _disarm_escalation(unit, order)
        if warning:
            r["line"] += "; " + warning
    return r


def _undo(act_id, why, owner_said, per_ruling, p, now, base):
    no = lambda w: {"ok": False, "why": w, "act": None, "line": "NOT undone: " + w, "after": None}
    with txn(p) as c:
        a = c.execute("SELECT * FROM acts WHERE id=?", (act_id,)).fetchone()
        if not a:
            ids = [r[0] for r in c.execute("SELECT id FROM acts ORDER BY rev DESC LIMIT 200").fetchall()]
            return no("no act %r in the store; nearest: %s (pipe log)" % (
                act_id, ", ".join(difflib.get_close_matches(act_id, ids, n=3, cutoff=0.3)) or "none"))
        a = dict(a)
        prior = c.execute("SELECT id FROM acts WHERE undoes=?", (act_id,)).fetchone()
        if prior:
            return no("%s is already undone (by %s)" % (act_id, prior[0]))
        adj = c.execute("SELECT * FROM adjustments WHERE act=?", (act_id,)).fetchone() if _has_adj(c) else None
        if adj:
            adj = dict(adj)
            later = [dict(r) for r in c.execute(
                "SELECT * FROM adjustments WHERE mod=? AND res=? AND kind=? AND state='live' AND id>? ORDER BY id",
                (adj["mod"], adj["res"], adj["kind"], adj["id"])).fetchall()]
            if adj["kind"] == "count" and adj["verb"] == "add":    # adds commute; a later set or reset pinned the count
                later = [r for r in later if r["verb"] in ("set", "reset")]
            if later:
                return no("%s %s/%s is under later act(s) %s: undo those first (latest first)" % (
                    act_id, adj["mod"], adj["res"], ", ".join(r["act"] for r in later)))
            u = _act(c, "undo", a["scope"], {"undoes": act_id}, {"stops_counting": adj["id"]}, why, owner_said,
                     per_ruling, undoes=act_id, now=now)
            c.execute("UPDATE adjustments SET state='undone', undone_by=? WHERE id=?", (u["id"], adj["id"]))
            after = (_limit(c, adj["mod"], adj["res"], None) if adj["kind"] == "limit"
                     else sum(r["delta"] or 0 for r in _adj(c, adj["mod"], adj["res"], "count")))
            return {"ok": True, "why": None, "act": u, "after": after, "line": "%s %s/%s: %s undone (%s now %s)" % (
                adj["kind"], adj["mod"], adj["res"], act_id, "limit" if adj["kind"] == "limit" else "adjustment total",
                "the pipeline default" if after is None else after)}
        gs = [dict(r) for r in c.execute("SELECT * FROM grants WHERE act=?", (act_id,)).fetchall()]
        if gs:
            u = _act(c, "undo", a["scope"], {"undoes": act_id}, {"grant": -sum(g["qty"] for g in gs)}, why, owner_said,
                     per_ruling, undoes=act_id, now=now)
            for g in gs:
                c.execute("INSERT INTO grants (mod, resource, win, qty, act, why, owner_said, at) VALUES (?,?,?,?,?,?,?,?)",
                          (g["mod"], g["resource"], g["win"], -g["qty"], u["id"], why.strip(), owner_said, now))
            g = gs[0]
            # a look's base is its limit (1 unless `pipe limit` moved it), charges as admission reads them (slice
            # review 8: undo reported the base-0 balance, a false deficit)
            acc = (_account(c, g["mod"], LOOK, g["win"], _limit(c, g["mod"], LOOK, 1), used=0)
                   if g["resource"] == LOOK else _account(c, g["mod"], g["resource"], g["win"], base))
            return {"ok": True, "why": None, "act": u, "after": acc, "line": "%s %s (window %s): grant %s undone, "
                    "available %d%s" % (g["mod"], g["resource"], g["win"] or "none", act_id, acc["available"],
                                        " (a deficit: %d already consumed past it)" % -acc["available"]
                                        if acc["available"] < 0 else "")}
        if a["kind"] == "off":
            sw = c.execute("SELECT * FROM switches WHERE scope=? AND layer='control'", (a["scope"],)).fetchone()
            if not sw or sw["act"] != act_id:
                return no("%s OFF is no longer the switch's own act (now %s): `pipe on %s` lifts the current one" % (
                    act_id, sw["act"] if sw else "no switch", a["scope"]))
            prior = json.loads(a["before"] or "null")     # the switch row this off replaced (before-is-read)
            if not (isinstance(prior, dict) and prior.get("layer") == "control" and prior.get("scope") == a["scope"]):
                prior = None
            u = _act(c, "undo", a["scope"], dict(sw), prior, why, owner_said, per_ruling, undoes=act_id, now=now)
            if prior is None:
                c.execute("DELETE FROM switches WHERE scope=? AND layer='control'", (a["scope"],))
                return {"ok": True, "why": None, "act": u, "after": "ON", "line": "%s: OFF %s undone (ON)" % (
                    a["scope"], act_id)}
            cols = [r[1] for r in c.execute("PRAGMA table_info(switches)").fetchall()]
            c.execute("INSERT OR REPLACE INTO switches (%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols))),
                      [prior.get(k) for k in cols])
            after = "OFF" if _live(prior, now) else "ON"
            return {"ok": True, "why": None, "act": u, "after": after, "line": "%s: OFF %s undone; the OFF it replaced "
                    "is back, %s (%s)%s" % (a["scope"], act_id, prior.get("act") or "no act", str(prior.get("why"))[:60],
                                            "" if after == "OFF" else ", lapsed at its until: ON")}
        if a["kind"] == "stop":     # withdrawn while its run has not obeyed it (RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_...)
            if a.get("owner_said") and not owner_said:
                return no("%s is his stop (--owner-said): it binds; only his word withdraws it" % act_id)
            rows = c.execute("SELECT * FROM stops WHERE act=?", (act_id,)).fetchall()
            sw = None if a["scope"].startswith("unit:") else c.execute(
                "SELECT * FROM switches WHERE scope=? AND layer='control'", (a["scope"],)).fetchone()
            sw = sw if sw and sw["act"] == act_id else None
            live = [r for r in rows if r["state"] in ("pending", "seen")]
            if not live and not sw:
                ended = [dict(r) for r in rows if r["state"] in ("done", "escalated")]
                return no("%s was already obeyed (%s): nothing is left to withdraw. Resume the work: `python3 "
                          "src/RimMandrake/rimflow/detached_helper.py launch <ITEM> --resume <its session>` "
                          "(`detached_helper.py list` names the session)" % (
                              act_id, ", ".join("%s %s" % (r["unit"], r["state"]) for r in ended) or "no order is live"))
            u = _act(c, "undo", a["scope"], {"undoes": act_id}, {"withdrawn": [r["id"] for r in live],
                                                                 "switch_lifted": bool(sw)},
                     why, owner_said, per_ruling, undoes=act_id, now=now)
            wd, ob = _withdraw_stops(c, live, now)
            if sw:
                prior = json.loads(a["before"] or "null")
                if isinstance(prior, dict) and prior.get("layer") == "control" and prior.get("scope") == a["scope"]:
                    cols = [r[1] for r in c.execute("PRAGMA table_info(switches)").fetchall()]
                    c.execute("INSERT OR REPLACE INTO switches (%s) VALUES (%s)" % (",".join(cols), ",".join(
                        "?" * len(cols))), [prior.get(k) for k in cols])
                else:
                    c.execute("DELETE FROM switches WHERE scope=? AND layer='control'", (a["scope"],))
            told = [r["unit"] for r in wd if r["state"] == "seen"]
            return {"ok": True, "why": None, "act": u, "after": "withdrawn",
                    "timers": [(r["unit"], r["id"]) for r in wd if r["deadline"] is not None],
                    "line": "%s: stop %s withdrawn: %s%s%s" % (
                a["scope"], act_id, ", ".join(r["unit"] for r in wd) or "no order was live",
                "; new starts allowed again" if sw else "",
                "; %s already read it and is told on its next tool call that it is withdrawn" % ", ".join(told)
                if told else "")}
        return no("a %s act is not inverted by undo: use its own command (pipe on/off, pipe model, maturation_dispatch.py "
                  "unvoid, mod_owner_hold.py lift)" % a["kind"])


def import_accounts(pc_dir, p=None, now=None):
    """Opening balances: the old pipeline_control journal's counts and limits (control.jsonl, folded) become
    adjustments here, once each (idempotency key per key and value). -> lines."""
    path = os.path.join(pc_dir, "control.jsonl")
    try:
        with open(path, encoding="utf-8") as f:
            lines = [json.loads(x) for x in f if x.strip()]
    except FileNotFoundError:
        return ["old counters: no journal at %s ([] nothing to import)" % path]
    except (OSError, ValueError) as e:
        raise Unreadable("the old counter journal %s: %s" % (path, e))
    st = {"counts": {}, "limits": {}}
    for x in lines:
        if x.get("sec") in st:
            if x.get("after") is None:
                st[x["sec"]].pop(x.get("name"), None)
            else:
                st[x["sec"]][x["name"]] = x["after"]
    out = []
    for sec, rows in sorted(st.items()):
        for k, v in sorted(rows.items()):
            mod, _, res = k.partition("/")
            idem = "import:pc:%s:%s:%s" % (sec, k, v)
            why = "opening balance from %s (%s)" % (path, sec)
            r = (set_account(mod, res, int(v), why, verb="add", idem=idem, per_ruling="import", p=p, now=now)
                 if sec == "counts" else set_limit(mod, res, v, why, idem=idem, per_ruling="import", p=p, now=now))
            out.append("%s %s = %s %s" % (sec, k, v, "already imported" if r["replayed"] else "imported (%s)" %
                                          r["act"]["id"]))
    return out or ["old counters: the journal holds no count or limit ([] nothing to import)"]


# ---------------------------------------------------------------- the queue (slice 3)
# Item RIMMANDRAKE_ADD_PIPE_QUEUE_VERBS_QUEUE_VIEW_PRINTS_MEGABYTES. The shipped advancing list
# (maturation_dispatch.json) is the base; a row here gives a mod a position, or takes it out (member 0) or adds it
# (member 1, a mod the list does not ship). Order and membership are separate: a dropped mod keeps its position.

Q_SQL = ("CREATE TABLE IF NOT EXISTS queue (mod TEXT PRIMARY KEY, pos REAL, member INTEGER NOT NULL DEFAULT 1, act TEXT, "
         "at REAL)")
QUEUE_OPS = ("top", "bottom", "move", "drop", "add")


def _queue_rows(c):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='queue'").fetchone():
        return {}
    return {r["mod"]: dict(r) for r in c.execute("SELECT * FROM queue").fetchall()}


def _queue_order(rows, mods, members_only=True):
    mods = [key(m) for m in mods]
    allm = mods + sorted(m for m, r in rows.items() if m not in mods and (r["member"] or not members_only))
    keep = [m for m in allm if not members_only or (rows.get(m) or {}).get("member", 1)]
    base = {m: i for i, m in enumerate(allm)}
    # a positioned mod sorts by its position; an unpositioned one keeps its shipped place after them
    return sorted(keep, key=lambda m: ((rows.get(m) or {}).get("pos") is None,
                                       (rows.get(m) or {}).get("pos") or 0, base[m]))


def queue_apply(mods, p=None):
    """-> the advancing list `mods` in the store's queue order and membership (no queue act: `mods` unchanged).
    Raises Unreadable (the tick then keeps the shipped order; admission refuses everything on that store anyway)."""
    c = read(p)
    try:
        return _queue_order(_queue_rows(c), mods)
    except sqlite3.Error as e:
        raise Unreadable(_err(e))
    finally:
        c.close()


def queue_act(op, mod, why, n=None, mods=None, owner_said=None, per_ruling=None, idem=None, p=None, now=None):
    """`pipe queue top|bottom|move <N>|drop|add <Mod>` -> {"act", "before", "after", "replayed"} (orders of members).
    top/bottom/move renumber every member's position in the new order; drop/add change membership only."""
    if op not in QUEUE_OPS:
        raise Refused("queue takes %s, not %r" % ("|".join(QUEUE_OPS), op))
    if op == "move":
        try:
            n = int(n)
        except (TypeError, ValueError):
            raise Refused("queue move <Mod> <position>: a whole number, got %r" % (n,))
        if n < 1:
            raise Refused("a queue position is 1 or more, got %d" % n)
    mod = key(mod)
    mods = list(mods or [])
    now = time.time() if now is None else now
    with txn(p) as c:
        hit = _idem_hit(c, idem)
        if hit:
            return {"act": hit, "before": None, "after": _queue_order(_queue_rows(c), mods), "replayed": True}
        c.execute(Q_SQL)
        rows = _queue_rows(c)
        before = _queue_order(rows, mods)
        a = _act(c, "queue", "mod:" + mod, {"order": before}, {"op": op, "n": n}, why, owner_said, per_ruling, idem,
                 now=now)
        unshipped = mod not in [key(m) for m in mods]
        if op == "drop" or (op == "add" and not (unshipped and (rows.get(mod) or {}).get("pos") is None)):
            # membership only: a dropped mod keeps its position, an added one returns to it (critique 23)
            c.execute("INSERT OR REPLACE INTO queue (mod, pos, member, act, at) VALUES (?,?,?,?,?)",
                      (mod, (rows.get(mod) or {}).get("pos"), 1 if op == "add" else 0, a["id"], now))
        else:
            # a position: every member (and the target, member or not) is renumbered in the new order, so an
            # unshipped mod added at the end leaves the others where they were; membership is never changed here
            order = [m for m in _queue_order(rows, mods, members_only=False) if m != mod]
            at = 0 if op == "top" else len(order) if op in ("bottom", "add") else min(n - 1, len(order))
            order.insert(at, mod)
            for i, m in enumerate(order):
                r0 = rows.get(m) or {}
                member = 1 if (m == mod and op == "add") else r0.get("member", 1)
                c.execute("INSERT OR REPLACE INTO queue (mod, pos, member, act, at) VALUES (?,?,?,?,?)",
                          (m, i + 1, member, a["id"] if m == mod else r0.get("act"), now))
        return {"act": a, "before": before, "after": _queue_order(_queue_rows(c), mods), "replayed": False}


def shipped_advancing():
    """-> maturation_dispatch.json's advancing list (the queue's base) from the live tick's tree (DISPATCH_ROOT), else
    this tree: a queue edit renumbers against the list the tick reads (slice review 5). The tick may widen that list
    with seeded Designer concepts before it applies the queue; those keep their place after the positioned mods."""
    own = os.path.join(DISPATCH_ROOT, "src", "RimMandrake", "rimflow", "maturation_dispatch.json")
    with open(own if os.path.isfile(own) else os.path.join(HERE, "maturation_dispatch.json"), encoding="utf-8") as f:
        return list(json.load(f).get("advancing") or [])


def cmd_queue(o):
    mods = shipped_advancing()
    if not o.op or o.op == "list":
        c = read()
        try:
            rows = _queue_rows(c)
        finally:
            c.close()
        order = _queue_order(rows, mods)
        out = _queue_order(rows, mods, members_only=False)
        dropped = [m for m in out if m not in order]
        return ["queue (%s): %s" % ("the shipped advancing order, no queue act" if not rows else "store",
                                     " > ".join(order) or "[] empty"),
                "dropped (kept in order, out of the queue): %s" % (", ".join(dropped) or "[] none"),
                "shipped list: %s" % " > ".join(mods)]
    if not o.mod:
        raise Refused("pipe queue %s <Mod>" % o.op)
    sc = scope_of(o.mod)
    if not sc.startswith("mod:"):
        raise Refused("pipe queue takes a mod, not %s" % sc)
    m = sc[4:]
    r = queue_act(o.op, m, o.why or "", n=o.n, mods=mods, owner_said=o.owner_said, per_ruling=o.per_ruling,
                  idem=o.idem)
    if r["replayed"]:
        return ["queue %s %s: already done as %s (idempotency key %s): nothing changed" % (o.op, m, r["act"]["id"],
                                                                                         o.idem)]
    return ["queue %s %s: %s -> %s" % (o.op, m, " > ".join(r["before"]) or "[]", " > ".join(r["after"]) or "[]"),
            _who_line(r["act"]), "undo: pipe queue <top|bottom|move|drop|add> <Mod> --why \"...\" (a queue act is "
                                 "changed by the next one)"]


# ---------------------------------------------------------------- slice 4: forecast, export, containment permit
# Item RIMMANDRAKE_FORECAST_ON_SHARED_PLANNER_DROPIN_MIRROR_DEADMAN.

DISPATCH_ROOT = "/home/mandrake/rm/dispatch"     # rm-maturation-dispatch.service's tree: `pipe next` runs ITS code
PERMIT_NAME = "permit"
DROPIN_NAME = "50-rm-control-permit.conf"


def forecast_cmd(within="30m"):
    """-> (the tree named, argv): `maturation_dispatch.py next --within W` from the tree the live tick runs (its own
    decide/prioritise/admit, dry, on a moving clock: critique 19's limit, an agent's result is not forecast), else
    this tree, said so."""
    w = str(within or "30m").strip()
    if not (w[:-1] if w[-1:] in "smhd" else w).isdigit():
        raise Refused("pipe next takes a window like 30m, 2h, 1d, got %r" % within)
    own = os.path.join(DISPATCH_ROOT, "src", "RimMandrake", "rimflow", "maturation_dispatch.py")
    py = "/usr/bin/python3" if os.path.exists("/usr/bin/python3") else sys.executable
    if os.path.isfile(own):
        return "%s (the live tick's tree)" % DISPATCH_ROOT, [py, own, "next", "--within", w]
    return "%s (this tree: the tick's tree has no maturation_dispatch.py)" % REPO, [
        py, os.path.join(HERE, "maturation_dispatch.py"), "next", "--within", w]


NEXT_BRIEF_MAX = 1500      # next-fits-a-screen: `pipe next` without --full prints fewer characters than this
NEXT_STARTS_SHOWN = 5


def _cut(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1] + "…"


def _reason_head(why):
    """A waiting mod's reason, up to its first ` (` or `: ` (`HELD BY OWNER 2026-11-16`, `OFF by pipe`), at most 70
    characters: mods that wait for the same reason share one line."""
    s = " ".join(str(why or "no reason given").split())
    cuts = [i for i in (s.find(" ("), s.find(": ")) if i >= 8]
    return _cut(s[:min(cuts)] if cuts else s, 70)


def forecast_brief(fc, head, limit=NEXT_BRIEF_MAX):
    """The dispatch forecast (maturation_dispatch.forecast's JSON) in under `limit` characters: what starts, when and
    by which rule; one line per reason the other mods wait, naming every mod; each UNMEASURED part and role cut to one
    short line. A start is never cut; any other line past the limit is, and a last line says how many and where."""
    mins = int(float(fc.get("within_s") or 0) // 60)
    t0 = fc.get("at") or 0
    out = ["%s, from %s, the next %d min (pipe next --full: every reason in full)" % (head, fc.get("at_pac", UNM), mins)]
    starts = fc.get("launches") or []
    for x in starts[:NEXT_STARTS_SHOWN]:
        k = x.get("launch") or {}
        out.append(_cut("WILL START %s (+%d min): %s %s, model %s, by %s" % (
            x.get("at_pac", UNM), (float(x.get("at") or t0) - t0) // 60, x.get("mod"), k.get("kind", "run"),
            k.get("model", UNM), k.get("rule", UNM)), 160))
    if len(starts) > NEXT_STARTS_SHOWN:
        out.append("and %d more start(s): pipe next --full" % (len(starts) - NEXT_STARTS_SHOWN))
    if not starts:
        out.append("NOTHING WILL START in the next %d min%s" % (mins, " (but see UNMEASURED below)"
                                                               if fc.get("unmeasured") else ""))
    keep = len(out)
    groups = {}
    for b in fc.get("blocked") or []:
        groups.setdefault((b.get("decision"), _reason_head(b.get("why"))), []).append(str(b.get("mod")))
    for (dec, why), mods in groups.items():
        out.append("waits, %s, %s (%d): %s" % (dec, why, len(mods), ", ".join(mods)))
    out += [_cut(u, 140) for u in fc.get("unmeasured") or []]
    out += [_cut(str(r).split(";")[0], 120) for r in fc.get("roles") or []]
    cut = 0
    while len("\n".join(out)) > limit - 50 and len(out) > keep:
        out.pop()
        cut += 1
    if cut:
        out.append("+%d line(s) cut to fit: pipe next --full" % cut)
    return out


def forecast(within="30m", runner=subprocess.run, full=False):
    """`pipe next [30m] [--full]` -> (rc, lines): the dispatch tree's own forecast, headed by the tree and its HEAD.
    Without --full, forecast_brief of the tree's JSON (next-fits-a-screen); --full prints the tree's text whole."""
    tree, argv = forecast_cmd(within)
    root = tree.split(" ", 1)[0]
    try:
        h = runner(["git", "-C", root, "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)
        head = h.stdout.strip() if h.returncode == 0 else "HEAD UNMEASURED (git exit %d)" % h.returncode
        # budget: danger=a hung forecast holds the pipe command; never reached in the 14 days to 2026-11-24; no record of its
        # budget: run
        r = runner(argv + ([] if full else ["--json"]), capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as e:
        return FAILED, ["pipe next: the forecast could not run (%s: %s)" % (type(e).__name__, e)]
    if r.returncode:
        return FAILED, ["forecast by %s at %s" % (tree, head)] + (r.stdout or "").rstrip("\n").splitlines()[-5:] + [
            "pipe next: the forecast exited %d: %s" % (r.returncode, (r.stderr or "").strip()[-200:])]  # cut-ok: terminal display
    if full:
        return OK, ["forecast by %s at %s" % (tree, head)] + (r.stdout or "").rstrip("\n").splitlines()
    try:
        fc = json.loads(r.stdout or "")
        if not isinstance(fc, dict):
            raise ValueError("not an object")
    except ValueError as e:
        return FAILED, ["forecast by %s at %s" % (tree, head), "pipe next: the forecast's JSON cannot be read (%s); "
                        "pipe next --full prints its text" % e]
    return OK, forecast_brief(fc, "forecast by %s at %s" % (tree.split(" (", 1)[0], head))


def export_acts(path, p=None):
    """Write every act, in revision order, as one JSON line each to `path` (replaced whole, atomically): the store's
    audit as a file a belt can commit. -> count."""
    rows = _q("SELECT * FROM acts ORDER BY rev", (), p)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return len(rows)


def permit_path(p=None):
    return os.path.join(os.path.dirname(os.path.abspath(p or db_path())), PERMIT_NAME)


def permit_sync(permit=None, p=None, now=None):
    """The containment permit: present while the store reads and no live `all` switch blocks; removed otherwise (an
    unreadable store is closed). -> line."""
    permit = permit or permit_path(p)
    now = time.time() if now is None else now
    try:
        c = read(p)
        try:
            rows = blocking(c, ["all"], now)
            r = rev(c)
        finally:
            c.close()
        why = describe(rows[0]) if rows else None
    except (Unreadable, sqlite3.Error) as e:
        why, r = "CONTROL UNREADABLE: %s" % e, None
    if why:
        try:
            os.unlink(permit)
        except FileNotFoundError:
            pass
        return "permit removed (%s): %s" % (permit, why)
    os.makedirs(os.path.dirname(permit), exist_ok=True)
    with open(permit + ".tmp", "w", encoding="utf-8") as f:
        f.write("rev %s at %s\n" % (r, pac(now)))
    os.replace(permit + ".tmp", permit)
    return "permit written (%s, rev %s)" % (permit, r)


def dropin_text(permit):
    return ("# rm-control containment (control.py, slice 4): a unit of this prefix starts only while the control\n"
            "# store's permit exists (permit_sync; `pipe off all` or an unreadable store removes it).\n"
            "[Unit]\nConditionPathExists=%s\n" % permit)


def install_dropin(prefix, permit, root=None):
    """Write <prefix>.service.d/50-rm-control-permit.conf and daemon-reload. -> the directory. The live prefixes
    (rm-detached-, rm-role-) are the Conductor's to install; a test uses a private rm-probe- prefix."""
    root = root or os.path.join(os.path.expanduser("~"), ".config", "systemd", "user")
    d = os.path.join(root, prefix + ".service.d")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, DROPIN_NAME), "w", encoding="utf-8") as f:
        f.write(dropin_text(permit))
    rc, out = _systemctl(["daemon-reload"], 30)
    if rc:
        raise RuntimeError("daemon-reload failed (rc %d): %s" % (rc, out.strip()[:120]))  # cut-ok: exception message
    return d


def remove_dropin(prefix, root=None):
    root = root or os.path.join(os.path.expanduser("~"), ".config", "systemd", "user")
    d = os.path.join(root, prefix + ".service.d")
    try:
        os.unlink(os.path.join(d, DROPIN_NAME))
        os.rmdir(d)
    except FileNotFoundError:
        pass
    _systemctl(["daemon-reload"], 30)


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
    reaped = []
    out = _admit(spec, now, p, reaped)
    for x in dict.fromkeys(reaped):     # after the commit: a dead holder's look released is a metered fault
        _fault_alarm(x, p)
    return out


def _admit(spec, now, p, reaped):
    with txn(p) as c:
        rows = blocking(c, run_scopes(spec), now)
        why = describe(rows[0]) if rows else None
        rid = "run_%s" % spec["unit"]
        replaced = None
        if not why:
            old = c.execute("SELECT id, state, pid, host FROM runs WHERE unit=?", (spec["unit"],)).fetchone()
            mine = old is not None and old["state"] == "admitted" and old["host"] == socket.gethostname() and (
                old["pid"] == os.getpid() or not os.path.exists("/proc/%d" % (old["pid"] or 0)))
            again = spec.get("reuse_name") and old is not None and old["state"] not in LIVE_STATES
            if old and (old["state"] in NEVER_RAN or mine or again):
                # that name never ran a payload, or its admission is this process's own earlier try (or a dead
                # launcher's) whose unit never reached its start check: it may be admitted again, under a run id of
                # its own, so the earlier try's unit (which carries the old id) finds no admission at its start check,
                # and every failed attempt is its own fault (round-two claim 1); a launcher that reuses one name for
                # every run (reuse_name) takes it again once the earlier run is over
                n = old["id"].rsplit("~", 1)[1] if "~" in old["id"] else "1"
                rid = "%s~%d" % (rid, (int(n) if n.isdigit() else 1) + 1)
                replaced = old["id"]    # replaced only once every check below passes (round-three claim 1)
            elif old:
                why = ("DUPLICATE: unit %s is already admitted (state %s): an ambiguous start is investigated, never "
                       "relaunched under the same name" % (spec["unit"], old["state"]))
        if not why:
            reaped += _reap(c, now)
            for res in spec.get("resources") or []:     # the try it replaces does not hold against it
                acc = _account(c, key(res.get("mod") or spec.get("mod")), res["resource"], res.get("win", ""),
                               int(res.get("base", 0)), exclude_run=replaced, used=res.get("used"))
                if acc["available"] < int(res.get("qty", 1)):
                    why = "%s: none available (%s)" % (res["resource"], fmt_acct(acc))
                    break
        if why:
            c.execute("INSERT INTO refusals (at, unit, family, mod, why) VALUES (?,?,?,?,?)",
                      (now, spec["unit"], spec["family"], spec.get("mod"), why))
            c.execute("DELETE FROM refusals WHERE id <= (SELECT MAX(id) FROM refusals) - 2000")
            return {"ok": False, "run": None, "why": why, "rev": rev(c)}
        if replaced:
            c.execute("DELETE FROM runs WHERE id=?", (replaced,))
            _release(c, "run=?", (replaced,), "replaced by its re-admission %s" % rid, now)
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
        elif r["state"] == "admitted":  # its start check never passed (the store unreadable there): it never ran
            c.execute("UPDATE runs SET state='refused', ended_at=?, result=?, why=? WHERE id=?",
                      (now, result, "its unit ended before its start check passed (unreadable store, or never run)",
                       run))
        c.execute("UPDATE stops SET state='done', ended_at=? WHERE run=? AND state IN ('pending','seen')", (now, run))
        n = _release(c, "run=?", (run,), "ended (%s) with no validated settlement" % result, now,
                     fault=r["state"] in LIVE_STATES)
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
        k = _release(c, "run=?", (run,), "%s: %s" % (state, why), now, fault) if n else 0
        if n:   # a run that reached a terminal state owes no stop order (an escalation then finds nothing to do)
            c.execute("UPDATE stops SET state='done', ended_at=? WHERE run=? AND state IN ('pending','seen')", (now, run))
    if fault and k:
        _fault_alarm(run, p)
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


RECEIPT_TAG = "rm-control"     # the journal tag of every hook line (journalctl --user -t rm-control)


def _hook_quiet():
    """A hook (condition / ended / escalate) writes NOTHING to fd 1 or 2: in a unit they are its StandardOutput=file:,
    which systemd reopens at offset 0 for every Exec* step, so a printed receipt overwrote the head of a role's result
    JSON and a run that succeeded read as failed (RIMMANDRAKE_MOVE_END_RECEIPT_OFF_RESULT_FILE_ROLES_FAILED; the same
    trap as wrapup.py's, 2026-11-04). Both fds go to /dev/null, a traceback included; the line goes to the journal."""
    null = os.open(os.devnull, os.O_WRONLY)
    sys.stdout.flush()
    sys.stderr.flush()
    os.dup2(null, 1)
    os.dup2(null, 2)
    os.close(null)


def _receipt(line):
    """The hook's line, to the journal only (the store already holds the state). Never raises."""
    try:
        # budget: danger=a hung journal holds the hook of a live run; its reach leaves no record; no record of its run
        subprocess.run(["systemd-cat", "-t", RECEIPT_TAG], input=line + "\n", text=True, timeout=10,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass


def hook_script(clone=None):
    """-> the control.py a run's hooks run: its own clone's when it has one (it lives until the run's return, after
    claude and the ExecStopPost receipts), else this one. A continuation launches from the previous run's clone, which
    that run's return deletes: a hook naming the launcher's file is dead for the whole new run."""
    own = clone and os.path.join(os.path.abspath(clone), "src", "RimMandrake", "rimflow", "control.py")
    return own if own and os.path.isfile(own) else os.path.abspath(__file__)


def hook_cmd(verb, run, p, clone=None):
    """-> one command line, each word quoted (systemd and sh both read single quotes): a path with a space stays one
    argument (round-three claim 10). A path with `$` in it is outside the page (plain-paths): systemd would expand it.
    It runs the first control.py that still exists when systemd runs it: the run's clone's, the launcher's, then the
    seat clones' (detached_helper's resolver). Either clone may be returned before the end receipt, and a receipt that
    cannot start leaves its run `started` for good (RIMMANDRAKE_END_GHOST_RUNS_STORE_SAYS_STARTED_SYSTEMD_GONE)."""
    import shlex
    import detached_helper as DH
    import wrapup
    rel = os.path.join("src", "RimMandrake", "rimflow", "control.py")
    cands = ([os.path.join(os.path.abspath(clone), rel)] if clone else []) + [os.path.abspath(__file__)] + \
        [os.path.join(c, rel) for c in wrapup.seat_clones()]
    words = DH.stop_resolver(cands, [verb, run, "--db", os.path.abspath(p)])
    if any("$" in x for x in words):
        raise Refused("plain-paths: a clone or store path has no $ in it: %s" % " ".join(words))
    return " ".join(shlex.quote(x) for x in words)


_REAL_RUN = subprocess.run      # launch_unit: a test that replaced subprocess.run brought its own runner


def launch_unit(args, spec, runner=None, p=None, clone=None, **kw):
    """THE launch primitive: every `systemd-run` that starts pipeline work goes through here (selftest_control
    enumerates the call sites; an unrouted one fails it). `args` are systemd-run's arguments: its options, `--`, then
    the payload; the unit's name is spec["unit"], a field, and control puts `--unit` last among the options, so the
    name systemd runs is the one control records. args are never read. admit(spec) first; a refusal returns a Launch
    with .refused (rc LAUNCH_REFUSED_RC) and never runs systemd-run. An admitted run's unit carries ExecCondition (the
    start-time re-check) and ExecStopPost (its end receipt). After systemd-run returns, the run's state decides: refused
    or cancelled at start -> .refused, never "running". -> Launch. Raises what the runner raises (a timeout leaves the
    run admitted for reconcile: an ambiguous start is investigated, never relaunched under the same name)."""
    if runner is None and subprocess.run is _REAL_RUN and spec.get("family") != "probe" and test_process():
        return _refusal(list(args), "a test process starts no real pipeline unit (family %s): a test passes runner=, "
                                    "replaces subprocess.run, or launches a throwaway unit in the probe family"
                        % spec.get("family"))
    runner = runner or subprocess.run
    p = p or db_path()
    args = list(args)
    if args and os.path.basename(str(args[0])) == "systemd-run":
        return _refusal(args, "launch-through-one-door: a launch passes systemd-run's arguments and names its unit "
                              "in spec['unit']; control runs systemd-run")
    if "--" not in args:
        return _refusal(args, "launch-through-one-door: the payload follows `--` in a launch's arguments")
    try:
        hook_cmd("condition", "run", p, clone)      # plain-paths, refused before anything is admitted
        adm = admit(spec, p)
    except Unreadable as e:
        return _refusal(args, str(e), unreadable=True)
    except Refused as e:
        return _refusal(args, str(e))
    if not adm["ok"]:
        return _refusal(args, adm["why"])
    rid = adm["run"]
    permit_sync(p=p)    # admitted means `all` is on: a timed all-off that lapsed by itself left no permit behind
    j = args.index("--")
    full = ["systemd-run"] + args[:j] + ["--unit", spec["unit"],
                                         "-p", "ExecCondition=" + hook_cmd("condition", rid, p, clone),
                                         "-p", "ExecStopPost=-" + hook_cmd("ended", rid, p, clone)] + args[j:]
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
        return _refusal(args, "%s at start: %s" % (st["state"], st["why"]), run=rid)
    if st and st["state"] == "admitted" and r.returncode != 0:
        _mark(rid, "fail_launch", "systemd-run exit %d" % r.returncode, p, fault=True)
    return out


def reconcile(p=None, now=None, min_age_s=300, unit_loaded=None):
    """Close admitted runs whose unit never started and whose launcher is gone: abandoned, reservations released. The
    condition fences them (an abandoned run's unit, if it ever starts, is refused). A started run whose unit systemd
    reads gone (its end receipt never ran) is ended, its stop orders done. -> [unit]."""
    now = time.time() if now is None else now
    unit_loaded = unit_loaded or _unit_loaded
    rows = _q("SELECT * FROM runs WHERE state='admitted' AND admitted_at < ?", (now - min_age_s,), p)
    out = []
    for r in rows:
        alive = r["host"] == socket.gethostname() and r["pid"] and os.path.exists("/proc/%d" % r["pid"])
        if not alive and unit_loaded(r["unit"]) is False:
            if _mark(r["id"], "abandoned", "never started; its launcher (pid %s) is gone" % r["pid"], p, now, True):
                out.append(r["unit"])
    for r in ghosts(p, now, unit_loaded)["gone"]:
        ended(r["id"], "end receipt missed: systemd reads the unit gone (reconcile)", p, now)
        out.append(r["unit"])
    return out


def ghosts(p=None, now=None, unit_loaded=None, min_age_s=60):
    """Started runs against systemd: -> {"gone": [row] (systemd reads the unit inactive or not loaded: its end receipt
    never ran), "unreadable": [row] (systemd could not be read: left as it is, never read as ended)}."""
    now = time.time() if now is None else now
    unit_loaded = unit_loaded or _unit_loaded
    out = {"gone": [], "unreadable": []}
    for r in _q("SELECT * FROM runs WHERE state='started' AND started_at < ?", (now - min_age_s,), p):
        st = unit_loaded(r["unit"])
        if st is not True:
            out["gone" if st is False else "unreadable"].append(r)
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
                 "note {item} --text \"{note_head}STOPPED (write-now): done: ...; half-done: ...; next: ...\" --why "
                 "\"pipe stop\"` and publish its shard; then end your turn. {then_text}At {deadline} the run is killed.",
    "at_easy_spot": "STOP ORDER, at the next easy spot (pipe stop --at-easy-spot, act {act} at {at}, by {who}: {why}). "
                    "Finish the unit of work in hand, start no other, then write where you are: commit and ./publish "
                    "what is finished; put a short handoff note on your item ({item}) with `python3 "
                    "src/RimMandrake/rimflow/cli.py note {item} --text \"{note_head}STOPPED (at-easy-spot): done: ...; "
                    "half-done: ...; next: ...\" --why \"pipe stop\"` and publish its shard; then end your turn. "
                    "{then_text}{deadline_text}",
    # the account's warning (account_end.warn_text): said once, and it ends no run
    "warn": "{why} (act {act} at {at}, by {who})",
}
STOP_THEN_TEXT = {      # (the order's last sentence, the head of the note it asks for)
    "continue": ("A fresh run carries this work on from that note once the cause of the stop is gone; do not close "
                 "the item for the stop.", "LEFT OPEN: "),
    "end": ("This stop ends the work: no run carries it on.", ""),
}


def stop_then(act):
    """-> "continue" | "end": what a stop act (an `acts` row as a dict) leaves behind. An act written before --end
    existed reads "continue", the writing modes' default."""
    try:
        v = json.loads((act or {}).get("after") or "{}").get("then")
    except (TypeError, ValueError, AttributeError):
        v = None
    return v if v in STOP_THEN else "continue"


# budget: danger=a hung systemd holds the pipeline's control; never reached in the 14 days to 2026-11-24; no record of its run
def _systemctl(args, timeout=10):
    try:
        r = subprocess.run(["systemctl", "--user"] + args, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return -1, "%s: %s" % (type(e).__name__, e)


def _cgroup_pids(unit):
    """-> (the pids now in the unit's cgroup as a probe_result answer, could_not_look when systemd or the cgroup cannot
    be read; the cgroup path, "" when there is none)."""
    rc, out = _systemctl(["show", "-p", "ControlGroup", "--value", unit], 5)
    if rc != 0:     # a failed read is "could not look", never an empty cgroup (a unit that does not exist reads rc 0)
        return P.could_not_look("systemctl show failed (rc %d): %s" % (rc, out.strip())), ""
    cg = out.strip()
    if not cg:
        return P.empty(), ""
    return _procs(cg), cg


CGROUP_ROOT = "/sys/fs/cgroup"


def _procs(cg):
    """-> the pids in cgroup `cg` AND every cgroup below it (a delegated unit's processes may sit only in a child:
    round-three claim 8), read from each cgroup.procs, as a probe_result answer: empty when the cgroup is gone or holds
    none; could_not_look when any part could not be read (a cgroup that still exists without a readable cgroup.procs
    included)."""
    top = os.path.join(CGROUP_ROOT, cg.lstrip("/"))
    if not os.path.isdir(top):
        return P.empty()
    out = []
    for d, _dirs, _files in os.walk(top):
        try:
            with open(os.path.join(d, "cgroup.procs"), encoding="ascii") as f:
                out += [int(x) for x in f.read().split()]
        except FileNotFoundError:
            if os.path.isdir(d):    # it exists and cannot be read; gone meanwhile is simply empty
                return P.could_not_look("%s exists with no readable cgroup.procs" % d)
        except (OSError, ValueError) as e:
            return P.could_not_look("%s/cgroup.procs: %s" % (d, e))
    return P.value(out) if out else P.empty()


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
        got, cg = _cgroup_pids(u)
        pids, blind = (list(got), "") if got.ok else (None, got.cause)    # None: could not look, death UNVERIFIED
        t0 = time.monotonic()
        rc, said = _systemctl(["kill", "--signal=SIGKILL", "--kill-whom=all", u], 10)
        if pids:        # belt and braces: the pids seen in the cgroup get SIGKILL too (a unit systemd no longer lists)
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
        left = list(pids or [])
        late = rc != 0 and pids is not None and bool(cg)
        while (left or late) and time.monotonic() - t0 < wait_s:
            if late:    # systemd's cgroup kill failed: a process that entered the cgroup after the snapshot is only
                now_in = _procs(cg)     # seen by reading the cgroup again (round-two claim 4)
                if not now_in.ok:
                    pids, blind = None, now_in.cause    # the reread could not look: death UNVERIFIED, never assumed
                    break
                for pid in now_in:
                    if pid not in left and _alive(pid):
                        left.append(pid)
                        pids.append(pid)    # it was in the unit: counted as one of its processes
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except (ProcessLookupError, PermissionError):
                            pass
                if not [x for x in now_in if _alive(x)]:
                    late = False
            left = [x for x in left if _alive(x)]
            if left or late:
                time.sleep(0.01)
        left = [x for x in left if _alive(x)]
        if late and pids is not None:   # the cgroup never read empty inside the wait (or the kill spent the wait)
            fin = _procs(cg)
            if not fin.ok:      # could not look: UNVERIFIED, never "dead" (round-three claim 4)
                pids, blind = None, fin.cause
            else:
                for pid in fin:
                    if pid not in left and _alive(pid):
                        pids.append(pid)
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except (ProcessLookupError, PermissionError):
                            pass
                left = sorted({x for x in left + list(fin) if _alive(x)})
        ms = int((time.monotonic() - t0) * 1000)
        _systemctl(["stop", "--no-block", u], 10)
        _systemctl(["reset-failed", u], 5)
        if pids is None:
            out.append({"unit": u, "dead": None, "ms": ms, "survivors": [],
                        "said": "its cgroup could not be read (%s): death UNVERIFIED" % blind})
        elif not pids:
            out.append({"unit": u, "dead": None, "ms": ms, "survivors": [], "said": "nothing was running in it"})
        else:
            out.append({"unit": u, "dead": not left, "ms": ms, "survivors": left,
                        "said": "%d process(es) killed" % len(pids) if not left else "SURVIVED: pids %s" % left})
    return out


def _live_runs(c, scope):
    return [dict(r) for r in c.execute("SELECT * FROM runs WHERE state='started' ORDER BY started_at").fetchall()
            if _in_scope(r, scope)]


def _stand_in(unit, find_scopes=False):
    """-> the row a stop uses for a unit the store cannot name (unreadable, or no run row): its claude scope
    (claude-seat-<seat>-<unit>.scope, role_launch.role_scope) is a cgroup of its own that the unit's kill misses, so a
    kill lists it from systemd by name; a listing that fails is carried as scope_err (the kill then reads UNVERIFIED)."""
    row = {"id": None, "unit": unit, "spec": "{}", "item": None, "mod": None, "family": "?"}
    if find_scopes:
        pat = "claude-seat-*-%s.scope" % unit
        rc, out = _systemctl(["list-units", "--all", "--plain", "--no-legend", "--type=scope", pat], 5)
        if rc != 0:
            row["scope_err"] = "its claude scope (%s) could not be listed (rc %d: %s): death UNVERIFIED" % (
                pat, rc, out.strip()[:80])
        else:
            found = [w for w in (ln.replace("\u25cf", " ").split() for ln in out.splitlines()) if w]
            row["spec"] = json.dumps({"extra_units": [w[0] for w in found if w[0].endswith(".scope")]})
    return row


def _extra_units(run):
    try:
        spec = json.loads(run.get("spec") or "{}")
    except ValueError:
        spec = {}
    return [x for x in spec.get("extra_units") or [] if isinstance(x, str)]


def order_runs(units, mode, why, deadline=None, p=None, now=None):
    """One order for each unit of `units` and nothing else: no OFF switch, no void, no reservation released, no kill
    timer (the account's end, account_end.py: the switch itself ends what is left, and a run that finishes in time keeps
    its result). Mode `warn` is the account's warning: the hook says it once and the run keeps working. `deadline` is
    only said in the order. -> the act's row. Raises Unreadable / Refused."""
    now = time.time() if now is None else now
    if mode not in STOP_TEXT:
        raise Refused("no stop order %r (%s)" % (mode, ", ".join(STOP_TEXT)))
    units = [u[:-len(".service")] if u.endswith(".service") else u for u in units]
    with txn(p) as c:
        act = _act(c, "account_end", "all", None, {"mode": mode, "units": units, "deadline": deadline}, why, now=now)
        for u in units:
            r = c.execute("SELECT id FROM runs WHERE unit=?", (u,)).fetchone()
            c.execute("INSERT INTO stops (unit, run, mode, act, why, at, deadline, state) VALUES (?,?,?,?,?,?,?,'pending')",
                      (u, r["id"] if r else None, mode, act["id"], why.strip(), now, deadline))
    return act


def withdraw_orders(acts, why, p=None, now=None):
    """Take back the orders of order_runs that no run has obeyed. -> how many. A delivered one is said withdrawn to its
    run by the hook."""
    now = time.time() if now is None else now
    with txn(p) as c:
        rows = [r for a in acts for r in c.execute("SELECT * FROM stops WHERE act=? AND state IN ('pending','seen')",
                                                   (a,)).fetchall()]
        if not rows:
            return 0
        _act(c, "account_end", "all", {"acts": list(acts)}, {"withdrawn": [r["id"] for r in rows]}, why, now=now)
        return len(_withdraw_stops(c, rows, now)[0])


def stop(target, mode, why, deadline_s=None, owner_said=None, per_ruling=None, p=None, now=None, killer=None,
         reaper=None, escalator=None, idem=None, then="continue"):
    """`pipe stop`: block new launches on the scope at once (a control switch, every unstarted run cancelled, in one
    transaction), release the live runs' trials (void, fail_system), and per live run: write_now / at_easy_spot write a
    stop order its hook delivers; kill SIGKILLs its whole cgroup (and its claude scope) and verifies it dead. `then`
    (STOP_THEN) is booked on the act: a writing stop's run is carried on (carry_stop) unless it is "end". A unit
    kill never waits on the store: on a locked store it kills first and records the kill once the store frees. `idem`:
    a replayed key changes nothing (out["replayed"]). -> dict."""
    now = time.time() if now is None else now
    if mode not in STOP_MODES:
        raise Refused("no stop mode %r (%s)" % (mode, ", ".join(STOP_MODES)))
    if then not in STOP_THEN:
        raise Refused("no stop --then %r (%s)" % (then, ", ".join(STOP_THEN)))
    plan_after = {"mode": mode, "deadline_s": deadline_s, "then": "end" if mode == "kill" else then}
    killer = killer or kill_units
    t = str(target or "").strip()
    if t.endswith(".service"):  # `pipe stop rm-x.service` is rm-x: the run row and its claude scope (round-four claim 2)
        t = t[:-len(".service")]
    unit_target = t.startswith("unit:") or t.startswith("rm-")
    scope = ("unit:" + t[5:] if t.startswith("unit:") else "unit:" + t) if unit_target else scope_of(t)
    if deadline_s is None and mode == "write_now":
        deadline_s = WRITE_NOW_DEADLINE_S
    emergency = unit_target and mode == "kill"
    faulted = []

    def book(c, ended_run=None):
        """The stop's store half, inside one transaction. -> (act, cancelled, runs, replayed act or None).
        `ended_run`: the id of a run this stop's own kill ended before its booking (a locked store: claim r3-2)."""
        del faulted[:]
        hit = _idem_hit(c, idem)
        if hit:
            return hit, [], [], hit
        act = None
        if not unit_target:
            old = c.execute("SELECT * FROM switches WHERE scope=? AND layer='control'", (scope,)).fetchone()
            act = _act(c, "stop", scope, dict(old) if old else None, plan_after, why, owner_said, per_ruling, idem,
                       now=now)
            c.execute("INSERT OR REPLACE INTO switches (scope, layer, why, said, date, until, act, at_pacific, who)"
                      " VALUES (?,?,?,?,?,?,?,?,?)", (scope, "control", "stopped (%s): %s" % (mode, why.strip()),
                                                      owner_said, utc(now)[:10], None, act["id"],
                                                      act["at_pacific"], act["who"]))
        # a unit target fences its admitted, unstarted run too: its start check refuses it
        cancelled = _cancel_in_scope(c, scope, "stopped: " + why, now)
        runs = _live_runs(c, scope)
        if ended_run and not any(r["id"] == ended_run for r in runs):
            e = c.execute("SELECT * FROM runs WHERE id=? AND state IN ('ended','started')", (ended_run,)).fetchone()
            runs += [dict(e)] if e else []
        if unit_target and not runs and (mode == "kill" or not cancelled):
            # a cooperative order is never written for a run just cancelled before its start: nothing would end it
            runs = [_stand_in(scope[5:], mode == "kill")]
            done = c.execute("SELECT state FROM runs WHERE unit=?", (scope[5:],)).fetchone()
            if done and done["state"] not in LIVE_STATES:
                runs[0]["terminal"] = done["state"]     # its bookkeeping was its own end's or kill's: no second reap
        if unit_target:
            act = _act(c, "stop", scope, None, plan_after, why, owner_said, per_ruling, idem, now=now)
        for r in runs:
            if r["id"]:     # its trials released: a stopped run is void and charges nothing (fail_system)
                c.execute("INSERT OR IGNORE INTO voids VALUES (?,?,?,?,?,?)",
                          (r["id"], r["mod"], act["id"], "stopped (%s): %s" % (mode, why.strip()), owner_said, now))
                if _release(c, "run=?", (r["id"],), "fail_system: stopped (%s): %s" % (mode, why), now, True):
                    faulted.append(r["id"])
                c.execute("UPDATE reservations SET state='voided', settled_at=? WHERE run=? AND state='charged'",
                          (now, r["id"]))
            if mode != "kill":
                r["order"] = c.execute(
                    "INSERT INTO stops (unit, run, mode, act, why, at, deadline, state) VALUES (?,?,?,?,?,?,?, "
                    "'pending')", (r["unit"], r["id"], mode, act["id"], why.strip(), now,
                                   now + deadline_s if deadline_s else None)).lastrowid
        return act, cancelled, runs, None

    store_err = None
    known = None
    if emergency:   # lock-free reads (WAL) before any side effect: a replayed key does nothing (claim r3-3), and the
        try:        # run's identity survives a locked store, so the kill is booked on THAT run (claim r3-2)
            hit = _q("SELECT * FROM acts WHERE idem=?", (idem,), p, one=True) if idem else None
            if hit:
                return {"scope": scope, "mode": mode, "act": hit, "cancelled": [], "units": [], "store": True,
                        "replayed": True}
            known = _q("SELECT * FROM runs WHERE unit=? AND state IN ('started','admitted')", (scope[5:],), p,
                       one=True)
        except Unreadable:
            pass
    try:
        with txn(p, KILL_STORE_WAIT_S if emergency else 3.0) as c:
            act, cancelled, runs, replayed = book(c)
        store = True
    except Unreadable as e:
        if not emergency:
            raise
        act, cancelled, store, replayed = None, [], False, None
        runs = [_stand_in(scope[5:], True)]
        if known:   # its family and claude scope from the store's last committed word, read without the lock
            runs = [dict(known, spec=json.dumps(dict(json.loads(known.get("spec") or "{}"), extra_units=sorted(set(
                _extra_units(known) + _extra_units(runs[0]))))), scope_err=runs[0].get("scope_err"))]
        store_err = str(e)
    out = {"scope": scope, "mode": mode, "act": act, "cancelled": cancelled, "units": [], "store": store,
           "replayed": bool(replayed)}
    if replayed:
        return out
    if not store:
        out["store_err"] = store_err
    if mode == "kill":
        res_of = {r["unit"]: _kill_checked(r, killer) for r in runs}     # after the store half, or without it
        if not store and "locked" in store_err and all(_verdict(x)[0] for x in res_of.values()):
            # the store was only busy: the kill is recorded now, with the normal wait (round-two claim 3)
            killed_some = any(x["dead"] for res in res_of.values() for x in res)
            try:
                with txn(p) as c:
                    act, cancelled, runs2, _r = book(c, known["id"] if known and killed_some else None)
                if _r:      # the same key was booked meanwhile: nothing more is written
                    out.update(act=_r, store=True, replayed=True)
                    del out["store_err"]
                    return out
                store = True
                out.update(act=act, cancelled=cancelled, store=True)
                del out["store_err"]
                first = res_of[runs[0]["unit"]]
                for r in runs2:
                    r["late"] = "; recorded after the kill (the store was locked at it)"
                    res_of.setdefault(r["unit"], first)
                runs = runs2
            except Unreadable as e:
                out["store_err"] = "%s; recording the kill after it failed too: %s" % (store_err, e)
        if store:
            for x in faulted:   # after the commit: a live run's trial released by the stop is a metered fault
                _fault_alarm(x, p)
        for r in runs:
            books = _books(r, mode, why, owner_said, act, p, per_ruling) if store else ""
            out["units"].append(_finish_kill(r, res_of[r["unit"]], act, why, store, p, reaper, books))
    else:
        for x in faulted:   # after the commit: a live run's trial released by the stop is a metered fault
            _fault_alarm(x, p)
        for r in runs:
            books = _books(r, mode, why, owner_said, act, p, per_ruling) if store else ""
            esc = (escalator or schedule_escalation)(r["unit"], deadline_s, p, r.get("order")) if deadline_s else None
            unset = bool(esc) and "NOT set" in esc
            out["units"].append({"unit": r["unit"], "ok": not unset, "said": "stop order written (%s)%s%s" % (
                mode, "; escalates to --kill at %s (%s)" % (pac(now + deadline_s), esc) if deadline_s else
                "; no deadline", books)})
    if scope == "all":      # `pipe stop all` writes an all-switch: the permit follows it (slice review 13)
        permit_sync(p=p, now=now)
    return out


def _books(r, mode, why, owner_said, act, p, per_ruling):
    """A stopped run spends no trial in the dispatch books either (run_void.py; card 2026-11-18)."""
    if not r.get("id"):
        return ""
    return void_books(r["unit"], r.get("mod"), "stopped (%s): %s" % (mode, why), owner_said, act["id"], p,
                      per_ruling=per_ruling)


def _kill_checked(r, killer):
    res = list(killer([r["unit"]] + _extra_units(r)))
    if r.get("scope_err"):
        res.append({"unit": "claude-seat-*-%s.scope" % r["unit"], "dead": None, "ms": 0, "survivors": [],
                    "said": r["scope_err"]})
    return res


def _verdict(res):
    """-> (ok, bad rows). ok: every process that was in the unit (and its claude scope) is gone; a unit with nothing
    running is fine; a cgroup that could not be read is UNVERIFIED, and a survivor is a failure."""
    bad = [x for x in res if x["dead"] is False or (x["dead"] is None and "nothing was running" not in x["said"])]
    return not bad, bad


def _finish_kill(r, res, act, why, store, p, reaper, books):
    """-> one killed unit's row: its run recorded killed (from ended too when the kill killed something: its own end
    receipt may land while the kill verifies, round-two claim 5) and its bookkeeping."""
    ok, _bad = _verdict(res)
    row = {"unit": r["unit"], "dead": ok and any(x["dead"] for x in res), "ms": max(x["ms"] for x in res),
           "said": "; ".join("%s: %s" % (x["unit"], x["said"]) for x in res), "ok": ok}
    if not ok:      # something survived or death is unverified: never recorded killed, the clone kept
        row["bookkeeping"] = "NOT recorded killed and its clone kept: %s" % row["said"]
        return row
    moved = not r.get("terminal")   # a stand-in is reaped as before, unless the store holds its run already ended
    if store and r.get("id"):   # only the kill that moves the run to killed reaps it (two kills: once, claim r3-5)
        moved = _mark(r["id"], "killed", "pipe stop --kill (%s): %s" % (act["id"], why), p,
                      frm=("started", "admitted") + (("ended",) if row["dead"] else ()))
    if not moved:
        row["bookkeeping"] = ("its run is already %s: its bookkeeping was that end's" % r["terminal"]) if r.get(
            "terminal") else "already recorded killed by another kill: its bookkeeping is that kill's"
    else:
        row["bookkeeping"] = (reaper or reap_detached)(r, act, why) if r.get("family") == "detached" or \
            str(r["unit"]).startswith("rm-detached-") else "no bookkeeping owed (family %s)" % r.get("family")
    row["bookkeeping"] += books + r.get("late", "")
    return row


def _escalation_name(unit, order):
    return "rm-control-escalate-%s%s" % (unit[-60:], "-o%d" % order if order else "")


def _disarm_escalation(unit, order):
    name = _escalation_name(unit, order) + ".timer"
    rc, out = _systemctl(["stop", name])
    if rc not in (0, 5):   # systemctl returns 5 when the timer is no longer loaded
        return "timer %s NOT disarmed (exit %d: %s)" % (name, rc, " ".join(out.split())[:80])


def schedule_escalation(unit, deadline_s, p=None, order=None, runner=subprocess.run):
    """A transient timer (bookkeeping, not pipeline work): at the deadline, `escalate` kills the run if it has not
    ended. -> line. The writer of the order may stand in a pool clone that is returned before the deadline, so the
    timer runs the first control.py that still exists: this one, then the seat clones' (detached_helper's resolver).
    The timer is named by its stop order (`order`, the stops row id), so a second deadline on one unit sets a second
    timer instead of colliding with the first (round-two claim 6). It is due at the deadline's WALL-CLOCK time, the time
    the order states (deadline-is-wall-clock): an `--on-active` timer counts monotonic time, which on this WSL2 VM falls
    behind the wall clock, and a 2-minute deadline fired 105 s late (control_agent_drill.py, 2026-11-19)."""
    import math
    name = _escalation_name(unit, order)
    due = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(math.ceil(time.time() + deadline_s)))
    import detached_helper as DH
    import wrapup
    rel = os.path.join("src", "RimMandrake", "rimflow", "control.py")
    cands = [os.path.abspath(__file__)] + [os.path.join(c, rel) for c in wrapup.seat_clones()]
    try:
        r = runner(["systemd-run", "--user", "--quiet", "--collect", "--unit", name,
                    "--on-calendar=" + due, "--timer-property=AccuracySec=1s",
                    *DH.stop_resolver(cands, ["escalate", unit, "--db", os.path.abspath(p or db_path())])],
                   # budget: danger=a hung systemd-run holds the stop; longest=1.3s (admission to start of 1057 runs,
                   # budget: control.db)
                   capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return "escalation timer NOT set (%s)" % e
    if r.returncode:
        return "escalation timer NOT set (exit %d: %s)" % (r.returncode, (r.stderr or "").strip()[:80])
    # The order commits before the timer is armed. If undo got there first, stop the newly armed timer too.
    if order and _q("SELECT id FROM stops WHERE id=? AND state LIKE 'withdrawn%'", (order,), p, one=True):
        return _disarm_escalation(unit, order) or "timer %s disarmed (order withdrawn)" % name
    return "timer %s" % name


def escalate(unit, p=None, now=None, killer=None, reaper=None):
    """The deadline of a stop order passed: kill the run if it has not ended, and say so (an act). -> line."""
    now = time.time() if now is None else now
    with txn(p) as c:
        s = c.execute("SELECT * FROM stops WHERE unit=? AND state IN ('pending','seen') AND deadline IS NOT NULL "
                      "AND deadline <= ? ORDER BY id DESC", (unit, now + ESCALATE_SLACK_S)).fetchone()
        if not s:   # a timer acts on an order whose deadline passed, never on a newer one that has none yet
            return "ESCALATE %s: nothing to do (no pending stop order's deadline has passed)" % unit
        a = _act(c, "escalate", "unit:" + unit, {"mode": s["mode"]}, {"mode": "kill"},
                 "the %s stop order's deadline passed (%s) and the run had not ended: escalated to --kill" % (
                     s["mode"], pac(s["deadline"] or now)), now=now)
        c.execute("UPDATE stops SET state='escalated', ended_at=? WHERE id=?", (now, s["id"]))
        r = c.execute("SELECT * FROM runs WHERE unit=?", (unit,)).fetchone()
    r = dict(r) if r else _stand_in(unit, True)
    res = (killer or kill_units)([unit] + _extra_units(r))
    if r.get("scope_err"):
        res = list(res) + [{"unit": "claude-seat-*-%s.scope" % unit, "dead": None, "ms": 0, "survivors": [],
                            "said": r["scope_err"]}]
    bad = [x for x in res if x["dead"] is False or (x["dead"] is None and "nothing was running" not in x["said"])]
    if bad:     # the order stays deliverable: the surviving agent's hook keeps telling it (round-three claim 9)
        try:
            with txn(p) as c:
                c.execute("UPDATE stops SET state=?, ended_at=NULL WHERE id=? AND state='escalated'",
                          (s["state"], s["id"]))
        except Unreadable as e:
            return "ESCALATION FAILED %s (%s): %s; NOT recorded killed; its order could NOT be put back (%s)" % (
                unit, a["id"], "; ".join(x["said"] for x in bad), e)
        return "ESCALATION FAILED %s (%s): %s; NOT recorded killed; its stop order stands" % (
            unit, a["id"], "; ".join(x["said"] for x in bad))
    moved = True
    if r.get("id"):     # from ended too when the kill killed something (its end receipt may land first: claim 5)
        moved = _mark(r["id"], "killed", "escalated to --kill (%s)" % a["id"], p,
                      frm=("started", "admitted") + (("ended",) if any(x["dead"] for x in res) else ()))
    book = (reaper or reap_detached)(r, a, "escalated") if str(unit).startswith("rm-detached-") and moved else \
        "" if moved else "(already recorded killed by another kill)"
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
                            "-p", "RuntimeMaxSec=3600"] + env + [py, os.path.abspath(__file__), "reap", unit],
                           # budget: danger=a hung systemd-run holds the stop; longest=1.3s (admission to start of 1057 runs,
                           # budget: control.db)
                           capture_output=True, text=True, timeout=30)
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
        # budget: danger=a locked store holds a hook of a live run; its reach leaves no record; no record of its run
        c = sqlite3.connect(p, timeout=0.5, isolation_level=None)
        try:
            c.row_factory = sqlite3.Row
            s = c.execute("SELECT * FROM stops WHERE unit=? AND state IN ('pending','seen') ORDER BY id DESC LIMIT 1",
                          (unit,)).fetchone()
            if not s:
                w = c.execute("SELECT * FROM stops WHERE unit=? AND state='withdrawn_owed' ORDER BY id DESC LIMIT 1",
                              (unit,)).fetchone()
                if w and c.execute("UPDATE stops SET state='withdrawn' WHERE id=? AND state='withdrawn_owed'",
                                   (w["id"],)).rowcount:
                    return 2, ("STOP ORDER WITHDRAWN (act %s): the stop order you read earlier is taken back. Carry on "
                               "with your work as before." % w["act"])
                return 0, ""
            # a warning (mode warn) is said once and is then done; a stop order is said after each tool call
            if not c.execute("UPDATE stops SET state=CASE WHEN mode='warn' THEN 'delivered' ELSE 'seen' END, "
                             "seen_at=COALESCE(seen_at, ?), seen_n=seen_n+1, ended_at=CASE WHEN mode='warn' THEN ? "
                             "ELSE ended_at END WHERE id=? AND state IN ('pending','seen')", (now, now, s["id"])).rowcount:
                return 0, ""    # it ended between the lookup and the mark: a done order is never revived
            a = c.execute("SELECT * FROM acts WHERE id=?", (s["act"],)).fetchone()
            r = c.execute("SELECT item FROM runs WHERE unit=?", (unit,)).fetchone()
        finally:
            c.close()
    except sqlite3.Error:
        return 0, ""
    item = (r["item"] if r else None) or os.environ.get("RM_CONTROL_ITEM") or "<your item>"
    dl = s["deadline"]
    then_text, note_head = STOP_THEN_TEXT[stop_then(dict(a) if a else {})]
    text = STOP_TEXT[s["mode"]].format(act=s["act"], at=(a["at_pacific"] if a else "?"), who=(a["who"] if a else "?"),
                                       why=s["why"], item=item, deadline=pac(dl) if dl else "no deadline",
                                       deadline_text=" At %s the run is killed." % pac(dl) if dl else "",
                                       then_text=then_text + " ", note_head=note_head)
    return 2, text


def claude_settings(p=None, clone=None):
    """-> the `--settings` JSON a run's claude carries: its PostToolUse hook reads the stop channel (`hook`), from the
    run's own clone (hook_script)."""
    py = "/usr/bin/python3" if os.path.exists("/usr/bin/python3") else sys.executable
    import shlex
    cmd = " ".join(shlex.quote(x) for x in (py, hook_script(clone), "hook", "--db", os.path.abspath(p or db_path())))
    return json.dumps({"hooks": {"PostToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": cmd,
                                                                              "timeout": 5}]}]}})


# ---------------------------------------------------------------- the call-site census (no launch bypasses admit)

# Files whose `systemd-run` starts no pipeline work (paths under src/RimMandrake), each with why. A pipeline launch
# passes systemd-run's arguments to launch_unit, which alone writes `systemd-run`: every other literal is a bypass.
NOT_PIPELINE = {
    "Utils/timers_guard.py": "re-arms a paused timer (no model)",
    "Utils/clone_mem_probe.py": "a memory-probe scope (no model)",
    "Utils/run_selftests.py": "the selftest harness scope (no model)",
    "Utils/mutation/run_mutation.py": "mutation-test workers (no model)",
    "rimflow/own_cgroup.py": "a git child's own memory scope (no model)",
    "rimflow/login_watch.py": "the account login switch (no model)",
    "rimflow/seat_restart.py": "a seat restart timer (no model)",
    "rimflow/control.py": "the primitive itself, its escalation timer and its killed-run bookkeeping unit",
}
BOOKKEEPING = {
    "rimflow/detached_helper.py:return_argv": "a finished run's clone-return step (starts no model)",
    "rimflow/role_launch.py:stoppost_handoff": "a finished run's wrap-up step, an ExecStopPost (starts no model)",
    "rimflow/role_clones.py:make_in_background": "makes a missing role clone (`role_clones.py ensure`, a scratch "
                                                 "clone copy; starts no model)",
}


def _sr_list(node):
    import ast
    if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
        e = node.elts[0]
        return isinstance(e, ast.Constant) and isinstance(e.value, str) and os.path.basename(e.value) == "systemd-run"
    return False


def call_sites(root=None):
    """-> [{"file", "func", "line", "col", "routed" (bool), "why"}] for every list literal whose first element is
    systemd-run in every non-test .py under `root` (src/RimMandrake). Routed only when NOT_PIPELINE or BOOKKEEPING names
    it; the selftest fails on any routed=False."""
    import ast
    import warnings
    root = root or os.path.join(REPO, "src", "RimMandrake")
    out = []
    for d, _dirs, files in os.walk(root):
        parts = os.path.relpath(d, root).split(os.sep)
        if any(x.startswith(".") and x != "." for x in parts) or "__pycache__" in parts:
            continue
        for f in files:
            if not f.endswith(".py") or f.startswith("selftest") or f.startswith("test_") or f.endswith("_accept.py"):
                continue
            path = os.path.join(d, f)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            try:
                with open(path, encoding="utf-8") as fh, warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    tree = ast.parse(fh.read())
            except (OSError, SyntaxError, ValueError):
                continue

            def visit(node, fn):
                for ch in ast.iter_child_nodes(node):
                    if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        visit(ch, ch.name)
                        continue
                    if _sr_list(ch):
                        k = "%s:%s" % (rel, fn)
                        why = ("not pipeline: " + NOT_PIPELINE[rel] if rel in NOT_PIPELINE else
                               "bookkeeping: " + BOOKKEEPING[k] if k in BOOKKEEPING else
                               "UNROUTED: starts a unit without control.launch_unit")
                        out.append({"file": rel, "func": fn, "line": ch.lineno, "col": ch.col_offset,
                                    "routed": not why.startswith("UNROUTED"), "why": why})
                    visit(ch, fn)
            visit(tree, "<module>")
    return out


# ---------------------------------------------------------------- the import (cutover)

def import_owner(holds, p=None, now=None):
    """Learn every row of his hold file the store lacks (`pipe init --import`, and mod_owner_hold.mirror before it
    writes): a row of a hold he lifted is not learned, and a mod the store already holds keeps the store's row (the
    store is the writer; the file is its mirror). Never removes a hold. -> lines."""
    import hashlib
    now = time.time() if now is None else now
    out = []
    lifted, held = lifted_owner(p), mod_holds(p, now)
    for m, h in sorted(holds.items()):
        if (m, h.get("date") or "", h["said"]) in lifted:   # a stale mirror row of a hold he lifted never holds again
            out.append("owner hold %s already lifted: not imported" % m)
            continue
        if held.get(m, {}).get("store"):
            out.append("owner hold %s already imported" % m)
            continue
        # the key carries his words: a new hold after a lift, same mod and day, is a new hold (round-four claim 10)
        r = switch("mod:" + m, True, "his hold (mod_owner_hold.json): " + h["said"], layer="owner", said=h["said"],
                   date=h.get("date"), idem="import:owner:%s:%s:%s" % (m, h.get("date"), hashlib.sha1(
                       h["said"].encode("utf-8")).hexdigest()[:12]), p=p, now=now, per_ruling="mod_owner_hold.json",
                   extra={k: v for k, v in h.items() if k == "design_allowed"} or None)
        out.append("owner hold %s %s" % (m, "already imported" if r["replayed"] else "imported (%s)" % r["act"]["id"]))
    return out


def import_live(p=None, now=None, hold_file=None, concepts=None, voids_file=None):
    """Seed the store from today's records, idempotently (each import act carries an idempotency key): his owner holds
    (mod_owner_hold.json, his words and date), the pipeline pause (pause.json), the retired Relentless family OFF, the
    granted coverage look of every concept with a standing release as an opening balance (charges = the refusing looks
    since that release), and run_void's standing voids (voids.jsonl). -> lines."""
    now = time.time() if now is None else now
    out = []
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import mod_owner_hold as OH
    out += import_owner(OH.load_file(hold_file or OH.PATH), p=p, now=now)
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
    try:    # the old pipeline_control counters and limits, as opening balances (slice 2)
        import pipeline_control as PC
        out += import_accounts(PC.control_dir(), p=p, now=now)
    except Exception as e:      # noqa: BLE001
        out.append("old counters: could not be imported (%s: %s)" % (type(e).__name__, e))
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
        import re   # the whole name: rm-judge-1 is not named by rm-judge-10 or rm-judge-1-reader (round-four claim 13)
        named = re.compile(r"(?<![\w.~-])%s(?![\w.~-])" % re.escape(v["run"]))
        if any(named.search(json.dumps(h)) and (h.get("to") or h.get("stage") or h.get("what") in (
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
        pins = ({r["mod"]: r["model"] for r in c.execute("SELECT mod, model FROM mod_models").fetchall()}
                if _has_models(c) else {})
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
    import mod_next as MN       # the one reader of the tick's reading
    rd, _, rd_why = MN.tick_reading()
    tickmods = MN.tick_rows(rd)
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
    out += game_lines()
    for s in sw:
        if not s["scope"].startswith("mod:") and s["scope"] != "all":
            out.append("%s %s" % (s["scope"], label(s)[:150]))  # cut-ok: terminal display
    for m in mods:
        ms = [s for s in sw if s["scope"] == "mod:" + m]
        state = "; ".join(label(s) for s in ms) or "ON"
        tr = tickmods.get(m) or {}
        look = [a for (am, _w), a in accts.items() if am == m]
        line = "%-18s %-15s %-40s tick: %s" % (m, str(tr.get("stage") or "-")[:15], state[:40],
                                                str(tr.get("decision") or "-") if rd else "UNMEASURED (%s)" % rd_why)
        if look:
            line += "  look %d left" % look[-1]["available"]
        if pins.get(m):
            line += "  builders on %s" % pins[m]
        out.append(line)
        if mod:
            out += ["  %s" % describe(s) for s in ms]
            out += ["  look window %s: %s" % (w, fmt_acct(a)) for (am, w), a in accts.items() if am == m]
            if tr.get("why"):
                out.append("  tick why: %s" % str(tr["why"])[:200])  # cut-ok: terminal display
            if tr.get("live"):
                out.append("  live (tick): %s" % ", ".join(str(x) for x in tr["live"])[:200])  # cut-ok: terminal display
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


def game_lines(short=False):
    """-> one line per game: who drives it, read from its lock at this moment (game_lock.py, the one record of who drives
    a game; RIMMANDRAKE_BUILD_ONE_GAME_LOCK_CLAIM_FOUR_RECORDS_DISAGREE). No lock readable here: no line. A reading that
    fails says COULD NOT LOOK, never nothing."""
    out = []
    try:
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import game_lock as GL
        for g in GL.games():
            path = GL.lock_path(g)
            if not path:
                continue
            r = GL.query(g, pipe=False, path=path)
            out.append(("%s %s%s" % (GL.game_names.show(g), r["state"], " " + r["seat"] if r.get("seat") and r["state"] != "FREE"
                                          else "")) if short else r["line"])
    except Exception as e:      # noqa: BLE001
        out.append("games: COULD NOT LOOK (%s: %s)" % (type(e).__name__, e))
    return out


def why(mod, p=None, now=None):
    """-> one line: may the pipeline run this mod now, and why (mod_next.next_for, the one home, without the stage
    record's exit tests), then the tick's row, the game holds and drivers, and the checks owed at Stage 6."""
    m = key(mod)
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import mod_next as MN
    import maturation as M
    r = MN.next_for(M.REPO, m, now=now, gate=False, src={"blocked": lambda spec: blocked(spec, p, now)})
    res, rwhy = r["may_run"]["result"], r["may_run"]["why"]
    head = ("BLOCKED " + rwhy) if res in ("held", "off", "paused") else "may run: %s (%s)" % (res, rwhy)
    try:
        gh = game_holds(p, now)
        games = " | games held: %s" % "; ".join("%s %s" % kv for kv in sorted(gh.items())) if gh else ""
    except Unreadable as e:
        games = " | game holds UNMEASURED (%s)" % e
    drivers = game_lines(short=True)
    games += " | drivers now: %s" % "; ".join(drivers) if drivers else ""
    # the whole why, never cut: a cut hid which game a wait was for (RIMMANDRAKE_DEFINE_BOTH_GAMES_EVERYWHERE_WAITING_SAID_AGAIN)
    return "%s: %s | %s%s%s" % (m, head, r["tick"]["line"], games, to_run_text(mod))


def to_run_text(mod, root=None):
    """-> ' | in-game visit N runs K of M checks: ...' for a mod at Stage 6, else '': only the checks the change touches
    run again (owner, 2026-11-21; maturation.ingame_to_run). A reading that fails says UNMEASURED, never nothing."""
    try:
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import maturation as M
        root = root or M.REPO
        name = next((d for d in os.listdir(os.path.join(root, "design", "concepts")) if key(d) == key(mod)), mod)
        rec = M.load(root, name) or {}
        if rec.get("stage") != "in_game":
            return ""
        n = max(1, len(M.ingame_openings(rec)))
        tt, _ = M.read_json(root, name, "version/test_table.json")
        run, counted = M.ingame_to_run(root, name, n, tt)
        import raid_pause as RP
        raids = RP.said(RP.read_scenes(root, name, n, tt))
        return " | in-game visit %d runs %d of %d checks: %s%s" % (n, len(run), len(run) + len(counted),
                                                                   ", ".join(run) or "none", " | " + raids if raids else "")
    except Exception as e:      # noqa: BLE001  a reading that cannot run is UNMEASURED, never an empty list
        return " | checks to run UNMEASURED (%s: %s)" % (type(e).__name__, e)


def log(n=10, p=None):
    rows = _q("SELECT * FROM acts ORDER BY rev DESC LIMIT ?", (n,), p)
    if not rows:
        return ["[] no acts yet (the store at %s is initialised and empty)" % (p or db_path())]
    return ["%s r%d %s %-5s %s: %s%s [%s -> %s]" % (
        r["id"], r["rev"], r["at_pacific"], r["kind"], r["scope"], r["why"][:120],  # cut-ok: terminal display
        " (his words: %s)" % r["owner_said"][:60] if r["owner_said"] else "", _brief(r["before"]), _brief(r["after"]))
        for r in reversed(rows)]


def _brief(raw, n=60):
    """An act's stored before or after, short, for `pipe log` (before-is-read): a switch row as OFF <act> (<why>)."""
    try:
        v = json.loads(raw) if isinstance(raw, str) else raw
    except ValueError:
        v = raw
    if v is None:
        return "none"
    if isinstance(v, dict) and "layer" in v and "why" in v:
        return "OFF%s (%s)" % (" " + v["act"] if v.get("act") else "", str(v["why"])[:40])
    t = v if isinstance(v, str) else json.dumps(v, sort_keys=True, default=str)
    return t if len(t) <= n else t[:n - 3] + "..."


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
    scope = scope_of(o.target, unseeded=True)
    import game_names
    shown = game_names.show_scope(scope)     # game:a is the store's key; people read game:ArchBig
    r = switch(scope, off, o.why, owner_said=o.owner_said, per_ruling=o.per_ruling, idem=o.idem)
    if r["replayed"]:
        return ["%s: already applied as %s (idempotency key %s): nothing changed" % (shown, r["act"]["id"], o.idem)]
    if not off and not r["had"]:
        if r["still"]:
            return ["%s: no `pipe off` switch to lift; still %s" % (shown, r["still"][0][:160])]  # cut-ok: terminal display
        return ["%s is already ON (the store holds no switch for it)" % shown]
    if r.get("withdrawn"):
        lines0 = ["%s: stop order(s) withdrawn: %s" % (shown, ", ".join(x["unit"] for x in r["withdrawn"]))]
    else:
        lines0 = []
    after = "OFF" if off else ("still " + r["still"][0][:120] if r["still"] else "ON")  # cut-ok: terminal display
    lines = ["%s %s -> %s%s" % (shown, r["before"], after,
                                "; cancelled before start: %s" % ", ".join(r["cancelled"]) if r["cancelled"] else "")]
    rep = r.get("replaced")
    if rep:     # the old switch's reason is gone from the store now: a later `pipe on` lifts both (2026-11-23)
        lines.append("REPLACES %s (%s, %s): %s -- a later `pipe on %s` lifts that switch too; to keep it, put it back "
                     "with its own --why" % (rep.get("act") or "-", rep.get("who") or "-", rep.get("at_pacific") or "-",
                                            str(rep.get("why") or "")[:300], o.target))  # cut-ok: terminal display
    if off:
        try:
            live = [x for x in _q("SELECT * FROM runs WHERE state='started'") if _in_scope(x, scope)]
        except Unreadable as e:     # could not look is never "none live" (round-four claim 12)
            live = None
            tail = "; live runs in it UNVERIFIED (%s): pipe show, then pipe stop %s if one is" % (e, o.target)
        if live is not None:
            tail = ("; %d run(s) live in it, untouched: stop with pipe stop %s --write-now | --at-easy-spot | --kill"
                    % (len(live), o.target)) if live else "; new starts only (no run is live in it)"
        lines.append(_who_line(r["act"]) + tail)
    else:
        t = tick_now()
        lines.append(_who_line(r["act"]) + ("; " + t if t else ""))
    lines.append("undo: pipe %s %s --why \"...\"" % ("on" if off else "off", o.target))
    return lines0 + lines


def remote_stop(target, mode, why, root=None, runner=subprocess.run, end=False):
    """A unit whose detached record names a host (run_host.py) is stopped by that host's own `./pipe stop`; nothing
    here holds it. -> (code, lines), or None when the target is not such a unit."""
    t = str(target or "").strip()
    t = t[len("unit:"):] if t.startswith("unit:") else t
    t = t[:-len(".service")] if t.endswith(".service") else t
    if not t.startswith("rm-"):
        return None
    import detached_helper as DH
    import run_host
    rec = DH.read_record(t, root)
    if not (isinstance(rec, dict) and rec.get("host") and run_host.door(rec["host"])):
        return None
    argv = run_host.stop_argv(rec, mode, why, end=end)
    try:
        r = runner(argv, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)  # budget: class=call
        rc, said = r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except Exception as e:  # noqa: BLE001 - could not look: the unit is not known stopped
        rc, said = 99, "%s: %s" % (type(e).__name__, e)
    head = "unit:%s stop on %s: %s" % (t, rec["host"], "done" if rc == 0 else "NOT DONE (rc %s)" % rc)
    return (OK if rc == 0 else FAILED), [head, said[-400:] or "(the host said nothing)"]  # cut-ok: terminal display


def cmd_stop(o):
    modes = [m for m, f in (("write_now", o.write_now), ("at_easy_spot", o.at_easy_spot), ("kill", o.kill)) if f]
    if len(modes) > 1:
        raise Refused("one stop mode, not %s" % ", ".join(modes))
    mode = modes[0] if modes else DEFAULT_STOP_MODE
    named = bool(modes)
    then = "end" if getattr(o, "end", False) else "continue"
    if then == "end" and mode == "kill":
        raise Refused("--end goes with a writing stop; a --kill is never carried on anyway")
    remote = remote_stop(o.target, mode, o.why, end=then == "end")
    if remote is not None:
        return remote
    dl = parse_dur(o.deadline) if o.deadline else None
    r = stop(o.target, mode, o.why, deadline_s=dl, owner_said=o.owner_said, per_ruling=o.per_ruling, idem=o.idem,
             then=then)
    if r["replayed"]:
        return OK, ["%s stop: already done as %s (idempotency key %s): nothing changed" % (r["scope"], r["act"]["id"],
                                                                                         o.idem)]
    bad = [u for u in r["units"] if not u.get("ok")]
    head = "%s stop %s (%s%s): %s" % (r["scope"], "--" + mode.replace("_", "-"), "named" if named else
                                      "NO MODE GIVEN: the default; always name one", "" if r["store"] else
                                      "; STORE UNREADABLE: %s" % r.get("store_err"),
                                      "; ".join("%s %s" % (u["unit"], ("dead in %d ms" % u["ms"]) if u.get("dead")
                                                           else u["said"]) for u in r["units"]) or "[] no run live")
    l2 = ("%s%s" % (_who_line(r["act"]) if r["act"] else "no act written",
                    "; cancelled before start: %s" % ", ".join(r["cancelled"]) if r["cancelled"] else ""))
    if mode == "kill":
        l2 += "; " + "; ".join(u.get("bookkeeping", "") for u in r["units"])[:300]  # cut-ok: terminal display
    then_line = [] if mode == "kill" else [
        "then END: no run carries the work on" if then == "end" else
        "then CARRIED ON: a fresh run picks the work up from its LEFT OPEN note once the cause is gone (--end ends it)"]
    return (FAILED if bad else OK), [head[:400], l2[:400]] + then_line + [  # cut-ok: terminal display
                                                             "undo: pipe undo %s --why \"...\" (withdraws the order while the run has not obeyed it)" % (
                                                                 r["act"]["id"] if r["act"] else "<act>")]


def parse_dur(s):
    s = str(s).strip().lower()
    mult = {"s": 1, "m": 60, "h": 3600}
    try:
        v = int(float(s[:-1]) * mult[s[-1]]) if s[-1] in mult else int(float(s))
    except (ValueError, IndexError):
        raise Refused("a duration is N, Ns, Nm or Nh, got %r" % s)
    if v < 1:   # 0 would silently mean "no deadline" (round-three claim 11)
        raise Refused("a deadline is at least 1 s, got %r" % s)
    return v


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
    sc = scope_of(o.mod)
    if not sc.startswith("mod:"):   # slice review 20: `all`[4:] was the mod ""
        raise Refused("pipe grant takes a mod, not %s" % sc)
    m = sc[4:]
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
        try:
            ok = c.execute("PRAGMA quick_check").fetchone()[0]
            if ok != "ok":      # a damaged store is not a healthy one (round-four claim 11)
                raise Unreadable("corrupt: quick_check says %s" % str(ok)[:200].replace("\n", " | "))  # cut-ok: exception message
            lines = ["store %s: quick_check ok, rev %d" % (db_path(), rev(c))]
            c.execute("PRAGMA busy_timeout=3000")   # a held write lock is no healthy store (slice review 17)
            c.execute("BEGIN IMMEDIATE")
            c.execute("ROLLBACK")
        except sqlite3.Error as e:
            raise Unreadable(_err(e))
        finally:
            c.close()
        lines.append("reconcile: abandoned or ended %s" % (reconcile() or "[] none"))
        blind = [r["unit"] for r in ghosts()["unreadable"]]
        if blind:
            lines.append("UNREADABLE in systemd (left started): %s" % blind)
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import mod_owner_hold as OH
        try:
            lines += OH.drift()[1]
        except OH.Unreadable as e:
            lines.append("owner hold mirror: could not look (%s)" % e)
        return OK, lines
    except Unreadable as e:
        return UNREADABLE, ["CONTROL UNREADABLE: %s" % e,
                            "fix: missing -> `pipe init --import`; permission -> chmod u+rw; corrupt -> move it aside "
                            "(keep it) and `pipe init --import`; locked -> find the writer (fuser %s)" % db_path()]


def main(argv=None):
    av = list(sys.argv[1:] if argv is None else argv)
    if av[:1] in (["set"], ["add"], ["reset"], ["limit"], ["undo"]):
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import pipeline_control as PC
        return PC.main(av)
    if av[:1] == ["bundle"]:    # ./pipe bundle <home | Mod | ID...> --why "...": one work bundle (work_bundle.py)
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import work_bundle as WB
        return WB.main(["launch"] + av[1:])
    if av[:1] == ["hook"]:      # the run's PostToolUse hook: as fast and as quiet as possible
        db = av[av.index("--db") + 1] if "--db" in av else None
        code, text = hook(db)
        if text:
            sys.stderr.write(text + "\n")
        return code
    import argparse  # only the CLI parses arguments; game_lock imports this module for its control-store read
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
    p.add_argument("--end", action="store_true", help="the work ends with this writing stop: no run carries it on "
                                                      "(default: a fresh run carries it on once the cause is gone)")
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
    p = w(sub.add_parser("model"))
    p.add_argument("mod")
    p.add_argument("model", help="a pinnable tier (mod_model.pinnable: fable, opus, sonnet), or default to lift the pin")
    p = sub.add_parser("next")
    p.add_argument("within", nargs="?", default="30m")
    p.add_argument("--full", action="store_true", help="every reason in full (default: under 1,500 characters)")
    p = sub.add_parser("export")
    p.add_argument("--to", default=os.path.join(REPO, "infrastructure", "state", "control", "acts.jsonl"))
    sub.add_parser("permit")
    p = sub.add_parser("queue")
    p.add_argument("op", nargs="?", choices=("list",) + QUEUE_OPS)
    p.add_argument("mod", nargs="?")
    p.add_argument("n", nargs="?")
    p.add_argument("--why")
    p.add_argument("--owner-said")
    p.add_argument("--per-ruling")
    p.add_argument("--idem")
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
            _hook_quiet()
            try:
                if o.verb == "condition":
                    code, line = condition(o.run)
                else:
                    code, line = OK, ended(o.run) if o.verb == "ended" else escalate(o.run)
                    if line.startswith("ESCALATION FAILED"):
                        code = FAILED
            except Exception as e:      # noqa: BLE001  named in the journal; the fds are /dev/null now
                _receipt("%s %s: FAILED: %s: %s" % (o.verb, o.run, type(e).__name__, e))
                raise
            _receipt(line)
            return code
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
        elif o.verb == "model":
            lines = cmd_model(o)
        elif o.verb == "queue":
            lines = cmd_queue(o)
        elif o.verb == "next":
            code, lines = forecast(o.within, full=o.full)
        elif o.verb == "export":
            lines = ["%d act(s) exported to %s" % (export_acts(o.to), o.to)]
        elif o.verb == "permit":
            lines = [permit_sync()]
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
