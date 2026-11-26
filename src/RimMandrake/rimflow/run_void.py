#!/usr/bin/env python3
"""run_void.py: no trial, turn, look or cycle is ever spent by a system failure or a stopped run (item
RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT). The owner, 2026-11-18 ~10:30 AM PST, about Graffiti: "Ensure it
didn't use up it's turns, trials, whatever... I will not accept ANY system that pointlessly expends such statistical
measurements based on failed system calls or behavior. You know that. Fix the system such that it's easy to indicate
this to it. And NEVER tell me "I can't that's frozen" or "it's a write only ledger" or bullshit like that."

Two parts, one effect: a VOID run consumes none of the Maturation Pipeline's counters (the census is
design/RimMandrake/pipeline_trial_counters_census_2026-11-18.md).

  hand    `maturation_dispatch.py void <unit>... | --item ID | --mod MOD --since TIME --why "..." [--owner-said "..."]`
          appends a void line to voids.jsonl (beside state.json and releases.jsonl); `unvoid <unit> --why` appends the
          line that reverses it. An append-only file is no excuse: the fold of its lines is the truth, read by every
          counter reader through sync_dispatch (state.json, in read_state) and sync_stage (a Designer stage.json, in
          designer_stage.load_state and maturation_autonomy.designer_state). A voided run's book entries are MOVED to
          the mod's `voided` list (never deleted), so an unvoid puts them back; a look it applied is un-applied (the
          grant stands again).
  system  sync_system classes a run `void_system` when its record's own result shows a system cause the machine can
          see (killed, timed out, the CLI exiting with no result of its own, a launch that never started and has no
          retry left; system_cause): it is moved out the same
          way and counted on the mod's own `system_faults`, never on its trials. At SYSTEM_FAULT_LIMIT faults since
          the last `clear` the mod reads `system_fault` (alarm OPS_MATURATION_SYSTEM_FAULT_LOOP): none of its own work
          launches and no trial is spent. The tick starts one repair run, whose end resets the count; `clear` (after
          reading the cause) resets it by hand. A launch that never started adds no fault (form_fault).

Four answers stay apart in every record and line: a run that FAILED on the mod's merits counts; a VOID run counts
nothing (hand or system, with its why); ZERO is a measured count; UNMEASURED is a record that could not be read
(that run is left exactly as the books had it, and named). Spend already burnt stays measured as spend: it is shown
apart as void spend, and off the stage ceiling by his card of 2026-11-18 (maturation_dispatch.void_units).
"""
import copy
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import form_fault as FF  # noqa: E402

ALARM_ID = "OPS_MATURATION_SYSTEM_FAULT_LOOP"
SYSTEM_FAULT_LIMIT = 3
# the dispatch books a run can sit in: dict books keyed by state key or item, list books of launch entries, and single
# entries holding one run
DICT_BOOKS = ("steward", "fixers")
# releases_used is reached by the automatic class only: a ceiling release a void_system run spent is given back (the
# Conductor's decision of 2026-11-18 1:05 PM PST on RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS: "a
# ceiling release spent by a voided run IS given back ... reverse that for void_system runs only"; that run's spend is
# off the ceiling too). A hand void leaves it spent.
RELEASE_BOOK = "releases_used"
LIST_BOOKS = ("blind_auto", "ingame_auto", "launches", "holder_road_back", "pilot_launches", "ledger_runs")
ONE_BOOKS = ("last_run", "cert_rerun", "cert_red", "cert_red_seen")
# books the automatic class reads: a run there that died of a system cause would otherwise count as its trial. Not
# ledger_runs: it is end_ledger_runs' bookkeeping (every unit in it sits in another book too), and its entry must stay
# for the run.end; not cert_rerun: its unit has no detached record (cert_rerun_decide retries it on its own)
SYSTEM_BOOKS = DICT_BOOKS + ("blind_auto", "ingame_auto", "launches", "holder_road_back", "pilot_launches")
# single entries that go out (and come back) with their unit's `launches` entry: the builder's last run, and the
# red-decider builder (or red-proof run) cert_red_decide reads as "ended and still red" (or "still owe their red proof")
FOLLOW_LAUNCH = ("last_run", "cert_red", "cert_red_seen")
UNM = "UNMEASURED"


# ---- the void ledger ------------------------------------------------------------------------------------------------

def path():
    p = os.environ.get("RM_RUN_VOIDS_FILE")
    if p:
        return p
    d = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "maturation")
    return os.path.join(d, "voids.jsonl")


