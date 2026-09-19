# LIVESTOCK_STARTER_TRIO_1 — onnik + karrask + moornak, shared-art batch

Green-lit from `design/Jawa/proposals/ludicrous_livestock_deep_design.md`
(owner, 2026-09-01). The doc's own v1 is the PAIR (onnik + karrask — zero new
job types, shared art base); the owner asked for a trio, so moornak rides as
the third IF it needs no new job type (its comp is passive) — drop to the pair
rather than invent a job. Everything else in the doc waits for
PROPOSAL_SUITE_REVIEW_1.

## spec

Per the doc's rosters and §7.2 shared-art batching:
1. **Onnik (kiln-belly)**: feed-cycle industrial — fed clay/raw ceramic input,
   fires it in its gut, yields ceramic product on a cycle; chokes or fires
   cold when mis-fed (the doc's mis-feed failure states). Extends the proven
   urrak/vokka single-input template. Its fired ceramic is the cuisine doc's
   sand-oven cookware — keep the product def name generic enough to share.
2. **Karrask (molt-plate)**: harvest-on-schedule — sheds carapace plates on a
   molt cycle; plates are an armor/crafting material. Standard shear-like
   harvest job, no new job code.
3. **Moornak (grief-eater)**: passive aura comp — visibly eases mourning
   (mood buff to grieving pawns in radius) while SECRETLY storing every
   debuff absorbed; on death, releases the entire backlog onto the colony.
   The hidden ledger is scribed (survives save/load). No new job type.
   ⚠️ The secret must be genuinely invisible in the inspect pane — the dread
   is the design; a visible counter kills it.
4. All three: role-band sizes per the doc, tameable, tradeable, RimStarWars
   tier; sprites via `generating-rimworld-sprites` contract (128 px/cell,
   chroma-key alpha, silhouette-first), beast-normalization spirit (born
   normalized, no retrofit).

## owner art rulings (2026-09-01)

Onnik = option 2 · karrask = option 2 · moornak = option 3. Kept files and the
full table: `src/RimStarWars/Livestock/art/mockups/PICKS.md`. Three rejects were
PROMOTED, not dropped: karrask opt 3 → its own new creature; moornak opts 1+2 →
"other crag creatures" (owner's term, family undefined) — each needs a design row
before any build; none belongs to this item.

## verify

Quicktest: spawn/tame each; (a) onnik full feed→fire→product cycle plus one
mis-feed failure observed; (b) karrask molt yields on schedule and the plate
is craftable-with; (c) moornak buffs a grieving pawn, then its death releases
the stored backlog (dev-kill after accumulation; MEASURED debuff count in =
count out); (d) save/load round-trip keeps moornak's hidden ledger; (e) art
passes the offline validator per facing before any game load.

## criteria

Three creatures live in a quicktest with full cycles observed; zero new job
types shipped; shared-art batch discipline held (one body base reused);
Player.log clean.

## Watch out

- Animal product comps: `CompHasGatherableBodyResource` covers karrask;
  onnik's feed-specific input needs a custom comp — keep it one comp, data-
  tuned, so drassik (v2) reuses it.
- Moornak's death-release must fire on ANY death path (slaughter, violence,
  age) — hook the death notify, not the slaughter job.
- Trainability/wildness numbers decide tameability at spawn — the census
  trap: a spawned "tame" test animal may substitute silently; verify the
  actual kind spawned (see census memory).

## 2026-09-02 — scoping pass, nothing written (FOUNDRY, background fanout)

0% built: no ThingDefs/PawnKindDefs/sprites for onnik/karrask/moornak exist
anywhere in the repo, only design-doc rosters and owner-picked mockup PNGs.
`src/RimStarWars/Livestock/` (`mandrake.rsw.livestock`) is currently
entirely occupied by the sibling item `FORSAKEN_CRAGS_PREDATORS_BUILD_1`'s
content (Cindermare/Skarnix) — no defName collision found (grepped for
Onnik/Karrask/Moornak across `src`, empty), but this item and
`FORSAKEN_CRAGS_PREDATORS_BUILD_1`/`HELIX_TELLUROX_BUILD_1` would share one
mod package, which needs a naming/ownership call rather than a guess.

Also: the design doc's own spec claims onnik "extends the proven
urrak/vokka single-input template" — checked, urrak/vokka have zero
implementation anywhere in `src`. Onnik's feed-cycle/cold-fire-failure
mechanic needs a genuinely new custom `ThingComp`, not a reuse; not the
small increment the spec's own framing suggested.

**Two open questions, needs owner/BENCH before building moornak:**
1. This item's own spec text (simple mood-buff + hidden ledger +
   release-on-death) doesn't match a materially richer, LATER owner ruling
   in the design doc's "RULED — owner sitting" table (same date,
   2026-09-02): self-tames readily, arrives pre-loaded with grief, a
   negative colony-wide "unsettled" hediff, 30-day release duration,
   triggers manhunter on release, sells but never buys back, must be
   trapped/abandoned. Unclear whether the later ruling supersedes this
   item's spec or belongs to a still-deferred review pass.
