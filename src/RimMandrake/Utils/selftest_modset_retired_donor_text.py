#!/usr/bin/env python3
"""MODSET_TIERS_FIX_RETIRED_DONOR_TEXT: no modset tier's `want` names a donor the owner retired
(infrastructure/state/facts/retired_mods.json), and a tier `why` that names one by packageId says it is
retired, forbidden or absent -- resolve() filters them anyway, so stale text only misleads (offline)."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modset_builder as mb
import retired_mods

fails = []
retired = [r["packageId"].lower() for r in retired_mods.entries() if r.get("packageId")]
ABSENT = ("retir", "forbid", "not include", "not in the list", "never load", "neither", "no longer")
# Per-clause, not per-why: a clause that names a retired packageId must itself say it is gone. A why that says
# "sarg.alphaanimals stays: another donor, W5; insectoid2 retired" is the misleading text this item removes, even
# though 'retired' appears in the same why (blind check at 213c6432 found the per-why check let it through).
CLAUSE = re.compile(r"[.;:](?:\s|$)|\s--\s")


def clauses(text):
    return [c for c in CLAUSE.split(text) if c.strip()]


def problems(tiers):
    out = []
    for name, t in tiers.items():
        for w in t.get("want", ()):
            if retired_mods.is_retired(w):
                out.append("%s: want names retired donor %s" % (name, w))
        for clause in clauses(t.get("why", "")):
            low = clause.lower()
            named = [p for p in retired if p in low]
            if named and not any(k in low for k in ABSENT):
                out.append("%s: why clause names retired %s without saying so: %r" % (name, named, clause.strip()[:90]))
    return out


# sanity probe: the instrument must see a planted stale tier
probe = problems({"probe": {"why": "pulls sarg.alphaanimals transitively", "want": ["sarg.alphaanimals"]}})
if len(probe) != 2:
    fails.append("probe blind: %r" % probe)
# per-clause probe: the old donor_off_w4 line names alphaanimals as staying; 'retired' elsewhere must not hide it
probe2 = problems({"probe2": {"why": "sarg.alphaanimals stays: another donor, W5; insectoid2 retired 2026-10-18",
                              "want": []}})
if len(probe2) != 1:
    fails.append("per-clause probe blind: %r" % probe2)
# and a clause that does say so stays clean
probe3 = problems({"probe3": {"why": "Both art donors (it and sarg.alphaanimals) were retired 2026-10-18. W5 next.",
                              "want": []}})
if probe3:
    fails.append("per-clause probe over-fires: %r" % probe3)
if "sarg.alphaanimals" not in retired or "mlie.starwarsanimalcollection" not in retired:
    fails.append("retired list lacks the two art donors: %r" % retired)

fails += problems(mb.TIERS)
print("FAIL: " + "; ".join(fails) if fails else "OK selftest_modset_retired_donor_text (%d tiers)" % len(mb.TIERS))
sys.exit(1 if fails else 0)
