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
        item("RIMMANDRAKE_LANE_READY", "A lane item whose check fails", days=1.5, effect="cmd:false"),
        item("RIMMANDRAKE_LANE_HOLDS", "A lane item whose check holds", days=1.4, effect="cmd:true"),
        item("RIMMANDRAKE_LANE_STOPPED", "A lane item the lane stopped on", days=1.3, effect="cmd:false"),
        item("RIMMANDRAKE_LIVE_NO_MOD", "A lane run recorded for no mod", days=1.2, effect="cmd:false"),
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
        rec("u-nomod", "RIMMANDRAKE_LIVE_NO_MOD", NOW - 1 * H, status="running", env={"RM_CONTROL_MOD": "none"}),
    ]
    red_at = NOW - 300 if red_at is None else red_at
    return {"mods": list(MODS), "items": items, "evs": evs, "records": recs,
            "red_reading": {"at": red_at, "items": {
                "SELFTEST_FIX_RED_ONE": {"decision": "slots_full", "why": "2 live"},
                "SELFTEST_FIX_RED_STOPPED": {"decision": "stopped", "why": "an attempt ended and the item is open"}}},
            "red_state": {"items": {"SELFTEST_FIX_RED_OLD": {"attempts": [{"unit": "u-red"}]}}},
            "alarms": {"X:y": {"item": "OPS_ALARM_ITEM", "state": "OPEN", "cause": "X:y"}},
            "games": ["ArchBig FREE", "ArchSmall HELD by BENCH"], "showings": ["RIMMANDRAKE_READY_LOOK"], "causes": {},
            "his": {"RIMMANDRAKE_HELD_FOR_OWNER"},
            "lane": {"at": NOW - 120, "items": {
                "RIMMANDRAKE_LANE_HOLDS": {"decision": "close", "why": "the check holds"},
                "RIMMANDRAKE_LANE_STOPPED": {"decision": "stopped", "why": "2 Work runs ended and the check still fails"},
                "RIMMANDRAKE_LIVE_NO_MOD": {"decision": "live", "why": "u-nomod is live on it"},
                "RIMMANDRAKE_LANE_READY": {"decision": "slots_full", "why": "2 live Workshop Pipeline runs"}}}}


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
    assert x["open_total"] == 21, x["open_total"]
    assert x["unclassed"] == 1 and x["unclassed_ids"] == ["RIMMANDRAKE_FIX_ADG_THING"], x["unclassed_ids"]
    # detached_helper records RM_CONTROL_MOD=none on a run for no mod: that is not a recorded mod
    assert "RIMMANDRAKE_LIVE_NO_MOD" in x["stage_of"], "a run recorded for mod 'none' made its item mod work"
    t = text()
    for mod_id in ("RIMMANDRAKE_FIX_FLOWWORKS_PUMP", "RIMMANDRAKE_TUNE_FIRE_SPREAD", "RIMMANDRAKE_RUN_CONTROLLED",
                   "RIMMANDRAKE_FIX_FLOWWORKS_DONE"):
        assert mod_id not in t, mod_id + " is mod work and is in a list"
    assert "item_identity.named_mod" in t and "Could not class: 1" in t


WANT_STAGE = {
    "RIMMANDRAKE_FIX_PAGE_TYPO_NEVER_LAUNCHED": "shape", "RIMMANDRAKE_BUILD_LIVE_THING": "shape",
    "SELFTEST_FIX_RED_ONE": "shape", "SELFTEST_FIX_RED_STOPPED": "shape", "RIMMANDRAKE_WAIT_DATE_PASSED": "shape",
    "RIMMANDRAKE_ENDED_LEFT_OPEN": "shape", "RIMMANDRAKE_ENDED_SILENT": "shape", "RIMMANDRAKE_REOPENED": "shape",
    "RIMMANDRAKE_WAIT_DATE_FUTURE": "waiting", "RIMMANDRAKE_BLOCKED_ON_TYPO": "waiting",
    "RIMMANDRAKE_WAIT_LIVE_GAME": "waiting", "RIMMANDRAKE_HELD_FOR_OWNER": "review", "RIMMANDRAKE_READY_LOOK": "review",
    "RIMMANDRAKE_ENDED_STOPPED": "trouble", "RIMMANDRAKE_ENDED_CAPPED": "trouble", "RIMMANDRAKE_REFUSED_LAUNCH": "trouble",
    "RIMMANDRAKE_UNIT_DIED": "trouble", "RIMMANDRAKE_LANE_STOPPED": "trouble", "RIMMANDRAKE_LANE_READY": "ready",
    "RIMMANDRAKE_LANE_HOLDS": "verify", "RIMMANDRAKE_LIVE_NO_MOD": "work"}


