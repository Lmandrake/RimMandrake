# Canal cover: a shallow canal as a wet foxhole (design, 2026-10-17)

Item: `CANAL_COVER_DESIGN_WET_FOXHOLE` (design, offline, for BENCH). Owner, verbatim (2026-10-17):
*"file a ticket to consider standing in a shallow canal a trench with cover implications"*.

Status: **DESIGN ONLY. No code written.** Nothing here is built; every number is a proposed default.
The build belongs to FOUNDRY once the owner answers §11. Engine facts below were read from the 1.6 source through
RimSage on 2026-10-17 (file and line given); FlowWorks facts were read from `src/RimMandrake/FlowWorks/Source/`.

## 0. The answer in five lines

1. **Yes, it can be done cheaply**, and without an elevation model: a trench wall is read exactly the way vanilla
   reads a sandbag, from the pawn's 8 neighbours, angle and distance included. No line walk, no height map.
2. **Cover comes from the wall, not the water.** A square gives trench cover when a neighbour's ground is higher than
   the pawn's floor. Water depth decides only the costs (slow, wet, swimming, drowning).
3. **It falls out right by itself:** a canal shot along its length gives no cover (enfilade); a flat basin floor
   gives none; the bank of a dug canal facing the shooter gives the most; a shooter standing on the lip gets
   almost none of it.
4. **It breaks a design law.** LAW 2 (2026-09-16) lists *"cover from below"* under *"Cut and stay cut"*. Building
   this needs his ruling that trench cover is a third stated exception (§11 Q1). That is the first question.
5. **Cost:** about 2 to 3 agent-days plus a short live check, after the depth rebuild's relative rules land.

## 1. What already exists (searched first)

| what | where | what it means for this design |
|---|---|---|
| **No trench cover code anywhere** | `grep` of `src/` for `trench`, `foxhole`, `CoverUtility`, `BaseBlockChance`, `ShotReport` (2026-10-17) | Only hit: `RSW Armoury/JumppackForMeleeAI` *reads* `CoverUtility.CalculateCoverGiverSet`. Nothing gives cover from depth. |
| **LAW 2** | `design/RimMandrake/flowworks_mod_definition.md:920`; restated in `RM_ExcavationDepth.cs:15-23` | *"Depth affects MOVEMENT and LIQUID. It never affects sight or shooting."* Cut list includes *"cover from below"*. Two stated exceptions: ruling 23 (shooting restriction) and [D] (a pit bounds a room). |
| **Ruling 23, the shooting restriction** | `RM_Patch_SuperdeepShooting.cs` (prefix on `Verb.CanHitTargetFrom`, validator on `AttackTargetFinder.BestAttackTarget`) | A pawn in a 2 m pit trades fire only with its 8 neighbours. Its own header: *"IT IS A RESTRICTION, NEVER A BONUS."* Setting `superdeepShootingRuleEnabled`. |
| **V5, the relative rewrite of ruling 23** | `flowworks_one_rebuild_plan_2026-10-17.md` V5; item `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` | Shooting is blocked only when the shot line crosses ground higher than both ends by more than a person's height. Owed, not built. Trench cover must hand over to V5 smoothly (§4). |
| **R8, elevation is dead** | rebuild plan R8 (card, 2026-10-17) | *"no raised ground, hills, height line of sight, or cells above cells."* This design reads no line of sight and no height map, so it stays inside R8. |
| **Hollow depth, cover-aware step depth** | `RM_MapComponent_Excavation.HollowDepthAt` (:302), `ClimbDepthAt`, `ClimbCellCount`; `RM_PocketGridMath` (a covered cell reads 0) | The one depth to read. Natural water reads 0 here (only dug squares and dry pond beds read as holes), so lakes and rivers never become trenches by accident. |
| **Person height** | `relative_depth_climb_design_2026-10-12.md` §8.2 | `H = 1.0 × sqrt(bodySize)` cells; a 0.5 m notch is 0.3 cells; a person is about 1.7 m. Reused, not reinvented. |
| **Water ladder** | `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` (P14), `FlowWorks_PondStageTerrain.xml` | `RM_WaterThin` 0.5 m (pathCost 18), `WaterShallow` 1 m (30), `RM_WaterChestDeepStill` 1.5 m (42), 2 m+ swimmable (R12, `DEEP_WATER_BUILD_SWIM_OR_SINK`). |
| **Dry channel costs** | `FlowWorks_Terrain.xml` | `RM_Channel_Empty` 30, `_Mid` 45, `_Deep` 80, `_Superdeep` 300. |
| **Drowning rule V2** | `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` | Drown when water covers the head: over 0.9 H standing, **0.2 H lying**. So a downed pawn drowns in about 0.35 m of water. |
| **Climb limit** | `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` (FOUNDRY, 4 ledger events, live proof owed) | A person climbs a 0.5 m step easily, 1 m slowly, and is held by a sheer 1.5 m step. A deeper "foxhole" is also a cage. |

