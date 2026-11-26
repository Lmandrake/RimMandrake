#!/usr/bin/env python3
"""pipe: command the Maturation Pipeline in one line (item RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS).

The owner, 2026-11-18 ~10:40 AM PST: "I want to be able to trivially have you submit a command to change consumable
resources like looks, runs, etc. to modify the record when it fails due to other reasons or even if we want to make an
exception. ... This should be a one-line bash command, ok? ... Individual items should be trivially switchable on and
off. Queues should be trivially editable. Make all of this deterministic, easy, traceable, reproducable, testable".

ONE control store, in the pipeline's shared state folder (the Dispatch tick's, not a clone: a command typed in any
clone acts on the one live pipeline at its next read, no publish):
    <dir>/control.jsonl   the journal: one JSON line per act (who, when in UTC and Pacific, why, before, after)
    <dir>/control.json    the state the journal folds to (rewritten after every act; rebuilt from the journal when
                          it lags, so a crash between the two writes loses nothing)
<dir> is RM_PIPE_CONTROL_DIR, else RM_MATURATION_DISPATCH_DIR, else doorbell.state_dir()/maturation
(D:\\ClaudeWork\\rimmandrake\\dispatcher\\maturation, the folder rm-maturation-dispatch.service's tick writes).

Readers (every one goes through this module; selftest_pipeline_control enumerates them):
    used(mod, res, measured)  -> the pipeline's own count plus the store's override, never below 0
    limit(mod, res, default)  -> the store's limit, else the default the reader passes
    off(mod=, item=, stage=)  -> why that thing is OFF, or None
    off_mods()                -> {mod: hold-shaped row} for mod_owner_hold.load(), so every hold reader honours it
    queue_order(mods)         -> mods in the store's queue order (unlisted ones after, in their own order)
An unreadable or malformed store raises Unreadable from every reader: a reader launches nothing it cannot prove on.

  pipe show [Mod]                         every mod: stage, ON/OFF, each consumable used/limit, the queue
  pipe set <Mod> <res> <N> --why ...      the count reads N now (the override is N minus the pipeline's own count)
  pipe add <Mod> <res> <+N|-N> --why ...  move the count by N
  pipe reset <Mod> <res|all> --why ...    the count reads 0
  pipe limit <Mod> <res> <N|default> --why ...   the most allowed (default: the pipeline's own setting)
  pipe on|off <Mod|item:ID|stage:S|all> --why ...
  pipe queue [list|top <Mod>|bottom <Mod>|move <Mod> <pos>|drop <Mod>|add <Mod>] --why ...
  pipe log [-n N]                         the last acts
  pipe undo <act-id> --why ...            put back what that act changed (itself an act)
Every act takes --why (and --owner-said when the words are his) and prints at most 3 lines: before -> after, the act
id, the undo command. Selftest: selftest_pipeline_control.py.
"""
import argparse
import contextlib
import datetime as dt
import difflib
import fcntl
import hashlib
import json
import os
import re
import socket
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DISPATCH_ROOT = "/home/mandrake/rm/dispatch"     # rm-maturation-dispatch.service's WorkingDirectory: the tree it reads
JOURNAL, SNAPSHOT, LOCK = "control.jsonl", "control.json", "control.lock"
SECTIONS = ("counts", "limits", "off", "queue")
UNM = "UNMEASURED"


class Unreadable(Exception):
    pass


class Refused(Exception):
    pass


def control_dir():
    d = os.environ.get("RM_PIPE_CONTROL_DIR")
    if not d:
        d = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    if not d:
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import doorbell
        d = os.path.join(doorbell.state_dir(), "maturation")
    return d


def isolated():
    """True when a selftest has pointed the owner hold at its own file but the control store at nothing: such a test
    reads no live switches (the live store would make it depend on today's acts)."""
    return bool(os.environ.get("RM_OWNER_HOLD_FILE")) and not (
        os.environ.get("RM_PIPE_CONTROL_DIR") or os.environ.get("RM_MATURATION_DISPATCH_DIR"))


# ---------------------------------------------------------------- the store

def empty():
    return {"counts": {}, "limits": {}, "off": {}, "queue": None, "acts": 0, "last": None}


def apply_act(state, a):
    """Fold one act into state (in place). The act carries the full after value of one key; None removes it."""
    sec, name, after = a["sec"], a.get("name"), a.get("after")
    if sec == "queue":
        state["queue"] = after
    elif after is None:
        state[sec].pop(name, None)
    else:
        state[sec][name] = after
    state["acts"] += 1
    state["last"] = a["id"]
    return state


def _check_act(a, n, p):
    if not (isinstance(a, dict) and isinstance(a.get("id"), str) and a.get("sec") in SECTIONS
            and (a["sec"] == "queue" or isinstance(a.get("name"), str))):
        raise Unreadable("%s line %d is not a control act: %r" % (p, n, a))


def fold(lines, p="journal"):
    st = empty()
    for n, ln in enumerate(lines, 1):
        if not ln.strip():
            continue
        try:
            a = json.loads(ln)
        except ValueError as e:
            raise Unreadable("%s line %d cannot be read (%s)" % (p, n, e))
        _check_act(a, n, p)
        apply_act(st, a)
    return st


_CACHE = {}