def t_stages_from_one_rule():
    x = sec()
    assert x["stage_of"] == WANT_STAGE, {k: v for k, v in x["stage_of"].items() if WANT_STAGE.get(k) != v}
    st = {r["stage"]: r for r in x["stages"]}
    assert [r["stage"] for r in x["stages"]] == list(N.STAGE_ORDER)
    for k in N.STAGE_ORDER:
        assert st[k]["who"] in ("program", "by hand") and st[k]["how"], st[k]
    assert st["shape"]["who"] == "program" and st["ready"]["who"] == "program" and st["trouble"]["who"] == "by hand"
    assert sum(r["count"] for r in x["stages"]) == x["open_total"]
    assert st["shape"]["count"] == 8 and st["shape"]["oldest"].startswith("Fix the typo"), st["shape"]
    # the stage function the page is given is the one it uses
    seen = []
    N.section(stores(), NOW, spend=spend, stage=lambda f, t: seen.append(1) or N.LP.stage_of(f, t))
    assert len(seen) >= x["open_total"]
    t = text()
    assert "**Shape** · program · **8**" in t and "**Ready** · program · **1**" in t, t[:900]
    # a run end nobody acted on is trouble; one with a later act is not
    s = stores()
    s["evs"].append({"event": "note", "id": "RIMMANDRAKE_ENDED_STOPPED", "ts": iso(NOW - H),
                     "text": "DETACHED run u-stop ended timeout (killed KILL) after 600 s"})    # the finish's own note
    assert sec(s)["stage_of"]["RIMMANDRAKE_ENDED_STOPPED"] == "trouble"
    s["evs"].append({"event": "note", "id": "RIMMANDRAKE_ENDED_STOPPED", "ts": iso(NOW - H), "text": "read it"})
    assert sec(s)["stage_of"]["RIMMANDRAKE_ENDED_STOPPED"] == "shape"


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
    assert len(d) == 2 and d[1]["what"].startswith("A lane run recorded for no mod"), d
    r = d[0]
    assert r["what"].startswith("Build the live thing (`RIMMANDRAKE_BUILD_LIVE_THING`)"), r["what"]
    assert "Conductor's hand" in r["who"] and "PST" in r["since"] and r["why"] == "the owner asked for it", r
    s = stores()
    s["evs"] = [e for e in s["evs"] if e.get("event") != "file"]
    assert sec(s)["doing"][0]["why"] == "no cause on the ledger"
    t = text()
    assert "Doing now (2)" in t and "Why: the owner asked for it" in t


def t_next_names_its_wait():
    x = sec()
    nx = ids_in(x["next"])
    assert "1 Ready; what each waits for now: slots_full 1" in nx and "Ready: A lane item whose check fails" in nx, nx
    assert "Nightly red: selftest_one fails (`SELFTEST_FIX_RED_ONE`) waits for a free red-fix slot" in nx, nx
    assert "left_open_continue continues u-left" in nx, nx
    assert "1 item waits on a live game" in nx and "ArchBig FREE" in nx and "ArchSmall HELD" in nx, nx
    assert "Shape: 8 items have no outcome check and no route; the tick lists 0 of them" in nx, nx
    assert "the oldest is Fix the typo on the status page" in nx
    stale = ids_in(sec(stores(red_at=NOW - 3 * H))["next"])
    assert "180 min old" in stale and "SELFTEST_FIX_RED_ONE" not in stale, stale


def t_closed_last_day():
    c = sec()["closed"]
    assert c["count"] == 1 and c["by"] == {"close": 1}, c
    assert "Closed two hours ago (`RIMMANDRAKE_CLOSED_RECENT`)" in c["rows"][0]["what"]
    assert "Closed in the last 24 h (1: 1 closed)" in text()


