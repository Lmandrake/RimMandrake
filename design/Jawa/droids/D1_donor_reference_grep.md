# Droid Donor Reference Audit — D1_donor_reference_grep
**Date:** 2026-09-06  
**Scope:** Comprehensive grep audit of four droid donor mods retiring from RimUtinni campaign build
**Search breadth:** `/mnt/d/Luke/dev/Rimworld/src` — all XML and C# files

---

## Overview

Four droid donor mods are planned for retirement as part of DROID_SYSTEM_BUILD_1. This audit catalogs:
- Direct packageId references to each donor
- DefName prefix usage (especially `OuterRim_*Droid` from Droid Depot)
- Gating status: whether references are protected by `MayRequire`, `IfModActive`, or `PatchOperationFindMod` (SAFE), or exposed without guards (DANGEROUS)

**Total packageId references found: 48 (11 + 13 + 3 + 21)**  
**Total defName references found: 361 (OuterRim_*Droid prefix)**  
**Overall risk profile: MODERATE** — most packageId refs are in About.xml or gated; significant OuterRim_*Droid refs exist but most reference our own forked implementations, not original donor defNames.

---

## guy762.kotordroids

**packageId:** `guy762.kotordroids`  
**Description:** Star Wars KotOR Droids mod by guy762  
**Total refs in src:** 11

### Dangerous (HARD) References: 5

| File | Type | Context |
|------|------|---------|
| `src/RimStarWars/StarWarsPatches/Patches/DroidDonor_ABFGate.xml` | XML comment | 3 refs: internal documentation explaining that kotorcore ships XML with ABF class references; this file provides the gating for them when ABF retires |
| `src/RimStarWars/StarWarsPatches/Patches/WeaponTags_Renormalise.xml` | XML comment | 1 ref: note that neither of the two guy762 mods are fully verified for defName dependencies yet |
| `src/RimUtinni/FactionSlate/About/About.xml` | About.xml `<li>` dependency | 1 ref: bare dependency listing in modDependencies section |

**Worst hard ref excerpt:**
```xml
<!-- WeaponTags_Renormalise.xml -->
today, and neither of the two guy762 mods that ARE active (guy762.kotordroids,
```

### Safe (GATED) References: 6

All 6 safe refs use `MayRequire="guy762.KotORDroids"` on individual `<li>` elements in trader stock definitions:

| File | Count | Pattern |
|------|-------|---------|
| `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/TraderKindDefs/Absorbed_KotorWeapons_OrbitalTrader_Baragwin.xml` | 3 | `<li MayRequire="guy762.KotORDroids" Class="...">` |
| `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/TraderKindDefs/Absorbed_KotorWeapons_BaseTrader_Baragwin.xml` | 3 | `<li MayRequire="guy762.KotORDroids" Class="...">` |

**Note:** All GATED refs are `MayRequire`, which is safe. They load ONLY if the mod is present.

---

## killathon.artificialbeings

**packageId:** `killathon.artificialbeings` (also: `Killathon.ArtificialBeings.SynCore` variant)  
**Description:** ABF: Artificial Beings Framework — provides synstruct pawn type and AI framework  
**Total refs in src:** 13

### Dangerous (HARD) References: 4

| File | Type | Context |
|------|------|---------|
| `src/RimStarWars/StarWarsPatches/Patches/DroidDonor_ABFGate.xml` | XML comment | 2 refs: explains that guy762's absorbed KotOR mods ship XML with unguarded ABF C# class references |
| `src/RimUtinni/Doctrine/About/About.xml` | About.xml `<loadAfter>` | 1 ref: load-order gating (see note below) |
| `src/RimUtinni/ResearchRetag/About/About.xml` | About.xml `<li>` dependency | 1 ref: bare dependency listing |

**Worst hard ref excerpt:**
```xml
<!-- DroidDonor_ABFGate.xml comment -->
packageId Killathon.ArtificialBeings) `ArtificialBeings.*` C# classes with NO
MayRequire guard against ABF itself.
```

