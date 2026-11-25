#!/usr/bin/env python3
"""list_dispatch.py: the Workshop Pipeline's Waiting, Ready and Work stages. No model, no tokens of its own.

Item RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST, step 2 of
design/specs/2026-11-22-coordination-every-agent-must-use/plan.md. Page design/specs/2026-11-23-list-dispatch/boundary.md;
selftest selftest_list_dispatch.py; acceptance acceptance/step2_list_lane_accept.py. Why: on 2026-11-23 about 918 open list
items waited for the Conductor's hand, because no program launched them. The shape of red_dispatch.py.

    python3 src/RimMandrake/rimflow/list_dispatch.py tick [--apply] [--only ID...]   one pass; acts only with --apply
    python3 src/RimMandrake/rimflow/list_dispatch.py status              the last reading
    python3 src/RimMandrake/rimflow/list_dispatch.py clear ITEM --why "..."   the Conductor lifts a stop: one more run

Per open list item that carries an outcome check (step 1, list_effect.py), raised items first (`rimflow raise`), then
oldest item that another waits on, then oldest filing, one decision:
  close           the check holds (work already done): closed as the pipeline's act; nothing launches
  blind | no_effect  the check is unmeasured | the item has no check
  adopt           no check, but its ## verify names an existing *_accept.py: attached as `cmd:python3 <path>` (seen
                  failing by the step-1 gate); nothing launches on that tick
  shape           no check and no route, and due for Shape (list_shape.due: named, or filed after shape_from and older
                  than shape_grace_h): one Shape run (opus, the brief roles/list_shape.md), through every gate below. It
                  shapes the item and, when the item is small, does its work in the same run. A `large` Shape run is not
                  counted as a Work run. A Shape run that left neither check nor route reads stopped. A due item whose
                  acceptance script was refused or is too heavy to adopt also reads shape
  routed          a part routed to judge, owner, conductor or review and not yet answered (with or without a check):
                  nothing launches; the party that answers shapes the item again (list_shape.py)
  live            a detached run is live on it
  waits_on | blocked | waiting | reshape   it waits on an open item | is blocked | has a dated wait ahead | its dated
                  wait passed and the check fails on an old item that nobody named (a date never launches old work). A due
                  item with no check whose wait passed reads shape. A lane item (named, or filed after shape_from) whose
                  wait passed gets one second look: a Work run, opus, inside max_runs_per_item
  mod_work        its home is mod:<folder>, or every repo path it names is inside one mod's folder (mod_work.of): it
                  waits for that mod's Maturation Pipeline run; no check runs, nothing is adopted, closed or launched.
                  A home that cannot be read reads blind ("could not look")
  held | off      its mod is held by the owner | a `pipe off` (all, family:list_dispatch, family:detached, item, mod)
  stopped         a run ended on its own merits and the check fails with no named next act, or after max_runs_per_item
                  such runs, or a launch refused for its form: a Needs Conductor line, once
  system_wait     the last run died of a cause outside the work, or max_never_started launches in a row never started:
                  nothing is spent (failure_class), the next launch waits SYSTEM_WAIT_S
  disabled | pipeline_paused | account_hold | chain_stop | machine_load | slots_full | pool_full   the gates
                  machine_load: the larger of the 1 and 5 minute load averages is at or over machine_load_per_core times
                  the cores: nothing launches on this machine, own slots included (a host with room still takes it); a
                  load or core count that cannot be read is said on the row (load_could_not_look) and the launch goes on
                  slots_full: the own slots are full and load plus recent and same-tick launches leaves no spare room
  launch          one detached helper (detached_helper.py launch --next-act-owner list_dispatch), sonnet when the check
                  runs a selftest or acceptance script, else opus
  in_bundle | bundled | bundle_live   work bundles (work_bundle.py, design/specs/2026-11-24-work-bundles): the launch rows
                  of one system (its home, else item:<ID>) are ONE bundle run; the first leads and takes the slot, the
                  others (and slots_full rows of that system) read bundled; a member of a live bundle reads in_bundle; a
                  ready row of a system whose bundle is live reads bundle_live; a member its bundle refused reads stopped
A run's end is read from the item: closed (done), a wait (Waiting), a `LEFT OPEN:` note (its next act: one more run),
nothing (stopped). The tick files no item.
Runs on rm-list-dispatch.timer from the dispatch clone. Reading: <RM_DISPATCHER_STATE>/list_dispatch/reading.json
(RM_LIST_DISPATCH_DIR overrides).
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import failure_class as FC  # noqa: E402
from form_fault import FORM_HEAD  # noqa: E402

ITEM = "RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST"
UNIT = "rm-list-dispatch.service"
FAMILY = "list_dispatch"
CFG_PATH = os.path.join(HERE, "list_dispatch.json")
CLOSED = ("done", "dropped", "superseded")
# after a run or launches that did not count: the danger is a launch sent again every tick into the same refusal (the
# night of 2026-11-20, maturation_dispatch.REPAIR_LAUNCH_MOST)
# budget: danger=a launch is sent again every tick into the same refusal (the night of 2026-11-20); ends no work: a wait before
# budget: the next try
SYSTEM_WAIT_S = 3600
PAC = dt.timezone(dt.timedelta(hours=-8), "PST")
ACCEPT_RX = re.compile(r"python3\s+((?:design|src)/[^\s'\"`]+?_accept\.py)\b")
WRITTEN_NOT_LANDED = 4      # a rimflow write's --publish exit: the event stands, its landing failed (ledger_landing.py)
# Hang guard (the class of call_deadline_lint.py) for one `detached_helper.py launch` (a clone sync, a fetch).
LAUNCH_TIMEOUT_S = 10800  # budget: class=launch
# Hang guard for `rimflow effect` (it runs the check once, then publishes).
EFFECT_TIMEOUT_S = 6000  # budget: danger=a hung outcome check holds the list tick; longest=584s (rm-list-effect.service, user journal, 14 days to 2026-11-24)


def load_cfg(path=CFG_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sdir(create=True):
    d = os.environ.get("RM_LIST_DISPATCH_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "list_dispatch")
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def _read(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write(p, obj):
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)


def pac(t):
    return dt.datetime.fromtimestamp(t, PAC).strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def _one(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


# ---- pure helpers ---------------------------------------------------------------------------------------------------

def order_ids(items):
    """-> item ids: raised items first in raise order (`rimflow raise`, model.raise_key), then an item another open item
    waits on, then the oldest filing, then the id."""
    return sorted(items, key=lambda i: ((items[i] or {}).get("raised") or (1, "", 0), not (items[i] or {}).get("blocks_others"),
                                        (items[i] or {}).get("filed") or 9e18, i))


def accept_script(text, exists=None):
    """-> the first existing `*_accept.py` that the item's ## verify or ## criteria runs with python3, or None."""
    exists = exists or (lambda p: os.path.isfile(os.path.join(REPO, p)))
    for sec in re.findall(r"^## (?:verify|criteria)[ \t]*\n(.*?)(?=^## |\Z)", text or "", re.M | re.S):
        for p in ACCEPT_RX.findall(sec):
            if exists(p):
                return p
    return None


def mod_of(iid, title, mods):
    """-> the first mod whose name is a word of the item's id or title, or None."""
    words = set(w.upper() for w in re.split(r"[^A-Za-z0-9]+", "%s %s" % (iid or "", title or "")) if w)
    for m in mods:
        if m and m.upper() in words:
            return m
    return None


