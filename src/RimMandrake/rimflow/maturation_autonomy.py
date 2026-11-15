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
           (OPS_MATURATION_MOD_PAUSED) while any mod is paused, so a repeat reopens it
  owner    a stop that is genuinely his (his walk, the lock, opening the next version, a Designer turn waiting on him):
           a ready-to-ask card text goes in the Conductor log once
A steward or fixer run is tried ONCE per state (its key); if it ends and the state has not moved, the mod is PAUSED,
never retried (the owner's condition, 2026-11-14: "As long as we don't have automated loops rejecting/cycling things,
we can't get into too much trouble."). A mod in `wait` with nothing named running, or with no class, for stalled_min
(10) raises maturation.stalled (OPS_MATURATION_MOD_STALLED).

Never: certify, lock, classify Convergent/Divergent, loosen a bar, take the bridge or a game, launch on a mod with a
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
        "queued"}
LAUNCH = {"launch", "launched", "would_launch"}
STEWARD_ON = {"hand_step", "ready", "exit_met", "exit_not_met"}
OWNER_STAGES = {"his_walk": "his live walk (Stage 8): the version passes on his words alone",
                "passed": "the version passed; opening the next version is decided with him (spec §3.8)"}
STEWARD_STAGES = {"preflight", "pre_human"}     # stages whose whole step is the steward's: run it, then advance
CHAIN_AFTER = ("coverage_release", "coverage_stop", "lock")


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
        raise RuntimeError("land.sh exited %d: %s" % (p.returncode, p.stderr.strip()[-300:]))
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
    for m in found:
        if m not in adv:
            adv.append(m)
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
    try:
        with open(os.path.join(root, "design", "concepts", mod, "record.json"), encoding="utf-8") as f:
            st["_asks"] = [a.get("title") or a.get("id") for a in json.load(f).get("asks") or [] if isinstance(a, dict)]
    except (OSError, ValueError, AttributeError):
        pass
    return st


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
        if '"Designer"' not in ln or '"launched"' not in ln:
            continue
        try:
            e = json.loads(ln)
        except ValueError:
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


def version_locked(root, mod):
    v, _ = M.read_json(root, mod, "version/VERSION.json")
    return str((v or {}).get("state") or "").startswith("locked")


# ---- one class per mod -----------------------------------------------------------------------------------------------

def _steward(row, kind, key, why, brief_need):
    row.update(aut="steward", steward_kind=kind, steward_key=key, decision="steward", why=why, need=None)
    row["steward_need"] = brief_need


def resolve(root, cfg, st, facts, rows, launches, now, fx=None):
    """-> (rows, launches): every row gets `klass` and a plain `status`; hand-step decisions become steward or fixer
    launches (within max_live and the caps), paused or owner. Mutates st (steward/fixer keys, queue, class clocks)."""
    fx = fx or {}
    mods = st.setdefault("mods", {})
    import maturation_dispatch as MD
    live_total = MD.occupancy(facts)
    live_total = None if live_total is None else live_total + len(launches)
    open_items = fx.get("open_items", lambda ids: M.ledger_items_caused_by(root, ids))
    dstate = fx.get("designer_state", lambda m: designer_state(root, m))
    locked = fx.get("version_locked", lambda m: version_locked(root, m))
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
        if dec in WAIT or dec in LAUNCH:
            pass
        elif (st.get("seed_refused") or {}).get(mod):
            row.update(decision="seed_refused", why="its stage record could not be seeded: %s" % st["seed_refused"][mod])
        else:
            _route(root, cfg, s, f, row, ver, dstate, locked, open_items, fx.get("designer_unit", designer_unit))
        # one automatic run per state, then a steward or fixer within the caps
        if row.get("aut"):
            ok, why = _gate(cfg, s, row, live_total, ver)
            if ok:
                live_total = None if live_total is None else live_total + 1
                launches = [m for m in launches if m != mod] + [mod]
            else:
                row.update(decision=why[0], why=why[1], aut=None)
    return rows, launches


