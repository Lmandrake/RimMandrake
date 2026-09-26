# Sweetline guardian — generic guardian species spec

**Item:** `SHRUBLAND_TREE_GUARDIAN_1` · **Ruling:** owner, 2026-09-21, option (b) — one
generic `PawnKindDef` that spawns near any sweetline tree and guards it.
**Status:** DESIGN — no def, XML or C# written. Build is a separate item.

## 0. Summary

- **What:** a medium-band arboreal climber that roosts in the crown of a sweetline tree
  (`RUT_SweetlineTree`), lines its bower with the giant-wool snagged on the bark, and drops on
  any tool-user that comes within ~9 cells of the trunk. Two or three per tree. Wild
  (faction-null), huntable, tameable but wild (0.95). It does not fly.
- **Mechanism:** the `SHRUBLAND_GIANT_ENRAGE_1` shape, generalised from "guard a calf" to
  "guard a Thing" — a comp on the guardian scans a radius around its HOME TREE and pushes a
  scoped `MentalState_Manhunter` subclass that is hostile to ONE intruder and ends when that
  intruder is beyond twice the radius from the tree. Two more small pieces: a roost comp on the
  tree that spawns and re-spawns its guardians, and an `Animal_PreMain` think-tree insert that
  walks a strayed guardian home. **Needs C#** — three small classes in
  `mandrake.rm.creaturebehaviors`, each a generalisation of code already in that assembly. No
  Harmony, no patch of any vanilla def (§2).
- **Tier (RULED, card 2026-09-25 + Q11a):** species def `RM_Barkwarden` in the Arid
  Shrubland's own `RM_` biome mod; mechanism `RM_` in the kit; the binding (the roost comp on
  the tree and the biome wiring) `RUT_` in AshkarrFlora / UtinniPatches (§7).
- **Names (RULED, card 2026-09-25):** defName `RM_Barkwarden`; player label **"bark-warden"** (§7).
- **Owner questions:** §11 — the wool-harvest pace reconciliation and the tunnel-snake
  body-size flag; tier and name are ruled.

## 1. What the creature is

The tree is the only vertical in a biome that is a knee-high canopy horizon to horizon. Its
crown is the one place on the plain with sightlines, shade and a hanging larder — the
giant-wool the bark snags — and the kessrik is what took it. A knuckle-walking climber about
the mass of a large dog, long-armed, hook-clawed, with a flat wide head and a coat the
silver-grey of the wool it sleeps in; it is invisible in the crown until it is not. It eats
what the tree brings it (bark-lickers, the runway animals that come to the trunk, fuzz at the
foot of the tree when nothing else comes) and never goes far, because the tree is the whole
of its territory: a kessrik more than a dozen cells from its trunk is a kessrik walking back.

What it does to you: nothing, until you come within nine cells of the trunk. Then one drops
from the crown onto you with no warning, and the others follow. Back off past eighteen cells
and it stops — it wants you gone, not dead — and climbs back up. Cut or harvest the tree and
every kessrik in it comes down at once on whoever is holding the tool. That is the whole
creature: **a valuable hanging harvest, in a dangerous place**, where the danger is
proportional, local, and readable — you can see the tree from a day's walk, and every Jawa
knows what lives in it.

Register notes, for the description text: the wild here is quiet and "danger announces itself
by posture, never by voice" (§5 of the biome sheet) — the kessrik gives no call before the
drop, and its `soundAngry` should be breath and claws, not a roar. Slots in the size ladder:
medium, the interface-killer band, alongside Anooba and Massiff; it is the one medium
predator that hunts DOWN from above rather than across the interface, which is the niche the
ladder leaves open ("come from the sky and dive" is the fliers' route; this is the canopy's).

## 2. Territorial mechanism — how "aggressive only near the tree" is actually done

RimWorld has no territory field. Four real mechanisms were checked against the decompiled 1.6
engine this pass (RimSage, 2026-09-21) before choosing; the first three are rejected with the
measured reason.

