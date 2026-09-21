# SHRUBLAND_SCRAPNEST_BIRDS_1 — scrap-nest bird-analogs: nest-theft C# + base-stealing candidate

## what is wrong

`COMMISSION_LEDGER_CLEANUP_1`'s arid_shrubland sheet slug
`scrap-nest-bird-analogs-glittering-treasure-nests-steal-from` has no def and
no mechanism. `design/Jawa/worldbuilding/biomes/arid_shrubland.md` §4
"Venomvine — the fortress flora":

> **The scrap nests.** The bird-analogs are scavengers too: they line their
> nests in the vine with glittering scrap — wire, lens-glass, chips of hull —
> beautiful creations, and a treasure worth seeking for a Jawa. Snake-analogs
> feed on the birds and their eggs and are replete here: the treasure has its
> serpent, coiled in the one corridor you both fit. *(Candidate: the birds
> also steal from player bases.)*

The roster's own `new_defs` entry (`rosters/arid_shrubland.json`) tags this
slug's `mechanic_load` as **"C#: nest-theft/scrap-hoard"** — a mechanics ask,
not a pure art/def commission, which is why `COMMISSION_LEDGER_CLEANUP_1`
filed it here instead of building it directly.

## why it matters

Without it, "scrap nests" is prose with nothing backing it: no nest object to
loot, no scrap-collecting behaviour, and the base-stealing candidate (the part
that would make these birds a nuisance as well as a treasure) is entirely
unbuilt. `RSW_TunnelSnake` (built this pass, `COMMISSION_LEDGER_CLEANUP_1`)
already carries the "snake-analog preys on the birds and their nests" half of
the fiction on its own description — this item is the other half.

## the work (not yet scoped in detail — this is a filing, not a design)

- A bird-analog `ThingDef`/`PawnKindDef` (body-donor pick still owed — check
  `design/Jawa/fauna/cast_assignment.csv` and `animal_census.csv` for an
  unclaimed SW bird before inventing anything; `arid_shrubland.md`'s own
  wildAnimals list already carries several flier-interface birds
  — `Whisperbird`, `Convor`, `Porg` — any of which might be the intended
  donor rather than a wholly new species).
- A "nest" object/building the bird builds or is associated with, holding
  scrap loot (glittering scrap — wire, lens-glass, chips of hull) a Jawa can
  raid.
- The nest-theft/scrap-hoard behaviour itself: C#, likely a JobGiver that
  makes the bird collect small-item Things from the map into its nest, mirror
  of vanilla's `JobGiver_ScarabsToObelisk` or squirrel-style hoarding —
  survey the engine before inventing a new pattern.
- The "candidate" base-stealing behaviour (birds raiding a player colony's
  stockpile) is explicitly a *candidate*, not a ruled mechanic — flag it for
  an owner card before building, same caution the tree-guardian slug got
  (`SHRUBLAND_TREE_GUARDIAN_1`), rather than assuming yes.

## Watch out

- Don't reuse `RSW_TunnelSnake`'s or `RSW_ShrublandGiant`'s art/body without
  re-checking `cast_assignment.csv` for whatever donor gets picked — same
  double-booking risk this pass caught for `Klorslug` (claimed by
  `RUT_Greentide`).
- Re-verify currency before building: `infrastructure/artpipe/{done,pending,
  registry.jsonl}` and `src/` for "scrap nest", "glitter bird", "nest theft"
  before queuing any art or writing any C#.
- `DESERT_GLITTER_BIRDS_COMMENSALS_1` (filed this same item's desert-sheet
  partial pass, 2026-09-20/21) is a DIFFERENT bird mechanic — shade-follow
  commensalism, not nest-theft/scrap-hoarding. Don't conflate the two just
  because both are "small birds owed a mechanic."

## what shipped (2026-09-20)

**Built whole, not re-scoped.** The engine survey the item asked for changed
only the SPLIT, not the ambition:

- 🔴 **`JobGiver_ScarabsToObelisk` does not exist** — 0 hits in the decompiled
  1.6 source — and no vanilla animal hoards anything. The closest vanilla gets
  to "an animal made a lootable structure" is `Hive`, which does not haul: it
  SPAWNS insect jelly in place (`CompProperties_Spawner`) and pays out
  `killedLeavings` when smashed.
- ⇒ the nest and its restock are therefore **pure vanilla defs, no C# at all**
  (the Hive pattern, retuned), and only the HAULING is C# — assembled out of
  vanilla's own `Toils_Haul` toils rather than a bespoke carry.

| what | where |
|---|---|
| `RSW_ScrapNestBird` ThingDef/PawnKindDef + 2 eggs | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ScrapNestBird.xml` |
| `RSW_ScrapNest` building, `RSW_HoardScrap` JobDef, `RSW_ScrapHoarderInsert` think-tree insert | `src/RimStarWars/SWBestiary/Defs/ScrapNest/RSW_ScrapNest.xml` |
| `CompScrapHoarder` / `JobGiver_HoardScrap` / `JobDriver_HoardScrap` | `src/RimStarWars/SWBestiary/Source/BeastMechanics/` |
| placeholder nest art (3 PNGs) + its generator | `src/RimStarWars/SWBestiary/art/ScrapNest/gen_scrapnest_placeholder.py` |
| wired into the biome at commonality 0.45 | `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml` |
| Mod Setting `scrapHoardingEnabled` | `RSW_BeastMechanicsSettings.cs` |

**Donor, and the double-booking check that came first:** body/art/flight frames
reskinned from `RSW_Whisperbird` (ours, same mod, complete 4-frame directional
flip-book) under a new defName and an oil-dark retint —
`design/Jawa/fauna/cast_assignment.csv` assigns the *species* `Whisperbird` to
four biomes, so this places no fifth whisperbird; it reuses the ASSET the way
`RSW_TunnelSnake` reused `RSW_Klorslug`'s. Zero new creature PNGs. Currency
re-verified before building: `infrastructure/artpipe/{done,pending}`,
`registry.jsonl` and `src/` hold nothing for "scrap nest", "glitter bird" or
"nest theft" except `RSW_TunnelSnake`'s own description.

**The base-stealing candidate was NOT built**, per the item's own caution: the
job giver refuses anything in a player home area or in any storage, and no Mod
Setting relaxes that. Filed for the owner as `SCRAPNEST_BIRD_BASE_THEFT_1`
(decision, offline) with four shaped options.

**Verification: offline, and that is the whole bar this item set.** Assembly
builds clean (0 warnings, 0 errors, all three new sources confirmed in the
Csc invocation); all three def files validate clean against the live 618-mod
load set (ParentNames resolve, texPaths resolve, the only remaining notes are
the expected "this mod ships its own Assemblies/" Class infos); 69/69
selftests pass; `deploy_custom_mods.py` reports SWBestiary and UtinniPatches
**in sync** with the game folder. Not observed in a running game — the bridge
was taken by the other window mid-task. Successor:
`SCRAPNEST_BIRD_LIVE_VERIFY_1`.

⚠️ **Deploy trap worth keeping:** `deploy_custom_mods.py` FAILED to write
`Assemblies/RimMandrakeBeastMechanicsRSW.dll` with `[Errno 22] Invalid
argument` while RimWorld was running, and reported the mod as not deployed —
but the file is not exclusively locked. A truncating copy (`shutil.copy2`, or
`open(dst,"wb")`) fails; an in-place `open(dst,"r+b")` write followed by
`os.truncate` SUCCEEDS and lands the assembly byte-identical. Without that,
the XML deploys and the DLL does not, which discards `RSW_ScrapNestBird`
whole on the next load (unresolvable comp `Class`) and leaves the biome
pointing at a dead reference.

## criteria

A bird-analog with a real nest-theft/scrap-hoard mechanism ships, OR the
concept is dropped/re-scoped with a one-line reason recorded here. The
base-stealing candidate is either ruled on (owner card) or explicitly deferred
before being built.
