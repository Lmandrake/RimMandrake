#!/usr/bin/env python3
"""v3_ready: a read-only GO / NO-GO table for the RimFlow v3 trial night (2026-10-28).

    python3 src/RimMandrake/rimflow/v3_ready.py [--no-selftests] [--expect-account NAME] [--json]

Runbook: design/RimMandrake/rimflow_v3_trial_night_2026-10-28.md (every step that changes something is there; this
program changes nothing). It reads the Dispatcher's state, its unit file, the schedule the Dispatcher actually reads
(the dispatch clone's), ops_watch's status.json, the seat sessions Claude Code registers, the switching plan's HOLD
brake, and git; it runs only read-only commands (systemctl is-active, deadman_check.py run without --file-alarms,
claude-account --json status, git log/diff/cat-file/rev-parse, and the selftests through run_selftests.py --only).

Verdicts per row:
  GO          measured, and fine for tonight.
  NO-GO       measured, and it blocks (the evidence column says what was seen).
  UNMEASURED  the instrument could not tell (file torn or missing, command failed, reading stale). Never a guess and
              never a GO: it blocks like a NO-GO until someone looks.
  WARN        measured, worth a look, does not block (e.g. a runway under 0.8 of the time to reset).
  INFO        a state to know (a role's enabled flag, whether the cutover was applied); never blocks.
OVERALL is NO-GO if any blocking row is NO-GO, else UNMEASURED if any blocking row is, else GO.
Exit code: 0 GO, 1 NO-GO, 2 UNMEASURED.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
from collections import namedtuple
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True            # read-only: no __pycache__ from importing role_launch
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"   # nor from the child Pythons it runs
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

SCHEDULE_REL = "src/RimMandrake/rimflow/dispatcher_schedule.json"
GOALS_REL = "infrastructure/state/CONDUCTOR_GOALS.md"
CUTOVER_REL = "src/RimMandrake/rimflow/v3_cutover.py"
CUTOVER_RECORD_REL = "infrastructure/state/v3_cutover/record.json"
FOUNDRY_SHARD_REL = "infrastructure/state/ledger/events/FOUNDRY.jsonl"
DEADMAN_REL = "src/RimMandrake/Utils/deadman_check.py"
RUNNER_REL = "src/RimMandrake/Utils/run_selftests.py"

TICK_STALE_S = 600          # 5 ticks of 120 s
OPS_STALE_S = 2700          # the schedule's ops_stale_s
LEDGER_STALE_S = 6 * 3600   # FOUNDRY's shard published within 6 h
RING_RECENT_S = 3600        # a ring this recent proves the doorbell worked
MIN_INSTR_BYTES = 200
RUNWAY_WARN = 0.8           # account_pick's switch line
WEEK_LEFT_NOGO = 10.0       # %
CODEX_USED_NOGO = 90.0      # %

R = "src/RimMandrake/rimflow/"
U = "src/RimMandrake/Utils/"
# Selftests per component. Roles also get any rimflow/selftest_<role>*.py found on disk (a helper's new test counts
# without editing this map); Producer and Innovator have no role-specific test yet, so their row runs the launcher's.
SELFTESTS = {
    "Dispatcher": [R + "selftest_dispatcher.py", R + "selftest_dispatcher_r2.py", R + "selftest_account_pick.py",
                   U + "selftest_deadman_check.py", R + "selftest_role_tokens.py"],
    "Conductor": [R + "selftest_delegated_digest.py", R + "selftest_role_launch.py"],
    "Operations": [U + "selftest_ops_watch.py", R + "selftest_blind_view.py", R + "selftest_role_launch.py"],
    "Arbiter": [R + "selftest_arbiter_tiers.py", R + "selftest_isolated_evidence.py", R + "selftest_role_launch.py"],
    "Auditor": [R + "selftest_audits.py", R + "selftest_audit_prescreen.py", R + "selftest_role_launch.py"],
    "Producer": [R + "selftest_role_launch.py"],
    "Innovator": [R + "selftest_role_launch.py"],
    "Cutover": [R + "selftest_v3_cutover.py", R + "selftest_flowworks_lane.py"],
    "Seat restart": [R + "selftest_seat_restart.py"],
}
LAUNCHER_ONLY = {R + "selftest_role_launch.py"}

Row = namedtuple("Row", "comp check verdict evidence blocking")


def row(comp, chk, verdict, evidence):
    return Row(comp, chk, verdict, evidence, verdict in ("GO", "NO-GO", "UNMEASURED"))


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def from_iso(s):
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc).timestamp()
        except (TypeError, ValueError):
            continue
    return None


CLOCK_SKEW_S = 300


def num(x):
    """A finite real number (not a bool, not NaN/inf) or None."""
    if isinstance(x, bool) or not isinstance(x, (int, float)) or x != x or x in (float("inf"), float("-inf")):
        return None
    return x


def ago(s):
    s = int(s)
    return "%d s" % s if s < 120 else ("%d min" % (s // 60) if s < 7200 else "%.1f h" % (s / 3600.0))


def real_run(argv, timeout=60, cwd=None):
    """(rc, stdout+stderr); rc None when the command could not run or timed out."""
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return None, "%s: %s" % (type(e).__name__, e)


class Ctx:
    def __init__(self, repo=None, dispatch="/home/mandrake/rm/dispatch",
                 S="/mnt/d/ClaudeWork/rimmandrake/dispatcher", O="/mnt/d/ClaudeWork/rimmandrake/ops_watch",
                 unit=os.path.expanduser("~/.config/systemd/user/rm-dispatcher.service"),
                 plan_dir="/mnt/d/ClaudeWork/rimmandrake/switching_plan", sessions=None, proc="/proc",
                 run=real_run, now=None, selftests=True, expect_account=None,
                 trial_dirs=("/mnt/d/ClaudeWork/rimmandrake/v3_build",)):
        self.repo = repo or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
        self.dispatch, self.S, self.O, self.unit, self.plan_dir = dispatch, S, O, unit, plan_dir
        home = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
        self.sessions = sessions or os.path.join(home, "sessions")
        self.proc, self.run, self.selftests, self.expect_account = proc, run, selftests, expect_account
        self.now = time.time() if now is None else now
        self.trial_dirs = tuple(trial_dirs)


def read_json(path):
    """-> (data, None) or (None, why)."""
    try:
        with open(path) as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "missing: %s" % path
    except (OSError, ValueError) as e:
        return None, "unreadable %s: %s" % (path, str(e)[:80])


def git(ctx, cwd, *args, timeout=30):
    return ctx.run(["git", "-C", cwd] + list(args), timeout=timeout)


def on_origin(ctx, rel):
    """-> (verdict, evidence) for 'this path's working copy is what origin/main has'."""
    rc, out = git(ctx, ctx.repo, "cat-file", "-e", "origin/main:" + rel)
    if rc is None:
        return "UNMEASURED", "git did not run: " + out[:80]
    if rc != 0:
        return "NO-GO", "not on origin/main (untracked or unpublished)"
    rc, out = git(ctx, ctx.repo, "diff", "--quiet", "origin/main", "--", rel)
    if rc is None:
        return "UNMEASURED", "git diff did not run: " + out[:80]
    if rc != 0:
        return "NO-GO", "working copy differs from origin/main (unpublished edits)"
    return "GO", "on origin/main, working copy equal"


