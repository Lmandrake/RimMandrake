---
state: validated
needs: bridge
---

# SURFACE_RIVER_WEIRS_1

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Port the weir / bank-works / breach system to ordinary surface river tiles (owner-typed 2026-09-26): weir, silt-trap, stake-line, hopper, and the untended-weir-meets-flood breach cascade on normal rivers

Built at `eab81a09523d` (origin/main); code is in, what is owed is below.

## what is left

- A3

## latest ledger notes

- 2026-10-05: Slice 1 built eab81a095 (offline, not deployed): new mod src/RimMandrake/RiverWorks (mandrake.rm.riverworks) - surface current from vanilla riverFlowMap (fast=chest-deep 45t, edge=shallow 90t), size-scaled by RiverDef.widthOnMap, flood surge (SeasonalFlood/TorrentialRainFlood + RegisterFloodSource seam), RM_FordStones terrain (shallow only), wash-off-map -> walks home 1-3 d with letters, bruise/drop hazards, undrafted path-cost raise, full settings, first script validation.py + walk + selftest. 
- 2026-10-06: Slice 2 landed 456d00ca2 (+ bd25c2f21 art-ledger records): bank works moved from TerminalBiomes into River Works (defNames kept, TerminalBiomes depends on it); weir 1x2 + slack pool, fish and biome-relevant drift catch, breach washes the catch downstream, continuous stake-line levee, silt swap table, rope ferry; static_call proofs in RM_RiverWorksProofWorks; all tuning PROVISIONAL; not deployed. NEXT: deploy River Works + TerminalBiomes, run the live proof rows (Transient/belt_riverworks2_202610
- 2026-10-13: Triage 2026-10-13: ext_river 20261013b has current, ford_exempt, weir_arrest_and_pool, weir_fish_draws_stock, breach_wash, silt_richen_and_revert, ferry_rope, levee x2, breach_cascade PASS; A2 also lists flood surge and drift: flood_refill UNMEASURED (SITE). Short check: spawn SeasonalFlood on the river site (jawa/flowworks_spawn_flood) and assert surge + ProofWeirCatch drift (~5 min); A3 is the RiverWorks walk on the minimal list.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify SURFACE_RIVER_WEIRS_1 --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=SURFACE_RIVER_WEIRS_1` first: another commit may already do it.
