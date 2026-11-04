#!/usr/bin/env python3
"""ops_lives: the register of lives, READ ONLY. Step 3 of design/RimMandrake/operations_metronome_strategy_2026-11-02.md (§4).

One row per thing that can die and be raised (seat windows, role runs, Relentless workers and checkers, helpers, timer
services, memory-killed processes), with its WANTED state, and one line per death with, separately:
  ending   how it ended, from a fixed list (ENDINGS): what the record says happened
  cause    what probably caused it, or `unknown`; the share of unknown causes is itself a reading
Not every exit is a death: a role run that finishes, a worker that reports (finish, snag), a planned seat restart, a
window the owner cleared — those are PLANNED and are counted as such, never as deaths.

It gathers nothing new and decides nothing (build step 4 raises from it). It reads three stores:
  Dispatcher journal  $RM_DISPATCHER_STATE/journal.jsonl (default D:\\ClaudeWork\\rimmandrake\\dispatcher):
                      dead:<SEAT> alarms, helper_lost (a window ended), restart_kill, role_launch/role_done/role_stop,
                      unit_repair and timer:<unit> alarms
  memwatch events     $XDG_STATE_HOME/rm-memwatch/events.jsonl: oom_kill / oom_group_kill per cgroup
  Relentless store    <root>/store/items/*/attempts.jsonl: each worker/checker life's `end`
and the Dispatcher schedule (src/RimMandrake/rimflow/dispatcher_schedule.json) for the seats' and roles' wanted state.

A store that cannot be read is said in `blind` and its things are absent, never "no deaths".

Usage:
  python3 ops_lives.py build [--now EPOCH] [--days 14] [--out DIR]   write lives.json + lives.md (one generation)
  python3 ops_lives.py check [--max-age-min 120]                     0 = one fresh, sane generation; 1 = say why not
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCHEDULE = os.path.join(REPO, "src", "RimMandrake", "rimflow", "dispatcher_schedule.json")
DEFAULT_OUT = "/mnt/d/ClaudeWork/rimmandrake/ops_lives"
DEFAULT_DISPATCHER = "/mnt/d/ClaudeWork/rimmandrake/dispatcher"
DEFAULT_RELENTLESS = "/home/mandrake/rm/relentless"
DAY = 86400.0

# How it ended: the fixed list (§4). A death's ending is always one of these.
ENDINGS = ("silence", "out_of_memory", "time_limit", "exit_failed", "window_gone", "login_or_quota", "launch_failed",
           "unit_failed")
UNKNOWN = "unknown"

# Relentless attempt ends that are deaths, -> (thing kind, ending, cause). Every other `end` is the worker's or the
# supervisor's own word (finish, done, a snag class, a game verdict): a planned exit.
RELENTLESS_DEATHS = {
    "worker_lost": ("worker", "window_gone", UNKNOWN),
    "worker_stale": ("worker", "silence", UNKNOWN),
    "worker_full": ("worker", "time_limit", UNKNOWN),
    "account_lost": ("worker", "login_or_quota", None),     # cause: its detail (the change-over or quota line)
    "launch_fail": ("worker", "launch_failed", "auth or quota: dead at once, nothing spent (relentless.py launch_fail)"),
    "checker_lost": ("checker", "window_gone", UNKNOWN),
}

# helper_lost's window ending, read from the parenthesis: -> (death?, ending, cause)
WINDOW_ENDS = (
    ("/clear", False, "window_gone", "cleared with /clear"),
    ("before the last boot", True, "window_gone", "machine reboot, or a quit or crash before it"),
    ("transcript just stops", True, "window_gone", UNKNOWN),
)

DEAD_RX = re.compile(r"has had no session for (\d+) s")
HELPER_LOST_RX = re.compile(r"window (\S+) of (\S+) ended (\S+) \(([^)]*)\): (\d+) helper\(s\) died mid-work")
FIRST_FAILED_RX = re.compile(r"first failed (\S+?Z)")
RUN_SECS_RX = re.compile(r"after (\d+) s \(run_max_s (\d+)\)")
SCOPE_RX = re.compile(r"claude-seat-(?P<seat>[A-Z]+)-(?P<rest>.+?)(?:\.scope)?$")
RELENTLESS_UNIT_RX = re.compile(r"rm-relentless-(work|check)-([0-9a-f]{10})-g(\d+)")
ROLE_UNIT_RX = re.compile(r"rm-role-([a-z]+)-(\d+)")
RESTART_SKEW_S = 30     # a window's end may be stamped this much before the kill that ended it
RESTART_MATCH_S = 300   # a window ending this near a restart_kill of its seat is that restart
DEAD_MERGE_S = 300      # dead:<SEAT> alarms whose computed death time agree within this are one death


def parse_ts(s):
    """ISO with Z or a numeric offset (memwatch writes -0700) -> epoch, or None."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip()
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        m = re.match(r"(.*[T ]\d\d:\d\d:\d\d(?:\.\d+)?)([+-]\d\d)(\d\d)$", s)
        if m:
            s = "%s%s:%s" % m.groups()
        d = datetime.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.timestamp()
    except ValueError:
        return None


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_jsonl(path, blind, label):
    """-> list of dicts. A missing or unreadable file goes to blind; torn lines are counted, not fatal."""
    if not os.path.isfile(path):
        blind.append("%s: %s does not exist" % (label, path))
        return None
    out, torn = [], 0
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    torn += 1
                    continue
                if isinstance(r, dict):
                    out.append(r)
                else:
                    torn += 1
    except OSError as e:
        blind.append("%s: %s unreadable (%s)" % (label, path, e))
        return None
    if torn:
        blind.append("%s: %d torn line(s) in %s skipped" % (label, torn, path))
    return out


