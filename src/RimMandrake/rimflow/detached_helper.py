#!/usr/bin/env python3
"""detached_helper.py — long helper work that runs OUTSIDE the window (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

An in-process helper (the Agent tool) dies with its window, so a window past its context limit cannot restart while
one runs. A detached run lives in its own transient systemd unit and survives the window's restart:

  python3 src/RimMandrake/rimflow/detached_helper.py launch --seat BENCH --item ITEM_ID --brief-file F \
      [--model fable|opus|sonnet] [--max-s none|SECONDS] [--budget-usd 15]
  python3 src/RimMandrake/rimflow/detached_helper.py status [--all]
  python3 src/RimMandrake/rimflow/detached_helper.py finish --unit U     (the unit's ExecStopPost; never by hand)
  python3 src/RimMandrake/rimflow/detached_helper.py return --unit U [--no-publish-ledger]   (the unit's last ExecStopPost)

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
on the item, publishes the seat's shard from the clone, and appends one line to the Conductor log. Once per run.
return: the run's last step gives the pool clone <ITEM>.det BACK (RIMMASTER_RELEASE_POOL_FROZEN_ITEMS_HOLD_CLONES, 2026-11-07:
three finished .det clones, a stopped pipeline's ten and SHOWINGS held 16 of 16 pool places and 67 of 70 GB while little ran).
It lands the clone's conversation records, publishes the seat shard if the run left it dirty, levels the clone with
./sync, then hands what is still unlanded to Effects.remove_clone, which bundles every commit, stash and dirty file to
the store before the clone goes (or parks it as a warm spare). A bundle that cannot be made KEEPS the clone, and the step
says so; a clone the caller gave with --clone, one a process sits in and one another live run uses are never touched.
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
EVENTS_REL = "infrastructure/state/ledger/events"

FOOTER = """

---
You are a DETACHED helper: you run in your own systemd unit, outside any window, in the clone {clone} (your cwd).
Ledger item: {item}. Seat: {seat}. {bound_text}; spend bound ${budget}.
- Work only in that clone. Land code with `./publish -m "subject" <explicit paths>` (never git add -A, never --force).
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


def take_clone(item, runner=subprocess.run):
    """-> (clone path, log line). A pool clone named <ITEM>.det: made by scratch_clone.py, or reused and synced."""
    name = item + ".det"
    dest = os.path.join(pool_root(), "clones", name)
    if os.path.isdir(os.path.join(dest, ".git")):
        r = runner(["./sync"], cwd=dest, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        return dest, "reused %s (sync exit %d: %s)" % (dest, r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-160:])
    env = dict(os.environ, RM_SCRATCH_ROOT=pool_root(), RM_SEAT="clones")
    r = runner(["python3", os.path.join(REPO, "src", "RimMandrake", "Utils", "scratch_clone.py"), "clone",
                "detached run for " + item, "--name", name, "--checkout", "--fetch"],
               env=env, capture_output=True, text=True, timeout=540, stdin=subprocess.DEVNULL)
    if r.returncode or not os.path.isdir(os.path.join(dest, ".git")):
        raise RuntimeError("scratch_clone failed (exit %d): %s" % (r.returncode, ((r.stdout or "") + (r.stderr or ""))[-300:]))
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
    said = [RL._stop_call(runner, ["systemctl", "--user", "kill", "--signal=SIGKILL", scope], 20),
            RL._stop_call(runner, ["systemctl", "--user", "stop", "--no-block", scope], 20)]
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


def other_users(rec, root=None):
    """Units of other runs that are still going and hold this run's clone."""
    out = []
    d = runs_dir(root)
    for n in sorted(os.listdir(d)):
        if not n.endswith(".json") or n.endswith(".out.json"):
            continue
        o = read_record(n[:-5], root)
        if o and o.get("unit") != rec.get("unit") and o.get("clone") == rec.get("clone") \
                and o.get("status") in ("launching", "running"):
            out.append(o["unit"])
    return out


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
    mates = other_users(rec, root)
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
        bundle, kept = None, "eviction raised: %s" % str(e)[:200]
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
                unit, item, clone, "KEPT" if kept else "returned, leftovers bundled at %s" % bundle, "; ".join(steps)[-300:], item),
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
            "-p", "StandardOutput=file:" + rec["out"], "-p", "StandardError=file:" + rec["err"],
            "-p", "ExecStopPost=" + finish,
            "-p", "ExecStopPost=" + wrapup,     # the census of what it left (wrapup.py), after finish recorded it
            "-p", "ExecStopPost=" + back,       # last: the pool clone goes back, bundled (return_clone)
            "--working-directory", clone,
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


