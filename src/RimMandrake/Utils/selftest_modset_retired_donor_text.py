#!/usr/bin/env python3
"""MODSET_TIERS_FIX_RETIRED_DONOR_TEXT: no modset tier's `want` names a donor the owner retired
(infrastructure/state/facts/retired_mods.json), and a tier `why` that names one by packageId says it is
retired, forbidden or absent -- resolve() filters them anyway, so stale text only misleads (offline)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modset_builder as mb
import retired_mods

fails = []
retired = [r["packageId"].lower() for r in retired_mods.entries() if r.get("packageId")]
ABSENT = ("retir", "forbid", "not include", "not in the list", "never load")


def problems(tiers):
    out = []
    for name, t in tiers.items():
        for w in t.get("want", ()):
            if retired_mods.is_retired(w):
                out.append("%s: want names retired donor %s" % (name, w))
        why = t.get("why", "")
        low = why.lower()
        named = [p for p in retired if p in low]
        if named and not any(k in low for k in ABSENT):
            out.append("%s: why names retired %s without saying so" % (name, named))
    return out


# sanity probe: the instrument must see a planted stale tier
probe = problems({"probe": {"why": "pulls sarg.alphaanimals transitively", "want": ["sarg.alphaanimals"]}})
if len(probe) != 2:
    fails.append("probe blind: %r" % probe)
if "sarg.alphaanimals" not in retired or "mlie.starwarsanimalcollection" not in retired:
    fails.append("retired list lacks the two art donors: %r" % retired)

fails += problems(mb.TIERS)
print("FAIL: " + "; ".join(fails) if fails else "OK selftest_modset_retired_donor_text (%d tiers)" % len(mb.TIERS))
sys.exit(1 if fails else 0)