class Register:
    def __init__(self):
        self.things = {}     # id -> row
        self.deaths = []
        self.planned = []

    def thing(self, tid, kind, wanted, **extra):
        row = self.things.setdefault(tid, {"id": tid, "kind": kind, "wanted": wanted})
        for k, v in extra.items():
            row.setdefault(k, v)
        return row

    def death(self, tid, at, ending, cause, source, evidence, **extra):
        assert ending in ENDINGS, ending
        self.deaths.append(dict({"thing": tid, "at": at, "ending": ending, "cause": cause or UNKNOWN,
                                 "source": source, "evidence": evidence[:300]}, **extra))

    def plan(self, tid, at, how, source):
        self.planned.append({"thing": tid, "at": at, "how": how, "source": source})


# ---------------------------------------------------------------- the Dispatcher journal

def seat_wanted(schedule):
    """-> {SEAT: wanted} from the schedule: an enabled seat is `running`, a disabled one `stopped`. A seat absent from
    the schedule (FOUNDRY, retired 2026-11-02) is `stopped`: on purpose, never raised."""
    seats = (schedule or {}).get("seats") or {}
    return {s: ("running" if (c or {}).get("enabled", True) else "stopped") for s, c in seats.items()}


def role_wanted(schedule):
    return {r.get("name"): ("done" if r.get("enabled") else "stopped")
            for r in ((schedule or {}).get("roles") or []) if isinstance(r, dict) and r.get("name")}