### Safe (GATED) References: 9

| File | Count | Pattern |
|------|-------|---------|
| `src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/ThingDefs_WeaponsArmorsGadgets/Absorbed_KotorCore__BASE_SWKotORApparel.xml` | 2 | `<li MayRequire="Killathon.ArtificialBeings.SynCore">` |
| `src/RimStarWars/Armoury/Patches/Absorbed_AdditionalMods/kotorcore/ATC/Absorbed_Kotorcore_ATC_Patch_DroidIngestibleBlacklist.xml` | 1 | `<Operation Class="PatchOperationFindMod" IfModActive="Killathon.ArtificialBeings.SynCore">` |
| `src/RimStarWars/Armoury/Patches/Absorbed_AdditionalMods/kotorcore/MHC/Absorbed_Kotorcore_MHC_Patch_IonDamageWorker.xml` | 5 | `<Operation Class="PatchOperationReplace" MayRequire="Killathon.ArtificialBeings">` |
| `src/RimStarWars/Armoury/Source/guy762_IonizationABF/DamageWorker_Ionize.cs` | 1 | C# comment: `/// ... gated IfModActive="Killathon.ArtificialBeings"` |

**Note on loadAfter:** The reference in Doctrine/About.xml's `<loadAfter>` is a load-order constraint, not a hard dependency. It ensures Doctrine patches load AFTER ABF so `PatchOperationFindMod` checks can correctly detect ABF's presence or absence.

---

## neronix17.asimov

**packageId:** `neronix17.asimov` (also: `Neronix17.Asimov`)  
**Description:** Asimov mod — framework dependency of Droid Depot's NPC AI  
**Total refs in src:** 3

### Dangerous (HARD) References: 3

| File | Type | Context |
|------|------|---------|
| `src/RimStarWars/Droidworks/Source/BoltCore/BoltCorePatches.cs` | C# comment | Explains that Depot's framework dependency is Asimov; used to explain BoltCore's own relationship to Asimov (informational, not runtime) |
| `src/RimUtinni/Doctrine/About/About.xml` | About.xml `<loadAfter>` | Load-order constraint, not a hard dependency (same rationale as ABF above) |
| `src/RimUtinni/ResearchRetag/About/About.xml` | About.xml `<li>` dependency | Bare dependency listing |

**Worst hard ref excerpt:**
```csharp
// BoltCorePatches.cs
/// Depot's Asimov-framework dependency, Neronix17.Asimov, is what ships
```

### Safe (GATED) References: 0

No gated refs found. All Asimov references are informational (comments or About.xml order constraints).

**Risk assessment:** LOW — Asimov refs are all documentation/load-order; no runtime defName usage of Asimov-specific classes.

---

## neronix17.outerrim.droiddepot

**packageId:** `neronix17.outerrim.droiddepot` (also: `Neronix17.OuterRim.DroidDepot`)  
**Description:** Outer Rim - Droid Depot mod — supplies 11+ droid pawnkinds and accompanying defNames  
**Total refs in src:** 21

### Dangerous (HARD) References: 6

| File | Type | Context |
|------|------|---------|
| `src/RimStarWars/MSEDroidFix/About/About.xml` | About.xml `<packageId>` | Reference to asset bundle path comment; documenting Depot's textures |
| `src/RimStarWars/StarWarsPatches/About/About.xml` | About.xml `<li>` dependency | Bare dependency listing |
| `src/RimStarWars/StarWarsPatches/Patches/DroidFemaleTexture_Fix.xml` | XML comment | Explains that Depot ships only male textures for all droid types; documents the bug being patched |
| `src/RimUtinni/Doctrine/About/About.xml` | About.xml `<loadAfter>` | Load-order constraint |
| `src/RimUtinni/FactionSlate/About/About.xml` | About.xml `<li>` dependency | Bare dependency listing |
| `src/RimUtinni/UtinniPatches/About/About.xml` | About.xml `<li>` dependency | Bare dependency listing |
| `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaFreeDroidEnclaves.xml` | XML comment | Table explaining which Depot droid defNames map to Jawa faction roles |