def _stat(p):
    try:
        s = os.stat(p)
        return (s.st_mtime_ns, s.st_size)
    except FileNotFoundError:
        return None


def state(d=None):
    """-> the control state. No journal at all is the empty store (nothing ever commanded: a measured empty, not a
    blind read). A journal that cannot be read, or a snapshot that is not an object, raises Unreadable."""
    d = d or control_dir()
    jp, sp = os.path.join(d, JOURNAL), os.path.join(d, SNAPSHOT)
    js, ss = _stat(jp), _stat(sp)
    key = (d, js, ss)
    if _CACHE.get("key") == key:
        return _CACHE["state"]
    if js is None:
        if ss is not None:
            raise Unreadable("%s exists with no %s beside it: the journal is the record; restore it" % (sp, jp))
        st = empty()
    else:
        snap = None
        if ss is not None:
            try:
                with open(sp, encoding="utf-8") as f:
                    snap = json.load(f)
            except (OSError, ValueError):
                snap = None         # a torn snapshot is rebuilt from the journal below
        if isinstance(snap, dict) and snap.get("journal_bytes") == js[1] and all(k in snap for k in empty()):
            st = {k: snap[k] for k in empty()}
        else:
            try:
                with open(jp, encoding="utf-8") as f:
                    st = fold(f.read().splitlines(), jp)
            except OSError as e:
                raise Unreadable("%s: %s" % (jp, e))
    for k in ("counts", "limits", "off"):
        if not isinstance(st.get(k), dict):
            raise Unreadable("%s: %s is not an object" % (d, k))
    if st.get("queue") is not None and not isinstance(st["queue"], list):
        raise Unreadable("%s: queue is not a list" % d)
    _CACHE.update(key=key, state=st)
    return st


@contextlib.contextmanager
def _locked(d):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, LOCK), "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _write_snapshot(d, st):
    js = _stat(os.path.join(d, JOURNAL))
    doc = dict(st, journal_bytes=js[1] if js else 0)
    p = os.path.join(d, SNAPSHOT)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False, sort_keys=True)
    os.replace(p + ".tmp", p)


def who():
    seat = (os.environ.get("AGENT_SEAT") or os.environ.get("RIMFLOW_SEAT") or os.environ.get("USER") or "?").strip()
    return "%s@%s:%s" % (seat, socket.gethostname(), os.path.basename(os.getcwd()))


def pac_str(t):
    try:
        from zoneinfo import ZoneInfo
        z = ZoneInfo("America/Los_Angeles")
    except Exception:       # noqa: BLE001  no tz database: say so rather than print a UTC time as Pacific
        return UNM
    return dt.datetime.fromtimestamp(t, z).strftime("%Y-%m-%d %I:%M:%S %p %Z")


def act(sec, name, after, why, verb, owner_said=None, undoes=None, d=None, now=None, before_fn=None):
    """Append one act and refold. -> the act. before_fn(state) -> the value before (default: the store's own)."""
    if not (isinstance(why, str) and why.strip()):
        raise Refused("--why is required")
    d = d or control_dir()
    now = now if now is not None else time.time()
    with _locked(d):
        _CACHE.clear()
        st = state(d)
        before = before_fn(st) if before_fn else (st["queue"] if sec == "queue" else st[sec].get(name))
        seed = "%s|%s|%s|%s|%s|%d" % (sec, name, json.dumps(after, sort_keys=True), why, now, st["acts"])
        a = {"id": "pc_" + hashlib.sha1(seed.encode()).hexdigest()[:10], "verb": verb, "sec": sec, "name": name,
             "before": before, "after": after, "why": why.strip(), "who": who(),
             "at": dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "at_pacific": pac_str(now), "ts": now}
        if sec == "off" and isinstance(after, dict):
            a["after"] = after = dict(after, act=a["id"])     # every OFF status names the act that switched it
        if owner_said:
            a["owner_said"] = owner_said
        if undoes:
            a["undoes"] = undoes
        with open(os.path.join(d, JOURNAL), "a", encoding="utf-8") as f:
            f.write(json.dumps(a, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        new = apply_act(json.loads(json.dumps(st)), a)
        _write_snapshot(d, new)
        _CACHE.clear()
    return a


def journal(d=None):
    p = os.path.join(d or control_dir(), JOURNAL)
    try:
        with open(p, encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as e:
        raise Unreadable("%s: %s" % (p, e))


# ---------------------------------------------------------------- the readers

def _ck(mod, res):
    return "%s/%s" % (os.path.basename(os.path.normpath(str(mod))), res)


def _C():
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import control as C
    return C


def used(mod, res, measured, st=None):
    """The count every reader compares with its limit: the pipeline's own count plus the control store's
    adjustments (control.used: typed accounts, slice 2), never below 0. Raises Unreadable on a store that cannot be
    read. `st` is accepted for old callers and not read: the counts left this journal."""
    C = _C()
    try:
        return C.used(mod, res, measured)
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)


def limit(mod, res, default, st=None):
    C = _C()
    try:
        return C.limit(mod, res, default)
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)


def subjects(res):
    """-> every account key holding a live adjustment of `res` (control.subjects). Raises Unreadable."""
    C = _C()
    try:
        return C.subjects(res)
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)


