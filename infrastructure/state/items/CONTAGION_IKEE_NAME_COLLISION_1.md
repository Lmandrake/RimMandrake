## What happened
Found live 2026-09-29 while deploying `CONTAGION_RULED_CONTENT_1` Wave A
(`deploy_custom_mods.py --compose biomes`'s own cross-mod overlap check —
"3 relative path(s) shipped by more than one entry; RimWorld keeps only one
of each (DirectXmlLoader TryAdd), silently").

Two DIFFERENT biomes independently built a creature named **"ikee"** off
what reads like the SAME owner naming ruling (2026-08-15), on the SAME day
(2026-09-27):

- **The Contagion** (this item's Wave A, cast bible §2): "ikee" — "a
  shivering eye-cluster on legs that follows bigger things and watches,"
  the eyeling/wretched-small, defName `RM_Ikee` per the cast bible.
- **Stillsand** (`STILLSAND_RULED_CONTENT_1`, Q1 tier move sitting,
  `src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Ikee.xml`, already
  built and presumably deployed before this pass): "ikee" — "a grotesquely
  enlarged eye that drags itself along on a few fleshy tentacles," ported
  from `RSW_Ikee` (Star Wars DesertPort) into a franchise-free RM_ copy for
  the Dune Sea.

Both are eye-creatures, both are named "ikee," both cite the same 2026-08-15
ruling, and both live in `defName RM_Ikee` — a hard collision. RimWorld's
`DirectXmlLoader` keeps only whichever one loads last and silently drops the
other's ThingDef+PawnKindDef; the game would not error, it would just make
one of the two creatures vanish from the world with no diagnostic.

## What I did (non-destructive, does not adjudicate)
Renamed ONLY the Contagion side's defName to `RM_ContagionIkee` (ThingDef,
PawnKindDef, race reference, texPath, and the matching Textures/ folder) so
both mods can coexist without a silent drop. The Contagion creature's
**label** stays "ikee" (unchanged, per the cast bible's naming ruling) — only
the internal defName changed. Stillsand's `RM_Ikee.xml` was NOT touched.

## What needs an owner ruling
The label collision is still live: a player who has both biome mods active
will see two different creatures both called "ikee" in-game (tooltips,
bestiary, kill logs). Options for the owner:
1. One of the two is renamed at the LABEL level too (which biome actually
   owns "ikee"? — the 2026-08-15 ruling's original context would settle it,
   but that context isn't in either build's own file).
2. Both keep the label "ikee" and it's accepted as a homonym across
   unrelated biomes (RimWorld has precedent for reused common-word labels
   across mods; less clean but not unheard of).
3. One is renamed to a distinct label entirely (freeing "ikee" for the
   other).

## Verify (once ruled)
- Exactly one live def carries the label "ikee," OR the owner explicitly
  accepts the homonym — recorded here either way.