def t_open_by_reason_oldest_first():
    x = sec()
    o = {g["reason"]: g for g in x["open"]}
    assert o["no outcome check yet (Shape)"]["count"] == 8, o
    assert o["no outcome check yet (Shape)"]["oldest"].startswith("Fix the typo on the status page"), o
    assert o["no outcome check yet (Shape)"]["oldest"].endswith(", 9 days"), o
    assert o["waiting on RIMMANDRAKE_FIX_PAGE_TYPO_NEVER_LAUNCHED"]["count"] == 1
    assert any(k.startswith("waiting on a date") for k in o) and any(k.startswith("waiting on a live block") for k in o), o
    assert sum(g["count"] for g in x["open"]) == x["open_total"]
    ranks = [N.STAGE_ORDER.index(g["stage"]) for g in x["open"]]
    assert ranks == sorted(ranks), ranks
    assert all("min" not in g["oldest"] for g in x["open"])
    assert N.game_line({"game": "archmagi", "state": "HELD", "seat": "BENCH", "since_local": "9:00 PM PST",
                        "purpose": "a visit", "held_s": 600}) == "ArchBig HELD by BENCH since 9:00 PM PST, for: a visit"
    big = sec(stores(extra_filed=15))
    t = "\n".join(N.markdown(big))
    assert {g["reason"]: g for g in big["open"]}["no outcome check yet (Shape)"]["count"] == 23
    assert "**no outcome check yet (Shape)** (23, program): oldest Fix the typo" in t, t[:400]


def t_escalated_from_run_ends():
    e = sec()["escalated"]
    kinds = {r["what"].split("(`")[1].rstrip("`)"): r["kind"] for r in e}
    assert kinds == {"RIMMANDRAKE_ENDED_STOPPED": "trouble", "RIMMANDRAKE_ENDED_CAPPED": "trouble",
                     "RIMMANDRAKE_REFUSED_LAUNCH": "trouble", "RIMMANDRAKE_UNIT_DIED": "trouble",
                     "RIMMANDRAKE_LANE_STOPPED": "trouble", "SELFTEST_FIX_RED_STOPPED": "red stopped"}, kinds
    words = {r["what"].split("(`")[1].rstrip("`)"): r["words"] for r in e}
    assert "was capped" in words["RIMMANDRAKE_ENDED_CAPPED"] and "was refused" in words["RIMMANDRAKE_REFUSED_LAUNCH"]
    assert "2 Work runs ended" in words["RIMMANDRAKE_LANE_STOPPED"], words


def t_ready_for_review():
    r = sec()["ready"]
    assert [x["what"].split("(`")[1].rstrip("`)") for x in r] == ["RIMMANDRAKE_READY_LOOK", "RIMMANDRAKE_HELD_FOR_OWNER"], r
    look = r[0]
    assert "READY TO SHOW" in look["note"] and look["where"].endswith(r"showings\RIMMANDRAKE_READY_LOOK"), look
    assert "routed to the owner" in r[1]["why"] and r[1]["where"] is None, r[1]
    assert "ready for his look" in look["why"], look
    s = stores()
    s["evs"].append({"event": "note", "id": "RIMMANDRAKE_FIX_PAGE_TYPO_NEVER_LAUNCHED", "ts": iso(NOW - H),
                     "text": "the keeper save is LOOK_2 for him"})
    r2 = sec(s)["ready"]
    assert len(r2) == 3 and any(x["where"] and "no showings folder" in x["where"] for x in r2), r2
    s["evs"].append({"event": "note", "id": "RIMMANDRAKE_WAIT_DATE_FUTURE", "ts": iso(NOW - H),
                     "text": "floor grows zero flora; No keeper save. NEXT: restage"})     # a negation is not a look
    assert len(sec(s)["ready"]) == 3, sec(s)["ready"]
    s["his"] = None                     # who is his could not be read: nothing is routed to him by that rule
    s["causes"] = {"who is his (owner_queue.is_his)": "ledger: OSError"}
    t = "\n".join(N.markdown(sec(s)))
    assert "Could not look: who is his" in t


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
    assert "Stages (" not in blind and "(0)" not in blind
    norec = stores()
    norec["records"] = None
    norec["causes"] = {"the run records": "run records: OSError: gone"}
    x = sec(norec)
    t = "\n".join(N.markdown(x))
    assert x["doing"] == "UNMEASURED" and x["escalated"] == "UNMEASURED"
    assert "Doing now (UNMEASURED)" in t and "Could not look: the run records" in t, t[:600]
    failed = "\n".join(N.markdown(N.safe_section({"items": 5, "causes": {}}, NOW)))
    assert failed.count("FAILED") == 1 and "Doing now" not in failed, failed
    nolane = stores()
    nolane["lane"] = None
    nolane["causes"] = {"the Workshop Pipeline tick's reading.json": "FileNotFoundError: gone"}
    y = sec(nolane)
    assert {y["stage_of"][i] for i in ("RIMMANDRAKE_LANE_READY", "RIMMANDRAKE_LANE_HOLDS")} == {"unmeasured"}, y["stage_of"]
    nl = "\n".join(N.markdown(y))
    assert "could not look: FileNotFoundError: gone" in nl and "**Unmeasured** · by hand · **3**" in nl, nl[:900]
    stale = stores()
    stale["lane"]["at"] = NOW - 2 * H
    assert sec(stale)["stage_of"]["RIMMANDRAKE_LANE_READY"] == "unmeasured"
    ok = text()
    zero = stores()
    zero["red_reading"]["items"] = {}
    zero["records"] = [r for r in zero["records"] if r["status"] != "running"]
    z = "\n".join(N.markdown(sec(zero)))
    assert "**Work** · program · **0**" in z and "Doing now (0)" in z and "none (looked: the run records" in z, z
    assert len({blind, t, failed, z, ok}) == 5
