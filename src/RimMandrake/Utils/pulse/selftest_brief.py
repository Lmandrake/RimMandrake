#!/usr/bin/env python3
"""Selftest for the morning brief's second-agent judge (RIMPULSE_BRIEF_BUILD_MORNING_PAPER_PHONE).

Sanity probe for the instrument: a judge that passes everything is worthless, so every claim type is
checked BOTH ways on fixture events - a true claim passes and a tampered one is withheld. Also checks
that compose only puts owner-needs items on the page and that the heartbeat goes red on a stale monitor.
Fixture events only; touches no live state.
"""
import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_selftest_brief_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
os.environ["RM_PULSE_STATE"] = tempfile.mkdtemp(prefix="brief_state_")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brief  # noqa: E402

FAILS = []
NOW = 1_792_900_000.0


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


def ev(n, event, iid, **kw):
    t = NOW - 3600 + n * 60
    import time as _t
    return {"seat": "BENCH", "event": event, "id": iid, "ts": _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime(t)),
            "tsn": int(t * 1e9), **kw}


EVENTS = [
    ev(0, "file", "ASK_OPEN_ITEM", title="Owner must pick a colour", kind="task", target="v1", needs="owner", **{"for": "BENCH"}),
    ev(1, "file", "ASK_CLOSED_ITEM", title="Owner question already answered", kind="task", target="v1", needs="owner", **{"for": "BENCH"}),
    ev(2, "close", "ASK_CLOSED_ITEM", sha="abc1234", reason="answered"),
    ev(3, "file", "AGENT_WORK_ITEM", title="Agent work", kind="task", target="v1", needs="offline", **{"for": "BENCH"}),
    ev(4, "close", "AGENT_WORK_ITEM", sha="abc1235", reason="built and tested"),
    ev(5, "note", "AGENT_WORK_ITEM", text="delegated call", why="delegated: design default"),
]
CLOSE_TSN = EVENTS[4]["tsn"]


def line(claim):
    return {"text": "x", "claim": claim}


