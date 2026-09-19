## 2026-09-12 (FOUNDRY, third pass) — LIVE-VERIFIED clean, CLOSING

`QUICKTEST_POSTSETUP_CRASH_1`'s fix (commit `fa95b3fdc`) made a fresh
`start_debug_game_ready` moot to chase further: instead of restarting into
a random-biome map, painted the ALREADY-LOADED disposable quicktest map's
own tile (51056, was `BiomeArcticOasis`) to `Desert` + `LargeHills` via
`jawa/world_tile_set` + `jawa/world_commit` (raw read-back confirmed the
write), then fired `Actions\Regenerate Current Map` via
`execute_debug_action`. Since the map's tile is unchanged, `Map.IsStartingMap`
(`Find.GameInfo.startingTile == Tile`) stayed true, which is what makes
`GenStep_ScatterShrines.ShouldSkipMap` NEVER skip (`RimWorld/GenStep_ScatterShrines.cs:26`)
— a more reliable route to a guaranteed shrine-generation attempt than hoping
`start_debug_game_ready` happens to land on a Desert tile, which it cannot be
steered to at all.

`jawa/map_info` confirmed `mapBiome: "Desert"` post-regen. `jawa/list_things`
on the regenerated map:
- `AncientCryptosleepCasket` — 19 present (the doctrine's own extra
  `PodContentsType.AncientHostile` watch caskets, plus the unchanged
  `ancientShrinesGroup` sleepers)
- `Mech_Centipede`/`Mech_Scyther`/`Mech_Lancer`/`Mech_Pikeman`/`MechCluster` — **0**
- `Fleshbeast` — **0**
- `Hive` — **0**
- `AncientBarrel`, `AncientHermeticCrate`, `MedicineIndustrial` — present
  (the swapped `MapGen_AncientComplexRoomLoot_Default` scavenged-loot table
  and its Ideology hermetic-crate wrap, per `PushScavengedLoot`)

This is exactly the substitution `AmbientShrineGuardians.cs` documents: the
mechanoid/fleshbeast/hive guardian branch never fires on a DENY-side biome,
replaced by the dead Rakatan watch + scavenged salvage, while the loot table
swaps off the elite `MapGen_AncientTempleContents`. `Player.log` tail after
the regen is clean of anything naming this patch, `Interior_AncientTemple`,
or `AmbientDoctrine` — the only NREs anywhere in the log are pre-existing,
unrelated third-party mod issues (RimFridge, GravTechBC, a Worldbuilder
Harmony postfix), confirmed by reading their stack traces, not just grepping
the string.

**Criteria met**: quicktest-proven on Desert (one of the 8 candidate biomes,
cheapest per the item's own spec). Closing.

## 2026-09-12 (FOUNDRY, later same night) — still blocked, but for a NEW reason: quicktest itself crashes

Deploy confirmed already done tonight (`deploy_custom_mods.py --mod
UtinniPatches` reports "in sync", carried over from earlier tonight's
restart). The remaining gap is purely the quicktest-proof on a Desert
biome — attempted, blocked on a DIFFERENT problem than last time.

This session spent considerable effort getting `start_debug_game_ready`
working at all on the full 592-mod list: found and fixed a load-blocking
`thingClass` NRE (`257bbbc7f`, see `BUILDING_THEFT_HAULER_1`) and a stale
`CreatureBehaviors.dll` missing an already-written crash fix
(`3e05542a6`). After both fixes, quicktest gets much further (full colony
scenario, auto-research completes) but then **reliably crashes the whole
RimWorldWin64 process** at the exact same point in the log, twice in a
row, with no managed exception logged (looks like a native crash — the
kind `Exception was thrown while trying to handle exception` doesn't even
catch). Filed as its own item: `QUICKTEST_POSTSETUP_CRASH_1`.

**Why this item stays blocked rather than substituting the loaded real
colony map** (as `BUILDING_THEFT_HAULER_1`/`NINEFOLD_FIRE_HOOK_RATELIMITED_1`
did tonight): this item's verify needs a **Desert-biome** map specifically
(to trigger `SymbolResolver_Interior_AncientTemple_AmbientDoctrine`'s
biome gate against a DENY-side biome), and the loaded canonical colony's
own tile is not Desert. `start_debug_game_ready` also has no
biome-selection parameter to steer it even if it were stable, so this item
was never going to close on the currently-loaded map regardless of the
crash.

`needs=bridge` stays accurate (once `QUICKTEST_POSTSETUP_CRASH_1` is fixed
or worked around, e.g. via a minimal+target mod list swap, this item's own
quicktest becomes reachable again) — re-filing under a different `needs`
would misrepresent what's actually blocking it.

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
