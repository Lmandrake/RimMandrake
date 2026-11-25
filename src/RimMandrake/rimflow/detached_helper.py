#!/usr/bin/env python3
"""detached_helper.py — long helper work that runs OUTSIDE the window (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

An in-process helper (the Agent tool) dies with its window, so a window past its context limit cannot restart while
one runs. A detached run lives in its own transient systemd unit and survives the window's restart:

  python3 src/RimMandrake/rimflow/detached_helper.py launch --seat BENCH --item ITEM_ID --brief-file F \
      --budget-usd USD|0 [--model fable|opus|sonnet] [--max-s none|SECONDS] [--resume SESSION] [--continue-on-cap N]
      [--agent NAME]
  python3 src/RimMandrake/rimflow/detached_helper.py status [--all]
  python3 src/RimMandrake/rimflow/detached_helper.py finish --unit U     (the unit's ExecStopPost; never by hand)
  python3 src/RimMandrake/rimflow/detached_helper.py return --unit U [--no-publish-ledger]   (the unit's last ExecStopPost)
  python3 src/RimMandrake/rimflow/detached_helper.py backfill-cost [--apply]   (dollars of runs finished before cost_usd)

launch: the item must be on the ledger, and FILED ON origin/main: the helper's clone is made from origin/main, so an item whose
file event sits in an unpublished shard (OWNER.jsonl from --owner-said, say) is one the helper's `rimflow note` refuses for
the whole run (lesson 20261107T214121Z-BENCH-detached-helper-item-not-origin). One fetch, then a search of every shard under
infrastructure/state/ledger/events/ at origin/main; no hit refuses (exit 2) with the exact `./publish` command that passes
(it publishes nothing itself; boundary design/specs/2026-11-19-launch-unpublished-item/boundary.md).
It takes a pool clone <pool>/clones/<ITEM>.det through scratch_clone.py
(reused, synced, when it exists), then starts role_launch's path: systemd-run --user + claude_bounded.sh -p, the
model passed, NO wall-time limit by default (owner, 2026-11-08: "No time limits please"; --max-s none or 0). An explicit
--max-s SECONDS still bounds it twice (the unit's RuntimeMaxSec and claude_bounded's scope). Spend is bounded by
spend_watchdog.py, from outside the agent, at the cap the launch states (required, no default; 0 = none; a --resume
without one carries the newest run record of that session's cap, and refuses when none is readable), never with
claude --max-budget-usd, which tells the agent its spend every turn:
owner 2026-11-16, RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN); the brief states no spend or cap. The brief gets a footer: work in the clone, land with ./publish, put state, evidence and one
imperative NEXT on the item as a rimflow note with --publish (the write lands its own shards, ledger_landing.py), and a
PROGRESS: note after each experiment.
--resume SESSION follows the one resume rule (left_open_continue.whole_or_fresh): a session whose context is at or over
RESUME_WHOLE_MAX_TOKENS, when its item holds a progress record, launches FRESH from the brief, that record and the
previous brief; otherwise it resumes. --agent NAME starts claude as that agent (its .claude/agents file is the system
prompt); boundary design/specs/2026-11-21-live-sitting-context-burn/boundary.md.
finish: runs when the unit stops for any reason (done, failed, killed at its bound). It first KILLs and stops the run's
claude_bounded scope (claude-seat-<seat>-<unit>.scope): claude lives there, outside the unit, so a stopped unit alone left
it running and billing (DETACHED_STOP_FIX_ORPHAN_KEEPS_BILLING, 2026-11-03: killed at 15:06:59, ran to ~15:13). It writes the outcome as a note
on the item, publishes the seat's shard from the clone, and appends one line to the Conductor log. Once per run. A run
that ends success with its item still open and no `LEFT OPEN:` note since it began gets one plain OWED line in that note,
that log line and its record (`owed_close`, which MATURATION_NOW's Needs Conductor lists while the item stays open); it
closes nothing (RIMMANDRAKE_FLAG_DETACHED_SUCCESS_LEAVING_ITEM_OPEN, 2026-11-15: a run fixed 17 gaps, exited 0, and its
item stayed `proposed` until a hand closed it).
A run that ends success with work left (its item open with a `LEFT OPEN:` note since it began, or lane tickets of its
brief still open), or one the spend watchdog stopped whose launch carried --continue-on-cap N, gets ONE continuation:
finish plans it and starts left_open_continue.py's own unit, which launches it once the clone is back (at most 3 a day
per item, then an alarm; never for a killed, voided or held run; RIMMANDRAKE_CONTINUE_LEFT_OPEN_RUNS_WITHOUT_A_HAND_RELAUNCH).
return: the run's last step gives the pool clone <ITEM>.det BACK (RIMMASTER_RELEASE_POOL_FROZEN_ITEMS_HOLD_CLONES, 2026-11-07:
three finished .det clones, a stopped pipeline's ten and SHOWINGS held 16 of 16 pool places and 67 of 70 GB while little ran).
It lands the clone's conversation records, publishes the seat shard if the run left it dirty, levels the clone with
./sync, then hands what is still unlanded to Effects.remove_clone, which bundles every commit, stash and dirty file to
the store before the clone goes (or parks it as a warm spare). A bundle that cannot be made KEEPS the clone, and the step
says so; a clone the caller gave with --clone, one a process sits in and one another live run uses are never touched.
A launch never takes a <ITEM>.det another run still holds (RIMMANDRAKE_HOLD_DET_CLONE_UNTIL_RETURNED, 2026-11-13/14: a
relaunch read "ended", started inside the clone the return step deleted seconds later, and two runs spent ~0.67 USD each on
nothing): it WAITS (RETURN_WAIT_S) while the run before is still in its stop steps or its -return unit is going, then
refuses with the command that passes; a live run's clone, a dead run's (record running, unit gone) and one its return
kept are refused at once. A run whose unit is gone reads "dead", never "running" (live_status). The unit's working
directory is "-"-prefixed, so its ExecStopPost steps still run (in /) once the clone is gone; they used to fail
200/CHDIR, finish never ran, and the stale "running" record kept later runs' clones.
Records: <RM_DISPATCHER_STATE>/detached/<unit>.json. Use it for anything expected to run over ~20 min; the Agent
tool stays for short work (CONDUCTOR.md "Checkpoint, so a drain never freezes him").
"""
import argparse
import contextlib
import fcntl
import glob
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import own_cgroup  # noqa: E402  a clone checkout outside the calling unit's memory limit
import run_tmp  # noqa: E402  (its own TMPDIR: TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP)
import principal  # noqa: E402  a gate of form never refuses the owner or the Conductor window (principal.form)
import form_fault as FF  # noqa: E402  the brief line: a refusal that names its repair is an instruction
try:                                    # whole text, never a silent cut (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS)
    from . import fulltext
except ImportError:
    import fulltext  # noqa: E402

DEFAULT_MAX_S = None    # unbounded: no RuntimeMaxSec on the unit, no CLAUDE_SCOPE_RUNTIME_MAX (owner 2026-11-08)
# budget: danger=a wall bound under one minute ends a run before its first turn; ends no work: a launch that asks for it is
# budget: refused, with the repair
MIN_MAX_S = 60
# budget: danger=a stopped run that never ends holds its clone; longest=584s (the stop steps hold a publish: the longest of
# budget: 636); stays=TimeoutStopSec is also how long a stopped run may ignore SIGTERM, and his stops stay as they are
STOP_S = 600           # TimeoutStopSec: the stop-post steps' bound (finish, wrapup, the return's start)
# budget: danger=a run with a wall bound is ended while it finishes and publishes; never reached in the 14 days to 2026-11-24;
# budget: no record of its run
GRACE_S = 120          # finish + publish time on top of the run's own bound
# The per-run stop guards a runaway unattended burn (owner 2026-11-12: "not burn 90M tokens overnight by itself"), and
# has NO default level: a $15 default named no danger and stopped 4 real runs (3 lessons), so a launch states its cap,
# and --resume carries the earlier run's (boundary design/specs/2026-11-19-launch-spend-cap/boundary.md).
# The model tiers, their repair from a full id and the id each launches as: role_launch.TIERS, tier and launch_model,
# the one alias table (design/specs/2026-11-22-run-spend-and-model-alias/boundary.md).
SEATS = ("BENCH", "STEVE", "RUNNER")   # FOUNDRY retired (owner by card 2026-11-02)
REAL_LOG = "/mnt/d/ClaudeWork/rimmandrake/conductor/log.md"
ORIGIN_REF = "origin/main"
# Linux refuses any one argument over 128 KB (MAX_ARG_STRLEN, E2BIG): Gimme Some Slack's in-game brief (94.5 KB) plus
# its holder packet passed it and every launch failed (2026-11-16). Every brief now goes in by file on stdin (a short
# one in argv was matched by the run's own `pgrep -f`, 2026-11-23); this stays the bound no launch argument may reach.
ARG_BRIEF_MAX = 100_000
DEAD_STATES = ("inactive", "failed", "not-found")   # a unit in one of these runs nothing; "unknown" is not proof of death
KILL_STATUSES = ("HUP", "INT", "KILL", "TERM", "129", "130", "137", "143")   # systemd's EXIT_STATUS of a signal stop
# budget: danger=a launching run with no unit yet reads as dead; ends no work: the record reads as a dead launch
LAUNCH_GRACE_S = 120   # a record "launching" this young may simply not have its unit yet
# budget: danger=a return that never ends holds the launch; longest=289s (1151 return units, user journal, 14 days to
# budget: 2026-11-24)
RETURN_WAIT_S = 3000    # how long launch waits for the run before to give the clone back (a 3.6 GB bundle takes minutes)
RETURN_POLL_S = 10
# the longest Bash call of a run (BASH_MAX_TIMEOUT_MS in its unit): one long wait (Utils/waitalive.py, 55 min) in place of
# many of 10 min, under the one-hour prompt cache. Tried in real units: design/specs/2026-11-23-long-waits/experiment.json.
# 0 = not set. A Claude Code that does not know the variable ignores it.
BASH_MAX_MS = 3420000
EVENTS_REL = "infrastructure/state/ledger/events"
# RIMMANDRAKE_MOVE_BIOME_FEATURE_JUDGE_RULES_OUT_POINTERS_STAY: CLAUDE.md keeps only a pointer for these rule groups, so
# every detached brief names their homes. Boundary: design/specs/2026-11-19-rule-homes-in-briefs/boundary.md.
RULE_HOMES = """- Some rules live outside CLAUDE.md. Read the home file before the work it names. A biome, roster, sea,
  creature or creature name: `design/RimMandrake/biome_rulings.md`. An in-game LLM call, a pit, Direct Sun or shade, or
  a flyer: its section of `design/RimMandrake/standing_rulings.md`. A judge, a gate or a judge brief:
  `design/RimMandrake/standing_rulings.md` §The judge refuses flaws, not polish and §A refusal carries its path to pass.
"""

FOOTER = """

---
You are a DETACHED helper: you run in your own systemd unit, outside any window, in the clone {clone} (your cwd).
Ledger item: {item}. Seat: {seat}. {bound_text}.
- Work only in that clone. Land code with `./publish` and explicit paths (never git add -A, never --force). The command
  lines named below (claim, note, wait, close, publish) stand filled in at the end of this brief.
- Pass `--publish` on every rimflow write (claim, note, wait, close, file): the write lands exactly the files it wrote,
  OWNER.jsonl included when the event is the owner's, and prints `PUBLISHED <sha>`. Exit 4 means written but not
  landed: the line names the cause and the command that passes.
- First, claim your item (the claim line).
- At the end, close it with the sha ./publish printed (the close line; an operational item also takes `--live`), or, when
  anything is left, write a note whose text starts `LEFT OPEN:` and says exactly what. A run that ends success with its item open and no such note is
  flagged to the Conductor.
- An acceptance check can pass on less than the spec. Before you close, read each spec line again: build what is not
  built, or file it as ONE ticket and close with `--remainder <its id>`. `close` asks when your words name an unbuilt part.
- A `LEFT OPEN:` note relaunches this brief in a fresh session (left_open_continue.py). When what is left is not a
  helper's to do (the owner's decision, an act of the Conductor's, a date), also put a dated wait on the item, so it
  is not relaunched for nothing (the wait line).
- Before you stop: write your state, evidence paths and one imperative NEXT as a note (the note line). A program
  reads your process for your sign of life: no note is asked by the clock.
- After each experiment or step that changes what you know, write your progress record as a note whose text starts
  `PROGRESS:` and names the theory, the experiment, the reading and the next action (`"PROGRESS: theory: ... |
  experiment: ... | reading: ... | next: ..."`). A stopped run with a large context is carried on by a fresh session that has only this brief and those notes.
- This run ends when your turn ends: a helper or command still running in the background then is killed and its work
  is lost. Run helpers and long commands in the foreground and take their results before your last message; never end
  "waiting" for anything.
- A command that can take over 10 minutes: one Bash call with `timeout` BASH_MAX_MS of
  `python3 src/RimMandrake/Utils/waitalive.py run --name <name> -- <command>`. It waits up to 55 minutes and its last line
  is the verdict: exit 0 FINISHED rc=0, 1 FINISHED rc=N, 3 HUNG, 4 STILL RUNNING, 5 COULD NOT LOOK, 6 DIED. It kills
  nothing: after 3, 4 or a cut call, `python3 src/RimMandrake/Utils/waitalive.py attach <name>` waits again. For a job
  whose work is on Windows or another machine, add `--progress <the log that it writes>`. Do not poll with `sleep`.
- Nobody reads your stdout until you end; the note is what the Conductor sees. End with a 5-line summary.
""".replace("BASH_MAX_MS", str(BASH_MAX_MS)) + RULE_HOMES + FF.BRIEF_LINE


