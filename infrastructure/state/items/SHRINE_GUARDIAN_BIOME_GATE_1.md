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
- [ ] Harmony postfix (or equivalent transpiler/prefix) on
      `SymbolResolver_AncientTemple.Resolve` reads the map's biome and
      substitutes guardian/loot content for the 8 candidate biomes above
- [ ] Quicktest-proven on at least one candidate biome
- [ ] `design/Jawa/worldbuilding/mechanoid_biome_presence_draft.md`'s ANCIENT
      column and `MECH_PRESENCE_ENFORCEMENT_1`'s piece-4 note stay the
      record of what this replaces — no re-deriving the symbol-stack chain
