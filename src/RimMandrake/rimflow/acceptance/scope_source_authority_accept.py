#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_LABEL_CONDUCTOR_OPENED_SCOPE_NOT_HIS_WORDS (DESIGN DECISION 2026-11-18, settling the
scope_source question left on RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS): a Conductor event MAY open a built
thing's scope (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM), but it is never stored under his name.
  scope "opened_by_owner"     needs scope_source OWNER:<tsn>, at least one cited event carrying his words (ownerSaid or
                              byCard); an OWNER-shard event with none of his words does not open it.
  scope "opened_by_conductor" needs scope_source CONDUCTOR:<tsn>, each an OWNER-shard event whose perRuling is
                              CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM and which carries none of his words.
Both let a removal ask through (ask_errors) and both count as in scope (UNIT_SCOPES). Found, not found in a ledger that
was read, and ledger unread stay three answers. Red on 29dc91cd2 (watched)."""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402

FAILS = []
RULING = "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"
EV = {"7001": {"tsn": "7001", "id": "ITEM_X", "seat": "OWNER", "ownerSaid": "we may not need the ladder after all"},
      "7002": {"tsn": "7002", "id": "ITEM_X", "seat": "OWNER", "byCard": "Ladder: keep or cut? -> ask me"},
      "7003": {"tsn": "7003", "id": "ITEM_X", "seat": "OWNER", "perRuling": RULING,
               "why": "delegated: the ladder's scope is open", "text": "open the ladder's scope"},
      "7004": {"tsn": "7004", "id": "ITEM_X", "seat": "OWNER",
               "perRuling": "RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME",
               "why": "delegated: evidence-for-ask: open the ladder"},
      "7005": {"tsn": "7005", "id": "ITEM_X", "seat": "OWNER", "why": "a note with no words of his and no ruling"},
      "7006": {"tsn": "7006", "id": "ITEM_X", "seat": "OWNER", "perRuling": RULING, "ownerSaid": "open it",
               "why": "his words, relayed"}}


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def errs(scope, src, ev=EV):
    e = {"id": "inv_ladder", "impl": "present", "impl_evidence": "src/x.cs", "proof": "missing", "scope": scope}
    if src is not None:
        e["scope_source"] = src
    try:
        return DS.inventory_errors(e, None, ev)
    except Exception as x:
        return ["CRASH %s: %s" % (type(x).__name__, x)]


def opens(name, scope, src, ev=EV):
    got = errs(scope, src, ev)
    check(name, got == [], got)


def shut(name, scope, src, ev=EV, need=None):
    """Refused for the scope's own reason: a crash, or today's `scope ... is not one of` line, is not that."""
    got = errs(scope, src, ev)
    ok = bool(got) and not any("CRASH" in g or "is not one of" in g for g in got)
    if need:
        ok = ok and any(need in g for g in got)
    check(name, ok, got)


def main():
    O, C = "opened_by_owner", "opened_by_conductor"
    opens("owner: his typed words open it", O, "OWNER:7001")
    opens("owner: his card opens it", O, ["OWNER:7002"])
    opens("owner: one of several cited events carrying his words opens it", O, ["OWNER:7003", "OWNER:7001"])
    opens("owner: a legacy space-separated citation with his words opens it", O, "OWNER:7001 OWNER:7002")
    opens("owner: his words relayed under the ruling are still his words", O, "OWNER:7006")
    shut("owner: a Conductor per-ruling event is not stored as his opening", O, "OWNER:7003")
    shut("owner: an OWNER-shard event with no words of his does not open it", O, "OWNER:7005")
    shut("owner: only word-less events, several, do not open it", O, ["OWNER:7003", "OWNER:7005"])
    shut("owner: an event that is not in the ledger does not open it", O, "OWNER:999999")
    shut("owner: no source does not open it", O, None)
    shut("owner: a CONDUCTOR: citation does not open it under his name", O, "CONDUCTOR:7003")
    opens("conductor: a Conductor-authority event opens it", C, "CONDUCTOR:7003")
    opens("conductor: a list of one opens it", C, ["CONDUCTOR:7003"])
    shut("conductor: another ruling's event (Evidence-for-Ask) does not open it", C, "CONDUCTOR:7004")
    shut("conductor: an event with no ruling does not open it", C, "CONDUCTOR:7005")
    shut("conductor: his own words are not stored as the Conductor's", C, "CONDUCTOR:7001")
    shut("conductor: an event that is not in the ledger does not open it", C, "CONDUCTOR:999999")
    shut("conductor: an OWNER: citation does not open it", C, "OWNER:7003")
    shut("conductor: no source does not open it", C, None)
    shut("conductor: a prefix with no event id does not open it", C, "CONDUCTOR:abc")
    shut("conductor: one bad citation in a list shuts it", C, ["CONDUCTOR:7003", "CONDUCTOR:7005"])
    shut("conductor: a ledger that was not read is UNMEASURED, not a forgery", C, "CONDUCTOR:7003", ev=None,
         need="UNMEASURED")
    shut("conductor: a ledger read as no events is UNMEASURED too", C, "CONDUCTOR:7003", ev={}, need="UNMEASURED")
    check("opened_by_conductor is a scope value", C in DS.SCOPE, DS.SCOPE)
    check("a scope the Conductor opened counts as in scope (UNIT_SCOPES)", C in DS.UNIT_SCOPES, DS.UNIT_SCOPES)
    ask = {"id": "a1", "text": "Keep or remove the ladder?", "decision": "ladder stays or goes",
           "about": ["inv_ladder"], "offers_removal": True, "author": "run-1",
           "review": {"by": "agent-2", "verdict": "pass", "why": "cites the entry"}, "source": "log.md#L1"}

    def removal_refused(scope):
        rec = {"inventory": [{"id": "inv_ladder", "impl": "present", "scope": scope}]}
        try:
            return any("offers to remove" in g for g in DS.ask_errors(dict(ask), rec))
        except Exception as x:
            return "CRASH %s: %s" % (type(x).__name__, x)
    check("a removal ask on a scope nobody opened is refused", removal_refused("approved") is True,
          removal_refused("approved"))
    check("a removal ask on a scope he opened is let through", removal_refused(O) is False, removal_refused(O))
    check("a removal ask on a scope the Conductor opened is let through", removal_refused(C) is False,
          removal_refused(C))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
