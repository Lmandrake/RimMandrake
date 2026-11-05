#!/usr/bin/env python3
"""metronome: Operations' one beat (OPS_METRONOME_PROVE_IN_SHADOW, OPS_METRONOME_MIGRATE_CLOCKS_FENCED; strategy §2
and §8 steps 5-6, design/RimMandrake/operations_metronome_strategy_2026-11-02.md).

One beat runs the phases of the table (src/RimMandrake/Utils/systemd/metronome_phases.json) in the fixed order
sense, remember, raise, ring, dispatch, chores. A phase is in SHADOW until the table gives it `owns`: its command
only reads, or writes into the state dir (ops_watch into its own store there, the Dispatcher's dry tick). Cutover
(step 6) moves one clock a day: the phase gets `owns` (the old timer, which is then disabled) and its real command,
which carries `{gen}`, its OWNERSHIP GENERATION: the program acts only while `may_act(phase, gen)` holds (the live
generation, not fenced), and a run of the old program with no generation refuses while `owner_of(timer)` names a
phase. So neither a killed child nor a run of the old timer that was already going can write over the owner.
`--shadow` on `beat` is accepted and changes nothing (the unit once passed it); ownership is the table's.

The rules that make "a crash is just the next beat" true, each a case in selftest_metronome.py:
  total budget   the table's budget_s (45) bounds the beat, not only each phase. The limits (+ cleanup) of the
                 reserved phases (raise, ring) due this beat are set aside first, then those of overdue phases
                 while they fit; any other phase whose limit would not fit beside that reserve is DEFERRED,
                 logged, and is due again next beat (state "overdue"), held in the reserve then, never squeezed.
  process group  each phase runs in its own session (setsid); past its limit the group gets SIGTERM, then after
                 cleanup_s SIGKILL; stragglers left in the group after a normal exit are killed too.
  generations    a beat's number is its generation. The beat publishes a phase's output (out/<phase>.json,
                 carrying gen and observed_at) only for a phase that exited 0 inside its limit; a child may publish
                 itself only while its generation is the live one. A killed phase's generation is FENCED
                 (fence/<phase>, the killed generations): `publish` refuses a fenced or superseded generation and
                 `read` a fenced one, so a child that escaped the kill cannot publish. An earlier good generation
                 stays readable; its age decides.
  single flight  a beat holds an flock on beat.lock; a second beat while one runs exits 75 and logs `duplicate`.
  crash          a beat that died mid-phase left `inflight` in state.json: the next beat kills that process
                 group, fences it, logs `beat_died` and runs the phase as overdue.
  operation ids  every act outside the program takes an id first (`op begin`, deterministic from kind+key), and
                 ends it after (`op end`). An id begun and never ended is `unresolved`: the caller looks for it
                 in the world (`op reconcile --found|--absent`), never just acts again.
  retry          a families phase killed or failed loses no family for a whole round: its families run again,
                 one a beat, before the round robin moves on; a retry that fails again is dropped (no stall).
  persistence    beat number, round-robin position, families to retry, overdue phases, wall-clock slots done (keyed "YYYY-MM-DDTHH:MM"
                 local, never by beat number) and last success per phase live in state.json, written whole.
  freshness      a phase's `reads` name the outputs it uses and the oldest age it accepts; an older (or missing,
                 or fenced) one makes the phase refuse that beat (`stale_input`), and the beat line names the
                 oldest reading used.
  useful work    `health` reads the age of each critical phase's last SUCCESSFUL run, not the heartbeat.

Every phase run, deferral, refusal and duplicate writes one line to beats.jsonl: beat, phase, start, seconds, exit,
and the hash of what it read.

Usage:
  metronome.py beat [--table P] [--dir D]
  metronome.py health [--dir D] [--table P]                  0 = every critical phase did useful work in time
  metronome.py read --phase P [--max-age S] [--dir D]        a published output, or exit 1 and why not
  metronome.py publish --phase P --gen G --file F [--dir D]  (children) refused unless G is the live generation
  metronome.py op begin|end|reconcile ...                    operation ids
  metronome.py lint [--table P]                              validate a phase table
State dir: --dir, else $RM_METRONOME_DIR, else D:\\ClaudeWork\\rimmandrake\\metronome\\shadow.
"""
import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TABLE = HERE / "systemd" / "metronome_phases.json"
ORDER = ("sense", "remember", "raise", "ring", "dispatch", "chores")
RESERVED = ("raise", "ring")
EXIT_DUPLICATE = 75


