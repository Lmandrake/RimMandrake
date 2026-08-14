# Cherry Picker — the resolved target list

_CREATE, 2026-08-14. **VISION's `cherrypick_inbox.md` names races and objects;
this resolves every one to the def the game actually keys on.** Every row below
was read from the live def dump, not from the design doc and not from memory._

🔴 **Read `§0 The key format` before entering anything.** A wrong def TYPE is not
a wrong guess, it is a silent miss — and several of these names exist as four or
five different def types at once.

---

## 0. HOW IT IS APPLIED — a hand-written file works, and no restart is needed

**Read from IL, not assumed.** `CherryPickerUtility` carries
`[StaticConstructorOnStartup]` and its `.cctor` ends `Setup(false)`:

```
Mod_CherryPicker::.ctor -> GetSettings<ModSettings_CherryPicker>
    -> ReadModSettings -> ExposeData -> Scribe_Collections.Look(allRemovedDefs, "keys")
StaticConstructorOnStartupUtility.CallAll()
    -> CherryPickerUtility::.cctor -> Setup(false)
        -> MakeWorkingList   (reads allRemovedDefs)
        -> ProcessList       (resolves each key, calls RemoveDef)
```

⇒ **No UI interaction, no click-OK, no settings write.** The removals are applied
inline during the startup pass of the load we are already paying for.

⚠️ **`Scribe.mode == 1` is `Saving`, not `LoadingVars`** — so the `ProcessList`
call inside `ExposeData` fires only when the settings window is closed. The
startup path above is the one that matters, and it is unconditional.

⚠️ **Restart dialogs exist but do not apply to us.** `CherryPicker.RestartRequired`
is raised only from the *restore* path (un-picking something), and the reload
dialog only when `ProgramState == Playing`. A fresh, additive list needs neither.

---

## 0b. 🔴 THE TWO WAYS A HAND-WRITTEN FILE FAILS SILENTLY

**1. A key with no `/` kills the ENTIRE remaining list.**
`DefUtility::ToDefName` is `key.Split('/')[1]` with **no bounds check**
(IL_0000–IL_000b). A key containing no slash throws `IndexOutOfRangeException`,
and that call sits in `MakeWorkingList` / `ProcessList` — **outside**
`RemoveDef`'s catch. `ProcessList` has no catch of its own, so it propagates up
to `Setup`, which logs `[Cherry Picker] Error processing master def list...` and
returns. **Every removal after the bad key is lost.** One typo, no picks.

**2. A def outside `allDefs` is accepted and never applied — with no report line.**
`allDefs` is not every def. `ThingDef`s are filtered to category **Item / Building
/ Plant / Pawn** only, excluding blueprints, frames and `isUnfinishedThing`;
`PawnKindDef` excludes `Colonist`; `FactionDef` requires
`maxConfigurableAtWorldCreation > 0`; `QuestScriptDef` requires that no
`IncidentDef` references it. **Out-of-scope keys produce no FAILED line** — they
are simply dropped from the working set and kept in the file forever.

⇒ **Validate offline before writing: exactly one or two `/`, and the def in
scope.** Those two checks are the whole difference between a working file and a
wasted load.

---

## 0c. What "removal" actually does

**13 def types are really deleted** from the database — `RecipeDef`, `TraitDef`,
`ResearchProjectDef`, `DesignationCategoryDef`, `MemeDef`, `PreceptDef`,
`RitualPatternDef`, `HairDef`, `BeardDef`, `TattooDef`, `BackstoryDef`,
**`GeneDef`**, `XenotypeDef`. Everything else is **neutered in place**.

`PawnKindDef`: `combatPower = float.MaxValue`, `canArriveManhunter`,
`canBeSapper`, `allowInMechClusters` all false, `minGenerationAge = 0`. The
`CompProperties_SpawnerPawn` strip happens separately in `PostProcess`, via
`spawnablePawnKinds.RemoveAll(processedDefs.Contains)`.

⚠️ **`HediffDef` is a NO-OP inside `RemoveDef`** — it returns immediately. Hediffs
are blocked at runtime instead, by a Harmony prefix on
`Pawn_HealthTracker.AddHediff`. So picking a HediffDef works, but by a different
mechanism.

---

## 0d. The key format, read from `CherryPicker.dll` IL

Cherry Picker stores one string per removal. `DefUtility.ToDefName` is
`key.Split('/')[1]` and `ToType` is `[0]`, with an optional `[2]` namespace
(`ldc.i4.s 47` = `/`). So:

```
<DefType>/<defName>            e.g.  PawnKindDef/ShamblerSoldier
```

Settings file, format confirmed against other mods' saved settings:

```
Config/Mod_3521312241_Mod_CherryPicker.xml
  <SettingsBlock>
    <ModSettings Class="CherryPicker.ModSettings_CherryPicker">
      <keys>
        <li>PawnKindDef/ShamblerSoldier</li>
      </keys>
```

⭐ **A bad key is NOT silent.** `CherryPickerUtility.ProcessList` appends
`" - FAILED: <key>"` to its report for anything that will not resolve. That
report is the confirmation this list is correct.

---

## 1. 🔴 The three findings that would have wasted the reload

### a. `Shambler` is not a race, and there is no `Shambler` PawnKindDef

The inbox lists it under "race defName". **There is no `ThingDef/Shambler` and no
`PawnKindDef/Shambler`.** A shambler is a *mutant*: an ordinary corpse with a
`MutantDef` applied. Entering `ThingDef/Shambler` or `PawnKindDef/Shambler` gives
two FAILED lines and removes nothing.