def from_dispatcher(reg, recs, schedule, since, now):
    seats = seat_wanted(schedule)
    roles = role_wanted(schedule)

    def seat_row(seat):
        return reg.thing("seat:" + seat, "seat", seats.get(seat, "stopped"),
                         wanted_why="dispatcher_schedule.json seats" if seat in seats else "not in the schedule: retired")

    def inside(t):
        return t is not None and since <= t <= now

    # planned restarts first: a window that ends at a restart_kill of its seat ended on purpose
    kills = {}
    role_end = {}       # role unit -> its first terminal record at or before --now, over the whole journal
    for i, r in enumerate(recs):
        t = parse_ts(r.get("at"))
        if t is None or t > now:
            continue
        if r.get("do") == "restart_kill":
            kills.setdefault(r.get("seat") or "?", []).append(t)
        elif r.get("do") in ("role_done", "role_stop") and r.get("unit"):
            role_end[r["unit"]] = min((t, i), role_end.get(r["unit"], (t, i)))   # time, then journal order

    # each restart_kill ended ONE window: the one of its seat ending nearest at or after it (journal skew aside). A
    # crash before it is a crash, and so is a second window (its replacement) dying soon after
    ends = {}           # seat -> {window: end epoch}
    for r in recs:
        if r.get("do") == "alarm" and (r.get("kind") or "").startswith("helper_lost:"):
            m = HELPER_LOST_RX.search(r.get("why") or "")
            t = parse_ts(m.group(3)) if m else None
            if t is not None and t <= now:
                ends.setdefault(m.group(2), {}).setdefault(m.group(1), t)
    planned_windows = set()
    for seat, ks in kills.items():
        for k in sorted(ks):
            near = sorted((t - k if t >= k else RESTART_SKEW_S + k - t, w) for w, t in ends.get(seat, {}).items()
                          if -RESTART_SKEW_S <= t - k <= RESTART_MATCH_S and (seat, w) not in planned_windows)
            if near:
                planned_windows.add((seat, near[0][1]))

    def restarted(seat, win):
        return (seat, win) in planned_windows

    dead_seen = {}      # seat -> last computed death epoch
    stopped = set()     # role runs stopped on purpose: a later failed receipt is that stop
    alarmed = []        # timer alarms, joined after every repair is read
    for i, r in enumerate(recs):
        at = parse_ts(r.get("at"))
        do, kind = r.get("do"), r.get("kind") or ""
        if at is None or at > now or (at < since and do != "role_launch"):
            continue        # an alarm is never older than what it reports: a cheap first cut. A launch before the
            #                 window is kept: the run may still be open in it
        why = r.get("why") or ""
        if do == "alarm" and kind.startswith("dead:"):
            seat = kind.split(":", 1)[1]
            m = DEAD_RX.search(why)
            gone = at - int(m.group(1)) if m else at
            last = dead_seen.get(seat)
            dead_seen[seat] = gone
            if last is not None and abs(gone - last) <= DEAD_MERGE_S:
                continue        # the same dead window, alarmed again
            if not inside(gone):
                continue
            seat_row(seat)
            cause = ("a planned restart did not relaunch it" if any(0 <= gone - k <= 3 * RESTART_MATCH_S
                                                                   for k in kills.get(seat, ())) else UNKNOWN)
            reg.death("seat:" + seat, iso(gone), "window_gone", cause, "dispatcher dead:%s" % seat, why)
        elif do == "alarm" and kind.startswith("helper_lost:"):     # a rate-limited repeat still carries its count
            m = HELPER_LOST_RX.search(why)
            if not m:
                continue
            win, seat, ended, how, helpers = m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5))
            seat_row(seat)
            wt = parse_ts(ended) or at
            if not inside(wt):
                continue
            for needle, is_death, ending, cause in WINDOW_ENDS:
                if needle in how:
                    break
            else:
                is_death, ending, cause = True, "window_gone", UNKNOWN
            if restarted(seat, win):
                is_death, cause = False, "planned seat restart"
            wid = "window:%s:%s" % (seat, win)
            reg.thing(wid, "window", seats.get(seat, "stopped"), seat=seat)
            if any(x["thing"] == wid for x in reg.deaths + reg.planned):
                pass            # one window ends once: a later alarm on the same receipt is a repeat (its helper
                #                 count still goes in below, and coalesce keeps the largest)
            elif is_death:
                reg.death(wid, iso(wt), ending, cause, "dispatcher helper_lost", why)
            else:
                reg.plan(wid, iso(wt), cause, "dispatcher helper_lost")
            if helpers:
                hid = "helpers:%s:%s" % (seat, win)
                reg.thing(hid, "helper", "running", seat=seat, note="helpers that were mid-work when their window ended")
                reg.death(hid, iso(wt), "window_gone", "their window ended: %s" % how, "dispatcher helper_lost",
                          why, count=helpers)
        elif do == "restart_kill":
            seat = r.get("seat") or "?"
            seat_row(seat)
            reg.plan("seat:" + seat, iso(at), "planned seat restart (%s)" % (r.get("result") or "killed"),
                     "dispatcher restart_kill")
        elif do == "role_launch" and r.get("unit"):
            if at < since and role_end.get(r["unit"], (now + 1, 0))[0] < since:
                continue        # launched and ended before the window
            role = r.get("role") or "?"
            row = reg.thing("role:" + r["unit"], "role_run", "done", role=role, launched=iso(at),
                            role_wanted=roles.get(role, UNKNOWN))
            if r["unit"] not in role_end:
                row["open"] = True      # no terminal record by --now: running, or its end was never journalled
        elif do == "role_stop" and r.get("unit"):
            if (at, i) != role_end[r["unit"]]:
                continue        # the run ended earlier (perhaps before the window): this is a repeat
            tid = "role:" + r["unit"]
            reg.thing(tid, "role_run", "done", role=r.get("role") or "?")
            m = RUN_SECS_RX.search(why)
            if m:
                reg.death(tid, iso(at), "time_limit", UNKNOWN, "dispatcher role_stop", why,
                          ran_s=int(m.group(1)), limit_s=int(m.group(2)))
            else:
                reg.plan(tid, iso(at), "stopped: %s" % why[:120], "dispatcher role_stop")
                stopped.add(tid)
        elif do == "role_done" and r.get("unit"):
            if (at, i) != role_end[r["unit"]]:
                continue        # the run ended earlier (a stop, perhaps before the window): its receipt is that end
            tid = "role:" + r["unit"]
            reg.thing(tid, "role_run", "done", role=r.get("role") or "?")
            if tid in stopped:
                continue        # stopped on purpose: its failed receipt is that stop
            outcome = (r.get("blind") or {}).get("outcome") or ("failed" if " failed" in why else "completed")
            if outcome == "completed":
                reg.plan(tid, iso(at), "finished", "dispatcher role_done")
            else:
                cause = ("never ran: 0 tokens spent, no model" if re.search(r"\b0 (weighted )?tokens", why)
                         else UNKNOWN)
                reg.death(tid, iso(at), "exit_failed", cause, "dispatcher role_done", why)
        elif do == "unit_repair" and r.get("unit"):
            tid = "unit:" + r["unit"]
            if r["unit"].endswith(".scope"):     # a failed transient scope cleared (`how: clear`): the death of what it held,
                tid, skind = oom_thing(r["unit"])   # named as memwatch names it, so the two records of one life meet
                m = SCOPE_RX.match(r["unit"])
                reg.thing(tid, skind, (seats.get(m.group("seat"), "stopped") if m else "running") if skind == "window"
                          else "done", wanted_why="a transient scope: meant to run to its end")
            else:
                reg.thing(tid, "timer", "running", wanted_why="a Dispatcher-repaired unit: it is meant to run")
            reg.death(tid, iso(at), "unit_failed", UNKNOWN, "dispatcher unit_repair", why)
        elif do == "alarm" and kind.startswith("timer:"):    # every alarm, noted or throttled: the join below
            #                                                   de-duplicates by the failure it names
            unit = kind.split(":", 1)[1]
            tid = "unit:" + unit
            m = FIRST_FAILED_RX.search(why)
            ft = parse_ts(m.group(1)) if m else None
            if not inside(ft):
                continue
            reg.thing(tid, "timer", "running", wanted_why="a watched timer: it is meant to run")
            alarmed.append((tid, ft, why))

    # a timer alarm names the first failure; a repair of that failure, before or after it in the journal, is the same
    for tid, ft, why in alarmed:
        same = [d for d in reg.deaths if d["thing"] == tid and (
            parse_ts(d["at"]) == ft if d["source"] == "dispatcher timer alarm"      # a repeat names the same failure
            else abs((parse_ts(d["at"]) or 0) - ft) < ALARM_JOIN_S)]                # a repair is stamped near it
        if same:
            if ft < parse_ts(same[0]["at"]):
                same[0]["failed_at"] = iso(ft)  # the failure, not its later repair, is when it died: applied after the
                #                                 joins (build), so a kill seen between the two still meets the repair
            continue
        reg.death(tid, iso(ft), "unit_failed", UNKNOWN, "dispatcher timer alarm", why)