def state_dir(arg=None):
    return Path(arg or os.environ.get("RM_METRONOME_DIR") or "/mnt/d/ClaudeWork/rimmandrake/metronome/shadow")


# ---------------------------------------------------------------- files

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp%d" % os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def append_line(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


class Lock:
    def __init__(self, path, block=True):
        self.path, self.block, self.f = Path(path), block, None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(self.path, "a+")
        try:
            fcntl.flock(self.f, fcntl.LOCK_EX | (0 if self.block else fcntl.LOCK_NB))
        except OSError:
            self.f.close()
            raise
        return self

    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()


# ---------------------------------------------------------------- table

FAMILY_SOURCES = {"ops_watch.FAMILIES": ("ops_watch.py", "FAMILIES")}


def resolve_families(ref, here=None):
    """A phase's `families` named by reference ("ops_watch.FAMILIES") -> that tuple as a list, read from the module's
    source (no import). A hand-copied list drifted once: db682f0890 added `wrapup` to ops_watch and not here, and the
    nightly went red (NIGHTLY_COP_FIX_RED_APGIHI_JAKI); a reference cannot drift. Raises ValueError naming the gap."""
    import ast
    if ref not in FAMILY_SOURCES:
        raise ValueError("families reference %r unknown (known: %s)" % (ref, ", ".join(sorted(FAMILY_SOURCES))))
    fname, var = FAMILY_SOURCES[ref]
    try:
        tree = ast.parse((Path(here or HERE) / fname).read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as e:
        raise ValueError("families reference %r: cannot read %s (%s)" % (ref, fname, e))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == var:
            try:
                fams = list(ast.literal_eval(node.value))
            except ValueError:
                break
            if fams and all(isinstance(f, str) for f in fams):
                return fams
            break
    raise ValueError("families reference %r: %s holds no literal list of names %s" % (ref, fname, var))


def load_table(path=None):
    """The phase table, validated; raises ValueError naming what is wrong."""
    t = read_json(path or TABLE)
    if not isinstance(t, dict):
        raise ValueError("phase table %s missing or not an object" % (path or TABLE))
    b = t.get("budget_s")
    if not isinstance(b, (int, float)) or b <= 0:
        raise ValueError("budget_s must be a positive number")
    ph = t.get("phases")
    if not isinstance(ph, dict) or set(ph) != set(ORDER):
        raise ValueError("phases must be exactly %s" % ", ".join(ORDER))
    for name in ORDER:
        if isinstance(ph[name], dict) and isinstance(ph[name].get("families"), str):
            ph[name]["families"] = resolve_families(ph[name]["families"])
    for name in ORDER:
        p = ph[name]
        every, off = p.get("every"), p.get("offset", 0)
        if not isinstance(every, int) or every < 1 or not isinstance(off, int) or not 0 <= off < every:
            raise ValueError("%s: every must be an int >= 1 and 0 <= offset < every" % name)
        for k in ("limit_s", "cleanup_s"):
            if not isinstance(p.get(k), (int, float)) or p[k] <= 0:
                raise ValueError("%s: %s must be a positive number" % (name, k))
        if p.get("argv") is not None and not (isinstance(p["argv"], list) and p["argv"]
                                              and all(isinstance(a, str) for a in p["argv"])):
            raise ValueError("%s: argv must be a non-empty list of strings, or null (no shadow command)" % name)
        for src, age in (p.get("reads") or {}).items():
            if src not in ORDER or not isinstance(age, (int, float)) or age <= 0:
                raise ValueError("%s: reads must map a phase to a positive max age" % name)
        for s in p.get("slots") or []:
            datetime.strptime(s, "%H:%M")
        if p.get("families") is not None and (not p["families"] or not isinstance(p.get("per_beat"), int)
                                              or p["per_beat"] < 1):
            raise ValueError("%s: families needs a non-empty list and per_beat >= 1" % name)
        if p.get("owns") is not None:
            if not (isinstance(p["owns"], list) and p["owns"] and all(isinstance(x, str) and x.endswith(".timer")
                                                                     for x in p["owns"])):
                raise ValueError("%s: owns must be a non-empty list of the .timer units it replaced" % name)
            if not p.get("argv") or not any("{gen}" in a for a in p["argv"]) or "--no-file" in p["argv"]:
                raise ValueError("%s: an owning phase needs its real argv carrying {gen} (no --no-file)" % name)
        if p.get("critical") and not isinstance(p.get("max_ok_age_s"), (int, float)):
            raise ValueError("%s: a critical phase needs max_ok_age_s" % name)
    reserve = sum(ph[n]["limit_s"] + ph[n]["cleanup_s"] for n in RESERVED)
    if reserve > b:
        raise ValueError("reserved phases need %.1f s, more than the %.1f s budget" % (reserve, b))
    for name in ORDER:
        if name not in RESERVED and ph[name]["limit_s"] + ph[name]["cleanup_s"] + reserve > b:
            raise ValueError("%s can never fit: its %.1f s beside the %.1f s reserve exceeds the %.1f s budget"
                             % (name, ph[name]["limit_s"] + ph[name]["cleanup_s"], reserve, b))
    return t


# ---------------------------------------------------------------- state, slots

def new_state():
    return {"beat": 0, "generation": 0, "rr": 0, "fam_retry": {}, "overdue": [], "slots_done": {}, "last_ok": {},
            "last_run": {}, "inflight": None}


def load_state(d):
    st = read_json(d / "state.json")
    if st is None:
        return new_state()
    if not isinstance(st, dict) or not isinstance(st.get("beat"), int):
        raise SystemExit("metronome: %s is unreadable: refusing to restart the beat count" % (d / "state.json"))
    for k, v in new_state().items():
        st.setdefault(k, v)
    return st


def slot_due(slots, max_late_min, now, done):
    """(due_key, missed_keys): the earliest wall-clock slot (today or yesterday, local) at or before now and not
    done; one later than max_late_min is MISSED (reported, never silently dropped)."""
    due, missed = None, []
    base = datetime.fromtimestamp(now)
    cands = []
    for day in (base - timedelta(days=1), base):
        for s in slots:
            hh, mm = map(int, s.split(":"))
            at = day.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if at.timestamp() <= now:
                cands.append((at.timestamp(), at.strftime("%Y-%m-%dT%H:%M")))
    for at, key in sorted(cands):
        if key in done:
            continue
        if now - at > max_late_min * 60:
            missed.append(key)
        elif due is None:
            due = key
    return due, missed


# ---------------------------------------------------------------- outputs, generations

def fenced(d, phase):
    """The generations of this phase that were killed (or whose beat died): none of them may publish or be read."""
    try:
        return {int(x) for x in (d / "fence" / phase).read_text().split()}
    except FileNotFoundError:
        return set()


def set_fence(d, phase, gen):
    with Lock(d / "publish.lock"):
        keep = sorted(fenced(d, phase) | {gen})[-200:]
        (d / "fence").mkdir(parents=True, exist_ok=True)
        tmp = d / "fence" / (phase + ".tmp")
        tmp.write_text("\n".join(map(str, keep)) + "\n")
        os.replace(tmp, d / "fence" / phase)


def publish(d, phase, gen, payload, observed_at):
    """(ok, why). Refused for a fenced generation or one a newer beat has superseded."""
    with Lock(d / "publish.lock"):
        live = load_state(d).get("generation", 0)
        if gen in fenced(d, phase):
            return False, "generation %d of %s is fenced (killed)" % (gen, phase)
        if gen < live:
            return False, "generation %d is superseded by %d" % (gen, live)
        cur = read_json(d / "out" / ("%s.json" % phase)) or {}
        if cur.get("gen", 0) > gen:
            return False, "a newer generation %d is already published" % cur["gen"]
        write_json(d / "out" / ("%s.json" % phase),
                   {"phase": phase, "gen": gen, "observed_at": observed_at, "published": time.time(),
                    "payload": payload})
        return True, "published"


def may_act(d, phase, gen):
    """(ok, why): an owning phase's child acts only while its generation is the live one and not fenced."""
    with Lock(d / "publish.lock"):
        live = load_state(d).get("generation", 0)
        if gen in fenced(d, phase):
            return False, "generation %d of %s is fenced (killed)" % (gen, phase)
        if gen != live:
            return False, "generation %d of %s is not the live generation %d" % (gen, phase, live)
        return True, "live"


def owner_of(timer, table_path=None):
    """The phase of the phase table that owns this old timer, or None. An unreadable table owns nothing, and says
    so on stderr: the old timer is disabled at cutover, so this is the second fence, not the first."""
    try:
        t = read_json(table_path or TABLE)
        for name, p in (t.get("phases") or {}).items():
            if timer in (p.get("owns") or []):
                return name
    except Exception as e:  # noqa: BLE001
        print("metronome: phase table unreadable (%s): no owner known" % e, file=sys.stderr)
    return None


def read_output(d, phase, max_age=None, now=None):
    """(record, why): None and the reason for a missing, fenced or too-old output."""
    rec = read_json(d / "out" / ("%s.json" % phase))
    if not isinstance(rec, dict):
        return None, "%s: nothing published" % phase
    if rec.get("gen", 0) in fenced(d, phase):
        return None, "%s: generation %s is fenced" % (phase, rec.get("gen"))
    age = (now or time.time()) - float(rec.get("observed_at") or 0)
    if max_age is not None and age > max_age:
        return None, "%s: observed %.0f s ago, older than %.0f s" % (phase, age, max_age)
    return rec, "ok"


# ---------------------------------------------------------------- operation ids

def op_id(kind, key):
    return hashlib.sha256(("%s|%s" % (kind, key)).encode()).hexdigest()[:16]


def _op_last(d, oid):
    last = None
    p = d / "ops.jsonl"
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("op") == oid:
                last = r
    return last


def op_begin(d, kind, key, beat=None, shadow=True):
    """('do'|'done'|'unresolved', id). 'do' is written BEFORE the act; only 'do' may act."""
    oid = op_id(kind, key)
    with Lock(d / "ops.lock"):
        last = _op_last(d, oid)
        if last and last["state"] in ("end", "found"):
            return "done", oid
        if last and last["state"] == "begin":
            return "unresolved", oid
        append_line(d / "ops.jsonl", {"op": oid, "kind": kind, "key": key, "state": "begin", "beat": beat,
                                      "shadow": shadow, "at": time.time()})
        return "do", oid


def op_end(d, oid, result="ok"):
    with Lock(d / "ops.lock"):
        last = _op_last(d, oid)
        if not last or last["state"] != "begin":
            raise ValueError("op %s is not begun (%s)" % (oid, last and last["state"]))
        append_line(d / "ops.jsonl", {"op": oid, "state": "end", "result": result, "at": time.time()})


def op_reconcile(d, oid, found):
    """An unresolved id looked up in the world: found -> done, absent -> may be begun again."""
    with Lock(d / "ops.lock"):
        last = _op_last(d, oid)
        if not last or last["state"] != "begin":
            raise ValueError("op %s is not unresolved" % oid)
        append_line(d / "ops.jsonl", {"op": oid, "state": "found" if found else "absent", "at": time.time()})


# ---------------------------------------------------------------- process groups

def _group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def kill_group(pgid, cleanup_s, proc=None):
    """SIGTERM the group, wait up to cleanup_s, then SIGKILL. Returns how it ended."""
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return "gone"
    end = time.monotonic() + cleanup_s
    while time.monotonic() < end:
        if proc is not None:
            proc.poll()
        if not _group_alive(pgid):
            return "killed_term"
        time.sleep(0.05)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        return "killed_term"
    end = time.monotonic() + 2.0
    while time.monotonic() < end:
        if proc is not None:
            proc.poll()
        if not _group_alive(pgid):
            return "killed_kill"
        time.sleep(0.05)
    return "unreaped"


# ---------------------------------------------------------------- the beat

def _expand(s, ctx):
    for k, v in ctx.items():
        s = s.replace("{%s}" % k, v)
    return s


def _due(name, p, n, st, now):
    if name in st["overdue"]:
        return True, None, []
    slot, missed = (None, [])
    if p.get("slots"):
        slot, missed = slot_due(p["slots"], p.get("max_late_min", 120), now, set(st["slots_done"].get(name, [])))
    return (n % p["every"] == p.get("offset", 0)) or slot is not None, slot, missed


def run_phase(d, table, name, n, st, limit, slot, log):
    p = table["phases"][name]
    out = d / "out"
    out.mkdir(parents=True, exist_ok=True)
    start = time.time()
    line = {"beat": n, "gen": n, "phase": name, "start": round(start, 3), "shadow": not p.get("owns")}
    if slot:
        line["slot"] = slot
    # freshness: what this phase reads, and the oldest of it
    read_bytes, oldest = [], None
    for src, max_age in sorted((p.get("reads") or {}).items()):
        rec, why = read_output(d, src, max_age, now=start)
        if rec is None:
            line.update(seconds=0.0, exit="stale_input", why=why)
            log(line)
            return "stale_input"
        read_bytes.append(json.dumps(rec, sort_keys=True).encode())
        if oldest is None or rec["observed_at"] < oldest[1]:
            oldest = (src, rec["observed_at"])
    line["read_hash"] = hashlib.sha256(b"\0".join(read_bytes)).hexdigest()[:16]
    if oldest:
        line["oldest_reading"] = {"phase": oldest[0], "observed_at": oldest[1]}
    if p.get("argv") is None:
        line.update(seconds=0.0, exit="no_command", why=p.get("why_no_command", "no shadow command"))
        log(line)
        return "no_command"
    fams, retry = [], []
    if p.get("families"):
        f = p["families"]
        retry = [x for x in (st["fam_retry"].get(name) or []) if x in f]
        if retry:                       # a killed pass's families, one a beat, before the round moves on
            fams = retry[:1]
            line["retry"] = True
        else:
            fams = [f[(st["rr"] + i) % len(f)] for i in range(min(p["per_beat"], len(f)))]
        line["families"] = fams
    ctx = {"python": sys.executable, "repo": str(REPO), "state": str(d), "gen": str(n)}
    argv = []
    for a in p["argv"]:
        if a == "{families}":
            for fam in fams:
                argv += ["--family", fam]
        else:
            argv.append(_expand(a, ctx))
    env = dict(os.environ)
    for k, v in {**(table.get("env") or {}), **(p.get("env") or {})}.items():
        env[k] = _expand(v, ctx)
    staged = out / ("%s.%d.staged" % (name, n))
    env.update(METRONOME_DIR=str(d), METRONOME_GEN=str(n), METRONOME_PHASE=name, METRONOME_OUT=str(staged),
               METRONOME_SHADOW="0" if p.get("owns") else "1", METRONOME_OLDEST_READING=str(oldest[1]) if oldest else "",
               METRONOME_DEADLINE="%.3f" % (start + limit))   # when the kill comes: an acting child stops starting acts before it
    if slot:
        env["METRONOME_SLOT"] = slot
    logf = open(out / ("%s.log" % name), "w", encoding="utf-8")
    try:
        proc = subprocess.Popen(argv, cwd=str(REPO), env=env, stdout=logf, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, start_new_session=True)
    except OSError as e:
        logf.close()
        line.update(seconds=round(time.time() - start, 3), exit="spawn_failed", why=str(e))
        log(line)
        return "spawn_failed"
    st["inflight"] = {"beat": n, "phase": name, "pgid": proc.pid, "start": start}
    write_json(d / "state.json", st)
    try:
        rc = proc.wait(timeout=limit)
        if _group_alive(proc.pid):          # the leader exited; its group may not have
            line["stragglers"] = kill_group(proc.pid, p["cleanup_s"])
    except subprocess.TimeoutExpired:
        line["killed"] = kill_group(proc.pid, p["cleanup_s"], proc)
        proc.poll()
        set_fence(d, name, n)
        rc = "overrun"
    logf.close()
    end = time.time()
    line.update(seconds=round(end - start, 3), exit=rc)
    if rc == 0:
        payload, observed = None, start
        sj = read_json(staged) if staged.exists() else None
        if isinstance(sj, dict):
            payload, observed = sj.get("payload"), float(sj.get("observed_at") or start)
        else:
            tail = (out / ("%s.log" % name)).read_text(encoding="utf-8", errors="replace")[-2000:]
            payload = {"log_tail": tail}
        okp, why = publish(d, name, n, payload, observed)
        line["published"] = okp if okp else why
        st["last_ok"][name] = end
        if slot:
            st["slots_done"].setdefault(name, []).append(slot)
            st["slots_done"][name] = st["slots_done"][name][-50:]
    for leftover in out.glob("%s.*.staged" % name):
        leftover.unlink()
    if retry:                           # tried once more, whatever came of it: a slow family never stalls the round
        st["fam_retry"][name] = retry[1:]
    elif fams:
        st["rr"] = (st["rr"] + len(fams)) % len(p["families"])
        st["fam_retry"][name] = list(fams) if rc != 0 else []
    st["last_run"][name] = end
    st["inflight"] = None
    write_json(d / "state.json", st)
    log(line)
    return rc


def beat(d, table, shadow=True):
    """One beat. Returns 0, or EXIT_DUPLICATE when another beat holds the lock. `shadow` is kept for old callers
    and changes nothing: which phases act is the table's `owns`."""
    d.mkdir(parents=True, exist_ok=True)
    beats = d / "beats.jsonl"

    def log(obj):
        append_line(beats, obj)

    try:
        lk = Lock(d / "beat.lock", block=False).__enter__()
    except BlockingIOError:
        log({"beat": None, "phase": "*", "start": round(time.time(), 3), "seconds": 0.0, "exit": "duplicate",
             "why": "another beat holds beat.lock"})
        print("metronome: another beat is running")
        return EXIT_DUPLICATE
    try:
        st = load_state(d)
        inf = st.get("inflight")
        if inf:                                  # the last beat died mid-phase: a crash is just the next beat
            ended = kill_group(inf["pgid"], table["phases"][inf["phase"]]["cleanup_s"]) \
                if _group_alive(inf["pgid"]) else "gone"
            set_fence(d, inf["phase"], inf["beat"])
            log({"beat": inf["beat"], "gen": inf["beat"], "phase": inf["phase"], "start": inf["start"],
                 "seconds": None, "exit": "beat_died", "orphan": ended})
            if inf["phase"] not in st["overdue"]:
                st["overdue"].append(inf["phase"])
            st["inflight"] = None
        n = st["beat"] + 1
        st["beat"] = st["generation"] = n
        write_json(d / "state.json", st)        # the generation is live before any phase runs
        t0 = time.monotonic()
        deadline = t0 + table["budget_s"]
        now = time.time()
        due = {}
        for name in ORDER:
            p = table["phases"][name]
            isdue, slot, missed = _due(name, p, n, st, now)
            for key in missed:
                log({"beat": n, "phase": name, "start": round(now, 3), "seconds": 0.0, "exit": "slot_missed",
                     "slot": key})
                st["slots_done"].setdefault(name, []).append(key)
            if isdue:
                due[name] = slot
        cost = {k: table["phases"][k]["limit_s"] + table["phases"][k]["cleanup_s"] for k in ORDER}
        # reserved first: raise and ring, then each overdue phase in order while it fits, so a deferred phase
        # cannot starve behind phases that are due every beat
        held = [k for k in RESERVED if k in due]
        owed = sum(cost[k] for k in held)
        for k in ORDER:
            if k in due and k in st["overdue"] and k not in held and owed + cost[k] <= table["budget_s"]:
                held.append(k)
                owed += cost[k]
        for name in ORDER:
            if name not in due:
                continue
            p = table["phases"][name]
            left = deadline - time.monotonic()
            if name in held:
                owed -= cost[name]
                limit = max(0.5, min(p["limit_s"], left - p["cleanup_s"] - owed))
            else:
                if cost[name] > left - owed:
                    log({"beat": n, "phase": name, "start": round(time.time(), 3), "seconds": 0.0,
                         "exit": "deferred", "why": "needs %.1f s, %.1f s left beside %.1f s reserved"
                         % (cost[name], left - owed, owed)})
                    if name not in st["overdue"]:
                        st["overdue"].append(name)
                    continue
                limit = p["limit_s"]
            if name in st["overdue"]:
                st["overdue"].remove(name)
            run_phase(d, table, name, n, st, limit, due[name], log)
        write_json(d / "state.json", st)
        return 0
    finally:
        lk.__exit__()


def health(d, table, now=None):
    """(ok, lines): each critical phase's last successful run against its allowance."""
    now = now or time.time()
    st = load_state(d)
    ok, lines = True, []
    for name in ORDER:
        p = table["phases"][name]
        if not p.get("critical"):
            continue
        last = st["last_ok"].get(name)
        if last is None:
            ok = False
            lines.append("%s: UNMEASURED (no successful run on record)" % name)
            continue
        age = now - last
        good = age <= p["max_ok_age_s"]
        ok &= good
        lines.append("%s: last success %.0f s ago (allowed %.0f) %s" % (name, age, p["max_ok_age_s"],
                                                                         "ok" if good else "DEAD"))
    return ok, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("beat")
    b.add_argument("--shadow", action="store_true")
    for s in (b, sub.add_parser("health"), sub.add_parser("lint")):
        s.add_argument("--table")
        s.add_argument("--dir")
    r = sub.add_parser("read")
    r.add_argument("--phase", required=True, choices=ORDER)
    r.add_argument("--max-age", type=float)
    r.add_argument("--dir")
    pb = sub.add_parser("publish")
    pb.add_argument("--phase", required=True, choices=ORDER)
    pb.add_argument("--gen", required=True, type=int)
    pb.add_argument("--file", required=True, help="JSON {payload, observed_at}")
    pb.add_argument("--dir")
    op = sub.add_parser("op")
    op.add_argument("action", choices=["begin", "end", "reconcile"])
    op.add_argument("--kind")
    op.add_argument("--key")
    op.add_argument("--id")
    op.add_argument("--result", default="ok")
    g = op.add_mutually_exclusive_group()
    g.add_argument("--found", action="store_true")
    g.add_argument("--absent", action="store_true")
    op.add_argument("--dir")
    a = ap.parse_args(argv)
    d = state_dir(a.dir)
    if a.cmd in ("beat", "health", "lint"):
        try:
            table = load_table(a.table)
        except ValueError as e:
            print("metronome: bad phase table: %s" % e, file=sys.stderr)
            return 2
        if a.cmd == "lint":
            print("metronome: table ok, budget %.0f s" % table["budget_s"])
            return 0
        if a.cmd == "beat":
            return beat(d, table, shadow=a.shadow)
        ok, lines = health(d, table)
        print("\n".join(lines))
        return 0 if ok else 1
    if a.cmd == "read":
        rec, why = read_output(d, a.phase, a.max_age)
        print(json.dumps(rec, sort_keys=True) if rec else why)
        return 0 if rec else 1
    if a.cmd == "publish":
        sj = read_json(a.file) or {}
        okp, why = publish(d, a.phase, a.gen, sj.get("payload"), float(sj.get("observed_at") or time.time()))
        print(why)
        return 0 if okp else 1
    if a.action == "begin":
        if not (a.kind and a.key):
            ap.error("op begin needs --kind and --key")
        state, oid = op_begin(d, a.kind, a.key)
        print("%s %s" % (state, oid))
        return {"do": 0, "done": 3, "unresolved": 4}[state]
    if not a.id:
        ap.error("op %s needs --id" % a.action)
    try:
        if a.action == "end":
            op_end(d, a.id, a.result)
        else:
            if not (a.found or a.absent):
                ap.error("op reconcile needs --found or --absent")
            op_reconcile(d, a.id, a.found)
    except ValueError as e:
        print("metronome: %s" % e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