def pid_alive(ctx, pid, start=None):
    try:
        with open(os.path.join(ctx.proc, str(int(pid)), "stat")) as f:
            stat = f.read()
    except (OSError, ValueError, TypeError):
        return False
    if start is None:
        return True
    fields = stat.rsplit(")", 1)[-1].split()
    return len(fields) > 19 and fields[19] == str(start)


# ---------------------------------------------------------------- components

def schedules(ctx):
    """-> (effective, repo, why_bad). The effective schedule is the dispatch clone's (the one the live Dispatcher
    reads); it is never replaced by the repo copy. why_bad is set when it is unreadable or lacks seats/roles."""
    eff, why = read_json(os.path.join(ctx.dispatch, SCHEDULE_REL))
    repo, _ = read_json(os.path.join(ctx.repo, SCHEDULE_REL))
    if eff is not None and not (isinstance(eff, dict) and isinstance(eff.get("seats"), dict) and eff["seats"]
                                and isinstance(eff.get("roles"), list) and eff["roles"]):
        eff, why = None, "dispatch clone schedule has no seats or no roles"
    return eff, repo, (None if eff is not None else why)


def dispatcher_rows(ctx, sch, repo_sch, src, state, state_why):
    C = "Dispatcher"
    out = []
    try:
        with open(ctx.unit) as f:
            ex = [ln.strip() for ln in f if ln.strip().startswith("ExecStart=")]
        if not ex:
            out.append(row(C, "live (--apply)", "UNMEASURED", "no ExecStart in %s" % ctx.unit))
        elif ex[-1].endswith("tick --apply"):
            out.append(row(C, "live (--apply)", "GO", "unit ExecStart ends 'tick --apply'"))
        else:
            out.append(row(C, "live (--apply)", "NO-GO", "unit is DRY: " + ex[-1][-60:]))
    except OSError as e:
        out.append(row(C, "live (--apply)", "UNMEASURED", "unit unreadable: %s" % e))
    if state is None:
        out.append(row(C, "ticking", "UNMEASURED", state_why))
    else:
        t = from_iso(state.get("last_ok_tick"))
        if t is None:
            out.append(row(C, "ticking", "UNMEASURED", "state.json has no readable last_ok_tick"))
        else:
            age = ctx.now - t
            if age < -CLOCK_SKEW_S:
                v = "UNMEASURED"
            elif age > TICK_STALE_S or state.get("apply") is False:
                v = "NO-GO"
            elif state.get("apply") is True:
                v = "GO"
            else:
                v = "UNMEASURED"
            out.append(row(C, "ticking", v, "last_ok_tick %s ago (limit %s), apply=%s"
                           % (ago(max(age, 0)) if age >= 0 else "in the future", ago(TICK_STALE_S),
                              state.get("apply"))))
    rc, o = ctx.run(["systemctl", "--user", "is-active", "rm-dispatcher.timer"], timeout=20)
    if rc is None:
        out.append(row(C, "timer active", "UNMEASURED", "systemctl did not run: " + o[:80]))
    else:
        st = o.strip()
        v = "GO" if (rc == 0 and st == "active") else ("NO-GO" if st in ("inactive", "failed") else "UNMEASURED")
        out.append(row(C, "timer active", v, "rm-dispatcher.timer: " + (st or "?")[:40]))
    p = os.path.join(ctx.S, "PAUSE")
    if os.path.exists(p):
        try:
            txt = open(p).read().strip()[:80]
        except OSError:
            txt = "?"
        out.append(row(C, "no PAUSE", "NO-GO", "PAUSE present: " + txt))
    else:
        out.append(row(C, "no PAUSE", "GO", "no PAUSE file"))
    rc1, h1 = git(ctx, ctx.dispatch, "rev-parse", "HEAD")
    rc2, h2 = git(ctx, ctx.repo, "rev-parse", "origin/main")
    if rc1 != 0 or rc2 != 0:
        out.append(row(C, "dispatch clone current", "WARN", "could not compare HEADs"))
    elif h1.strip() == h2.strip():
        out.append(row(C, "dispatch clone current", "GO", "dispatch HEAD %s = origin/main" % h1.strip()[:10]))
    else:
        out.append(row(C, "dispatch clone current", "WARN", "dispatch HEAD %s, origin/main %s (testq-tick pulls "
                        "each minute)" % (h1.strip()[:10], h2.strip()[:10])))
    if sch is not None and repo_sch is not None:
        a = {r.get("name"): r.get("enabled") for r in sch.get("roles", [])}
        b = {r.get("name"): r.get("enabled") for r in repo_sch.get("roles", [])}
        if a != b or sch.get("seat_restart", {}).get("enabled") != repo_sch.get("seat_restart", {}).get("enabled"):
            out.append(row(C, "schedule published", "WARN", "repo and %s schedules differ in enabled flags "
                            "(unpublished, or not pulled yet)" % src))
    if state is not None:
        al = sorted((state.get("alarms") or {}).keys())
        out.append(row(C, "open alarms", "INFO", ", ".join(al) if al else "none"))
    return out