def off(mod=None, item=None, stage=None, st=None):
    """-> why the named thing is OFF ('all', the mod, the item or the stage), or None. The switches live in control.py's
    store (`pipe on|off`), the one store every launch reads; `st` is accepted for old callers and not read. Raises
    Unreadable when that store cannot be read (nothing launches on a switch nobody can read)."""
    import control as C
    keys = ["all"]
    if mod:
        keys.append("mod:" + os.path.basename(os.path.normpath(str(mod))))
    if item:
        keys.append("item:" + str(item))
    if stage:
        keys.append("stage:" + str(stage))
    try:
        rows = {(r["scope"], r["layer"]): r for r in C.switches()}
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)
    for k in keys:
        r = rows.get((k, "control")) or rows.get((k, "owner"))
        if r:
            return "OFF by pipe (%s, act %s at %s): %s" % (k, r.get("act"), r.get("at_pacific"), r.get("why")) \
                if r["layer"] == "control" else C.describe(r)
    return None


def off_mods(st=None):
    """-> {mod: a mod_owner_hold-shaped row} for every mod `pipe off` switched off (control.py's store; his own holds
    are mod_owner_hold's). Rows carry control=True; their status reads OFF, never HELD BY OWNER."""
    import control as C
    try:
        return {m: h for m, h in C.mod_holds().items() if h.get("control")}
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)


def queue_order(mods, st=None):
    """-> mods reordered by the store's queue (a queued mod not in mods is skipped; an unqueued one keeps its place
    after the queued ones). With no queue set, mods unchanged."""
    st = st if st is not None else (empty() if isolated() else state())
    q = st.get("queue")
    if not q:
        return list(mods)
    first = [m for m in q if m in mods]
    return first + [m for m in mods if m not in first]


# ---------------------------------------------------------------- the consumables (census)

def _root():
    r = os.environ.get("RM_PIPE_ROOT")
    if r:
        return r
    return DISPATCH_ROOT if os.path.isdir(os.path.join(DISPATCH_ROOT, "src")) else REPO


class Ctx:
    """Lazy reads for measuring: the dispatch tree and the tick's state.json, each read once."""

    def __init__(self, root=None, mdir=None):
        self.root = root or _root()
        self.mdir = mdir
        self._st = self._cfg = None
        self._facts = {}

    def _imp(self):
        if HERE not in sys.path:
            sys.path.insert(0, HERE)

    def dstate(self):
        if self._st is None:
            d = self.mdir or os.environ.get("RM_MATURATION_DISPATCH_DIR")
            if not d:
                self._imp()
                import doorbell
                d = os.path.join(doorbell.state_dir(), "maturation")
            p = os.path.join(d, "state.json")
            try:
                with open(p, encoding="utf-8") as f:
                    self._st = json.load(f)
            except FileNotFoundError:
                self._st = {}
            except (OSError, ValueError) as e:
                self._st = {"_error": "%s: %s" % (p, e)}
        return self._st

    def cfg(self):
        if self._cfg is None:
            try:
                with open(os.path.join(self.root, "src", "RimMandrake", "rimflow", "maturation_dispatch.json"),
                          encoding="utf-8") as f:
                    self._cfg = json.load(f)
            except (OSError, ValueError):
                self._cfg = {}
        return self._cfg

    def mods(self):
        ms = list(self.cfg().get("advancing") or [])
        return ms + [m for m in sorted((self.dstate().get("mods") or {})) if m not in ms]

    def mstate(self, mod):
        return (self.dstate().get("mods") or {}).get(mod) or {}

    def reading(self):
        """The tick's last reading (reading.json beside state.json): each mod's stage and stage_tokens."""
        if "reading" not in self._facts:
            d = self.mdir or os.environ.get("RM_MATURATION_DISPATCH_DIR")
            if not d:
                self._imp()
                import doorbell
                d = os.path.join(doorbell.state_dir(), "maturation")
            p = os.path.join(d, "reading.json")
            try:
                with open(p, encoding="utf-8") as f:
                    self._facts["reading"] = json.load(f)
            except FileNotFoundError:
                self._facts["reading"] = {"_error": "%s: no reading yet" % p}
            except (OSError, ValueError) as e:
                self._facts["reading"] = {"_error": "%s: %s" % (p, e)}
        return self._facts["reading"]

    def refusal_counters(self):
        if "refusals" not in self._facts:
            self._imp()
            try:
                import refusal_contract as RC
                self._facts["refusals"] = RC.counters()
            except Exception as e:      # noqa: BLE001  UNMEASURED, never 0
                self._facts["refusals"] = {"_error": "%s: %s" % (type(e).__name__, e)}
        return self._facts["refusals"]

    def version(self, mod):
        self._imp()
        try:
            import maturation as M
            return (M.load(self.root, mod) or {}).get("version") or UNM
        except Exception:       # noqa: BLE001
            return UNM

    def facts(self, mod, kind):
        k = (mod, kind)
        if k not in self._facts:
            self._imp()
            try:
                import maturation as M
                self._facts[k] = (M.blind_facts if kind == "blind" else M.ingame_facts)(self.root, mod)
            except Exception as e:      # noqa: BLE001  a measure that cannot read is UNMEASURED, never 0
                self._facts[k] = {"_error": "%s: %s" % (type(e).__name__, e)}
        return self._facts[k]

    def stage(self, mod):
        self._imp()
        try:
            import maturation as M
            rec = M.load(self.root, mod) or {}
            return rec.get("stage") or "-"
        except Exception as e:      # noqa: BLE001
            return UNM

    def coverage(self, mod):
        k = (mod, "coverage")
        if k not in self._facts:
            d = os.path.join(self.root, "design", "concepts", mod)
            try:
                with open(os.path.join(d, "stage.json"), encoding="utf-8") as f:
                    st = json.load(f)
                self._imp()
                import coverage_judge as CJ
                self._facts[k] = (st, d, CJ.rounds(st, d), CJ)
            except FileNotFoundError:
                self._facts[k] = None
            except Exception as e:      # noqa: BLE001
                self._facts[k] = {"_error": "%s: %s" % (type(e).__name__, e)}
        return self._facts[k]