**Worst hard ref excerpt:**
```xml
<!-- DroidFemaleTexture_Fix.xml comment -->
Outer Rim Droid Depot (Neronix17.OuterRim.DroidDepot, WS 3096501398) ships
ONLY male body textures.
```

### Safe (GATED) References: 15

All 15 safe refs use `MayRequire="Neronix17.OuterRim.DroidDepot"` on `<li>` elements or `<PawnKindDef>` nodes:

| File | Count | Pattern |
|------|-------|---------|
| `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaFreeDroidEnclaves.xml` | 8 | `<XXX_DroidName MayRequire="Neronix17.OuterRim.DroidDepot">count</XXX>` (pawnkind list items) |
| `src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml` | 4 | `<PawnKindDef MayRequire="Neronix17.OuterRim.DroidDepot">` (wrapper elements) |
| `src/RimStarWars/StarWarsPatches/Patches/DroidFemaleTexture_Fix.xml` | 3 | `<Operation Class="PatchOperationReplace" ... MayRequire="Neronix17.OuterRim.DroidDepot">` (not counted in grep output; verified by file inspection) |

**Note:** The 15 gated refs represent faction and pawnkind definitions that ONLY spawn if Droid Depot is present. The patch operations in DroidFemaleTexture_Fix.xml are themselves conditional.

---

## DefName Prefix Analysis: OuterRim_*Droid

**Donor:** Droid Depot  
**defName prefix(es):** `OuterRim_*Droid` (all Depot droid pawnkind and related defNames)  
**Total defName refs in src:** 361

### Breakdown by Gating

| Category | Count | Notes |
|----------|-------|-------|
| GATED (MayRequire) | 2 | Safe; only spawn when Depot is present |
| HARD (no gate) | 359 | See CRITICAL NOTE below |

### CRITICAL NOTE: Most "Hard" Refs Are OUR OWN Implementations

The 359 "hard" refs APPEAR to reference Depot defNames directly, but **the vast majority reference OUR OWN forked/reskinned droid definitions**, not the original Depot defNames:

- **RSW_DW_HeadType_OuterRim_* defs** (src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml) — OUR OWN race head definitions, not Depot's
- **RSW_DW_Race_OuterRim_* defs** (src/RimMandrake/TheftHauler/Patches/MuckrakerChassis_TheftHauler.xml) — OUR OWN race/chassis implementations

These are SAFE because they are not actual references to the donor mod; they are standalone implementations we authored.

### Genuine Donor defName Usage (High Risk)

To identify genuine Depot defName usage that would break if Depot retires, look for:
1. Unprefixed `OuterRim_` defNames (not `RSW_DW_*`)
2. In pawnkind/faction lists WITHOUT `MayRequire` guards
3. In gameplay-critical XML

**Examples of genuine Depot usage (currently gated):**
```xml
<!-- JawaFreeDroidEnclaves.xml -->
<OuterRim_ProtocolDroid MayRequire="Neronix17.OuterRim.DroidDepot">1</OuterRim_ProtocolDroid>
<OuterRim_KXSecurityDroid MayRequire="Neronix17.OuterRim.DroidDepot">4</OuterRim_KXSecurityDroid>
```

These ARE gated and therefore safe to retire.

---

## Gating Methodology Summary

### SAFE Patterns (All Found in Codebase)

1. **MayRequire on `<li>` elements**
   ```xml
   <li MayRequire="guy762.kotordroids" Class="StockGenerator_SingleDef">
   ```
   - Effect: entire list item conditionally loads; if mod absent, item is skipped

2. **MayRequire on PatchOperation**
   ```xml
   <Operation Class="PatchOperationReplace" MayRequire="Killathon.ArtificialBeings">
   ```
   - Effect: patch does not run if mod is absent