def deadman_rows(ctx):
    rc, o = ctx.run([sys.executable, os.path.join(ctx.repo, DEADMAN_REL), "run"], timeout=60)
    if rc is None:
        return [row("Deadman", "all arms alive", "UNMEASURED", "deadman_check did not run: " + o[:80])]
    if "all arms alive" in o and rc == 0:
        return [row("Deadman", "all arms alive", "GO", "deadman: all arms alive")]
    lines = [ln for ln in o.strip().splitlines() if ln.strip()]
    if not lines:
        return [row("Deadman", "all arms alive", "UNMEASURED", "deadman printed nothing (rc %s)" % rc)]
    return [row("Deadman", "all arms alive", "NO-GO", lines[-1][:120])]


def journal_tail(ctx, nbytes=262144):
    p = os.path.join(ctx.S, "journal.jsonl")
    try:
        with open(p, "rb") as f:
            f.seek(0, 2)
            n = f.tell()
            f.seek(max(0, n - nbytes))
            raw = f.read().decode("utf-8", "replace")
    except OSError:
        return []
    out = []
    for ln in raw.splitlines():
        try:
            out.append(json.loads(ln))
        except ValueError:
            continue
    return out


def doorbell_rows(ctx, sch, state, journal):
    out = []
    for seat, cfg in sorted((sch or {}).get("seats", {}).items()):
        if not (cfg.get("enabled") and cfg.get("wake")):
            continue
        C = "Doorbell " + seat
        d, why = read_json(os.path.join(cfg.get("clone", ""), ".claude", "settings.local.json"))
        if d is None:
            out.append(row(C, "hook installed", "NO-GO" if why.startswith("missing") else "UNMEASURED", why))
        else:
            hooks = [h for blk in ((d.get("hooks") or {}).get("Stop") or []) for h in (blk.get("hooks") or [])]
            ok = [h for h in hooks if h.get("type") == "command" and h.get("asyncRewake") is True
                  and re.search(r"\bpython3\b.*src/RimMandrake/rimflow/doorbell\.py", str(h.get("command")))]
            script = os.path.join(cfg.get("clone", ""), "src", "RimMandrake", "rimflow", "doorbell.py")
            if not ok:
                out.append(row(C, "hook installed", "NO-GO", "no python3 doorbell.py asyncRewake Stop hook"))
            elif not os.path.isfile(script):
                out.append(row(C, "hook installed", "NO-GO", "hook set but %s missing" % script))
            else:
                out.append(row(C, "hook installed", "GO", "Stop hook python3 doorbell.py asyncRewake; script present"))
        alarms = (state or {}).get("alarms") or {}
        armed, _ = read_json(os.path.join(ctx.S, "armed", seat + ".json"))
        rings = [e for e in journal if e.get("do") == "ring" and e.get("seat") == seat and e.get("result") == "rung"
                 and from_iso(e.get("at")) is not None and ctx.now - from_iso(e.get("at")) <= RING_RECENT_S]
        if state is None:
            out.append(row(C, "armed or rung", "UNMEASURED", "dispatcher state unreadable"))
        elif "unwakeable:" + seat in alarms:
            out.append(row(C, "armed or rung", "NO-GO", "Dispatcher alarm unwakeable:%s (idle, no doorbell)" % seat))
        elif isinstance(armed, dict) and pid_alive(ctx, armed.get("pid")) and owner_live(ctx, armed):
            out.append(row(C, "armed or rung", "GO", "armed now, pid %s, armed_at %s" % (armed.get("pid"),
                                                                                      armed.get("armed_at"))))
        elif rings:
            out.append(row(C, "armed or rung", "GO", "rung %s ago (ring %s)" % (
                ago(ctx.now - from_iso(rings[-1]["at"])), rings[-1].get("ring_id", "?"))))
        else:
            out.append(row(C, "armed or rung", "UNMEASURED", "not armed now and no ring in the last hour "
                            "(seat busy? recheck after its next turn ends)"))
    return out