# ---------------------------------------------------------------- memwatch

def leaf_ooms(recs, since):
    """oom_kill/oom_group_kill counts propagate up the cgroup tree: one kill shows in the leaf and every parent at the
    same ts. Keep only the leaf-most cgroups of each ts."""
    by_ts = {}
    for r in recs:
        if r.get("kind") not in ("oom_kill", "oom_group_kill"):
            continue
        at = parse_ts(r.get("ts"))
        if at is None or at < since or not r.get("cgroup"):
            continue
        by_ts.setdefault(r["ts"], []).append(r)
    out = []
    for ts, rs in sorted(by_ts.items(), key=lambda kv: parse_ts(kv[0])):
        delta = {}
        for r in rs:
            delta[r["cgroup"]] = max(delta.get(r["cgroup"], 0), int(r.get("delta") or 1))
        for cg in sorted(delta):
            below = [o for o in delta if o.startswith(cg + "/")]
            top = [o for o in below if not any(o.startswith(b + "/") for b in below)]   # nearest descendants only
            left = delta[cg] - sum(delta[o] for o in top)
            if left > 0:        # kills not explained by a descendant were this cgroup's own
                r = next(x for x in rs if x["cgroup"] == cg)
                out.append(dict(r, delta=left, _at=parse_ts(ts)))
    return out


def scope_of(cgroup):
    """'claude-seats.slice/claude-seat-BENCH-rm-relentless-work-abc-g3.scope/claude-code-bash' ->
    (scope name, child or None). The innermost systemd unit on the path (a claude-seat-* group, or any *.scope) is
    the scope: named as the Dispatcher names it (unit_repair `unit:<name>.scope`), so the two records of one scope
    meet. A path with no unit in it (a bare slice) is its own thing, whole."""
    parts = cgroup.split("/")
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].startswith("claude-seat-") or parts[i].endswith((".scope", ".service")):
            return parts[i], ("/".join(parts[i + 1:]) or None)
    return cgroup, None


