#!/usr/bin/env python3
"""run_alive.py: a detached run's sign of life and its mod lease come from the running process, not from the agent's hand
(RIMMANDRAKE_TIE_LIFE_SIGN_TO_PROCESS_484_HAND_NOTES; page design/specs/2026-11-23-run-alive/boundary.md).

    run_alive.py beat            one look at every live run (rm-run-alive.timer, every 5 min). exit 0 looked, 1 could not
    run_alive.py beat --dry      decide and print; renew nothing, write nothing
    run_alive.py show            the last reading

It launches nothing, stops nothing, files nothing and writes no rimflow note. It renews a live run's mod lease with the
run's own writer and token, in the run's own clone, and keeps `<unit>.alive.json` beside the run record.
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
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import detached_helper as DH  # noqa: E402
import modledger  # noqa: E402
import spend_talk  # noqa: E402

BEAT_S = 1200       # the page's LIMITS name each number's danger
# budget: danger=a hung run keeps its lease; ends no work: the silence bound of a progress guard, above the longest call that
# budget: the harness allows (7200 s): the lease is not renewed
SILENCE_S = 7500
# budget: danger=a brief with no renewal lines while no program renews; ends no work: the reading says that the timer is not
# budget: live
LIVE_S = 3600
# budget: danger=a young run reads as gone; ends no work: the run reads blind, not gone
START_S = 120
CMD_S = 300  # budget: class=rimflow
TAIL = 1 << 20      # the last message is looked for in the last MB first, then in the whole file: speed, not a cut
SHELL_MARK = "/shell-snapshots/"
DEAD = DH.DEAD_STATES
ENDED = {"argv": [], "ppid": 0}     # a process that ended, reaped or not, has no command line


class CouldNotLook(Exception):
    """A fact could not be read; its text is the cause."""


# ---- the decision ------------------------------------------------------------------------------------------------

def decide(f, beat_s=BEAT_S, silence_s=SILENCE_S):
    """-> {"act": "renew"|"wait"|"lapse"|"blind", "why"}. The facts are the acceptance script's contract. Pure."""
    def out(act, why):
        return {"act": act, "why": why}
    st = f.get("unit_state")
    if st == "remote":
        return out("blind", "could not look: it runs on %s, not on this machine" % f.get("host"))
    if st == "inactive":
        return out("lapse", "gone: its unit is not running")
    if st != "active":
        return out("blind", "could not look: the unit's state could not be read (%s)" % st)
    if f.get("proc_alive") is None:
        return out("blind", "could not look: the run's process could not be read")
    if not f["proc_alive"]:
        return out("lapse", "gone: its unit is up and its claude process is not")
    silent = f.get("silent_s")
    if silent is None:
        return out("blind", "could not look: its transcript could not be read")
    said = "alive: its transcript grew %d s ago" % silent
    if silent > silence_s:
        if f.get("child_running") is None:
            return out("blind", "could not look: silent %d s, and whether it runs a command could not be read" % silent)
        if not f["child_running"]:
            return out("lapse", "hung: silent %d s (past %d s) with no command running" % (silent, silence_s))
        said = "alive: silent %d s, and its command runs (a long wait)" % silent
    since = f.get("since_beat_s")
    if since is not None and since < beat_s:
        return out("wait", "%s; the last beat was %d s ago" % (said, since))
    return out("renew", said)


# ---- the line ----------------------------------------------------------------------------------------------------

def _flat(text):
    return " ".join(spend_talk.strip(text).split())


def line(unit, last_text, commits, now):
    """-> "ALIVE: ..." from the run's own last message ("" = looked, none; None = could not look) and its commits (a list
    of "<sha> <subject>"; None = could not look). The run's words, less any spend sentence; no judgement of its own."""
    if last_text is None:
        msg = "its last message: could not look"
    elif not last_text.strip():
        msg = "no message yet (looked)"
    else:
        msg = _flat(last_text)
        msg = 'its last message: "%s"' % msg if msg else "its last message held only words this line does not carry"
    if commits is None:
        com = "its commits: could not look"
    elif not commits:
        com = "its commits: none (looked)"
    else:
        com = "its commits: " + "; ".join(_flat(c) or c.split(" ")[0] for c in commits)
    return "ALIVE: %s at %s. %s. %s" % (unit, time.strftime("%Y-%m-%d %-I:%M %p %Z", time.localtime(now)), msg, com)