## 2. Vanilla cover, as the 1.6 engine does it (read 2026-10-17, RimSage)

- **Cover is a Thing in a neighbouring square.** `CoverUtility.TryFindAdjustedCoverInCell` (`Verse/CoverUtility.cs`)
  looks at each of the target's 8 neighbours for `GetCover` (a Thing with `fillPercent`). Base block chance =
  `fillPercent` (0.75 if the Thing fills its square). Sandbags and barricades are **0.55**.
- **Angle falloff:** the angle between "target to cover" and "target to shooter" (×1.75 for a diagonal neighbour):
  under 15° full, then ×0.8 / ×0.6 / ×0.4 / ×0.2, and from 65° no cover at all.
- **Distance falloff:** a shooter under 1.9 squares from the cover square gets ×0.333; under 2.9, ×0.667. The square
  the shooter stands in is skipped.
- **Combining:** `num += (1 - num) × block` over the neighbours (`CalculateOverallBlockChance`).
- **Who reads it:** `ShotReport.HitReportFor` (hit chance and the tooltip), `CastPositionFinder.CastPositionPreference`
  (AI picks a firing square, `+ block × 0.55` when it wants cover), `AttackTargetFinder` (target score `- block × 10`),
  `JobGiver_AIFightEnemy.TryGiveJob` (a pawn with cover over 1% stays put and fires).
- **The trap for us:** when a shot fails the cover roll, `Verb_LaunchProjectile.TryCastShot` fires the bullet *at the
  cover Thing* (`GetRandomCoverToMissInto`) and reads its `.Position`. A trench wall is not a Thing, so putting trench
  cover straight into `coversOverallBlockChance` would throw a null reference on every "hit the cover" roll. §10
  routes around this.
- **Prone already exists:** `ShotReport.FactorFromPosture` halves the hit chance on a lying target at 4.5 squares or
  more. Pawns cannot choose to lie down; only the downed and sleeping lie.
- **Water already costs something:** every vanilla water terrain inherits `traversedThought SoakingWet`,
  `extinguishesFire`, and a perceived path cost (+180 undrafted, +18 drafted), so idle pawns avoid water and
  drafted ones accept it. Our water ladder inherits all of it.

## 3. When a pawn in a canal counts as in a trench

A pawn **is in a trench** against a given shooter when **all** hold:

1. It stands on its feet (not downed, not lying, not swimming, not flying).
2. Its own square's ground is lower than at least one neighbouring square's ground: wall height
   `h = ground(neighbour) − ground(own)`, in metres, from `HollowDepthAt` (covered pit squares, bridges and a
   pit cover read as ground level, 0).
3. That neighbour faces the shooter, by vanilla's angle rule (under 65°).
4. The shooter is not standing in that neighbour square (vanilla skips it too).

Consequences, all wanted and none special-cased:
- **Water is irrelevant to the cover.** A dry 1 m trench and a 1 m canal with 0.5 m of water give the same cover. The
  owner's "shallow canal" case is the wet version of the general rule (§11 Q2 asks whether dry counts too).
- **Enfilade:** a one-square-wide canal shot straight down its length shows no wall to the shooter: no cover.
- **Basins:** on the flat floor of a big dug basin, neighbours are level: no cover, except against the wall side.
- **Natural lakes and rivers never count** (their squares read 0 in `HollowDepthAt`). Wading a river is not a trench.
- **The lip shooter** standing on the wall square gets no cover from it, and a shooter one square back gets a third
  of it: vanilla's distance falloff. Close assault on a foxhole works the way it does on sandbags.

## 4. Cover value vs depth

Proposed base block chance for one wall square, before vanilla's angle and distance falloff:

`block = 0.75 × clamp(h / H, 0, 1)` × the strength setting (default 1.0).

| wall height h | person (H ≈ 1.7 m) | comparable to | notes |
|---|---|---|---|
| under 0.25 m | 0 | nothing | the under-25 cm water look; no wall worth the name |
| 0.5 m (knee) | **0.22** | a rock chunk at half | easy to climb out |
| 1.0 m (waist) | **0.44** | just under sandbags (0.55) | the classic fighting position; slow climb out |
| 1.5 m (chest) | **0.66** | between sandbags and a wall (0.75) | a sheer 1.5 m step **holds** a person (climb rule): the foxhole is now a cage unless it has a ramp or ladder |
| over person height | — | — | **V5 takes over**: across a step higher than a person, only point-blank shots are allowed at all. Cover is moot. |