def page_dict(s=None, **kw):
    d = {"mods": [], "others": [], "held": {"total": 0, "counted": 0, "counted_files": 0, "uncounted": [],
                                            "per_mod": {}},
         "needs": {"mandrake": [], "conductor": [], "pipeline": ["Slots: 0 live of max_live 4"]}, "now": NOW,
         "intake": {"count": 0, "questions_total": 0}, "errors": [], "convergence": None, "nonmod": sec(s)}
    d.update(kw)
    return d


def built(d):
    import datetime as dt
    t = dt.datetime.fromtimestamp(NOW, dt.timezone.utc)
    return M.build(d, t), (M.build_detail(d, t) if hasattr(M, "build_detail") else ("", ""))


def t_lists_go_to_detail():
    (md, page), (dmd, dpage) = built(page_dict())
    for x in (md, page):
        assert N.TITLE not in x and "Pipeline now (the Dispatch tick)" not in x, "the whole lists are on the summary page"
        assert "MATURATION_DETAIL" in x, "the summary names its detail page"
    for x in (dmd, dpage):
        a, b, c = x.find("Pipeline now (the Dispatch tick)"), x.find(N.TITLE), x.find("mods in the pipeline")
        assert -1 < a < b < c, (a, b, c)
    assert "\n" not in N.html_block(sec())         # Typora: no blank line inside the HTML block


LOG_WORDS = ("Launched by", "rm-list-dispatch.timer", "reading.json", "item_identity", "oldest:", "Why: the owner asked",
             "python3 ", "maturation_dispatch.py")


def t_page_is_a_picture_not_a_log():
    s = stores(extra_filed=15)
    (md, page), _ = built(page_dict(s))
    for x in (md, page):
        assert N.PANEL_TITLE in x, "no Workshop Pipeline picture on the page"
        hit = [w for w in LOG_WORDS if w in x]
        assert not hit, "log lines on the summary page: %s" % hit
        assert len(x) < 40000, len(x)
    one = [ln for ln in md.splitlines() if "Workshop Pipeline: open" in ln]
    assert len(one) == 1 and one[0].startswith("<div>"), "the picture is one line of HTML (Typora)"
    import re as _re
    words = _re.findall(r">([^<>]+)</text>", one[0])
    for w in ("Shape", "Waiting", "Ready", "Work", "Verify", "Closed", "Trouble", "His review", "Conflict", "Unread",
              "being worked now", "stuck, needs a hand"):
        assert w in words, "%s is not in the picture" % w
    assert "23" in words and "36 open tickets that are not mod work, by stage" in words, words[:30]
    # a plain title first; an id only small and beside it, and never as the main text
    for w in words:
        assert not _re.match(r"[A-Z0-9]+_[A-Z0-9_]+$", w), "an id is main text: %s" % w
    assert "Build the live thing" in words and "A run that timed out" in words
    stuck = words.index("stuck, needs a hand")
    assert words[stuck - 1] == "6", words[stuck - 2:stuck + 1]