# ---- the lease ---------------------------------------------------------------------------------------------------

def lease_env(rec):
    env = rec.get("env") if isinstance(rec.get("env"), dict) else {}
    w, t = env.get("RM_MODLEDGER_WRITER") or "", env.get("RM_MODLEDGER_TOKEN") or ""
    return (w, t) if w.startswith("HOLDER.") and t else (None, None)


def mod_of(rec):
    """-> the mod of the run's lease: RM_CONTROL_MOD, else the one mod of its clone whose DISPATCH shard grants the lease;
    None when no shard or more than one does."""
    env = rec.get("env") if isinstance(rec.get("env"), dict) else {}
    if env.get("RM_CONTROL_MOD"):
        return env["RM_CONTROL_MOD"]
    w, _ = lease_env(rec)
    hits = set()
    for p in glob.glob(os.path.join(rec.get("clone") or "", "design", "concepts", "*", "ledger", "DISPATCH.jsonl")):
        with open(p, encoding="utf-8", errors="replace") as fh:
            for e in _events(fh.read()):
                if e.get("kind") == "lease.grant" and "HOLDER.%s" % (e.get("body") or {}).get("lease") == w:
                    hits.add(e.get("mod"))
    return hits.pop() if w and len(hits) == 1 else None


def renew(rec, append):
    """-> "renewed" | "no lease" | "refused: <why>". append(mod, writer, token) is called once, for a run with a lease."""
    w, t = lease_env(rec)
    if not w:
        return "no lease"
    try:
        mod = mod_of(rec)
        if not mod:
            return "refused: the run's env names a lease and no mod, and no one shard of its clone grants %s" % w
        append(mod, w, t)
    except Exception as e:  # noqa: BLE001  any raise is a refusal with its cause, never a renewal
        return "refused: %s" % (str(e).strip() or type(e).__name__)
    return "renewed"


def _events(text):
    out = []
    for ln in (text or "").splitlines():
        try:
            e = json.loads(ln)
        except ValueError:
            continue
        if isinstance(e, dict):
            out.append(e)
    return out


