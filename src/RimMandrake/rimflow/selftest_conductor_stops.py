#!/usr/bin/env python3
"""selftest_conductor_stops.py: the promises of design/specs/2026-11-26-conductor-stops/boundary.md (each t_ function
is one promise, by name). Offline: fake readings, a temp concepts root, fake items. Written before conductor_stops.py;
seen failing on the base (the module absent, owed.view without stops).

    python3 src/RimMandrake/rimflow/selftest_conductor_stops.py
"""
import json
import os
import re
import sys
import tempfile
from types import SimpleNamespace as NS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
NOW = 1_800_000_000.0
H = 3600.0


def CS():
    import conductor_stops
    return conductor_stops


def reading(items, at=NOW - 60):
    return {"at": at, "items": items}


def concepts(rests, sorted_ids=None):
    root = tempfile.mkdtemp(prefix="cs_concepts_")
    for mod, (stage, since) in rests.items():
        d = os.path.join(root, mod, "version")
        os.makedirs(os.path.join(d, "next_version"))
        with open(os.path.join(d, "stage_record.json"), "w") as f:
            json.dump({"mod": mod, "stage": stage, "since": since}, f)
    for mod, ids in (sorted_ids or {}).items():
        with open(os.path.join(root, mod, "version", "next_version", "tickets.md"), "w") as f:
            f.write("# sorted\n" + "".join("- %s: a reason\n" % i for i in ids))
    return root


def iso(t):
    import datetime as dt
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat()


LANE = {"C1": {"decision": "chain_stop", "why": "its chain holds 3 lane runs", "since": NOW - 31 * H},
        "S1": {"decision": "stopped", "why": "a run ended with no next act", "since": NOW - 17 * H},
        "N1": {"decision": "no_bundle", "why": "left out of WB-x", "since": NOW - 2 * H},
        "H1": {"decision": "adopt_too_heavy", "why": "its ## verify runs x.py", "since": NOW - 60},
        "W1": {"decision": "waiting", "why": "a dated wait", "since": NOW - 5 * H},
        "X1": {"decision": "close_refused", "why": "close refused (an owed criterion): x; repair: y", "since": NOW - 3 * H},
        "R1": {"decision": "routed", "why": "routed to judge", "since": NOW - 5 * H}}


def t_the_four_kinds_go_to_the_conductor():
    rows = CS().rows(reading(LANE), NOW, rests={})
    kinds = {r["items"][0]: r["kind"] for r in rows}
    assert kinds == {"C1": "chain_stop", "S1": "stopped", "N1": "no_bundle", "H1": "adopt_too_heavy",
                     "X1": "close_refused"}, kinds
    h1 = [r for r in rows if r["items"] == ["H1"]][0]
    assert h1["age"] == "1m", "no clock comes first: a minute-old stop is listed (%s)" % h1["age"]
    c1 = [r for r in rows if r["items"] == ["C1"]][0]
    assert c1["age"] == "31h00" and "chain" in c1["why"], c1
    n1 = [r for r in rows if r["items"] == ["N1"]][0]
    # a clear of the lane's state cannot change what the host's sort read (a refusal note, a hold, a lease): the hint
    # names the host's reason, never `clear` (2026-11-27, item RIMMANDRAKE_LET_CLEAR_PASS_CHAIN_STOP_THREE_CLEARS_NO_LAUNCH)
    assert "list_dispatch.py clear" not in n1["why"] and "reason" in n1["why"], n1
    # the lead row's why as list_dispatch.launch_bundle_row writes it: the host's line, then "; its own: <reason>". The
    # host's line for an item system is 135 characters, so a cut of the whole why at 160 left 14 of the reason.
    own = "a dated wait of its own ahead: 2026-12-01 (the owner's walk of Pyrelands; nothing to run before it)"
    long_why = ("on SteveDesktop: NO BUNDLE: item:RIMMANDRAKE_READ_FIX_EB96DF47E5_WITH_FRESH_EYES has no ready member "
                "(0 closed by the sort, 1 left out); its own: " + own)
    n2 = CS().rows(reading({"N2": {"decision": "no_bundle", "why": long_why, "since": NOW - H}}), NOW, rests={})[0]
    assert own in n2["why"], "the hint names the host's reason, so the row shows it whole: %s" % n2["why"]
    assert [r["items"][0] for r in rows][0] == "C1", "oldest first"
    assert CS().rows(reading({"X": {"decision": "chain_stop", "why": "w"}}), NOW, rests={})[0]["age"] == "age?", \
        "a row with no since says so, never 0"