def _cov_since(c, malformed=False):
    """-> (the rounds the caps count: since the later of the last release and the last sign-off, else all; True when a
    release still stands), by coverage_judge's own counting_window, so the count shown is the count the stop reads.
    malformed=True: the malformed cap's rounds (a sign-off does not reset them)."""
    st, d, rs, cj = c
    standing, win, _since, bad_win, _bad_since = cj.counting_window(st, d, rs)
    return (bad_win if malformed else win), bool(standing)


def m_granted_look(ctx, mod):
    """The refusing looks since the release (coverage_judge.stop_reason's count): its one look spent by a refusal."""
    c = ctx.coverage(mod)
    if c is None:
        return None, None
    if isinstance(c, dict):
        return UNM + " (%s)" % c["_error"], 1
    after, rel = _cov_since(c)
    return (sum(1 for r in c[3]._looks(after) if r.get("verdict") == "not_covered"), 1) if rel else (None, None)


def _cov_count(pred, lim_name, before_release_only=False, malformed=False):
    def m(ctx, mod):
        c = ctx.coverage(mod)
        if c is None:
            return None, None
        if isinstance(c, dict):
            return UNM + " (%s)" % c["_error"], None
        after, rel = _cov_since(c, malformed)
        if before_release_only and rel:     # stop_reason counts these only while no release stands
            return None, None
        if pred is None:            # the run cap counts looks (coverage_judge._looks), not every round
            return len(c[3]._looks(after)), getattr(c[3], lim_name)
        return sum(1 for r in after if pred(r)), getattr(c[3], lim_name)
    return m


def m_blind_visit(ctx, mod):
    f = ctx.facts(mod, "blind")
    if f.get("_error"):
        return UNM + " (%s)" % f["_error"], None
    if ctx.stage(mod) != "blind_challenge":
        return None, None
    vid = "%s#%s" % (f.get("version"), f.get("visit_first"))
    ours = [x for x in ctx.mstate(mod).get("blind_auto") or [] if x.get("visit_id") == vid]
    return len(ours), int(ctx.cfg().get("blind_auto_cycles_per_visit", 1))


def m_blind_total(ctx, mod):
    f = ctx.facts(mod, "blind")
    if f.get("_error"):
        return UNM + " (%s)" % f["_error"], None
    if ctx.stage(mod) != "blind_challenge":
        return None, None
    ctx._imp()
    import maturation as M
    return int(f.get("visit") or 0), M.CYCLE_LIMIT


def m_ingame_visit(ctx, mod):
    f = ctx.facts(mod, "ingame")
    if f.get("_error"):
        return UNM + " (%s)" % f["_error"], None
    if ctx.stage(mod) != "in_game":
        return None, None
    vid = "%s#%s" % (f.get("version"), f.get("visit"))
    ours = [x for x in ctx.mstate(mod).get("ingame_auto") or [] if x.get("visit_id") == vid]
    return len(ours), int(ctx.cfg().get("ingame_auto_runs_per_visit", 1))


def m_steward(ctx, mod):
    """The steward runs on the mod's current version (maturation_autonomy._gate's count, the key in flight included)."""
    ver = ctx.version(mod)
    if ver == UNM:
        return UNM, None
    done = ctx.mstate(mod).get("steward") or {}
    import maturation_autonomy as AUT
    return len([k for k, x in done.items() if str(k).startswith(str(ver)) and AUT.is_run(x)]), int(
        ctx.cfg().get("steward_max_per_version", 12))


def m_fixer(ctx, mod):
    return len(ctx.mstate(mod).get("fixers") or {}), int(ctx.cfg().get("steward_max_per_version", 12))


def m_launch_tries(ctx, mod):
    """The most tries spent by one of the mod's booked launches that failed (each book: blind, in-game, stewards,
    fixers, a Stage 3 retry); None when none failed. The readers count each entry's own tries against the limit."""
    s = ctx.mstate(mod)
    ents = []
    for k in ("blind_auto", "ingame_auto"):
        ents += [x for x in s.get(k) or [] if isinstance(x, dict)]
    for k in ("steward", "fixers"):
        ents += [x for x in (s.get(k) or {}).values() if isinstance(x, dict)]
    ents += [x for x in (s.get("launch_retry"), s.get("stopped")) if isinstance(x, dict)]
    tries = [int(x.get("tries") or 1) for x in ents if x.get("failed") or x.get("launch_failed")]
    return (max(tries) if tries else None), int(ctx.cfg().get("launch_tries", 3))


