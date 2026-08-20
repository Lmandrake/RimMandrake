# Mechanoid removal — offline feasibility study

> ⛔ **SUPERSEDED — DO NOT ACT ON THIS DOCUMENT.**
> **Owner's ruling, 2026-08-15: "We are keeping the mechanoids. Deprecate any
> action about turning mechanoids off."** O-v2 is dead and B25(c), the queue item
> that would have executed it, is deprecated. This study is kept as a record of
> what was measured, not as a plan. Its *mechanism* findings (what patches what,
> what Cherry Picker can and cannot reach) remain accurate and may be cited; its
> recommendations may not be revived.

**Seat:** a retired seat · **Date:** 2026-08-13 · **Game state:** DOWN (offline study only)
**Ask:** owner, relayed by a retired seat as O-v2 — cherry-pick out the mechanoid defs *and*
the `Mechanoid` faction; answer three questions.

**Nothing was changed.** No `ModsConfig.xml` edit, no Cherry Picker config written,
no mod folder touched. This document is the entire output.

## Sources of evidence

| what | where |
|---|---|
| Live def dump, 573 mods, captured today 14:51 UTC, game 1.6.4871 rev591 | `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\` |
| Cherry Picker assembly, disassembled with `ilprobe` | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3521312241\1.6\Assemblies\CherryPicker.dll` |
| Vanilla + DLC defs | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\{Core,Royalty,Ideology,Biotech,Anomaly,Odyssey}\` |
| Alpha Mechs | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2973169158\` |
| Mechs and Animals for NPC Factions | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3407831843\` |

Out of scope by instruction: `matathias.ruthlessmechanoids` (Ruthless Faction Pursuit —
the gravship pursuer redirect, not a mech mod despite the packageId).

---

## 0. The Cherry Picker schema — read from the assembly, not guessed

Cherry Picker is workshop `3521312241`, packageId `Owlchemist.CherryPicker`.
**It has no config file yet** — nothing matching `Mod_3521312241_*` exists in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\`
(78 entries checked). Its settings have never been saved.

The settings class is `CherryPicker.ModSettings_CherryPicker : ModSettings`, with
exactly one persisted field:

```
[public static] HashSet`1<...> allRemovedDefs
```

`ExposeData` scribes it under the label **`keys`**, not `allRemovedDefs`:

```
### ModSettings_CherryPicker::ExposeData
  IL_002e: ldsflda   ModSettings_CherryPicker::allRemovedDefs
  IL_0033: ldstr     "keys"
  IL_0039: call      MethodSpec#42          // Scribe_Collections.Look<string>
```

Each entry is a string key of the form **`TypeName/defName`**, and
`TypeName/defName/Namespace` when the def's type is not in a vanilla namespace.
From `DefUtility::ToKey` and `DefUtility::ToDefName`:

```
### DefUtility::ToKey
  IL_0011: callvirt  MemberInfo::get_Name       // e.g. "PawnKindDef"
  IL_0016: ldstr     "/"
  IL_001c: ldfld     Def::defName
  IL_0021: call      String::Concat             // -> "PawnKindDef/Mech_Scyther"
  ...
  IL_0031: ldsfld    DefUtility::assumedNameSpaces
  IL_003c: callvirt  Contains                   // vanilla ns -> stop here
  IL_0064: ldstr     "/"
  IL_006a: call      String::Concat             // else append "/Namespace"

### DefUtility::ToDefName
  IL_0001: ldc.i4.s  47                         // '/'
  IL_0004: callvirt  String::Split
  IL_000a: ldelem.ref [1]
```

So the file, once written, is `Mod_3521312241_ModSettings_CherryPicker.xml` with
`<keys><li>PawnKindDef/Mech_Scyther</li>…</keys>`.

🔴 **Do not hand-write it anyway.** Let the in-game Mod Settings UI create it once,
then edit that file. A typo'd key is silently ignored, so a hand-written list gives
no feedback that it did nothing.

---

## 1. Does the game still load with mechanoid defs and the `Mechanoid` faction removed?

### Short answer: **yes — because Cherry Picker does not actually remove them.**

The failure mode named in the ask, `Could not resolve cross-reference`, is emitted by
`DefDatabase.ResolveAllReferences` during startup def load. **Cherry Picker runs after
that has finished**, from a Harmony postfix on the main menu:

```
### Patch_MainMenuDrawer_MainMenuOnGUI::Postfix
  IL_0000: ldc.i4.1
  IL_0001: call    CherryPickerUtility::Setup
  IL_0006: ldstr   "Owlchemist.CherryPicker.Unpatcher"
  ...
  IL_002c: call    Harmony::Unpatch          // runs once, then unpatches itself
```

By the time `Setup` runs, every cross-reference in the game is already resolved.
**Cherry Picker is structurally incapable of producing a cross-reference error.**

And it goes further than that: for vanilla def types it does not delete the def at
all. `CherryPickerUtility::RemoveDef` reaches `DefDatabase<T>.Remove` on **exactly two**
type names — `PowerDef` and `PsycasterPathDef`, both Vanilla-Expanded types
(IL_0ff3–IL_1099). Every other type takes a branch that **zeroes its selection
weights in place** and jumps straight to the exit at `IL_1115`:

