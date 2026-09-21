# WORLD_LABEL_SIZE_HIERARCHY_1 — the planet has no visual label hierarchy

## the ask

🔴 **Owner ruling, 2026-09-21 (BENCH question card): size the whole planet.**

MEASURED: **all 71 world features on the canonical save sit at `maxDrawSizeInTiles = 10`**,
the bottom of the engine's size curve, so every label draws at the minimum. The 1,692-tile
Dune Sea letters exactly as large as Notch.

The Fall Line was raised to **26** (effective 15 → 42) as the single test case under
`FALL_LINE_MAJOR_REGION_LABEL_1`, verified by parsing the `.rws`, saved as
`ASHKARR_FALLLINE_LABEL26_2026-09-21` with the canonical save byte-unchanged. The other 70
are untouched. This item is the pass that scales them all.

## spec

1. Derive each feature's `maxDrawSizeInTiles` from its tile count — a curve, not a table,
   so a feature added later gets a sensible size without a hand edit.
2. Apply offline against the save. **No cold load is needed.**
3. Keep the Fall Line's 26 consistent with whatever curve is chosen, or say why it differs.
4. Produce one picture of the whole map for the owner before anything is written to the
   canonical save.

## Watch out

- 🔴 **Back up the canonical save and confirm its byte size afterwards.** Write to a NEW
  slot; `rimworld/save_game` has silently written the current slot instead of `saveName`.
- 🔴 **A `.rws` edit must use binary mode** — text mode rewrites line endings and silently
  changes the file. Check the size delta.
- ⚠️ 71 is the MEASURED feature count on the canonical save as of 2026-09-21. Re-measure
  before applying; the number moves as features are authored.

## criteria

Every world feature's label size reflects its extent, the owner has seen one picture of the
result, and the canonical save is only written on his word.