def oom_thing(scope):
    """-> (thing id, kind). Relentless and role scopes name the life they hold; a seat's numbered scope is a window."""
    m = RELENTLESS_UNIT_RX.search(scope)
    if m:
        return "relentless:%s:%s:g%s" % ("worker" if m.group(1) == "work" else "checker", m.group(2), m.group(3)), (
            "worker" if m.group(1) == "work" else "checker")
    m = ROLE_UNIT_RX.search(scope)
    if m:
        return "role:" + m.group(0), "role_run"
    m = SCOPE_RX.match(scope)
    if m:
        return "window:%s:scope-%s" % (m.group("seat"), m.group("rest")), "window"
    if scope.endswith(".scope"):
        return "unit:" + scope, "scope"
    if scope.endswith(".service"):
        return "unit:" + scope, "timer"     # as the Dispatcher names a repaired service; it runs again and again
    return "cgroup:" + scope, "process_group"


def from_memwatch(reg, recs, since, now, seats):
    """Each leaf oom kill is a death of what it killed. A kill inside a scope's child (claude-code-bash: a tool
    command) kills that command, not the window: the command group is the thing, and the scope's own ending is left
    to its own record; the kill is kept as `oom_in` for whoever ends that scope (see attach_ooms)."""
    kills = []
    for r in leaf_ooms(recs, since):
        if r["_at"] > now:
            continue
        scope, child = scope_of(r["cgroup"])
        tid, kind = oom_thing(scope)
        if child:
            cid = "%s/%s" % (tid, child)
            reg.thing(cid, "command", "done", note="the tool commands run inside %s" % tid)
            reg.death(cid, iso(r["_at"]), "out_of_memory", "memory limit of %s" % r["cgroup"], "memwatch %s"
                      % r["kind"], "%s %s +%s" % (r["cgroup"], r["kind"], r.get("delta")), count=r.get("delta") or 1)
        else:
            m = SCOPE_RX.match(scope)
            wanted = ((seats.get(m.group("seat"), "stopped") if m else "running") if kind == "window"
                      else "running" if kind in ("process_group", "timer") else "done")     # a slice runs on; a scope ends
            reg.thing(tid, kind, wanted)
            reg.death(tid, iso(r["_at"]), "out_of_memory", "memory limit of %s" % r["cgroup"], "memwatch %s"
                      % r["kind"], "%s %s +%s" % (r["cgroup"], r["kind"], r.get("delta")), count=r.get("delta") or 1)
        kills.append({"thing": tid, "at": r["_at"], "child": child, "cgroup": r["cgroup"], "delta": r.get("delta") or 1})
    return kills


# ---------------------------------------------------------------- Relentless

def short(item):
    """relentless.py short(): the 10-hex id its unit names carry."""
    return hashlib.sha1(item.encode()).hexdigest()[:10]


def from_relentless(reg, root, since, now, blind):
    items = os.path.join(root, "store", "items")
    if not os.path.isdir(items):
        blind.append("relentless: %s does not exist" % items)
        return
    n = 0
    for p in sorted(glob.glob(os.path.join(items, "*", "attempts.jsonl"))):
        item = os.path.basename(os.path.dirname(p))
        recs = read_jsonl(p, blind, "relentless %s" % item) or []
        n += 1
        starts, ended = {}, set()
        for r in recs:
            at = parse_ts(r.get("at"))
            if at is None or r.get("gen") is None:
                continue        # an item-level line (its `done`, an unhold) ends no process
            if "start" in r and not r.get("end"):
                starts[r["gen"]] = at
                continue
            end = r.get("end")
            if not end:
                continue
            if at > now:
                continue        # not yet happened at --now: the life is still open then
            ended.add(r["gen"])
            if at < since:
                continue
            death = RELENTLESS_DEATHS.get(end)
            kind = death[0] if death else "worker"
            tid = "relentless:%s:%s:g%s" % (kind, short(item), r.get("gen"))
            reg.thing(tid, kind, "done", item=item, started=iso(starts[r.get("gen")]) if r.get("gen") in starts else None)
            if death:
                cause = death[2] if death[2] is not None else (r.get("detail") or UNKNOWN)[:200]
                reg.death(tid, iso(at), death[1], cause, "relentless attempts", "%s: %s" % (end, r.get("detail") or ""),
                          item=item)
            else:
                reg.plan(tid, iso(at), end, "relentless attempts")
        for gen, at in starts.items():
            if gen not in ended and at <= now:     # a life with no end on record: alive, or not yet reaped
                reg.thing("relentless:worker:%s:g%s" % (short(item), gen), "worker", "done", item=item,
                          started=iso(at), open=True)
    if n == 0:
        blind.append("relentless: no attempts.jsonl under %s" % items)


# kinds that live once: every record of one of their deaths (memwatch's kill, the Dispatcher's repair, the run's own
# receipt) is the same death, however late it was written. Seats, timers, slices and command groups die again and again.
REPAIR_AFTER_KILL_S = 900
ALARM_JOIN_S = 600         # a timer alarm's `first failed` and memwatch's kill stamp of the same failure
ONE_LIFE = ("role_run", "worker", "checker", "window", "helper", "scope")