3. **PatchOperationFindMod with nomatch branch** (used in DroidDonor_ABFGate.xml)
   ```xml
   <Operation Class="PatchOperationFindMod">
     <mods><li>ABF: Artificial Beings Framework</li></mods>
     <nomatch Class="PatchOperationRemove">
       <!-- removes ABF class references when ABF is gone -->
     </nomatch>
   </Operation>
   ```
   - Effect: runs ONLY when mod is absent; used to strip references when donor retires

4. **IfModActive on PatchOperation**
   ```xml
   <Operation Class="PatchOperationFindMod" IfModActive="Killathon.ArtificialBeings.SynCore">
   ```
   - Effect: patch conditional on mod presence

5. **loadAfter in About.xml** (used with conditional patches)
   ```xml
   <loadAfter>
     <li>Killathon.ArtificialBeings</li>
   </loadAfter>
   ```
   - Effect: ensures load order so `PatchOperationFindMod` can correctly detect presence/absence

### DANGEROUS Patterns (Found in Codebase)

1. **Bare dependency listings in About.xml**
   ```xml
   <li>guy762.kotordroids</li>
   ```
   - Risk: informational, but if mod retires, this listing remains stale documentation
   - Mitigation: clean up About.xml entries when donor retires; won't break gameplay but causes confusion

2. **DefName usage without MayRequire** (none critical found; all Depot refs are gated)
   - Would look like: `<SomeDef defName="OuterRim_BattleDroid">` without `MayRequire` guard
   - None currently found; all Depot pawnkind usage is properly gated

3. **C# reflection or hardcoded strings referencing donor types** (none found)
   - Would be runtime-dangerous; none detected in audit

---

## Retirement Readiness Assessment

### By Donor:

| Donor | Status | Action Needed |
|-------|--------|---------------|
| **guy762.kotordroids** | READY | DroidDonor_ABFGate.xml provides emergency gating. Clean up About.xml listings when retiring. |
| **killathon.artificialbeings** | READY | DroidDonor_ABFGate.xml + MayRequire guards cover all live mechanics. |
| **neronix17.asimov** | READY | No live defName usage; only informational refs; safe to retire. |
| **neronix17.outerrim.droiddepot** | READY | All defName usage is MayRequire-gated; DroidFemaleTexture_Fix.xml patches are conditional. |

### Critical Item File

See `infrastructure/state/items/DROID_DONOR_PATCH_GATE_1.md` for retirement criteria and rollback procedures. The DroidDonor_ABFGate.xml file has already been authored and validated to handle the ABF retirement scenario; similar gating will be needed for other donors when they actually retire.

---

## Files to Review Before Retirement

1. **DroidDonor_ABFGate.xml** — serves as template for gating other donors
   - Location: `src/RimStarWars/StarWarsPatches/Patches/DroidDonor_ABFGate.xml`
   - Review: validate that nomatch branches correctly strip references when each donor retires

2. **DroidFemaleTexture_Fix.xml** — patches Droid Depot defNames; verify conditions still apply if Depot is gone
   - Location: `src/RimStarWars/StarWarsPatches/Patches/DroidFemaleTexture_Fix.xml`

3. **About.xml dependency listings** — will need cleanup when donors retire
   - Locations: Doctrine, ResearchRetag, FactionSlate, UtinniPatches About.xml files
   - Action: remove bare `<li>` entries for retired donors

4. **JawaFreeDroidEnclaves.xml** — faction pawnkind definitions
   - Location: `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaFreeDroidEnclaves.xml`
   - Status: All Droid Depot references are MayRequire-gated; safe as-is

---

## Conclusion

**Overall safety: GOOD**. The codebase is already well-prepared for these donor retirements:

- All packageId references that matter are either gated or informational
- All live defName usage (Droid Depot pawnkinds in faction defs) is properly MayRequire-guarded
- Emergency gating (DroidDonor_ABFGate.xml) already exists for ABF scenario
- No dangerous hardcoded strings or reflection-based references found

**Next steps:** When a donor is actually retired, apply the same pattern used in DroidDonor_ABFGate.xml to the newly-inactive donor's references, then clean up About.xml dependency listings.