def time_script(path, limit, runner=subprocess.run):
    """-> probe_result: value(seconds one `python3 <path>` run took from the repo root), or could_not_look(cause) when it
    did not end inside `limit` or could not start: either way it cannot be a beat's check."""
    import probe_result as PR
    t0 = time.time()
    try:
        runner(["python3", path], cwd=REPO, capture_output=True, text=True, timeout=limit, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return PR.could_not_look("it did not end inside %gs" % limit)
    except OSError as e:
        return PR.could_not_look("it could not start: %s" % e)
    return PR.value(round(time.time() - t0, 1))


def timed_accept(iid, path, events, st, limit, runner=subprocess.run):
    """-> the script's seconds, or None with the cause kept in st (over the bound, or it could not start). Measured once
    per (path, item event count, bound) and kept in st."""
    s = st.setdefault("items", {}).setdefault(iid, {})
    got = s.get("accept_timed") or {}
    if got.get("fp") != [path, events, limit]:
        r = time_script(path, limit, runner)
        got = s["accept_timed"] = {"fp": [path, events, limit], "s": r.value if r.ok else None,
                                   "why": None if r.ok else r.cause}
    return got.get("s")


def spent(attempts):
    """The lane runs that count: launched, and not ended by a cause outside the work (failure_class)."""
    return [a for a in attempts or [] if not a.get("failed") and not a.get("void")]


def chain_depth(iid, parent_of, st):
    """-> the lane runs (spent attempts) on the item's caused_by ancestors, the item itself excluded."""
    items, seen, n = (st or {}).get("items") or {}, {iid}, 0
    cur = parent_of(iid)
    while cur and cur not in seen:
        seen.add(cur)
        n += len(spent((items.get(cur) or {}).get("attempts")))
        cur = parent_of(cur)
    return n


def _shipped():
    """The shipped settings, for a key a partial cfg leaves out. An unreadable file raises: no guessed cap."""
    return load_cfg()


def pick_model(cfg, effect):
    rx = cfg.get("sonnet_if_check_regex", _shipped().get("sonnet_if_check_regex"))
    if rx and re.search(rx, effect or ""):
        return "sonnet", "the check runs a selftest or an acceptance script, which proves the fix"
    return "opus", "the check is not a test of code"


# ---- the decision ---------------------------------------------------------------------------------------------------

def slot_free(cfg, live_total, new, load, *, recent=0):
    """-> (free, why not). The lane's own max_live slots always; past them, spare room on the machine: the load average
    plus load_per_run for each recent or same-tick launch stays under load_line. None means no reading and no spare."""
    most = int(cfg.get("max_live", 2))
    if live_total < most:
        return True, None
    line = cfg.get("load_line")
    why = "%d live Workshop Pipeline runs, the lane's own slots are %d" % (live_total, most)
    if not line:
        return False, why
    if load is None:
        return False, why + "; the load average could not be read, so no spare room is counted"
    if recent is None:
        return False, why + "; recent launch records could not be read, so no spare room is counted"
    est = load + float(cfg.get("load_per_run", 0)) * (new + recent)
    if est < float(line):
        return True, None
    return False, "%s; load average %.1f plus %d recent and %d same-tick launches reaches the machine's line of %g" % (
        why, load, recent, new, float(line))


def machine_load(cfg, load, cores):
    """-> (over, why, could_not_look). The machine's own line, before any slot: load (the larger of the 1 and 5 minute
    load averages) at or over machine_load_per_core * cores launches nothing here. A load or a core count that cannot be
    read is no verdict: it is said (could_not_look) and the launch goes on, never read as 0. Pure."""
    per = cfg.get("machine_load_per_core")
    if not per:
        return False, None, None
    if load is None:
        return False, None, "the load average could not be read, so the machine_load gate did not look"
    if not cores:
        return False, None, "the core count could not be read, so the machine_load gate did not look"
    line = float(per) * int(cores)
    if float(load) >= line:
        return True, "load average %.1f on %d cores is at or over the machine's line of %g (%g per core)" % (
            float(load), int(cores), line, float(per)), None
    return False, None, None


def host_room(cfg, hosts, new=0):
    """-> (host, why not). A lane run whose own slots are full goes to a host of cfg["hosts"] that has fewer live lane
    runs (its own, plus `new` placed there this tick) than its max_live, and whose live account has more than its
    min_left_pct of the week left. A reading that is missing (None) is no room. Pure."""
    whys = []
    for name, hc in sorted((cfg.get("hosts") or {}).items()):
        f = (hosts or {}).get(name) or {}
        most, floor = int(hc.get("max_live", 0)), float(hc.get("min_left_pct", 5))
        placed = new.get(name, 0) if isinstance(new, dict) else int(new or 0)
        if f.get("live") is None:
            whys.append("%s: its live lane runs could not be read" % name)
        elif f["live"] + placed >= most:
            whys.append("%s: %d live and %d placed this tick, its max_live is %d" % (name, f["live"], placed, most))
        elif f.get("left") is None:
            whys.append("%s: what is left on its account could not be read (%s)" % (name, f.get("left_why") or "no reading"))
        elif float(f["left"]) <= floor:
            whys.append("%s: its account has %g%% of the week left, the line is %g%%" % (name, f["left"], floor))
        else:
            return name, None
    return None, "; ".join(whys) or "no host is configured"


def host_facts(cfg, live, runner=None):
    """{host: {"live", "left", "left_why"}}: live lane runs per host (from _runs), and the week left on the host's live
    account, read from account_usage's latest readings by the name the host itself reports."""
    out = {}
    for name in (cfg.get("hosts") or {}):
        d = {"live": live.get(name, 0), "left": None, "left_why": None}
        try:
            import run_host
            # every Claude run on the host counts, not only the lane runs this machine recorded (2026-11-24: 9 there
            # against max_live 6); an unread count is no room
            there = run_host.live_units(name, **({"runner": runner} if runner else {}))
            d["live"] = None if there is None else max(there, d["live"])
            import account_usage as AU
            acct = run_host.read_facts(name, "-", **({"runner": runner} if runner else {})).get("account")
            row = (AU.read_now().get("accounts") or {}).get(acct) if acct else None
            if not acct:
                d["left_why"] = "the host's live account could not be read"
            elif not row:
                d["left_why"] = "account_usage has no reading of %s" % acct
            else:
                d["left"] = AU.week_left_for(row)[0]
        except Exception as e:  # noqa: BLE001 - could not look: no room
            d["left_why"] = "%s: %s" % (type(e).__name__, e)
        out[name] = d
    return out


def load_now():
    """-> probe_result: the larger of the 1 and 5 minute load averages, or could_not_look(cause)."""
    import probe_result as PR
    try:
        return PR.value(max(os.getloadavg()[:2]))
    except OSError as e:
        return PR.could_not_look("%s" % e)


def _need(iid, it, why, smallest):
    return {"outcome": "%s: its outcome check %s still fails (%s)" % (iid, it.get("effect"), _one(it.get("out"), 160))
            if it.get("effect") else "%s: no program can close it; it has neither an outcome check nor a route" % iid,
            "why_not_recovered": why, "smallest_act": smallest}


def decide(cfg, st, facts, now, account=(True, "")):
    """-> (rows, launches). Pure over (cfg, st, facts, now, account); writes only st. One row per item, in order."""
    items = (facts or {}).get("items")
    if items is None:
        why = "the ledger could not be read; nothing launches"
        return [{"item": "-", "decision": "blind", "why": why, "could_not_look": why}], []
    sti = st.setdefault("items", {})
    runs_blind = "runs" in facts and facts["runs"] is None     # the run-record folder could not be listed
    runs = facts.get("runs") or {}
    lane = facts.get("lane_items") or items         # --only narrows `items`; the slots are the whole lane's
    live_total = sum(len((runs.get(i) or {}).get("live") or []) - len((runs.get(i) or {}).get("host_live") or [])
                     for i in lane if (lane[i] or {}).get("effect") or (lane[i] or {}).get("shape_due"))
    placed = {}     # this tick's launches per host
    paused, pool = facts.get("paused"), facts.get("pool")
    recent = facts.get("recent")
    max_runs = int(cfg.get("max_runs_per_item", 2))
    max_never = int(cfg.get("max_never_started", 2))
    rows, launches = [], []
    for iid in list(items):
        it = items[iid] or {}
        s = sti.get(iid) or {}
        att = s.get("attempts") or []
        run = runs.get(iid) or {}
        for a in att:
            if not a.get("failed") and not a.get("void") and a.get("unit") in (run.get("system") or {}):
                a.update(void=run["system"][a["unit"]], void_at=now)
        done = spent(att)
        row = {"item": iid}
        rows.append(row)

        def put(decision, why, row=row):
            row["decision"], row["why"] = decision, why
            if decision == "blind":
                row["could_not_look"] = why     # held on a reading that could not be made (blind_hold counts it)

        def stop(why, smallest, row=row, it=it, s=s, iid=iid, att=att):
            put("stopped", why)
            fp = [len(att), it.get("events")]
            if s.get("told") != fp:
                row["need"] = _need(iid, it, why, smallest)
                row["told_fp"] = fp

        if it.get("state") in CLOSED:
            put("closed", "the item is %s" % it.get("state"))
            continue
        mw = it.get("mod_work")     # mod_work.of: a mod's ticket is the Maturation Pipeline's, never the lane's
        if isinstance(mw, dict) and mw.get("unreadable"):
            put("blind", "could not look whether it is mod work: %s; nothing launches it" % mw["unreadable"])
            continue
        if isinstance(mw, dict) and mw.get("mod"):
            put("mod_work", "waits for the Maturation Pipeline run of %s (%s); the Workshop Pipeline does not work it"
                % (mw["mod"], mw.get("why") or "it is that mod's work"))
            continue
        if not cfg.get("enabled"):          # the lane's own acts all stop: no close, no adoption, no launch
            put("disabled", "list_dispatch.json has enabled: false")
            continue
        if paused:
            put("pipeline_paused", paused)
            continue
        if it.get("off_unreadable"):
            put("blind", it["off_unreadable"])
            continue
        if it.get("off"):
            put("off", it["off"])
            continue
        claimed = it.get("claimed") if not att else None     # the lease of a run of ours never stops our next run
        shape = False
        if not it.get("effect"):
            acc = it.get("accept")
            if claimed:
                put("claimed", "%s; the holder works it, so its check is not attached" % claimed)
                continue
            ref = s.get("adopt_refused") or {}
            refused = bool(acc) and ref.get("fp") == [acc, it.get("events")]
            heavy = bool(acc) and "accept_s" in it and it["accept_s"] is None
            if it.get("route"):     # routed first: no script is adopted (or said refused) past an open route
                r = it["route"]
                put("routed", "routed to %s: %s; resumes on: %s" % (r.get("who"), r.get("ask"), r.get("resumes")))
            elif (refused or heavy) and it.get("shape_due"):
                shape = True        # its script cannot be its check, so a due item gets one from Shape
            elif refused:
                put("adopt_refused", "attaching %s was refused: %s" % (acc, _one(ref.get("why"), 200)))
            elif heavy:
                put("adopt_too_heavy", "its ## verify runs %s: %s; a check runs on every beat of two timers, so it is "
                                       "not attached (a Shape run gives it a lighter check when the item is due for Shape: `rimflow "
                                       "shape %s --enter`)"
                    % (acc, it.get("accept_why") or "it did not end inside %ss" % cfg.get(
                        "max_adopt_check_s", _shipped().get("max_adopt_check_s")), iid))
            elif acc:
                put("adopt", "no outcome check; its ## verify runs %s, attached as its check this tick" % acc)
                row["accept"] = acc
            elif it.get("shape_due"):
                shape = True
            else:
                put("no_effect", "the item carries no outcome check and is not due for Shape: %s"
                    % (it.get("shape_why") or "not named"))
            if not shape:
                continue
        verdict = it.get("verdict")
        if not shape and verdict == "holds":
            ref = s.get("close_refused") or {}
            if ref.get("fp") == [it.get("effect"), it.get("events")]:
                put("close_refused", "the check holds but `rimflow close` refused: %s" % _one(ref.get("why"), 200))
            else:
                put("close", "the check holds: the work is done (%s)" % _one(it.get("out"), 160))
            continue
        if not shape and verdict != "fails":
            put("blind", "the check is unmeasured: %s" % _one(it.get("out") or verdict, 200))
            continue
        if it.get("route"):     # an open routed part holds the item: its answer re-shapes it (list_shape.py)
            r = it["route"]
            put("routed", "a part is routed to %s: %s; resumes on: %s" % (r.get("who"), r.get("ask"), r.get("resumes")))
            continue
        if runs_blind:
            put("blind", "whether a run is live on it is unknown (%s); nothing launches it" % facts.get("recent"))
            continue
        if run.get("bundle"):      # work_bundle.py: the bundle's run works it, restarts included
            put("in_bundle", "a member of the live work bundle %s; that bundle's run works it" % run["bundle"])
            continue
        if run.get("live"):
            put("live", "%s is live on it" % ", ".join(run["live"]))
            continue
        if claimed:
            put("claimed", "%s and no lane run is on it" % claimed)
            continue
        if it.get("waits_on"):
            put("waits_on", "it waits on the open item(s) %s" % ", ".join(it["waits_on"]))
            continue
        if it.get("blocked"):
            put("blocked", "the item is blocked: %s" % (it.get("blocked_reason") or "no reason given"))
            continue
        wu = it.get("wait_until")
        # a wait that passed on a lane item: one second look, unless a lane run launched since the date was that look
        since = bool(wu) and any((a.get("at") or 0) >= wu for a in done)
        look = bool(wu) and wu <= now and not shape and it.get("second_look") and not since
        if wu and not look and not (since and wu <= now):
            if wu > now:
                put("waiting", "it waits until %s: %s" % (pac(wu), it.get("wait_reason") or "no reason given"))
            elif not shape:     # a due item with no check goes on to Shape: that is the second look
                put("reshape", "its wait to %s passed and the check still fails; it is an old item that nobody named, and a "
                               "date never launches old work: name it (`rimflow shape %s --enter`) for a second look"
                    % (pac(wu), iid))
            if wu > now or not shape:
                continue
        if it.get("held"):
            put("held", it["held"])
            continue
        if att and att[-1].get("void") and now < (att[-1].get("void_at") or 0) + SYSTEM_WAIT_S:
            put("system_wait", "run %s did not count: %s; the next launch from %s" % (
                att[-1].get("unit"), _one(att[-1]["void"], 200), pac(att[-1]["void_at"] + SYSTEM_WAIT_S)))
            continue
        # A split written by a party that is no run of this item (an answered route, a hand shape) starts the count again
        # (boundary a-reshape-by-another-party-starts-the-run-count-again); the item's own run never does.
        sat = it.get("shape_at")
        own = set(a.get("unit") for a in att) | set(run.get("live") or []) | set(run.get("ended") or [])
        fresh = [a for a in done if a.get("at", 0) > sat] if sat and it.get("shape_unit") not in own else done
        # A `large` Shape run only shaped: it is not a Work run (list_shape.py; boundary a-large-shape-run-is-not-a-work-run)
        work = [a for a in fresh if not (a.get("kind") == "shape" and it.get("shape_size") == "large")]
        if done:
            last = done[-1]
            if last.get("unit") not in (run.get("ended") or []):
                put("unseen", "run %s is neither live nor seen ended in the run records; no second launch" % last.get("unit"))
                continue
            shapes = [a for a in done if a.get("kind") == "shape"]
            if shape and shapes:
                last = shapes[-1]
                stop("Shape run %s ended and the item still has neither an outcome check nor a route" % last.get("unit"),
                     "read run %s's notes on %s, then shape it by hand (`rimflow shape %s --parts ...`), drop it, or "
                     "`list_dispatch.py clear %s --why ...` for one more Shape run" % (last.get("unit"), iid, iid, iid))
                continue
        refused = run.get("bundle_refused")
        if refused and work and not shape:     # its bundle refused it, with a reason: the Conductor reads that reason
            stop("work bundle %s refused it: %s" % (refused.get("id"), _one(refused.get("why"), 300)),
                 "read the refusal on %s, then act on its reason: drop it, re-home it, or `list_dispatch.py clear %s --why "
                 "...` for one more run" % (iid, iid))
            continue
        if work and not shape:      # a Work run on an earlier, cleared check is no Shape run
            last = work[-1]
            if len(work) >= max_runs:
                stop("%d Work runs (%s) ended and the check still fails; %d is the most" % (
                    len(work), ", ".join(str(a.get("unit")) for a in work), max_runs),
                    "read the runs' notes on %s, then do the rest by hand, put a wait on it, drop it, or "
                    "`list_dispatch.py clear %s --why ...` for one more run" % (iid, iid))
                continue
            if last is done[-1] and not last.get("next") and not look and not run.get("bundle_resume"):
                stop("run %s ended with no LEFT OPEN: note (no next act of its own) and no wait, and the check still "
                     "fails" % last.get("unit"),
                     "read run %s's note on %s, then do the rest by hand, put a wait on it, drop it, or "
                     "`list_dispatch.py clear %s --why ...` for one more run" % (last.get("unit"), iid, iid))
                continue
        tail = 0
        for a in reversed(att):
            if not a.get("failed"):
                break
            tail += 1
        never = FC.of_launch(att[-1].get("failed")) if tail else None
        form = bool(tail) and FORM_HEAD in str(att[-1].get("failed"))
        if tail >= max_never and not form and not never.counts:     # it ran no work: it waits and says so, once
            due = (att[-1].get("at") or 0) + SYSTEM_WAIT_S
            if now < due:
                why = "%d launches in a row never started (%s: %s); the next from %s" % (
                    tail, never.word, _one(never.why, 200), pac(due))
                put("system_wait", why)
                fp = ["never", it.get("events")]
                if s.get("told_never") != fp:
                    row["need"] = _need(iid, it, why, "clear the cause the launch names")
                    row["told_key"], row["told_fp"] = "told_never", fp
                continue
        elif tail >= max_never:
            stop("%d launches in a row never started; the last: %s" % (tail, _one(att[-1].get("failed"), 200)),
                 "clear the cause the launch names, then `list_dispatch.py clear %s --why ...`" % iid)
            continue
        if not account[0]:
            put("account_hold", account[1] or "the account gate holds launches")
            continue
        if int(it.get("depth") or 0) >= int(cfg.get("max_chain_depth", 2)):
            put("chain_stop", "its chain of causes already holds %s lane runs; %s is the most" % (
                it.get("depth"), cfg.get("max_chain_depth", 2)))
            continue
        over, owhy, ocnl = machine_load(cfg, facts.get("load"), facts.get("cores"))
        if ocnl:
            row["load_could_not_look"] = ocnl
        if over:
            free, full = False, owhy
        else:
            free, full = slot_free(cfg, live_total, len(launches), facts.get("load"),
                                   recent=0 if recent is None else recent.value if recent.ok else None)
            if not free and recent is not None and not recent.ok:
                full += " (%s)" % recent
        host = None
        if not free:
            host, hwhy = host_room(cfg, facts.get("hosts"), placed)
            if not host and over:
                put("machine_load", owhy + "; nothing launches on this machine" + (
                    "; no host has room: " + hwhy if cfg.get("hosts") else ""))
                continue
            if not host:
                put("slots_full", full + ("; no host has room: " + hwhy if cfg.get("hosts") else ""))
                if cfg.get("load_line") and (facts.get("load") is None or (recent is not None and not recent.ok)):
                    # no spare room was counted only because a reading could not be made, not because the room is used
                    row["could_not_look"] = ("the load average could not be read" if facts.get("load") is None
                                             else recent.cause)
                continue
        if pool and not it.get("clone_exists"):
            put("pool_full", pool)
            continue
        if shape:
            model, mwhy = "opus", "a Shape run is a judgement, and does the work too when the item is small"
        elif look:
            model, mwhy = "opus", "a second look is a judgement"
        else:
            model, mwhy = pick_model(cfg, it.get("effect"))
        cap = cfg.get("%s_cap_usd" % model, _shipped().get("%s_cap_usd" % model))   # a partial cfg keeps the shipped cap
        if not (isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0):
            put("no_cap", "list_dispatch.json has no positive %s_cap_usd; nothing launches without a cap" % model)
            continue
        if host:
            placed[host] = placed.get(host, 0) + 1
            row["host"] = host
        else:
            live_total += 1
        if shape:
            row.update(model=model, cap=cap, run_n=1, kind="shape")
            put("shape", "Shape run: %s (%s); %s" % (model, mwhy, it.get("shape_why") or "due for Shape"))
        else:
            row.update(model=model, cap=cap, run_n=len(work) + 1)
            if look:
                row["look"] = it.get("wait_reason") or "no reason given"
            put("launch", "Work run %d%s: %s (%s); the check fails: %s" % (
                len(work) + 1, ", a second look (its wait to %s passed)" % pac(wu) if look else "", model, mwhy,
                _one(it.get("out"), 120)))
        if host:
            row["why"] = "%s; on %s: the lane's own slots are full (%s)" % (row.get("why", ""), host, full)
        if ocnl:
            row["why"] = "%s; machine load: could not look (%s)" % (row.get("why", ""), ocnl)
        launches.append(iid)
    if facts.get("systems") is not None:     # work_bundle.py: one bundle per system, the first launch row leads it
        import work_bundle as WB
        rows, launches = WB.group(rows, launches, facts["systems"], facts.get("bundles_live") or {})
    return rows, launches


# ---- what is true now -----------------------------------------------------------------------------------------------

def _mods():
    out = []
    try:
        import control as C
        out += C.known_mods()
    except Exception:  # noqa: BLE001 - no mod list: the hold file below still names the held ones
        pass
    try:
        import mod_owner_hold as MOH
        out += [m for m in MOH.load() if m not in out]
    except Exception:  # noqa: BLE001
        pass
    return sorted(set(out), key=lambda m: (-len(m), m))


def _held(mod):
    if not mod:
        return None
    import mod_owner_hold as MOH
    h = MOH.held(mod)
    if not h:
        return None
    return "HELD BY OWNER: %s (%s): %s" % (mod, h.get("date") or "-", _one(h.get("said"), 120))


def _off(iid, mod):
    """-> (why it is off or None, could-not-look text or None)."""
    import control as C
    try:
        for fam in (FAMILY, "detached"):
            why = C.blocked({"family": fam, "item": iid, "mod": mod})
            if why:
                return why, None
    except Exception as e:  # noqa: BLE001 - could not look is never "nothing is off"
        return None, "the control store could not be read (%s: %s)" % (type(e).__name__, e)
    return None, None


def _pool():
    try:
        import scratch_clone as SC
        return SC.pool_admit(SC.pool_root() / "list-dispatch-probe.det")
    except Exception as e:  # noqa: BLE001 - a pool that cannot be read admits no new clone
        return "the clone pool could not be read (%s: %s)" % (type(e).__name__, e)


def _clone_exists(iid):
    import detached_helper as DH
    return os.path.isdir(os.path.join(DH.pool_root(), "clones", iid + ".det"))


def _could_be_recent(path, now, lag):
    """-> None when the record file at `path` was last written `lag` or more seconds before `now`, so the launch it holds
    cannot be inside the lag (a record is written at launch, and only rewritten later); else the cause why it may be."""
    try:
        age = now - os.stat(path).st_mtime
    except OSError as e:
        return "its file time could not be read (%s: %s)" % (type(e).__name__, e)
    return None if age >= lag else "it was written %d s ago, inside the %d s lag" % (max(age, 0), lag)


def _runs(ids, now, lag, hosts=None, unread_old=None):
    """-> ({item: {"live", "ended", "system"?}}, probe_result of the recent lane launches). hosts: filled with {host:
    live lane runs there}; such runs stay live on their item, and take no own slot. An unreadable record blinds
    the recent count only when it could hold a recent launch (_could_be_recent); an older one goes to `unread_old`
    (a list) and changes no answer. A folder that cannot be listed blinds the count."""
    import detached_helper as DH
    import probe_result as PR
    out, unreadable, recent = {}, [], 0
    hosts = {} if hosts is None else hosts

    def unread(name):
        p = os.path.join(DH.runs_dir(), name)
        why = _could_be_recent(p, now, lag)
        if why:
            unreadable.append("the run record %s could not be read and %s" % (p, why))
        elif unread_old is not None:
            unread_old.append(p)
    try:
        for rec in DH.all_records(unreadable=unread):
            item = rec.get("item")
            lane = rec.get("next_act_owner") == FAMILY
            if item not in ids and not lane:
                continue
            live = DH.live_status(rec) in ("launching", "running")
            if rec.get("host"):
                if live and lane:
                    hosts[rec["host"]] = hosts.get(rec["host"], 0) + 1
                if live and item in ids:
                    out.setdefault(item, {"live": [], "ended": []}).setdefault("host_live", []).append(rec["unit"])
            elif live and lane:
                at = rec.get("at")
                if type(at) not in (int, float) or not 0 < at < float("inf"):
                    unreadable.append("the run record %s has no readable launch time" % DH.record_path(rec["unit"]))
                elif 0 < now - at < lag:
                    recent += 1
            if item in ids:
                r = out.setdefault(item, {"live": [], "ended": []})
                r["live" if live else "ended"].append(rec["unit"])
                fc = FC.of_run(rec)
                if not live and not fc.counts:
                    r.setdefault("system", {})[rec["unit"]] = "%s (%s)" % (fc.word, fc.why)
    except OSError as e:     # no run is seen at all: which items have a live run is unknown too (runs None)
        return None, PR.could_not_look("the run-record folder could not be listed (%s: %s)" % (type(e).__name__, e))
    return out, PR.could_not_look(unreadable[0]) if unreadable else PR.value(recent)


def _paused(now):
    try:
        import pipeline_pause as PP
        return PP.blocks(None, now)
    except Exception as e:  # noqa: BLE001 - a pause that cannot be read is a pause
        return "the pause store could not be read (%s: %s)" % (type(e).__name__, e)


def _read_next(st, iids, runs):
    """Fill `next` on each spent attempt whose run is seen ended and not yet read: the run's LEFT OPEN: note since it
    began, or None. One ledger read, only when an attempt needs it."""
    need = [(i, a) for i in iids for a in spent(((st.get("items") or {}).get(i) or {}).get("attempts"))
            if "next" not in a and a.get("unit") in ((runs.get(i) or {}).get("ended") or [])]
    if not need:
        return
    import left_open_continue as LOC
    import model as LM
    evs = [e for e in LM.read() if e.get("id") in set(i for i, _ in need) and e.get("event") == "note"]
    for i, a in need:
        n = LOC.last_left_open(evs, i, a.get("at") or 0)
        a["next"] = str(n.get("text")) if n else None


def block_facts(world, x, now):
    """-> (the open items that x's block waits on, whether a block with no open predecessor still holds). Whether a block
    holds at all is priority.block_holds, the one rule of every offer path."""
    up = os.path.dirname(HERE)
    if up not in sys.path:
        sys.path.insert(0, up)          # priority imports only as rimflow.priority
    from rimflow import priority as PR
    if not PR.block_holds(world, x, now):
        return [], False
    waits = []
    for on in PR.block_ons(x):
        b = PR.follow(world, on)[0]
        if b is not None and b.state not in CLOSED and b.id not in waits:
            waits.append(b.id)
    return waits, not waits


def gather(st, now=None, root=None, load_lag_s=None):
    import list_effect as LE
    now = time.time() if now is None else now
    root = root or LE.check_root()
    try:
        w = LE._world()
    except Exception:  # noqa: BLE001 - the ledger could not be read: one blind row
        return {"items": None, "runs": {}, "other_live": 0}
    import model as LM
    open_ = {i: x for i, x in w.items.items() if x.state not in CLOSED}
    waited_on = set()
    for x in open_.values():
        for b in (x.blocked_on,) + tuple(x.blocked_also or ()):
            if b:
                waited_on.add(b)
    import list_shape as LS
    import mod_work as MW
    mods = _mods()
    try:
        mw_mods, mw_cause = MW.mods(), None
    except Exception as e:  # noqa: BLE001 - no mod list: every item reads "could not look", none is launched
        mw_mods, mw_cause = None, "the mod folders could not be read (%s: %s)" % (type(e).__name__, e)
    adopt_ok = os.path.isdir(LM.ITEMS)
    cfg = _shipped()
    items = {}
    for iid, x in open_.items():
        acc = None
        sf = LS.facts(x)
        sdue, swhy = LS.due(sf, cfg, now)
        if not x.effect and adopt_ok:
            p = os.path.join(LM.ITEMS, iid + ".md")
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    acc = accept_script(f.read())
        if not x.effect and not acc and not sdue and not sf["route"]:
            continue
        waits, blocked = block_facts(w, x, now)
        mw = ({"mod": None, "why": mw_cause, "unreadable": mw_cause} if mw_mods is None else
              MW.reading(x, mw_mods, LM.ITEMS))
        d = {"state": x.state, "blocked": blocked, "blocked_reason": x.blocked_reason,
             "effect": x.effect, "waits_on": waits, "events": len(x.history), "title": x.title,
             "filed": LM.epoch(x.created_at) if x.created_at else None, "blocks_others": iid in waited_on,
             "caused_by": x.caused_by, "mod_work": mw, "shape_due": sdue, "shape_why": swhy, "route": sf["route"],
             "shape_size": sf["size"], "shape_at": sf["shape_at"], "shape_unit": sf["shape_unit"],
             "raised": LM.raise_key(x) if x.raised is not None else None,
             "second_look": bool(sf["named"] or (sf["filed"] and cfg.get("shape_from")
                                                 and sf["filed"] >= LS._epoch(cfg["shape_from"])))}
        if x.state == "doing" and LM.lease_status(x, now) == "live":
            d["claimed"] = "doing under %s, whose lease is live to %s" % (x.owner, (x.lease or {}).get("expires"))
        if x.wait_until:
            try:
                d["wait_until"], d["wait_reason"] = LM.epoch(x.wait_until), x.wait_reason
            except Exception:  # noqa: BLE001 - an unreadable date is not "no wait"
                d["blocked"], d["blocked_reason"] = True, "its wait date %r cannot be read" % x.wait_until
        if acc:
            d["accept"] = acc
            if not d.get("claimed") and not (mw.get("mod") or mw.get("unreadable")):   # a mod's script is not timed
                d["accept_s"] = timed_accept(iid, acc, d["events"], st, float(_shipped().get("max_adopt_check_s")))
                d["accept_why"] = ((st.get("items") or {}).get(iid) or {}).get("accept_timed", {}).get("why")
        items[iid] = d
    ordered = {i: items[i] for i in order_ids(items)}
    on_hosts, unread_old = {}, []
    runs, recent = _runs(set(ordered), now, cfg["load_lag_s"] if load_lag_s is None else load_lag_s, on_hosts,
                         unread_old)
    systems, bundles_live = None, {}
    if runs is not None:
        import work_bundle as WB
        try:
            bundles = WB.all_bundles()
        except Exception as e:  # noqa: BLE001 - which items a live bundle holds is unknown: nothing launches
            runs, recent = None, PR_could_not_look("the work-bundle store could not be read (%s: %s)" % (type(e).__name__, e))
        else:
            import detached_helper as DH
            def unit_live(u):       # a record that cannot be read counts live: never a second launch on its members
                rec = DH.read_record(u)
                return rec is None or DH.live_status(rec) in ("launching", "running")
            runs = WB.overlay(runs, ordered, bundles, live=unit_live)
            bundles_live = WB.live_bundles(bundles)
            systems = {}
            for iid, d in ordered.items():
                mwd = d.get("mod_work") or {}
                if not (mwd.get("mod") or mwd.get("unreadable")):
                    systems[iid] = WB.system_of(w.items[iid], lambda it, m=mwd: m)
    _read_next(st, ordered, runs or {})
    paused = _paused(now)
    for iid, d in ordered.items():
        d["mod"] = mod_of(iid, d.get("title"), mods)
        d["off"], cnl = _off(iid, d["mod"])
        if cnl:
            d["off_unreadable"] = cnl
        mwd = d.get("mod_work") or {}
        if (not (d.get("effect") or d.get("shape_due")) or paused or d["off"] or cnl   # no check runs where the lane may not act
                or mwd.get("mod") or mwd.get("unreadable")):
            continue
        if d.get("effect"):
            d["verdict"], d["out"] = LE.run(d["effect"], root)
            if d["verdict"] != "fails":
                continue
        try:
            d["held"] = _held(d["mod"])
        except Exception as e:  # noqa: BLE001
            d["off_unreadable"] = "the owner's mod holds could not be read (%s: %s)" % (type(e).__name__, e)
        d["depth"] = chain_depth(iid, lambda i: (w.items.get(i).caused_by if w.items.get(i) else None), st)
        d["clone_exists"] = _clone_exists(iid)
    live = None if runs is None else sum(len(r["live"]) for r in runs.values())
    load = load_now()
    return {"items": ordered, "runs": runs, "other_live": 0, "paused": paused, "systems": systems,
            "bundles_live": bundles_live,
            "pool": _pool(), "live_lane": live, "load": load.value if load.ok else None, "recent": recent,
            "cores": os.cpu_count(),
            "hosts": host_facts(cfg, on_hosts), "unread_old": unread_old}


def account_gate(gate=None, drain=None, now=None):
    """-> (go, why): the switching plan's drain first (detached_helper.drain_refusal: a launch now would be refused, and
    a refusal is not the item's fault), then the Dispatcher's account pick (maturation_dispatch.account_gate)."""
    import detached_helper as DH
    import maturation_dispatch as MD
    why = (drain or DH.drain_refusal)(time.time() if now is None else now)
    if why:
        return False, why
    return (gate or MD.account_gate)()


# ---- the acts -------------------------------------------------------------------------------------------------------

def brief_text(iid, it, row):
    return """Work list item {item} (the Workshop Pipeline's Work stage, run {n} of at most 2).

Title: {title}
Its outcome check, which fails now:   {check}
What the check printed: {out}

The check is the judge of "done". The item is done when the check holds on origin/main, and not before.
{look}
Steps:
0. Start the item, before anything else:
   python3 src/RimMandrake/rimflow/cli.py start {item} --seat BENCH --why "Workshop Pipeline Work run (list_dispatch.py)" --publish
1. Read it whole: the ITEM PACKET below holds its prose, its notes and what earlier runs left. Run
   python3 src/RimMandrake/rimflow/cli.py show {item}
   only for a part that the packet left out or could not read, or when this brief holds no packet.
2. Do the work the item asks for. The need is what the item says, not only the check's text: a check that you can pass
   while the need stays unmet is wrong, and you say so in a note instead of passing it.
3. Run the check in your clone until it reads holds:
   python3 src/RimMandrake/rimflow/list_effect.py check '{check}'
4. Land with ./publish -m "{item}: <what>" <explicit paths>, then close:
   python3 src/RimMandrake/rimflow/cli.py close {item} --sha <published sha> --seat BENCH --why "Workshop Pipeline: the check holds at <sha>" --publish
   (an operational item also takes its --live promise).
5. If you cannot finish, end with exactly one of these on the item, and nothing else:
   - a note whose text starts `LEFT OPEN:` and names the ONE next act that a second run of yours would do. The lane gives
     the item at most one more run, and only on that note.
   - a dated wait (`cli.py wait {item} --until <YYYY-MM-DD> --reason "<who acts next and on what>"`) when the next act is
     someone else's (the owner's, the Conductor's, a date).
   Do not file a new item for your own next step.
""".format(item=iid, n=row.get("run_n", 1), title=it.get("title") or "-", check=it.get("effect"),
           out=_one(it.get("out"), 600) or "(nothing)",
           look=LOOK % _one(row["look"], 400) if row.get("look") else "")


LOOK = """
This run is a second look. The item had a dated wait, the date passed, and the check still fails. The wait was for: %s
First find if that thing happened, and if the work is still worth the touch (CLAUDE.md, Touching code has a cost). Not
worth it: drop the item with the reason. Already done by other work: close it with that sha. Not happened yet, and only
someone else can make it happen: put a new dated wait that names who and what. Otherwise do the work now.
"""


def PR_could_not_look(cause):
    import probe_result as PR
    return PR.could_not_look(cause)


def launch(item, model, cap, brief, seat, mod, host=None, env=None):
    d = os.path.join(sdir(), "briefs")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%s-%d.md" % (item, int(time.time())))
    with open(path, "w", encoding="utf-8") as f:
        f.write(brief)
    argv = [sys.executable, os.path.join(HERE, "detached_helper.py"), "launch", "--by-program", "list_dispatch", "--seat", seat, "--item", item,
            "--brief-file", path, "--model", model, "--budget-usd", "%g" % cap, "--next-act-owner", FAMILY]
    if mod:
        argv += ["--env", "RM_CONTROL_MOD=%s" % mod]
    if host:
        argv += ["--host", host]
    for k, v in sorted((env or {}).items()):
        argv += ["--env", "%s=%s" % (k, v)]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=LAUNCH_TIMEOUT_S, stdin=subprocess.DEVNULL)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    m = re.search(r"^DETACHED (\S+)", r.stdout or "", re.M)
    return r.returncode, out, (m.group(1) if m and not r.returncode else None)


