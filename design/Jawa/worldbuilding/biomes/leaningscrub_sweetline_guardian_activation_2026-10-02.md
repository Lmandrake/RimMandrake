# Leaning Scrub sweetline guardian: activation design (2026-10-02)

Item: `LEANINGSCRUB_SWEETLINE_GUARDIAN_1` (with `SHRUBLAND_TREE_GUARDIAN_1` folded in). BENCH
design pass with the owner away. Nothing here is built, filed or ruled. It answers the item's
two open questions: **dormant pawn or incident**, and **what counts as harm**. Its other
question, *what is the guardian*, is already ruled (§1).

Companion doc: `design/Jawa/worldbuilding/biomes/sweetline_guardian_spec.md` (2026-09-21, 456
lines) holds the creature (stats, drops, art, tier). This doc does not repeat it. It replaces
that spec's **activation** half (§2 trigger, §9.7 "no warning"), and §1.3 below lists where the
spec is now wrong.

## 0. Summary

- **Recommendation: a visible sleeper, woken by harm, with a meter you can read.** Two or three
  bark-wardens spawn with the tree and stay on it, in a dormant "roosting" state, using vanilla
  `CompCanBeDormant`. A disturbance meter on the tree fills when someone works or wounds the
  tree, shows warning stages, and wakes them at full. While awake they attack only the pawn who
  did it, using the kit's **already-built** `RM_MentalState_ScopedAggression`. The meter drains
  over days, so a tree forgives you.
- **Harm is defined as** wool-harvesting work on the tree (Harvest and Cut are the same job on
  this tree, §3) and violent damage to the tree. Walking past is **not** harm: it only makes
  them watch you. Picking up the wool the tree sheds on its own is never harm.
- **Key findings:** (1) `RM_SweetlineTree` **appears on no map today**. It is in no
  `wildPlants` and no genstep (§1.2), so whatever is built has no natural tree to sit on until
  the placement work in `TREE_GRAPHICS_OWNERSHIP_1` lands. (2) This tree **cannot be felled** by
  Cut or Harvest (engine-checked, §3), so "harm" is really harvest and damage. (3) The spec's
  roost comp ticks on `CompTickRare`. A plant only Long-ticks, so as written its re-spawn would
  never fire.

## 1. What is ruled and built (measured 2026-10-02)

### 1.1 Ruled, settled, not reopened

| what | ruling | where |
|---|---|---|
| A guardian exists, as one **generic species** (option b), not per-tree uniques | owner card 2026-09-21 | `infrastructure/state/items/SHRUBLAND_TREE_GUARDIAN_1.md` |
| Name **bark-warden**, defName **`RM_Barkwarden`** | card 2026-09-25 | ledger note 2026-09-26 on `SHRUBLAND_TREE_GUARDIAN_1` |
| Tier **RM_**, in the shrubland's own RM biome mod (= `mandrake.rm.leaningscrub`) | Q11a test, 2026-09-26 | `sweetline_guardian_spec.md` §7 |
| Gated by the existing "Named sweetline trees" Mod Setting | item criteria | `LEANINGSCRUB_SWEETLINE_GUARDIAN_1.md` |
| Nothing vanishes or strikes without a readable sign | owner 2026-09-29/30 | `CLAUDE.md` "One kind of heat" |
| The creature's body, stats, drops and art plan | spec §1, §4, §5, §8, §10 | not reopened here |

### 1.2 Built

- **The tree:** `RM_SweetlineTree`, at
  `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml`. It has 650 HP,
  Flammability 0.1, harvestWork 4200, `harvestedThingDef RM_SweetlineWool`, yield 20 and
  `harvestAfterGrowth 0.05`. It carries one comp.
- **`RM_CompSweetlineStation`**, at `src/RimMandrake/LeaningScrub/Source/RM_SweetlineStation.cs`:
  - It gives the tree a generated name, kept in the save.
  - It keeps a "History" gizmo listing up to 12 entries.
  - It sheds **5 wool every 5 days** beside the trunk, ticking on `CompTickLong` as a plant must.
  - It already logs harm: `PostPostApplyDamage` adds a "struck by <instigator>" entry, at most
    one per day.
  - Its own header names "the resident guardian that harm wakes" as a filed follow-up. That is
    this item.
  - The setting is `RM_LeaningScrubSettings.sweetlineStationsEnabled`, shown as "Named sweetline
    trees" in `src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs` l.200.
