# The sweetline tree, its wool and its bark-wardens: the ruled spec

**The one authoritative spec** for the sweetline tree's wool economy, the scratching-tree
behaviour, the bark-warden guardian and its activation, tree placement, and their settings.
Every owner question on `LEANINGSCRUB_SWEETLINE_GUARDIAN_1` is ruled (2026-10-03). The former
`leaningscrub_sweetline_guardian_activation_2026-10-02.md` was merged here and is now a pointer.
The owner-facing account of how this was reached is `Transient/barkwarden_readout_2026-10-03.md`
(transient; this file is the authority).

Items: `SHRUBLAND_TREE_GUARDIAN_1` (closed, built `fd8b0b8d2`), `SWEETLINE_SCRATCHING_TREE_BUILD_1`
(the rubbing behaviour, owed), `LEANINGSCRUB_SWEETLINE_GUARDIAN_1` (this decision item), and
`TREE_GRAPHICS_OWNERSHIP_1` (tree art pick). Mod: `mandrake.rm.leaningscrub`
(`src/RimMandrake/LeaningScrub/`), shipped inside the composed `mandrake.rm.biomes`.

## 0. Summary

- **The tree** (`RM_SweetlineTree`) is an ancient named giant. A **rare map step** plants one or
  two on a Leaning Scrub map (§8). It cannot be felled by Cut or Harvest, only by damage.
- **The wool comes from animals, not from giants alone.** Any animal that grows a shearable coat
  now and then walks to a sweetline tree and **rubs its coat off** against the bark: an
  auto-shearing spot, *"just a really wonderfully scratchy tree they like"* (§3). Most of the coat
  drops on the ground at the trunk as that animal's own product; the rest felts into the bark.
- **Two ways to take wool, both worth it** (§4). The **free drop** stays generous: the rubbed-off
  coats on the ground, plus the tree's own shed of felt (5 every 5 days, which keeps going after
  a harvest). The **harvest** strips the **felted mass of everything rubbed in**, which with the
  bark's resins is a uniquely comfortable blend: the existing item `RM_SweetlineWool` (§5).
- **The bark-wardens** (`RM_Barkwarden`, 2–3 per tree) sleep **visibly** against the trunk:
  *"Roosting in the crown of <tree name>."* Walking up is not hostile; they watch. Harvest work and
  wounds fill a **disturbance meter** with two warnings, and at full they drop on the harvester,
  about halfway through the job. The tree forgives in about 5 days (§6, §7). Built `fd8b0b8d2`.