def t_a_question_for_the_conductor_is_its_own_block():
    s = stores()
    q = item("RIMMANDRAKE_ASK_WHO_MAY_ADVANCE", "May the program advance a mod", days=1, effect="cmd:false",
             shape={"size": "small", "parts": [{"name": "rule", "effect": None, "fooled_by": None,
                                                "route": {"who": "conductor", "ask": "rule it", "resumes": "its ruling"}}]})
    s["items"][q["id"]] = q
    s["lane"]["items"][q["id"]] = {"decision": "routed", "why": "a part is routed to conductor: rule it"}
    x = sec(s)
    assert [r["id"] for r in x["asked"]] == [q["id"]], x["asked"]
    assert q["id"] not in [r["id"] for r in x["escalated"]] and len(x["escalated"]) == len(sec()["escalated"])
    svg = N.panel(x)
    a, b = svg.index("stuck, needs a hand"), svg.index("a question for the Conductor")
    assert b > a and svg.index("May the program advance a mod") > b, "the question stands under its own head"
    assert "a question for the Conductor" not in N.panel(sec()), "no question: no head"
    assert dict(x["waits"])["a ruling of the Conductor"] == 1, x["waits"]


def t_waits_in_plain_words():
    x = sec()
    assert dict(x["waits"]) == {"a date": 1, "another ticket to close": 1, "a live game": 1}, x["waits"]
    assert sum(n for _k, n in x["waits"]) == {r["stage"]: r["count"] for r in x["stages"]}["waiting"]


def t_plain_titles():
    need()
    assert N.plain("Bridge conditions T10 (spec a/b.md row T10): flyer flight recorded as STATE: probes") == \
        "Bridge conditions T10: flyer flight recorded as STATE"
    assert N.plain("`a` " + "word " * 60).endswith("…") and len(N.plain("word " * 60)) <= 84
    assert N.plain("") == "(no title on the ledger)"
    g_ = N.alike([{"title": "Plain-English rewrite of skills/one"}, {"title": "Other"}, {"title": "Plain-English rewrite of skills/two"}])
    assert [(t, n) for t, n, _ in g_] == [("Plain-English rewrite of skills/one", 2), ("Other", 1)], g_


def t_page_four_answers_differ():
    need()
    blind = N.panel(N.safe_section(N.off_stores("live reads off (--no-live)"), NOW))
    failed = N.panel(N.safe_section({"items": 5, "causes": {}}, NOW))
    norec = stores()
    norec["records"] = None
    norec["causes"] = {"the run records": "run records: OSError: gone"}
    nr = N.panel(sec(norec))
    quiet = stores()
    quiet["records"] = []
    quiet["red_reading"]["items"] = {}
    quiet["lane"]["items"].pop("RIMMANDRAKE_LANE_STOPPED")
    q = N.panel(sec(quiet))
    assert "COULD NOT LOOK" in blind and "live reads off" in blind and "<svg" not in blind, blind
    assert "FAILED" in failed and "<svg" not in failed, failed
    assert "The run records could not be read." in nr and "Nothing: no run is live" not in nr and "UNMEASURED" in nr, nr[:400]
    assert "Could not look: the run records" in nr
    assert "Nothing: no run is live on a ticket" in q and "Nothing is stuck." in q and "UNMEASURED" not in q
    assert len({blind, failed, nr, q}) == 4


