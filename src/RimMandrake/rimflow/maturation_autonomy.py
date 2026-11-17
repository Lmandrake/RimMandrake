#!/usr/bin/env python3
"""maturation_autonomy.py: the layer of the Dispatch step that leaves no mod waiting on the Conductor's hand.

Item RIMMANDRAKE_AUTOMATE_MATURATION_HAND_STEPS_MODS_SAT_WAITING. The owner, 2026-11-15: "we're not going to just
manually frog walk things along anymore. It's taking days because you let things sit. Get the automation going so things
can keep moving even if that means we have to pause them to fix something. But at least then it's paused animation
instead of manual replication of no automation."

maturation_dispatch.decide() still makes the per-stage decision; resolve() runs after it, on the same tick, and gives
every mod exactly one class:
  launch   a run starts this tick: a builder, a blind judge or a live driver (decide's own), a STEWARD run (the
           Conductor's old hand step: confirm an exit it reads, route a not-met visit's failed lines back as named items,
           advance a mod whose exit tests all pass, the locked-change chain), or a FIXER on a road-back item
  wait     on a named running unit, a busy game driver (queue order recorded), a held bridge, full slots, an account
           hold, a settling run, or the Designer's own launcher
  paused   the pipeline stops that mod and says why and what un-pauses it; ops_watch raises ONE alarm with a fixed id
           (OPS_MATURATION_MOD_PAUSED) while any mod is paused, so a repeat reopens it; a pause whose cause is a
           filed open fix item (coverage stopped, or a Designer blocked on a named item) launches that item's one
           fixer run itself (_stop_tickets), and stays paused meanwhile
  rested   a passed version: nothing runs and nothing is asked; opening the next version is an ordering call
  owner    a stop that is genuinely his (his walk, a Designer turn waiting on him, a lock
           with recorded evidence against 0.1.0): a ready-to-ask card text goes in the Conductor log once, and it
           quotes the evidence (his Evidence-for-Ask ruling, 2026-11-15)
A new mod whose concept tree is locked and whose Design Version is not is LOCKED AT 0.1.0 BY THE PIPELINE (autolock:
locked_by "pipeline", per_ruling M.EVIDENCE_FOR_ASK, one delegated record in his daily digest) unless version_evidence()
reads recorded evidence that 0.1.0 is wrong; only then does it go to him, with that evidence in the card.
A steward or fixer run is tried ONCE per state (its key); if it ends and the state has not moved, the mod is PAUSED,
never retried (the owner's condition, 2026-11-14: "As long as we don't have automated loops rejecting/cycling things,
we can't get into too much trouble."). A launch that never started on a TRANSIENT fault (a git lock, its item not yet
on origin/main: transient()) is not a run: the next tick tries it again on the same item, up to launch_tries (3), then
PAUSED naming the count and the last fault (RIMMANDRAKE_RETRY_STEWARD_LAUNCH_GIT_LOCK_COUNTED_AS_SPENT).
`maturation_dispatch.py clear MOD` releases a mod's never-launched keys and its ended runs outside an open road back. A mod in `wait` with nothing named running, or with no class, for stalled_min
(10) raises maturation.stalled (OPS_MATURATION_MOD_STALLED).

Never: certify, lock (except the autolock above), classify Convergent/Divergent, loosen a bar, take the bridge or a game, launch on a mod with a
live unit. The steward brief says so, and a steward is opus (judging another agent's work, Agent_Policy.md).
Selftest: selftest_maturation_autonomy.py.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import maturation as M          # noqa: E402

UNM = "UNMEASURED"
EXCLUDE_MARKER = ".maturation-exclude"      # a concept folder holding it is never discovered (test fixtures)
WAIT = {"live", "settling", "driver_busy", "bridge_held", "slots_full", "slots_unknown", "account_hold", "designer_wait",
        "queued", "launch_retry", "upstream_wait", "certificate"}
# a launch that never started on one of these is retried (measured 2026-11-15: a git index.lock at publish, then the
# launcher's "not on origin/main" refusal, read as a spent steward run)
TRANSIENT = re.compile(r"index\.lock|is not on origin/main|ingest\.lock stayed busy|publish stopped|another "
                       r"ingest/publish holds|systemd-run did not answer")
# a refusal no retry can pass: the clone is held by a run whose finish never ran (detached_helper.clone_holders). It
# read transient when the filing's own publish line said "publish stopped", and three tries went in two minutes
# (RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD, 2026-11-16)
NEVER_TRANSIENT = re.compile(r"finish step never ran")


def transient(text):
    """-> True when a launch failure's text names a transient fault (a lock, an unpublished shard, a silent
    systemd-run that left no unit), and no refusal a retry cannot pass."""
    return bool(text) and bool(TRANSIENT.search(str(text))) and not NEVER_TRANSIENT.search(str(text))


def releasable(s, key, x):
    """-> True when `clear` may release book entry x: it never launched, or it ended outside the open road back and
    no closed road back re-keyed after it (those keys are the road back's own record)."""
    if not isinstance(x, dict):
        return False
    if x.get("failed") and not x.get("unit"):
        return True
    if x.get("road_back_closed"):
        return False
    rb = s.get("road_back") or {}
    book = s.get("steward") or {}
    opener = next((k for k, v in book.items() if isinstance(v, dict) and v.get("item") == rb.get("caused_by")), None)
    return not (opener and str(key).split("|")[:4] == opener.split("|")[:4])
LAUNCH = {"launch", "launched", "would_launch"}
# a Conductor hold stands: nothing automatic is routed past it, a road-back fixer included
# (RIMMANDRAKE_HONOUR_CONDUCTOR_HOLD_ROAD_BACK_FIXER_IGNORED_IT)
HOLDS = {"held"}
STEWARD_ON = {"hand_step", "ready", "exit_met", "exit_not_met"}
OWNER_STAGES = {"his_walk": "his live walk (Stage 8): the version passes on his words alone"}
# A passed version rests (spec: "pass record written; the mod rests"); opening the next one is weighed against the other
# mods, an ordering call (delegation_policy.md §1), so it is no card to him (Evidence-for-Ask, owner 2026-11-15).
RESTED = ("the version passed and the mod rests; opening its next version is the Conductor's ordering call against "
          "the other mods (delegation_policy.md §1, Evidence-for-Ask), taken with `maturation.py next-version`")
STEWARD_STAGES = {"preflight", "pre_human"}     # stages whose whole step is the steward's: run it, then advance
CHAIN_AFTER = ("coverage_release", "coverage_stop", "lock")
ROAD_BACK_STAGES = ("offline_build", "blind_challenge", "in_game")


def _h(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()[:8]


def _iso_ts(s):
    try:
        import datetime as dt
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


# ---- discovery: a concept the Designer is working is seen, seeded when it has no record ------------------------------

def discovered(root):
    """-> concept folders under design/concepts with a stage.json (the Designer works them) and no EXCLUDE_MARKER."""
    d = os.path.join(root, "design", "concepts")
    out = []
    for m in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, m)
        if os.path.isfile(os.path.join(p, "stage.json")) and not os.path.exists(os.path.join(p, EXCLUDE_MARKER)):
            out.append(m)
    return out


def seed_and_land(root, mod):
    """Seed the mod's maturation record in this clone and land it (land.sh -m: a temp index, nothing else touched)."""
    rec, made = M.seed_mod(root, mod)
    if not made:
        return "had a record"
    import designer_stage as DS
    p = subprocess.run([DS.LAND, "-m", "maturation: seed %s's stage record (Dispatch step, a Designer concept with no "
                        "record)" % mod, "design/concepts/%s/%s" % (mod, M.RECORD)], cwd=root, capture_output=True,
                       text=True, timeout=300, env=dict(os.environ, LAND_REPO=root))
    if p.returncode:
        # the record made here never reached origin/main: remove it, so the next tick seeds again (a kept one read as
        # "had a record" and its seed_refused stood for good; RIMMANDRAKE_RETRY_SEED_LANDING_LOCAL_RECORD_KEPT_REFUSAL)
        try:
            os.remove(os.path.join(M.mod_dir(root, mod), M.RECORD))
        except OSError:
            pass
        raise RuntimeError("land.sh exited %d: %s" % (p.returncode, p.stderr.strip()))
    return (p.stdout.strip().splitlines() or ["PUBLISHED ?"])[-1]


def widen(root, cfg, st, apply, fx=None):
    """-> cfg with the discovered concepts appended to `advancing` (seeding each with no record, only with apply), and
    the in-game candidates ordered by how long they have queued (fair across mods: the one live game goes to the
    longest waiter). Seed refusals are kept in st for resolve() to PAUSE on."""
    fx = fx or {}
    cfg = dict(cfg)
    adv = list(cfg.get("advancing") or [])
    found = fx["discovered"]() if "discovered" in fx else discovered(root)
    seed = fx.get("seed", seed_and_land)
    st.setdefault("seed_refused", {})
    import mod_owner_hold as OH
    held = OH.load()
    for m in found:
        if m not in adv:
            adv.append(m)
        if m in held:
            continue        # the owner holds it (mod_owner_hold.py): not seeded; the tick lists it HELD BY OWNER
        if not os.path.isfile(os.path.join(root, "design", "concepts", m, M.RECORD)) and apply:
            try:
                st["seed_refused"].pop(m, None)
                st.setdefault("seeded", {})[m] = seed(root, m)
            except Exception as e:   # noqa: BLE001
                st["seed_refused"][m] = "%s: %s" % (type(e).__name__, e)
    q = st.get("ingame_queue") or {}
    adv.sort(key=lambda m: (0, q[m]) if m in q else (1, 0))     # stable: list order among the rest
    cfg["advancing"] = adv
    return cfg


# ---- the Designer lane and the locked-change chain -------------------------------------------------------------------

def designer_state(root, mod):
    """-> stage.json, with the titles of record.json's asks under "_asks" (for an owner card), or None."""
    try:
        with open(os.path.join(root, "design", "concepts", mod, "stage.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(st, dict):    # a wrong-shaped file is unreadable, never a crash of the tick
        return None
    try:
        with open(os.path.join(root, "design", "concepts", mod, "record.json"), encoding="utf-8") as f:
            st["_asks"] = [a.get("title") or a.get("id") for a in json.load(f).get("asks") or [] if isinstance(a, dict)]
    except (OSError, ValueError, AttributeError):
        pass
    return st


# The Designer's Dispatcher lanes: Claude's and Codex's (dispatcher_schedule.json, item
# RIMMANDRAKE_DRAFT_BIOME_DESIGNER_PASSES_WITH_CODEX_BEFORE_RESET); a reader of one lane alone calls a Codex run "nothing".
DESIGNER_ROLES = ("Designer", "DesignerCodex")


def designer_unit(mod, tail=600):
    """-> the Dispatcher's Designer role unit live on this concept, or None: the newest Designer launch for
    design/concepts/<mod> in the Dispatcher's journal, if systemd says it is active."""
    try:
        import doorbell
        with open(os.path.join(doorbell.state_dir(), "journal.jsonl"), encoding="utf-8") as f:
            lines = f.readlines()[-tail:]
    except (OSError, ImportError):
        return None
    seen, other = set(), None
    for ln in reversed(lines):
        if '"Designer' not in ln or '"launched"' not in ln:
            continue
        try:
            e = json.loads(ln)
        except ValueError:
            continue
        if (e.get("blind") or {}).get("role") not in DESIGNER_ROLES:
            continue
        unit, concept = (e.get("blind") or {}).get("unit"), os.path.basename(str(e.get("concept") or ""))
        if not unit or unit in seen:
            continue
        seen.add(unit)
        r = subprocess.run(["systemctl", "--user", "is-active", unit + ".service", unit + ".scope"],
                           capture_output=True, text=True, timeout=30)
        live = "active" in (r.stdout or "").split()
        if concept == mod:
            return unit if live else other
        if live and other is None:      # the Designer slot is busy on another concept: a named wait, not a stall
            other = "the Designer slot (%s on %s)" % (unit, concept)
    return other


def designer_chain(mod, now):
    """-> (chained runs on this concept today, chain_max_per_day) from the Dispatcher's state and schedule, or None when
    either cannot be read. role_launch.chain_ask asks no run-now past the cap, so a ready concept at it sits."""
    try:
        import doorbell
        import role_launch as RL
        with open(os.path.join(doorbell.state_dir(), "state.json"), encoding="utf-8") as f:
            allrs = json.load(f).get("roles") or {}
        with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
            sched = json.load(f)
    except (OSError, ValueError, ImportError, AttributeError):
        return None
    roles = sched.get("roles", sched) if isinstance(sched, dict) else sched
    cap = next((r.get("chain_max_per_day") for r in roles or [] if isinstance(r, dict) and r.get("name") == "Designer"),
               None)
    lanes = [allrs.get(n) or {} for n in DESIGNER_ROLES]
    rs = {"chain_day": {}, "chain_cap_said": []}
    for lane in lanes:
        for k, v in (lane.get("chain_day") or {}).items():
            if isinstance(v, int):
                rs["chain_day"][k] = rs["chain_day"].get(k, 0) + v
        rs["chain_cap_said"] += list(lane.get("chain_cap_said") or [])
    cap = cap if isinstance(cap, int) and not isinstance(cap, bool) else RL.CHAIN_MAX_PER_DAY
    day = RL.day_of(now)
    n = sum(v for k, v in (rs.get("chain_day") or {}).items() if isinstance(v, int) and str(k).startswith(day + " ")
            and os.path.basename(os.path.normpath(str(k).split(" ", 1)[1])) == mod)
    # past the cap a stage not chained today still chains (role_launch.chain_ask: the cap brakes loops, not forward
    # stages), so the cap holds a concept only once the Dispatcher has refused it today (chain_cap_said)
    said = any(str(k).startswith(day + " ") and os.path.basename(os.path.normpath(str(k).split(" ", 1)[1])) == mod
               for k in rs.get("chain_cap_said") or [])
    if n >= cap and not said and n < 2 * cap:
        return None
    return n, cap


def coverage_stopped(dst):
    """-> the coverage_stop event judging stands stopped on, or None: the concept is blocked and its newest coverage
    event (stop, release, locked change, lock) is a stop. A locked change after the stop owes the chain instead."""
    if not isinstance(dst, dict) or dst.get("status") != "blocked" or "OWNER HOLD" in str(dst.get("blocked_on") or ""):
        return None
    ev = [h for h in dst.get("history") or [] if isinstance(h, dict) and h.get("what") in CHAIN_AFTER + ("locked_change",)]
    if not ev:
        return None
    last = max(ev, key=lambda h: _iso_ts(h.get("at")) or 0)
    return last if last.get("what") == "coverage_stop" else None


def chain_owed(dst):
    """-> the locked_change event a chain is owed for, or None. Owed when the newest locked_change is newer than every
    coverage release, coverage stop and lock, and the concept is not locked again (a re-signed tree has had its look)."""
    if not isinstance(dst, dict) or dst.get("status") == "locked":
        return None
    hist = dst.get("history") or []
    lc = [h for h in hist if h.get("what") == "locked_change"]
    if not lc:
        return None
    t = _iso_ts(lc[-1].get("at")) or 0
    after = [_iso_ts(h.get("at")) or 0 for h in hist if h.get("what") in CHAIN_AFTER]
    return lc[-1] if all(t > a for a in after) else None


def final_stop(dst):
    """-> (release, stop) when judging stopped after the FINAL look (a release coverage_judge applied from his grant,
    RIMMANDRAKE_GRANT_LOOK_AFTER_FIXES_CLOSE) and nothing he does (a lock, another release) has followed the stop: the
    next step is his, so a later locked change owes no chain and no fixer runs. Else None."""
    if not isinstance(dst, dict) or not isinstance(dst.get("coverage_releases"), list) or not dst["coverage_releases"]:
        return None
    rel = dst["coverage_releases"][-1]
    if not (isinstance(rel, dict) and rel.get("final")):
        return None
    t = _iso_ts(rel.get("at")) or 0
    hist = [h for h in dst.get("history") or [] if isinstance(h, dict)]
    stops = [h for h in hist if h.get("what") == "coverage_stop" and (_iso_ts(h.get("at")) or 0) > t]
    if not stops:
        return None
    ts = _iso_ts(stops[-1].get("at")) or 0
    if any(h.get("what") in ("coverage_release", "lock") and (_iso_ts(h.get("at")) or 0) > ts for h in hist):
        return None
    return rel, stops[-1]


_LEDGER = {}


def ledger_items():
    """-> {id: Item} from the whole ledger (model.replay), read once per process."""
    if "items" not in _LEDGER:
        import model
        _LEDGER["items"] = model.replay(model.read()).items
    return _LEDGER["items"]


def stop_tickets(dst, s, items):
    """-> [{id}] the coverage-stopped concept's OWN open fix tickets, in order: the items his granted look waits on
    (coverage_release_granted.after), its open road back's items (any kind), and the kind-fix items caused by the
    concept's item. RIMMANDRAKE_RUN_FIX_TICKETS_WHILE_PAUSED: they get their fixer runs while the mod stays paused."""
    import model
    want, out = [], []
    g = dst.get("coverage_release_granted") if isinstance(dst, dict) else None
    want += [i for i in (g or {}).get("after") or [] if i in items]
    rb = (s or {}).get("road_back")
    cbs = set(_road_back_ids(s, rb)) if rb else set()
    want += sorted(i for i, x in items.items() if cbs and x.caused_by in cbs)
    if isinstance(dst, dict) and dst.get("item"):
        want += sorted(i for i, x in items.items() if x.kind == "fix" and x.caused_by == dst["item"])
    # RIMMANDRAKE_FIND_CHAIN_STEWARD_FIXES_WHILE_STOPPED_TICK_BLIND: the locked-change chain steward's look is what
    # stops judging, and it files the gaps caused by its own item; without this they waited on no fixer
    chains = {v.get("item") for k, v in ((s or {}).get("steward") or {}).items()
              if isinstance(v, dict) and v.get("item") and str(k).split("|")[1:2] == ["chain"]}
    want += sorted(i for i, x in items.items() if x.kind == "fix" and x.caused_by in chains)
    for i in want:
        if i not in out and items[i].state and items[i].state not in model.TERMINAL:
            out.append(i)
    return [{"id": i} for i in out]


ITEM_NAME = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){3,}\b")


def blocked_tickets(dst, items):
    """-> [{id}] the open ledger items a blocked Designer's blocked_on names, in the order named (an alarm name or
    unknown word is no item; a closed item is no ticket). RIMMANDRAKE_BUDGET_DESIGNER_EXAM_HELPERS_FIVE_READERS_ZERO_SLOTS:
    a Designer run that ends blocked on a pipeline defect files its fix item and names it; the tick launches it."""
    import model
    out = []
    for i in ITEM_NAME.findall(str((dst or {}).get("blocked_on") or "") if isinstance(dst, dict) else ""):
        x = items.get(i)
        if x is not None and x.state and x.state not in model.TERMINAL and i not in out:
            out.append(i)
    return [{"id": i} for i in out]


def ticket_runs(item):
    """-> [(unit, status)] of the detached runs launched on this item (a hand launch counts as its one fixer run)."""
    import detached_helper as DH
    return [(r.get("unit"), r.get("status")) for r in DH.all_records() if r.get("item") == item]


def exam_gate(root, mod):
    """-> (errors, tree hash): the gate coverage_judge.plan reads before a stage-5 look (an exam that does not pass makes
    it skip). ([], None) when the concept is not at stage 5, is parked, or has no real tree."""
    import concept_tree as CT
    import designer_stage as DS
    d = os.path.join(root, "design", "concepts", mod)
    st = DS.read_json(os.path.join(d, "stage.json"), {}) or {}
    if st.get("stage") != 5 or DS.standing_park(st, d, root):
        return [], None
    try:
        tree = CT.load(d)
    except (OSError, ValueError):
        return [], None
    if not isinstance(tree, dict) or tree.get("dry_walk") is True:
        return [], None
    return DS.exam_errors(DS.read_json(os.path.join(d, "exam.json")), d, st, root), CT.tree_hash(tree)


def version_locked(root, mod):
    v, _ = M.read_json(root, mod, "version/VERSION.json")
    return isinstance(v, dict) and str(v.get("state") or "").startswith("locked")


UPSTREAM_WAIT = re.compile(r"waits for ([A-Za-z0-9_]+) (\d+\.\d+\.\d+) to pass")


def upstream_wait(root, mod):
    """RIMMANDRAKE_READ_STALE_OWNER_HOLD_AS_WAITING: (mod, version, where it stands) when this mod's VERSION.json state
    says it waits for another mod's version to pass ("waits for Pyrelands 0.1.0 to pass", his card 2026-11-13) and that
    version's version/stage_record.json does not yet read stage passed; None when nothing upstream explains a wait."""
    v, _ = M.read_json(root, mod, "version/VERSION.json")
    m = UPSTREAM_WAIT.search(str((v if isinstance(v, dict) else {}).get("state") or ""))
    if not m:
        return None
    up, uv = m.group(1), m.group(2)
    rec, err = M.read_json(root, up, "version/stage_record.json")
    rec = rec if isinstance(rec, dict) else {}
    if rec.get("version") == uv and rec.get("stage") == "passed":
        return None
    return up, uv, (err or ("at %s" % rec.get("stage") if rec.get("version") == uv else
                            "its stage record names version %s" % rec.get("version")))


SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def version_evidence(root, mod):
    """-> the recorded evidence that 0.1.0 is NOT this mod's Design Version (his Evidence-for-Ask ruling, 2026-11-15:
    the pipeline takes the obvious answer unless evidence says otherwise). Each entry names its file and quotes it; []
    means a new mod, and the pipeline locks 0.1.0 itself."""
    ev = []
    v, err = M.read_json(root, mod, "version/VERSION.json")
    if err and err != "no file":
        ev.append("version/VERSION.json is %s" % err)
    elif v is not None and not isinstance(v, dict):
        ev.append("version/VERSION.json is not an object")
    v = v if isinstance(v, dict) else {}
    if v.get("version") not in (None, "", "0.1.0"):
        ev.append("version/VERSION.json names version %r, not 0.1.0" % v.get("version"))
    state = str(v.get("state") or "")
    if state and not re.match(r"^(open|locked)\b", state):
        ev.append("version/VERSION.json state reads %r" % state)
    rec, _ = M.read_json(root, mod, M.RECORD)
    rec = rec if isinstance(rec, dict) else {}
    rv = str(rec.get("version") or "")
    if SEMVER.match(rv) and rv != "0.1.0":
        ev.append("%s names version %s" % (M.RECORD, rv))
    if rec.get("stage") == "passed":
        ev.append("%s reads stage passed (a version already passed)" % M.RECORD)
    vd = os.path.join(M.mod_dir(root, mod), "version")
    for fn in sorted(os.listdir(vd)) if os.path.isdir(vd) else []:
        m = re.match(r"^stage_record_(.+)\.json$", fn)
        if m and SEMVER.match(m.group(1)):
            ev.append("version/%s exists (an earlier Design Version's record)" % fn)
    r, _ = M.read_json(root, mod, "record.json")
    if isinstance(r, dict) and r.get("version_objection"):
        ev.append("record.json version_objection reads %r" % str(r["version_objection"]))
    return ev


def _measure(fn):
    try:
        return fn()
    except Exception:
        return UNM


def autolock_and_land(root, mod, now=None, land=None):
    """Lock a new mod's Design Version at 0.1.0 as the pipeline (his Evidence-for-Ask ruling), write the delegated
    record his daily digest reads, and land both in one landing. -> the landing's last line (PUBLISHED <sha>).
    Numbers are measured or UNMEASURED; no owner_words (they are not his)."""
    import coverage_judge as CJ
    now = now or time.time()
    d = M.mod_dir(root, mod)
    stj, _ = M.read_json(root, mod, "stage.json")
    stj = stj if isinstance(stj, dict) else {}
    tree, _ = M.read_json(root, mod, "tree.json")
    spent = (stj.get("budget") or {}).get("spent")
    p = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=60)
    day = time.strftime("%Y-%m-%d", time.localtime(now))
    why = ("the concept tree is locked and no recorded evidence says 0.1.0 is wrong: a new mod's first Design Version "
           "is 0.1.0 (his Evidence-for-Ask ruling, 2026-11-15)")
    v = {"mod": mod, "version": "0.1.0", "state": "locked", "locked_on": day, "locked_by": "pipeline",
         "per_ruling": M.EVIDENCE_FOR_ASK, "why": why,
         "bars_total": _measure(lambda: len(CJ.required_ids(d, tree)) if isinstance(tree, dict) else UNM),
         "bars_met": UNM,
         "judge_rounds": _measure(lambda: len(CJ.rounds(stj, d))),
         "tokens_spent": spent if isinstance(spent, int) else UNM,
         "locked_from_commit": p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else UNM,
         "measured_from": {"bars_total": "coverage_judge.required_ids(record.json inventory + tree.json leaves)",
                           "judge_rounds": "coverage_judge.rounds(stage.json)", "tokens_spent": "stage.json budget.spent",
                           "bars_met": "not measured at the lock: the preflight and judges measure it"},
         "caveats": ["stage.json `locked` is the concept tree's gate; this file is the Design Version lock",
                     "locked by the pipeline under his Evidence-for-Ask ruling, not on his card: "
                     "version_evidence() read no recorded evidence against 0.1.0"]}
    vrel = "design/concepts/%s/version/VERSION.json" % mod
    drel = "infrastructure/state/delegated/%s/%s-design-version-0.1.0.json" % (day, mod)
    dg = {"item": M.EVIDENCE_FOR_ASK, "subject": "%s Design Version 0.1.0" % mod, "class": "design",
          "decision": "locked 0.1.0 (the pipeline, Evidence-for-Ask ruling: no recorded evidence against it)",
          "reasons": why, "evidence": vrel, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}
    was = {}
    for rel, obj in ((vrel, v), (drel, dg)):
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        try:
            with open(os.path.join(root, rel), "rb") as f:
                was[rel] = f.read()
        except OSError:
            was[rel] = None
        with open(os.path.join(root, rel), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
            f.write("\n")
    subject = "maturation: the pipeline locks %s's Design Version at 0.1.0 (Evidence-for-Ask ruling)" % mod
    try:
        if land:
            return land(subject, [vrel, drel])
        import designer_stage as DS
        p = subprocess.run([DS.LAND, "-m", subject, vrel, drel], cwd=root, capture_output=True, text=True, timeout=300,
                           env=dict(os.environ, LAND_REPO=root))
        if p.returncode:
            raise RuntimeError("land.sh exited %d: %s" % (p.returncode, p.stderr.strip()))
        return (p.stdout.strip().splitlines() or ["PUBLISHED ?"])[-1]
    except Exception:
        # an unlanded lock is no lock: put both files back, so the next tick reads the version unlocked and the
        # autolock's own retry count decides (a kept local lock routed on to preflight unpublished;
        # RIMMANDRAKE_RESTORE_VERSION_FILE_WHEN_AUTOLOCK_LANDING_FAILS)
        for rel, b in was.items():
            p_ = os.path.join(root, rel)
            try:
                if b is None:
                    os.remove(p_)
                else:
                    with open(p_, "wb") as f:
                        f.write(b)
            except OSError:
                pass
        raise


REPIN_WAIT = "the re-pin ("     # how coverage_judge.grant_waits names the locked_change a LOCKED concept's grant waits on


def repin_owed(root, mod, dst, items=None):
    """RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE -> True when the standing grant waits on nothing but the re-pin: every
    --after item is closed, the concept is LOCKED, and no locked_change follows the stop the grant lifts (read by
    coverage_judge.grant_waits itself). Before this, no stage, ticket or brief owed that re-pin, and the grant never
    came due unless a hand-filed item carried "then one re-pin"."""
    import coverage_judge as CJ
    items = ledger_items() if items is None else items
    w = CJ.grant_waits(dst or {}, lambda ids: {i: getattr(items.get(i), "state", None) for i in ids},
                       d=M.mod_dir(root, mod))
    return bool(w) and all(str(x).startswith(REPIN_WAIT) for x in w)


def repin_and_land(root, mod, sources, now=None, land=None, repin=None):
    """The pipeline's re-pin of a LOCKED concept whose grant waits on it: designer_stage.repin with the sources
    designer_stage.repin_sources found (his cards only, every check a hand re-pin passes), then stage.json landed in one
    landing. -> the landing's last line. An unlanded re-pin is no re-pin: stage.json is put back byte for byte, and the
    act's own retry count decides."""
    import designer_stage as DS
    d = M.mod_dir(root, mod)
    rel = "design/concepts/%s/stage.json" % mod
    with open(os.path.join(root, rel), "rb") as f:
        was = f.read()
    why = ("the grant's --after items are closed and it waits on the re-pin: the Maturation tick re-pins citing the "
           "cards of his each fix carries out (RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE)")
    subject = "maturation: the pipeline re-pins locked %s for its granted look (%s)" % (mod, ", ".join(sources))
    try:
        (repin or DS.repin)(d, list(sources), why, repo=root)
        if land:
            return land(subject, [rel])
        p = subprocess.run([DS.LAND, "-m", subject, rel], cwd=root, capture_output=True, text=True, timeout=300,
                           env=dict(os.environ, LAND_REPO=root))
        if p.returncode:
            raise RuntimeError("land.sh exited %d: %s" % (p.returncode, p.stderr.strip()))
        return (p.stdout.strip().splitlines() or ["PUBLISHED ?"])[-1]
    except Exception:
        with open(os.path.join(root, rel), "wb") as f:
            f.write(was)
        raise


# ---- one class per mod -----------------------------------------------------------------------------------------------

def _steward(row, kind, key, why, brief_need):
    row.update(aut="steward", steward_kind=kind, steward_key=key, decision="steward", why=why, need=None)
    row["steward_need"], row["steward_why"] = brief_need, why


def resolve(root, cfg, st, facts, rows, launches, now, fx=None):
    """-> (rows, launches): every row gets `klass` and a plain `status`; hand-step decisions become steward or fixer
    launches (within max_live and the caps), paused or owner. Mutates st (steward/fixer keys, queue, class clocks)."""
    fx = fx or {}
    mods = st.setdefault("mods", {})
    import maturation_dispatch as MD
    base = MD.occupancy(facts)      # the live runs; this tick's planned launches are counted at each gate, so a
    # launch taken back (a road-back fixer replacing a mod's own build) gives its slot back
    # (RIMMANDRAKE_RETURN_SLOT_OF_REPLACED_LAUNCH_FIXER_NEVER_RAN: at max_live 1 the fixer read slots_full for good)
    open_items = fx.get("open_items", lambda ids: M.ledger_items_caused_by(root, ids))
    dstate = fx.get("designer_state", lambda m: designer_state(root, m))
    locked = fx.get("version_locked", lambda m: version_locked(root, m))
    evidence = fx.get("version_evidence", lambda m: version_evidence(root, m))
    queue = st.setdefault("ingame_queue", {})
    for row in rows:
        mod, f = row["mod"], facts.get(row["mod"]) or {}
        s = mods.setdefault(mod, {})
        dec = row.get("decision")
        ver = f.get("version") or (M.load(root, mod) or {}).get("version")
        # the in-game queue: a visit owed waits its turn by first-seen time
        if row.get("stage") == "in_game" and f.get("owed") == "run" and dec not in LAUNCH:
            queue.setdefault(mod, now)
        elif dec in LAUNCH or f.get("owed") != "run":
            queue.pop(mod, None)
        _mark_worked(s, ver, row.get("stage"), f.get("live_units"), now, f.get("ended_runs"))
        dst = None if dec in ("live", "settling") else dstate(mod)
        fs, cs = final_stop(dst), coverage_stopped(dst)
        if fs:
            rel, stop = fs
            row.update(decision="owner", aut=None,
                       why="judging stopped %s after the final look he granted (%s): %s" % (
                           stop.get("at"), rel.get("granted_at") or rel.get("at"),
                           str(stop.get("why") or "no reason written")),
                       card="%s: the final look (granted %s, after %s) ran at %s and judging stopped %s: %s. Judging "
                            "stays stopped; the next step is his. Evidence: design/concepts/%s/coverage_verdict.json "
                            "and stage.json." % (mod, rel.get("granted_at") or "-", ", ".join(rel.get("after") or [])
                                                 or "nothing", rel.get("at"), stop.get("at"),
                                                 str(stop.get("why") or "no reason written"), mod))
            row["need"] = "%s: OWNER, judging stopped after the final look; the next step is his" % mod
            launches = [m for m in launches if m != mod]
        elif cs:
            row.update(decision="coverage_stop", aut=None, why="judging stopped %s: %s; `coverage_judge.py release "
                       "design/concepts/%s --why ...` (one more look, on his word) un-pauses it" % (
                           cs.get("at"), str(cs.get("why") or "no reason written"), mod))
            # its Needs Conductor line says the pause, not decide's stage reading (Pyrelands read "ready to advance")
            row["need"] = ("%s: PAUSED, coverage judging stopped %s; nothing moves on it until `coverage_judge.py "
                           "release design/concepts/%s --why ...` (one more look, on his word)" % (mod, cs.get("at"), mod))
            launches = [m for m in launches if m != mod]
            _stop_tickets(fx, row, s, dst, now, root=root, ver=ver)
        elif dec in LAUNCH and s.get("road_back") and row.get("stage") in ROAD_BACK_STAGES and \
                _road_back(s, row, open_items, now, moved=True):
            # RIMMANDRAKE_RUN_ROAD_BACK_FIXERS_SAME_STAGE_SKIPPED_THEM: the road back's items get their fixers before
            # the next cycle or visit launches (a blind_challenge -> blind_challenge road back launched at once)
            launches = [m for m in launches if m != mod]
        elif dec in WAIT or dec in LAUNCH or dec in HOLDS:
            pass
        elif (st.get("seed_refused") or {}).get(mod):
            row.update(decision="seed_refused", why="its stage record could not be seeded: %s" % st["seed_refused"][mod])
        else:
            _route(root, cfg, s, f, row, ver, dstate, locked, open_items, fx.get("designer_unit", designer_unit),
                   fx.get("designer_chain", lambda m: designer_chain(m, now)), now=now, fx_evidence=evidence,
                   fx_exam=fx.get("exam_gate", lambda m: exam_gate(root, m)))
            if row.get("decision") == "designer_blocked":
                # a Designer blocked on a filed fix item (a pipeline defect) gets that item's one fixer run; the mod
                # stays paused meanwhile (RIMMANDRAKE_BUDGET_DESIGNER_EXAM_HELPERS_FIVE_READERS_ZERO_SLOTS)
                _stop_tickets(fx, row, s, dst, now, kind="blocked")
        if row.get("aut") in ("autolock", "autorepin"):
            # the pipeline's lock (or re-pin) is an act, not a run: no slot; tried once (transient faults up to
            # launch_tries)
            x = (s.get("steward") or {}).get(row["steward_key"])
            if x and not (x.get("failed") and transient(x.get("failed")) and int(x.get("tries") or 1) <
                          int(cfg.get("launch_tries", 3))):
                row.update(decision="launch_failed", aut=None,
                           why=("the pipeline's 0.1.0 lock of %s was tried (%s) and VERSION.json still reads unlocked; "
                                if row["aut"] == "autolock" else
                                "the pipeline's re-pin of %s was tried (%s) and the grant still waits on the re-pin; ")
                           % (mod, str(x.get("failed") or x.get("landed") or "ended")) +
                           "`maturation_dispatch.py clear %s --why ...` un-pauses it" % mod)
                if row.get("repin_sources") is not None:
                    row["need"] = "%s: PAUSED, the grant waits on the re-pin; the pipeline's re-pin was tried (%s): %s" % (
                        mod, str(x.get("failed") or x.get("landed") or "ended"), _repin_cmd(mod, row["repin_sources"]))
            else:
                row["retry_of"] = dict(x or {})
                launches = [m for m in launches if m != mod] + [mod]
            continue
        # one automatic run per state, then a steward or fixer within the caps
        if row.get("aut"):
            launches = [m for m in launches if m != mod]
            ok, why = _gate(cfg, s, row, None if base is None else base + len(launches), ver)
            if ok:
                launches = launches + [mod]
            else:
                if why[0] == "slots_full":
                    row["waits_on"] = "a free slot for the %s run on %s" % (
                        row["aut"], row.get("fix_item") or row.get("steward_kind"))
                row.update(decision=why[0], aut=None, why=why[1] + (
                    "; it was for: %s" % str(row["steward_why"]) if row.get("steward_why") else ""))
    return rows, launches


def _repin_cmd(mod, sources):
    return "python3 src/RimMandrake/rimflow/designer_stage.py repin design/concepts/%s %s --why \"...\"" % (
        mod, " ".join("--source %s" % sv for sv in sources) or "--source OWNER:<tsn>@<commit> ...")


def _repin_route(fx, root, row, dst, ver):
    """RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE: the grant waits on the re-pin alone. designer_stage.repin_sources
    finds the cards of his each fix carries out (the checks of a hand re-pin, its dry run the last word): found, the
    pipeline re-pins as an act (autorepin, like the autolock: no brief, no run, one landing); refused, the mod stays
    PAUSED and its line names the wait, the hand command and the refusal record. Never a CONDUCTOR source."""
    import designer_stage as DS
    mod, g = row["mod"], (dst or {}).get("coverage_release_granted") or {}
    try:
        sources, refusal = (fx["repin_plan"](mod) if "repin_plan" in fx
                            else DS.repin_sources(M.mod_dir(root, mod), repo=root))
    except Exception as e:      # noqa: BLE001  an unreadable history is a refusal, never the tick's crash
        sources, refusal = [], {"clause": DS.REPIN_CLAUSE, "evidence": ["%s: %s" % (type(e).__name__, e)],
                                "observed": "the commits since the pin could not be read",
                                "would_pass": DS.REPIN_WOULD_PASS,
                                "smallest_fix": {"what": "repair what the error names; the next tick tries again",
                                                 "attainable": "yes", "cost": "rerun"}}
    lead = "judging stopped; the grant (%s) has its --after items closed and waits on the re-pin" % g.get("at")
    if refusal is None:
        row.update(aut="autorepin", decision="autorepin", steward_key="%s|repin|%s" % (ver, g.get("at")), need=None,
                   repin_sources=list(sources),
                   why="%s: the pipeline re-pins, citing his cards %s (designer_stage.repin's own checks passed dry)" % (
                       lead, ", ".join(sources)))
        row["steward_why"] = "the re-pin the grant waits on, citing %s" % ", ".join(sources)
        return
    fix = refusal.get("smallest_fix") or {}
    said = "refused (%s): %s; evidence: %s; would pass: %s; smallest fix: %s" % (
        refusal.get("clause"), refusal.get("observed"), "; ".join(str(e) for e in refusal.get("evidence") or []),
        refusal.get("would_pass"), fix.get("what") if isinstance(fix, dict) else fix)
    row["refusal"] = refusal
    row["why"] = "%s; %s, and the pipeline's re-pin %s" % (str(row.get("why") or ""), lead, said)
    row["need"] = "%s: PAUSED, the grant waits on the re-pin: %s; the pipeline's re-pin %s" % (
        mod, _repin_cmd(mod, sources), said)


def _stop_tickets(fx, row, s, dst, now, kind="stop", root=None, ver=None):
    """RIMMANDRAKE_RUN_FIX_TICKETS_WHILE_PAUSED: a coverage-stopped mod stays paused, but its own open fix tickets get
    one fixer run each (the road-back fixer, extended): a live run on a ticket is waited on and booked as its run, an
    earlier run on it counts as spent, and the status names the ticket. No ticket or an unreadable ledger: as before.
    RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE: once no ticket run is live and the grant waits on the re-pin alone, the
    re-pin is owed before any other ticket (_repin_route)."""
    lead = "judging stopped" if kind == "stop" else "the Designer is blocked"
    try:
        if kind == "blocked":
            tk = (fx["blocked_tickets"](row["mod"], dst) if "blocked_tickets" in fx
                  else blocked_tickets(dst, ledger_items()))
        else:
            tk = fx["stop_tickets"](row["mod"], dst, s) if "stop_tickets" in fx else stop_tickets(dst, s, ledger_items())
    except Exception:       # noqa: BLE001  an unreadable ledger leaves the plain pause
        tk = None
    runs_of = fx.get("ticket_runs", ticket_runs)
    fixed = s.setdefault("fixers", {}) if tk else {}
    for t in tk or []:
        for unit, status in runs_of(t["id"]):
            if status == "launch_failed":
                continue
            fixed.setdefault(t["id"], {"item": t["id"], "unit": unit, "hand": True, "at": now})
            if status in ("launching", "running"):
                row.update(decision="live", waits_on="%s (fix ticket %s)" % (unit, t["id"]), need=None,
                           why="%s and stays paused; its fix ticket %s has a live run %s" % (lead, t["id"], unit))
                return
    if kind == "stop" and root is not None and tk is not None:
        try:
            owed = repin_owed(root, row["mod"], dst, fx["ledger_items"]() if "ledger_items" in fx else None)
        except Exception:   # noqa: BLE001  an unreadable grant or ledger leaves the plain pause
            owed = False
        if owed:
            _repin_route(fx, root, row, dst, ver)
            return
    if not tk:
        return
    todo =[t["id"] for t in tk if t["id"] not in fixed]
    ids = ", ".join(t["id"] for t in tk)
    if todo:
        row.update(aut="fixer", fix_item=todo[0], decision="fixer", need=None, fix_for=kind,
                   why="%s; its fix ticket %s (of %d open: %s) gets one fixer run while the mod stays "
                       "paused" % (lead, todo[0], len(tk), ids))
    else:
        row["why"] = str(row.get("why") or "") + "; every open fix ticket (%s) has had its one fixer run and is still open" % ids
        row["need"] = (row.get("need") or "%s: PAUSED, %s" % (row["mod"], lead)) + \
            "; its open fix tickets (%s) have each had their one fixer run" % ids


def classify(cfg, st, rows, now):
    """After the acts: one class per row (launched, failed and waiting rows read as they ended this tick)."""
    queue = st.get("ingame_queue") or {}
    for row in rows:
        _klass(cfg, st.setdefault("mods", {}).setdefault(row["mod"], {}), row, now, queue)
    return rows


def _road_back_ids(s, rb):
    """-> the steward items whose filings make up this road back: the run that opened it and every steward run on the
    same state (version, stage, decision, cycle or visit: the first four fields of its key). A second steward on the
    same cycle replaces s["road_back"], so its sibling's open items are found here, never dropped."""
    book = s.get("steward") or {}
    opener = next((k for k, v in book.items() if isinstance(v, dict) and v.get("item") == rb.get("caused_by")), None)
    ids = [rb.get("caused_by")]
    if opener:
        pre = opener.split("|")[:4]
        ids += [v.get("item") for k, v in sorted(book.items()) if isinstance(v, dict) and v.get("item")
                and k.split("|")[:4] == pre and v.get("item") not in ids]
    return ids


def _road_back(s, row, open_items, now=None, moved=False):
    """-> True when the mod's open road back decides the row: a fixer on its next open item, fixers spent, or an
    unreadable ledger. Keyed on the road back being open, never on a stage change: blind_challenge -> blind_challenge
    is the road back ROADS_BACK draws for a blind cycle, so the stage never changes.
    With no open item it returns False, and the road back closes (is popped) when a tick saw it hold items (its fixers
    closed them) or when the mod has moved (moved: a next cycle or visit is owed, so the steward's landing is in this
    clone). Then the steward runs it covers are marked road_back_closed, so the state they read is a new state
    (_after_road_backs). An empty road back on an unmoved mod stays open: the clone's ledger may not hold the steward's
    filings yet; a steward that filed nothing stays spent."""
    rb = s.get("road_back")
    if not rb:
        return False
    ids = _road_back_ids(s, rb)
    items = open_items(ids)
    if items is None:
        row.update(decision="blind", why="the ledger cannot be read for the road-back items")
        return True
    if items:
        rb["had_items"] = True      # a tick saw it hold items: its closing is a new state
        # offline stages never wait for a game: at one, an item only the game can show gets no run; it is Stage 6 work
        # (RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED)
        game = ([x for x in items if (x or {}).get("needs") in M.LIVE_NEEDS]
                if row.get("stage") in M.OFFLINE_STAGES else [])
        work = [x for x in items if x not in game]
        if not work:
            ids6 = [x["id"] for x in game]
            row.update(decision="game_only", aut=None, why="every open road-back item (%s) is a fault only the game can "
                       "show, and %s is an offline stage: none gets a run here" % (", ".join(ids6), row.get("stage")),
                       need="%s: PAUSED, its open road-back items need the live game (%s); Stage 6 work, not %s's: %s"
                       % (row.get("mod"), ", ".join(ids6), row.get("stage"), M.game_only_cmd(row.get("mod"), ids6)))
            return True
        items = work
        fixed = s.setdefault("fixers", {})
        todo = [x for x in items if x["id"] not in fixed]
        if todo:
            row.update(aut="fixer", fix_item=todo[0]["id"], decision="fixer",
                       why="road-back item %s (of %d open, caused by %s) gets one fixer run" % (
                           todo[0]["id"], len(items), " or ".join(ids)))
        else:
            row.update(decision="fixer_spent", why="every open road-back item (%s) has had its one fixer run and "
                       "is still open" % ", ".join(x["id"] for x in items))
        return True
    if not (rb.get("had_items") or moved):
        return False
    s.pop("road_back", None)        # every road-back item closed: the mod moves on (visit N+1 when it arrives)
    for v in (s.get("steward") or {}).values() if rb.get("had_items") else ():
        if isinstance(v, dict) and v.get("item") in ids:
            v.setdefault("road_back_closed", now)
    row["road_back_closed"] = rb["caused_by"]
    return False


def _after_road_backs(s, key):
    """-> (key, [items]): a steward key whose run opened a road back now closed names a new state (its fixers ran and
    closed what it filed), so the key grows `|after:<item>` once per closed road back; one whose state another run
    worked after it ended (_mark_worked) grows `|worked:<t>`. Unmarked keys are unchanged."""
    book, after = s.get("steward") or {}, []
    while isinstance(book.get(key), dict) and (book[key].get("road_back_closed") or book[key].get("worked_after")):
        if book[key].get("road_back_closed"):
            after.append(book[key].get("item"))
            key = "%s|after:%s" % (key, book[key].get("item"))
        else:
            key = "%s|worked:%d" % (key, int(book[key]["worked_after"]))
    return key, after


def _mark_worked(s, ver, stage, live, now, ended=None):
    """A steward run that ended on an unmoved state is spent for that state, but a run of another unit (a builder, a
    fixer) live on the mod at the same stage after it ended is new work: the next reading of that state is a new state.
    Pyrelands 2026-11-16: its 'ready' steward refused a false pass, builders closed the owed tickets, and the same
    'every exit test passes' key read steward_spent for good (RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING).
    A run that began and ended between two ticks of this reading is never seen live, so an ended run of another unit
    whose end is later than the steward's own end counts too (`ended`, the mod's ended runs with their `end`): Gimme
    Some Slack 2026-11-17, a Fable run worked stage 6 for hours after the visit steward ended and the key still read
    steward_spent (RIMMANDRAKE_SEE_RESCUE_RUN_ON_ITS_MOD)."""
    live = [u for u in live or [] if u]
    ends = {r.get("unit"): r.get("end") for r in ended or []
            if isinstance(r, dict) and r.get("unit") and isinstance(r.get("end"), (int, float))}
    if not live and not ends:
        return
    for k, v in (s.get("steward") or {}).items():
        if not (isinstance(v, dict) and v.get("unit") and not v.get("worked_after") and v["unit"] not in live
                and str(k).startswith("%s|%s|" % (ver, stage))):
            continue
        if live:
            v["worked_after"] = now
            continue
        mine = ends.get(v["unit"])          # the steward's own end; unread means it is not known to have ended
        later = [e for u, e in ends.items() if u != v["unit"] and mine is not None and e > mine]
        if later:
            v["worked_after"] = max(later)


def _route(root, cfg, s, f, row, ver, dstate, locked, open_items, fx_dunit=designer_unit, fx_dchain=None, now=None,
           fx_evidence=None, fx_exam=None):
    mod, dec, stage = row["mod"], row.get("decision"), row.get("stage")
    dst = dstate(mod)
    lc = chain_owed(dst)
    if lc:
        _steward(row, "chain", "%s|chain|%s" % (ver, lc.get("at")),
                 "a locked change landed %s and no coverage look has followed it: re-pin, Cold Reader exam retake, "
                 "ONE coverage-judge look" % lc.get("at"),
                 "the locked change of %s (%s): check its re-pin (designer_stage.py repin, already done when the history "
                 "says re-pinned), retake the Cold Reader exam on the new tree by "
                 "src/RimMandrake/rimflow/roles/designer_exam.md in full (the Challenger's scenarios and the control "
                 "copy included: an exam failing its gate makes the judge skip), then give it ONE coverage-judge look "
                 "(coverage_judge.py release <dir> --why ...; when stage.json holds coverage_release_granted, that plain "
                 "release applies the grant as the final look and refuses until its `after` items close: add no "
                 "release of your own, and close an `after` item whose notes say its work landed, with its published "
                 "sha, after checking that sha is on origin/main). The release lifts the block, so publish it with "
                 "your stage-4 `designer_stage.py open <dir> --run <id>`; after the stage-4 close, claim stage 5 the "
                 "same way and publish the claim BEFORE `coverage_judge.py run <dir>`, so the launcher's stage-5 run "
                 "(whose pre-step is the judge) cannot open beside it; after the look, close the claim with "
                 "`RM_ROLE_UNIT=<id> python3 src/RimMandrake/rimflow/role_launch.py stage5-program <dir>`, or, when "
                 "judging stopped, `designer_stage.py close <dir> --run <id> --tokens 0` with no result.json (the "
                 "block stays for him; stage5-program would return the gaps to stage 3) "
                 "(RIMMANDRAKE_GUARD_ONE_COVERAGE_LOOK_STEWARD_LAUNCHER_BOTH_RAN). Before the look, write "
                 "coverage_fixes.json against the last verdict's judge: one claim per gap whose fix landed, its "
                 "evidence the fix's sha and acceptance test; a gap with no claim is carried open whatever the judge "
                 "finds (RIMMANDRAKE_CLAIM_FIXED_GAPS_BEFORE_FINAL_LOOK_JUDGE_AGREED). Never a second look." % (
                     lc.get("at"), str(lc.get("why"))))
        return
    # an open road back: its filed items are fixed before the mod moves on, whether or not the steward moved its stage
    if stage in ROAD_BACK_STAGES and _road_back(s, row, open_items, now):
        return
    if row.get("road_back_closed") and dec == "stopped":
        s.pop("stopped", None)
    if stage == "passed":
        row.update(decision="rested", why=RESTED)
        return
    if stage in OWNER_STAGES:
        row.update(decision="owner", why=OWNER_STAGES[stage],
                   card="%s %s stands at %s. %s. Evidence: design/concepts/%s/journal.md and %s." % (
                       mod, ver, M.label(stage), OWNER_STAGES[stage], mod, M.RECORD))
        return
    if stage in (UNM, "designer", "intake") or stage is None:
        _designer_lane(row, mod, ver, dst, locked, fx_dunit, fx_dchain, evidence=fx_evidence, exam=fx_exam,
                       root=root)
        return
    if stage in STEWARD_STAGES and dec == "not_offline":
        if stage == "pre_human":
            # Stage 7 judges nothing (owner, 2026-11-17, RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO): one
            # fresh reader, who made none of the evidence writes, writes his walk brief; it has no veto
            _steward(row, "stage", "%s|%s" % (ver, stage), "%s: one fresh reader writes it, then advance" % (
                         M.label(stage)),
                     "a fresh reader that made none of %s's evidence writes writes design/concepts/%s/%s/arrival_<N>.md "
                     "(N = the record's pre_human_arrivals) per "
                     "src/RimMandrake/rimflow/roles/walk_brief.md (no veto: findings go into the brief or onto a "
                     "ticket), then maturation.py advance %s --to his_walk" % (mod, mod, M.WALK_BRIEF_DIR, mod))
            return
        _steward(row, "stage", "%s|%s" % (ver, stage), "%s is the steward's step: run it, then advance" % M.label(stage),
                 "do %s as the spec says (design/specs/2026-11-13-maturation-pipeline.md) and advance with "
                 "--steward-confirms naming what you read" % M.label(stage))
        return
    stop = s.get("stopped") or {}
    if (dec == "stopped" and stage == "offline_build" and str(stop.get("why")).startswith("run ")
            and not stop.get("ceiling") and not stop.get("launch_failed")):
        # a builder ended and resolved none of its refused bars: the cause is unknown until someone reads the run, so
        # one steward reads it and files what it finds (RIMMANDRAKE_TRIAGE_STALLED_BUILDER_GRAFFITI_WAITED_ON_HELPERS).
        # Never a second builder at the same refusals: the stop lifts only when a refused bar is resolved.
        unit = (s.get("last_run") or {}).get("unit")
        item = next((x.get("item") for x in s.get("launches") or [] if x.get("unit") == unit), None)
        key, after = _after_road_backs(s, "%s|offline_build|builder_stalled|%s" % (ver, _h([unit, stop.get("ids")])))
        _steward(row, "builder_stalled", key, stop.get("why"),
                 "builder run %s (item %s; its result file is <dispatcher state>/detached/%s.out.json, its end line is "
                 "in the Conductor log) ended and %s refused bars stand: %s" % (
                     unit, item or "not launched by the tick: find it with `detached_helper.py status --all`", unit,
                     len(stop.get("ids") or []), ", ".join((stop.get("ids") or [])[:40])))
        if after:
            row["road_back_after"] = after
        return
    # a blind cycle's record with no exit block and nothing live: the night of 2026-11-14 each one got a reconcile run
    # by hand. One steward completes the record from its files or says what judging is missing. An unfinished in-game
    # visit stays a hand: the game it left needs a look, and a steward never takes the bridge.
    if dec in STEWARD_ON or (dec == "cycle_unfinished" and stage == "blind_challenge"):
        n = row.get("visit") if stage == "in_game" else row.get("cycle") if stage == "blind_challenge" else None
        if dec == "exit_not_met" and stage == "blind_challenge" and (f.get("visit") or 0) >= M.CYCLE_LIMIT:
            row.update(decision="cycle_limit", why="three blind cycles in this visit ended not met; his rule of "
                       "2026-11-13 brings the Conductor in (maturation.py advance %s --to blind_challenge "
                       "--conductor-decision \"...\" un-pauses it)" % mod)
            return
        key, after = _after_road_backs(s, "%s|%s|%s|%s|%s" % (ver, stage, dec, n, _h(row.get("refused_ids") or
                                                                                      row.get("why"))))
        _steward(row, dec, key, row.get("why"), row.get("need") or row.get("why"))
        if after:
            row["road_back_after"] = after


def _designer_lane(row, mod, ver, dst, locked, dunit=designer_unit, dchain=None, evidence=None, exam=None,
                   root=None):
    if dst is None:
        row.update(decision="designer_unreadable", why="design/concepts/%s/stage.json cannot be read" % mod)
        return
    stt, stg = dst.get("status"), dst.get("stage")
    if dst.get("running") or dst.get("open_run"):
        run = dst.get("running") or dst.get("open_run")
        row.update(decision="designer_wait", waits_on=str(run.get("run") if isinstance(run, dict) else run),
                   why="the Designer's run %s is open (stage %s)" % (run.get("run") if isinstance(run, dict) else run, stg))
    elif stt == "waiting_owner":
        last = (dst.get("history") or [{}])[-1]
        row.update(decision="owner", why="a Designer turn waits on him (stage %s)" % stg,
                   card="%s, Designer stage %s, waits on you: %s Pending: %s Its asks: %s. Evidence: "
                        "design/concepts/%s/record.json (asks), park_summary.md and stage.json." % (
                            mod, stg, str(last.get("why") or ""), str(dst.get("pending_decision") or "none"),
                            "; ".join(str(x) for x in (dst.get("_asks") or [])[:6]) or "none written", mod))
    elif stt == "blocked" and "OWNER HOLD" in str(dst.get("blocked_on") or "") and root and upstream_wait(root, mod):
        # the hold's own condition is met; what it waits for is another mod's version (the hold stays, nothing launches)
        up, uv, at = upstream_wait(root, mod)
        row.update(decision="upstream_wait", waits_on="%s %s to pass" % (up, uv),
                   why="its Design Version waits for %s %s to pass (%s; design/concepts/%s/version/VERSION.json); the "
                       "hold on the Designer (stage %s) stays until then" % (up, uv, at, mod, stg))
    elif stt == "blocked" and "OWNER HOLD" in str(dst.get("blocked_on") or ""):
        row.update(decision="owner", why="an owner hold stands on the Designer (stage %s)" % stg,
                   card="%s, Designer stage %s, is held for you: %s Evidence: design/concepts/%s/stage.json." % (
                       mod, stg, str(dst.get("blocked_on")), mod))
    elif stt == "blocked":
        row.update(decision="designer_blocked", why="%s (designer_stage.py unblock or the named release un-pauses "
                   "it)" % str(dst.get("blocked_on") or "no reason written"))
    elif (stt == "locked" or stg == 5) and locked(mod):
        # RIMMANDRAKE_GATE_DESIGNER_LOCKED_ON_VERSION_FILE_NOT_TREE: the Design Version lock is VERSION.json (his word),
        # never stage.json's `locked` (the concept tree passed its gate)
        _steward(row, "designer_locked", "%s|designer|locked" % ver, "the Design Version is locked: advance it to "
                 "preflight", "the version is locked; record its bars (`maturation.py lock-bars %s --by BENCH --why ...`, land "
                 "version/locked_bars.json). If version/stage_record.json names another version than VERSION.json (a "
                 "record seeded before the lock reads UNMEASURED), open it with `maturation.py next-version %s --by "
                 "BENCH --why ...` (it starts at preflight); otherwise advance %s --to preflight (the lock clause "
                 "passes)" % (mod, mod, mod))
    elif stt == "locked":
        # his Evidence-for-Ask ruling (2026-11-15): a new mod's first Design Version is 0.1.0; the pipeline locks it
        # unless recorded evidence says otherwise, and only then asks him, quoting that evidence
        ev = (evidence or (lambda m: []))(mod)
        if not ev:
            row.update(aut="autolock", decision="autolock", steward_key="%s|designer|autolock" % ver, need=None,
                       why="the concept tree is locked and no Design Version is: the pipeline locks 0.1.0 (his "
                           "Evidence-for-Ask ruling, %s); no recorded evidence says 0.1.0 is wrong" % M.EVIDENCE_FOR_ASK)
        else:
            q = "; ".join(ev)
            row.update(decision="owner", why="the concept tree is locked, and recorded evidence says 0.1.0 may not be "
                       "its Design Version: %s" % q,
                       card="Which Design Version is %s? The Designer finished Lock (stage.json reads locked, stage %s). "
                            "A new mod is locked at 0.1.0 by the pipeline, but recorded evidence says 0.1.0 may be "
                            "wrong here: %s. On his answer: write version/VERSION.json (state locked, locked_by owner, "
                            "owner_words), then `maturation.py next-version %s`. Evidence: design/concepts/%s/version/ "
                            "and record.json." % (mod, stg, q, mod, mod))
    else:
        unit = dunit(mod)
        cc = None if unit or dchain is None else dchain(mod)
        if cc and cc[0] >= cc[1]:
            row.update(decision="designer_chain_cap", why="the Designer stands at stage %s (%s) and the Dispatcher "
                       "chained %d runs on it today, the most is %d (chain_max_per_day): no run-now is asked until "
                       "tomorrow; look at its stage history, then `role_launch.py run-now --role Designer --concept "
                       "design/concepts/%s --by Conductor --why \"...\" --apply` un-pauses it" % (stg, stt, cc[0], cc[1], mod))
            return
        errs, th = exam(mod) if exam and stg == 5 and not unit else ([], None)
        if errs:
            # RIMMANDRAKE_RETAKE_FAILING_EXAM_NOT_SILENT: coverage_judge skips a stage-5 concept whose exam fails its
            # gate, so nothing ever moved it; the retake is owed work, once per tree
            _steward(row, "exam_retake", "%s|exam_retake|%s" % (ver, str(th)[:12]),
                     "exam fails its gate: %s" % "; ".join(errs), "; ".join(errs))
            return
        row.update(decision="designer_wait", waits_on=unit,
                   why="the Designer stands at stage %s (%s): %s" % (stg, stt, "its run %s is live" % unit if unit else
                       "the Dispatcher's Designer launcher runs it (no Designer run live now)"))


def _gate(cfg, s, row, live_total, ver):
    """-> (go, (decision, why)) for a steward or fixer launch: once per key, the version's count, the cap, the slots."""
    if row.get("aut") == "fixer":
        key, done = row["fix_item"], s.setdefault("fixers", {})
    else:
        key, done = row["steward_key"], s.setdefault("steward", {})
    if key in done:
        x = done[key]
        tries, most_tries = int(x.get("tries") or 1), int(cfg.get("launch_tries", 3))
        # a launch that failed on a defect is tried again once the pipeline's code changed since (the fix may have
        # landed); before this the Conductor cleared it by hand (maturation_dispatch.code_changed)
        fresh_code = bool(x.get("code") and cfg.get("_code") and x["code"] != cfg["_code"])
        if not (x.get("failed") and not x.get("unit") and (transient(x["failed"]) or fresh_code)
                and tries < most_tries):
            what = ("failed to launch %d times on a transient fault, the last: %s" % (tries, x["failed"])
                    if x.get("failed") and transient(x["failed"]) else "failed to launch: %s" % x["failed"]
                    if x.get("failed") else "ended and the state has not moved")
            return False, ("steward_spent" if row["aut"] == "steward" else "fixer_spent",
                           "the automatic %s run on this state (%s) %s; un-pause: `maturation_dispatch.py clear %s "
                           "--why ...` after reading it" % (row["aut"], x.get("unit") or x.get("item"), what,
                                                             row["mod"]))
        row["retry_of"] = dict(x, tries=tries)
    if not cfg.get("steward_enabled", True):
        return False, ("steward_off", "steward_enabled is off in maturation_dispatch.json")
    n = len([k for k in done if k != key and (row["aut"] != "steward" or str(k).startswith(str(ver)))])
    most = int(cfg.get("steward_max_per_version", 12))
    if n >= most:
        return False, ("steward_spent", "%d automatic %s runs on %s at this version, the most is %d" % (
            n, row["aut"], row["mod"], most))
    cap = cfg.get("fix_cap_usd" if row["aut"] == "fixer" else "steward_cap_usd")
    if not (isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0):
        return False, ("no_cap", "no positive %s in the settings" % ("fix_cap_usd" if row["aut"] == "fixer"
                                                                    else "steward_cap_usd"))
    if live_total is None:
        return False, ("slots_unknown", "the live runs of an advancing mod cannot be read; the %s run waits on a "
                       "readable occupancy" % row["aut"])
    if live_total >= int(cfg.get("max_live", 2)):
        return False, ("slots_full", "%d live runs on advancing mods, the most is %s; the %s run (%s) waits for a slot" % (
            live_total, cfg.get("max_live", 2), row["aut"], row.get("steward_kind") or row.get("fix_item")))
    row["cap"] = cap
    return True, None


PAUSE_WHY = {
    "stopped": "the last automatic run did not move it", "blind": "an input cannot be read",
    "blocked": "a non-build refusal", "held": "a Conductor hold (a release line in the journal un-pauses it)",
    "no_cap": "no spend cap", "blind_off": "blind launches are off", "ingame_off": "in-game launches are off",
    "launch_failed": "a launch failed", "launch_retry": "a launch is retried", "auto_spent": "the automatic runs of this visit are spent",
    "hand_run_seen": "a hand-launched run worked here and wrote no record", "steward_spent": "the steward run is spent",
    "fixer_spent": "the fixer runs are spent",
    "game_only": "its open road-back items need the live game: Stage 6 work, the record goes back there",
    "cycle_unfinished": "a cycle record has no exit block",
    "visit_unfinished": "a visit record has no exit block", "cycle_limit": "three blind cycles: the Conductor decides",
    "seed_refused": "its record cannot be seeded", "designer_blocked": "the Designer is blocked",
    "designer_unreadable": "its stage.json cannot be read", "disabled": "the step is disabled",
    "steward_off": "steward runs are off", "designer_chain_cap": "the Designer's daily chain cap is reached",
    "coverage_stop": "coverage judging stopped on it (REFUSAL_NOTHING_COULD_EVER_PASS)",
    "ceiling": "the stage's spend plus the next run's cap passes stage_ceiling_usd", "not_offline": "no automatic step exists for its stage",
}


def _klass(cfg, s, row, now, queue):
    dec = row.get("decision")
    if dec in LAUNCH or (row.get("aut") and dec in ("steward", "fixer", "autolock", "autorepin")):
        k, txt = "launch", "moving: %s %s" % (row.get("aut") or "run", row.get("unit") or row.get("item") or "")
        if row.get("fix_item") and row["fix_item"] not in txt:
            txt = "%s on %s" % (txt.rstrip(), row["fix_item"])
        if row.get("steward_why"):
            txt = "%s for: %s" % (txt.rstrip(), str(row["steward_why"]))
    elif dec in WAIT:
        on = row.get("waits_on")
        if on is None and dec != "designer_wait":
            live = row.get("live") if isinstance(row.get("live"), list) else []
            on = ", ".join(live) or None
        if dec == "driver_busy" and row["mod"] in queue:
            pos = sorted(queue, key=lambda m: queue[m]).index(row["mod"]) + 1
            row["queue"] = pos
            on = "%s (game queue position %d of %d)" % (re.sub(r".*\((rm-[^)]*)\).*", r"\1", row.get("why") or ""),
                                                         pos, len(queue))
        if dec in ("bridge_held", "slots_full", "account_hold", "settling") and not on:
            on = dec.replace("_", " ")
        if dec == "launch_retry":
            on = "a retry next tick (%s)" % row.get("why")
        row["waits_on"] = on
        k, txt = "wait", "waiting on %s" % (on or "nothing running (%s)" % dec)
    elif dec == "owner":
        k, txt = "owner", "OWNER %s" % row.get("why")
    elif dec == "rested":
        k, txt = "rested", "RESTED %s" % row.get("why")
    else:
        k = "paused"
        txt = "PAUSED %s: %s" % (PAUSE_WHY.get(dec, dec), row.get("why"))
    row["klass"], row["status"] = k, txt
    prev = s.get("klass_since") or {}
    named = bool(row.get("waits_on"))
    # a named wait that ends (a Designer run closed) restarts the clock: the stall counts from when nothing ran
    if prev.get("k") != k or prev.get("d") != dec or prev.get("w", named) != named:
        s["klass_since"] = {"k": k, "d": dec, "w": named, "at": now}
    row["for_min"] = round((now - s["klass_since"]["at"]) / 60)
    stuck = (k == "wait" and not row.get("waits_on")) or k not in ("launch", "wait", "paused", "owner", "rested")
    row["stalled"] = bool(stuck and row["for_min"] >= int(cfg.get("stalled_min", 10)))


# ---- the acts: steward and fixer launches, owner cards ---------------------------------------------------------------

STEWARD_RULES = """Rules (the owner's, carried; every one binds you):
- You are the Maturation Pipeline's STEWARD for this one state: you do what the Conductor used to do by hand here, with
  his authority for this step only (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). Read the evidence first; write what you read.
- Never certify a concept tree, lock a version (the Dispatch tick itself locks a new mod at 0.1.0 under his
  Evidence-for-Ask ruling), classify a change Convergent or Divergent, loosen a bar, change his rulings, or pass his
  walk. If the state needs one of those, stop and write the ready-to-ask card text (question, options, evidence
  paths) in your ledger note; the pipeline shows it to him.
- Evidence-for-Ask (his ruling, 2026-11-15): any other choice you meet, take the obvious answer and log it as a
  delegated call (`--why "delegated: <class>"`). Write a card only with recorded evidence that the obvious answer is
  wrong, and the card quotes that evidence.
- Never take the bridge, start or stop a game, or launch another run yourself: the Dispatch tick launches the next run
  when your move lands. Never open a fourth blind cycle in one visit.
- A failed or UNMEASURED line is filed as a NAMED item (`rimflow file <NAME> --for BENCH --caused-by %(item)s ...`;
  name grammar PROJECT_VERB_INTENTION_TWIST, `rimflow namecheck`), each with its acceptance test (a command that fails
  now and passes on a fix, or `Acceptance test: none, <reason>`), caused by THIS item so the tick finds and fixes them.
- Move the mod only with `python3 src/RimMandrake/rimflow/maturation.py advance <Mod> --to <stage> --by BENCH --why
  "..." [--steward-confirms "<what you read and the verdict>"]`, forward one stage or along a drawn road back.
- Land with `./publish -m "subject" <explicit paths>` (the record, the journal, the ledger shard); a move that is not on
  origin/main did not happen. Close this item with the published sha.
- Judge the judge first (the Conductor's night rule, 2026-11-15). Before you act on a blind cycle's or a visit's record,
  sort every reason `maturation.py next` gives for "not met" into one of three and say which in your note:
  RECORD GAP (the run did it but did not record it in the form the reader wants): redo the demonstration for real (a
  fix: its test red at the commit before, green at HEAD), never write it from the report.
  CRITERION FLAW (the check demands what no correct build could give): never loosened by you or by the builder. File
  it as a named item for a neutral fixer with a refusal record (evidence, would_pass, smallest_fix); if the bar keeps
  its meaning, the criterion's text is repaired and re-pinned (next rule); if the bar's words are wrong, it is his card.
  REAL MISS (a Problem left open, a rerun not done): file it down the road back.
  Then read `tests_edited.json` and the diff of every test the judge touched: an assertion weakened, skipped or
  deleted is a REAL MISS, filed, and the cycle's verdict does not stand on that test.
- Re-pin rule (his standing decision, 2026-11-14): a locked file that changed after the lock ONLY in test text, check
  wording or bookkeeping fields, the bar's meaning unchanged, is re-pinned in `version/bars.md` with a journal line
  saying what changed and why the meaning is the same. A changed bar (its words, its numbers, what decides it, which
  version holds it) is never re-pinned by you: that is his card, with the before and after text.
""" + M.SELF_FIX_RULE + "\n"


# a Stage 6 failure goes to the lowest stage that can show it (spec Stage 6 road back; "Offline stages never wait for a
# game"): RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED, after FlowWorks and Explosive Knockback sat at
# Stage 3 with twelve items only the game could close
STAGE6_ROAD = (
    "Sort each failed line by the lowest stage that can show its fault, and say which in its item:\n"
    "- An offline test can show it (a selftest against a fake bridge or map, a pure-function check, a criterion text): "
    "file it with `--needs offline`; its body names that offline acceptance command (red on the old code), and its "
    "in-game check (the test table's stage-6 id and its exact live command), which its fixer records UNRUN for Stage 6 "
    "with `maturation.py unrun` when it closes the item on the offline test.\n"
    "- Only the game can show it (the cause is unknown until a live experiment, or the fault lives in the engine's "
    "behaviour no fake models): file it with `--needs game-up`; it is Stage 6 work, game-only, and is never sent to "
    "Stage 3. When every failed line is game-only, advance --to in_game (the next visit), never --to offline_build.\n"
    "- A mix: advance --to offline_build for the offline lines; the tick gives the game-only ones no run there, and "
    "when only they are open the record goes back with `maturation.py advance <Mod> --to in_game --game-only <IDS>`.")


def steward_brief(root, mod, row):
    try:
        nx = M.next_step(root, mod)
        nxt = nx.get("next")
        refs = "\n".join("- %s: %s" % (r["clause"], r["observed"]) for r in nx.get("refusals") or [])
    except Exception as e:      # noqa: BLE001
        nxt, refs = "maturation.py next failed: %s" % e, ""
    kind = row.get("steward_kind")
    task = {
        "exit_not_met": "The %s ended NOT met. Read its SUMMARY.md and rows. File EACH failed or UNMEASURED line as a "
                        "named item (caused by this item); when a line's check is an OFFLINE command (a selftest or offline check "
                        "that runs in under 120 s, never a bridge, game or live run), its item's prose (items/<ID>.md) "
                        "carries `## launch-checks` then `must-fail: <that command>`, so a fixer whose red already passes "
                        "is refused at launch. Then send the mod down its road back (%s). If the reading says "
                        "a new blind judge is owed (its Problems were FIXED in the cycle), file nothing new: advance "
                        "--to blind_challenge, so a judge who did not see the fixes judges them. The tick launches "
                        "one fixer per item, and the next visit or cycle when they close.%s" % (
                            "in-game visit" if row.get("stage") == "in_game" else "blind cycle",
                            "advance --to offline_build, or --to blind_challenge when every failure is a check or "
                            "scene of the blind lane, or --to in_game when every failure is game-only; see below"
                            if row.get("stage") == "in_game" else "advance --to blind_challenge opens the next cycle",
                            "\n\n" + STAGE6_ROAD if row.get("stage") == "in_game" else ""),
        "exit_met": "The program reads the exit as met. Read SUMMARY.md and the rows yourself; if they bear it out, "
                    "advance with --steward-confirms naming the run and the verdict read; if not, file what is wrong "
                    "as named items caused by this item and do not advance.",
        "ready": "Every exit test passes: advance the mod one stage (no confirmation is owed).",
        "exam_retake": "The concept stands at Designer stage 5 and its Cold Reader exam fails its gate, so the coverage "
                       "judge skips it and nothing else moves it. The gate reads: %s. Retake the exam by "
                       "src/RimMandrake/rimflow/roles/designer_exam.md IN FULL (read the whole file first): frozen "
                       "inputs, the Examiner's scenarios, the Challenger's scenarios (a second fresh agent), the "
                       "Readers, and the control copy (`designer_stage.py exam-control design/concepts/%s --leaf <id>`, "
                       "its control Reader's missed_ids). Its Examiner, Challenger, Readers and control Reader are "
                       "fresh subagents you start (opus or sonnet), as that file says; they are not pipeline runs. "
                       "Never edit tree.json, the sheet or the scenes. Done when `coverage_judge.py status "
                       "design/concepts/%s` no longer reads \"the exam does not pass\" (it runs the exam gate; a "
                       "retake opens no Designer run, so there is no result.json to check); land exam.json and exam_control/ with ./publish." % (
                           row.get("steward_need") or row.get("why"), mod, mod),
        "cycle_unfinished": "The blind cycle's record has no Exit block and nothing is live on it, so no program can "
                            "read whether it was met. Read the record folder (SUMMARY.md, lane1, lane2, "
                            "tests_edited.json) and `maturation.py next`. If the judging is all there and only its "
                            "form is missing (no Exit block, a row with no command, a result in the wrong folder), "
                            "that is a RECORD GAP: complete the record from the files, redoing any red-then-green "
                            "demonstration for real, and never write a verdict the files do not hold. If the lanes are "
                            "not all there (the judge stopped before it finished judging), do not judge in its place: "
                            "write in your note exactly which lanes and rows are missing and stop; the Conductor "
                            "decides between resuming this cycle and opening the next.",
        "builder_stalled": "An offline builder ended and resolved NONE of the refused bars, so nothing more is built "
                           "on this mod until someone knows why. Find out; do not build the checks yourself. Read the "
                           "builder's item to its end (`rimflow show <item>`), its result file, what it published "
                           "(`git log origin/main --grep <item>`) and the bundle its end line names. Say which of "
                           "these it was, with the evidence, in your note:\n"
                           "- STOPPED EARLY: its last words wait on helpers or a background command, or its bound ran "
                           "out with work unlanded (a headless run ends with its turn; what it left running died). "
                           "File the bars it did not reach as named items of about six bars each, each with the "
                           "command that shows its bars refused now, caused by this item: one fixer builds each.\n"
                           "- WRONG KIND OF WORK: the bars are refused for something no builder can build (a hand "
                           "step, his decision, a check only the live game can run). File or card each as what it is.\n"
                           "- PIPELINE DEFECT: the table, the reader or a tool refused correct work. The self-fix rule "
                           "below: file it, fix it, tests first.\n"
                           "- TOO BIG for one run: split it into named items as under STOPPED EARLY.\n"
                           "Never run `maturation_dispatch.py clear` and never launch a builder: the stop lifts by "
                           "itself when a refused bar is resolved, and the tick runs one fixer per item you file.",
        "hand_step": "Only hand steps remain (%s): read what each asks and pass --steward-confirms if it holds; if it "
                     "does not, file the gap as a named item caused by this item." % ", ".join(row.get("hand_steps") or []),
    }.get(kind, row.get("steward_need") or row.get("why"))
    if row.get("road_back_after"):
        task = ("%s\n\nThis state was read before: the road back %s opened is CLOSED (every item it filed is closed, each "
                "through its fixer run). File nothing already filed; read whether the fixes owe a new blind judge or "
                "visit, and if they do, advance (--to blind_challenge for a blind cycle) so a judge who did not see the "
                "fixes judges them." % (task, " then ".join(str(x) for x in row["road_back_after"])))
    return "\n".join([
        "# Maturation steward run: %s, %s (%s)" % (mod, M.label(row.get("stage")) if row.get("stage") in M.WORDS
                                                   else row.get("stage"), kind),
        "", "Item: %(item)s. Seat BENCH.", "",
        "## The state the Dispatch tick read", "", "- decision: %s" % row.get("decision"),
        "- why: %s" % row.get("why"), "- maturation.py next: %s" % nxt, refs, "",
        "## Your task", "", str(task), "", "Detail: %s" % (row.get("steward_need") or ""), "",
        STEWARD_RULES, "",
        "Before you stop, write a ledger note (`rimflow note %(item)s --text ... --seat BENCH --why \"steward run\"`) "
        "saying what you read, what you moved or filed, and anything that is the owner's (as card text).", ""])


LIVE_NEEDS = M.LIVE_NEEDS


def live_only(items):
    """True when there are items and every one needs the live game (its ledger `needs` in LIVE_NEEDS): at a Stage 6
    record (M.game_takeable) a holder run on them is given the live brief (RIMMANDRAKE_LET_HOLDER_TAKE_BRIDGE_ALL_ITEMS_
    NEED_GAME); at an offline stage they get no run at all, the record goes back to Stage 6
    (RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED)."""
    return bool(items) and all((x or {}).get("needs") in LIVE_NEEDS for x in items)


def live_rules(purpose, mod, seat="BENCH"):
    """-> the live half of a holder or fixer brief: maturation.BRIDGE_RULES (the in-game driver's rules) plus bringing
    the game up and running each item's live acceptance commands."""
    rules = [r % tuple(x for x in ((purpose, seat) if "take --idle-ok" in r else (seat,) if "release" in r else
                                   (mod,) if "deploy_custom_mods" in r else ()))
             for r in M.BRIDGE_RULES]
    return ("\n## The bridge and the game (this run may use them; each rule binds)\n\n"
            "Every item here needs the live game, so this run takes it; one bridge holder at a time.\n%s\n"
            "- Bring the game up on the tier the test needs, after the bridge is yours (holding the bridge is blanket "
            "authorization to start Steam and launch the game): swap the list if the test names one, deploy, then "
            "`./game --idle-ok --why \"%s\" up` once it is at a usable menu or map.\n"
            "- The live acceptance commands are in each item's newest note starting `LEFT OPEN:` (`python3 "
            "src/RimMandrake/rimflow/cli.py show <ITEM>`): run them, diagnose and fix what fails while the game is up, "
            "and re-run until it passes or you know why it cannot.\n"
            "- Before you end: the game is at a clean state or closed, and the bridge is released.\n" % (
                "\n".join(rules), purpose))


# the offline half of a road-back item (RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED; spec Stage 3 exit and
# Stage 6 road back): it closes on an offline test; its in-game check is recorded UNRUN for Stage 6, never run here
OFFLINE_CLOSE = (
    "This run is offline: the item closes on its OFFLINE acceptance test (an offline test that fails on the old code, "
    "written first, run and seen passing on the fix). Its in-game check is Stage 6's: record it UNRUN with its exact "
    "command, `python3 src/RimMandrake/rimflow/maturation.py unrun %(mod)s --item %(item)s --check <the test table's "
    "stage-6 id> --command \"<its exact live command>\" --offline \"<the offline test>\" --sha <the sha it is green "
    "at>`, land `design/concepts/%(mod)s/version/in_game/unrun.jsonl` with the fix, then close the item. If no offline "
    "test can show the fault, say why in a note starting LEFT OPEN: and set `rimflow needs %(item)s --to game-up`: it is "
    "Stage 6 work, and the record goes back there. Never take the bridge or a game.")


def fixer_brief(item, mod, cap, fix_for=None, live=False):
    if fix_for == "blocked":
        return ("# Pipeline-defect fix: %s (%s)\n\nItem: %s. Seat BENCH.\n\nRead `python3 "
                "src/RimMandrake/rimflow/cli.py show %s` to its end: %s's Designer ended blocked on it, a defect in the "
                "pipeline's own machinery, and the mod is PAUSED until it is fixed. Fix it, its acceptance test first "
                "(watch it fail on the base), land with `./publish -m ... <paths>`, close the item with the published "
                "sha, then un-block the Designer: `python3 src/RimMandrake/rimflow/designer_stage.py unblock "
                "design/concepts/%s --why \"%s fixed at <sha>\"` and land design/concepts/%s/stage.json. If it cannot "
                "be fixed offline, or the fix is the owner's (a bar, a ruling, a spend cap), write that in a note "
                "starting LEFT OPEN: and drop nothing. Never take the bridge or a game.\n%s\n" % (
                    item, mod, item, item, mod, mod, item, mod, M.SELF_FIX_RULE))
    return ("# Road-back fix: %s (%s)\n\nItem: %s. Seat BENCH.\n\nRead `python3 "
            "src/RimMandrake/rimflow/cli.py show %s` to its end: it is one failed line of %s's in-game visit or blind "
            "cycle, sent back by the steward. A line sent back is one symptom: before you fix it, read the other failed "
            "lines of the same visit or cycle that touch the same system, and if two or more share a cause, fix the "
            "cause. If this line has come back before (its item history shows it), do not tune it again: say what the "
            "earlier fixes changed and why they did not hold. Fix it, run its acceptance test (watch it fail first if "
            "it is new), land "
            "with `./publish -m ... <paths>`, and close the item with the published sha. If it cannot be fixed "
            "offline, or the fix is the owner's (a bar, a ruling, a classification), write that in a note and drop "
            "nothing. %s\n%s\n\n%s\n\n%s\n" % (item, mod, item, item, mod, "Its acceptance test needs the live game: use it "
                                               "as the section below says, and write a note starting LEFT OPEN: on "
                                               "what still fails." if live else OFFLINE_CLOSE % {"mod": mod, "item": item},
                                               M.SELF_FIX_RULE, M.HOW_A_BAR_HOLDS, M.OFFLINE_MODEL)
            + (live_rules("%s holder run on %s" % (mod, item), mod) if live else ""))


ADVANCE_KINDS = ("ready",)     # a steward that only advances; designer_locked's own steps (lock-bars, next-version) can
                               # turn the gate's version clause, so a launch check there would refuse a good run


def advance_checks(row):
    """-> the `## launch-checks` block for a steward item that advances the mod one stage, or None."""
    stage = row.get("stage")
    if row.get("steward_kind") not in ADVANCE_KINDS or stage not in M.WORDS or M.WORDS.index(stage) + 1 >= len(M.WORDS):
        return None
    import launch_checks
    return launch_checks.block_for("advance", mod=row["mod"], to=M.WORDS[M.WORDS.index(stage) + 1])


def item_name(row, known):
    mod = row["mod"].upper()
    n = M_word(row.get("visit") if row.get("stage") == "in_game" else row.get("cycle"))
    kind = row.get("steward_kind")
    what = "VISIT" if row.get("stage") == "in_game" else "CYCLE"
    base = {"exit_not_met": "RIMMANDRAKE_ROUTE_%s_%s_%s_FAILURES_BACK" % (mod, what, n),
            "exit_met": "RIMMANDRAKE_CONFIRM_%s_%s_%s_EXIT_MET" % (mod, what, n),
            "ready": "RIMMANDRAKE_ADVANCE_%s_PAST_%s" % (mod, str(row.get("stage")).upper()),
            "hand_step": "RIMMANDRAKE_CONFIRM_%s_%s_HAND_STEPS" % (mod, str(row.get("stage")).upper()),
            "chain": "RIMMANDRAKE_RETAKE_%s_EXAM_AFTER_LOCKED_CHANGE" % mod,
            "exam_retake": "RIMMANDRAKE_RETAKE_%s_EXAM_FAILING_ITS_GATE" % mod,
            "designer_locked": "RIMMANDRAKE_ADVANCE_%s_LOCKED_VERSION_TO_PREFLIGHT" % mod,
            "stage": "RIMMANDRAKE_STEWARD_%s_%s_STAGE" % (mod, str(row.get("stage")).upper()),
            "builder_stalled": "RIMMANDRAKE_TRIAGE_%s_BUILDER_RESOLVED_NOTHING" % mod,
            "cycle_unfinished": "RIMMANDRAKE_COMPLETE_%s_CYCLE_%s_RECORD_NO_EXIT" % (mod, n),
            }.get(kind, "RIMMANDRAKE_STEWARD_%s_HAND_STEP" % mod)
    while len(base) > 56:
        base = base.rsplit("_", 1)[0]
    if base not in known:
        return base
    for k in range(2, 20):
        cand = "%s_RUN_%s" % (base, M_word(k))
        if cand not in known:
            return cand
    return None


def M_word(n):
    import maturation_dispatch as MD
    return MD.word(n or 0) if isinstance(n, int) else "ONE"


def launch_brief(item, text, model, cap, seat="BENCH", runner=subprocess.run, env=None, session=None):
    path = os.path.join(M.brief_dir(), "%s-%d.md" % (item, int(time.time())))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    argv = [sys.executable, M.detached_helper_path(), "launch", "--seat", seat, "--item", item, "--brief-file", path,
            "--model", model, "--budget-usd", "%g" % cap]
    for k, v in sorted((env or {}).items()):        # a pilot holder's RM_MODLEDGER_WRITER (maturation_dispatch.ledger_open)
        argv += ["--env", "%s=%s" % (k, v)]
    if session:     # a pilot holder's recorded session (modledger.resume_plan), resumed
        argv += ["--resume", session]
    r = runner(argv, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    m = re.search(r"^DETACHED (\S+)", r.stdout or "", re.M)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip(), (m.group(1) if m and not r.returncode else None)


def execute(root, cfg, st, rows, launches, now, fx=None):
    """Launch the steward and fixer rows named in launches. Each try is recorded under its key BEFORE the result is
    known, so a failure is never retried on its own."""
    import maturation_dispatch as MD
    fx = fx or {}
    do_file = fx.get("file", MD.file_and_publish)
    do_launch = fx.get("launch_brief", launch_brief)
    do_publish = fx.get("publish", MD.publish_filed)
    known = fx["known"]() if "known" in fx else MD.known_items()
    for row in rows:
        if row["mod"] not in launches or not row.get("aut"):
            continue
        try:
            if row["aut"] == "autolock":     # the pipeline's own act: no brief, no run, one landing
                text = fx.get("autolock", autolock_and_land)(root, row["mod"], now=now)
                st["mods"][row["mod"]].setdefault("steward", {})[row["steward_key"]] = {
                    "item": M.EVIDENCE_FOR_ASK, "unit": None, "at": now, "failed": None,
                    "tries": int((row.get("retry_of") or {}).get("tries") or 0) + 1, "landed": text}
                row.update(decision="launched", why="the pipeline locked %s at 0.1.0 (his Evidence-for-Ask ruling): %s"
                           % (row["mod"], text))
                continue
            if row["aut"] == "autorepin":    # RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE: an act like the autolock
                text = fx.get("autorepin", repin_and_land)(root, row["mod"], row["repin_sources"], now=now)
                st["mods"][row["mod"]].setdefault("steward", {})[row["steward_key"]] = {
                    "item": None, "unit": None, "at": now, "failed": None, "sources": list(row["repin_sources"]),
                    "tries": int((row.get("retry_of") or {}).get("tries") or 0) + 1, "landed": text}
                row.update(decision="launched", why="the pipeline re-pinned %s for its granted look, citing his cards "
                           "%s: %s" % (row["mod"], ", ".join(row["repin_sources"]), text))
                continue
            _execute_one(root, cfg, st, row, now, do_file, do_launch, known, do_publish)
        except Exception as e:      # noqa: BLE001  one row's failure is that row's PAUSE, never the tick's crash
            book = st["mods"][row["mod"]].setdefault("fixers" if row.get("aut") == "fixer" else "steward", {})
            book[row.get("fix_item") or row.get("steward_key")] = {
                "item": row.get("item"), "unit": None, "at": now, "failed": "%s: %s" % (type(e).__name__, e),
                "tries": int((row.get("retry_of") or {}).get("tries") or 0) + 1}
            row.update(decision="launch_failed", why="%s: %s" % (type(e).__name__, e))


def _execute_one(root, cfg, st, row, now, do_file, do_launch, known, do_publish=None):
    import maturation_dispatch as MD
    mod, s = row["mod"], st["mods"][row["mod"]]
    model = cfg.get("steward_model", "opus")
    retry = row.get("retry_of") or {}
    tries, filed = int(retry.get("tries") or 0) + 1, False
    if row["aut"] == "fixer":
        item, ok, text = row["fix_item"], True, "road-back item filed by the steward"
        # a pilot's fixer on an item that needs the game is given the game (RIMMANDRAKE_LET_HOLDER_TAKE_BRIDGE_ALL_ITEMS_NEED_GAME)
        live = (row.get("fix_for") != "blocked" and M.game_takeable(row.get("stage")) and MD.pilot_ledger(root, mod)
                and live_only([{"needs": M.ledger_needs(root, [item]).get(item)}]))
        brief = fixer_brief(item, mod, row["cap"], row.get("fix_for"), live=live)
        book = s.setdefault("fixers", {})
        key = item
    else:
        key, book = row["steward_key"], s.setdefault("steward", {})
        if retry.get("item") and retry.get("filed", str(retry.get("failed") or "").startswith("filed ")):
            # the last try filed its item and the launch never started: publish again, launch the same item
            item = retry["item"]
            ok, text = (do_publish or MD.publish_filed)(item)
            text = "retry %d of %s, filed earlier; %s" % (tries, item, text)
        else:
            item = item_name(row, known)
            title = "%s: maturation steward run, %s at %s (launched by the Dispatch step)" % (
                mod, row.get("steward_kind"), row.get("stage"))
            why = "delegated: maturation_autonomy.py; %s; measured %s" % (str(row.get("why")), MD.pac(now))
            spec = advance_checks(row)      # the launch re-reads the gate first (GATE_FIRST)
            ok, text = (do_file(item, title, why, **({"spec": spec} if spec else {})) if item else
                        (False, "no free item name"))
        filed = ok
        brief = (steward_brief(root, mod, row).replace("%(item)s", str(item)).replace("%(cap)s", str(row["cap"]))
                 if ok else "")
    unit, led = None, None
    if ok and MD.pilot_ledger(root, mod):       # a pilot mod's run starts from its ledger packet (modledger.launch)
        led = MD.ledger_open(root, mod, row["aut"], brief, stage=row.get("stage"), now=now)
        brief = led["brief"]
    if ok:
        rc, text2, unit = do_launch(item, brief, model, row["cap"], cfg.get("seat", "BENCH"),
                                    **({"env": led["env"]} if led else {}))
        ok = rc == 0 and bool(unit)
        text = "%s; %s" % (text, (text2 or "").splitlines()[0] if text2 else rc)
    if led:
        text = "%s; %s" % (text, MD.ledger_after(root, st, mod, led, unit if ok else None, item, now))
    book[key] = {"item": item, "unit": unit, "at": now, "cap": row.get("cap"), "failed": None if ok else text,
                 "tries": tries, "filed": filed}
    if not ok and cfg.get("_code"):
        book[key]["code"] = cfg["_code"]
    if ok and row["aut"] == "steward" and row.get("steward_kind") in ("exit_not_met", "exit_met", "builder_stalled"):
        s["road_back"] = {"caused_by": item, "at": now, "from": row.get("stage")}
    if ok:
        row.update(decision="launched", unit=unit, item=item, why=text)
        known.add(item) if isinstance(known, set) else None
    elif transient(text) and tries < int(cfg.get("launch_tries", 3)):
        row.update(decision="launch_retry", why="the %s launch failed on a transient fault (try %d of %d), the next "
                   "tick tries it again: %s" % (row["aut"], tries, int(cfg.get("launch_tries", 3)), text))
    else:
        row.update(decision="launch_failed", why=text)


def conductor_log():
    p = os.environ.get("RM_CONDUCTOR_LOG")
    if p:
        return p
    import doorbell
    return os.path.join(os.path.dirname(doorbell.state_dir()), "conductor", "log.md")


def post_cards(rows, st, now, fx=None):
    """Write each OWNER row's card text in the Conductor log once per (mod, card)."""
    import maturation_dispatch as MD
    fx = fx or {}
    write = fx.get("card", None)
    posted = st.setdefault("owner_cards", {})
    out = []
    for row in rows:
        if row.get("klass") != "owner" or not row.get("card"):
            continue
        key = "%s|%s" % (row["mod"], _h(row["card"]))
        if key in posted:
            continue
        text = ("\n## %s Maturation Pipeline: a stop that is his (%s)\n\nCard, ready to ask (question-card skill): %s\n"
                % (MD.pac(now), row["mod"], row["card"]))
        try:
            if write:
                write(text)
            else:
                with open(conductor_log(), "a", encoding="utf-8") as f:
                    f.write(text)
            posted[key] = now
            out.append(row["mod"])
        except OSError as e:
            row["card_error"] = str(e)
    return out


def annotate(rd, rows):
    """Add the classes to the dispatch reading: per mod klass/status/for_min, and the paused, owner and stalled lists
    ops_watch counts (maturation.paused, maturation.stalled)."""
    for r in rows:
        m = rd["mods"].setdefault(r["mod"], {})
        for k in ("klass", "status", "for_min", "waits_on", "queue", "unit", "item"):
            if r.get(k) is not None:
                m[k] = r.get(k)
        m["decision"], m["why"] = r.get("decision"), r.get("why")
    rd["paused"] = ["%s: %s" % (r["mod"], r.get("status")) for r in rows if r.get("klass") == "paused"]
    rd["owner"] = ["%s: %s" % (r["mod"], r.get("card") or r.get("why")) for r in rows if r.get("klass") == "owner"]
    rd["stalled"] = [r["mod"] for r in rows if r.get("stalled")]
    return rd