- **Owed:** the rubbing behaviour, the felt store and harvest bonus, the comfort effect, the
  placement genstep, text fixes, art and live proof (§11, about 500 lines of C# in total).

## 1. Rulings

| # | ruling | when, how | recorded |
|---|---|---|---|
| R1 | One **generic** guardian species, not per-tree uniques | card 2026-09-21 | `SHRUBLAND_TREE_GUARDIAN_1` |
| R2 | Name **bark-warden**, defName `RM_Barkwarden`, `RM_` tier in the Leaning Scrub mod (invented name, Q11a) | card 2026-09-25; Q11a 2026-09-26 | same |
| R3 | Gated by the **"Named sweetline trees"** Mod Setting | item criteria | `LEANINGSCRUB_SWEETLINE_GUARDIAN_1` |
| R4 | Nothing strikes or vanishes without a **readable sign** | owner 2026-09-29/30 | `CLAUDE.md` |
| R5 | **Walking up is not hostile**; the wardens watch | card 2026-10-03 | ledger note on this item |
| R6 | **Harvesting wakes them gradually**: stirring, restless, then the drop on the harvester **about halfway** | card 2026-10-03 | same |
| R7 | A harmed tree **forgives in about 5 days**, adjustable | card 2026-10-03 | same |
| R8 | Wardens **visible, asleep against the trunk**, "Roosting in the crown of <tree>" when selected | card 2026-10-03 | same |
| R9 | The **disturbance meter is the only robbed-nest effect** (no extra sulk after a harvest) | 2026-10-03 | same |
| R10 | **Wool source:** any animal that produces a wool-like shearable product periodically comes to the tree and rubs it off; an auto-shearing spot, any animal, whatever its material | typed, 2026-10-03 | same |
| R11 | **Prize = both:** the free drop stays generous, and a harvested tree keeps shedding | card 2026-10-03 | same |
| R12 | **Harvest** gathers the felted mass of everything rubbed into the bark; with the bark's resins it makes a uniquely comfortable material: the existing sweetline wool item, now a blend | typed, 2026-10-03 | same |
| R13 | **Placement:** a rare map step plants one or two sweetline trees on Leaning Scrub maps | card 2026-10-03 | same |
| R14 | The bark-warden **does not fly**; it climbs and drops | flyer rule, 2026-09-19 | this spec §6 |

## 2. The tree

**Fiction (ruled, biome sheet `arid_shrubland.md` §4):** huge, ancient, never small; grows only on
the sweetline; a surveyor's mark seen from a day's walk; every tree has a name and the roads run
tree to tree. Its bark is rough enough that every coated beast of the plain comes to scratch on it,
and the scratched-off coats, matted into the bark's resin, are the sweetline felt.

**As built** (`src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml`,
`thingClass RimMandrake.LeaningScrub.RM_Plant_Guarded`):

| field | value | note |
|---|---|---|
| HP / Flammability / Mass / outdoor beauty | 650 / 0.1 / 900 / 10 | flavour values, not a balance pass |
| Drawn size | 7.7–10 cells on a one-cell footprint | |
| growDays | 240 | the map step plants them fully grown (§8) |
| harvestWork | 4200 | the meter's timing is set against this (§7) |
| harvestedThingDef / harvestYield | `RM_SweetlineWool` / 20 | the base yield; the felt store adds to it (§4) |
| harvestMinGrowth / harvestAfterGrowth | 0.40 (TreeBase) / 0.05 | regrow to the next harvest: 240 × 0.35 = **84 growing days** |
| Cut vs Harvest | the same act; neither fells it | engine §12 E1 |
| Kills it | damage only: weapons, explosives, fire | |
| Comps | `RM_CompSweetlineStation` (name, History, shed, visitors) and `RM_CompGuardianRoost` (wardens, meter) | `Source/RM_SweetlineStation.cs`, `Source/RM_SweetlineGuardians.cs` |

**Name and History (built).** Each tree rolls a unique name on first spawn
(`RM_NamerSweetlineTree`, register draft in `leaningscrub_sweetline_name_register_2026-10-03.md`)
and keeps up to 12 dated History entries: named, shed, struck by, visitors, warden events. The
rubbing adds a "scratched" entry (§3).

**Not in `wildPlants`, on purpose.** A landmark is not scatter; it reaches maps only through the
map step in §8 (or dev spawn).

## 3. The scratching tree: animals rub their coats off

**Ruling R10.** Any animal that produces a shearable, wool-like product comes to the tree now and
then and rubs it off. It is the animal's own idea; nobody orders it.

**Who rubs.** Any spawned animal (wild or tame, any faction) whose race carries vanilla
`CompShearable` (or a subclass), whatever its `woolDef` is: sheep and alpaca wool, muffalo and
bison coats, bantha and nerf wool in the campaign layer, the Sump's brommet wool, and anything a
mod adds. Milk (`CompMilkable`) and eggs are not coats and never count. Humanlikes never rub.

🔴 **Engine fact that shapes the build (E2): a wild animal grows no wool in vanilla.**
`CompHasGatherableBodyResource.Active` returns false when `parent.Faction == null`, and
`CompTick` only grows `fullness` while Active. So a wild bantha's coat sits at 0 forever and a wild
animal would never have anything to rub off. The free `RM_` Leaning Scrub roster has **no**
shearable animal at all; the campaign layer adds wild `RSW_Bantha` (100 wool / 25 days) and
`RSW_FeralNerf` (40 / 30 days). So:

- **Tame and other-faction animals** use vanilla `fullness` as-is.
- **Wild animals** need their coat to grow. Built as a **Harmony postfix on `CompShearable.Active`**:
  for a pawn with no faction, return true when the vanilla checks other than faction pass (life
  stage `shearable`, not a shambler, not suspended). A side effect, wanted: wild animals then show
  vanilla's "Wool growth: N%" inspect line, which is the readable sign of an animal that is due a
  scratch. Vanilla `WorkGiver_Shear` only takes the player's own animals, so the player still
  cannot shear wild ones in place. The patch is behind the scratching setting (§9). It runs in the
  per-tick `Active` getter, so it must be a field test and a cached settings bool, nothing more.

**When it goes.** A `ThinkTreeDef` inserted at **`Animal_PreWander`** (Core `Animal.xml`,
engine E4): after needs, mating, trained jobs and the tame "useful things" block, and before idle
wandering. It applies to wild and tame animals alike. Inside it, a
`ThinkNode_ChancePerHour_Constant` (MTB about 6 hours) and then `RM_JobGiver_ScratchOnSweetline`,
which returns a job only if all of these hold:

- the pawn has a `CompShearable` with `Fullness ≥` the "coat ready" threshold (default 0.8);
- a spawned sweetline tree is within 60 cells, and `pawn.CanReach` it (`TraverseParms.For(pawn)`
  already honours fences for fence-avoiding animals, engine E5, so a penned herd only reaches a
  tree inside its pen);
- for a player animal, the trunk's touch cell is in its allowed area, and it is not roped;
- the tree is not in the **awake** stage (§7). Wardens never target animals (engine E6), but an
  animal walking into a fight looks wrong.

**The job** `RM_JobDriver_ScratchOnSweetline`: go to touch the trunk, then about 600 ticks of
rubbing (the tree's harvest effecter or a dust fleck, posture maintained). At the end:

1. `amount = RoundRandom(woolAmount × fullness)`.
2. **Ground share** (default 80%) of `amount` drops beside the trunk as the animal's own `woolDef`,
   with `GenPlace.TryPlaceThing(Near)`. Unforbidden for player animals; whatever vanilla does for
   wild-dropped items otherwise.
3. **Felt share** (the remaining 20%) is banked in the tree's felt store at the felt rate (§4).
4. `fullness = 0` by direct field write (`AccessTools.FieldRefAccess` on the protected
   `fullness`). **Do not call `Gathered(doer)`** (engine E3): it rolls the doer's
   `AnimalGatherYield` stat, places the product at the doer, and logs an error when the comp is not
   Active, so it is a colonist-shearing API, not a self-shearing one.
5. History: "<animal kind> scratched against the bark" (at most one line per day per tree, so a
   herd does not flood the 12 entries). A short message for the player's own animals is not
   wanted; the pile at the trunk is the sign.

**What it never does.** It never raises the disturbance meter (not plant work, not a person),
never involves the wardens, and never needs a colonist. A colony that keeps a woolly herd near a
tree has an auto-shearer that keeps 80% of the wool and turns 20% into felt for the harvest.

## 4. Ground drop vs harvest: what each path gives, and the rates

**Three sources, one place (the trunk):**

| path | what you get | guarded? | rate |
|---|---|---|---|
| **Rubbed-off coats** (§3) | each animal's own product (sheep wool, bantha wool …), 80% of its coat | no | one animal's whole coat per rub, as often as its coat regrows (sheep 10 days, muffalo 15) |
| **The tree's shed** (built) | `RM_SweetlineWool` felt, 5 at a time | no | 5 every 5 days, about 60 per in-game year; keeps going after a harvest (R11, built `fd8b0b8d2` via the station's `everMature` flag) |
| **The harvest** (Harvest or Cut on the tree) | `RM_SweetlineWool` felt: base yield **plus the whole felt store** | yes: the wardens drop on the harvester about halfway (§7) | base 10–20 (vanilla `YieldNow`: growth and HP scaled) once per 84 growing days, plus the store |

**The felt store** (`feltStore`, a float on the tree, Scribed):

- Each rub banks `0.2 × amount × feltPerCoatUnit`, with `feltPerCoatUnit` default **0.25**
  (felting is lossy: four units of rubbed coat make one of felt).
- Cap **120** felt, so an untended tree cannot hoard forever.
- Paid out at harvest through `ThingComp.GetAdditionalHarvestYield()` on the roost or station comp
  (engine E7: `JobDriver_PlantWork` calls it on every comp when the plant is harvestable), then
  reset to 0 in `PlantCollected`. No change to `YieldNow`.
- Shown on the tree's inspect pane: "Felted into the bark: 37 (harvestable)".

**Worked numbers, per 84-day harvest cycle (defaults):**

| situation | free (ground) | harvest |
|---|---|---|
| No coated animals (free `RM_` roster, no herd) | about 84 felt from the shed | 10–20 felt |
| Wild campaign banthas, say 2 rubbing each 25 days | the shed, plus about 540 bantha wool | 10–20 + about 34 felt |
| A tame herd of 6 sheep fenced with the tree (45 wool, 10 days) | the shed, plus about 1,800 sheep wool | 10–20 + **about 113 felt** (cap 120) |

**Why both are worth it.** The ground path is safe, generous and never stops: the shed alone is
about one felt a day, and a herd's coats arrive sheared for free. The harvest is the only way to
get felt **in bulk**, and its size is something the player builds by keeping animals at the tree,
then pays for with a fight. A tree with no animals gives a small harvest, which is the honest
consequence of R10 (the wool is the animals'). All numbers here are tunables in the comp props or
settings (§9), set to these values on first build.

## 5. The material: sweetline felt, a blend

**Ruling R12.** The harvest is "the felted mass of everything rubbed into the bark", which with the
bark's resins becomes a uniquely comfortable material. It is the **existing item**
`RM_SweetlineWool` (`Defs/ThingDefs_Items/RM_SweetlineTree_Items.xml`, `ParentName WoolBase`), now
described as a blend. One item serves both the shed and the harvest; there is no per-animal felt.

- **Keeps:** fabric stuff (sharp 0.42, heat armour 1.3, cold 36, heat 14), value 5.5, rare in
  random generation (0.04), the smother-blanket recipe (15 felt + 40 fuzz fiber,
  `RM_SmotherCraft.xml`).
- **Label:** "giant-wool" names a source that is no longer the source. Working label **"sweetline
  felt"** in the rebuilt description; the defName stays `RM_SweetlineWool` (§13 asks the owner to
  confirm the word).
- **Description (to write):** coats of every woolly beast that scratches on the bark, matted and
  cured in the tree's resin into a dense, soft felt; warmer than fleece and softer against the skin
  than anything sheared.

**"Uniquely comfortable" needs code (engine E8).** Vanilla has no comfort from a material: the
`Comfort` StatDef has only a quality part, nothing reads the stuff, and apparel has no comfort
stat. Two cheap real channels, both built:

1. **Furniture:** a `StatPart_RM_StuffComfort` appended to `StatDef Comfort` by a PatchOperationAdd,
   adding **+0.10** when the thing's Stuff carries `RM_StuffComfortExtension` (on
   `RM_SweetlineWool`). Matters for fabric-stuffed seats such as the armchair.