def owner_live(ctx, armed):
    """The armed doorbell's Claude window (owner_pid) is a registered session whose start time matches /proc, so a
    reused pid cannot read as a live doorbell."""
    op = armed.get("owner_pid")
    if not op:
        return False
    for ss in sessions_by_name(ctx).values():
        for x in ss:
            if str(x.get("pid")) == str(op) and x.get("procStart") is not None \
                    and pid_alive(ctx, op, x.get("procStart")):
                return True
    return False


def sessions_by_name(ctx):
    out = {}
    for p in glob.glob(os.path.join(ctx.sessions, "*.json")):
        d, _ = read_json(p)
        if isinstance(d, dict) and d.get("name"):
            out.setdefault(d["name"], []).append(d)
    return out


TILE_LABEL = {"BENCH": "CONDUCTOR"}   # v3: the Conductor absorbs Bench and keeps seat BENCH's tile (CONDUCTOR.md)


def live_sessions(ctx, by, name):
    return [s for s in by.get(name, []) if s.get("procStart") is not None
            and pid_alive(ctx, s.get("pid"), s.get("procStart"))]


def window_rows(ctx, sch):
    """Every enabled seat's tile must be a live session. A role's window_name is only a HOLD (role_launch: while a
    window of that name is live the role's headless run waits), so it is reported as INFO, never blocking."""
    seats = [(TILE_LABEL.get(k, k), cfg["session_name"]) for k, cfg in sorted((sch or {}).get("seats", {}).items())
             if cfg.get("enabled") and cfg.get("session_name")]
    holds = [(r.get("name"), r["window_name"]) for r in (sch or {}).get("roles", []) if r.get("window_name")]
    if not os.path.isdir(ctx.sessions):
        return ([row("Window " + lab, "live session", "UNMEASURED", "no sessions dir %s" % ctx.sessions)
                 for lab, _ in seats] +
                [row(rn, "hold window", "INFO", "UNMEASURED (no sessions dir)") for rn, _ in holds])
    by = sessions_by_name(ctx)
    out = []
    for lab, n in seats:
        C = "Window " + lab
        live = live_sessions(ctx, by, n)
        if live:
            s = live[-1]
            out.append(row(C, "live session", "GO", "'%s' pid %s status %s%s" % (
                n, s.get("pid"), s.get("status"), "" if len(live) == 1 else " (%d live with this name)" % len(live))))
        else:
            out.append(row(C, "live session", "NO-GO", "no live session named '%s' (%d stale file(s))"
                            % (n, len(by.get(n, [])))))
    for rn, n in holds:
        live = live_sessions(ctx, by, n)
        out.append(row(rn, "hold window", "INFO", ("'%s' live: headless %s runs are HELD" % (n, rn)) if live
                       else "'%s' absent: headless %s runs launch" % (n, rn)))
    return out