def t_a_resting_mod_sorts_after_an_hour():
    mw = {"G1": {"decision": "mod_work", "why": "waits for the run of GSS", "mod": "GSS", "since": NOW - 40 * H},
          "G2": {"decision": "mod_work", "why": "w", "mod": "GSS", "since": NOW - 40 * H},
          "G3": {"decision": "mod_work", "why": "w", "mod": "GSS", "since": NOW - 40 * H, "wait_until": NOW + 5 * 86400},
          "G4": {"decision": "mod_work", "why": "w", "mod": "GSS", "since": NOW - 40 * H},
          "E1": {"decision": "mod_work", "why": "w", "mod": "EK", "since": NOW - 30 * 60},
          "F1": {"decision": "mod_work", "why": "w", "mod": "FW", "since": NOW - 40 * H}}
    root = concepts({"GSS": ("passed", iso(NOW - 45 * H)), "EK": ("passed", iso(NOW - 30 * 60)),
                     "FW": ("offline_build", iso(NOW - 45 * H))}, sorted_ids={"GSS": ["G4"]})
    rests = CS().rests(root)
    assert set(rests) == {"GSS", "EK"}, "only a passed mod rests (%s)" % rests
    rows = CS().rows(reading(mw), NOW, rests=rests, sorted_of=lambda m: CS().sorted_ids(root, m))
    rest = [r for r in rows if r["kind"] == "mod_rest"]
    assert len(rest) == 1 and rest[0]["mod"] == "GSS" and rest[0]["items"] == ["G1", "G2"], rest
    assert rest[0]["age"] == "45h00", "the age is the rest's (%s)" % rest[0]["age"]
    assert "sort" in rest[0]["why"], "the line names the sort command"
    unread = CS().rows(reading(mw), NOW, rests={"GSS": None}, sorted_of=lambda m: [])
    assert [r["age"] for r in unread if r["kind"] == "mod_rest"] == ["age?"], "an unread rest start hid the mod"


def t_the_owed_view_shows_them():
    import model
    import owed
    w = model.replay([], strict=True)
    rows = CS().rows(reading(LANE), NOW, rests={})
    out = "\n".join(owed.view(w, "BENCH", now=NOW, stops=(rows, None)))
    assert "STOPS FOR YOU (5)" in out and "C1" in out and "chain_stop" in out, out
    blind = "\n".join(owed.view(w, "BENCH", now=NOW, stops=(None, "the lane reading is 200 min old")))
    assert "STOPS FOR YOU: could not look (the lane reading is 200 min old)" in blind, blind
    assert "STOPS FOR YOU" not in "\n".join(owed.view(w, "BENCH", now=NOW)), "no stops given: no block"
    got, cause = CS().from_reading(reading(LANE, at=NOW - CS().READING_STALE_S - 1), NOW, rests={})
    assert got is None and "could not look" in cause, "a stale reading is not read as now"


def t_unread_asks_go_to_the_conductor():
    import model
    import owed
    w = model.replay([], strict=True)
    asks = ([{"item": "ASK_X", "q": "Is the quest owed v1 work?", "age": "3d"}], None)
    out = "\n".join(owed.view(w, "BENCH", now=NOW, asks=asks))
    assert "ASKS TO READ (1)" in out and "ASK_X" in out and "ASK HIS:" in out, out
    evs = [{"event": "file", "seat": "BENCH", "ts": "2026-11-20T12:00:00Z", "id": "ASK_X", "title": "t", "kind": "task",
            "needs": "offline", "for": "BENCH"},
           {"event": "shape", "seat": "BENCH", "ts": "2026-11-21T12:00:00Z", "id": "ASK_X",
            "parts": [{"name": "p", "effect": None, "fooled_by": None,
                       "route": {"who": "owner", "ask": "Is the quest owed v1 work?", "resumes": "x"}}]}]
    w2 = model.replay(evs, strict=True)
    got, cause = CS().asks(evs, w2, now=model.iso_epoch("2026-11-24T12:00:00Z"))
    assert cause is None and [x["item"] for x in got] == ["ASK_X"], (got, cause)


def t_the_sort_is_one_line():
    root = concepts({"GSS": ("passed", iso(NOW - 45 * H))})
    ran = []
    item = NS(id="G1", open=True, home=None, title="fix src/RimMandrake/GimmeSomeSlack/x.cs")
    rc, line = CS().sort("G1", "lane", "a typo in a tooltip", item=item, mod="GSS", root=root,
                         runner=lambda argv: ran.append(argv) or 0)
    assert rc == 0 and ran and "fix:GSS" in " ".join(ran[0]) and "home" in ran[0], ran
    assert "fix:GSS" in line
    ran.clear()
    rc, line = CS().sort("G1", "next", "a new feature", item=item, mod="GSS", root=root,
                         runner=lambda argv: ran.append(argv) or 0)
    p = os.path.join(root, "GSS", "version", "next_version", "tickets.md")
    assert rc == 0 and "G1" in open(p).read() and ran and "./publish" in ran[0][0], (rc, ran)
    assert CS().sorted_ids(root, "GSS") == ["G1"]
    rc, line = CS().sort("G1", "next", "x", item=item, mod="NOPE", root=root, runner=lambda argv: 0)
    assert rc != 0 and "rest" in line, "a mod that does not rest is refused (%s)" % line


def t_each_limit_names_its_danger():
    src = open(os.path.join(HERE, "conductor_stops.py")).read()
    for name in ("REST_S", "READING_STALE_S"):
        m = re.search(r"^# .*\n(?:# .*\n)*%s = " % name, src, re.M)
        assert m and re.search(r"[Dd]anger|his words", m.group(0)), "%s has no danger line above it" % name


def main():
    failed = 0
    tests = [t_the_four_kinds_go_to_the_conductor, t_a_resting_mod_sorts_after_an_hour, t_the_owed_view_shows_them,
             t_unread_asks_go_to_the_conductor, t_the_sort_is_one_line, t_each_limit_names_its_danger]
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
