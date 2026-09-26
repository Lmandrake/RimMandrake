# Lantern Deeps — art jobs owed

**CAVERNS_PARITY_BUILD_1, filed 2026-09-18.**

Owner ruling that produced this file (2026-09-18, on
`caverns_replacement_scoping.md` §5 decision 1 — *copy or restyle?*): **restyle.**
The donor's textures are **not** copied. Every texture below is **regenerated to
the crystal-caverns sheet's blue-on-black palette**
(`design/Jawa/worldbuilding/biomes/the_lantern_deeps.md` §9: *"a blue lantern
burning under the mountain, and a dead miner's suit walking toward it"* —
lanternstone blue as the only ambient, fungal grey and green, facets/geodes/
lattices as the silhouette language).

🔴 **Until these land, every def below renders as the missing-texture magenta
square. That is EXPECTED and is not a bug to chase.** The defs are written
against the new `RM_LanternDeeps/...` paths on purpose; pointing them back at
`BMT_Caverns/...` would re-couple the mod to the donor it exists to retire.

⚠️ **Canvas sizes are MEASURED from the donor PNGs** (`python3` PNG IHDR read,
2026-09-18, workshop `2969748433`), so a regenerated sprite drops into the same
`drawSize` without any def change. Where a def sets `drawSize` larger than the
canvas the canvas still governs resolution — do not shrink these.

⚠️ `Graphic_Random` paths are **folders**. The file count per folder is the
variant count and is not optional: a folder with fewer files than the donor had
simply has less variety, but a folder with **zero** files renders magenta.

---

## 1. Terrain — 1 job

| # | texPath | canvas | files | subject |
|---|---|---|---|---|
| 1 | `RM_LanternDeeps/Terrains/Lanternstone` | 1024×1024 | 1 (`Lanternstone.png`) | Tiling cave floor of fractured blue crystal shelf. Near-black matrix with pale blue facet planes catching an unseen light from below; value range kept low so a colonist sprite reads on top of it. Must tile seamlessly and must not read as ice. |

## 2. Natural walls — 3 jobs