def classify(cfg, st, rows, now):
    """After the acts: one class per row (launched, failed and waiting rows read as they ended this tick)."""
    queue = st.get("ingame_queue") or {}
    for row in rows:
        _klass(cfg, st.setdefault("mods", {}).setdefault(row["mod"], {}), row, now, queue)
    return rows


def _route(root, cfg, s, f, row, ver, dstate, locked, open_items, fx_dunit=designer_unit):
    mod, dec, stage = row["mod"], row.get("decision"), row.get("stage")
    dst = dstate(mod)
    lc = chain_owed(dst)
    if lc:
        _steward(row, "chain", "%s|chain|%s" % (ver, lc.get("at")),
                 "a locked change landed %s and no coverage look has followed it: re-pin, Cold Reader exam retake, "
                 "ONE coverage-judge look" % lc.get("at"),
                 "the locked change of %s (%s): check its re-pin (designer_stage.py repin, already done when the history "
                 "says re-pinned), retake the Cold Reader exam on the new tree, then give it ONE coverage-judge look "
                 "(coverage_judge.py release <dir> --why ..., then run). Never a second look." % (
                     lc.get("at"), str(lc.get("why"))[:300]))
        return
    rb = s.get("road_back")
    if rb and stage in ("offline_build", "blind_challenge", "in_game") and stage != rb.get("from"):
        # the steward moved the mod down its road back: its filed items are fixed before the mod moves on
        items = open_items([rb["caused_by"]])
        if items is None:
            row.update(decision="blind", why="the ledger cannot be read for the road-back items")
            return
        if items:
            fixed = s.setdefault("fixers", {})
            todo = [x for x in items if x["id"] not in fixed]
            if todo:
                row.update(aut="fixer", fix_item=todo[0]["id"], decision="fixer",
                           why="road-back item %s (of %d open, caused by %s) gets one fixer run" % (
                               todo[0]["id"], len(items), rb["caused_by"]))
            else:
                row.update(decision="fixer_spent", why="every open road-back item (%s) has had its one fixer run and "
                           "is still open" % ", ".join(x["id"] for x in items))
            return
        s.pop("road_back", None)        # every road-back item closed: the mod moves on (visit N+1 when it arrives)
        row["road_back_closed"] = rb["caused_by"]
        if dec == "stopped":
            s.pop("stopped", None)
    if stage in OWNER_STAGES:
        row.update(decision="owner", why=OWNER_STAGES[stage],
                   card="%s %s stands at %s. %s. Evidence: design/concepts/%s/journal.md and %s." % (
                       mod, ver, M.label(stage), OWNER_STAGES[stage], mod, M.RECORD))
        return
    if stage in (UNM, "designer", "intake") or stage is None:
        _designer_lane(row, mod, ver, dst, locked, fx_dunit)
        return
    if stage in STEWARD_STAGES and dec == "not_offline":
        _steward(row, "stage", "%s|%s" % (ver, stage), "%s is the steward's step: run it, then advance" % M.label(stage),
                 "do %s as the spec says (design/specs/2026-11-13-maturation-pipeline.md) and advance with "
                 "--steward-confirms naming what you read" % M.label(stage))
        return
    if dec in STEWARD_ON:
        n = row.get("visit") if stage == "in_game" else row.get("cycle") if stage == "blind_challenge" else None
        if dec == "exit_not_met" and stage == "blind_challenge" and (f.get("visit") or 0) >= M.CYCLE_LIMIT:
            row.update(decision="cycle_limit", why="three blind cycles in this visit ended not met; his rule of "
                       "2026-11-13 brings the Conductor in (maturation.py advance %s --to blind_challenge "
                       "--conductor-decision \"...\" un-pauses it)" % mod)
            return
        _steward(row, dec, "%s|%s|%s|%s|%s" % (ver, stage, dec, n, _h(row.get("refused_ids") or row.get("why"))),
                 row.get("why"), row.get("need") or row.get("why"))


