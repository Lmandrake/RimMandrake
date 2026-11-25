"""Offline selftest: a record a chain makes OUTSIDE any component is kept on the chain (TestContext.setup_records), never
dropped (RIMMANDRAKE_READ_WHY_STEVE_SICKLY_SWEEP_FINDS_NONE_SAVES_SAY_TWO).

The Pyrelands chain loads its registered site in chain setup, before its first component; that load's record carries the
site's quiet-profile receipt (the Sickly sweep that removed the trait), and suite._record dropped it, so the sheet showed
no removal at all (SteveDesktop J20261125T193718Z-312826). Run: python3 selftest_suite_setup_records.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

import suite as S                       # noqa: E402
from rimdrive.fake import FakeWorld     # noqa: E402

_results = []


def check(name, cond, detail=""):
    _results.append((name, bool(cond)))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + detail) if (detail and not cond) else ""))


def main():
    t = S.TestContext(FakeWorld())
    receipt = {"quietSite": {"diseaseTraits": {"removed": [["Human75828", "Immunity -1"]]}}}
    t._record("on_site: loaded the registered site NS_Pyrelands_site_1_417df172fdb5_visit5", receipt)
    kept = getattr(t, "setup_records", None) or []
    check("a record outside any component is kept on the chain",
          len(kept) == 1 and kept[0].get("result") == receipt, str(kept))
    with t.component("inside"):
        t._record("inside call", {"ok": True})
    comp = t.components[-1]
    check("a record inside a component still goes to that component only",
          any(e.get("call") == "inside call" for e in comp.evidence) and len(getattr(t, "setup_records", [])) == 1,
          "%s %s" % (comp.evidence, getattr(t, "setup_records", None)))
    bad = sum(1 for _, ok in _results if not ok)
    print("\n%d/%d passed" % (len(_results) - bad, len(_results)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