| def type | what "removing" it actually does | IL |
|---|---|---|
| `FactionDef` | `maxConfigurableAtWorldCreation = -1`, `startingCountAtWorldCreation = 0`, `requiredCountAtGameStart = 0` | IL_0ed9–IL_0ef1 |
| `PawnKindDef` | `combatPower = 0`, `canArriveManhunter = false`, `canBeSapper = false`, `allowInMechClusters = false`, `minGenerationAge = 0` | IL_0e48–IL_0e6d |
| `QuestScriptDef` | `rootSelectionWeight = 0`, `decreeSelectionWeight = 0` | IL_0b09–IL_0b15 |
| `IncidentDef` | `baseChance = 0`, `baseChanceWithRoyalty = 0`, plus `earliestDay` / `minThreatPoints` / `minPopulation` pushed out of reach | IL_0b26–IL_0b56 |
| `GenStepDef` | removed from every `MapGeneratorDef.genSteps` list | IL_0e72–IL_0eaa |
| `ScenarioDef` | `Scenario.showInUI = false` | IL_0ebc |
| `StorytellerDef` | `listVisible = false` | IL_0eaf |

**Nothing dangles, because nothing is deleted.** That is the direct answer.

### What DOES dangle — the other removal method

The dangle analysis is real, it just belongs to a *different* technique: XML deletion
(`PatchOperationRemove`, or disabling the mod that provides a def). If mech
ThingDefs/PawnKindDefs were removed that way, the damage would be severe, because
RimWorld resolves two shapes of reference very differently:

| XML shape | on missing def | verdict |
|---|---|---|
| `<li>Mech_Scyther</li>` (plain `List<Def>`) | entry silently dropped | degrades |
| `<Mech_Scyther>10</Mech_Scyther>` (dict-keyed: `PawnGenOption`, `mechKindOptions`, recipe `products`) | record kept with a **null** def; the next consumer that builds a weights dictionary throws far from the source | **hard break** |
| scalar `<race>`, `<pawnKind>`, `<mechKind>`, `<kindDef>` | field null → null `RaceProperties` cascades into worldgen | **hard break** |

Concrete hard-break sites if you went the XML route:

- `Data/Core/Defs/PawnKinds/PawnKinds_Breach.xml:25` — `PawnKindDef Mech_Termite_Breach`
  has scalar `<race>Mech_Termite</race>`. Remove the ThingDef and keep the PawnKindDef
  and you get NREs in map/world generation **with no mod named in the stack trace.**
- `Data/Core/Defs/ThingDefs_Buildings/Buildings_Ancient_Indoors.xml:553` —
  `AncientMechGestatorTank.mechKindOptions`, dict-keyed, scattered through ancient ruins.
- `Data/Odyssey/Defs/ThingDefs_Buildings/Buildings_Misc.xml:1348` —
  `MechhiveAssembler.options`, 13 dict-keyed mech kinds.
- `Data/Biotech/Defs/BossgroupDefs/Bossgroups.xml` — scalar `kindDef` plus ~60 dict-keyed
  escort entries.
- All mech gestation recipes — `<products><Mech_Militor>1</Mech_Militor></products>`.
- `Data/Biotech/Defs/Scenarios/Scenarios.xml:23` — `ScenPart_StartingMech` scalar
  `<mechKind>`; the Mechanitor scenario would not start.

And Alpha Mechs would be a total loss on the XML route: **100% of its mechs inherit
from vanilla abstracts** (`BaseMechanoidKind` ×26, `BaseMechanoid` ×13,
`BaseMechanoidWalker` ×10, `LancerMechanoidWalker` ×2, Biotech `LightMechanoid` ×10,
`NonCombatLightMechanoidKind` ×9, `HeavyMechanoidKind` ×3, `SuperHeavyMechanoid` ×3).
Even its own abstracts chain up to vanilla —
`…\2973169158\1.6\Mods\Biotech\Defs\ThingDefs_RacesMechanoids\Bases.xml:4`:
`<ThingDef Name="AM_MediumMechanoid" ParentName="BaseMechanoid" Abstract="True">`.

🔴 **Conclusion: use Cherry Picker, never XML deletion.** Same intent, and one of the
two routes cannot crash by construction.

### One vanilla assertion that removing the faction is unsupported

`Data/Odyssey/Defs/Scenarios/ScenParts_Various.xml:9`, on `ScenPartDef PursuingMechanoids`:

```xml
<preventRemovalOfFaction>Mechanoid</preventRemovalOfFaction>
```

Ludeon explicitly marks the Mechanoid faction as non-removable for the Odyssey gravship
scenario — which is the scenario family this campaign sits in. Cherry Picker's neutering
sidesteps the world-creation screen rather than satisfying this flag.

### And it does nothing to an existing save

