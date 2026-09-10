# DROID_RETIRE_KOTORDROIDS_1

## Spec (written by FOUNDRY, thin item — no spec/verify existed)
Retire `guy762.kotordroids` (wave R1, `DROID_UNIFIED_FRAMEWORK_DESIGN.md` §2/§5
row D2) after its listed prerequisites (B2 B3 C1 C2 C7 D1 A3) close — confirmed
all closed before starting. "Retire" = stop loading the donor mod
(`ModsConfig.xml`) + clean up references to it that would otherwise break; NOT
deleting our own absorbed content and NOT touching kotordroids' own mod files.
Verify = a full-list cold load with zero NEW `Config error in` /
`Could not resolve cross-reference` lines against
`infrastructure/state/facts/config_error_baseline_2026-09-06.json`.

## Pre-flight grep (own fresh check, not trusting the 2-day-old D1 census)
Re-grepped `src/` for `guy762.kotordroids`/`KotORDroid`/
`guy762_KotORFaction_RogueDroids` myself. Confirmed D1's finding: the only
non-comment, non-`RSW_DW_`-absorbed live reference was `FactionSlate/About.xml`'s
`modDependency` — except FactionSlate no longer exists as its own mod (folded
into `mandrake.rut.patches` this sprint); the equivalent line is
`src/RimUtinni/UtinniPatches/About/About.xml:46`, and on direct read it is
`<forceLoadAfter><li>guy762.kotordroids</li>...`, not `<modDependencies>` — a
load-order hint, not a hard dependency (harmless if the mod is absent, but kept
correct anyway since `OnlyOurFactions.xml` still needs to reach
`guy762_KotORFaction_RogueDroids` while kotordroids IS active).
`OnlyOurFactions.xml`'s own reference to that FactionDef is properly
`PatchOperationConditional`-wrapped (silent no-op once the def is gone) — no
action needed there. All other `KotORDroid`-substring hits in `src/` are our own
`RSW_DW_KotORDroidColonist_*`/`RSW_DW_KotORDroidGood_*`/`RSW_DW_KotORDroidBad_*`
absorbed content (Droidworks, MayRequire-gated on `mandrake.rsw.droidworks`,
not on kotordroids) or Python/comment provenance text. **This part of the D1
census held up.**

