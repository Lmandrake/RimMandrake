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

    print(f"\n{'FAILED ' + str(len(FAILS)) if FAILS else 'ALL PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
