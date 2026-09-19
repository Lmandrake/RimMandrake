# ISHKO_DARK_LANDMARKS_1

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-08-31.

## spec

`design/Jawa/worldbuilding/sacred_sites_pass_1.md` §1c/§3: Ishko is the
one god of the Nine with no curated LandmarkDef of his own (his read is
biome-class only — nightside HorrorWastes/AB_RockyCrags/Cavern-type
terrain). Flagged as "real work — build item," not a free
reinterpretation, with an explicit instruction not to guess a candidate
without verifying the live shortlist first.

## verify

Pulled the live def dump's full `LandmarkDef.json` (113 defs, matching
the structure_injection_roster.md's own earlier census) and checked
which cold/dark/cavern-themed ones (`Cavern`, `Hollow`, `Crevasse`,
`VEE_Sinkholes`, `FrozenRuins`, etc.) are already cited in
`design/Jawa/`. All of them are — but only as generic biome-class
reasoning (the same finding sacred_sites_pass_1.md §1c already made),
never as a curated, owned Ishko landmark with its own identity. No
existing legal LandmarkDef matches "lightless sink / shadowed overhang /
cold lava tube" specifically. Confirmed: new content, not
reinterpretation.

`validate_patch.py`: 0 errors, 0 warnings on both the About.xml and the
Defs file — texPath existence (the reused Ash'karr-styled icons) checked
clean.

## criteria

- 2-3 new LandmarkDefs, each anchored on a real legal TileMutatorDef (no
  new C#, no new TileMutatorDef). **Met**: `mandrake.rut.ishkolandmarks`,
  three defs (`RUT_LightlessSink` → `Hollow`, `RUT_ShadowedOverhang` →
  `Chasm`, `RUT_ColdLavaTube` → `Cavern`).
- Description text grounded in Ishko's established canon
  (`reconciled_lore/05_the_clan.md` line 75: "hiding, ambush, stillness;
  orange eyes in the dark... never punishes a skipped rite"), not
  invented lore.
- Icons don't ship broken or mismatched — reused the existing
  Ash'karr-styled repaints (`mandrake.rut.ashkarrlandmarkart`) of the
  closest vanilla silhouette; bespoke art flagged as a follow-up, not
  silently skipped.
- **Placement stays the owner's hand** (the item's own title) — these
  defs are NOT placed on any Ash'karr tile. That's a live world-tile
  edit on the frozen map, out of scope here, same boundary this session
  held for `SEAS_WATERLINE_PASS_1`'s fishing mutators and
  `TILE_STRUCTURE_DESIGNS_1`'s Moisture Farm.

## CLOSED 2026-08-31 (FOUNDRY)

Deployed, added to `ModsConfig.xml` right after
`mandrake.rut.ashkarrlandmarkart` (icon-source dependency). Not yet
observed loading live — same as this session's other new mods, owed to
the next restart, which is the owner's call.
