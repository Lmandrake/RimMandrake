# RaidRedesigner — validation walk
subject: src/RimMandrake/RaidRedesigner  (packageId mandrake.rm.raidredesigner)
deps: brrainz.harmony (hard, modDependencies — already in the minimal list); mandrake.rm.property (loadAfter only in About.xml, but the compiled DLL hard-references `RimMandrakeProperty.dll` — `RaidRedesigner/Source/RM_RaidRedesigner.csproj:85` `<Reference Include="RimMandrakeProperty">` — and `Patch_CaravanRobbed.cs` calls `RimMandrake.Property.PropertyEngine.Fire` directly, so Property must actually be present at runtime despite the soft About.xml declaration)
list: minimal+property
status-hint: a scribed roster (`GameComponent_OldFriends`, cap 24 living `OldFriendEntry` records) of persistent NPCs, populated by eight Harmony postfix hooks at real vanilla/sibling-mod seams (fled raider/captain, escaped/released prisoner, robbed caravan via Property's TakingEvent, kidnapped colonist, Blackstar guest-status change); pure bookkeeping, no defs, no LLM.

## must be true
- On startup, Harmony patches all eight hooks and logs the exact count: `"[RimMandrake.RaidRedesigner] ready: " + patches + " capture-hook patches."` (`RaidRedesigner/Source/RaidRedesignerMod.cs:24`).
- `GameComponent_OldFriends.MaxLivingEntries` is 24; recording a 25th living entry prunes the lowest-notability one, and a dead entry collapses to one line and stays rather than being pruned (`RaidRedesigner/Source/GameComponent_OldFriends.cs:15`).
- Every `OldFriendEntry.role` written by a real hook is one of the eight non-stub `RoleTag` values — `FledRaider`, `Captain`, `EscapedPrisoner`, `Released`, `BetrayedTrader`, `Kidnapper`, `NamedHunter` — never `WokenAncient`, which `Patch_WokenAncient_STUB.cs` deliberately never fires (`RaidRedesigner/Source/RoleTag.cs`).
- A recorded/recalled pawn that leaves the map is pinned via `Find.WorldPawns.PassToWorld(pawn, PawnDiscardDecideMode.KeepForever)`, so it survives world-pawn GC rather than being discarded (`RaidRedesigner/Source/WorldPawnPinning.cs`).
- The roster round-trips through save/load (`ExposeData`) with entries, role tags and dead-flags intact.
- Ships zero Defs and zero LLM/menu-authority code, per About.xml.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.raidredesigner" and no XML error naming RaidRedesigner's About.xml, AND contains "[RimMandrake.RaidRedesigner] ready: 8 capture-hook patches." — the literal count is a regression tripwire: if a future edit removes or fails to register one of the eight postfixes, this line changes   # load-time
2. [L] `dotnet run` in `RaidRedesigner/Source/SelfTest/` (no python wrapper exists yet for this mod's SelfTest project, unlike Property's/Visibility's) runs without throwing — covers whatever pure logic `RaidRedesigner/Source/SelfTest/Program.cs` extracts offline
3. [D] a live RimDefDump capture lists zero defs with `modName` "RimMandrake: Raid Redesigner — Old Friends" — confirms the "no defs" claim in About.xml
4. [B] `jawa/spawn_pawn` a hostile-faction raider, then `jawa/list_pawns` to confirm it exists on the map — precondition for exercising `Patch_FledRaiderAndCaptain.cs`'s `Pawn.ExitMap` postfix, which cannot itself be triggered by a bridge tool today (no "force pawn to flee/exit map" tool exists in `Transient/bench_tools_dump.json`) — note as a walk gap, not a false pass
X. [S] (human pass) none — pure back-end roster, no rendered UI
