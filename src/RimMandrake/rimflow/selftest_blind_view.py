#!/usr/bin/env python3
"""selftest_blind_view.py — the token-blind view of the queue and of item notes (blind_view.py; review W, L1 + L3).

The ruling: no token, account, runway, quota, week, burn or cap value may reach a token-blind role. The view is a
closed type (contracts.blind; BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF): no title, note, reason or summary text at all.
  phrasings    every phrasing review W and review X found, put in a title, a block reason and a note of a fake
               item: the queue and show pages carry none of its words or numbers
  real ledger  the real current BENCH and FOUNDRY queues and every note of every V3 item, through the blind view,
               checked by an INDEPENDENT leak detector (its own regexes, clause-level)
  instrument   the detector is first shown to find leaks in the RAW text of the same items, so a clean result
               means the view kept them out, not that the detector is blind
Reads the ledger; writes nothing.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import blind_view as B  # noqa: E402
from contracts import blind_core as BC  # noqa: E402
from rimflow import model, render  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


# ---- the independent detector: shares no code with blind_view ----
_SENS = re.compile(r"(?i)(account|token|quota|budget|runway|burn|spend|spent|usage|limit|week|percent|pct|economy"
                   r"|(?<![a-z])cap(?:s|ped|ping)?(?![a-z]))")
_UNIT = re.compile(r"(?<![A-Za-z0-9_])\$?\d+(?:[.,]\d+)*\s?(?:[kKM]|%|tokens?)(?![A-Za-z0-9])")
_NUM = re.compile(r"(?<![A-Za-z0-9_\-:.])\d+(?:[.,]\d+)*(?![A-Za-z0-9_\-:])")
_DT = re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?Z?)?|\b\d{1,2}:\d{2}(?::\d{2})?Z?")
_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")       # item ids: their words are names, not values
_ACCOUNT_ID = re.compile(r"\b(?:OPS|OPERATIONS|ACCOUNTS?|QUOTAS?)_[A-Z0-9_]+")
# a duration or a frame rate is never an account value (a frame budget of 8 ms, a wait of 5 min)
_DURATION = re.compile(r"\b\d+(?:\.\d+)?\s?(?:ms|s|min|h|TPS|FPS|weeks?)\b")


def leaks(text):
    """-> the clauses of `text` that carry an account or cap value: a number with a k/M/%/tokens unit anywhere, or a
    number in the same clause as an account/cap word; and any id naming accounts."""
    out = [m.group() for m in _ACCOUNT_ID.finditer(text)]
    for line in text.splitlines():
        line = _DURATION.sub(" DUR ", _ID.sub(" ID ", _DT.sub(" DT ", line)))
        for clause in re.split(r";|\.\s|\(|\)|,\s|\s[-–]\s|:\s", line):
            if _UNIT.search(clause) or (_SENS.search(clause) and _NUM.search(clause)):
                out.append(clause.strip()[:160])
    return out


class _It:
    def __init__(self, iid, title="", kind="task"):
        self.id, self.title, self.kind = iid, title, kind


PHRASES = ["Producer daily_token_cap 125,000 vs run and event caps of 100,000: after a 09:00 run over 25k",
           "lukas has 7 left", "lukas fell from 93 to 41 since Monday", "codex sits at 61/100",
           "sonnet at 30, opus at 85", "forecast: plan misses by 1.4 days on lukas",
           "REPLAN REQUEST: the rows will not fit; lukas has 0.4d", "steven remaining 7, system 12",
           "running 2.6x over pace", "burn rate 2.6x", "headroom 0.4d on codex 1.3d", "~120 thousand used so far",
           "a hundred and twenty five thousand", "spent 3 million", "allowance of \u20ac120",
           "| item | runway |\n|---|---|\n| d | 88 |", "| seat | share |\n| BENCH | 61 |",
           "see PRODUCER_RUN_30K_EVENT", "see LUKAS_93_WEEK_DRAIN", "see HELPER_WAITS_93_PERCENT",
           "usage limit reached 4217", "weekly quota 77 percent", "account acct-7781 drained 4.2M"]


class _Full(_It):
    def __init__(self, iid, title="", kind="task", owner="BENCH", hist=()):
        super().__init__(iid, title, kind)
        self.owner, self.state, self.blocked, self.needs, self.row, self.open = owner, "doing", True, "offline", None, True
        self.blocked_reason, self.closed_sha, self.superseded_by = title, None, None
        self.history = list(hist)


def test_phrasings():
    """Every known phrasing, as title, block reason and notes: none of its words or digits reaches either page."""
    from contracts import blind as BL
    evs = [{"event": "note", "ts": "2026-10-27T10:00:%02dZ" % n, "seat": "BENCH", "text": t + " see SAFE_ITEM_ONE"}
           for n, t in enumerate(PHRASES)] + [{"event": "claim", "ts": "2026-10-27T11:00:00Z", "seat": "BENCH"}]
    it = _Full("SAFE_ITEM_TWO", "\n".join(PHRASES), hist=range(len(evs)))
    hold = _Full("OPS_RUNWAY_RESCUE_LUKAS", "lukas 7 left")
    q = BL.render_queue(BL.project_queue("BENCH", [("NEXT", [it, hold])], frozenset({hold.id})))
    page = BL.render_item(BL.project_item(it, evs[:-1], evs[-1:], frozenset({hold.id}), frozenset({"SAFE_ITEM_ONE"}),
                                          last=0, prefix="REPLAN REQUEST"))
    for name, text in (("queue", q), ("show", page)):
        bad = [w for t in PHRASES for w in re.findall(r"[A-Za-z]{4,}|\d+(?:[.,]\d+)?", t)
               if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(w), text)
               and w not in ("REPLAN", "REQUEST", "BENCH", "item", "rows", "state", "will", "since", "see", "seat")
               and not re.fullmatch(r"\d{1,2}", w)]
        check(not bad and not leaks(text), "phrasings: the %s page holds none of them: %s %s" % (name, bad[:6],
                                                                                              leaks(text)[:3]))
    check("SAFE_ITEM_ONE" in page and "OPS_RUNWAY" not in page + q, "phrasings: a known id is referenced, "
          "a withheld one never named")
    check("1 match the prefix" in page, "phrasings: --prefix counts the REPLAN note")
    check("1 open item(s) withheld" in q, "phrasings: the queue counts the withheld item")


def test_closed():
    """The page types are closed: no direct construction, no extra field, no renderer on a dict."""
    from contracts import blind as BL
    import pydantic
    for f in (lambda: BL.QueueItem(id="A_B", state="doing", blocked=False, needs="offline"),
              lambda: BL.BlindQueue.model_construct(seat="BENCH"),
              lambda: BL.render_queue({"seat": "BENCH", "sections": []}),
              lambda: BL.render_item({"withheld": True})):
        try:
            f()
            ok = False
        except (pydantic.ValidationError, BL.ProjectionOnly):
            ok = True
        check(ok, "closed: a page cannot be built or rendered except by projection")



def test_withheld():
    check(B.withheld(_It("OPS_RUNWAY_RESCUE_LUKAS")), "an OPS_ item is withheld")
    check(B.withheld(_It("QUOTA_LEFT_AT_RESET_MEASURE_PER_ACCOUNT")), "an id with an ACCOUNT or QUOTA part is withheld")
    check(B.withheld(_It("X_Y_Z", "", "budget")), "a budget kind is withheld")
    check(not B.withheld(_It("TPS_VERDICT_FIX", "windows ACCOUNTED for")), "a title word alone withholds nothing")
    check(not B.withheld(_It("DUNG_HATCH_WILDLIFE_CAP_1")) and not B.withheld(_It("ANIMALDUPES_ORPHAN_OPS_AUDIT")),
          "game words (a wildlife CAP, patch OPS mid-id) withhold nothing")
    check(not B.withheld(_It("V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE", "Eight chairs")), "an ordinary item is shown")


def test_real_ledger():
    evs = model.read()
    world = model.replay(evs)
    v3 = sorted(i for i in world.items if "V3" in i.split("_"))
    check(len(v3) >= 3, "the ledger has V3 items to read (%d)" % len(v3))
    blind, raw = [], []
    for seat in ("BENCH", "FOUNDRY"):
        q = B.queue_text(world, seat)
        check(q.count("\n- **") >= 5, "%s blind queue lists items (%d)" % (seat, q.count("\n- **")))
        blind.append(q)
        for it in world.items.values():
            if it.owner == seat and it.open:
                raw.append("## %s %s\nblocked: %s\nsummary: %s" % (it.id, it.title, it.blocked_reason or "",
                                                                   render.summary(it.id)))
    for iid in v3:
        blind.append(B.show_text(evs, world, iid, last=0))
        it = world.items[iid]
        raw.append(it.title or "")
        raw += [evs[i].get("text") or "" for i in it.history if evs[i].get("event") == "note"]
    # instrument: the detector sees leaks in the raw text of the very same items
    raw_hits = leaks("\n".join(raw))
    check(len(raw_hits) >= 5, "instrument: the detector finds %d leak clause(s) in the RAW queue + V3 notes"
          % len(raw_hits))
    check(any("100,000" in h or "125,000" in h for h in raw_hits) or "PRODUCER_CAP_BALANCE_EVENT_ROOM" not in
          "\n".join(raw), "instrument: the raw L1 cap values are among the detector's hits (while that item is open)")
    hits = leaks("\n".join(blind))
    check(not hits, "the blind queues and V3 notes carry no account or cap value (%d hit(s)): %s"
          % (len(hits), hits[:5]))
    hidden = B.hidden_ids(world)
    shown = set(re.findall(r"^- \*\*(\S+?)\*\*", "\n".join(blind), re.M))
    check(len(shown) >= 10, "the blind queues name items (%d)" % len(shown))
    check(not (shown & hidden), "no withheld item is listed: %s" % sorted(shown & hidden)[:5])
    check(all(B.show_text(evs, world, i).count("\n") == 1 for i in list(hidden)[:20]),
          "show on a withheld item prints one line")
    # every open item of the seat is either listed or counted withheld: a section the view does not know is never dropped
    for seat, q in zip(("BENCH", "FOUNDRY"), blind):
        open_ids = {i.id for i in world.items.values() if i.owner == seat and i.open and i.id not in hidden}
        listed = set(re.findall(r"^- \*\*(\S+?)\*\*", q, re.M))
        refused = {i for i in open_ids if BC.item_id_problem(i)}      # an id with a token word: withheld, counted
        n = int(re.search(r"(\d+) open item\(s\) withheld", q).group(1))
        check(open_ids - refused <= listed, "%s: every open item is listed (%d missing: %s)" % (
            seat, len(open_ids - refused - listed), sorted(open_ids - refused - listed)[:4]))
        check(n >= len(refused) + len({i.id for i in world.items.values() if i.owner == seat and i.open} & hidden),
              "%s: every open item not listed is counted withheld (%d)" % (seat, n))


def test_ids_survive():
    class W:
        pass
    w = W()
    w.items = {i: _Full(i) for i in ("DUNG_HATCH_WILDLIFE_CAP_1", "PRODUCER_RUN_30K_EVENT")}
    keep, hide = B.known_ids(w), B.hidden_ids(w)
    check("DUNG_HATCH_WILDLIFE_CAP_1" in keep and "PRODUCER_RUN_30K_EVENT" in hide, "ids: 30K id withheld, CAP_1 kept")
    out = B.show_text([], w, "DUNG_HATCH_WILDLIFE_CAP_1")
    check(out.startswith("DUNG_HATCH_WILDLIFE_CAP_1 state doing"), "ids: show finds the CAP_1 item: %r" % out[:60])
    check("withheld" in B.show_text([], w, "PRODUCER_RUN_30K_EVENT") and "30" not in B.show_text(
        [], w, "PRODUCER_RUN_30K_EVENT"), "ids: show withholds the 30K item and never names it")


def main():
    for t in (test_withheld, test_phrasings, test_closed, test_ids_survive, test_real_ledger):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
