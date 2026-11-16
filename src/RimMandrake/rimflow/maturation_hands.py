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
  hand_run          a detached run the tick did not launch that does a stage's work on an advancing mod: a blind judge,
                    an in-game driver, a fix on one of the tick's own road-back or stop tickets, or a run live at the
                    offline build with build work owed. Any other run on the mod (a feature build) is not one
  hand_move         a stage move that names no run (maturation.py advance writes its run's unit) and that no run the
                    tick launched was live for
  hand_close        a close, drop or supersede, from a window, of an item whose run the tick launched
  settings_edit     a changed value in maturation_dispatch.json (a doc-only edit is none)
  tick_gap          the tick did not run for GAP_S or more (paused, stopped or dead)
  manual            written by `record`

Each act is one line in <state dir>/hand_acts.jsonl, once (its id). A fold is one line in hand_folds.jsonl. An act
older than the census (BASELINE_TS) is folded by the census; one whose reason names an item on the ledger is folded by
that item. Any other act is open until `fold`. The reading's `hand_acts` block counts the open ones and the overdue
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


def tick_units(s):
    """-> ({unit: (start, )}, {item}) of the runs the tick launched for one mod, from its books."""
    units, items = set(), set()
    for x in (s.get("launches") or []) + (s.get("blind_auto") or []) + (s.get("ingame_auto") or []):
        if isinstance(x, dict):
            units.update([x.get("unit")] + list(x.get("killed_before") or []))
            if x.get("unit"):
                items.add(x.get("item"))
    for book in ("steward", "fixers"):
        for x in (s.get(book) or {}).values():
            if isinstance(x, dict) and x.get("unit"):
                units.add(x["unit"])
                items.add(x.get("item"))
    units.discard(None)
    items.discard(None)
    return units, items


def _fix_queue(s):
    """The tick's own fix tickets for a mod: its fixer keys and what its road back names."""
    ids = set((s.get("fixers") or {}).keys())
    rb = s.get("road_back") or {}
    for k in ("items", "ids"):
        if isinstance(rb.get(k), list):
            ids.update(str(x) for x in rb[k])
    return ids


def collect(root, cfg, st, facts, now, fx=None):
    """-> the hand acts visible now (already-recorded ones included; observe keeps each id once)."""
    import maturation_dispatch as MD
    fx = fx or {}
    h = st.setdefault("hands", {})
    since = float(h.setdefault("since", now))
    out = []
    recs, _bad = MD.read_releases()
    for r in recs:
        if not r.get("auto"):
            out.append(_act(r["id"], ts(r["ts"]) or now, "ceiling_release", r["mod"],
                            "%s released %s past the ceiling at %s (read %s)" % (
                                r["by"], MD.wt(r["release_usd"]), r["stage"], MD.wt(r["read_usd"])), r["why"]))
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
        w = s.get("watch") or {}
        for r in runs:
            at, item = r.get("at"), str(r.get("item") or "")
            if r["unit"] in units or not isinstance(at, (int, float)) or at <= since:
                continue
            what = ("a blind judge" if "BLIND" in item.upper() else
                    "an in-game driver" if MD._is_ingame_item(item) else
                    "a fix on the tick's own ticket" if item in queue else
                    "a run at the offline build with %s bars refused" % w.get("refused")
                    if (w.get("unit") == r["unit"] and not w.get("ours") and f.get("stage") == "offline_build"
                        and (w.get("refused") or 0) > 0) else None)
            if what:
                out.append(_act("run-%s" % r["unit"], at, "hand_run", mod, "%s launched by hand: %s on %s" % (
                    what, r["unit"], item)))
        rec = _json(os.path.join(root, "design", "concepts", mod, "version", "stage_record.json")) or {}
        spans = [(r.get("at"), r.get("end")) for r in runs if r["unit"] in units and isinstance(r.get("at"), (int, float))]
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
        hid = hashlib.sha1(json.dumps([was, vals], sort_keys=True).encode()).hexdigest()[:10]
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


def observe(root, cfg, st, facts, now, rd, fx=None):
    """One pass: record the new acts, fold what folds by itself, write rd['hand_acts'] and a Needs Conductor line per
    overdue act. -> rd. A failure in here must never cost the tick: the caller guards it."""
    fx = fx or {}
    have = {a["id"] for a in read_acts()}
    new = [a for a in collect(root, cfg, st, facts, now, fx) if a["id"] not in have]
    seen, known = set(), None
    for a in new:
        if a["id"] in seen:
            continue
        seen.add(a["id"])
        _append(ACTS, dict(a, recorded=now))
        if a["at"] <= BASELINE_TS:
            _append(FOLDS, {"id": a["id"], "at": now, "census": BASELINE_FOLD, "by": "maturation_hands"})
            continue
        named = ID_RX.findall(a["why"])
        if named:
            known = _known(fx) if known is None else known
            hit = [n for n in named if n in known]
            if hit:
                _append(FOLDS, {"id": a["id"], "at": now, "item": hit[0], "by": "maturation_hands",
                                "why": "its reason names the item"})
    acts, folds = read_acts(), read_folds()
    open_ = [a for a in acts if a["id"] not in folds]
    over = [a for a in open_ if now - a["at"] >= DAY_S]
    rd["hand_acts"] = {"recorded": len(acts), "open": len(open_), "overdue": len(over),
                       "oldest_h": round(max([now - a["at"] for a in open_] or [0]) / 3600.0, 1),
                       "ids": [a["id"] for a in over][:8], "alarm": ALARM_NAME}
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
    """-> (rc, text). The act must be recorded; --item must be on the ledger; --census must be text a census file holds."""
    if act_id not in {a["id"] for a in read_acts()}:
        return 2, "REFUSED: no hand act %s is recorded (`maturation_hands.py list --all` shows every id)" % act_id
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
    _append(FOLDS, rec)
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
        aid = "manual-%s" % hashlib.sha1(("%s|%s|%s|%d" % (o.kind, o.mod, o.what, now)).encode()).hexdigest()[:10]
        _append(ACTS, dict(_act(aid, now, o.kind, o.mod, o.what, o.why), recorded=now))
        print("RECORDED %s; it needs a follow-up within a day: maturation_hands.py fold %s --item <ID>" % (aid, aid))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
