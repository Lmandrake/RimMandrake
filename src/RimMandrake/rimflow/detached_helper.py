#!/usr/bin/env python3
"""detached_helper.py — long helper work that runs OUTSIDE the window (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

An in-process helper (the Agent tool) dies with its window, so a window past its context limit cannot restart while
one runs. A detached run lives in its own transient systemd unit and survives the window's restart:

  python3 src/RimMandrake/rimflow/detached_helper.py launch --seat BENCH --item ITEM_ID --brief-file F \
      [--model fable|opus|sonnet] [--max-s none|SECONDS] [--budget-usd 15]
  python3 src/RimMandrake/rimflow/detached_helper.py status [--all]
  python3 src/RimMandrake/rimflow/detached_helper.py finish --unit U     (the unit's ExecStopPost; never by hand)
  python3 src/RimMandrake/rimflow/detached_helper.py return --unit U [--no-publish-ledger]   (the unit's last ExecStopPost)
  python3 src/RimMandrake/rimflow/detached_helper.py backfill-cost [--apply]   (dollars of runs finished before cost_usd)

launch: the item must be on the ledger, and FILED ON origin/main: the helper's clone is made from origin/main, so an item whose
file event sits in an unpublished shard (OWNER.jsonl from --owner-said, say) is one the helper's `rimflow note` refuses for
the whole run (lesson 20261107T214121Z-BENCH-detached-helper-item-not-origin). One fetch, then a search of every shard under
infrastructure/state/ledger/events/ at origin/main; no hit refuses (exit 2) and names the local shard to publish first.
It takes a pool clone <pool>/clones/<ITEM>.det through scratch_clone.py
(reused, synced, when it exists), then starts role_launch's path: systemd-run --user + claude_bounded.sh -p, the
model passed, NO wall-time limit by default (owner, 2026-11-08: "No time limits please"; --max-s none or 0). An explicit
--max-s SECONDS still bounds it twice (the unit's RuntimeMaxSec and claude_bounded's scope). Spend is bounded by
claude --max-budget-usd. The brief gets a footer: work in the clone, land with ./publish, put state, evidence and one
imperative NEXT on the item as a rimflow note and publish the shard.
finish: runs when the unit stops for any reason (done, failed, killed at its bound). It first KILLs and stops the run's
claude_bounded scope (claude-seat-<seat>-<unit>.scope): claude lives there, outside the unit, so a stopped unit alone left
it running and billing (DETACHED_STOP_FIX_ORPHAN_KEEPS_BILLING, 2026-11-03: killed at 15:06:59, ran to ~15:13). It writes the outcome as a note
on the item, publishes the seat's shard from the clone, and appends one line to the Conductor log. Once per run. A run
that ends success with its item still open and no `LEFT OPEN:` note since it began gets one plain OWED line in that note,
that log line and its record (`owed_close`, which MATURATION_NOW's Needs Conductor lists while the item stays open); it
closes nothing (RIMMANDRAKE_FLAG_DETACHED_SUCCESS_LEAVING_ITEM_OPEN, 2026-11-15: a run fixed 17 gaps, exited 0, and its
item stayed `proposed` until a hand closed it).
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
import json
import os
import re
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import run_tmp  # noqa: E402  (its own TMPDIR: TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP)
try:                                    # whole text, never a silent cut (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS)
    from . import fulltext
except ImportError:
    import fulltext  # noqa: E402

DEFAULT_MAX_S = None    # unbounded: no RuntimeMaxSec on the unit, no CLAUDE_SCOPE_RUNTIME_MAX (owner 2026-11-08)
MIN_MAX_S = 60
GRACE_S = 120          # finish + publish time on top of the run's own bound
DEFAULT_BUDGET_USD = 15.0
MODELS = ("fable", "opus", "sonnet")  # owner ladder 2026-11-12: Fable for blank-page design; Haiku is banned
# The CLI alias "fable" resolved to claude-fable-5-1 (measured 2026-11-12); the ladder means Fable 5.2, so pass the full id.
MODEL_IDS = {"fable": "claude-fable-5-2"}
SEATS = ("BENCH", "STEVE", "RUNNER")   # FOUNDRY retired (owner by card 2026-11-02)
REAL_LOG = "/mnt/d/ClaudeWork/rimmandrake/conductor/log.md"
ORIGIN_REF = "origin/main"
DEAD_STATES = ("inactive", "failed", "not-found")   # a unit in one of these runs nothing; "unknown" is not proof of death
KILL_STATUSES = ("HUP", "INT", "KILL", "TERM", "129", "130", "137", "143")   # systemd's EXIT_STATUS of a signal stop
LAUNCH_GRACE_S = 120   # a record "launching" this young may simply not have its unit yet
RETURN_WAIT_S = 600    # how long launch waits for the run before to give the clone back (a 3.6 GB bundle takes minutes)
RETURN_POLL_S = 10
EVENTS_REL = "infrastructure/state/ledger/events"

FOOTER = """

