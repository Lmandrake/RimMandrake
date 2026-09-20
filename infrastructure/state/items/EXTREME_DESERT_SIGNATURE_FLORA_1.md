# EXTREME_DESERT_SIGNATURE_FLORA_1 — author the extreme desert's own signature flora

## ruling (owner, 2026-09-20)

The deep desert's signature leafless silver/bone-white tree is named
**ollim**. Passes `check_pseudo_sw_name.py` (PASS, checked against the 137
canon entries, 2026-09-20). This is the final name — `deep_desert.md`'s
"owner to pick" line is now stale and has been corrected. Not yet authored
as a def; that remains this item's own work (defName e.g. `RSW_Ollim`, per
the naming-tier grammar).

## what is wrong

3,969 tiles of RUT_ExtremeDesert carry one plant: a donor bloddle whose own
"no green, no leaves" eye-test is unverified (see `BLODDLE_DUNE_SEA_EYE_TEST_1`).
The biome's actual signature flora, named in the design sheets, has no def and
no ledger item: **glass-nub light-pipes** (dune_sea §4 — "the only visible part
of almost everything alive here") and the silver/bone-white tree, working name
"silverbole" in deep_desert.md §4b, final name **ollim** per the 2026-09-20
ruling above.

## why it matters

The extreme desert's visual identity is entirely absent from the shipped
biome — a player walking it sees only one unverified donor plant.

## the work

Author two ThingDef plants:
- `RSW_` light-pipe nub — tiny, glassy, `fertilityMin` 0.05, no leaves.
- `RSW_Ollim` (final name, see ruling above) — tree, no leaves, bone-white,
  `RSW_`-tier wood ThingDef carrying a heat-immune / sharp-weak stat
  signature.

Wire both into RUT_ExtremeDesert's `wildPlants` at trace commonality (nub 0.1,
ollim 0.01); leave `plantDensity` at the biome's current 0.008. Art via
`fill_queue.py` — never hand-written. No separate name card is needed; confirm
before shipping that "silver required" (deep_desert §4b) is satisfied by the
actual stat/material choice, not just the name.

## Watch out

Cross-reference `BLODDLE_DUNE_SEA_EYE_TEST_1` — if that item's resolution
moves bloddle off RUT_ExtremeDesert onto RUT_Desert, light-pipe/silverbole
become the ONLY flora on RUT_ExtremeDesert and the commonality math above
should be revisited before shipping.

## verify

RUT_ExtremeDesert's BiomeDef `wildPlants` lists both new RSW_ defNames at the
stated commonality; both plants render with real (non-placeholder) art in a
rendered contact sheet.

## criteria

The extreme desert has its own named signature flora matching the design
sheet, not a single unverified donor plant.