2. **Apparel:** a `ThoughtDef` with a `ThoughtWorker` modelled on vanilla
   `ThoughtWorker_HumanLeatherApparel`: "Sweetline felt against the skin" **+2 mood** while wearing
   at least one piece made of it. Not stacked per piece.

## 6. The bark-warden

**Built** `fd8b0b8d2`: `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_Barkwarden.xml`
(ThingDef, PawnKindDef and the `RM_RoostDefence` MentalStateDef).

**Visual brief** (the source for any future art prompt): a knuckle-walking climber about the mass
of a large dog, long-armed, hook-clawed, flat wide head, coat the silver-grey of the felt it sleeps
in. It sleeps curled against the trunk; "in the crown" is fiction, because a pawn occupies a ground
cell.

| aspect | value (built) |
|---|---|
| Body size / health scale / speed | 1.2 / 1.6 / 4.8 (medium band; the biome bans residents of 1.5–3.5) |
| Attacks | bite 15; two hook-claws 12 with a stun-6 surprise opener (the drop); headbutt 6 |
| Armour | 0.20 sharp / 0.15 blunt |
| combatPower / MarketValue | 110 / 420. A full tree (2–3) is 220–330: one colonist alone loses, two with guns win |
| Diet | `OmnivoreAnimal`, **not a predator** (a predator would leave the tree and hunt pets) |
| Wildness / trainability | 0.95 / Advanced; `manhunterOnDamageChance` 1.0 |
| Flight | none (R14): no `MaxFlightTime`, `canFlyIntoMap` false |
| Dormancy | `CompCanBeDormant` (`startsDormant`, job dormancy, Food and Rest frozen); `CompWakeUpDormant` with `wakeUpOnDamage` and the radius wake **off** |
| Body | interim reskin of vanilla Cougar art (`Things/Pawn/Animal/Cougar/Cougar`) |
| Spawning | only from a tree's roost; **never** in any `wildAnimals` table |
| Drops | the reskinned body's meat and leather. **No felt, no special drop**: if killing them gave felt, the tree would be scenery |
| Sound | breath and claws, no roar ("danger announces itself by posture, never by voice") |