def m_chain(ctx, mod):
    ctx._imp()
    import maturation_autonomy as AUT
    r = AUT.designer_chain(mod, time.time(), raw=True)
    return (UNM, None) if r is None else r[:2]


def refusal_subject(ctx, name):
    """The refusal account a `pipe` line names: an item in the refusal counters as written (Graffiti@0.1.0, an item
    id), else a mod, read as <Mod>@<its version> (maturation_advance's item). -> the subject, or Refused."""
    cs = ctx.refusal_counters()
    items = cs.get("items") or {} if isinstance(cs, dict) and not cs.get("_error") else {}
    if name in items:
        return name
    if "@" in str(name):        # <Mod>@<version>, before its first counted verdict: the mod must be the pipeline's
        m, ver = str(name).split("@", 1)
        return "%s@%s" % (mod_name(m, ctx), ver)
    m = mod_name(name, ctx)
    ver = ctx.version(m)
    if ver == UNM:
        raise Refused("%s has no readable stage record, so its refusal account (<Mod>@<version>) is unknown; name the "
                      "item as the counters write it" % m)
    return "%s@%s" % (m, ver)


def m_refusals(ctx, subject):
    ctx._imp()
    import refusal_contract as RC
    cs = ctx.refusal_counters()
    if cs.get("_error"):
        return UNM + " (%s)" % cs["_error"], RC.ITEM_ALARM_AT
    it = (cs.get("items") or {}).get(subject)
    if it is None:
        return None, RC.ITEM_ALARM_AT
    # a <Mod>@<version> subject is maturation.py advance's, whose family counts refusals in a window (FAMILY_TUNING)
    tune = RC.FAMILY_TUNING.get("maturation_advance") if "@" in subject else None
    if tune:
        now = time.time()
        return len([h for h in it.get("refused_at") or [] if now - float(h.get("at") or 0) < tune["window_s"]]), \
            RC.ITEM_ALARM_AT
    return int(it.get("refused") or 0), RC.ITEM_ALARM_AT


def _m_spend(stage):
    """The stage's spend on the mod's merits (the tick's last reading of it, reading.json's stage_tokens) and the
    ceiling (stage_ceiling_tokens), both weighted tokens as they stand: the store keeps whole numbers. A reading from
    before 2026-11-26 holds stage_usd (list dollars): it converts once, through role_launch.list_usd_to_weighted."""
    def m(ctx, mod):
        if ctx.stage(mod) != stage:
            return None, None
        ctx._imp()
        import maturation_dispatch as MD
        import role_launch as RL
        c = ctx.cfg().get("stage_ceiling_tokens")
        lim = int(c) if MD._amount_ok(c, True) else None
        rd = ctx.reading()
        if rd.get("_error"):
            return UNM + " (%s)" % rd["_error"], lim
        row = (rd.get("mods") or {}).get(mod) or {}
        if row.get("stage") != stage:
            return UNM + " (no stage_tokens in the tick's last reading)", lim
        if MD._amount_ok(row.get("stage_tokens")):
            return int(round(row["stage_tokens"])), lim
        if MD._amount_ok(row.get("stage_usd")):     # a reading from before 2026-11-26
            return RL.list_usd_to_weighted(row["stage_usd"]), lim
        return UNM + " (no stage_tokens in the tick's last reading)", lim
    return m


def pilot_subject(ctx, name):
    """The Test Pilot streak account a `pipe` line names: an item id, as the ledger writes it (the streak is an item's,
    never a mod's). An id the ledger does not hold yet is taken: the account waits for the item, and the reply says
    so. -> the id, or Refused for a name that is no item id."""
    if not re.match(r"^[A-Z][A-Z0-9_]*$", str(name or "")):
        raise Refused("pilot_streak is an item's account: name the item id (UPPER_SNAKE), not %r" % (name,))
    return str(name)


def m_pilot_streak(ctx, item):
    """The item's Test Pilot streak as testpilot_route.judge counts it (non-pass runs in a row since its last sitting,
    voided runs out, the worse of the whole item and one criterion or config) and its default limit (STREAK)."""
    ctx._imp()
    import testpilot_route as TP
    try:
        import model
        evs = model.read()
        it = model.replay(evs).items.get(item)
    except Exception as e:      # noqa: BLE001  UNMEASURED, never 0
        return UNM + " (the ledger: %s: %s)" % (type(e).__name__, e), TP.STREAK
    if it is None:
        return None, TP.STREAK
    void, _unread = TP.voids()
    return TP.streak_count(it, evs, void)[0], TP.STREAK


SPEND_RES = {"offline_build": "spend_offline_build", "blind_challenge": "spend_blind_challenge",
             "in_game": "spend_in_game"}
ACCOUNT_KEY = {"refusals": refusal_subject,      # a consumable not keyed by the mod alone: its subject
               "pilot_streak": pilot_subject}