def main():
    snap = {"rows": [{"key": "card:1", "agent": False}, {"key": "agentrow", "agent": True}],
            "sources": {"tokens": {"ok": True}, "dead": {"ok": False}}}
    cases = [
        ("ask open owner item passes", {"type": "ask", "id": "ASK_OPEN_ITEM"}, True),
        ("ask on a closed item is withheld", {"type": "ask", "id": "ASK_CLOSED_ITEM"}, False),
        ("ask on a non-owner item is withheld", {"type": "ask", "id": "AGENT_WORK_ITEM"}, False),
        ("ask on an invented id is withheld", {"type": "ask", "id": "NO_SUCH_ITEM"}, False),
        ("card still on the monitor passes", {"type": "card", "key": "card:1"}, True),
        ("card gone from the monitor is withheld", {"type": "card", "key": "card:2"}, False),
        ("card that is an agent row is withheld", {"type": "look", "key": "agentrow"}, False),
        ("moved with the real close event passes", {"type": "moved", "id": "AGENT_WORK_ITEM", "to": "done", "tsn": CLOSE_TSN}, True),
        ("moved with a wrong tsn is withheld", {"type": "moved", "id": "AGENT_WORK_ITEM", "to": "done", "tsn": CLOSE_TSN + 1}, False),
        ("moved naming the wrong item is withheld", {"type": "moved", "id": "ASK_OPEN_ITEM", "to": "done", "tsn": CLOSE_TSN}, False),
        ("moved with a wrong state is withheld", {"type": "moved", "id": "AGENT_WORK_ITEM", "to": "validated", "tsn": CLOSE_TSN}, False),
        ("moved_many with one bad member is withheld", {"type": "moved_many", "items": [
            {"id": "AGENT_WORK_ITEM", "to": "done", "tsn": CLOSE_TSN}, {"id": "X", "to": "done", "tsn": 1}]}, False),
        ("delegated with real events passes", {"type": "delegated", "tsns": [EVENTS[5]["tsn"]]}, True),
        ("delegated with a non-delegated event is withheld", {"type": "delegated", "tsns": [EVENTS[4]["tsn"]]}, False),
        ("measure from a live source passes", {"type": "measure", "src": "tokens"}, True),
        ("measure from a down source is withheld", {"type": "measure", "src": "dead"}, False),
        ("seat naming an open item passes", {"type": "seat", "id": "ASK_OPEN_ITEM"}, True),
        ("seat naming a closed item is withheld", {"type": "seat", "id": "AGENT_WORK_ITEM"}, False),
        ("an unknown claim type is withheld", {"type": "made_up"}, False),
    ]
    b = {"sections": {"t": [line(c) for _, c, _ in cases]}}
    brief.judge(b, EVENTS, snap)
    for (name, _, want), ln in zip(cases, b["sections"]["t"]):
        check(name, (ln["check"] == "pass") == want, ln["check"])
    check("withheld count matches the failing lines", b["withheld"] == sum(1 for *_, w in cases if not w), b["withheld"])

    # compose: a live card with no item id reads as its own text (no dangling "<title>: " prefix)
    csnap = {"collected_at": NOW, "rows": [{"kind": "amber", "key": "card:9", "text": "BENCH asks: pick one", "since": NOW}],
             "chips": [], "sources": {k: {"ok": True} for k in ("ledger", "hands", "sheets", "tokens", "sessions")}}
    cb = brief.compose(csnap, EVENTS, NOW - 7200, NOW)
    w = cb["sections"]["word"]
    check("a card line has no dangling prefix", len(w) == 1 and w[0]["text"] == "BENCH asks: pick one", w)

    # look packets (owner card 2026-10-25): all four parts or "packet incomplete", and the judge re-reads it
    full = Path(tempfile.mkdtemp()) / "full.md"
    full.write_text("# x\n## Recommendation\nkeep A\n## Alternatives\nB: slower\n## Evidence\nmeasured 3 runs\n"
                    "## Doubts\nnot measured on the full list\n")
    part = full.with_name("part.md")
    part.write_text("## Recommendation\nkeep A\n## Evidence\nmeasured\n## Doubts\n\n")
    check("a full packet has nothing missing", brief.read_packet(str(full))[1] == [], brief.read_packet(str(full)))
    check("an empty heading does not count", brief.read_packet(str(part))[1] == ["alternatives", "doubts"],
          brief.read_packet(str(part)))
    check("no packet misses all four", brief.read_packet(None)[1] == list(brief.PACKET_PARTS))
    lsnap = {**csnap, "rows": [{"kind": "look", "key": "hand:a", "title": "Sheet A", "since": NOW,
                                "packet": str(full), "link": {"value": "http://x/a"}},
                               {"kind": "look", "key": "hand:b", "title": "Sheet B", "since": NOW,
                                "packet": str(part), "link": {"value": "http://x/b"}}]}
    lb = brief.compose(lsnap, EVENTS, NOW - 7200, NOW)
    o = {ln["claim"]["key"]: ln for ln in lb["sections"]["open"]}
    check("a complete look keeps its link", o["hand:a"]["link"] == "http://x/a" and not o["hand:a"]["missing"], o["hand:a"])
    check("an incomplete look has no bare link", o["hand:b"]["link"] is None and o["hand:b"]["missing"], o["hand:b"])
    o["hand:b"]["claim"]["missing"] = []          # tamper: the line claims a complete packet
    brief.judge(lb, EVENTS, lsnap)
    check("judge passes the true look line", o["hand:a"]["check"] == "pass", o["hand:a"]["check"])
    check("judge withholds a look claiming a packet it lacks", o["hand:b"]["check"] != "pass", o["hand:b"]["check"])
    html_ = brief.render(lb, {"red": False, "text": "x"}, NOW)
    check("render shows the four parts of a full packet", all(f"<b>{k}</b>" in html_ for k in brief.PACKET_PARTS))

    # heartbeat: a stale snapshot is red, a fresh one with a fresh brief is not
    fresh = {"collected_at": NOW, "rows": [], "chips": [{"seat": "BENCH", "state": "run", "since": NOW - 60}], "sources": {}}
    good_brief = {"at": NOW - 600, "judged": True, "sections": {}}
    hb = brief.heartbeat(fresh, good_brief, NOW)
    check("heartbeat calm on a fresh snapshot + brief", not hb["red"], hb)
    hb = brief.heartbeat({**fresh, "collected_at": NOW - 3600}, good_brief, NOW)
    check("heartbeat red when the monitor is stale", hb["red"], hb)
    hb = brief.heartbeat(fresh, {**good_brief, "at": NOW - 20 * 3600}, NOW)
    check("heartbeat red when the brief is missed", hb["red"] and hb["why"] == "brief", hb)
    hb = brief.heartbeat({**fresh, "rows": [{"kind": "amber", "text": "card", "key": "c"}]}, good_brief, NOW)
    check("heartbeat red when an amber card blocks a seat", hb["red"] and hb["why"] == "card", hb)
    hb = brief.heartbeat(None, good_brief, NOW)
    check("heartbeat red with no snapshot at all", hb["red"], hb)

    # RIMPULSE_PAGE_FIX_CHORES_POSE_AS_RULINGS: goals are packages/areas, never a title's first word
    pk = {"rimbiomes": "RimBiomes"}
    check("goal from a src mod path", brief.goal_of("WIDGET_FIX_X", None, "src/RimMandrake/RimBiomes/Defs/a.xml", pk) == "RimBiomes",
          brief.goal_of("WIDGET_FIX_X", None, "src/RimMandrake/RimBiomes/Defs/a.xml", pk))
    check("no first-word goal: a bare slug has no package", brief.goal_of("WIDGET_FIX_X", None, "", pk) == "No package recorded",
          brief.goal_of("WIDGET_FIX_X", None, "", pk))
    check("a tool slug word names its area", brief.goal_of("RIMPULSE_PAGE_FIX_X", None, "", pk) == "RimPulse",
          brief.goal_of("RIMPULSE_PAGE_FIX_X", None, "", pk))
    oe = [ev(10, "close", "AGENT_WORK_ITEM", sha="abc", reason="hose stays linked when raised")]
    check("outcome comes from the close note", brief.outcome_of("AGENT_WORK_ITEM", oe, NOW - 7200, NOW + 3600)
          == "hose stays linked when raised", brief.outcome_of("AGENT_WORK_ITEM", oe, NOW - 7200, NOW + 3600))
    # labels and chores: the plain question on the word line, the machine job in "When you're home"
    hsnap = {**csnap, "rows": [
        {"kind": "review", "key": "needs:ASK_OPEN_ITEM", "label": "Colour: which colour?", "since": NOW},
        {"kind": "chore", "key": "needs:CHORE_ITEM", "label": "Enable virtualisation in the BIOS", "machine": "SteveDesktop",
         "minutes": 10, "since": NOW - 30 * 86400}],
        "chips": [{"seat": "BENCH", "state": "idle", "agents": 2, "title": ""},
                  {"seat": "FOUNDRY", "state": "idle", "agents": 0, "title": ""}]}
    hb_ = brief.compose(hsnap, EVENTS, NOW - 7200, NOW)
    wl = hb_["sections"]["word"]
    check("a word line shows the plain question, the slug in id", len(wl) == 1 and wl[0]["text"] == "Colour: which colour?"
          and wl[0]["id"] == "ASK_OPEN_ITEM", wl)
    hl = hb_["sections"]["home"]
    check("a chore goes to When you're home, not Needs your word", len(hl) == 1 and hl[0]["text"].startswith("SteveDesktop: Enable")
          and hl[0]["meta"]["minutes"] == 10, hl)
    nx = {ln["text"] for ln in hb_["sections"]["next"]}
    check("an idle seat with helpers is not 'idle'", "Bench: 2 helpers working" in nx and "Foundry: idle" in nx, nx)
    tamper = {"seat": "BENCH", "state": "idle", "agents": 0, "id": None, "type": "seat"}
    jb = {"sections": {"t": [line(tamper)]}}
    brief.judge(jb, EVENTS, hsnap)
    check("judge withholds a seat line whose helper count the chip denies", jb["sections"]["t"][0]["check"] != "pass",
          jb["sections"]["t"][0]["check"])
    rh = brief.render({**hb_, "sections": {k: [{**ln, "check": "pass"} for ln in v] for k, v in hb_["sections"].items()},
                       "withheld": 0}, {"red": False, "text": "x"}, NOW)
    check("render titles the home list with its total time", "When you&#x27;re home (1 · ~10 min)" in rh, rh[:0])

    # CLAUDE_PLAN_USAGE_MEASURE_A_SOURCE: spend lines come from the monitor's measured usage panel
    up = {"at": NOW, "evening_share": 0.4, "codex": None, "accounts": [
        {"name": "own_a", "role": "owned", "cap": None, "state": "measured", "pct": 40.0, "resets_at": NOW + 2 * 86400,
         "five_pct": 1.0, "measured_at": NOW - 60, "why": ""}]}
    usnap = {**csnap, "charts": {"usage": up}}
    ub = brief.compose(usnap, EVENTS, NOW - 7200, NOW)
    sp = [ln for ln in ub["sections"]["spend"] if (ln.get("claim") or {}).get("type") == "usage"]
    check("a measured account becomes a spend line", len(sp) == 1 and sp[0]["text"].startswith("own_a: 40% of the week used"), sp)
    nob = brief.compose(csnap, EVENTS, NOW - 7200, NOW)
    check("no usage panel reads unknown", any("unknown" in ln["text"] and ln["claim"]["type"] == "unknown"
                                                for ln in nob["sections"]["spend"]), nob["sections"]["spend"])
    sp[0]["claim"]["pct"] = 41.0                    # tamper
    brief.judge(ub, EVENTS, {**usnap, "sources": {**usnap["sources"], "tokens": {"ok": True}}})
    check("judge withholds a usage line the panel does not hold", sp[0]["check"] != "pass", sp[0]["check"])

    # MORNING_PAPER follow-up (owner 2026-10-25): "new" = since he last opened the paper, per device
    check("no opens at all: new is since the previous paper", brief.since_basis({"at": NOW - 3600}, {}, NOW)
          == (NOW - 3600, {"kind": "previous"}))
    r1 = brief.record_open("phone", NOW - 50000, NOW - 40000)
    check("a first open on a device has nothing to compare", r1["before"] is None and r1["visits"] == 1, r1)
    r2 = brief.record_open("phone", NOW - 50000, NOW - 40000 + 120)       # its own 2-minute reload
    check("a reload inside one visit is not a new visit", r2["visits"] == 1 and r2["before"] is None, r2)
    brief.record_open("tablet", NOW - 90000, NOW - 80000)
    sb, basis = brief.since_basis({"at": NOW - 3600}, brief.read_opens(), NOW)
    check("new is since the newest paper he opened on any device", sb == NOW - 50000 and basis["device"] == "phone"
          and basis["kind"] == "opened", (sb, basis))
    check("an unopened later paper does not move it", brief.since_basis({"at": NOW - 100}, brief.read_opens(), NOW)[0]
          == NOW - 50000)
    r3 = brief.record_open("phone", NOW - 600, NOW)
    check("a later visit marks what it saw last time", r3["before"] == NOW - 50000 and r3["visits"] == 2, r3)
    vb = {"at": NOW - 600, "since": sb, "since_basis": basis, "judged": True, "withheld": 0, "notes": {},
          "sections": {"word": [{"text": "old ask", "meta": {"since": NOW - 60000}, "check": "pass", "claim": {}},
                                {"text": "fresh ask", "meta": {"since": NOW - 1000}, "check": "pass", "claim": {}}]}}
    vh = brief.render(vb, {"red": False, "text": "x"}, NOW, visit=r3)
    check("only what this device has not seen is marked new", "fresh ask <span class=new>new</span>" in vh
          and "old ask <span class=new>" not in vh, vh[vh.find("old ask") - 40: vh.find("old ask") + 200])
    check("the page says new since the paper he last opened", "the paper you last opened (phone," in vh)
    folder = Path(tempfile.mkdtemp())
    o0 = brief.read_opens()
    brief.page("/brief", lambda: {}, folder)                          # loopback / agent fetch: no device
    # the whole record, not just phone's: an open filed under any other key would also be wrong
    check("a fetch with no device of his is not an open", brief.read_opens() == o0, brief.read_opens())

    # RIMPULSE_PLAN_BUILD_ON_TRACK_WHILE_AWAY: the trip plan, on track or not, from the ledger (fixture plan)
    pev = EVENTS + [ev(10, "file", "PLAN_BLOCKED_ITEM", title="Stuck on a part", kind="task", target="v1", **{"for": "BENCH"}),
                    ev(11, "block", "PLAN_BLOCKED_ITEM", reason="waits for a part"),
                    ev(12, "file", "PLAN_DROPPED_ITEM", title="Not happening", kind="task", target="v1", **{"for": "BENCH"}),
                    ev(13, "drop", "PLAN_DROPPED_ITEM", reason="no longer wanted")]
    world = brief._model().replay(pev)
    plan = {"by": "BENCH", "at": NOW - 3600, "until": NOW + 3 * 3600, "items": ["AGENT_WORK_ITEM", "ASK_OPEN_ITEM"],
            "first_need": {"text": "pick the colour", "id": "ASK_OPEN_ITEM"}, "fallback": "ship grey", "edits": []}
    st = brief.plan_states(plan, world)
    check("plan states come from the ledger", st == {"AGENT_WORK_ITEM": "done", "ASK_OPEN_ITEM": "proposed"}
          or (st["AGENT_WORK_ITEM"] == "done" and st["ASK_OPEN_ITEM"] not in brief.DONE_STATES), st)
    ok, words = brief.plan_verdict(plan, st, NOW)
    check("1 of 2 done a quarter in is on track", ok and words.startswith("on track: 1 of 2 done"), words)
    ok, words = brief.plan_verdict({**plan, "at": NOW - 3 * 3600, "until": NOW + 60}, {"A": "doing", "B": "doing", "C": "done"}, NOW)
    check("1 of 3 done near the end is behind", not ok and words.startswith("behind: 1 of 3 done"), words)
    ok, words = brief.plan_verdict(plan, brief.plan_states({**plan, "items": ["AGENT_WORK_ITEM", "PLAN_BLOCKED_ITEM"]}, world), NOW)
    check("a blocked plan item is not on track", not ok and "PLAN_BLOCKED_ITEM is blocked" in words, words)
    ok, words = brief.plan_verdict(plan, brief.plan_states({**plan, "items": ["PLAN_DROPPED_ITEM", "NO_SUCH_ITEM"]}, world), NOW)
    check("a dropped or vanished item is not on track", not ok and "were dropped or replaced" in words, words)
    ok, words = brief.plan_verdict({**plan, "until": NOW - 60}, st, NOW)
    check("past the return with work open is missed", not ok and words.startswith("missed: 1 of 2") and "ASK_OPEN_ITEM" in words, words)
    ok, words = brief.plan_verdict(plan, {"AGENT_WORK_ITEM": "done", "X": "validated"}, NOW)
    check("all done or checked is done", ok and words.startswith("done: all 2"), words)

    pb = brief.compose(csnap, pev, NOW - 7200, NOW, plan={**plan, "edits": [
        {"at": NOW - 600, "by": "BENCH", "owner_said": "skip the colour, do it after", "change": "-ASK_OPEN_ITEM"}]})
    aw = pb["sections"]["away"]
    tx = [ln["text"] for ln in aw]
    check("the paper leads with the plan when there is one", brief.ORDER[0] == "away" and aw[0].get("head")
          and aw[0]["text"].startswith("on track"), aw[:1])
    check("the plan shows first need, fallback and his change", any(t.startswith("First thing that will need you: pick the colour") for t in tx)
          and "If it goes wrong: ship grey" in tx and any(t.startswith("Changed by you") and "skip the colour" in t for t in tx), tx)
    check("no plan, no section, a note", "away" not in [k for k, v in cb["sections"].items() if v] and cb["notes"].get("away") == "no trip plan",
          cb.get("notes"))
    brief.judge(pb, pev, csnap)
    check("judge passes the true plan lines", all(ln["check"] == "pass" for ln in aw), [ln["check"] for ln in aw])
    tb = brief.compose(csnap, pev, NOW - 7200, NOW, plan=plan)
    tb["sections"]["away"][0]["claim"]["on_track"] = False                    # tamper: the verdict
    tb["sections"]["away"][1]["claim"]["states"] = {"AGENT_WORK_ITEM": "doing"}  # tamper: a state
    brief.judge(tb, pev, csnap)
    check("judge withholds a forged verdict and a forged state",
          [ln["check"] != "pass" for ln in tb["sections"]["away"][:2]] == [True, True], [ln["check"] for ln in tb["sections"]["away"][:2]])
    ph = brief.render(pb, {"red": False, "text": "x"}, NOW)
    check("render shows By your return", "By your return" in ph and "ship grey" in ph)
    check("no plan, no heading on the page", "By your return" not in brief.render(cb, {"red": False, "text": "x"}, NOW))

    # the CLI an agent uses: set, edit with his words, show, clear; ids checked against the ledger
    import contextlib
    import io
    pf = Path(tempfile.mkdtemp()) / "away_plan.json"
    import time as _t
    ret = _t.strftime("%Y-%m-%d %H:%M", _t.localtime(_t.time() + 2 * 86400))
    with contextlib.redirect_stdout(io.StringIO()):
        rc = brief.plan_cli(["set", "--by", "BENCH", "--until", ret, "--item", "AGENT_WORK_ITEM", "--item", "ASK_OPEN_ITEM",
                             "--first-need", "pick the colour", "--first-need-id", "ASK_OPEN_ITEM", "--fallback", "ship grey"], pf, pev)
    got = brief.read_plan(pf)
    check("plan set writes the file", rc == 0 and got["items"] == ["AGENT_WORK_ITEM", "ASK_OPEN_ITEM"] and got["fallback"] == "ship grey", got)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            brief.plan_cli(["set", "--by", "BENCH", "--until", ret, "--item", "INVENTED_ID", "--first-need", "x", "--fallback", "y"], pf, pev)
        refused = False
    except SystemExit as e:
        refused = "INVENTED_ID" in str(e)
    check("plan set refuses an id the ledger lacks", refused and brief.read_plan(pf)["items"] == got["items"])
    with contextlib.redirect_stdout(io.StringIO()):
        brief.plan_cli(["edit", "--by", "BENCH", "--owner-said", "drop the colour", "--drop", "ASK_OPEN_ITEM"], pf, pev)
    got = brief.read_plan(pf)
    check("plan edit records his words and the change", got["items"] == ["AGENT_WORK_ITEM"]
          and got["edits"][-1]["owner_said"] == "drop the colour" and got["edits"][-1]["change"] == "-ASK_OPEN_ITEM", got)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        brief.plan_cli(["show"], pf, pev)
    check("plan show prints the verdict", "done: all 1" in out.getvalue(), out.getvalue())
    with contextlib.redirect_stdout(io.StringIO()):
        brief.plan_cli(["clear"], pf, pev)
    check("plan clear ends the trip", brief.read_plan(pf) is None)

    # widget: a look row's packet_view comes from the same reader as the phone brief, and index.html draws it
    full = Path(tempfile.mkdtemp(prefix="pv_")) / "full.md"
    full.write_text("## Recommendation\nship it\n## Alternatives\nwait\n## Evidence\nshot.png\n## Doubts\nlight\n")
    part = Path(full.parent) / "part.md"
    part.write_text("## Recommendation\nship it\n")
    pv = brief.packet_view({"packet": str(full), "key": "hand:x"})
    check("widget packet_view: complete packet has four parts and nothing missing",
          pv["missing"] == [] and pv["parts"].get("doubts") == "light", pv)
    pv = brief.packet_view({"packet": str(part), "key": "hand:y"})
    check("widget packet_view: short packet names what is missing",
          pv["missing"] == ["alternatives", "evidence", "doubts"], pv)
    pv = brief.packet_view({"key": "hand:z"})
    check("widget packet_view: no packet source reads incomplete in full", len(pv["missing"]) == 4, pv)
    html = (Path(__file__).resolve().parent / "widget" / "index.html").read_text(encoding="utf-8")
    check("widget draws packet_view and the incomplete wording", "packetHTML(r)" in html and "packet incomplete: no" in html)
    psrc = (Path(__file__).resolve().parent / "pulse.py").read_text(encoding="utf-8")
    check("snapshot attaches packet_view to look rows via brief.packet_view", "brief.packet_view(r)" in psrc)

    print(f"\n{'FAILED ' + str(len(FAILS)) if FAILS else 'ALL PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
