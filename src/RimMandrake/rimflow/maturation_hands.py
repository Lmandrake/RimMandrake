#!/usr/bin/env python3
"""maturation_hands.py: every hand act on the Maturation Pipeline, recorded where the Dispatch tick reads it, and an
alarm for one that nobody followed up. No model, no tokens.

Item RIMMANDRAKE_RECORD_HAND_ACTS_TICK_ONLY_SAW_ITS_OWN. The owner, 2026-11-15 about 1:45 PM PST: "ensure that the
wisdom of what it had to fix has been built into the Pipeline itself so that it will do the right thing from now on,
NOT merely rely on Conductor/Owner to notice and request an inspection." The census of every hand act up to that hour
is design/RimMandrake/pipeline_interventions_census_2026-11-15.md; this keeps the census going by program.

    python3 src/RimMandrake/rimflow/maturation_hands.py list [--all]      the open hand acts (--all: folded ones too)
    python3 src/RimMandrake/rimflow/maturation_hands.py fold ACT --item ID [--why "..."]
            the act is followed up by ledger item ID (it must exist): the fix that makes the hand unnecessary
    python3 src/RimMandrake/rimflow/maturation_hands.py fold ACT --census "<row>" [--why "..."]
            the act is one more of a lesson a census file already holds (the row's name, verbatim, in a
            design/RimMandrake/pipeline_interventions_census_*.md)
    python3 src/RimMandrake/rimflow/maturation_hands.py record --kind KIND --mod MOD --what "..." [--why "..."]
            a hand act the tick cannot see (a timer paused, a run stopped by hand)

A hand act (observe, called by maturation_dispatch.tick on every applied tick):
  ceiling_release   a `maturation_dispatch.py release` record (the tick's own killed-run refund is marked auto: not one)
  clear             a `maturation_dispatch.py clear`
  coverage_release  a `coverage_judge.py release` or a grant written by hand (a release a grant made is the grant's)
  hand_run          a detached run that neither the tick nor left_open_continue.py launched and that does a stage's
                    work on an advancing mod: a blind judge, an in-game driver, a fix on one of the tick's own road-back or stop tickets, or a run live at the
                    offline build with build work owed. Any other run on the mod (a feature build) is not one
  hand_move         a stage move that names no run (maturation.py advance writes its run's unit) and that no run the
                    tick launched was live for
  hand_close        a close, drop or supersede, from a window, of an item whose run the tick launched
  settings_edit     a changed value in maturation_dispatch.json (a doc-only edit is none)
  tick_gap          the tick did not run for GAP_S or more (paused, stopped or dead)
  manual            written by `record`

Each act is one line in <state dir>/hand_acts.jsonl, once (its id). A fold is one line in hand_folds.jsonl. An act
older than the census (BASELINE_TS) is folded by the census; one whose reason names an item on the ledger is folded by
that item. A move off his_walk by OWNER is his walk verdict (one of his five acts) and folds by itself. Any other act
is open until `fold`. The reading's `hand_acts` block counts the open ones and the overdue
ones (open for DAY_S); each overdue act is a Needs Conductor line, and ops_watch reads maturation.hand_acts_overdue:
over 0 raises OPS_MATURATION_HAND_ACT_UNFOLDED (ops_watch_rules.json), one fixed item id.
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ACTS, FOLDS = "hand_acts.jsonl", "hand_folds.jsonl"
BASELINE_TS = 1794779100.0      # 2026-11-15 1:45 PM PST: the census covers every act up to here
BASELINE_FOLD = "design/RimMandrake/pipeline_interventions_census_2026-11-15.md (every act before it was written)"
DAY_S = 86400
GAP_S = 900                     # 15 missed ticks
LEDGER_S = 600                  # the ledger is read for hand closes this often, not every tick
CENSUS_GLOB = os.path.join("design", "RimMandrake", "pipeline_interventions_census_*.md")
ALARM_NAME = "OPS_MATURATION_HAND_ACT_UNFOLDED"
ID_RX = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b")
NOT_HANDS = ("RUNNER", "DISPATCHER")    # the seats the tick and the Dispatcher write as


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ts(s):
    if isinstance(s, (int, float)) and not isinstance(s, bool):
        return float(s)
    try:
        return dt.datetime.strptime(str(s)[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp()
    except ValueError:
        return None


def _sdir():
    import maturation_dispatch as MD
    return MD.sdir()


def _lines(name):
    out = []
    try:
        with open(os.path.join(_sdir(), name), encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict) and r.get("id"):
                    out.append(r)
    except FileNotFoundError:
        pass
    return out


def _append(name, rec):
    with open(os.path.join(_sdir(), name), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")


def read_acts():
    """-> every recorded act, oldest first, each id once."""
    seen, out = set(), []
    for r in _lines(ACTS):
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out


def read_folds():
    """-> {act id: its last fold}."""
    return {r["id"]: r for r in _lines(FOLDS)}


def _json(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _act(aid, at, kind, mod, what, why=""):
    return {"id": aid, "at": at, "kind": kind, "mod": mod, "what": what, "why": str(why or "")}


def continued_from(unit, fx=None):
    """The run that left_open_continue.py continued as `unit`, or None (no parent, or its record cannot be read: then the
    run still counts as a hand's). A continuation is a program's launch, never a hand act."""
    get = (fx or {}).get("record")
    if get is None:
        import detached_helper as DH
        get = DH.read_record
    rec = get(unit)
    return rec.get("continued_from") if rec else None


def tick_units(s):
    """-> ({unit}, {item}): the units the tick launched (or tried to) for one mod, and their items, from its books."""
    units, items = set(), set()
    # a failed launch is booked unit=None and `tried` (maturation_dispatch.tried_unit): its record is the tick's own
    for x in (s.get("launches") or []) + (s.get("blind_auto") or []) + (s.get("ingame_auto") or []) + \
            (s.get("holder_road_back") or []):
        if isinstance(x, dict):
            units.update([x.get("unit"), x.get("tried")] + list(x.get("killed_before") or []))
            if x.get("unit"):
                items.add(x.get("item"))
    for book in ("steward", "fixers"):
        for x in (s.get(book) or {}).values():
            if isinstance(x, dict) and (x.get("unit") or x.get("tried")):
                units.update([x.get("unit"), x.get("tried")])
                items.add(x.get("item")) if x.get("unit") else None
    # a voided run's entry is moved out of its book into `voided` (run_void.sync_dispatch): still the tick's own
    # (RIMMANDRAKE_OWN_VOIDED_TICK_RUNS_ARCHIVE_HID_THEM)
    for m in s.get("voided") or []:
        x = m.get("entry") if isinstance(m, dict) else None
        if isinstance(x, dict):
            units.update([m.get("unit"), x.get("unit"), x.get("tried")] + list(x.get("killed_before") or []))
            items.add(x.get("item")) if x.get("unit") else None
    # `maturation_dispatch.py clear` moves ended entries to cleared[*].released: still the tick's own
    # (RIMMANDRAKE_OWN_CLEARED_TICK_RUNS_ALARM_CRIED_FIVE)
    for c in s.get("cleared") or []:
        rel = c.get("released") if isinstance(c, dict) else None
        if not isinstance(rel, dict):
            continue
        for book in ("blind_auto", "ingame_auto", "steward", "fixers"):
            b = rel.get(book)
            xs = b if isinstance(b, list) else list(b.values()) if isinstance(b, dict) else []
            for x in xs:
                if isinstance(x, dict):
                    units.update([x.get("unit"), x.get("tried")] + list(x.get("killed_before") or []))
                    items.add(x.get("item")) if x.get("unit") else None
    units.discard(None)
    items.discard(None)
    return units, items


def _fix_queue(s):
    """The tick's own fix tickets for a mod: its fixer keys and what its road back names."""
    ids = {str(k).split("|")[0] for k in (s.get("fixers") or {})}     # a Test Pilot sitting's key is ITEM|pilot|<tsn>
    # a voided fixer's entry sits in `voided` under its book key: its ticket is still the tick's
    ids.update(str(m.get("key")).split("|")[0] for m in s.get("voided") or []
               if isinstance(m, dict) and m.get("book") == "fixers" and m.get("key") is not None)
    rb = s.get("road_back") or {}
    for k in ("items", "ids"):
        if isinstance(rb.get(k), list):
            ids.update(str(x) for x in rb[k])
    return ids


def _road_back_items(root, s, fx, h):
    """-> the items the road back's steward runs filed (caused_by them, ended ones too: a fixer may close its item
    fast), or None when the ledger could not be read (kept in h["road_back_error"] for this tick, never read as no items). The tick
    writes road_back as {caused_by, at, from}: a fixer it has not booked yet is found here only
    (RIMMANDRAKE_COUNT_HAND_FIX_ON_UNBOOKED_ROAD_BACK_TICKET)."""
    rb = s.get("road_back")
    if not isinstance(rb, dict) or not rb.get("caused_by"):
        return set()
    import maturation_autonomy as AUT
    ids = AUT._road_back_ids(s, rb)
    try:
        if "caused_by" in fx:
            got = fx["caused_by"](ids)
        else:
            import maturation as M
            got = [x["id"] for x in M.ledger_items_caused_by(root, ids, ended_too=True)]
    except Exception as e:      # noqa: BLE001  a blind ledger costs this source, never the tick
        h["road_back_error"] = "%s: %s" % (e.__class__.__name__, e)
        return None
    return {str(x) for x in got}


def collect(root, cfg, st, facts, now, fx=None):
    """-> the hand acts visible now (already-recorded ones included; observe keeps each id once)."""
    import maturation_dispatch as MD
    fx = fx or {}
    h = st.setdefault("hands", {})
    since = float(h.setdefault("since", now))
    h.pop("road_back_error", None)      # this tick's reading only
    out = []
    recs, _bad = MD.read_releases()
    for r in recs:
        if not r.get("auto"):
            out.append(_act(r["id"], ts(r["ts"]) or now, "ceiling_release", r["mod"],
                            "%s released %s past the ceiling at %s (read %s)" % (
                                r["by"], MD.wt(r["release_tokens"]), r["stage"], MD.wt(r["read_tokens"])), r["why"]))
    mods = st.get("mods") or {}
    names = list(dict.fromkeys(list(cfg.get("advancing") or []) + list(mods) + list(facts or {})))
    for mod in names:
        s = mods.get(mod) or {}
        for c in s.get("cleared") or []:
            if isinstance(c, dict) and isinstance(c.get("at"), (int, float)):
                out.append(_act("clear-%s-%d" % (mod, c["at"]), c["at"], "clear", mod, "a stop was cleared by hand (was: %s)"
                                % ((c.get("was") or {}).get("why") or "not stopped"), c.get("why")))
        dst = _json(os.path.join(root, "design", "concepts", mod, "stage.json")) or {}
        for c in dst.get("coverage_releases") or []:
            if isinstance(c, dict) and not c.get("granted_at") and ts(c.get("at")):
                out.append(_act("covrel-%s-%d" % (mod, ts(c["at"])), ts(c["at"]), "coverage_release", mod,
                                "coverage judging released for one more look", c.get("why")))
        g = dst.get("coverage_release_granted")
        if isinstance(g, dict) and ts(g.get("at")):
            out.append(_act("covgrant-%s-%d" % (mod, ts(g["at"])), ts(g["at"]), "coverage_release", mod,
                            "a coverage release granted, to take effect after %s" % ", ".join(g.get("after") or []),
                            g.get("why")))
        units, _items = tick_units(s)
        f = (facts or {}).get(mod) or {}
        runs = [r for r in f.get("runs_seen") or [] if isinstance(r, dict) and r.get("unit")]
        queue = _fix_queue(s)
        rb_items = False        # read once per mod, only when a run needs it
        w = s.get("watch") or {}
        for r in runs:
            at, item = r.get("at"), str(r.get("item") or "")
            # a launch record that never ran (launch_failed) worked on nothing: no run, no hand
            if r["unit"] in units or r.get("ran") is False or not isinstance(at, (int, float)) or at <= since:
                continue
            if item not in queue and not MD._is_blind_item(item) and not MD._is_ingame_item(item):
                if rb_items is False:
                    rb_items = _road_back_items(root, s, fx, h)
                if rb_items and item in rb_items:
                    queue = queue | {item}
            what = ("a blind judge" if MD._is_blind_item(item) else
                    "an in-game driver" if MD._is_ingame_item(item) else
                    "a fix on the tick's own ticket" if item in queue else
                    "a run at the offline build with %s bars refused" % w.get("refused")
                    if (w.get("unit") == r["unit"] and not w.get("ours") and f.get("stage") == "offline_build"
                        and (w.get("refused") or 0) > 0) else None)
            if what and not continued_from(r["unit"], fx):
                out.append(_act("run-%s" % r["unit"], at, "hand_run", mod, "%s launched by hand: %s on %s" % (
                    what, r["unit"], item)))
        rec = _json(os.path.join(root, "design", "concepts", mod, "version", "stage_record.json")) or {}
        # a tick launch that never ran (launch_failed, end None) is no span: it would read live to now and hide hand moves
        spans = [(r.get("at"), r.get("end")) for r in runs if r["unit"] in units and r.get("ran") is not False
                 and isinstance(r.get("at"), (int, float))]
        for m in rec.get("moves") or []:
            at = ts(m.get("at")) if isinstance(m, dict) else None
            if at is None or at <= since or m.get("unit"):
                continue
            if any(a - 120 <= at <= (e if isinstance(e, (int, float)) else now) + 120 for a, e in spans):
                continue        # a run the tick launched was live then (a run from before moves carried their unit)
            out.append(_act("move-%s-%d" % (mod, at), at, "hand_move", mod, "moved %s -> %s by %s, naming no run" % (
                m.get("from"), m.get("to"), m.get("by")), m.get("why")))
    # hand closes of the tick's own items: the ledger, read every LEDGER_S
    if "events" in fx or now - float(h.get("ledger_at") or 0) >= LEDGER_S:
        h["ledger_at"] = now
        mine = {}
        for mod in names:
            for it in tick_units(mods.get(mod) or {})[1]:
                mine[it] = mod
        try:
            if "events" in fx:
                evs = fx["events"]()
            else:
                import model
                evs = model.read()
        except Exception as e:      # noqa: BLE001  a blind ledger costs this source, never the tick
            h["ledger_error"] = "%s: %s" % (e.__class__.__name__, e)
            evs = []
        for e in evs:
            if (e.get("event") in ("close", "drop", "supersede") and e.get("id") in mine and not e.get("role_unit")
                    and e.get("seat") not in NOT_HANDS and (ts(e.get("ts")) or 0) > since):
                at = ts(e["ts"])
                out.append(_act("close-%s-%d" % (e["id"], at), at, "hand_close", mine[e["id"]],
                                "%s of %s by %s from a window, not by its run" % (e["event"], e["id"], e.get("seat")),
                                e.get("why") or e.get("reason")))
    # a settings edit: the shipped values, doc keys aside
    vals = {k: v for k, v in sorted(cfg.items()) if not str(k).startswith("_")}
    was = h.get("cfg")
    if isinstance(was, dict) and was != vals:
        diff = ["%s: %s -> %s" % (k, json.dumps(was.get(k)), json.dumps(vals.get(k)))
                for k in sorted(set(was) | set(vals)) if was.get(k) != vals.get(k)]
        # keyed by tick time too: 4 -> 6, back to 4, then 6 again on later ticks is three edits
        # (RIMMANDRAKE_KEY_SETTINGS_EDITS_BY_OCCURRENCE_ABAB_LOST_ONE)
        hid = hashlib.sha1(json.dumps([was, vals, now], sort_keys=True).encode()).hexdigest()[:10]
        out.append(_act("settings-%s" % hid, now, "settings_edit", "-", "maturation_dispatch.json changed: %s" % "; ".join(diff)))
    h["cfg"] = vals
    last = h.get("last_tick")
    if isinstance(last, (int, float)) and now - last >= GAP_S and not fx.get("quiet_gap"):
        out.append(_act("gap-%d" % last, last, "tick_gap", "-", "the tick did not run for %d min (%s to %s UTC): paused, "
                        "stopped or dead" % ((now - last) // 60, iso(last), iso(now))))
    h["last_tick"] = now
    return out


def _known(fx):
    if fx and "known" in fx:
        return fx["known"]()
    import helper_checkpoint as HC
    return HC.known_items()


def _fold_named(fx, h, fresh, now):
    """Fold every open act whose reason names a ledger item: this tick's new acts at once, the older open ones every
    LEDGER_S (one recorded on a tick whose ledger read failed, or by `record --why`), so none stays open for want of a
    second look (RIMMANDRAKE_FOLD_RECORDED_HAND_ACTS_AFTER_KNOWN_FAILS). A read that fails, or reads no item at all,
    is could-not-look: h["fold_error"], nothing folded, retried next tick; never a verdict on the acts."""
    # a read that failed last tick is retried now, over every open act, not only at the next due sweep
    sweep = now - float(h.get("fold_at") or 0) >= LEDGER_S or bool(h.get("fold_error"))
    folds = read_folds()
    todo = [(a, ID_RX.findall(a.get("why") or "")) for a in read_acts()
            if a["id"] not in folds and (a["id"] in fresh or sweep)]
    todo = [(a, named) for a, named in todo if named]
    if not todo:
        if sweep:
            h["fold_at"] = now
            h.pop("fold_error", None)   # nothing left to look up: no lookup is failing
        return
    try:
        known = _known(fx)
    except Exception as e:      # noqa: BLE001  a blind ledger costs this fold, never the tick
        h["fold_error"] = "%s: %s" % (e.__class__.__name__, e)
        return
    if not known:
        h["fold_error"] = "the ledger read no items at all (blind)"
        return
    h.pop("fold_error", None)
    if sweep:
        h["fold_at"] = now
    for a, named in todo:
        hit = [n for n in named if n in known]
        if hit:
            _append(FOLDS, {"id": a["id"], "at": now, "item": hit[0], "by": "maturation_hands",
                            "why": "its reason names the item"})


WALK_VERDICT = "moved his_walk -> "


def _fold_his_walk(now):
    """Fold every open hand_move off his_walk by OWNER: his walk verdict (a pass, or the road back he gave) is his act,
    one of his five acts (the pass at his walk). No run makes it, so there is no hand judgement to build into the
    pipeline; read as a hand act it sat overdue at his rung (Pyrelands 0.1.0, 43 h, 2026-11-26;
    RIMMANDRAKE_FOLD_HIS_WALK_VERDICT_NOT_A_HAND_ACT). Reads only the acts file, so it cannot be blind."""
    folds = read_folds()
    for a in read_acts():
        w = str(a.get("what") or "")
        if a["id"] in folds or a.get("kind") != "hand_move" or not w.startswith(WALK_VERDICT) or " by OWNER," not in w:
            continue
        _append(FOLDS, {"id": a["id"], "at": now, "by": "maturation_hands",
                        "why": "his walk verdict: his act, one of his five acts (the pass at his walk), not a hand's"})


def _fold_tick_own(st, now, fx=None):
    """Fold every open hand_run act whose unit the tick's current books hold: it was recorded as a hand run before a
    tick_units fix taught the books to see it (voided 11-18, cleared 11-20), and collect never looks at a recorded act
    again, so it stayed open and overdue for good (RIMMANDRAKE_FOLD_HAND_RUNS_THE_BOOKS_NOW_OWN: seven such acts at his
    rung, 11-21). Reads only state.json, so it cannot be blind the way a ledger read can. Also folds a continuation."""
    folds = read_folds()
    mods = st.get("mods") or {}
    units = {}
    for a in read_acts():
        if a["id"] in folds or a.get("kind") != "hand_run" or not str(a["id"]).startswith("run-"):
            continue
        mod = a.get("mod")
        if mod not in units:
            units[mod] = tick_units(mods.get(mod) or {})[0]
        if a["id"][len("run-"):] in units[mod]:
            _append(FOLDS, {"id": a["id"], "at": now, "by": "maturation_hands",
                            "why": "the tick's own run by its current books (recorded as a hand run before a "
                                   "tick_units fix)"})
            continue
        parent = continued_from(a["id"][len("run-"):], fx)
        if parent:
            _append(FOLDS, {"id": a["id"], "at": now, "by": "maturation_hands",
                            "why": "left_open_continue.py continued %s: a program launched it (recorded as a hand run "
                                   "before 2026-11-23)" % parent})


def observe(root, cfg, st, facts, now, rd, fx=None):
    """One pass: record the new acts, fold what folds by itself, write rd['hand_acts'] and a Needs Conductor line per
    overdue act. -> rd. A failure in here must never cost the tick: the caller guards it."""
    fx = fx or {}
    h = st.setdefault("hands", {})
    have = {a["id"] for a in read_acts()}
    new = [a for a in collect(root, cfg, st, facts, now, fx) if a["id"] not in have]
    seen = set()
    for a in new:
        if a["id"] in seen:
            continue
        seen.add(a["id"])
        _append(ACTS, dict(a, recorded=now))
        if a["at"] <= BASELINE_TS:
            _append(FOLDS, {"id": a["id"], "at": now, "census": BASELINE_FOLD, "by": "maturation_hands"})
    _fold_named(fx, h, seen, now)
    _fold_tick_own(st, now, fx)
    _fold_his_walk(now)
    acts, folds = read_acts(), read_folds()
    open_ = [a for a in acts if a["id"] not in folds]
    over = [a for a in open_ if now - a["at"] >= DAY_S]
    rd["hand_acts"] = {"recorded": len(acts), "open": len(open_), "overdue": len(over),
                       "oldest_h": round(max([now - a["at"] for a in open_] or [0]) / 3600.0, 1),
                       "ids": [a["id"] for a in over][:8], "alarm": ALARM_NAME}
    if h.get("fold_error"):
        rd["hand_acts"]["fold_error"] = h["fold_error"]
    for a in over[:5]:
        rd.setdefault("needs_conductor", []).append(
            "hand act %s (%s on %s: %s) has had no follow-up item or census row for %d h: build the hand's judgement "
            "into the pipeline, then `python3 src/RimMandrake/rimflow/maturation_hands.py fold %s --item <ID>` (or "
            "--census \"<row>\")" % (a["id"], a["kind"], a["mod"], a["what"], (now - a["at"]) // 3600, a["id"]))
    return rd


def census_holds(root, row):
    row = str(row or "").strip()
    if len(row) < 8:
        return None
    for p in sorted(glob.glob(os.path.join(root, CENSUS_GLOB))):
        try:
            with open(p, encoding="utf-8") as f:
                if row in f.read():
                    return os.path.relpath(p, root)
        except OSError:
            continue
    return None


def fold(root, act_id, item=None, census=None, why="", by=None, fx=None, now=None):
    """-> (rc, text). --item must be on the ledger; --census must be text a census file holds. An act the tick has not
    recorded yet (`clear` prints its id before the next tick records it) is no refusal: the fold is kept, and read_folds
    applies it when the act is recorded (RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT)."""
    pending = act_id not in {a["id"] for a in read_acts()}
    if bool(item) == bool(census):
        return 2, "REFUSED: name exactly one of --item ID or --census \"<row>\""
    rec = {"id": act_id, "at": now or time.time(), "by": by or "hand", "why": str(why or "")}
    if item:
        if item not in _known(fx):
            return 2, ("REFUSED: %s is not an item on the ledger; file the follow-up first (`rimflow file`), with its "
                       "acceptance test, then fold" % item)
        rec["item"] = item
    else:
        path = census_holds(root, census)
        if not path:
            return 2, ("REFUSED: no %s file holds the row \"%s\" (give the row's name verbatim, 8 characters or more; "
                       "add the row to the census first if the lesson is new)" % (CENSUS_GLOB, census))
        rec["census"] = "%s: %s" % (path, str(census).strip())
    if pending:
        rec["pending_act"] = True
    _append(FOLDS, rec)
    if pending:
        return 0, ("KEPT: the fold of %s by %s; no hand act %s is recorded yet (the tick records it on its next pass), and "
                   "the fold applies then" % (act_id, rec.get("item") or rec["census"], act_id))
    return 0, "FOLDED %s by %s" % (act_id, rec.get("item") or rec["census"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=REPO)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--all", action="store_true")
    fo = sub.add_parser("fold")
    fo.add_argument("act")
    fo.add_argument("--item")
    fo.add_argument("--census")
    fo.add_argument("--why", default="")
    rc_ = sub.add_parser("record")
    rc_.add_argument("--kind", default="manual")
    rc_.add_argument("--mod", required=True)
    rc_.add_argument("--what", required=True)
    rc_.add_argument("--why", default="")
    o = ap.parse_args(argv)
    now = time.time()
    if o.cmd == "list":
        folds = read_folds()
        rows = [a for a in read_acts() if o.all or a["id"] not in folds]
        for a in rows:
            f = folds.get(a["id"])
            print("%s  %-16s %-18s %s%s [%s]" % (
                iso(a["at"]), a["kind"], a["mod"], a["what"], (" | why: %s" % a["why"]) if a["why"] else "",
                ("folded by %s" % (f.get("item") or f.get("census"))) if f else
                "OPEN %d h, id %s" % ((now - a["at"]) // 3600, a["id"])))
        print("%d act(s) shown, %d recorded, %d open" % (len(rows), len(read_acts()),
                                                         len([a for a in read_acts() if a["id"] not in folds])))
        return 0
    if o.cmd == "fold":
        import doorbell
        rc, text = fold(os.path.abspath(o.root), o.act, o.item, o.census, o.why, by=doorbell.seat_name() or "hand")
        print(text)
        return rc
    if o.cmd == "record":
        # one id per call: two records in one second with the same words are two acts
        # (RIMMANDRAKE_SPLIT_MANUAL_HAND_ACT_IDS_WITHIN_ONE_SECOND)
        aid = "manual-%s" % hashlib.sha1(("%s|%s|%s|%s|%r|%s" % (o.kind, o.mod, o.what, o.why, now,
                                                                 os.urandom(8).hex())).encode()).hexdigest()[:12]
        _append(ACTS, dict(_act(aid, now, o.kind, o.mod, o.what, o.why), recorded=now))
        print("RECORDED %s; it needs a follow-up within a day: maturation_hands.py fold %s --item <ID>" % (aid, aid))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