- **Size matters for free:** a muffalo (body size 2.4, H ≈ 1.55 cells) in a 1 m canal gets 0.29, not 0.44; a child
  or a dog gets more. No table per race.
- **Continuity with V5:** cover climbs toward 0.75 as h reaches H, and above H the V5 restriction blocks the shot
  outright. There is no depth where the rule jumps the wrong way.
- **Shooting out:** a pawn in a trench shoots out normally while h is under its height (it fires over the lip). Over
  its height, V5 and ruling 23 already say it cannot. No new outgoing rule.

## 5. Costs

What standing in a wet canal already costs, and what is proposed. Each extra is its own setting and its own question.

| cost | status | detail |
|---|---|---|
| Slow movement | **exists** | water pathCost 18 / 30 / 42 by depth; dry channels 30 / 45 / 80. Getting in and out also pays the climb cost. |
| Wet mood | **exists** | vanilla `SoakingWet` thought from `traversedThought`. |
| Fire | **exists** | water squares put out fire; a canal of oil or propane is the opposite (FlowWorks liquid fire). |
| Can't lie down safely | **exists, and lethal** | V2: a downed pawn drowns when water covers 0.2 H (about 0.35 m). A wounded defender in a wet foxhole drowns unless pulled out. Readable warning owed by the no-vanishing rule. §11 Q8. |
| Trapped by its own trench | **exists** | the climb rule: a sheer 1.5 m step holds a person. A ramp or a lowered ladder is the way out. |
| Aim penalty in deep water | **proposed, off by default** | standing in water at chest depth (1.5 m) or more: the shooter's own hit chance ×0.85 (weapon held high, footing poor). §11 Q4. |
| Weapon fouling | **proposed, rejected for v1** | jams or durability loss need a new mechanic and new UI; nothing in vanilla to hang it on. Listed so it is a choice, not an omission. |
| Cold | **proposed, off by default** | "one kind of heat" (2026-09-29/30) says no new kind of cold either: if wanted, a wet pawn's comfortable minimum temperature rises (vanilla stat offset), so ordinary hypothermia arrives sooner. No new hediff. §11 Q4. |
| Swimming | **exists (owed build)** | 2 m+ water is swum (R12). A swimmer is not in a trench and, proposed, cannot fire ranged weapons (§11 Q6). |

## 6. Interactions

- **Deep water and swimming (R12, `DEEP_WATER_BUILD_SWIM_OR_SINK`):** a swimmer gets no trench cover (rule §3.1).
  Raise the water in a foxhole past 2 m and its occupants become swimmers in the open.
- **Flooding and level water (R1, `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`):** water rising in a trench changes
  costs and, at the head, drowning; it never changes cover, because cover reads the ground, not the surface. A
  player can drown a trench line by opening a sluice: a real tactic, and already a pit tactic.
- **Non-water liquids:** cover still reads the wall; the liquid's own effects (slime slip, poison fill, burning oil,
  tar) apply as today. A tar-filled trench gives cover and a slow, sticky death.
- **Pits (`PIT_SUPERDEEP_COLLAPSE_1`, ruling 23, V5):** a superdeep pit is a trench too deep to shoot out of. The
  three rules nest: shallow, trench cover; over a person's height, V5's lip-only restriction; sheer over the climb
  limit, held.
- **Pit covers:** a covered square reads ground level: a pawn on a cover is not in a trench, and a pawn next to a
  covered pit gets no wall from it. When the cover gives way, the hole reads again.
- **Bridges** over a canal: the pawn on the bridge is at ground level, no cover. A bridge square beside a pawn in
  the canal reads as ground: it is a wall (correct: it is solid).
- **Sandbags on the lip:** vanilla cover and trench cover stack by vanilla's own combine rule
  (`1 − (1 − a)(1 − b)`). Sandbags on a 1 m trench's lip: 0.55 then 0.44 → 0.75 total straight on. Strong, as it
  should be: that is a real fortification. A cap setting is offered (§9).
- **Explosions:** vanilla explosions ignore cover entirely. Proposed: unchanged (§11 Q7).
- **Melee:** unchanged.
- **Combat Extended** (if ever loaded) replaces all of this; trench cover would simply not apply. Noted, not handled.

## 7. AI use (raiders using canals)

