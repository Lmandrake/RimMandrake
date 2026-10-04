# WARSCAR_SNAP_MARK_1 — the chatrak's snap and the mark made a trade, franchise-free on RM

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.5 and §2.6 (both ruled IN
at turn 2; the loosened panel adopted at the GPT card). Both are XML on shipped RM classes plus small C#.
The RUT twin (`SCARLANDS_MECHANICS_2`) is frozen and untouched.

## spec

1. **`RM_ChatrakSnapArming`** in `RM_Warscar`'s `<biomeMapConditions>`: `GameCondition_ArmLatentHazard`
   + `ArmLatentHazardExtension` (`pawnKindFilter: [RM_Chatrak]`, `requiredHediff: Scaria`,
   `hediffToApply: RM_ChatrakIncubation`). The twin's `RUT_ScariaOnsetArming` with the filter swapped.
2. **`RM_ChatrakIncubation`** with **visible** stages: 0 hidden; 1 (≥0.4) *plates lifting*, a
   render-node overlay (a worker subclass of `PawnRenderNodeWorker_OverlayScaria` drawing from this
   stage; art `RM_ChatrakPlatesLifted`); 2 (≥0.7) *off its feed*, `hungerRateFactor 0`; 3 (≥0.9)
   *circling*, a ~40-line ThinkNode wandering radius 3 (leaves a ring of prints in a Settling); 4 (1.0)
   *the snap*, `ManhunterPermanent` mtb 0.5 d. Density: about one snap per week or two.
3. **`RM_WarscarMark`** (HediffDef, copied from `RUT_ScarlandsMark`, label franchise-free): stages hidden /
   mild ≥0.25 / deepening ≥0.5 (`Wander_Sad` 6 d) / heavy ≥0.75 (3 d), `SeverityPerDay -0.1`,
   `HediffCompProperties_SeverityFloor` (trigger 0.5, floor 0.25). Thoughts ported as
   `RM_WarscarMarkThoughts`.
4. **`RM_WarscarMarkLock`**: `GameCondition_EnvironmentalWeather` + extension, 0.0125 per 2,500 ticks,
   `onlyUnroofed false`. About eight days arms the floor.
5. **The pay, per stage `statOffsets`:** `HackingSpeed` +15/25/35%, `ButcheryMechanoidSpeed` +10/20/30%,
   `SmeltingSpeed` +10% from deepening.
6. **`RM_LoosenedPanel`**: a few per map set into ruin walls by the ruins genstep, each with an Odyssey
   `AncientSealedCrate`-family cache placed **behind it at generation**. Always visible, own graphic.
   Only a pawn at **deepening or above** can work it loose (WorkGiver gated on hediff stage); anyone
   else: *"It won't give. Someone who knows this ground might."*
7. **No stacking** (ruled): both marks carry a shared `RM_WarscarMarkFamily` tag; the lock skips a pawn
   carrying the other.
8. **Mod Settings:** snap on/off · arming interval · stage speed · mark on/off · accrual · floor on/off ·
   trade bonuses on/off · loosened panels per map.

## criteria

- A dev-spawned scaria chatrak on a Warscar quicktest shows the lifted-plate overlay at stage 1, stops
  eating at 2, circles at 3, goes manhunter at 4 (state reads per stage).
- A clean chatrak tames and never snaps.
- A pawn with eight days on the map reaches the floor; its stat tooltip lists the trade bonuses.
- A pawn below deepening is refused at a loosened panel; one at deepening opens it onto a real crate.
