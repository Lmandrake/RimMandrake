<!-- status: live — phase 0 of DROID_SYSTEM_EMBRACE_1 -->
# Droid verb census — what the accepted mods actually ship (2026-08-29)

Three parallel subagent sweeps of the mod XML on disk, against frozen dump
`OFFICIAL-2026-08-29` (584). Every row was read from a def unless marked
UNCERTAIN. Curation surface: `droid_verbs_sheet.html` → `droid_verbs_decisions.json`.

## The structural finding

**Three frameworks coexist, and they don't overlap:**

| framework | carries | capturable? | verbs |
|---|---|---|---|
| **ABF/Synstructs + HAR** | all KotOR droids (44 kinds, 32 backstories) | ✅ downs like a human | rich (C#) |
| **Asimov** (Neronix17) | all Droid Depot droids (19 kinds, 10 traits) | ✅ reprogram job | rich (C#) |
| **vanilla Biotech mechanoid** | all JDS Separatists (15 kinds) | ⛔ force-killed (ruled feature) | zero original |

🔴 **KotOR Droids hard-depends on Synstructs Core** (`Killathon.ArtificialBeings`
+ `.SynCore` in its modDependencies). The ruled capture target already rides the
richest framework — the spine question is half-answered by the load order we ship.

JDS and ABF are structurally incompatible for content sharing: JDS droids are
plain mechanoid ThingDefs, ABF droids are HAR alien races. Backstories/traits
cannot cross that line without converting the race (a rewrite, not a patch).

## ABF/Synstructs verbs (all CONFIRMED from XML)

- Inert-but-repairable states replace death/downed (`ABF_Hediff_Artificial_*`).
- **Formatting**: live conversion mindless drone ↔ programmable ↔ sapient ↔ blank
  (`Format*` recipes, `ArtificialBeings.Recipe_Make*`); deformatting a sapient is
  explicitly flagged as murder.
- **Directives**: 18 drone perks on a `complexityCost` budget (work 8 / combat 9 /
  social 1) — a whole perk system for drones.
- Energy + component **needs** replace food/rest; manual chemfuel/component
  top-off surgeries; **charging infrastructure**: room Beamcoil, assignable
  Enervoir dock, Powerjack wall socket.
- Overclock (reversible), part swap/restore via PartPacks, blank-body **Cradle**
  (16.5k work), anti-droid **hack abilities** (force-berserk, interference).
- Reprogram-as-recruit: `pawnState Reprogrammable` +
  `playerReprogrammableDronePawnKindDef` maps every wild kind to a colonist kind,
  with `initialResistanceRange` — recruitment resistance, droid-flavored.

## KotOR content on top (CONFIRMED)

24 player kinds (incl. heroes HK-47, T3-M4) + 20 rogue kinds; 19 model-specific
childhood backstories + 13 service adulthoods (`guy762BSC_Droid_*` categories —
**our Assembly × Service-Record set has ready-made slots**). Upgrade **modules as
apparel** in droid-only body groups (hardware/software/sensor/gadget/weapon/
shield). Repair kits eaten like meds (burst healing). Bench droid **generators**
(16, `CompProperties_PawnSpawner`). Batteries as food. Shield-recharge bench
recipes. Stun/poison/frostbite immunity. **Exactly two explosive droids**:
KX-12 probe (known) and the **Gonk** building-variant (new finding). Corpses
salvage to materials — **no rebuild verb exists in KotOR**.

## Asimov / Droid Depot verbs (CONFIRMED unless noted)

- **Restraining bolt** — real mechanics: Talking 0, Manipulation ×0.75, slave
  suppression locked, trait breaks suppressed, `isViolation` (slavery-like).
  Install/remove surgeries + a 600-tick **field clamp job** on downed droids.
- **Memory wipe** (`Recipe_WipeDroid`): zero skills, factory reset from backstory
  or `Comp_Automaton`, clears traits AND relations, faction → player.
- **Capture** = `JobDriver_ReprogramDroid` (600 ticks, prisoner/downed →
  `SetFaction(player)`). Trigger JobDef not located — UNCERTAIN how invoked.
- **Reactivation kit**: heals everything; on a corpse calls `TryResurrect`,
  improvises missing limbs. The rebuild verb KotOR lacks.
- Skill **data-disks** (+1 level, droid-only), damage/EMP **shielding implants**,
  **droid factory** (`Asimov.Building_AutoCrafter`, 19 recipes), corpse butchery
  + live-droid shutdown disassembly, 10 personality traits + 2 droid-only mental
  breaks (Rebellious, Loose Screws). `Comp_DroidHealer` aura exists but was not
  seen attached to any ThingDef — UNCERTAIN.
- **No power/recharge need at all** — a metabolism inconsistency with ABF's
  battery-eaters, unruled.
- ⚠️ Robustify: GNK droid rides VEF `CompProperties_Electrified` and TabulaRasa
  classes with **no declared modDependency** — silent no-op risk.

## JDS Separatists (CONFIRMED; extends the 2026-08-13 ruling)

Pure-XML mechanoid reskin, no DLL, zero original verbs. Everything is Biotech
plumbing: gestator recipes and `JDSCIS_ResurrectDroid_Light/_Heavy` exist ONLY
inside a `PatchOperationFindMod [Biotech]` block (new finding: hard gate).
Dormancy, mechanitor control, Droideka shields — all vanilla comps. Ships a
`TSDA_Commander` scenario (irrelevant to the campaign). B1 Commander has a
`MayRequire aoba.framework` relay comp.

## Discrepancy corrected

`droid_ruling.md` said Droid Depot is capturable "via data spike". **No data
spike exists in any accepted mod** — the verb is the reprogram job above. The
ruling doc now carries the correction; "data spike" survives only as a candidate
verb WE might author (owner named it for v2).