- **One patch gives the AI everything vanilla cover gives it.** Because trench cover enters through
  `CoverUtility.CalculateOverallBlockChance` (§10), the AI that already loves sandbags reads it with no extra code:
  raiders choosing a firing square prefer a canal facing you (`CastPositionPreference`), a raider in a canal stays
  and fires (`JobGiver_AIFightEnemy`), and your shooters rate a raider in a canal as a worse target
  (`AttackTargetFinder`).
- **What raiders weigh against it:** they still pay the water path cost to get there, and idle pathing avoids water.
  They do not know a 1.5 m sheer canal will hold them; a raider who jumps in may be stuck there. That is a feature in
  the pit design (Q7 of `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST` decides whether raiders read traps); this design changes
  nothing about it. Proposed: a raider choosing a cast square **skips squares it could not climb out of** (one
  pocket-grid read), so raiders use foxholes, not cages. §11 Q5.
- **Colonists** get the tooltip (the hit chance line shows "trench wall: blocks N%"), so the player learns by looking.
  No auto-take-cover is added (vanilla has none either).
- **Raid generation** is untouched: no new raid type, no "trench raiders".

## 8. Performance

- **The hot readers are already hot in vanilla:** `CalculateOverallBlockChance` runs per shot, per tooltip frame, and
  per candidate square in every `CastPositionFinder` search (hundreds of squares). The trench read adds, per call,
  8 byte reads from `depthGrid`/`bedGrid` (the same 8 neighbours vanilla already visits) and reuses vanilla's angle
  and distance arithmetic.
- **Fast exit:** on a map with nothing dug (`ClimbCellCount == 0`) the whole rule is one int compare, the same
  pattern ruling 23 uses (`SuperdeepCellCount`). A further one-byte check skips any target square that is not
  itself a hollow.