| # | texPath | canvas | files | subject |
|---|---|---|---|---|
| 2 | `RM_LanternDeeps/Things/Natural/Linked/lanternstone_wall_atlas` | 2048×2048 | 1 | Linked-wall atlas (same cell grid as the donor's `crystal_wall_atlas`, which this replaces 1:1). Rough natural lanternstone: black rock shot through with blue crystal veins that brighten toward broken faces. |
| 3 | `RM_LanternDeeps/Things/Natural/Linked/smoothedlanternstone_wall_atlas` | 2048×2048 | 1 | Same atlas grid, polished: flat blue facets, mirror highlights, the veins now continuous bands rather than broken ones. |
| 4 | `RM_LanternDeeps/Things/Natural/Linked/lanternstone_wall_icon` | 64×64 | 1 | Build-menu icon for `RM_BuiltLanternstoneWall`. One wall segment, blue-on-black, legible at 64px. |

## 3. Lanternstone formations — 4 jobs

Four sizes, all glowing, all volatile except the sowable line (§4). Silhouette
language: **facets, geodes, lattices** — a cluster of angular blades rising from
a geode base, never a rounded gem.

| # | texPath | canvas | files | subject |
|---|---|---|---|---|
| 5 | `RM_LanternDeeps/Things/Crystals/LanternstoneSmall` | 256×256 | 3 (`A`,`B`,`C`) | Ankle-high cluster of 3–5 blue blades on a dark geode crust. Drawn at `drawSize 1.0`, so it must read at one tile. |
| 6 | `RM_LanternDeeps/Things/Crystals/LanternstoneMedium` | 256×256 | 3 (`A`,`B`,`C`) | Waist-high fan of blades, 2×2 footprint, `drawSize 3.0`. Brightest core near the base; tips near-white. |
| 7 | `RM_LanternDeeps/Things/Crystals/LanternstoneLarge` | 384×384 | 2 (`A`,`B`) | Person-height spire group, 3×3 footprint, `drawSize 5.0`. Internal glow strong enough to be the room's light source. |
| 8 | `RM_LanternDeeps/Things/Crystals/LanternstoneHuge` | 512×512 | 2 (`A`,`B`) | Building-sized crystal mass, 5×5 footprint, `drawSize 7.0`, impassable. 🔑 Read the lore: *large enough that a smaller crystal could break off from it* — it is a **parent**, so show at least one near-detached blade at a cleave line. |

## 4. Sowable lanternstone — 1 job

| # | texPath | canvas | files | subject |
|---|---|---|---|---|
| 9 | `RM_LanternDeeps/Things/Crystals/LanternstoneSowableImmature` | 256×256 | 1 | Immature stage for `RM_Lanternstone_Sowable`. A single low blue shoot, barely faceted, dim. The grown stage reuses job 6's folder. |

## 5. Items and chunks — 3 jobs

| # | texPath | canvas | files | subject |
|---|---|---|---|---|
| 10 | `RM_LanternDeeps/Things/Item/Lanternstone` | 256×256 | 3 (`A`,`B`,`C`) | `Graphic_StackCount` set for the raw material: cut blue blocks, increasingly large piles. Faintly self-lit. |
| 11 | `RM_LanternDeeps/Things/Chunks/LanternstoneChunk` | 256×256 | 4 (`a`–`d`) | Rubble chunk of blue crystal in black matrix, four silhouettes. Should read as a chunk, not a gem. |
| 12 | `RM_LanternDeeps/Things/Item/Crops/PufferTendrils` | 256×256 | 1 | Harvested crop item for `RM_PufferTendrils`: a small heap of cut fungal tentacles, finger-length, grey-blue, a few curled as if still moving. One of the few non-crystal things down here; must read as food at inventory scale. Job `twitchingpuffer_tendrils_v1` (DEEP_FLORA_RENAME_1). |

## 6. Cave flora — 11 jobs

Palette note for this whole section: the sheet gives the flora **fungal grey and
green** against the blue ambient, with the glowing species pushing cyan. They are
the crystals' *pasture*, so they should read as soft and organic beside the hard
faceted crystal art.

| # | texPath | canvas | files | subject |
|---|---|---|---|---|
| 13 | `RM_LanternDeeps/Things/Plant/Mycelium` | 512×512 | 3 (`A`,`B`,`C`) | Ground-cover mat of pale filaments, `maxMeshCount 4`, `visualSizeRange 0.2~0.4` — mostly texture, almost no silhouette. Grey-green, very slight bloom. |
| 14 | `RM_LanternDeeps/Things/Plant/ZivvitTaper` | 128×128 | 2 (`A`,`B`) | Zivvit taper: narrow mushroom with a long glowing cap tip. `drawSize 2.0` at a small canvas — keep it simple and bright at the tip only. |
| 15 | `RM_LanternDeeps/Things/Plant/QuorrFern` | 128×128 | 4 (`A`–`D`) | Quorr fern: bush-sized fern/mushroom symbiosis: fern fronds rising from a fungal base. Grey-green, no glow. |
| 16 | `RM_LanternDeeps/Things/Plant/OsskBramble` | 128×128 | 2 (`A`,`B`) | Ossk bramble: tangled thorny shoots with **crystalline tips** — leaves grey-green, thorn tips blue and faceted. The one place flora and crystal meet. |
| 17 | `RM_LanternDeeps/Things/Plant/BrellikBulb` | 128×128 | 2 (`A`,`B`) | Brellik bulb: squat bulbs with brightly glowing tips. 🔑 Glow colour here is **warm amber** `(252,187,113)`, not blue — deliberate contrast against the ambient; keep it. |
| 18 | `RM_LanternDeeps/Things/Plant/TwitchingPuffer/PufferGrown` | 256×256 | 1 (`a`) | Twitching puffer, grown: a single swollen grey-blue fungal ball on a stubby foot, taut and faintly translucent as if inflated, ringed on its upper half by a fringe of short finger-like tentacles caught mid-twitch. The ball is a **rounded** organic form — the one exception to the no-rounded-gems rule; crystal language stays in the background veins only. No face, eyes or mouth. Job `twitchingpuffer_grown_v1`. |
| 18b | `RM_LanternDeeps/Things/Plant/TwitchingPuffer/PufferImmature` | 256×256 | 1 (`a`) | Same fungus young: fist-sized ball, dull and wrinkled, not yet inflated, tentacle nubs as bumps; smaller silhouette inside the same footprint. Job `twitchingpuffer_immature_v1`. |
| 18c | `RM_LanternDeeps/Things/Plant/TwitchingPuffer/PufferHarvested` | 256×256 | 1 (`a`) | Same fungus after harvest: ball intact but sagging, half-deflated, tentacles cut to stubs; nothing broken open (`leaflessGraphicPath`). Job `twitchingpuffer_harvested_v2` (v1 rendered a wrapped cocoon, content miss). |
| 19 | `RM_LanternDeeps/Things/Plant/ThrakkCap` | 256×256 | 2 (`A`,`B`) | Thrakk cap: mushroom **tree** with a crystal-plated cap. Woody trunk, cap faceted and faintly blue. Must read at tree scale. |
| 20 | `RM_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceGrown` | 256×256 | 3 (`A`,`B`,`C`) | Prenna lace: grey fungus trailing cloth-like lace from under the cap — the lace is the harvest, so it must be the readable feature. |
| 20b | `RM_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceImmature` | 256×256 | 1 (`a`) | Same, cap closed, no lace yet. |
| 21 | `RM_LanternDeeps/Things/Plant/VellokReed` | 256×256 | 2 (`A`,`B`) | Vellok reed: tall aquatic fungus, tree-category, `visualSizeRange 1.5~2.5`. Glows cyan `(78,226,229)`. Stands in shallow water. |
| 22 | `RM_LanternDeeps/Things/Plant/KuvraSpout` | 256×256 | 2 (`a`,`b`) | Kuvra spout: upside-down cone growing out of shallow water, glowing cyan `(78,226,229)`. `maxMeshCount 9` — small and clustered. |
| 23 | `RM_LanternDeeps/Things/Plant/NurrikGill` | 256×256 | 2 (`A`,`B`) | Nurrik gill: dark, almost black cap; the **underside** glows brightly. The glow is reflected light on the water/ground under it, not a glower comp — draw the bounce. |

---

## Count

**26 texture jobs** across 23 numbered rows (rows 18/18b/18c and 20/20b are
multi-stage sets for one plant). **51 individual PNG files** once the per-folder
variant counts are honoured — counted by section: terrain 1, walls 3,
formations 10, sowable 1, items 8, flora 28.

## Audio — owed, not an art job

`RM_DeepCalm` ships with **no `ambientSounds`**. The donor's
`BMT_Ambient_Cave_Calm` is a SoundDef backed by a donor `.ogg` and does not come
with us. The sheet calls for *"the hum, rising to a Chorus; the click of a suit's
servo; the shatter"* (§9) — that is a sound-design job of its own and is not in
this build. A weather with no ambient sound is silent, not broken.

## Not in this build

The sheet's crystal-life cast — the Lantern, the Creep, the Cleavers, the
Chorus, the Shard-minds — is **new content owed by the frozen sheet**, donor or
no donor (`caverns_replacement_scoping.md` §2, *"What is NOT replacement"*). It
is its own L-sized C#-plus-art program and must not be billed to this retirement.