---
You are a DETACHED helper: you run in your own systemd unit, outside any window, in the clone {clone} (your cwd).
Ledger item: {item}. Seat: {seat}. {bound_text}; spend bound ${budget}.
- Work only in that clone. Land code with `./publish -m "subject" <explicit paths>` (never git add -A, never --force).
- First, claim your item: `python3 src/RimMandrake/rimflow/cli.py claim {item} --seat {seat} --why "detached run"`.
- At the end, close it with the sha ./publish printed: `python3 src/RimMandrake/rimflow/cli.py close {item} --sha <sha>
  --seat {seat} --why "..."` (an operational item also takes `--live`), or, when anything is left, write a note whose
  text starts `LEFT OPEN:` and says exactly what. A run that ends success with its item open and no such note is
  flagged to the Conductor.
- Before you stop, and at least every 20 minutes: write your state, evidence paths and one imperative NEXT as
  `python3 src/RimMandrake/rimflow/cli.py note {item} --text "..." --seat {seat} --why "detached run"`, then publish the
  shard: `./publish -m "ledger: {item} note" infrastructure/state/ledger/events/{seat}.jsonl`.
- Nobody reads your stdout until you end; the note is what the Conductor sees. End with a 5-line summary.
"""


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
    tmp = p + ".tmp"
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


def origin_check(item, runner=subprocess.run, repo=None):
    """-> None when `item` is filed on origin/main, else the one-line refusal text.

    One fetch (the ref could be stale), then `git grep` of every shard under EVENTS_REL at origin/main for lines holding the
    id, kept only if filed_ids() reads the item from one: a `file` event's id or a `spawn` event's name. An item found is
    allowed even when the fetch failed; one not found says so when it did, since origin/main may then be stale. A git that
    cannot be read at all (not 0 or 1) refuses too: a blind instrument is not a pass."""
    repo = repo or REPO
    stale = ""
    try:
        r = runner(["git", "fetch", "-q", "--no-tags", "origin", "main"], cwd=repo, capture_output=True, text=True,
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
    say = ("publish %s first" % ", ".join(shards)) if shards else "no local shard holds it either"
    return "refused: %s is not on %s; %s%s" % (item, ORIGIN_REF, say, " (%s; %s may be stale)" % (stale, ORIGIN_REF) if stale else "")


def live_status(rec, runner=subprocess.run, now=None):
    """The record's status as its unit sees it: "launching" or "running" whose unit is inactive, failed or not found is
    "dead" (finish never ran: the 2026-11-14 stale records). A young "launching" record and an unreadable unit keep theirs."""
    st = rec.get("status")
    if st not in ("launching", "running"):
        return st
    if st == "launching" and (now or time.time()) - (rec.get("at") or 0) < LAUNCH_GRACE_S:
        return st
    import role_launch as RL
    return "dead" if RL.unit_state(rec["unit"], runner=runner) in DEAD_STATES else st


def all_records(root=None):
    d = runs_dir(root)
    for n in sorted(os.listdir(d)):
        if n.endswith(".json") and not n.endswith(".out.json"):
            rec = read_record(n[:-5], root)
            if rec and rec.get("unit"):
                yield rec


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


def hold_until_returned(dest, runner=subprocess.run, sleep=time.sleep, now=None, root=None, kept_ok=False):
    """-> None when no run holds `dest` (waiting up to RETURN_WAIT_S while one is giving it back), else the refusal line."""
    waited = 0
    while True:
        held = clone_holders(dest, runner, now, root, kept_ok)
        if not held:
            return None
        hard = [h for h in held if not h[1]]
        if hard or waited >= RETURN_WAIT_S:
            return "refused: clone %s is held%s: %s" % (
                dest, "" if hard else " after %d s of waiting" % waited, " | ".join(h[2] for h in (hard or held)))
        sleep(RETURN_POLL_S)
        waited += RETURN_POLL_S


def take_clone(item, runner=subprocess.run):
    """-> (clone path, log line). A pool clone named <ITEM>.det: made by scratch_clone.py, or reused and synced."""
    name = item + ".det"
    dest = os.path.join(pool_root(), "clones", name)
    if os.path.isdir(os.path.join(dest, ".git")):
        r = runner(["./sync"], cwd=dest, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        return dest, "reused %s (sync exit %d: %s)" % (dest, r.returncode, ((r.stdout or "") + (r.stderr or "")).strip())
    env = dict(os.environ, RM_SCRATCH_ROOT=pool_root(), RM_SEAT="clones")
    r = runner(["python3", os.path.join(REPO, "src", "RimMandrake", "Utils", "scratch_clone.py"), "clone",
                "detached run for " + item, "--name", name, "--checkout", "--fetch"],
               env=env, capture_output=True, text=True, timeout=540, stdin=subprocess.DEVNULL)
    if r.returncode or not os.path.isdir(os.path.join(dest, ".git")):
        raise RuntimeError("scratch_clone failed (exit %d): %s" % (r.returncode, ((r.stdout or "") + (r.stderr or ""))))
    return dest, "made " + dest


def claude_bin():
    import shutil
    return os.environ.get("RM_DISPATCHER_CLAUDE") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")


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
            "-p", "RuntimeMaxSec=1800", "-p", "StandardOutput=file:" + rec["out"] + ".return", "-p", "StandardError=inherit",
            *env, "/usr/bin/python3", me, "return", "--unit", rec["unit"]]


def owns_clone(rec):
    """True for the pool clone <pool>/clones/<ITEM>.det that launch made or reused itself. A clone the caller gave with
    --clone is theirs, and so is any other path: this step never touches them."""
    how = rec.get("clone_how") or ""
    want = os.path.join(pool_root(), "clones", rec.get("item", "") + ".det")
    return how.startswith(("made ", "reused ")) and os.path.abspath(rec.get("clone") or "") == os.path.abspath(want)


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


def evict_clone(item, clone, before=None):
    """-> (bundle dir or None, why the clone stayed or None). relentless Effects.remove_clone: every commit, stash and
    dirty file goes to the store's bundles first, then the clone is parked as a warm spare or removed. A bundle that
    cannot be made keeps the clone (and alarms on the relentless journal)."""
    import relentless as R
    store = R.Store(pool_root())
    fx = R.Effects(R.rules(), store)
    out = fx.remove_clone({"clone": clone, "item": item}, before)
    if os.path.isdir(clone):
        return out, "the clone stayed: its bundle or its removal failed (alarm on the relentless journal)"
    return out, None


def _tail(r, n=140):
    return ((getattr(r, "stdout", "") or "") + (getattr(r, "stderr", "") or "")).strip()[-n:]


def return_clone(unit, now=None, runner=subprocess.run, evictor=None, busy=None, publish_ledger=True, root=None, log_path=None):
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
        return 0, "kept %s: still in use by %s" % (clone, ", ".join(mates))
    if not os.path.isdir(clone):
        rec.update(returned=now, return_steps=["clone already gone"])
        write_record(rec, root)
        return 0, "returned %s: the clone was already gone" % unit
    if (busy or clone_busy)(clone):
        return 0, "kept %s: a process is working in it" % clone
    steps = []

    def run(argv, what, timeout=300):
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
        r = run(["git", "status", "--porcelain", "--", shard], "shard status", 60)
        if r.returncode == 0 and (r.stdout or "").strip():
            r = run(["./publish", "-m", "ledger: %s returned its clone" % item, shard], "publish")
            m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", _tail(r, 400))
            steps.append("publish " + (m.group(1)[:10] if m else "FAILED: " + _tail(r, 100)))
    run(["./sync"], "sync")
    told = []

    def before(bundle):     # the clone still stands: say where its leftovers went
        told.append(bundle)
        if not publish_ledger:  # its dirty ledger lines ride in the bundle; a note's publish would send them upstream too
            return
        text = ("DETACHED run %s left work no remote had; its clone %s is bundled at %s and goes back to the pool. NEXT: "
                "restore it from that bundle (relentless restore_bundle) if the work is still wanted." % (unit, clone, bundle))
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


def return_all(runner=subprocess.run, evictor=None, busy=None, publish_ledger=True, root=None, now=None, grace_s=3600):
    """Every finished run whose pool .det clone is still standing and not returned (a return step that never ran), except
    a run that ended less than grace_s ago: whoever launched it may still be reading the clone."""
    out, worst = [], 0
    now = now or time.time()
    d = runs_dir(root)
    for n in sorted(os.listdir(d)):
        if not n.endswith(".json") or n.endswith(".out.json"):
            continue
        rec = read_record(n[:-5], root)
        if rec and rec.get("status") == "finished" and not rec.get("returned") and owns_clone(rec) \
                and os.path.isdir(rec["clone"]) and now - (rec.get("ended") or rec.get("at") or 0) >= grace_s:
            rc, text = return_clone(rec["unit"], now=now, runner=runner, evictor=evictor, busy=busy, publish_ledger=publish_ledger, root=root)
            out.append(text)
            worst = max(worst, rc)
    return worst, "\n".join(out) or "no finished run holds a pool clone"


def launch_argv(rec, msg, claude):
    """role_launch.launch_argv's shape, plus ExecStopPost=finish so the outcome is recorded even on a kill."""
    clone, unit, seat = rec["clone"], rec["unit"], rec["seat"]
    bounded = os.path.join(clone, "src", "RimMandrake", "Utils", "claude_bounded.sh")
    bound = int(rec["max_s"]) + GRACE_S if rec.get("max_s") else None     # None: unbounded
    path = os.path.dirname(claude) + ":" + os.environ.get("PATH", "/usr/bin:/bin")
    finish = "/usr/bin/python3 %s finish --unit %s" % (shlex.quote(os.path.abspath(__file__)), unit)
    wrapup = "-+/usr/bin/python3 %s unit --unit %s --seat %s --clone %s" % (
        shlex.quote(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wrapup.py")), shlex.quote(unit),
        shlex.quote(seat), shlex.quote(clone))
    back = "-" + shlex.join(return_argv(rec))
    cmd = [bounded, "-p", msg, "--model", MODEL_IDS.get(rec["model"], rec["model"]), "--name", "DETACHED %s %s" % (seat, rec["item"]),
           "--max-budget-usd", "%g" % rec["budget_usd"], "--output-format", "json", "--dangerously-skip-permissions"]
    return ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit,
            # append:, never file: — file: hands every ExecStopPost the file at offset 0 and finish's line overwrote the
            # head of claude's JSON (RIMMANDRAKE_KEEP_RUN_RESULT_WHOLE_FINISH_WRITES_OVER); finish also moves its own
            # output off these files (keep_off_result), so the JSON stays whole and alone
            "-p", "StandardOutput=append:" + rec["out"], "-p", "StandardError=append:" + rec["err"],
            "-p", "ExecStopPost=" + finish,
            "-p", "ExecStopPost=" + wrapup,     # the census of what it left (wrapup.py), after finish recorded it
            "-p", "ExecStopPost=" + back,       # last: the pool clone goes back, bundled (return_clone)
            "-p", "WorkingDirectory=-" + clone,    # "-": a gone clone is not fatal, so ExecStopPost still runs (in /)
            "--setenv", "AGENT_SEAT=" + seat, "--setenv", "RIMFLOW_SEAT=" + seat,
            *(sum((["--setenv", "%s=%s" % kv] for kv in run_tmp.env(rec["tmp"]).items()), []) if rec.get("tmp") else []),
            "--setenv", "CLAUDE_SCOPE_UNIT=" + scope_name(seat, unit)[:-len(".scope")],
            "--setenv", "RM_ROLE_UNIT=" + unit, "--setenv", "RM_DETACHED_UNIT=" + unit,
            "--setenv", "RM_DISPATCHER_STATE=" + rec["state"],
            *(["--setenv", "CLAUDE_SCOPE_RUNTIME_MAX=%d" % bound, "-p", "RuntimeMaxSec=%d" % bound] if bound else []),
            "-p", "TimeoutStopSec=30",
            "--setenv", "PATH=" + path, "--"] + cmd