def _designer_lane(row, mod, ver, dst, locked, dunit=designer_unit):
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
                            mod, stg, str(last.get("why") or "")[:400], str(dst.get("pending_decision") or "none")[:400],
                            "; ".join(str(x) for x in (dst.get("_asks") or [])[:6]) or "none written", mod))
    elif stt == "blocked" and "OWNER HOLD" in str(dst.get("blocked_on") or ""):
        row.update(decision="owner", why="an owner hold stands on the Designer (stage %s)" % stg,
                   card="%s, Designer stage %s, is held for you: %s Evidence: design/concepts/%s/stage.json." % (
                       mod, stg, str(dst.get("blocked_on"))[:500], mod))
    elif stt == "blocked":
        row.update(decision="designer_blocked", why="%s (designer_stage.py unblock or the named release un-pauses "
                   "it)" % str(dst.get("blocked_on") or "no reason written")[:300])
    elif stt == "locked" or (stg == 5 and locked(mod)):
        _steward(row, "designer_locked", "%s|designer|locked" % ver, "the Design Version is locked: advance it to "
                 "preflight", "the version is locked; advance %s --to preflight (the lock clause passes)" % mod)
    elif stg == 5 and not locked(mod):
        row.update(decision="owner", why="the lock is his (Designer stage 5, VERSION.json not locked)",
                   card="Lock %s's Design Version? The Designer stands at stage 5 (Lock); VERSION.json is not locked. "
                        "Evidence: design/concepts/%s/tree.json and record.json." % (mod, mod))
    else:
        unit = dunit(mod)
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
        return False, ("steward_spent" if row["aut"] == "steward" else "fixer_spent",
                       "the automatic %s run on this state (%s) %s and the state has not moved; un-pause: "
                       "`maturation_dispatch.py clear %s --why ...` after reading it" % (
                           row["aut"], x.get("unit") or x.get("item"), "failed to launch: %s" % x["failed"]
                           if x.get("failed") else "ended", row["mod"]))
    if not cfg.get("steward_enabled", True):
        return False, ("steward_off", "steward_enabled is off in maturation_dispatch.json")
    n = len([k for k in done if str(k).startswith(str(ver))]) if row["aut"] == "steward" else len(done)
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
    "launch_failed": "a launch failed", "auto_spent": "the automatic runs of this visit are spent",
    "hand_run_seen": "a hand-launched run worked here and wrote no record", "steward_spent": "the steward run is spent",
    "fixer_spent": "the fixer runs are spent", "cycle_unfinished": "a cycle record has no exit block",
    "visit_unfinished": "a visit record has no exit block", "cycle_limit": "three blind cycles: the Conductor decides",
    "seed_refused": "its record cannot be seeded", "designer_blocked": "the Designer is blocked",
    "designer_unreadable": "its stage.json cannot be read", "disabled": "the step is disabled",
    "steward_off": "steward runs are off",
    "ceiling": "the stage's spend plus the next run's cap passes stage_ceiling_usd", "not_offline": "no automatic step exists for its stage",
}


def _klass(cfg, s, row, now, queue):
    dec = row.get("decision")
    if dec in LAUNCH or (row.get("aut") and dec in ("steward", "fixer")):
        k, txt = "launch", "moving: %s %s" % (row.get("aut") or "run", row.get("unit") or row.get("item") or "")
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
        row["waits_on"] = on
        k, txt = "wait", "waiting on %s" % (on or "nothing running (%s)" % dec)
    elif dec == "owner":
        k, txt = "owner", "OWNER %s" % row.get("why")
    else:
        k = "paused"
        txt = "PAUSED %s: %s" % (PAUSE_WHY.get(dec, dec), row.get("why"))
    row["klass"], row["status"] = k, txt
    prev = s.get("klass_since") or {}
    if prev.get("k") != k or prev.get("d") != dec:
        s["klass_since"] = {"k": k, "d": dec, "at": now}
    row["for_min"] = round((now - s["klass_since"]["at"]) / 60)
    stuck = (k == "wait" and not row.get("waits_on")) or k not in ("launch", "wait", "paused", "owner")
    row["stalled"] = bool(stuck and row["for_min"] >= int(cfg.get("stalled_min", 10)))


