---
state: built
needs: bridge
---

# HOSE_REEL_SHADOW_FIX_FULL_TILE_SQUARE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Scrapper/Industrial/Futuristic hose reels cast a full-tile square block shadow while Modern casts almost none: RM_HoseReelStyles.xml shadowData volume (1.23,0.35,1.04) vs Modern (0.65,0.35,0.65); pick one volume that fits the reel body (capture s5_reels_13-16_v)

Built at `705e8eb1490a` (origin/main); code is in, what is owed is below.

## what is left

- A1

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_REEL_SHADOW_FIX_FULL_TILE_SQUARE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_REEL_SHADOW_FIX_FULL_TILE_SQUARE` first: another commit may already do it.
