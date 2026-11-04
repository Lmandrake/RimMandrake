#!/usr/bin/env python3
"""selftest_bottleneck_measure: bottleneck_measure.py on hand-built stores and transcripts whose answers are known.

HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM. Each fixture is small enough to count by hand; the comment above each
assertion says where the number comes from.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bottleneck_measure as bm  # noqa: E402

T0 = bm.ts("2026-11-03T00:00:00Z")


def Z(sec):
    return bm.iso(T0 + sec)


def stamp(sec):
    return bm.iso(T0 + sec).replace("-", "").replace(":", "")


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def store_fixture(d):
    """One hour. Item P holds the game: staged 0-600, a round 900-1500 (proof log 1000-1200); item W waits on P at
    every tick 0..3000 (ticks every 300 s), the last tick at 3300 has no wait. Offline item O: enrolled 0, worker
    100-700, check 800-1000, done 1000. Live item W done at 3500: enrolled 0, worker 0-200."""
    root = os.path.join(d, "rl")
    ticks = []
    for k in range(0, 12):
        t = 300 * k
        acts = []
        if t < 3300:
            acts.append({"do": "game_waits", "item": "W", "why": "one live user at a time: P holds the game phase"})
        if t == 0:
            acts.append({"do": "game_stage", "item": "P"})
            acts.append({"do": "wait", "why": "max_workers"})
        if t == 600:
            acts.append({"do": "game_staged", "item": "P"})
        if t == 900:
            acts.append({"do": "game_prove", "item": "P", "pid": 1})
        if t == 600:
            acts.append({"do": "check_started", "item": "O"})
        ticks.append({"at": Z(t), "do": "tick", "acts": acts})
    # check of O ends with done at 900 (tick) -> but O's check is 600..900
    ticks.append({"at": Z(900), "do": "tick", "acts": [{"do": "done", "item": "O"}]})
    write_jsonl(os.path.join(root, "store", "journal.jsonl"), ticks)
    with open(os.path.join(root, "store", "journal.jsonl"), "a", encoding="utf-8") as f:
        f.write("not json\n")
    os.makedirs(os.path.join(root, "live"))
    with open(os.path.join(root, "live", "round.out"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"at": Z(1500), "runs": [{"outcome": "PASS"}, {"outcome": "UNMEASURED"}], "why": "done"},
                           indent=1) + "\n[\"a list line\"]\n")
    lp = os.path.join(root, "live", "P-A1-%s.log" % stamp(1000))
    open(lp, "w").close()
    os.utime(lp, (T0 + 1200, T0 + 1200))
    open(os.path.join(root, "live", "notaproof.log"), "w").close()
    for item, enr, done, att, game in (("O", 0, 1000, [(100, 700)], None), ("W", 0, 3500, [(0, 200)], {"x": 1})):
        idir = os.path.join(root, "store", "items", item)
        os.makedirs(idir)
        json.dump({"item": item, "status": "done", "enrolled_at": T0 + enr, "done_at": T0 + done, "game": game},
                  open(os.path.join(idir, "state.json"), "w"))
        rows = []
        for a, b in att:
            rows += [{"at": Z(a), "start": "u", "gen": 1}, {"at": Z(b), "end": "finish", "gen": 1}]
        write_jsonl(os.path.join(idir, "attempts.jsonl"), rows)
    write_jsonl(os.path.join(root, "store", "staffing.jsonl"),
                [{"t": T0, "why": "pool full: x", "running": 2, "target": 3},
                 {"t": T0 + 1800, "why": None, "running": 3, "target": 3}])
    return root


def t_intervals():
    assert bm.merge([(5, 7), (0, 2), (1, 3), (9, 9)]) == [(0, 3), (5, 7)]
    assert bm.total([(0, 2), (1, 3)]) == 3
    assert bm.subtract([(0, 10)], [(2, 3), (5, 20)]) == [(0, 2), (3, 5)]
    assert bm.overlap(0, 10, [(2, 4), (8, 12)]) == 4
    assert bm.ts("20261103T000000Z") == T0


def t_game(d):
    root = store_fixture(d)
    r = bm.game_measure(root, T0, T0 + 3600)
    g = r["game"]
    # proof log 1000..1200 -> 200 s; the notaproof.log name does not parse and is ignored
    assert g["proof_logs"] == 1 and abs(g["proving_h"] * 3600 - 200) < 1, g
    # stage 0..600
    assert abs(g["staging_h"] * 3600 - 600) < 1, g
    # round: launch tick 900 (no wall_s) -> round.out end 1500
    assert g["rounds"] == 1 and abs(g["round_h"] * 3600 - 600) < 1, g
    assert g["outcomes"] == {"rounds": 1, "rounds_with_runs": 1, "criterion_runs": {"PASS": 1, "UNMEASURED": 1}}, g
    # busy = 0..600 + 900..1500 = 1200 s
    assert abs(g["busy_h"] * 3600 - 1200) < 1, g
    # W waits at ticks 0..3000 (11 ticks x 300 s = 3300 s); the extra done tick at 900 splits 900..1200 into 0 and 300
    w = r["game_wait_item_h"]
    assert abs(w["total"] * 3600 - 3300) < 1, w
    # behind the proof: 200; behind staging: 600; behind the round's non-proof part: 600-200 = 400; idle: rest
    assert abs(w["while_proving"] * 3600 - 200) < 1, w
    assert abs(w["while_staging"] * 3600 - 600) < 1, w
    assert abs(w["while_round_not_proving"] * 3600 - 400) < 1, w
    assert abs(w["while_idle"] * 3600 - 2100) < 1, w
    assert set(r["game_wait_by_reason_item_h"]) == {"held_by_item"}
    # the demand window is 0..3300 and the game was busy 1200 of it
    assert abs(g["demand_and_idle_h"] * 3600 - 2100) < 1, g
    # max_workers named once, at tick 0 -> 300 s
    assert abs(r["worker_slots_full_h"] * 3600 - 300) < 1, r
    items = {i["item"]: i for i in r["items"]}
    o, wi = items["O"], items["W"]
    # O: queue 0..100, worker 600, check 600..900 (journal), rest 'other'
    assert (o["live"], o["queue_s"], o["worker_s"], o["check_s"]) == (False, 100, 600, 300), o
    assert abs(o["other_s"] - 0) < 1, o
    # W: live, worker 200, own proof 0, waited 3300 (200 of it behind a running proof)
    assert wi["live"] and wi["worker_s"] == 200 and abs(wi["game_wait_s"] - 3300) < 1, wi
    assert abs(wi["proj_2x_save_hi_s"] - 200) < 1 and wi["proj_2x_save_lo_s"] == 0, wi
    assert r["done_items"]["live"]["n"] == 1 and r["done_items"]["offline"]["n"] == 1
    # staffing: pool full 0..1800, None 1800..3600 (the last sample runs to the window end)
    assert r["staffing"]["why_s"] == {"pool full: x": 1800, "None": 1800}, r["staffing"]
    assert abs(r["staffing"]["running_ge_target_s"] - 1800) < 1


def t_classify():
    c = bm.classify_publish
    assert c("PUBLISHED abc123") == "published"
    assert c("REFUSED: nothing to publish: HEAD is already on origin/main") == "benign"
    assert c("REFUSED: replaying x onto origin/main stopped on a conflict in: a/b.dll. Your commit") == "conflict"
    assert c("REFUSED: a DLL needs rebuilding from committed source, but this clone has uncommitted edits to: x") \
        == "dirty_tree"
    assert c("REFUSED: the DLL/source-stamp guard refused again after a rebuild") == "dll_stamp"
    assert c("REFUSED: origin kept moving: 5 non-fast-forward rejections in a row") == "race"
    assert c("REFUSED: git push failed: boom") == "race"
    assert c("REFUSED: something new") == "other_refused"
    assert c("(timed out)") == "no_verdict"


def transcript(path, calls):
    rows = []
    for i, (t, cmd, out) in enumerate(calls):
        rows.append({"timestamp": Z(t), "message": {"content": [
            {"type": "tool_use", "name": "Bash", "id": "u%d" % i, "input": {"command": cmd}}]}})
        rows.append({"timestamp": Z(t + 5), "message": {"content": [
            {"type": "tool_result", "tool_use_id": "u%d" % i, "content": [{"type": "text", "text": out}]}]}})
    write_jsonl(path, rows)


def t_publish(d):
    proj = os.path.join(d, "projects")
    transcript(os.path.join(proj, "-home-mandrake-rm-relentless-clones-X", "a.jsonl"), [
        (0, "./publish a -m x", "REFUSED: replaying y stopped on a conflict in: z"),
        (100, "git status", "clean"),
        (160, "cd /c && ./publish a -m x", "PUBLISHED deadbeef"),
        (200, "./publish -m y", "REFUSED: nothing to publish: HEAD is already on origin/main")])
    transcript(os.path.join(proj, "-home-mandrake-rm-bench", "s", "subagents", "b.jsonl"), [
        (0, "./publish p -m x", "REFUSED: this clone has uncommitted edits to: q"),
        (90000, "./publish p -m x", "REFUSED: a dirty tree")])
    transcript(os.path.join(proj, "-home-mandrake-elsewhere", "c.jsonl"), [(0, "./publish", "PUBLISHED x")])
    r = bm.publish_measure(T0, T0 + 2 * 86400, proj)
    m = r["by_model_day"]
    assert set(m) == {"per_writer_clone", "shared_seat_clone"}, m      # the elsewhere project is no writer model
    pw = m["per_writer_clone"]["2026-11-03"]
    assert pw["calls"] == 3 and pw["classes"] == {"benign": 1, "conflict": 1, "published": 1}, pw
    assert pw["collisions"] == 1 and pw["writers"] == 1, pw
    assert abs(pw["recover_min_median"] - 160 / 60) < 1e-6 and pw["unrecovered"] == 0, pw   # refusal 0 -> PUBLISHED 160
    sh = m["shared_seat_clone"]
    # subagent transcripts are found recursively; the second refusal falls on the next day; neither recovers
    assert sh["2026-11-03"]["classes"] == {"dirty_tree": 1} and sh["2026-11-03"]["unrecovered"] == 1, sh
    assert sh["2026-11-04"]["classes"] == {"dirty_tree": 1} and sh["2026-11-04"]["unrecovered"] == 1, sh


TESTS = [t_intervals, t_game, t_classify, t_publish]


def main():
    ok = 0
    for t in TESTS:
        d = tempfile.mkdtemp(prefix="bm_selftest_")
        try:
            t(d) if t.__code__.co_argcount else t()
            ok += 1
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, e))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print("%d/%d passed" % (ok, len(TESTS)))
    return 0 if ok == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