**Who it can attack (engine E6).** Its rage is `RM_MentalState_ScopedAggression`, hostile to one
pawn and never to a faction. `JobGiver_Manhunter`'s target validator only accepts tool-users and
humanlikes, so it can never attack an animal: rubbing herds and pets are always safe.

**Life cycle (built):**

- **Roost:** `RM_CompGuardianRoost.PostSpawnSetup` spawns 2–3 (capped by the per-tree setting)
  adult, factionless wardens within 3 cells, asleep, bound to the tree. On an existing save the
  refill fills them.
- **Refill:** one dead, tamed or lost slot refills every **30–60 days**, so clearing a tree by
  force buys about one harvest. History: "a bark-warden has taken up the crown". Never silent.
- **Kept asleep:** the warden's own 250-tick check puts a sleeper the animal think tree woke back
  to sleep (whether a lordless wild animal leaves `Wait_AsleepDormancy` on its own is UNMEASURED
  live; this covers both answers).
- **Tamed:** ordinary Advanced animal; inert as a guardian; its slot refills. Taming one does not
  tame the tree: a harvest by its handler still counts.
- **Tree dies:** its wardens wake and become ordinary wild animals ("…have lost their tree"); they
  re-home once a day to a vacant tree within 60 cells, never vanish, never despawn.