def launch(seat, item, brief, model, max_s, budget, now=None, runner=subprocess.run, known=None, clone=None):
    """-> (exit code, text). Refuses an unknown item, one not filed on origin/main, a bad model or seat, an empty brief."""
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
        rec["why"] = ((r.stdout or "") + (r.stderr or "")).strip()[-300:]
        write_record(rec, root)
        return 1, "LAUNCH FAILED %s: %s" % (unit, rec["why"])
    rec["status"] = "running"
    write_record(rec, root)
    return 0, ("DETACHED %s\n  item %s, model %s, bound %s, $%g\n  clone %s (%s)\n  record %s\n"
               "  it ends with a note on %s and a line in the Conductor log; `detached_helper.py status` lists runs"
               % (unit, item, model, ("%d s" % max_s) if max_s else "none", budget, clone, how, record_path(unit, root), item))


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
        if len(tail) > 400:   # the end of the reply, cut at a word
            tail = "..." + tail[-400:].split(" ", 1)[-1]
        if res.get("is_error"):
            svc = svc + "/claude-error"
    else:
        try:
            with open(rec["err"], encoding="utf-8", errors="replace") as f:
                tail = "no result JSON; stderr tail: " + f.read()[-300:]
        except OSError:
            tail = "no result JSON, no stderr"
    return "%s (%s %s)" % (svc, code, status), tokens, " ".join(tail.split())


def finish(unit, now=None, env=None, runner=subprocess.run, log_path=None):
    """The unit's ExecStopPost. -> (exit code, text). Once per run: a second call changes nothing."""
    now = now or time.time()
    env = os.environ if env is None else env
    rec = read_record(unit)
    if not rec:
        return 2, "no record for %s" % unit
    if rec.get("status") == "finished":
        return 0, "already finished %s" % unit
    st, tokens, tail = outcome(rec, env)
    took = int(now - rec["at"])
    text = ("DETACHED run %s ended %s after %d s, %s tokens (model %s). Result: %s. Output %s; clone %s."
            % (unit, st, took, "UNMEASURED" if tokens is None else tokens, rec["model"], (tail if len(tail) <= 300 else "..." + tail[-300:].split(" ", 1)[-1]) or "-",
               rec["out"], rec["clone"]))
    clone, seat, item = rec["clone"], rec["seat"], rec["item"]
    cli = os.path.join(clone, "src", "RimMandrake", "rimflow", "cli.py")
    steps = [stop_scope(seat, unit, runner)]     # first: the unit is gone but claude is not (and TimeoutStopSec=30)
    r = runner(["python3", cli, "note", item, "--text", text, "--seat", seat, "--why", "detached run ended"],
               cwd=clone, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    steps.append("note exit %d" % r.returncode)
    r = runner(["./publish", "-m", "ledger: detached run on %s ended" % item,
                "infrastructure/state/ledger/events/%s.jsonl" % seat],
               cwd=clone, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    pub = ((r.stdout or "") + (r.stderr or "")).strip()
    m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", pub)
    steps.append("publish " + (m.group(1)[:10] if m else "exit %d: %s" % (r.returncode, pub[-120:])))
    try:
        path = conductor_line("%s on %s (%s seat): %s, %d s, %s tokens. %s. READ: rimflow show %s."
                              % (unit, item, seat, st, took, "UNMEASURED" if tokens is None else tokens,
                                 (tail if len(tail) <= 200 else "..." + tail[-200:].split(" ", 1)[-1]) or "-", item), now, log_path)
        steps.append("conductor log " + path)
    except Exception as e:  # noqa: BLE001
        steps.append("conductor log FAILED: %s" % e)
    rec.update(status="finished", ended=now, result=st, tokens=tokens, steps=steps)
    write_record(rec)
    return 0, "FINISHED %s: %s" % (unit, "; ".join(steps))


def status(show_all=False, runner=subprocess.run):
    import role_launch as RL
    lines = []
    d = runs_dir()
    for n in sorted(os.listdir(d)):
        if not n.endswith(".json") or n.endswith(".out.json"):
            continue
        rec = read_record(n[:-5])
        if not rec or (rec.get("status") == "finished" and not show_all):
            continue
        live = RL.unit_state(rec["unit"], runner=runner) if rec.get("status") != "finished" else "-"
        lines.append("%s  %s  %s  item %s  %s  started %s" % (rec["unit"], rec.get("status"), live, rec["item"],
                                                               rec["model"], iso(rec["at"])))
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
    args = ap.parse_args(argv)
    if args.cmd == "launch":
        brief = args.brief
        if args.brief_file:
            with open(args.brief_file, encoding="utf-8") as fh:
                brief = fh.read()
        rc, text = launch({"CONDUCTOR": "BENCH"}.get(args.seat.upper(), args.seat.upper()), args.item, brief, args.model, args.max_s, args.budget_usd,
                          clone=args.clone)
    elif args.cmd == "finish":
        rc, text = finish(args.unit)
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
