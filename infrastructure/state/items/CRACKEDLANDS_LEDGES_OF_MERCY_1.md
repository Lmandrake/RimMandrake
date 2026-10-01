# CRACKEDLANDS_LEDGES_OF_MERCY_1 — refuge ledges, carvings, chime-line anchors

Split from `CRACKEDLANDS_GPT_ENRICHMENT_1` §1 (owner-picked by card from the 2026-09-30 GPT consult,
`Transient/bedazzle_gpt_enrich_2026-09-30/crackedlands.md` §3). Also carries the mechanics item's
§6 "refuge ledges as mapgen/KCSG features" and is what `FLOOD_WITNESS_EVENT_1` depends on.

## spec (as picked)

Map generation places high ledges bearing worn figures, old offerings, and chime lines stretched
across the canyon below. Inscriptions call the flood *"the mercy that kills, then feeds."* During
warnings, neutral visitors and trained animals try to reach the nearest ledge. Inspectable carvings
and one-shot memories; no campaign precepts. Each ships a Mod Settings toggle.

## what already exists to hook

- `RM_MapComponent_CanyonFlood` now has a Herald phase and a `pendingSeed` (where the water will
  arrive), chosen when the warning begins. Chimes toll at POSITIONS on a far-corner→seed line
  (`ChimeCell`). Once chime-line anchors exist as things, replace those positions with the nearest
  anchors.
- Flood cells exclude any cell with an edifice (`Eligible`), so a ledge built as an edifice is
  never flooded.

## open questions (owner)

1. **What is a "high ledge" in RimWorld**, which has no elevation? Options: a walkable edifice
   platform (never flooded, because flood cells skip edifices); a KCSG structure cut into a cliff
   face; or a terrain band beside natural walls that `Eligible` excludes. Each changes placement and
   art.
2. **The inscription lines and carving descriptions** are lore in the owner's voice (review §G:
   "drafted lines must go to him"). Draft them for him; do not ship them unreviewed.
3. **One-shot memory**: mood value and duration for reading a carving. Choosing one would invent a
   number.
4. **Art** for the ledge, the worn figures, the offerings and the chime line. Check artpipe
   `done/`, `_artsrc/` and `registry.jsonl` first.

## build once answered

GenStep placing the ledges outside floodable ground; a flood-phase hook that, during Herald and
Warned, gives neutral visitors and the player's trained animals a goto job to the nearest reachable
ledge (sonnet; escalate to opus if the lord AI fights the engine); an inspectable carving building
with the one-shot thought; chime-line anchor things that `RingChime` uses in place of positions.

## criteria

Quicktest: ledges generate and are never flooded; during a debug-armed warning a neutral visitor
and a trained animal path to a ledge (state read); a carving's inspect text and its one-shot thought
fire once per pawn.
