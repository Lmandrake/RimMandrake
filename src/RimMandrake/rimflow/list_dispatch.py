#!/usr/bin/env python3
"""list_dispatch.py: the List Pipeline's Waiting, Ready and Work stages. No model, no tokens of its own.

Item RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST, step 2 of
design/specs/2026-11-22-coordination-every-agent-must-use/plan.md. Page design/specs/2026-11-23-list-dispatch/boundary.md;
selftest selftest_list_dispatch.py; acceptance acceptance/step2_list_lane_accept.py. Why: on 2026-11-23 about 918 open list
items waited for the Conductor's hand, because no program launched them. The shape of red_dispatch.py.

    python3 src/RimMandrake/rimflow/list_dispatch.py tick [--apply] [--only ID...]   one pass; acts only with --apply
    python3 src/RimMandrake/rimflow/list_dispatch.py status              the last reading
    python3 src/RimMandrake/rimflow/list_dispatch.py clear ITEM --why "..."   the Conductor lifts a stop: one more run

Per open list item that carries an outcome check (step 1, list_effect.py), oldest item that another waits on first, then
oldest filing first, one decision:
  close           the check holds (work already done): closed as the pipeline's act; nothing launches
  blind | no_effect  the check is unmeasured | the item has no check
  adopt           no check, but its ## verify names an existing *_accept.py: attached as `cmd:python3 <path>` (seen
                  failing by the step-1 gate); nothing launches on that tick
  live            a detached run is live on it
  waits_on | blocked | waiting | reshape   it waits on an open item | is blocked | has a dated wait ahead | its dated
                  wait passed and the check fails (a date never launches old work; Shape, step 4, takes it)
  held | off      its mod is held by the owner | a `pipe off` (all, family:list_dispatch, family:detached, item, mod)
  stopped         a run ended and the check fails with no named next act, or after max_runs_per_item runs, or after
                  max_never_started launches that never started: a Needs Conductor line, once
  disabled | pipeline_paused | account_hold | chain_stop | slots_full | pool_full   the gates
  launch          one detached helper (detached_helper.py launch --next-act-owner list_dispatch), sonnet when the check
                  runs a selftest or acceptance script, else opus
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

ITEM = "RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST"
UNIT = "rm-list-dispatch.service"
FAMILY = "list_dispatch"
CFG_PATH = os.path.join(HERE, "list_dispatch.json")
CLOSED = ("done", "dropped", "superseded")
PAC = dt.timezone(dt.timedelta(hours=-8), "PST")
ACCEPT_RX = re.compile(r"python3\s+((?:design|src)/[^\s'\"`]+?_accept\.py)\b")
# Hang guard (the class of call_deadline_lint.py) for one `detached_helper.py launch` (a clone sync, a fetch).
LAUNCH_TIMEOUT_S = 900
# Hang guard for `rimflow effect` (it runs the check once, then publishes).
EFFECT_TIMEOUT_S = 900


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
    """-> item ids: an item another open item waits on first, then the oldest filing, then the id."""
    return sorted(items, key=lambda i: (not (items[i] or {}).get("blocks_others"),
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


def spent(attempts):
    return [a for a in attempts or [] if not a.get("failed")]


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

def _need(iid, it, why, smallest):
    return {"outcome": "%s: its outcome check %s still fails (%s)" % (iid, it.get("effect"), _one(it.get("out"), 160)),
            "why_not_recovered": why, "smallest_act": smallest}


def decide(cfg, st, facts, now, account=(True, "")):
    """-> (rows, launches). Pure over (cfg, st, facts, now, account); writes only st. One row per item, in order."""
    items = (facts or {}).get("items")
    if items is None:
        return [{"item": "-", "decision": "blind", "why": "the ledger could not be read; nothing launches"}], []
    sti = st.setdefault("items", {})
    runs = facts.get("runs") or {}
    live_total = sum(len((runs.get(i) or {}).get("live") or []) for i in items if (items[i] or {}).get("effect"))
    paused, pool = facts.get("paused"), facts.get("pool")
    max_runs = int(cfg.get("max_runs_per_item", 2))
    max_never = int(cfg.get("max_never_started", 2))
    rows, launches = [], []
    for iid in list(items):
        it = items[iid] or {}
        s = sti.get(iid) or {}
        att = s.get("attempts") or []
        done = spent(att)
        run = runs.get(iid) or {}
        row = {"item": iid}
        rows.append(row)

        def put(decision, why, row=row):
            row["decision"], row["why"] = decision, why

        def stop(why, smallest, row=row, it=it, s=s, iid=iid, att=att):
            put("stopped", why)
            fp = [len(att), it.get("events")]
            if s.get("told") != fp:
                row["need"] = _need(iid, it, why, smallest)
                row["told_fp"] = fp

        if it.get("state") in CLOSED:
            put("closed", "the item is %s" % it.get("state"))
            continue
        claimed = it.get("claimed") if not att else None     # the lease of a run of ours never stops our next run
        if not it.get("effect"):
            acc = it.get("accept")
            if claimed:
                put("claimed", "%s; the holder works it, so its check is not attached" % claimed)
                continue
            ref = s.get("adopt_refused") or {}
            if acc and ref.get("fp") == [acc, it.get("events")]:
                put("adopt_refused", "attaching %s was refused: %s" % (acc, _one(ref.get("why"), 200)))
            elif acc:
                put("adopt", "no outcome check; its ## verify runs %s, attached as its check this tick" % acc)
                row["accept"] = acc
            else:
                put("no_effect", "the item carries no outcome check, so it is not the lane's (Shape, step 4)")
            continue
        verdict = it.get("verdict")
        if verdict == "holds":
            ref = s.get("close_refused") or {}
            if ref.get("fp") == [it.get("effect"), it.get("events")]:
                put("close_refused", "the check holds but `rimflow close` refused: %s" % _one(ref.get("why"), 200))
            else:
                put("close", "the check holds: the work is done (%s)" % _one(it.get("out"), 160))
            continue
        if verdict != "fails":
            put("blind", "the check is unmeasured: %s" % _one(it.get("out") or verdict, 200))
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
        if wu:
            if wu > now:
                put("waiting", "it waits until %s: %s" % (pac(wu), it.get("wait_reason") or "no reason given"))
            else:
                put("reshape", "its wait to %s passed and the check still fails; a date never launches old work, so the "
                               "Shape stage (plan step 4) looks at it again" % pac(wu))
            continue
        if it.get("held"):
            put("held", it["held"])
            continue
        if it.get("off_unreadable"):
            put("blind", it["off_unreadable"])
            continue
        if it.get("off"):
            put("off", it["off"])
            continue
        if done:
            last = done[-1]
            if last.get("unit") not in (run.get("ended") or []):
                put("unseen", "run %s is neither live nor seen ended in the run records; no second launch" % last.get("unit"))
                continue
            if len(done) >= max_runs:
                stop("%d Work runs (%s) ended and the check still fails; %d is the most" % (
                    len(done), ", ".join(str(a.get("unit")) for a in done), max_runs),
                    "read the runs' notes on %s, then do the rest by hand, put a wait on it, drop it, or "
                    "`list_dispatch.py clear %s --why ...` for one more run" % (iid, iid))
                continue
            if not last.get("next"):
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
        if tail >= max_never:
            stop("%d launches in a row never started; the last: %s" % (tail, _one(att[-1].get("failed"), 200)),
                 "clear the cause the launch names, then `list_dispatch.py clear %s --why ...`" % iid)
            continue
        if not cfg.get("enabled"):
            put("disabled", "list_dispatch.json has enabled: false")
            continue
        if paused:
            put("pipeline_paused", paused)
            continue
        if not account[0]:
            put("account_hold", account[1] or "the account gate holds launches")
            continue
        if int(it.get("depth") or 0) >= int(cfg.get("max_chain_depth", 2)):
            put("chain_stop", "its chain of causes already holds %s lane runs; %s is the most" % (
                it.get("depth"), cfg.get("max_chain_depth", 2)))
            continue
        if live_total >= int(cfg.get("max_live", 2)):
            put("slots_full", "%d live list-lane runs, the most is %s" % (live_total, cfg.get("max_live", 2)))
            continue
        if pool and not it.get("clone_exists"):
            put("pool_full", pool)
            continue
        model, mwhy = pick_model(cfg, it.get("effect"))
        cap = cfg.get("%s_cap_usd" % model, _shipped().get("%s_cap_usd" % model))   # a partial cfg keeps the shipped cap
        if not (isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0):
            put("no_cap", "list_dispatch.json has no positive %s_cap_usd; nothing launches without a cap" % model)
            continue
        live_total += 1
        row.update(model=model, cap=cap, run_n=len(done) + 1)
        put("launch", "Work run %d: %s (%s); the check fails: %s" % (len(done) + 1, model, mwhy, _one(it.get("out"), 120)))
        launches.append(iid)
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


def _runs(ids):
    import detached_helper as DH
    out = {}
    for rec in DH.all_records():
        if rec.get("item") not in ids:
            continue
        stt = DH.live_status(rec)
        r = out.setdefault(rec["item"], {"live": [], "ended": []})
        r["live" if stt in ("launching", "running") else "ended"].append(rec["unit"])
    return out


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
        a["next"] = str(n.get("text"))[:600] if n else None


def gather(st, now=None, root=None):
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
    mods = _mods()
    adopt_ok = os.path.isdir(LM.ITEMS)
    items = {}
    for iid, x in open_.items():
        acc = None
        if not x.effect and adopt_ok:
            p = os.path.join(LM.ITEMS, iid + ".md")
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    acc = accept_script(f.read())
            if not acc:
                continue
        waits = [b for b in (x.blocked_on,) + tuple(x.blocked_also or ())
                 if b and b in w.items and w.items[b].state not in CLOSED]
        d = {"state": x.state, "blocked": bool(x.blocked) and not waits, "blocked_reason": x.blocked_reason,
             "effect": x.effect, "waits_on": waits, "events": len(x.history), "title": x.title,
             "filed": LM.epoch(x.created_at) if x.created_at else None, "blocks_others": iid in waited_on,
             "caused_by": x.caused_by}
        if x.state == "doing" and LM.lease_status(x, now) == "live":
            d["claimed"] = "doing under %s, whose lease is live to %s" % (x.owner, (x.lease or {}).get("expires"))
        if x.wait_until:
            try:
                d["wait_until"], d["wait_reason"] = LM.epoch(x.wait_until), x.wait_reason
            except Exception:  # noqa: BLE001 - an unreadable date is not "no wait"
                d["blocked"], d["blocked_reason"] = True, "its wait date %r cannot be read" % x.wait_until
        if acc:
            d["accept"] = acc
        items[iid] = d
    ordered = {i: items[i] for i in order_ids(items)}
    runs = _runs(set(ordered))
    _read_next(st, ordered, runs)
    for iid, d in ordered.items():
        if not d.get("effect"):
            continue
        d["verdict"], d["out"] = LE.run(d["effect"], root)
        if d["verdict"] != "fails":
            continue
        d["mod"] = mod_of(iid, d.get("title"), mods)
        try:
            d["held"] = _held(d["mod"])
        except Exception as e:  # noqa: BLE001
            d["off_unreadable"] = "the owner's mod holds could not be read (%s: %s)" % (type(e).__name__, e)
        d["off"], cnl = _off(iid, d["mod"])
        if cnl:
            d["off_unreadable"] = cnl
        d["depth"] = chain_depth(iid, lambda i: (w.items.get(i).caused_by if w.items.get(i) else None), st)
        d["clone_exists"] = _clone_exists(iid)
    live = sum(len(r["live"]) for r in runs.values())
    return {"items": ordered, "runs": runs, "other_live": 0, "paused": _paused(now),
            "pool": _pool(), "live_lane": live}


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
    return """Work list item {item} (the List Pipeline's Work stage, run {n} of at most 2).

Title: {title}
Its outcome check, which fails now:   {check}
What the check printed: {out}

The check is the judge of "done". The item is done when the check holds on origin/main, and not before.

Steps:
0. Start the item, before anything else:
   python3 src/RimMandrake/rimflow/cli.py start {item} --seat BENCH --why "list lane Work run (list_dispatch.py)" --publish
1. Read it whole: python3 src/RimMandrake/rimflow/cli.py show {item}  (its prose, its notes, what earlier runs left).
2. Do the work the item asks for. The need is what the item says, not only the check's text: a check that you can pass
   while the need stays unmet is wrong, and you say so in a note instead of passing it.
3. Run the check in your clone until it reads holds:
   python3 src/RimMandrake/rimflow/list_effect.py check '{check}'
4. Land with ./publish -m "{item}: <what>" <explicit paths>, then close:
   python3 src/RimMandrake/rimflow/cli.py close {item} --sha <published sha> --seat BENCH --why "list lane: the check holds at <sha>" --publish
   (an operational item also takes its --live promise).
5. If you cannot finish, end with exactly one of these on the item, and nothing else:
   - a note whose text starts `LEFT OPEN:` and names the ONE next act that a second run of yours would do. The lane gives
     the item at most one more run, and only on that note.
   - a dated wait (`cli.py wait {item} --until <YYYY-MM-DD> --reason "<who acts next and on what>"`) when the next act is
     someone else's (the owner's, the Conductor's, a date).
   Do not file a new item for your own next step.
""".format(item=iid, n=row.get("run_n", 1), title=it.get("title") or "-", check=it.get("effect"),
           out=_one(it.get("out"), 600) or "(nothing)")


def launch(item, model, cap, brief, seat, mod):
    d = os.path.join(sdir(), "briefs")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%s-%d.md" % (item, int(time.time())))
    with open(path, "w", encoding="utf-8") as f:
        f.write(brief)
    argv = [sys.executable, os.path.join(HERE, "detached_helper.py"), "launch", "--seat", seat, "--item", item,
            "--brief-file", path, "--model", model, "--budget-usd", "%g" % cap, "--next-act-owner", FAMILY]
    if mod:
        argv += ["--env", "RM_CONTROL_MOD=%s" % mod]
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
                s["told"] = row.pop("told_fp")
            except Exception as e:  # noqa: BLE001 - the line stays owed and is said on the row
                row["need_failed"] = "%s: %s" % (type(e).__name__, e)
        if row["decision"] == "close":
            text = "outcome check holds (list_dispatch, before a Work run): %s | output: %s" % (
                it.get("effect"), _one(it.get("out"), 400) or "(none)")
            rc, said = do_close(iid, text, "pipeline act (list_dispatch tick, %s): the item's outcome check holds" % UNIT)
            if rc == 0:
                row["decision"] = "closed_by_check"
            else:
                s["close_refused"] = {"fp": [it.get("effect"), it.get("events")], "why": _one(said, 600), "at": now}
                row.update(decision="close_refused", why=_one(said, 300))
            continue
        if row["decision"] == "adopt":
            rc, said = do_attach(iid, "cmd:python3 %s" % row["accept"],
                                 "pipeline act (list_dispatch tick, %s): its ## verify runs this acceptance script" % UNIT)
            if rc == 0:
                row["decision"] = "adopted"
            else:
                s["adopt_refused"] = {"fp": [row["accept"], it.get("events")], "why": _one(said, 600), "at": now}
                row.update(decision="adopt_refused", why=_one(said, 300))
            continue
        if iid not in launches:
            continue
        rc, text, unit = do_launch(iid, row["model"], row["cap"], brief_text(iid, it, row), cfg.get("seat", "BENCH"),
                                   it.get("mod"))
        ok = rc == 0 and bool(unit)
        s.pop("told", None)
        s.setdefault("attempts", []).append({"at": now, "unit": unit, "model": row["model"], "cap": row["cap"],
                                             "failed": None if ok else "never started: " + (_one(text, 400) or "rc %s" % rc)})
        if ok:
            row.update(decision="launched", unit=unit)
        else:
            row.update(decision="launch_failed", why=_one(text, 300) or "rc %s" % rc)


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
        facts = fx["facts"](st) if "facts" in fx else gather(st, now)
        account = fx["account"]() if "account" in fx else account_gate()
        gone = []
        if only and facts.get("items") is not None:     # the Conductor's run-now: these items, every gate
            gone = [i for i in only if i not in facts["items"]]
            facts = dict(facts, items={i: facts["items"][i] for i in only if i in facts["items"]})
        rows, launches = decide(cfg, st, facts, now, account)
        rows += [{"item": i, "decision": "not_found",
                  "why": "not an open item with an outcome check or an acceptance script"} for i in gone]
        if apply:
            execute(cfg, st, rows, launches, facts, now, fx)
        else:
            for r in rows:
                r["decision"] = {"launch": "would_launch", "close": "would_close", "adopt": "would_adopt"}.get(
                    r["decision"], r["decision"])
                r.pop("need", None)
        counts = {}
        for r in rows:
            counts[r["decision"]] = counts.get(r["decision"], 0) + 1
        rd = {"schema": 1, "at": now, "at_pac": pac(now), "apply": apply, "account": list(account), "counts": counts,
              "launched": [{"item": r["item"], "unit": r.get("unit"), "model": r.get("model")} for r in rows
                           if r.get("decision") == "launched"],
              "items": {r["item"]: {k: r.get(k) for k in ("decision", "why", "model", "unit", "need")} for r in rows}}
        if apply:
            _write(os.path.join(d, "state.json"), st)
            _write(os.path.join(d, "reading.json"), rd)
            with open(os.path.join(d, "ticks.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps({"at": now, "counts": counts, "launched": rd["launched"]}) + "\n")
        return rd
    finally:
        if lock:
            lock.close()


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