- **Breeding:** asleep with frozen needs they do not breed; a free (tree-less) one breeds as any
  wild animal. Not a defect.
- **Hunting a sleeper:** dormant pawns are skipped by auto-targeting and threat detection (engine
  E9); whether a Hunt order can target one is UNMEASURED. Shooting one wakes it (vanilla
  `wakeUpOnDamage`) and it takes ordinary revenge on the shooter.

## 7. Activation: the disturbance meter

Each tree's roost comp keeps `disturbance` from 0 to 1 (Scribed). Built in
`RM_CompGuardianRoost`; numbers are the shipped comp props.

| act | counts? | amount | caught by |
|---|---|---|---|
| Harvest/Cut work on the tree by a person | yes | +0.10 per 250 ticks × harvest setting | the warden's 250-tick check (plant work applies no damage, engine E1) |
| That harvest completing | yes | +0.25 × harvest setting | `RM_Plant_Guarded.PlantCollected` |
| Violent damage to the tree | yes | +0.05 per damage point (two rifle shots wake them) | roost `PostPostApplyDamage` |
| Fire or damage with no person behind it | yes | as above | they wake **watchful**, with nobody to attack |
| Damage to a sleeping warden | wakes that one | instant | vanilla `wakeUpOnDamage`, then revenge |
| Walking, standing, camping near the tree | **no** (R5) | 0 | raises the watching sign only |
| Picking up shed felt or rubbed-off coats | **never** | 0 | |
| Animals doing anything, including rubbing (§3) | **never** | 0 | instigator must be a tool-user or humanlike |
| Lingering, **only if** the opt-in setting is on | yes | +0.02 per check | off by default |

**Stages (R6).** At 0.3 **stirring**: a caution message, "The bark-wardens of <tree> are stirring.
Whoever is working the tree should stop." At 0.6 **restless**: "…are about to drop." At 1.0
**awake**: every bound warden wakes and enters `RM_RoostDefence` against the last harm-doer, anchor
the tree, disengage at 18 cells, about 2500 ticks; message "…drop on <pawn>." plus a History entry.
No letter. At harvest speed 1 the meter fills at about 2500 of the 4200 work ticks, around 60% of
the job, which is "about halfway".

**After.** Wardens return to the trunk and stay **watchful** (leashed within 6 cells) until the meter
falls below 0.3, then sleep again: "…climb back into the crown." The meter drains at
`1 / forgiveness days` per day while nobody is raging (R7, default 5 days).

**Signs (R4, R8), all built:** the sleepers are visible; their inspect line is "Roosting in the
crown of <tree name>"; the tree reads "Bark-wardens roost here (3). Calm."; a disturbance bar gizmo
with marks at 30% and 60%; a "watching <pawn>" line and mote when a person is within 9 cells.

**The robbed nest (R9):** nothing beyond the meter. A harvested tree is not touchier afterwards.

## 8. Placement: the map step

**Ruling R13:** a rare map step plants one or two sweetline trees on Leaning Scrub maps.

- **Hook (engine E10):** `BiomeDef.extraGenSteps` is concatenated onto the map generator's steps
  for every map of that biome. Add a `GenStepDef RM_SweetlineTrees` to `RM_LeaningScrub`'s
  `extraGenSteps`. The frozen `RUT_` twin is not touched.
- **Order 910:** after `Plants` (900) so the trunk cell can be cleared of scrub, before `Animals`
  (1200). Core's ordering comment puts non-critical generation (geysers, plants, animals) at
  900–1200.
