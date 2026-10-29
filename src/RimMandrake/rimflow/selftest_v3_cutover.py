#!/usr/bin/env python3
"""Selftest: v3_cutover.py (V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY) on a throwaway ledger, lane file
and doc tree — never the repo's. Covers: the keep rule (v3: the Conductor keeps only what
needs him live — needs owner / next level L4 — plus the cutover item), a live lease deferring an item, plan writing nothing, apply
reassigning through real `reassign` events stamped with his words, flipping the lane seat, landing the
staged doc patch and recording all of it; apply re-run is a no-op; revert
undoes exactly what the record says; a question as --owner-said and a patch that no longer applies
are refused before anything is written.

    python3 src/RimMandrake/rimflow/selftest_v3_cutover.py
"""
import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from rimflow import model  # noqa: E402
import selftest_built as sb  # noqa: E402
import v3_cutover as vc  # noqa: E402

PASS, FAIL = [], []
SAID = "Once we switch over to Conductor + ispatch + Foundry, all bench items get reassigned to Dispatch-> Foundry"
DOC_BEFORE = "# FOUNDRY\n\n- BENCH owns ALL FlowWorks; you never pick one up.\n- other rule\n"
DOC_AFTER = "# FOUNDRY\n\n- You own FlowWorks and GSS since the v3 cutover.\n- other rule\n"


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def ev(n, seat, verb, iid, **kw):
    e = {"seat": seat, "event": verb, "ts": "2026-10-28T00:%02d:%02dZ" % (n // 60, n % 60), "id": iid}
    e.update(kw)
    return e


def filed(n, iid, seat="BENCH", **kw):
    d = {"for": seat, "title": "t " + iid, "kind": "task"}
    d.update(kw)
    return [ev(n, seat, "file", iid, **d)]


def fixture():
    """-> paths dict for a fresh world: ledger, lane, docs root with a staged patch."""
    root = tempfile.mkdtemp(prefix="v3_cutover_")
    led = os.path.join(root, "ledger", "events.jsonl")
    os.makedirs(os.path.dirname(led))
    evs = []
    evs += filed(0, "HOSE_FIX_MOVE_ME")                                    # plain BENCH task: moves
    evs += filed(2, "OWNER_WALK_NEEDS_HIM", needs="owner")                 # needs him: stays
    evs += filed(4, "LORE_DESIGN_MOVES_TOO", kind="design")                # v3: design work is FOUNDRY's too
    evs += filed(6, "FOUNDRY_ALREADY_OWNS", seat="FOUNDRY")                # not BENCH's: untouched
    evs += filed(8, "DOING_NO_LEASE_MOVES") + [ev(9, "BENCH", "claim", "DOING_NO_LEASE_MOVES")]
    evs += filed(10, "LEASED_NOW_DEFERS") + [
        ev(11, "BENCH", "lease", "LEASED_NOW_DEFERS", action="take", token="tok1abcd", expires="2026-10-28T01:30:00Z")]
    evs += filed(12, "DONE_ALREADY_SKIPPED") + [ev(13, "BENCH", "drop", "DONE_ALREADY_SKIPPED", reason="x")]
    evs += filed(14, vc.CUTOVER_ITEM)                                      # the cutover item itself: stays
    evs += filed(16, "L4_OWNER_ACCEPT") + [
        ev(17, "BENCH", "claim", "L4_OWNER_ACCEPT"),
        ev(18, "BENCH", "implemented", "L4_OWNER_ACCEPT", sha="a" * 12, ref="origin/main",
           criteria=[{"id": "A1", "level": "L4", "text": "he looks"}], needs="owner")]
    with open(led, "w") as fh:
        for e in evs:
            fh.write(json.dumps(e) + "\n")
    lane = os.path.join(root, "flowworks_lane.json")
    with open(lane, "w") as fh:
        json.dump({"_why": "x", "seat": "BENCH", "id_patterns": ["^HOSE_"]}, fh)
    docs = os.path.join(root, "repo")
    os.makedirs(os.path.join(docs, "infrastructure", "agents"))
    doc = os.path.join(docs, "infrastructure", "agents", "FOUNDRY.md")
    with open(doc, "w") as fh:
        fh.write(DOC_BEFORE)
    patch = os.path.join(root, "docs.patch")
    rel = "infrastructure/agents/FOUNDRY.md"
    diff = "".join(difflib.unified_diff(DOC_BEFORE.splitlines(True), DOC_AFTER.splitlines(True),
                                        "a/" + rel, "b/" + rel))
    with open(patch, "w") as fh:
        fh.write(diff)
    model.EVENTS = led
    return {"root": root, "ledger": led, "lane": lane, "repo": docs, "doc": doc, "patch": patch,
            "record": os.path.join(root, "record.json")}


def cfg(p):
    return vc.Paths(lane=p["lane"], patch=p["patch"], record=p["record"], repo=p["repo"])


def world():
    return model.replay(model.read())


def owners():
    return {i.id: (i.owner, i.state) for i in world().items.values()}


def t_classify_states_the_rule_and_splits_move_keep_defer():
    p = fixture()
    try:
        r = vc.classify(world(), now=model.epoch("2026-10-28T01:00:00Z"))
        move = {i.id for i in r["move"]}
        keep = {i.id: why for i, why in r["keep"]}
        defer = {i.id for i, _ in r["defer"]}
        assert move == {"HOSE_FIX_MOVE_ME", "DOING_NO_LEASE_MOVES", "LORE_DESIGN_MOVES_TOO"}, move
        assert set(keep) == {"OWNER_WALK_NEEDS_HIM", vc.CUTOVER_ITEM, "L4_OWNER_ACCEPT"}, keep
        assert "owner" in keep["OWNER_WALK_NEEDS_HIM"], keep
        assert "owner" in keep["L4_OWNER_ACCEPT"], keep  # L4 owed => needs=owner (model enforces)
        assert defer == {"LEASED_NOW_DEFERS"}, defer
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_plan_writes_nothing():
    p = fixture()
    try:
        before = open(p["ledger"]).read(), open(p["lane"]).read(), open(p["doc"]).read()
        out = vc.plan_text(cfg(p), now=model.epoch("2026-10-28T01:00:00Z"))
        after = open(p["ledger"]).read(), open(p["lane"]).read(), open(p["doc"]).read()
        assert before == after
        assert not os.path.exists(model.shard_path("OWNER")), "plan appended a shard"
        assert "move 3" in out and "keep 3" in out and "defer 1" in out, out
        assert "docs patch: applies cleanly" in out, out
        assert "RULE" in out, out
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_apply_reassigns_flips_and_records_then_rerun_is_noop():
    p = fixture()
    try:
        rc = vc.apply(cfg(p), SAID, why="cutover test", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        assert rc == 0, rc
        o = owners()
        assert o["HOSE_FIX_MOVE_ME"] == ("FOUNDRY", "proposed"), o["HOSE_FIX_MOVE_ME"]
        assert o["DOING_NO_LEASE_MOVES"] == ("FOUNDRY", "ready"), o["DOING_NO_LEASE_MOVES"]
        assert o["LORE_DESIGN_MOVES_TOO"][0] == "FOUNDRY"
        for k in ("OWNER_WALK_NEEDS_HIM", vc.CUTOVER_ITEM, "L4_OWNER_ACCEPT", "LEASED_NOW_DEFERS"):
            assert o[k][0] == "BENCH", (k, o[k])
        assert o["FOUNDRY_ALREADY_OWNS"][0] == "FOUNDRY"
        evs = [json.loads(l) for l in open(model.shard_path("OWNER"))]
        ra = [e for e in evs if e["event"] == "reassign"]
        assert len(ra) == 3 and all(e["ownerSaid"] == SAID and e["to"] == "FOUNDRY" for e in ra), ra
        assert json.load(open(p["lane"]))["seat"] == "FOUNDRY"
        assert json.load(open(p["lane"]))["id_patterns"] == ["^HOSE_"], "lane patterns must stay as data"
        assert open(p["doc"]).read() == DOC_AFTER
        rec = json.load(open(p["record"]))
        assert rec["state"] == "applied" and sorted(rec["moved"]) == ["DOING_NO_LEASE_MOVES", "HOSE_FIX_MOVE_ME", "LORE_DESIGN_MOVES_TOO"], rec
        assert rec["lane_seat_before"] == "BENCH" and rec["ownerSaid"] == SAID, rec
        n = len(open(model.shard_path("OWNER")).readlines())
        rc = vc.apply(cfg(p), SAID, why="again", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        assert rc == 0, rc
        assert len(open(model.shard_path("OWNER")).readlines()) == n, "re-run wrote events"
        assert open(p["doc"]).read() == DOC_AFTER, "re-run touched the doc"
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_rerun_after_lease_lapses_moves_the_deferred_item():
    p = fixture()
    try:
        vc.apply(cfg(p), SAID, why="t", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        with open(p["ledger"], "a") as fh:
            fh.write(json.dumps(ev(30, "BENCH", "lease", "LEASED_NOW_DEFERS", action="release", token="tok1abcd")) + "\n")
        vc.apply(cfg(p), SAID, why="t2", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        assert owners()["LEASED_NOW_DEFERS"][0] == "FOUNDRY"
        rec = json.load(open(p["record"]))
        assert "LEASED_NOW_DEFERS" in rec["moved"] and len(rec["moved"]) == 4, rec["moved"]
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_revert_undoes_what_the_record_says():
    p = fixture()
    try:
        vc.apply(cfg(p), SAID, why="t", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        rc = vc.revert(cfg(p), owner_said=None, why="undo test", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        assert rc == 0, rc
        o = owners()
        assert o["HOSE_FIX_MOVE_ME"][0] == "BENCH" and o["DOING_NO_LEASE_MOVES"][0] == "BENCH", o
        assert o["FOUNDRY_ALREADY_OWNS"][0] == "FOUNDRY", "revert touched an item it never moved"
        assert json.load(open(p["lane"]))["seat"] == "BENCH"
        assert open(p["doc"]).read() == DOC_BEFORE
        assert json.load(open(p["record"]))["state"] == "reverted"
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_revert_refuses_before_any_write_when_docs_cannot_be_reversed():
    p = fixture()
    try:
        vc.apply(cfg(p), SAID, why="t", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        with open(p["doc"], "w") as fh:
            fh.write("# FOUNDRY\n\nhand-edited after the cutover\n")
        n = len(open(model.shard_path("OWNER")).readlines())
        rc = vc.revert(cfg(p), owner_said=None, why="undo", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        assert rc != 0
        assert not os.path.exists(model.shard_path("BENCH")), "revert wrote events although the docs refused"
        assert len(open(model.shard_path("OWNER")).readlines()) == n
        assert json.load(open(p["lane"]))["seat"] == "FOUNDRY" and json.load(open(p["record"]))["state"] == "applied"
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_revert_keeps_a_live_leased_item_pending_and_finishes_it_later():
    p = fixture()
    try:
        vc.apply(cfg(p), SAID, why="t", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        with open(p["ledger"], "a") as fh:      # FOUNDRY starts work on a moved item
            t0 = model.epoch_now()      # after the reassign events, which carry the wall clock
            fh.write(json.dumps({"seat": "FOUNDRY", "event": "lease", "id": "HOSE_FIX_MOVE_ME", "action": "take",
                                 "token": "tok2abcd", "ts": iso(t0 + 5), "expires": iso(t0 + 1800)}) + "\n")
        vc.revert(cfg(p), owner_said=None, why="undo", now=t0 + 60, commit=False)
        rec = json.load(open(p["record"]))
        assert rec["state"] == "reverting" and rec["revert_pending"] == ["HOSE_FIX_MOVE_ME"], rec
        assert owners()["HOSE_FIX_MOVE_ME"][0] == "FOUNDRY" and owners()["DOING_NO_LEASE_MOVES"][0] == "BENCH"
        rc = vc.revert(cfg(p), owner_said=None, why="finish", now=t0 + 7200, commit=False)
        assert rc == 0 and json.load(open(p["record"]))["state"] == "reverted"
        assert owners()["HOSE_FIX_MOVE_ME"][0] == "BENCH"
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_a_question_is_refused_before_anything_is_written():
    p = fixture()
    try:
        before = open(p["ledger"]).read(), open(p["lane"]).read()
        rc = vc.apply(cfg(p), SAID + ", right?", why="t", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        assert rc != 0
        assert (open(p["ledger"]).read(), open(p["lane"]).read()) == before
        assert not os.path.exists(model.shard_path("OWNER")) and not os.path.exists(p["record"])
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_a_stale_patch_refuses_apply_before_any_write():
    p = fixture()
    try:
        with open(p["doc"], "w") as fh:
            fh.write("# FOUNDRY\n\nsomeone rewrote this file\n")
        assert "docs patch: DOES NOT APPLY" in vc.plan_text(cfg(p), now=model.epoch("2026-10-28T01:00:00Z"))
        rc = vc.apply(cfg(p), SAID, why="t", now=model.epoch("2026-10-28T01:00:00Z"), commit=False)
        assert rc != 0
        assert not os.path.exists(model.shard_path("OWNER")), "events written although the docs patch failed"
        assert json.load(open(p["lane"]))["seat"] == "BENCH"
    finally:
        shutil.rmtree(p["root"], ignore_errors=True)


def t_shipped_patch_and_record_are_consistent():
    """The real staged patch applies to the real docs while the cutover is pending (or is already in when applied)."""
    real = vc.Paths()
    rec = vc.read_record(real)
    st = (rec or {}).get("state")
    ok, why = vc.patch_status(real)
    if st == "applied":
        assert why == "already applied", why
    else:
        assert ok and why == "applies cleanly", why


CASES = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]

if __name__ == "__main__":
    saved = model.EVENTS
    for fn in CASES:
        try:
            fn(); PASS.append(fn.__name__); print("ok    " + fn.__name__)
        except Exception as e:  # noqa: BLE001
            FAIL.append(fn.__name__); print("FAIL  %s\n        %s: %s" % (fn.__name__, type(e).__name__, e))
        finally:
            model.EVENTS = saved
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
