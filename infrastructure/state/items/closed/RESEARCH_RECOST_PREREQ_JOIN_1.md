# RESEARCH_RECOST_PREREQ_JOIN_1 — re-cost to tier bands, join logical prereqs, flag functionless tech

Owner, 2026-09-04, going AFK: *"accept all your fixes, and yes time for
recosting and joining logical prerequisites together. Please also flag
effectively functionless tech in the game that might be repurposed for our
plot or other functions."*

## spec

Source of truth: `design/Jawa/research_review/research_deck_FROZEN_20260904.json`
(the owner's frozen deck). Target:
`infrastructure/output/research_manifest_draft.csv`.

1. Apply the four accepted prereq rulings (beamcasting→RimAI Lv2; ship-designs
   and military-clothing dead prereqs dropped; plasma onto the blaster spine).
2. Re-cost every surviving out-of-band row into its frozen tier's band
   (T0≤600 · T1 700–1600 · T2 1700–3000 · T3 3200–5000 · T4 5200+ targets).
3. Prereq join: drop edges to cut rows and tier-inverted edges (they contradict
   the frozen tiers); anchor rootless T1+ rows to a lower-tier same-tree row,
   same category preferred; every change noted per-row in the manifest.
4. Functionless sweep → `design/Jawa/research_review/functionless_tech_candidates.md`.

## verify

`research_manifest_validate.py`: checks 2, 4, 5, 6, 7 PASS (prereqs resolve,
one blaster chain, coverage 522==522 fingerprint-verified, no cycles). Check 3's
remaining 185 are ALL techLevel-field mismatches — fixable only by the retag
def patch (known later execution), not by any CSV value. Check 1: 0 fail.

## done

2026-09-04, BENCH. Re-cost 103 rows + 3 merge donors; dropped 106 tier-inverted
edges; anchored 61 rootless rows; wired the blaster spine mini→hvy→blasters
with plasma off hvy. Functionless: 8 real candidates triaged (ship-design trio =
the plot carriers; Xenobiology = the Anomaly-access anchor candidate; 2 RR
scaffold nodes left alone), 7 allowlisted alive.
