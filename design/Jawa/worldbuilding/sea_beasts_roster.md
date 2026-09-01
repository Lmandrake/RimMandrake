<!-- status: RULED roster — SW_SEA_MONSTERS_ART_1, owner 2026-08-31: ALL 18 round-1
     mockups kept, each its own creature ("They're exceptional. Don't get rid of any
     of them"); BENCH picked the alignment on his word. Art source of truth:
     src/RimStarWars/SeaBeasts/art/mockups/<slug>_opt<n>.png (committed 6a02f477).
     Roles and size bands: depths_concept.md §5. Tier RimStarWars (RSW_). -->
# Sea beasts roster — 18 creatures, six roles, three each

Each role becomes a small family: the three mockups are cast as related species
within the role's bodySize band, canon Star Wars where a name exists, honest
originals where it does not. Every creature keeps its mockup as final-concept
art source; no re-rolls.

## Silt ambushers (band 1–2) — the opee family

| art | creature | canon? | size | cast |
|---|---|---|---|---|
| `opee_opt1` | **Opee sea killer** | CANON (Naboo) | 1.4 | The baseline: brown armored angler-crab, lure stalks. |
| `opee_opt2` | **Crimson opee** | variant, original | 1.7 | The tongue-hunter: barnacled red morph, adhesive tongue out — the canon opee's signature hunt made visible. More aggressive, warm-silt shallows. |
| `opee_opt3` | **Shale gorger** | original | 2.0 | The heavy benthic cousin: slate plate armor, pale blind eyes, sits in scree and swallows. Slowest, hardest to kill. |

## Harpooners (band 2–4) — the colo family

| art | creature | canon? | size | cast |
|---|---|---|---|---|
| `colo_opt1` | **Colo claw fish** | CANON (Naboo) | 3.0 | The baseline: pale cave eel, whisker lures, claw forelimbs. |
| `colo_opt2` | **Abyssal colo** | variant, original | 3.6 | Deep-trench morph: bioluminescent blue spot-rows, hunts in full dark below the silt line. |
| `colo_opt3` | **Thornback colo** | variant, original | 2.6 | Spined shallow morph: purple-dark, faster, ambushes from wrecks and reef cuts. |

## Leviathans (band 12–20) — the sando family

| art | creature | canon? | size | cast |
|---|---|---|---|---|
| `sando_opt1` | **Sando aqua monster** | CANON (Naboo) | 14 | The baseline: grey lion-faced swimming quadruped. |
| `sando_opt2` | **Elder sando** | variant, original | 20 | The scarred bull: barnacle-crusted, old wounds, apex of the apex — rare, near-mythic. |
| `sando_opt3` | **Storm sando** | variant, original | 12 | The pelagic morph: blue biolum striping, finned, faster, ranges open water rather than trenches. |

## Shoal grazers (band 0.1–0.5) — the scalefish (CANON family, Naboo)

| art | creature | canon? | size | cast |
|---|---|---|---|---|
| `grazer_opt1` | **Mee** | CANON scalefish | 0.15 | Silver-blue schooling fish, biolum dot-line. The bulk protein of the shallows. |
| `grazer_opt2` | **Faa** | CANON scalefish | 0.2 | Gold-olive scalefish, same biolum line — warm-water counterpart. |
| `grazer_opt3` | **Laa** | CANON scalefish | 0.4 | The big ornate one: striped, streamer-finned, eye-spot false faces. Prized catch. |

## Scavenger swarm (≈0.2 each) — the bottom-feeders

| art | creature | canon? | size | cast |
|---|---|---|---|---|
| `swarm_opt1` | **Yobshrimp** | CANON (Naboo) | 0.2 | Pale isopod, feather antennae — the carcass-stripper baseline. |
| `swarm_opt2` | **Silt lamprey** | original | 0.2 | Black round-maw eel; latches on live prey too — the swarm's nasty edge. |
| `swarm_opt3` | **Rust nipper** | original | 0.25 | Red-shelled spiky crab, glowing eyes; armored, aggressive when massed. |

## Colossal neutrals (band 30+) — the great filter-feeders (all original)

| art | creature | canon? | size | cast |
|---|---|---|---|---|
| `colossus_opt1` | **Reefback** | original | 32 | So old the reef grows on it: coral, kelp, hangers-on. A moving ecosystem. |
| `colossus_opt2` | **Starmaw** | original | 36 | Constellation-spotted; its biolum patterns read like a night sky. The one sailors navigate by. |
| `colossus_opt3` | **Lanternwhale** | original | 40 | Moss-shrouded, trailing blue lantern tendrils that draw the plankton it strains. The largest living thing in the seas. |

## Ecology in one line each

Scalefish feed everything; the swarm cleans everything; opee kill from the silt,
colo from the dark, sando from above; the colossi ignore all of it and are
followed by scalefish shoals and swarm scavengers alike. Variants split by
depth/temperature so spawn biomes separate them naturally (shallows: crimson
opee, thornback colo, faa · mid: baselines, mee · deep/trench: shale gorger,
abyssal colo, elder sando, the colossi · open water: storm sando, laa).

## Next (unchanged process)

Palette passes are SKIPPED — the kept mockups are the approved concepts.
Straight to: facings per creature, sprite validator per facing
(128 px/cell, chroma-key alpha), PROVE/EXPECT/LIES beside each PNG, then defs
sized per this table under beast-normalization Laws 3+4.
