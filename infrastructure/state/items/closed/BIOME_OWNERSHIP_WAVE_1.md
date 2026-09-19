# BIOME_OWNERSHIP_WAVE_1 — own every planet biome we have not yet owned

Owner, 2026-09-09, verbatim on the filing: *"make our own versions of all the biomes on
the planet, one for each we have not yet owned. Not intending to retire Alpha biomes and
alpha animals, but you have argued we should simply own our own version for parameter and
assignment control."*

## Why (the argument the owner is ratifying)
A donor-owned def means our control lives in wholesale-replace patches: a donor update
can move underneath them, the label item (`BIOME_LABEL_CAMPAIGN_NAMES_1`) has to rename
26 defs from outside, the runtime padder (`WILD_ANIMALS_PADDED_LISTS_1`) fights the cast,
and every parameter (weather, temps, diseases, plantDensity, ambient) is a patch target
instead of a field we write. The five RUT_ liquid/nightside defs took their assignment
rosters natively in their own def files — that is the model. Donors stay installed as
content libraries (their plants/animals/terrains are referenced freely); nothing here
retires Alpha Biomes or Alpha Animals.

## Scope
One owned BiomeDef per painted def not yet ours. From `_def_bindings_2026-09-09.md`
(29 painted defs) minus the owned five (`RUT_NightsideIce`, `RUT_TwilightSea`,
`RUT_GreySea`, `RUT_TheScald`, `RUT_PropaneLake`) and the two already ticketed
switches (`BiomeGRimond`→`RUT_BlueDesert` = `BLUE_DESERT_WORLD_SWITCH_1`;
`ZBiome_Grasslands`→`RM_FE_Pyrelands` = `PYRELANDS_SELF_CONTAINED_BIOME_1`/
`PYRELANDS_WORLD_SWITCH_1` — both ride their own items, not this wave):

Desert · ExtremeDesert · AridShrubland · Wasteland · PoisonForest · AB_PropaneLakes ·
AB_MycoticJungle · AB_RockyCrags · ZBiome_Badlands · ZBiome_DesertOasis ·
AB_MechanoidIntrusion · BiomeCypreJungle · AB_OcularForest · AB_FeraliskInfestedJungle ·
AB_GelatinousSuperorganism · AB_MiasmicMangrove · Scarlands ·
COMIGO_GreaterSwamp_Tropical · AB_TarPits · AB_PyroclasticConflagration · LavaField ·
Volcano — **22 defs → ~20 owned successors** (the Forge trio may merge or stay three;
its sheet says "one sheet, one massif" — decide at authoring).

## The pattern (already proven)
Per biome: author the owned def (naming per `design/NAMING_SCHEME_PLAN.md` — `RUT_` for
campaign biomes, `RM_` where genuinely reusable, label = campaign name natively) → def
carries its sheet-derived parameters AND its roster from
`design/Jawa/worldbuilding/biomes/rosters/<sheet>.json` directly (no cast patch for owned
defs) → prove in a quicktest → world-switch the tiles (repaint per def, the
`PYRELANDS_WORLD_SWITCH_1` template: batches, getter read-back, CSV re-export + LOSS
diff per freeze R36) → re-freeze.

## Sequence
1. AFTER the assignment pass lands (`BIOME_FAUNA_ASSIGNMENT_SITTING_1`) — the rosters
   are def-keyed data; each ownership switch is a `defNames` rebind in the roster JSON
   plus a repaint, never a redesign.
2. Rides the owed world re-import window(s); coordinate with `WORLDMAP_FINAL_REVIEW_1`
   so the STARE happens on the final defs (or explicitly before, twice).
3. `CONTAGION_BIOME_PLACEMENT_1` (tile move) and `HORRORWASTES_BIOME_DISSOLVE_1` land
   first or fold in — do not repaint a biome twice.

## Constraints / traps
- **R22 stands**: ExtremeDesert's owned successor stays ONE def (dune sea + deep desert
  merged). Owning defs would make a split cheap; that is the OWNER's call to reopen, not
  this item's.
- `wildAnimals` uses the custom loader — the `<li>` trap discards the whole def
  silently; validate with the patch validator AND a load.
- The de-dup union (`biome_animal_conflicts.py`) and the animal-side `wildBiomes` strip
  must be regenerated against the NEW defNames when each switch lands.
- Worldmap decoration icons don't auto-update (`WORLDMAP_BIOME_ICONS_REGEN_1`).
- Absorbs `BIOME_LABEL_CAMPAIGN_NAMES_1` def-by-def: an owned def carries its campaign
  label natively; that item shrinks to whatever defs remain un-owned when it runs (write
  the shrink into that item as ownership lands).
- Savegame/shortHash: repainting biomes on the frozen world touches the save's biome
  grid — back up first, R36 bar applies to every switch.

## verify
- Every painted tile's biome def is `mandrake.*`-tier (MEASURED off a fresh tiles CSV
  export: zero defs from the donor list above remain painted).
- Each owned def's roster matches its `rosters/<sheet>.json` (generator check, not eye).
- Full-list load with zero new Config errors; one quicktest map per switched biome batch.
