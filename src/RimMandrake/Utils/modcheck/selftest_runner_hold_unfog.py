#!/usr/bin/env python3
"""Selftest for HARNESS_REPAIR_CAUSE_3EA971C0 (and 9F08EBA4): the per-chain site hold (runner._hold_site) must unfog the
map and re-sweep what the unfog releases BEFORE it calls the site bland.
Evidence: FlowWorks machinery_pipes (J20261124T092437Z-3a510b) held a fresh debug map with kill_hostiles targeted [] and
then lost the row to Bulbfreak 7948 + its Divide brood (Toughspike 36698, Trispikes 36700/36702/36704) at tick 953-1021;
toggle_river_steam (J20261124T145356Z-fe9ee3) met Bulbfreaks 4719-4722, map-gen ids, mid-chain. The listing could not see
them at the hold; TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG (r7): the whole-map unfog releases such pawns on 4 of 5 fresh
maps, and test_site_saves.clean_map already unfogs + re-sweeps, the hold did not.
Offline: the bridge and the helpers recipe are faked; the map model releases hidden fleshbeasts on jawa/set_fog unfogAll."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import runner  # noqa: E402
import helpers  # noqa: E402
import testenv_guards as TG  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


class HiddenBeastMap(object):
    """hostiles: listed now. hidden: on the map but unlisted until the whole map is unfogged (r7).
    fixtures: a chain's non-hostile fixtures (must survive the hold). keeps_releasing: each sweep is followed by more."""
    def __init__(self, hidden=(), keeps_releasing=False):
        self.hostiles, self.hidden = [], list(hidden)
        self.fixtures = ["Fixture_Cow1"]
        self.keeps_releasing, self.calls = keeps_releasing, []

    def call(self, tool, **p):
        self.calls.append(tool)
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": h} for h in self.hostiles]}
        if tool == "jawa/set_fog":
            self.hostiles += self.hidden
            self.hidden = []
            return {"success": True, "foggedCellsBefore": 5000, "foggedCellsNow": 0}
        if tool == "jawa/destroy_bulk":        # nonColonists: would take the fixtures too
            self.hostiles, self.fixtures = [], []
            return {"success": True}
        return {"success": True}


def fake_kill_hostiles(session, expected_ids=()):
    gone = list(session.hostiles)
    session.hostiles = ["Mech_Pikeman9%d" % len(session.calls)] if (session.keeps_releasing and gone) else []
    return helpers.HelperResult("kill_hostiles", acted=len(gone), verified=True, evidence={"targeted": gone})


def fake_prepare_bland_map(session, tx, expected_ids, kill=True, resurrect=False):
    rep = helpers.BlandReport()
    rep.steps.append(helpers.HelperResult("assert_bland", verified=True))
    if session.hostiles:
        rep.problems.append("hostile_pawns: %s" % session.hostiles)
    return rep


def main():
    helpers.kill_hostiles, helpers.prepare_bland_map = fake_kill_hostiles, fake_prepare_bland_map
    beasts = ["Bulbfreak7948", "Warg8183"]

    m = HiddenBeastMap(hidden=beasts)
    hold = runner._hold_site(m, object(), ["Fixture_Cow1"])
    ok(m.hostiles == [] and m.hidden == [], "the hold leaves no hidden fleshbeast to arrive mid-row (3EA971C0)",
       (m.hostiles, m.hidden))
    ok(hold.get("bland") is True, "a map whose released beasts were swept holds bland", hold)
    fog = [s for s in hold.get("steps") or [] if s.get("name") == "clear_map_fog"]
    ok(fog and fog[0]["evidence"].get("releasedByUnfog") == beasts,
       "the receipt names what the unfog released (releasedByUnfog)", fog)
    ok(m.fixtures == ["Fixture_Cow1"] and "jawa/destroy_bulk" not in m.calls,
       "the hold's re-sweep is hostile-only: a chain's non-hostile fixture survives", (m.fixtures, m.calls))
    ok("jawa/set_fog" in m.calls and m.calls.index("jawa/set_fog") > 0,
       "the unfog runs after the first hostile sweep (an unfog on a listed hostile is refused)", m.calls)

    m = HiddenBeastMap()
    hold = runner._hold_site(m, object(), [])
    ok(hold.get("bland") is True, "control: a map with nothing hidden holds bland", hold)

    m = HiddenBeastMap(hidden=["Bulbfreak4719"], keeps_releasing=True)
    hold = runner._hold_site(m, object(), [])
    ok(hold.get("bland") is False and any("SITE" in str(p) for p in hold.get("problems") or []),
       "can-fail: a map that keeps releasing hostiles is not bland (chain UNMEASURED at the hold, not mid-row)", hold)

    # the guard's own sweep= hook: default stays the calm's nonColonists vanish
    m = HiddenBeastMap(hidden=beasts)
    r = TG.clear_map_fog(m)
    ok(r["verified"] and "jawa/destroy_bulk" in m.calls, "clear_map_fog default sweep is unchanged (destroy_bulk)", r)

    print("%d failure(s), %d checks" % (len(FAILS), 8))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
