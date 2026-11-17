---
state: proposed
needs: offline
---

# GSS_MODERN_STRIP_BUILD_PLUGS_AT_LAST

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

GSS Modern look: 3/4-way junctions draw the long PowerStrip art with every cord plugged in (a 3-way takes two cords plus its own lead); Industrial keeps Junction_T/X; Scrapper and Futuristic unchanged

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show GSS_MODERN_STRIP_BUILD_PLUGS_AT_LAST` history before building.

## latest ledger notes

- 2026-11-08: Owner sitting 2026-11-08 12:20 fixes on ralph/gss: strip plugs lean toward back/free-arm cords (StripLeanBack 1.3, StripLeanFree 0.9; Modern hairpins >150 deg 9 -> 2 of 39); strip PNG cord tails removed; grid heap knob CordBuilder.HeapDensity 0.35 with floors 3 boxes / HeapMinCables 6 (Modern heap 14 cables 7 strips -> 6 and 3; Scrapper 23 and 13 -> 9 and 5); drip loops off by default (AerialMath.DripLoopsDefault false, the pole-top kinks); a pole's or mast's device lead lies from its foot on th

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GSS_MODERN_STRIP_BUILD_PLUGS_AT_LAST --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GSS_MODERN_STRIP_BUILD_PLUGS_AT_LAST` first: another commit may already do it.