**(i) The hive pattern — `CompSpawnerPawn` + a hidden hostile faction + a defend lord.**
REJECTED. `CompSpawnerPawn.TrySpawnPawn` generates the pawn with `parent.Faction` and ALWAYS
files it into a lord: `(Lord ?? CreateNewLord(parent, aggressive, Props.defendRadius,
Props.lordJob)).AddPawn(pawn)`, where `CreateNewLord` is
`LordMaker.MakeNewLord(byThing.Faction, Activator.CreateInstance(lordJobType, new
SpawnedPawnParams{…}))` (RimWorld/CompSpawnerPawn.cs l.140–154, l.263–290). A plant has no
faction and no `lordJob` type exists that takes `SpawnedPawnParams` except the hive and
mechanoid ones, so on a tree this either throws or builds a faction-null hive lord. And a
faction-null pawn is hostile to nobody — `GenHostility.HostileTo(Thing, Thing)` falls through
every special case to `if (a.Faction == null || b.Faction == null) return false`
(RimWorld/GenHostility.cs l.9–98, re-read this pass) — so the defend-point duties'
`JobGiver_AIFightEnemies` would never find a target. Giving the guardian a hidden
permanent-enemy faction instead (Insect-style) makes it hostile to every colonist on the whole
map, untameable, and an active threat for `DangerWatcher` (`GenHostility.IsActiveThreatTo`
exempts only `LordJob_DefendAndExpandHive`, l.311–334). That is the exact opposite of
"aggressive only near the tree".

**(ii) `CompCanBeDormant` + `CompWakeUpDormant`** (what `RSW_TunnelSnake` uses). REJECTED as
the mechanism: it is a sleep switch, not a territory. It wakes into vanilla behaviour with no
leash and no scope, and a woken faction-null animal still attacks nobody.

**(iii) Vanilla Manhunter via the kit's `RM_CompPlantAlarm`** (`ROT_GUARDIAN_GROVES_1`):
damage or harvest on the plant pushes `MentalStateDefOf.Manhunter` onto every tagged responder
within 18 cells. REJECTED as the primary — `MentalState_Manhunter.ForceHostileTo` answers true
for every humanlike and every humanlike faction on the map (Verse/AI/MentalState_Manhunter.cs
l.13–35), so one harvest turns the tree's guardians into a map-wide manhunter pack that
chases your colonists home. Kept, in scoped form, as the harvest hook (below).

**(iv) A scoped manhunter subclass — CHOSEN.** This is `SHRUBLAND_GIANT_ENRAGE_1`, already
built, deployed and wired onto `RSW_ShrublandGiant`, with the anchor changed from "my calf"
to "my tree". Two engine facts carry it, and both are load-bearing:

1. `GenHostility.HostileTo(Thing a, Thing b)` consults `pawn.MentalState.ForceHostileTo(b)`
   BEFORE any faction logic (GenHostility.cs l.9–98: the mental-state check comes right
   after the dormancy, `hostileToAll` and trait tests; the faction-vs-faction comparison is
   the final fallthrough). A state whose `ForceHostileTo(Thing)` answers true for exactly
   one pawn makes the guardian hostile to that pawn and nobody else; `ForceHostileTo(Faction)`
   answering false means no faction ever goes to war over it. Symmetric for free: the
   intruder sees the guardian as hostile and may shoot back.
2. `ThinkTreeDef MentalStateNonCritical` routes manhunting through
   `ThinkNode_ConditionalMentalStateClass`, whose `Satisfied()` is
   `stateClass.IsInstanceOfType(mentalState)` — an instance check, so a SUBCLASS of
   `MentalState_Manhunter` inherits `JobGiver_Manhunter`'s whole chase-and-melee behaviour
   with no think-tree patch. (MEASURED 2026-09-20 by the enrage build, Verse/AI/
   ThinkNode_ConditionalMentalStateClass.cs l.19; not re-read this pass.)

And one fact that shapes what the guardian can attack at all: `JobGiver_Manhunter.
FindPawnTarget`'s validator is `x is Pawn && (int)x.def.race.intelligence >= 1` — ToolUser
or Humanlike only (RimWorld/JobGiver_Manhunter.cs l.79–84). **A kessrik can never target an
animal.** Your pets grazing under the tree are safe; so is every wild thing. "Defend them from
human-sized things" is what the engine gives, not something to build.

### The three pieces, all in `mandrake.rm.creaturebehaviors` (RM tier — names no species)

