# Phase 0 P2: questions for the owner (Alpha Animals, 2026-10-15)

Nothing below is built. Each one is a keep/cut or a ruling only he can give.

## Q1. Seven creatures have no render and no port: keep or cut?

A cast row today names each of them. A port needs art we do not have (about three facings each), so each "keep" is
one new creature to draw. Evictions are stopped, so none is cut without his word.

| creature (donor def) | where it is cast | what it is | if KEEP | if CUT |
|---|---|---|---|---|
| AA_BloodShrimp | RM_Greentide 0.2 | a fast (5.5) fish-sized shrimp, size 1, 4 tools | port + 3 facings of art | Greentide loses one 0.2 small predator |
| AA_RaptorShrimp ("sharpshrimp", Miasma sheet 2026-10-08) | RM_Miasma 0.2, channel predator | bigger (1.4), 750 value, 4 tools | port + 3 facings | Miasma loses its channel predator; the Miasma sheet named and ruled it |
| AA_Eyeling ("ikee") | none in the shipping layer; `RSW_Ikee` already exists | matched, nothing to do | none | none |
| AA_GreenGoo | RUT_ twin only (Slime 2.0); rider (acid burst, SpasticScaled) | a goo blob | P3-style port + art | dies with the frozen twin at the one-time paint |
| AA_AcanthamoebaGiganteaSmall / Large | RUT_ twin only (Wasteland, Slime); rider (acid burst) | amoeba | P3-style port + art | dies with the twin |
| AA_RedGoo, AA_RedSpore | RUT_Contagion twin only; riders | goo / spore | same | same |

The shrimps are the only two with a live `RM_` row. For the RUT_-only ones, "cut" costs nothing in the shipping game.

## Q2. Aerofleet + dustveil: art already exists, but it is not on a sheet he has ruled

All 11 new creature ports already have finished artpipe renders bound to the donor def or name-matched (for example
`gapall_AA_Aerofleet_v1`, `angelmoth_option_a/b/c_v1`, `gapall_AA_AnimaColossus_v1`, `cauldronfix_bedbug_v2`,
`enact_f2b850a2_crystalmit_v1`, `miasma_siezer_v1`, `gapall_AA_Metallovore_v1`, `gapall_AA_Plasmorph_v1`,
`nightsideice_shockgoat_v1`, `rot_swarmling_v2`; the silkie has 14 ledger variants). None is installed under the new `RM_` texPath, so every new port has NO picture in game until
the Phase 0 sheet (O1) is ruled and `art.py enact` runs. Question for the sheet: accept the existing renders as they are,
or send any back? Nothing was queued for these creatures.

## Q3. Skorra: the def was deleted on 2026-10-08, and he said "cut from where I said cut, not from game" on 2026-10-11

`RM_Skorra` (the needlepost) was deleted by `d074b131a` with the 15 cut creatures, but `RM_Greentide` still casts the donor
`AA_Needlepost` at 0.3. I restored the def (`src/RimStarWars/SWBestiary/Defs/DesertPort/RM_Skorra.xml`, verbatim from
before the sweep, texPath moved to our path) and pointed the Greentide row at it, because his 2026-10-11 ruling reads as
"the creature stays in the game". Keep that, or cut the Greentide row and the def? Its art (`gapall_RSW_Skorra_v1`)
still awaits his keep/replace.

## Q4. Three ports now have more than one home (his one-biome rule)

Repointing a donor row to an existing port gives that port a second cast row. Evictions are stopped, so I repointed;
this is a heads-up for the biome sittings, where multi-homed rows are decided.

| port | its original home | now also cast in |
|---|---|---|
| RM_Lirrith (murkling) | Abyss, header says "this biome only" | FloodedCanyon (patch row in `WildAnimals_CrackedLands.xml`) |
| RM_Bileworm (helixien) | Warscar, header says "ONE HOME" | Cauldron 0.1, Miasma 0.1 |
| RM_Mullgoth (wildpod) | TheRot | Cauldron 0.05, LeaningScrub 0.025 |

## Q5. Dustveil (angel moth) art is byte-identical to the donor's

`src/RimMandrake/TheRot/Textures/RotSpecies/AngelMoth/AngelMoth_{east,north,south}.png` is the donor's own picture. The new
`RM_Dustveil` points at it, so it still fails the "0 donor-identical PNGs a def references" gate until one of the four
finished renders (`angelmoth_option_a/b/c_v1`, `gapall_AA_AngelMoth_v1`) is chosen and installed.

## Q6. Two cosmetic losses to flag, and one provisional meat

- **Falling-leaves effect on the pluur'va** (donor `AA_AnimaLeaves` + 3 fleck textures) is dropped: three more art jobs for a
  cosmetic. Say the word and it is rebuilt.
- **Sexes share one picture** where the donor drew a female variant (giant crowned silkie), and the dessicated donor pictures are
  dropped (vanilla fallback).
- **Meat and leather are vanilla stand-ins, PROVISIONAL** (`useMeatFrom` Megaspider/Tortoise/Iguana/Elephant), as the Abyss and
  Warscar ports did, so no meat or hide art is owed.
