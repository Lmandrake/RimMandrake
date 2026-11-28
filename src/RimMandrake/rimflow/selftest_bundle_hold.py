#!/usr/bin/env python3
"""selftest_bundle_hold.py - the lane bundles by home: reader homes, the hold, urgent tickets, folded reads.

Item RIMMANDRAKE_FILL_BUNDLES_BY_HOME_HOLD_MEDIAN_ONE_TODAY; page design/specs/2026-11-24-work-bundles/boundary.md,
section "Large bundles by home" (each t_ function is one promise of it, by name). Offline: the replay of the real
arrivals (bundle_replay.py) through the real work_bundle code, a fake clock, nothing launched or written. Seen failing on
the parent (hold_systems, reader_home and read_fold absent); each rule's planted fault turns its test red (the faults
are run inside the tests: the hold at 0, the urgent rule off, the reader home off).
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(HERE, "..", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
os.environ.setdefault("RM_WORK_BUNDLE_DIR", tempfile.mkdtemp(prefix="selftest_bundle_hold_"))
FAILS = []
DAY = "2026-11-27"


def chk(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def _reader(iid, paths, sha="abc1234"):
    import fresh_reader as FR
    return {"id": iid, "title": FR.title(sha, paths, "a run"), "home": None, "caused_by": None}


def _cfg_hold():
    import list_dispatch as LD
    c = LD.load_cfg()
    return float(c["bundle_hold_h"]) * 3600, int(c["bundle_full_n"])


def t_every_lane_ticket_has_a_real_home():
    import list_home as LH
    import work_bundle as WB
    r = lambda it: {"mod": None}    # noqa: E731
    chk(LH.reader_home(_reader("A", ["src/RimMandrake/Utils/x.py"])) == "pipeline:read-utils", "a Utils reader reads read-utils")
    chk(LH.reader_home(_reader("B", ["src/RimMandrake/rimflow/y.py", "src/RimMandrake/Utils/x.py"]))
        == "pipeline:read-rimflow", "a mixed reader takes the area of its first file")
    chk(LH.reader_home(_reader("C", ["src/RimMandrake/FlowWorks/a.cs"])) == "pipeline:read-other", "a mod file reads read-other")
    chk(LH.reader_home({"id": "D", "title": "Fix the thing"}) is None, "a ticket that is no reader gets no reader home")
    chk(WB.system_of(_reader("E", ["src/RimMandrake/Utils/x.py"]), r, {}) == "pipeline:read-utils",
        "system_of keys a reader ticket on its home, not item:<ID>")
    chk(WB.system_of({"id": "F", "title": "x", "home": {"home": "pipeline:ledger"}}, r, {}) == "pipeline:ledger",
        "a ticket's own home still comes first")


def t_a_home_holds_until_five_or_the_hold_time():
    import work_bundle as WB
    now, h = 1_000_000.0, 4 * 3600

    def rows(n, s="pipeline:x"):
        return [{"item": "T0", "decision": "launch", "bundle": {"system": s, "members": ["T%d" % i for i in range(n)]}}]
    chk("pipeline:x" in WB.hold_systems(rows(1), {"T0": now - 60}, {}, now, h, 5), "one young ticket holds")
    chk(WB.hold_systems(rows(5), {"T0": now - 60}, {}, now, h, 5) == {}, "five ready tickets start at once")
    chk(WB.hold_systems(rows(1), {"T0": now - h}, {}, now, h, 5) == {}, "the oldest at the hold time starts")
    chk(WB.hold_systems(rows(1), {"T0": now - 60}, {}, now, 0, 5) == {}, "a hold of 0 holds nothing")
    w = WB.hold_systems(rows(2), {"T0": now - 60}, {}, now, h, 5).get("pipeline:x", "")
    chk("2 of 5 ready" in w and "at the latest" in w, "the hold's why says the size and the latest start: %s" % w[:120])


def t_the_replay_of_nov_27_reads_a_median_of_five():
    import bundle_replay as R
    fx = R.load()
    hold_s, n = _cfg_hold()
    parent = R.day_figures(R.replay(fx, 0, reader_home=False, urgent_rule=False), DAY)
    fixed = R.day_figures(R.replay(fx, hold_s, n), DAY)
    no_hold = R.day_figures(R.replay(fx, 0, n), DAY)                     # planted fault: the hold removed
    no_home = R.day_figures(R.replay(fx, hold_s, n, reader_home=False), DAY)     # planted fault: the reader home removed
    chk(parent["median"] < 5, "the parent's form reads a median under 5 on Nov 27: %s" % parent)
    chk(fixed["median"] >= 5, "the fix reads a median of 5 or more on Nov 27: %s" % fixed)
    chk(no_hold["median"] < 5, "planted fault, the hold removed: the median falls under 5: %s" % no_hold)
    chk(no_home["median"] < 5, "planted fault, the reader home removed: the median falls under 5: %s" % no_home)


def t_no_ticket_waits_past_the_hold_time():
    import bundle_replay as R
    hold_s, n = _cfg_hold()
    res = R.replay(R.load(), hold_s, n)
    worst = max(res["held_s"].values() or [0])
    chk(0 < worst <= hold_s, "the longest wait for the hold is %.2f h, at most the hold %.2f h" % (worst / 3600, hold_s / 3600))


def t_an_urgent_ticket_never_waits():
    import bundle_replay as R
    import work_bundle as WB
    fx = R.load()
    hold_s, n = _cfg_hold()
    t = min(a["filed"] for a in fx["arrivals"] if R._day(a["filed"]) == DAY) + 3600
    plant = [{"id": "RIMMANDRAKE_PLANTED_URGENT_TICKET_OF_A_SMALL_HOME", "filed": t, "title": "planted",
              "home": "pipeline:planted-home", "urgent": "planted urgent"}]
    got = dict(R.replay(fx, hold_s, n, extra=plant)["urgent"])
    chk(got.get(plant[0]["id"], 1e9) < R.TICK_S, "the planted urgent ticket starts in the tick that first sees it: %s" % got)
    off = dict(R.replay(fx, hold_s, n, extra=plant, urgent_rule=False)["urgent"])
    gone = R.replay(fx, hold_s, n, extra=plant, urgent_rule=False)
    waited = max(gone["held_s"].get(plant[0]["id"], 0), 0)
    chk(not off and waited >= R.TICK_S, "planted fault, the urgent rule removed: it waits for the hold (%.1f h)" % (waited / 3600))
    chk(WB.urgent_why("OPS_LIST_GATE_HOLDS_READY_WORK", None, {}) == "an Ops alarm item", "an Ops alarm id is urgent")
    chk("broken" in (WB.urgent_why("RIMMANDRAKE_X_Y_Z_W", "unit dead", {}) or ""), "a broken live promise is urgent")
    blocks = WB.readiness_blocks({"FlowWorks": "| RIMMANDRAKE_FIX_THE_PUMP_ON_ITS_PATH | BLOCKS | x |\n"
                                               "READY. No BLOCKS ticket is open on this path, RIMMANDRAKE_A_B_C_D."})
    chk(blocks == {"RIMMANDRAKE_FIX_THE_PUMP_ON_ITS_PATH": "FlowWorks"}, "a BLOCKS row marks its ticket, a No BLOCKS line none: %s" % blocks)
    chk("BLOCKS" in (WB.urgent_why("RIMMANDRAKE_FIX_THE_PUMP_ON_ITS_PATH", None, blocks) or ""), "a BLOCKS ticket is urgent")
    chk(WB.urgent_why("RIMMANDRAKE_A_B_C_D", None, blocks) is None, "a ticket that is none of these is not urgent")


def t_the_lane_holds_before_its_room_gates():
    import list_dispatch as LD
    now = 2_000_000_000.0
    it = {"state": "proposed", "effect": "cmd:true", "verdict": "fails", "out": "fails", "events": 1, "title": "t",
          "mod_work": {"mod": None}}
    facts = {"items": {"A1": dict(it), "B1": dict(it)}, "runs": {}, "systems": {"A1": "pipeline:a", "B1": "pipeline:b"},
             "bundles_live": {}, "join": {}, "load": 1.0, "cores": 14, "hosts": {}}
    cfg = dict(LD.load_cfg(), max_live=1, hosts={})
    st = {"items": {"B1": {"ready_at": now - 5 * 3600}}}
    rows, launches = LD.decide(cfg, st, facts, now)
    by = {r["item"]: r["decision"] for r in rows}
    chk(by.get("A1") == "bundle_hold" and launches == ["B1"], "a held home takes no slot: the one slot goes to the home "
                                                             "past its hold: %s %s" % (by, launches))
    chk(st["items"]["A1"].get("ready_at") == now and st["items"]["B1"]["ready_at"] == now - 5 * 3600,
        "each ready row keeps its first ready tick")
    facts["items"]["A1"]["urgent"] = "an Ops alarm item"
    rows, launches = LD.decide(cfg, {"items": {}}, facts, now)
    chk(launches[:1] == ["A1"], "an urgent ticket's row goes first and starts at once: %s" % launches)


def t_fresh_reader_tickets_fold():
    import work_bundle as WB
    items = {"R1": _reader("R1", ["src/RimMandrake/Utils/a.py", "src/RimMandrake/Utils/b.py"], "1111111"),
             "R2": _reader("R2", ["src/RimMandrake/Utils/a.py"], "2222222"),
             "W1": {"id": "W1", "title": "a work ticket"}}
    f = WB.read_fold(["R1", "R2", "W1"], items)
    chk(f == {"src/RimMandrake/Utils/a.py": ["R1", "R2"], "src/RimMandrake/Utils/b.py": ["R1"]},
        "two reader tickets of one file become one read: %s" % f)
    txt = WB.read_fold_text(["R1", "R2", "W1"], items)
    chk(txt.count("`src/RimMandrake/Utils/a.py`") == 1 and "2 file(s) for 2 reader ticket(s)" in txt,
        "the brief lists the file once, with the tickets it covers")
    chk(WB.read_fold_text(["W1"], items) == "", "a bundle with no reader ticket has no read block")
    rec = {"id": "WB-x", "system": "pipeline:read-utils", "state_file": "s.md", "lead": "R1", "members": ["R1", "R2"],
           "why": "w"}
    chk("covers R1, R2" in WB.brief(rec, items, {}), "the bundle's brief carries the folded reads")


# ---- the live routes (item RIMMANDRAKE_BUNDLE_SHAPE_ROWS_BY_HOME_HOLD_HELD_NOTHING) ----------------------------------

T0 = 1_796_000_000 - 1_796_000_000 % 600       # a tick boundary; no real arrival is near it


def _arr(iid, filed=T0, **kw):
    a = {"id": iid, "filed": filed, "title": "t", "home": None, "home_at": 0, "caused_by": None, "parent_home": None,
         "parent_home_at": 0, "check_at": None, "route_at": None, "claim_at": None, "closed_at": None, "mod": None,
         "lane_taken": False, "old": False, "window": True}
    a.update(kw)
    return a


def _live(arrivals, rule="live", hold_s=4 * 3600, **kw):
    import bundle_replay as R
    return R.replay_live({"bundle_s": 2700, "arrivals": arrivals}, hold_s, 5, rule=rule, **kw)


def _bundle_of(res, iid):
    return next((b for b in res["bundles"] if iid in b["members"]), None)


def t_the_live_replay_models_the_live_routes():
    import bundle_replay as R
    g = R.GRACE_S
    arr = [_arr("PIPE_ALONE_ONE_TICKET_HOME", home="pipeline:alone"),
           _arr("PIPE_MANY_FIRST_OF_THREE", home="pipeline:many"), _arr("PIPE_MANY_SECOND_OF_THREE", home="pipeline:many"),
           _arr("PIPE_MANY_THIRD_OF_THREE", home="pipeline:many"),
           _arr("OPS_PLANTED_ALARM_OF_A_SMALL_HOME", home="pipeline:ops-home", check_at=T0),
           _arr("OPS_HOME_CHECKED_COMPANION_TICKET", home="pipeline:ops-home", check_at=T0),
           _arr("HELD_HOME_CHECKED_LONE_TICKET", home="pipeline:held", check_at=T0),
           _arr("CAUSE_CHILD_FIRST_OF_TWO", caused_by="CAUSE_PARENT_WITH_NO_HOME"),
           _arr("CAUSE_CHILD_SECOND_OF_TWO", caused_by="CAUSE_PARENT_WITH_NO_HOME"),
           _arr("ITEM_LONE_TICKET_NO_HOME_NO_CAUSE"), _arr("ITEM_CHECKED_TICKET_NO_HOME_NO_CAUSE", check_at=T0),
           _arr("FILER_CLOSED_IT_WITHIN_THE_HOUR", home="pipeline:alone", closed_at=T0 + 3600),
           _arr("FILER_CLAIMED_ITS_CHECKED_TICKET", home="pipeline:claimed", check_at=T0, claim_at=T0 + 60),
           _arr("RIMMANDRAKE_READ_FIX_ABCDEF1234_WITH_FRESH_EYES", home="pipeline:read-utils", check_at=T0),
           _arr("OLD_TICKET_OF_A_CAUSE_HOME", old=True, caused_by="CAUSE_PARENT_WITH_NO_HOME")]
    res = _live(arr)
    b = _bundle_of(res, "PIPE_ALONE_ONE_TICKET_HOME")
    chk(b and b["members"] == ["PIPE_ALONE_ONE_TICKET_HOME"] and g <= b["at"] - T0 < g + R.TICK_S and b["route"] == "onboard",
        "one ticket alone in its home, no check: unseen for shape_grace_h, then its home's onboarding run, not held: %s" % b)
    b = _bundle_of(res, "PIPE_MANY_FIRST_OF_THREE")
    chk(b and len(b["members"]) == 3 and b["at"] - T0 < g + R.TICK_S,
        "several tickets of one home in one tick: one onboarding run, never held (live): %s" % b)
    b = _bundle_of(res, "OPS_PLANTED_ALARM_OF_A_SMALL_HOME")
    chk(b and set(b["members"]) == {"OPS_PLANTED_ALARM_OF_A_SMALL_HOME", "OPS_HOME_CHECKED_COMPANION_TICKET"}
        and b["at"] - T0 < R.TICK_S, "an OPS_ ticket among them starts at once and takes its home's ready ticket: %s" % b)
    b = _bundle_of(res, "HELD_HOME_CHECKED_LONE_TICKET")
    chk(b and 4 * 3600 <= b["at"] - T0 < 4 * 3600 + R.TICK_S, "a lone checked ticket waits the hold, no more: %s" % b)
    c1, c2 = _bundle_of(res, "CAUSE_CHILD_FIRST_OF_TWO"), _bundle_of(res, "CAUSE_CHILD_SECOND_OF_TWO")
    chk(c1 and c2 and c1 is not c2 and len(c1["members"]) == 1 and c1["route"] == "shape",
        "a cause: home under the live rule: each Shape row is a run of its own, never held: %s %s" % (c1, c2))
    b = _bundle_of(res, "ITEM_LONE_TICKET_NO_HOME_NO_CAUSE")
    chk(b and b["members"] == ["ITEM_LONE_TICKET_NO_HOME_NO_CAUSE"] and b["at"] - T0 < g + R.TICK_S,
        "an item: home: a Shape run of its own at shape_grace_h: %s" % b)
    b = _bundle_of(res, "ITEM_CHECKED_TICKET_NO_HOME_NO_CAUSE")
    chk(b and 4 * 3600 <= b["at"] - T0 < 4 * 3600 + R.TICK_S, "live: a checked item: ticket waits the hold: %s" % b)
    chk(_bundle_of(res, "FILER_CLOSED_IT_WITHIN_THE_HOUR") is None, "a ticket its filer closed first never arrives")
    chk(_bundle_of(res, "FILER_CLAIMED_ITS_CHECKED_TICKET") is None, "a ticket its filer claimed at once never arrives")
    chk(_bundle_of(res, "RIMMANDRAKE_READ_FIX_ABCDEF1234_WITH_FRESH_EYES") is None,
        "the code review switch leaves out a reader ticket")
    chk(_bundle_of(_live(arr, review=True), "RIMMANDRAKE_READ_FIX_ABCDEF1234_WITH_FRESH_EYES") is not None,
        "with the review tickets kept, the reader ticket starts")
    chk(_bundle_of(res, "OLD_TICKET_OF_A_CAUSE_HOME") is None, "an old ticket of a cause: home never starts (live)")
    grp = _live(arr, rule="shape_by_home")
    c1, c2 = _bundle_of(grp, "CAUSE_CHILD_FIRST_OF_TWO"), _bundle_of(grp, "CAUSE_CHILD_SECOND_OF_TWO")
    chk(c1 is not None and c1 is c2 and 4 * 3600 <= c1["at"] - (T0 + g) < 4 * 3600 + R.TICK_S,
        "shape_by_home: the Shape rows of one cause: home are one run, held for the hold: %s" % c1)
    b = _bundle_of(grp, "ITEM_LONE_TICKET_NO_HOME_NO_CAUSE")
    chk(b and b["at"] - T0 < g + R.TICK_S, "shape_by_home: an item: home is never held (it can gain no company): %s" % b)
    b = _bundle_of(grp, "ITEM_CHECKED_TICKET_NO_HOME_NO_CAUSE")
    chk(b and b["at"] - T0 < R.TICK_S, "shape_by_home: a checked item: ticket starts at once: %s" % b)
    b = _bundle_of(grp, "OPS_PLANTED_ALARM_OF_A_SMALL_HOME")
    chk(b and b["at"] - T0 < R.TICK_S, "shape_by_home: the OPS_ ticket still starts at once: %s" % b)
    empty = _live([])
    chk(empty["bundles"] == [] and empty["held_s"] == {}, "an empty tick: no run, no wait")


def t_the_live_replay_reads_close_to_the_lane():
    import statistics
    import bundle_replay as R
    fx = R.load(R.LIVE_ARRIVALS)
    lane = fx["lane"][DAY]
    got = R.day_figures(R.replay_live(fx, 4 * 3600, 5, rule="live", game=True), DAY)
    share = lambda f: f["singles"] / float(f["bundles"])    # noqa: E731
    chk(got["median"] == lane["median"] == 1 and abs(share(got) - share(lane)) <= 0.10,
        "the live-route replay of Nov 27 reads the lane's median and its share of singles within 10 points: replay %s, "
        "lane %s" % (got, lane))
    for day in ("2026-11-25", "2026-11-26", "2026-11-27"):
        res = R.replay_live(fx, 24 * 3600, 5, rule="live")
        per = {}
        for i, s in res["systems"].items():
            if R._day(R.live_route(next(a for a in fx["arrivals"] if a["id"] == i))[1]) == day:
                per[s] = per.get(s, 0) + 1
        chk(statistics.median(per.values()) == 1, "%s: one bundle per system for the whole day reads median 1 (%d "
            "systems, %d of one ticket): no rule of one system per bundle raises the median" % (
                day, len(per), sum(1 for v in per.values() if v == 1)))


def main():
    for t in [t_every_lane_ticket_has_a_real_home, t_a_home_holds_until_five_or_the_hold_time,
              t_the_replay_of_nov_27_reads_a_median_of_five, t_no_ticket_waits_past_the_hold_time,
              t_an_urgent_ticket_never_waits, t_the_lane_holds_before_its_room_gates, t_fresh_reader_tickets_fold,
              t_the_live_replay_models_the_live_routes, t_the_live_replay_reads_close_to_the_lane]:
        print("-- %s" % t.__name__)
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILS.append("%s raised %s: %s" % (t.__name__, type(e).__name__, e))
            print("FAIL %s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_bundle_hold: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
