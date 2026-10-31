#!/usr/bin/env python3
"""Selftest: the Test Pilot rule (testpilot_route.py). The ledger events are replayed by the real model, so the rule is
tested against the Run and Item it meets in production. The threshold is checked on both sides (2 stays, 3 routes),
and the Dispatcher half is checked from a `next --peek` text to the words FOUNDRY receives.

    python3 src/RimMandrake/rimflow/selftest_testpilot_route.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from rimflow import dispatcher, model, testpilot_route as R             # noqa: E402
import selftest_built as sb                                             # noqa: E402

PASS, FAIL = [], []
IT = "CAUSEWAY_FIX_THE_LIP"
DIAG = "CAUSEWAY_DIAGNOSE_THE_LIP"


class Log(object):
    """A ledger under construction: each method appends one real event."""

    def __init__(self, iid=IT):
        self.iid = iid
        self.evs = sb.filed("FOUNDRY", iid, 0)

    def add(self, verb, **kw):
        self.evs.append(sb.ev(len(self.evs) + 2, kw.pop("seat", "FOUNDRY"), verb, self.iid, **kw))
        return self

    def runs(self, *results, config="c1"):
        for r in results:
            self.add("verify", config=config, result=r, evidence="e.txt", sha="a" * 12)
        return self

    def note(self, text):
        return self.add("note", text=text)

    def verdict(self):
        return R.judge(model.replay(self.evs).items[self.iid], self.evs)


def kind(v):
    return v and v["kind"]


def t_threshold_two_stays_three_routes():
    assert Log().runs("fail", "partial").verdict() is None, "two misses are still worth a retest"
    v = Log().runs("fail", "partial", "fail").verdict()
    assert kind(v) == "streak" and "3 non-pass" in v["why"], "three misses route, fail and partial alike: %r" % v


def t_the_number_is_the_measured_one():
    assert R.STREAK == 3, "changing the threshold means re-measuring it from the ledger; see the module docstring"


def t_a_pass_resets_the_count():
    assert Log().runs("fail", "fail", "fail", "pass").verdict() is None, "a green run ends the streak"
    assert kind(Log().runs("fail", "fail", "pass", "fail", "fail", "fail").verdict()) == "streak", "a new streak counts"


def t_one_config_failing_behind_another_passing_still_routes():
    log = Log().runs("fail", config="a").runs("pass", config="b").runs("fail", config="a").runs("pass", config="b")
    v = log.runs("fail", config="a").verdict()
    assert kind(v) == "streak" and "on a" in v["why"], "the item never streaks, config a does: %r" % v


class Run(object):
    def __init__(self, criterion, config, result):
        self.criterion, self.config, self.result = criterion, config, result


def worst(*rows):
    return R.streaks([Run(*row) for row in rows])[1]


def t_a_config_streak_survives_its_runs_having_criteria():
    n = worst(("a", "c1", "fail"), ("x", "c2", "pass"), ("b", "c1", "fail"), ("y", "c2", "pass"), ("c", "c1", "fail"))
    assert n == 3, "three misses in config c1 under three different criteria: %r" % n


def t_a_criterion_and_a_config_of_one_name_count_apart():
    n = worst(("c1", "c2", "fail"), ("x", "c3", "pass"), (None, "c1", "fail"), ("x", "c3", "pass"), ("c1", "c2", "fail"))
    assert n == 2, "criterion c1 and config c2 have two misses each, config c1 one: %r" % n


def t_a_sitting_restarts_the_count_and_fresh_misses_send_it_back():
    log = Log().runs("fail", "fail", "fail").note(R.SAT + ": cause found, abc123")
    assert log.verdict() is None, "the pilot's finding gets its fix and retest"
    assert log.runs("fail", "fail").verdict() is None, "two misses after a sitting are still only two"
    assert kind(log.runs("fail").verdict()) == "streak", "three fresh misses go back to a pilot"


def t_blocked_owner_and_closed_never_route():
    blocked = Log().runs("fail", "fail", "fail").add("block", reason="x", seat="OWNER")
    assert model.replay(blocked.evs).items[IT].blocked, "the block event did not land, so this case proves nothing"
    assert blocked.verdict() is None, "blocked"
    assert Log().runs("fail", "fail", "fail").add("needs", to="owner", seat="BENCH").verdict() is None, "needs owner is his look"
    closed = Log().runs("fail", "fail", "fail").add("drop", reason="x", why="x", seat="OWNER")
    assert model.replay(closed.evs).items[IT].state not in model.OPEN_STATES, "the drop did not land: proves nothing"
    assert closed.verdict() is None, "closed"


def t_an_art_verdict_never_routes():
    assert Log("RIVER_WEIR_ART_JUDGE_SQUINTS").runs("fail", "fail", "fail").verdict() is None, "JUDGE is not a debug"


def t_a_lane_pause_is_not_a_test():
    assert Log().runs("fail", "fail", "fail", config="steve-lane").verdict() is None, "steve-lane records pauses"


def t_a_seat_can_ask_for_live_observation():
    log = Log().note(R.WANTED + ": only shows live")
    assert kind(log.verdict()) == "wanted", "a wanted note routes with no runs at all"
    assert log.note(R.SAT + ": seen").verdict() is None, "a sitting answers it"
    assert Log().note("a note that mentions " + R.WANTED).verdict() is None, "the marker must start the note"


def t_a_live_diagnose_routes_once():
    log = Log(DIAG).add("needs", to="bridge", seat="BENCH")
    assert kind(log.verdict()) == "diagnose", "a DIAGNOSE on the live game goes to a pilot first"
    assert log.note(R.SAT + ": done").verdict() is None, "and is cleared by the sitting"
    assert Log(DIAG).verdict() is None, "an offline DIAGNOSE stays with its seat"


def t_host_prefers_steve_then_archmagi_then_nothing():
    assert R.pick_host({"stevedesktop": "FREE", "archmagi": "FREE"}) == "stevedesktop", "Steve's game is ours"
    assert R.pick_host({"stevedesktop": "HELD", "archmagi": "FREE"}) == "archmagi", "a busy lane falls to Archmagi"
    assert R.pick_host({"stevedesktop": None, "archmagi": "STALE"}) == "archmagi", "an unreachable host is not picked"
    assert R.pick_host({"stevedesktop": "HELD", "archmagi": "HELD"}) is None, "both held means wait, never force"


def t_read_statuses_survives_an_unreachable_steve():
    class Guard(object):
        @staticmethod
        def status():
            return {"state": "HELD"}

        @staticmethod
        def remote(host, args, timeout=0):
            return 255, "ssh: no route"
    assert R.read_statuses(Guard) == {"archmagi": "HELD", "stevedesktop": None}, "ssh failure reads as unknown"


def t_each_host_brief_carries_its_own_take():
    v = {"id": IT, "kind": "streak", "why": "3 non-pass runs in a row"}
    steve, arch = R.brief(v, "stevedesktop"), R.brief(v, "archmagi")
    assert "--host stevedesktop" in steve and "STEVE_WSL" in steve and "rm-testpilot" in steve, steve
    assert "--host archmagi" in arch and "ModsConfig" in arch and R.SAT in arch, arch


def t_dispatcher_reads_the_route_and_tells_the_seat():
    out = "%s   ready  row 1  needs bridge  target x\ntitle\n\n%s\n" % (
        IT, R.route_line({"id": IT, "why": "3 non-pass runs in a row"}))
    ticket = dispatcher.parse_peek(out)
    assert ticket == {"id": IT, "needs": "bridge", "pilot": "3 non-pass runs in a row"}, repr(ticket)
    text = dispatcher.message("FOUNDRY", {}, ticket, "r1")
    assert "TEST PILOT" in text and "rimflow pilot %s" % IT in text and "rm-testpilot" in text, text


def t_no_route_keeps_the_old_ticket_and_message():
    ticket = dispatcher.parse_peek("%s   ready  row 1  needs -  target x\n" % IT)
    assert ticket == {"id": IT, "needs": None}, repr(ticket)
    assert "TEST PILOT" not in dispatcher.message("FOUNDRY", {}, ticket, "r1"), "an ordinary ring is unchanged"


def t_a_route_for_another_item_is_not_this_tickets():
    out = "%s   ready  row 1  needs -\nROUTE rm-testpilot OTHER_ITEM_X: 3 non-pass runs\n" % IT
    assert "pilot" not in dispatcher.parse_peek(out), "the route must name the peeked item"


def t_open_states_pinned_to_the_model():
    assert R.OPEN_STATES == model.OPEN_STATES, "testpilot_route.OPEN_STATES drifted from the model's"


CASES = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]

if __name__ == "__main__":
    for fn in CASES:
        try:
            fn(); PASS.append(fn.__name__); print("ok    " + fn.__name__)
        except (AssertionError, model.TransitionError) as e:
            FAIL.append(fn.__name__); print("FAIL  %s\n        %s" % (fn.__name__, e))
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
