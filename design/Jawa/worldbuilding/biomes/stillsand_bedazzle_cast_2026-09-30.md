<!-- status: cast bible — commissioned under STILLSAND_BEDAZZLE_SITTING_1 movement 4 -->
# The Stillsand — bedazzle cast bible (movement 4: ticket-out and commission)

**Item:** `STILLSAND_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 9)
**Date:** 2026-09-30 · **Author:** BENCH movement-4 commission agent

## 0. Rulings this commission carries (turn 4, 2026-09-30)

**Authorities:** `stillsand_turn3_development_2026-09-30.md` (the turn-3 development, `7136bb115`),
`stillsand_bedazzle_review_2026-09-29.md` (movements 1–2), and the ledger notes on
`STILLSAND_BEDAZZLE_SITTING_1`. Where the rulings and the turn-3 doc differ, **the rulings win**.
Card selections are recorded as *decision taken by question card*; only typed words are quoted.

| # | ruling | how | what changed against the turn-3 doc |
|---|---|---|---|
| 1 | Krayts (`RSW_KraytDragon` 0.15, `RSW_GreaterKraytDragon` 0.001) and the war wyrm (`RSW_WarWyrm` 0.2) **stay wild**; krayt attack events are added on top | card | the doc recommended incident-only; **declined** |
| 2 | Heat cover follows the sun angle: `overhead` rules above about 55°, `lowSun` below | card | as recommended |
| 3 | The muurrok **YES**, the free tier's giant, typed: *"Yes and use the beam attack style from mechanics due to reflections"* | card + typed | new: a reflected-sun beam in the mechanoid style. RimSage-verified as `Verb_ShootBeam` (`Gun_BeamGraser`), which needs an animal-safe copy (see `STILLSAND_EVENT_CREATURES_1` §3) |
| 4 | The piinnok **admitted** with its sink-when-threat warning | card | it is also the first member of `WATCHER_CREATURES_MOD_1`, which owns its def, behaviour and art |
| 5 | Drift shovelling yields glass sand at **full yield** | card | **reverses** the dunes engine's "dig vanishes" (the doc recommended no). The sieve becomes a grader (`STILLSAND_GLASS_LENS_CHAIN_1` §2); `design/MOVING_DUNES_DESIGN.md` corrected in this commission |
| 6 | Slate IN: droids invisible to swimmers; the thumper, typed *"Also thumper needs moisture not just thump"*; gale static; the mirage; fulgurites; sun glare + goggles; the sun lance; singing dunes warn; dust devils | card + typed | the thumper draws only while its sand is wet |
| 7 | Slate OUT: travel thirsty (the water appraisal), dunes take the ship, sinkholes | card | removed everywhere: no "wettest body" targeting, no hull burial, no sand caves |
| 8 | Glare is race-gated, typed: *"the sun protection for the eyes is great for races that need it, but the Jawa won't need it, but the slaves might"* | typed | Jawas immune by gene (`RM_GlareAdapted` on `RSW_RimMandrakeJawa`); everyone else, slaves included, is affected |
| 9 | Fulgurite art from real photographs, typed: *"the full rights should be looked up so you get realistic images of full rights, not some crazy simple tube or other fantasy image, actual lightning, striking actual sand"* ("full rights" = fulgurites, voice-typed) | typed | six real photos saved with licences in `references/fulgurite/` |
| 10 | Lore IN: the mummified caravan, the krayt horn, the wringing still. OUT: the glass sea landmark | card | `RUT_GlassSea` stays unplaced |

## 1. The build items filed

All filed `--for FOUNDRY` with prose in `infrastructure/state/items/<ID>.md` (## spec, ## criteria).
Each carries a Mod Settings toggle per feature and the readable-sign rule.

| item | what | waits on |
|---|---|---|
| `STILLSAND_BEDAZZLE_CONTENT_1` | wire 6 finished render sets; the 9 ruled fill-out defs; wire this commission's creature art; copy borrowed textures in; vaalok, qorrax inline, eemmok, vozzik comp; catches to `RM_` | nothing |
| `STILLSAND_SAND_SWIM_KIT_1` | the sand-swim kit (submerge, wake, rumble, breach, signs); droids invisible; the wet thumper; sand fishing on `RM_Stillsand`; the sound bed and singing-dune warning | nothing |
| `STILLSAND_SUN_FROM_LATITUDE_1` | pinned sky from the tile; clamp ~85°; cover by sun angle; sin(elev) heat; glare floor; race-gated glare-blind and goggles; the mirage; wind locked to the sun bearing | `SOLAR_HEAT_EXPOSURE_1` |
| `STILLSAND_EVENT_CREATURES_1` | krayt attack incident (krayts stay wild); the muurrok and its mirror beam; sarlacc comes to root; greater krayt den quest; krayt horn; Long Hunger live-fire | the swim kit |
| `STILLSAND_PRECIOUS_CAVES_1` | the rock genstep, the cave as a place, the precious table; **replaces `STILLSAND_CAVERN_AUTHORING_1`** | nothing |
| `STILLSAND_DUNE_GALE_1` | the dune gale, abrasion, carry-and-return, static, one emergence (mummified caravan), seeding, dust devils, tracks wiped | `MOVING_DUNES_BUILD_1` live run |
| `STILLSAND_GLASS_LENS_CHAIN_1` | drift → glass sand; sieve as grader; sun furnace; sun glass; lens bench; lenses; solar still (+ wringing); solar oven; sun lance; geophone; fulgurites on Stillsand + real-photo art; ship lens array row | nothing (crest-plate oven upgrade waits on the muurrok) |
| `STILLSAND_SKELETONS_TRACKS_1` | skeleton buildings, bone harps, corpse-to-skeleton, krayt graveyard re-pointed, track filths erased by the dunes, horizon warnings | the swim kit (wake filth) |
| `STILLSAND_RETURN_RITUAL_1` | the Debt, the Return ritual at a debt stone, bloom-on-pour (RM) | the still |

## 2. Shared law. Every entry obeys this without restating it

- **The light.** A fixed white sun that never sets. Sprites are lit by one hard white key from high
  front-top with crisp dark undersides. 🔴 **No baked cast shadow**: the pinned sun's elevation now
  varies by latitude (ruling 2), so a painted shadow would be wrong on most maps.
- 🔴 **Palette diversity is law.** Owner, verbatim, carried in every `style_notes`: *"Your color
  palette is too uniform per biome. Needs more variety."* Each subject has its own anchor (§6), no
  two the same.
- **The admission test** (`stillsand_bedazzle_2026-09-27.md` §1): everything admitted is buried,
  dormant, giant, or a line. The new creatures are a buried-until-it-arrives giant (muurrok) and
  owed faces for creatures already built.
- **Hard bans** (dune_sea §6, deep_desert): no rain and nothing rain-slicked (the thunderstorm is
  dry); no lush green; no pursuit predators (every predator is drawn as an ambusher or lunger); no
  nameable Earth animal; no fire from any sun weapon.
- **House style:** painterly vanilla-RimWorld, matte, no outlines, never cute. On faced jobs north
  is a true rear view with no face; facings derive from the accepted east master
  (`fill_queue.py` default).
- **Tier (Q11a):** invented names are `RM_`; canon-krayt things (`RSW_KraytHorn`, `RSW_KraytLens`,
  the krayt and war wyrm skeletons, the crawler tread) are `RSW_`.

## 3. Art dedup sweep

**MEASURED 2026-09-30, before anything was queued.** One python sweep over the on-disk
`infrastructure/artpipe/{done,_artsrc,pending,active,failed,_withdrawn}` (4,369 / 2,013 / 1 / 1 /
122 / 40 entries), `registry.jsonl`, the `origin/main` artpipe tree (3,753 paths) and every PNG
under `origin/main:src` (7,512). Each subject was searched by current, port and alternate names.

**Sanity probes, so a zero means zero:** `soorrak` 42 registry lines and 18 disk entries;
`whisperbird` 78 registry lines and 16 PNGs; `korrum` 3 PNGs.

| subject | spellings | result |
|---|---|---|
| vozzik, vekka, drazzik, nizzek, guzzka, aurrok | + sandlion, cavernbeast, cavebeast, spinedgow | 0 everywhere, **queued** |
| biosilica | biosilica | 0, **queued** |
| muurrok | + tuullik, kaaddok, haarrok | 0, **queued** |
| piinnok, zuurrik | + tiillok, muurra | 0; **held** (§5) |
| glass sand, sun glass, lenses, furnace, still, oven, sieve, sun lance, geophone, thumper, krayt horn, debt stone, water jar, dust devil, sand wake | the obvious spellings + heliostat, groundcaller, sandhammer, wringing | 0, **queued** |
| goggles | goggle | only Armoury headgear PNGs (Bothan, light-scan, pao hat), none a desert sun goggle, **queued**; existing goggles also cancel glare by tag |
| skeletons | skeleton, ribcage, kraytskull, kraytgraveyard | only `RM_FossilSkeleton` (Flooded Canyon, an item) and the krayt `*_Dessicated` corpse sprites; no giant skeleton building, **queued** |
| tracks | tread, print, scar | `RSW_CrawlerTreadWreck` is a wreck, not a track; `RM_Filth_MiddenshellFootprint` is the Wasteland's; **queued** |
| fulgurite | fulgurite | **EXISTS**: `RM_FE_Fulgurite` (Pyrelands, `pyre_fulgurite_v1`, `offbiome_fulgurite_v2/_v3`). The mechanism is reused; only the art is re-made, because the owner ruled it must come from real photographs |

`fill_queue.py --dry-run`: 61 would be filed, 0 refused as duplicates, 0 row errors.

## 4. Cast entries

The CSV's `prompt` and `style_notes` cells are the exact text each job carries; this is the intent.

### 4A. Owed faces for creatures already built (`STILLSAND_BEDAZZLE_CONTENT_1`)
The defs exist and their texPaths resolve nowhere. Each is drawn as our own animal from its own
description, never from a donor sprite. **Vozzik** (bs 5): a near-motionless plated grazing slug,
chalk-and-slate. **Vekka** (bs 2): the sand-swimming ambusher caught half-surfaced, burnt sienna.
**Drazzik** (bs 2.2): the false-drum lurker with a resonating throat-plate, pallid lilac.
**Nizzek** (bs 0.2): its hostile newborn in shell fragments. **Guzzka** (bs 5.5): the cavern beast
crusted with mineral dust so it reads as stone, salt-white over umber. **Aurrok** (bs 4): the
sail-backed placid giant, off Alpha Animals' texture, indigo sail. **Biosilica**: a handful of clear
grown lenses.

### 4B. The muurrok and its parts (`STILLSAND_EVENT_CREATURES_1`)
The free tier's leviathan, drawn **surfaced**, because submerged it is invisible. The read is one
enormous true-mirror crest on a dark oxblood body: that crest is its beam weapon and the only thing
seen when it cruises. 1024 canvas (ds ~10). **Crest-plate** (its corpse yield, the oven's
reflector) and the **krayt horn** (Obi-Wan's call, RSW) are item icons.

### 4C. Sand to glass to lens (`STILLSAND_GLASS_LENS_CHAIN_1`)
Five materials that must read as a refinement ladder: glass sand (ivory powder) → lens sand
(sugar-white, visibly finer) → sun glass (pale honey slabs) → precision lens (clear, brass rim) →
pearl lens (opal milk) and krayt lens (luminous amber). Buildings: the **sun furnace** (mirror dish
on a crucible, no fire), the **sieve** (driftwood grading screen with two trays, the ruling's new
grader), the **lens bench** (3×1, faced), the **solar still** (black basin, beaded glass, one focal
spot), the **solar oven** (mirror petals), the **sun lance** (base + rotating heliostat top) and the
**geophone** (glass-bulb resonator spike).
🔴 **The fulgurite** is drawn from the six real photographs in
`design/Jawa/worldbuilding/biomes/references/fulgurite/` (Sahara dunes, Mauritania, Algeria,
South Australia; licences in `SOURCES.json`): a crusty, knobbly, sand-coated, slightly flattened
fused root with a frothy white glass hollow where it broke. The prompt bans a clear glass tube, a
crystal and anything glowing. It replaces `RM_FE_Fulgurite.png` for every biome once accepted.

### 4D. Glare and the thumper (`STILLSAND_SUN_FROM_LATITUDE_1`, `STILLSAND_SAND_SWIM_KIT_1`)
**Sun goggles**: icon plus a worn eyes-layer set (faced). **Thumper**: a hammer tripod with a water
bladder and a visibly wet patch, because moisture is half the lure. **Sand wake**: a tileable trough
filth.

### 4E. Skeletons and tracks (`STILLSAND_SKELETONS_TRACKS_1`)
Seven skeleton buildings, the poster image: krayt, greater krayt, war wyrm (RSW); oommok (with
clinging mirror flakes), muurrok (fused crest-spine), guzzka, vozzik (RM). Tracks: oommok print,
eruption scar, glasscrust scar, crawler tread (RSW).

### 4F. Gale, ritual, caves
**Dust devil** (translucent spinning column, `STILLSAND_DUNE_GALE_1`), **debt stone**
(`STILLSAND_RETURN_RITUAL_1`), **sealed water jar** (`STILLSAND_PRECIOUS_CAVES_1`).

## 5. Wire-only, held and skipped

**Wire-only, never queued (art finished; `STILLSAND_BEDAZZLE_CONTENT_1` wires it):**
`rmmirrorgiant_v1` → `RM_Oommok` · `rmdusthusk_v1` → `RM_Siidda` · `rmshademite_v1`/`_v2` →
`RM_ShadeMite` · `RM_Ruukka_*`, `RM_Oorrik_*`, `RM_SandBusterMound_south` · the fill-out sets
`RM_Soorrak_b`, `RM_Gaanok_b`, `RM_Loomma_b`, `RM_KneelOllim_b`, `RM_Liikka`, `RM_Duumma`,
`RM_Veessa`, `RM_Hourbloom`, `RM_Glasscrust` · `RM_Qorrax` (KEEP) · `rslpn_v1` / `rswollim_v1` /
`rswollimwood_v1` (copy into `Stillsand/Textures`).

**Held, not queued:**
- **piinnok**: owned by `WATCHER_CREATURES_MOD_1`. Its sprite's shape depends on that pitch's Q9
  (peek art baked in, or a plain sprite plus a rim layer), so its art waits for that ruling.
- **zuurrik** (the blood-waker, review §6 fill #1): proposed, never ruled. No def, no art.
- **vaalok**: ruled (Q11) but never designed to art-brief level; CONTENT_1 files the def and queues
  the art after a dedup check.
- **Terrain** (brine seep, cave floor, the Return-line stain): terrain textures are authored with
  the terrain defs, not through these sprite jobs.

**Skipped, art already in the game:** `RM_FE_Fulgurite`'s mechanism (only its art is re-made);
krayt corpses (`*_Dessicated`); `RSW_KraytDragonSkull`, `RSW_KraytPearl`; the krayt SoundDefs.

## 6. Queued art: FILED 2026-09-30, 61 jobs, 0 refused

**CSV:** `infrastructure/artpipe/art_lists/stillsand_bedazzle_cast.csv`. Channel codex,
transparent, `reference` empty on every row (fresh designs, never reskins; the fulgurite's photo
references are described in its prompt rather than passed as `reference`, which would trigger
reskin validation). Queued with `fill_queue.py`, derive-facings default.
**43 subjects (9 faced sets + 34 singles) = 61 job files.**

| item | id | canvas | facings | anchor |
|---|---|---|---|---|
| CONTENT | `RM_Vozzik` | 512 | s,e,n | chalk and slate |
| CONTENT | `RM_Vekka` | 256 | s,e,n | burnt sienna |
| CONTENT | `RM_Drazzik` | 256 | s,e,n | pallid lilac |
| CONTENT | `RM_Nizzek` | 256 | s,e,n | raw pink-grey |
| CONTENT | `RM_Guzzka` | 512 | s,e,n | mineral salt |
| CONTENT | `RM_Aurrok` | 512 | s,e,n | sail indigo |
| CONTENT | `RM_Biosilica` | 256 | single | water-clear |
| EVENT | `RM_Muurrok` | 1024 | s,e,n | mirror and oxblood |
| EVENT | `RM_CrestPlate` | 256 | single | polished silver |
| EVENT | `RSW_KraytHorn` | 256 | single | old ivory |
| LENS | `RM_GlassSand` / `RM_LensSand` / `RM_SunGlass` | 256 | single | ivory powder / sugar white / pale honey |
| LENS | `RM_PrecisionLens` / `RM_PearlLens` / `RSW_KraytLens` | 256 | single | clear+brass / opal milk / krayt amber |
| LENS | `RM_SunFurnace` | 512 | single | white heat and steel |
| LENS | `RM_SandSieve` | 256 | single | driftwood and wire |
| LENS | `RM_LensBench` | 512×256 | s,e,n | patina brass and bone |
| LENS | `RM_SolarStill` | 512 | single | black and clear |
| LENS | `RM_SolarOven` | 256 | single | sand ceramic and mirror |
| LENS | `RM_SunLance_Base` / `RM_SunLance_Top` | 256 | single | slate and steel / faceted mirror |
| LENS | `RM_Geophone` | 256 | single | glass and bronze |
| LENS | `RM_FE_Fulgurite_real` | 256 | single | fused sand (real photos) |
| SUN | `RM_SunGoggles` | 256 | single | smoked honey and leather |
| SUN | `RM_SunGogglesWorn` | 256 | s,e,n | smoked honey and leather |
| SWIM | `RM_Thumper` | 256 | single | iron and wet sand |
| SWIM | `RM_Filth_SandWake` | 256 | single | shaded dun |
| SKEL | `RSW_KraytSkeleton` / `RSW_GreaterKraytSkeleton` / `RSW_WarWyrmSkeleton` | 1024×512 | single | sun-bleached bone / old ivory / grey bone |
| SKEL | `RM_OommokSkeleton` / `RM_MuurrokSkeleton` | 1024×512 | single | bone and mirror / chalk and oxblood |
| SKEL | `RM_GuzzkaSkeleton` / `RM_VozzikSkeleton` | 512 | single | salt-crusted bone / chalk plate |
| SKEL | `RM_Filth_OommokPrint` | 512 | single | slumped dun |
| SKEL | `RM_Filth_EruptionScar` / `RM_Filth_GlasscrustScar` | 256 | single | blown ochre / frosted shard |
| SKEL | `RSW_Filth_CrawlerTread` | 512×256 | single | pressed tan |
| GALE | `RM_DustDevil` | 256×512 | single | spun ochre |
| RITUAL | `RM_DebtStone` | 256 | single | sandstone rose |
| CAVES | `RM_SealedWaterJar` | 256 | single | terracotta and wax |

## 7. Handoff notes

- **Owner still to rule:** (a) the sieve's new role as a grader is BENCH's rethink after ruling 5
  removed its old job; (b) zuurrik, never carded; (c) the watcher pitch's Q9 (peek art), which
  gates the piinnok's art; (d) the first-value heat numbers (55 °C substellar, 0.35 glare floor),
  which the owner-watched heat sitting tunes.
- `RM_FE_Fulgurite_real` is a re-make of a shipped texture: when it lands, put it beside the current
  `RM_FE_Fulgurite.png` on a review sheet before swapping, since the Pyrelands ships the old one.
- The worn-goggle set assumes a plain eyes-layer apparel with no body-type variants; if the def pass
  chooses otherwise, re-cut from the accepted east master.
- The skeleton buildings are queued at 1024×512 single; if the build wants rotations, re-cut the
  accepted render rather than re-generating.
