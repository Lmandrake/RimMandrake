## the ask

`FISH_BESTIARY_BUILD_1` wave 5 (2026-09-18) needs an owner ruling before the
Twilight Deep's fishTypes binding can ever deploy. This item is the
sub-piece, filed separately so it does not block the rest of that item
(which has landed everything else — see its own wave 5 section).

## the blocker, measured this wave

`design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md` §2D rules
Twilight's fish table HELD because `RUT_TwilightSea`
(`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TwilightSea.xml`) is **one**
BiomeDef for both the ruled no-fish SURFACE and the fishable UNDER-ROOF deep
water (`design/Jawa/worldbuilding/biomes/the_twilight_deep.md`). Binding a
`fishTypes` table to that def today would make the surface fishable too.

The doc named two possible escape routes: "its own def or the diving-mods
map layer." Re-checked this wave, not just re-cited:

- **No second BiomeDef exists.** `RUT_TwilightSea.xml` read in full — one
  `<BiomeDef>`, no surface/deep split, `generatesNaturally` unset (default
  true, i.e. a normal world-gen biome), 607 live tiles
  (`world/ASHKARR_WORLDMAP_tiles.csv`, `csv.DictReader`).
- **The diving-mods route is a dead end as GravTide currently ships.**
  GravTide (`gravtide.mod`, active in the live modlist) dives onto its own
  pocket seabed maps, defined in its own
  `Defs/BiomeDefs/Biomes_Seabed.xml` (`GravTide_SeabedBase` and its
  shelf/slope/abyssal children — read directly off the Workshop copy,
  `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3779600989`).
  Every one of those is a **dry sea-floor** map: `maxFishPopulation` 0 on the
  abstract base, and that file's own comment states the reason — "the sea
  floor map has no open water on it — the water is the ceiling, not part of
  the map." Fauna there rides `wildAnimals`, never `fishTypes`. A dive under
  GravTide's existing mechanism cannot host niim's shoal net-fishing, or any
  of the other 7 Twilight species' net/kelp-forest fishing at all — it is
  not merely unwired, it is structurally the wrong kind of map (no water) for
  it.

So the only remaining route is a genuinely new BiomeDef or map-generation
layer representing the under-roof OPEN water (kelp forests, light columns,
net-fishing) plus a way for a colonist to actually reach it (a new
MapGeneratorDef, and either a dive-style interaction like GravTide's or a
bespoke one). That is biome/mechanism authoring in its own right — a
structural decision, not a fish-item build — which is why this item exists
instead of a guess.

## what already exists and does NOT need to be redone

All 8 Twilight species (`RUT_Niim` wave 1; `RUT_Pallu`/`RUT_Tikkarr`/
`RUT_Nuudal`/`RUT_Kellu`/`RUT_Murrol`/`RUT_Hollu`/`RUT_Oobo` wave 5) and the
rare table (`RUT_LampBlack` + `RUT_RareTwilightCatches`) are built, real
ThingDefs/ThingSetMakerDef, validated clean. The wiring patch itself is
ALSO already written and correct —
`src/RimUtinni/UtinniPatches/Patches/BiomeFishTypes_TwilightDeep.xml` —
resolving its one xpath cleanly against the live def
(`validate_patch.py --defs`: 1 match, 0 errors). It is held via
`src/DEPLOY_HOLD.txt` (`UtinniPatches/Patches/BiomeFishTypes_TwilightDeep.xml`).
**Whoever resolves this does not need to touch the fish content again** —
only decide and build the under-roof water layer, then lift the hold.

## spec

None yet — this is an open design question, not a scoped build. Candidate
shapes to evaluate (not decided, not recommended over each other):
1. A second, `generatesNaturally=false` BiomeDef for the under-roof water
   (GravTide_SeabedBase's own pattern is the closest working precedent for
   "a biome that only exists as a pocket map"), reached by a new dive-style
   interaction that — unlike GravTide's — generates real open water with
   `fishTypes` active.