def parse_max_s(v):
    """None, 0, "", "none", "0" -> None (unbounded); else whole seconds (ValueError on junk)."""
    if v is None or str(v).strip().lower() in ("", "none", "0", "infinity", "unbounded"):
        return None
    return int(v)


def launch(seat, item, brief, model, max_s, budget, now=None, runner=subprocess.run, known=None, clone=None, sleep=time.sleep):
    """-> (exit code, text). Refuses an unknown item, one not filed on origin/main, a bad model or seat, an empty brief, and
    a clone another run still holds (after waiting for one that is being given back)."""
    now = now or time.time()
    if seat not in SEATS:
        return 2, "refused: seat %r is not one of %s" % (seat, ", ".join(SEATS))
    if model not in MODELS:
        return 2, "refused: model %r is not one of %s" % (model, ", ".join(MODELS))
    if not (brief or "").strip():
        return 2, "refused: empty brief"
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
    unpublished = origin_check(item, runner=runner)     # before a clone is made or a unit started
    if unpublished:
        return 2, unpublished
    held = hold_until_returned(clone or os.path.join(pool_root(), "clones", item + ".det"), runner, sleep, now,
                               kept_ok=bool(clone))
    if held:
        return 2, held
    if clone:
        how = "given " + clone
    else:
        try:
            clone, how = take_clone(item, runner=runner)
        except Exception as e:  # noqa: BLE001
            return 1, "clone failed: %s" % e
    root = state_dir()
    rec = {"seat": seat, "item": item, "clone": clone, "model": model, "max_s": max_s,
           "budget_usd": float(budget), "at": now, "state": root, "status": "launching", "clone_how": how}
    unit = reserve_record(rec, root)    # a name no other run's record holds; never overwrites one
    msg = brief.rstrip() + FOOTER.format(clone=clone, item=item, seat=seat,
                                         bound_text=("Wall-time bound: %d s" % max_s) if max_s else "no wall-time bound", budget="%g" % budget)
    if runner is subprocess.run:        # its own TMPDIR, deleted by run_tmp.sweep when the unit is gone
        rec["tmp"] = run_tmp.prepare(unit)
        write_record(rec, root)
    r = runner(launch_argv(rec, msg, claude_bin()), capture_output=True, text=True, timeout=60,
               stdin=subprocess.DEVNULL)
    if r.returncode:
        rec["status"] = "launch_failed"
        rec["why"] = ((r.stdout or "") + (r.stderr or "")).strip()
        write_record(rec, root)
        return 1, "LAUNCH FAILED %s: %s" % (unit, rec["why"])
    rec["status"] = "running"
    write_record(rec, root)
    return 0, ("DETACHED %s\n  item %s, model %s, bound %s, $%g\n  clone %s (%s)\n  record %s\n"
               "  it ends with a note on %s and a line in the Conductor log; `detached_helper.py status` lists runs"
               % (unit, item, model, ("%d s" % max_s) if max_s else "none", budget, clone, how, record_path(unit, root), item))