# name -> (short label, what it counts, measure(ctx, mod) -> (measured | None when it does not apply | UNM..., default
#          limit), the readers that must call used()/limit() with this name: (module, function))
RESOURCES = {
    "granted_look": ("look", "refusing coverage looks since the last release (a release grants exactly one look)",
                     m_granted_look, [("coverage_judge", "look_balance")]),
    "coverage_runs": ("cov-runs", "coverage-judge runs (since the last sign-off or release, if any)",
                      _cov_count(None, "JUDGE_RUNS_MAX"), [("coverage_judge", "_caps")]),
    "coverage_not_covered": ("cov-nc", "not_covered coverage verdicts (since the last sign-off; none while a release stands)",
                             _cov_count(lambda r: r.get("verdict") == "not_covered", "NOT_COVERED_LIMIT", True),
                             [("coverage_judge", "stop_reason")]),
    "coverage_malformed": ("cov-bad", "malformed coverage verdicts (since the last release, if any)",
                           _cov_count(lambda r: r.get("verdict") == "malformed", "MALFORMED_LIMIT", malformed=True),
                           [("coverage_judge", "_caps")]),
    "blind_cycles_visit": ("blind-auto", "automatic blind cycles this visit (blind_auto_cycles_per_visit)",
                           m_blind_visit, [("maturation_dispatch", "decide_blind")]),
    "blind_cycles_total": ("cycles", "blind cycles in this visit; past the limit the Conductor decides (CYCLE_LIMIT)",
                           m_blind_total, [("maturation", "evaluate"), ("maturation", "gate_step"),
                                           ("maturation_autonomy", "_route")]),
    "ingame_runs_visit": ("ingame-auto", "automatic in-game runs this visit (ingame_auto_runs_per_visit)",
                          m_ingame_visit, [("maturation_dispatch", "decide_ingame")]),
    "steward_runs": ("stewards", "automatic steward runs at this version (steward_max_per_version)",
                     m_steward, [("maturation_autonomy", "_gate")]),
    "fixer_runs": ("fixers", "automatic road-back fixer runs on the mod, every version (steward_max_per_version)",
                   m_fixer, [("maturation_autonomy", "_gate")]),
    "launch_tries": ("tries", "tries of a booked launch that failed, each launch its own count (launch_tries)",
                     m_launch_tries, [("maturation_autonomy", "tries_left")]),
    "chain_runs_day": ("chains", "chained Designer runs on the concept today (chain_max_per_day)",
                       m_chain, [("role_launch", "chain_cap"), ("maturation_autonomy", "designer_chain")]),
    "refusals": ("refusals", "refused verdicts on one item, <Mod>@<version> (refusal_contract.ITEM_ALARM_AT: the "
                 "item's alarm)", m_refusals, [("refusal_contract", "submit")]),
    "pilot_streak": ("streak", "non-pass runs in a row on one item since its last Test Pilot sitting, voided runs out "
                     "(testpilot_route.STREAK: past it the item goes to a Test Pilot)", m_pilot_streak,
                     [("testpilot_route", "judge")]),
    "spend_offline_build": ("spend-build", "weighted tokens spent at the offline build (stage_ceiling_tokens)",
                            _m_spend("offline_build"), [("maturation_dispatch", "stage_spend")]),
    "spend_blind_challenge": ("spend-blind", "weighted tokens spent at the blind challenge (stage_ceiling_tokens)",
                              _m_spend("blind_challenge"), [("maturation_dispatch", "stage_spend")]),
    "spend_in_game": ("spend-ingame", "weighted tokens spent at in-game acceptance (stage_ceiling_tokens)",
                      _m_spend("in_game"), [("maturation_dispatch", "stage_spend")]),
}


def resource(name):
    if name in RESOURCES:
        return name
    by_label = {v[0]: k for k, v in RESOURCES.items()}
    if name in by_label:
        return by_label[name]
    near = difflib.get_close_matches(name, list(RESOURCES) + list(by_label), n=4, cutoff=0.3)
    raise Refused("no consumable %r; nearest: %s (all: pipe show <Mod>)" % (name, ", ".join(near) or ", ".join(RESOURCES)))


def mod_name(name, ctx):
    m = os.path.basename(os.path.normpath(str(name)))
    mods = ctx.mods()
    if m in mods or os.path.isdir(os.path.join(ctx.root, "design", "concepts", m)):
        return m
    near = difflib.get_close_matches(m, mods, n=4, cutoff=0.3) or mods[:6]
    raise Refused("no mod %r in the pipeline; nearest: %s" % (m, ", ".join(near)))


def reading(ctx, mod, res, st):
    """-> (measured, used, limit, adjusted: the store holds a count adjustment) for one consumable, or None when it does
    not apply to the mod now."""
    if res in ACCOUNT_KEY:
        try:
            mod = ACCOUNT_KEY[res](ctx, mod)
        except Refused:
            return None
    meas, dlim = RESOURCES[res][2](ctx, mod)
    u, lim = used(mod, res, meas if meas is not None else 0), limit(mod, res, dlim)
    big = 10 ** 15      # a count no consumable reaches: it moves only when the store holds an adjustment
    adjusted = used(mod, res, big) != big
    if meas is None and not u and lim == dlim and not adjusted:
        return None
    return meas, u, lim, adjusted


# ---------------------------------------------------------------- the verbs

def _fmt(meas, u, lim):
    return "%s/%s" % (u, "-" if lim is None else lim)


def _undo_line(a):
    return "undo: pipe undo %s --why \"...\"" % a["id"]