def t_needs_short_and_his_first():
    need()
    co = ["FlowWorks: Stage 6 has run 25 times", "Pyrelands: Stage 6 has run 45 times",
          "Dispatch step, 2026-11-23 1:00 PM PST: FlowWorks Stage 6 (In-game) DIVERGING, open rising: open 15 -> 13",
          "Dispatch step, 2026-11-23 1:00 PM PST: FlowWorks: the ceiling, ≈19.8M weighted tokens spent at In-game "
          "acceptance (Stage 6) plus the next run's cap; release it: python3 x.py",
          "run rm-x ended success; item X_Y is still doing: close it", "Pyrelands: a run has been live 2.4 h (Stage 3, since 10)"]
    short = M.conductor_short(co, [{"name": "FlowWorks", "label": "FlowWorks"}])
    assert len(short) == 5, short
    assert "Repeating a stage: FlowWorks Stage 6 (25 times), Pyrelands Stage 6 (45 times)" in short, short
    assert "Not converging, decide what changes: FlowWorks Stage 6" in short, short
    assert not any("python3" in x or "weighted" in x or "rm-x" in x for x in short), short
    view = {"his": [{"item": "X_LOOK", "q": "Look at the drawbridges in game (save A): do they work? 10 minutes"}],
            "ours": [], "home": {"no_home": None, "by_source": {}, "unmeasured": []}}
    p = M.needs_panel(page_dict(view=view, needs={"mandrake": [], "conductor": co, "journal": [], "pipeline": []}))
    assert "\n" not in p and "Needs Mandrake (1)" in p and "Needs the Conductor (5)" in p, p[:300]
    assert p.find("Needs Mandrake") < p.find("Needs the Conductor")
    assert "look in game · 10 min" in p and "needs not filed anywhere: UNMEASURED" in p, p
    none = M.needs_panel(page_dict(view=dict(view, his=[])))
    assert "Nothing waits on you." in none
    blind = M.needs_panel(page_dict(errors=["ledger: OSError: gone"]))
    assert "Needs Mandrake (UNMEASURED)" in blind and "Nothing waits on you." not in blind, blind


def t_trend_on_the_page():
    need()
    import maturation_trend as T
    (md, page), _ = built(page_dict(trend={"state": "blind", "cause": "the ledger was not read"}))
    for x in (md, page):
        assert T.TITLE in x and "COULD NOT LOOK" in x, "no graph of tickets by hour on the page"


def t_plain_waits():
    need()
    assert M.plain_wait("waiting: rm-detached-x-1 is live on it (in-game visit 5)") == "a run is on it now (in-game visit 5)"
    assert M.plain_wait('held: HELD BY OWNER 2026-11-16: "And stop" (lift: python3 x)') == "your hold, since Nov 16"
    assert M.plain_wait("off: OFF by pipe (act ct_1 at 2026-11-20 12:00:12 PM PST): admitted; waits (on: pipe on X --why)") == \
        "switched off since Nov 20: admitted; waits"
    assert "python3" not in M.plain_wait("ceiling: ≈19.8M weighted tokens spent at In-game acceptance (Stage 6) plus the next "
                                         "run's cap; release it: python3 x.py")
    assert M.plain_wait("something new") == "something new"


def t_same_inputs_same_section():
    need()
    a = N.markdown(N.section(stores(), NOW, spend=spend))
    b = N.markdown(N.section(copy.deepcopy(stores()), NOW, spend=spend))
    assert a == b
    assert N.panel(N.section(stores(), NOW, spend=spend)) == N.panel(N.section(copy.deepcopy(stores()), NOW, spend=spend))
    assert N.html_block(N.section(stores(), NOW, spend=spend)) == N.html_block(N.section(stores(), NOW, spend=spend))


def steve_view(at=None):
    return {"schema": "augur.remote_host/1", "host": "SteveDesktop", "written_at": NOW - 60 if at is None else at,
            "machine": {"load1": 4.2, "ncpu": 18},
            "games": {"rows": [{"name": "Steve1", "up": True, "driver_state": "FREE"},
                               {"name": "Steve2", "up": True, "driver_state": "HELD", "driver": "BENCH",
                                "for": "a proof job"}]},
            "claude_runs": {"rows": [{"unit": "rm-detached-bench-steve-thing-1.service", "item": "RIMMANDRAKE_STEVE_THING"},
                                     {"unit": "rm-detached-bench-x-1-return.service", "item": None}]},
            "jobs": {"running": [{"id": "J1", "mod": "pipeline"}], "running_why": None, "queued": [], "queued_why": None}}


def machine_stores(**kw):
    s = stores()
    s["records"] = s["records"] + [rec("u-lane-here", "RIMMANDRAKE_LANE_READY", NOW - 600, status="running",
                                       next_act_owner="list_dispatch"),
                                   rec("u-mod-bundle", "RIMMANDRAKE_FIX_FLOWWORKS_PUMP", NOW - 600, status="running",
                                       env={"RM_WORK_BUNDLE": "WB-mod-FlowWorks-1"})]
    s["lane"] = dict(s["lane"], machines={
        "Archmagi": {"live": 1, "max_live": 2, "load": 6.6, "load_line": 28, "machine_line": 28},
        "SteveDesktop": {"live": 1, "max_live": 6, "left": 70.0, "min_left_pct": 5, "pool_more": None,
                         "pool_why": "the pool holds no clone"}})
    s["steve"] = steve_view()
    s["feed_off"] = "the visit feed is stopped by fill.stop"
    s.update(kw)
    return s


