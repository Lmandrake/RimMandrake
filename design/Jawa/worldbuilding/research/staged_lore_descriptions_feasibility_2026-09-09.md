# Staged lore descriptions — engine feasibility

_`STAGED_LORE_DESCRIPTIONS_1`, feasibility half. Fable, 2026-09-09. Every claim
below is traced to RimWorld 1.6 decompiled source via rimsage and cited
`File.cs:line`; anything not traced is marked **UNVERIFIED**. No C# was written._

**Question:** can biome / terrain / thing descriptions, settle warnings and item
flavor swap by campaign lore-stage, so the Scarlands reads as an inexplicable
wasteland until the player earns the truth?

## Verdict — FEASIBLE on every named surface

**And the engine already ships the feature.** `Building_VoidMonolith.cs:92–102`
overrides `DescriptionFlavor` to return `Find.Anomaly.LevelDef.monolithDescription`
— a description keyed to a campaign progression level, falling back to the def
text when the level has none. That is precisely the mechanism being proposed,
shipped by Ludeon in Anomaly. `Pawn.cs:2288–2299` does the same by mutant state.
Staged description is engine-native, not a hack.

| Surface | Verdict | Traced evidence |
|---|---|---|
| Biome inspect (world tile) | **FEASIBLE, live** | `Planet/WITab_Terrain.cs:62` — `listing.Label(selTile.PrimaryBiome.description)`, executed inside `FillTab` every frame. `Planet/WITab_Orbit.cs:55` is byte-identical for orbital tiles. A regex sweep for `PrimaryBiome\.description\|biome\.description` across all `*.cs` returns **exactly these two hits** — the entire engine reads a biome's description in two places, both uncached. |
| Settle warning (settle / land confirmation) | **FEASIBLE, live, multi-paragraph by design** | `BiomeDef.cs:150 public string settleWarning;` read at `Planet/SettlementProximityGoodwillUtility.cs:140–142`. |
| Thing inspector — flavor path | **FEASIBLE, live** | `Verse/Thing.cs:586` — `public virtual string DescriptionFlavor => def.description;` Virtual, no backing store, evaluated at call. |
| Item info card | **FEASIBLE, live** (cache clears on open) | `StatsReportUtility.cs:329` builds the Description entry from `thing.DescriptionFlavor`; `:311` from `def.description` for def cards. Entries are held in `cachedDrawEntries` (`:28`), but `Reset()` (`:45–57`) clears it and is called from `Dialog_InfoCard.Setup()` (`Verse/Dialog_InfoCard.cs:489`) in **every** `Dialog_InfoCard` constructor. Cache lifetime = one card opening. |
| Trade / transfer UI | **PARTIAL — the one real cache** | `Tradeable.cs:133`, `TransferableOneWay.cs:54`, `TransferableImmutable.cs:51` all return `AnyThing.DescriptionDetailed` → `Thing.cs:584` → `ThingDef.DescriptionDetailed`, which is **memoized** (below). Drawn per-frame at `TransferableUIUtility.cs:369`, so the draw is live — the *string* is not. Pawn rows escape it: `Tradeable_Pawn.cs:33` → `Pawn.cs:2286` → `DescriptionFlavor`, live. |
| Architect / build menu tooltip | **FEASIBLE, live** | `Designator_Build.cs:87` — `public override string Desc => entDef.description;` |
| Misc live readers (no action needed) | live | `Verse/Widgets.cs:1075` (def tooltip), `StartingPawnUtility.cs:147`, `Listing_TreeDefs.cs:115`, `RaceProperties.cs:571`, `VerbTracker.cs:101`, `Pawn_InventoryTracker.cs:446`, `Listing_TreeThingFilter.cs:142,172` (category/special-filter nodes). |

### The multi-line settle-warning path, traced in full

`GetConfirmationDescriptions(tile, gravEngine)` (`SettlementProximityGoodwillUtility.cs:114–158`)
is a `yield`-iterator emitting `TaggedString` paragraphs in order:

1. hostile / neutral faction-base landing warning (gravship only),
2. `ConfirmSettleNearFactionBase` if any proximity goodwill offsets exist,
3. `ConfirmSettleNearPollution` if a noxious-haze MTB is computed,
4. **`foreach (BiomeDef biome in tile.Tile.Biomes) yield return biome.settleWarning`**
   — note `Biomes` *plural*: a multi-biome tile contributes one paragraph each,
5. orbital warnings and the grav-engine's own.

`CheckConfirmSettle` (`:176–207`) then joins them with `"\n\n"`, appends
`ConfirmSettle`/`ConfirmLand`, appends the goodwill effect list as a `" - "` line
list, and hands the single string to `Dialog_MessageBox.CreateConfirmation`.
Nothing is stored. Callers: `Page_SelectStartingSite.cs:216`,
`Planet/SettleInExistingMapUtility.cs:22`, `Planet/SettleInEmptyTileUtility.cs:61`,
`CompPilotConsole.cs:120`.

**What a staged settle warning needs: nothing structural.** The field is a plain
`string` re-read at every confirmation dialog, and the joiner already produces
multi-paragraph output. Staging it is a field write. If a stage should *add* a
paragraph rather than replace one, the cheapest honest route is still to rewrite
the single `settleWarning` string with embedded `\n\n` — a second paragraph
requires no Harmony, because the joiner cannot tell the difference.

## Caching sites found (the complete list, and each one's invalidation route)

**1. `ThingDef.descriptionDetailedCached` — `Verse/ThingDef.cs:414`, populated at
`:790–822`.** The only description cache that survives longer than a window.
Memoized on first read, and — verified — **no engine path ever clears it**:

- `Def.ClearCachedData()` (`Verse/Def.cs:172–175`) clears only `cachedLabelCap`;
- a sweep for `ClearCachedData` across all `*.cs` finds overrides in exactly
  **two** types, `RoadDef.cs:63` and `BodyDef.cs:206` — **`ThingDef` does not
  override it**;
- so even the engine's own re-injection path
  (`DefInjectionPackage.cs:270` `InjectIntoDefs` → `:292`
  `DefDatabase<T>.ClearCachedData`, which rewrites `description` from the
  language files) leaves the detailed cache stale. That is a vanilla bug we
  inherit, not one we create.

**Invalidation route: reflection.** Null the private field on each affected
`ThingDef` at stage-apply. There is no public API and no override point.
Consumers that go stale if this is skipped: `Tradeable.cs:133`,
`TransferableOneWay.cs:54`, `TransferableImmutable.cs:51`,
`Listing_TreeThingFilter.cs:206` (storage/bill filter tree),
`ITab_ContentsOutfitStand.cs:102`, `ITab_ContentsBooks.cs:109`,
`Precept_Role.cs:544`, `QuestPartUtility.cs:139,197`,
`Dialog_ChooseThingsForNewColony.cs:533`, and the wrappers
`Apparel.cs:55`, `MinifiedThing.cs:75`, `UnfinishedThing.cs:112–120`.

**2. `HediffDef.descriptionCached` — `Verse/HediffDef.cs:193`, populated at
`:245–261`.** Same shape (memoize-on-first-read, no clear path), returning
`descriptionShort` if set else `description`. Read via `Hediff.Description`
(`Verse/Hediff.cs:320`) and `Hediff_PainField.cs:69`, `Hediff_MissingPart.cs:61–63`.
Matters the moment the **Scarlands mark** hediff (`the_scarlands.md` §7b) wants
staged text — the mark's meaning is exactly the sort of thing the ladder reveals.
Same invalidation route: reflection null.