def coalesce(reg):
    """One life dies once: fold every death line of a ONE_LIFE thing into the first. It keeps the earliest time (the
    kill, not a late receipt), out_of_memory if memwatch saw the kill (memory is how it ended, whatever the receipt
    says), a known cause over `unknown`, the largest count, and every source."""
    kinds = {t["id"]: t["kind"] for t in reg.things.values()}
    groups, keep = {}, []
    for d in reg.deaths:
        if kinds.get(d["thing"]) in ONE_LIFE:
            groups.setdefault(d["thing"], []).append(d)
        else:
            keep.append(d)
    for tid, ds in groups.items():
        ds.sort(key=lambda d: d["at"])
        first = dict(ds[0])
        oom = next((d for d in ds if d["ending"] == "out_of_memory"), None)
        if oom:
            first.update(ending="out_of_memory", cause=oom["cause"])
        if first["cause"] == UNKNOWN:
            first["cause"] = next((d["cause"] for d in ds if d["cause"] != UNKNOWN), UNKNOWN)
        if len(ds) > 1:
            kills = sum(int(d.get("count") or 1) for d in ds if d["source"].startswith("memwatch"))
            first["count"] = max([kills] + [int(d.get("count") or 1) for d in ds if not d["source"].startswith("memwatch")])
            #                  distinct kills add up; repeated receipts of the same victims do not
            first["source"] = " + ".join(dict.fromkeys(d["source"] for d in ds))
            first["evidence"] = " | ".join(d["evidence"] for d in ds)[:300]
            first["folded"] = len(ds)
        keep.append(first)
    # a thing that dies again and again (a service, a slice): memwatch's kill and the Dispatcher's timer alarm naming
    # that failure (no repair on record) are one death, whichever was stamped first
    for d in [d for d in keep if d["source"] == "dispatcher timer alarm" and kinds.get(d["thing"]) not in ONE_LIFE]:
        ft = parse_ts(d["at"])
        kill = next((k for k in keep if k["thing"] == d["thing"] and k["source"].startswith("memwatch")
                     and k["ending"] == "out_of_memory" and "timer alarm" not in k["source"]
                     and abs(parse_ts(k["at"]) - ft) <= ALARM_JOIN_S), None)
        if kill is None:
            continue
        kill["source"] += " + " + d["source"]
        kill["evidence"] = (kill["evidence"] + " | " + d["evidence"])[:300]
        kill["folded"] = kill.get("folded", 1) + 1
        kill["failed_at"] = min(d["at"], kill.get("failed_at") or d["at"])
        keep.remove(d)
    # and memwatch's kill and the Dispatcher's repair of it a few minutes later are one death
    keep.sort(key=lambda d: (d["at"], not d["source"].startswith("memwatch")))     # on a tie the kill comes first
    out = []
    for d in keep:
        prev = next((o for o in reversed(out) if o["thing"] == d["thing"]), None)
        if (prev is not None and kinds.get(d["thing"]) not in ONE_LIFE and prev["ending"] == "out_of_memory"
                and "unit_repair" not in prev["source"]     # each kill absorbs one repair
                and prev["source"].startswith("memwatch") and d["source"] == "dispatcher unit_repair"
                and 0 <= parse_ts(d["at"]) - parse_ts(prev["at"]) <= REPAIR_AFTER_KILL_S):
            prev["source"] += " + " + d["source"]
            prev["evidence"] = (prev["evidence"] + " | " + d["evidence"])[:300]
            prev["folded"] = prev.get("folded", 1) + 1
            if d.get("failed_at"):
                prev["failed_at"] = min(d["failed_at"], prev.get("failed_at") or d["failed_at"])
            continue
        out.append(d)
    reg.deaths[:] = out


def attach_ooms(reg, kills, window_s=1800):
    """A kill inside a life's command group (claude-code-bash: a tool command), shortly before that life died of an
    unknown cause, is its probable cause: said as such, the ending unchanged (the record says how it ended; this says
    why). A kill of the life's own scope is already that death (coalesce)."""
    for d in reg.deaths:
        if d["cause"] != UNKNOWN or d["ending"] == "out_of_memory":
            continue
        dt = parse_ts(d["at"])
        near = [k for k in kills if k["thing"] == d["thing"] and k["child"] and 0 <= dt - k["at"] <= window_s]
        if near:
            k = near[-1]
            d["cause"] = "probably memory: oom kill in %s at %s" % (k["cgroup"], iso(k["at"]))


# ---------------------------------------------------------------- the register

