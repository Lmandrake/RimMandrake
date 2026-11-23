---
state: proposed
needs: offline
---

# REEL_TAIL_VERIFY_RED_DRUM_BEIGE_TAIL

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Modern hose reel: drum hose is a red firehose (155016141574) but the C#-drawn paid-out hose may still be beige; a judge saw red-drum/beige-tail on s5_reels_13-16_v.png (2026-10-23, predates the firehose deploy) - check the current Modern hose atlas against the drum and match or rule it fine

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show REEL_TAIL_VERIFY_RED_DRUM_BEIGE_TAIL` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify REEL_TAIL_VERIFY_RED_DRUM_BEIGE_TAIL --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=REEL_TAIL_VERIFY_RED_DRUM_BEIGE_TAIL` first: another commit may already do it.
