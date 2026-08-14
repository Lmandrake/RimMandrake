# Cherry Picker — the resolved target list

_CREATE, 2026-08-14. **VISION's `cherrypick_inbox.md` names races and objects;
this resolves every one to the def the game actually keys on.** Every row below
was read from the live def dump, not from the design doc and not from memory._

🔴 **Read `§0 The key format` before entering anything.** A wrong def TYPE is not
a wrong guess, it is a silent miss — and several of these names exist as four or
five different def types at once.

---

## 0. The key format, read from `CherryPicker.dll` IL

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