2. Shared-mod-folder ownership with `FORSAKEN_CRAGS_PREDATORS_BUILD_1` (see
   above) — needs a naming decision before any file gets written into that
   directory.

Smallest safe next increment once unblocked: karrask alone, XML-only
(`CompHasGatherableBodyResource` for the molt-plate harvest per the owner's
2026-09-02 ruling — "tough material like chitin, easy to work, not pretty,"
NOT wearable armor), additive-only filenames, ~1 hour. Onnik's comp is a
separate half-day pass. Final sprite art stays deferred per the doc's own
palette-pass sequence.

## 2026-09-02 — karrask built (concurrent collision), onnik/moornak still 0/3

**Karrask is now structurally built** (`Defs/ThingDefs_Animals/ThingDefs_Karrask.xml`,
`Defs/PawnKindDefs/PawnKindDefs_Karrask.xml`, `Defs/RecipeDefs/RecipeDefs_Karrask.xml`
— all currently untracked, not yet committed by whoever wrote them): natural
armor via ArmorRating stats, a `WorkToMake` stuff-property factor for
"easy to work," a Crafting-gated cure recipe at tailoring benches.
`validate_patch.py` clean except 6 expected `texPath` errors (no production
sprite yet, only the owner-picked mockup). ⚠️ **A FOUNDRY-dispatched agent
independently building the same karrask defs collided with whoever wrote
the files above** — two workers targeted this item's same files at the same
time; the agent's own content was overwritten mid-pass and it correctly did
not revert the surviving (more complete) version, only removed one
now-orphaned file of its own that would have duplicate-defName-collided
(`ThingDefs_Items/ThingDefs_KarraskMaterials.xml`, never committed, no repo
history to worry about).

**Onnik's next increment, scoped**: a new custom `ThingComp` for the
3-dose kiln-cycle feed mechanic (spaced doses over a day, cools/resets if
underfed >1 day, mis-feed produces cracked/worthless ceramic) — one new
comp, no new job type, follow this mod's existing comp-authoring pattern
(`CompLightAversion.cs`). Medium build, roughly comparable in size to
karrask's own pass.

**Moornak stays blocked** on the same scope question raised above (this
item's spec vs. the design doc's later, materially richer owner ruling) —
not re-litigated here, still needs a call before anyone writes code for it.

## 2026-09-09 — onnik built and offline-verified; 2/3, moornak still the gap (FOUNDRY, BELT, offline)

Game was mid-cold-load all pass (bridge confirmed FREE via `rimflow bridge who`
but never taken — this item's own scope is offline defs/art/C#, per the
dispatching note). Read the item and the design doc's onnik section
(`ludicrous_livestock_deep_design.md` "Onnik - the kiln-belly") before
writing anything, per the standing instruction to check what's already
built.