def selftest_results(ctx):
    """-> ({rel: verdict}, None) or (None, why). One run_selftests.py call over every mapped file on disk."""
    files = sorted({f for fs in SELFTESTS.values() for f in fs} | set(role_globs(ctx)))
    files = [f for f in files if os.path.exists(os.path.join(ctx.repo, f))]
    if not files:
        return None, "no mapped selftest file on disk"
    rc, o = ctx.run([sys.executable, os.path.join(ctx.repo, RUNNER_REL), "--only"] + files, timeout=420,
                    cwd=ctx.repo)
    if rc is None:
        return None, "run_selftests did not finish: " + o[:80]
    res = {}
    for ln in o.splitlines():
        m = re.match(r"^(PASS|FAIL|UNMEASURED|CRASH|SKIPPED)\s+(?:[\d.]+s\s+)?(\S+\.py)\b", ln)
        if m:
            res[m.group(2)] = m.group(1)
    if not res:
        return None, "run_selftests printed no verdict lines (rc %s)" % rc
    return res, None


def role_globs(ctx, name=None):
    out = []
    for n in ([name] if name else ["conductor", "operations", "arbiter", "auditor", "producer", "innovator"]):
        for p in glob.glob(os.path.join(ctx.repo, R, "selftest_%s*.py" % n.lower())):
            out.append(os.path.relpath(p, ctx.repo))
    return out


def selftest_row(ctx, comp, res, why):
    files = list(dict.fromkeys(SELFTESTS.get(comp, []) + role_globs(ctx, comp) if comp in ROLE_NAMES
                               else SELFTESTS.get(comp, [])))
    missing = [f for f in files if not os.path.exists(os.path.join(ctx.repo, f))]
    files = [f for f in files if f not in missing]
    if not ctx.selftests:
        return row(comp, "selftests", "UNMEASURED", "not run (--no-selftests)")
    if missing:
        return row(comp, "selftests", "UNMEASURED", "mapped selftest missing on disk: " +
                   ", ".join(os.path.basename(f) for f in missing))
    if res is None:
        return row(comp, "selftests", "UNMEASURED", why)
    got = {f: res.get(f, "MISSING") for f in files}
    bad = {f: v for f, v in got.items() if v in ("FAIL", "CRASH")}
    unk = {f: v for f, v in got.items() if v not in ("PASS", "FAIL", "CRASH")}
    short = lambda d: ", ".join("%s %s" % (os.path.basename(f), v) for f, v in d.items())  # noqa: E731
    if bad:
        return row(comp, "selftests", "NO-GO", short(bad))
    if unk:
        return row(comp, "selftests", "UNMEASURED", short(unk))
    note = " (launcher test only; no role-specific selftest)" if set(files) <= LAUNCHER_ONLY else ""
    return row(comp, "selftests", "GO", "PASS %d/%d%s" % (len(files), len(files), note))


ROLE_NAMES = ("Conductor", "Operations", "Arbiter", "Auditor", "Producer", "Innovator")


def run_records(ctx, role, state):
    """-> list of (t, kind, record) newest last. kind 'state' (Dispatcher's record) or 'trial' (an out file only)."""
    recs = []
    known = set()
    for r in (((state or {}).get("roles") or {}).get(role["name"]) or {}).get("runs") or []:
        recs.append((r.get("at") or 0, "state", r))
        for k in ("unit", "marker"):
            if r.get(k):
                known.add(r[k])
        if r.get("out"):
            known.add(os.path.basename(r["out"])[:-5])
    pat = "rm-role-%s-*.json" % role["name"].lower()
    paths = glob.glob(os.path.join(ctx.S, "roles", pat))
    for d in ctx.trial_dirs:
        paths += glob.glob(os.path.join(d, "**", pat), recursive=True)
    for p in sorted(set(paths)):
        stem = os.path.basename(p)[:-5]
        if stem in known:
            continue
        m = re.search(r"-(\d{9,})$", stem)
        recs.append((int(m.group(1)) if m else os.path.getmtime(p), "trial", p))
    recs.sort(key=lambda x: x[0])
    return recs


def cap_for(role, mode):
    if mode == "economy" and role.get("economy_token_cap"):
        return role["economy_token_cap"]
    if mode == "quick" and role.get("quick_token_cap"):
        return role["quick_token_cap"]
    return role.get("run_token_cap") or role.get("quick_token_cap")


