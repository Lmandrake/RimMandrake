#!/usr/bin/env python3
"""selftest_status_board.py - the owner's status board (STATUS_PAGES_BUILD_REPLACE_RIMPULSE), offline.

His card of 2026-11-03, one check per clause: every STUCK line says what is planned and who it waits on
(fleet_mods.stuck_of); "Needs you (N)" matches every needs-you tag below it (the tag comes only from
owner_queue.is_his); no cryptic lines (no hold-class slug, no bare item id in the visible text); the dark 70s-brown
look (no light background anywhere); phone-readable (viewport meta, a narrow-screen rule, a scrolling table); trends
carry finished, errors handled / to a person and live-test yield, and a day before the journal reads "no record",
never 0. The last block builds the board from the live cache and store when they exist (read-only, writes nothing).
"""
import json
import os
import re
import sys
import tempfile
import time
import types
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fleet_mods as M  # noqa: E402
import status_board as B  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def item(iid, **kw):
    d = dict(id=iid, title=iid.replace("_", " ").lower(), open=True, needs=None, blocked=False, blocked_kind=None,
             blocked_on=None, blocked_reason=None, blocked_until=None, held=False, history=[], state="ready")
    d.update(kw)
    return types.SimpleNamespace(**d)


# ---- stuck_of: who it waits on and what is planned, for every way an item can stand still
known = {"A_ONE": item("A_ONE", title="Build the first thing"), "B_TWO": item("B_TWO")}
cases = {
    "owner": (item("X", needs="owner"), {}, "you"),
    "proof_weak hold": (item("X"), {"status": "held", "hold": {"kind": "proof_weak", "why": "w"}}, "the Conductor"),
    "strikes hold": (item("X"), {"status": "held", "hold": {"kind": "strikes", "why": "w"}}, "the Conductor"),
    "unknown hold": (item("X"), {"status": "held", "hold": {"kind": "zzz", "why": "w"}}, "the Conductor"),
    "game hold": (item("X"), {"status": "held", "hold": {"kind": "game", "why": "w"}}, "the game"),
    "blocked on item": (item("X", blocked=True, blocked_kind="item", blocked_on="A_ONE"), {}, "another item"),
    "blocked live": (item("X", blocked=True, blocked_kind="live"), {}, "the game"),
    "blocked judge": (item("X", blocked=True, blocked_kind="judge"), {}, "a judge agent"),
    "blocked time": (item("X", blocked=True, blocked_kind="time", blocked_until="2026-11-09T00:00:00Z"), {}, "time"),
    "blocked external": (item("X", blocked=True, blocked_kind="external", blocked_reason="vendor fix"), {},
                         "something outside the project"),
    "blocked, no reason": (item("X", blocked=True), {}, "the Conductor"),
    "held FAIL": (item("X", held=True), {}, "a fix"),
    "relentless game": (item("X"), {"status": "game"}, "the game"),
    "relentless retired": (item("X"), {"status": "retired"}, "the Conductor"),
    "relentless blocked": (item("X"), {"status": "blocked"}, "another item"),
}
for name, (it, rs, who) in cases.items():
    s = M.stuck_of(it, rs, [], known, {})
    check("stuck_of %s -> waits on %s" % (name, who), bool(s) and s["waits"] == who)
    check("stuck_of %s has a plan sentence" % name, bool(s) and len(s.get("plan", "").split()) >= 4)
check("stuck_of names the blocking item by title",
      "Build the first thing" in M.stuck_of(cases["blocked on item"][0], {}, [], known, {})["plan"])
check("stuck_of: a moving item is not stuck", M.stuck_of(item("X"), {"status": "running"}, [], known, {}) is None)
check("stuck_of: a closed item is not stuck", M.stuck_of(item("X", open=False, needs="owner"), {}, [], known, {}) is None)
for reason in ("PARKED by owner card", "deferred until after the world remake (question card)", "owner ruling: stop"):
    s = M.stuck_of(item("X", blocked=True, blocked_reason=reason), {}, [], known, {})
    check("free-text block naming the owner is never 'you' (%s)" % reason[:20], s["waits"] != "you")
check("plain_reason: snag prefix gone, known id -> title, unknown id -> words, slug -> words, file kept",
      M.plain_reason("relentless snag blocked_by_predecessor: wait for XB_ONE_XY and ZZ_TOP_ONE; see foo_bar.py",
                     {"XB_ONE_XY": item("XB_ONE_XY", title="Build the first thing")}) ==
      "wait for 'Build the first thing' and another item; see foo_bar.py")
check("plain_reason: a bare slug becomes words", M.plain_reason("tmp mount is masked_now") == "tmp mount is masked now")
check("block_who: a live wait is the game", M.block_who("needs a live quicktest pass") == "the game")
check("first_sentence cuts at a word and drops a trailing ;", M.first_sentence("needs a map type; then more") ==
      "needs a map type" and M.first_sentence("x " * 200).endswith("…"))
