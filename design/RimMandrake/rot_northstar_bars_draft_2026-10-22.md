# The Rot: four north-star bars, drafted for the owner

**DRAFT — NOT VALIDATED.** Nothing here is in the `## north star` section of
`design/validation_walks/RimMandrake/TheRot.md`, and its `validated-hash:` is untouched. Only the owner validates.
Source: Rot open questions Q7 (card, 2026-10-22: "all four bars are to be DRAFTED for his validation") and Q2
(`design/RimMandrake/rot_warm_mat_portable_2026-10-22.md`). Experience being barred (his words, 2026-10-20): *"A cathedral
of mushrooms in the dark, generous and hungry. The Rot shares everything, including you."*

Common setup for every bar: a **quicktest map** (~90 s, `rimworld-debug-testing`), no cold load. Suite:
`src/RimMandrake/TheRot/validation.py`, run through `modcheck`, one live driver at a time, bridge held via `rimflow bridge take`.
`UNMEASURED` is a legal outcome and is never a pass. A bar goes in only with its check written and run once (red on a planted defect, green on the clean tree).

## Bar 1. The grove tends its own

**Sentence.** A wounded creature of the Rot's network heals faster while at least two of its kin stand within 12 cells of it, by 3 severity a day per point of its body size.

**Live check.** (Mechanism: `RM_HediffComp_KinMending` via `RM_KinMendingNetwork`, `src/RimMandrake/CreatureBehaviors/Source/RM_HediffComp_KinMending.cs`; carriers today are `RM_Mullgoth` and `RM_Durrok`, tag `RotNetwork`; restored in commit 69905fd71.)
1. Quicktest map, any biome. Spawn 2 groups of `RM_Mullgoth`, apart in space (more than 30 cells, no other `RotNetwork` body within 12 cells of either): group K = 3 mullgoth in a 5-cell cluster; group I = 1 mullgoth alone. Same body size by construction. Clear other hostiles.
2. Read each pawn's `BodySize` and confirm `RM_KinMendingNetwork` is on it. Give one mullgoth in K and the lone one in I an identical bruise (blunt, non-permanent, no bleeding) of severity 10; read injury severity as `s0`.
3. Advance 15,000 ticks (six 2,500-tick cycles; cycle phase is random per pawn, so at least five cycles land).
4. Read both bruises: `healed = s0 - s_now`.

**Pass.** `healed(K) - healed(I) >= 0.5 x BodySize`. Mechanism: each cycle heals `3 x BodySize x 2500/60000 = 0.125 x BodySize` extra, so 5 to 6 cycles give 0.625 to 0.75 x BodySize. **Fail.** Smaller difference, or `I` heals as much as `K` (no gate), or either pawn lacks the hediff (instrument blind). Neither bruise may reach 0.

**Cost/time.** One quicktest map plus 15,000 ticks; about 3 minutes. L2.

**Existing rows.** `health_sharing` (`map_mechanics`, toggle `healthSharing`) is the measuring row; today UNMEASURED (needs a bridge wound tool and the RSW bestiary spawns). Its offline half, written and run with this draft in `static_checks`, pins the five-body wiring, exactly two mending bodies, and the four defaults the threshold is derived from (2,500-tick cycle, 3 a day per body size, radius 12, min kin 2). Mod options `kinMendingEnabled`, `kinMendingBoostMultiplier` (default 1) scale it; the check runs at defaults.

## Bar 2. The gut takes the fallen

**Sentence.** A downed colonist left on open ground near a hwelgrue is swallowed alive, can be heard and found in the hwelgrue, and is cut out alive by damaging the hwelgrue.

**Live check.**
1. Any quicktest map (the comp works on any map). `RM_HwelgrueProof.ProofSpawn 1` places one hwelgrue; place one downed colonist on open ground (not in a stockpile, not roofed) near it.
2. Read `ProofSwallow`: expect `SWALLOW held`, `spawned False`, the inspect line naming the pawn alive inside.
3. Read `ProofKnock 0.8` and `ProofKnock 0.2`: knocking is louder and `RM_GutKnocking` early, `RM_GutKnocking_Failing` late.
4. `ProofCut 200` (belly first, up to six parts): expect `released True`, `spawned True`, pawn alive, not dead.
5. Control: a downed colonist inside a stockpile or under a roof is not swallowed.

**Pass.** Steps 2 to 4 read exactly as stated; the control is not swallowed. **Fail.** Any step reads otherwise, or the cut-out pawn is dead.

**Cost/time.** One quicktest map, no long tick advance; about 3 minutes. L2.

**Existing rows.** `hwelgrue.swallow_then_cut_out`, `hwelgrue.knocking_louder_early` (both measure steps 2 to 4). The stockpile/roof control is named in the chain docstring as NOT proven: owed (`ProofGrazeTarget`).

## Bar 3. The mat keeps you (written against the NEW portable living mat)

**Sentence.** A sealed room whose floor is at least 60% living mat warms with no fuel toward the lesser of 18 C above outside and 21 C, and never past 21 C; off the Rot the root that grows the mat must be fed, and in the Rot it is not.