def last_run_row(ctx, role, state):
    C = role["name"]
    recs = run_records(ctx, role, state)
    live = [r for r in recs if r[1] == "state" and r[2].get("state") == "running"]
    done = [r for r in recs if not (r[1] == "state" and r[2].get("state") == "running")]
    tail = " (a run is live now)" if live else ""
    if not done:
        return row(C, "last run under cap", "UNMEASURED", "never run (no Dispatcher record, no trial out file)" + tail)
    t, kind, rec = done[-1]
    if kind == "state":
        mode, tok, st = rec.get("mode"), rec.get("tokens"), rec.get("state")
        where = "run %s %s" % (rec.get("unit", "?"), datetime.fromtimestamp(t, timezone.utc).strftime("%m-%d %H:%MZ"))
        if st != "done":
            return row(C, "last run under cap", "NO-GO", "%s ended '%s'%s" % (where, st, tail))
    else:
        d, why = read_json(rec)
        where = "trial %s" % os.path.basename(rec)
        if d is None:
            return row(C, "last run under cap", "UNMEASURED", "%s: %s" % (where, why))
        mode, tok = None, RL.run_tokens(d)
        if d.get("is_error") or d.get("subtype") != "success":
            return row(C, "last run under cap", "NO-GO", "%s ended %s is_error=%s%s" % (
                where, d.get("subtype"), d.get("is_error"), tail))
    cap = cap_for(role, mode)
    if not isinstance(tok, (int, float)):
        return row(C, "last run under cap", "UNMEASURED", "%s: tokens unmeasured%s" % (where, tail))
    if not cap:
        return row(C, "last run under cap", "UNMEASURED", "%s: %d tokens, no cap in the schedule" % (where, tok))
    v = "GO" if tok <= cap else "NO-GO"
    return row(C, "last run under cap", v, "%s: %s tokens / cap %s%s%s" % (
        where, format(int(tok), ","), format(int(cap), ","), " (%s)" % mode if mode else "", tail))


def role_rows(ctx, sch, state, st_res, st_why):
    out = []
    for role in (sch or {}).get("roles", []):
        C = role.get("name", "?")
        p = os.path.join(ctx.repo, role.get("instructions") or "/nonexistent")
        try:
            n = os.path.getsize(p)
            out.append(row(C, "instructions", "GO" if n >= MIN_INSTR_BYTES else "NO-GO",
                           "%s, %d bytes" % (role.get("instructions"), n)))
        except OSError:
            out.append(row(C, "instructions", "NO-GO", "missing: %s" % role.get("instructions")))
        out.append(selftest_row(ctx, C, st_res, st_why))
        out.append(last_run_row(ctx, role, state))
        off = role.get("off_file")
        offp = off and (off if off.startswith("/") else RL.wsl_path(off))
        en = "ON" if role.get("enabled") else "OFF (schedule)"
        if offp and os.path.exists(offp):
            en += ", off file present: %s" % offp
        out.append(row(C, "enabled", "INFO", en))
    return out


def ledger_rows(ctx, sch):
    C = "FOUNDRY ledger"
    out = []
    rc, o = git(ctx, ctx.repo, "log", "-1", "--format=%ct", "origin/main", "--", FOUNDRY_SHARD_REL)
    try:
        t = int(o.strip()) if rc == 0 else None
    except ValueError:
        t = None
    if t is None:
        out.append(row(C, "published recently", "UNMEASURED", "git log failed (rc %s): %s" % (rc, o.strip()[:60])))
    else:
        age = ctx.now - t
        out.append(row(C, "published recently", "GO" if age <= LEDGER_STALE_S else "NO-GO",
                       "last on origin/main %s ago (limit %s; as of this clone's last fetch)" % (
                           ago(max(age, 0)), ago(LEDGER_STALE_S))))
    clone = ((sch or {}).get("seats", {}).get("FOUNDRY") or {}).get("clone")
    if clone:
        rc, o = git(ctx, clone, "diff", "--numstat", "HEAD", "--", FOUNDRY_SHARD_REL)
        if rc == 0:
            add = sum(int(ln.split()[0]) for ln in o.splitlines() if ln.split() and ln.split()[0].isdigit())
            out.append(row(C, "uncommitted lines in FOUNDRY clone", "INFO" if add == 0 else "WARN",
                           "%d line(s) not committed in %s" % (add, clone)))
    return out


def cutover_rows(ctx, st_res, st_why):
    C = "Cutover"
    p = os.path.join(ctx.repo, CUTOVER_REL)
    if not os.path.exists(p):
        out = [row(C, "tool on origin/main", "NO-GO", "missing: " + CUTOVER_REL)]
    else:
        out = [row(C, "tool on origin/main", *on_origin(ctx, CUTOVER_REL))]
    out.append(selftest_row(ctx, C, st_res, st_why))
    rec, why = read_json(os.path.join(ctx.repo, CUTOVER_RECORD_REL))
    out.append(row(C, "applied", "INFO", ("record.json present (applied%s)" % (
        " at %s" % rec.get("at") if isinstance(rec, dict) and rec.get("at") else "")) if rec is not None
        else "not applied (no record.json)"))
    return out


