# Sea-beast family review save — grid key

Review savegame: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\SEABEAST_FAMILIES_20260903.rws`

A throwaway dev quicktest map (250x250, tile 7597, grassland/coast), cleared and
painted `Sand` over `12,12,196,220`, holding **18 sea-beast families, 54 pawns**:
one baby, one juvenile and one adult of every `mandrake.rsw.seabeasts` creature.
The game is saved PAUSED at 11 AM. Nothing here is campaign state.

**What the owner is judging:** baby and juvenile `drawSize` are INTERPOLATED
(~0.55x and ~0.80x of adult), not authored — the ratio came from four vanilla
marine animals. The spec gives adult sizes only. Each cell shows the three
stages side by side, west to east: **baby - juvenile - adult**.

**Layout.** Six rows, one per def file/family; three columns. Row A is at the
SOUTH edge (low z) and row F at the north. Column pitch 62 cells, row pitch 36.
Within a cell the three stages are spaced by their own draw sizes, so nothing
overlaps.

⚠️ **Wild animals wander the moment the game is unpaused.** The coordinates below
are true for the saved, paused state only.

⚠️ **`RSW_Starmaw` (B2) and `RSW_Lanternwhale` (B3) have NO TEXTURES.** Player.log:
`Failed to find any textures at Things/Pawn/Animal/SeaBeasts/Starmaw/Starmaw`
(same for Lanternwhale). 16 of the 18 creatures have art deployed; those two
render as nothing. Their three pawns are present in the save regardless.

## Grid key

| cell | creature | family | baby (x,z) / drawSize | juvenile (x,z) / drawSize | adult (x,z) / drawSize |
|---|---|---|---|---|---|
| **A1** | `RSW_ColoClawFish` | Colo | (34,32) / 1.81 | (38,32) / 2.63 | (43,32) / 3.29 |
| **A2** | `RSW_AbyssalColo` | Colo | (96,32) / 1.98 | (100,32) / 2.88 | (105,32) / 3.6 |
| **A3** | `RSW_ThornbackColo` | Colo | (158,32) / 1.68 | (162,32) / 2.45 | (167,32) / 3.06 |
| **B1** | `RSW_Reefback` | Colossi | (29,68) / 5.89 | (38,68) / 8.56 | (50,68) / 10.7 |
| **B2** | `RSW_Starmaw` | Colossi | (90,68) / 6.27 | (100,68) / 9.12 | (112,68) / 11.4 |
| **B3** | `RSW_Lanternwhale` | Colossi | (152,68) / 6.6 | (162,68) / 9.6 | (175,68) / 12.0 |
| **C1** | `RSW_OpeeSeaKiller` | Opee | (34,104) / 1.24 | (38,104) / 1.8 | (42,104) / 2.25 |
| **C2** | `RSW_CrimsonOpee` | Opee | (96,104) / 1.36 | (100,104) / 1.98 | (104,104) / 2.48 |
| **C3** | `RSW_ShaleGorger` | Opee | (158,104) / 1.48 | (162,104) / 2.15 | (166,104) / 2.69 |
| **D1** | `RSW_SandoAquaMonster` | Sando | (31,140) / 3.91 | (38,140) / 5.69 | (46,140) / 7.11 |
| **D2** | `RSW_ElderSando` | Sando | (92,140) / 4.68 | (100,140) / 6.8 | (110,140) / 8.5 |
| **D3** | `RSW_StormSando` | Sando | (156,140) / 3.62 | (162,140) / 5.26 | (170,140) / 6.58 |
| **E1** | `RSW_Mee` | Scalefish | (35,176) / 0.55 | (38,176) / 0.8 | (41,176) / 1.0 |
| **E2** | `RSW_Faa` | Scalefish | (97,176) / 0.55 | (100,176) / 0.8 | (103,176) / 1.0 |
| **E3** | `RSW_Laa` | Scalefish | (159,176) / 0.66 | (162,176) / 0.96 | (165,176) / 1.2 |
| **F1** | `RSW_Yobshrimp` | Swarm | (35,212) / 0.55 | (38,212) / 0.8 | (41,212) / 1.0 |
| **F2** | `RSW_SiltLamprey` | Swarm | (97,212) / 0.55 | (100,212) / 0.8 | (103,212) / 1.0 |
| **F3** | `RSW_RustNipper` | Swarm | (159,212) / 0.55 | (162,212) / 0.8 | (165,212) / 1.0 |

## How each life stage was produced

`jawa/spawn_pawn` (faction `none`) then `jawa/set_pawn_age` with
`biologicalYears` set below/inside/above the def's `lifeStageAges` thresholds and
`allowBackwards: true` (RimWorld's `DebugSetAge` walks birthdays forward only, so
aging a generated adult down to a baby needs the raw setter). Ages used:

| lifeStageAges (minAge) | baby | juvenile | adult | creatures |
|---|---|---|---|---|
| 0 / 0.1 / 0.3333 | 0.05 | 0.20 | 1.0 | colo + opee families |
| 0 / 0.2 / 0.6 | 0.10 | 0.40 | 2.0 | colossi + sando families |
| 0 / 0.05 / 0.15 | 0.02 | 0.10 | 1.0 | scalefish (Mee, Faa, Laa) |
| 0 / 0.1 / 0.25 | 0.05 | 0.17 | 1.0 | swarm (Yobshrimp, SiltLamprey, RustNipper) |

Read back per pawn: `set_pawn_age` reported `AnimalBaby` / `AnimalJuvenile` /
`AnimalAdult` 18 times each, and `jawa/list_pawns` confirmed all 54 pawns present
at the coordinates above with the requested `kindDef` (0 substitutions).