# ---- the acts: steward and fixer launches, owner cards ---------------------------------------------------------------

STEWARD_RULES = """Rules (the owner's, carried; every one binds you):
- You are the Maturation Pipeline's STEWARD for this one state: you do what the Conductor used to do by hand here, with
  his authority for this step only (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). Read the evidence first; write what you read.
- Never certify a concept tree, lock a version, classify a change Convergent or Divergent, loosen a bar, change his
  rulings, or pass his walk. If the state needs one of those, stop and write the ready-to-ask card text (question,
  options, evidence paths) in your ledger note; the pipeline shows it to him.
- Never take the bridge, start or stop a game, or launch another run yourself: the Dispatch tick launches the next run
  when your move lands. Never open a fourth blind cycle in one visit.
- A failed or UNMEASURED line is filed as a NAMED item (`rimflow file <NAME> --for BENCH --caused-by %(item)s ...`;
  name grammar PROJECT_VERB_INTENTION_TWIST, `rimflow namecheck`), each with its acceptance test (a command that fails
  now and passes on a fix, or `Acceptance test: none, <reason>`), caused by THIS item so the tick finds and fixes them.
- Move the mod only with `python3 src/RimMandrake/rimflow/maturation.py advance <Mod> --to <stage> --by BENCH --why
  "..." [--steward-confirms "<what you read and the verdict>"]`, forward one stage or along a drawn road back.
- Land with `./publish -m "subject" <explicit paths>` (the record, the journal, the ledger shard); a move that is not on
  origin/main did not happen. Close this item with the published sha.
"""


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
                        "named item (caused by this item), then send the mod down its road back (%s). The tick launches "
                        "one fixer per item, and the next visit or cycle when they close." % (
                            "in-game visit" if row.get("stage") == "in_game" else "blind cycle",
                            "advance --to offline_build, or --to blind_challenge when every failure is a check or "
                            "scene of the blind lane" if row.get("stage") == "in_game" else
                            "advance --to blind_challenge opens the next cycle"),
        "exit_met": "The program reads the exit as met. Read SUMMARY.md and the rows yourself; if they bear it out, "
                    "advance with --steward-confirms naming the run and the verdict read; if not, file what is wrong "
                    "as named items caused by this item and do not advance.",
        "ready": "Every exit test passes: advance the mod one stage (no confirmation is owed).",
        "hand_step": "Only hand steps remain (%s): read what each asks and pass --steward-confirms if it holds; if it "
                     "does not, file the gap as a named item caused by this item." % ", ".join(row.get("hand_steps") or []),
    }.get(kind, row.get("steward_need") or row.get("why"))
    return "\n".join([
        "# Maturation steward run: %s, %s (%s)" % (mod, M.label(row.get("stage")) if row.get("stage") in M.WORDS
                                                   else row.get("stage"), kind),
        "", "Item: %(item)s. Seat BENCH. Spend bound $%(cap)s.", "",
        "## The state the Dispatch tick read", "", "- decision: %s" % row.get("decision"),
        "- why: %s" % row.get("why"), "- maturation.py next: %s" % nxt, refs, "",
        "## Your task", "", str(task), "", "Detail: %s" % (row.get("steward_need") or ""), "",
        STEWARD_RULES, "",
        "Before you stop, write a ledger note (`rimflow note %(item)s --text ... --seat BENCH --why \"steward run\"`) "
        "saying what you read, what you moved or filed, and anything that is the owner's (as card text).", ""])