**A. `RM_TreeGuardianExtension` (DefModExtension on the race) + `RM_CompTreeGuardian`
(ThingComp on the race).** The comp holds `homeTree` (a `Thing`, `Scribe_References`). At
`CompTickRare` (250 ticks), if the home tree is spawned and the pawn is wild and not already
in a mental state: a bounded `GenRadial.RadialDistinctThingsAround` scan of `triggerRadius`
cells around the TREE (not the pawn — the pawn may be up the trunk or twelve cells off
grazing; the territory is the tree's). Same intruder filter as `RM_CompParentalEnrage.
FindIntruder`: ToolUser+ only, exempt same race, exempt the guardian's own faction (a tamed
one never rages at its handlers), skip psychologically-invisible, LOS optional and off. The
nearest qualifying pawn becomes `otherPawn` of a forced, force-wake `TryStartMentalState` of
`RM_TerritorialRage`. Cooldown per guardian `600` ticks — short on purpose: a loiterer inside
the radius gets charged again every ~15 in-game minutes, which is the pressure the loop needs.

Fields, with the shipped defaults for the kessrik: `rageState` (null = inert, as
`enrageState` is), `triggerRadius 9`, `disengageRadius 18` (explicit rather than 2×, so a
race can be given a tight trigger and a long grudge), `rageDurationTicks 2500`,
`cooldownTicks 600`, `leashRadius 12`, `rehomeSearchRadius 60`,
`onlyToolUserOrHumanlikeTriggers true`, `exemptSameRace true`, `exemptSameFaction true`,
`requireLineOfSight false`.

**`RM_TerritorialRage`** (MentalStateDef) with stateClass `RM_MentalState_TerritorialRage`.
It is `RM_MentalState_ParentalEnrage` with the anchor typed `Thing` instead of `Pawn`:
`ForceHostileTo(Thing t) => t == causedByPawn`, `ForceHostileTo(Faction) => false`,
`MentalStateTick` recovers the moment the target is dead, downed, despawned, or farther than
`disengageRadius` from the ANCHOR (the tree — measured from the tree, not the guardian,
because the guardian is the one doing the chasing). 🔑 Builder's call whether to hoist a
shared `RM_MentalState_GuardRage` base with `Thing anchor` and re-derive ParentalEnrage from
it, or write the sibling — but do not fork the disengage logic silently: one of the two must
call the other. Def block copies `RM_ParentalEnrage`: `category Aggro`, no `beginLetter` (no
warning is the ruling, same as the giant), `minTicksBeforeRecovery 600`, `recoveryMtbDays
0.05`, `stopsJobs true`, `recoverFromDowned true`, `recoverFromSleep false`, and no
ParentName.

**B. `RM_CompProperties_GuardianRoost` (ThingComp on the TREE, attached by the RUT flora
XML with `MayRequire="mandrake.rm.creaturebehaviors"`).** Fields: `guardianKind`
(PawnKindDef), `count` (IntRange, `2~3`), `respawnDays` (FloatRange, `8~14`),
`spawnRadius 4`, `stopIfInHomeArea true`, `homeAreaGraceDays 3`. Behaviour:
- `PostSpawnSetup(respawningAfterLoad: false)` → spawn the full complement. This fires on
  map generation and on wild regrowth alike (both reach `GenSpawn.Spawn`); on a save that
  already has trees it does NOT fire, and the top-up below fills them within one respawn
  interval instead, so existing maps get guardians without a special case.
- `CompTickRare` → prune the `guardians` list of dead/despawned; if fewer than `count` are
  alive and bound to me and the respawn timer has elapsed, spawn ONE and reset the timer.
- Spawn is `PawnGenerator.GeneratePawn(new PawnGenerationRequest(guardianKind, faction: null,
  fixedBiologicalAge: adult))` at `CellFinder.RandomClosewalkCellNear(parent.Position,
  spawnRadius)` — the shape `WildAnimalSpawner.SpawnRandomWildAnimalAt` uses (RimWorld/
  WildAnimalSpawner.cs l.109–161), no lord, no faction. Then set the new pawn's
  `RM_CompTreeGuardian.homeTree = parent`.
- Nothing about points, storyteller reproduction factor, dormancy or messages is copied from
  `CompSpawnerPawn`; a guardian spawning is silent (the biome's law).

**C. `RM_JobGiver_ReturnToRoost`** in a `ThinkTreeDef` with `<insertTag>Animal_PreMain
</insertTag>` — the kit's own `RM_ThinkTree_VerminBehaviors` pattern (`Defs/ThinkTreeDefs/`),
so no vanilla def is patched. In Core's `Animal.xml` that tag sits at l.99, AFTER the
`MentalStateNonCritical` subtree at l.72 (RimSage, this pass): a rage always outranks the
leash, which is the right order. `TryGiveJob` returns null unless the pawn carries the
extension, is wild, has a spawned home tree, and is farther than `leashRadius` from it; then
it is a `Goto` to a random standable cell within 3 of the trunk. Vanilla wander drifts it;
the leash pulls it back; `predator false` (§4) means nothing else drags it off.

**Harvest hook.** The tree also carries the kit's existing `RM_CompProperties_PlantAlarm`
with `tag SweetlineGuardian` and `radius 24`; the race carries `RM_AlarmResponderExtension`
with the same tag. One small change to `RM_CompPlantAlarm` is owed: an optional
`scopedRageState` field (MentalStateDef) — when set, a responder is pushed into THAT state
with `otherPawn = dinfo.Instigator` (damage) or the harvester (`Plant.PlantCollected(Pawn by,
…)`, RimWorld/Plant.cs l.621 — the only harvest seam; the tree's `thingClass` becomes a tiny
`RM_Plant_Alarming : Plant` whose override calls `TriggerAlarm(by)`), instead of vanilla
`Manhunter`. Default null keeps the rot grove exactly as it behaves today. Cutting the tree
(harvestWork 4200) is therefore a fight the whole way down, and a harvest job interrupted by
a rage simply resumes — until the player either clears the crown or gives up. That is the
loop.

**Cost.** One radial scan of radius 9 (≈250 cells) per guardian per 250 ticks, one list
prune per tree per 250 ticks. Trees are `wildClusterWeight 0.05`; a 250×250 shrubland map
carries a handful. Negligible.

## 3. Finding its tree at spawn; tree death

- **Roost-spawned (the normal case):** the roost comp sets `homeTree` at spawn. No search.
- **Spawned any other way** (dev spawn, a trader's cargo escaping, a tamed one going feral,
  a future incident): `homeTree` is null, so on its first rare tick the guardian comp runs a
  ONE-TIME search for the nearest thing carrying `RM_CompGuardianRoost` within
  `rehomeSearchRadius` (60) that has a vacancy (`guardians.Count < count.max`), and binds to
  it — the roost's list gains the pawn, so the roost stops re-spawning for that slot. If none:
  it is an ordinary wild animal — no rage, no leash, wanders, leaves the map when vanilla says
  so. The search is repeated at most once a day, never every rare tick.
- **The tree dies or is cut:** `homeTree` despawns → the same re-home rule, once. Guardians
  that find no vacant tree are simply free animals from then on. Nothing kills them, nothing
  makes them manhunt, nothing spawns a replacement (the roost comp died with the tree). The
  rage started by the cutting ends on its own rules (target gone or `rageDurationTicks`).
- **The tree burns** (`Flammability 0.1`): same as cut; the arsonist is `dinfo.Instigator`
  on the fire damage and gets the scoped rage via the harvest hook while it burns.
- **Tamed:** faction non-null → the comp goes inert (no scan, no leash), the roost prunes it
  on the next rare tick (it checks faction as well as death), and the slot re-spawns on the
  timer. A tamed kessrik is a normal Advanced-trainable animal from then on. Going feral
  again re-enters the "spawned any other way" rule.
- **Save/load:** both references are `Scribe_References`; a `homeTree` that fails to
  resolve reads as null and the re-home rule handles it.

## 4. Combat weight and numbers

**Band constraint first.** Biome ban 4 (linter-checkable): no resident creature in the LARGE
band, 1.5–3.5 bodySize. The guardian is therefore MEDIUM, capped at 1.4 — it makes the harvest
dangerous by numbers, an opener and a leash-bounded fight, not by mass.

**Calibration set** — read from the defs on disk this pass (`mlie.starwarsanimalcollection`
`1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml`, and our own `src/RimStarWars/SWBestiary/
Defs/ThingDefs_Races/`):

| creature | bodySize | healthScale | speed | main attacks (power / cooldown) | armour S/B | combatPower | group |
|---|---|---|---|---|---|---|---|
| Anooba (medium interface) | 0.95 | 1.00 | 5.0 | bite 16/2.0, scratch 10.9/2.0 ×2 | — | 80 | 3–6 |
| Massiff (medium interface) | 0.85 | 1.00 | 5.0 | bite 16/2.0, scratch 9.9/2.0 ×2 | 0.12/0.12 | 60 | 3–6 |
| Strill (medium, flier) | 1.0 | 2.00 | 3.5 | bite 18/2.0, scratch 10.9/2.0 ×2 | 0.12/0.12 | 60 | — |
| `RSW_TunnelSnake` | 2.0 ⚠ | 3.00 | 3.2 | toxic stinger 16/2.6, claws 15/2.0 ×2 (+stun 8 surprise), bite 18/1.4 | 0.25/0.35 | 320 | 1 |
| `RSW_ShrublandGiant` | 6.0 | 8.50 | 2.8 | bite 26/2.6, feet 22/2.0 ×2 | 0.50/0.45 | 380 | 1–3 |
| Mudhorn (huge predator icon) | 4.0 | 4.50 | 4.0 | horn 26/2.0, bite 19/2.6 | 0.24/0.24 | 475 | 1 |
| **kessrik (proposed)** | **1.2** | **1.6** | **4.8** | **bite 15/1.8; hook-claws Scratch 12/2.0 ×2, surpriseAttack Stun 6; head Blunt 6/2.0 (chanceFactor 0.2)** | **0.20/0.15** | **110** | **2–3 per tree** |

⚠ `RSW_TunnelSnake` at bodySize 2.0 is inside the banned large band. Found while calibrating,
not this spec's to fix; reported to the owner (§11). It is NOT used as a ceiling here for that
reason — the kessrik is calibrated against Anooba (the biome's own medium predator) and the
giant (the thing whose wool it lives in).

**Why these numbers.**
- bodySize 1.2 / healthScale 1.6: about 1.6× an Anooba's hit points, well under the snake's,
  so a single kessrik dies to two colonists with any weapon but outlasts one unarmed Jawa.
- Speed 4.8 vs Anooba 5.0: a colonist (4.6) with a head start reaches the 18-cell disengage
  line before being caught more often than not; a colonist who dawdles inside the radius does
  not. The rage disengages at the line, so the chase is bounded by design, not by speed.
- The opener: `surpriseAttack` Stun 6 on the hook-claws is the drop from the crown — a stun of
  that size is a lost second or two, enough for the second kessrik to arrive, not enough to
  chain-lock a pawn (the snake's is 8; that one is an ambusher by trade). No venom: the venom
  register belongs to the small band and the snake, and toxic on a 2–3 pack tips "dangerous"
  into "lethal on contact".
- Armour 0.20/0.15: bark-hide; noticeably tougher than Anooba, a third of the giant. Bullets
  work.
- combatPower 110 each, so a full tree is 220–330 points — roughly one tunnel snake, or a
  third to half a shrubland giant. That is the weight the loop wants: **one colonist alone
  should lose; two with guns firing from outside 9 cells win while the kessriks charge (they
  charge — see manhunterOnDamage below); three in melee take real wounds.** The re-spawn
  timer (8–14 days) makes it a renewable cost, not a one-time clearance.
- `Wildness 0.95`, `manhunterOnDamageChance 1.0`, `manhunterOnTameFailChance 0.5`: shooting
  one from thirty cells is vanilla revenge — it comes for the shooter, unscoped, exactly as a
  wild animal should. Ranged cheese is still a fight.
- `predator false`, `foodType OmnivoreAnimal`, `baseHungerRate 0.4`: it eats fuzz and whatever
  the build's donor body allows, and does not roam to hunt. The "eats the bark-lickers" line is
  description text, not `predator true` — a predator's hunt range would drag it off its tree
  and would make it hunt your pets. `maxPreyBodySize` unset.
- `herdAnimal false`, `wildGroupSize 1` on the PawnKindDef: it must NEVER appear through the
  biome's `wildAnimals` table (commonality 0 there, and not listed at all) — every kessrik
  comes from a roost. A kessrik with no tree is the failure mode, not a spawn table entry.
- `lifeStageAges` the ordinary three-stage ladder (adult at 1.0 years); the roost spawns
  adults; `gestationPeriodDays 12`; young born on the map inherit `homeTree` from the mother
  in `RM_CompTreeGuardian.PostSpawnSetup` if she has one and the roost has a vacancy —
  otherwise the "spawned any other way" rule. Live birth (flesh, blood) like the giant.
- `ComfyTemperatureMin -5 / Max 50`, the giant's envelope: same plain, same wind.

## 5. Huntable, tameable, drops

- **Huntable: yes.** Vanilla Hunt designation works on a wild faction-null animal; the
  approach to hunt it is the approach that rouses it, and a hit at range is a manhunter
  revenge, so hunting IS the fight. No special case.
- **Tameable: yes, hard.** `trainability Advanced`, `petness 0`, `Wildness 0.95`. Taming
  requires standing inside the trigger radius with food — the rage is the tame-failure
  penalty before the roll ever happens (`onlyToolUserOrHumanlikeTriggers` does not exempt a
  handler). A tamed kessrik goes inert as a guardian (§3) and is a good guard animal for its
  weight; it does not guard anything of the colony's. No `specialTrainables` beyond the
  Odyssey `AttackTarget` the snake already ships.
- **Drops:** meat and a leather from the donor body the build reskins — the giant precedent
  (`RSW_Leather_Fambaa` / `RSW_Gorg_Meat`) is to reuse rather than mint. **No signature drop.**
  The reward is the tree's, deliberately: if the kessrik dropped wool, killing them would be
  the harvest and the tree would be scenery again. `MarketValue 420` (Anooba 400, Strill 450).
- **Its bower** is not a Thing. The wool it sleeps in is the wool on the bark; the harvest
  and the roost are one object, which is why harvesting is an attack on it.

## 6. Mod Settings

Standing ruling (owner, 2026-09-12): every mod ships a real settings screen; defaults =
shipped behaviour; all-off degrades gracefully. This feature's switches live in the kit's
existing `RM_CreatureBehaviorsSettings` screen (`RM_CreatureBehaviorsMod.cs`, numbered
entries 28–31 in its header list, same conventions as 27 `parentalEnrageEnabled`). The RSW
race and the RUT binding carry no settings of their own — SWBestiary's
`RSW_BeastMechanicsSettings` precedent is for mechanics that live in SWBestiary; these do not.

| setting | type / range | default | on → off, exactly |
|---|---|---|---|
| `treeGuardiansEnabled` | bool | **true** | Off: roost comps spawn nothing new; guardian comps stop scanning and stop leashing, so every existing kessrik is an ordinary wild animal from the next rare tick (it is NOT despawned — the owner's animals stay his). A rage already running ends on its own rules. Stats, tools and `manhunterOnDamageChance` are untouched: it is exactly as dangerous as its card says and no more. |
| `treeGuardianRadiusMultiplier` | slider 0.5–2.0 | **1.0** | Scales `triggerRadius` and `disengageRadius` together (so the hysteresis ratio holds). 0.5 = "you have to touch the trunk"; 2.0 = a 36-cell exclusion zone. Never the leash. |
| `treeGuardianCountMultiplier` | slider 0–2.0 | **1.0** | Scales the roost `count` range (rounded, floor 0). At 0 a tree spawns and re-spawns nothing; existing kessriks stay. At 2.0 a tree holds 4–6. |
| `treeGuardianHarvestRage` | bool | **true** | Off: cutting, harvesting or burning the tree does not rouse them (the PlantAlarm scoped path is skipped); proximity still does. For the player who wants the sentry, not the siege. |

Label the group **"Tree guardians (map generation and wild regrowth)"** — it is not a
worldgen toggle (the planet is fixed and shipped), but it does decide what a NEW map or a
regrown tree spawns, and the standing ruling asks for that class of effect to be named.

Graceful degradation, checked case by case: `rageState` null in XML → inert, as
`enrageState` is; kit absent (`MayRequire` on every block) → the tree is a tree and the race
loads as a plain animal with no comp; assembly present but the settings file missing →
defaults; all four at their minimum → a tree with no guardians and a kessrik that is a
slightly tough Anooba.

## 7. Naming — defName and player-facing label

**Tier, and why.** `design/NAMING_SCHEME_PLAN.md` §1: the engine/content rule says "the
engine takes the highest tier it honestly passes, the content pack takes its own tier; one
mod may not straddle." So this is three tiers, one each, and none of them straddles:

| layer | tier | where | why |
|---|---|---|---|
| mechanism (extension, comps, rage state, roost, leash JobGiver) | **RM_** | `mandrake.rm.creaturebehaviors` | names no species, no tree, no biome — "guard a Thing" would serve a medieval-tribe player's own mod unchanged (the RM test). Same call the enrage kit made. |
| the species (ThingDef + PawnKindDef + art) | **RM_** | the Arid Shrubland's own `RM_` biome mod (staged with the biome kit until that mod exists at its sitting) | **Q11a** (`design/RimMandrake/biome_mod_architecture.md` §7, owner 2026-09-22): an invented name is not Star Wars IP, so it does not route through the franchise layer — and the free `RM_` biome mod must carry its full cast, never a thinned fallback. The def names no tree and no campaign lore: it guards whatever roost spawned it, so nothing about it is Utinni-specific either. Ruled by card 2026-09-25 (name = Bark-warden; tier by the Q11a test). |
| the binding (roost comp + PlantAlarm on `RUT_SweetlineTree`; anything in the campaign's shrubland wiring) | **RUT_** | `mandrake.rut.ashkarrflora` / `mandrake.rut.utinnipatches` | this is where the campaign says WHICH tree carries WHICH guardian. `RUT` depends on `RM` — downward only, which is the grammar. |

(`RSW_ShrublandGiant` / `RSW_TunnelSnake` were this spec's original tier precedent; they predate
Q11a and are themselves due `RSW_`→`RM_` at the shrubland's biome sitting per the split rulings of
2026-09-23, so they no longer argue for `RSW_` here.)

**Names — RULED by card, 2026-09-25.** defName **`RM_Barkwarden`** (reused for ThingDef and
PawnKindDef, the siblings' convention); player label **"bark-warden"**. The rename joins
`ARIDSHRUBLAND_SHIPPING_NAMES_1` only if the sitting later changes the word — the label is his
pick, not a working placeholder.

## 8. Flight

**It does not fly.** It climbs, and it drops. Nothing in §1 or in the description text may
say glide, wing, sail or soar — the standing rule ("if it flies in the fiction, it flies in
the game") is satisfied by keeping the fiction on the ground: the drop from the crown is the
`surpriseAttack` stun on the claw tool, an animation-free melee opener, not a flight. The
dive route on the interface is already the fliers' (Whisperbird, Convor, the scrap-nest
birds), and this creature is the canopy's answer, not the sky's. `MaxFlightTime` is not set;
`canFlyIntoMap` is false (a kessrik arriving by air would have no tree).

If the owner wants it to glide between trees, that is a different creature: `MaxFlightTime`
> 0 (a stat, never a bool), a whole-body directional flip-book on the PawnKindDef, and no
Spastic wing layer — and it would need the roost logic to survive a mid-air re-home. Not
proposed.

## 9. What could make this annoying rather than good

Honest list. Each has a mitigation in the design or a stated acceptance.

1. **A tree on the doorstep.** Roads follow the trees; players settle by landmarks; a
   colony built around a sweetline tree gets charged every time someone walks to the fridge.
   Mitigation, built in: `stopIfInHomeArea` — a roost whose tree stands inside the player's
   Home area stops re-spawning, and guardians whose tree has been inside the Home area for
   `homeAreaGraceDays` (3) quit: re-home to another tree if one is vacant within 60 cells,
   otherwise become free wild animals. The player who wants the tree tame has a lever that
   is already in the game (the Home area) and a three-day siege to earn it. No new UI.
2. **Rage flapping at the edge.** An intruder standing at exactly the trigger line would
   trigger/disengage every rare tick. Mitigation: hysteresis — trigger 9, disengage 18, and
   a 600-tick per-guardian cooldown.
3. **The eternal harvest job.** A colonist ordered to cut the tree is interrupted by a rage,
   the rage ends, the job resumes, another rage — for as long as the player leaves the order
   standing. Accepted: that IS "dares the traffic", and the player's options (guards, guns,
   give up) are the design. What must NOT happen is the harvest completing between rages
   without a fight: `harvestWork 4200` on the tree and `cooldownTicks 600` guarantee several
   charges per harvest.
4. **Visitors, traders and quest pawns on the tree-roads.** They are tool-users; they get
   mauled. A wild animal attack costs no goodwill, but a dead trader is a lost trade.
   Accepted as the biome ("every raider knows…"), and it applies to raiders too — players
   will route a raid past a tree on purpose. Emergent, allowed.
5. **Ranged cheese.** Shoot from 30 cells and the kessrik cannot reach you before it dies.
   `manhunterOnDamageChance 1.0` makes it charge on the first hit, so it costs ammunition and
   a fight, and the roost re-spawns in 8–14 days, so it is a recurring cost, not a one-time
   clearance. Accepted.
6. **Threat state while a rage runs.** `category Aggro` puts the pawn in
   `pawnsInAggroMentalState`, so for up to 2500 ticks the map has an active threat (danger
   music, some jobs refused). Bounded by the time-box and the disengage rule; the giant
   already does this and the owner has tested it live without complaint.
7. **No warning.** No letter, no sound before the drop. This is the ruling for the giant and
   is kept here for consistency; the player learns the rule from the tree's description and
   the first drop. If the owner wants a tell, it is a `soundCall` on the crown, never a
   letter.
8. **The kessrik that lost its tree.** A free ex-guardian is a 1.2-body wild animal that
   wanders like any other. Fine. What it must not do is manhunt or vanish; both are covered
   in §3.
9. **A guardian on a tree the player never visits** costs a radial scan every 250 ticks
   forever. Negligible at these counts (§2, Cost); worth a profiler line in the build's
   quicktest, not a design change.
10. **Pets cannot be hurt by it and cannot bait it** (`JobGiver_Manhunter` targets ToolUser+
    only). A player expecting a guard-dog stand-off gets nothing. Accepted: the alternative —
    a kessrik that kills a passing muffalo — makes every tree a pet-killer and the loop
    stops being about the harvest.
11. **The two-tree overlap.** Two sweetline trees within 18 cells of each other would give
    a single intruder two roosts' worth of rages. `wildClusterRadius 0` / `wildClusterWeight
    0.05` make this rare; the roost comp additionally refuses to spawn if another roost tree
    stands within `triggerRadius` — its slot stays empty. Worth one line in the build.

## 10. Art

**None exists, and none is queued here.** Searched this pass by subject:
`infrastructure/artpipe/done/*.json`, `infrastructure/artpipe/registry.jsonl` and
`infrastructure/artpipe/_artsrc/` for `sweetline`, `guardian`, `warden` — the only hits are
`ROT_GUARDIAN_GROVES_1`'s flora (agelesscap, euphoriccrown, falsefruit, regenerantveil),
which is a different item and a different biome. No review sheet has ruled on a creature for
this slot.

**Build-pass recommendation:** do what both siblings did — reskin an existing RSW quadruped
body and art under the new defName with a silver-grey retint (`RSW_ShrublandGiant` reskinned
Fambaa; `RSW_TunnelSnake` reskinned Klorslug; zero new PNGs either time). Pick a donor with a
long-armed, low, clawed silhouette at drawSize ~1.6–1.8, and check `design/Jawa/fauna/
cast_assignment.csv` first so the donor SPECIES is not double-booked (the snake pass's own
rule). New art is the owner's call, after he has seen the reskin in a review save.

**Canon:** this is an invented species with no `design/RimStarWars/canon_references/` entry,
and the canon skill is explicit that no entry means no target — do not fabricate one. The
visual brief is §1 of this spec; if new art is ever commissioned, §1 is the prompt's source
and the reskin is the reference image.

## 11. Open questions for the owner

1. ✅ **RULED (card 2026-09-25 + Q11a test): species def is `RM_Barkwarden`, `RM_` tier**, in
   the shrubland's own biome mod — invented name, no IP, nothing campaign-specific in the def
   (§7). Mechanism RM, binding RUT, unchanged.
2. ✅ **RULED (card 2026-09-25): the label is "bark-warden".**
3. ✅ **BUILT, `SWEETLINE_WOOL_HARVEST_1` (2026-09-21).** `RUT_SweetlineTree` now ships
   `harvestedThingDef` RUT_SweetlineWool (`RUT_SweetlineTree_Items.xml`, ParentName WoolBase)
   and `harvestAfterGrowth` 0.05, so `HarvestDestroys` is false and both the Harvest and Cut
   Plant jobs leave the tree standing. harvestYield dropped from TreeBase's 160 (wood) to 20.
   ⚠️ **Pace does NOT match this spec's own suggestion.** This item's regrow pace is
   `growDays * (harvestMinGrowth - harvestAfterGrowth)` = `240 * (0.40 - 0.05)` = **84 in-game
   days**, picked to read as "rare" against arid_shrubland.md's own fiction directly — it was
   NOT matched to this spec's suggested 8–14-day roost respawn (that number did not exist as a
   ruling when the harvest was built, only as this open question). Whoever builds the guardian
   next must reconcile the two paces — either retune `harvestAfterGrowth`/`harvestMinGrowth` on
   the tree, or accept a guardian roost cycle that outpaces the harvest it's guarding.
4. ⚠ **`RSW_TunnelSnake` is bodySize 2.0**, inside biome ban 4's large-band void (1.5–3.5),
   with the roster's own Terrorworm interim beside it. Found while calibrating §4; not this
   spec's to change. Either the ban has a snake carve-out he has not written down, or the
   snake needs to come down to ≤1.4 (or the Klorslug body it borrows is the wrong donor).

## Build handoff (for the item that follows)

Files the build touches, so the estimate is honest: kit — three new `.cs` (extension+comp,
roost comp+props, leash JobGiver), one new MentalStateDef XML, one ThinkTreeDef insert XML,
one small change to `RM_CompPlantAlarm` (optional scoped state + a pawn-carrying
`TriggerAlarm(Pawn)`), one `RM_Plant_Alarming : Plant`, four settings entries; SWBestiary —
one race XML (ThingDef + PawnKindDef, reskin); AshkarrFlora — three lines on
`RUT_SweetlineTree` (thingClass, roost comp, plant alarm) under `MayRequire`. Nothing in
`RUT_AridShrubland.xml` — the kessrik is not a `wildAnimals` entry and must never become one.
Quicktest, minimal list + the three mods: spawn a tree, confirm 2–3 guardians within 4 cells,
walk a colonist to 8 cells (rage), to 19 cells (recovery), cut the tree (rage at the cutter),
save/load mid-rage, and toggle each of the four settings live.