## What the cold load found — BLOCKED, not closed
Backed up the live full list to
`infrastructure/state/modlists/ModsConfig.PRESWAP.20260908_before_D2_kotordroids_retire.xml`
(also byte-identical to the repo's own
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` before this attempt),
removed `guy762.kotordroids` from both the live `ModsConfig.xml` and the repo
snapshot, fixed the `About.xml` forceLoadAfter line, deployed, and cold-loaded
the full (599-mod) list via Steam. Bridge came up clean
(`Bridge token: b80d3f83edfd44b4b881524a1d83510d`).

`check_config_errors.py` against the 2026-09-06 baseline: **NOT CLEAN** — 4
distinct NEW cross-reference errors, all naming donor droid weapon ammo
ThingDefs:

```
Could not resolve cross-reference: No Verse.ThingDef named guy762_DroidWeapon_microrocket
  found to give to ModularWeapons2.MWAbilityProperties
Could not resolve cross-reference: No Verse.ThingDef named guy762_DroidWeapon_railgun
  found to give to Verse.ThingDefCountClass (1x null)
Could not resolve cross-reference: No Verse.ThingDef named guy762_DroidWeapon_seekerrocket
  found to give to ModularWeapons2.MWAbilityProperties
Could not resolve cross-reference: No Verse.ThingDef named guy762_DroidWeapon_trishot
  found to give to Verse.ThingDefCountClass (1x null)
```

**Root cause traced** (not guessed): these 4 `guy762_DroidWeapon_*` ThingDefs are
NOT defined by `guy762.kotordroids` itself, and NOT defined by
`guy762.KotORWeapons` (which is not even in the active mod list — already
retired in an earlier wave). They are defined by `guy762.mm.kotorcore`
(workshop `3254370945`)'s own `_DroidsBase` AdditionalMods folder
(`Defs/ThingDefs_DroidEquipment/Apparel_KotORDroidWeapons.xml`), whose
`LoadFolders.xml` gates that whole folder on
`<li IfModActive="guy762.KotORDroids">1.6/AdditionalMods/_DroidsBase</li>`.
Disabling kotordroids silently stops that folder from loading too (a second
gate, on a THIRD mod, that nothing in the D1 census or the design doc's own
risk column named) — and two of our OWN files consume those ammoDefs
ungated: `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ModularPartDefs/
Absorbed_KotorWeapons_ModularPartDefs_HelmetArmorTech.xml` and
`..._Wristgun.xml` (`<ammoDef>guy762_DroidWeapon_{microrocket,railgun,
seekerrocket,trishot}</ammoDef>`, no `MayRequire`/`PatchOperationConditional`).

These 4 defs sit outside B2's own absorption scope (B2 absorbed the KotOR
*droid module* apparel set — `Absorbed_KotorDroidModules/` — not the droid
*weapon/ammo* set consumed by Armoury's separate KotorWeapons absorption).
`retirement_order.py`'s documented `_DroidsBase` constraint
(`DROID_RETIREMENT_ORDER_ASSERT_1`) is about a DIFFERENT failure mode (ABF/
SynCore retiring before kotordroids silently discarding 12 downstream defs via
a `ParentName` break) and does not cover this one — this is a same-shape but
distinct gap: an indirect two-hop chain (kotordroids → kotorcore's
`_DroidsBase` → our own Armoury absorption) that neither B2's manifest nor D1's
per-donor grep walked.

**Reverted per the block-not-guess rule**: live `ModsConfig.xml` restored from
the backup above (kotordroids back in, verified `count 600, has kotordroids:
True`); repo's `ModsConfig.FULL.LATEST.xml` and `About.xml` reverted with `git
checkout`; `UtinniPatches` redeployed to resync the game Mods folder with the
reverted repo state (33 files — picked up other already-committed, previously
undeployed drift from earlier-closed items in the same pass, unrelated to this
revert); RimWorld closed (game left DOWN, as found). Bridge released.

## What actually needs to happen before D2 can close
A real fix, not a live guess — either:
1. Absorb the 4 `guy762_DroidWeapon_{microrocket,railgun,seekerrocket,trishot}`
   ammo ThingDefs into our own namespace (Armoury or Droidworks,
   `RSW_*`-prefixed, same pattern as B2) and repoint the two Armoury
   `ModularPartDefs` consumers onto the absorbed names; or
2. Gate the two consumer `<ammoDef>` fields (and their sibling
   `Absorbed_KotorWeapons_ModularPartDefs_HelmetArmorTech.xml`/`_Wristgun.xml`
   content generally) behind `MayRequire="guy762.KotORDroids"` or
   `PatchOperationConditional`, accepting that this specific ability loses its
   ammo requirement (or the whole ability) once kotordroids retires.
Whoever picks this up: check `gen_kotorcore_absorption.py` (the tool that
generated the Absorbed_KotorWeapons content) for whether it already has a
mechanism for tagging donor-folder-conditional defs — it clearly missed these
4 the first time.

## Verify
```
PROVE   the 4 cross-reference lines above, reproducible on any full-list cold
        load with guy762.kotordroids removed and guy762.mm.kotorcore active
EXPECT  once fixed (absorption or gating), a repeat of this exact retirement
        attempt (remove kotordroids from ModsConfig.xml, cold load) produces
        check_config_errors.py CLEAN with zero new lines
LIES    trusting the D1 census's per-donor "every reference in src/ and every
        active mod's XML" framing as complete — it did not walk a reference
        that crosses THROUGH a third mod's own conditional LoadFolders gate
```

## 2026-09-09 — Option 2 (gating) applied, offline only
Picked up the "check both, gate, don't guess" fix left above. Read both
consumer files in full first.

**Shapes found** (both already visible in the item's own error text, now
confirmed by direct read): `<ammoDef>` is a scalar field on the `<ability>`
block, `ModularWeapons2.MWAbilityProperties` (microrocket x2, seekerrocket
x1); the `guy762_DroidWeapon_railgun`/`_trishot` references are
`<costList>` entries, `Verse.ThingDefCountClass` shorthand (railgun x2 --
also consumed by `guy762_KotORpartWristgun_flamethrower`'s costList, a
donor-original reuse of the same item as flamethrower fuel, not something
this pass introduced; trishot x1). Total 6 usages across 2 defs needing
ammo (`..._kneerocket`, `..._wristgun_microrocket`) + 4 defs needing
costList (`..._wristgun_trishot`, `_seeker`, `_railgun`, `_flamethrower`) --
12 top-level defs once each paired `AbilityDef` is counted.

Neither shape can be conditionally patched in place (both are scalar/
inline values inside a GENERATED, defName-preserving `<Defs>` file, not a
`<Patch>` file with xpaths to guard). Checked precedent in these exact
sibling files first, per the item's steer: both files already carry
donor-authored `MayRequire="kentington.saveourship2"` (EVA armor tech) and
`MayRequire="Ludeon.RimWorld.Biotech"` (toxdart part + its AbilityDef) on
whole `ModularPartsDef`/`AbilityDef` elements -- the exact same "def
references content requiring another mod's presence" shape as here.
Applied the same mechanism: `MayRequire="guy762.KotORDroids"` (casing
matches this pack's own already-shipped
`Absorbed_KotorWeapons_{Base,Orbital}Trader_Baragwin.xml`, not the
lowercase `guy762.kotordroids` ModsConfig packageId string -- RimWorld's
own MayRequire match is case-insensitive and this is the value already
proven live) on all 6 `ModularPartsDef` consumers and their 6 paired
`AbilityDef`s. Accepts the item's stated cost: each ability (not just its
ammo requirement) disappears entirely once kotordroids retires -- judged
acceptable since these are donor flavor abilities, not load-bearing to any
Jawa/Armoury system.

**Generator checked, and fixed, not just hand-patched.**
`gen_kotorweapons_absorption.py` had no mechanism at all for this --
its only per-element filter is the unrelated rule-6 "blocked namespace"
list (Class=/compClass= tied to a DLL that retires with kotorcore).
`gen_kotorcore_absorption.py`'s docstring confirms the droid-ammo folder
was OUT OF SCOPE for that generator on purpose (never walks
`_DroidsBase`), so no generator anywhere already absorbs or gates these
4 ammoDefs. `absorption_content_fixes.py`, though, already exists as
exactly this injection point -- "known content issue, corrected at
generation time so the fix survives every regen instead of being hand-
edited into a file whose header says GENERATED" -- so extended it rather
than leaving the gate as a hand-edit a future regen would silently drop:
added `MAYREQUIRE_FIXES` (defName -> required packageId) alongside the
existing text-fix `FIXES` table, and had `apply_content_fixes()` set the
`MayRequire` attribute on the top-level element (no-op if already
correctly set; warns and skips rather than overwriting if some future
donor update sets a different one). Verified programmatically that
running `apply_content_fixes()` against each of the 12 defNames now
produces `MayRequire="guy762.KotORDroids"` -- matches the hand-patch
applied to the two already-committed generated files below (did NOT
rerun the full generator, to avoid the unrelated-churn risk of a whole-
file regen; the two files were edited by hand to the exact state a
regen with this fix would produce).

**Files changed:**
- `src/RimStarWars/Armoury/Source/absorption_content_fixes.py` (new
  `MAYREQUIRE_FIXES` table + `apply_content_fixes()` extended to apply it)
- `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ModularPartDefs/Absorbed_KotorWeapons_ModularPartDefs_HelmetArmorTech.xml`
  (2 defs gated: `guy762_KotORpartArmorTech_kneerocket` +
  `guy762_MW2WeaponVerbAbility_kneerocket`)
- `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ModularPartDefs/Absorbed_KotorWeapons_ModularPartDefs_Wristgun.xml`
  (10 defs gated: `guy762_KotORpartWristgun_{trishot,microrocket,seeker,
  railgun,flamethrower}` + their 5 paired `AbilityDef`s)

**Validation:** `validate_patch.py` against both edited files with all
three live `--defs` roots (Data/Mods/workshop, 581 active mods per the
live `ModsConfig.xml` at time of this pass) -- `OK, 0 errors, 0 warnings`
on both files.

**Not done in this pass, on purpose:** no live game touched, no
`ModsConfig.xml` edit, no cold load. This was offline-only per the
instruction handing this off; the actual repeat-the-retirement-attempt
verify (remove kotordroids, cold load, expect `check_config_errors.py`
CLEAN) is still owed and left to whoever resumes State/Verify below.

## State left behind
- `ModsConfig.xml` (live, game machine): restored to the pre-attempt 600-mod
  full list, kotordroids present — byte-identical to
  `infrastructure/state/modlists/ModsConfig.PRESWAP.20260908_before_D2_kotordroids_retire.xml`.
- `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`: unchanged (git
  checkout reverted the working-tree edit).
- `src/RimUtinni/UtinniPatches/About/About.xml`: unchanged (git checkout
  reverted the working-tree edit), redeployed to the game Mods folder along
  with other already-committed pending drift for `mandrake.rut.patches`.
- Game: closed/DOWN.
- Bridge: released, free.
- Item: left `doing`, now blocked with this file as the record — not closed.
