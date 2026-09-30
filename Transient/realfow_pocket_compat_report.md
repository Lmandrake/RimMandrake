# REALFOW_POCKET_MAP_COMPAT_1 report

## Donor members (measured)

Decompiled with ilspycmd from
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3391128917\1.6\Assemblies\rimworld-mod-real-fow.dll`
(packageId `Mlie.NWNRealFogOfWar`), 2026-09-30:

- `RimWorldRealFoW.CompFieldOfViewWatcher : ThingSubComp`
  - `private List<Pawn> nearByPawn`, `private Pawn pawn`, `private MapComponentSeenFog mapCompSeenFog`
  - `private void livePawnHear(Faction)`: iterates `nearByPawn`, calls `mapCompSeenFog.IsShown(faction, item.Position)`
    for moving non-faction pawns.
  - `private void updateNearbyPawn(Pawn, float, float)`: `nearByPawn = MapUtils.GetPawnsAround(...) as List<Pawn>`.
  - `PostSpawnSetup` resets ticks and calls `initMap()`, which re-points `mapCompSeenFog`. It never clears `nearByPawn`.
- `MapUtils.GetPawnsAround` builds a fresh `new List<Pawn>()` on every call, so editing the cached list in place is safe.
- `MapComponentSeenFog.IsShown(Faction,int,int)`: `GetFactionShownCells(faction)[z * mapSizeX + x]`, no bounds check.

## Patch

Host: **DivingInteraction** (`mandrake.rm.divinginteraction`). It already references Harmony and calls `PatchAll`, and it
is the mod that owns the pocket maps. No new dependency was needed.

`src\RimMandrake\DivingInteraction\Source\Patch_RealFoWStaleHearing.cs` adds a **prefix on
`CompFieldOfViewWatcher.livePawnHear`**. Before each hearing pass it removes every cached pawn that is not on the listening
pawn's current map, and it clears the list when the listener has no map. The root cause is the stale list, so the fix
removes the stale entries. It does not only swallow the out-of-bounds read. It covers both ways the list goes stale:
the listener changes map, or a heard pawn leaves.

- `Prepare()` resolves the type with `AccessTools.TypeByName`. When Real FoW is absent, or when any expected member is
  missing or has the wrong type, it returns false and PatchAll skips the class. The member-mismatch case also logs one warning.
- Toggle: `RM_DivingSettings.realFowCompatEnabled`, default ON. The checkbox is shown outside the `masterEnabled` block
  because the fix applies to every map change, not only to dives.

## Build/tests

- `dotnet.exe build ... -c Release`: 0 warnings, 0 errors. The DLL and its `.srchash` were rebuilt.
- Selftests: see the final section.

## Live check owed

Run with Real FoW active. Wait until a colonist has moving wild animals within hearing range on the home map, then take
that colonist through an `RM_SeaDiveHatch` onto a sea floor and let at least 400 ticks pass.
`Player.log` must show **no** `MapComponentSeenFog.IsShown` / `livePawnHear` IndexOutOfRangeException.
Before this fix it threw every 100 ticks (`Transient/sea_dive_player_log_2026-09-30.txt`, around line 26834).