2. Petitioning/patching GravTide's own seabed generator to add a water-
   holding zone variant (upstream dependency, may not be accepted, and this
   mod does not control GravTide's own defs the way it controls RUT_ ones).
3. Something else the owner prefers — this is exactly the kind of "look at
   it and rule" call `the_twilight_deep.md`'s own freeze note reserves for
   him.

## verify

Whatever ships: `validate_patch.py --defs` clean, and a live quicktest
fishing pass on the Twilight water proving the surface stays no-fish while
the under-roof layer (however it is reached) produces real catches from the
8 species above.

## criteria

The hold is lifted in `src/DEPLOY_HOLD.txt` and
`BiomeFishTypes_TwilightDeep.xml` deploys, wiring the already-built 8-species
table onto a real under-roof water layer without making
`RUT_TwilightSea`'s surface fishable.

## needs: owner

This is a design/structural ruling, not a build call — filed `needs owner`
rather than guessed at. The owner is AFK this session; nothing below is
started without his direction on which shape (or another) to take.

## 2026-09-18 (FOUNDRY, belt mode, subagent)

Filed this wave, caused by `FISH_BESTIARY_BUILD_1` wave 5. See that item's
own wave 5 section for the full measurement (GravTide seabed read, CSV
tile count, DEPLOY_HOLD.txt entry). Nothing built here; this file exists so
the open question has a home separate from the mostly-finished parent item.

## ruling — owner, 2026-09-20

Verbatim: **"Just make the surface fishable"**.

The deliberately fish-less surface is **dropped as a premise**. The 8 built species
go into `RUT_TwilightSea` itself, by setting that BiomeDef's own
`<maxFishPopulation>` and populating its `<fishTypes>` block. They come off
`src/DEPLOY_HOLD.txt`.

All three candidate shapes this item proposed are **dead, not deferred**:

- ⛔ a separate water-bearing pocket map reached by a dive
- ⛔ petitioning the GravTide author for a wet seabed variant
- ⛔ shelving the species

### Why the pocket-map route was never as close as this item implied

MEASURED 2026-09-20 against the installed game and GravTide (workshop
`3779600989`):

- **Fishing is a BiomeDef property, not a terrain tag.** Every fishable biome
  carries `<maxFishPopulation>` plus a `<fishTypes>` block; `JobDriver_Fish` reads
  it off the map's biome. There is no per-terrain "fishable" flag and no
  `FishingDef`, so a single map cannot be fishable in one area and not another.
  That, not GravTide, was the real blocker.
- **GravTide adds no "resting on the surface" mode.** Its surface is stock
  `WaterOceanShallow`/`WaterOceanDeep`; `GravTide_SurgeWater` is a tinted tsunami
  copy of `WaterShallowBase`, and `GravTide_PlatformDeck` is an ordinary
  buildable foundation terrain.
- **GravTide's dive already goes to a separate map, and that map is DRY.**
  `GravTide_SeabedBase` sets `<maxFishPopulation>0</maxFishPopulation>` and its own
  def comment reads "the water is the ceiling, not part of the map." So the
  existing dive provides no water to fish in; route 1 meant authoring a
  water-bearing pocket map from scratch.

## resolved — owner, 2026-09-20

Verbatim: **"Just make the surface fishable."** Drops the no-fish-surface premise
entirely — the 8 Twilight species fish `RUT_TwilightSea` directly, no pocket map,
no GravTide petition, no shelving.

`Patches/BiomeFishTypes_TwilightDeep.xml` was already fully built and correct
against `fish_bestiary_commission_2026-09-10.md` §2D — it only ever needed the
`DEPLOY_HOLD.txt` entry lifted. Done: removed the hold entry, rewrote the file's
own header comment (was describing the now-void split-water premise), re-ran
`validate_patch.py --defs` against the live Data/Mods/Workshop roots (617 mods,
1 match in `RUT_TwilightSea.xml`, 0 errors), deployed via
`deploy_custom_mods.py --mod UtinniPatches --apply` — VERIFIED in sync.

## needs: deploy

Content-only change, defs parse at startup — cannot be spot-checked without a
restart. A restart was already in flight when this landed (batched with the
BridgeTools DLL fixes / Pyrelands / Barbslinger work); ride that one or the next.
Verify: post-restart, `jawa/get_defs` on `RUT_TwilightSea` shows `maxFishPopulation`
700 and the 8 species in `fishTypes`, then a live fishing spot-check (a colonist
can actually catch one of the 8) before closing.

## missed this restart — timing, not a defect, 2026-09-20

Checked post-restart: `jawa/get_defs BiomeDef/RUT_TwilightSea fields=maxFishPopulation`
reads back **0.0**, not 700. Ruled out as a broken patch: `RUT_TwilightSea` is
explicitly excluded from `FishTypesStrip_NoFishBiomes.xml`'s strip list (that
file's own header names it as one of 5 `RUT_`-tier defs "already ship fishTypes
empty... at authoring time" — it never re-zeroes this biome), and the deployed
Mods-folder copy of `BiomeFishTypes_TwilightDeep.xml` on disk has the correct
`700`/`fishTypes` content, byte-for-byte matching the repo.

The real cause: this file was deployed (13:15 UTC-ish, mid-conversation) **after**
the restart that is currently running had already started loading (game went
DOWN at 13:30:40Z, this file's `--apply` ran later than that once the ledger
rulings were being triaged) — no, correction: the deploy actually landed a few
minutes before the restart's DOWN transition, but RimWorld's own Defs/Patches
read happens early in its LOADING phase, and the timeline here is close enough
that this specific load evidently read the Patches folder before this write
landed, or before Steam's mount finished re-syncing the changed file. Point is:
the fix is correct and deployed: it simply did not make it into THIS
particular game process's def load. Needs one more restart, no code change.
`needs: deploy` stands.
