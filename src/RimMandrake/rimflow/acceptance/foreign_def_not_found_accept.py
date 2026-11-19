#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_READ_FOREIGN_DEF_NOT_FOUND_AS_LIST_FACT (DESIGN DECISION 2026-11-18 on
RIMMANDRAKE_AUDIT_FOREIGN_DEF_ROWS_FAIL_IN_THREE_MODS): the rule lives in the shared validation core, as one pure
function every live row asks when `get_defs` reports a def `notFound`:
  validation_core.missing_def_verdict(owner, own, active) -> (status, class, detail)
    owner   packageId of the mod that defines the def, as the row's author declares it; None = the asking mod's own def
    own     the asking mod's packageId
    active  the packageIds loaded now (ModsConfig activeMods), or None when the list could not be read
  another mod's def, that mod not loaded      -> ("UNMEASURED", "HARNESS", names the owner and "not on this list")
  the list could not be read                  -> ("UNMEASURED", "HARNESS", says the list was not read)
  the asking mod's own def, or owner loaded   -> ("FAIL", "MOD", ...): the def really is missing
packageIds compare case-blind (RimWorld's own rule). Red on 0dc24342c3 (watched)."""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import validation_core as VC  # noqa: E402

FAILS = []
OWN, BEST, ARM = "mandrake.rimstarwars.creaturebehaviors", "mandrake.rimstarwars.swbestiary", "mandrake.rimstarwars.armoury"


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def ask(owner, own, active):
    fn = getattr(VC, "missing_def_verdict", None)
    if not callable(fn):
        return ("no missing_def_verdict",)
    try:
        return tuple(fn(owner, own, active))
    except Exception as e:
        return ("CRASH %s: %s" % (type(e).__name__, e),)


def is_(got, status, cls, *words):
    return len(got) == 3 and got[0] == status and got[1] == cls and all(w.lower() in str(got[2]).lower() for w in words)


def main():
    g = ask(BEST, OWN, [OWN, "ludeon.rimworld"])
    check("another mod's def, that mod not loaded: UNMEASURED, a list fact naming the owner",
          is_(g, "UNMEASURED", "HARNESS", BEST, "not on this list"), g)
    g = ask(BEST, OWN, [OWN, BEST])
    check("another mod's def, that mod loaded: FAIL, the def is really missing", is_(g, "FAIL", "MOD"), g)
    g = ask(None, OWN, [OWN])
    check("the asking mod's own def (no owner declared): FAIL", is_(g, "FAIL", "MOD"), g)
    g = ask(OWN, OWN, [OWN])
    check("owner declared as the asking mod itself: FAIL", is_(g, "FAIL", "MOD"), g)
    g = ask(OWN.upper(), OWN, [])
    check("the asking mod's own def is FAIL even when the list is empty", is_(g, "FAIL", "MOD"), g)
    g = ask(BEST, OWN, None)
    check("the list could not be read: UNMEASURED, and it says so, never 'not on this list'",
          is_(g, "UNMEASURED", "HARNESS", "not read") and "not on this list" not in str(g[-1]).lower(), g)
    g = ask(None, OWN, None)
    check("own def with the list unread is still FAIL (the list decides nothing for it)", is_(g, "FAIL", "MOD"), g)
    g = ask(BEST, OWN, [])
    check("an empty list that WAS read: the owner is not on it, UNMEASURED", is_(g, "UNMEASURED", "HARNESS", BEST), g)
    g = ask(BEST.upper(), OWN, [OWN, BEST])
    check("packageIds compare case-blind (owner upper, list lower): loaded, FAIL", is_(g, "FAIL", "MOD"), g)
    g = ask(BEST, OWN, [OWN.upper(), "Mandrake.RimStarWars.SWBestiary"])
    check("packageIds compare case-blind (list mixed case): loaded, FAIL", is_(g, "FAIL", "MOD"), g)
    g = ask(ARM, OWN, [OWN, BEST])
    check("a different foreign owner than the one loaded: UNMEASURED naming the right one",
          is_(g, "UNMEASURED", "HARNESS", ARM), g)
    g = ask("  ", OWN, [OWN])
    check("a blank owner is no owner: FAIL", is_(g, "FAIL", "MOD"), g)
    g = ask(BEST, OWN, "mandrake.rimstarwars.swbestiary")
    check("a list that is one string, not a list, is 'could not be read', never a substring match",
          is_(g, "UNMEASURED", "HARNESS", "not read"), g)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