All three fields Cherry Picker sets on a `FactionDef` are **world-creation** fields. On a
save whose world already contains the Mechanoid faction, that faction keeps existing and
keeps behaving normally. Cherry-picking the faction only affects a **new world**. Suppress
mech *encounters* in an ongoing game by cherry-picking the `IncidentDef`s and
`QuestScriptDef`s instead — those take effect on load.

---

## 2. Does `Samael.NPCMechsAndAnimals` survive, and does its ANIMALS half still work?

**Yes to both, and the two halves are cleanly separable — the cleanest result in this study.**

The mod is `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3407831843\`.
Its entire content is two files:

```
About/{About.xml, MNA.png, ModIcon.png, Preview.png, PublishedFileId.txt}
Patches/NPC_Animals.xml     258 lines
Patches/NPC_Mechs.xml       341 lines
```

**No `Assemblies/` folder. No Defs. Pure XML patches.**

`NPC_Animals.xml` contains **zero** occurrences of the string "mech"
(`grep -ci mech` → 0). It only adds wolves, wargs, bears, megaspiders, rhinos,
elephants, megasloths and Odyssey's great wolf / mastodon to tribal and outlander
`pawnGroupMakers`.

`NPC_Mechs.xml` touches **only non-mechanoid factions' `pawnGroupMakers`** — 30 xpath
targets across `OutlanderFactionBase`, `Pirate`, `PirateWaster`, `PirateYttakin`,
`OutlanderRoughPig`, `Empire`, `TradersGuild`. The defs it injects:

`Mechanitor` ×30, `Mech_Scyther` ×21, `Mech_Militor` ×21, `Mech_Pikeman` ×16,
`Mech_CentipedeGunner` ×6, `Mech_Lancer` ×4, `Mech_Cyclops` ×3, `Mech_CentipedeBurner` ×3,
`Mech_CentipedeBlaster` ×3, `Mech_Legionary` ×2, `Mech_Centurion` ×2, `Mech_Tesseron` ×1.

So the mech half of this mod is exactly "pirates and outlanders sometimes bring mechs".
Nothing in the animal half depends on it, and nothing in the mech half depends on the
animal half. There is **no assembly and no def chain joining them.**

**Two ways to kill the mech half and keep the animals:**

1. **Cherry-pick the mech PawnKindDefs** (`PawnKindDef/Mech_Scyther`, etc.). Their
   `combatPower` goes to 0 — the pawnGroupMakers still list them, and pawn group
   generation will still pick them but score them at zero points, which distorts raid
   sizing. Works, but it is the blunt instrument.
2. 🔴 **Better: neuter the file.** Copy the mod to
   `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\NPCMechsAndAnimals_AnimalsOnly\`,
   delete `Patches/NPC_Mechs.xml`, unsubscribe or disable the Workshop copy. Zero mech
   references remain and the animal half is byte-identical. **A Workshop folder must not
   be edited in place — Steam re-downloads it and silently reverts the change.**

---

## 3. Is `Samael.NPCMechsAndAnimals` configurable?

**No. It has no settings, and it cannot have any — there is no assembly to hold them.**

- No `Assemblies/` directory anywhere in the mod (full file listing above, 7 files).
- No `Mod_3407831843_*.xml` in the Config directory, and there never can be — a
  `ModSettings` subclass requires compiled code.
- `About.xml` declares no dependencies at all.

Cherry-picking (or the file deletion in §2) is the only lever for this mod. So the
"a toggle beats cherry-picking" test fails here.

### 🔴 BUT IT SUCCEEDS FOR ALPHA MECHS — AND THAT IS THE BIGGER FINDING

**Alpha Mechs already ships a per-mech on/off toggle in its mod settings, and the owner
has never touched it.**

`…\2973169158\1.6\Assemblies\AlphaMechs.dll` (49,664 bytes) contains
`AlphaMechs_Mod`, `AlphaMechs_Settings`, `GetSettings`, `DoSettingsWindowContents`, and
per-mech toggle keys: `AM_Aura`, `AM_Daggersnout`, `AM_Demolisher`, `AM_Fireworm`,
`AM_Goliath`, `AM_Phalanx`, `AM_Siegebreaker`, `AM_Apoptosis`, `AM_Infernus`,
`AM_WarEmpress`, `AM_Mech_Legate`, `AM_PristineStrider`.

Every core mech's `<description>` ends with a sentence the mod author wrote for exactly
this situation: *"If toggled to not spawn via mod options, they will get replaced by a
&lt;vanilla mech&gt;."*

And **no `Mod_2973169158_AlphaMechs_Mod.xml` exists** in the Config directory — the mod
is running on hardcoded defaults with everything enabled. **Nobody has opened its
settings page.** Any per-mech shaping of Alpha Mechs should start there, not in Cherry
Picker. *(`Mod_3316062206_AM_Mod.xml` in Config is a red herring — that ID is "Ancient
urban ruins".)*

---

## 4. ⚠️ THE ALPHA MECHS TENSION — reported, deliberately unresolved

**This is the owner's call. It is laid out here and not decided.**

Alpha Mechs defines **no FactionDef of its own** — `grep -rn "<FactionDef" 1.6/` returns
zero hits. It is a pure parasite on the vanilla `Mechanoid` faction. It attaches through
exactly two patch operations:

| file | line | xpath | adds |
|---|---|---|---|
| `…\2973169158\1.6\Patches\RaidGroups.xml` | 6 | `/Defs/FactionDef[defName = "Mechanoid"]/pawnGroupMakers` | 6 new `<li>` group makers (commonality 100/100/80/30/30/70) |
| `…\2973169158\1.6\Patches\BreachMechGroups.xml` | 4 | same xpath | 1 breach-raid `<li>` (commonality 0.5), the only spawn route for `AM_Demolisher` |

The live def dump confirms this landed. `FactionDef[Mechanoid].pawnGroupMakers` currently
has **14 group makers** carrying **24 distinct pawnkinds**, of which **7 are Alpha Mechs'**:

```
AM_Aura ×4   AM_Daggersnout ×5   AM_Demolisher ×1   AM_Fireworm ×2
AM_Goliath ×2   AM_Phalanx ×3   AM_Siegebreaker ×1
```

Group maker `li[13]` is Alpha Mechs' own `CAMechanoidPawnGroupKindCombatMixed`.

### So: cherry-picking `FactionDef/Mechanoid` takes Alpha Mechs' raids with it.

Alpha Mechs' pawns get their faction implicitly from
`Data/Core/Defs/ThingDefs_Races/Races_Mechanoid.xml:57` —
`<defaultFactionDef>Mechanoid</defaultFactionDef>` on `BaseMechanoidKind`. With no
Mechanoid faction generated in a new world, the scary animal-shaped mechs have nothing
to arrive as.

**Options, with costs. No recommendation is offered on this point.**

| option | what the owner keeps | what it costs |
|---|---|---|
| **A. Keep the Mechanoid faction; cherry-pick only the vanilla mech PawnKindDefs** | Alpha Mechs raids intact — `AM_Daggersnout` (insectlike), `AM_Fireworm` (worm), `AM_Phalanx` (rhino-beetle), `AM_Aura` (angel/moth), `AM_Demolisher` (crab/mole) still arrive | The faction is still called "mechanoid hive" in-fiction. Vanilla mechs zeroed to `combatPower 0` still appear in group makers, distorting raid point maths |
| **B. Cherry-pick the faction too** | No mechanoid anything in a new world | Alpha Mechs becomes dead weight — its raid content has no delivery vector. Its **cleaners survive** (see below) |
| **C. Keep the faction, rename it** | Everything works; "mechanoid hive" reads as a droid faction | A one-line `PatchOperationReplace` on `FactionDef[Mechanoid]/label` + `description`. Cheapest possible change. Does not remove a single mech |
| **D. Keep the faction, replace its roster** | Droids raid you instead of mechs, Alpha Mechs kept or dropped per-mech via its own settings toggle | A small patch mod — see §6 |

**The cleaners survive option B regardless.** They are player-buildable, not raid content,
and none of them route through `pawnGroupMakers`:

| defName | label | role |
|---|---|---|
| `AM_Mech_TurboCleaner` | turbocleaner | the literal cleaner — `CleaningSpeed 0.5`, `<li>Cleaning</li>` |
| `AM_Mech_MasterChef` | culinarius | cook |
| `AM_Mech_PristineAssembler` | pristine assembler | fabricator |
| `AM_Mech_PristineSlurrypede` | pristine slurrypede | feeder |
| `AM_PristineStrider` | pristine strider | hauler / mount |
| `AM_Mech_Apiarist`, `AM_Mech_Librarian`, `AM_Mech_Angler`, `AM_Mech_Geneticor`, `AM_Mech_Nucleotron`, `AM_Mech_Sanguinarius` | — | mod-gated specialists |

⚠️ **But they are built by a mechanitor**, and the mechanitor research chain is what
breaks worst (§5). Keeping the cleaners means keeping Biotech mechtech intact.

---

## 5. What BREAKS or becomes unwinnable

Faction Control's tooltip is right that removing mechanoids leaves them in ancient danger
rooms and quest objectives. The live set is worse than that, because this is an **Odyssey
gravship campaign** and Odyssey routes its core progression through mechanoids.

### 🔴 5a. The Odyssey endgame becomes unreachable — the worst finding

`GravEngine` (`Data/Odyssey/Defs/QuestScriptDefs/Script_GravShip.xml:26,36-48`) offers
nine gravcore subquests. The live dump confirms all of them present:

```
Gravcore_MechanoidRelay              ← mech
Gravcore_OrbitalMechanoidPlatform    ← mech
Gravcore_CrashedMechanoidPlatform    ← mech
Gravcore_Mechhive                    ← mech (the endgame location)
Gravcore_InsectLair
Gravcore_AncientReactor
Gravcore_AncientStockpile
Gravcore_OrbitalAncientPlatform
Gravcore_FrozenTerraformer
```

`Gravcore_Mechhive` has `<requiredSubquestsGiven>7</requiredSubquestsGiven>` (line 288).
Remove the three other mech gravcore quests and only **5 of the remaining 8** can ever be
given — **the 7-subquest gate is never met, and the Mechhive never unlocks.**

Ludeon's own comment says 7 was chosen so the chain survives the *Insect* faction being
disabled. It does not survive this.

**This lands squarely on the scope rule: everything ships THIN, except the gravship,
which ships DEEP.** Blocking the Odyssey gravship endgame is the single most expensive
consequence in this document.

Mitigation that costs nothing: cherry-pick the *quests* rather than the mechs, and leave
`Gravcore_Mechhive` alone. Or accept the mech-flavoured gravcore sites as
"ancient droid factory" and reskin them (§6).

### 🔴 5b. Permanent research dead-end (Biotech)

Three chips are gated behind super-heavy mech kills and bossgroup rewards, and have no
other source anywhere in the live set:

| chip | only source |
|---|---|
| `SignalChip` | Diabolus — `Data/Biotech/Defs/ThingDefs_Races/Races_Mechanoids_SuperHeavy.xml:544` |
| `PowerfocusChip` | Warqueen — same file `:419` |
| `NanostructuringChip` | Apocriton — same file `:94` |
| all three | `Data/Biotech/Defs/BossgroupDefs/Bossgroups.xml:116,233,362` |

They appear as `<requiredAnalyzed>` on:

- `StandardMechtech` → **permanently blocked**
- `HighMechtech` → blocked
- `UltraMechtech` → blocked
- **`WastepackAtomizer` → blocked**, which is the *only* toxic-wastepack disposal building

Every Alpha Mechs cleaner above tier 1 sits behind those research projects. **Removing
mechs removes the cleaners by a second route, even if their defs survive.**

### 5c. Quests that cannot complete

| quest | file | why |
|---|---|---|
| `MechanitorStartingMech` | `Data/Biotech/Defs/QuestScriptDefs/Script_StartingMech.xml:16` | `<mechKinds>` both gone → gives nothing. Fired automatically by installing a `Mechlink` |
| `MechanitorShip` | `Data/Biotech/Defs/QuestScriptDefs/Script_MechanitorShip.xml:42-79` | 6 scalar `<pawnKind>` refs |
| `Bossgroup` | `Data/Biotech/Defs/QuestScriptDefs/Script_Bossgroup.xml:32` | scalar `kindDef` + dict-keyed waves |
| `Gravcore_Mechhive` | `Script_GravShip.xml:288` | unreachable, §5a |
| `GravshipWreckage` | `Script_GravShip.xml` | all three descriptions promise "destroy a number of bothersome mechanoids"; the royal-asker variant can **hang** |
| Mechanitor scenario | `Data/Biotech/Defs/Scenarios/Scenarios.xml:23` | `ScenPart_StartingMech` scalar `<mechKind>` — scenario cannot start |

⚠️ **`OpportunitySite_MechanoidPlatform` has a vanilla copy-paste bug.**
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\QuestScriptDefs\Script_SpaceSites.xml`
line 394 (the game's own copy — not the same-named file under `vendor/mod_sources/`) guards on
`QuestNode_FactionExists <faction>Insect</faction>` — **not Mechanoid.** It will keep
firing while insects exist. Cherry Picker's neutering makes this harmless (the site still
generates, just with zero-power pawns); XML deletion would make it throw.