- **`RM_GenStep_SweetlineTrees`** (about 70 lines). With chance **25%** (setting) the map gets
  trees; then 1 tree, or 2 with chance 30%. Cell rules: standable, not water, fertility above 0,
  at least 15 cells from the map edge, no building or `UsedRect`, and **at least 40 cells from the
  other tree** so two roosts' 18-cell rage radii never overlap. Up to 200 random tries, then give
  up silently (a map without a tree is the normal case).
- **Spawn:** `ThingMaker.MakeThing(RM_SweetlineTree)`, set `Growth = 1` and a large `Age` (an
  ancient giant), clear plants on the cell, `GenSpawn.Spawn`. Spawning runs the station comp
  (name, History "named") and the roost comp (wardens, asleep). Pawns spawning during map
  generation is normal (`GenStep_Animals` does it).
- **Not retroactive.** It runs only when a map is generated. An existing home map gets no tree;
  the dev spawn remains the way to place one by hand.
- **Off** when "Named sweetline trees" is off or the placement chance is 0.

## 9. Mod Settings

All under LeaningScrub's existing **"Named sweetline trees"** group (`RM_LeaningScrubMod.cs`,
`RM_LeaningScrubSettings`), which gates everything here (R3). Defaults equal shipped behaviour.

| setting | range | default | at off / minimum | state |
|---|---|---|---|---|
| `sweetlineStationsEnabled` "Named sweetline trees" | bool | on | no names, History, shed, wardens, rubbing or placement | built |
| `sweetlineVisitorsEnabled` + `sweetlineVisitIntervalDays` | bool, 2–30 | on, 8 | no road-folk visits | built |
| `sweetlineGuardiansEnabled` "Bark-wardens guard sweetline trees" | bool | on | no new wardens; existing ones wake as ordinary wild animals, none removed | built |
| `sweetlineGuardianMaxPerTree` | 0–4 | 3 (each tree rolls 2–3) | 0: a tree spawns and refills none | built |
| `sweetlineHarvestDisturbance` | 0–3× | 1× | 0: harvest is never harm; wounds still are | built |
| `sweetlineForgivenessDays` | 1–30 | 5 | drain rate of the meter | built |
| `sweetlineProximityCharge` "also rouse at anyone who lingers" | bool | **off** | opt-in only (R5 rules walk-up harmless by default) | built |
| `sweetlineScratchingEnabled` "Animals scratch their coats off on sweetline trees" | bool | on | no rubbing, and the wild-coat patch (§3) is inert | built |
| `sweetlineCoatReady` "Coat fullness before an animal goes to scratch" | 50–100% | 80% | | built |
| `sweetlineFeltShare` "Share of a rubbed coat that felts into the bark" | 0–50% | 20% | 0: rubs give only ground wool, the harvest is base yield only | built |
| `sweetlineTreeMapChance` "Chance a new Leaning Scrub map has sweetline trees" | 0–100% | 25% | 0: no trees on new maps (labelled "affects newly generated maps; not worldgen") | built |

## 10. Art

| subject | state | plan |
|---|---|---|
| Tree, 14 variants A–N (`Textures/Things/Plant/RM_SweetlineTree/`) | shipped | `TREE_GRAPHICS_OWNERSHIP_1` waits on the owner's pick among recovered candidates; nothing here changes it |
| Bark-warden | interim Cougar reskin | silver-grey long-armed climber per the §6 brief; invented species, so no canon entry and no canon target. New art only after the owner has seen the reskin in a review save |
| `RM_SweetlineWool` (felt) stack icon | **missing**: the def points at `Things/Item/Resource/RM_SweetlineWool` and no such file exists in the mod | search artpipe first (`artpipe_state.py find sweetline`), then queue a matted silver-grey felt bundle |
| `RM_SweetlineToken` | missing, placeholder | already owed by `LEANINGSCRUB_SWEETLINE_VISITORS_1` |
| Rubbing | no new art | the tree harvest effecter or a dust fleck; the dropped coats are vanilla items |

## 11. Build plan, sized

**Built** (`fd8b0b8d2`, `SHRUBLAND_TREE_GUARDIAN_1`, in `mandrake.rm.leaningscrub`, not the kit):
`Source/RM_SweetlineGuardians.cs` (roost comp, warden comp, dormancy comp, `RM_Plant_Guarded`,
disturbance gizmo), `Defs/ThingDefs_Races/RM_Barkwarden.xml`, the roost comp on the tree, 5
guardian settings, the shed continuing after a harvest. Live proof is owed.

