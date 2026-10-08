# CRACKEDLANDS_LEDGES_OF_MERCY_1 — refuge ledges, carvings, chime-line anchors

Split from `CRACKEDLANDS_GPT_ENRICHMENT_1` §1 (owner-picked by card from the 2026-09-30 GPT consult,
`Transient/bedazzle_gpt_enrich_2026-09-30/crackedlands.md` §3). Also carries the mechanics item's
§6 "refuge ledges as mapgen/KCSG features" and is what `FLOOD_WITNESS_EVENT_1` depends on.

## spec (as picked)

Map generation places high ledges bearing worn figures, old offerings, and chime lines stretched
across the canyon below. Inscriptions call the flood *"the mercy that kills, then feeds."* During
warnings, neutral visitors and trained animals try to reach the nearest ledge. Inspectable carvings
and one-shot memories; no campaign precepts. Each ships a Mod Settings toggle.

## form (ruled)

**Decision taken by question card 2026-10-08: the ledge is CUT INTO THE CLIFF FACE** (a KCSG-style
structure on cliff cells). Built as our own GenStep, not a KCSG def: FloodedCanyon is RM tier and
depends only on Harmony + FlowWorks, so no framework dependency was added.

## built

- `Source/RM_LedgeRefuge.cs`: refuge/anchor marker extensions; the warning-phase sweep that sends
  neutral visitors and the player's trained animals to the nearest reachable ledge cell and holds
  them there; the flood never takes a refuge cell; chimes toll from the nearest anchor.
- `Source/RM_MercyLedges.cs` + `Defs/GenStepDefs/RM_FloodedCanyon_MercyLedges.xml` (order 245) +
  `Patches/RM_FloodedCanyon_MercyLedges_Register.xml` (MapCommonBase): carves 2-6 pockets (up to 3
  wide, 2 deep) into HIGH natural-rock faces, floors them with the rock's smoothed stone and one
  `RM_MercyLedge` per cell; cuts one `RM_MercyCarving` and one `RM_ChimeLineAnchor` into each
  pocket's walls; places as many anchors again on other high faces.
- `Defs/ThingDefs_Buildings/RM_MercyLedges.xml`: `RM_MercyLedge` (non-edifice, standable, refuge
  extension), `RM_MercyCarving` (wall cell, `CompRM_MercyCarving`: inspect shows one inscription line
  and a reader count; a humanlike within 2.9 cells with line of sight gains the memory once per
  carving), `RM_ChimeLineAnchor` (wall cell, anchor extension). All unclaimable, so the player
  cannot deconstruct them.
- `Defs/ThoughtDefs/RM_MercyCarving.xml`: `RM_ReadMercyCarving`, **PROVISIONAL +4 mood for 2 days**
  (numbers ruling 2026-10-03).
- Settings: "Ledges cut into the cliff faces (worldgen)" and "Reading a ledge carving lifts the
  mood", beside the existing refuge and anchor toggles.
- Debug: "Carve mercy ledges now (current map)" runs the carver on any map; "Report ledge refuge"
  now also prints `carvings=` and `carvingReaders=`.
- PROVISIONAL numbers: 0.5 ledges per 10k cells clamped 2-6, 30 cells between ledges, 20 between
  free anchors, 5-cell edge margin, read radius 2.9.

## owed

1. **Inscription lines and all descriptions are PLACEHOLDERS.** Drafts for the owner's review:
   `Transient/ledges_inscriptions_draft_20261008.md`. His chosen lines go into the
   `<inscriptions>` list and the descriptions.
2. **Art is PLACEHOLDER** (vanilla party-spot / small-sculpture / torch-lamp textures, tinted).
   artpipe searched 2026-10-08 (ledge, carving, chime, inscription, offering, mercy, canyon): nothing
   for this subject. Not queued: the subject's art is not yet approved.
3. Old offerings are described on the carving only; no separate offering things.

## criteria

Quicktest: ledges generate and are never flooded; during a debug-armed warning a neutral visitor
and a trained animal path to a ledge (state read); a carving's inspect text and its one-shot thought
fire once per pawn.