def build(now, days, dispatcher_root, memwatch_events, relentless_root, schedule_path):
    """Every record through --now is read and joined first, and the window is cut last: a life killed just before the
    window whose receipt lands inside it is a death before the window, not a new one."""
    since = now - days * DAY
    history = 0.0
    blind = []
    reg = Register()
    try:
        with open(schedule_path, encoding="utf-8") as f:
            schedule = json.load(f)
    except (OSError, ValueError) as e:
        schedule = None
        blind.append("schedule: %s unreadable (%s): seat and role wanted states are UNMEASURED" % (schedule_path, e))
    seats = seat_wanted(schedule)
    for seat, w in seats.items():
        reg.thing("seat:" + seat, "seat", w, wanted_why="dispatcher_schedule.json seats")
    recs = read_jsonl(os.path.join(dispatcher_root, "journal.jsonl"), blind, "dispatcher")
    if recs is not None:
        from_dispatcher(reg, recs, schedule, history, now)
    kills = []
    mrecs = read_jsonl(memwatch_events, blind, "memwatch")
    if mrecs is not None:
        kills = from_memwatch(reg, mrecs, history, now, seats)
    from_relentless(reg, relentless_root, history, now, blind)
    coalesce(reg)
    attach_ooms(reg, kills)
    for d in reg.deaths:
        if d.get("failed_at") and d["failed_at"] < d["at"]:
            d["at"] = d["failed_at"]
    for d in reg.deaths:       # a life that died is not open, whether or not its own receipt was ever written
        if d["thing"] in reg.things and reg.things[d["thing"]]["kind"] in ONE_LIFE:
            reg.things[d["thing"]].pop("open", None)
    reg.deaths[:] = [d for d in reg.deaths if parse_ts(d["at"]) >= since]
    reg.planned[:] = [p for p in reg.planned if parse_ts(p["at"]) >= since]
    seen = {d["thing"] for d in reg.deaths} | {p["thing"] for p in reg.planned}
    reg.things = {k: t for k, t in reg.things.items()
                  if k in seen or t.get("open") or (t["kind"] == "seat" and k[5:] in seats)}
    if schedule is None:
        for row in reg.things.values():
            if row["kind"] in ("seat", "window"):
                row["wanted"] = "UNMEASURED"

    reg.deaths.sort(key=lambda d: d["at"])
    for row in reg.things.values():
        mine = [d for d in reg.deaths if d["thing"] == row["id"]]
        row["deaths_24h"] = sum(1 for d in mine if now - parse_ts(d["at"]) <= DAY)
        row["deaths_7d"] = sum(1 for d in mine if now - parse_ts(d["at"]) <= 7 * DAY)
        row["deaths"] = len(mine)
        row["last_ending"] = mine[-1]["ending"] if mine else None
        row["last_cause"] = mine[-1]["cause"] if mine else None
        row["planned_exits"] = sum(1 for p in reg.planned if p["thing"] == row["id"])
    endings = {}
    for d in reg.deaths:
        endings[d["ending"]] = endings.get(d["ending"], 0) + 1
    unknown = sum(1 for d in reg.deaths if d["cause"] == UNKNOWN)
    return {
        "generation": "%d-%d" % (int(now), os.getpid()),
        "built_at": iso(now), "built_epoch": now, "window_days": days, "since": iso(since),
        "sources": {"dispatcher_journal": os.path.join(dispatcher_root, "journal.jsonl"),
                    "memwatch_events": memwatch_events,
                    "relentless_items": os.path.join(relentless_root, "store", "items"),
                    "schedule": schedule_path},
        "blind": blind,
        "readings": {"things": len(reg.things), "deaths": len(reg.deaths), "planned_exits": len(reg.planned),
                     "deaths_24h": sum(1 for d in reg.deaths if now - parse_ts(d["at"]) <= DAY),
                     "victims": sum(int(d.get("count") or 1) for d in reg.deaths),
                     "cause_unknown": unknown,
                     "cause_unknown_share": round(unknown / len(reg.deaths), 3) if reg.deaths else None,
                     "by_ending": endings},
        "things": sorted(reg.things.values(), key=lambda r: (-r["deaths_7d"], r["id"])),
        "deaths": reg.deaths,
        "planned": sorted(reg.planned, key=lambda p: p["at"]),
    }