- 🔴 **The tree spawns on no map.** It is deliberately left out of `RM_LeaningScrub`'s
  `wildPlants` (comment at `RM_LeaningScrub_Biome.xml` l.208–216). The frozen
  `RUT_AridShrubland` never wired it either. The only other repo hit is ExplosiveGrowth's
  roster, which marks it `top None`. Placing the named trees is still owed under
  `TREE_GRAPHICS_OWNERSHIP_1` (owed item 3, "a world-editing pass"). So a guardian has to hook
  on **tree spawn**, whatever spawns the tree later, and a quicktest has to dev-spawn the tree.
- **The bark-warden:** **not built.** Zero `RM_Barkwarden` hits in `src/`.
- **Kit pieces already in `mandrake.rm.creaturebehaviors`**
  (`src/RimMandrake/CreatureBehaviors/Source/`) that this design reuses:
  - `RM_MentalState_ScopedAggression`: a subclass of `MentalState_Manhunter`. It is hostile only
    to `causedByPawn` and never flips a faction. It disengages when the target is beyond
    `disengageRadius` from an **anchor cell**, or is dead, downed or off the map. The tree never
    moves, so its position is a correct anchor. **This makes the spec's proposed
    `RM_TerritorialRage` class unnecessary.**
  - `RM_CompReactionSource` + `RM_ReactionResponseRule_SpawnPawns` /
    `RM_ReactionResponseRule_ActivateSelf`: a working "harm spawns attackers" or "harm wakes this
    pawn" mechanism, with a shared budget, a cooldown and a population cap. Its first consumer
    is the Greentide wasp gall. This is the cheap "incident" route in §2.
  - `RM_CompPlantAlarm`: pushes **vanilla** `Manhunter` onto every tagged responder in range.
    It is map-wide hostile to every humanlike (spec §2 iii). **Do not use it here.**
  - Settings already present: `guardianAlarmEnabled` (#15), `parentalEnrageEnabled` (#28),
    `reactionSourceSpawnEnabled` / `reactionSourceBudgetMultiplier` (#34).

### 1.3 Where `sweetline_guardian_spec.md` is now wrong

These are reported here for whoever builds. Per the brief, this pass edits no other file.

1. **§2 B, roost comp on `CompTickRare`.** A plant never Rare-ticks: `Plant` overrides only
   `TickLong` (`CLAUDE.md`, RimSage-confirmed 2026-09-27). As written, the top-up and re-spawn
   would never run. It must use `CompTickLong`.
2. **§7 tier table, binding in `RUT_` AshkarrFlora on `RUT_SweetlineTree`.** The tree is now
   `RM_SweetlineTree` in `mandrake.rm.leaningscrub` (§7 Q8 dissolution). The binding is RM, in
   LeaningScrub's own XML.
3. **§2 A, proximity trigger "within 9 cells, drop with no warning", and §9.7 "No warning".**
   Both conflict with the 2026-09-29/30 readable-sign rule and with the bedazzle slate's own
   wording, "a guardian unique that ignores you until you touch the tree"
   (`leaningscrub_bedazzle_review_2026-09-29.md` l.345–350). This is owner question 1.
4. **§2 A, a new `RM_TerritorialRage` class.** It already exists as
   `RM_MentalState_ScopedAggression` (above).
5. **§3, "Cut or harvest the tree … tree dies or is cut".** Cutting does not kill this tree (§3
   below). It dies only to damage.

## 2. Dormant pawn vs incident, engine-checked

Every row below was read from the decompiled 1.6 source via RimSage this pass, unless marked.

### Engine facts that decide it

- **`CompCanBeDormant`** (RimWorld/CompCanBeDormant.cs):
  - `startsDormant` decides the state at make. With `jobDormancy`, the pawn sleeps in the
    `Wait_AsleepDormancy` job, and `Awake` simply reads `CurJobDef != SleepJob`.
  - `ToSleep()` puts it back to sleep and `WakeUp()` wakes it. Both are public, so the guardian
    can be re-roosted after a fight, which vanilla clusters never do.
  - Its inspect string is `dormantStateLabelKey` while asleep (default "DormantCompInactive") and
    `awakeStateLabelKey` ("woke N days ago") once awake. Both are overridable keys, so "Roosting
    in the crown" is a Keyed string, not code.
  - ⚠️ `ShowZs` returns **false for any Pawn**, so a dormant animal shows no sleep-Z by itself.
    The readable sign has to be ours (§4).
  - `ConfigErrors` requires `receivesSignals` **or** `jobDormancy`. Use `jobDormancy`.
- **Needs freeze while dormant.** `Need.cs` l.111–126 freezes any need listed in the comp's
  `freezeNeeds` while `!Awake`. List `Food` and `Rest`, and a roosting bark-warden never starves
  on a tree nobody visits. This removes the obvious objection to a months-long sleeper.
- **Dormant pawns are skipped as threats and auto-targets.** See `AttackTargetFinder.cs`
  l.718–719, `GenHostility.cs` l.285–286 and `DangerWatcher.cs` l.92. A roosting tree does not
  start danger music, and colonist turrets and auto-fire ignore it. That is exactly "ignores
  you, you ignore it". Whether the player can still force-attack it or **Hunt** it while it
  roosts is **UNMEASURED**: hunting is a forced job, not an auto-target. Settle this in the
  quicktest.
- **`CompWakeUpDormant`** (vanilla): `wakeUpOnDamage` wakes it the instant it takes external
  violence. So shooting a roosting bark-warden wakes it, and then the spec's
  `manhunterOnDamageChance` revenge applies. Its radius wake (`wakeUpIfAnyTargetClose`, LOS
  scan every 250 ticks) is the vanilla proximity trigger. **Do not set it** (question 1).
- **Pawns tick in Normal mode.** Vanilla's own dormancy comp runs its 250-tick work as
  `CompTick` + `IsHashIntervalTick(250)`, and the watcher can copy that. **The tree cannot run
  it.** A plant's comps only get `CompTickLong` (2000 ticks), which is too coarse to catch a
  harvest in progress. ⇒ The guardian pawn does the watching. The tree stores the meter.
- **`GenHostility.HostileTo`** consults `MentalState.ForceHostileTo` before any faction logic
  (l.9–98, re-read). This is why scoped aggression works on a faction-null animal.
- ⚠️ **UNMEASURED: whether a lordless wild animal STAYS in `Wait_AsleepDormancy`.** Every
  vanilla dormant pawn found (mech clusters, `GenStep_SleepingMechanoids`, the Odyssey insect
  lair, Anomaly's sleeping Fingerspike) belongs to a faction or a lord. Frozen needs remove
  hunger and rest as reasons to get up, but the animal think tree may still override the job.
  **Fallback, a known pattern:** a `ThinkTreeDef` insert at `Animal_PreMain` (the kit's
  `RM_ThinkTree_VerminBehaviors` shape) that re-issues the dormancy job while the roost says
  "roosting". Budget for it.

### The three shapes compared

| | **A. Resident sleeper** (recommended) | **B. Spawn-on-harm** (the "incident") | **C. Awake proximity roost** (the spec as written) |
|---|---|---|---|
| what is on the map before harm | 2–3 visible bark-wardens on the tree, "roosting" | nothing; the tree only | 2–3 awake bark-wardens leashed to the tree |
| what wakes them | the tree's disturbance meter reaching full (§3) | first qualifying harm, via `RM_CompReactionSource` + `SpawnPawns` | any tool-user within 9 cells |
| readable before the strike? | **yes**: visible pawns, inspect line, meter stages | **no**, unless a sign is added; they appear out of a tree that had no visible occupant | partly; the pawns are visible, but the drop has no warning by spec |
| new C# | roost comp, guardian comp, plant subclass (§6) | plant subclass only (the PlantCollected hook) | roost comp, guardian comp, leash JobGiver, PlantCollected hook |
| traders, visitors, raiders on the roads | untouched unless they harm the tree | untouched | mauled when they pass (spec §9.4) |
| colony built beside a tree | fine; they sleep | fine | charged on every fridge trip, so the spec needed a Home-area mitigation (§9.1) |
| huntable, tameable, killable in advance | yes; the player can clear a tree on purpose | no; nothing exists to clear | yes |
| cost while nobody visits | one 250-tick check per guardian (frozen needs, no path) | zero | radial scan + leash every 250 ticks |
| "a storyteller incident" | — | ⛔ not really. An `IncidentWorker` fires on the storyteller's clock, not on harm. "Incident" here can only mean a local spawn-on-trigger, which is shape B. | — |

**Why A.** The owner rule says nothing strikes without a readable sign, and a creature you can
see sleeping on the tree from the day you arrive is the strongest sign there is. It also keeps
the biome's register ("danger announces itself by posture, never by voice"). B is the cheapest
build, but its whole surprise is creatures appearing from nowhere, which is the thing the rule
forbids. C solves a different problem (an exclusion zone), and spec §9 lists most of its costs.

## 3. What counts as harm

### Engine facts about this specific tree

- **Cut and Harvest are the same act here, and neither kills it.**
  - `PlantProperties.HarvestDestroys => harvestAfterGrowth <= 0f` (PlantProperties.cs l.205).
    This tree has 0.05, so it is false.
  - `Plant.PlantCollected` (Plant.cs l.621–664) therefore takes the `else` branch: it resets
    growth to 0.05 and returns. No stump, no destroy.
  - `JobDriver_PlantWork` calls `PlantCollected` for both the Harvest and the Cut job
    (JobDriver_PlantWork.cs l.40–131).
  - ⇒ **The only ways to kill a sweetline tree are damage: weapons, explosives, fire.**
- **Ideology's tree-lover machinery never fires for it.** `HistoryEventDefOf.CutTree` and
  `treeDestructionTracker.Notify_TreeCut` sit inside the `HarvestDestroys` branch. A
  non-destroying harvest records nothing, so there is no vanilla "harm to tree" event to borrow.
- **Harvest work applies no damage.** `workDone` accumulates on a tick action, and the only
  engine call into the plant is `PlantCollected` at **completion**. So "harvest in progress" is
  invisible to damage hooks. It is only seen by checking who is doing plant work on the tree,
  which is why the guardian pawn watches (§2).
- **The wool must regrow before the next harvest.** That takes
  `growDays × (harvestMinGrowth − harvestAfterGrowth)` = 240 × (0.40 − 0.05) = **84 days**
  (spec §11.3). So a "second harvest wakes them" rule could never trigger.

### The definition (all numbers are proposals; the knobs are in §5)

The tree's comp keeps **`disturbance`**, a value from 0 to 1, in the save. It has three stages.

| act | counts? | how much | caught by |
|---|---|---|---|
| A pawn doing Harvest/Cut work on the tree | **yes** | **+0.10 per 250 ticks of work** | guardian comp, 250-tick check: a spawned pawn whose current job driver is `JobDriver_PlantWork` (or subclass) with target A = the tree |
| That harvest completing | yes | +0.25 | `RM_Plant_Guarded : Plant` overriding `PlantCollected(by, mode)` (the only harvest seam, as in `RUT_Plant_FalseFruit`) |
| Violent damage to the tree with a Pawn instigator | **yes** | **+damage ÷ 20** (a 10-damage bullet ≈ 0.5; two shots wake them) | tree comp `PostPostApplyDamage`, `dinfo.Def.ExternalViolenceFor(tree)` |
| Fire or other damage **with no pawn instigator** | yes, but no target | as above | same hook. They wake **watchful**, with no one to attack; an untargeted `ScopedAggression` is harmless by design (`ForceHostileTo` needs `causedByPawn`). History logs it. |
| Damage to a roosting bark-warden | yes, it wakes **that one** | instant | vanilla `CompWakeUpDormant.wakeUpOnDamage`; then vanilla revenge (`manhunterOnDamageChance`, spec §4) |
| Walking, standing or camping near the tree | **no** | 0 | it only raises the "watching" sign (§4) — owner question 1 |
| Hauling the wool the tree **sheds itself** (`RM_CompSweetlineStation`, 5 every 5 days) | **never** | 0 | — the tree paying its visitors is the opposite of harm |
| Animals, including tamed ones, harvesting or attacking | no | 0 | instigator must be ToolUser+; also `JobGiver_Manhunter` can only ever target ToolUser+ (spec §2, measured 2026-09-21) |
| A harvest by the bark-wardens' own handler (tamed guardian present) | yes | same | taming one bark-warden does not tame the tree |

**Stages and what a harvest actually feels like.** At work speed 1, a 4200-work harvest is
about 17 checks:

- Meter **0.3 "stirring"** after about 750 ticks (≈12 s at 1×). This is the warning stage.
- Meter **0.6 "restless"** after about 1500 ticks. This is the last warning.
- Meter **1.0 "awake"** after about 2500 ticks, roughly 60% of the way through the harvest.

So **an unguarded harvest is a fight unless the player stops at the warning**. That matches the
sheet: "a rare hanging harvest for whoever dares the traffic". A fast harvester, or guards
standing by, still gets the wool. Owner question 2 decides whether harvest wakes them at all.

**On waking** (meter reaches 1.0):

- Every bark-warden bound to the tree gets `CompCanBeDormant.WakeUp()`, then a forced
  `TryStartMentalState(RM_RoostDefence, otherPawn: last harm-doer)`.
- `RM_RoostDefence` is a new MentalStateDef reusing the existing
  `RM_MentalState_ScopedAggression`. The response sets `anchorCell` = tree position and
  `disengageRadius` 18, exactly as `RM_ReactionResponseRule_SpawnPawns` already does.
- The meter is then held at 1.0 for `rageDurationTicks` (2500).

**Forgiveness:**

- The meter drains **0.2 per day** in `CompTickLong` while no harm is happening, so calm returns
  in at most 5 days.
- After a fight ends (target dead, downed, gone, or beyond 18 cells from the tree), the
  bark-wardens walk back to the trunk and stay **watchful**, awake and leashed within 3 cells,
  until the meter falls below 0.3. Then `ToSleep()` re-roosts them.
- A tree you hurt stays touchy for a few days and is calm again within a week. Question 4 offers
  the stricter alternative.

**The tree dies** (damage only): the bound bark-wardens wake and become ordinary free wild
animals, as in spec §3. A message names the tree, and the History records it. They never vanish
and never despawn.

## 4. Readable warning signs

The rule: nothing vanishes or strikes without a readable sign. Every sign below is text or a
visual. None is a roar: the biome's "posture, never voice" register holds, so `soundAngry` stays
breath and claws (spec §1).

| moment | sign | mechanism |
|---|---|---|
| Always | The bark-wardens are **visible pawns on the tree**. Their inspect line reads "Roosting in the crown of <tree name>." | `CompCanBeDormant.dormantStateLabelKey` → a Keyed string in LeaningScrub's `Languages/` (it is `.Translate()`d) |
| Always | The tree's description says it is guarded. Its inspect pane adds "Bark-wardens roost here (3). Calm." | new line in the roost comp's `CompInspectStringExtra`, next to the station comp's wool line |
| Always (selected) | A **disturbance bar** gizmo on the tree, 0–100%, with stage ticks at 30% and 60% | own `Gizmo` modelled on Anomaly's `ActivityGizmo` (`CompActivity` is `sealed` and tied to entity suppression and study, so it is copied as a pattern, not reused) |
| A tool-user within 9 cells | The roosting pawns get a periodic "watching" mote (vanilla meta-icon fleck), and the inspect line becomes "…watching <pawn>." **No hostility.** | guardian comp, 250-tick check |
| Stirring (0.3) | Message (CautionInput, targets the tree): "The bark-wardens of <tree> are stirring. Whoever is working the tree should stop." A fleck over the tree each check. | `Messages.Message` + `MessagesRepeatAvoider` (the pattern `CompActivity.PostPostApplyDamage` uses) |
| Restless (0.6) | Second message (ThreatSmall): "The bark-wardens of <tree> are about to drop." | same |
| Awake (1.0) | Message (ThreatBig) naming the target: "The bark-wardens of <tree> drop on <pawn>." Plus a History entry. **No letter**: a message is enough for a local fight, and the giant's precedent has none. | — |
| Fight ends | Neutral message "…climb back into the crown." History entry. The inspect line reads "Watchful" until re-roost. | — |
| Tree destroyed | Message "The bark-wardens of <tree> have lost their tree." | — |
| A roost slot refilled later | History entry "a bark-warden has taken up the crown". **No silent appearance**, though the spawn itself is quiet. | roost comp |

## 5. Mod Settings

Per the item's criteria, all guardian switches sit under LeaningScrub's existing **"Named
sweetline trees"** group. That is `RM_LeaningScrubSettings`, the same screen as
`sweetlineStationsEnabled`. Defaults equal shipped behaviour. All-off degrades to "a tree with a
sleeping animal on it" and never to a missing animal.

| setting | type / range | default | off / at minimum, exactly |
|---|---|---|---|
| `sweetlineGuardiansEnabled` — "Bark-wardens guard sweetline trees" | bool | true | No new guardians spawn. Existing ones **wake and become ordinary wild animals** on the next check, so nothing is despawned. A running fight ends on its own rules. Also effectively off whenever "Named sweetline trees" is off (the item's gate). |
| `sweetlineGuardianCount` — "Bark-wardens per tree" | int 0–4 | 2–3 (rand) | 0 = the tree spawns and refills nothing; existing ones stay |
| `sweetlineHarvestDisturbance` — "How fast harvesting disturbs them" | slider 0–3× | 1× | 0 = harvest is never harm (owner Q2 option b, as a player choice); damage still counts |
| `sweetlineForgivenessDays` — "Days for a disturbed tree to calm" | slider 1–30 | 5 | drives the 0.2/day drain |
| `sweetlineProximityCharge` — "Bark-wardens also charge anyone who lingers under the tree" | bool | **false** | on = the spec's 9-cell territorial trigger, as an opt-in (owner Q1 option b) |

Label note, per the 2026-09-12 standing ruling on world-affecting toggles: "affects newly spawned
sweetline trees". It is not worldgen, since the planet is fixed.

## 6. Build plan (FOUNDRY), sized

The tree and the species are both RM_ in LeaningScrub. The mechanism names no species, so it
goes in the kit, as the spec intended.

**Kit, `mandrake.rm.creaturebehaviors`** (`RM_CreatureBehaviors.csproj` sets
`EnableDefaultCompileItems false`, so **every new `.cs` needs its own `<Compile Include>`
line**):

1. `RM_CompProperties_GuardianRoost` / `RM_CompGuardianRoost` goes on the **tree**, about 220
   lines:
   - `PostSpawnSetup(!respawningAfterLoad)` spawns `count` guardians with
     `PawnGenerator.GeneratePawn(kind, faction null)` near the trunk (the
     `WildAnimalSpawner` / `SpawnPawns` shape), dormant, and binds them.
   - `CompTickLong`, **not** Rare: prune the dead and tamed, refill one per `respawnDays`, and
     drain the meter.
   - It holds the `disturbance` meter and its stages, plus the inspect line and the bar gizmo.
   - `PostPostApplyDamage` adds damage harm.
   - It exposes `Notify_Harvested(Pawn)` and `AddDisturbance(float, Pawn)`.
   - Scribe: the guardian refs, the meter, and the last harm-doer.
2. `RM_CompRoostGuardian` goes on the **pawn**, about 160 lines. `CompTick` with
   `IsHashIntervalTick(250)`, copying vanilla `CompCanBeDormant`. It:
   - detects plant work on its tree (→ `AddDisturbance`);
   - raises the watching sign;
   - re-homes once if the tree is gone (spec §3 rule);
   - re-roosts with `ToSleep()` when the meter is calm;
   - leashes while watchful;
   - goes inert when tamed or when the setting is off.
3. `RM_Plant_Guarded : Plant`, about 20 lines. It overrides `PlantCollected` to call
   `Notify_Harvested(by)` and then the base method.
4. `ThinkTreeDef` insert at `Animal_PreMain` (about 40 lines + XML) is built **only if** the
   quicktest shows a lordless animal leaving `Wait_AsleepDormancy`. That behaviour is
   UNMEASURED.
5. `MentalStateDef RM_RoostDefence`: stateClass `RM_MentalState_ScopedAggression` (existing),
   category Aggro, no beginLetter, `recoverFromSleep false`.

**LeaningScrub, `mandrake.rm.leaningscrub`:**

6. `RM_Barkwarden` ThingDef + PawnKindDef, a reskin per spec §4/§10. It adds:
   - `CompCanBeDormant` with `startsDormant true`, `jobDormancy true`,
     `freezeNeeds [Food, Rest]`, and `dormantStateLabelKey` / `awakeStateLabelKey` set to our
     keys;
   - `CompWakeUpDormant` with `wakeUpOnDamage true` and the radius wake **off**;
   - `RM_CompRoostGuardian`.

   It is **not** in `wildAnimals`.
7. `RM_SweetlineTree.xml`: set `thingClass RM_Plant_Guarded` and add the roost comp under
   `MayRequire="mandrake.rm.creaturebehaviors"`. Update the description.
8. `Languages/English/Keyed/` for the roosting, watchful, stage and message strings.
9. Five settings in `RM_LeaningScrubMod.cs` (§5).

**Size:** about 450 lines of C# across 3–4 files, 3 XML files and 1 Keyed file. That is one
FOUNDRY build pass plus one quicktest. **Not blocked by tree placement:** the quicktest
dev-spawns the tree. **Players see nothing until** `TREE_GRAPHICS_OWNERSHIP_1` owed item 3
places trees.

**Quicktest** (minimal list + creaturebehaviors + leaningscrub, all DLC):

1. Dev-spawn the tree and confirm 2–3 roosting bark-wardens with frozen food.
2. Wait 2 in-game days and confirm they are still dormant. This is the UNMEASURED check.
3. Walk a colonist to 5 cells: watching sign only.
4. Designate a harvest: stirring, then restless, then the drop at about 60%.
5. Walk to 19 cells: they disengage, return to the trunk and re-roost once the meter is below
   0.3.
6. Shoot the tree twice: they wake.
7. Burn it: they wake watchful, attack no one, and the History shows it.
8. Kill the tree: they become free animals and stay on the map.
9. Tame one: it goes inert.
10. Try Hunt on a roosting one. This is UNMEASURED.
11. Save and load at each stage.
12. Flip each of the five settings live.

**Reconcile while building:** the spec's 8–14-day respawn sits against an 84-day wool regrow
(spec §11.3). With sleepers that the player can kill in advance, a respawn of **30–60 days** is
proposed, so that clearing a tree buys about one harvest.

## 7. Questions for the owner

1. **What happens when someone just walks up to a sweetline tree?**
   - **(a) Recommended: nothing hostile.** The bark-wardens wake enough to watch you, and you can
     see them watching. Only harm wakes them. Traders and travellers on the tree-roads are safe,
     and a colony can live beside a tree.
   - (b) The earlier spec's rule: anyone within 9 cells gets charged, with no warning. This
     makes every tree a no-go zone, and it mauls traders and visitors. It also needs a fix for
     colonies built nearby.
   - (c) Charge only someone who lingers under the tree for an hour or more. A middle ground,
     but one more rule for the player to learn.
2. **Does harvesting the wool wake them?**
   - **(a) Recommended: yes, gradually.** They visibly stir, then turn restless, then drop on
     the harvester about halfway through. Stop at the first warning, or bring guards. The
     harvest is a fight unless you are ready for it.
   - (b) No. Only wounding the tree wakes them, and the harvest is free. Simpler and safer, but
     the guardian only matters if you attack the tree.
   - (c) Yes, the moment work starts, with no build-up. Harsher, with a smaller window to back
     off.
3. **Are they on the tree from the start, or do they come out of it when harmed?**
   - **(a) Recommended: visible sleepers on the tree from the start.** You can see what you are
     about to disturb. You can also hunt or tame them first, which lets you clear a tree on
     purpose.
   - (b) Nothing visible until harm, then they burst out of the crown. This is the cheapest
     build (the wasp-gall machinery already does it), but it is a surprise attack, which your
     "readable sign" rule argues against.
4. **After a fight, how long until a tree forgives you?**
   - **(a) Recommended: it calms over about 5 days** (adjustable in settings). Then they sleep
     again.
   - (b) Never. A tree you have harmed stays hostile to everyone near it until its bark-wardens
     are dead, which makes it a permanent danger zone.
   - (c) Right away: once the culprit leaves, they settle. Very forgiving, so a second harvest
     attempt the same day is easy.