(Owner, 2026-10-22: *"Make it work anywhere... Needs food. Would grow in other biomes if tended with food. Rot doesn't require feeding due to sharing lore."* Cap kept from 2026-09-17: *"It doesn't make enough to trivialize the deep deep dark. It just helps a lot."*)

**Live check.**
1. **Non-Rot quicktest map** (cold outdoors, e.g. an ice or boreal quicktest; outdoor must be below 3 C so the target is not already met). `RM_LivingMatRootProof.ProofStage` builds a sealed, roofed 5x5 wood room with a full root at its centre; confirm it reads `STAGED` and `rot False`.
2. `ProofSweeps 5|fed`: 5 hurried sweeps. Read food eaten and grown cells.
3. `ProofSweeps 40|fed`: read mat cells over total, room temperature before and after, outdoor temperature.
4. `ProofSweeps 3|empty`: read grown cells and the starving flag.
5. **Rot map** (needs an `RM_TheRot` map, or a quicktest with `RM_TheRot` biome): `ProofStage`, `ProofSweeps 5|fed`; food gauge must not move and mat must still spread.

**Pass.** Step 2 eats more than 0 and lays exactly 5 cells. Step 3 ends with at least 60% mat, room never above 21.05 C, and a room below target at the start ends warmer (target = min(outdoor + 18, 21)). Step 4 uncovers exactly 3 grown cells and reads `starving`. Step 5 food unchanged and cells grown. **Fail.** Any other reading, or temperature past 21 C at any read.

**Cost/time.** Steps 1 to 4 about 3 minutes on a quicktest map; step 5 needs a Rot map (UNMEASURED today; the one real cold-load or save-load cost in this draft). The gravship carry (minify, reinstall on substructure, launch, land) is a separate L2 owed in the spec and is **not** part of this bar until the engine behaviour is observed.

**Existing rows.** `living_mat_root.fed_root_spreads_and_eats`, `mat_room_warms_to_cap`, `starved_root_dies_back` (steps 2 to 4, written, never run live). `rot_root_eats_nothing` is UNMEASURED (step 5). The Rot's own, fuel-free `warm_living_ground` (`RM_MapComponent_WarmGround`, toggle `warmMat`) is UNMEASURED and covers the wild mat; the sentence's "in the Rot" half rests on it.

## Bar 4. The Sheen marks you

**Sentence.** A colonist standing unroofed in Sheen-fall gains the Sheen coating, climbs to the saturated stage in about a day and a half, and is slowed by protective gear and stopped by the symbiosis.

**Live check.**
1. `RM_TheRot` map, or any map where the weather def can be forced with `weather_set RM_SheenFall` (forcing the weather is reliable; the biome-scoped rotation is the unreliable part and is not what is barred). Spawn 3 colonists: A unroofed bare, B unroofed with the chitin spider helmet, C unroofed with `RM_SheenSymbiosis`; plus D roofed. Check `RM_SheenExposureLock` carrier hediff bootstraps `RM_SheenCoating` on each.
2. Read `RM_SheenCoating` severity on all four at t0.
3. Advance 36,000 ticks (1.5 days) under forced Sheen-fall; read severity and stage again.
4. Stop the weather; advance 15,000 ticks; read A's severity again.

**Pass.** A at or above 1.0 (stage `saturated`, within +/-20% of the 1.5-day anchor, 0.667 per day); B at or about a quarter of A's rate (0.75 protection, floor 0.05); C and D at 0 growth; A decays after the weather stops (-0.3 per day). **Fail.** Any other pattern, A does not climb, or no bootstrapped hediff on any pawn (instrument blind).

**Cost/time.** About 36,000 + 15,000 ticks; a long advance on a quicktest map, 4 to 8 minutes depending on tick rate. L2. Must run the proof harness's log-budget and tick-advance guards (`live-debugging-proof-harness`); shorten with a hurried-severity tool if one exists.

**Existing rows.** `sheen_exposure_ladder` (`map_mechanics`), toggle `sheenExposure`: UNMEASURED today ("needs an RM_TheRot map with a colonist under the Sheen weather and game hours of ticks"). Static: hediff and weather defs resolve (`defs_resolve`). A top-stage `RM_SporeFlesh` giver (mtbDays 0.25) is a further read, not part of this bar.

## Summary table

| bar | rows measuring it today | status | blocking |
|---|---|---|---|
| 1 the grove tends its own | `health_sharing` (static half runs) | live half UNMEASURED | a bridge wound tool and RSW bestiary spawns |
| 2 the gut takes the fallen | `hwelgrue.swallow_then_cut_out`, `knocking_louder_early` | written, never run live | stockpile/roof control row |
| 3 the mat keeps you | three `living_mat_root` rows | written, never run live | Rot-map row (`rot_root_eats_nothing`), a Rot-biome test map |
| 4 the Sheen marks you | `sheen_exposure_ladder` | UNMEASURED | a forced-weather, long-tick row |

## What the owner does

Validates, edits or strikes any bar's sentence. FOUNDRY writes the checks only after he names which sentences stand; the hash-bound text goes in `## north star` on his word only.