def t_each_machine_shows_its_runs_room_games_and_lane():
    """RIMMANDRAKE_SEND_PIPELINE_TICKETS_TO_STEVEDESKTOP_FIRST_IT_SAT_IDLE: the owner, 2026-11-25 10:52 PM PST, "I also
    don't see SteveDesktop on MATURATION_NOW.md. It used to be shown there I believe... the Workshop Pipeline"."""
    x = sec(machine_stores())
    ms = {m["name"]: m for m in x.get("machines") or []}
    assert set(ms) == {"Archmagi", "SteveDesktop"}, "no block per machine: %s" % list(ms)
    page = N.panel(x)
    detail = "\n".join(N.markdown(x))
    for t in (page, detail):
        for w in ("Archmagi", "SteveDesktop", "Steve1", "Steve2", "test lane", "RIMMANDRAKE_STEVE_THING",
                  "RIMMANDRAKE_LANE_READY", "fill.stop"):
            assert w in t, "%s is not in the machine block" % w
        assert "$" not in t.split("Workshop Pipeline: all work")[-1] and "token" not in " ".join(
            ms["SteveDesktop"]["lines"] + ms["Archmagi"]["lines"]).lower(), "a spend or token figure in the block"
    a, sd = " ".join(ms["Archmagi"]["lines"]), " ".join(ms["SteveDesktop"]["lines"])
    assert "1 of 2" in a and "1 of 6" in sd and "70" in sd, (a, sd)
    assert "-return" not in sd, "a bookkeeping unit is not a run"
    assert "FLOWWORKS_PUMP" not in a and "WB-mod-" not in a, "a mod's bundle run is not a Workshop run: %s" % a
    (md, pg), _ = built(page_dict(machine_stores()))
    for t in (md, pg):
        assert "SteveDesktop" in t and "Steve2" in t, "the machine block is not on MATURATION_NOW"
        hit = [w for w in LOG_WORDS if w in t]
        assert not hit, "log lines on the summary page: %s" % hit


def t_an_unreadable_machine_reads_could_not_look():
    for what, s in (("no SteveDesktop reading", machine_stores(steve=None, causes={"SteveDesktop's reading": "gone"})),
                    ("an old SteveDesktop reading", machine_stores(steve=steve_view(at=NOW - 4000))),
                    ("no room reading", machine_stores(lane={"at": NOW - 120, "items": {}}))):
        m = {b["name"]: b for b in sec(s)["machines"]}["SteveDesktop"]
        blind = [x.lower() for x in m["lines"] if "could not look" in x]
        want = 1 if what == "no room reading" else 3      # the room line, or the three lines its reading feeds
        assert len(blind) >= want, "%s: %s" % (what, m["lines"])
        assert not any(w in x for x in blind for w in (" 0 ", "idle", "none live", "0 live", "0 of", "0 running")), \
            "%s reads as idle: %s" % (what, blind)
    m = {b["name"]: b for b in sec(machine_stores(records=None))["machines"]}["Archmagi"]
    assert "could not look" in " ".join(m["lines"]).lower(), m


def main():
    tests = [t_mod_or_not_by_one_rule, t_stages_from_one_rule, t_launcher_from_records, t_doing_now_rows,
             t_next_names_its_wait, t_closed_last_day, t_open_by_reason_oldest_first, t_escalated_from_run_ends,
             t_ready_for_review, t_cannot_see_is_unmeasured, t_four_answers_differ, t_lists_go_to_detail,
             t_page_is_a_picture_not_a_log, t_a_question_for_the_conductor_is_its_own_block, t_waits_in_plain_words, t_plain_titles, t_page_four_answers_differ,
             t_needs_short_and_his_first, t_trend_on_the_page, t_plain_waits, t_same_inputs_same_section,
             t_each_machine_shows_its_runs_room_games_and_lane, t_an_unreadable_machine_reads_could_not_look]
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