def read(p=None):
    """-> (records in file order, malformed line count). No file: ([], 0), no void stands."""
    recs, bad = [], 0
    try:
        with open(p or path(), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        return recs, 0
    for line in lines:
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            r = None
        if isinstance(r, dict) and r.get("act") in ("void", "unvoid") and isinstance(r.get("unit"), str) and \
                r["unit"].strip() and isinstance(r.get("why"), str) and r["why"].strip():
            recs.append(r)
        else:
            bad += 1
    return recs, bad


def active(p=None, recs=None):
    """-> {unit: its standing void line}: the fold of every void and unvoid line, in order."""
    out = {}
    for r in (read(p)[0] if recs is None else recs):
        if r["act"] == "void":
            out[r["unit"]] = r
        else:
            out.pop(r["unit"], None)
    return out


def _iso(t=None):
    return dt.datetime.fromtimestamp(time.time() if t is None else t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(rec, p=None):
    rec["id"] = "void-%s" % hashlib.sha1(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:12]
    p = p or path()
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def parse_time(s):
    """-> epoch seconds for an ISO time (Z or an offset) or a local Pacific 'YYYY-MM-DD HH:MM' (his clock); None when
    it is neither."""
    s = str(s or "").strip()
    try:
        if s.endswith("Z"):
            return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
        t = dt.datetime.fromisoformat(s.replace(" ", "T"))
    except ValueError:
        return None
    if t.tzinfo is None:
        import maturation_now as MN
        t = t.replace(tzinfo=MN.PAC)
    return t.timestamp()


# ---- what a unit is -------------------------------------------------------------------------------------------------

def _units_of(x):
    return [x["unit"]] if isinstance(x, dict) and isinstance(x.get("unit"), str) and x["unit"] else []


def book_entries(st):
    """-> [(mod, book, key, entry)] for every run-bearing entry of state.json's books (key: the dict key, the list
    index, or None for a single entry)."""
    out = []
    for mod, s in ((st or {}).get("mods") or {}).items():
        if not isinstance(s, dict):
            continue
        for b in DICT_BOOKS:
            for k, x in (s.get(b) or {}).items() if isinstance(s.get(b), dict) else []:
                out.append((mod, b, k, x))
        for b in LIST_BOOKS:
            for n, x in enumerate(s.get(b) or []) if isinstance(s.get(b), list) else []:
                out.append((mod, b, n, x))
        for b in ONE_BOOKS:
            if isinstance(s.get(b), dict):
                out.append((mod, b, None, s[b]))
    return out


def _at_of(x):
    v = (x or {}).get("at")
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0


def voided_cycle_run(s, visit_id, cycle):
    """-> the newest booked judge run on blind cycle `cycle` of visit `visit_id` when it is VOID and no counted
    `blind_auto` entry on that cycle is as new, else None. A voided run gave no verdict: its exit block is interim
    (RIMMANDRAKE_RESUME_VOIDED_BLIND_JUDGE_NOT_READ_AS_VERDICT; design/specs/2026-11-23-resume-voided-blind-judge/).
    s: one mod's dict of the Dispatch state (after sync_dispatch). -> {"entry", "unit", "run" (its ledger run or None),
    "void", "class", "why"}."""
    if not isinstance(s, dict):
        return None

    def on(x):
        return (isinstance(x, dict) and x.get("cycle") == cycle and x.get("visit_id") == visit_id
                and bool(_units_of(x)))
    moved = [m for m in s.get("voided") or [] if isinstance(m, dict) and m.get("book") == "blind_auto"
             and on(m.get("entry"))]
    if not moved:
        return None
    last = max(moved, key=lambda m: _at_of(m["entry"]))
    if any(on(x) and _at_of(x) >= _at_of(last["entry"]) for x in s.get("blind_auto") or []):
        return None
    unit = last["entry"]["unit"]
    runs = [m.get("entry") for m in s.get("voided") or [] if isinstance(m, dict) and m.get("book") == "ledger_runs"] + \
        list(s.get("ledger_runs") or [])
    run = next((r.get("run") for r in runs if isinstance(r, dict) and r.get("unit") == unit and r.get("run")), None)
    return {"entry": dict(last["entry"]), "unit": unit, "run": run, "void": last.get("void"),
            "class": last.get("class"), "why": last.get("why")}


def stage_runs(st):
    """-> {unit: at (epoch or None)} for the runs a Designer stage.json names: its coverage judges, its results and the
    runs its history opened."""
    out = {}
    for r in st.get("coverage_rounds") or []:
        if isinstance(r, dict) and r.get("judge"):
            out[r["judge"]] = parse_time(r.get("at"))
    for r in st.get("results") or []:
        if isinstance(r, dict) and r.get("run"):
            out.setdefault(r["run"], parse_time(r.get("at")))
    for h in st.get("history") or []:
        m = re.match(r"run (\S+?),? ", str((h or {}).get("why") or "")) if isinstance(h, dict) else None
        if m and h.get("what") == "open":
            out[m.group(1)] = parse_time(h.get("at"))
    for c in (st.get("budget") or {}).get("charges") or []:     # a legacy judge known only by its charge
        ref = str((c or {}).get("ref") or "") if isinstance(c, dict) else ""
        if ref.startswith("rm-coverage-judge-"):
            out.setdefault(ref, parse_time(c.get("at")))
    return out


def stage_parents(st):
    """-> {unit: the detached run that launched it, or None when none was recorded} for the runs stage_runs names: a
    coverage round's and a result's `parent`, and the `parent` on the history row that opened a Designer run
    (role_launch carries RM_DETACHED_UNIT from the run-now request into both)."""
    out = {}
    for r in st.get("coverage_rounds") or []:
        if isinstance(r, dict) and r.get("judge"):
            out[r["judge"]] = r.get("parent") or None
    for r in st.get("results") or []:
        if isinstance(r, dict) and r.get("run") and (r.get("parent") or r["run"] not in out):
            out[r["run"]] = r.get("parent") or None
    for h in st.get("history") or []:
        m = re.match(r"run (\S+?),? ", str((h or {}).get("why") or "")) if isinstance(h, dict) else None
        if m and h.get("what") == "open" and (h.get("parent") or m.group(1) not in out):
            out[m.group(1)] = h.get("parent") or None
    return out


def concept_dirs(root):
    d = os.path.join(root, "design", "concepts")
    try:
        return [os.path.join(d, n) for n in sorted(os.listdir(d)) if os.path.isfile(os.path.join(d, n, "stage.json"))]
    except OSError:
        return []


def _raw_stage(d):
    try:
        with open(os.path.join(d, "stage.json"), encoding="utf-8") as f:
            st = json.load(f)
        return st if isinstance(st, dict) else None
    except (OSError, ValueError):
        return None


def children(root, mod, rec):
    """-> the Designer runs and coverage judges a detached run started on MOD's concept: every one whose recorded
    `parent` is its unit, whenever it started; and, for an entry with no parent recorded (written before launches
    recorded one), those that STARTED while it was live (its record's at to its end; no slack after). An entry another
    run launched is never taken, however it overlaps (Codex review of 5070199008, point 10). `void` prints every unit
    it takes."""
    t0 = rec.get("at")
    t1 = next((rec[k] for k in ("ended", "returned") if isinstance(rec.get(k), (int, float))), None)
    if not isinstance(t0, (int, float)) or not mod:
        return []
    t1 = t1 if t1 is not None else time.time()
    st = _raw_stage(os.path.join(root, "design", "concepts", mod)) or {}
    # a voided stage file still names its moved runs: they are children too (a second void finds the same set)
    runs, par = dict(stage_runs(st)), dict(stage_parents(st))
    for m in ((st.get("voided") or {}).get("moved") or []):
        one = {m["field"]: [m["entry"]]} if m.get("field") in ("coverage_rounds", "results", "history") else {}
        runs.update(stage_runs(one))
        par.update({u: p for u, p in stage_parents(one).items() if p or u not in par})
    for u in runs:      # a second reader's charge (<judge>-reader) is its judge's: it takes the judge's parent
        if u.endswith("-reader") and not par.get(u) and par.get(u[:-len("-reader")]):
            par[u] = par[u[:-len("-reader")]]
    me = rec.get("unit")
    return sorted(u for u, at in runs.items() if (me and par.get(u) == me) or (
        not par.get(u) and at is not None and t0 <= at <= t1))


VERIFY_RUN = re.compile(r"^(?P<item>[A-Z0-9_]+)/run-\d+@.+$")    # model.Run.name: a Test Pilot verify run


def ledger_run(name):
    """-> True when the ledger holds the verify run `name` (model.Run.name)."""
    import model
    m = VERIFY_RUN.match(name)
    it = model.replay(model.read()).items.get(m.group("item")) if m else None
    return bool(it) and any(r.name == name for r in it.runs)


def resolve(root, st, units=(), item=None, mod=None, since=None, record=None, verify_run=None):
    """-> ([(unit, mod, item, rec)], refusal or None). A unit is known when it has a run record, sits in a dispatch book
    or is named by a concept's stage.json, or is a verify run the ledger holds (`<ID>/run-N@<config>`, voided when a
    harness fault recorded its fail: testpilot_route then counts it in no streak); anything else is refused by name."""
    import detached_helper as DH
    record = record or DH.read_record
    books = book_entries(st)
    in_book = {}
    for m, b, k, x in books:
        for u in _units_of(x):
            in_book.setdefault(u, (m, x.get("item")))
    for m, s in ((st or {}).get("mods") or {}).items():     # a run already moved out (void_system) is known too
        for v in (s.get("voided") or []) if isinstance(s, dict) else []:
            if v.get("unit"):
                in_book.setdefault(v["unit"], (m, (v.get("entry") or {}).get("item")))
    staged = {}
    for d in concept_dirs(root):
        for u, at in stage_runs(_raw_stage(d) or {}).items():
            staged.setdefault(u, (os.path.basename(d), at))
    want = list(units or [])
    if item:
        want += [u for u, (m, it) in in_book.items() if it == item]
        try:
            want += [r["unit"] for r in DH.all_records() if r.get("item") == item]
        except OSError:
            pass
        if not want:
            return [], "no run is known for item %s (no book entry, no run record)" % item
    if mod and since is not None:
        got = [u for m, b, k, x in books for u in _units_of(x) if m == mod and isinstance(x.get("at"), (int, float))
               and x["at"] >= since]
        s = ((st or {}).get("mods") or {}).get(mod)     # a run sync_system already moved out, by its entry's saved at
        for v in (s.get("voided") or []) if isinstance(s, dict) else []:
            at = (v.get("entry") or {}).get("at") if isinstance(v, dict) else None
            if v.get("class") == "void_system" and v.get("unit") and isinstance(at, (int, float)) and at >= since:
                got.append(v["unit"])
        got += [u for u, (m, at) in staged.items() if m == mod and at is not None and at >= since]
        if not got:
            return [], "no run on %s since %s" % (mod, _iso(since))
        want += got
    out, seen = [], set()
    for u in want:
        if u in seen:
            continue
        seen.add(u)
        vm = VERIFY_RUN.match(u)
        if vm and u not in in_book and u not in staged:
            if not (verify_run or ledger_run)(u):
                return [], "unknown run %s: the ledger holds no such verify run" % u
            out.append((u, mod, vm.group("item"), None))
            continue
        rec = record(u)
        if not rec and u not in in_book and u not in staged:
            return [], "unknown run %s: no run record, no dispatch book entry, no concept names it" % u
        m = (in_book.get(u) or (None,))[0] or (staged.get(u) or (None,))[0] or mod
        it = (rec or {}).get("item") or (in_book.get(u) or (None, None))[1]
        out.append((u, m, it, rec))
    return out, None


# ---- the verbs ------------------------------------------------------------------------------------------------------

def void(root, st, units=(), item=None, mod=None, since=None, why="", by="", owner_said=None, record=None, p=None,
         now=None, verify_run=None):
    """Append one void line per run (and per Designer run or judge it started). -> (lines written, refusal or None).
    A unit already void is refused, never written twice; every void here is a HAND void: a run that genuinely failed
    on the mod's merits may be voided (his call), and its line says hand."""
    if not str(why or "").strip():
        return [], "a void says why (--why)"
    got, bad = resolve(root, st, units, item, mod, since, record, verify_run)
    if bad:
        return [], bad
    cur = active(p)
    plan = []
    for u, m, it, rec in got:
        kids = children(root, m, rec) if rec else []
        plan.append((u, m, it, rec, None))
        plan += [(k, m, it, None, u) for k in kids if k != u]
    dup = [u for u, m, it, rec, par in plan if u in cur and par is None]
    if dup:
        return [], "already VOID: %s" % "; ".join("%s since %s (%s)" % (u, cur[u]["ts"], cur[u]["id"]) for u in dup)
    out, done = [], set()
    for u, m, it, rec, par in plan:
        if u in cur or u in done:
            continue
        done.add(u)
        r = {"act": "void", "ts": _iso(now), "unit": u, "mod": m, "item": it, "why": why.strip(), "by": by or UNM,
             "kind": "hand", "result": (rec or {}).get("result") or UNM,
             "cost_usd": (rec or {}).get("cost_usd") if isinstance((rec or {}).get("cost_usd"), (int, float)) else UNM}
        if par:
            r["parent"] = par
        if owner_said:
            r["owner_said"] = owner_said
        out.append(_append(r, p))
    return out, None


def unvoid(units, why, by="", owner_said=None, p=None, now=None):
    """Reverse standing voids (the unit's children with it). -> (lines written, refusal or None)."""
    if not str(why or "").strip():
        return [], "an unvoid says why (--why)"
    cur = active(p)
    miss = [u for u in units if u not in cur]
    if miss:
        return [], "not VOID: %s" % ", ".join(miss)
    out = []
    targets = list(units) + [u for u, r in cur.items() if r.get("parent") in units and u not in units]
    for u in targets:
        r = {"act": "unvoid", "ts": _iso(now), "unit": u, "mod": cur[u].get("mod"), "item": cur[u].get("item"),
             "why": why.strip(), "by": by or UNM, "of": cur[u]["id"]}
        if owner_said:
            r["owner_said"] = owner_said
        out.append(_append(r, p))
    return out, None


# ---- the readers' choke points --------------------------------------------------------------------------------------

def _moved(s):
    return s.setdefault("voided", [])


def _void_items(cur):
    return {r.get("item") for r in cur.values() if r.get("item")}


def sync_dispatch(st, cur=None):
    """Make state.json's books agree with the standing voids, in place: an entry whose unit is VOID moves to its mod's
    `voided` list (book, key, entry, the void's id and why), a moved entry whose hand void was reversed goes back, and
    a road back a voided steward opened goes with it. System voids (class void_system) are sync_system's and stay.
    -> st. Idempotent: every reader may call it."""
    cur = active() if cur is None else cur
    for mod, s in ((st or {}).get("mods") or {}).items():
        if not isinstance(s, dict):
            continue
        mv = s.get("voided") or []
        # a hand void of a run already classed void_system makes it a hand void: the owner's or Conductor's stop is
        # his call, not a fault of the machine, so it leaves the system-fault count (it comes back if he unvoids it)
        hand = {m.get("unit") for m in mv if m.get("class") == "void_system" and m.get("unit") in cur}
        spent = [m for m in mv if m["book"] == RELEASE_BOOK and m.get("unit") in hand and _restore(s, m)]
        if spent:       # a hand void leaves a release spent: the one its run's void_system class gave back is spent again
            mv = s["voided"] = [m for m in mv if not any(m is x for x in spent)]
        for m in mv:
            if m["book"] == "road_back" and m.get("class") == "void_system" and _caused_by_hand(m, mv, hand):
                m["unit"] = next(x.get("unit") for x in mv if x.get("unit") in hand and x["book"] == "steward"
                                 and x["entry"].get("item") == m["entry"].get("caused_by"))
            if m.get("unit") in hand and m.get("class") == "void_system":
                m.update({"class": "void_hand", "void": cur[m["unit"]].get("id"),
                          "why": cur[m["unit"]].get("why") or m.get("why"), "was": "void_system"})
        if hand:
            s["system_faults"] = [f for f in s.get("system_faults") or [] if f.get("unit") not in hand]
        back = [m for m in mv if m.get("class") == "void_hand" and m.get("unit") not in cur]
        back = [m for m in back if _restore(s, m)]     # one whose place is taken stays saved, retried each read
        if back:
            s["voided"] = [m for m in mv if not any(m is b for b in back)]
        _strip(s, mod, lambda x: next((cur[u] for u in _units_of(x) if u in cur), None), "void_hand")
        for m in s.get("voided") or []:     # a hand-voided road back is tied to its steward's unit, so its unvoid
            if m.get("class") == "void_hand" and m["book"] == "road_back" and not m.get("unit"):    # restores it
                m["unit"] = next((x.get("unit") for x in s["voided"] if x["book"] == "steward"
                                  and x["entry"].get("item") == m["entry"].get("caused_by")), None)
    return st


def _caused_by_hand(m, mv, hand):
    """Does a moved road back belong to a steward run that is now hand-voided?"""
    items = {x["entry"].get("item") for x in mv if x.get("unit") in hand and x["book"] == "steward"}
    return (m.get("entry") or {}).get("caused_by") in items


def _strip(s, mod, judge, klass):
    """Move every entry `judge(entry)` names (-> a void line or a dict with id/why) out of s's books."""
    moved = []
    for b in DICT_BOOKS:
        book = s.get(b)
        for k, x in list(book.items()) if isinstance(book, dict) else []:
            v = judge(x)
            if v:
                moved.append({"book": b, "key": k, "entry": book.pop(k)})
                moved[-1].update(_tag(v, klass, x))
    for b in LIST_BOOKS:
        book = s.get(b)
        if not isinstance(book, list):
            continue
        keep = []
        for x in book:
            v = judge(x)
            if v:
                moved.append(dict({"book": b, "key": None, "entry": x}, **_tag(v, klass, x)))
            else:
                keep.append(x)
        if len(keep) != len(book):
            s[b] = keep
    for b in ONE_BOOKS:
        x = s.get(b)
        v = judge(x) if isinstance(x, dict) else None
        if v:
            moved.append(dict({"book": b, "key": None, "entry": s.pop(b)}, **_tag(v, klass, x)))
    items = {m["entry"].get("item") for m in moved if m["book"] == "steward"}
    rb = s.get("road_back")
    if isinstance(rb, dict) and rb.get("caused_by") in items - {None}:
        src = next(m for m in moved if m["book"] == "steward" and m["entry"].get("item") == rb["caused_by"])
        moved.append(dict({"book": "road_back", "key": None, "entry": s.pop("road_back")},
                          **{k: src[k] for k in ("class", "void", "why", "unit")}))
    if moved:
        _moved(s).extend(moved)
    return moved


def _tag(v, klass, x):
    return {"class": klass, "void": v.get("id"), "why": v.get("why") or v.get("cause"),
            "unit": (_units_of(x) or [None])[0]}


def _restore(s, m):
    b, x = m["book"], m["entry"]
    if b in DICT_BOOKS or (m.get("key") is not None and not isinstance(m.get("key"), int)
                           and b not in LIST_BOOKS + ONE_BOOKS + ("road_back",)):
        book = s.setdefault(b, {})
        if m["key"] in book:        # a newer run took the key since: it stands, this one stays saved (said in status)
            m["collision"] = "unvoided, but a newer run holds %s %s: it stands, this one stays saved" % (b, m["key"])
            return False
        book[m["key"]] = x
    elif b in LIST_BOOKS:
        s[b] = sorted((s.get(b) or []) + [x], key=lambda e: e.get("at") if isinstance(e.get("at"), (int, float)) else 0)
    elif b in ONE_BOOKS or b == "road_back":
        if s.get(b) is not None and s.get(b) != x:
            m["collision"] = "unvoided, but a newer %s stands: this one stays saved" % b
            return False
        s[b] = x
    m.pop("collision", None)
    return True


# ---- the automatic class --------------------------------------------------------------------------------------------

def system_cause(rec, runner=None):
    """-> the system cause a run record shows, or "". Read from the record's own `result` (detached_helper.outcome,
    written at finish from systemd's ExecStopPost variables), never from re-reading its output file: a detached run's
    out is not one JSON document, so "no result JSON" read from it would class every finished run void (measured
    2026-11-18 11:10 AM PST: four success runs on four mods read void_system that way). System causes: a launch that
    never started; KILLED (detached_helper.killed: a signal stop, or a unit dead with its finish never run); a TIMEOUT;
    the CLI exiting non-zero with no result of its own ("exit-code ..."). Not system: "success ..." (it ended), and
    "exit-code/claude-error" (claude answered with an error of its own: a cap or the agent's, not the machine's). A
    record that cannot be read, or whose result is absent, is "" here: UNMEASURED, left as the books had it. A result
    "unknown (...)" is a finish that ran without systemd's variables (by hand on a dead unit) and READ the agent's own
    result JSON (outcome() writes "killed: unknown" when there is none): the run ended on its merits and counts."""
    import detached_helper as DH
    if not isinstance(rec, dict):
        return ""
    if rec.get("status") == "launch_failed" or rec.get("state") == "launch_failed":   # real records: the word is in `status` (`state` is a folder path); the old reading stays
        return "its launch never started (%s)" % str(rec.get("result") or rec.get("why") or rec.get("err") or "launch_failed")
    res = str(rec.get("result") or "")
    if res.startswith("killed"):
        return "killed with no result JSON (%s)" % res
    if rec.get("status") in ("launching", "running"):
        k = DH.killed(rec, runner) if runner else DH.killed(rec)
        return k or ""
    if rec.get("status") != "finished":
        return ""
    if res.startswith("timeout"):
        return "it timed out (%s)" % res
    if res.startswith("exit-code") and not res.startswith("exit-code/claude-error"):
        return "the CLI exited with no result of its own (%s)" % res
    return ""


def heal_system(s, record):
    """A void_system entry whose record no longer shows a system cause (the class was fixed, or the record was
    repaired) goes back to its book and its fault is dropped; so does the road back its steward opened. -> [units]."""
    mv = s.get("voided") or []
    # an entry an earlier build moved from a book voids no longer reach goes back whatever its class (a release moved
    # under a hand void, which leaves it spent); a void_system run's release stays given back until that run heals
    back = [m for m in mv if m["book"] not in DICT_BOOKS + LIST_BOOKS + ONE_BOOKS + ("road_back",)
            and not (m["book"] == RELEASE_BOOK and m.get("class") == "void_system")]    # given back while void
    for m in mv:
        u = m.get("unit")
        if m.get("class") != "void_system" or not u or m["book"] in FOLLOW_LAUNCH + ("road_back", RELEASE_BOOK) \
                or m in back:
            continue
        rec = record(u)
        if isinstance(rec, dict) and rec.get("status") == "finished" and not system_cause(rec):
            back.append(m)
    # a given-back release whose run no longer stands void_system (healed now, or earlier with the release's key then
    # held by a newer run: it stayed saved) is spent again, retried on its own each read (Codex review r1-1)
    still = {m.get("unit") for m in mv if m.get("class") == "void_system" and m["book"] not in (
        RELEASE_BOOK,) + FOLLOW_LAUNCH and not any(m is b for b in back)}
    back += [m for m in mv if m["book"] == RELEASE_BOOK and m.get("class") == "void_system"
             and m.get("unit") not in still and not any(m is b for b in back)]
    if not back:
        return []
    units = {m["unit"] for m in back if m.get("class") == "void_system" and m["book"] != RELEASE_BOOK}
    items = {m["entry"].get("item") for m in back if m["book"] == "steward"}
    back += [m for m in mv if m.get("class") == "void_system" and not any(m is b for b in back) and (
        (m["book"] in FOLLOW_LAUNCH and m.get("unit") in units) or
        (m["book"] == "road_back" and (m.get("entry") or {}).get("caused_by") in items))]
    done = [m for m in back if _restore(s, m)]
    s["voided"] = [m for m in mv if not any(m is d for d in done)]
    s["system_faults"] = [f for f in s.get("system_faults") or [] if f.get("unit") not in units]
    seen = s.setdefault("void_seen", {})
    for u in units:
        seen[u] = "counted"
    return sorted(units)


def sync_system(st, record, keep_failed=None, kills_left=None, now=None):
    """Class `void_system` and move out every book entry whose run died of a system cause, in place; each goes on its
    mod's `system_faults` (one per kill or launch try it holds). keep_failed(book, x) -> True for a never-started
    launch the tick still retries (its tries are the retry's own); kills_left(book, x, cause) -> True for a killed run
    the tick still resumes. Entries whose record cannot be read stay. -> {mod: [moved]}."""
    now = time.time() if now is None else now
    seen_out = {}
    for mod, s in ((st or {}).get("mods") or {}).items():
        if not isinstance(s, dict):
            continue
        heal_system(s, record)
        seen = s.setdefault("void_seen", {})
        unmeasured = set()

        def judge(x, book=None):
            if not isinstance(x, dict) or x.get("void"):
                return None
            u = (_units_of(x) or [None])[0]
            if not u:
                if x.get("wait") and x.get("failed"):   # a wait refusal: no system fault (maturation_autonomy.wait_refusal)
                    return None
                if (x.get("failed") or book == "holder_road_back") and not (keep_failed and keep_failed(book, x)):
                    text = str(x.get("failed") or "no unit")
                    # a launch that never started is a fault of form: repaired, never counted (form_fault; standing
                    # rulings §A fault of form is repaired where it is found); one repair is owed, and the same refusal
                    # after a finished repair counts once, as that repair's fault
                    if FF.fault_class(text) == "wait":
                        return None
                    held = FF.owe_repair(s, text, "%s %s" % (mod, book), now, book=book)
                    return {"cause": held or "its launch never started (form, repairing): %s" % text,
                            "faults": 1 if held else 0, "class": "void_system" if held else "void_form"}
                return None
            if seen.get(u) == "counted":
                return None
            rec = record(u)
            if not isinstance(rec, dict):
                unmeasured.add(u)   # could not look: the books keep it as it is, and status names it UNMEASURED
                return None
            if rec.get("status") not in ("finished", "launching", "running"):
                return None
            why = system_cause(rec)     # a running record is void only when its unit is dead (finish never ran)
            if not why:
                if rec.get("status") == "finished":
                    seen[u] = "counted"     # only an ended run's answer is final
                return None
            if kills_left and kills_left(book, x, why):
                return None
            return {"cause": why, "faults": 1 + len(x.get("killed_before") or [])}

        moved = []
        for b in SYSTEM_BOOKS:
            book = s.get(b)
            if isinstance(book, dict):
                for k, x in list(book.items()):
                    v = judge(x, b)
                    if v:
                        moved.append(dict({"book": b, "key": k, "entry": book.pop(k)},
                                          **{"class": v.get("class", "void_system"), "void": None, "why": v["cause"],
                                             "unit": (_units_of(x) or [None])[0], "faults": v["faults"]}))
            elif isinstance(book, list):
                keep = []
                for x in book:
                    v = judge(x, b)
                    if v:
                        moved.append({"book": b, "key": None, "entry": x, "class": v.get("class", "void_system"), "void": None,
                                      "why": v["cause"], "unit": (_units_of(x) or [None])[0], "faults": v["faults"]})
                    else:
                        keep.append(x)
                if len(keep) != len(book):
                    s[b] = keep
        launched = {m["unit"] for m in moved if m["book"] == "launches"}
        for b in FOLLOW_LAUNCH:
            lr = s.get(b)
            if isinstance(lr, dict) and lr.get("unit") and lr["unit"] in launched:
                moved.append({"book": b, "key": None, "entry": s.pop(b), "class": "void_system",
                              "void": None, "why": "its run is void_system", "unit": lr["unit"], "faults": 0})
        items = {m["entry"].get("item") for m in moved if m["book"] == "steward"}
        rb = s.get("road_back")
        if isinstance(rb, dict) and rb.get("caused_by") in items - {None}:
            moved.append({"book": "road_back", "key": None, "entry": s.pop("road_back"), "class": "void_system",
                          "void": None, "why": "its steward run is void_system", "unit": None, "faults": 0})
        sys_units = {m["unit"] for m in moved if m.get("unit")} | {
            m.get("unit") for m in s.get("voided") or [] if m.get("class") == "void_system" and m.get("unit")}
        rel = s.get(RELEASE_BOOK)
        for k, x in list(rel.items()) if isinstance(rel, dict) else []:
            if isinstance(x, dict) and x.get("unit") in sys_units:
                moved.append({"book": RELEASE_BOOK, "key": k, "entry": rel.pop(k), "class": "void_system",
                              "void": None, "faults": 0, "unit": x["unit"],
                              "why": "its run %s is void_system: the ceiling release is given back" % x["unit"]})
        if unmeasured:
            s["void_unmeasured"] = sorted(unmeasured)
        else:
            s.pop("void_unmeasured", None)
        if moved:
            _moved(s).extend(moved)
            counted = set()
            for m in moved:     # one fault per run (or launch), however many books held it
                if m["unit"] and m["unit"] in counted:
                    continue
                counted.add(m["unit"])
                if m["faults"]:
                    s.setdefault("system_faults", []).append({"at": now, "book": m["book"], "key": m["key"],
                                                              "unit": m["unit"], "cause": m["why"], "n": m["faults"]})
                if m["unit"]:
                    seen[m["unit"]] = m.get("class") or "void_system"
            seen_out[mod] = moved
    return seen_out


def counted_fault(f):
    """-> True for a system_faults entry the fault loop counts. A launch with no unit booked "its launch never started"
    is a fault of form (form_fault): only builds before 2026-11-21 wrote one, and today's builds book such a launch
    only as "the repair of ... did not hold". Two of 2026-11-18 tripped ExplosiveKnockback's loop on 2026-11-23."""
    return isinstance(f, dict) and not (not f.get("unit")
                                        and str(f.get("cause") or "").startswith("its launch never started"))


def faults(s):
    """-> system faults on a mod since its last `clear` (a sum of kills and launch tries). The tick's own reset after a
    repair run on the fault loop ended (auto_cleared, form_fault.sync_repairs) counts as a clear."""
    cl = [c.get("at") for c in (s.get("cleared") or []) + (s.get("auto_cleared") or [])
          if isinstance(c, dict) and isinstance(c.get("at"), (int, float))]
    t0 = max(cl) if cl else 0
    return sum(int(f.get("n") or 1) for f in s.get("system_faults") or [] if counted_fault(f)
               and (f.get("at") or 0) > t0)


def void_spend(s, record):
    """-> (list dollars of the mod's void runs, units whose spend is UNMEASURED). True spend: shown apart."""
    usd, unm, seen = 0.0, [], set()
    for m in s.get("voided") or []:
        u = m.get("unit")
        if not u or m["book"] in FOLLOW_LAUNCH + ("road_back",) or u in seen:
            continue
        seen.add(u)
        c = (record(u) or {}).get("cost_usd")
        if isinstance(c, (int, float)) and not isinstance(c, bool):
            usd += c
        else:
            unm.append(u)
    return usd, unm


# ---- a Designer stage.json ------------------------------------------------------------------------------------------

def _names(item, text):
    return bool(item) and bool(re.search(r"(?<![A-Z0-9_])%s(?![A-Z0-9_])" % re.escape(item), str(text or "")))


def sync_stage(st, cur=None):
    """Make one concept's stage.json agree with the standing voids, in place: a void judge's coverage round (and its
    -reader), a void run's result and its open/close/retry/over_budget history rows move to st["voided"]["moved"]; a
    coverage release a void run applied is un-applied: the grant it spent stands again, and the stop and block it
    lifted are put back. Budget charges stay (the spend is true) and their refs are listed in st["voided"]["spend_refs"]
    so coverage_judge.rounds builds no round from them. An unvoid puts everything back. -> st."""
    cur = active() if cur is None else cur
    if not isinstance(st, dict):
        return st
    # a verify run's void names an item but applied no coverage look: it is never attributed one by that name
    cur = {u: r for u, r in cur.items() if not VERIFY_RUN.match(str(u))}
    vd = st.get("voided") if isinstance(st.get("voided"), dict) else {}
    for m in [m for m in vd.get("moved") or [] if m.get("unit") not in cur]:
        _stage_restore(st, m)
        vd["moved"].remove(m)
    units = set(cur)

    def unit_of(field, x):
        if not isinstance(x, dict):
            return None
        if field == "coverage_rounds":
            j = str(x.get("judge") or "")
            return next((u for u in units if j == u or j.startswith(u + "-")), None)
        if field == "results":
            return x.get("run") if x.get("run") in units else None
        if field == "history":
            w = str(x.get("why") or "")
            if x.get("what") in ("open", "close", "retry", "over_budget"):
                return next((u for u in units if re.search(r"run %s\b" % re.escape(u), w)), None)
            if x.get("what") == "coverage_release":
                return next((u for u, r in cur.items() if _names(r.get("item"), w)), None)
        if field == "coverage_releases":
            return next((u for u, r in cur.items() if _names(r.get("item"), x.get("why"))), None)
        return None

    moved = []
    for field in ("coverage_rounds", "results", "history", "coverage_releases"):
        lst = st.get(field)
        if not isinstance(lst, list):
            continue
        keep = []
        for n, x in enumerate(lst):
            u = unit_of(field, x)
            if u:
                moved.append({"field": field, "index": n, "entry": x, "unit": u, "void": cur[u].get("id"),
                              "why": cur[u].get("why"), "after": copy.deepcopy(lst[n - 1]) if n else None,
                              "before": copy.deepcopy(lst[n + 1]) if n + 1 < len(lst) else None, "first": n == 0})
            else:
                keep.append(x)
        st[field] = keep
    for m in moved:
        if m["field"] == "coverage_releases" and m["entry"].get("granted_at"):
            m["fields_before"] = {k: copy.deepcopy(st.get(k)) for k in ("coverage_release_granted", "coverage_stop",
                                                                        "status", "blocked_on")}
            m["fields_absent"] = [k for k in m["fields_before"] if k not in st]
            if not isinstance(st.get("coverage_release_granted"), dict):
                st["coverage_release_granted"] = {"at": m["entry"]["granted_at"], "why": m["entry"].get("granted_why"),
                                                  "after": list(m["entry"].get("after") or [])}
            stop = _stop_before(st, m["entry"].get("at"))
            if stop and not st.get("coverage_stop"):
                st["coverage_stop"] = {"at": stop["at"], "why": stop["short"]}
                if st.get("status") != "blocked":
                    st["status"], st["blocked_on"] = "blocked", stop["on"]
            m["fields_set"] = {k: copy.deepcopy(st.get(k)) for k in m["fields_before"]}
    refs = sorted({str(c.get("ref") or "") for c in (st.get("budget") or {}).get("charges") or []
                   if isinstance(c, dict) and any(str(c.get("ref") or "") in (u, "run " + u) for u in units)})
    if moved or vd.get("moved") or refs:
        vd.setdefault("moved", []).extend(moved)
        vd["spend_refs"] = refs
        st["voided"] = vd
    elif "voided" in st:
        st.pop("voided")
    return st


def _stop_before(st, at):
    """-> the last coverage_stop history row before `at`: {at, short, on}."""
    t = parse_time(at) or float("inf")
    rows = [h for h in st.get("history") or [] if isinstance(h, dict) and h.get("what") == "coverage_stop"
            and (parse_time(h.get("at")) or 0) <= t]
    if not rows:
        return None
    on = str(rows[-1].get("why") or "")
    short = on.split(": ", 1)[-1].split("; judging stopped", 1)[0]
    return {"at": rows[-1].get("at"), "short": short, "on": on}


def _stage_restore(st, m):
    """Put a moved stage entry back in time order (its `at` among the entries now there; an entry with no time goes to
    its old index), and reverse only the fields that still hold what the void installed: a grant, stop or status set
    since (a newer grant, say) stands."""
    lst = st.setdefault(m["field"], [])
    t = parse_time((m["entry"] or {}).get("at")) if isinstance(m.get("entry"), dict) else None
    nb = [n for n, x in enumerate(lst) if m.get("after") is not None and x == m["after"]]
    na = [n for n, x in enumerate(lst) if m.get("before") is not None and x == m["before"]]
    if m.get("first"):
        pos = 0                 # it led the list: it leads again
    elif nb:
        pos = nb[-1] + 1        # straight after the entry it followed (ties in time keep their order)
    elif na:
        pos = na[0]             # else straight before the entry that followed it
    elif t is None:
        pos = min(int(m.get("index") or 0), len(lst))
    else:
        pos = next((n for n, x in enumerate(lst) if isinstance(x, dict) and (parse_time(x.get("at")) or 0) > t),
                   len(lst))
    lst.insert(pos, m["entry"])
    fb, fs = m.get("fields_before") or {}, m.get("fields_set") or {}
    grant = "coverage_release_granted"
    group = [k for k in fb if k != grant]       # the stop, the status and the block reason move together
    for keys in ([grant], group):
        if any(k in fs and st.get(k) != fs[k] for k in keys):
            continue        # changed since the void: the newer state stands, as a whole
        for k in keys:
            if k in (m.get("fields_absent") or []):
                st.pop(k, None)
            elif k in fb:
                st[k] = fb[k]


def stage_spend_refs(st):
    return set((st.get("voided") or {}).get("spend_refs") or []) if isinstance(st, dict) else set()


def status_lines(st, record=None):
    """-> one line per voided run on each mod (VOID hand or VOID system, with its why), plus the system-fault count and
    the void spend in weighted tokens."""
    import detached_helper as DH
    record = record or DH.read_record
    out = []
    for mod, s in sorted(((st or {}).get("mods") or {}).items()):
        if not isinstance(s, dict) or not (s.get("voided") or s.get("system_faults") or s.get("void_unmeasured")):
            continue
        seen = set()
        for m in s.get("voided") or []:
            key = (m.get("unit"), m.get("class"))
            if key in seen or not m.get("unit"):
                continue
            seen.add(key)
            out.append("%s: VOID %s %s (%s): %s" % (mod, "hand" if m["class"] == "void_hand" else "system",
                                                    m["unit"], m["book"], m.get("why")))
        for m in s.get("voided") or []:
            if m.get("collision"):
                out.append("%s: UNVOID WAITING %s: %s" % (mod, m.get("unit"), m["collision"]))
        if s.get("void_unmeasured"):
            out.append("%s: UNMEASURED run record(s), counted as the books had them: %s" % (
                mod, ", ".join(s["void_unmeasured"])))
        usd, unm = void_spend(s, record)
        try:
            import maturation_dispatch as MD
            import role_launch as RL
            spent = MD.wt(RL.list_usd_to_weighted(usd))     # MD.wt formats weighted tokens (2026-11-26)
        except Exception:  # noqa: BLE001
            spent = "USD %.2f" % usd
        out.append("%s: void spend %s (true spend, shown apart)%s; system faults %d since the last clear (limit %d)" % (
            mod, spent, "; UNMEASURED for %s" % ", ".join(unm) if unm else "", faults(s), SYSTEM_FAULT_LIMIT))
    return out


# ---- the verdict file a void judge left ------------------------------------------------------------------------------

VERDICT = "coverage_verdict.json"


def _at(text):
    try:
        return parse_time((json.loads(text) or {}).get("at")) or 0
    except (ValueError, AttributeError):
        return 0


def landable(root, paths):
    """-> the paths a void verb must land: those that differ from HEAD or are untracked. A void whose rewritten
    stage.json equals HEAD has nothing to land, and ./publish refuses an empty landing (exit 1), which the verb read
    as WRITTEN, NOT LANDED (RIMMANDRAKE_SKIP_VOID_LANDING_WHEN_STAGE_FILE_UNCHANGED). Where git cannot look, every
    path stays landable: could not look is not unchanged."""
    import subprocess
    if not paths:
        return []
    try:
        r = subprocess.run(["git", "-C", root, "status", "--porcelain", "--untracked-files=all", "--"] + list(paths),
                           capture_output=True, text=True, timeout=120)   # hang guard on a slow mount; a real status takes about 2 s
    except (OSError, subprocess.TimeoutExpired):
        return list(paths)
    if r.returncode != 0:
        return list(paths)
    dirty = {ln[3:].strip().strip('"') for ln in r.stdout.splitlines() if len(ln) > 3}
    return [p for p in paths if os.path.normpath(p) in {os.path.normpath(d) for d in dirty}]


def swap_verdict(root, mod, judge, back=False, runner=None):
    """A VOID coverage judge's coverage_verdict.json is kept as evidence (coverage_verdict.void.<judge>.json) and the
    verdict before it, read from git, is put back: the next look checks the look before the void one, as if it never
    ran. back=True reverses it. -> [repo-relative paths written], [] when there was nothing to do."""
    import subprocess
    runner = runner or subprocess.run
    d = os.path.join(root, "design", "concepts", mod)
    vf, arch = os.path.join(d, VERDICT), os.path.join(d, "coverage_verdict.void.%s.json" % judge)
    rel = lambda q: os.path.relpath(q, root)    # noqa: E731

    def judge_of(text):
        try:
            return (json.loads(text) or {}).get("judge")
        except ValueError:
            return None
    try:
        cur = open(vf, encoding="utf-8").read()
    except OSError:
        cur = None
    meta = arch[:-len(".json")] + ".meta.json"
    if back:
        if not os.path.exists(arch):
            return []
        arch_text = open(arch, encoding="utf-8").read()
        if cur is not None and judge_of(cur) not in active() and _at(cur) > _at(arch_text):
            return []       # a newer verdict landed since the void: it stands; the archive stays as evidence
        with open(vf, "w", encoding="utf-8") as f:
            f.write(open(arch, encoding="utf-8").read())
        os.remove(arch)
        if os.path.exists(meta):
            os.remove(meta)
        return [rel(vf), rel(arch), rel(meta)]
    if cur is None or judge_of(cur) != judge:
        return []
    void = set(active()) | {judge}
    old = None
    r = runner(["git", "-C", root, "log", "--format=%H", "--", rel(vf)], capture_output=True, text=True, timeout=60)
    for sha in (r.stdout or "").split():
        g = runner(["git", "-C", root, "show", "%s:%s" % (sha, rel(vf))], capture_output=True, text=True, timeout=60)
        if g.returncode == 0 and judge_of(g.stdout) is not None and judge_of(g.stdout) not in void:
            old = g.stdout      # the latest verdict of a judge that is not void
            break
    with open(arch, "w", encoding="utf-8") as f:
        f.write(cur)
    with open(meta, "w", encoding="utf-8") as f:
        json.dump({"void_judge": judge, "put_back": judge_of(old) if old else None}, f, indent=1)
    if old is None:     # no earlier verdict: the file goes, and prior_verdict reads none (round 1's open search)
        os.remove(vf)
    else:
        with open(vf, "w", encoding="utf-8") as f:
            f.write(old)
    return [rel(vf), rel(arch), rel(meta)]