def attach(iid, check, why):
    """`rimflow effect <iid> --check <check> --publish` as the pipeline's act. -> (rc, output)."""
    argv = [sys.executable, os.path.join(HERE, "cli.py"), "effect", iid, "--check", check, "--seat", "BENCH",
            "--why", why, "--publish"]
    env = dict(os.environ, RM_ROLE_UNIT=os.environ.get("RM_ROLE_UNIT") or UNIT, RIMFLOW_SEAT="BENCH")
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"):
        env.pop(k, None)
    try:
        r = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=EFFECT_TIMEOUT_S,
                           stdin=subprocess.DEVNULL, errors="replace")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def close(iid, text, why, publish=True):
    import list_effect as LE
    os.environ["RM_ROLE_UNIT"] = os.environ.get("RM_ROLE_UNIT") or UNIT
    return LE.close_item(iid, text, why, publish)


def conductor_need(text, now, path=None):
    """One Needs Conductor line in the Conductor log (the guards red_dispatch.conductor_need uses)."""
    import detached_helper as DH
    import doorbell
    import conductor_log_guard
    path = path or DH.conductor_log_path()
    if (os.path.abspath(path) == os.path.abspath(DH.REAL_LOG)
            and os.environ.get("RM_DISPATCHER_STATE", doorbell.DEFAULT_STATE) != doorbell.DEFAULT_STATE):
        raise RuntimeError("refusing to write the REAL conductor log from a test process: " + path)
    conductor_log_guard.refuse_if_test(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n%s — NEEDS CONDUCTOR (list_dispatch): %s\n" % (DH.iso(now), text))
    return path


def _need_text(n):
    return "%s | not recovered: %s | smallest act: %s" % (n["outcome"], n["why_not_recovered"], n["smallest_act"])


def execute(cfg, st, rows, launches, facts, now, fx=None):
    import list_effect as LE
    fx = fx or {}
    do_launch, do_need = fx.get("launch", launch), fx.get("need", conductor_need)
    do_close, do_attach = fx.get("close", close), fx.get("effect", attach)
    items = facts.get("items") or {}
    sti = st.setdefault("items", {})
    for row in rows:
        iid = row["item"]
        it = items.get(iid) or {}
        s = sti.setdefault(iid, {}) if iid != "-" else {}
        if row.get("need"):
            try:
                do_need(_need_text(row["need"]), now)
                s[row.pop("told_key", "told")] = row.pop("told_fp")
            except Exception as e:  # noqa: BLE001 - the line stays owed and is said on the row
                row["need_failed"] = "%s: %s" % (type(e).__name__, e)
        if row["decision"] == "close":
            text = "outcome check holds (list_dispatch, before a Work run): %s | output: %s" % (
                it.get("effect"), _one(it.get("out"), 400) or "(none)")
            rc, said = do_close(iid, text, "pipeline act (list_dispatch tick, %s): the item's outcome check holds" % UNIT)
            if rc in (0, WRITTEN_NOT_LANDED):
                row["decision"] = "closed_by_check"
                if rc:
                    row["why"] = "closed; the event is written, not landed yet: %s" % _one(said, 200)
            elif rc in (LE.LIVE_WAIT, LE.LIVE_BLIND):
                row.update(decision="blind" if rc == LE.LIVE_BLIND else "close_refused", why=_one(said, 600))
                if rc == LE.LIVE_BLIND:
                    row["could_not_look"] = row["why"]
            else:
                s["close_refused"] = {"fp": [it.get("effect"), it.get("events")], "why": _one(said, 600), "at": now}
                row.update(decision="close_refused", why=_one(said, 300))
            continue
        if row["decision"] == "adopt":
            rc, said = do_attach(iid, "cmd:python3 %s" % row["accept"],
                                 "pipeline act (list_dispatch tick, %s): its ## verify runs this acceptance script" % UNIT)
            if rc in (0, WRITTEN_NOT_LANDED):
                row["decision"] = "adopted"
                if rc:
                    row["why"] = "attached; the event is written, not landed yet: %s" % _one(said, 200)
            else:
                s["adopt_refused"] = {"fp": [row["accept"], it.get("events")], "why": _one(said, 600), "at": now}
                row.update(decision="adopt_refused", why=_one(said, 300))
            continue
        if iid not in launches:
            continue
        if row.get("bundle"):       # work_bundle.py: one run for every ready member of the system
            launch_bundle_row(cfg, st, row, items, now, do_launch)
            continue
        if row.get("kind") == "shape":
            import list_shape as LS
            brief = LS.brief_text(iid, it, row)
        else:
            brief = brief_text(iid, it, row)
        rc, text, unit = do_launch(iid, row["model"], row["cap"], brief, cfg.get("seat", "BENCH"), it.get("mod"),
                                   **({"host": row["host"]} if row.get("host") else {}))
        ok = rc == 0 and bool(unit)
        s.pop("told", None)
        s.setdefault("attempts", []).append({"at": now, "unit": unit, "model": row["model"], "cap": row["cap"],
                                             **({"host": row["host"]} if row.get("host") else {}),
                                             "kind": row.get("kind") or "work",
                                             "failed": None if ok else "never started: " + (_one(text, 400) or "rc %s" % rc)})
        if ok:
            row.update(decision="launched", unit=unit)
        else:
            row.update(decision="launch_failed", why=_one(text, 300) or "rc %s" % rc)


def launch_bundle_row(cfg, st, row, items, now, do_launch):
    """A lead row launches its system's bundle (work_bundle.launch_bundle writes the record first). Each member gets the
    same attempt, so its own run count and stop rule read the bundle's run. Opus for a bundle of more than one (design
    section 5); a bundle of one keeps the row's model."""
    import work_bundle as WB
    b = row["bundle"]
    model = row["model"] if len(b["members"]) == 1 else "opus"
    cap = row["cap"] if model == row["model"] else cfg.get("opus_cap_usd", _shipped().get("opus_cap_usd"))
    mod = (items.get(b["members"][0]) or {}).get("mod")

    def launcher(rec, text):
        return do_launch(rec["lead"], model, cap, text, cfg.get("seat", "BENCH"), mod, env={WB.ENV: rec["id"]})
    rc, rec = WB.launch_bundle(b["system"], b["members"], items, "the Workshop Pipeline's ready tickets of %s (list_dispatch "
                               "tick, %s)" % (b["system"], UNIT), "workshop", now=now, launcher=launcher,
                               launched_by=UNIT)
    sti = st.setdefault("items", {})
    if rc == 2:
        row.update(decision="bundle_live", why=str(rec))
        return
    unit = (rec.get("units") or [{}])[-1].get("unit") if rc == 0 else None
    for m in b["members"]:
        s = sti.setdefault(m, {})
        s.pop("told", None)
        s.setdefault("attempts", []).append({"at": now, "unit": unit, "model": model, "cap": cap, "kind": "work",
                                             "bundle": rec["id"], "failed": None if unit else
                                             "never started: " + (_one(rec.get("launch_out"), 400) or "rc %s" % rc)})
    if unit:
        row.update(decision="launched", unit=unit, model=model, bundle_id=rec["id"],
                   why="work bundle %s of %s: %d member(s), %s" % (rec["id"], b["system"], len(b["members"]), model))
    else:
        row.update(decision="launch_failed", why=_one(rec.get("launch_out"), 300))


def tick(cfg, apply, fx=None, now=None, only=None):
    fx = fx or {}
    now = time.time() if now is None else now
    d = sdir(create=apply)
    lock = None
    if apply:
        lock = open(os.path.join(d, "tick.lock"), "w")
        fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        st = _read(os.path.join(d, "state.json"), {})     # a dry tick reads it and writes nothing
        facts = fx["facts"](st) if "facts" in fx else gather(st, now, load_lag_s=cfg.get("load_lag_s"))
        account = fx["account"]() if "account" in fx else account_gate()
        gone = []
        if only and facts.get("items") is not None:     # the Conductor's run-now: these items, every gate
            gone = [i for i in only if i not in facts["items"]]
            facts = dict(facts, lane_items=facts["items"], items={i: facts["items"][i] for i in only if i in facts["items"]})
        rows, launches = decide(cfg, st, facts, now, account)
        rows += [{"item": i, "decision": "not_found",
                  "why": "not an open item with an outcome check, an acceptance script, a route, or due for Shape"}
                 for i in gone]
        if apply:
            execute(cfg, st, rows, launches, facts, now, fx)
        else:
            for r in rows:
                r["decision"] = {"launch": "would_launch", "close": "would_close", "adopt": "would_adopt",
                                 "shape": "would_shape"}.get(
                    r["decision"], r["decision"])
                r.pop("need", None)
        counts = {}
        for r in rows:
            counts[r["decision"]] = counts.get(r["decision"], 0) + 1
        # a run-now (--only) tick sees part of the lane: it neither counts nor ends the streak; a dry tick writes nothing
        bh = blind_hold(st.get("blind_hold"), rows, now) if apply and not only else st.get("blind_hold")
        if apply and not only:
            st["blind_hold"] = bh
        rd = {"schema": 1, "blind_hold": bh, "at": now, "at_pac": pac(now), "apply": apply, "account": list(account), "counts": counts,
              "launched": [{"item": r["item"], "unit": r.get("unit"), "model": r.get("model")} for r in rows
                           if r.get("decision") == "launched"],
              "items": {r["item"]: dict({k: r.get(k) for k in ("decision", "why", "model", "unit", "need")},
                                        stage=row_stage((facts.get("items") or {}).get(r["item"]), r, now))
                        for r in rows}}
        if apply:
            _write(os.path.join(d, "state.json"), st)
            _write(os.path.join(d, "reading.json"), rd)
            with open(os.path.join(d, "ticks.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps({"at": now, "counts": counts, "launched": rd["launched"]}) + "\n")
        return rd
    finally:
        if lock:
            lock.close()


def blind_hold(prev, rows, now):
    """-> the streak of applied ticks in a row that held work on a could-not-look: {"passes": n, "since", "held": the
    count of items held this tick, "gate": decision of the first, "cause": its reading that could not be made, "items":
    the first few}. passes 0 when this tick held nothing on one. ops_watch reads it from reading.json and raises
    OPS_LIST_GATE_HOLDS_READY_WORK_ON_COULD_NOT_LOOK past its line (design/specs/2026-11-23-list-dispatch/boundary.md
    §a-gate-held-on-could-not-look-is-told)."""
    held = [r for r in rows if r.get("could_not_look")]
    if not held:
        return {"passes": 0, "held": 0, "at": now}
    prev = prev if isinstance(prev, dict) and isinstance(prev.get("passes"), int) and prev["passes"] > 0 else {}
    first = held[0]
    return {"passes": prev.get("passes", 0) + 1, "since": prev.get("since", now), "at": now, "held": len(held),
            "gate": "list_dispatch %s" % first.get("decision"), "cause": _one(first["could_not_look"], 300),
            "items": [r["item"] for r in held[:4]]}


def row_stage(it, row, now):
    """-> the Workshop Pipeline stage of one tick row, from list_pipeline.stage_of over the tick's own facts (the page calls
    the same function over the ledger, design/specs/2026-11-23-list-stage-view/boundary.md)."""
    import list_pipeline as LP
    if not it:
        return "unmeasured"         # the blind row, or an --only id that is not an item of the lane
    dec = row.get("decision")
    waits = None
    if it.get("waits_on"):
        waits = {"on": ", ".join(it["waits_on"]), "resumes": "%s closes" % " and ".join(it["waits_on"]), "until": None}
    elif it.get("wait_until"):
        waits = {"on": "a date: %s" % _one(it.get("wait_reason") or "no reason given", 90),
                 "resumes": "the date %s" % pac(it["wait_until"]), "until": it["wait_until"]}
    elif it.get("blocked"):
        waits = {"on": "a block: %s" % _one(it.get("blocked_reason") or "no reason given", 90),
                 "resumes": "the block is lifted", "until": None}
    live = dec in ("live", "launched", "claimed", "in_bundle")
    f = {"state": it.get("state"), "effect": it.get("effect"), "verdict": LP.lane_verdict(dec, bool(it.get("effect"))),
         "route": it.get("route"), "waits": waits,
         "run": ("live_work" if it.get("effect") else "live_shape") if live else None,
         "stopped": dec == "stopped", "note": "%s: %s" % (dec, _one(row.get("why"), 140)),
         "mod_work": it.get("mod_work")}
    return LP.stage_of(f, now)["stage"]


def _print(rd):
    for iid, r in rd["items"].items():
        print("%-64s %-16s %s" % (iid, r["decision"], _one(r.get("why"), 170)))
    print("list_dispatch %s at %s: %d item(s); %s" % ("tick" if rd.get("apply") else "dry tick", rd["at_pac"],
                                                     len(rd["items"]),
                                                     ", ".join("%s %d" % kv for kv in sorted(rd["counts"].items()))))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick")
    t.add_argument("--apply", action="store_true", help="act and write state; without it, a dry pass")
    t.add_argument("--only", nargs="+", metavar="ID", help="the Conductor's run-now: decide only these items (every "
                                                          "gate and slot still applies)")
    sub.add_parser("status")
    c = sub.add_parser("clear")
    c.add_argument("item")
    c.add_argument("--why", required=True)
    o = ap.parse_args(argv)
    if o.cmd == "tick":
        _print(tick(load_cfg(), o.apply, only=o.only))
        return 0
    if o.cmd == "status":
        rd = _read(os.path.join(sdir(create=False), "reading.json"), None)
        if not rd:
            print("UNMEASURED: no reading yet at %s" % os.path.join(sdir(create=False), "reading.json"))
            return 2
        _print(rd)
        return 0
    p = os.path.join(sdir(), "state.json")
    st = _read(p, {})
    s = st.setdefault("items", {}).setdefault(o.item, {})
    s["cleared"] = s.get("cleared", []) + [{"at": time.time(), "why": o.why, "attempts": s.get("attempts") or []}]
    s.pop("told", None)
    s["attempts"] = []
    _write(p, st)
    print("CLEARED %s: the next tick may launch one more run (earlier attempts kept under `cleared`)" % o.item)
    return 0


if __name__ == "__main__":
    sys.exit(main())
