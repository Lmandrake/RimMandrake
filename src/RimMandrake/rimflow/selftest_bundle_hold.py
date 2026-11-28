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


def main():
    for t in [t_every_lane_ticket_has_a_real_home, t_a_home_holds_until_five_or_the_hold_time,
              t_the_replay_of_nov_27_reads_a_median_of_five, t_no_ticket_waits_past_the_hold_time,
              t_an_urgent_ticket_never_waits, t_the_lane_holds_before_its_room_gates, t_fresh_reader_tickets_fold]:
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