Only **2 of 29** hard `Mechanoid` faction references in Core/DLC XML are guarded by
`QuestNode_FactionExists` (both in `Data/Royalty/Defs/QuestScriptDefs/Scripts_ProblemCausers.xml`).
Everything else assumes the faction exists.

### 5d. Content that degrades quietly (playable)

- Ancient danger mech rooms: `ComplexThreatDef SleepingMechanoids`
  (`Data/Core/Defs/ComplexThreatDefs/ComplexThreats_Misx.xml:30`) and
  `SitePartDef SleepingMechanoids` — threat never arrives, room becomes free loot.
- Mech clusters: `IncidentDef MechCluster`, `SitePartDef MechCluster`, and the entire
  condition-causer family (`SunBlocker`, `PsychicDroner`, `ToxicSpewer`, 11 total) lose
  their only delivery vector. Condition-causer quests stop appearing.
- `DefoliatorShipPartCrash` / `PsychicEmanatorShipPartCrash` — the ship part still lands,
  undefended. Free psychic emanator.
- Mech spawners (`MechCapsule`, `MechAssembler`, `MechDropBeacon`) go inert —
  `<li>`-shaped lists, safe.
- `OrbitalTargeterMechCluster` has `<requiresFactionToAcquire>Mechanoid</requiresFactionToAcquire>`
  — never obtainable.