flyer = {"status": "held", "hold": {"kind": "game", "why": "game phase: " + M.owner_queue.relentless_game.FLYER}}
check("flyer game hold routed to him is 'you'", M.stuck_of(item("X", needs="owner"), flyer, [], known, {})["waits"] == "you")
check("flyer game hold not yet routed is stuck, but not 'you' (Needs you must match)",
      M.stuck_of(item("X"), flyer, [], known, {})["waits"] == "Relentless")


# ---- trends: tick acts only, per local day, "no record" before the journal starts
now = time.time()
iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))  # noqa: E731
j = [json.dumps({"do": "tick", "at": iso(now - 60), "acts": [{"do": "done"}, {"do": "done"}, {"do": "blind_fail"},
                                                             {"do": "held_delivered"}, {"do": "game_implemented"},
                                                             {"do": "game_fail"}, {"do": "game_unmeasured"}]}),
     json.dumps({"do": "done", "at": iso(now - 60), "item": "X"}),        # the standalone copy of a tick's act
     json.dumps({"do": "tick", "at": iso(now - 86400 - 60), "acts": [{"do": "proof_weak"}]}),
     "not json"]
tr = B.trends(j, now)
check("trends: 7 rows, today last", len(tr) == 7 and tr[-1]["day"] == B.local_day(now))
t = tr[-1]
check("trends: a standalone done line is not counted twice", t["done"] == 2)
check("trends: handled / to a person", t["handled"] == 1 and t["unhandled"] == 1)
check("trends: live yield counts answers and non-answers", t["answers"] == 2 and t["no_answer"] == 1 and t["passed"] == 1)
check("trends: days before the journal's first tick are 'no record', not zeros", all(r.get("none") for r in tr[:5]))
check("trends: yesterday is measured", not tr[-2].get("none") and tr[-2]["handled"] == 1)
check("trends: an empty journal is no record on every day", all(r.get("none") for r in B.trends([], now)))


# ---- render: a synthetic board
fleet = {"factory": {"ok": True, "running": 3, "target": 8}, "t": now, "good_t": now,
         "needs": {"lines": [{"item": "OWN_ONE", "q": "Look at the bridge: right?"},
                             {"item": "OWN_TWO", "q": "Pick a colour for the pipes?"},
                             # raw ledger text (the 2026-11-06 nightly red): ids, a Python None, a snake_case slug
                             {"item": "OWN_RAW", "q": "Ratify the sheet that gates MOD_VALIDATION_RETROFIT_1 before "
                                                      "CANONICAL_ASHKARR_START_2026-09-12 (owner_call)"}]},
         "mods": [{"id": "Bridge", "name": "Bridge Works", "closed": 2, "open": 3, "parked": 1, "tasks": [
                       {"id": "DONE_ONE", "kind": "pass", "title": "Bridges draw right"},
                       {"id": "DONE_TWO", "kind": "done", "title": "Leaves open"},
                       {"id": "OPEN_ONE", "kind": "open", "title": "Bridge sounds"},
                       {"id": "OWN_ONE", "kind": "open", "title": "bridge look"}],
                   "stuck": [M.stuck_of(item("OWN_ONE", needs="owner"), {}, [], known, {}) | {"id": "OWN_ONE",
                                                                                               "title": "Look at the bridge"},
                             M.stuck_of(item("S2"), {"status": "held", "hold": {"kind": "proof_weak"}}, [], known, {}) |
                             {"id": "S2", "title": "Bridge proof"},
                             M.stuck_of(item("S3"), {"status": "retired"}, [], known, {}) |
                             {"id": "S3", "title": "Nightly red: ledger ended it ('close', None) for "
                                                  "FLYER_TIER_ONE_REBUILD_REDO_ROWS_FIRST"}]},
                  {"id": "_infra", "name": "Infrastructure & tooling", "infra": True, "closed": 1, "open": 0,
                   "parked": 0, "tasks": [], "stuck": []}]}
d = {"now": now, "fleet": fleet, "states": B.collections.Counter(running=3, queued=20, held=2, blocked=4, checking=1),
     "trends": tr}
page = B.render(d)


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("style", "script")

    def handle_endtag(self, tag):
        self.skip -= tag in ("style", "script")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def visible(html):
    p = Text()
    p.feed(html)
    return " ".join(p.out)


def needs_count(html):
    m = re.search(r"Needs you \((\d+)\)", html)
    return int(m.group(1)) if m else None


def tag_ids(html):
    return set(re.findall(r'<li title="([^"]+)">(?:(?!</li>).)*?<span class="tag">needs you</span>', html, re.S))


def needs_ids(html):
    box = html.split('<div class="box needs">', 1)[1].split("</div>", 1)[0]
    return set(re.findall(r'<li title="([^"]+)">', box))