def fixer_brief(item, mod, cap):
    return ("# Road-back fix: %s (%s)\n\nItem: %s. Seat BENCH. Spend bound $%s.\n\nRead `python3 "
            "src/RimMandrake/rimflow/cli.py show %s` to its end: it is one failed line of %s's in-game visit or blind "
            "cycle, sent back by the steward. Fix it, run its acceptance test (watch it fail first if it is new), land "
            "with `./publish -m ... <paths>`, and close the item with the published sha. If it cannot be fixed "
            "offline, or the fix is the owner's (a bar, a ruling, a classification), write that in a note and drop "
            "nothing. Never take the bridge or a game.\n" % (item, mod, item, cap, item, mod))


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
            "designer_locked": "RIMMANDRAKE_ADVANCE_%s_LOCKED_VERSION_TO_PREFLIGHT" % mod,
            "stage": "RIMMANDRAKE_STEWARD_%s_%s_STAGE" % (mod, str(row.get("stage")).upper()),
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


def launch_brief(item, text, model, cap, seat="BENCH", runner=subprocess.run):
    path = os.path.join(M.brief_dir(), "%s-%d.md" % (item, int(time.time())))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    argv = [sys.executable, M.detached_helper_path(), "launch", "--seat", seat, "--item", item, "--brief-file", path,
            "--model", model, "--budget-usd", "%g" % cap]
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
    known = fx["known"]() if "known" in fx else MD.known_items()
    for row in rows:
        if row["mod"] not in launches or not row.get("aut"):
            continue
        try:
            _execute_one(root, cfg, st, row, now, do_file, do_launch, known)
        except Exception as e:      # noqa: BLE001  one row's failure is that row's PAUSE, never the tick's crash
            book = st["mods"][row["mod"]].setdefault("fixers" if row.get("aut") == "fixer" else "steward", {})
            book[row.get("fix_item") or row.get("steward_key")] = {"item": row.get("item"), "unit": None, "at": now,
                                                                   "failed": "%s: %s" % (type(e).__name__, e)}
            row.update(decision="launch_failed", why="%s: %s" % (type(e).__name__, e))


def _execute_one(root, cfg, st, row, now, do_file, do_launch, known):
    import maturation_dispatch as MD
    mod, s = row["mod"], st["mods"][row["mod"]]
    model = cfg.get("steward_model", "opus")
    if row["aut"] == "fixer":
        item, ok, text = row["fix_item"], True, "road-back item filed by the steward"
        brief = fixer_brief(item, mod, row["cap"])
        book = s.setdefault("fixers", {})
        key = item
    else:
        item = item_name(row, known)
        key, book = row["steward_key"], s.setdefault("steward", {})
        title = "%s: maturation steward run, %s at %s (launched by the Dispatch step)" % (
            mod, row.get("steward_kind"), row.get("stage"))
        why = "delegated: maturation_autonomy.py; %s; measured %s" % (str(row.get("why"))[:300], MD.pac(now))
        ok, text = do_file(item, title, why) if item else (False, "no free item name")
        brief = (steward_brief(root, mod, row).replace("%(item)s", str(item)).replace("%(cap)s", str(row["cap"]))
                 if ok else "")
    unit = None
    if ok:
        rc, text2, unit = do_launch(item, brief, model, row["cap"], cfg.get("seat", "BENCH"))
        ok = rc == 0 and bool(unit)
        text = "%s; %s" % (text, (text2 or "").splitlines()[0] if text2 else rc)
    book[key] = {"item": item, "unit": unit, "at": now, "cap": row.get("cap"), "failed": None if ok else text}
    if ok and row["aut"] == "steward" and row.get("steward_kind") in ("exit_not_met", "exit_met"):
        s["road_back"] = {"caused_by": item, "at": now, "from": row.get("stage")}
    if ok:
        row.update(decision="launched", unit=unit, item=item, why=text)
        known.add(item) if isinstance(known, set) else None
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
