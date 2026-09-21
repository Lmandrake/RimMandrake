# VENOMVINE_CONTACT_VENOM_BUILD_1 — build the venomvine and its contact-venom comp

## what is wrong

The desert's "strange vines and thorny venom" (desert.md §4b, FROZEN) and the
arid shrubland's venomvine ("Desert lineage", arid_shrubland.md §Venomvine,
FROZEN) are one plant with no def and no mechanism. `DESERT_SHADE_PLANTS_DESIGN_1`
decided the mechanism; this item builds it. **Read the design first — it is the
authority and it names every number:**
`design/Jawa/worldbuilding/desert_shade_plants_design.md` §1, §3, §5.

## why it matters

Without it every shaded patch in the desert is free real estate, contradicting
§4b ("a patch that looks like the best shelter for a kilometre may be
somebody's"). The shrubland's fortress flora reuses the same comp later.

## the work — all in `src/RimMandrake/EnvironmentalHazards` (`mandrake.rm.environmentalhazards`)

C# (namespace `RimMandrake.EnvironmentalHazards`, the kit's existing assembly):

- `CompProperties_ContactVenom` / `CompContactVenom` — fields `damageDef`,
  `damageAmount` (3), `armorPenetration` (0.05), `contactIntervalTicks` (2500),
  `bodyHeight` (Bottom). On `PostSpawnSetup`/`PostDeSpawn` it registers and
  unregisters the parent's cell with the MapComponent. It does nothing on tick
  (plants tick Long; this comp must not depend on ticking).
- `MapComponent_ContactVenom` — `HashSet<IntVec3>` of registered cells; every 15
  ticks, for each `map.mapPawns.AllPawnsSpawned` whose `Position` is registered
  and who is not `Flying` and whose race def carries no `ContactVenomImmunity`:
  first contact → scratch now; otherwise scratch when the per-pawn next-scratch
  tick passes. Per-pawn state (last contact, next scratch) in a dictionary,
  `ExposeData`'d, pruned when a pawn has been out of contact longer than the
  interval. Moving between two registered cells is lingering, not re-entry.
  `DamageInfo`: the comp's damageDef, amount, AP, `Instigator` = the vine Thing
  at that cell, `SetBodyRegion(Bottom, Outside)`; no instigator pawn ever.
- `ContactVenomImmunity : DefModExtension` — empty marker on a race ThingDef.
- Settings in `RM_EnvironmentalHazardsSettings` (the kit's existing screen):
  contact venom on/off (default on), scratch damage multiplier, venom lethal
  on/off (default on). All-off must degrade gracefully (the plant stays, inert).

XML:

- `DamageDef RM_VenomvineScratch` — `ParentName="Scratch"`, `additionalHediffs`
  → `RM_VenomvineVenom`, `severityPerDamageDealt 0.04`,
  `victimSeverityScalingByInvBodySize true`, no `victimSeverityScaling` stat.
  Copy Core's `ScratchToxic` block in `Damages_MeleeWeapon.xml` and change the
  hediff.
- `HediffDef RM_VenomvineVenom` — `severityPerDay -0.5`, stages 0.05 / 0.30 /
  0.60 as the design lists them, `lethalSeverity 1.0` (gated by the setting).
- `ThingDef RM_Venomvine` — the design's §1d block verbatim (`pathCost 60`,
  `MaxHitPoints 300`, `harvestWork 900`, `Flammability 0.1`, `fertilityMin 0.5`,
  `lifespanDaysPerGrowDays 0`, `allowAutoCut false`, clusters 4/6, no harvest,
  rust-umber colour, no green) with the comp attached.
- `RUT_Desert.xml` `wildPlants`: `RM_Venomvine` at 0.25,
  `MayRequire="mandrake.rm.environmentalhazards"`, same pattern as the SWBestiary
  entries in that list.
- Art: search `infrastructure/artpipe/{done,_artsrc,registry.jsonl,art_status.json}`
  for vine/thorn/venom AGAIN before filing (2026-09-20: none of ours exists;
  `ripthorn_v1`/`tropicalchokevine_v1` are other rosters' donors). Then one
  `fill_queue.py` job; texPath pending is expected until it lands.

## Watch out

- Cutting stands adjacent (`JobDriver_PlantWork`, `PathEndMode.Touch`), so a
  cutter is only scratched if it must stand in another vine — that is intended;
  do not "fix" it.
- Do NOT build the shrubland thicket's body-size passability here — separate owed
  slug (`venomvine-fortress-flora-passability-by-body-size`,
  `COMMISSION_LEDGER_CLEANUP_1`). Just don't preclude it.
- `PLANT_GROWTH_SPEC.md`'s ×4 growth postfix applies to this plant too; 8 growDays
  is authored against that.
- The C# rides a game load alone (tier c): compile with the user-local .NET SDK,
  deploy the DLL only while the game is down.

## verify

The design's §5 list, steps 1–6 and 8, on a quicktest map with all five DLC:
one leg scratch per crossing, one per hour lingering, serious stage at ~3 h,
lethal at ~9 h only with lethality on, adjacent cutting safe, flyers and
immune races untouched, Sharp armour reduces and can zero the venom, per-pawn
clock survives save/load.

## criteria

`RM_Venomvine` grows wild in `RUT_Desert`, scratches and envenoms exactly as the
design specifies, behind a working settings toggle, with the comp reusable by
any other plant via XML alone.

## built — 2026-09-20, `10033074a`

Everything the item asked for, at the names it asked for, all in
`mandrake.rm.environmentalhazards`:

| | |
|---|---|
| `Source/CompContactVenom.cs` | `CompProperties_ContactVenom` + `CompContactVenom` — all five fields at the item's defaults. Registers and deregisters its cell only; no tick. |
| `Source/MapComponent_ContactVenom.cs` | the 15-tick sweep, the per-pawn contact clock, `ExposeData`, pruning, the lethality gate. |
| `Source/ContactVenomImmunity.cs` | the empty race-level marker. |
| `Defs/DamageDefs/RM_Damages_ContactVenom.xml` | `RM_VenomvineScratch`. |
| `Defs/HediffDefs/RM_Hediffs_ContactVenom.xml` | `RM_VenomvineVenom`. |
| `Defs/ThingDefs_Plants/RM_Venomvine.xml` | the plant, §1d verbatim. |
| `RM_EnvironmentalHazardsMod.cs` | settings 37/38/39 — `contactVenomEnabled`, `contactVenomScratchMultiplier`, `contactVenomLethal`. |
| `RUT_Desert.xml` | `RM_Venomvine` at 0.25, `MayRequire="mandrake.rm.environmentalhazards"`. |
| `infrastructure/artpipe/pending/rmvenomvine_v1.json` | the art job. |

MEASURED offline: assembly builds clean (0 warnings, 0 errors, user-local .NET
SDK); all four XML files `ET.parse` and `validate_patch.py` clean against the
full 618-mod load set (the only warning is `RM_Venomvine`'s pending texPath,
expected until the art job lands); `run_selftests.py` 67/67.

Art search re-run this pass, as the item required:
`infrastructure/artpipe/{done,_artsrc,registry.jsonl,art_status.json}` for
vine/thorn/venom/bramble/briar. Every hit is a donor plant regenerated for
another roster under `ART_REGEN_FLORA_WAVE1_QUEUE_1` — `ripthorn_v1`,
`tropicalchokevine_v1`, `firevine*`, `brambles_v1`, `twistingthorn*`,
`crystaltipbrambles_*`. None is ours. One job filed, `rmvenomvine_v1`.

### three decisions where the item was silent

1. **`PawnKindDef.immuneToTraps` is honoured** alongside the
   `ContactVenomImmunity` extension. The item named only the extension.
   `immuneToTraps` is vanilla's exact flag for "a hazard sitting on the ground
   does not catch this kind" (`Building_Trap.SpringChance` reads it), and this
   is that class of hazard — without it a scripted or quest-critical kind
   vanilla is careful never to trap could be killed by a plant.
2. **Lethality is gated by clamping severity to `lethalSeverity × 0.99` right
   after each scratch**, not by editing the def. `lethalSeverity` is a
   `HediffDef` field the engine reads directly, and severity on this hediff
   only ever RISES from a scratch (`severityPerDay` is negative), so the
   clamp covers the only path to the threshold. Turning the option off never
   heals a carrier already past it.
3. **`contactVenomScratchMultiplier` multiplies with the kit-global
   `hazardDamageMultiplier`** rather than replacing it, so the kit's own law
   ("one dial scales every damage number the kit deals") still holds while
   this hazard can be softened alone.

### what is NOT done

The `## verify` list above is live-only and was not run — this pass had no
game. Filed as `VENOMVINE_LIVE_VERIFY_1`, which carries the design's §5 steps
and names the one never-observed mechanism ("a MapComponent damages a pawn for
standing on a registered cell"). The DLL also still needs deploying, and a
companion DLL deploys only while the game is down.