def goals_rows(ctx):
    p = os.path.join(ctx.repo, GOALS_REL)
    try:
        n = os.path.getsize(p)
    except OSError:
        return [row("Goals", "present", "NO-GO", "missing: " + GOALS_REL)]
    out = [row("Goals", "present", "GO" if n >= MIN_INSTR_BYTES else "NO-GO", "%s, %d bytes" % (GOALS_REL, n))]
    v, e = on_origin(ctx, GOALS_REL)
    out.append(row("Goals", "on origin/main", v if v == "GO" else ("WARN" if v == "NO-GO" else v), e))
    return out


def hold_rows(ctx):
    C = "Account HOLD"
    p = os.path.join(ctx.plan_dir, "HOLD")
    out = [row(C, "HOLD file present", "GO" if os.path.exists(p) else "NO-GO",
               p if os.path.exists(p) else "missing: %s (switching_plan.py would act)" % p)]
    rc, o = ctx.run(["systemctl", "--user", "is-active", "account-plan.timer"], timeout=20)
    if rc is None:
        out.append(row(C, "account-plan.timer off", "UNMEASURED", "systemctl did not run: " + o[:60]))
    else:
        st = o.strip()
        v = "NO-GO" if st in ("active", "activating", "reloading") else ("GO" if st in ("inactive", "failed")
                                                                          else "UNMEASURED")
        out.append(row(C, "account-plan.timer off", v, "account-plan.timer: " + (st or "?")[:30]))
    return out


def account_rows(ctx):
    rc, o = ctx.run(["claude-account", "--json", "status"], timeout=30)
    d = None
    if rc == 0:
        try:
            d = json.loads(o[o.index("{"):]) if "{" in o else None
        except ValueError:
            d = None
    if not isinstance(d, dict) or not d.get("live"):
        return None, [row("Account", "live account", "UNMEASURED", "claude-account status unreadable (rc %s)" % rc)]
    live = d["live"]
    st = {a.get("name"): a.get("state") for a in d.get("accounts") or []}
    ev = "live %s (state %s)" % (live, st.get(live, "?"))
    if ctx.expect_account:
        v = "GO" if live == ctx.expect_account and st.get(live) == "ok" else "NO-GO"
        ev += ", expected %s" % ctx.expect_account
    else:
        v = "INFO"
    return live, [row("Account", "live account", v, ev)]


def runway_rows(ctx, live):
    C = "Runway"
    d, why = read_json(os.path.join(ctx.O, "status.json"))
    cl = "Claude (%s)" % (live or "?")
    if d is None:
        return [row(C, cl, "UNMEASURED", why), row(C, "Codex", "UNMEASURED", why)]
    t = num(d.get("t")) if "t" in d else from_iso(d.get("at"))   # a present but invalid t is not replaced
    if t is None or ctx.now - t > OPS_STALE_S or t - ctx.now > CLOCK_SKEW_S:
        why = "ops_watch status.json stale or undated (%s)" % (ago(ctx.now - t) + " old" if t else "no t")
        return [row(C, cl, "UNMEASURED", why), row(C, "Codex", "UNMEASURED", why)]
    pts = d.get("points") or {}

    def pt(k):
        p = pts.get(k) or {}
        ok = p.get("m") in ("MEASURED", "ESTIMATE") and num(p.get("v")) is not None
        return (p.get("v"), p.get("m")) if ok else (None, p.get("m") or "absent")
    out = []
    if not live:
        out.append(row(C, cl, "UNMEASURED", "live account unknown"))
    else:
        rw, rm = pt("accounts.%s.runway" % live)
        wl, wm = pt("accounts.%s.week_left_pct" % live)
        if wl is not None and not 0 <= wl <= 100:
            out.append(row(C, cl, "UNMEASURED", "week left %r out of range" % wl))
        elif wl is not None and wl < WEEK_LEFT_NOGO:
            out.append(row(C, cl, "NO-GO", "week left %.0f%% %s (runway %s)" % (wl, wm, rm if rw is None else rw)))
        elif rw is None or wl is None:
            out.append(row(C, cl, "UNMEASURED", "runway %s, week left %s" % (rm, wm)))
        else:
            ev = "runway %.2f %s, week left %.0f%% %s" % (rw, rm, wl, wm)
            v = "NO-GO" if wl < WEEK_LEFT_NOGO else ("WARN" if rw < RUNWAY_WARN else "GO")
            out.append(row(C, cl, v, ev))
    rw, rm = pt("codex.runway")
    used, um = pt("codex.week_used_pct")
    if used is not None and not 0 <= used <= 100:
        out.append(row(C, "Codex", "UNMEASURED", "week used %r out of range" % used))
    elif used is not None and used >= CODEX_USED_NOGO:
        out.append(row(C, "Codex", "NO-GO", "week used %.0f%% %s (runway %s)" % (used, um, rm if rw is None else rw)))
    elif rw is None or used is None:
        out.append(row(C, "Codex", "UNMEASURED", "runway %s, used %s" % (rm, um)))
    else:
        v = "NO-GO" if used >= CODEX_USED_NOGO else ("WARN" if rw < RUNWAY_WARN else "GO")
        out.append(row(C, "Codex", v, "runway %.2f %s, week used %.0f%% %s" % (rw, rm, used, um)))
    return out


