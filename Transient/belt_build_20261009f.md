# BELT build 2026-10-09f (FOUNDRY offline builder)

## RECONCILE PIT_SUPERDEEP_COLLAPSE_1 — DONE
Verdict **partial** on 5d5e6cc12 (umbrella; 5d5e6cc12 promoted v2 pit/ladder/cover rows to state reads,
offline+mock green, never live). Open: EXCAVATION_WALL_ART_1 (proposed; RM_Ladder still on vanilla
TrapSpikeArmed texPath), PIT_TEMPERATURE_SOFTENING_1 (validated, awaiting acceptance), live v2 run, L0 lint/doctor.
Lease: the briefed token FOUNDRY.pid16925.bb13cbbc does NOT hold it — held by FOUNDRY.pid41324.6df99a6d
until 20:42Z (another helper). Not released by me (only holder may).

## DONOR_CODE_PLAIN_PORTS_1
Spec: Transient/donor_code_creatures_sheet_2026-10-09.html — "Port plain = copy the creature into our own
defs and drop or swap the donor class (no new C#)". Pattern: donor_retirement_plan Step C (close every
reference, re-point texPath, drop donor-assembly comps).

No C# in a plain port (sheet's own definition), so no csproj/winbuild change. Not new mods: Cauldron and
Miasma are composed members of mandrake.rm.biomes, whose Mod Settings already exist. First script:
`src/RimMandrake/Utils/donor_plain_ports_check.py` (one row per port, sanity probe; wired into Miasma's
validation.py static_checks). Offline only — nothing loaded.

### Radyak -> RM_Radyak "ossrith" (Cauldron) — built
- `src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_Radyak.xml`: ThingDef+PawnKindDef, owner-ruled ossrith
  label/description; dropped GraphicsRefresher + AA_Alternates + AnimalStatExtension; donor wildBiomes not ported.
- Crystal harvest kept (VEF AnimalProduct, MayRequire VEF) -> our RM_OssrithCrystal + RM_RefineOssrithCrystal
  (biofuel refinery -> 15 uranium). Crystal art = vanilla uranium tinted green (placeholder).
- ART OWED: our redraw is enact_f3decf4d_radyak_v1_* awaiting verdict; texPaths stay on the donor path
  (RSW_DesertPortMisc precedent) and the RM_Cauldron row stays guarded on sarg.alphaanimals until art lands.
- Description says "biofuel refinery" (vanilla's name for the building the recipe sits on) where the
  ruled text said "chemfuel refinery".
### Thermadon -> RM_Thermadon "duskfire" (Miasma) — built
- `src/RimMandrake/Miasma/Defs/ThingDefs_Races/RM_Thermadon.xml`: donor parent AA_AlphaBaseInsect inlined;
  fire spit kept as our RM_DuskfireSpit AbilityDef+projectile (vanilla icon/texture/sound) via VEF
  InitialAbility (guarded). Our art installed via `art.py install` at Things/Pawn/Animal/RM_Thermadon/.
- RM_Miasma roster row now `<RM_Thermadon>0.1` unguarded. Campaign twin RUT_Miasma + UtinniPatches untouched.
### Remaining 5 — not started (Agaripawn, Agaripod, DecayDrake, MycoidColossus, RipperHound)
