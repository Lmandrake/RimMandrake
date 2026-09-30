# CONTAGION_FLORA_PORT_1 — report (in progress)

## Status: DONE — pushed b632297aa

## Scope
Port 9 flora from cast bible §4 into RM_ContagionFlora.xml, replace donor
AB_* rows in RM_Contagion.xml <wildPlants>.

## Steps
- [x] Read cast bible §4 + §8
- [x] Check existing defs in src/ (grep) — 0 collisions
- [x] Find donor defs (installed mods) — Alpha Biomes, workshop 1841354677
- [x] Search artpipe for existing art — all 9 validated pass, copied in
- [x] Write RM_ContagionFlora.xml appends (9 plants + tellRattlers stub note)
- [x] Add RM_RedSap.xml + RM_SeedFistFertilizer.xml (Sapblister/Bloody Fist
      harvest items, ban-4 compliant, no ingestible/Nutrition)
- [x] Update RM_Contagion.xml wildPlants (donor AB_* out, 9 RM_ rows in) +
      wired RM_Rattlegrope into existing `<tellRattlers>` (data-only, no
      new C#) + corrected the stale header comment (donor-free claim)
- [x] Verify: XML parse (4/4 OK after fixing "--" inside comments, invalid
      XML), 0 defName collisions, validate_patch.py --defs (Data+Mods+
      Workshop) 0 errors/0 warnings across all 4 touched/new files
- [x] run_selftests.py: 76/78 pass, 1 UNMEASURED (bridgetools DLL build,
      needs Windows-side .NET SDK, offline as expected), 1 known FAIL
      (`selftest_deployed_biome_refs.py`) — unchanged by this work. All 21
      dangling refs it names are RUT_TheRot.xml/RUT_TheForge.xml/
      RUT_WeepingStones.xml/RUT_Contagion.xml (the separate RimUtinni-tier
      twin biome file, not the RM_Contagion.xml this item touched) —
      pre-existing fungus/mushroom defs, none of my 9 new RM_ flora
      defNames or commonalities appear anywhere in its output. Neither
      fixed nor worsened.
- [ ] Commit + push

### NOT done, flagged for the coordinator
`RM_ContagionSkyExtension.cs`'s `tellRattlers` field comment still says
"Empty until the Rattlegrope port lands (RM_Rattlegrope does not exist yet)"
— now stale, since RM_Rattlegrope exists and is wired into `<tellRattlers>`.
Did NOT fix: this repo's DLL_SOURCE_STAMP_GUARD_1 requires any Source/*.cs
edit to be followed by a DLL rebuild (RimMandrake.Contagion.dll +
.srchash), and this worktree's sandbox refuses any Bash command that
references a path outside the worktree (blocks invoking dotnet.exe at
/mnt/c/Program Files/dotnet/dotnet.exe), so a rebuild isn't possible from
here. No .cs file was touched (edit made then reverted) — comment fix is a
one-line follow-on for a seat that can build the DLL.

## Findings

### Existing defs check
No collision: grep for RM_Eyebark/Lashgrass/Bleedleaf/Gorestalk/Rattlegrope/
Sapblister/BloodyFist/HalfmadeTree/HalfmadeTreeBlighted across src/, design/,
infrastructure/state/items found only the cast bible + this item's own prose.
0 existing defs.

### Donor defs (measured, read from installed mod)
Donor mod: Alpha Biomes (workshop id 1841354677), packageId `sarg.alphabiomes`.
- `AB_AlienGrass`,`AB_RedLeaves`,`AB_RedPlantsTall`,`AB_AlienTree`,
  `AB_HalfAlienTree`,`AB_TentacularPlant`,`AB_GlobularPlant`,`AB_BloodBouquet`:
  `1.6/Defs/ThingDefs_Plants/Plants_OcularForest.xml`
- `AB_AlienTree_Polluted`: `1.6/Mods/Biotech/Defs/ThingDefs_Plants/
  Plants_Ocular_Polluted.xml`

### Art search (registry.jsonl + _artsrc, sanity probe: Meatvine/Toothmoss/
Wombpod all read 0 in artpipe dirs too — confirms this WORKTREE's copy of
infrastructure/artpipe is stale/behind the main tree, not that the search
tool is broken)
All 9 new names show `registered -> queued -> generated -> validated (pass)`
in registry.jsonl. Actual PNGs are NOT in this worktree's artpipe dirs (git
worktree is behind the live daemon output on the main tree) but ARE present
on disk at the native main-tree path (read-only, no git op):
`D:\Luke\dev\Rimworld\infrastructure\artpipe\_artsrc\RM_<Name>\RM_<Name>.png`
— all 256x256 RGBA, verified with PIL. RM_Eyebark has both v1 and a
validated v2 IMPROVE pass (owner note: "Make it hang droopily downward like
a willow") — used v2 as the shipped art per the improve superseding the v1.
Copied all 9 into
`src/RimMandrake/Contagion/Textures/Things/Plant/RM_<Name>/RM_<Name>.png`.
No BLOCKED art — all 9 found and wired.

### Rattlegrope stub
`RM_ContagionSkyExtension.cs`'s `tellRattlers` list already exists and is
already consumed by `RM_MapComponent_ContagionSky.cs` (a pre-built mechanism,
not new C#). Wired `RM_Rattlegrope` into the biome extension's
`<tellRattlers>` (pure data wiring of an already-live mechanism) and left the
plant def itself with a stub comment only — no new comp/CompTickLong added.
