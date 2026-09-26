# Rescued: mandrake.rut.lanterndeeps (2026-09-26)

Byte-exact recovery of the whole 82-file mod does not need this directory:
81 files are at `8a2b2364b:src/RimUtinni/LanternDeeps` (the tree `1f1c368f7`
removed, with its C# source) and the DLL is blob `73566ff39` in `6ce1ccf9c`
(MEASURED 2026-09-26, sha256 against the game folder). This directory is the
convenience copy of the 28 non-art files of the **live, active** mod
`mandrake.rut.lanterndeeps`. Before this rescue its current tree
existed in exactly one place on the machine: `C:\Program Files (x86)\Steam\
steamapps\common\RimWorld\Mods\LanternDeeps` (WSL:
`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/LanternDeeps`)
— no repo copy anywhere, so a disk failure would have lost it outright. The
canonical campaign save references its `RUT_LanternDeeps` defs (the biome, the
two entrance buildings, lanternstone terrain and walls, cave flora) and
nothing else resolves them. Background and hazards: item
`LANTERNDEEPS_TIER_COLLISION_1`.

## What is here

The 28 files that are **unique** to the live mod — everything in it that is
NOT byte-identical to a file already committed under the RM successor at
`src/RimMandrake/LanternDeeps`:

- `About/About.xml` (packageId `mandrake.rut.lanterndeeps`)
- `Assemblies/RimMandrake.Utinni.LanternDeeps.dll`
- 19 `RUT_*` def XML files under `Defs/` (Biomes, MapGeneration, SoundDefs,
  TerrainDefs, ThingDefs_Buildings, ThingDefs_Items, ThingDefs_Natural,
  ThingDefs_Plants, Weather)
- 7 `RUT_*` patch XML files under `Patches/`

Each is at its original relative path under the mod root, so
`About/About.xml` here is `<mod root>/About/About.xml`, etc. Verified
byte-for-byte (sha256) against the game-folder source at time of rescue —
all 28 matched exactly.

## What is deliberately NOT duplicated here

The other **54 files** of the live mod (all art, including the 11 MB
`Textures/RUT_LanternDeeps/Things/Natural/Linked/lanternstone_wall_atlas.png`)
are byte-identical to files already tracked in git under
`src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/...` (same bytes,
different path — the RM tier renamed the texture folder but kept the source
art unchanged). Duplicating identical bytes a second time here would just be
bulk with no new provenance, so they were skipped. The rule: **only files
with no byte-identical twin anywhere in the repo get copied here.**

## This is an archive, not a deployable mod

⛔ **Do not put this content under `src/{RimMandrake,RimStarWars,RimUtinni,
SPLIT_Phase3}/`.** `deploy_custom_mods.py` discovers mods by that exact path
pattern (`SRC_TIERS`) and keys them by folder name. `mandrake.rm.lanterndeeps`
already deploys to `Mods\LanternDeeps` (same folder name the live RUT mod
occupies in the game folder) — a second mod also named `LanternDeeps` under
one of those tier roots would collide with it silently, which is the exact
hazard `LANTERNDEEPS_TIER_COLLISION_1` exists to prevent. This directory
lives under `infrastructure/state/rescued/`, invisible to the deploy tool, on
purpose.

Nothing here should be deployed, patched in place, or treated as a live
source tree. It exists so the content is not lost, not so it can be built or
shipped from this location.

## How to reconstitute the full mod, if ever needed

The full 82-file `mandrake.rut.lanterndeeps` mod is: these 28 files, plus the
54 byte-identical files, which can be recovered from
`src/RimMandrake/LanternDeeps` at the paths below (swap `RM_LanternDeeps` for
`RUT_LanternDeeps` in the texture paths to restore the original folder
layout):

```
src/RimMandrake/LanternDeeps/LICENSE
src/RimMandrake/LanternDeeps/Patches/RUT_LanternDeepEvictCrystalFauna.xml   (or its RM equivalent, byte-identical)
src/RimMandrake/LanternDeeps/Patches/RUT_LanternstoneFictionRename.xml     (or its RM equivalent, byte-identical)
src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/**                   (identical bytes to Textures/RUT_LanternDeeps/** in the live mod)
```

Assembling the two sets back onto the original relative paths recreates the
live mod's file tree exactly. The tier migration itself (deciding whether the
RUT mod is retired in place of the RM one, or the two coexist under different
folder names through a transition) is still owed — see
`LANTERNDEEPS_TIER_COLLISION_1`. This rescue only discharges the loss-risk
half: the content now exists in git, committed and pushed, regardless of
what happens to the game-folder copy.