def dirty_shards(clone, seat, runner=subprocess.run):
    """RIMMANDRAKE_PUBLISH_EVERY_DIRTY_SHARD_OWNER_FILES_WENT_UNSENT: -> every ledger shard under events/ the clone has
    changed, the seat's own first. A --per-ruling/--owner-said/--by-card event lands in OWNER.jsonl, not the seat's
    shard; publishing only the seat's left two file events to ride into an orphan bundle (2026-11-19). [] when git
    cannot answer (then the seat's shard is still published by its caller)."""
    try:
        r = runner(["git", "status", "--porcelain", "--untracked-files=all", "--", EVENTS_REL], cwd=clone,
                   capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        return []
    if getattr(r, "returncode", 1):
        return []
    paths = {ln[3:].strip() for ln in (r.stdout or "").splitlines() if ln[3:].strip().endswith(".jsonl")}
    own = "%s/%s.jsonl" % (EVENTS_REL, seat)
    return sorted(paths, key=lambda p: (p != own, p))


def state_dir():
    import doorbell
    return doorbell.state_dir()


def runs_dir(root=None):
    d = os.path.join(root or state_dir(), "detached")
    os.makedirs(d, exist_ok=True)
    return d


def record_path(unit, root=None):
    return os.path.join(runs_dir(root), unit + ".json")


def read_record(unit, root=None):
    try:
        with open(record_path(unit, root), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_record(rec, root=None):
    p = record_path(rec["unit"], root)
    # a temp name of its own: two writers sharing <record>.tmp could publish a half-written file
    # (RIMMANDRAKE_UNIQUE_TEMP_PER_RECORD_WRITE_SHARED_TMP)
    tmp = "%s.%d.%d.tmp" % (p, os.getpid(), time.monotonic_ns())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.replace(tmp, p)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def unit_name(seat, item, now, n=1):
    slug = re.sub(r"[^a-z0-9]+", "-", item.lower()).strip("-")[:40].strip("-")
    return "rm-detached-%s-%s-%d%s" % (seat.lower(), slug, int(now), "" if n == 1 else "-%d" % n)


def reserve_record(rec, root=None, tries=100):
    """Claim a unit name no other run holds: create its record with O_EXCL, bumping a -N suffix on a clash.
    Two launches of one item in the same second used to share a name, so the second one's systemd-run failed and
    its launch_failed record overwrote the RUNNING helper's (DETACHED_LAUNCH_FIX_SAME_SECOND_CLOBBER)."""
    for n in range(1, tries + 1):
        unit = unit_name(rec["seat"], rec["item"], rec["at"], n)
        try:
            fd = os.open(record_path(unit, root), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            continue
        d = runs_dir(root)
        rec.update(unit=unit, out=os.path.join(d, unit + ".out.json"), err=os.path.join(d, unit + ".err"))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
        return unit
    raise RuntimeError("no free unit name for %s after %d tries" % (rec["item"], tries))


def pool_root():
    return os.environ.get("RM_DETACHED_POOL") or os.path.expanduser("~/rm/relentless")


def filed_ids(lines):
    """The ids the ledger's own reader (helper_checkpoint.known_items) takes from event lines: a `file` event's `id` and a
    `spawn` event's `name`. A line that merely mentions an id (a note, a spawn's `from`, a longer id) files nothing."""
    ids = set()
    for line in lines:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        if ev.get("event") == "file" and ev.get("id"):
            ids.add(ev["id"])
        elif ev.get("event") == "spawn" and ev.get("name"):
            ids.add(ev["name"])
    return ids


def local_shards(item, repo=None):
    """-> the ledger shards in this clone's working tree (repo-relative) that file `item`, sorted. These are the ones to publish."""
    repo = repo or REPO
    d = os.path.join(repo, *EVENTS_REL.split("/"))
    try:
        names = sorted(n for n in os.listdir(d) if n.endswith(".jsonl"))
    except OSError:
        return []
    found = []
    for n in names:
        try:
            with open(os.path.join(d, n), encoding="utf-8", errors="replace") as f:
                if item in filed_ids(ln for ln in f if item in ln):
                    found.append(EVENTS_REL + "/" + n)
        except OSError:
            continue
    return found


def publish_command(item, shards):
    """The one command that puts `item`'s filing on origin/main (boundary design/specs/2026-11-19-launch-unpublished-item:
    seven lessons said "publish the shard first" and agents kept meeting the refusal). origin_check prints it; origin_gate
    runs it for a principal. A write in this clone lands its own shards with `rimflow ... --publish` (ledger_landing.py)."""
    return './publish -m "ledger: %s filed" %s' % (item, " ".join(shards))


def origin_check(item, runner=subprocess.run, repo=None, seat=None):
    """-> None when `item` is filed on origin/main, else the one-line refusal text, holding the exact command that passes.

    One fetch (the ref could be stale), then `git grep` of every shard under EVENTS_REL at origin/main for lines holding the
    id, kept only if filed_ids() reads the item from one: a `file` event's id or a `spawn` event's name. An item found is
    allowed even when the fetch failed; one not found says so when it did, since origin/main may then be stale. A git that
    cannot be read at all (not 0 or 1) refuses too: a blind instrument is not a pass."""
    repo = repo or REPO
    stale = ""
    try:
        r = runner(["git", "fetch", "-q", "--no-tags", "origin", "main"], cwd=repo, capture_output=True, text=True,
                   # budget: class=call
                   timeout=120, stdin=subprocess.DEVNULL)
        if r.returncode:
            stale = "fetch exit %d: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-80:])
    except (OSError, subprocess.SubprocessError) as e:
        stale = "fetch failed: %s" % str(e)[-80:]
    try:
        r = runner(["git", "grep", "-h", "-F", "-I", "-e", item, ORIGIN_REF, "--", EVENTS_REL], cwd=repo,
                   capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return "refused: cannot read %s to check %s on it (%s)" % (ORIGIN_REF, item, str(e)[-80:])
    if r.returncode not in (0, 1):
        return "refused: cannot read %s to check %s on it (git grep exit %d: %s)" % (
            ORIGIN_REF, item, r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-80:])
    if item in filed_ids((r.stdout or "").splitlines()):
        return None
    shards = local_shards(item, repo)
    if shards:
        say = "to pass, run in %s: %s" % (repo, publish_command(item, shards))
    else:       # filed in another clone: its seat's shard (a plain file) and OWNER.jsonl (a provenance flag's)
        say = "no local shard holds it either; to pass, run in the clone that filed it: %s" % publish_command(
            item, ["%s/%s.jsonl" % (EVENTS_REL, s) for s in (seat or "<SEAT>", "OWNER")])
    return "refused: %s is not on %s; %s%s" % (item, ORIGIN_REF, say, " (%s; %s may be stale)" % (stale, ORIGIN_REF) if stale else "")


def origin_gate(item, runner=subprocess.run, repo=None, seat=None, env=None):
    """origin_check, and its repair for a principal (the owner or the Conductor window, principal.form): when shards in
    this clone file the item, the launcher runs the one ./publish itself and checks again, instead of refusing
    (RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT). Anyone else gets origin_check's refusal unchanged.
    -> None when the item is on origin/main (now), else the refusal text, which names what the publish said."""
    text = origin_check(item, runner=runner, repo=repo, seat=seat)
    if not text:
        return None
    repo = repo or REPO
    shards = local_shards(item, repo)
    if not shards or not principal.form("%s was not on %s: the launcher publishes %s itself" % (
            item, ORIGIN_REF, " ".join(shards)), env=env):
        return text
    argv = shlex.split(publish_command(item, shards)) + ["--ledger"]    # waits for no peer's publish (publish.land_ledger)
    try:
        r = runner(argv, cwd=repo, capture_output=True, text=True, timeout=21600, stdin=subprocess.DEVNULL)  # budget: class=publish
    except (OSError, subprocess.SubprocessError) as e:
        return "%s; the launcher's own publish could not run (%s)" % (text, str(e))
    again = origin_check(item, runner=runner, repo=repo, seat=seat)     # fetches first: a publish that exited non-zero may
    if r.returncode:                                                    # still find the item landed (another publish won)
        if again is None:
            principal.form("the launcher's own publish exited %d (%s) but %s is on %s now: going on" % (
                r.returncode, _tail(r, 120), item, ORIGIN_REF), env=env)
            return None
        return "%s; the launcher's own publish exited %d: %s" % (text, r.returncode, _tail(r, 200))
    return again


def live_status(rec, runner=subprocess.run, now=None):
    """The record's status as its unit sees it: "launching" or "running" whose unit is inactive, failed or not found is
    "dead" (finish never ran: the 2026-11-14 stale records). A young "launching" record and an unreadable unit keep theirs."""
    st = rec.get("status")
    if st not in ("launching", "running"):
        return st
    if st == "launching" and (now or time.time()) - (rec.get("at") or 0) < LAUNCH_GRACE_S:
        return st
    if rec.get("host"):     # a run on another host (run_host.py): its live state and its end are the host's own
        return remote_live_status(rec, runner)
    import role_launch as RL
    return "dead" if RL.unit_state(rec["unit"], runner=runner) in DEAD_STATES else st


def remote_live_status(rec, runner=subprocess.run, root=None):
    """The host's reading of a remote run; an end it reports is copied into this machine's record (host_end)."""
    import run_host
    st, host_rec = run_host.remote_status(rec, runner=runner)
    if st not in ("launching", "running"):
        keep = {k: v for k, v in (host_rec or {}).items() if k in ("status", "ended", "outcome", "cost_usd", "rc",
                                                                   "result", "note")}
        try:
            write_record(dict(rec, status=st, host_end=keep or None), root)
        except OSError:
            pass
    return st


# The run-record folder is shared: run_alive.py writes <unit>.alive.json there, finish <unit>.out.json, and .err, .log,
# .md and .jsonl files sit beside them. A reader that took every *.json for a record read 123 sign-of-life files as
# broken records, and list_dispatch then counted no spare room and held 11 ready items for about a day (2026-11-24).
# So a reader names what a record is: the file <unit>.json, where a unit holds no dot (unit_name), and the record in
# it names the same unit. Every other file is another writer's, and no reader of run records looks at it.
# (RIMMANDRAKE_SCOPE_COULD_NOT_LOOK_ONE_STRAY_FILE_HELD_ELEVEN_TICKETS; design/specs/2026-11-24-record-readers/boundary.md)
RECORD_NAME = re.compile(r"([^./]+)\.json")


def record_unit(name):
    """-> the unit whose run record a file of this name is, or None when the name is another writer's file."""
    m = RECORD_NAME.fullmatch(os.path.basename(name))
    return m.group(1) if m else None


def is_record(rec, unit):
    """True when `rec` (a parsed <unit>.json) is the run record of `unit`: a dict that names that unit."""
    return isinstance(rec, dict) and rec.get("unit") == unit


def record_units(root=None):
    """-> the sorted units that have a record file in the folder (no other writer's file). An OSError when the folder
    cannot be listed: could not look is never "no records"."""
    return sorted(u for u in map(record_unit, os.listdir(runs_dir(root))) if u)


def all_records(root=None, unreadable=None):
    """Each run record in the folder. A file named as a record that cannot be read or parsed goes to
    `unreadable(name)`; one that parses but does not name its unit is not a record, and is not looked at, like every
    other writer's file. An OSError when the folder cannot be listed."""
    for u in record_units(root):
        rec = read_record(u, root)
        if is_record(rec, u):
            yield rec
        elif rec is None and unreadable is not None:
            unreadable(u + ".json")


def clone_holders(dest, runner=subprocess.run, now=None, root=None, kept_ok=False):
    """-> [(unit, wait, why)] for every run that still holds the clone at `dest`. wait=True: it is giving the clone back
    (its stop steps or its -return unit are going), so launch may wait; False: refuse now. `why` names the command that
    passes. kept_ok: the caller named the clone with --clone, so one a return kept is theirs to take as it stands, and only
    runs that took it as their own pool clone (whose return step may delete it) count; a run on a given clone never does."""
    import role_launch as RL
    me = "python3 src/RimMandrake/rimflow/detached_helper.py"
    out = []
    for rec in all_records(root):
        if os.path.abspath(rec.get("clone") or "") != os.path.abspath(dest) or rec.get("returned"):
            continue
        if kept_ok and not owns_clone(rec):
            continue
        u = rec["unit"]
        st = live_status(rec, runner, now)
        if st in ("launching", "running"):
            out.append((u, False, "run %s is %s in it; it ends with a line in the Conductor log, then its return step "
                                  "gives the clone back: launch again after that" % (u, st)))
        elif st == "dead":
            out.append((u, False, "run %s is recorded running but its unit is gone, so its finish step never ran; to pass: "
                                  "%s finish --unit %s, then %s return --unit %s, then launch again" % (u, me, u, me, u)))
        elif st == "finished" and owns_clone(rec) and os.path.isdir(dest):
            going = [(x, s) for x, s in ((u, RL.unit_state(u, runner=runner)),
                                         (u + "-return", RL.unit_state(u + "-return", runner=runner))) if s not in DEAD_STATES]
            if going:
                out.append((u, True, "run %s is still giving the clone back (%s); to pass: wait for it to end "
                                      "(systemctl --user status %s) and launch again"
                                      % (u, ", ".join("%s %s" % g for g in going), going[-1][0])))
            elif not kept_ok:
                steps = "; ".join(rec.get("return_steps") or []) or "its return step left no steps"
                out.append((u, False, "run %s finished but its return did not give the clone back (%s); to pass: %s "
                                      "return --unit %s (it bundles what is left), or launch with --clone %s to take it "
                                      "as it stands" % (u, fulltext.clip(steps, 160, record_path(u, root)), me, u, dest)))
    return out


def live_holders(dest, runner=subprocess.run, now=None, root=None):
    """-> the units of the runs launching or running in the clone at `dest` (clone_holders' live ones; [] = none). A run
    that is giving the clone back, or dead, is not listed: the launcher's own gate says what passes for those."""
    return [u for u, wait, why in clone_holders(dest, runner, now, root)
            if not wait and why.startswith("run %s is " % u) and " in it; " in why]


CLONE_RETURNER = None   # a test's stand-in for return_clone; None = return_clone


def kept_by_return(held):
    """-> the units among `held` that are finished runs whose return KEPT the clone (units gone, record not returned)."""
    return [u for u, wait, why in held if not wait and why.startswith("run %s finished but its return" % u)]


def hold_until_returned(dest, runner=subprocess.run, sleep=time.sleep, now=None, root=None, kept_ok=False, notes=None):
    """-> None when no run holds `dest` (waiting up to RETURN_WAIT_S while one is giving it back), else the refusal line.
    A fault of form repaired here (RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_FOUR): when every holder is a
    finished run whose return kept the clone, the launcher runs that return itself (the command the refusal names),
    once per holder, appends one NOTE line to `notes`, and checks again. A live, dead or still-returning holder is never
    returned here. A return that keeps the clone again is refused with its own text."""
    waited = 0
    tried = {}
    while True:
        held = clone_holders(dest, runner, now, root, kept_ok)
        if not held:
            return None
        kept = kept_by_return(held)
        if kept and len(kept) == len(held) and not set(kept) & set(tried):
            import form_fault
            for u in kept:
                try:
                    rc, text = (CLONE_RETURNER or return_clone)(u, now=now, runner=runner, root=root)
                except Exception as e:  # noqa: BLE001  a return that raises is said, and the clone stays held
                    rc, text = 1, "return raised %s: %s" % (type(e).__name__, e)
                tried[u] = text
                if notes is not None:
                    notes.append("%sclone %s was held by finished run %s, whose return had kept it -> the launcher ran "
                                 "its return: %s" % (form_fault.NOTE_HEAD, dest, u, fulltext.clip(text, 240, record_path(u, root))))
            continue
        hard = [h for h in held if not h[1]]
        if hard and tried:
            return "refused: clone %s is held: %s" % (dest, " | ".join(
                h[2] + ("; the launcher's own return: %s" % tried[h[0]] if h[0] in tried else "") for h in hard))
        if hard or waited >= RETURN_WAIT_S:
            return "refused: clone %s is held%s: %s" % (
                dest, "" if hard else " after %d s of waiting" % waited, " | ".join(h[2] for h in (hard or held)))
        sleep(RETURN_POLL_S)
        waited += RETURN_POLL_S


def seat_identity(dest):
    """A reused .det clone takes the seat clone's repo-local commit identity, as a new one does (scratch_clone.set_identity;
    RIMMANDRAKE_SET_HELPER_CLONE_NOREPLY_GMAIL_SLIPS_ONTO_PUBLIC). -> its step line; never raises."""
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
        import scratch_clone as SC
        return SC.set_identity(SC.Path(dest))
    except Exception as e:  # noqa: BLE001
        return "identity NOT set: %s: %s" % (type(e).__name__, e)


def resume_clone_name(item, now):
    """The fresh pool clone a resume takes when <ITEM>.det is held by a finished run: <ITEM>.r<epoch>.det."""
    return "%s.r%d.det" % (item, int(now))


def resume_fresh_clone(item, dest, runner=subprocess.run, now=None, root=None):
    """-> the path of a fresh pool clone for a resume, or None to use `dest`. A resume never depends on a clone that may
    vanish (RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT: a resume was refused on a finished run's
    clone, and one given that clone with --clone died at once when the clone was removed under it). Only when every run
    holding `dest` is FINISHED (its return step owns the clone): a live run still refuses (two runs, one clone), and a
    dead one too (its finish never ran, so its work is in that clone and nowhere else)."""
    held = clone_holders(dest, runner, now, root)
    if not held or not all(not wait and why.startswith("run %s finished" % u) for u, wait, why in held):
        return None
    return os.path.join(pool_root(), "clones", resume_clone_name(item, now or time.time()))


def session_bundle(session, root=None):
    """-> (bundle dir, unit) from the newest run record of `session` that names one, else (None, why)."""
    best = None
    for r in all_records(root):
        if session in (r.get("session"), r.get("resume_session")) and r.get("bundle") and \
                (best is None or (r.get("at") or 0) > (best.get("at") or 0)):
            best = r
    if best is None:
        return None, "no run record of session %s names a bundle" % session
    if not os.path.isdir(best["bundle"]):
        return None, "the bundle %s of %s is gone" % (best["bundle"], best["unit"])
    return best["bundle"], best["unit"]


def restore_session_bundle(item, session, clone, restorer=None, root=None):
    """The resumed run's fresh clone takes the work its session left in a bundle. -> one line saying what it restored."""
    bundle, unit = session_bundle(session, root)
    if not bundle:
        return "restored nothing: " + unit
    try:
        if restorer is None:
            import run_store as R
            restorer = R.Effects(R.rules(), R.Store(pool_root())).restore_bundle
        bad = restorer(item, bundle, clone)     # -> the parts that did not come back ([] = all of it)
    except Exception as e:  # noqa: BLE001  a failed restore is said, and the bundle stays where it is
        return "restore of %s (run %s) FAILED: %s: %s; the bundle stays there" % (bundle, unit, type(e).__name__, e)
    if not isinstance(bad, list):
        return "restore of %s (run %s) UNMEASURED: the restorer answered %r, not a list of what failed" % (
            bundle, unit, bad)
    return "restored the work of run %s from %s%s" % (unit, bundle, "; NOT restored: " + "; ".join(bad) if bad else "")


def retired_trees_root():
    """The agent storage root's retired-trees folder (a half-made clone that holds work is moved here, never deleted)."""
    if os.environ.get("RM_RETIRED_TREES"):
        return os.environ["RM_RETIRED_TREES"]
    sys.path.insert(0, os.path.expanduser("~/dev/Lodestar/bin/lib"))
    import agent_storage
    return agent_storage.subdir("retired-trees", create=True)


def clone_holds_work(dest, runner=subprocess.run):
    """True when `dest` (a git clone whose checkout is incomplete) holds anything a replacement would lose: a commit on no
    remote ref, a changed or added or untracked file. A deleted file is not work (HEAD still has it: a half-made checkout
    reads as thousands of deletions). Any git answer that cannot be read counts as work: moved aside, never lost."""
    def git(*a):
        return runner(["git", *a], cwd=dest, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    try:
        if git("rev-parse", "--verify", "-q", "HEAD").returncode == 0:      # no HEAD: no commit to lose
            r = git("rev-list", "--count", "HEAD", "--not", "--remotes")
            if r.returncode or (r.stdout or "").strip() != "0":
                return True
        r = git("status", "--porcelain", "--untracked-files=all")
        if r.returncode:
            return True
        return any(ln[:2] not in (" D", "D ", "DD") for ln in (r.stdout or "").splitlines() if ln.strip())
    except Exception:  # noqa: BLE001
        return True


def move_half_made_aside(dest, name, runner=subprocess.run, now=None):
    """-> one line. `dest` cannot start a unit (its checkout died partway, or it is no clone): moved aside, never deleted.
    One holding work goes to the retired-trees folder; one holding none goes beside the pool's clones (same disk, at once);
    an empty directory is just taken away."""
    stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(now or time.time()))
    is_git = os.path.isdir(os.path.join(dest, ".git"))
    if not is_git and not os.listdir(dest):
        os.rmdir(dest)
        return "an empty directory stood where the clone goes: taken away"
    if clone_holds_work(dest, runner) if is_git else True:
        target = os.path.join(retired_trees_root(), "%s.halfcheckout-%s" % (name, stamp))
        why = "holds work" if is_git else "is no git clone"
    else:
        target = "%s.halfcheckout-%s" % (dest, stamp)
        why = "holds no work"
    shutil.move(dest, target)
    return "%s %s, moved aside to %s" % (dest, why, target)


def take_clone(item, runner=subprocess.run, name=None):
    """-> (clone path, log line). A pool clone named <ITEM>.det (or `name`, a resume's fresh one): made by
    scratch_clone.py, or reused and synced. A clone whose checkout is incomplete (no ./sync at its root: its first checkout
    died partway) or that is no clone is moved aside and made again, said in one line
    (RIMMANDRAKE_REPLACE_HALF_MADE_POOL_CLONE_LAUNCH_FAILED_THRICE: three launches died on `./sync` missing)."""
    name = name or item + ".det"
    if runner is subprocess.run:    # a checkout is gigabytes of file cache: never in a timed unit's own memory limit
        runner = own_cgroup.run
    dest = os.path.join(pool_root(), "clones", name)
    replaced = ""
    if os.path.isdir(dest) and not (os.path.isdir(os.path.join(dest, ".git")) and os.path.isfile(os.path.join(dest, "sync"))):
        replaced = "half-made clone replaced: " + move_half_made_aside(dest, name, runner) + "; "
    if os.path.isdir(os.path.join(dest, ".git")):
        r = runner(["./sync"], cwd=dest, capture_output=True, text=True, timeout=1800, stdin=subprocess.DEVNULL)  # budget: class=call
        said = ((r.stdout or "") + (r.stderr or "")).strip()
        if r.returncode:    # a stale clone builds stale code: refused, as a new clone that fails is
            # (RIMMANDRAKE_REFUSE_STALE_DET_CLONE_WHEN_SYNC_FAILS)
            raise RuntimeError("reused %s but its ./sync failed (exit %d): %s" % (dest, r.returncode, said))
        return dest, "reused %s (sync exit 0: %s; %s)" % (dest, said, seat_identity(dest))
    env = dict(os.environ, RM_SCRATCH_ROOT=pool_root(), RM_SEAT="clones")
    r = runner(["python3", os.path.join(REPO, "src", "RimMandrake", "Utils", "scratch_clone.py"), "clone",
                "detached run for " + item, "--name", name, "--checkout", "--fetch"],
               env=env, capture_output=True, text=True, timeout=10800, stdin=subprocess.DEVNULL)  # budget: class=launch
    if r.returncode or not os.path.isdir(os.path.join(dest, ".git")):
        raise RuntimeError("scratch_clone failed (exit %d): %s" % (r.returncode, ((r.stdout or "") + (r.stderr or ""))))
    return dest, replaced + "made " + dest


def clone_lock_path(dest):
    return os.path.abspath(dest).rstrip("/") + ".lock"


@contextlib.contextmanager
def clone_lock(dest):
    """One launch at a time takes a clone: held from the last holder check to the run's record
    (RIMMANDRAKE_LOCK_DET_CLONE_TAKE_TWO_LAUNCHES_ONE_CLONE: two launches of one item both passed the check)."""
    os.makedirs(os.path.dirname(clone_lock_path(dest)), exist_ok=True)
    with open(clone_lock_path(dest), "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def claude_bin():
    import shutil
    return os.environ.get("RM_DISPATCHER_CLAUDE") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")


INGAME_ITEM = re.compile(r"IN_GAME_(ACCEPTANCE|VISIT)", re.I)     # maturation_dispatch._is_ingame_item's names


def run_game(item, env):
    """-> the game a run drives, for admission (`pipe off game:<g>`): its RM_GAME_INSTANCE, else game a for an in-game
    run (its item names IN_GAME_ACCEPTANCE or IN_GAME_VISIT), else None. The stage is not the test: a steward run at
    stage in_game works offline, and one that needs a game later takes a free one through game_lock, which refuses a
    held game (RIMMANDRAKE_FIX_OFFLINE_STEWARD_REFUSED_BY_GAME_A_WALK_HOLD)."""
    g = ((env or {}).get("RM_GAME_INSTANCE") or "").strip().lower()
    if g:
        return g
    return "a" if INGAME_ITEM.search(str(item or "")) else None


def scope_name(seat, unit):
    """The claude_bounded scope this run's claude lives in (named by CLAUDE_SCOPE_UNIT at launch; role_launch's form)."""
    import role_launch as RL
    return RL.role_scope(seat, unit)


def stop_scope(seat, unit, runner=subprocess.run):
    """KILL the scope's whole cgroup, queue its stop, read its state. -> one line. Never raises.
    Not the RM_ROLE_UNIT marker scan: finish itself runs with the unit's environment and would carry the marker."""
    import role_launch as RL
    scope = scope_name(seat, unit)

    def gone(line):
        return " exit " in line and bool(RL.NOT_FOUND_RX.search(line))
    kill = RL._stop_call(runner, ["systemctl", "--user", "kill", "--signal=SIGKILL", scope], 20)
    if gone(kill):      # the clean finish: claude left its scope and systemd collected it (every run read as an error)
        return "scope %s: already gone (claude left it and systemd collected it)" % scope
    said = [kill, RL._stop_call(runner, ["systemctl", "--user", "stop", "--no-block", scope], 20)]
    said = ["%s: already gone" % s.split(" exit ")[0] if gone(s) else
            s if s.endswith(" ok") else "FAILED " + s for s in said]
    return "scope %s: %s; now %s" % (scope, "; ".join(said), RL.unit_state(scope, runner=runner))


# A stop step's script is resolved when the step runs, never fixed to the launcher's clone
# (RIMMANDRAKE_RUN_FINISH_WITHOUT_LAUNCHER_CLONE_HOLDER_LOST_RESULT: Explosive Knockback's first holder run's finish
# named the clone pilot-launch ran in, deleted by its end: "can't open file", finish never ran, its result read
# "unknown"). The resolver runs the first candidate that exists, with the step's arguments; none left fails naming
# them. No '$' or '%' in it: systemd expands both in an Exec line. No single quote either (shlex.join quotes it whole).
STOP_RESOLVER_MARK = "detached_helper stop resolver"
_RESOLVER = ("import os,sys;a=sys.argv[1:];i=a.index(chr(45)*2);c=[x for x in a[:i] if os.path.isfile(x)];"
             "c or sys.exit(chr(10).join([\"no stop-step script among:\"]+a[:i]));"
             "os.execv(sys.executable,[sys.executable,c[0]]+a[i+1:])#" + STOP_RESOLVER_MARK)


def stop_resolver(candidates, args):
    """-> argv: python runs the first of `candidates` that exists at stop time with `args`."""
    return ["/usr/bin/python3", "-c", _RESOLVER] + list(dict.fromkeys(candidates)) + ["--"] + list(args)


def stop_candidates(rec, name, run_clone_last=False):
    """-> the paths a stop step's script `name` (in src/RimMandrake/rimflow) may run from: the run's own clone (it
    lives until the return, the last step), this launcher's, then the seat clones (wrapup.seat_clones). The return
    deletes the run's clone, so it puts that clone last."""
    rel = os.path.join("src", "RimMandrake", "rimflow", name)
    own = [os.path.join(rec["clone"], rel)] if rec.get("clone") else []
    try:
        import wrapup
        seats = [os.path.join(c, rel) for c in wrapup.seat_clones()]
    except Exception:       # noqa: BLE001  the seat clones are a fallback only
        seats = []
    mine = [os.path.join(HERE, name)]
    return (mine + seats + own) if run_clone_last else (own + mine + seats)


def return_argv(rec):
    """The unit's last ExecStopPost: start the return step in a unit of its own and let go (--no-block). ExecStopPost runs
    under the run's TimeoutStopSec=30, and a bundle of a 3.6 GB clone, a landing and a ./sync take longer than that."""
    me = os.path.abspath(__file__)
    env = ["--setenv", "RM_DISPATCHER_STATE=" + rec["state"], "--setenv", "RIMFLOW_SEAT=" + rec["seat"],
           "--setenv", "AGENT_SEAT=" + rec["seat"]]
    for k in ("RM_DETACHED_POOL", "RM_CONDUCTOR_LOG", "RELENTLESS_ROOT"):
        if os.environ.get(k):
            env += ["--setenv", "%s=%s" % (k, os.environ[k])]
    return ["/usr/bin/systemd-run", "--user", "--quiet", "--collect", "--no-block", "--unit", rec["unit"] + "-return",
            "-p", "RuntimeMaxSec=3600", "-p", "StandardOutput=file:" + rec["out"] + ".return", "-p", "StandardError=inherit",
            *env, *stop_resolver(stop_candidates(rec, os.path.basename(me), run_clone_last=True),
                                 ["return", "--unit", rec["unit"]])]


def owns_clone(rec):
    """True for the pool clone <pool>/clones/<ITEM>.det that launch made or reused itself. A clone the caller gave with
    --clone is theirs, and so is any other path: this step never touches them."""
    how = rec.get("clone_how") or ""
    item = rec.get("item", "")
    base = os.path.basename(os.path.abspath(rec.get("clone") or ""))
    mine = base == item + ".det" or bool(re.fullmatch(re.escape(item) + r"\.r[0-9]+\.det", base))    # a resume's own
    return how.startswith(("made ", "reused ")) and mine and \
        os.path.dirname(os.path.abspath(rec.get("clone") or "")) == os.path.abspath(os.path.join(pool_root(), "clones"))


def other_users(rec, root=None, runner=subprocess.run):
    """Units of other runs that are still going and hold this run's clone. A dead one (unit gone, record "running") holds
    nothing: it used to keep later runs' clones forever."""
    return [o["unit"] for o in all_records(root) if o["unit"] != rec.get("unit") and o.get("clone") == rec.get("clone")
            and live_status(o, runner) in ("launching", "running")]


def clone_busy(clone):
    """True when a process has its cwd in the clone (scratch_clone's own test; this process is not counted)."""
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    import scratch_clone as SC
    return SC.clone_in_use(SC.Path(clone))


# A process that ignores SIGTERM gets SIGKILL after this long. Danger: one that never exits would hold the return step
# (and so the clone) for good; the return unit's own RuntimeMaxSec=3600 is the only other bound.
# budget: danger=a process that never exits holds the return, and so the clone; its reach leaves no record; no record of its run
REAP_TERM_WAIT_S = 5


def _proc_state(pid):
    """-> the pid's /proc state letter, "gone" when /proc has no such pid, or "unknown" when its stat cannot be read."""
    try:
        with open("/proc/%d/stat" % pid, "rb") as f:
            return f.read().rsplit(b")", 1)[1].split()[0].decode("ascii", "replace")
    except FileNotFoundError:
        return "gone"
    except (OSError, IndexError):
        return "unknown"


def _alive(pid):
    """True unless the pid is gone or a zombie (a zombie holds no cwd and no clone); a stat that cannot be read is alive:
    could not look is never "gone"."""
    return _proc_state(pid) not in ("gone", "Z")


def scan_marked_live(marker, since=None, proc="/proc"):
    """role_launch.scan_marked, less its zombie blind spot: a zombie's environ cannot be read, and scan_marked calls the
    whole scan blind for it (measured 2026-11-19: one `[python3] <defunct>` of this uid made every scan blind). A zombie
    holds no cwd and runs nothing, so it is ruled out here. -> (pids, None) or (pids, why blind)."""
    import role_launch as RL
    want = ("RM_ROLE_UNIT=%s" % marker).encode()
    try:
        names = [n for n in os.listdir(proc) if n.isdigit() and int(n) != os.getpid()]
    except OSError as e:
        return [], "%s unlistable (%s)" % (proc, type(e).__name__)
    btime = RL._boot_time(proc) if since is not None else None
    uid, out, todo, why = os.getuid(), [], names, None
    for attempt in range(RL.SCAN_RETRIES + 1):      # a process mid-exec is unreadable for a moment (scan_marked's retry)
        if attempt:
            time.sleep(RL.SCAN_RETRY_S)
        again, why = [], None
        for n in todo:
            try:
                with open(os.path.join(proc, n, "environ"), "rb") as f:
                    env = f.read()
            except FileNotFoundError:
                continue
            except OSError:
                if not _alive(int(n)):
                    continue                    # a zombie or gone
                try:
                    if os.stat(os.path.join(proc, n)).st_uid != uid:
                        continue
                except OSError:
                    continue
                started = RL._started_at(proc, n, btime) if btime is not None else None
                if started is not None and started < since - RL.SINCE_SLACK_S:
                    continue
                why = why or "pid %s environ unreadable" % n
                again.append(n)
                continue
            if want in env.split(b"\0"):
                out.append(int(n))
        todo = again
        if not todo:
            break
    return out, why


def reap_leftovers(rec, scan=None, kill=os.kill, alive=_alive, sleep=time.sleep):
    """End every process a finished run left running: each carries the run's RM_ROLE_UNIT=<unit> marker, whatever
    cgroup it is in (run_selftests.py puts each test in a scope of rm-harness.slice, outside the run's own cgroup, so
    stop_scope never reached it: RIMMANDRAKE_REAP_SELFTEST_CHILD_ENDED_RUN_LEFT_HOLDING_CLONE). TERM, then KILL after
    REAP_TERM_WAIT_S. A blind scan ends nothing. -> one step line, or "" when the run left nothing running."""
    try:
        pids, blind = (scan or scan_marked_live)(rec["unit"], since=rec.get("at"))
    except Exception as e:  # noqa: BLE001
        pids, blind = [], "%s: %s" % (type(e).__name__, e)
    if blind:
        return "leftover scan blind (%s): no process ended" % blind
    pids = [p for p in pids if p != os.getpid()]
    if not pids:
        return ""
    for p in pids:
        try:
            kill(p, signal.SIGTERM)
        except OSError:
            pass
    waited = 0.0
    while waited < REAP_TERM_WAIT_S and any(alive(p) for p in pids):
        sleep(0.1)
        waited += 0.1
    hard = [p for p in pids if alive(p)]
    for p in hard:
        try:
            kill(p, signal.SIGKILL)
        except OSError:
            pass
    return "ended %d leftover process(es) of the run (pids %s%s)" % (
        len(pids), ", ".join(str(p) for p in pids), "; KILL after TERM: %s" % ", ".join(map(str, hard)) if hard else "")


def evict_clone(item, clone, before=None):
    """-> (bundle dir or None, why the clone stayed or None). relentless Effects.remove_clone: every commit, stash and
    dirty file goes to the store's bundles first, then the clone is parked as a warm spare or removed. A bundle that
    cannot be made keeps the clone (and alarms on the relentless journal)."""
    import run_store as R
    store = R.Store(pool_root())
    fx = R.Effects(R.rules(), store)
    out = fx.remove_clone({"clone": clone, "item": item}, before)
    if os.path.isdir(clone):
        return out, "the clone stayed: its bundle or its removal failed (alarm on the relentless journal)"
    return out, None


def _tail(r, n=140):
    return ((getattr(r, "stdout", "") or "") + (getattr(r, "stderr", "") or "")).strip()[-n:]


def kept_why(rec, reason, root=None):
    """A finished run's return that keeps its clone writes the reason into return_steps (never `returned`), so a later
    refusal names it instead of "its return step left no steps". The step leaves the clone's path out: the refusal
    names the clone, and a long path pushed the reason past the refusal's clip. -> "kept <clone>: <reason>"."""
    rec["return_steps"] = ["kept: " + reason]
    write_record(rec, root)
    return "kept %s: %s" % (rec["clone"], reason)


def return_clone(unit, now=None, runner=subprocess.run, evictor=None, busy=None, publish_ledger=True, root=None, log_path=None,
                 scan=None):
    """The run's last step. -> (exit code, text). Gives the pool clone back after landing what can land and bundling the
    rest; keeps it (exit 1) when a bundle cannot be made. Once per run: a second call changes nothing."""
    now = now or time.time()
    rec = read_record(unit, root)
    if not rec:
        return 2, "no record for %s" % unit
    if rec.get("returned"):
        return 0, "already returned %s" % unit
    clone, seat, item = rec["clone"], rec["seat"], rec["item"]
    if not owns_clone(rec):
        return 0, "left alone: %s is not a pool clone this helper made (%s)" % (clone, rec.get("clone_how", "-"))
    if rec.get("status") != "finished":
        return 0, "kept %s: the run is %s, not finished (its finish step has not recorded it)" % (clone, rec.get("status"))
    mates = other_users(rec, root, runner)
    if mates:
        return 0, kept_why(rec, "still in use by %s" % ", ".join(mates), root)
    if not os.path.isdir(clone):
        rec.update(returned=now, return_steps=["clone already gone"])
        write_record(rec, root)
        return 0, "returned %s: the clone was already gone" % unit
    reaped = reap_leftovers(rec, scan)       # the run's own leftovers first: they are not "a process working in it"
    if (busy or clone_busy)(clone):
        return 0, kept_why(rec, "a process is working in it%s" % ("; " + reaped if reaped else ""), root)
    steps = [reaped] if reaped else []

    # budget: danger=a hung return step holds the clone; longest=289s (the whole return, an upper bound; 1151 return units, user
    # budget: journal, 14 days to 2026-11-24)
    def run(argv, what, timeout=3000):
        r = runner(argv, cwd=clone, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        steps.append("%s exit %d" % (what, r.returncode))
        return r
    land = os.path.join(clone, "src", "RimMandrake", "Utils", "conversations_land.py")
    if os.path.exists(land):
        r = run(["python3", land, "--apply"], "conversations")
        if r.returncode:
            steps.append("conversations: " + _tail(r))
    shard = "infrastructure/state/ledger/events/%s.jsonl" % seat
    if publish_ledger:
        shards = dirty_shards(clone, seat, lambda argv, **kw: run(argv, "shard status", 60))
        if shards:
            r = run(["./publish", "-m", "ledger: %s returned its clone" % item] + shards, "publish")
            m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", _tail(r, 400))
            steps.append("publish " + (m.group(1)[:10] if m else "FAILED: " + _tail(r, 100)))
    run(["./sync"], "sync")
    told = []

    def before(bundle):     # the clone still stands: say where its leftovers went
        told.append(bundle)
        if not publish_ledger:  # its dirty ledger lines ride in the bundle; a note's publish would send them upstream too
            return
        text = ("DETACHED run %s left work no remote had; its clone %s is bundled at %s and goes back to the pool. NEXT: "
                "restore it from that bundle (run_store.Effects.restore_bundle) if the work is still wanted." % (unit, clone, bundle))
        r = run(["python3", os.path.join(clone, "src", "RimMandrake", "rimflow", "cli.py"), "note", item, "--text", text,
                 "--seat", seat, "--why", "detached run clone returned"], "bundle note", 120)
        if r.returncode == 0:
            r = run(["./publish", "-m", "ledger: %s clone bundled" % item, shard], "publish note")
            m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", _tail(r, 400))
            steps.append("publish note " + (m.group(1)[:10] if m else "FAILED: " + _tail(r, 100)))
    try:
        bundle, kept = (evictor or evict_clone)(item, clone, before)
    except Exception as e:  # noqa: BLE001  never lose the clone to a surprise: it stays
        bundle, kept = None, "eviction raised: %s" % str(e)
    steps.append("bundle " + (bundle or "none (nothing left to bundle)"))
    if kept:
        steps.append("KEPT: " + kept)
    # the return works for seconds to minutes on the record it read at its start. Another step of the same run (the
    # continuation step's "waits for the account switch") writes the record meanwhile: this write adds the return's
    # own fields to the record as it is NOW, and takes nothing away
    latest = read_record(unit, root)
    if latest is not None:      # a record that cannot be read now: the return keeps the copy that it read at its start
        rec = {**rec, **latest}
    rec.update(return_steps=steps, bundle=bundle)
    if not kept:
        rec["returned"] = now
    write_record(rec, root)
    if bundle or kept:
        try:
            conductor_line("%s on %s: clone %s %s. %s. READ: rimflow show %s." % (
                unit, item, clone, "KEPT" if kept else "returned, leftovers bundled at %s" % bundle, "; ".join(steps), item),
                now, log_path)
        except Exception as e:  # noqa: BLE001
            steps.append("conductor log FAILED: %s" % e)
    return (1 if kept else 0), "%s %s: %s" % ("KEPT" if kept else "RETURNED", unit, "; ".join(steps))


# budget: danger=a clone is taken from a run whose launcher still reads it; ends no work: the sweep leaves the clone for a later
# budget: sweep
def return_all(runner=subprocess.run, evictor=None, busy=None, publish_ledger=True, root=None, now=None, grace_s=3600):
    """Every finished run whose pool .det clone is still standing and not returned (a return step that never ran), except
    a run that ended less than grace_s ago: whoever launched it may still be reading the clone."""
    out, worst = [], 0
    now = now or time.time()
    for u in record_units(root):
        rec = read_record(u, root)
        if is_record(rec, u) and rec.get("status") == "finished" and not rec.get("returned") and owns_clone(rec) \
                and os.path.isdir(rec["clone"]) and now - (rec.get("ended") or rec.get("at") or 0) >= grace_s:
            rc, text = return_clone(rec["unit"], now=now, runner=runner, evictor=evictor, busy=busy, publish_ledger=publish_ledger, root=root)
            out.append(text)
            worst = max(worst, rc)
    return worst, "\n".join(out) or "no finished run holds a pool clone"


# RIMMANDRAKE_GIVE_DETACHED_UNITS_WINDOWS_PATH_PYTHON_EXE_VANISHED: a launcher started from a timer has no /mnt/c on PATH
# and no WSL_INTEROP, so its unit could not run python.exe, tasklist.exe or ./game (FlowWorks visit 1, 2026-11-15).
WSL_FLAG = "/proc/sys/fs/binfmt_misc/WSLInterop"
WSL_SOCKET = "/run/WSL/1_interop"
WIN_DIRS = ("/mnt/c/Windows/System32", "/mnt/c/Windows", "/mnt/c/Windows/System32/WindowsPowerShell/v1.0")
WIN_APPS_GLOB = "/mnt/c/Users/*/AppData/Local/Microsoft/WindowsApps"


def unit_path(base, claude, exists=os.path.exists, isdir=os.path.isdir, globber=glob.glob):
    """-> the unit's PATH: claude's dir, the launcher's PATH, and on WSL the Windows dirs it lacks, each once."""
    parts = [os.path.dirname(claude)] + (base or "/usr/bin:/bin").split(":")
    if exists(WSL_FLAG):
        parts += [d for d in WIN_DIRS if isdir(d)] + sorted(d for d in globber(WIN_APPS_GLOB) if isdir(d))
    out = []
    for d in parts:
        if d and d not in out:
            out.append(d)
    return ":".join(out)


def unit_interop(environ=os.environ, exists=os.path.exists):
    """-> the WSL interop socket the unit gets: the launcher's when it is alive, else the machine's; None off WSL."""
    v = environ.get("WSL_INTEROP")
    if v and exists(v):
        return v
    return WSL_SOCKET if exists(WSL_SOCKET) else None


PROJECTS = os.path.expanduser("~/.claude/projects")
SESSION_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def project_dir(cwd, projects=None):
    """claude's transcript folder for a working directory: every character but a letter or digit becomes '-'."""
    return os.path.join(projects or PROJECTS, re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd)))


def find_transcript(session_id, projects=None):
    """-> the newest <session>.jsonl under any project folder, or None."""
    if not SESSION_RE.match(session_id or ""):
        return None
    hits = glob.glob(os.path.join(projects or PROJECTS, "*", session_id + ".jsonl"))
    return max(hits, key=os.path.getmtime) if hits else None


def carry_session(session_id, clone, projects=None):
    """Each run gets its own pool clone: copy the holder's transcript into that clone's project folder (a newer copy
    already there is kept) and refuse a session with no transcript. claude 2.x resumed a session from another
    directory without the copy (measured 2026-11-15, /tmp/rh_a -> /tmp/rh_b); the copy keeps the run independent of
    that lookup. -> the path, or None."""
    src = find_transcript(session_id, projects)
    if not src:
        return None
    dst = os.path.join(project_dir(clone, projects), session_id + ".jsonl")
    if os.path.abspath(src) != os.path.abspath(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            shutil.copy2(src, dst)
    return dst


def context_tokens(transcript):
    """-> the context the session's last main-thread turn read (input + cache creation + cache read + output), or
    None. A sidechain (a subagent's turn) is not the holder's context."""
    last = None
    try:
        with open(transcript, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                u = (ev.get("message") or {}).get("usage") if isinstance(ev, dict) else None
                if isinstance(u, dict) and not ev.get("isSidechain"):
                    last = u
    except OSError:
        return None
    if not last:
        return None
    return sum(int(last.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                                "cache_read_input_tokens", "output_tokens"))


def session_of(unit, root=None, projects=None):
    """-> (session id, context tokens) of a finished run, from claude's result JSON and its transcript; (None, None)
    when unreadable."""
    rec = read_record(unit, root) or {}
    sid = rec.get("session_id")
    if not sid and rec.get("out"):
        try:
            with open(rec["out"], encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            m = re.search(r'"session_id"\s*:\s*"([A-Za-z0-9-]{8,64})"', text)
            sid = m.group(1) if m else None
        except OSError:
            sid = None
    if not sid:
        return None, None
    t = find_transcript(sid, projects)
    return sid, (context_tokens(t) if t else None)


def run_session(unit, root=None, projects=None):
    """-> (session id, context tokens, how) of a run, also one KILLED before it wrote a result (session_of then reads
    nothing): the transcript in its clone's project folder written during the run (from its start to 10 min after its
    end), the newest one. (None, None, why) when none is found (resume a voided judge:
    design/specs/2026-11-23-resume-voided-blind-judge/boundary.md)."""
    sid, ctx = session_of(unit, root, projects)
    if sid:
        return sid, ctx, "its result file"
    rec = read_record(unit, root)
    if not isinstance(rec, dict) or not rec.get("clone"):
        return None, None, "no run record with a clone for %s" % unit
    t0, t1 = [rec.get(k) if _num(rec.get(k)) else None for k in ("at", "ended")]
    d = project_dir(rec["clone"], projects)
    hits = []
    for p in glob.glob(os.path.join(d, "*.jsonl")):
        m = os.path.getmtime(p)
        if SESSION_RE.match(os.path.basename(p)[:-len(".jsonl")]) and (t0 is None or m >= t0) and \
                (t1 is None or m <= t1 + 600):
            hits.append((m, p))
    if not hits:
        return None, None, "no transcript in %s written during the run" % d
    p = max(hits)[1]
    return os.path.basename(p)[:-len(".jsonl")], context_tokens(p), "its clone's transcript %s" % p


def session_records(session, root=None):
    """-> the run records of `session` (their `session`, their `resume_session`, or the session_id in a result file of a
    record from before `session` was kept), oldest first. OSError when the records cannot be read."""
    out = []
    for r in all_records(root):
        sid = r.get("session") or None
        if sid is None and r.get("out"):
            try:
                with open(r["out"], encoding="utf-8", errors="replace") as fh:
                    m = re.search(r'"session_id"\s*:\s*"([A-Za-z0-9-]{8,64})"', fh.read())
                sid = m.group(1) if m else None
            except OSError:
                sid = None
        if session in (sid, r.get("resume_session")) and _num(r.get("at")):
            out.append(r)
    return sorted(out, key=lambda r: r["at"])


def earlier_cap(session, root=None):
    """-> (cap, unit) of the newest run record of `session` (session_records), or (None, why) when no record holds it or
    the newest one has no numeric budget_usd. Never a fallback number: a resume that cannot read its cap is refused by
    its caller."""
    try:
        recs = session_records(session, root)
    except OSError as e:
        return None, "the run records are unreadable (%s)" % e
    if not recs:
        return None, "no run record holds session %s" % session
    best = recs[-1]
    if not _num(best.get("budget_usd")):
        return None, "the newest run record of session %s (%s) has no numeric budget_usd" % (session, best["unit"])
    return float(best["budget_usd"]), best["unit"]


def _control_settings(rec):
    import control as C
    return C.claude_settings(clone=rec.get("clone"))


def game_env(env):
    """-> the run's RM_ variables, plus the whole environment of the game it names (game_instance.env: its port, token,
    folders and the WSLENV that carries them into python.exe) when RM_GAME_INSTANCE names a game other than a. Without
    WSLENV a python.exe child never sees the name, its bridge client falls back to game a's port 5174, and a game-b run
    drives game a (2026-11-20, RIMMANDRAKE_CARRY_WSLENV_INTO_B_RUNS_PROOF_HIT_A). A bad name raises
    ValueError (game_instance.InstanceError)."""
    env = dict(env or {})
    name = (env.get("RM_GAME_INSTANCE") or "").strip().lower()
    if name in ("", "a"):
        return env
    utils = os.path.join(REPO, "src", "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import game_instance
    return dict(env, **game_instance.env(name))


AGENT_ENV = "RM_CLAUDE_AGENT"     # the run starts as `claude --agent <name>`: .claude/agents/<name>.md is its system prompt


def agent_repair(rec, clone, msg):
    """A run whose env names an agent with no .claude/agents/<name>.md in its clone: a fault of form, repaired here. The
    agent is dropped from the env (no --agent), the record says why, and the brief gets the role-file line. -> msg."""
    name = (rec.get("env") or {}).get(AGENT_ENV)
    if not name:
        return msg
    path = os.path.join(clone or "", ".claude", "agents", "%s.md" % name)
    if re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) and os.path.isfile(path):
        return msg
    rec["env"] = {k: v for k, v in rec["env"].items() if k != AGENT_ENV}
    rec["agent_dropped"] = "agent %r has no %s in the clone: launched without --agent" % (name, path)
    return ("Your launch could not start you as agent %s (no `.claude/agents/%s.md` in your clone). If that file exists "
            "on origin/main, read it in full first, as your role file.\n\n" % (name, name)) + msg


def launch_argv(rec, msg, claude):
    """role_launch.launch_argv's shape, plus ExecStopPost=finish so the outcome is recorded even on a kill."""
    clone, unit, seat = rec["clone"], rec["unit"], rec["seat"]
    bounded = os.path.join(clone, "src", "RimMandrake", "Utils", "claude_bounded.sh")
    bound = int(rec["max_s"]) + GRACE_S if rec.get("max_s") else None     # None: unbounded
    path = unit_path(os.environ.get("PATH"), claude)
    soc = unit_interop()
    finish = shlex.join(stop_resolver(stop_candidates(rec, os.path.basename(os.path.abspath(__file__))),
                                      ["finish", "--unit", unit]))
    wrapup = "-+" + shlex.join(stop_resolver(stop_candidates(rec, "wrapup.py"),
                                             ["unit", "--unit", unit, "--seat", seat, "--clone", clone]))
    back = "-" + shlex.join(return_argv(rec))
    via_file = rec.get("brief_file")    # the brief: claude -p reads it from stdin (StandardInput=file:), never argv
    cmd = [bounded, "-p"] + ([] if via_file else [msg]) + [
           "--model", _RL().launch_model(rec["model"]), "--name", "DETACHED %s %s" % (seat, rec["item"]),
           "--output-format", "json", "--dangerously-skip-permissions",
           "--settings", _control_settings(rec)]     # its PostToolUse hook: the stop channel (`pipe stop --write-now`)
    if rec.get("resume_session"):       # a mod's holder session (modledger.resume_plan), carried into this clone
        cmd += ["--resume", rec["resume_session"]]
    if (rec.get("env") or {}).get(AGENT_ENV):   # its role file is the system prompt: no Read of it, ~15k fewer a request
        cmd += ["--agent", rec["env"][AGENT_ENV]]
    # the spend cap is enforced from outside: the agent is never told its spend (owner 2026-11-16, spend_watchdog.py);
    # --budget-usd 0 launches with no cap at all
    if rec["budget_usd"] > 0:
        import spend_watchdog
        cmd = spend_watchdog.wrap(cmd, rec["budget_usd"], python="python3")
        mine = os.path.join(clone, "src", "RimMandrake", "rimflow", "spend_watchdog.py")
        cmd[1] = mine if os.path.exists(mine) else cmd[1]     # the clone's own copy, as with claude_bounded.sh
    return ["--user", "--quiet", "--collect",      # systemd-run's arguments; control.launch_unit names the unit
            # append:, never file: — file: hands every ExecStopPost the file at offset 0 and finish's line overwrote the
            # head of claude's JSON (RIMMANDRAKE_KEEP_RUN_RESULT_WHOLE_FINISH_WRITES_OVER); finish also moves its own
            # output off these files (keep_off_result), so the JSON stays whole and alone
            "-p", "StandardOutput=append:" + rec["out"], "-p", "StandardError=append:" + rec["err"],
            *(["-p", "StandardInput=file:" + via_file] if via_file else []),
            "-p", "ExecStopPost=" + finish,
            "-p", "ExecStopPost=" + wrapup,     # the census of what it left (wrapup.py), after finish recorded it
            "-p", "ExecStopPost=" + back,       # last: the pool clone goes back, bundled (return_clone)
            "-p", "WorkingDirectory=-" + clone,    # "-": a gone clone is not fatal, so ExecStopPost still runs (in /)
            "--setenv", "AGENT_SEAT=" + seat, "--setenv", "RIMFLOW_SEAT=" + seat,
            *(sum((["--setenv", "%s=%s" % kv] for kv in run_tmp.env(rec["tmp"]).items()), []) if rec.get("tmp") else []),
            "--setenv", "CLAUDE_SCOPE_UNIT=" + scope_name(seat, unit)[:-len(".scope")],
            "--setenv", "RM_ROLE_UNIT=" + unit, "--setenv", "RM_DETACHED_UNIT=" + unit,
            "--setenv", "RM_DISPATCHER_STATE=" + rec["state"],
            *sum((["--setenv", "%s=%s" % kv] for kv in sorted(game_env(rec.get("env")).items())), []),
            *(["--setenv", "BASH_MAX_TIMEOUT_MS=%d" % BASH_MAX_MS] if BASH_MAX_MS else []),
            *(["--setenv", "CLAUDE_SCOPE_RUNTIME_MAX=%d" % bound, "-p", "RuntimeMaxSec=%d" % bound] if bound else []),
            # the ExecStopPost steps run inside this bound: finish's note (120 s) and publish (300 s), wrapup and the
            # return start; 30 s killed ten finishes in a week, measured 2026-11-15 (RIMMANDRAKE_COVER_FINISH_IN_TIMEOUTSTOPSEC_TEN_KILLED)
            "-p", "TimeoutStopSec=%d" % STOP_S,
            *(["--setenv", "WSL_INTEROP=" + soc] if soc else []),
            "--setenv", "PATH=" + path, "--"] + cmd


# A brief that names a skill's folder (skills/<name>/ or skills\<name>\, in this repo or ~/dev): most project skills are not
# registered, so a helper reads only the skills its brief names by path (owner, 2026-11-19). skills/BY_WORK.md alone is the map,
# not a skill. Boundary page: design/specs/2026-11-19-brief-skill-paths/boundary.md.
SKILL_PATH = re.compile(r"skills[/\\][A-Za-z0-9][A-Za-z0-9_.-]*[/\\]")


def skill_path_warning(brief):
    """-> one WARNING line when the brief names no skill path, else None. It refuses nothing."""
    if SKILL_PATH.search(brief or ""):
        return None
    return ("WARNING: the brief names no skill path (skills/<name>/SKILL.md); the helper sees no unregistered skill. "
            "Name the paths for its kind of work from skills/BY_WORK.md")


def prose_after(brief, item):
    """-> the faults of the brief's new sentences with their repairs, "" for none (Utils/guiding_prose.py; page
    design/specs/2026-11-23-guiding-prose-check/boundary.md). Run by main() after the start. It refuses nothing."""
    try:
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import guiding_prose
        return guiding_prose.after_launch(brief, item)
    except Exception as e:  # noqa: BLE001  the run has started
        return "GUIDING PROSE: UNMEASURED, the check did not load (%s: %s). The run has started." % (type(e).__name__, e)


# budget: danger=a stopped switching plan holds every launch; ends no work: an older notice is not obeyed
DRAIN_NOTICE_FRESH_S = 20 * 60     # switching_plan.py writes its notice every 5 min: an older one means its timer stopped


def drain_refusal(now, extra=None, resume_session=None, path=None):
    """-> why a NEW run may not start now, or None. While the switching plan drains an account (its fresh notice reads
    soft with drain true), live runs finish on it and no new run starts there: a switch stops every Claude process, and
    a run started now would be killed by it (design/specs/2026-11-20-account-drain/boundary.md). A continuation of a
    live run, or a resume of its session, is that run finishing and goes, unless the account is at its line (the notice's
    `account_end`: its runs were told to save and end, page design/specs/2026-11-24-account-end/boundary.md). Between the
    warning line and the line nothing is refused: the notice then carries only a warning (account_warning). While the
    fleet is stopped (state stop) nothing starts. An unreadable or stale notice refuses
    nothing (a dead plan timer must not hold every launch)."""
    carried = bool((extra or {}).get("continued_from") or resume_session)
    p = path or os.path.join(os.environ.get("RM_SWITCH_PLAN_DIR") or "/mnt/d/ClaudeWork/rimmandrake/switching_plan",
                             "notice.json")
    try:
        with open(p, encoding="utf-8") as f:
            n = json.load(f)
    except (OSError, ValueError):
        return None
    at = _epoch(n.get("at")) if isinstance(n, dict) else None
    if not (isinstance(n, dict) and at is not None and now - at <= DRAIN_NOTICE_FRESH_S):
        return None
    if n.get("state") == "stop":    # the fleet is stopped on an account that is out: a run here would take it to zero
        return ("refused: the account %s is out (switching plan notice since %s): the fleet is stopped and nothing starts "
                "until an account resets (`python3 src/RimMandrake/Utils/switching_plan.py status` shows it)." % (
                    n.get("account") or "?", n.get("since") or "?"))
    if not (n.get("state") == "soft" and n.get("drain")):
        return None
    if carried and not n.get("account_end"):
        return None
    return ("refused: the account %s is draining (switching plan notice since %s): live runs finish on it and no new "
            "run starts until the switch. Launch again after it (`python3 src/RimMandrake/Utils/switching_plan.py "
            "status` shows it). Why: %s" % (n.get("account") or "?", n.get("since") or "?",
                                             " ".join(str(n.get("why") or "").split())))


def account_warning(now, path=None):
    """-> the account's warning that a run starting now gets in its start package, or None. The switching plan's fresh
    notice carries it while the live account is between its warning line and its line (switching_plan.write_notice):
    the run saves a note, publishes what is done and keeps working. An unreadable or stale notice adds nothing."""
    p = path or os.path.join(os.environ.get("RM_SWITCH_PLAN_DIR") or "/mnt/d/ClaudeWork/rimmandrake/switching_plan",
                             "notice.json")
    try:
        with open(p, encoding="utf-8") as f:
            n = json.load(f)
    except (OSError, ValueError):
        return None
    at = _epoch(n.get("at")) if isinstance(n, dict) else None
    if not (isinstance(n, dict) and at is not None and now - at <= DRAIN_NOTICE_FRESH_S):
        return None
    w = n.get("warning")
    return w if isinstance(w, str) and w.strip() else None


def card_refusal(item, brief, events_dir=None):
    """-> None, or the text naming what a brief on a by-card item lacks: a picked option's description verbatim. The launch
    no longer refuses on it (card_repair adds the text);
    (RIMMANDRAKE_RECORD_CARD_OPTION_TEXT_LABEL_LOST_THE_ART: "needs bigger art" was retold from memory as "check if the
    sprite is blurry", and no art was made). Whitespace and quote style aside, the description must be in the brief."""
    import card_capture
    cards = card_capture.item_cards(item, events_dir=events_dir or os.path.join(REPO, EVENTS_REL))
    missing = card_capture.brief_missing(brief, cards)
    if not missing:
        return None
    return ("refused: %s was decided by card, and the brief does not carry the picked option's description verbatim:\n%s\n"
            "Smallest fix: paste it into the brief, word for word (e.g. under \"What the card said\"); the card's whole "
            "text: python3 src/RimMandrake/rimflow/card_capture.py show %s"
            % (item, "\n".join("  \u00ab%s\u00bb" % d for d in missing), item))


def card_repair(item, brief, events_dir=None):
    """-> (brief, added): the brief with "## What the card said" and each of the item's cards (as a launched agent may
    read them) appended when a picked option's description is not in it, else unchanged. The launch adds the card's
    words itself and never refuses for their lack, for every caller, a hand launch included (owner 2026-11-20: "The
    system should not be refusing needed items."; RIMMANDRAKE_STOP_GATES_DEMANDING_OWNER_WORDS_HE_ALREADY_SPOKE).
    A card store that cannot be read leaves the brief as it was: the launch goes on."""
    try:
        import card_capture as CC
        cards = CC.item_cards(item, events_dir=events_dir or os.path.join(REPO, EVENTS_REL))
        if not CC.brief_missing(brief, cards):
            return brief, False
        return ("%s\n\n%s\n\nThe owner decided this item by card; its whole text, word for word:\n\n%s\n" % (
            brief.rstrip("\n"), CC.HEADING, "\n\n".join(CC.flatten(c, brief=True) for c in cards))), True
    except Exception as e:  # noqa: BLE001
        print("launch: %s: the card text could not be read (%s: %s); the brief goes as written"
              % (item, type(e).__name__, e), file=sys.stderr)
        return brief, False


def card_footer(item, events_dir=None):
    """-> the footer lines naming each consequence the item's cards state ("needs X"): work owed at close. "" if none."""
    import card_capture
    owed = []
    for c in card_capture.item_cards(item, events_dir=events_dir or os.path.join(REPO, EVENTS_REL)):
        owed += [x for x in card_capture.consequences(c) if x not in owed]
    if not owed:
        return ""
    return ("- This item was decided by card, and the picked option states work owed: %s. Each is yours to do or to file;"
            " your close's --why must name where each was done or filed (`rimflow close` refuses otherwise).\n"
            % "; ".join(owed))


def command_lines(item, seat):
    """-> the run's command lines (brief_commands.filled). A launch never fails on them: what raised is said in the text."""
    try:
        import brief_commands
        return brief_commands.filled(item, seat)["text"]
    except Exception as e:  # noqa: BLE001
        return ("- could not look: the command lines of this run could not be made (%s: %s): run "
                "`python3 src/RimMandrake/rimflow/cli.py --help`\n" % (type(e).__name__, e))


def mark_fresh(rec, brief, session=None, root=None):
    """Return the fresh-start role and leave it on the record's env so a resume or continuation gets no history.
    With a session, read the role from its earlier runs on this item if the brief and env do not say it.
    A role that cannot be read marks nothing and is said."""
    try:
        import item_packet
        role = item_packet.role_of(brief, rec.get("env"))
        for r in session_records(session, root) if session and not role else ():
            if r.get("item") != rec.get("item") or role:
                continue
            first = ""
            if r.get("brief_src") and os.path.isfile(r["brief_src"]):
                with open(r["brief_src"], encoding="utf-8", errors="replace") as fh:
                    first = fh.read()
            role = item_packet.role_of(first, r.get("env"))
        if role:
            rec["env"] = dict(rec.get("env") or {}, **{item_packet.ROLE_ENV: role})
        return role
    except Exception as e:  # noqa: BLE001
        print("launch: the fresh-start role could not be read (%s: %s)" % (type(e).__name__, e), file=sys.stderr)


def item_history(brief, item, clone, env=None):
    """-> the item packet (item_packet.packet) of this run, or one line for a role that starts fresh (blind judge, fresh reader,
    examiner, challenger, coverage judge): no history for it. A launch never fails on it: what raised is said in the text.
    Page design/specs/2026-11-23-item-packet/boundary.md."""
    try:
        import item_packet
        role = item_packet.role_of(brief, env)
        if role:
            return "\n\n---\nYou start fresh (%s): this brief holds no history of the item.\n" % role
        return "\n\n---\n" + item_packet.packet(item, item_packet.gather(item, clone))["text"]
    except Exception as e:  # noqa: BLE001
        return ("\n\n---\nITEM PACKET of %s: could not look (%s: %s): run "
                "`python3 src/RimMandrake/rimflow/cli.py show %s`\n" % (item, type(e).__name__, e, item))


def brief_message(brief, item, seat, clone, max_s=None, env=None):
    """-> the whole text a detached run is given: the brief, the item's history (item_history: item_packet), the footer, its
    cards' owed work, its command lines."""
    return (brief.rstrip() + item_history(brief, item, clone, env)
            + FOOTER.format(clone=clone, item=item, seat=seat,
                            bound_text=("Wall-time bound: %d s" % max_s) if max_s else "no wall-time bound")
            + card_footer(item) + command_lines(item, seat))


# budget: danger=a hung launch check holds the launch; never reached in the 14 days to 2026-11-24; no record of its run
def launch_check_refusal(item_text, cwd, runner=subprocess.run, timeout_s=120):
    """-> (refusal text or None, notes): the item's `## launch-checks` block run in the run's clone before the unit starts
    (GATE_FIRST, RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES). notes: one "launch check did not run: ..." line
    per check that could not run; those never refuse."""
    import launch_checks as LC
    res = LC.run(LC.parse(item_text), cwd, timeout_s=timeout_s, runner=runner)
    notes = ["launch check did not run: " + d for d in res["did_not_run"]]
    if res["ok"]:
        return None, notes
    out = ["refused: launch check: %d of the item's declared checks refuse this launch (%d ms)"
           % (len(res["refusals"]), res["ms"])]
    for r in res["refusals"]:
        out += ["- %s" % r["check"], "  evidence: %s" % r["evidence"].replace("\n", "\n    "),
                "  would pass: %s" % r["would_pass"], "  smallest fix: %s" % r["smallest_fix"]]
    return "\n".join(out + notes), notes


def item_text(clone, item):
    """-> the item's live prose as the run's clone holds it, then the `spec` of each event that filed it (a program's
    filer writes its `## launch-checks` block there: spawn --spec). "" when neither exists: no launch checks."""
    out = []
    try:
        with open(os.path.join(clone, "infrastructure", "state", "items", item + ".md"), encoding="utf-8") as fh:
            out.append(fh.read())
    except OSError:
        pass
    for rel in local_shards(item, clone):
        try:
            with open(os.path.join(clone, rel), encoding="utf-8", errors="replace") as fh:
                for ln in fh:
                    if item not in ln:
                        continue
                    try:
                        ev = json.loads(ln)
                    except ValueError:
                        continue
                    if (isinstance(ev, dict) and ev.get("spec") and item in filed_ids([ln])
                            and item in (ev.get("id"), ev.get("name"))):
                        out.append(str(ev["spec"]))
        except OSError:
            continue
    return "\n".join(out)


def parse_max_s(v):
    """None, 0, "", "none", "0" -> None (unbounded); else whole seconds (ValueError on junk)."""
    if v is None or str(v).strip().lower() in ("", "none", "0", "infinity", "unbounded"):
        return None
    return int(v)


class _NoShadow(object):
    """ticket_preflight could not be imported: every check below runs exactly as before."""

    def __init__(self, why):
        self.why, self.run_id = why, None

    def run(self, **kw):
        return self

    def gate(self, gid, fn, *a, **kw):
        kw.pop("judge", None)
        return fn(*a, **kw)

    def finish(self):
        return "preflight did not run (%s); the launch carries on" % self.why


def _refusal(res):
    """A launch gate's answer (None, or refusal text) as an observation."""
    return ("FAIL", str(res)) if res else ("PASS", "")


def launch(seat, item, brief, model, max_s, budget, now=None, runner=subprocess.run, known=None, clone=None, sleep=time.sleep,
           events_dir=None, skip_launch_checks=None, env=None, resume_session=None, projects=None, extra=None):
    """-> (exit code, text). extra: fields the run's record carries from creation (`continue_on_cap`, a
    continuation's chain: left_open_continue.py). Refuses an unknown item, one not filed on origin/main, a bad model or seat, an empty brief, and
    (a by-card brief missing its card's words is completed by card_repair, never refused)
    a clone another run still holds (after waiting for one that is being given back).
    The ticket preflight runs here IN SHADOW (RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS): its new checks in
    the run's clone once there is one, and this door's own checks observed in place; it refuses nothing, and its lines
    end the text. Enforcement is ticket 4 (RIMMANDRAKE_ENFORCE_PREFLIGHT_AT_CLAIM_DECLARED_FACTS_ONLY)."""
    try:
        import ticket_preflight
        pf = ticket_preflight.Shadow("helper_launch", item, seat,      # a test's fake runner records nothing real
                                     runs_path=None if runner is subprocess.run else os.devnull)
    except Exception as e:  # noqa: BLE001  a preflight that cannot load never stops a launch
        pf = _NoShadow("%s: %s" % (type(e).__name__, e))
    code, text = 1, ""
    try:
        code, text = _launch(seat, item, brief, model, max_s, budget, now, runner, known, clone, sleep, events_dir,
                             skip_launch_checks, pf, env, resume=(resume_session, projects), extra=extra)
    finally:
        try:
            tail = pf.finish()
        except Exception as e:  # noqa: BLE001
            tail = "preflight did not run (%s: %s); the launch carries on" % (type(e).__name__, e)
    # a refusal's text stays exactly the gate's own (its line is still in runs.jsonl); a launch shows the preflight's lines
    text = (text + "\n" + tail) if tail and code == 0 else text
    warn = skill_path_warning(brief) if code == 0 else None     # last, so it is the line a launcher's eye lands on
    return code, (text + "\n" + warn) if warn else text


OWN_LAUNCH = launch     # a test's stand-in for launch() starts nothing: main() then checks and records no brief


def _RL():
    import role_launch
    return role_launch


def _launch(seat, item, brief, model, max_s, budget, now, runner, known, clone, sleep, events_dir, skip_launch_checks, pf,
            env=None, resume=(None, None), extra=None):
    now = now or time.time()
    bad = pf.gate("I1", lambda: None if seat in SEATS else "refused: seat %r is not one of %s" % (seat, ", ".join(SEATS)),
                  judge=_refusal)
    if bad:
        return 2, bad
    RL = _RL()
    model = RL.tier(model)   # a full model id is a fault of form: repaired here, never refused

    def h4():
        if model not in RL.TIERS:
            return "refused: model %r is not one of %s" % (model, ", ".join(RL.TIERS))
        try:
            RL.launch_model(model)
        except RL.UnknownModel as e:
            return "refused: %s" % e
        return None
    bad = pf.gate("H4", h4, judge=_refusal)
    if bad:
        return 2, bad
    if not (brief or "").strip():
        return 2, "refused: empty brief"
    brief, carded = card_repair(item, brief, events_dir)     # a by-card brief carries the card's words: added, never refused
    pf.gate("I3", lambda: None, judge=_refusal)
    max_s = parse_max_s(max_s)
    if max_s is not None and max_s < MIN_MAX_S:
        return 2, "refused: --max-s %d is under %d (use none for no limit)" % (max_s, MIN_MAX_S)
    if known is None:
        import helper_checkpoint as HC
        known = HC.known_items()
    if not known:
        return 2, "refused: the ledger read 0 items (blind instrument), cannot check %s" % item
    if item not in known:
        return 2, "refused: %s is not a ledger item; file it first (rimflow namecheck, then file)" % item
    if runner is subprocess.run:    # a test's fake runner never reads the live switching notice
        draining = drain_refusal(now, extra, resume[0])
        if draining:
            return 2, draining
    unpublished = pf.gate("I6", origin_gate, item, runner=runner, seat=seat, judge=_refusal)    # before a clone or a unit
    if unpublished:
        return 2, unpublished
    notes = []
    if clone and not clone_can_start(clone):    # RIMMANDRAKE_GUARD_HELPER_LAUNCH_ON_MISSING_CLONE_TWO_RUNS_DIED_UNSTARTED
        notes.append("NOTE (form, repaired): --clone %s is missing or has no claude_bounded.sh (the pool took it back); "
                     "this launch took a pool clone for %s instead, as a launch without --clone does." % (clone, item))
        clone = None
    dest = clone or os.path.join(pool_root(), "clones", item + ".det")
    if resume[0]:
        fresh = resume_fresh_clone(item, dest, runner, now)
        if fresh:       # the clone a finished run still holds may vanish under a resume: the resume takes its own
            dest, clone = fresh, None
    held = hold_until_returned(dest, runner, sleep, now, kept_ok=bool(clone), notes=notes)
    if held:
        return 2, held
    with clone_lock(dest):
        code, text = _launch_locked(seat, item, brief, model, max_s, budget, now, runner, clone, dest, skip_launch_checks,
                                    pf, env, resume=resume, extra=extra)
    return code, "\n".join([text] + notes) if notes else text


def clone_can_start(clone):
    """True when a unit can start in `clone`: the directory holds the claude_bounded.sh the unit's argv runs."""
    return os.path.isfile(os.path.join(clone, "src", "RimMandrake", "Utils", "claude_bounded.sh"))


def _launch_locked(seat, item, brief, model, max_s, budget, now, runner, clone, dest, skip_launch_checks=None, pf=None,
                   env=None, resume=(None, None), extra=None):
    resume_session, projects = resume
    pf = pf or _NoShadow("no preflight handed in")
    held = clone_holders(dest, runner, now, kept_ok=bool(clone))     # again, under the lock: no waiting now
    if held:
        return 2, "refused: clone %s was taken while this launch waited: %s" % (dest, " | ".join(h[2] for h in held))
    if clone:
        how = "given " + clone
    else:
        try:
            clone, how = take_clone(item, runner=runner, name=os.path.basename(dest))
        except Exception as e:  # noqa: BLE001
            return 1, "clone failed: %s" % e
        if resume_session and os.path.basename(dest) != item + ".det":
            how += "; " + restore_session_bundle(item, resume_session, clone)
    notes = []
    if runner is subprocess.run:    # the ticket's new checks, against the copy this run's clone holds (spec 6.2)
        pf.run(root=clone)
    if not skip_launch_checks:      # the item's declared checks, in the clone the run will use (GATE_FIRST)
        # observed as F14: the `## launch-checks` block, whose must-fail line is spec group F's added check (2026-11-15)
        refused, notes = pf.gate("F14", launch_check_refusal, item_text(clone, item), clone,
                                 judge=lambda r: _refusal(r[0]))
        if refused:
            return 2, refused + "\n(the Conductor's bypass: --skip-launch-checks \"<why>\")"
    root = state_dir()
    rec = {"seat": seat, "item": item, "clone": clone, "model": model, "max_s": max_s,
           "budget_usd": float(budget), "at": now, "state": root, "status": "launching", "clone_how": how}
    rec.update({k: v for k, v in (extra or {}).items() if k not in rec})
    if skip_launch_checks:
        rec["launch_checks_skipped"] = skip_launch_checks
    if env:
        rec["env"] = dict(env)
        brief = agent_repair(rec, clone, brief)
    mark_fresh(rec, brief, resume_session, root)
    if resume_session:
        moved = carry_session(resume_session, clone, projects)
        if not moved:
            return 2, ("REFUSED: session %s has no transcript under %s; the holder starts from the packet instead "
                       "(drop --resume)" % (resume_session, projects or PROJECTS))
        rec["resume_session"] = resume_session
        rec["resume_transcript"] = moved
    if notes:
        rec["launch_checks_did_not_run"] = notes
    if getattr(pf, "run_id", None):
        rec["preflight_run"] = pf.run_id
    unit = reserve_record(rec, root)    # a name no other run's record holds; never overwrites one
    try:    # the brief as given, so a run a fleet stop killed can be relaunched without its transcript (stop_resume)
        rec["brief_src"] = os.path.join(runs_dir(root), unit + ".brief.src.md")
        with open(rec["brief_src"], "w", encoding="utf-8") as fh:
            fh.write(brief)
        write_record(rec, root)
    except OSError:
        rec.pop("brief_src", None)
    msg = brief_message(brief, item, seat, clone, max_s, rec.get("env"))
    if runner is subprocess.run:        # a test's fake runner never reads the live switching notice
        warned = account_warning(now)
        if warned:                      # the live account is in its warning zone: this run starts warned
            msg += "\n\n---\n" + warned + "\n"
    if runner is subprocess.run:        # its own TMPDIR, deleted by run_tmp.sweep when the unit is gone
        rec["tmp"] = run_tmp.prepare(unit)
        write_record(rec, root)
    # every brief, of any length, goes in by file on stdin: a phrase of it in a wrapper's argv let the run's own
    # `pgrep -f <phrase>` match spend_watchdog.py and kill it (RIMMANDRAKE_STOP_KILLING_WORKING_JUDGE_AT_FORTY_FIVE_MIN)
    rec["brief_file"] = os.path.join(runs_dir(root), unit + ".brief.md")
    with open(rec["brief_file"], "w", encoding="utf-8") as fh:
        fh.write(msg)
    write_record(rec, root)
    import control as C     # the one admission point (control.py): a switch, his hold or a duplicate refuses here
    cenv = rec.get("env") or {}
    cspec = {"family": "detached", "unit": unit, "item": item, "model": model, "mod": cenv.get("RM_CONTROL_MOD"),
             "stage": cenv.get("RM_CONTROL_STAGE"), "extra_units": [scope_name(seat, unit)],
             # the game it drives (`pipe off game:a` keeps every run off ArchBig)
             "game": run_game(item, cenv)}
    try:
        r = C.launch_unit(launch_argv(rec, msg, claude_bin()), cspec, runner=runner, clone=rec.get("clone"),
                          # budget: danger=a hung launch holds its caller; longest=1.3s (admission to start of 1057 runs,
                          # budget: control.db)
                          capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except OSError as e:                # it never ran (E2BIG, ENOENT): no unit can exist, nothing to ask systemd
        rec["status"] = "launch_failed"
        rec["why"] = "systemd-run could not be started: %s" % e
        write_record(rec, root)
        return 1, "LAUNCH FAILED %s: %s" % (unit, rec["why"])
    except subprocess.SubprocessError as e:
        # systemd-run did not answer (2026-11-16: the launch raised and its record stayed "launching" with no unit,
        # holding the clone; the next two launches were refused on it). Ask systemd.
        import role_launch as RL
        st = RL.unit_state(unit, runner=runner)
        if st in DEAD_STATES:
            try:    # no unit now: make sure a start still queued in systemd never runs behind a launch_failed record
                runner(["systemctl", "--user", "stop", "--no-block", unit], capture_output=True, text=True, timeout=30,
                       stdin=subprocess.DEVNULL)
            except (subprocess.SubprocessError, OSError):
                pass
            rec["status"] = "launch_failed"
            rec["why"] = "systemd-run did not answer (%s); systemd reads the unit %s" % (type(e).__name__, st)
            write_record(rec, root)
            return 1, "LAUNCH FAILED %s: %s" % (unit, rec["why"])
        if st == "unknown":
            return 1, ("LAUNCH UNCONFIRMED %s: systemd-run did not answer (%s) and systemd cannot be read; the record "
                       "stays 'launching' (`detached_helper.py status` resolves it)" % (unit, type(e).__name__))
        r = subprocess.CompletedProcess([], 0, "", "")      # the unit is up after all: recorded running below
    if getattr(r, "refused", False):    # control refused it: nothing ran, nothing is charged, no failed-launch alarm
        rec["status"] = "refused"
        rec["why"] = r.why
        write_record(rec, root)
        return 2, "REFUSED %s by control: %s" % (unit, r.why)
    if r.returncode:
        rec["status"] = "launch_failed"
        rec["why"] = ((r.stdout or "") + (r.stderr or "")).strip()
        write_record(rec, root)
        return 1, "LAUNCH FAILED %s: %s" % (unit, rec["why"])
    now_rec = read_record(unit, root) or {}
    if now_rec.get("status") not in (None, "launching"):
        # a helper that ended at once was recorded by its finish step before this line: never `running` over it
        # (RIMMANDRAKE_KEEP_FINISHED_RECORD_LAUNCH_WROTE_RUNNING)
        rec = now_rec
    else:
        rec["status"] = "running"
        write_record(rec, root)
    return 0, ("DETACHED %s\n  item %s, model %s, bound %s, $%g\n  clone %s (%s)\n  record %s\n"
               "  it ends with a note on %s and a line in the Conductor log; `detached_helper.py status` lists runs%s"
               % (unit, item, model, ("%d s" % max_s) if max_s else "none", budget, clone, how, record_path(unit, root), item,
                  "".join("\n  " + n for n in notes + (["launch checks skipped: " + skip_launch_checks]
                                                       if skip_launch_checks else []))))


LEFT_OPEN = "LEFT OPEN:"    # a run's note saying what it left (RIMMANDRAKE_FLAG_DETACHED_SUCCESS_LEAVING_ITEM_OPEN)
READ_ITEM = r"""
import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "rimflow"))
import model
item = sys.argv[1]
evs = model.read()
items = model.replay(evs).items
it = items.get(item)
rest = {}
try:
    import close_remainder as CR
    ends = [e for e in evs[CR.last_start(evs, item):] if e.get("id") == item and e.get("event") == "close"]
    rest = {"unit": ends[-1].get("role_unit") if ends else None, "linked": CR.linked(item, evs, items) or (ends and (
        ends[-1].get("remainder") or ends[-1].get("noRemainder"))) or "", "name": CR.name(item, items),
        "held": [i for i in items if CR.holds(items, item, i)]}
except Exception as e:
    rest = {"blind": "%s: %s" % (type(e).__name__, e)}
print(json.dumps({"state": getattr(it, "state", None), "wait_until": getattr(it, "wait_until", None), "rest": rest,
                  "notes": [e for e in evs if e.get("id") == item and e.get("event") == "note"]}))
"""


def read_item(clone, item):
    """-> {"state", "wait_until", "notes"} for the item as the run's clone folds its ledger (the run's own close sits there before
    any other clone pulls it), or None when that cannot be read."""
    try:
        r = subprocess.run([sys.executable, "-c", READ_ITEM, item], cwd=clone, capture_output=True, text=True,
                           timeout=300, stdin=subprocess.DEVNULL)  # budget: class=rimflow
        return json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _epoch(ts):
    try:
        import datetime
        return datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def left_open_noted(notes, item, since):
    """A note on the item, written at or after `since`, whose text starts LEFT OPEN: (a note with no readable time
    is no excuse: it may be an older run's)."""
    for e in notes or []:
        t = _epoch(e.get("ts")) if isinstance(e, dict) else None
        if (t is not None and t >= since and e.get("id") == item and e.get("event") == "note"
                and str(e.get("text") or "").strip().upper().startswith(LEFT_OPEN)):
            return True
    return False


def _transcript_path(rec, sid):
    """-> the session transcript of the run, or None. claude keeps it under its config dir, in a folder named by the
    run's cwd (the clone) with every non-alphanumeric as '-'."""
    clone = str(rec.get("clone") or "")
    roots = [os.environ.get("CLAUDE_CONFIG_DIR") or "", os.path.expanduser("~/.claude")]
    for root in [r for r in roots if r]:
        p = os.path.join(root, "projects", re.sub(r"[^A-Za-z0-9]", "-", clone), sid + ".jsonl")
        if clone and os.path.isfile(p):
            return p
    for root in [r for r in roots if r]:
        hits = glob.glob(os.path.join(root, "projects", "*", sid + ".jsonl"))
        if hits:
            return hits[0]
    return None


def _turn_finals(path):
    """-> the last main-chain assistant text of each finished turn (a stop_hook_summary ends a turn), oldest first."""
    finals, last = [], None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("type") == "assistant" and not r.get("isSidechain"):
                parts = [c.get("text") for c in ((r.get("message") or {}).get("content") or [])
                         if isinstance(c, dict) and c.get("type") == "text" and c.get("text")]
                if parts:
                    last = "\n".join(parts)
            elif r.get("type") == "system" and r.get("subtype") == "stop_hook_summary" and last is not None:
                finals.append(last)
                last = None
    if last is not None:
        finals.append(last)
    return finals


def run_report(rec, res=None):
    """-> the run's report text. claude's result JSON holds only the LAST turn: when a background task ended after the
    report, the run said one more line and that line was all the result kept (twice on 2026-11-19,
    RIMMANDRAKE_KEEP_RUN_REPORT_WHEN_LATE_REMARK_FOLLOWS). For such a result (result_index >= 1) the final text of each
    of the last result_index + 1 turns is read from the transcript, oldest first. A transcript it cannot read leaves
    the last result, with a line naming the report UNMEASURED; it never passes for the whole report silently."""
    import role_launch as RL
    if res is None:
        res = RL.read_result({"out": rec.get("out") or "", "err": rec.get("err") or ""})
    if not isinstance(res, dict):
        return ""
    last = str(res.get("result") or "")
    n = res.get("result_index")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        return last
    sid = str(res.get("session_id") or "")
    p = _transcript_path(rec, sid) if sid else None
    why = "no session_id" if not sid else ("no transcript for session %s" % sid if not p else "")
    finals = []
    if p:
        try:
            finals = _turn_finals(p)
        except OSError as e:
            why = "transcript unreadable: %s" % e
    if finals:
        return "\n\n".join(finals[-(n + 1):])
    return "%s\n\n(earlier report UNMEASURED: this is turn %d of the run and %s)" % (
        last, n + 1, why or "the transcript holds no finished turn")


def result_left_open(rec):
    """-> the paragraph of the run's result text that starts LEFT OPEN: (to the next blank line), or "". Two of the 13
    runs that ended owed by 2026-11-19 wrote what was left there and not as a note."""
    t = run_report(rec)
    # A note starts a line or a sentence (optional */_ emphasis). A mention inside a sentence, such as "no `LEFT OPEN:`
    # note", is not one: read as a note it sent an owed run the carry-on brief (2026-11-19 8:01 PM PST,
    # RIMMANDRAKE_FIX_LEFT_OPEN_PARSE_READS_ITS_OWN_DENIAL).
    m = _LEFT_OPEN_AT.search(t)
    return re.split(r"\n\s*\n", t[m.start(1):], maxsplit=1)[0] if m else ""


_LEFT_OPEN_AT = re.compile(r"(?:^|(?<=[.!?]) )[ \t]*([*_]{0,3}" + re.escape(LEFT_OPEN) + ")",
                           re.IGNORECASE | re.MULTILINE)


def file_remainder(rec, got, report, runner=subprocess.run):
    """A run that closed its item while its own report declares unbuilt parts, with no ticket linked: the program files
    the ticket (close_remainder.py), with the report in a note on it. -> one step line, or "" when nothing is owed."""
    import close_remainder as CR
    import spend_talk
    rest = got.get("rest") or {}
    if got.get("state") != "done":
        return ""
    item = rec["item"]
    parts = [p for p in CR.declared(report) if not any(c in (rest.get("held") or ()) for c in CR.ids(p))]
    if not parts:
        return ""
    if rest.get("blind") or not rest:
        return "remainder: could not look (%s); the report declares: %s" % (rest.get("blind") or "no reading", " | ".join(parts))
    if rest.get("linked") or rest.get("unit") != rec.get("unit"):
        return ""
    cli = os.path.join(rec["clone"], "src", "RimMandrake", "rimflow", "cli.py")
    for argv in (["file", rest["name"], "--for", "BENCH", "--title", CR.title(item, [spend_talk.strip(p) for p in parts]),
                  "--caused-by", item],
                 ["note", rest["name"], "--text", "Filed at the end of %s, which closed %s. Its report:\n%s"
                  % (rec["unit"], item, spend_talk.strip(report))]):
        r = runner(["python3", cli] + argv + ["--seat", rec["seat"], "--why", "a run closed its item with parts unbuilt"],
                   cwd=rec["clone"], capture_output=True, text=True, timeout=1800, stdin=subprocess.DEVNULL)  # budget: class=call
        if r.returncode:
            return "remainder FAILED (%s exit %d: %s)" % (argv[0], r.returncode,
                                                          ((r.stderr or "") + (r.stdout or "")).strip())
    return "remainder filed: " + rest["name"]


def owed_close(rec, state, notes):
    """-> the plain line for a run that ended success with its item still open and no LEFT OPEN: note since it
    began (or in its result text), or "". It closes nothing: only evidence closes an item; left_open_continue
    continues such a run once to close it or say what is left."""
    import model
    if not str(rec.get("result") or "").startswith("success (") or state in model.TERMINAL:
        return ""
    if left_open_noted(notes, rec.get("item"), rec.get("at") or 0) or result_left_open(rec):
        return ""
    return ("run %s ended success; item %s is still %s: close it with its published sha or say what is left "
            "(a note starting %s)" % (rec.get("unit"), rec.get("item"), state or "absent from the ledger", LEFT_OPEN))


def owed_lines(records, items, evs):
    """The status page's lines: every finished run finish flagged (record `owed_close`) whose item is still open
    and has no LEFT OPEN: note since, read against today's ledger (`items` {id: item with .state})."""
    out = []
    for rec in records or []:
        if rec.get("owed_close"):
            line = owed_close(rec, getattr(items.get(rec.get("item")), "state", None), evs)
            if line:
                out.append(line)
    return out


def conductor_log_path():
    p = os.environ.get("RM_CONDUCTOR_LOG")
    if p:
        return p
    try:
        import dispatcher
        return dispatcher.no_handoff_rule(dispatcher.load_schedule()).get("conductor_log") or REAL_LOG
    except Exception:  # noqa: BLE001
        return REAL_LOG


def conductor_line(text, now, path=None, head="DETACHED RUN ENDED"):
    """One line in the Conductor log. Same guard as dispatcher.conductor_log: a test process never writes the real log.
    head: the line's kind (stop_resume writes "STOP RESUME")."""
    import doorbell
    path = path or conductor_log_path()
    if (os.path.abspath(path) == os.path.abspath(REAL_LOG)
            and os.environ.get("RM_DISPATCHER_STATE", doorbell.DEFAULT_STATE) != doorbell.DEFAULT_STATE):
        raise RuntimeError("refusing to write the REAL conductor log from a test process: " + path)
    import conductor_log_guard
    conductor_log_guard.refuse_if_test(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n%s — %s: %s\n" % (iso(now), head, text))
    return path


def cap_stopped(res):
    """True when a run's result JSON is a spend stop: the spend watchdog's, or claude's own budget stop."""
    return isinstance(res, dict) and (res.get("stopped_by") == "spend_watchdog"
                                      or res.get("subtype") == "error_max_budget_usd")


INTERRUPTED = "interrupted before it finished; its session can be resumed"


def outcome(rec, env):
    """-> (short status, weighted_v2 tokens or None, result tail). Reads claude's JSON and systemd's ExecStopPost
    variables. The tokens come from the result's modelUsage (the whole process, each model at its own list prices),
    else its usage as the record's model; a model not in role_launch.MODEL_PRICES leaves them UNMEASURED, named in
    rec["unknown_model"], never weighed as another model."""
    import role_launch as RL
    res = RL.read_result({"out": rec["out"], "err": rec["err"]})
    svc = env.get("SERVICE_RESULT") or "unknown"
    code = env.get("EXIT_CODE") or "-"
    status = env.get("EXIT_STATUS") or "-"
    tokens = None
    if isinstance(res, dict):
        try:
            tokens = RL.run_tokens(res, rec.get("model"))
        except RL.UnknownModel as e:
            rec["unknown_model"] = str(e)
    if isinstance(res, dict):
        tail = run_report(rec, res)
        if not tail:            # an empty result: its subtype says what kind of end it was
            tail = str(res.get("subtype") or "")
        if res.get("is_error"):
            svc = svc + "/claude-error"
    else:
        try:
            with open(rec["err"], encoding="utf-8", errors="replace") as f:
                tail = "no result JSON; stderr tail: " + f.read()
        except OSError:
            tail = "no result JSON, no stderr"
        if svc != "timeout" and (svc in ("unknown", "signal") or code in ("killed", "dumped") or status in KILL_STATUSES):
            svc = "killed: " + svc
    return "%s (%s %s)" % (svc, code, status), tokens, " ".join(tail.split())


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def earlier_session_totals(rec, sid, root=None):
    """-> (largest weighted_v2 tokens, largest dollars) an earlier run of claude session `sid` recorded as its session
    total, each None when none is readable. A record from before RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_
    TOTAL_LOGGED has no `session`: its result file is read instead."""
    import role_launch as RL
    best = [None, None]
    try:
        units = record_units(root)
    except OSError:
        return tuple(best)      # the folder cannot be listed: none is readable, as the docstring says
    for u in units:
        r = read_record(u, root)
        if not is_record(r, u) or r.get("unit") == rec["unit"] or not (_num(r.get("at")) and r["at"] < rec["at"]):
            continue
        if "session" in r:
            if r["session"] != sid:
                continue
            got = (r.get("session_tokens"), r.get("session_cost_usd"))
        else:
            res = RL.read_result({"out": r.get("out"), "err": r.get("err")})
            if not isinstance(res, dict) or res.get("session_id") != sid:
                continue
            try:
                got = (RL.run_tokens(res, r.get("model")), result_cost(res)[0])
            except RL.UnknownModel:
                got = (None, result_cost(res)[0])
        best = [max(b, g) if _num(b) and _num(g) else (g if _num(g) else b) for b, g in zip(best, got)]
    return best[0], best[1]


def own_part(rec, res, tokens, usd, root=None):
    """A resumed run's result reports the whole claude session so far (modelUsage, total_cost_usd), earlier runs
    included (measured 2026-11-19: 26 of 26). -> (tokens, dollars, record fields): its own part, the session total
    less the largest one an earlier run of the session recorded; the session totals under their own names. A spend
    watchdog stop already measured this launch's turns only. An unreadable earlier total leaves the part None
    (UNMEASURED), its cause in tokens_why."""
    sid = res.get("session_id") if isinstance(res, dict) else None
    if not rec.get("resume_session"):
        return tokens, usd, {"session": sid, "session_tokens": tokens, "session_cost_usd": usd}
    sid = rec["resume_session"]
    pt, pu = earlier_session_totals(rec, sid, root)
    stop = isinstance(res, dict) and res.get("stopped_by") == "spend_watchdog"
    (tp, ts), (up, us) = session_part(tokens, pt, stop), session_part(usd, pu, stop)
    fields = {"session": sid, "session_tokens": ts, "session_cost_usd": us}
    if tp is None and _num(tokens):
        fields["tokens_why"] = "a resume of session %s whose earlier total no run record holds" % sid
    return tp, up, fields


def session_part(total, earlier, watchdog_stop=False):
    """A resumed claude call's figure (tokens or dollars) -> (its own part, the session's total), each None when it
    cannot be read. The CLI's result is the whole session so far, earlier launches included; a spend watchdog stop
    measured this launch only. Shared by own_part and coverage_judge's re-asks."""
    if watchdog_stop:
        return total, (total + earlier if _num(total) and _num(earlier) else None)
    return (total - earlier if _num(total) and _num(earlier) else None), total


def _model_sum(mu):
    """-> the sum of every model's costUSD, or None when any model has none (one model's figure is not the run's)."""
    if not isinstance(mu, dict) or not mu:
        return None
    cs = [m.get("costUSD") if isinstance(m, dict) else None for m in mu.values()]
    return round(sum(cs), 6) if all(_num(c) for c in cs) else None


def result_cost(res):
    """-> (dollars or None, how) from claude's result JSON: total_cost_usd, else the sum of modelUsage costUSD (the two
    were equal on all 10 whole result files of 2026-11-15). None is UNMEASURED, never 0."""
    if not isinstance(res, dict):
        return None, "no result JSON"
    if _num(res.get("total_cost_usd")):
        return float(res["total_cost_usd"]), "total_cost_usd"
    s = _model_sum(res.get("modelUsage"))
    if s is not None:
        return s, "sum of modelUsage costUSD"
    return None, "no dollars in the result JSON"


_TOTAL_RX = re.compile(r'"total_cost_usd"\s*:\s*(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)')
_MODELS_RX = re.compile(r'"modelUsage"\s*:\s*(?=\{)')


def recover_cost(text):
    """-> (dollars or None, how) from a result file's text, whole or with its head written over (the finish line landed
    at offset 0 before RIMMANDRAKE_KEEP_RUN_RESULT_WHOLE_FINISH_WRITES_OVER). Only a key outside any JSON string counts
    (one quoted inside the result text reads \\"total_cost_usd\\" and does not match); a lone surviving costUSD is not the
    run's total."""
    text = text or ""
    try:
        res, _ = json.JSONDecoder().raw_decode(text.lstrip())
    except ValueError:
        res = None
    if isinstance(res, dict):
        usd, how = result_cost(res)
        return (usd, how) if usd is not None else (None, "UNMEASURED: " + how)
    totals = _TOTAL_RX.findall(text)
    if totals:
        return float(totals[-1]), "total_cost_usd in the surviving tail"
    for m in reversed(list(_MODELS_RX.finditer(text))):
        try:
            mu, _ = json.JSONDecoder().raw_decode(text, m.end())
        except ValueError:
            continue
        s = _model_sum(mu)
        if s is not None:
            return s, "sum of modelUsage costUSD in the surviving tail"
    return None, "UNMEASURED: the result file's dollars were written over" if text.strip() else "UNMEASURED: empty result file"


def measured_cost(rec):
    """-> (dollars or None, how) read from the run's result file now."""
    try:
        with open(rec["out"], encoding="utf-8", errors="replace") as f:
            return recover_cost(f.read())
    except (OSError, KeyError, TypeError):
        return None, "UNMEASURED: no result file"


def _usd(v):
    return "UNMEASURED" if not _num(v) else "%.2f" % v


def finish_log_path(unit, root=None):
    """Where finish's own line goes: never the result file (RIMMANDRAKE_KEEP_RUN_RESULT_WHOLE_FINISH_WRITES_OVER)."""
    return os.path.join(runs_dir(root), unit + ".finish.log")


def keep_off_result(unit, root=None):
    """Point this process's stdout and stderr at the run's finish log when they are its result or error file. A unit
    launched before the append: change hands finish those files at offset 0, so its print overwrote claude's JSON.
    -> the fds moved. Never raises."""
    rec = read_record(unit, root) or {}
    ids = set()
    for k in ("out", "err"):
        try:
            st = os.stat(rec[k])
            ids.add((st.st_dev, st.st_ino))
        except (OSError, KeyError, TypeError):
            pass
    moved = []
    for fd, stream in ((1, sys.stdout), (2, sys.stderr)):
        try:
            st = os.fstat(fd)
            if (st.st_dev, st.st_ino) not in ids:
                continue
            stream.flush()
            log = os.open(finish_log_path(unit, root), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            os.dup2(log, fd)
            os.close(log)
            moved.append(fd)
        except (OSError, ValueError, AttributeError):
            pass
    return moved


def backfill_cost(apply=False, root=None, now=None):
    """Finished runs recorded before finish kept the dollars: read them back from what survives of each result file.
    What cannot be read is marked UNMEASURED, never guessed. -> (0, summary)."""
    now = now or time.time()
    counts, lines = {}, []
    for rec in all_records(root):
        if rec.get("status") != "finished" or "cost_usd" in rec:
            continue
        if now - (rec.get("ended") or 0) < 3600:    # its return step may still be writing this record
            counts["skipped"] = counts.get("skipped", 0) + 1
            continue
        usd, how = measured_cost(rec)
        key = "measured" if usd is not None else "UNMEASURED"
        counts[key] = counts.get(key, 0) + 1
        lines.append("%s  %s  %s" % (rec["unit"], _usd(usd), how))
        if apply:
            rec.update(cost_usd=usd if usd is not None else "UNMEASURED", cost_how=how + " (backfilled %s)" % iso(now))
            write_record(rec, root)
    head = "backfill-cost %s: %d measured, %d UNMEASURED, %d ended under an hour ago (left)" % (
        "APPLIED" if apply else "dry run (--apply writes)", counts.get("measured", 0), counts.get("UNMEASURED", 0),
        counts.get("skipped", 0))
    return 0, "\n".join([head] + lines)


def killed(rec, runner=subprocess.run, now=None):
    """-> why, or "" : the run was KILLED from outside before claude wrote its result JSON (an account switch SIGTERMs
    every Claude process, measured 2026-11-15 ~12:00 PM PST: two judge runs, empty out and err files, units gone, finish
    never run). Either its unit died with finish never run (live_status "dead") or finish recorded a signal stop ("killed:"
    from outcome). A run that wrote its result, hit its budget, or was stopped at its own time limit was not killed: it
    ended (RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT)."""
    import role_launch as RL
    if not isinstance(rec, dict) or isinstance(RL.read_result({"out": rec.get("out") or "", "err": rec.get("err")}), dict):
        return ""
    if str(rec.get("result") or "").startswith("killed"):
        return "killed with no result JSON (%s)" % rec["result"]
    if rec.get("status") in ("launching", "running") and live_status(rec, runner, now) == "dead":
        return "its unit died with no result JSON and its finish never ran"
    return ""


def mark_killed(unit, why, now=None, root=None):
    """`pipe stop --kill` killed this run's whole cgroup, its own ExecStopPost steps included (measured 2026-11-18: the
    cgroup SIGKILL also kills the stop-post finish, so the record stayed `running` and the clone held). Record it
    finished, result `killed: <why>`, with its finish OWED (finish then writes the note and log line once). -> line."""
    rec = read_record(unit, root)
    if not rec:
        return "no record for %s (not a detached run): nothing to mark" % unit
    if rec.get("status") == "finished":
        return "already finished %s" % unit
    rec.update(status="finished", result="killed: " + why, ended=now or time.time(), finish_owed=True)
    write_record(rec, root)
    return "record %s finished (killed), its finish owed" % unit


def finish(unit, now=None, env=None, runner=subprocess.run, log_path=None, item_reader=None, waker=None, continuer=None,
           states_reader=None):
    """The unit's ExecStopPost. -> (exit code, text). Once per run: a second call changes nothing. A run `pipe stop
    --kill` marked killed (mark_killed) gets its owed note and log line here, its result kept."""
    now = now or time.time()
    env = os.environ if env is None else env
    rec = read_record(unit)
    if not rec:
        return 2, "no record for %s" % unit
    if rec.get("status") == "finished" and not rec.get("finish_owed"):
        return 0, "already finished %s" % unit
    st, tokens, tail = outcome(rec, env)
    if rec.get("finish_owed"):
        st = rec.get("result") or st
    usd, how = measured_cost(rec)       # read now, with the tokens, before anything else touches the file
    import role_launch as RL
    tokens, usd, split = own_part(rec, RL.read_result({"out": rec["out"], "err": rec["err"]}), tokens, usd)
    if usd is None and split.get("tokens_why"):
        how = "UNMEASURED: " + split["tokens_why"]
    took = int(now - rec["at"])
    # the owner, 2026-11-16: "Please speak in terms of weighted tokens not money." The dollars stay in the record
    # (cost_usd) for the stage ceiling; what a person reads says weighted tokens only (weighted_v2: MODEL_PRICES,
    # run_tokens)
    why = rec.get("unknown_model") or split.get("tokens_why")
    unmeasured = "UNMEASURED (%s)" % why if why else "UNMEASURED"
    resumed = " (its own part: a resume of session %s)" % rec["resume_session"] if rec.get("resume_session") else ""
    # the item note is what a resumed or continued run reads (`rimflow show`): no spend, no token figure, no path to
    # the result file that holds them, and a spend stop reads only "interrupted" (owner 2026-11-16: no launched agent
    # is told its spend; RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED). The Conductor log line below and
    # the record keep the cause, the tokens and the output path.
    import role_launch as RL
    capped = cap_stopped(RL.read_result({"out": rec["out"], "err": rec["err"]}))
    import spend_talk       # the run's own words may state its spend ("$21.6 of the $30 budget", 2026-11-15)
    text = ("DETACHED run %s ended %s after %d s (model %s). Result: %s. Clone %s."
            % (unit, st, took, rec["model"], INTERRUPTED if capped else (spend_talk.strip(tail) or "-"), rec["clone"]))
    clone, seat, item = rec["clone"], rec["seat"], rec["item"]
    cli = os.path.join(clone, "src", "RimMandrake", "rimflow", "cli.py")
    steps = [stop_scope(seat, unit, runner)]     # first: the unit is gone but claude is not
    if steps[0].count("FAILED") >= 2 and re.search(r"now (active|activating|reloading)\b", steps[0]):
        # neither the kill nor the stop took and the scope still runs: claude may still be billing. Not finished: the
        # record stays as it was, so a later finish (the tick's dead-run chore) tries again
        # (RIMMANDRAKE_RETRY_FINISH_WHEN_SCOPE_STOP_FAILED_BILLING)
        rec["finish_blocked"] = {"at": now, "why": steps[0]}
        write_record(rec)
        return 1, "NOT FINISHED %s: %s" % (unit, steps[0])
    if not st.startswith("success ("):   # its last sign of life, once, for the run that carries it on (run_alive.py)
        try:
            import run_alive
            text += " " + run_alive.run_line(rec, now)
        except Exception as e:  # noqa: BLE001  the line never stops the finish
            text += " ALIVE: could not look (%s: %s)." % (type(e).__name__, e)
    owed = ""
    got = None
    if not os.path.isdir(clone):                 # deleted under the run: no clone to note from, the log line still goes
        steps.append("clone gone: no note on the item, nothing published")
    else:
        cap_opt = int(rec.get("continue_on_cap") or 0) > int(rec.get("cap_continues_used") or 0)
        if st.startswith("success (") or (cap_opt and not st.startswith("killed")):
            # its item still open with nothing said: one plain line, everywhere; and what a continuation would carry on
            got = (item_reader or read_item)(clone, item)
            if isinstance(got, dict) and st.startswith("success ("):
                owed = owed_close(dict(rec, result=st), got.get("state"), got.get("notes"))
                steps.append("item " + (got.get("state") or "absent") + (": OWED" if owed else ""))
                try:
                    left = file_remainder(rec, got, run_report(rec), runner)
                except Exception as e:  # noqa: BLE001  the filing never stops the finish; its failure is said
                    left = "remainder FAILED (%s: %s)" % (type(e).__name__, e)
                if left:
                    steps.append(left)
                    text += " " + left[0].upper() + left[1:] + "."
            else:
                steps.append("item state UNMEASURED (its clone's ledger could not be read)")
        if owed:
            text += " OWED: " + owed + "."
        r = runner(["python3", cli, "note", item, "--text", text, "--seat", seat, "--why", "detached run ended"],
                   cwd=clone, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)  # budget: class=rimflow
        steps.append("note exit %d" % r.returncode)
        own = "infrastructure/state/ledger/events/%s.jsonl" % seat
        r = runner(["./publish", "-m", "ledger: detached run on %s ended" % item, own]
                   + [p for p in dirty_shards(clone, seat) if p != own],
                   cwd=clone, capture_output=True, text=True, timeout=21600, stdin=subprocess.DEVNULL)  # budget: class=publish
        pub = ((r.stdout or "") + (r.stderr or "")).strip()
        m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", pub)
        steps.append("publish " + (m.group(1)[:10] if m else "exit %d: %s" % (r.returncode, pub)))
    try:
        path = conductor_line("%s on %s (%s seat): %s, %d s, %s weighted tokens%s. %s. Output %s. READ: rimflow show %s.%s"
                              % (unit, item, seat, st, took, unmeasured if tokens is None else "{:,}".format(tokens), resumed,
                                 fulltext.clip(tail, 200, rec["out"]) or "-", rec["out"], item,
                                 " OWED: " + owed + "." if owed else ""), now, log_path)
        steps.append("conductor log " + path)
    except Exception as e:  # noqa: BLE001
        steps.append("conductor log FAILED: %s" % e)
    steps.append(wake_conductor(unit, st, rec["out"], item, seat, waker, owed) if run_wakes(rec, owed)
                 else "wake: none for a scan run (the log line stands)")
    import role_launch as RL
    rec.pop("finish_owed", None)
    rec.update(status="finished", ended=now, result=st, tokens=tokens, token_unit=RL.TOKEN_UNIT, steps=steps,
               cost_usd=usd if usd is not None else "UNMEASURED", cost_how=how, owed_close=owed, **split)
    write_record(rec)
    if isinstance(got, dict):   # work left: ONE continuation, its own unit (RIMMANDRAKE_CONTINUE_LEFT_OPEN_RUNS_WITHOUT_A_HAND_RELAUNCH)
        try:
            import left_open_continue as LOC
            _, line = LOC.at_finish(read_record(unit) or rec, got, clone, now, runner, continuer, states_reader)
        except Exception as e:  # noqa: BLE001  the run is finished; a continuation that cannot be planned is said
            line = "continue FAILED: %s: %s" % (type(e).__name__, e)
        steps.append(line)
        rec = read_record(unit) or rec      # fresh: the continuation step may already have written to it
        rec["steps"] = steps
        write_record(rec)
    return 0, "FINISHED %s: %s" % (unit, "; ".join(steps))


def run_wakes(rec, owed=""):
    """-> whether this run's end wakes the Conductor window. The standing scan's runs do not: each is routine, and a wake
    costs the window tokens (quiet_scan.py says its own stop). One that owes something does."""
    return bool(owed) or rec.get("next_act_owner") != "quiet_scan"


def wake_conductor(unit, st, out, item, seat, waker=None, owed=""):
    """A run of the Conductor's seat wakes the live Conductor window with its result and its owed line (run_end_wake.py;
    RIMMANDRAKE_WAKE_CONDUCTOR_ON_RUN_END_LOG_ONLY_TODAY). A test process never posts to the real one: it passes a
    waker. -> the step's line."""
    if seat != "BENCH":
        return "wake: not the Conductor's seat"
    try:
        import conductor_log_guard
        if waker is None:
            if conductor_log_guard.under_test():
                return "wake: skipped under a selftest"
            import run_end_wake
            waker = run_end_wake.post
        p = waker(unit, st, out, item, owed)
        return "wake " + (p if p else "none: no live Conductor window (the log line stands)")
    except Exception as e:  # noqa: BLE001 - the run is finished; the log line is its record
        return "wake FAILED: %s: %s" % (type(e).__name__, e)


def status(show_all=False, runner=subprocess.run):
    import role_launch as RL
    lines = []
    for rec in all_records():
        if rec.get("status") == "finished" and not show_all:
            continue
        live = RL.unit_state(rec["unit"], runner=runner) if rec.get("status") != "finished" else "-"
        st = rec.get("status")
        if live in DEAD_STATES and (st == "running" or (st == "launching" and time.time() - (rec.get("at") or 0) >= LAUNCH_GRACE_S)):
            st = "DEAD (unit %s, finish never ran: detached_helper.py finish --unit %s)" % (live, rec["unit"])
        lines.append("%s  %s  %s  item %s  %s  started %s" % (rec["unit"], st, live, rec["item"],
                                                               rec.get("model"), iso(rec["at"])))
        if rec.get("status") in ("launching", "running"):
            import run_alive
            lines.append("    " + run_alive.status_text(rec["unit"]))
    return "\n".join(lines) or "no detached runs" + ("" if show_all else " running (--all lists finished ones)")


def launch_on_host(args, brief, env, runner=subprocess.run, reader=None):
    """`launch --host H`: the host's own launcher runs it (run_host.py); this machine keeps a record naming host, unit
    and item. -> rc: 0 started, 2 refused, 5 could not look, else the host's rc."""
    import tempfile
    import run_host
    facts = (reader or run_host.read_facts)(args.host, args.item, os.environ.get("RM_PICKED_ACCOUNT"))
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(brief)
    try:
        pl = run_host.plan(args.host, args.item, fh.name, facts, model=args.model, budget=args.budget_usd,
                           seat=args.seat.upper(), next_act_owner=args.next_act_owner,
                           env=["%s=%s" % kv for kv in env.items()])
        print("%s: %s" % (pl["verdict"], pl["why"]))
        if pl["verdict"] != "REMOTE":
            return 2 if pl["verdict"] == "REFUSED" else 5
        with open(fh.name, encoding="utf-8") as stdin:
            r = runner(pl["argv"], stdin=stdin, capture_output=True, text=True, timeout=10800)  # budget: class=launch
    finally:
        os.unlink(fh.name)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    unit = run_host.parse_unit(r.stdout) if r.returncode == 0 else None
    if unit:
        rec = run_host.record(args.host, args.item, unit, args.model, args.budget_usd, seat=args.seat.upper(),
                              next_act_owner=args.next_act_owner)
        write_record(rec)
        out = "DETACHED %s\nREMOTE on %s, record %s\n%s" % (unit, args.host, record_path(unit), out)
    print(out)
    return r.returncode if r.returncode else (0 if unit else 5)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("launch")
    a.add_argument("--seat", required=True)
    a.add_argument("--item", required=True)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--brief")
    g.add_argument("--brief-file")
    a.add_argument("--model", default="sonnet")
    a.add_argument("--max-s", default=DEFAULT_MAX_S, help="seconds, or none/0 for no wall-time limit (default)")
    a.add_argument("--budget-usd", type=float, default=None,
                   help="the run's spend cap, stated per job (0 = none); required, no default. A --resume without it "
                        "carries the earlier run's cap")
    a.add_argument("--clone", help="an existing clone to run in (default: a pool clone <ITEM>.det)")
    a.add_argument("--env", action="append", default=[], metavar="RM_KEY=VALUE",
                   help="an RM_ variable the run's unit carries (a pilot holder's RM_MODLEDGER_WRITER, say)")
    a.add_argument("--skip-launch-checks", metavar="WHY",
                   help="the Conductor's bypass of the item's ## launch-checks block; WHY is recorded on the run record")
    a.add_argument("--resume", metavar="SESSION", help="resume this claude session (a mod's holder; its transcript is "
                                                        "carried into the run's clone)")
    a.add_argument("--planned-resume", action="store_true",
                   help="the --resume was decided by its caller's own rule (a mod holder's modledger.resume_plan, his "
                        "400k card): launch it as given, outside left_open_continue's 150k resume rule")
    a.add_argument("--agent", metavar="NAME", help="start the run as `claude --agent NAME` (.claude/agents/NAME.md "
                                                    "is its system prompt); sets RM_CLAUDE_AGENT on the run")
    a.add_argument("--continue-on-cap", type=int, default=0, metavar="N",
                   help="a stop by the spend watchdog is carried on by itself up to N times (left_open_continue.py); "
                        "default 0: a cap stop ends the work")
    a.add_argument("--host", metavar="NAME", help="start the run on this host (SteveDesktop) as a systemd user unit in its "
                                                   "own clone under ~/rm/list/; default: this machine (run_host.py)")
    a.add_argument("--next-act-owner", metavar="NAME",
                   help="the program that reads this run's LEFT OPEN: note and decides its next run (list_dispatch: the "
                        "Workshop Pipeline's two-run rule); left_open_continue.py does not continue such a run")
    f = sub.add_parser("finish")
    f.add_argument("--unit", required=True)
    b = sub.add_parser("return", help="give the run's pool clone back, bundled (the unit's last step; --all sweeps strays)")
    b.add_argument("--unit")
    b.add_argument("--all", action="store_true", help="every finished run whose pool .det clone still stands")
    # budget: danger=a clone is taken from a run whose launcher still reads it; ends no work: the sweep leaves the clone for a
    # budget: later sweep
    b.add_argument("--grace-s", type=int, default=3600, help="with --all: skip a run that ended more recently than this")
    b.add_argument("--no-publish-ledger", action="store_true",
                   help="do not publish the seat shard from the clone (its dirty lines ride in the bundle instead)")
    s = sub.add_parser("status")
    s.add_argument("--all", action="store_true")
    c = sub.add_parser("backfill-cost", help="finished runs without cost_usd: read the dollars back from what survives "
                                             "of each result file, UNMEASURED where nothing does")
    c.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "launch":
        brief = args.brief
        if args.brief_file:
            with open(args.brief_file, encoding="utf-8") as fh:
                brief = fh.read()
        env = dict(kv.partition("=")[::2] for kv in args.env)
        if args.agent:
            env[AGENT_ENV] = args.agent
        bad = [k for k in env if not re.match(r"^RM_[A-Z0-9_]+$", k)]
        if args.host and args.host.strip().lower() not in ("archmagi", "local"):
            return launch_on_host(args, brief, env)
        budget, carried = args.budget_usd, ""
        if budget is None and args.resume:
            budget, src = earlier_cap(args.resume)
            carried = "" if budget is None else "spend cap %g carried from %s (the run this resumes)\n" % (budget, src)
        if bad:
            rc, text = 2, "REFUSED: --env takes RM_ variables only, not %s" % ", ".join(bad)
        elif budget is None and args.resume:
            rc, text = 2, ("REFUSED: --resume %s states no --budget-usd and its earlier cap cannot be read: %s. State it: "
                           "--budget-usd <USD>, or --budget-usd 0 for none" % (args.resume, src))
        elif budget is None:
            rc, text = 2, ("REFUSED: a spend cap is required: --budget-usd <USD> sized to this job, or --budget-usd 0 for "
                           "none; there is no default (design/specs/2026-11-19-launch-spend-cap/boundary.md)")
        elif budget < 0:
            rc, text = 2, "REFUSED: --budget-usd %g is negative (0 = no cap)" % budget
        else:
            extra = {"continue_on_cap": args.continue_on_cap} if args.continue_on_cap > 0 else {}
            if args.next_act_owner:
                extra["next_act_owner"] = args.next_act_owner
            session, first, written = args.resume, "", brief
            if session and not args.planned_resume:     # the one resume rule (left_open_continue.whole_or_fresh): a large session with a progress
                import left_open_continue as LOC        # record starts fresh from it
                cr = LOC.conductor_resume(session, args.item, brief, env=env)
                session, brief, first = cr["session"], cr["brief"], cr["line"]
                env = cr.get("env", env)
                extra.update(cr["extra"])
            rc, text = launch({"CONDUCTOR": "BENCH"}.get(args.seat.upper(), args.seat.upper()), args.item, brief, args.model,
                              args.max_s, budget, clone=args.clone, skip_launch_checks=args.skip_launch_checks,
                              env=env, resume_session=session, extra=extra or None)
            text = (first + "\n" if first else "") + carried + text
            if rc == 0 and launch is OWN_LAUNCH:     # the writer reads the faults of the brief's new sentences; it refuses nothing
                prose = prose_after(written, args.item)
                text += "\n" + prose if prose else ""
    elif args.cmd == "finish":
        keep_off_result(args.unit)      # before anything prints: never into claude's result or error file
        rc, text = finish(args.unit)
    elif args.cmd == "backfill-cost":
        rc, text = backfill_cost(apply=args.apply)
    elif args.cmd == "return":
        os.chdir("/")           # the unit's working directory is the clone; a process sitting in it would keep it
        if bool(args.unit) == bool(args.all):
            rc, text = 2, "return: give --unit U, or --all"
        elif args.all:
            rc, text = return_all(publish_ledger=not args.no_publish_ledger, grace_s=args.grace_s)
        else:
            rc, text = return_clone(args.unit, publish_ledger=not args.no_publish_ledger)
    else:
        rc, text = 0, status(args.all)
    print(text)
    return rc


if __name__ == "__main__":
    sys.exit(main())