LEFT_OPEN = "LEFT OPEN:"    # a run's note saying what it left (RIMMANDRAKE_FLAG_DETACHED_SUCCESS_LEAVING_ITEM_OPEN)
READ_ITEM = r"""
import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "rimflow"))
import model
item = sys.argv[1]
evs = model.read()
it = model.replay(evs).items.get(item)
print(json.dumps({"state": getattr(it, "state", None),
                  "notes": [e for e in evs if e.get("id") == item and e.get("event") == "note"]}))
"""


def read_item(clone, item):
    """-> {"state", "notes"} for the item as the run's clone folds its ledger (the run's own close sits there before
    any other clone pulls it), or None when that cannot be read."""
    try:
        r = subprocess.run([sys.executable, "-c", READ_ITEM, item], cwd=clone, capture_output=True, text=True,
                           timeout=120, stdin=subprocess.DEVNULL)
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


def owed_close(rec, state, notes):
    """-> the plain line for a run that ended success with its item still open and no LEFT OPEN: note since it
    began, or "". It closes nothing: only evidence closes an item."""
    import model
    if not str(rec.get("result") or "").startswith("success (") or state in model.TERMINAL:
        return ""
    if left_open_noted(notes, rec.get("item"), rec.get("at") or 0):
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


def conductor_line(text, now, path=None):
    """One line in the Conductor log. Same guard as dispatcher.conductor_log: a test process never writes the real log."""
    import doorbell
    path = path or conductor_log_path()
    if (os.path.abspath(path) == os.path.abspath(REAL_LOG)
            and os.environ.get("RM_DISPATCHER_STATE", doorbell.DEFAULT_STATE) != doorbell.DEFAULT_STATE):
        raise RuntimeError("refusing to write the REAL conductor log from a test process: " + path)
    import conductor_log_guard
    conductor_log_guard.refuse_if_test(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n%s — DETACHED RUN ENDED: %s\n" % (iso(now), text))
    return path


def outcome(rec, env):
    """-> (short status, tokens or None, result tail). Reads claude's JSON and systemd's ExecStopPost variables."""
    import role_launch as RL
    res = RL.read_result({"out": rec["out"], "err": rec["err"]})
    svc = env.get("SERVICE_RESULT") or "unknown"
    code = env.get("EXIT_CODE") or "-"
    status = env.get("EXIT_STATUS") or "-"
    tokens = RL.run_tokens(res) if isinstance(res, dict) else None
    if isinstance(res, dict):
        tail = str(res.get("result") or res.get("subtype") or "")
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


def finish(unit, now=None, env=None, runner=subprocess.run, log_path=None, item_reader=None):
    """The unit's ExecStopPost. -> (exit code, text). Once per run: a second call changes nothing."""
    now = now or time.time()
    env = os.environ if env is None else env
    rec = read_record(unit)
    if not rec:
        return 2, "no record for %s" % unit
    if rec.get("status") == "finished":
        return 0, "already finished %s" % unit
    st, tokens, tail = outcome(rec, env)
    usd, how = measured_cost(rec)       # read now, with the tokens, before anything else touches the file
    took = int(now - rec["at"])
    text = ("DETACHED run %s ended %s after %d s, %s tokens, USD %s (model %s). Result: %s. Output %s; clone %s."
            % (unit, st, took, "UNMEASURED" if tokens is None else tokens, _usd(usd), rec["model"], tail or "-",
               rec["out"], rec["clone"]))
    clone, seat, item = rec["clone"], rec["seat"], rec["item"]
    cli = os.path.join(clone, "src", "RimMandrake", "rimflow", "cli.py")
    steps = [stop_scope(seat, unit, runner)]     # first: the unit is gone but claude is not (and TimeoutStopSec=30)
    owed = ""
    if not os.path.isdir(clone):                 # deleted under the run: no clone to note from, the log line still goes
        steps.append("clone gone: no note on the item, nothing published")
    else:
        if st.startswith("success ("):          # its item still open with nothing said: one plain line, everywhere
            got = (item_reader or read_item)(clone, item)
            if isinstance(got, dict):
                owed = owed_close(dict(rec, result=st), got.get("state"), got.get("notes"))
                steps.append("item " + (got.get("state") or "absent") + (": OWED" if owed else ""))
            else:
                steps.append("item state UNMEASURED (its clone's ledger could not be read)")
        if owed:
            text += " OWED: " + owed + "."
        r = runner(["python3", cli, "note", item, "--text", text, "--seat", seat, "--why", "detached run ended"],
                   cwd=clone, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        steps.append("note exit %d" % r.returncode)
        r = runner(["./publish", "-m", "ledger: detached run on %s ended" % item,
                    "infrastructure/state/ledger/events/%s.jsonl" % seat],
                   cwd=clone, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        pub = ((r.stdout or "") + (r.stderr or "")).strip()
        m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", pub)
        steps.append("publish " + (m.group(1)[:10] if m else "exit %d: %s" % (r.returncode, pub)))
    try:
        path = conductor_line("%s on %s (%s seat): %s, %d s, %s tokens, USD %s. %s. READ: rimflow show %s.%s"
                              % (unit, item, seat, st, took, "UNMEASURED" if tokens is None else tokens, _usd(usd),
                                 fulltext.clip(tail, 200, rec["out"]) or "-", item,
                                 " OWED: " + owed + "." if owed else ""), now, log_path)
        steps.append("conductor log " + path)
    except Exception as e:  # noqa: BLE001
        steps.append("conductor log FAILED: %s" % e)
    rec.update(status="finished", ended=now, result=st, tokens=tokens, steps=steps,
               cost_usd=usd if usd is not None else "UNMEASURED", cost_how=how, owed_close=owed)
    write_record(rec)
    return 0, "FINISHED %s: %s" % (unit, "; ".join(steps))


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
    return "\n".join(lines) or "no detached runs" + ("" if show_all else " running (--all lists finished ones)")


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
    a.add_argument("--budget-usd", type=float, default=DEFAULT_BUDGET_USD)
    a.add_argument("--clone", help="an existing clone to run in (default: a pool clone <ITEM>.det)")
    f = sub.add_parser("finish")
    f.add_argument("--unit", required=True)
    b = sub.add_parser("return", help="give the run's pool clone back, bundled (the unit's last step; --all sweeps strays)")
    b.add_argument("--unit")
    b.add_argument("--all", action="store_true", help="every finished run whose pool .det clone still stands")
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
        rc, text = launch({"CONDUCTOR": "BENCH"}.get(args.seat.upper(), args.seat.upper()), args.item, brief, args.model, args.max_s, args.budget_usd,
                          clone=args.clone)
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