def render_md(reg):
    r = reg["readings"]
    out = ["# Register of lives (read only)", "",
           "Built %s over %d days since %s; generation %s. Sources: %s." % (
               reg["built_at"], reg["window_days"], reg["since"], reg["generation"],
               ", ".join("%s `%s`" % kv for kv in reg["sources"].items())), ""]
    if reg["blind"]:
        out += ["**Blind:**"] + ["- %s" % b for b in reg["blind"]] + [""]
    share = "UNMEASURED (no deaths)" if r["cause_unknown_share"] is None else "%.0f%%" % (100 * r["cause_unknown_share"])
    out += ["%d things, %d deaths (%d victims; %d in 24 h), %d planned exits. Cause unknown: %d (%s). By ending: %s." % (
        r["things"], r["deaths"], r["victims"], r["deaths_24h"], r["planned_exits"], r["cause_unknown"], share,
        ", ".join("%s %d" % kv for kv in sorted(r["by_ending"].items(), key=lambda kv: -kv[1])) or "none"), "",
        "## Things that died (most in 7 days first)", "",
        "| thing | kind | wanted | 24 h | 7 d | all | last ending | last cause |", "|---|---|---|---|---|---|---|---|"]
    for t in reg["things"]:
        if t["deaths"]:
            out.append("| `%s` | %s | %s | %d | %d | %d | %s | %s |" % (
                t["id"], t["kind"], t["wanted"], t["deaths_24h"], t["deaths_7d"], t["deaths"], t["last_ending"],
                (t["last_cause"] or "").replace("|", "/")[:90]))
    quiet = [t for t in reg["things"] if not t["deaths"]]
    out += ["", "%d more things with no death in the window." % len(quiet), "", "## The last 30 deaths", ""]
    for d in reg["deaths"][-30:]:
        out.append("- %s `%s` ended **%s**; cause: %s (%s)" % (d["at"], d["thing"], d["ending"], d["cause"][:120],
                                                               d["source"]))
    return "\n".join(out) + "\n"


def publish(reg, out_dir):
    """Both files as one generation: each written whole beside its target, then swapped in with os.replace; json last,
    so a reader of lives.json never finds a newer md than json's generation says."""
    os.makedirs(out_dir, exist_ok=True)
    for name, text in (("lives.md", render_md(reg)), ("lives.json", json.dumps(reg, indent=1, sort_keys=True))):
        fd, tmp = tempfile.mkstemp(prefix="." + name, dir=out_dir)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, os.path.join(out_dir, name))


def check(out_dir, now, max_age_min):
    p = os.path.join(out_dir, "lives.json")
    try:
        with open(p, encoding="utf-8") as f:
            reg = json.load(f)
    except (OSError, ValueError) as e:
        return 1, "lives.json unreadable: %s" % e
    age = (now - float(reg.get("built_epoch") or 0)) / 60
    if age > max_age_min:
        return 1, "lives.json is %.0f min old (max %d)" % (age, max_age_min)
    try:
        with open(os.path.join(out_dir, "lives.md"), encoding="utf-8") as f:
            md = f.read()
    except OSError as e:
        return 1, "lives.md unreadable: %s" % e
    if reg["generation"] not in md:
        return 1, "lives.md is not generation %s" % reg["generation"]
    bad = [d for d in reg["deaths"] if d["ending"] not in ENDINGS]
    if bad:
        return 1, "%d death(s) with an ending off the fixed list" % len(bad)
    r = reg["readings"]
    return 0, "OK generation %s, %d things, %d deaths, %d blind source note(s)" % (
        reg["generation"], r["things"], r["deaths"], len(reg["blind"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--now", type=float)
    b.add_argument("--days", type=float, default=14)
    b.add_argument("--out", default=DEFAULT_OUT)
    b.add_argument("--dispatcher", default=os.environ.get("RM_DISPATCHER_STATE", DEFAULT_DISPATCHER))
    b.add_argument("--memwatch", default=os.path.join(
        os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state"), "rm-memwatch", "events.jsonl"))
    b.add_argument("--relentless", default=os.environ.get("RM_RELENTLESS_ROOT", DEFAULT_RELENTLESS))
    b.add_argument("--schedule", default=SCHEDULE)
    c = sub.add_parser("check")
    c.add_argument("--out", default=DEFAULT_OUT)
    c.add_argument("--max-age-min", type=int, default=120)
    c.add_argument("--now", type=float)
    a = ap.parse_args(argv)
    now = a.now if a.now is not None else time.time()
    if a.cmd == "build":
        reg = build(now, a.days, a.dispatcher, a.memwatch, a.relentless, a.schedule)
        publish(reg, a.out)
        r = reg["readings"]
        print("lives: %d things, %d deaths (%d in 24 h, cause unknown %d), %d planned exits, %d blind; %s" % (
            r["things"], r["deaths"], r["deaths_24h"], r["cause_unknown"], r["planned_exits"], len(reg["blind"]),
            os.path.join(a.out, "lives.md")))
        return 0
    code, msg = check(a.out, now, a.max_age_min)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