def stuck_lines(html):
    return re.findall(r'<div class="stuck"><h4>Stuck</h4><ul>(.*?)</ul></div>', html, re.S)


def board_checks(page, label):
    n = needs_count(page)
    check("%s: Needs you (N) equals its own list" % label, n is not None and n == len(needs_ids(page)))
    check("%s: every needs-you tag below is in Needs you" % label, tag_ids(page) <= needs_ids(page))
    lis = [x for blk in stuck_lines(page) for x in re.findall(r"<li[^>]*>(.*?)</li>", blk, re.S)]
    check("%s: every stuck line has Planned: and Waits on:" % label,
          all("Planned: " in x and re.search(r"Waits on: <span class=\"who\">[^<]+</span>", x) for x in lis))
    vis = visible(page)
    slugs = [s for s in ("proof_weak", "owner_call", "blocked_by_predecessor", "held_delivered", "game_unmeasured",
                         "may not install", "None", "UNMEASURED_") if s in vis]
    check("%s: no cryptic slug in the visible text %s" % (label, slugs), not slugs)
    ids = [x for x in re.findall(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b", vis)]
    check("%s: no bare item id in the visible text %s" % (label, ids[:3]), not ids)
    light = []
    # surfaces only: a progress-bar fill (.bar span, .tb) is a mark, not a page background
    surfaces = "".join(body for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", page)
                       if not re.search(r"\.bar span|\.tb", sel)) + "".join(re.findall(r'style="([^"]*)"', page))
    for m in re.finditer(r"background(?:-color)?:\s*(#[0-9a-fA-F]{3,6}|white|var\(--[a-z0-9]+\))", surfaces):
        v = m.group(1)
        if v.startswith("var("):
            mm = re.search(r"--%s:(#[0-9a-fA-F]{6})" % re.escape(v[6:-1]), page)
            v = mm.group(1) if mm else v
        if v == "white":
            light.append(v)
            continue
        if not v.startswith("#"):
            continue
        h = v[1:] if len(v) == 7 else "".join(c * 2 for c in v[1:])
        r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.45:
            light.append(v)
    check("%s: no light background (dark 70s-brown) %s" % (label, light), not light)
    check("%s: phone: viewport meta, a narrow-screen rule, a scrolling table" % label,
          'name="viewport"' in page and "@media (max-width:" in page and 'class="scroll"' in page)
    check("%s: the tab reloads itself" % label, 'http-equiv="refresh"' in page)
    check("%s: carries the week's trends" % label, all(w in page for w in ("Errors handled", "Errors to a person",
                                                                         "Game tests with a real answer", "Finished")))


board_checks(page, "synthetic")
check("synthetic: Needs you (3)", needs_count(page) == 3)
check("synthetic: the needs-you tag is on its stuck line", tag_ids(page) == {"OWN_ONE"})
check("synthetic: tooling work sits in a collapsed section", "<details><summary>Tooling and cross-mod work (1)" in page)
check("synthetic: a not-yet-checked finish says so", "not yet re-checked" in page)
check("synthetic: the needs line names its mod", "Look at the bridge: right? <span class=\"note\">(Bridge Works)" in page)
check("synthetic: no record shown for days before the journal", "no record" in page)
check("synthetic: raw ids become words, the internal name stays in the hover title",
      "gates mod validation retrofit before canonical ashkarr start 2026-09-12 (owner call)" in page
      and 'title="OWN_RAW"' in page and "flyer tier one rebuild redo rows first" in page)
bad = B.render(dict(d, fleet=dict(fleet, factory={"ok": False, "why": "staffing silent 20m"}), states=None, trends=None))
check("not working says why, and unreadable sources say UNMEASURED",
      "NOT working right now: staffing silent 20m" in bad and bad.count("UNMEASURED") == 2)
empty = B.render(dict(d, fleet=dict(fleet, needs={"lines": []})))
check("an empty Needs you says so", "Needs you (0)" in empty and "Nothing waits on you" in empty)

with tempfile.TemporaryDirectory() as tmp:
    cache = os.path.join(tmp, "fleet.json")
    with open(cache, "w") as f:
        json.dump(fleet, f)
    out = B.write(out=os.path.join(tmp, "b.html"), cache=cache)
    check("write: atomic file written from the given cache", os.path.exists(out) and "Bridge Works" in open(out).read())


# ---- the live cache and store, when present (read-only)
if os.path.exists(B.FLEET_CACHE):
    live = B.render(B.gather())
    if any("stuck" in m for m in json.load(open(B.FLEET_CACHE)).get("mods") or []):
        board_checks(live, "live")
    else:
        print("SKIP live: the cache predates the stuck field (its next fleet refresh adds it)")
else:
    print("SKIP live: no fleet cache on this machine")

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