def do_count(ctx, verb, mod, res, n, why, owner_said=None):
    """`pipe set|add|reset`: one adjustment in the control store (control.set_account), at this revision."""
    res = resource(res)
    mod = ACCOUNT_KEY[res](ctx, mod) if res in ACCOUNT_KEY else mod_name(mod, ctx)
    meas, dlim = RESOURCES[res][2](ctx, mod)
    C = _C()
    m = meas if isinstance(meas, int) and not isinstance(meas, bool) else None
    try:
        r = C.set_account(mod, res, n, why, measured=m, verb=verb, owner_said=owner_said)
        lim = limit(mod, res, dlim)
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)
    except C.Refused as e:
        raise Refused(str(e))
    note = ("pipeline count %d" % m) if m is not None else "pipeline count %s; adjustment total pinned" % (
        "not applicable now" if meas is None else meas)
    a = r["act"]
    return ["%s %s used %s -> %s (%s, adjustment %+d)" % (mod, res, _fmt(None, r["before"], lim),
                                                         _fmt(None, r["after"], lim), note, r["delta"]),
            "act %s rev %s at %s" % (a["id"], a["rev"], a["at_pacific"]), _undo_line(a)]


def do_limit(ctx, mod, res, n, why, owner_said=None):
    res = resource(res)
    mod = ACCOUNT_KEY[res](ctx, mod) if res in ACCOUNT_KEY else mod_name(mod, ctx)
    _meas, dlim = RESOURCES[res][2](ctx, mod)
    C = _C()
    try:
        r = C.set_limit(mod, res, None if n == "default" else int(n), why, owner_said=owner_said)
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)
    a = r["act"]
    return ["%s %s limit %s -> %s (pipeline default %s)" % (mod, res, dlim if r["before"] is None else r["before"],
                                                            dlim if n == "default" else n, dlim),
            "act %s rev %s at %s" % (a["id"], a["rev"], a["at_pacific"]), _undo_line(a)]


STAGES = ("designer", "offline_build", "blind_challenge", "in_game", "his_walk")


def target_key(t, ctx):
    if t == "all":
        return "all"
    if t.startswith("item:"):
        return t
    if t.startswith("stage:"):
        s = t[6:]
        if s not in STAGES:
            near = difflib.get_close_matches(s, STAGES, n=3, cutoff=0.3)
            raise Refused("no stage %r; nearest: %s" % (s, ", ".join(near or STAGES)))
        return t
    if t.startswith("RIMMANDRAKE_") or t.startswith("RIMMASTER_"):
        return "item:" + t
    return "mod:" + mod_name(t.split(":", 1)[1] if t.startswith("mod:") else t, ctx)


def do_switch(ctx, on, t, why, owner_said=None):
    """`pipe on|off`: a switch in control.py's store (binds at once: every launch reads it at the moment it starts)."""
    import control as C
    k = target_key(t, ctx)
    try:
        r = C.switch(k, not on, why, owner_said=owner_said)
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)
    if on and not r["had"]:
        return ["%s is already ON (nothing switched; %s)" % (k, "the store holds no switch for it" if not r["still"]
                                                              else "still " + r["still"][0])]
    a = r["act"]
    return ["%s %s -> %s" % (k, r["before"], "ON" if on else "OFF"), "act %s rev %s at %s" % (a["id"], a["rev"],
                                                                                         a["at_pacific"]),
            "undo: pipe %s %s --why \"...\"" % ("off" if on else "on", t)]


def do_undo(act_id, why, owner_said=None):
    """`pipe undo <act>`: a control-store act (ct_...) is undone there (control.undo, a compensating act refused with
    the later acts it would break); a pc_ act is one of this journal's (the queue, until slice 3)."""
    if not str(act_id).startswith("pc_"):
        C = _C()
        try:
            r = C.undo(act_id, why, owner_said=owner_said)
        except C.Unreadable as e:
            raise Unreadable("the control store: %s" % e)
        if not r["ok"]:
            raise Refused(r["why"])
        return [r["line"], "act %s rev %s at %s" % (r["act"]["id"], r["act"]["rev"], r["act"]["at_pacific"]),
                "(an undo is itself an act: pipe log)"]
    js = journal()
    a = next((x for x in js if x.get("id") == act_id), None)
    if not a:
        near = difflib.get_close_matches(act_id, [x["id"] for x in js], n=3, cutoff=0.3)
        raise Refused("no act %r in the journal; nearest: %s (pipe log)" % (act_id, ", ".join(near) or "none"))
    b = act(a["sec"], a.get("name"), a.get("before"), why, "undo", owner_said, undoes=act_id)
    return ["%s %s: %s -> %s (undoes %s)" % (a["sec"], a.get("name") or "", _short(b["before"]), _short(b["after"]),
                                            act_id),
            "act %s at %s" % (b["id"], b["at_pacific"]), _undo_line(b)]


def _short(v):
    if isinstance(v, dict):
        return "OFF" if "why" in v else json.dumps(v)[:40]
    if v is None:
        return "none"
    return json.dumps(v)[:60] if isinstance(v, list) else str(v)


def do_log(n):
    """The acts of the one control store (control.log): counts, limits, switches, stops and voids live there now; the
    queue's journal acts follow, marked, while the queue still lives here (slice 3)."""
    C = _C()
    try:
        out = C.log(n)
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)
    q = [a for a in journal() if a.get("sec") == "queue"][-n:]
    return out + ["%s %s queue: %s -> %s  (%s)" % (a["id"], a.get("at_pacific", UNM), _short(a.get("before")),
                                                  _short(a.get("after")), a.get("why")) for a in q]