def origin_dispatch(mod, runner=subprocess.run, repo=REPO):
    """-> the DISPATCH events of `mod` on origin/main (fetched first; an unreachable origin leaves the last fetch).
    CouldNotLook when git cannot give them."""
    rel = "design/concepts/%s/ledger/DISPATCH.jsonl" % mod
    try:
        runner(["git", "-C", repo, "fetch", "-q", "origin", "main"], capture_output=True, text=True, timeout=CMD_S,
               stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        r = runner(["git", "-C", repo, "show", "origin/main:" + rel], capture_output=True, text=True, timeout=CMD_S,
                   stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        raise CouldNotLook("could not read origin's leases of %s: %s" % (mod, e))
    if r.returncode:
        raise CouldNotLook("could not read origin's leases of %s: %s" % (mod, (r.stderr or "").strip()))
    return _events(r.stdout)


def fence_check(origin_events, clone_events, writer, token):
    """Raise when another lease stands above this one, or DISPATCH revoked it, on origin/main or in the clone. Pure."""
    lease = modledger.writer_suffix(writer)
    seen, evs = set(), []
    for e in list(clone_events) + list(origin_events):
        k = e.get("id") or json.dumps(e, sort_keys=True, default=str)
        if k not in seen:
            seen.add(k)
            evs.append(e)
    by, cur = modledger.leases(evs)
    g = by.get(lease)
    if g is None:
        raise modledger.ModLedgerError("lease %r was never granted (looked on origin/main and in the clone)" % lease)
    if str(g["token"]) != str(token):
        raise modledger.ModLedgerError("stale token %s: lease %r holds token %d" % (token, lease, g["token"]))
    if cur != lease:
        raise modledger.ModLedgerError("stale token %s: lease %r has fenced lease %r" % (token, cur, lease))
    if g["released"]:
        raise modledger.ModLedgerError("lease %r was released" % lease)


def clone_append(rec, runner=subprocess.run, repo=REPO):
    """-> append(mod, writer, token): the run's own clone's `modledger.py append`, as its agent ran it by hand, after the
    fence on origin/main is read. Raises with the cause when it did not write."""
    def go(mod, writer, token):
        clone = rec.get("clone") or ""
        tool = os.path.join(clone, "src", "RimMandrake", "rimflow", "modledger.py")
        if not os.path.isfile(tool):
            raise CouldNotLook("the run's clone holds no modledger.py: %s" % clone)
        fence_check(origin_dispatch(mod, runner, repo), modledger.read(clone, mod), writer, token)
        env = dict({k: v for k, v in os.environ.items() if k != "RM_MODLEDGER_ROOT"}, RM_MODLEDGER_WRITER=writer)
        r = runner([sys.executable or "python3", tool, "append", "--mod", mod, "--writer", writer, "--token", str(token),
                    "--kind", "lease.renew", "--subject", "lease"], cwd=clone, env=env, capture_output=True, text=True,
                   timeout=CMD_S, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise modledger.ModLedgerError("%s" % (((r.stderr or "") + (r.stdout or "")).strip() or
                                                   "modledger append exit %d" % r.returncode))
    return go


# ---- the facts ---------------------------------------------------------------------------------------------------

def unit_fact(state):
    """systemd's ActiveState -> the contract's word. An ending unit is read by its process."""
    if state in DEAD:
        return "inactive"
    return "active" if state in ("active", "activating", "reloading", "deactivating") else "unknown"


def cgroup_pids(unit, runner=subprocess.run, fs="/sys/fs/cgroup"):
    """-> the pids in the unit's control group and the groups below it; [] when it has none. CouldNotLook when systemd or
    the folder cannot be read."""
    try:
        r = runner(["systemctl", "--user", "show", "-p", "ControlGroup", "--value", unit], capture_output=True, text=True,
                   timeout=CMD_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        raise CouldNotLook("systemctl show %s: %s" % (unit, e))
    if r.returncode:
        raise CouldNotLook("systemctl show %s: %s" % (unit, (r.stderr or "").strip()))
    cg = (r.stdout or "").strip()
    if not cg:
        return []
    out = []

    def bad(e):
        if not isinstance(e, FileNotFoundError):    # a group that ended while it was read holds no process
            raise CouldNotLook("control group of %s: %s" % (unit, e))
    for d, _, names in os.walk(fs + cg, onerror=bad):
        if "cgroup.procs" not in names:
            continue
        try:
            with open(os.path.join(d, "cgroup.procs"), encoding="ascii") as fh:
                out += [int(x) for x in fh.read().split()]
        except FileNotFoundError:
            continue
        except OSError as e:
            if e.errno == 19:       # ENODEV: the group was removed under the read
                continue
            raise CouldNotLook("control group of %s: %s" % (unit, e))
    return out


def read_proc(pid, proc="/proc"):
    """-> {"argv", "ppid"}; ENDED when the process ended. CouldNotLook when it cannot be read."""
    try:
        with open("%s/%d/cmdline" % (proc, pid), "rb") as fh:
            argv = [a.decode("utf-8", "replace") for a in fh.read().split(b"\0") if a]
        with open("%s/%d/stat" % (proc, pid), encoding="utf-8", errors="replace") as fh:
            rest = fh.read().rsplit(")", 1)[1].split()
        return {"argv": argv, "ppid": int(rest[1])}
    except (FileNotFoundError, ProcessLookupError):
        return ENDED
    except (OSError, ValueError, IndexError) as e:
        raise CouldNotLook("process %d: %s" % (pid, e))


def process_facts(procs):
    """{pid: read_proc's dict} of the run's groups -> (proc_alive, child_running). The run's claude is the one that has no
    claude above it; its command is a descendant shell that names a Claude shell snapshot. A process that ended unreaped has no command line. Pure."""
    def above(p):
        seen = set()
        p = procs[p]["ppid"]
        while p in procs and p not in seen:
            seen.add(p)
            yield p
            p = procs[p]["ppid"]
    claudes = {p for p, d in procs.items() if d["argv"] and os.path.basename(d["argv"][0]) == "claude"}
    tops = {p for p in claudes if not claudes.intersection(above(p))}
    if not tops:
        return False, None
    child = any(any(SHELL_MARK in a for a in d["argv"]) and tops.intersection(above(p)) for p, d in procs.items())
    return True, child


def transcript(rec, projects=None):
    """-> the run's own session transcript: the session it resumes when that one was written in this run, else the first
    one begun in its clone's project folder since the launch. CouldNotLook when there is none."""
    d = DH.project_dir(rec.get("clone") or "", projects)
    at = rec.get("at") or 0
    hits = []
    for p in glob.glob(os.path.join(d, "*.jsonl")):
        try:
            if os.path.getmtime(p) >= at:
                hits.append(p)
        except OSError:
            continue
    if not hits:
        raise CouldNotLook("no transcript in %s written since the launch" % d)
    for p in hits:
        if rec.get("resume_session") and os.path.basename(p) == rec["resume_session"] + ".jsonl":
            return p
    return min(hits, key=lambda p: (_begun(p), p))


def _begun(path):
    """The ISO time of the transcript's first dated line, as text; one with none sorts last."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for i, ln in enumerate(fh):
                m = re.search(r'"timestamp"\s*:\s*"([^"]+)"', ln)
                if m:
                    return m.group(1)
                if i > 200:
                    break
    except OSError:
        pass
    return "~"


def silence(path, now):
    """-> seconds since the transcript, or a subagent's transcript under its session folder, grew."""
    try:
        times = [os.path.getmtime(path)]
    except OSError as e:
        raise CouldNotLook("transcript: %s" % e)
    for p in glob.glob(os.path.join(path[:-len(".jsonl")], "**", "*.jsonl"), recursive=True):
        try:
            times.append(os.path.getmtime(p))
        except OSError:
            continue
    return max(0.0, now - max(times))


def _last_in(text):
    for ln in reversed(text.splitlines()):
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(r, dict) or r.get("type") != "assistant" or r.get("isSidechain"):
            continue
        content = (r.get("message") or {}).get("content")
        parts = [c["text"] for c in content or [] if isinstance(c, dict) and c.get("type") == "text" and c.get("text")] \
            if isinstance(content, list) else []
        if parts:
            return "\n".join(parts)
    return None


def last_message(path):
    """-> the run's last message; "" when the transcript was read and holds none. CouldNotLook when it cannot be read."""
    try:
        with open(path, "rb") as fh:
            size = os.fstat(fh.fileno()).st_size
            fh.seek(max(0, size - TAIL))
            got = _last_in(fh.read().decode("utf-8", "replace"))
            if got is None and size > TAIL:
                fh.seek(0)
                got = _last_in(fh.read().decode("utf-8", "replace"))
    except OSError as e:
        raise CouldNotLook("transcript: %s" % e)
    return got or ""


def commits_of(rec, runner=subprocess.run):
    """-> ["<sha> <subject>", ...] the commits since the launch, in the run's clone, that name its item, newest first; the
    ledger's own lines (`ledger: ...`) are left out. CouldNotLook when git cannot say."""
    try:
        r = runner(["git", "-C", rec.get("clone") or "", "log", "HEAD", "origin/main", "--since=@%d" % int(rec.get("at") or 0),
                    "--format=%h %s", "--fixed-strings", "--grep=" + rec["item"]], capture_output=True, text=True,
                   timeout=CMD_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        raise CouldNotLook("git log: %s" % e)
    if r.returncode:
        raise CouldNotLook("git log: %s" % (r.stderr or "").strip())
    return [ln for ln in (r.stdout or "").splitlines() if ln.strip() and not ln.split(" ", 1)[-1].startswith("ledger:")]


def _try(fn, *a):
    """-> (value, None), or (None, cause) when it could not look."""
    try:
        return fn(*a), None
    except CouldNotLook as e:
        return None, str(e)


def facts(rec, now, prev=None, runner=subprocess.run, projects=None):
    """-> (decide()'s facts, {fact: why it could not be read}, the transcript's path or None)."""
    import role_launch as RL
    import run_host
    import socket
    door = run_host.door(rec.get("host"))
    if door and run_host._norm(rec.get("host")) != socket.gethostname().strip().lower():    # its unit, its /proc and its transcript are that machine's; this machine's systemd says inactive for it
        f = {"unit_state": "remote", "host": rec["host"], "proc_alive": None, "silent_s": None, "child_running": None,
             "since_beat_s": None}
        return f, {"host": "read it there: ssh %s 'cd ~/rm/bench && python3 src/RimMandrake/rimflow/detached_helper.py "
                           "status'" % door}, None
    blind = {}
    f = {"unit_state": unit_fact(RL.unit_state(rec["unit"], runner=runner)), "proc_alive": None, "silent_s": None,
         "child_running": None, "since_beat_s": None}
    if f["unit_state"] == "unknown":
        blind["unit"] = "systemd could not be read"

    def procs():
        pids = cgroup_pids(rec["unit"], runner) + cgroup_pids(DH.scope_name(rec["seat"], rec["unit"]), runner)
        return process_facts({p: read_proc(p) for p in pids})
    if f["unit_state"] == "active":
        got, why = _try(procs)
        if why:
            blind["process"] = why
        elif not got[0] and now - (rec.get("at") or 0) < START_S:
            blind["process"] = "the run is %d s old and its claude is not up yet" % (now - (rec.get("at") or 0))
        else:
            f["proc_alive"], f["child_running"] = got
    path, why = _try(transcript, rec, projects)
    if path:
        f["silent_s"], why = _try(silence, path, now)
    if why:
        blind["transcript"] = why
    if isinstance((prev or {}).get("beat_at"), (int, float)):
        f["since_beat_s"] = now - prev["beat_at"]
    return f, blind, path


def run_line(rec, now, runner=subprocess.run, projects=None):
    """-> the ALIVE: line of this run now, read from its transcript and its clone."""
    path, _ = _try(transcript, rec, projects)
    text = _try(last_message, path)[0] if path else None
    return line(rec["unit"], text, _try(commits_of, rec, runner)[0], now)


# ---- the beat ----------------------------------------------------------------------------------------------------

def alive_path(unit, root=None):
    return os.path.join(DH.runs_dir(root), unit + ".alive.json")


def read_alive(unit, root=None):
    """-> the last look, or None when none is on file. CouldNotLook when the file cannot be read."""
    if not os.path.lexists(alive_path(unit, root)):
        return None
    try:
        with open(alive_path(unit, root), encoding="utf-8") as fh:
            got = json.load(fh)
    except (OSError, ValueError) as e:
        raise CouldNotLook("%s: %s" % (alive_path(unit, root), e))
    if not isinstance(got, dict):
        raise CouldNotLook("%s: not an object" % alive_path(unit, root))
    return got


def _write(path, obj):
    tmp = "%s.%d.%d.tmp" % (path, os.getpid(), time.monotonic_ns())
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1)
    os.replace(tmp, path)


def look(rec, now, root=None, runner=subprocess.run, projects=None, appender=clone_append, dry=False):
    """One run's look. -> what it wrote. Its keys are never a run record's (`unit`, `status`, `item`): the readers of the
    run records must not take it for one."""
    prev, why = _try(read_alive, rec["unit"], root)
    prev = prev or {}
    f, blind, _ = facts(rec, now, prev, runner, projects)
    d = decide(f)
    if d["act"] == "blind" and blind:
        d["why"] += " (%s)" % "; ".join("%s: %s" % kv for kv in sorted(blind.items()))
    out = {"of": rec["unit"], "looked_at": now, "act": d["act"], "why": d["why"], "facts": f, "blind": blind,
           "beat_at": prev.get("beat_at"), "renewal": prev.get("renewal"), "line": prev.get("line")}
    if why:
        out["earlier_look"] = "could not look: " + why
    if d["act"] == "renew":
        out["renewal"] = "dry: not called" if dry else renew(rec, appender(rec))
        if not out["renewal"].startswith("refused"):
            out["beat_at"] = now        # a refused renewal is tried again at the next look
    elif d["act"] == "lapse":
        out["renewal"] = "not renewed: " + d["why"] if lease_env(rec)[0] else "no lease"
    if d["act"] in ("renew", "lapse"):
        out["line"] = run_line(rec, now, runner, projects)
    if not dry:
        _write(alive_path(rec["unit"], root), out)
    return out


def reading_path(root=None):
    return os.path.join(root or DH.state_dir(), "run_alive", "reading.json")


def beat(now=None, root=None, runner=subprocess.run, projects=None, appender=clone_append, dry=False, records=None):
    """-> (exit code, text). 0: every live run was looked at (a blind one says so); 1: the records could not be listed, and
    the old reading stands."""
    now = now or time.time()
    try:
        recs = [r for r in (records or DH.all_records)(root) if r.get("status") in ("launching", "running")]
    except OSError as e:
        return 1, "COULD NOT LOOK: the run records could not be listed: %s" % e
    rows = []
    for rec in recs:
        try:
            rows.append(look(rec, now, root, runner, projects, appender, dry))
        except Exception as e:  # noqa: BLE001  one run's surprise never stops the look at the others
            rows.append({"of": rec.get("unit"), "act": "blind", "why": "could not look: %s: %s" % (type(e).__name__, e),
                         "renewal": None})
    counts = {a: sum(r["act"] == a for r in rows) for a in ("renew", "wait", "lapse", "blind")}
    got = {"at": now, "looked": len(rows), "acts": counts,
           "refused": {r["of"]: r["renewal"] for r in rows if str(r.get("renewal") or "").startswith("refused")},
           "blind": {r["of"]: r["why"] for r in rows if r["act"] == "blind"},
           "lapsed": {r["of"]: r["why"] for r in rows if r["act"] == "lapse"}}
    if not dry:
        os.makedirs(os.path.dirname(reading_path(root)), exist_ok=True)
        _write(reading_path(root), got)
    text = "looked at %d live runs: %s" % (len(rows), ", ".join("%s %d" % kv for kv in counts.items()))
    return 0, "\n".join([text] + ["  %s  %s  %s  lease: %s" % (r["of"], r["act"], r["why"], r.get("renewal") or "-")
                                  for r in rows])


def reading_age(now, root=None):
    """-> seconds since the timer's reading was written. CouldNotLook when it is absent or cannot be read."""
    try:
        with open(reading_path(root), encoding="utf-8") as fh:
            return now - float(json.load(fh)["at"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise CouldNotLook("%s: %s: %s" % (reading_path(root), type(e).__name__, e))


def timer_live(now=None, root=None):
    """-> True only when the timer's reading was written in the last LIVE_S. One that cannot be read proves no timer: the
    brief then keeps asking, which costs a turn; the other way round costs a lease."""
    age, why = _try(reading_age, now or time.time(), root)
    return why is None and -START_S <= age <= LIVE_S


def status_text(unit, now=None, root=None):
    """-> the words `detached_helper.py status` adds to a live run."""
    got, why = _try(read_alive, unit, root)
    if why:
        return "sign of life: could not look: " + why
    if got is None:
        return "sign of life: no look on file"
    age = max(0, int(((now or time.time()) - (got.get("looked_at") or 0)) / 60))
    return "sign of life, %d min ago: %s; lease: %s; %s" % (age, got.get("why"), got.get("renewal") or "not called",
                                                         got.get("line") or "no ALIVE: line yet")


def relay_host_ends(runner=subprocess.run, me=None):
    """Each beat on this machine also writes the DETACHED RUN ENDED line of each run that ended on another host
    (run_host.relay_ends): that host's finish cannot reach this machine's Conductor log. -> its lines. Never raises: a
    host that cannot be read is said, and the beat's own exit code stands."""
    import socket
    import run_host
    me = (me or os.environ.get("RM_HOST") or socket.gethostname()).strip().lower()
    out = []
    for host in sorted(run_host.HOSTS):
        if host == me:
            continue
        try:
            out.append(run_host.relay_ends(host, runner=runner)[1])
        except Exception as e:  # noqa: BLE001
            out.append("relay ends: %s FAILED: %s: %s" % (host, type(e).__name__, e))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("beat")
    b.add_argument("--dry", action="store_true")
    sub.add_parser("show")
    a = ap.parse_args(argv)
    if a.cmd == "beat":
        rc, text = beat(dry=a.dry)
        print(text)
        if not a.dry:
            print(relay_host_ends())
        return rc
    try:
        with open(reading_path(), encoding="utf-8") as fh:
            print(fh.read())
        return 0
    except OSError as e:
        print("COULD NOT LOOK: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