- **No caches, no grids, no Things.** No invisible cover Things (rejected: thousands of Things on a canal network,
  the `huge_footprints_perf.md` lesson). No per-shot line walk (that is V5's cost, measured separately).
- **To measure at build:** the CastPositionFinder search time on a busy raid map with 500 dug squares, before and
  after (same harness as V5's "measure the cost on a busy map").

## 9. Mod Settings (FlowWorks, section "Pits, ladders and shooting")

| setting | default (proposed) | label and tooltip, plain |
|---|---|---|
| `trenchCoverEnabled` | on (if he rules it in) | **"Dug ground gives cover."** "A pawn standing in a dug trench or canal is covered by the wall facing the shooter, like a sandbag, more the deeper the trench. Off: depth never affects shooting except the pit rule." |
| `trenchCoverStrength` | 1.0 (range 0.25 to 1.5) | **"Trench cover strength."** "At 1.0 a waist-deep trench blocks a bit less than sandbags; chest-deep a bit more." |
| `trenchCoverCap` | 0.9 | **"Most cover from a trench plus sandbags."** Caps the combined block chance. |
| `trenchCoverWetOnly` | off | **"Only water-filled canals give cover."** (Exists only if he picks Q2 (b).) |
| `trenchAiAvoidsCages` | on | **"Raiders won't pick a foxhole they can't climb out of."** |
| `deepWaterAimPenalty` | off, ×0.85 | **"Shooting from chest-deep water is harder."** |
| `wetFeelsColder` | off, +6 °C | **"Wet pawns feel the cold sooner."** Ordinary temperature, no new illness. |
| `swimmersCannotShoot` | on | **"Swimmers can't use guns."** |

All off returns exactly today's behaviour. Each patch carries a `[PatchFeature]` tied to its setting, like
ruling 23's, so a game update that breaks one switches off only that feature.

## 10. Build plan (FOUNDRY, after §11 is answered)

**Gate:** lands after `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` (V5, so the hand-over at person height exists) and
reads depth in metres once `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` / P14 land; until then it reads notches × 0.5 m.

1. **Pure math, offline** (`RM_TrenchCoverMath.cs`): `WallBlock(hMetres, H, strength)`, and the vanilla angle and
   distance falloff copied with the line reference (`Verse/CoverUtility.cs`, `TryFindAdjustedCoverInCell`).
   Selftests: the §4 table, enfilade gives 0, lip shooter gets ×0.333, covered pit reads 0, natural water reads 0.
2. **One postfix on `CoverUtility.CalculateOverallBlockChance`**: combine trench block into the result for a
   standing, non-swimming target on a hollow square. This feeds the AI readers in §7 for free.
3. **One postfix on `ShotReport.HitReportFor`** to avoid the null-cover trap (§2): recompute the vanilla-only block,
   put it back in `coversOverallBlockChance`, and fold the trench share into the hit chance as its own factor, so a
   trench "miss" flies wild into the ground instead of at a cover Thing that does not exist. Postfix
   `GetTextReadout` to print the "trench wall" line. (Alternative considered: a guard inside `TryCastShot`; rejected
   because it is the most-patched method in the game.)
4. **Optional costs** (only those he picks): aim penalty in the shooter's half of `HitReportFor`; cold as a stat
   offset on a wet pawn; swimmers' ranged verbs refused in the existing `CanHitTargetFrom` prefix.
5. **AI cage guard** (if Q5 a): in the `CastPositionPreference` postfix, a square in a pocket the caster could not
   leave scores 0.
6. **Settings and labels** (§9).
7. **Functional script** (debug_process rule): `src/RimMandrake/FlowWorks/northstar/trench_cover_proof.py`, rows:
   - L1 offline: math selftests (step 1).
   - L2 quicktest: a 1 m dug trench, a pawn in it, a shooter 10 squares off square-on, along the axis, and on the lip;
     read `ShotReport` hit chance for each (state read, no screenshot). Expected: about 0.44 block, 0, small.
   - L2: a raider group against a colony with a canal line: count raiders whose cast square is a canal square.
   - L2: CastPositionFinder timing on a 500-dug-square map, on vs off.
8. **Validation walk row** in `design/validation_walks/RimMandrake/FlowWorks.md`.

Estimate: 2 to 3 agent-days offline plus about 0.5 live. No art. No new Things or defs beyond settings text.

## 11. Questions for the owner (plain language)

**Q1. This breaks a rule we wrote. Make an exception?** In September we wrote "digging changes movement and water,
never shooting", and listed "cover from below" as cut for good, because it usually means building a whole height
system. This design does not need one: it reads the 8 squares round a pawn, exactly like sandbags.
- (a) **Yes, trench cover is the third exception.** *Recommended.* Cheap, local, and it makes canals a defence.
- (b) Yes, but only as a mod setting that starts off. Safer; most players will never find it.
- (c) No, the rule stands; close the item.

**Q2. Dry trenches too, or only canals with water?**
- (a) **Any dug hole with a wall gives cover, wet or dry.** *Recommended:* a dry trench is the purer trench; water
  only adds costs.
- (b) Only water-filled canals. Matches your words literally; a dry ditch then gives none, which reads oddly.

**Q3. How strong?**
- (a) **Waist-deep a bit under sandbags, chest-deep a bit over.** *Recommended.*
- (b) Half that: a trench is a small edge, sandbags still matter.
- (c) Stronger: chest-deep as good as a wall. Trench lines would dominate defence.

**Q4. What should standing in water cost, beyond what the game already does (slower, wet mood)?**
- (a) **Nothing more for now.** *Recommended:* the drowning and trapping rules already make wet foxholes risky.
- (b) Add: shooting from chest-deep water is harder (about 15% worse).
- (c) Add: wet pawns feel the cold sooner (ordinary temperature, no new illness). (b) and (c) can both be picked.
- (Weapon fouling or jamming is left out: it needs a new mechanic. Say if you want it.)

**Q5. Should raiders use canals for cover?**
- (a) **Yes, the same way they use sandbags, but they won't jump into one they can't climb out of.** *Recommended.*
- (b) Yes, with no cage check: raiders sometimes trap themselves. Funnier, sometimes cheap.
- (c) No, only colonists benefit. Lopsided, and the game's AI usually plays by the player's rules.

**Q6. Can a swimming pawn fire a gun?**
- (a) **No.** *Recommended:* simple and believable.
- (b) Yes, badly (half accuracy).

**Q7. Does a trench protect from grenades and mortars?** The base game gives no cover from blasts at all.
- (a) **No, same as the base game.** *Recommended* for now.
- (b) Yes, partly: a trench halves blast damage to those in it. More real, more work, and it makes mortars weak.

**Q8. A downed pawn in a wet canal drowns** (the agreed drowning rule: water over a lying pawn's head, about a third
of a metre). So a wounded defender in a wet foxhole drowns unless pulled out.
- (a) **Keep it, with a clear warning when it starts.** *Recommended:* it is the price of a wet foxhole.
- (b) Spare them in shallow water (under 0.5 m): only deep water drowns the downed.

## 12. Open risks

- The `HitReportFor` fold (§10 step 3) depends on the struct's private field names in 1.6; read them on the Desktop
  before building (RimSage), and give the patch a `[PatchFeature]` so a rename switches it off cleanly.
- Other mods that patch `CalculateOverallBlockChance` or replace combat (Combat Extended, Yayo's Combat) were not
  checked against the live mod list; run `modcheck` for the list before building.
- `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` is still unproven live: the AI cage guard (Q5 a) trusts the pocket grid
  that proof is meant to confirm.