- Bossgroup call gizmos on the comms console and the two Biotech callers go dead.
- `GenStepDef AncientMechs`
  (`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Ideology\Defs\MapGeneration\CommonMapGenerator.xml`
  line 61 — the game's copy, not the same-named `vendor/mod_sources/CaveBiome` patch)
  scatters dormant ancient mechs on map gen — Cherry Picker strips it from
  `MapGeneratorDef.genSteps` cleanly.

### 5e. What is untouched

**Anomaly survives intact.** Its only mech contacts are a hediff blacklist entry, a
`CompProperties_MechPowerCell` class name, the `EntityMechanical` flesh type reusing mech
wound textures, and ~25 `<canTargetMechs>false</canTargetMechs>` booleans. Nothing spawns
mechs. Odyssey's `Drone_Hunter` / `Drone_Wasp` / `Drone_Sentry` are a separate race family
and are unaffected.

---

## 6. 🔴 THE REFRAMING — and the finding that settles it

The campaign is a Jawa scavenger clan on a desert world. Mechanoids are not Star Wars.
**Droids are.** The premise of the reframing was that replacing mech encounters with
droid encounters might beat removing them.

**It turns out the replacement is already installed and already running.**

From the def dump manifest (573 mods, captured today 14:51 UTC):

| load order | mod | packageId |
|---|---|---|
| 27 | [JDS] StarWars - Armory | `m3.continued.jangodsoul.starwars.bti` |
| **419** | **[JDS] StarWars - The Separatist Droid Army** | `m3.continued.jangodsoul.starwars.tsda` |
| **546** | **Outer Rim - Droid Depot** | `neronix17.outerrim.droiddepot` |
| **571** | **Star Wars KotOR Droids** | `guy762.kotordroids` |
| 565/566/572 | KotOR Resources, Weapons, Ship Pack | `guy762.*` |

### 🔴 Two hostile droid factions are already live, and they are structural twins of the Mechanoid faction

Read straight out of the live `FactionDef` dump:

| field | `Mechanoid` (Core) | `guy762_KotORFaction_RogueDroids` | `JDSCIS_CIS_Faction` |
|---|---|---|---|
| label | mechanoid hive | rogue droid collective | Confederacy of Independent Systems |
| `permanentEnemy` | **true** | **true** | **true** |
| `hidden` | **true** | **true** | **true** |
| `humanlikeFaction` | false | false | false |
| `startingCountAtWorldCreation` | 1 | 1 | 1 |
| `requiredCountAtGameStart` | 1 | 1 | 1 |
| `canMakeRandomly` | false | false | false |
| techLevel | Ultra | Spacer | Spacer |
| **`pawnGroupMakers`** | **14** | **7** | **8** |

Same shape, same role, same delivery mechanism — and the group makers are fully
populated, verified entry by entry in the live dump. KotOR's seven are all `Combat`
(commonality 100/100/75/50/25/25/10). The CIS's eight are seven `Combat` plus one
**`Settlement`** maker with 10 kinds, so the Separatists also have raidable bases —
something the mechanoid hive does not have. They have full rosters —
14 KotOR rogue-droid kinds at `combatPower` 35–500 (`KotORDroidBad_ADMkIV`,
`KotORDroidBad_hk50boss` at 500; `KotORDroidBad_KX12APD_sapper` is a sapper), and 16
Separatist kinds (`JDSCIS_B1_Battle_Droid`, `JDSCIS_B2_Super_Battle_Droid`,
`JDSCIS_Droideka_Droid`, `JDSCIS_IG-100_MagnaGuards`, `JDSCIS_BX_Commando_Droid`, …).

A third, `OuterRim_RogueDroidColony` ("Rogue Droids"), exists as a non-hidden
industrial-tech faction with no group makers of its own; Droid Depot's other 20 kinds
are `PlayerColony` — those are droids the Jawas *build*, which is exactly the right
fiction and is entirely unaffected by anything in this study.

The KotOR rogue droid faction is not merely similar to the mechanoid hive — its
`raidCommonalityFromPointsCurve` and `maxPawnCostPerTotalPointsCurve` are **byte-for-byte
identical to vanilla `Mechanoid`**, and it uses `ActiveDropPodMechanoid` /
`DropPodIncomingMechanoidRapid` for arrival. It is a deliberate structural clone,
already tuned to carry the same threat load.

### ⚠️ One real behavioural difference: the droids are humanlike alien races

Chain: `guy762_DroidRace_*` → `guy762_KotORDroidBase` → `ABF_Thing_Synstruct_HumanlikeBase`
(Artificial Beings Framework, `Killathon.ArtificialBeings`). That base sets
`intelligence Humanlike`, `thinkTreeMain Humanlike`, `fleshType ABF_FleshType_Synstruct_Base`
— **not** `fleshType Mechanoid`.

Mechanically they still *feel* like mechs: `needsRest false`, `foodType None`,
`isImmuneToInfections true`, `hasMeat false`, `specificMeatDef Steel`, and per-race
`blacklistedNeeds` covering Joy, Beauty, Comfort, Outdoors, Indoors, RoomSize and **Mood**,
with `canBeSapient false`. But three differences are player-visible:

- They can be **downed, captured and reprogrammed** (`pawnState Reprogrammable`). Mechs cannot.
- They carry **real apparel and weapons**, so their raids **drop loot**. Mech raids drop slag.
- Anything gated on `RaceProps.IsMechanoid` — mech shredding, full EMP effect, bossgroup
  calls, mech-specific incident text — will not fire on them.

For a Jawa **scavenger** clan, "the robots that attack you leave salvageable parts and can
be captured and reprogrammed" is arguably better fiction than vanilla mechs, not worse.
Flagging it as a change, not a defect.

### What that means

**"Replace mechanoid encounters with droid encounters" is already done.** No patch mod
is needed. The robot-enemy niche is *double*-covered by two permanent-enemy hidden
factions built the same way vanilla builds the mechanoid hive. Removing or suppressing
mechanoid raids therefore leaves **no hole in the threat roster** — it removes a
duplicate.

That collapses the option space:

### C — Rename only. One patch operation. ~15 minutes. **Zero risk.**

`PatchOperationReplace` on `FactionDef[defName="Mechanoid"]/label` and `/description`
(and optionally `/factionNameMaker`). "mechanoid hive" becomes a third droid faction in
name. **Nothing breaks. Nothing is removed. Every quest, every gravcore, every research
chain, every Alpha Mechs raid and every cleaner keeps working.** The Odyssey endgame is
untouched. Alpha Mechs' animal-shaped mechs read as war droids without a single def
change — which is precisely the "keep them, possibly renamed" the owner asked for.

*"Mechanoids are not Star Wars"* is a fiction complaint. A rename is a fiction fix, and
it is the cheapest action in this document by an order of magnitude.

### D — Roster swap into the Mechanoid faction. Feasible, ~200 lines, no C#.

For ordinary raids this is largely redundant now — two droid factions already raid on
their own group makers, so importing droids into the mechanoid faction duplicates work
the load order already does.

**Where D still buys something C does not: the non-raid encounters.** Ancient danger
rooms, mech clusters and sleeping-mech sites do *not* read the faction's roster the way
I assumed when writing §5d — they read it more directly than that:

```xml
<!-- Data/Core/Defs/ComplexThreatDefs/ComplexThreats_Misx.xml:30 -->
<ComplexThreatDef Name="SleepingMechanoids" ParentName="SleepingThreat">
  <workerClass>ComplexThreatWorker_SleepingMechanoids</workerClass>
  <faction>Mechanoid</faction>          <!-- no pawnkind list at all -->
</ComplexThreatDef>
```

It exposes **only `<faction>`**; pawn selection happens in C# by resolving that faction's
`pawnGroupMakers`. Same for the older ancient-danger path (`RuleDef SleepingMechanoids` →
`SymbolResolver_SleepingMechanoids`). **So patching `FactionDef[Mechanoid]/pawnGroupMakers`
converts ancient-danger sleeping mechs to droids for free, with zero extra patch work.**
That is the one thing a rename cannot do, and it is exactly the case Faction Control's
tooltip warns about.

The three mech spawner buildings need their own three-line patches, and their
`spawnablePawnKinds` are **plain `List<PawnKindDef>`, not mech-typed** — vanilla itself
uses the same comp for insects (`CocoonLocust`,
`Data/Odyssey/Defs/ThingDefs_Buildings/Buildings_Misc.xml:548`), which proves arbitrary
pawnkinds are accepted.

| # | xpath target | ~lines |
|---|---|---|
| 1 | `FactionDef[defName="Mechanoid"]/pawnGroupMakers` (replace wholesale) | 110–140 |
| 2 | `ThingDef[defName="MechAssembler"]//spawnablePawnKinds` | 8 |
| 3 | `ThingDef[defName="MechCapsule"]//spawnablePawnKinds` | 8 |
| 4 | `ThingDef[defName="MechDropBeacon"]//spawnablePawnKinds` | 8 |
| 5 (opt) | `AncientMechGestatorTank/mechKindOptions` | 6 |
| — | `About.xml` + `PatchOperationFindMod` guards | 40 |

**4–5 targets, ~180–210 lines of XML, no C#.** No hard blockers found:
`defaultFactionType` is only consulted when a pawn is generated with no explicit faction
(group makers pass it explicitly); `useFactionXenotypes false` on the droid base makes
xenotypes moot; apparel is pawnkind-driven; and `humanlikeFaction=false` with humanlike
alien races is already proven to work — the RogueDroids faction does exactly that today.

Two caveats: copy the `disallowedStrategies` blocks across (vanilla Mechanoid has none,
so droids would otherwise get siege/breach strategies the droid mod deliberately
restricts), and **the mech *architecture* stays** — turrets, `MechCapsule` shells,
`ChunkMechanoidSlag`. Only the pawns change. If the objection is total and aesthetic,
D leaves vanilla-mech furniture on the map.

⚠️ The `LordJob_MechanoidsDefend` on all three spawners is not mech-gated and should
drive humanlike pawns fine, but that is reasoned from XML alone — **smoke-test it on the
live bridge before trusting it.**

### B — Remove. Costs the Odyssey endgame; buys less than it looked like it would.

Everything in §5 still applies — the Mechhive gate, the mechtech research chips, the
mechanitor quests. What has changed is the upside: removal no longer *adds* Star Wars
flavour, because the flavour is already present. It only subtracts vanilla content.

---

## RECOMMENDATION

### (a) Safe and cheap — do these

1. 🔴 **Rename the `Mechanoid` faction (option C) and stop there for now.** One
   `PatchOperationReplace` on `label` + `description`. Two droid factions already raid
   this colony (§6), so the fiction complaint is satisfied by naming rather than
   deleting, at zero mechanical risk and zero cost to the gravship endgame. **Highest
   value-per-minute action in the study.**
2. 🔴 **Open Alpha Mechs' mod settings before doing anything else destructive.** It has
   never been opened; no config file exists. It already has per-mech toggles with
   automatic vanilla fallback. If the owner's objection is to specific Alpha Mechs pawns,
   this is the whole fix and it costs one settings page.
3. **Split `Samael.NPCMechsAndAnimals`.** Copy it to
   `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\NPCMechsAndAnimals_AnimalsOnly\`,
   delete `Patches\NPC_Mechs.xml`, disable the Workshop copy. Zero risk — the two halves
   share nothing. Pirates and outlanders stop bringing mechs; tribals keep their wargs.
   **Never edit the Workshop folder in place; Steam reverts it.**
4. **If specific mech encounters must go, cherry-pick the `IncidentDef`s and
   `QuestScriptDef`s, not the pawns.** Cherry Picker zeroes their selection weights,
   which is precise, reversible, and takes effect on an existing save. Cherry-picking
   pawns only zeroes `combatPower`, which distorts raid sizing without stopping spawns.
5. **If ancient danger rooms are the specific irritant, do option D target 1 alone.**
   `ComplexThreatDef SleepingMechanoids` carries no pawnkind list — only
   `<faction>Mechanoid</faction>` — so a single `PatchOperationReplace` on that faction's
   `pawnGroupMakers` converts sleeping-mech rooms to droids with no other patch needed.
   **This is precisely the case Faction Control's tooltip says removal cannot fix, and
   replacement fixes it where removal does not.**

### (b) Risky — understand the cost first

5. **Cherry-picking `FactionDef/Mechanoid`.** Only affects **new world generation** — it
   does nothing to an existing save. It takes Alpha Mechs' raid content with it (§4). And
   vanilla explicitly marks the faction non-removable for the Odyssey scenario
   (`preventRemovalOfFaction`).
6. **Cherry-picking the mech gravcore quests.** Drops the giveable gravcore pool from 9
   to 5 and permanently locks `Gravcore_Mechhive` behind its 7-subquest gate. **Do not do
   this while the gravship is v1-DEEP scope.**
7. **Any XML-deletion route** (`PatchOperationRemove`, disabling a mech-providing mod).
   This is the only route that produces `Could not resolve cross-reference` and NREs with
   no mod named in the trace. Cherry Picker's neutering is strictly safer for the same
   intent.
8. **Cherry-picking Biotech mech PawnKindDefs** while wanting Alpha Mechs' cleaners — the
   cleaners need the mechtech research chain, which needs chips that only super-heavy
   mechs drop (§5b).

### (c) Only the owner can decide

- **The Alpha Mechs / Mechanoid-faction tension.** Alpha Mechs has no faction of its own
  and hangs entirely off `FactionDef[Mechanoid]/pawnGroupMakers` — 7 of the 24 pawnkinds
  in that faction's group makers are `AM_*`. Removing the faction removes its raids.
  Keeping the faction keeps mechanoids in the fiction. **Options A–D are laid out in §4
  with their costs; this study deliberately recommends none of them.**
- **Remove versus rename, now that replacement turns out to be already done.** §6 shows
  two hostile droid factions (`guy762_KotORFaction_RogueDroids`, `JDSCIS_CIS_Faction`)
  already raid with 7 and 8 group makers, built the same way as the mechanoid hive. So
  the choice is narrower than it looked: rename the mechanoid faction into a third droid
  faction, or delete it and accept §5. Which reads better in the Jawa fiction is a
  taste call, not a technical one.
- **Whether the Odyssey gravcore endgame matters enough to protect.** If the campaign is
  never going to chase the Mechhive, §5a stops being a blocker and option B gets much
  cheaper.

---

*Method note for the next reader: Cherry Picker's behaviour above was read out of
`CherryPicker.dll` with `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\ilprobe\il.py`, IL
offsets cited inline. The live-set counts came from the def dump captured 2026-08-13
14:51 UTC, not from the offline Data tree — the two differ, and the dump is what the game
actually loaded.*

*One correction logged so it is not re-litigated: a sweep of the Workshop `About.xml`
files concluded `neronix17.outerrim.droiddepot` was not installed. It is —
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3096501398`, load order
546, `ModsConfig.xml:549`, and its `OuterRim_*` pawnkinds are in the live dump. **When
the offline tree and the def dump disagree about what is loaded, the dump wins.**
The `_DroidsBase` abstracts also live in a third mod (`guy762.MM.KotORCore`,
workshop `3254370945`) behind an `IfModActive` LoadFolders gate, which is why
folder-level greps under-report this mod family.*