**Owed** — one FOUNDRY pass, about **500 lines of C#** in LeaningScrub plus XML; filed as
`SWEETLINE_SCRATCHING_TREE_BUILD_1` (rubbing) and the rest under it or as siblings.
`RM_LeaningScrub.csproj` lists compile items explicitly, so every new `.cs` needs its
`<Compile Include>` line.

Pieces 1-5, 8 (the three scratching settings), 9 and 10 are **built** (`SWEETLINE_SCRATCHING_TREE_BUILD_1`,
`Source/RM_SweetlineScratching.cs`, `Defs/JobDefs/RM_SweetlineScratching.xml`). Two deliberate
departures: the felt store resets when it is paid out (in `GetAdditionalHarvestYield`), not in
`PlantCollected`, so a failed harvest roll keeps it; and wild coats grow only while a sweetline tree
stands somewhere in the running game. Piece 7 (map step) is built too (`SWEETLINE_TREE_MAP_STEP_1`, `Source/RM_GenStep_SweetlineTrees.cs`).
Piece 6 (comfort) is built (`SWEETLINE_FELT_COMFORT_BUILD_1`, `Source/RM_SweetlineFelt.cs`, settings
`sweetlineFeltComfortEnabled` / `sweetlineFeltApparelEnabled`). §11 is now fully built; live proof is owed.

| # | piece | where | size |
|---|---|---|---|
| 1 | Harmony postfix on `CompShearable.Active` for wild animals (§3) | new `Source/RM_SweetlineScratching.cs` | ~30 |
| 2 | `RM_JobGiver_ScratchOnSweetline` + `ThinkTreeDef` at `Animal_PreWander` + `JobDef` | same + `Defs/ThinkTreeDefs/`, `Defs/JobDefs/` | ~90 + XML |
| 3 | `RM_JobDriver_ScratchOnSweetline` (rub, drop, bank, reset fullness by field ref, History) | same | ~110 |
| 4 | Map-level tree registry (cached list of spawned sweetline trees, so the job giver and the postfix never scan) | same, or the station comp's spawn/despawn | ~40 |
| 5 | Felt store on the station comp: bank, cap, inspect line, `GetAdditionalHarvestYield`, reset on `PlantCollected`, Scribe | `RM_SweetlineStation.cs`, `RM_Plant_Guarded` | ~60 |
| 6 | Comfort: `StatPart_RM_StuffComfort` + PatchOperationAdd on `StatDef Comfort` + `RM_StuffComfortExtension`; `ThoughtWorker` + `ThoughtDef` for felt apparel | new `Source/RM_SweetlineFelt.cs`, `Patches/`, `Defs/ThoughtDefs/` | ~70 + XML |
| 7 | `RM_GenStep_SweetlineTrees` + `GenStepDef` + `extraGenSteps` entry on `RM_LeaningScrub` | new `Source/RM_GenStep_SweetlineTrees.cs`, `Defs/` | ~70 + XML |
| 8 | Four settings (§9) | `RM_LeaningScrubMod.cs` | ~30 |
| 9 | **Text fixes** (below) | XML and C# strings | small |
| 10 | Validation bars in `src/RimMandrake/LeaningScrub/validation.py` and the functional script | | |

**Text that is now false and must be rewritten in the build (R10, R12):**

- `RM_SweetlineTree` description: "scarred smooth … where the biome's giants have rubbed …; the
  bark sheds their snagged wool". Rewrite: every coated beast of the plain scratches here; the
  bark holds what they leave as felt. Keep the warden sentence.