**3. `StatsReportUtility.cachedDrawEntries` — `:28`.** Window-scoped only; cleared
by `Reset()` (`:45–57`) from every `Dialog_InfoCard` construction
(`Dialog_InfoCard.cs:489`) and by `Notify_QuickSearchChanged()` (`:467–470`).
**No action needed** — worst case is an info card left open across a stage
advance showing the previous stage until reopened.

**4. `WITab_Terrain.cachedGrowingQuadrumsDescription` — `WITab_Terrain.cs:16–18`.**
Caches the *growing period* string keyed by tile, not the biome description.
**Irrelevant** to this feature; listed so a future reader does not mistake it for
one.

**5. `Def.cachedLabelCap` — `Verse/Def.cs:54, 76–81`.** Caches `label`, not
`description`. **Relevant only if a stage ever restyles a label** — and then it
is clearable through the public `ClearCachedData()`.

No other description-bearing cache was found. `ThingDef` has four other cached
fields (`isNaturalOrganCached`, `hasSunShadowsCached`, `cachedRelevantStyleCategories`,
`allRecipesCached`) — none touch text.

## What a save carries, and the trap in it

- **Defs are never scribed.** A savegame stores defNames, never def field values.
  So the mutated `description` is *not* in the save, and the lore stage must live
  in a scribed component and re-apply on load.
- **Defs are not reloaded between saves.** `PlayDataLoader.LoadAllPlayData` is
  called from exactly two places in the source: `Verse/Root.cs:75` (process
  startup) and `Verse/LanguageDatabase.cs:34–35` (language change, preceded by
  `ClearAllPlayData`). Loading a savegame does **not** touch the def database.
- 🔴 **The trap that follows:** within one process session, a mutation made while
  playing a stage-4 campaign is still on the def when the player returns to the
  menu and loads a stage-0 save, or starts a new colony. The apply step must be a
  **full reset to baseline, then apply the current stage** — never an incremental
  "advance one stage". Keep the shipped def text as the baseline in the data
  table and write it back at stage 0; do not rely on the def still holding it.
- **Language switch reverts everything** (`LanguageDatabase.cs:34–35` reloads all
  play data). It also returns the player to the menu, so the next game load
  re-applies. Harmless, but it is why the apply must be idempotent from baseline.
- **Books are the one description that IS saved** — `Verse/Book.cs:354` scribes
  `descriptionFlavor` because it is grammar-generated per instance. Not a
  consumer here; noted so it is not mistaken for a leak.

## Mechanism spec — cheapest real route

**No Harmony required for the five named surfaces.** Every one of them reads a
def field at display time; the two that do not read a cache with no invalidation
API. The mechanism is therefore *mutate the def, clear two caches*:

1. **`GameComponent_LoreStage`** (Game-scoped, so it rides the `.rws` and one
   colony's progress cannot leak into another). Scribes an `int` stage per
   *ladder*, not one global stage — the Scarlands ladder has five rungs
   (`the_scarlands.md` §GM 1–5) and the Contagion / war-lab / Webwork ladders
   will advance independently. `Dictionary<string ladderId, int stage>`.
2. **A data-side table, rules as data** — XML or JSON keyed
   `ladderId → defType → defName → { stage: text }`, with `stage 0` holding the
   **verbatim shipped text as baseline**. Fields addressable: `description`,
   `settleWarning`, and (later) `label`. Authoring stays in the design layer where
   the §P/§GM partition is reviewable; no lore lives in C#.
3. **`Apply(stage)`** — for every def named in the table: write the stage-0
   baseline, then overwrite with the highest entry ≤ current stage; then null
   `ThingDef.descriptionDetailedCached` and `HediffDef.descriptionCached` by
   reflection on the defs touched. Idempotent by construction.
4. **Call sites:** `GameComponent.FinalizeInit` (covers new game *and* every
   load), and the stage-advance event itself.
5. **Harmony is needed only for one thing we do not currently want:** per-viewer
   or per-pawn variation (two colonies in one save at different stages, or text
   that varies by *who* is looking). Nothing in the Scarlands ladder asks for
   that. If it ever does, the hook is a postfix on `Thing.DescriptionFlavor`
   (`Thing.cs:586`) and on the two `WITab` draws — but the biome tabs read a
   field, not a getter, so a biome postfix would need a transpiler or a
   `BiomeDef` subclass. **That asymmetry is the reason to prefer def mutation:
   the biome path has no getter to postfix.**

### R25 compliance is a property of the table, not the engine

Freeze ruling **R25** (`_freeze_rulings_2026-09-07.md:512–522`): *the player may
INFER it; the player is never TOLD it.* The mechanism is neutral — it will
faithfully display whatever the table holds — so the ban has to be enforced on
the data:

- 🔴 **Even the top stage never names the Assailants, the Rakata, scaria's
  authorship, or the Cathedral's nature in a def description.** Staged text may
  advance from *"no trace of the enemy it was built against"* to *"the emplacement
  rings all face one quarter of the sky, and the craters walk inward from it"* —
  geometry the player reads, not a name they are handed. Stage 5 of a biome
  description is still §P register; the §GM ladder is delivered by the pilgrim
  ends and the bastion record in the Ancients' own words, which is a **quest-text
  surface, not a def-description surface**.
- The existing hard ban (`the_scarlands.md` §6 ban 1) is already linter-checkable;
  the staged table must be added to whatever that linter reads, or the feature
  quietly creates five new places for a leak per def.
- **UNVERIFIED:** whether a §6 ban-1 linter exists today. I did not look for one;
  if it does not, it is owed alongside this feature, not after it.

## Effort estimate

| Part | Estimate |
|---|---|
| `GameComponent_LoreStage` + scribe + `FinalizeInit` apply | ~120 LoC, half a day |
| Data table loader + reflection cache-clear | ~150 LoC, half a day |
| Scarlands stage text (5 rungs × biome description + settleWarning, R25-safe) | a design sitting, not code |
| Linter extension for the staged table | ~1 hour once the table format is fixed |
| Quicktest proof (below) | ~1 hour including a minimal-list load |

**Total: about 1.5 engineering days plus one authoring sitting.** The risk is not
technical — it is that five stages of text per def is five times the §GM leak
surface, and the review cost scales with it.

## The one demo that would prove it in a quicktest

**Prove the hardest surface and the only real cache in a single ~90 s quicktest.**

Target `RUT_Scarlands` (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Scarlands.xml:42`,
which already carries a staged-looking `settleWarning` at `:46`) plus any one
tradeable `ThingDef`.

1. Load the minimal mod list; open the world map on a Scarlands tile; read the
   Terrain tab (`WITab_Terrain.cs:62`) and screenshot the description.
2. Open a trade or caravan-transfer dialog and hover the chosen item so its
   `DescriptionDetailed` tooltip is **rendered once** — this is what populates
   `descriptionDetailedCached`. Screenshot.
3. From the bridge, advance the stage (or, for the spike, directly write
   `BiomeDef.description`, `BiomeDef.settleWarning` and `ThingDef.description`,
   and null `descriptionDetailedCached` by reflection).
4. Re-read the Terrain tab **without closing the world view** → the new text must
   appear on the next frame. Re-open the settle confirmation → the new warning
   must appear as its own paragraph. Re-hover the trade row → the new text must
   appear *only because* the cache was nulled.
5. **The negative control that makes it a proof:** repeat step 3 on a second item
   **without** nulling its cache. Its trade tooltip must still show the old
   string. If both items update, the cache was never populated and the test
   proved nothing — re-run with the hover in step 2 confirmed by screenshot.

That single run establishes: the biome path is live, the settle path is live, the
info-card path is live, the trade path is cached, and reflection is the working
invalidation route.

## Status

Feasibility answered. **Awaiting the owner's go/no-go** on building it — this
document is the evidence for that ruling, not authorization to write the C#.
