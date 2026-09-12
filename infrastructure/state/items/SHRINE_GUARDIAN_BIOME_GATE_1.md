## Spec
Piece 4/4 of `MECH_PRESENCE_ENFORCEMENT_1` (curate shrine contents where
ANCIENT-ALLOW/RARE meets AMBIENT-DENY) turned out to need C#, not XML, and
was spun off rather than built out-of-scope on that item.

Verified via `rimsage read_csharp_symbol` (not guessed):
`GenStep_ScatterShrines.ScatterAt` pushes a hardcoded symbol stack —
`BaseGen.symbolStack.Push("ancientTemple", resolveParams)` →
`SymbolResolver_AncientTemple` → `"interior_ancientTemple"` → SketchGen /
RulePackDef monument generation — gated only by the GLOBAL
`Storyteller.difficulty.peacefulTemples` toggle. No BiomeDef field, no
GenStepDef field, no per-biome or per-incident hook selects guardian type
or faction anywhere in that chain. There is no XML field to patch.

Doing this for real needs a Harmony postfix on
`SymbolResolver_AncientTemple.Resolve` (or the deeper monument/pawngen call
it makes) to pick guardian type/faction per-biome — outside XML-only scope.

Candidate biomes (ANCIENT ALLOW-or-RARE meeting AMBIENT DENY, per the
mechanoid/ancient-danger table): `AB_TarPits`, `ZBiome_DesertOasis`,
`ZBiome_Badlands`, `Desert`, `ExtremeDesert`, `BiomeGRimond`,
`PoisonForest`, `BiomeCypreJungle`.

## Verify
```
PROVE   a shrine generated on one DENY-side candidate biome (e.g. Desert)
        spawns AMBIENT-appropriate guardians/loot, not the stock
        ancientTemple monument content, via a quicktest map on that biome
EXPECT  Harmony postfix intercepts SymbolResolver_AncientTemple.Resolve (or
        its downstream call) and substitutes per-biome guardian/faction
        before the stock generation path fires
LIES    a clean 0W/0E build proves nothing about the postfix actually
        intercepting the resolver at runtime — only a live quicktest does
```

## Criteria
- [x] Gate mechanism reads the map's biome and substitutes guardian/loot
      content for the 8 candidate biomes above — built as
      `SymbolResolver_Interior_AncientTemple_AmbientDoctrine` (plain
      subclass, no Harmony; see below for why the spec's named target was
      wrong)
- [ ] Quicktest-proven on at least one candidate biome
- [ ] `design/Jawa/worldbuilding/mechanoid_biome_presence_draft.md`'s ANCIENT
      column and `MECH_PRESENCE_ENFORCEMENT_1`'s piece-4 note stay the
      record of what this replaces — no re-deriving the symbol-stack chain

## Status 2026-09-12 (FOUNDRY)
Built, not yet live-verified. Full mechanism analysis, biome list and every
judgment call are documented in the header of
`src/RimUtinni/UtinniPatches/Source/AmbientShrineGuardians.cs` — this note
only records what changed this pass and what remains.

**The item's own title named the wrong hook.** Read via
`mcp__rimsage__read_csharp_symbol` (RimWorld 1.6 decompiled source, spot-
checked again this pass — `SymbolResolver_AncientTemple.Resolve` and
`SymbolResolver_Interior_AncientTemple.Resolve` both match the .cs header's
claims line-for-line): `SymbolResolver_AncientTemple` only lays the shrine's
walls (SketchGen monument) and pushes `interior_ancientTemple`; guardian
type and loot are decided one symbol later, in
`SymbolResolver_Interior_AncientTemple.Resolve`. And no Harmony is needed at
all — `RuleDef.resolvers` is a plain `List<SymbolResolver>` loaded from
`<li Class="...">` with no custom XML loader, so
`Patches/AmbientShrineGuardians.xml` swaps the Class attribute on Core's
`Interior_AncientTemple` RuleDef li to point at the new subclass — same
shape as this mod's `GeothermalDensityField.cs`.

Done this pass:
- Built `RimMandrake.Utinni.UtinniPatches.dll` (`dotnet build -c Release`):
  0 Warnings, 0 Errors. Confirmed the new type's name is now actually
  present in the compiled DLL bytes (the prior BENCH note on 2026-09-11
  found it missing — stale build, not a mechanism defect).
- `validate_patch.py` against the full 592-mod live load set (`--defs` the
  RimWorld Data, Mods and workshop/294100 folders, `--mods-config` the live
  ModsConfig.xml): `AmbientShrineGuardians.xml`'s conditional and its
  attribute-set both hit exactly the one Core `Interior_AncientTemple`
  RuleDef `li`, 0 errors, 0 warnings.
- `deploy_custom_mods.py --apply` for `UtinniPatches`: **refused** —
  `RimWorldWin64` is running (BENCH's live `WORLDMAP_FINAL_REVIEW_1` session
  holds the bridge for Abandoned Mines / world reads), so the OS holds the
  DLL locked (`[Errno 22]`). Nothing else in the mod needed redeploying —
  the patch XML and settings toggle were already live from an earlier pass.
  Did not touch the game to force this: restarting would kill BENCH's live
  work, which the bridge file shows is not stale.

Still owed, in order:
1. **Deploy** the assembly on the next game-down window (FOUNDRY doctrine:
   assemblies deploy on DOWN). One file, already staged in the repo.
2. **Quicktest verify** on one candidate biome (Desert is cheapest) once the
   bridge is free: confirm a Desert ancient-temple shrine spawns the sealed
   `AncientCryptosleepCasket` watch and `MapGen_AncientComplexRoomLoot_Default`
   salvage pile, not the stock mechanoid/fleshbeast/hive guard — this is the
   one thing a clean build cannot prove (`RuleDef.resolvers` picks by
   `selectionWeight` among candidates that `CanResolve`, so a wrong xpath or
   a silently-uninherited `li` would still build clean and never fire).
   `rimflow verify` the run either way.
3. Only then may this item close — `needs=deploy` set below rather than
   `block`, since nothing here is wrong, it is gated on the same game-state
   sequencing every assembly change is.
