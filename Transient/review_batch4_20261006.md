# Review batch 4 — 2026-10-06

Offline full-file review. Engine facts checked with RimSage (Pawn.Kill, ThingWithComps.Kill,
FactionGenerator.NewGeneratedFaction, Faction.TryMakeInitialRelationsWith, Listing).

## Droidworks (721e81866, mindstone head): 7 files CLEAN, marked clean
- DroidAssembly, Recipe_AssembleDroid, Recipe_DWMemoryWipe, CompDWDataSpike, Recipe_DWFormat,
  CompDWHeadDropper, DroidworksDefOf.
- Kindled path: KindleMindstoneMind runs after SpawnDroid, so the spawn-time EnsureTier comes
  first and Sapient wins. EnsureTier is idempotent on load. The marker is a plain
  HediffWithComps, so it saves with hediffSet. It is isBad=false and nothing in the mod removes it.
- Immunity: wipe and format both return before touching the pawn. The spike gets refused and
  the item is still consumed (JobDriver finish action), as designed.
- Drop on death: ThingWithComps.Kill calls comp.Notify_Killed for every death, dinfo null
  included. prevMap is read before Pawn.Kill nulls it, and the hediff is still present at that
  point. A death in a caravan (no map) drops nothing, same as every other head.
- Null defs: both mindstone defs ship in Droidworks' own XML, so DefOf resolves them.
  IsMindstoneMind is null-safe. Minor and not fixed: if only the hediff def went missing,
  KindleMindstoneMind would call AddHediff(null).
- Observation, not a bug (true of all heads): resurrecting a droid corpse after its head
  dropped duplicates the head. For the mindstone that duplicates a 2500-silver archotech item.

## FeverWood RM_MapComponent_TwoFrontLure (58351a233): CLEAN, marked clean
- A scheduled second wave is saved as an absolute tick + defName + origin. On fire, the
  feralisk or skreth defName gets re-resolved to whichever is loaded, and a missing def is
  dropped quietly.
- Relations: NewGeneratedFaction → TryMakeInitialRelationsWith adds the relation on BOTH sides.
  All three FactionDefs are permanentEnemy, so each is hostile to the player and to the others.
- Null lookups are guarded. The faction cache checks that a faction is still in FactionManager,
  so a stale entry from another game is skipped.

## Webwork RM_WebworkMod (scroll fix): FIXED, not marked (uncommitted)
- BUG: lastContentHeight starts at 0, so on the first frame the view height is the window
  height. Listing.NewColumnIfNeeded then wraps the overflow into an off-screen second column
  and resets curY. CurHeight never gets past the window height, so the view never grows: the
  lower sections stayed unreachable and the scroll fix did nothing.
- Fix: `maxOneColumn = true` on the Listing_Standard. Rebuilt (winbuild OK, 0 warnings).
  Re-reviewed with no other findings.
- Same pattern, not touched (others' files): the sibling settings screens that self-measure
  CurHeight start with a big seed (1200–2000 px), which avoids this as long as the content fits
  inside the seed. Any that seed 0 have the same bug.
