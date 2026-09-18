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
