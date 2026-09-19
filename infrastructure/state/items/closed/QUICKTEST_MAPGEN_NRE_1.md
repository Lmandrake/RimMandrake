# QUICKTEST_MAPGEN_NRE_1 — root-caused: stale in-memory defs, fix already on disk

## Spec
Live `Player.log` (`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by
Ludeon Studios/Player.log`, the exact file/lines the queue title cites) shows the NRE
twice in the same session — once via `LoadGame`, once via `SetupForQuickTestPlay`:

```
Exception from asynchronous event: System.NullReferenceException: Object reference not set to an instance of an object
  at Verse.GenTypes.SameOrSubclassOf (System.Type baseType, System.Type parentType)
  at Verse.GenTypes.SameOrSubclassOf[T] (System.Type baseType)
  at RimWorld.ReadingPolicyDatabase.GenerateStartingPolicies ()
RimWorld.ReadingPolicyDatabase..ctor()
  at Verse.Game..ctor ()
  at Verse.Root_Play.SetupForQuickTestPlay ()
```

This is **not quicktest-specific** — it crashes `Verse.Game..ctor()` on *any* new
game/load. `ReadingPolicyDatabase.GenerateStartingPolicies()` is vanilla
(`RimWorld/ReadingPolicyDatabase.cs:69-110`, read via RimSage) and does:

```csharp
foreach (ThingDef item in DefDatabase<ThingDef>.AllDefsListForReading)
    if (item.thingClass.SameOrSubclassOf<Book>()) ...
```

No null-check on `item.thingClass`. `SameOrSubclassOf` is an extension method, so
calling it on a null `Type` doesn't throw at the call site — it throws inside
`GenTypes.SameOrSubclassOf(Type, Type)` the moment it touches `baseType`. Any
ThingDef with a null `thingClass` crashes every game start, unconditionally.

## Root cause
Grepping the same log for `has null thingClass` finds exactly 14 lines — the same
7 `RSW_*Juv` sea-beast ThingDefs `MIASMA_JUVENILES_NULL_THINGCLASS_1` already
identified (`RSW_MeeJuv`, `RSW_FaaJuv`, `RSW_LaaJuv`, `RSW_YobshrimpJuv`,
`RSW_SiltLampreyJuv`, `RSW_RustNipperJuv`, `RSW_OpeeSeaKillerJuv`), each preceded
one line earlier by `XML error: Could not find parent node named "RSW_<Species>"`
— their `ParentName` can't resolve, so `XmlInheritance` falls back to the Juv's
own bare XML (no `thingClass`, no `renderTree`, etc.). No other ThingDef in this
load has a null `thingClass`.

**This is the exact symptom `MIASMA_JUVENILES_NULL_THINGCLASS_1` already root-caused
and already fixed** (stale-deployed `SWBestiary`: the live `Mods/SWBestiary/...`
copy of `SeaBeasts_Scalefish.xml`/`SeaBeasts_Opee.xml`/`SeaBeasts_Swarm.xml` predated
the commit that added `Name="RSW_Mee"` etc., so nothing registered those names for
the juveniles to inherit from). That item's fix:
`deploy_custom_mods.py --mod SWBestiary --apply`, applied 2026-09-10 23:48:15 local.

**Why this crash still shows it: the fix landed mid-session, and RimWorld only
reads Defs from disk at process launch.**
- `Player-prev.log`'s mtime (22:31 local, 2026-09-10) is when *this* session's
  `Player.log` began (Unity rotates the previous log at launch).
- The SWBestiary XML files were rewritten to disk at 23:48:15 — over an hour
  *into* that same still-running session.
- The crash log's own evidence (`23:41` timestamp cited in
  `MIASMA_JUVENILES_NULL_THINGCLASS_1`, plus this file's 00:48 last-write) is all
  one continuous session that started before the fix and never restarted.
- **Verified at investigation time (this pass):** the live-deployed
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\SWBestiary\Defs\
  SeaBeasts\ThingDefs_Races\SeaBeasts_Scalefish.xml` and the repo's
  `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Scalefish.xml`
  are byte-identical and both carry `Name="RSW_Mee"` / `Name="RSW_Faa"` (etc.)
  correctly, right now — the fix is genuinely on disk.

**Ruled out:** `RESTORE_FALLOUT_TRIAGE_1`'s hedged hypothesis that these are
"orphaned juveniles" left behind by the 139-reversal CherryPicker restore (parent
cut, juvenile restored). Checked both ground-truth sources via `cherrypicker.py`:
neither the live settings file (`cherrypicker.load()`) nor this exact session's own
Player.log removal block (`cherrypicker.from_log()`) list any of the 7 adult
species (`RSW_Mee`, `RSW_Faa`, `RSW_Laa`, `RSW_Yobshrimp`, `RSW_SiltLamprey`,
`RSW_RustNipper`, `RSW_OpeeSeaKiller`) as cut. Cherry Picker is not the mechanism
here — stale mid-session defs are.

## Fix
**No new code or XML change made by this pass.** The actual fix (the SWBestiary
redeploy) already exists on disk, applied by `MIASMA_JUVENILES_NULL_THINGCLASS_1`
before this crash log was captured; this item's crash is that fix's effect not
yet having reached a running game process, not a second bug.

## Verify — owed, and it is a LIVE-only check (no bridge/game access from this
worktree)
A cold restart is the first load since 23:48:15's redeploy. On that next load's
fresh `Player.log`, confirm all three clear together (they're one mechanism):
- [ ] No `Could not find parent node named "RSW_Mee/Faa/Laa/Yobshrimp/
      SiltLamprey/RustNipper/OpeeSeaKiller"` lines.
- [ ] No `Config error in RSW_*Juv: has null thingClass` lines.
- [ ] `SetupForQuickTestPlay` (and `LoadGame`) no longer throw in
      `ReadingPolicyDatabase.GenerateStartingPolicies` — quicktest actually reaches
      a map.

If a next-load log ever shows this NRE again for a *different* ThingDef (not these
7), that is a new instance of the same vanilla gap (no null-check on `thingClass`
in `ReadingPolicyDatabase.GenerateStartingPolicies`) and worth considering a small
defensive Harmony postfix/prefix guard at that point — not attempted here since
the concrete cause has a concrete data fix already in place and adding an engine
patch for a currently-hypothetical future recurrence is scope beyond this item.

## Criteria
- [x] Real root cause identified from the live Player.log + vanilla source
      (RimSage), not guessed.
- [x] Confirmed the responsible data fix is already deployed and correct on disk
      (diff, byte-identical repo vs. live).
- [x] Confirmed Cherry Picker is not the mechanism (checked both its settings
      file and this session's own removal-block log).
- [ ] Cleared on an actual next cold load — not yet possible from this isolated,
      bridge-less worktree; owed to whoever next restarts the game.