def do_show(ctx, mod=None):
    st = state()
    mods = [mod_name(mod, ctx)] if mod else ctx.mods()
    out = []
    import control as C     # the switches live in control.py's store
    try:
        sw = [r for r in C.switches() if r["layer"] == "control"]
    except C.Unreadable as e:
        raise Unreadable("the control store: %s" % e)
    if any(r["scope"] == "all" for r in sw):
        out.append("ALL " + off())
    try:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import mod_owner_hold as OH
        holds = OH.load(os.environ.get("RM_OWNER_HOLD_FILE") or OH.PATH)    # his own list; pipe's offs are below
    except Exception as e:      # noqa: BLE001  shown, never read as "no holds"
        holds = None
        out.append("owner hold list: %s (%s)" % (UNM, e))
    for m in mods:
        why = off(mod=m)
        onoff = "OFF" if why else "HELD" if holds and m in holds else "?" if holds is None else "ON"
        cells = []
        for res, (lab, doc, _f, _r) in RESOURCES.items():
            r = reading(ctx, m, res, st)
            if r is None:
                continue
            meas, u, lim, adjusted = r
            mark = "*" if adjusted or lim != RESOURCES[res][2](ctx, m)[1] else ""     # the store moved it
            if mod:
                cells.append("  %-21s %-9s %s (pipeline count %s)%s" % (res, _fmt(meas, u, lim), doc, meas,
                                                                      ", overridden" if mark else ""))
            else:
                cells.append("%s %s%s" % (lab, _fmt(meas, u, lim), mark))
        head = "%-20s %-16s %-4s" % (m, ctx.stage(m), onoff)
        if mod:
            out.append(head + ("  " + why if why else ""))
            out += cells
        else:
            out.append(head + "  " + "  ".join(cells))
    for r in sorted(sw, key=lambda r: r["scope"]):
        if r["scope"] != "all" and not r["scope"].startswith("mod:"):
            out.append("%s OFF: %s" % (r["scope"], r["why"]))
    try:    # the queue lives in control.py's store (slice review 18: this read the old journal's)
        out.append(C.cmd_queue(argparse.Namespace(op=None))[0])
    except (C.Unreadable, C.sqlite3.Error) as e:
        raise Unreadable("the control store: %s" % e)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pipe", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="verb", required=True)

    def why(p):
        p.add_argument("--why", required=True)
        p.add_argument("--owner-said")
        return p

    p = sub.add_parser("show")
    p.add_argument("mod", nargs="?")
    for v in ("set", "add"):
        p = why(sub.add_parser(v))
        p.add_argument("mod")
        p.add_argument("res")
        p.add_argument("n")
    p = why(sub.add_parser("reset"))
    p.add_argument("mod")
    p.add_argument("res")
    p = why(sub.add_parser("limit"))
    p.add_argument("mod")
    p.add_argument("res")
    p.add_argument("n")
    for v in ("on", "off"):
        p = why(sub.add_parser(v))
        p.add_argument("target")
    p = sub.add_parser("log")
    p.add_argument("-n", type=int, default=10)
    p = why(sub.add_parser("undo"))
    p.add_argument("act_id")
    a = ap.parse_args(argv)
    try:
        ctx = Ctx()
        if a.verb == "show":
            lines = do_show(ctx, a.mod)
        elif a.verb in ("set", "add"):
            try:
                n = int(a.n)
            except ValueError:
                raise Refused("%s needs a whole number, got %r" % (a.verb, a.n))
            lines = do_count(ctx, a.verb, a.mod, a.res, n, a.why, a.owner_said)
        elif a.verb == "reset":
            if a.res == "all":
                ms = mod_name(a.mod, ctx)
                lines = []
                for r in RESOURCES:
                    rd = reading(ctx, ms, r, None)
                    if rd and rd[1]:
                        lines.append(do_count(ctx, "reset", ms, r, 0, a.why, a.owner_said)[0])
                lines = lines[:2] + (["(%d more reset; pipe log)" % (len(lines) - 2)] if len(lines) > 2 else []) \
                    or ["%s: every consumable already reads 0" % ms]
            else:
                lines = do_count(ctx, "reset", a.mod, a.res, 0, a.why, a.owner_said)
        elif a.verb == "limit":
            if a.n != "default":
                try:
                    int(a.n)
                except ValueError:
                    raise Refused("limit needs a whole number or 'default', got %r" % a.n)
            lines = do_limit(ctx, a.mod, a.res, a.n, a.why, a.owner_said)
        elif a.verb in ("on", "off"):
            lines = do_switch(ctx, a.verb == "on", a.target, a.why, a.owner_said)
        elif a.verb == "log":
            lines = do_log(a.n)
        elif a.verb == "undo":
            lines = do_undo(a.act_id, a.why, a.owner_said)
    except Refused as e:
        print("pipe: refused: %s" % e)
        return 2
    except Unreadable as e:
        print("pipe: the control store cannot be read, so the pipeline launches NOTHING until it is repaired: %s" % e)
        return 3
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