**Karrask (re-verified, one real fix):** defs, art (256x256, real alpha,
visually matches the owner's pick) and RecipeDef were already fully built
and shipped (commits `1931db8e`, `83c215e8`, `ba4fadec`, `42166e1a`, plus
the asymmetric-claw and code-review passes since) — did NOT re-author.
Found one real defect while reading the mechanism: `statBases/Mass` was
hand-set to 36 (bodySize 0.6 x the spec's 60 kg/bs convention,
pre-computed), but the `Mass` StatDef carries `StatPart_BodySize`
(confirmed via RimSage `read_csharp_symbol`: `TransformValue` does
`val *= bodySize`) - so a pre-multiplied 36 was landing at an ACTUAL
21.6 kg (36 x 0.6), not the intended 36. Fixed to the vanilla flat
`<Mass>60</Mass>` (matching 1,019/1,022 vanilla animals per
`beast_normalization_spec.md`), letting the engine's own multiplication
produce the correct 36 kg. `validate_patch.py --live` clean except the
two already-known `Things/Item/Resource/Leather` texPath lines, confirmed
false positives this pass by cross-checking vanilla `Leather_Plain`'s own
ThingDef via RimSage (identical texPath, real vanilla asset-bundle art,
not a loose file the validator can see) - not a defect, a validator blind
spot already on record.

**Onnik (built this pass, 0 -> fully offline-verified):** the doc's other
v1 entry (owner card 2026-09-02: "The ceramic should be an art material
that makes beautiful bricks, art pieces, etc."). Built:
- `Defs/Livestock/ThingDefs_Animals/ThingDefs_Onnik.xml` -
  `RSW_KilnClay` (feed), `RSW_FiredCeramicware` (good batch, a real Stuff
  off `StoneBlocksBase` per the owner's art-material ruling - positive
  Beauty, kept generically named so the cuisine mod's sand-oven cookware
  can share it later), `RSW_CrackedCeramicShards` (mis-feed junk), and
  `RSW_Onnik` itself (`AnimalThingBase`, `QuadrupedAnimalWithHooves`,
  bodySize 1.1 via beast_normalization Law 1 off a 2.0 drawSize).
- `Defs/Livestock/PawnKindDefs/PawnKindDefs_Onnik.xml` - same
  Graphic_Single-per-lifeStage shape as karrask's own.
- `Source/Livestock/CompKilnBelly.cs` - new `CompKilnBelly` (on the
  animal) + `CompKilnFeed` (on the feed item), wired through the real
  vanilla `Thing.Ingested` -> `ThingComp.PostIngested` hook (same pipeline
  `CompDrug` uses, confirmed via RimSage `search_source`/
  `read_csharp_symbol`, not guessed). All three doc numbers (3 spaced
  doses over a day, underfed-a-day cools the kiln, ~4 days between
  batches) are the class's own defaults; the two judgment calls the doc's
  prose doesn't pin down (what counts as "a single dump" vs "spaced," and
  that onnik's diet is NOT clay-exclusive this pass) are written into the
  file's own header, not hidden. Zero new job types - firing spawns
  product beside the animal via `GenPlace.TryPlaceThing`, the same call
  this mod's own `CompDWPartDropper` already uses.
- Fixed a real build-path bug found while building: the csproj's
  `OutputPath` (`..\Assemblies\`) and its own header's build-invocation
  comment both still named the PRE-MOVE `src/RimStarWars/Livestock/`
  layout from before the "Sprint wave A" fauna-to-SWBestiary move
  (`247cd6d4`) - every build since that move had been landing the DLL at
  `Source/Assemblies/`, which nothing deploys, never touching the real
  `SWBestiary/Assemblies/RimMandrakeLivestockRSW.dll` the game loads.
  Fixed to `..\..\Assemblies\`; rebuilt with
  `"%USERPROFILE%\.dotnet\dotnet.exe" build` and confirmed by file mtime
  that the fix landed the new DLL beside `JawaIkee.dll` at the mod root
  this time, not the stray `Source/Assemblies/` (deleted, was untracked).
- Art: chroma-keyed the owner's already-picked `onnik_opt2.png` mockup
  (clean key, zero fringe measured), cropped to its alpha bbox, scaled and
  centered onto a transparent 256x256 canvas (matching the 2.0 drawSize /
  128px-per-cell target). `validate_sprite.py --describe`: canvas 256x256,
  real alpha, 0 corners solid, 30.6% coverage, 0.28% fringe (negligible,
  the smoke-wisp's soft edge). Looked at the composited result directly -
  reads clearly as the picked design (tortoise-shell kiln-brick seams,
  chimney vent, heat-shimmer smoke) at both generation and thumbnail size.
- `validate_patch.py --live` clean except the two already-known
  `Things/Item/Resource/Leather` / `Things/Item/Resource/StoneBlocks`
  texPath lines (same confirmed-vanilla-asset-bundle false positive as
  karrask's own, checked against `BlocksSandstone`/`BlocksGranite`'s real
  use of that exact path).
- NOT live-verified (no bridge call made - the game was mid-cold-load all
  pass, per this item's own dispatch constraint and karrask's own
  precedent). The verify section's onnik checks (feed-cycle, mis-feed,
  cold-kiln reset) are still owed to whoever next holds the bridge free.

**Moornak: still the one open gap, unchanged from 2026-09-02.** Did not
build it and did not resolve the scope question myself - this item's own
spec (simple mood buff + hidden ledger + release-on-death) genuinely
conflicts with a later, richer owner ruling recorded in the design doc's
"RULED — owner sitting" table (self-tames readily, arrives pre-loaded with
grief, a colony-wide "unsettled" hediff, 30-day release duration, triggers
manhunter on release, sells but never buys back, trap/abandon only) - and
that table's own summary line does NOT list moornak among the rows
"delivered and RULED ON" (only drassik/duskhide/coo'la accepted, grubbin
cut), so it is genuinely unclear whether that richer text is a live ruling
or a still-deferred PROPOSAL_SUITE_REVIEW_1 row. Building the richer
version unilaterally would be inventing scope no one has actually ruled;
building the item's own simpler version would risk contradicting an owner
ruling that already exists in writing. Needs an explicit owner/BENCH call
naming which spec ships, not another pass guessing at it.

**Verdict: item stays in `doing`.** 2 of 3 creatures fully built and
offline-verified (karrask re-verified + one real fix, onnik built new);
moornak is the sole remaining gap and it is a decision gap, not a build
gap - closing criteria (all three creatures, full cycles observed) is not
met. Whoever picks this up next: the moornak scope call is the one thing
standing between this item and FOUNDRY closing it.