def seat_restart_rows(ctx, sch, st_res, st_why):
    sr = (sch or {}).get("seat_restart") or {}
    seats = sorted((sr.get("seats") or {}).keys())
    return [selftest_row(ctx, "Seat restart", st_res, st_why),
            row("Seat restart", "enabled", "INFO", "%s%s" % ("ON" if sr.get("enabled") else "OFF",
                                                            " seats: " + ",".join(seats) if seats else ""))]


def collect(ctx):
    sch, repo_sch, sch_bad = schedules(ctx)
    src = "dispatch clone"
    state, state_why = read_json(os.path.join(ctx.S, "state.json"))
    if state is not None and not isinstance(state, dict):
        state, state_why = None, "state.json is not an object"
    journal = journal_tail(ctx)
    st_res, st_why = selftest_results(ctx) if ctx.selftests else (None, "not run (--no-selftests)")
    rows = []
    rows.append(row("Schedule", "dispatch clone readable", "UNMEASURED" if sch_bad else "GO",
                    sch_bad or "%d seats, %d roles" % (len(sch["seats"]), len(sch["roles"]))))
    rows += dispatcher_rows(ctx, sch, repo_sch, src, state, state_why)
    rows.append(selftest_row(ctx, "Dispatcher", st_res, st_why))
    rows += deadman_rows(ctx)
    rows += doorbell_rows(ctx, sch, state, journal)
    rows += window_rows(ctx, sch)
    rows += role_rows(ctx, sch, state, st_res, st_why)
    rows += ledger_rows(ctx, sch)
    rows += cutover_rows(ctx, st_res, st_why)
    rows += seat_restart_rows(ctx, sch, st_res, st_why)
    rows += goals_rows(ctx)
    rows += hold_rows(ctx)
    live, arows = account_rows(ctx)
    rows += arows
    rows += runway_rows(ctx, live)
    return rows


def overall(rows):
    blk = [r for r in rows if r.blocking]
    if not blk:
        return "UNMEASURED"
    if any(r.verdict == "NO-GO" for r in blk):
        return "NO-GO"
    if any(r.verdict == "UNMEASURED" for r in blk):
        return "UNMEASURED"
    return "GO"


def render(rows, now=None):
    w1 = max([len(r.comp) for r in rows] + [9])
    w2 = max([len(r.check) for r in rows] + [5])
    lines = ["v3_ready %s" % iso(now if now is not None else time.time()),
             "%-*s  %-*s  %-10s  %s" % (w1, "COMPONENT", w2, "CHECK", "VERDICT", "EVIDENCE")]
    for r in rows:
        lines.append("%-*s  %-*s  %-10s  %s" % (w1, r.comp, w2, r.check, r.verdict, r.evidence))
    n = {k: sum(1 for r in rows if r.verdict == k) for k in ("GO", "NO-GO", "UNMEASURED", "WARN", "INFO")}
    lines.append("")
    lines.append("OVERALL: %s  (GO %d, NO-GO %d, UNMEASURED %d, WARN %d, INFO %d)" % (
        overall(rows), n["GO"], n["NO-GO"], n["UNMEASURED"], n["WARN"], n["INFO"]))
    for r in rows:
        if r.blocking and r.verdict != "GO":
            lines.append("  blocks: %s / %s: %s" % (r.comp, r.check, r.verdict))
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-selftests", action="store_true", help="skip the selftest run (rows read UNMEASURED)")
    ap.add_argument("--expect-account", help="the account that must be live (tonight: the one switched to)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    ctx = Ctx(selftests=not a.no_selftests, expect_account=a.expect_account)
    rows = collect(ctx)
    if a.json:
        print(json.dumps({"at": iso(ctx.now), "overall": overall(rows), "rows": [r._asdict() for r in rows]},
                         indent=1))
    else:
        sys.stdout.write(render(rows, ctx.now))
    return {"GO": 0, "NO-GO": 1}.get(overall(rows), 2)


if __name__ == "__main__":
    sys.exit(main())
