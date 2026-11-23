#!/usr/bin/env python3
"""selftest_maturation_nonmod.py: the promises of design/specs/2026-11-22-non-mod-pipeline-section/boundary.md.

    python3 src/RimMandrake/Utils/selftest_maturation_nonmod.py

Fixture ledger items, events, run records and a red reading; no ledger, no network, no game. On a tree before the
section (no maturation_nonmod.py, no section on the page) every test is RED for the reported reason: the page shows no
pipeline for work that is not mod work.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import maturation_nonmod as N  # noqa: E402
except ImportError:
    N = None
import maturation_now as M  # noqa: E402

NOW = 1_800_000_000.0
H = 3600.0
MODS = ["FlowWorks", "Pyrelands", "GimmeSomeSlack", "AlphaDeltaGamma", "AmberDuskGrove"]


def iso(t):
    import datetime as dt
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def item(iid, title, state="proposed", days=1.0, **kw):
    d = {"id": iid, "title": title, "state": state, "kind": kw.pop("kind", "task"), "created_at": iso(NOW - days * 24 * H),
         "wait_until": None, "wait_reason": None, "blocked": False, "blocked_kind": None, "blocked_on": None,
         "blocked_reason": None, "caused_by": None}
    d.update(kw)
    return d


def rec(unit, iid, at, status="finished", result="success (exited 0)", **kw):
    r = {"unit": unit, "item": iid, "at": at, "ended": None if status == "running" else at + 600, "status": status,
         "live_state": status, "result": None if status == "running" else result, "budget_usd": 5.0, "env": {}}
    r.update(kw)
    return r


def need():
    assert N is not None, "no maturation_nonmod.py: the page has no section for work that is not mod work"


def stores(extra_filed=0, red_at=None):
    it = [
        item("RIMMANDRAKE_FIX_PAGE_TYPO_NEVER_LAUNCHED", "Fix the typo on the status page", days=9),
        item("RIMMANDRAKE_BUILD_LIVE_THING", "Build the live thing", days=2),
        item("SELFTEST_FIX_RED_ONE", "Nightly red: selftest_one fails", days=0.5),
        item("SELFTEST_FIX_RED_STOPPED", "Nightly red: selftest_two fails", days=0.6),
        item("RIMMANDRAKE_WAIT_DATE_PASSED", "Read the week's numbers", days=8, wait_until=iso(NOW - 24 * H),
             wait_reason="the week ends"),
        item("RIMMANDRAKE_WAIT_DATE_FUTURE", "Read next week's numbers", days=3, wait_until=iso(NOW + 48 * H),
             wait_reason="next week ends"),
        item("RIMMANDRAKE_BLOCKED_ON_TYPO", "Ship after the typo fix", days=4, blocked=True, blocked_kind="item",
             blocked_on="RIMMANDRAKE_FIX_PAGE_TYPO_NEVER_LAUNCHED"),
        item("RIMMANDRAKE_HELD_FOR_OWNER", "His decision on the thing", days=5, blocked=True, blocked_kind="owner",
             blocked_reason="his call"),
        item("RIMMANDRAKE_WAIT_LIVE_GAME", "Look at it in a live game", days=6, blocked=True, blocked_kind="live",
             blocked_reason="needs a game"),
        item("RIMMANDRAKE_ENDED_STOPPED", "A run that timed out", days=3),
        item("RIMMANDRAKE_ENDED_LEFT_OPEN", "A run that left work", days=3),
        item("RIMMANDRAKE_ENDED_SILENT", "A run that said nothing", days=3),
        item("RIMMANDRAKE_ENDED_CAPPED", "A run that hit its cap", days=3),
        item("RIMMANDRAKE_REFUSED_LAUNCH", "A launch that was refused", days=3),
        item("RIMMANDRAKE_UNIT_DIED", "A run whose unit died", days=3),
        item("RIMMANDRAKE_READY_LOOK", "A look staged for him", days=2),
        # mod work, never in a list
        item("RIMMANDRAKE_FIX_FLOWWORKS_PUMP", "Fix the pump", days=7),
        item("RIMMANDRAKE_TUNE_FIRE_SPREAD", "Pyrelands fire spreads too far", days=7),
        item("RIMMANDRAKE_RUN_CONTROLLED", "A stage run", days=7),
        # a tie: ADG is the initials of two mods
        item("RIMMANDRAKE_FIX_ADG_THING", "Fix the ADG thing", days=7),
        # closed
        item("RIMMANDRAKE_CLOSED_RECENT", "Closed two hours ago", state="done", days=4),
        item("RIMMANDRAKE_CLOSED_OLD", "Closed thirty hours ago", state="done", days=4),
        item("RIMMANDRAKE_REOPENED", "Closed then reopened", days=4),
        item("RIMMANDRAKE_FIX_FLOWWORKS_DONE", "Closed mod work", state="done", days=4),
    ]
    for k in range(extra_filed):
        it.append(item("RIMMANDRAKE_EXTRA_FILED_%s" % chr(65 + k), "Extra filed item %d" % k, days=1 + k / 100.0))
    items = {x["id"]: x for x in it}
    evs = [
        {"event": "file", "id": "RIMMANDRAKE_BUILD_LIVE_THING", "ts": iso(NOW - 48 * H), "why": "the owner asked for it"},
        {"event": "note", "id": "RIMMANDRAKE_ENDED_LEFT_OPEN", "ts": iso(NOW - 2 * H), "text": "LEFT OPEN: step two"},
        {"event": "note", "id": "RIMMANDRAKE_ENDED_SILENT", "ts": iso(NOW - 2 * H),
         "text": "DETACHED run u-silent left work no remote had; NEXT: restore it from that bundle"},
        {"event": "note", "id": "RIMMANDRAKE_READY_LOOK", "ts": iso(NOW - 1 * H), "text": "READY TO SHOW: save LOOK_1"},
        {"event": "note", "id": "RIMMANDRAKE_FIX_PAGE_TYPO_NEVER_LAUNCHED", "ts": iso(NOW - 1 * H), "text": "an ordinary note"},
        {"event": "close", "id": "RIMMANDRAKE_CLOSED_RECENT", "ts": iso(NOW - 2 * H)},
        {"event": "close", "id": "RIMMANDRAKE_CLOSED_OLD", "ts": iso(NOW - 30 * H)},
        {"event": "close", "id": "RIMMANDRAKE_REOPENED", "ts": iso(NOW - 3 * H)},
        {"event": "close", "id": "RIMMANDRAKE_FIX_FLOWWORKS_DONE", "ts": iso(NOW - 2 * H)},
    ]
    recs = [
        rec("u-live", "RIMMANDRAKE_BUILD_LIVE_THING", NOW - 3 * H, status="running"),
        rec("u-stop", "RIMMANDRAKE_ENDED_STOPPED", NOW - 5 * H, result="timeout (killed KILL)"),
        rec("u-left", "RIMMANDRAKE_ENDED_LEFT_OPEN", NOW - 4 * H,
            continue_plan={"act": "continue", "target": "RIMMANDRAKE_ENDED_LEFT_OPEN", "unit": "u-left"}),
        rec("u-silent", "RIMMANDRAKE_ENDED_SILENT", NOW - 4 * H),
        rec("u-cap", "RIMMANDRAKE_ENDED_CAPPED", NOW - 4 * H, result="killed: unknown (- -)"),
        rec("u-refused", "RIMMANDRAKE_REFUSED_LAUNCH", NOW - 4 * H, status="refused", result=None),
        rec("u-dead", "RIMMANDRAKE_UNIT_DIED", NOW - 4 * H, status="running", live_state="dead"),
        rec("u-ctl", "RIMMANDRAKE_RUN_CONTROLLED", NOW - 4 * H, env={"RM_CONTROL_MOD": "Pyrelands"}),
    ]
    red_at = NOW - 300 if red_at is None else red_at
    return {"mods": list(MODS), "items": items, "evs": evs, "records": recs,
            "red_reading": {"at": red_at, "items": {
                "SELFTEST_FIX_RED_ONE": {"decision": "slots_full", "why": "2 live"},
                "SELFTEST_FIX_RED_STOPPED": {"decision": "stopped", "why": "an attempt ended and the item is open"}}},
            "red_state": {"items": {"SELFTEST_FIX_RED_OLD": {"attempts": [{"unit": "u-red"}]}}},
            "alarms": {"X:y": {"item": "OPS_ALARM_ITEM", "state": "OPEN", "cause": "X:y"}},
            "games": ["ArchBig FREE", "ArchSmall HELD by BENCH"], "showings": ["RIMMANDRAKE_READY_LOOK"], "causes": {}}


def spend(r):
    return ("UNMEASURED", None, r.get("unit") == "u-cap")


def sec(s=None):
    need()
    return N.section(s or stores(), NOW, spend=spend)


def text(s=None):
    return "\n".join(N.markdown(sec(s)))


def ids_in(lines):
    return " ".join(str(x) for x in lines)


# ---- the promises -------------------------------------------------------------------------------------------------

def t_mod_or_not_by_one_rule():
    need()
    x = sec()
    assert N.classify("RIMMANDRAKE_FIX_FLOWWORKS_PUMP", "Fix the pump", MODS, set()) == "mod"
    assert N.classify("RIMMANDRAKE_TUNE_FIRE_SPREAD", "Pyrelands fire spreads too far", MODS, set()) == "mod"
    assert N.classify("RIMMANDRAKE_RUN_CONTROLLED", "A stage run", MODS, {"RIMMANDRAKE_RUN_CONTROLLED"}) == "mod"
    assert N.classify("RIMMANDRAKE_FIX_ADG_THING", "", MODS, set()) == "unclassed"
    assert N.classify("RIMMANDRAKE_FIX_PAGE_TYPO_NEVER_LAUNCHED", "Fix the typo", MODS, set()) == "nonmod"
    assert x["open_total"] == 17, x["open_total"]
    assert x["unclassed"] == 1 and x["unclassed_ids"] == ["RIMMANDRAKE_FIX_ADG_THING"], x["unclassed_ids"]
    t = text()
    for mod_id in ("RIMMANDRAKE_FIX_FLOWWORKS_PUMP", "RIMMANDRAKE_TUNE_FIRE_SPREAD", "RIMMANDRAKE_RUN_CONTROLLED",
                   "RIMMANDRAKE_FIX_FLOWWORKS_DONE"):
        assert mod_id not in t, mod_id + " is mod work and is in a list"
    assert "item_identity.named_mod" in t and "Could not class: 1" in t


def t_steps_as_they_are():
    x = sec()
    st = x["steps"]
    assert [s["step"] for s in st] == ["Filed on the ledger", "Launched", "Runs", "Ends", "Read and acted on"], st
    assert st[0]["who"] == "program" and st[2]["who"] == "program" and st[3]["who"] == "program"
    assert st[4]["who"] == "by the Conductor's hand"
    assert "Conductor's hand" in st[1]["who"]
    for prog in ("red dispatcher", "left_open_continue", "stop_resume"):
        assert prog in st[1]["how"], prog
    assert "No program launches any other non-mod item" in st[1]["how"]
    assert "no program reads a run's result" in st[4]["how"]
    got = {s["step"]: s["sits"] for s in st}
    # filed: TYPO, RED_STOPPED (not a red wait), READY_LOOK, REOPENED
    assert got == {"Filed on the ledger": 4, "Launched": 1, "Runs": 1, "Ends": 1, "Read and acted on": 5}, got
    parked = dict(x["parked"])
    assert parked == {"waiting on a date": 2, "blocked on another item": 1, "held or blocked on something else": 2}, parked
    assert sum(got.values()) + sum(parked.values()) == x["open_total"]
    t = text()
    assert "Sitting here: **4**" in t and "Parked off the steps" in t


def t_launcher_from_records():
    need()
    red = {"u-red"}
    assert "red dispatcher" in N.launcher({"unit": "u-red"}, red)
    assert "left_open_continue" in N.launcher({"unit": "u2", "continued_from": "u1"}, red)
    assert "stop_resume" in N.launcher({"unit": "u3", "resumed_from": "u1"}, red)
    assert "Conductor's hand" in N.launcher({"unit": "u4"}, red)
    blind = N.launcher({"unit": "u4"}, None)
    assert blind.startswith("UNMEASURED") and "Conductor" not in blind, blind
    assert "left_open_continue" in N.launcher({"unit": "u2", "continued_from": "u1"}, None)


def t_doing_now_rows():
    x = sec()
    d = x["doing"]
    assert len(d) == 1, d
    r = d[0]
    assert r["what"].startswith("Build the live thing (`RIMMANDRAKE_BUILD_LIVE_THING`)"), r["what"]
    assert "Conductor's hand" in r["who"] and "PST" in r["since"] and r["why"] == "the owner asked for it", r
    s = stores()
    s["evs"] = [e for e in s["evs"] if e.get("event") != "file"]
    assert sec(s)["doing"][0]["why"] == "no cause on the ledger"
    t = text()
    assert "Doing now (1)" in t and "Why: the owner asked for it" in t


def t_next_names_its_wait():
    x = sec()
    nx = ids_in(x["next"])
    assert "Nightly red: selftest_one fails (`SELFTEST_FIX_RED_ONE`) waits for a free red-fix slot" in nx, nx
    assert "left_open_continue continues u-left" in nx, nx
    assert "1 item waits on a live game" in nx and "ArchBig FREE" in nx and "ArchSmall HELD" in nx, nx
    assert "The Conductor's hand: 10 items wait for it" in nx, nx
    assert "Fix the typo on the status page" in nx      # the oldest of those
    stale = ids_in(sec(stores(red_at=NOW - 3 * H))["next"])
    assert "180 min old" in stale and "SELFTEST_FIX_RED_ONE" not in stale, stale


def t_closed_last_day():
    c = sec()["closed"]
    assert c["count"] == 1 and c["by"] == {"close": 1}, c
    assert "Closed two hours ago (`RIMMANDRAKE_CLOSED_RECENT`)" in c["rows"][0]["what"]
    assert "Closed in the last 24 h (1: 1 closed)" in text()


def t_open_by_reason_oldest_first():
    x = sec()
    o = x["open"]
    assert {k: v["count"] for k, v in o.items()} == {"hand": 10, "red": 1, "date": 2, "item": 1, "other": 2}, o
    dates = o["date"]["rows"]
    assert "LATE" in dates[0]["why"] and "LATE" not in dates[1]["why"], dates
    hand = [r["what"] for r in o["hand"]["rows"]]
    assert hand[0].startswith("Fix the typo"), hand                     # 9 days: the oldest
    assert "blocked on Fix the typo on the status page" in o["item"]["rows"][0]["why"]
    assert any("held for the owner" in r["why"] for r in o["other"]["rows"])
    assert all(r["age"].startswith("filed ") and "min" not in r["age"] for r in o["hand"]["rows"])
    assert o["hand"]["rows"][0]["age"].endswith(", 9 days"), o["hand"]["rows"][0]["age"]
    assert N.game_line({"game": "archmagi", "state": "HELD", "seat": "BENCH", "since_local": "9:00 PM PST",
                        "purpose": "a visit", "held_s": 600}) == "ArchBig HELD by BENCH since 9:00 PM PST, for: a visit"
    big = sec(stores(extra_filed=15))
    t = "\n".join(N.markdown(big))
    assert big["open"]["hand"]["count"] == 25
    assert "Waiting on the Conductor's hand (25)" in t and "… and %d more" % (25 - N.ROWS) in t, t[:400]


def t_escalated_from_run_ends():
    e = sec()["escalated"]
    kinds = {r["what"].split("(`")[1].rstrip("`)"): r["kind"] for r in e}
    assert kinds == {"RIMMANDRAKE_ENDED_STOPPED": "stopped", "RIMMANDRAKE_ENDED_LEFT_OPEN": "left open",
                     "RIMMANDRAKE_ENDED_SILENT": "said nothing", "RIMMANDRAKE_ENDED_CAPPED": "capped",
                     "RIMMANDRAKE_REFUSED_LAUNCH": "refused", "RIMMANDRAKE_UNIT_DIED": "stopped",
                     "SELFTEST_FIX_RED_STOPPED": "red stopped"}, kinds
    s = stores()       # a NEXT: line the run wrote itself is a left-open
    s["evs"].append({"event": "note", "id": "RIMMANDRAKE_ENDED_SILENT", "ts": iso(NOW - H), "role_unit": "u-silent",
                     "text": "done part one. NEXT: do part two"})
    assert any(r["kind"] == "left open" and "ENDED_SILENT" in r["what"] for r in sec(s)["escalated"])


def t_ready_for_review():
    r = sec()["ready"]
    assert len(r) == 1, r
    assert r[0]["what"].startswith("A look staged for him") and "READY TO SHOW" in r[0]["note"]
    assert r[0]["where"].endswith(r"showings\RIMMANDRAKE_READY_LOOK"), r[0]["where"]
    s = stores()
    s["evs"].append({"event": "note", "id": "RIMMANDRAKE_FIX_PAGE_TYPO_NEVER_LAUNCHED", "ts": iso(NOW - H),
                     "text": "the keeper save is LOOK_2 for him"})
    r2 = sec(s)["ready"]
    assert len(r2) == 2 and any("no showings folder" in x["where"] for x in r2), r2
    s["evs"].append({"event": "note", "id": "RIMMANDRAKE_WAIT_DATE_FUTURE", "ts": iso(NOW - H),
                     "text": "floor grows zero flora; No keeper save. NEXT: restage"})     # a negation is not a look
    assert len(sec(s)["ready"]) == 2, sec(s)["ready"]


def t_cannot_see_is_unmeasured():
    need()
    for x in (sec(), N.section(N.off_stores("off"), NOW)):
        assert len(x["cannot"]) >= 5 and all(c.startswith("UNMEASURED: ") for c in x["cannot"]), x["cannot"]
        t = "\n".join(N.markdown(x))
        assert "What this section cannot see" in t and all(c.split(".")[0] in t for c in x["cannot"])
    assert any("promised in conversation" in c for c in N.CANNOT)


def t_four_answers_differ():
    need()
    blind = "\n".join(N.markdown(N.safe_section(N.off_stores("live reads off (--no-live)"), NOW)))
    assert "Could not look: every store (live reads off (--no-live))" in blind and "UNMEASURED" in blind, blind
    assert "Sitting here" not in blind and "(0)" not in blind
    norec = stores()
    norec["records"] = None
    norec["causes"] = {"the run records": "run records: OSError: gone"}
    x = sec(norec)
    t = "\n".join(N.markdown(x))
    assert x["doing"] == "UNMEASURED" and x["steps"][0]["sits"] == "UNMEASURED" and x["escalated"] == "UNMEASURED"
    assert "Doing now (UNMEASURED)" in t and "Could not look: the run records" in t, t[:600]
    failed = "\n".join(N.markdown(N.safe_section({"items": 5, "causes": {}}, NOW)))
    assert failed.count("FAILED") == 1 and "Doing now" not in failed, failed
    ok = text()
    assert "Waiting on the red dispatcher (1)" in ok
    zero = stores()
    zero["red_reading"]["items"] = {}
    z = "\n".join(N.markdown(sec(zero)))
    assert "Open and why: Waiting on the red dispatcher (0)" in z and "none (looked: the ledger)" in z, z
    assert len({blind, t, failed, z}) == 4


def t_placed_under_pipeline_now():
    need()
    d = {"mods": [], "others": [], "held": {"total": 0, "counted": 0, "counted_files": 0, "uncounted": [],
                                            "per_mod": {}},
         "needs": {"mandrake": [], "conductor": [], "pipeline": ["Slots: 0 live"]}, "now": NOW,
         "intake": {"count": 0, "questions_total": 0}, "errors": [], "convergence": None, "nonmod": sec()}
    import datetime as dt
    md, page = M.build(d, dt.datetime.fromtimestamp(NOW, dt.timezone.utc))
    a, b, c = md.find("## Pipeline now"), md.find("## " + N.TITLE), md.find("mods in the pipeline")
    assert -1 < a < b < c, (a, b, c)
    a, b, c = page.find("Pipeline now (the Dispatch tick)"), page.find(">" + N.TITLE + "<"), page.find("mods in the pipeline")
    assert -1 < a < b < c, (a, b, c)
    # Typora: no blank line inside the HTML block
    blk = N.html_block(d["nonmod"])
    assert "\n" not in blk


def t_same_inputs_same_section():
    need()
    a = N.markdown(N.section(stores(), NOW, spend=spend))
    b = N.markdown(N.section(copy.deepcopy(stores()), NOW, spend=spend))
    assert a == b
    assert N.html_block(N.section(stores(), NOW, spend=spend)) == N.html_block(N.section(stores(), NOW, spend=spend))


def main():
    tests = [t_mod_or_not_by_one_rule, t_steps_as_they_are, t_launcher_from_records, t_doing_now_rows,
             t_next_names_its_wait, t_closed_last_day, t_open_by_reason_oldest_first, t_escalated_from_run_ends,
             t_ready_for_review, t_cannot_see_is_unmeasured, t_four_answers_differ, t_placed_under_pipeline_now,
             t_same_inputs_same_section]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