The real surface is **six defs**, and four of them are incidents:

| key | what it is |
|---|---|
| `IncidentDef/ShamblerAssault` | shambler assault |
| `IncidentDef/ShamblerSwarm` | shambler swarm |
| `IncidentDef/SmallShamblerSwarm` | shambler swarm (small) |
| `IncidentDef/ShamblerSwarmAnimals` | shambler swarm (animals) |
| `PawnKindDef/ShamblerSoldier` | shambler soldier |
| `PawnKindDef/ShamblerSwarmer` | shambler swarmer |

⚠️ **Deadlife dust raises shamblers independently of any incident.** If shamblers
must not appear *at all*, the delivery items go too: `ThingDef/Grenade_Deadlife`,
`ThingDef/Shell_Deadlife`, `ThingDef/TrapIED_Deadlife`,
`ThingDef/Apparel_DeadlifePack`, `ThingDef/GrayStatueDeadlifeDust`.
**Owner's call — these are player-usable tools, not spawns.**

⚠️ **Three OTHER mods add shambler content that a vanilla pick does not touch:**
Alpha Genes ships ~20 `AG_Shambler_*` `GeneDef`s plus `AG_DeadlifeProducer` and
`AG_PseudoDeadlife`; Utility Columns adds `DeadColumnMod`; Vanilla Landmarks
Expanded adds `VEE_DeadlifeVent`. **Out of scope until ruled on.**

### b. `Ghoul` needs three keys, not one — and the inbox named only the recipe

| key | why |
|---|---|
| `PawnKindDef/Ghoul` | stops it being generated |
| `RecipeDef/GhoulInfusion` | the surgery that makes one — the inbox is right that this must go |
| `IncidentDef/GhoulAttack` | ⭐ **not in the inbox.** The incident that sends them at you; leaving it in is a ghoul raid with the kind removed |

⚠️ `MutantDef/Ghoul` also exists. Removing the PawnKindDef and the incident
should be enough; the MutantDef is the template a ghoul is made *from*.
**Do not remove `ResearchProjectDef/GhoulInfusion`** unless the owner wants the
research tab entry gone too — that is cosmetic, not behavioural.

### c. `AG_MeatBurst` is BOTH a `GeneDef` and a `HediffDef`

Alpha Genes ships the same name twice. **The gene is the one to cull —
`GeneDef/AG_MeatBurst`.** Entering `HediffDef/AG_MeatBurst` removes the effect's
carrier and leaves the gene selectable.

---

## 2. The list, ready to enter

### Anomaly creatures

| key | note |
|---|---|
| `PawnKindDef/Metalhorror` | ⚠️ also `ThingDef/Metalhorror` and `CreepJoinerBaseDef/Metalhorror` exist. Arrival is `IncidentDef/CreepJoinerJoin_Metalhorror` + `QuestScriptDef/CreepJoinerArrival_Metalhorror` — **remove the incident or they still arrive** |
| `PawnKindDef/Trispike` | see §3 — a patch already ships for the half a pick cannot reach |
| `PawnKindDef/Ghoul` + `RecipeDef/GhoulInfusion` + `IncidentDef/GhoulAttack` | §1b |
| the six shambler keys | §1a |

### Anomaly objects and items

| key | note |
|---|---|
| `ThingDef/GoldenCube` | `baseChance` is already 0 |
| `ThingDef/WarpedObelisk_Duplicator` | ⚠️ **`IncidentDef/WarpedObelisk_Duplicator` also exists** — same name, different type. Remove both or the incident still fires |
| `ThingDef/WarpedObelisk_Abductor` | ⚠️ same — an `IncidentDef` of the same name exists. Intended to orphan `LayoutRoomDef LabyrinthObelisk` |
| `ThingDef/RevenantSpine` | |
| `ThingDef/VoidNode` | artwork retained — removing a def does not delete a texture, so this is satisfied by construction |

### The two fleshbeast genes (VISION follow-on 2)

| key | note |
|---|---|
| `GeneDef/AG_MeatBurst` | §1c — the GeneDef, **not** the HediffDef |
| `GeneDef/Turn_Gene_FleshbeastBurster` | Integrated Genes |

---

## 3. What a cherry-pick CANNOT do, and what ships instead

🔴 **Cherry Picker neutralises; it does not delete.** Removing a `PawnKindDef`
sets `combatPower = float.MaxValue` and clears the cluster / manhunter / sapper
flags — that stops the kind being **selected** by anything that weighs
candidates. It does not stop a def that **names the kind directly**.

`DeathActionWorker_Divide` names kinds directly. So a cherry-picked Trispike
would still pour out of every Bulbfreak and Dreadmeld that dies.

✅ **Covered by `Jawa_Patches/Patches/Fleshbeast_TrispikeCull.xml` (`2fd57c2`)** —
strikes Trispike from `Bulbfreak`'s `dividePawnKindOptions` and from
`Dreadmeld`'s `dividePawnKindAdditionalForced` (which is *forced*, not weighted,
so nothing degrades gracefully). Already deployed.

⭐ **Generalises: cherry-picking a def stops it being SELECTED, never being
SUMMONED by name.** Before picking any creature, grep the dump for its defName
inside other defs' fields.

---

## 4. Still open

- **`FleshmassHeart` picks its defender kinds in C#, not in any def** — what the
  adult sarlacc spawns cannot be established offline. Live check.
- **Mechanoids, SW xenotypes, biomes** — no verdicts yet; do not pick.
- Whether the deadlife delivery items and the third-party shambler content in
  §1a are in scope.
