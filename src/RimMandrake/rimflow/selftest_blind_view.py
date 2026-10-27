#!/usr/bin/env python3
"""selftest_blind_view.py — the token-blind view of the queue and of item notes (blind_view.py; review W, L1 + L3).

The ruling: no token, account, runway, quota, week, burn or cap value may reach a token-blind role. Three parts:
  units        the leaking strings review W found, redacted; dates, clock times, shas and ordinary numbers pass
  real ledger  the real current BENCH and FOUNDRY queues and every note of every V3 item, through the blind view,
               checked by an INDEPENDENT leak detector (its own regexes, clause-level, stricter than redact())
  instrument   the detector is first shown to find leaks in the RAW text of the same items, so a clean result
               means the view redacted them, not that the detector is blind
Reads the ledger; writes nothing.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import blind_view as B  # noqa: E402
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
_DURATION = re.compile(r"\b\d+(?:\.\d+)?\s?(?:ms|s|min|h|TPS|FPS)\b")


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


def test_units():
    t = ("Producer daily_token_cap 125,000 vs run and event caps of 100,000: after a 09:00 run over 25k, "
         "no event run fits")
    r = B.redact(t)
    check("125,000" not in r and "100,000" not in r and "25k" not in r, "L1 title: every cap value redacted: %s" % r)
    check("09:00" in r and "daily_token_cap" in r, "L1 title: the clock time and the field name pass")
    t = "quick 30k/run, 200k/day, session 6% of week; runway bands GREEN>=1.5 AMBER>=1.0 RED<1.0 FLOOR<10% left"
    r = B.redact(t)
    check(not re.search(r"\d", r), "L3 note: no digit survives: %s" % r)
    t = "closed at 4a2b183eca on 2026-10-27T11:59:47Z after 3 rounds; see review_v3_W"
    check(B.redact(t) == t, "a sha, an ISO time and a small count with no account word pass unchanged")
    check(B.redact("week_left_pct 41 and session_week_pct_cap 80") == "week_left_pct %s and session_week_pct_cap %s"
          % (B.MASK, B.MASK), "snake_case account fields mask their values")
    check(B.MASK in B.redact("spent 3.8% of total"), "a % value masks even without an account word")
    check(B.redact("ran 1 2 3 then 99999") .endswith(B.MASK), "a bare number >= BIG_NUMBER is masked")
    check(B.redact("filed OPS_RUNWAY_RESCUE_LUKAS, _C01D (system)") == "filed %s, %s (system)" % (B.MASK, B.MASK),
          "account ids and alarm-id fragments are masked even when not in this world")
    check(B.redact("see X_Y", hide_ids={"X_Y"}) == "see " + B.MASK, "a withheld id is masked in other items' text")
    check(B.redact(None) == "", "None -> empty")


class _It:
    def __init__(self, iid, title="", kind="task"):
        self.id, self.title, self.kind = iid, title, kind


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
        check(q.count("\n## ") >= 5, "%s blind queue lists items (%d)" % (seat, q.count("\n## ")))
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
    shown = set(re.findall(r"^## (\S+)", "\n".join(blind), re.M))
    check(not (shown & hidden), "no withheld item is listed: %s" % sorted(shown & hidden)[:5])
    check(all(B.show_text(evs, world, i).count("\n") == 1 for i in list(hidden)[:20]),
          "show on a withheld item prints one line")


def main():
    for t in (test_units, test_withheld, test_real_ledger):
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
