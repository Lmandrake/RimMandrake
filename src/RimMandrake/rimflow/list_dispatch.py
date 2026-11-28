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
  routed          a part routed to owner, conductor or review and not yet answered (with or without a check):
                  nothing launches; the party that answers shapes the item again (list_shape.py)
  judge           a part routed to a judge: the old-work filter first (judge_facts: an ask whose every named repo path
                  is gone is stale, and reads stopped, for the Conductor), then one fresh judge run (opus, judge_brief_text)
                  through every gate below, never in a work bundle. An ask on in-game captures takes a free game
                  (game_lock.py); none free reads judge_waits_game with the games' lines, and games that could not be
                  read read blind. A judge run that ended and left its route reads stopped, by the Work run rule
  live            a detached run is live on it
  waits_game      its check is a live check (needs bridge, game-up or deploy) that exited 2: no game ran what it reads.
                  A free game of Archmagi takes it (one per row of a tick): a Work run, never in a bundle, whose brief
                  claims, deploys and releases that game; none free reads waits_game with the games' lines (no
                  could-not-look: the alarm counts it not); games that could not be read read blind
  waits_on | blocked | waiting | reshape   it waits on an open item | is blocked | has a dated wait ahead | its dated
                  wait passed and the check fails on an old item that nobody named (a date never launches old work). A due
                  item with no check whose wait passed reads shape. A lane item (named, or filed after shape_from) whose
                  wait passed gets one second look: a Work run, opus, inside max_runs_per_item. An old item that a
                  Shape split gave its check counts as named. The age line: a block
                  idle past block_idle_days whose `needs` window (game UP, a bridge free) opened block_window_min times
                  since is stale; it does not stop the lane, and an item with no check it makes due for Shape. A block
                  with no end (block_end) is stale after block_idle_days whatever its needs, where its route is open
  lane cause      a SteveDesktop lane-cause ticket that the steward holds blocked (lane_ticket.py) carries no check. Its
                  cause ended in two incidents and none is live: one Work run (opus, kind lane_cause, never in a bundle)
                  past the block, whose brief names each incident's end, alarm and recovery; a Work run since the latest
                  ended incident spends the offer, a third ended incident offers one more. One ended incident or a live
                  one reads blocked; a record that cannot be read reads blind
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
                  runs a selftest or acceptance script, else opus. A host of cfg["hosts"] (SteveDesktop) with room takes
                  it first (host_first: its runs, its account's leave line, its disk's clones, its work switch, and the
                  ticket's needs offline); Archmagi's own slots and spare load take the rest
  in_bundle | bundled | bundle_live   work bundles (work_bundle.py, design/specs/2026-11-24-work-bundles): the launch rows
                  of one system (its home, else item:<ID>) are ONE bundle run; the first leads and takes the slot, the
                  others (and slots_full rows of that system) read bundled; a member of a live bundle reads in_bundle; a
                  ready row of a system whose bundle is live reads bundle_live; a member its bundle refused reads stopped;
                  a lead whose room is a host runs its whole bundle on that host (work_bundle.launch_remote)
  onboard         the row `-onboard`: one onboarding run per home of an on class (list_dispatch.json onboard_classes)
                  that holds old tickets (no check, no route, no shaped split, older than shape_grace_h) and has no live
                  bundle, with no hand (onboard_step; work_bundle part 8; brief roles/list_onboard.md). A lead of the
                  home's bundle takes them; else the home's first Shape row leads it; else it takes room as a launch
                  does, SteveDesktop first. The row names the homes started, those not started and why, and each
                  left-out ticket with its reason. Could not look: one blind row, nothing starts
The no-home step (reading.json `old`; old_step): an applied full tick writes the rule homes of the old tickets with no
test and no home (list_home.rule_home), then names for Shape the oldest that no rule places, no_home_shape_per_day in
any 24 h, from no_home_shape_from.
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
import shlex
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
import new_machinery_review as NMR  # noqa: E402

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


def run_mod(it):
    """-> the mod a launched run is recorded on (RM_CONTROL_MOD), or None. Only mod_work's reading ties a run to a mod
    (home mod:<folder>, or every repo path inside that mod's folder). The word tie of mod_of (a word of the id or title)
    gates a launch (a stop or a hold on the mod) and never names the run's mod: a pipeline-tool ticket that names a mod
    as its example is no work on that mod, and the status page read such a run as a helper on the mod."""
    mw = (it or {}).get("mod_work")
    return mw.get("mod") if isinstance(mw, dict) and mw.get("mod") else None


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


def chain_grant(s, done):
    """-> the item's newest `cleared` record when no spent run launched after it, else None. A clear by a hand grants one
    lane run past the chain stop; the run spends it at launch (its attempt's `at` is the launch time). A launch that
    never started, or a run that did not count (void), spends nothing (boundary a-clear-grants-one-run-past-the-chain-stop)."""
    c = (s or {}).get("cleared") or []
    last = c[-1] if c and isinstance(c[-1], dict) else None
    if not last:
        return None
    return None if any((a.get("at") or 0) >= (last.get("at") or 0) for a in done) else last


def chain_depth(iid, parent_of, st, filed_by=None):
    """-> the lane runs (spent attempts) on the item's caused_by ancestors, the item itself excluded. filed_by(id) -> the
    role unit that filed the item (None: a hand): a link counts only when a lane run on the parent filed the child, so a
    child that a hand, the Conductor or another run filed ends the chain (the danger is the lane feeding itself;
    boundary a-chain-counts-only-links-that-a-lane-run-filed). filed_by None: every ancestor counts."""
    items, seen, n = (st or {}).get("items") or {}, {iid}, 0
    child, cur = iid, parent_of(iid)
    while cur and cur not in seen:
        seen.add(cur)
        par = items.get(cur) or {}
        # the runs that a clear moved under `cleared` still filed children (boundary a-clear-keeps-the-runs-in-the-chain)
        runs = spent([a for c in par.get("cleared") or [] for a in c.get("attempts") or []] + (par.get("attempts") or []))
        if filed_by is not None and filed_by(child) not in set(a.get("unit") for a in runs if a.get("unit")):
            break
        n += len(runs)
        child, cur = cur, parent_of(cur)
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


def switch_refuses(host, it):
    """-> why HOST takes no room for ticket IT, or None. A host on pipeline work only (rimflow/host_work_switch.py)
    takes no mod work: a ticket that mod_work reads as a mod's, one whose mod reading could not be made, or one that
    names a path inside a mod's folder (mod_work's "names")."""
    import host_work_switch as HWS
    sw = HWS.switched(host)
    if not sw:
        return None
    mw = it.get("mod_work") or {}
    if mw.get("unreadable"):
        return "%s: its mod could not be read (%s), and %s" % (host, mw["unreadable"], sw)
    if mw.get("mod") or it.get("mod"):
        return "%s takes no mod work (%s): %s" % (host, mw.get("mod") or it.get("mod"), sw)
    if str(it.get("home") or "").startswith("game:"):    # a game home's tickets build or fix mods, not the pipeline
        return "%s takes no game work (%s): %s" % (host, it["home"], sw)
    if mw.get("names"):     # a mod's files beside a design doc: may build that mod (measured 2026-11-27, crown shadows)
        return "%s takes no ticket that names a mod's files (%s): %s" % (host, ", ".join(mw["names"]), sw)
    return None


def host_room(cfg, hosts, new=0):
    """-> (host, why not). A host of cfg["hosts"] that has fewer live lane runs (its own, plus `new` placed there this
    tick) than its max_live, whose live account has more than its min_left_pct of the week left, whose own account gate
    lets a new run start (`gate`, run_host.host_gate: the gate the host's launcher asks; a drain there refused 27 launches
    on 2026-11-26 while the account read 50% left), and whose disk holds another helper clone (pool_more,
    rm-pool-room.timer's count, when it is a number; else the host's own pool_admit decides at launch). A reading that is
    missing (None) is no room; a facts dict with no `gate` key at all was made by no reader of it (host_facts always
    sets it). Pure."""
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
        elif "gate" in f and f["gate"] is not True:
            whys.append("%s: its own account gate %s (%s)" % (
                name, "refuses a new run" if f["gate"] is False else "could not be read", f.get("gate_why") or "no line"))
        elif isinstance(f.get("pool_more"), int) and placed >= f["pool_more"]:
            whys.append("%s: its disk holds %d more helper clone(s) and %d were placed this tick (rm-pool-room.timer)"
                        % (name, f["pool_more"], placed))
        else:
            return name, None
    return None, "; ".join(whys) or "no host is configured"


# A ticket that needs a thing only Archmagi has stays on Archmagi: its `needs` (model.NEEDS) is anything but offline
# (deploy, game-up, bridge and harvest name Archmagi's games and dumps; owner, the owner at Archmagi).
HOST_NEEDS = ("offline",)


def host_first(cfg, hosts, placed, it):
    """-> (host, why not). A ready ticket goes to a host with room first (host_room), unless its `needs` is not offline
    or the host's work switch refuses it (switch_refuses). Pure but for the switch file. Item
    RIMMANDRAKE_SEND_PIPELINE_TICKETS_TO_STEVEDESKTOP_FIRST_IT_SAT_IDLE."""
    if not cfg.get("hosts"):
        return None, None
    needs = it.get("needs") or "offline"
    if needs not in HOST_NEEDS:
        return None, "the ticket needs %s, which only Archmagi has" % needs
    host, why = host_room(cfg, hosts, placed)
    no = host and switch_refuses(host, it)
    if no:
        return None, no
    return host, why


def pool_room(host, runner=subprocess.run):
    """-> probe_result: the helper clones the host's disk still holds (rm-pool-room.timer's more_clones), or
    could_not_look(cause) (no door, the file could not be read, or its verdict is COULD_NOT_LOOK). No count is no
    verdict here: the host's own pool_admit still refuses a clone its disk cannot hold, at launch."""
    import probe_result as PR
    import run_host
    import time_budget
    target = run_host.door(host)
    if not target:
        return PR.could_not_look("no ssh door to %s" % host)
    try:
        r = runner(run_host._ssh(target, "cat ~/.local/state/rm-ssd/pool_room.json"), capture_output=True, text=True,
                   timeout=time_budget.CALL_S, stdin=subprocess.DEVNULL)
        if r.returncode:
            return PR.could_not_look("reading pool_room.json on %s exited %s" % (host, r.returncode))
        rec = json.loads(r.stdout)
    except Exception as e:  # noqa: BLE001
        return PR.could_not_look("pool_room.json on %s: %s: %s" % (host, type(e).__name__, e))
    more = rec.get("more_clones")
    if rec.get("verdict") in ("ROOM", "SHORT") and isinstance(more, int):
        return PR.value(more)
    return PR.could_not_look("pool_room.json on %s reads %s: %s" % (host, rec.get("verdict"), rec.get("why") or "-"))


def host_facts(cfg, live, runner=None):
    """{host: {"live", "left", "left_why", "pool_more", "pool_why", "gate", "gate_why"}}: live lane runs per host (from
    _runs), the week left on the host's live account, read from account_usage's latest readings by the name the host
    itself reports, the helper clones its disk still holds (pool_room), and the host's own account gate
    (run_host.host_gate)."""
    out = {}
    for name in (cfg.get("hosts") or {}):
        d = {"live": live.get(name, 0), "left": None, "left_why": None, "pool_more": None}
        try:
            import run_host
            # every Claude run on the host counts, not only the lane runs this machine recorded (2026-11-24: 9 there
            # against max_live 6); an unread count is no room
            there = run_host.live_units(name, **({"runner": runner} if runner else {}))
            d["live"] = None if there is None else max(there, d["live"])
            pr = pool_room(name, **({"runner": runner} if runner else {}))
            d["pool_more"], d["pool_why"] = (pr.value, None) if pr.ok else (None, pr.cause)
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
        try:
            import run_host
            d["gate"], d["gate_why"] = run_host.host_gate(name, **({"runner": runner} if runner else {}))
        except Exception as e:  # noqa: BLE001 - could not look: no room
            d["gate"], d["gate_why"] = None, "%s: %s" % (type(e).__name__, e)
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


def own_live(facts):
    """-> the live lane runs on this machine's own slots: runs on lane items (with a check, or due for Shape), less the
    ones on a host. --only narrows `items`; the slots are the whole lane's (lane_items)."""
    runs = (facts or {}).get("runs") or {}
    lane = (facts or {}).get("lane_items") or (facts or {}).get("items") or {}
    return sum(len((runs.get(i) or {}).get("live") or []) - len((runs.get(i) or {}).get("host_live") or [])
               for i in lane if (lane[i] or {}).get("effect") or (lane[i] or {}).get("shape_due"))


def machine_reading(cfg, facts):
    """-> {machine: its room as this tick measured it}, for the page (maturation_nonmod.machines). Archmagi: its own
    live lane runs, max_live, load, load_line and machine line; each host of cfg["hosts"]: its facts (None where they
    could not be read) with its max_live and min_left_pct. Pure."""
    per, cores = cfg.get("machine_load_per_core"), (facts or {}).get("cores")
    out = {"Archmagi": {"live": own_live(facts) if (facts or {}).get("items") is not None else None,
                        "max_live": int(cfg.get("max_live", 2)), "load": (facts or {}).get("load"),
                        "load_line": cfg.get("load_line"), "cores": cores,
                        "machine_line": float(per) * int(cores) if per and cores else None}}
    for name, hc in sorted((cfg.get("hosts") or {}).items()):
        f = ((facts or {}).get("hosts") or {}).get(name)
        out[name] = dict({"live": None, "left": None, "left_why": "the host's facts were not read", "pool_more": None},
                         **(f or {}), max_live=int(hc.get("max_live", 0)), min_left_pct=float(hc.get("min_left_pct", 5)))
    return out


# ready: it waits for room, for its home's live bundle, or for the hold; its wait counts from its first such tick
READY_ROWS = ("launch", "slots_full", "bundled", "bundle_hold", "bundle_live", "machine_load", "pool_full")


def decide(cfg, st, facts, now, account=(True, "")):
    """-> (rows, launches). Pure over (cfg, st, facts, now, account); writes only st. One row per item, in order; an
    urgent ticket's row first (work_bundle.urgent_why). The hold (work_bundle.hold_systems, design/specs/2026-11-24-work-
    bundles/boundary.md a-home-holds-until-five-or-the-hold-time): a pass on a copy of st finds the systems whose lead
    bundle waits; the real pass holds their rows before the room gates, so a held home takes no slot from another home.
    Each ready row's first ready tick is kept in st (ready_at), the start of its wait."""
    import copy
    items = (facts or {}).get("items")
    if items is not None:
        urgent = {i: d.get("urgent") for i, d in items.items() if (d or {}).get("urgent")}
        if urgent:
            facts = dict(facts, items=dict([(i, items[i]) for i in items if i in urgent]
                                           + [(i, items[i]) for i in items if i not in urgent]))
        if facts.get("systems") is not None:
            # A blind review must start in its own run, without a bundle's brief or history.
            facts = dict(facts, systems={i: s for i, s in facts["systems"].items() if not NMR.is_review(items.get(i))})
    hold, until = {}, {}
    if items is not None and facts.get("systems") is not None:
        import work_bundle as WB
        sti = (st or {}).get("items") or {}
        since = {i: (sti.get(i) or {}).get("ready_at", now) for i in items}
        urgent = {i: d.get("urgent") for i, d in items.items() if (d or {}).get("urgent")}
        hold_h = cfg.get("bundle_hold_h")
        hold_s = hold_h * 3600.0 if isinstance(hold_h, (int, float)) and not isinstance(hold_h, bool) else None
        for _n in range(len(set(facts["systems"].values())) + 1):     # each pass holds one more system at least
            rows, _l = _decide(cfg, copy.deepcopy(st), facts, now, account, hold)
            new = {s: w for s, w in WB.hold_systems(rows, since, urgent, now, hold_s, cfg.get("bundle_full_n", 5),
                                                    until=until).items() if s not in hold}
            if not new:
                break
            hold.update(new)
    rows, launches = _decide(cfg, st, facts, now, account, hold)
    for r in rows:
        if r.get("decision") == "bundle_hold":
            r["hold_until"] = until.get((facts.get("systems") or {}).get(r["item"]))     # lane_sweep: what ends it
    if items is not None:
        sti = st.setdefault("items", {})
        for r in rows:
            s = sti.get(r["item"])
            if r.get("decision") in READY_ROWS:
                sti.setdefault(r["item"], {}).setdefault("ready_at", now)
            elif s and "ready_at" in s:
                s.pop("ready_at")
    return rows, launches


def _decide(cfg, st, facts, now, account=(True, ""), hold=None):
    """-> (rows, launches): one pass of decide. hold: {system: why} of the systems whose rows wait for a larger bundle."""
    items = (facts or {}).get("items")
    if items is None:
        why = "the ledger could not be read; nothing launches"
        return [{"item": "-", "decision": "blind", "why": why, "could_not_look": why}], []
    sti = st.setdefault("items", {})
    runs_blind = "runs" in facts and facts["runs"] is None     # the run-record folder could not be listed
    runs = facts.get("runs") or {}
    live_total = own_live(facts)
    placed = {}     # this tick's launches per host
    games_taken = set()     # the games this tick's judge launches took: a second judge never takes the same one
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
            if run.get("live") or run.get("bundle"):
                row["live_run"] = True      # row_stage: a live run on it shows as Work, as list_pipeline.stage_of says
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
        shape = judge = live_game = repair = offer = False
        lc = it.get("lane_cause")       # a lane-cause ticket the steward holds blocked (lane_ticket.py): it has no check
        if lc is not None and not claimed:
            word, lwhy = _lane_ticket().offer(lc, [a.get("at") or 0 for a in done])
            if word == "offer":
                offer = True        # two incidents ended: one Work run between incidents, past the steward's block
            elif word == "could_not_look":
                put("blind", "the incident record of its lane cause could not be read (%s); nothing launches it" % lwhy)
                continue
            else:
                put("blocked", "%s; the item is blocked: %s" % (lwhy, it.get("blocked_reason") or "no reason given"))
                continue
        if not it.get("effect") and not offer:
            acc = it.get("accept")
            if claimed:
                put("claimed", "%s; the holder works it, so its check is not attached" % claimed)
                continue
            ref = s.get("adopt_refused") or {}
            refused = bool(acc) and ref.get("fp") == [acc, it.get("events")]
            heavy = bool(acc) and "accept_s" in it and it["accept_s"] is None
            if it.get("route") and it["route"].get("who") == "judge":
                judge = True        # the lane starts the judge (part 2): it goes on through the gates below
            elif it.get("route"):     # routed first: no script is adopted (or said refused) past an open route
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
            if not shape and not judge:
                continue
        verdict = it.get("verdict")
        close_fix = None    # a refused close whose repair a run can do: one close-fix run (boundary
        if not shape and not judge and verdict == "holds":  # a-refused-close-a-run-can-repair-gets-one-run)
            ref = s.get("close_refused") or {}
            live = run.get("bundle") or ", ".join(run.get("live") or [])
            if ref and live:
                put("in_bundle" if run.get("bundle") else "live", "the check holds and %s works it, so that run owns the "
                    "close that `rimflow close` refused: %s" % (live, _one(ref.get("why"), 200)))
                continue
            if ref.get("fp") != [it.get("effect"), it.get("events")]:
                put("close", "the check holds: the work is done (%s)" % _one(it.get("out"), 160))
                continue
            import list_effect as LE
            cause = LE.run_can_repair(ref.get("why"))
            fixes = [a for a in done if a.get("kind") == "close_fix"]
            if not cause:
                put("close_refused", "the check holds but `rimflow close` refused: %s" % _one(ref.get("why"), 200))
                continue
            if fixes:
                last = fixes[-1]
                stop("close-fix run %s ended and `rimflow close` still refuses (%s): %s" % (
                    last.get("unit"), cause, _one(ref.get("why"), 400)),
                    "read run %s's notes on %s, then do the repair that the refusal names by hand, drop it, or "
                    "`list_dispatch.py clear %s --why ...` for one more run" % (last.get("unit"), iid, iid))
                continue
            close_fix = ref.get("why")
        if not shape and not judge and not offer and verdict != "fails" and not close_fix:
            if run.get("bundle") or run.get("live"):    # a live run on it holds nothing back: say so, not blind
                put("in_bundle" if run.get("bundle") else "live", "its check is unmeasured (%s), but %s works it"
                    % (_one(it.get("out") or verdict, 120), "the live work bundle %s" % run["bundle"]
                       if run.get("bundle") else ", ".join(run["live"])))
                continue
            if not waits_for_game(it):
                # one item's check that cannot look: blind for its first ticks (a file or an event that lands minutes
                # later clears it), then a Work run that repairs the check (RELAPSE_MATURATION_FIX_DIED_TWICE)
                row["check_blind"] = True       # tick() counts the item's streak of these rows (blind_n)
                rp = cfg.get("blind_repair_passes", _shipped().get("blind_repair_passes"))
                n = int(s.get("blind_n") or 0) + 1      # this tick is the n-th in a row
                if not (isinstance(rp, int) and not isinstance(rp, bool) and rp > 0) or n < rp:
                    put("blind", "the check is unmeasured: %s" % _one(it.get("out") or verdict, 200))
                    continue
                repair = n
            else:
                live_game = True    # its live check cannot look: no game runs what it reads. A free game takes the work
        if it.get("route") and it["route"].get("who") == "judge":
            judge = True
        elif it.get("route"):     # an open routed part holds the item: its answer re-shapes it (list_shape.py)
            r = it["route"]
            put("routed", "a part is routed to %s: %s; resumes on: %s" % (r.get("who"), r.get("ask"), r.get("resumes")))
            continue
        jf = (it.get("judge") or {}) if judge else {}
        if judge:
            row["judge"] = True     # work_bundle.group never folds a judge row into a bundle: a judge is its own run
            if jf.get("stale"):     # the old-work filter (CLAUDE.md, Old work is filtered) comes before any launch
                stop("the judge ask is stale: %s" % jf["stale"],
                     "read the ask on %s against now, then re-shape it (`rimflow shape %s --parts ...`) or drop it"
                     % (iid, iid))
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
        if it.get("blocked") and not it.get("block_stale") and not offer:
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
        if judge:   # a judge counts only judge runs: the Work run that routed the part to a judge did its act by routing
            work = [a for a in fresh if a.get("kind") == "judge"]
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
        if work and not shape and not offer and not close_fix:  # a Work run on an earlier, cleared check is no Shape
            # run; an offer's new incident is its own reason to run, so earlier runs stop nothing; a close-fix run counts
            # only close-fix runs (above)
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
        game = None
        # a judge on captures, or a live check that no game could feed, takes a free game (CLAUDE.md, The bridge is
        # passed through one file: a stage that reads "needs the live game" while a game is free is a pipeline defect)
        if (judge and jf.get("live")) or live_game:
            need = ("the judge needs in-game captures" if judge else
                    "its live check cannot look until a game runs what it reads (%s)" % _one(it.get("out"), 160))
            games = facts.get("games")
            if not isinstance(games, list):     # None, or a could-not-look result from _games
                put("blind", "%s and whether a game is free could not be read (%s); nothing launches it"
                    % (need, getattr(games, "cause", None) or "no reading"))
                continue
            free = [g for g in games if g.get("state") == "FREE" and g.get("game") not in games_taken]
            if not free:
                put("judge_waits_game" if judge else "waits_game", "%s and no game is free: %s" % (
                    need, "; ".join("%s (taken by a launch of this tick)" % g.get("game") if g.get("game") in games_taken
                                    else str(g.get("line") or g.get("game")) for g in games) or "no game on this machine"))
                continue
            game = free[0]["game"]
        if not account[0]:
            put("account_hold", account[1] or "the account gate holds launches")
            continue
        grant = None
        if int(it.get("depth") or 0) >= int(cfg.get("max_chain_depth", 2)):
            grant = chain_grant(s, done)
            if not grant:
                spent_by = (s.get("cleared") or [{}])[-1].get("at")
                put("chain_stop", "its chain of causes already holds %s lane runs; %s is the most%s" % (
                    it.get("depth"), cfg.get("max_chain_depth", 2),
                    "; the clear of %s was spent by run %s" % (pac(spent_by), done[-1].get("unit"))
                    if spent_by and done else ""))
                continue
        hs = (facts.get("systems") or {}).get(iid)
        if hold and hs in hold and not (judge or shape or offer or game or repair or close_fix):
            put("bundle_hold", hold[hs])        # work_bundle.hold_systems: before the room gates, so it takes no slot
            continue
        over, owhy, ocnl = machine_load(cfg, facts.get("load"), facts.get("cores"))
        if ocnl:
            row["load_could_not_look"] = ocnl
        # a host with room first (boundary a-ready-ticket-goes-to-a-host-with-room-first); Archmagi takes the rest
        only = (cfg.get("archmagi_only_homes") or {}).get(it.get("home"))   # its tools are on Archmagi only
        if game:
            only = "its %s takes %s, a game of Archmagi" % ("judge" if judge else "live check", game)
        host, hwhy = host_first(cfg, facts.get("hosts"), placed, dict(it, needs="archmagi (%s)" % only) if only else it)
        if host:
            free, full = True, None
        elif over:
            free, full = False, owhy
        else:
            free, full = slot_free(cfg, live_total, len(launches), facts.get("load"),
                                   recent=0 if recent is None else recent.value if recent.ok else None)
            if not free and recent is not None and not recent.ok:
                full += " (%s)" % recent
        if not free:
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
        if pool and not it.get("clone_exists") and not host:     # Archmagi's pool: a host run makes its clone there
            put("pool_full", pool)
            continue
        if shape:
            model, mwhy = "opus", "a Shape run is a judgement, and does the work too when the item is small"
        elif offer:
            model, mwhy = "opus", "finding the cause of a lane stop is a diagnosis that no test proves"
        elif judge:
            model, mwhy = "opus", "a judge run is a judgement on work it did not make"
        elif look:
            model, mwhy = "opus", "a second look is a judgement"
        elif repair:
            model, mwhy = "opus", "the repair of a check that cannot look is a judgement"
        elif NMR.is_review(it):
            if not NMR.parse_title(it["title"])[0]:
                put("blind", "the machinery review ticket does not name its files and writer")
                continue
            model, mwhy = "opus", "new pipeline machinery gets a blind Opus review"
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
        if judge:
            if game:
                games_taken.add(game)
            row.update(model=model, cap=cap, run_n=len(work) + 1, kind="judge", **({"game": game} if game else {}))
            put("judge", "judge run %d: %s (%s); the ask: %s%s" % (
                len(work) + 1, model, mwhy, _one((it.get("route") or {}).get("ask"), 160),
                "; it takes %s for its captures" % game if game else ""))
        elif offer:
            row.update(model=model, cap=cap, run_n=len(work) + 1, kind="lane_cause", lane_cause=lc["ended"])
            put("launch", "Work run %d: %s (%s); its lane cause ended in %d incidents and no Work run is on it since the "
                          "latest (%s)" % (len(work) + 1, model, mwhy, len(lc["ended"]), _one(it.get("blocked_reason"), 100)))
        elif shape:
            row.update(model=model, cap=cap, run_n=1, kind="shape")
            put("shape", "Shape run: %s (%s); %s" % (model, mwhy, it.get("shape_why") or "due for Shape"))
        else:
            row.update(model=model, cap=cap, run_n=len(work) + 1)
            if look:
                row["look"] = it.get("wait_reason") or "no reason given"
            if it.get("blocked") and it.get("block_stale"):
                row["stale_block"] = it["block_stale"]
            if game:
                games_taken.add(game)
                row["game"] = game      # brief_text tells the run to claim it; work_bundle.group keeps it its own run
            if repair:
                row["repair_check"] = repair    # brief_text: repair the check first; work_bundle.group: its own run
            if close_fix:
                row.update(kind="close_fix", close_fix=close_fix)    # brief_text: the refusal; group: its own run
            put("launch", "Work run %d%s%s: %s (%s); %s" % (
                len(work) + 1, ", a second look (its wait to %s passed)" % pac(wu) if look else "",
                ", past a stale block" if row.get("stale_block") else "", model, mwhy,
                "its live check cannot look until a game runs what it reads (%s); it takes %s"
                % (_one(it.get("out"), 120), game) if game else
                "its check could not look on %d ticks in a row (%s); the run repairs the check" % (
                    repair, _one(it.get("out"), 120)) if repair else
                "the check holds but `rimflow close` refused (%s); the run does the repair that the refusal names" % _one(
                    close_fix, 200) if close_fix else "the check fails: %s" % _one(it.get("out"), 120)))
        if grant:
            row["chain_grant"] = grant.get("at")
            row["why"] = "%s; past the chain stop (depth %s) by the clear of %s: %s" % (
                row.get("why", ""), it.get("depth"), pac(grant.get("at")), _one(grant.get("why"), 160))
        if host:
            row["why"] = "%s; on %s: the host goes first and has room" % (row.get("why", ""), host)
        elif hwhy:
            row["why"] = "%s; on Archmagi: %s" % (row.get("why", ""), hwhy)
        if ocnl:
            row["why"] = "%s; machine load: could not look (%s)" % (row.get("why", ""), ocnl)
        launches.append(iid)
    if facts.get("systems") is not None:     # work_bundle.py: one bundle per system, the first launch row leads it
        import work_bundle as WB
        rows, launches = WB.group(rows, launches, facts["systems"], facts.get("bundles_live") or {}, facts.get("join"))
    if facts.get("onboard") is not None:     # the old tickets of each home: one onboarding run per home (onboard_step)
        room_st = {"live_total": live_total}

        def room(home=None):
            """-> (host, None) | ("", None) for Archmagi | (None, why): the room a launch row takes, through its gates.
            A home of cfg archmagi_only_homes needs Archmagi's own tools, and a home with a member that needs more
            than offline (its `needs`: a deploy, the game, a harvest) needs Archmagi's games, so neither takes a host."""
            if not cfg.get("enabled"):
                return None, "list_dispatch.json has enabled: false"
            if paused:
                return None, paused
            if not account[0]:
                return None, account[1] or "the account gate holds launches"
            only = (cfg.get("archmagi_only_homes") or {}).get(home)
            needs = (((facts.get("onboard") or {}).get("homes") or {}).get(home) or {}).get("needs") or {}
            if not only and needs:
                only = "; ".join("%s needs %s" % kv for kv in sorted(needs.items()))
            host, hwhy = host_first(cfg, facts.get("hosts"), placed,
                                    {"home": home, "needs": "archmagi (%s)" % only if only else "offline"})
            if host:
                placed[host] = placed.get(host, 0) + 1
                return host, None
            over, owhy, _cnl = machine_load(cfg, facts.get("load"), facts.get("cores"))
            no_host = ("; no host has room: " + hwhy) if hwhy else ""
            if over:
                return None, owhy + no_host
            free, full = slot_free(cfg, room_st["live_total"], len(launches), facts.get("load"),
                                   recent=0 if recent is None else recent.value if recent.ok else None)
            if not free:
                return None, full + no_host
            if pool:
                return None, pool
            room_st["live_total"] += 1
            return "", None
        rows, launches = onboard_step(cfg, rows, launches, dict(facts["onboard"], systems=facts.get("systems") or {}),
                                      facts.get("bundles_live") or {}, room)
    return rows, launches




def onboard_step(cfg, rows, launches, ob, live, room):
    """The old tickets of each home become ONE onboarding run per home (boundary old-tickets-are-onboarded-by-home).
    ob: {"homes": work_bundle.onboard_homes(...)["homes"], "systems": {lane item: system}} or {"could_not_look"};
    live: {system: live bundle id}; room(home) -> (host, None) | ("", None) | (None, why). For each home that
    work_bundle.onboard_pick lets start, in its order: a lead bundle of the home (a ticket with a check) takes the home's
    ready old tickets; else the home's first Shape row leads the run in the room it already has; else the run takes
    room(). Other Shape rows of a started home read bundled; a Shape row of a home with a live bundle reads
    bundle_live; one of a home whose class is off stays its own Shape run. One row `-onboard` says what started, what
    did not and why, and each left-out ticket with its reason. Edits rows and launches in place. -> (rows, launches)."""
    import work_bundle as WB
    if ob.get("could_not_look"):
        why = "could not look at the old tickets by home (%s); no onboarding run starts" % ob["could_not_look"]
        rows.append({"item": "-onboard", "decision": "blind", "why": why, "could_not_look": why})
        return rows, launches
    classes = cfg.get("onboard_classes")
    if classes is None:
        classes = _shipped().get("onboard_classes") or {}
    homes, systems = ob.get("homes") or {}, ob.get("systems") or {}
    # A ticket whose own row is any hold (a live run, a lease, system_wait, chain_stop, blind ...) or launches it as work joins
    # no onboarding run: two rows under one id made execute() take the `live` row as a launch (KeyError 'model' on
    # every tick, 2026-11-26 01:10 PST). It is left out with its row's reason.
    held = {r["item"]: "%s: %s" % (r["decision"], _one(r.get("why"), 200)) for r in rows
            if r.get("decision") not in ("shape", "launch") or (r["item"] in launches and r.get("kind") != "shape")}
    if held:
        homes = {s: dict(h, members=[i for i in h.get("members") or [] if i not in held],
                         left_out=dict(h.get("left_out") or {}, **{i: "its own row holds it (%s)" % held[i]
                                                                   for i in h.get("members") or [] if i in held}))
                 for s, h in homes.items()}
    go, no = WB.onboard_pick(homes, live, classes)
    cap = cfg.get("opus_cap_usd", _shipped().get("opus_cap_usd"))
    leads = {r["bundle"]["system"]: r for r in rows if r.get("bundle") and r["item"] in launches}
    shapes = {}
    for r in rows:
        if r.get("kind") == "shape" and r["item"] in launches and systems.get(r["item"]):
            shapes.setdefault(systems[r["item"]], []).append(r)
    started = []
    # a home whose lead or Shape row already holds room starts first: it takes no new room; the rest by go's order
    for s in sorted(go, key=lambda s: (s not in leads and s not in shapes, go.index(s))):
        mem = list(homes[s]["members"])
        if s in leads:
            lead = leads[s]
            b = lead["bundle"]
            b["members"] += [i for i in mem if i not in b["members"]]
            b["onboard"] = True
            lead["why"] = "%s; it is also the onboarding run of the %d old ticket(s) of %s" % (lead.get("why", ""), len(mem), s)
        elif s in shapes:
            lead = shapes[s][0]
            ids = [lead["item"]] + [i for i in mem if i != lead["item"]]
            lead.update(kind="onboard", decision="launch", model="opus", cap=cap, run_n=1,
                        bundle=dict({"system": s, "members": ids, "onboard": True},
                                    **({"host": lead["host"]} if lead.get("host") else {})),
                        why="the onboarding run of %s: %d old ticket(s), led by this named ticket in its own room%s" % (
                            s, len(ids), "; on %s" % lead["host"] if lead.get("host") else ""))
        else:
            host, why = room(s)
            if host is None:
                no[s] = "no room: %s" % why
                continue
            lead = {"item": mem[0], "decision": "launch", "kind": "onboard", "model": "opus", "cap": cap, "run_n": 1,
                    "bundle": dict({"system": s, "members": mem, "onboard": True}, **({"host": host} if host else {})),
                    "why": "the onboarding run of %s: %d old ticket(s); on %s" % (s, len(mem), host or "Archmagi")}
            if host:
                lead["host"] = host
            rows.append(lead)
            launches.append(lead["item"])
        for r in shapes.get(s, []):
            if r is not lead:
                r.update(decision="bundled", why="joins the onboarding run of %s that %s leads this tick" % (s, lead["item"]))
                if r["item"] in launches:
                    launches.remove(r["item"])
                if r["item"] not in lead["bundle"]["members"]:
                    lead["bundle"]["members"].append(r["item"])
        started.append({"system": s, "lead": lead["item"], "members": list(lead["bundle"]["members"]),
                        "host": lead["bundle"].get("host")})
    for s, rs in shapes.items():
        if s in (live or {}):
            for r in rs:
                r.update(decision="bundle_live", why="waits for the live bundle %s of %s; it joins the next one" % (live[s], s))
                if r["item"] in launches:
                    launches.remove(r["item"])
    left = {s: dict(h["left_out"]) for s, h in homes.items() if h.get("left_out")}
    head = "; ".join("%s (%d member(s), led by %s%s)" % (x["system"], len(x["members"]), x["lead"],
                                                       ", on %s" % x["host"] if x["host"] else "") for x in started)
    nots = "; ".join("%s: %s" % kv for kv in list(no.items())[:6])
    rows.append({"item": "-onboard", "decision": "onboard",
                 "why": "onboarding runs started: %s | not started: %d home(s)%s" % (
                     head or "none", len(no), (" (" + nots + ("; ..." if len(no) > 6 else "") + ")") if no else ""),
                 "onboard": {"started": started, "not_started": no, "left_out": left,
                             "no_system": ob.get("no_system") or {}}})
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


def readiness_texts(root=None):
    """-> {mod: the text of its newest readiness list} for each advancing mod (maturation_dispatch.json `advancing`) that
    the owner does not hold. Raises when a list cannot be read (work_bundle.urgent_why then reads none: the ticket waits
    at most the hold time)."""
    import glob
    import control as C
    import pipe_off_end as POE
    root = root or POE.CONCEPTS
    out = {}
    for mod in C.known_mods(advancing_only=True):
        if _held(mod):
            continue
        files = glob.glob(os.path.join(root, mod, "version", "in_game", "readiness_*.md"))
        if files:
            newest = max(files, key=lambda p: (int((POE.VISIT_RX.search(p) or [0, 0])[1]), os.path.basename(p)))
            with open(newest, encoding="utf-8") as f:
                out[mod] = f.read()
    return out


PAUSE_KEY = "code_review_pause"
PAUSE_PREFIX = "code review is paused: "


def _pause_setting():
    """-> the pause setting of list_dispatch.json: None when the file is readable and has no such key, else {"on": bool,
    "reason": str, "id_patterns": [str]} as written. Raises when the file cannot be read or the setting is malformed: a
    pause that cannot be read is never "off" (CLAUDE.md: could not look, failed, zero and empty are four answers)."""
    with open(CFG_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise ValueError("%s holds %s, not an object" % (os.path.basename(CFG_PATH), type(raw).__name__))
    s = raw.get(PAUSE_KEY)
    if s is None:
        return None
    if not isinstance(s, dict) or not isinstance(s.get("on"), bool):
        raise ValueError("%s needs an object with a true/false `on`" % PAUSE_KEY)
    pats = s.get("id_patterns")
    if s["on"] and (not isinstance(pats, list) or not all(isinstance(p, str) for p in pats)):
        raise ValueError("%s.id_patterns must be a list of regexes" % PAUSE_KEY)
    for p in pats or []:
        re.compile(p)
    return s


def _pause_cnl(e):
    return "could not look whether code review is paused: %s (%s: %s)" % (
        os.path.basename(CFG_PATH), type(e).__name__, _one(e, 200))


def _paused_class(iid):
    """-> (why the ticket is held by the code review pause or None, could-not-look text or None). The pause holds a
    ticket whose id matches an id_pattern while `on` is true (his order of 2026-11-27: the pipeline works before
    hardening). It only reads the id: no run is stopped, and nothing is refused at filing."""
    try:
        s = _pause_setting()
        if not s or not s["on"]:
            return None, None
        if any(re.search(p, iid) for p in s["id_patterns"]):
            return PAUSE_PREFIX + (str(s.get("reason") or "no reason written")), None
    except Exception as e:  # noqa: BLE001 - could not look is never "the pause is off"
        return None, _pause_cnl(e)
    return None, None


def pause_reading(items):
    """-> the pause as the reading says it: {"on", "reason", "held"} (held: the lane's tickets that it holds), or
    {"could_not_look": text}."""
    try:
        s = _pause_setting()
    except Exception as e:  # noqa: BLE001
        return {"could_not_look": _pause_cnl(e)}
    if not s or not s["on"]:
        return {"on": False, "reason": (s or {}).get("reason"), "held": 0}
    return {"on": True, "reason": s.get("reason"),
            "held": sum(1 for d in (items or {}).values() if str((d or {}).get("off") or "").startswith(PAUSE_PREFIX))}


def set_pause(text, on, reason, key=PAUSE_KEY):
    """-> list_dispatch.json's `text` with its one `key` line (code_review_pause or game_work_pause) set on or off (and
    `reason`, when given). Every other line stays byte for byte. Raises ValueError when the file has no such line."""
    rx = re.compile(r'^(\s*"%s":\s*)(\{.*\})(,?\s*)$' % re.escape(key), re.M)
    m = rx.search(text)
    if not m:
        raise ValueError('no one-line `"%s": {"on": true, "reason": "...", ...},` in the settings file; add one' % key)
    cur = json.loads(m.group(2))
    cur["on"] = bool(on)
    if reason:
        cur["reason"] = reason
    return text[:m.start()] + m.group(1) + json.dumps(cur, ensure_ascii=False) + m.group(3) + text[m.end():]


GAME_PAUSE_KEY = "game_work_pause"
GAME_PAUSE_PREFIX = "game work is paused: "
GAME_LIFT = ('python3 src/RimMandrake/rimflow/list_dispatch.py pause game off --why "..." (the owner or the Conductor '
             'window), then ./publish src/RimMandrake/rimflow/list_dispatch.json')


def _game_pause_setting():
    """-> the game work pause of list_dispatch.json: None when the file is readable and has no such key, else {"on": bool,
    "reason": str, "advancing_mods": [str]} as written. Raises when the file cannot be read or the setting is malformed:
    a pause that cannot be read is never "off"."""
    with open(CFG_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise ValueError("%s holds %s, not an object" % (os.path.basename(CFG_PATH), type(raw).__name__))
    s = raw.get(GAME_PAUSE_KEY)
    if s is None:
        return None
    if not isinstance(s, dict) or not isinstance(s.get("on"), bool):
        raise ValueError("%s needs an object with a true/false `on`" % GAME_PAUSE_KEY)
    am = s.get("advancing_mods")
    if not isinstance(am, list) or not all(isinstance(m, str) and m for m in am):
        raise ValueError("%s.advancing_mods must be a list of mod folder names" % GAME_PAUSE_KEY)
    return s


def work_of(x, mw):
    """-> the facts `game_work` reads of one ledger item `x`: its own home, whether it holds a live promise (or its
    promise broke), and its mod reading `mw` (a mod_work.of dict, or a function that makes one when it is needed)."""
    h = getattr(x, "home", None)
    return {"home": h.get("home") if isinstance(h, dict) else None,
            "live": bool(getattr(x, "live", None) or getattr(x, "live_broken", None)), "mod_work": mw}


def game_work(iid, work, advancing):
    """-> (is game work, why). Pure. An Ops alarm item (OPS_*), a live promise item, a pipeline: or machine: home and the
    work of an advancing mod are not game work; a game: home is; else a ticket that mod_work reads as one mod's work, or
    that names a mod's files (`names`), is game work when that mod is not in `advancing`. Raises ValueError when the
    mod reading could not be made: could not look is never "not game work"."""
    home = str(work.get("home") or "")
    if str(iid).startswith("OPS_"):
        return False, "an Ops alarm item"
    if work.get("live"):
        return False, "a live promise item"
    if home.startswith(("pipeline:", "machine:")):
        return False, "its home is %s" % home
    if home.startswith("game:"):
        return True, "its home is %s" % home
    mw = work.get("mod_work")
    if not isinstance(mw, dict) or mw.get("unreadable"):
        raise ValueError("its mod reading could not be made (%s)" % (
            mw.get("unreadable") if isinstance(mw, dict) else "no mod reading was given"))
    mods = sorted(set(([mw["mod"]] if mw.get("mod") else []) + list(mw.get("names") or [])))
    other = [m for m in mods if m not in advancing]
    if other:
        return True, "%s %s, not an advancing mod (advancing: %s)" % (
            "it is the work of" if mw.get("mod") in other else "it names the files of", ", ".join(other),
            ", ".join(advancing) or "none")
    return False, ("it is the work of an advancing mod (%s)" % ", ".join(mods)) if mods else "it names no mod's files"


def _game_paused(iid, work):
    """-> (why the game work pause holds the ticket or None, could-not-look text or None). The setting is not read for
    a ticket that is never game work (an Ops alarm, a live promise, a pipeline: or machine: home), so a setting that
    cannot be read holds no pipeline repair. work: work_of's dict, or None when the caller read no facts."""
    w = work or {}
    if str(iid).startswith("OPS_") or w.get("live") or str(w.get("home") or "").startswith(("pipeline:", "machine:")):
        return None, None
    try:
        s = _game_pause_setting()
    except Exception as e:  # noqa: BLE001 - could not look is never "the pause is off"
        return None, "could not look whether game work is paused: %s (%s: %s)" % (
            os.path.basename(CFG_PATH), type(e).__name__, _one(e, 200))
    if not s or not s["on"]:
        return None, None
    try:
        if work is None:
            raise ValueError("its home and mod reading were not read")
        mw = w.get("mod_work")
        game, why = game_work(iid, dict(w, mod_work=mw() if callable(mw) else mw), s["advancing_mods"])
    except Exception as e:  # noqa: BLE001 - a ticket the pause cannot class is held, and says so
        return None, "could not look whether it is game work, so the game work pause holds it: %s: %s" % (
            type(e).__name__, _one(e, 200))
    if not game:
        return None, None
    return "%s%s; %s; lift: %s" % (GAME_PAUSE_PREFIX, s.get("reason") or "no reason written", why, GAME_LIFT), None


def game_pause_reading(items):
    """-> the game work pause as the reading says it: {"on", "reason", "advancing_mods", "held"} (held: the lane's rows
    that it holds), or {"could_not_look": text}."""
    try:
        s = _game_pause_setting()
    except Exception as e:  # noqa: BLE001
        return {"could_not_look": "could not look whether game work is paused: %s (%s: %s)" % (
            os.path.basename(CFG_PATH), type(e).__name__, _one(e, 200))}
    if not s or not s["on"]:
        return {"on": False, "reason": (s or {}).get("reason"), "advancing_mods": (s or {}).get("advancing_mods"),
                "held": 0}
    return {"on": True, "reason": s.get("reason"), "advancing_mods": s.get("advancing_mods"),
            "held": sum(1 for d in (items or {}).values()
                        if str((d or {}).get("off") or "").startswith(GAME_PAUSE_PREFIX))}


def _off(iid, mod, work=None):
    """-> (why it is off or None, could-not-look text or None). work: work_of's facts of the ticket, which the game work
    pause reads (every route of the lane passes them)."""
    import control as C
    why, cnl = _paused_class(iid)
    if why or cnl:
        return why, cnl
    why, cnl = _game_paused(iid, work)
    if why or cnl:
        return why, cnl
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


def lane_cause_facts(x, op):
    """-> the incidents of a SteveDesktop lane-cause ticket that the steward holds blocked (lane_ticket.incidents), or None
    for any other ticket. The ticket's own ledger events are the record: a steward block is one ended incident, and a
    lift is a live one (lane_ticket.py). A record that cannot be read is {"unreadable": why}, never zero incidents."""
    try:
        LT = _lane_ticket()
        if not (LT.CAUSE_ITEM.fullmatch(x.id) and x.blocked and (x.blocked_reason or "").startswith(LT.WAIT)):
            return None
        return LT.incidents(op.cause_events.get(x.id))
    except Exception as e:  # noqa: BLE001 - lane_ticket.py could not be loaded: could not look, never "no incidents"
        return {"unreadable": "%s: %s" % (type(e).__name__, e)}


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


# The age line (P-5 of the retired Producer's weekly backlog review, revived by the Conductor 2026-11-25 as a line of
# this lane; table design/RimMandrake/retired_v3_role_duties_2026-11-23.md). Measured 2026-11-24: 30 items blocked past
# 3 days, 18 of them with a `needs` window that had opened since, and no program looked at one. Only these two `needs`
# have a ledger event that opens their window; offline, deploy, harvest and owner have none, so no proxy is invented.
WINDOW_EVENTS = {"game-up": ("game", "UP", "the game came UP"), "bridge": ("bridge", "released", "a bridge went free")}


def _lane_ticket():
    """The steward's pure lane_ticket.py, loaded by path: it lives in Utils/testq, whose other modules share names with
    this folder's (schema, testq), so that folder is never put on sys.path."""
    global _LT
    if _LT is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "lane_ticket", os.path.join(REPO, "src", "RimMandrake", "Utils", "testq", "lane_ticket.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _LT = mod
    return _LT


_LT = None


class Openings(object):
    """A replay observer: each item's last own event, the times each `needs` window opened, and the events of each
    SteveDesktop lane-cause ticket (lane_ticket.incidents reads them). One pass, no reread."""

    def __init__(self):
        self.last, self.opened = {}, {k: [] for k in WINDOW_EVENTS}
        self.filed = {}     # {item: the role unit that filed it, None for a hand} (chain_depth)
        self.cause_events = {}      # {lane-cause ticket: its events, oldest first; a time that cannot be read stays as written}

    def observe(self, ev, world, ok):
        if not ok:
            return
        who = ev.get("id") or ev.get("name")
        if who and who.startswith("STEVE_LANE_UNSTICK_") and _lane_ticket().CAUSE_ITEM.fullmatch(who):
            self.cause_events.setdefault(who, []).append(
                {k: ev.get(k) for k in ("event", "ts", "reason", "text", "title") if ev.get(k) is not None})
        import model as LM
        t = LM.epoch(ev.get("ts")) if ev.get("ts") else None
        if t is None:
            return
        if ev.get("id"):
            self.last[ev["id"]] = t
        born = ev.get("id") or ev.get("name")     # an item's first event is its filing (a spawn names it in `name`)
        if born and born not in self.filed:
            self.filed[born] = ev.get("role_unit")
        for k, (verb, state, _w) in WINDOW_EVENTS.items():
            if ev.get("event") == verb and ev.get("state") == state:
                self.opened[k].append(t)


def _epoch_of(v):
    """An epoch, or an ISO time -> epoch; None when it cannot be read."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    import model as LM
    return LM.epoch(v) if v else None      # model.epoch reads an unreadable date as None; callers say so


def block_end(x):
    """-> the event that lifts a block that holds with no open predecessor, or None when it has none: the owner's act
    (kind owner), its date (kind time with a lift date), an outside event (kind external with a reason), a `needs`
    window that a ledger event opens (kind live, needs game-up or bridge). No kind (or other), item or judge with no
    open predecessor, time with no date, external with no reason and live with no window have no end."""
    kind = (getattr(x, "blocked_kind", None) or "").strip()
    if kind == "owner":
        return "the owner's act (`rimflow unblock`)"
    if kind == "time":
        lift = getattr(x, "blocked_lift_at", None)
        return ("its date %s" % lift) if lift else None
    if kind == "external":
        return "an outside event, lifted by `rimflow unblock`" if getattr(x, "blocked_reason", None) else None
    if kind == "live":
        w = WINDOW_EVENTS.get(getattr(x, "needs", None))
        return ("the age line, once %s often enough" % w[2]) if w else None
    return None


ENDLESS_END = ("its block has no end, so after %g idle days the age line takes it past the block: a lane Shape run "
               "(list_dispatch.block_age), or its mod's bundle for a mod's ticket (work_bundle.mod_members); that run "
               "types the block or lifts it")


def endless_stale(x, since, now, cfg):
    """-> why the block of `x` has no end (block_end) and sat idle block_idle_days since `since` (its last own event),
    or None. A program reads it, never a hand: list_dispatch.block_age and work_bundle.mod_members."""
    if not getattr(x, "blocked", None) or block_end(x) is not None or since is None:
        return None
    idle = (now - since) / 86400.0
    if idle < float(cfg.get("block_idle_days", 3)):
        return None
    return "its block has no end (kind %s, no `--on`, no lift date) and is idle %.1f d" % (
        getattr(x, "blocked_kind", None) or "none", idle)


def endless_route_shut(system, cfg, now):
    """-> why the route of a ticket of `system` does not take it now, or None. A mod's ticket goes to its mod's bundle,
    never a lane Shape run; a home whose class is off waits for its class; a ticket with no home waits for
    no_home_shape_from (the date the Conductor gave the lane's no-home step)."""
    kind = str(system or "").partition(":")[0]
    if kind == "mod":
        return ("one mod's work: its mod's own bundle takes it past this block (work_bundle.mod_members), never a lane "
                "Shape run")
    if kind in ("item", "cause"):
        t = _epoch_of(cfg.get("no_home_shape_from"))
        if t is None or now < t:
            return "it has no home: the lane takes such a ticket from %s (no_home_shape_from)" % (
                cfg.get("no_home_shape_from") or "a date not set yet")
        return None
    if kind and (cfg.get("onboard_classes") or {}).get(kind) == "off":
        return "its home class %s: is off in list_dispatch.json onboard_classes, so it waits for its class" % kind
    return None


def block_age(x, op, now, cfg, system=None):
    """-> (due, why). Due for Shape: a block idle past block_idle_days (since the item's last own event) whose `needs`
    window opened block_window_min times or more since; or a block with no end (block_end) idle past block_idle_days,
    whatever its needs, when the route of its system is open (endless_route_shut). Pure over (x, op, now, cfg, system)."""
    if not getattr(x, "blocked", None):
        return False, "not blocked"
    if block_end(x) is None:
        since = op.last.get(x.id)
        if since is None:
            return False, "its last own event could not be read"
        why = endless_stale(x, since, now, cfg)
        if not why:
            return False, "its block has no end; idle %.1f d of %g" % ((now - since) / 86400.0,
                                                                       float(cfg.get("block_idle_days", 3)))
        shut = endless_route_shut(system, cfg, now)
        if shut:
            return False, "%s; %s" % (why, shut)
        return True, ("%s (%s). First read the ticket against now: drop it with its reason when it is stale or wrong "
                      "(`rimflow drop %s --reason ...`). Else type the block (`rimflow block %s --kind "
                      "<owner|time|external|live> ...`, with its lift) or lift it when its reason is gone (`rimflow "
                      "unblock %s --reason ...`). When it is one mod's work, give it that mod's home (`rimflow home %s "
                      "--home mod:<folder> --reason ...`) and stop: the Maturation Pipeline works a mod"
                      % (why, _one(getattr(x, "blocked_reason", None) or "no reason given", 120), x.id, x.id, x.id, x.id))
    kind = getattr(x, "blocked_kind", None)
    if kind in ("owner", "time"):       # his word, or its own date, lifts it; a game window is never its lift event
        return False, "a block of kind %s lifts on its own event, not on a needs window" % kind
    w = WINDOW_EVENTS.get(getattr(x, "needs", None))
    if w is None:
        return False, "needs %s: no ledger event opens that window" % getattr(x, "needs", None)
    since = op.last.get(x.id)
    if since is None:
        return False, "its last own event could not be read"
    idle = (now - since) / 86400.0
    days, least = float(cfg.get("block_idle_days", 3)), int(cfg.get("block_window_min", 2))
    n = sum(1 for t in op.opened.get(x.needs, ()) if t > since)
    if idle < days or n < least:
        return False, "its block idle %.1f d; %s %d time(s) since" % (idle, w[2], n)
    reason = _one(getattr(x, "blocked_reason", None) or "no reason given", 120)
    return True, ("its block (%s) idle %.1f d; %s %d times since, so the block may be stale: read its reason against "
                  "now, and lift it (`rimflow unblock %s --reason ...`) when the reason is gone, or block it again with "
                  "today's reason. When it is one mod's work, give it that mod's home (`rimflow home %s --home "
                  "mod:<folder> --reason ...`) and stop: the Maturation Pipeline works a mod"
                  % (reason, idle, w[2], n, x.id, x.id))


# ---- the no-home step: old tickets with no test and no home (the Conductor, 2026-11-26, question 1 of
# design/specs/2026-11-26-testless-tickets/conductor_decisions.md). The applied full tick writes the rule homes
# (list_home.rule_home), then names for Shape the oldest of the tickets that no rule places, no_home_shape_per_day in
# any 24 h, from no_home_shape_from. Before this, nothing ended such a ticket: Shape takes an old ticket only when
# someone names it, and onboarding never starts an item: or cause: home (266 tickets, measured 2026-11-26).

def no_home_names(cands, cfg, named, now):
    """-> ([ids to name now], why). cands {id: filed epoch}; named {id: epoch the lane named it}. Pure."""
    frm = cfg.get("no_home_shape_from")
    if not frm:
        return [], "no_home_shape_from is not set: the lane names no old ticket with no home"
    t = _epoch_of(frm)
    if t is None:
        return [], "no_home_shape_from %r cannot be read: the lane names none" % (frm,)
    if now < t:
        return [], "the lane names old tickets with no home for Shape from %s (no_home_shape_from)" % pac(t)
    per = int(cfg.get("no_home_shape_per_day", 5))
    recent = sum(1 for v in (named or {}).values() if isinstance(v, (int, float)) and 0 <= now - v < 86400)
    order = sorted(cands, key=lambda i: (cands[i], i))
    pick = order[:max(0, per - recent)]
    return pick, "%d named in the last 24 h of %d a day; %d old ticket(s) with no home wait, oldest first" % (
        recent, per, len(order))


def no_home_cands(items, now, cfg, system, parked, off, held, leased, placed):
    """-> {id: filed epoch} of the old tickets that the lane may name for Shape: open, no test, no route, no split
    (list_shape.needs_shape_run), never named, filed before shape_from, of an item: or cause: system (no home, not one
    mod's work), not given a rule home this tick (`placed`), not parked, off, held or under a live lease. A fact that
    cannot be read keeps the ticket out. Pure over its inputs."""
    import list_shape as LS
    frm = _epoch_of(cfg.get("shape_from"))
    if frm is None:
        return {}
    out = {}
    for i in sorted(items):
        x = items[i]
        try:
            if getattr(x, "state", None) in CLOSED or i in placed:
                continue
            sf = LS.facts(x)
            if not LS.needs_shape_run(sf) or sf.get("named") or sf.get("filed") is None or sf["filed"] >= frm:
                continue
            s = system(i)
            if not s or not str(s).startswith(("item:", "cause:")):
                continue
            if parked(i) or off(i) or held(i) or leased(i):
                continue
        except Exception:  # noqa: BLE001 - a fact that cannot be read keeps this ticket out
            continue
        out[i] = sf["filed"]
    return out


def old_facts(w, open_, now, cfg, mw_mods, mw_cause, mods):
    """-> {"homes": list_home.place_rows, "cands": no_home_cands}. Raises when it could not look."""
    import list_home as LH
    import model as LM
    import mod_work as MW
    import work_bundle as WB
    if mw_mods is None:
        raise RuntimeError(mw_cause or "the mod folders could not be read")
    before = _epoch_of(cfg.get("shape_from"))
    if before is None:
        return {"homes": [], "cands": {}}
    cache = {}

    def reading(it):
        k = getattr(it, "id", None)
        if k not in cache:
            cache[k] = MW.reading(it, mw_mods, LM.ITEMS)
        return cache[k]
    homes = LH.place_rows(open_, reading, mods, before)
    placed = set(i for i, _f in homes)

    def parked(i):
        x = open_[i]
        if x.wait_until:
            t = LM.epoch(x.wait_until)
            if t is None or t > now:
                return True
        waits, blocked = block_facts(w, x, now)
        return bool(waits or blocked)

    def off(i):
        o, cnl = _off(i, mod_of(i, open_[i].title, mods), work_of(open_[i], lambda: reading(open_[i])))
        return o or cnl
    cands = no_home_cands(open_, now, cfg, system=lambda i: WB.system_of(open_[i], reading, w.items), parked=parked,
                          off=off, held=lambda i: _held(mod_of(i, open_[i].title, mods)),
                          leased=lambda i: open_[i].state == "doing" and LM.lease_status(open_[i], now) == "live",
                          placed=placed)
    return {"homes": homes, "cands": cands}


NO_HOME_WHY = ("pipeline act (list_dispatch tick): an old ticket with no test that no rule gives a home, named for Shape "
               "(the Conductor's decision of 2026-11-26, design/specs/2026-11-26-testless-tickets/conductor_decisions.md "
               "question 1)")


def write_homes(rows):
    import list_home as LH
    return LH.write_rows(rows, LH.PLACE_WHY + " (list_dispatch tick)")


def name_for_shape(iid, why):
    """`rimflow shape <iid> --enter --publish` as the pipeline's act. -> (rc, output)."""
    argv = [sys.executable, os.path.join(HERE, "cli.py"), "shape", iid, "--enter", "--seat", "BENCH", "--why", why,
            "--publish"]
    env = dict(os.environ, RM_ROLE_UNIT=os.environ.get("RM_ROLE_UNIT") or UNIT, RIMFLOW_SEAT="BENCH")
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"):
        env.pop(k, None)
    try:
        r = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=EFFECT_TIMEOUT_S,
                           stdin=subprocess.DEVNULL, errors="replace")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def old_step(cfg, st, old, now, fx=None, write=False):
    """The no-home step of one tick. -> its reading. write=False (a dry tick, a run-now tick): what it would do."""
    fx = fx or {}
    if not isinstance(old, dict):
        return None
    if old.get("could_not_look"):
        return {"could_not_look": "could not look: %s" % _one(old["could_not_look"], 300), "homed": 0, "named": []}
    homes = old.get("homes") or []
    log = dict(st.get("no_home_named") or {})
    names, why = no_home_names(old.get("cands") or {}, cfg, log, now)
    if not write:
        return {"would_home": len(homes), "would_name": names, "why": why}
    out = {"homed": 0, "named": [], "why": why}
    if homes:
        rc, said = fx.get("home", write_homes)(homes)
        if rc in (0, WRITTEN_NOT_LANDED):
            out["homed"] = len(homes)
        else:
            out["home_failed"] = _one(said, 300)
    for i in names:
        rc, said = fx.get("name", name_for_shape)(i, NO_HOME_WHY)
        if rc in (0, WRITTEN_NOT_LANDED):
            log[i] = now
            out["named"].append(i)
        else:
            out.setdefault("name_failed", {})[i] = _one(said, 200)
    st["no_home_named"] = {i: v for i, v in log.items() if isinstance(v, (int, float)) and now - v < 30 * 86400}
    return out

def join_candidates(cands, now, want, system, facts, lease, off, held, refused):
    """-> {ticket: system} of the open tickets that have no lane row (no check) and may join their system's bundle this
    tick: no live lease, no block, no wait ahead, not off, not held, not refused by a bundle or in a live one, and a
    system in `want` (the lane's own systems; so only a home that has a lead can take it) that is not item: or mod:.
    cands: {id: model.Item}; the others are functions of one ticket. A fact that cannot be read keeps the ticket out
    (it is never "ready"). Why: RIMMANDRAKE_BUNDLE_LIST_TICKETS_BY_HOME_TEN_OF_TWELVE_HELD_ONE, ten of twelve bundles of
    2026-11-25 held one ticket while the hand bundle of a home took the whole home."""
    out = {}
    for i in sorted(cands):
        x = cands[i]
        try:
            if lease(x) == "live" or refused(i):
                continue
            wu = getattr(x, "wait_until", None)
            if wu:
                import model as LM
                t = LM.epoch(wu)
                if t is None or t > now:
                    continue
            s = system(i)
            if not s or s not in want or s.startswith(("item:", "mod:")):
                continue
            waits, blocked = facts(x)
            if waits or blocked:
                continue
            o, cnl = off(i)
            if o or cnl or held(i):
                continue
            import work_bundle as WB
            if WB.age_refusal(x, None, now):   # a joiner has no check: only a newer ticket with a recorded failure joins
                continue
        except Exception:  # noqa: BLE001 - a fact that cannot be read keeps this ticket out of every bundle
            continue
        out[i] = s
    return out


def onboard_facts_safe(fn):
    """-> fn(), or {"could_not_look": cause} when it raises: an unread list is never an empty one."""
    try:
        return fn()
    except Exception as e:  # noqa: BLE001 - could not look: no onboarding run starts, and the row says so
        return {"could_not_look": "%s: %s" % (type(e).__name__, _one(e, 300))}


def onboard_facts(open_, now, cfg, systems, ordered, w, mw_mods, mw_cause, bundles, mods):
    """-> work_bundle.onboard_homes over the open old tickets of the ledger, with `items` ({id: {"title", "state"}}) for
    the brief. A ticket is left out, with its reason, under a live lease, with a wait ahead, blocked or waiting on an
    open item, `pipe off`, held by the owner, refused by a bundle since its last other event, or in a live bundle."""
    import model as LM
    import mod_work as MW
    import work_bundle as WB
    grace = float(cfg.get("shape_grace_h", 24)) * 3600
    old = {i: x for i, x in open_.items() if WB.is_old(x, now, grace)}
    ref = WB.refusals(LM.read())
    busy = {}
    for b in bundles.values():
        if b.get("state") in WB.LIVE_STATES:
            for m in b.get("members") or []:
                busy[m] = b["id"]

    def mw_of(i):
        return (ordered.get(i) or {}).get("mod_work") or (
            {"mod": None, "unreadable": mw_cause} if mw_mods is None else MW.reading(old[i], mw_mods, LM.ITEMS))

    def system(i):
        if i in (systems or {}):
            return systems[i]
        mw = mw_of(i)
        return WB.system_of(old[i], lambda it, m=mw: m, w.items)

    def left_out(i):
        x = old[i]
        if LM.lease_status(x, now) == "live" and x.state == "doing":
            return "it is under a live lease (%s)" % x.owner
        if x.wait_until:
            t = LM.epoch(x.wait_until)
            if t is None or t > now:
                return "it waits until %s: %s" % (x.wait_until, x.wait_reason or "no reason given")
        waits, blocked = block_facts(w, x, now)
        if waits:
            return "it waits on the open item(s) %s" % ", ".join(waits)
        if blocked:
            return "it is blocked: %s" % (x.blocked_reason or "no reason given")
        mod = mod_of(i, x.title, mods)
        o, cnl = _off(i, mod, work_of(x, lambda: mw_of(i)))
        if o or cnl:
            return o or cnl
        h = _held(mod)
        if h:
            return h
        if ref.get(i):
            return "a bundle refused it since its last other event: %s" % _one(ref[i], 200)
        if i in busy:
            return "it is a member of the live bundle %s" % busy[i]
        return None
    got = WB.onboard_homes(old, system, left_out)
    got["items"] = {i: {"title": old[i].title, "state": old[i].state} for h in got["homes"].values() for i in h["members"]}
    return got


def gather(st, now=None, root=None, load_lag_s=None, keep=False, run_many=None):
    import list_effect as LE
    now = time.time() if now is None else now
    root = root or LE.check_root()
    try:
        op = Openings()
        w = LE._world(observe=op.observe)
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
        stale = None
        if x.blocked and block_facts(w, x, now) == ([], True):     # a block that holds, with no open predecessor
            bmw = ({"mod": None, "why": mw_cause, "unreadable": mw_cause} if mw_mods is None else
                   MW.reading(x, mw_mods, LM.ITEMS))
            import work_bundle as WB
            bdue, bwhy = block_age(x, op, now, cfg, system=WB.system_of(x, lambda it, m=bmw: m, w.items))
            if bdue:
                stale = bwhy
                if LS.needs_shape_run(sf):     # no check, no route, no split: the age line makes it due, and an item
                    # already due by itself launches past its block now, so its Shape why names the block either way
                    sdue, swhy = True, ("%s; and %s" % (swhy, bwhy)) if sdue else bwhy
        if not x.effect and adopt_ok:
            p = os.path.join(LM.ITEMS, iid + ".md")
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    acc = accept_script(f.read())
        lane_cause = lane_cause_facts(x, op)
        if not x.effect and not acc and not sdue and not sf["route"] and lane_cause is None:
            continue
        waits, blocked = block_facts(w, x, now)
        mw = ({"mod": None, "why": mw_cause, "unreadable": mw_cause} if mw_mods is None else
              MW.reading(x, mw_mods, LM.ITEMS))
        d = {"state": x.state, "blocked": blocked, "blocked_reason": x.blocked_reason,
             "effect": x.effect, "waits_on": waits, "events": len(x.history), "title": x.title,
             "filed": LM.epoch(x.created_at) if x.created_at else None, "blocks_others": iid in waited_on,
             "caused_by": x.caused_by, "needs": getattr(x, "needs", None), "home": (getattr(x, "home", None) or {}).get("home"), "mod_work": mw, "lane_cause": lane_cause, "shape_due": sdue, "shape_why": swhy, "route": sf["route"],
             "shape_size": sf["size"], "shape_at": sf["shape_at"], "shape_unit": sf["shape_unit"],
             "raised": LM.raise_key(x) if x.raised is not None else None, "block_stale": stale,
             "live_promise": bool(getattr(x, "live", None) or getattr(x, "live_broken", None)),
             # a Shape split is a naming: the run that wrote it read the old item against now (old-work filter)
             "second_look": bool(sf["named"] or sf["shape_at"] or (sf["filed"] and cfg.get("shape_from")
                                                 and sf["filed"] >= LS._epoch(cfg["shape_from"])))}
        if x.state == "doing" and LM.lease_status(x, now) == "live":
            d["claimed"] = "doing under %s, whose lease is live to %s" % (x.owner, (x.lease or {}).get("expires"))
        if x.wait_until:
            try:
                d["wait_until"], d["wait_reason"] = LM.epoch(x.wait_until), x.wait_reason
            except Exception:  # noqa: BLE001 - an unreadable date is not "no wait"
                d["blocked"], d["blocked_reason"] = True, "its wait date %r cannot be read" % x.wait_until
        if (sf["route"] or {}).get("who") == "judge":
            d["judge"] = judge_facts(sf["route"].get("ask"), root)
        if acc:
            d["accept"] = acc
            if not d.get("claimed") and not (mw.get("mod") or mw.get("unreadable")):   # a mod's script is not timed
                d["accept_s"] = timed_accept(iid, acc, d["events"], st, float(_shipped().get("max_adopt_check_s")))
                d["accept_why"] = ((st.get("items") or {}).get(iid) or {}).get("accept_timed", {}).get("why")
        items[iid] = d
    ordered = {i: items[i] for i in order_ids(items)}
    import work_bundle as WB
    try:        # an urgent ticket never waits for a bundle (work_bundle.urgent_why)
        blocks = WB.readiness_blocks(readiness_texts())
    except Exception as e:  # noqa: BLE001 - could not look: no ticket reads urgent by BLOCKS; each waits the hold at most
        print("readiness lists: could not look (%s: %s); no ticket reads urgent by BLOCKS" % (type(e).__name__, e),
              file=sys.stderr)
        blocks = {}
    for iid, d in ordered.items():
        d["urgent"] = WB.urgent_why(iid, getattr(open_[iid], "live_broken", None), blocks)
    on_hosts, unread_old = {}, []
    runs, recent = _runs(set(ordered), now, cfg["load_lag_s"] if load_lag_s is None else load_lag_s, on_hosts,
                         unread_old)
    systems, bundles_live, join, bundles = None, {}, {}, {}
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
            try:    # a bundle launched on a host: the host's own record says when it ends (work_bundle.refresh_remote)
                WB.refresh_remote(bundles, now, events=LM.read)
            except Exception as e:  # noqa: BLE001 - a marker that cannot be refreshed stays as it was: live holds
                print("work_bundle.refresh_remote: %s: %s" % (type(e).__name__, e), file=sys.stderr)
            runs = WB.overlay(runs, ordered, bundles, live=unit_live)
            bundles_live = WB.live_bundles(bundles)
            systems = {}
            for iid, d in ordered.items():
                mwd = d.get("mod_work") or {}
                if not (mwd.get("mod") or mwd.get("unreadable")):
                    systems[iid] = WB.system_of(w.items[iid], lambda it, m=mwd: m, w.items)
            try:        # a bundle another machine launched (SteveDesktop's own store) is live by its ledger acts
                evs = LM.read()
                cands = {i: x for i, x in open_.items() if i not in ordered}
                cand_sys = {}

                def sys_of(i):
                    if i not in cand_sys:
                        x = cands[i]
                        mw = ({"mod": None, "unreadable": mw_cause} if mw_mods is None else
                              MW.reading(x, mw_mods, LM.ITEMS))
                        cand_sys[i] = WB.system_of(x, lambda it, m=mw: m, w.items)
                    return cand_sys[i]
                for s, bid in WB.cited_live(evs, now, bundles, set(systems.values())).items():
                    bundles_live.setdefault(s, bid)
                ref = WB.refusals(evs)
                busy = set(m for b in bundles.values() if b.get("state") in WB.LIVE_STATES for m in b.get("members") or [])
                join = join_candidates(cands, now, want=set(systems.values()), system=sys_of,
                                       facts=lambda x: block_facts(w, x, now), lease=lambda x: LM.lease_status(x, now),
                                       off=lambda i: _off(i, mod_of(i, cands[i].title, mods), work_of(
                                           cands[i], lambda: {"mod": None, "unreadable": mw_cause} if mw_mods is None
                                           else MW.reading(cands[i], mw_mods, LM.ITEMS))),
                                       held=lambda i: _held(mod_of(i, cands[i].title, mods)),
                                       refused=lambda i: ref.get(i) or (i in busy))
            except Exception as e:  # noqa: BLE001 - which systems a remote bundle holds is unknown: nothing launches
                runs, recent = None, PR_could_not_look("the ledger's bundle citations or the tickets that may join a "
                                                       "bundle could not be read (%s: %s)" % (type(e).__name__, e))
    if runs is None:
        onboard = {"could_not_look": "the run records or the work-bundle store could not be read (%s)" % recent}
    else:
        onboard = onboard_facts_safe(lambda: onboard_facts(
            open_, now, cfg, systems, ordered, w, mw_mods, mw_cause, bundles, mods))
    _read_next(st, ordered, runs or {})
    paused = _paused(now)
    go = []
    for iid, d in ordered.items():
        d["mod"] = mod_of(iid, d.get("title"), mods)
        d["off"], cnl = _off(iid, d["mod"], {"home": d.get("home"), "live": d.get("live_promise"),
                                             "mod_work": d.get("mod_work")})
        if cnl:
            d["off_unreadable"] = cnl
        mwd = d.get("mod_work") or {}
        # the gate facts below are read for each row that may launch: a check, due for Shape, or a judge route (whose
        # launch passes every gate too, the owner's hold and the chain depth included); no check runs where the lane may not act
        if (not (d.get("effect") or d.get("shape_due") or d.get("judge")) or paused or d["off"] or cnl
                or mwd.get("mod") or mwd.get("unreadable")):
            continue
        go.append(iid)
    # each check once, in parallel under a bound, a kept result where its reads are unchanged: the list_effect timer
    # reads the same kept results (check_once.py)
    import check_once
    ran, cstats = (run_many or check_once.run_many)([ordered[i]["effect"] for i in go if ordered[i].get("effect")],
                                                    root, world=w, write=keep)
    for iid in go:
        d = ordered[iid]
        if d.get("effect"):
            d["verdict"], d["out"] = ran.get(d["effect"]) or ("unmeasured", "the check was not run")
            if d["verdict"] != "fails" and not waits_for_game(d):     # a live check with no game may still launch
                continue
        try:
            d["held"] = _held(d["mod"])
        except Exception as e:  # noqa: BLE001
            d["off_unreadable"] = "the owner's mod holds could not be read (%s: %s)" % (type(e).__name__, e)
        d["depth"] = chain_depth(iid, lambda i: (w.items.get(i).caused_by if w.items.get(i) else None), st,
                                 filed_by=op.filed.get)
        d["clone_exists"] = _clone_exists(iid)
    live = None if runs is None else sum(len(r["live"]) for r in runs.values())
    load = load_now()
    old = onboard_facts_safe(lambda: old_facts(w, open_, now, cfg, mw_mods, mw_cause, mods))
    return {"items": ordered, "runs": runs, "other_live": 0, "paused": paused, "systems": systems,
            "pause": pause_reading(ordered), "game_pause": game_pause_reading(ordered),
            "bundles_live": bundles_live, "join": join, "onboard": onboard, "old": old,
            "pool": _pool(), "live_lane": live, "load": load.value if load.ok else None, "recent": recent,
            "cores": os.cpu_count(), "checks": cstats,
            "hosts": host_facts(cfg, on_hosts), "unread_old": unread_old,
            # which game is free, read only when a row may take one (games_wanted)
            "games": _games() if games_wanted(ordered) else []}


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
    if NMR.is_review(it) and not (row.get("close_fix") or row.get("repair_check")):
        return NMR.brief_text(iid, it)
    return """Work list item {item} (the Workshop Pipeline's Work stage, run {n} of at most 2).

Title: {title}
Its outcome check, which {now}:   {check}
What the check printed: {out}

The check is the judge of "done". The item is done when the check holds on origin/main, and not before.
{look}{stale}
Steps:
0. Start the item, before anything else:
   python3 src/RimMandrake/rimflow/cli.py start {item} --seat BENCH --why "Workshop Pipeline Work run (list_dispatch.py)" --publish
1. Read it whole: the ITEM PACKET below holds its prose, its notes and what earlier runs left. Run
   python3 src/RimMandrake/rimflow/cli.py show {item}
   only for a part that the packet left out or could not read, or when this brief holds no packet.
2. Do the work the item asks for. The need is what the item says, not only the check's text: a check that you can pass
   while the need stays unmet is wrong, and you say so in a note instead of passing it.
3. Run the check in your clone until it reads holds:
   python3 src/RimMandrake/rimflow/list_effect.py check {check_q}
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
           now="holds now (its close was refused: see below)" if row.get("close_fix") else "fails now",
               check_q=shlex.quote(it.get("effect") or ""),
           out=_one(it.get("out"), 600) or "(nothing)",
           look=LOOK % _one(row["look"], 400) if row.get("look") else "",
           stale=STALE.replace("{item}", iid) % _one(row["stale_block"], 600) if row.get("stale_block") else "") + (
        GAME % {"game": row["game"], "item": iid} if row.get("game") else "") + (
        REPAIR % {"n": row["repair_check"], "item": iid} if row.get("repair_check") else "") + (
        CLOSE_FIX % {"why": _one(row["close_fix"], 1200), "item": iid} if row.get("close_fix") else "") + _reader(it)


def lane_cause_brief_text(iid, it, row):
    """The brief of the one Work run that a lane-cause ticket gets between incidents. It names no outcome check: the ticket
    has none. It carries each ended incident: when it ended, its alarm text and its recovery."""
    inc = []
    for k, e in enumerate(row.get("lane_cause") or [], 1):
        inc.append("  incident %d, ended %s\n    alarm:    %s\n    recovery: %s" % (
            k, e.get("ended") or "-", _one(e.get("alarm"), 600) or "(no alarm text on the ticket)",
            _one(e.get("recovery"), 600) or "(no recovery note on the ticket)"))
    return """Work list item {item} (the Workshop Pipeline's Work stage, a lane-cause run, run {n}).

Title: {title}

This ticket names the cause of a SteveDesktop test-lane stop that has now come back. The steward blocks the ticket while the
lane is healthy and lifts the block when the cause returns, so no run looked for the cause between incidents. The ticket
lane offers this one run now, between incidents, while the lane is healthy. The ticket has no outcome check.

The ended incidents (the whole record of each is the ITEM PACKET below):
{inc}

Steps:
0. Start the item, before anything else:
   python3 src/RimMandrake/rimflow/cli.py start {item} --seat BENCH --why "Workshop Pipeline lane-cause run (list_dispatch.py)" --publish
1. First read the ticket against now (CLAUDE.md, Old work is filtered): when the cause is already fixed by a later commit,
   close the ticket with that sha; when it is stale or wrong, drop it with the reason. Else read the ITEM PACKET below,
   then the lane's own record of those times: steward.jsonl, tick.log and
   infrastructure/stevedesktop/RUNBOOK.md. Find what the incidents have in common, and whether the alarm was true or a
   fault of the alarm's own timing or reading.
2. Fix the cause where you find it, in this run, test first (CLAUDE.md, Touching code has a cost). Land with
   ./publish -m "{item}: <what>" <explicit paths>.
3. End with exactly one of these on the item:
   - `python3 src/RimMandrake/rimflow/cli.py close {item} --sha <published sha> --evidence "<what ran>" --seat BENCH --why
     "<why the cause is gone>" --publish`, when you fixed the cause and the fix is running (an operational fix closes
     with its --live promise).
   - a note whose text starts `LEFT OPEN:` with what you found and the ONE next act, when the cause is known and not
     fixed. The ticket stays blocked by the steward until its next incident.
   - a note with your evidence, when you found no cause. Do not close the ticket then.
""".format(item=iid, n=row.get("run_n", 1), title=it.get("title") or "-", inc="\n".join(inc) or "  (none)")


GAME = """
Its check reads a running game, and no game ran what it reads, so it exited 2 (could not look). The ticket lane saw
%(game)s free. Take it first: python3 src/RimMandrake/rimflow/game_lock.py claim %(game)s --for "live check of %(item)s"
(exit 75 or 3: it was taken since; end with `LEFT OPEN: live check: no game was free at claim`). Deploy to %(game)s the
small list of the mod that the check reads (design/concepts/<Mod>/version/small_list.json; the rimworld-deploy skill;
for ArchSmall pass --instance ArchSmall), load it, and run the check against %(game)s until it reads. Release the game
the moment the check has read: python3 src/RimMandrake/rimflow/game_lock.py release %(game)s. Never fullscreen or focus
the game, and never live-test a creature flyer's flight.
"""


CLOSE_FIX = """
Read this before the steps above, which it changes: the check HOLDS now, and the lane's `rimflow close` was refused:
  %(why)s
So the work this run does is the repair that the refusal names (a class guard test shown failing on the instance with
`rimflow guard %(item)s --test <selftest*.py>`, a criterion verified at its level, a --live promise for an operational
item, or the close's words naming each piece of a card's work), then the close with that repair. When the item was an
alarm that reopened, read the reopen's detail in the packet first: a new cause that the old check cannot see needs a
check that sees it (shape it again) and its fix. The lane rings the Conductor only if this run ends with the close still
refused.
"""


REPAIR = """
Its check could not look on %(n)s ticks of the lane in a row: it neither holds nor fails (see what it printed above). A
check that cannot look is a fault of the check or of the program that runs it, not a verdict on the work, so this run
repairs the check first. Run the check in your clone (the command of step 3). If it reads there, find why the lane's
clone could not read it (a file not yet on origin/main, a tool missing from the timer's PATH, a ledger event not yet
landed) and repair that cause. If it cannot look in your clone either, give the item a check that can look: shape it
again with the same split and that part's check repaired, python3 src/RimMandrake/rimflow/cli.py shape %(item)s --parts
'<json list>' --seat BENCH --why "repair of a check that cannot look" --publish. When every check of one form fails the
same way, repair the runner (src/RimMandrake/rimflow/list_effect.py) instead. Then do the work.
"""


# ---- the judge (RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX part 2: owner by card 2026-11-26, "Ticket lane starts
# it (Recommended)": the lane first checks that the ask is still true, then launches one fresh judge run) -------------

# A repo path an ask names: a top folder of this repo, then a path with no placeholder or glob in it.
JUDGE_PATH_RX = re.compile(r"(?<![\\w/.-])((?:design|src|infrastructure|skills|world|observed)/[^\s'\"`,;:()<>*{}\[\]]+)")
# An ask that a judge answers from captures of a running game.
JUDGE_LIVE_RX = re.compile(r"\bin-game\b|\bin game\b|\bscreenshots?\b|\bcaptures?\b|\blive game\b|\bon this build\b", re.I)


def judge_facts(ask, root):
    """-> {"stale": why or None, "live": bool}: the program's part of the old-work filter on a judge ask. Stale when the ask
    names repo paths and every one of them is gone from `root` (the thing to judge is gone); an ask that names no path,
    or one path of now, is read against now by the judge run itself (its brief's step 1). live: the ask is answered from
    in-game captures, so the run takes a free game."""
    ask = str(ask or "")
    paths = sorted(set(m.rstrip(".") for m in JUDGE_PATH_RX.findall(ask)))
    gone = [q for q in paths if not os.path.exists(os.path.join(root, q))]
    stale = ("every repo path the ask names is gone now: %s" % ", ".join(gone)) if paths and len(gone) == len(paths) else None
    return {"stale": stale, "live": bool(JUDGE_LIVE_RX.search(ask)), "paths": paths}


# A check that reads a running game (OPS_LIST_GATE_HOLDS_READY_WORK_ON_COULD_NOT_LOOK_WTHJ, outage 5, 2026-11-27): its
# item needs one of Archmagi's games (model.NEEDS) and the check exited 2, a live check's "could not look: no running
# game has what I read". Its work is a deploy and a load on a free game, not a hold. Every other unmeasured check (exit
# 127, a deadline, a missing file) stays blind: that is a fault of the check, and the alarm names it.
GAME_NEEDS = ("bridge", "game-up", "deploy")


def waits_for_game(it):
    """-> True when the item's check is a live check that could not look for lack of a game that runs what it reads."""
    it = it if isinstance(it, dict) else {}
    return (it.get("needs") in GAME_NEEDS and it.get("verdict") == "unmeasured"
            and str(it.get("out") or "").startswith("exit 2 "))


def games_wanted(ordered):
    """-> True when a row of this tick may take a game: a judge on in-game captures, or a live check that waits for a game."""
    return any((d.get("judge") or {}).get("live") or waits_for_game(d) for d in (ordered or {}).values())


def _games():
    """-> [game_lock.query] for each game of this machine, or a could-not-look result naming its cause."""
    try:
        import game_lock as GL
        return [{"game": r.get("game"), "state": r.get("state"), "line": r.get("line")} for r in GL.query_all()]
    except Exception as e:  # noqa: BLE001 - which game is free is unknown: a live judge reads blind, with the cause
        return PR_could_not_look("the games could not be read (%s: %s)" % (type(e).__name__, e))


JUDGE_ART = "design/RimMandrake/art_judge_brief.md"
JUDGE_ART_RX = re.compile(r"art_judge_brief|\bart\b|sprite|picture|texture|facing|coat|redraw|re-bake|icon|graphics", re.I)


def judge_brief_text(iid, it, row, makers=()):
    r = it.get("route") or {}
    art = bool(JUDGE_ART_RX.search(str(r.get("ask") or "")))
    game = row.get("game")
    who = ", ".join(sorted(set(m for m in makers if m))) or "the runs that made the work"
    return """Judge list item {item}: you are a fresh judge run that the Workshop Pipeline's ticket lane launched (judge run {n}).

You are not {who}: you did not make the work you judge. If you find that you made it (your own commit, your own note),
end at once with a note that says so; never judge your own work.

Title: {title}
The ask routed to a judge: {ask}
What resumes the item: {resumes}

Read first: design/RimMandrake/standing_rulings.md sections "The judge refuses flaws, not polish" and "A refusal carries its
path to pass".{art}

Steps:
0. Start the item: python3 src/RimMandrake/rimflow/cli.py start {item} --seat BENCH --why "ticket lane judge run (list_dispatch.py)" --publish
1. The old-work filter (CLAUDE.md, Old work is filtered before any process takes it): read the ask against the state of
   now (the files, the item's later notes, his later words). If his later words, a later ruling or the code of now already
   answer it, the ask is STALE: re-shape the item without that route (`python3 src/RimMandrake/rimflow/cli.py shape {item}
   --parts ...`) with the reason in --why, and end. Judge nothing that is stale.
2. Judge what the ask names, and only that. The level that is enough: a flaw that the player would see, or a broken
   promise of the ask's own brief. When to stop looking: when you can rule on each thing the ask names; do not hunt for
   more. A finding below that level is not worth the touch: write it as one line on the polish.md beside the work (the
   polish route), never a ticket. A refusal names the flaw and its path to pass.
3. Write the verdict where the ask says, with your run's name as the judge, land it with ./publish and explicit paths,
   then re-shape the item so the routed part reads your verdict (a check that a program can read), or close it when its
   check holds.
4. If you cannot finish, end with a note that starts `LEFT OPEN:` and names the one next act, or a dated wait that names
   who acts next.
{game}
Never live-test a creature flyer's flight and never try to capture images of a creature flyer's flight (CLAUDE.md, If it
flies in the fiction). A gravship on the world map is a world object, not a flyer: capturing its icon is allowed.
Change no mod, no bar and no version. Start no helper of your own.
""".format(item=iid, n=row.get("run_n", 1), who=who, title=it.get("title") or "-", ask=_one(r.get("ask"), 1200),
           resumes=_one(r.get("resumes"), 400),
           art=("\nThis is an art ask: judge against %s and the subject's canon entry; read that brief whole." % JUDGE_ART)
           if art else "",
           game=("\nThis ask is answered from in-game captures. The ticket lane saw %s free. Take it first: python3 "
                 "src/RimMandrake/rimflow/game_lock.py claim %s --for \"judge captures for %s\" (exit 75 or 3: it was taken "
                 "since; end with `LEFT OPEN: judge: no game was free at claim`). Release it the moment the captures "
                 "are taken: python3 src/RimMandrake/rimflow/game_lock.py release %s. Never fullscreen or focus the game.\n"
                 % (game, game, iid, game)) if game else "")


def _reader(it):
    """The reader part of a fresh-reader ticket's brief (fresh_reader.py), else ""."""
    import fresh_reader as FR
    return FR.brief_block(it) if FR.is_reader(it) else ""


LOOK = """
This run is a second look. The item had a dated wait, the date passed, and the check still fails. The wait was for: %s
First find if that thing happened, and if the work is still worth the touch (CLAUDE.md, Touching code has a cost). Not
worth it: drop the item with the reason. Already done by other work: close it with that sha. Not happened yet, and only
someone else can make it happen: put a new dated wait that names who and what. Otherwise do the work now.
"""

STALE = """
The item is blocked, and the block looks stale (the lane's age line): %s
First settle the block. Its reason gone: lift it (python3 src/RimMandrake/rimflow/cli.py unblock {item} --reason
"<why it is gone>" --seat BENCH --publish), then do the work. Its reason still true: block it again with today's reason,
and end with a dated wait that names who acts next.
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


def _bundle_waits(rows, facts, now=None):
    """The applied tick's step: each local live bundle's record takes the tickets that wait on it (work_bundle.waiting_of,
    note_waiting), so its next restart takes them (a-live-bundle-takes-its-homes-new-tickets-at-restart). A record that
    cannot be written is said on stderr; it never stops the tick."""
    import work_bundle as WB
    now = time.time() if now is None else now
    live = facts.get("bundles_live") or {}
    waits = WB.waiting_of(rows, facts.get("join") or {}, live)
    for bid in sorted(set(live.values())):
        try:
            WB.note_waiting(bid, waits.get(bid, []), now)
        except Exception as e:  # noqa: BLE001
            print("list_dispatch: the waiting tickets of %s not written: %s: %s" % (bid, type(e).__name__, e),
                  file=sys.stderr)


def execute(cfg, st, rows, launches, facts, now, fx=None):
    import list_effect as LE
    fx = fx or {}
    do_launch, do_need = fx.get("launch", launch), fx.get("need", conductor_need)
    do_close, do_attach = fx.get("close", close), fx.get("effect", attach)
    items = dict(((facts.get("onboard") or {}).get("items") or {}), **(facts.get("items") or {}))   # + old members' titles
    sti = st.setdefault("items", {})
    for row in rows:
        iid = row["item"]
        it = items.get(iid) or {}
        s = sti.setdefault(iid, {}) if not iid.startswith("-") else {}
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
        if iid not in launches or row["decision"] not in ("launch", "shape", "judge"):
            continue        # a second row under a launched id (a hold row) is never a launch: it has no model
        if row.get("bundle"):       # work_bundle.py: one run for every ready member of the system
            launch_bundle_row(cfg, st, row, items, now, do_launch, remote=fx.get("remote"), rows=rows)
            continue
        if row.get("kind") == "shape":
            import list_shape as LS
            brief = LS.brief_text(iid, it, row)
        elif row.get("kind") == "lane_cause":
            brief = lane_cause_brief_text(iid, it, row)
        elif row.get("kind") == "judge":
            brief = judge_brief_text(iid, it, row, makers=[a.get("unit") for a in s.get("attempts") or [] if a.get("unit")]
                                     + ([it["shape_unit"]] if it.get("shape_unit") else []))
        else:
            brief = brief_text(iid, it, row)
        rc, text, unit = do_launch(iid, row["model"], row["cap"], brief, cfg.get("seat", "BENCH"), run_mod(it),
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


def launch_bundle_row(cfg, st, row, items, now, do_launch, remote=None, rows=()):
    """A lead row launches its system's bundle (work_bundle.launch_bundle writes the record first). Each member gets the
    same attempt, so its own run count and stop rule read the bundle's run. Opus for a bundle of more than one (design
    section 5); a bundle of one keeps the row's model. A lead whose room is another host launches the whole bundle on
    that host (work_bundle.launch_remote: the host's own `./pipe bundle`, Opus, the host's own cap, so the attempt
    records no cap); only the members the host took get the attempt, and a `bundled` row the host left out reads
    `host_left_out` with the host's reason. remote: the ssh runner (a test's fake)."""
    import work_bundle as WB
    b = row["bundle"]
    model = row["model"] if len(b["members"]) == 1 and not b.get("host") else "opus"
    cap = row["cap"] if model == row["model"] else cfg.get("opus_cap_usd", _shipped().get("opus_cap_usd"))
    mod = run_mod(items.get(b["members"][0]))
    why = ("the onboarding run of the old tickets of %s, with its ready tickets (list_dispatch tick, %s)" if b.get("onboard")
           else "the Workshop Pipeline's ready tickets of %s (list_dispatch tick, %s)") % (b["system"], UNIT)
    if b.get("host"):
        rc, rec = WB.launch_remote(b["host"], b["system"], b["members"], why, "workshop", now=now,
                                   launched_by=UNIT, onboard=bool(b.get("onboard")), **({"runner": remote} if remote else {}))
    else:
        def launcher(rec, text):
            return do_launch(rec["lead"], model, cap, text, cfg.get("seat", "BENCH"), mod, env={WB.ENV: rec["id"]})
        rc, rec = WB.launch_bundle(b["system"], b["members"], items, why, "workshop", now=now, launcher=launcher,
                                   launched_by=UNIT, onboard=bool(b.get("onboard")))
    sti = st.setdefault("items", {})
    if rc == 2:
        row.update(decision="bundle_live", why=str(rec))
        return
    for r in rows:
        if r is not row and r["item"] in (rec.get("left_out") or {}):
            r.update(decision="host_left_out", why="the sort on %s left it out of the bundle: %s" % (
                b["host"], rec["left_out"][r["item"]]))
    if rc == 3:         # the host launched nothing and said why (its own live bundle, its sort closed all, a refusal)
        own = (rec.get("left_out") or {}).get(row["item"])     # the lead left out too: its own row names the host's reason
        row.update(decision=rec["decision"], why=_one(rec["launch_out"], 300) + (
            "; its own: %s" % own if own else ""))
        return
    if b.get("host"):
        cap = None
    unit = (rec.get("units") or [{}])[-1].get("unit") if rc == 0 else None
    for m in (rec.get("members") if unit else None) or b["members"]:
        s = sti.setdefault(m, {})
        s.pop("told", None)
        s.setdefault("attempts", []).append({"at": now, "unit": unit, "model": model, "cap": cap, "kind": "work",
                                             **({"host": b["host"]} if b.get("host") else {}),
                                             "bundle": rec.get("id"), "failed": None if unit else
                                             "never started: " + (_one(rec.get("launch_out"), 400) or "rc %s" % rc)})
    if unit:
        row.update(decision="launched", unit=unit, model=model, bundle_id=rec["id"],
                   why="work bundle %s of %s: %d member(s), %s%s" % (rec["id"], b["system"], len(rec["members"]), model,
                                                                    " on %s" % b["host"] if b.get("host") else ""))
    else:
        row.update(decision="launch_failed", why=_one(rec.get("launch_out"), 300))


def _held_by(p, rows, prefix):
    """-> the pause reading `p` with `held` counted from the tick's rows: a row that reads off for that pause. A ticket
    whose row another decision took first (mod_work, closed, the pipeline's pause) is not held by it (measured
    2026-11-27: four mod: tickets of mods that do not advance were counted held, though their rows read mod_work)."""
    if not isinstance(p, dict) or "held" not in p:
        return p
    return dict(p, held=sum(1 for r in rows if r.get("decision") == "off" and str(r.get("why") or "").startswith(prefix)))


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
        facts = fx["facts"](st) if "facts" in fx else gather(st, now, load_lag_s=cfg.get("load_lag_s"), keep=apply)
        account = fx["account"]() if "account" in fx else account_gate()
        gone = []
        if only and facts.get("items") is not None:     # the Conductor's run-now: these items, every gate
            gone = [i for i in only if i not in facts["items"]]
            facts = dict(facts, lane_items=facts["items"], items={i: facts["items"][i] for i in only if i in facts["items"]})
        # the Codex lane (codex_lane.py): while the Claude room is short it takes the test-proven tickets first, and
        # the Claude lane does not see them; a run-now (--only) is the Conductor's and goes to Claude
        import codex_lane as CL
        lane_facts, cx_rows = (facts, []) if only else CL.step(cfg, st, facts, now, fx, apply, account)
        rows, launches = decide(cfg, st, lane_facts, now, account)
        rows = cx_rows + rows
        try:
            old = old_step(cfg, st, facts.get("old"), now, fx, write=apply and not only)
        except Exception as e:  # noqa: BLE001 - the no-home step never stops the lane's own rows; the reading says it
            old = {"could_not_look": "could not look: the no-home step raised %s: %s" % (type(e).__name__, _one(e, 300))}
        rows += [{"item": i, "decision": "not_found",
                  "why": "not an open item with an outcome check, an acceptance script, a route, or due for Shape"}
                 for i in gone]
        if apply:
            execute(cfg, st, rows, launches, facts, now, fx)
            if not only and facts.get("systems") is not None:
                (fx.get("bundle_waits") or _bundle_waits)(rows, facts, now)
        else:
            for r in rows:
                r["decision"] = {"launch": "would_launch", "close": "would_close", "adopt": "would_adopt",
                                 "shape": "would_shape", "judge": "would_judge"}.get(
                    r["decision"], r["decision"])
                r.pop("need", None)
        counts = {}
        for r in rows:
            counts[r["decision"]] = counts.get(r["decision"], 0) + 1
        # since: when each item took its decision (conductor_stops reads a stop's age from it); a decision that changes,
        # even for one tick, starts again. Only a full applied tick writes it.
        ks_old, ks = st.get("kind_since") or {}, {}
        for r in rows:
            prev = ks_old.get(r["item"])
            ks[r["item"]] = [r["decision"], prev[1] if isinstance(prev, list) and len(prev) == 2
                             and prev[0] == r["decision"] and isinstance(prev[1], (int, float)) else now]
        if apply and not only:
            st["kind_since"] = ks
            # each item's streak of ticks whose check could not look (decide reads blind_n); a launch, or any other
            # reading of the check, ends it. A dry or run-now tick neither counts nor ends it, as blind_hold
            sti = st.setdefault("items", {})
            for r in rows:
                if r.get("check_blind") and r.get("decision") != "launched":
                    sti.setdefault(r["item"], {})["blind_n"] = int((sti.get(r["item"]) or {}).get("blind_n") or 0) + 1
                elif r["item"] in sti:
                    sti[r["item"]].pop("blind_n", None)
        # a run-now (--only) tick sees part of the lane: it neither counts nor ends the streak; a dry tick writes nothing
        bh = blind_hold(st.get("blind_hold"), rows, now) if apply and not only else st.get("blind_hold")
        if apply and not only:
            st["blind_hold"] = bh
        rd = {"schema": 1, "blind_hold": bh, "at": now, "at_pac": pac(now), "apply": apply, "account": list(account), "counts": counts,
              "old": old, "pause": _held_by(facts.get("pause"), rows, PAUSE_PREFIX),
              "game_pause": _held_by(facts.get("game_pause"), rows, GAME_PAUSE_PREFIX),
              "checks": facts.get("checks"),       # the outcome checks' batch (check_once.run_many)
              "machines": machine_reading(cfg, facts),
              "launched": [{"item": r["item"], "unit": r.get("unit"), "model": r.get("model")} for r in rows
                           if r.get("decision") == "launched"],
              "items": {r["item"]: dict({k: r.get(k) for k in ("decision", "why", "model", "unit", "need", "hold_until")
                                         + (("onboard",) if r.get("onboard") else ())},
                                        stage=row_stage((facts.get("items") or {}).get(r["item"]), r, now),
                                        since=ks[r["item"]][1], **_mod_fields((facts.get("items") or {}).get(r["item"]), r))
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


def _mod_fields(it, row):
    """A mod_work row names its mod and the ticket's own dated wait (conductor_stops: a resting mod's tickets)."""
    if row.get("decision") != "mod_work" or not isinstance(it, dict):
        return {}
    mw = it.get("mod_work") if isinstance(it.get("mod_work"), dict) else {}
    return {"mod": mw.get("mod"), "wait_until": it.get("wait_until")}


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
    live = dec in ("live", "launched", "claimed", "in_bundle") or bool(row.get("live_run"))
    f = {"state": it.get("state"), "effect": it.get("effect"), "verdict": LP.lane_verdict(dec, bool(it.get("effect"))),
         "route": it.get("route"), "waits": waits,
         "run": ("live_work" if it.get("effect") else "live_shape") if live else None,
         "stopped": dec == "stopped", "note": "%s: %s" % (dec, _one(row.get("why"), 140)),
         "mod_work": it.get("mod_work")}
    return LP.stage_of(f, now)["stage"]


def _pause_line(p):
    if not isinstance(p, dict):
        return "code review pause: UNMEASURED (the reading carries none)"
    if p.get("could_not_look"):
        return p["could_not_look"]
    if not p.get("on"):
        return "code review pause: off"
    return "%s%s; %d ticket(s) held" % (PAUSE_PREFIX, p.get("reason"), p.get("held") or 0)


def _game_pause_line(p):
    if not isinstance(p, dict):
        return "game work pause: UNMEASURED (the reading holds no game_pause)"
    if p.get("could_not_look"):
        return p["could_not_look"]
    if not p.get("on"):
        return "game work pause: off"
    return "%s%s; advancing: %s; %d ticket(s) held" % (GAME_PAUSE_PREFIX, p.get("reason"),
                                                      ", ".join(p.get("advancing_mods") or []) or "none", p.get("held") or 0)


def _game_status():
    """`pause game status`: the setting now, and the count of held tickets of the last applied tick. -> rc (2 when that
    count is unmeasured)."""
    now = game_pause_reading({})
    if now.get("could_not_look"):
        print(now["could_not_look"])
        return 2
    head = ("game work pause: on; reason: %s; advancing: %s" % (now.get("reason"), ", ".join(now.get(
        "advancing_mods") or []) or "none")) if now.get("on") else "game work pause: off"
    p = os.path.join(sdir(create=False), "reading.json")
    rd = _read(p, None)
    gp = (rd or {}).get("game_pause") if isinstance(rd, dict) else None
    if not isinstance(gp, dict) or not isinstance(gp.get("held"), int):
        print("%s; held: UNMEASURED (%s holds no game pause count of an applied tick)" % (head, p))
        return 2
    print("%s; %d ticket(s) held at the last applied tick (%s)" % (head, gp["held"], rd.get("at_pac") or "-"))
    return 0


def _print(rd):
    print(_pause_line(rd.get("pause")))
    print(_game_pause_line(rd.get("game_pause")))
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
    pz = sub.add_parser("pause", help="the code review pause: on|off|show (code_review_pause); the game work pause: "
                                      "game on|off|status (game_work_pause)")
    pz.add_argument("words", nargs="+", metavar="[game] on|off|show|status")
    pz.add_argument("--why", help="the reason, written in the setting (on)")
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
    if o.cmd == "pause":
        game = o.words[0] == "game"
        mode = (o.words[1:] or [""])[0] if game else o.words[0]
        if len(o.words) != (2 if game else 1) or mode not in (("on", "off", "status", "show") if game else
                                                               ("on", "off", "show")):
            print("REFUSED: pause takes on|off|show (the code review pause) or game on|off|status (the game work "
                  "pause); got %r" % " ".join(o.words))
            return 2
        if game and mode in ("status", "show"):
            return _game_status()
        if mode == "show":
            print(_pause_line(pause_reading({})))
            return 0
        with open(CFG_PATH, encoding="utf-8") as f:
            text = f.read()
        try:
            new = set_pause(text, mode == "on", o.why, key=GAME_PAUSE_KEY if game else PAUSE_KEY)
        except ValueError as e:
            print("REFUSED: %s" % e)
            return 2
        tmp = CFG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(new)
        os.replace(tmp, CFG_PATH)
        print("%s pause %s in %s; it binds the lane once landed: ./publish -m \"<reason>\" %s"
              % ("game work" if game else "code review", mode, CFG_PATH, os.path.relpath(CFG_PATH)))
        return 0
    # The tick's lock: an applied tick reads state.json, decides for minutes and writes its copy back, so a clear written
    # in between was lost (2026-11-27 10:10 AM PST). The clear waits for a running tick and writes on top of its state.
    with open(os.path.join(sdir(), "tick.lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
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
