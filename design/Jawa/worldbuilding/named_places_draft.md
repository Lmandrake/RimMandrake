<!-- status: draft -->
# NAMED PLACES — draft set for the owner to veto

> 🔴 **HALF THE PLANET HAS NO NAME.** Measured 2026-08-22: **11,107 of 21,872 tiles** carry
> an empty `region`, in one contiguous blob spanning the whole world from arc 40° to 152°.
> The 23 regions authored so far cover the other half. This is the draft that closes it.

**How the ground was cut.** Not by hand and not at random: every unnamed land tile was keyed
by **(band × terrain)** — its angle from the substellar point, and what it is made of — and
then split into contiguous blocks. A name here therefore describes something a traveller
would actually notice changing under their feet. 37 blocks of 60+ tiles came out, covering
**9,820 of the 11,107**; the remaining ~1,287 tiles are slivers and stay unnamed for now.

## How to veto

**Edit the `Name` column below and nothing else.** The `seed` is how the block is identified
when the names are applied — it is a tile id, it is stable, and it must not be changed.
- To rename: overwrite the name.
- To reject a block entirely: put `-` in the Name column and it stays unnamed.
- To merge two blocks: give them the same name.

Then say the word and it goes into `world/ASHKARR_WORLDMAP_tiles.csv`.

⚠️ **Naming is not free.** These become RimWorld `WorldFeature`s, drawn across the world map
in curved label text. 37 more labels on top of 23 is a busy map — rejecting the small ones is
a legitimate and probably wise answer.


## THE DAY SIDE — the star stands overhead

| Name | tiles | terrain | arc | elevation | temp | seed |
|---|---:|---|---|---|---|---:|
| **The Glare** | 866 | desert | 40–60° | 12–988 m | 33 to 51 °C | `21` |
| **The Kiln** | 816 | desert | 40–60° | 12–776 m | 34 to 51 °C | `25` |
| **The Fever Wood** | 65 | fungal | 41–60° | 12–176 m | 38 to 51 °C | `175` |

## THE SUNWARD MARGIN

| Name | tiles | terrain | arc | elevation | temp | seed |
|---|---:|---|---|---|---|---:|
| **The Long Sand** | 670 | desert | 60–85° | 12–847 m | 15 to 38 °C | `24` |
| **The Thornbelt** | 492 | shrub | 60–85° | 12–587 m | 18 to 37 °C | `50` |
| **The Dry March** | 387 | desert | 60–79° | 12–1090 m | 21 to 36 °C | `38` |
| **The Combs** | 360 | desert | 60–84° | 12–533 m | 19 to 38 °C | `35` |
| **The Cracklands** | 210 | badlands | 60–85° | 12–256 m | 18 to 37 °C | `14` |
| **The Sunward Scrub** | 154 | shrub | 73–85° | 12–1062 m | 17 to 27 °C | `40` |
| **The Blight** | 140 | waste | 73–85° | 12–290 m | 17 to 28 °C | `110` |
| **The Warm Rot** | 93 | fungal | 74–85° | 148–838 m | 14 to 24 °C | `46` |
| **The Cinders** | 93 | waste | 63–82° | 12–394 m | 20 to 33 °C | `231` |
| **The Apron** | 70 | shrub | 75–85° | 12–12 m | 18 to 26 °C | `95` |
| **The Saddle** | 68 | desert | 61–70° | 12–624 m | 30 to 34 °C | `73` |

## THE TERMINATOR — the only liveable band

| Name | tiles | terrain | arc | elevation | temp | seed |
|---|---:|---|---|---|---|---:|
| **The Softground** | 275 | shrub | 85–100° | 12–1087 m | -4 to 18 °C | `43` |
| **The Sporefields** | 255 | fungal | 85–100° | 12–608 m | 0 to 18 °C | `1` |
| **The Scour** | 234 | waste | 85–100° | 12–598 m | -1 to 18 °C | `49` |
| **The Low Dew** | 230 | shrub | 85–96° | 12–156 m | 7 to 18 °C | `26` |
| **The Flatdew** | 141 | shrub | 85–100° | 12–12 m | 2 to 18 °C | `275` |
| **The Shelf Rot** | 85 | fungal | 86–95° | 355–902 m | 4 to 15 °C | `194` |
| **The Pan** | 79 | waste | 85–94° | 12–12 m | 10 to 18 °C | `0` |
| **The Knuckles** | 78 | crags | 87–99° | 12–179 m | 2 to 16 °C | `159` |

## THE NIGHTWARD MARGIN

| Name | tiles | terrain | arc | elevation | temp | seed |
|---|---:|---|---|---|---|---:|
| **The Rimewall** | 335 | crags | 100–125° | 12–1331 m | -35 to 2 °C | `33` |
| **The Cold Bloom** | 254 | fungal | 106–125° | 12–1235 m | -34 to -7 °C | `13` |
| **The Ashen Waste** | 202 | waste | 100–120° | 12–671 m | -25 to 2 °C | `48` |
| **The High Rot** | 165 | fungal | 100–120° | 535–1690 m | -29 to -2 °C | `398` |
| **The Last Green** | 144 | shrub | 100–124° | 12–939 m | -30 to -1 °C | `23` |
| **The Grayrot** | 123 | fungal | 100–113° | 118–915 m | -17 to 1 °C | `160` |
| **The Shoulder** | 68 | shrub | 100–106° | 640–1299 m | -11 to -2 °C | `218` |

## THE NIGHT SIDE — the star never rises

| Name | tiles | terrain | arc | elevation | temp | seed |
|---|---:|---|---|---|---|---:|
| **The Deadstone** | 1979 | crags | 125–152° | 65–1615 m | -66 to -30 °C | `4` |
| **The Cinderdark** | 146 | waste | 125–138° | 322–774 m | -46 to -30 °C | `138` |
| **The Frostbloom** | 142 | fungal | 125–136° | 728–1605 m | -49 to -32 °C | `57` |
| **The Deep Bloom** | 132 | fungal | 125–142° | 154–1046 m | -54 to -30 °C | `327` |
| **The Venom Wood** | 72 | fungal | 133–144° | 270–697 m | -53 to -40 °C | `215` |
| **The Coldspore** | 69 | fungal | 125–139° | 680–1196 m | -49 to -34 °C | `28` |
| **The Crown Rot** | 67 | fungal | 125–132° | 986–1528 m | -44 to -35 °C | `17` |
| **The Last Scrub** | 61 | shrub | 130–138° | 410–743 m | -47 to -36 °C | `78` |


## The voice these were written in

The 23 existing names are plain, harsh, functional English — *The Scald*, *The Salt*,
*The Anvil*, *The Fall Line*, *The Rust Cathedral*. A scavenger clan's names: what a place
does to you, not what it looks like. The draft holds to that. ⛔ Nothing here is Star
Wars-flavoured, and nothing is pretty for its own sake.

Three that are doing specific work and are worth a second look before you accept them:

- **The Deadstone** — 1,979 tiles, the single largest unnamed block on the planet, night-side
  rock between −66 and −30 °C. It is bigger than any currently-named region except the Dune
  Sea. If one name in this list matters, it is this one.
- **The Flatdew** and **The Pan** — both are dead flat at exactly 12 m, the world's floor
  elevation. They are named for being flat because that is the only thing true of them.
- **The Fever Wood** — 65 tiles of Feralisk jungle at 38–51 °C on the day side. Small, but it
  is the only warm forest on the planet and the only place that biome appears sunward.