- `RM_SweetlineWool` label "giant-wool" and description ("where the biome's giants have rubbed
  their flanks", "thick and oily with the animal that grew it"). Rewrite per §5.
- The shed's History line "shed N giant-wool snagged from passing giants."
  (`RM_SweetlineStation.cs`) and its inspect line "Snagged giant-wool …". Rewrite: "let go N
  sweetline felt".
- The tree XML's comment "a trickle beside the 20-hank harvest" and the station header's
  "snagged-wool timer": describe the shed as the generous free path (R11).
- The same wording on the frozen `RUT_SweetlineTree` / `RUT_SweetlineWool` in
  `src/RimUtinni/AshkarrFlora/` stays, because that mod is frozen until its world def is deleted.

**Quicktest** (minimal list + creaturebehaviors + leaningscrub, all DLC), extending the guardian
build's script:

1. Generate a Leaning Scrub map with the chance at 100%: 1–2 full-grown named trees, wardens asleep.
2. Dev-spawn a tame sheep at full coat in a pen with the tree: it walks over, rubs, 36 wool on the
   ground, about 2 felt banked, coat 0, History line, meter unchanged.
3. Dev-spawn a wild muffalo: "Wool growth" shows and rises; at 80% it scratches.
4. A penned sheep with the tree outside the pen never goes.
5. Harvest: the stages fire, the drop lands around 60%, the yield is base plus the store, the store
   resets, the shed continues.
6. Felt armchair comfort +0.10; a colonist in felt apparel has the +2 thought.
7. Save and load mid-rub and with a non-empty store; flip each new setting.
8. The guardian build's own owed checks: still asleep after 2 days, Hunt on a sleeper, burn, kill
   the tree, tame one.

## 12. Engine facts this spec rests on

Read from the decompiled 1.6 source (RimSage), 2026-10-03 unless dated otherwise.

- **E1** `PlantProperties.HarvestDestroys => harvestAfterGrowth <= 0`; this tree's 0.05 makes it
  false, so `Plant.PlantCollected` resets growth to 0.05 and keeps the tree. `JobDriver_PlantWork`
  calls `PlantCollected` for Harvest and Cut alike, and harvest work applies no damage, so harvest
  in progress is only visible by looking at the worker's job (2026-10-02).
- **E2** `CompHasGatherableBodyResource.Active` is false when `parent.Faction == null`, and
  `CompTick` grows `fullness` only while Active (`1 / (interval × 60000)` per tick ×
  `BodyResourceGrowthSpeed`). `CompShearable.Active` adds the life-stage `shearable` and shambler
  checks. **Wild animals grow no wool.**
- **E3** `Gathered(Pawn doer)` rolls `doer.GetStatValue(AnimalGatherYield)`, places the product at
  `doer.Position`, logs an error if not Active, and zeroes `fullness` (a protected field). Its only
  caller is `JobDriver_GatherAnimalBodyResources`.
- **E4** Core `Animal.xml` has two modder hooks, `Animal_PreMain` (after lord duties, before the
  wild-animal leave rules) and `Animal_PreWander` (after needs, mating and trained jobs, before idle
  wandering); both run for wild and tame animals.
- **E5** `TraverseParms.For(pawn)` sets `fenceBlocked = pawn.ShouldAvoidFences`, so `CanReach`
  respects pens.
- **E6** `JobGiver_Manhunter.FindPawnTarget` accepts only `intelligence >= ToolUser`: a scoped-rage
  warden can never target an animal (2026-09-21).
- **E7** `JobDriver_PlantWork` adds `ThingComp.GetAdditionalHarvestYield()` from every comp when
  the plant is `HarvestableNow`, before `PlantCollected`. `Plant.YieldNow()` is virtual.
- **E8** `StatDef Comfort` carries only `StatPart_Quality`; no stat part reads the stuff, and
  apparel has no comfort stat. `ThoughtWorker_HumanLeatherApparel` is the vanilla pattern for a
  mood effect from worn apparel's material.
- **E9** Dormant pawns are skipped by `AttackTargetFinder`, `GenHostility` threat checks and
  `DangerWatcher`; `CompCanBeDormant.ShowZs` is false for pawns, so the visible sign is ours
  (2026-10-02).
- **E10** `MapGenerator` concatenates `map.Biome.extraGenSteps` onto the generator's steps;
  `GenStepDef` order puts plants at 900 and animals at 1200.
- **E11** `GenHostility.HostileTo` consults `MentalState.ForceHostileTo` before faction logic, which
  is why a scoped rage works on a factionless animal (2026-09-21).

## 13. Open, not blocking

1. **The word for the material.** "giant-wool" no longer fits R10; the build ships "sweetline felt"
   as a working label unless the owner names it.
2. **Should the thunderstep grow a coat?** `RSW_ShrublandGiant` has no `CompShearable`, so under R10
   it does not rub. One comp line (campaign layer) would make the giants scratch here too. Not ruled.
3. **Body for the bark-warden art**: the Cougar reskin is interim until the owner sees it.
4. `TREE_GRAPHICS_OWNERSHIP_1`'s art pick and `LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1`'s three
   naming answers are their own items.
