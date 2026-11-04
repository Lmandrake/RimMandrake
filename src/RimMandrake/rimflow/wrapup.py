#!/usr/bin/env python3
"""wrapup.py — the deterministic wrap-up that runs after EVERY agent finishes (AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED).

Owner, 2026-11-04: "asking an agent to do something will NEVER assure it gets done, so there will be debris that piles
up if it leaves a trace. ... We need a deterministic check that ALWAYS happens after the agent finishes to ensure that
any wrap-up occurs. Period."

WHERE IT RUNS (no agent has to remember anything):
  unit      every launched run: role_launch.launch_argv (Relentless workers, checkers, helpers and every role run) and
            detached_helper.launch_argv put `-p ExecStopPost=... wrapup.py unit ...` on the systemd unit, so systemd
            runs it however the run ends: clean exit, kill, RuntimeMaxSec, a stop by the supervisor.
  session   a Claude Code window's end: .claude/hooks/wrapup_hook.py on SessionEnd. Skipped inside a launched unit
            (RM_ROLE_UNIT set): that unit's ExecStopPost is the one wrap-up for it.
  subagent  an in-window helper's end: the same hook on SubagentStop. Report-only: the window goes on, so it holds
            the seat's bridge and claims; what is the helper's own is the clones it worked in.

WHAT IT CENSUSES (one row each; act = cleaned | filed | carried | covered | ok | unmeasured):
  bridge    the shared bridge lock (BRIDGE_SHARED.json) held by this agent's holder from this agent's clone. A unit or
            a session that left it held is RELEASED (`rimflow bridge release` run in that clone); a release that fails,
            a subagent's hold, or one we cannot attribute is filed. His OWNER hold is never touched.
  debt      forced game settings and staged scenes: a tool that forces a setting or stages a scene calls owe() (or
            `wrapup.py owe`) and paid() when it restores; whatever this agent still owes at its end is filed with its
            undo. `owner_key()` names the agent: the unit, else the Claude session, else the process.
  clone     uncommitted, untracked or unpushed work in the clones the agent ran in. A Relentless worker's clone is
            carried (the next worker of that item continues it; the supervisor and the pool alarm own it after);
            so is a SEAT clone (SEAT_CLONES_DEFAULT, env RM_WRAPUP_SEAT_CLONES): every window of the seat shares it;
            anyone else's is filed.
  claims    (session) items this window's seat claimed or started during the session that are still `doing`, less
            those the Relentless supervisor started (it shares the seat key; it carries them).
  tmp       (unit) the run's own TMPDIR: covered by run_tmp.sweep (each Relentless tick); a unit is still stopping when
            ExecStopPost runs, so run_tmp refuses to drop it here.

FILED means: written to <dir>/open/<key>.json. ops_watch's `wrapup` family re-measures every open row (standing() below)
and the target `wrapup.debris_standing > 0` files ONE fixed alarm item (OPS_WRAPUP_DRAIN_DEBRIS_PILES_UP), reopened on a
repeat. A row stops standing when its debris is gone (clone clean and pushed or removed, bridge no longer that hold,
item no longer doing, debt paid); `wrapup.py sweep` moves fully cleared files to resolved/. Every wrap-up appends one
line to <dir>/runs.jsonl, an error included: the wrap-up itself never fails silently and never fails its unit.

    wrapup.py unit --unit U --seat S --clone C [--holder H] [--carried]
    wrapup.py owe --kind setting|scene --what TEXT [--undo TEXT] [--owner KEY]    -> prints the token
    wrapup.py paid TOKEN
    wrapup.py list | sweep | resolve KEY --why TEXT

State dir: RM_WRAPUP_DIR (default D:\\ClaudeWork\\rimmandrake\\wrapup). Names no host or account.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = "/mnt/d/ClaudeWork/rimmandrake/wrapup"
SHARED_BRIDGE_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/scratch/BRIDGE_SHARED.json"   # model.SHARED_BRIDGE_DEFAULT
GIT_TIMEOUT_S = 30
STANDING = ("filed",)


DEFAULT_DIR_WINDOWS = "D:\\ClaudeWork\\rimmandrake\\wrapup"     # a python.exe harness (validation_v2 --live) owes too
# WRAPUP_SEAT_CLONE_SILENCE_FALSE_ROWS: two debris classes no ending agent owns (40 false rows, 2026-11-04):
#  - a SEAT clone is shared by every window of its seat and lives on; its dirt is the seat's work in flight, carried;
#  - an item the Relentless supervisor started (relentless.py ledger_start writes this why, under the BENCH key it
#    shares with the Conductor) is carried by the supervisor, whichever window's session happened to span it.
SEAT_CLONES_DEFAULT = "/home/mandrake/rm/bench" + os.pathsep + "/home/mandrake/rm/foundry"     # = mirror.SEAT_CLONES
RELENTLESS_START_WHY = "relentless supervisor takes the item"                                # = relentless.ledger_start
DEBT_AGE_S = 6 * 3600       # a debt older than this stands whoever owes it: an owner no wrap-up can name still shows


def state_dir():
    if os.environ.get("RM_WRAPUP_DIR"):
        return os.environ["RM_WRAPUP_DIR"]
    if os.environ.get("RM_UNDER_SELFTEST"):
        # a selftest drives the stagers against fakes: its debts (some left on purpose by a failing-restore case)
        # go to its own TMPDIR, never the live register the alarm reads
        return os.path.join(tempfile.gettempdir(), "rm_wrapup_selftest")
    return DEFAULT_DIR_WINDOWS if os.name == "nt" else DEFAULT_DIR


def _p(*parts):
    return os.path.join(state_dir(), *parts)


def _now():
    return time.time()


def _iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def _write_json(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(body, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def safe_key(s):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in str(s))[:120]


# ---------------------------------------------------------------- debts (forced settings, staged scenes)

def owner_key(env=None):
    """The agent a debt belongs to: its launched unit, else its Claude session, else this process."""
    env = os.environ if env is None else env
    if env.get("RM_ROLE_UNIT"):
        return "unit:" + env["RM_ROLE_UNIT"]
    if env.get("CLAUDE_CODE_SESSION_ID"):
        return "session:" + env["CLAUDE_CODE_SESSION_ID"]
    return "pid:%d" % os.getpid()


def owe(kind, what, undo=None, owner=None, extra=None):
    """Record that this agent left the game changed (a setting forced, a scene staged) -> token for paid().
    `extra` adds fields (the bridge door's `key` and `orig`). Best effort for the caller: a register that cannot be
    written prints and returns None, never raises."""
    tok = "%s-%s" % (time.strftime("%Y%m%dT%H%M%S", time.gmtime()), uuid.uuid4().hex[:8])
    body = dict(extra or {})
    body.update({"token": tok, "kind": kind, "what": what, "undo": undo, "owner": owner or owner_key(),
                 "at": _iso(_now()), "cwd": os.getcwd()})
    try:
        _write_json(_p("debts", tok + ".json"), body)
    except OSError as e:
        sys.stderr.write("wrapup: could not record debt %r: %s\n" % (what, e))
        return None
    return tok


def paid(token):
    """The debt is undone. -> True when it was on the register (owed, or filed and keyed: see run())."""
    if not token:
        return False
    hit = False
    for where in (_p("debts"), _p("debts", "filed")):
        try:
            os.remove(os.path.join(where, safe_key(token) + ".json"))
            hit = True
        except OSError:
            pass
    return hit


def debts_keyed(key):
    """Open debts carrying this `key` (the bridge door's setting identity), whoever owes them."""
    out = []
    for f in sorted(glob.glob(_p("debts", "*.json")) + glob.glob(_p("debts", "filed", "*.json"))):
        d = _read_json(f)
        if d and d.get("key") == key:
            out.append(d)
    return out


def debts_of(owner):
    out = []
    for f in sorted(glob.glob(_p("debts", "*.json"))):
        d = _read_json(f)
        if d and d.get("owner") == owner:
            out.append(d)
    return out


# ---------------------------------------------------------------- the real world, behind one seam (tests replace it)

class World(object):
    def git(self, clone, *args):
        """-> (rc, stdout); rc None when git could not be run."""
        try:
            r = subprocess.run(["git", "-C", clone] + list(args), capture_output=True, text=True, timeout=GIT_TIMEOUT_S,
                               stdin=subprocess.DEVNULL)
            return r.returncode, r.stdout
        except (OSError, subprocess.SubprocessError):
            return None, ""

    def shared_bridge(self):
        p = os.environ.get("RIMFLOW_SHARED_BRIDGE", SHARED_BRIDGE_DEFAULT)
        if not p:
            return None
        d = _read_json(p)
        return d if isinstance(d, dict) and d.get("holder") else None

    def release_bridge(self, clone, holder):
        cli = os.path.join(clone, "src", "RimMandrake", "rimflow", "cli.py")
        if not os.path.isfile(cli):
            return False, "no rimflow in %s" % clone
        env = dict(os.environ, RIMFLOW_BRIDGE_SEAT=holder)
        try:
            r = subprocess.run([sys.executable, cli, "bridge", "release"], cwd=clone, env=env, capture_output=True,
                               text=True, timeout=120, stdin=subprocess.DEVNULL)
        except (OSError, subprocess.SubprocessError) as e:
            return False, "%s: %s" % (type(e).__name__, e)
        return r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()[-300:]

    def doing_claims(self, seat, since):
        """-> [(item, ts)] claimed or started by `seat` at or after `since` and still doing; raises when unreadable."""
        sys.path.insert(0, HERE)
        import model  # noqa: E402  (lazy: the unit path must not pay for the ledger)
        evs = model.read()
        w = model.replay(evs)
        return claims_of(evs, {i: getattr(it, "state", None) for i, it in w.items.items()}, seat, since)

    def exists(self, path):
        return os.path.isdir(path)


def claims_of(evs, states, seat, since):
    """-> [(item, ts)] claimed or started by `seat` at or after `since`, still doing, and not the Relentless
    supervisor's: an item whose latest claim/start is the supervisor's start is carried by the supervisor."""
    out, last = {}, {}
    for e in evs:
        if e.get("event") not in ("claim", "start") or not e.get("id"):
            continue
        last[e["id"]] = e
        if e.get("seat") != seat:
            continue
        ts = e.get("ts") or ""
        if ts >= _iso(since):
            out[e["id"]] = ts
    return sorted((i, t) for i, t in out.items()
                  if states.get(i) == "doing" and (last[i].get("why") or "") != RELENTLESS_START_WHY)


# ---------------------------------------------------------------- the census

def seat_clones(env=None):
    env = os.environ if env is None else env
    raw = env.get("RM_WRAPUP_SEAT_CLONES", SEAT_CLONES_DEFAULT)
    return [os.path.realpath(x) for x in raw.split(os.pathsep) if x]


def is_seat_clone(clone, env=None):
    return bool(clone) and os.path.realpath(clone) in seat_clones(env)


def check_clone(world, clone, carried):
    """One row for a clone: dirty / untracked / unpushed work, or ok. A seat clone is always carried."""
    if is_seat_clone(clone):
        return {"kind": "clone", "what": clone, "act": "carried",
                "why": "the shared seat clone: its state is the seat's work in flight, not this agent's debris"}
    if not world.exists(clone):
        return {"kind": "clone", "what": clone, "act": "ok", "why": "gone"}
    rc, top = world.git(clone, "rev-parse", "--show-toplevel")
    if rc != 0:
        return {"kind": "clone", "what": clone, "act": "ok", "why": "not a git clone"}
    rc1, dirty = world.git(clone, "status", "--porcelain", "--untracked-files=normal")
    rc2, ahead = world.git(clone, "rev-list", "--count", "@{upstream}..HEAD")
    if rc2 != 0:
        rc2, ahead = world.git(clone, "rev-list", "--count", "origin/main..HEAD")
    if rc1 != 0:        # doubt files: a clone we cannot read may hold anything
        return {"kind": "clone", "what": clone, "act": "carried" if carried else "filed", "why": "git status failed"}
    lines = [ln for ln in dirty.splitlines() if ln.strip()]
    n_ahead = int((ahead or "0").strip() or 0) if rc2 == 0 else None
    if not lines and n_ahead == 0:
        return {"kind": "clone", "what": clone, "act": "ok", "why": "clean and pushed"}
    why = "%d uncommitted/untracked path(s)%s, %s unpushed commit(s)" % (
        len(lines), (" e.g. " + ", ".join(ln[3:] for ln in lines[:3])) if lines else "",
        "an unmeasured number of" if n_ahead is None else n_ahead)
    return {"kind": "clone", "what": clone, "act": "carried" if carried else "filed", "why": why}


def check_bridge(world, ctx):
    sh = world.shared_bridge()
    if not sh:
        return {"kind": "bridge", "what": "shared lock", "act": "ok", "why": "free"}
    holder, clone = sh.get("holder"), sh.get("clone")
    if holder == "OWNER" or holder != ctx["holder"] or clone not in ctx["clones"]:
        return {"kind": "bridge", "what": "shared lock", "act": "ok",
                "why": "held by %s from %s: not this agent's" % (holder, clone)}
    what = "%s hold from %s (for: %s)" % (holder, clone, sh.get("purpose") or "?")
    if ctx["kind"] == "subagent" or ctx.get("report_only"):
        return {"kind": "bridge", "what": what, "act": "filed",
                "why": "the agent ended with the hold while its window goes on (a helper, or /clear): not released"}
    ok, out = world.release_bridge(clone, holder)
    return {"kind": "bridge", "what": what, "act": "cleaned" if ok else "filed",
            "why": ("released at the agent's end: " if ok else "release failed: ") + out}


def census(world, ctx):
    rows = []
    try:
        rows.append(check_bridge(world, ctx))
    except Exception as e:  # noqa: BLE001  one check's failure is a row, never the wrap-up's end
        rows.append({"kind": "bridge", "what": "shared lock", "act": "filed",     # doubt files
                     "why": "the bridge check failed: %s: %s" % (type(e).__name__, e)})
    for d in debts_of(ctx["owner"]):
        rows.append({"kind": "debt", "what": "%s: %s" % (d.get("kind"), d.get("what")), "act": "filed",
                     "why": "still owed at the agent's end; undo: %s" % (d.get("undo") or "none recorded"),
                     "token": d.get("token"), "keyed": bool(d.get("key"))})
    for c in ctx["clones"]:
        rows.append(check_clone(world, c, ctx.get("carried", False)))
    if ctx["kind"] == "session" and ctx.get("seat"):
        if ctx.get("since") is None:
            rows.append({"kind": "claims", "what": ctx["seat"], "act": "unmeasured", "why": "session start unknown"})
        else:
            try:
                for item, ts in world.doing_claims(ctx["seat"], ctx["since"]):
                    rows.append({"kind": "claims", "what": item, "act": "filed",
                                 "why": "claimed/started %s by %s in this session, still doing" % (ts, ctx["seat"])})
            except Exception as e:  # noqa: BLE001
                rows.append({"kind": "claims", "what": ctx["seat"], "act": "unmeasured",
                             "why": "ledger: %s: %s" % (type(e).__name__, e)})
    if ctx["kind"] == "unit":
        rows.append({"kind": "tmp", "what": ctx["key"], "act": "covered",
                     "why": "run_tmp.sweep removes the run's TMPDIR once the unit is gone"})
    return rows


def run(world, ctx):
    """Census, clean, file. -> the runs.jsonl row. Never raises."""
    t = _now()
    try:
        rows = census(world, ctx)
        err = None
    except Exception as e:  # noqa: BLE001
        rows, err = [{"kind": "wrapup", "what": ctx.get("key"), "act": "filed",
                      "why": "the wrap-up itself failed: %s: %s" % (type(e).__name__, e)}], True
    filed = [r for r in rows if r["act"] in STANDING]
    rec = {"at": _iso(t), "kind": ctx["kind"], "key": ctx["key"], "seat": ctx.get("seat"), "owner": ctx["owner"],
           "clones": ctx["clones"], "rows": rows, "filed": len(filed)}
    try:
        if filed:
            _write_json(_p("open", safe_key("%s-%s" % (ctx["kind"], ctx["key"])) + ".json"),
                        dict(rec, ctx={k: v for k, v in ctx.items() if k != "clones"}))
            for r in filed:                     # a filed debt moves off the register: the open file now holds it
                if r.get("token") and r.get("keyed"):
                    # the bridge door's debt stays findable by key (debts/filed/), so a later write back to the
                    # original pays it and the row stops standing; a restore must never owe the reverse change
                    n = safe_key(r["token"]) + ".json"
                    os.makedirs(_p("debts", "filed"), exist_ok=True)
                    try:
                        os.replace(_p("debts", n), _p("debts", "filed", n))
                    except OSError:
                        pass
                elif r.get("token"):
                    paid(r["token"])
        _append(_p("runs.jsonl"), rec if not err else dict(rec, error=True))
    except OSError as e:
        sys.stderr.write("wrapup: could not write the record: %s\n" % e)
    return rec


# ---------------------------------------------------------------- re-measure what is filed (ops_watch, sweep)

def row_standing(world, row, rec):
    """Is this filed row's debris still there?"""
    k = row.get("kind")
    if k == "clone":
        return check_clone(world, row["what"], False)["act"] in ("filed", "unmeasured")
    if k == "bridge":
        sh = world.shared_bridge()
        ctx = rec.get("ctx") or {}
        return bool(sh) and sh.get("holder") == ctx.get("holder") and sh.get("clone") in (rec.get("clones") or [])
    if k == "claims":
        try:
            return any(i == row["what"] for i, _ in world.doing_claims(rec.get("seat"), 0))
        except Exception:  # noqa: BLE001  unreadable: still standing (never clear on ignorance)
            return True
    if k == "debt" and row.get("keyed"):        # a door debt: until a write puts the setting back (paid())
        return os.path.exists(_p("debts", "filed", safe_key(row.get("token")) + ".json"))
    return True                                 # other debts, wrapup error: until someone resolves it


def aged_debts(now=None):
    """Debts on the register older than DEBT_AGE_S, whatever their owner: a python.exe harness whose owner key no
    wrap-up matches (its environment did not cross), or an agent whose wrap-up never ran. -> [debt]"""
    now = _now() if now is None else now
    cut = _iso(now - DEBT_AGE_S)
    out = []
    for f in sorted(glob.glob(_p("debts", "*.json"))):
        d = _read_json(f)
        if d is None or str(d.get("at") or "") < cut:
            out.append(d or {"token": os.path.basename(f)[:-5], "what": "unreadable debt file"})
    return out


def standing(world=None, now=None):
    """-> [(path, rec, [standing rows])] for every open file, plus one pseudo-file for the aged debts."""
    world = world or World()
    out = []
    old = aged_debts(now)
    if old:
        out.append((_p("debts", "aged.json"), {}, [{"kind": "debt", "what": "%s: %s" % (d.get("kind"), d.get("what")),
                                                    "act": "filed", "why": "owed over %d h by %s; undo: %s" % (
                                                        DEBT_AGE_S // 3600, d.get("owner"), d.get("undo") or "none"),
                                                    "token": d.get("token")} for d in old]))
    for f in sorted(glob.glob(_p("open", "*.json"))):
        rec = _read_json(f)
        if not rec:
            out.append((f, {}, [{"kind": "wrapup", "what": f, "act": "filed", "why": "unreadable open file"}]))
            continue
        rows = [r for r in rec.get("rows", []) if r.get("act") in STANDING and row_standing(world, r, rec)]
        out.append((f, rec, rows))
    return out


def sweep(world=None):
    """Move every open file whose rows have all cleared to resolved/. -> (cleared, still open)."""
    cleared, left = 0, 0
    for f, rec, rows in standing(world):
        if not rec:                             # the aged debts: cleared only by paid() or `wrapup.py paid`
            left += bool(rows)
            continue
        if rows:
            left += 1
            continue
        _resolve(f, "every filed row cleared on re-measure")
        cleared += 1
    return cleared, left


def _resolve(path, why):
    rec = _read_json(path) or {}
    rec["resolved"] = {"at": _iso(_now()), "why": why}
    _write_json(_p("resolved", os.path.basename(path)), rec)
    for r in rec.get("rows") or []:             # a resolved door debt leaves debts/filed/: the door forgets the key
        if r.get("keyed") and r.get("token"):
            paid(r["token"])
    os.remove(path)


# ---------------------------------------------------------------- entry points

def unit_ctx(unit, seat, clone, holder=None, carried=False, env=None):
    env = os.environ if env is None else env
    return {"kind": "unit", "key": unit, "seat": seat, "owner": "unit:" + unit,
            "holder": holder or env.get("RIMFLOW_BRIDGE_SEAT") or seat,
            "clones": [os.path.abspath(clone)] if clone else [], "carried": carried, "since": None}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("unit")
    u.add_argument("--unit", required=True)
    u.add_argument("--seat", required=True)
    u.add_argument("--clone", required=True)
    u.add_argument("--holder")
    u.add_argument("--carried", action="store_true")
    o = sub.add_parser("owe")
    o.add_argument("--kind", required=True, choices=("setting", "scene", "other"))
    o.add_argument("--what", required=True)
    o.add_argument("--undo")
    o.add_argument("--owner")
    p = sub.add_parser("paid")
    p.add_argument("token")
    sub.add_parser("list")
    sub.add_parser("sweep")
    r = sub.add_parser("resolve")
    r.add_argument("key")
    r.add_argument("--why", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "unit":
        run(World(), unit_ctx(a.unit, a.seat, a.clone, a.holder, a.carried))
        # silent: ExecStopPost inherits the unit's StandardOutput=file:, which reopens at offset 0 and overwrote the
        # head of the run's result JSON (role:Operations:failed "no result file", 2026-11-04); the record is runs.jsonl
        return 0                                # ExecStopPost: never fail the unit
    if a.cmd == "owe":
        tok = owe(a.kind, a.what, a.undo, a.owner)
        print(tok or "")
        return 0 if tok else 1
    if a.cmd == "paid":
        return 0 if paid(a.token) else 1
    if a.cmd == "list":
        for f, rec, rows in standing():
            for row in rows:
                print("%s  %s  %s  %s" % (os.path.basename(f)[:-5], row["kind"], row["what"], row.get("why", "")))
        return 0
    if a.cmd == "sweep":
        c, left = sweep()
        print("wrapup sweep: %d cleared, %d still open" % (c, left))
        return 0
    if a.cmd == "resolve":
        f = _p("open", safe_key(a.key) + ".json")
        if not os.path.isfile(f):
            print("wrapup: no open record %s" % a.key, file=sys.stderr)
            return 1
        _resolve(f, a.why)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
