# INHABITED_CHARACTERDEF_NAMESPACE_GAP_1

Harvested from the fresh Player.log at the 2026-09-02 game-UP signal:
`[RimMandrake.Inhabited] ready: 2 patches, 0 characters, 0 places, 0 casts.`
— the mod booted, but every one of its 269 authored `CharacterDef`s (across
12 factions' `CastRoster_*.xml`) failed to load, plus a real error:
`Type Inhabited.CharacterDef is not a Def type or could not be found, in
file CastRoster_BLACKSTAR.xml` (same for the other 11 files, one each).

Also masked by a second, independent bug: `harvest_log.py`'s "Inhabited
ready" check regex was still `\[Inhabited\] ready:` (the pre-migration bare
prefix), so it read RED/MISSING even on a log where the mod line was present
— a false negative on top of the real content failure.

## Root cause

`RimMandrake/Inhabited/Source/CharacterDef.cs` was renamed to namespace
`RimMandrake.Inhabited` under the three-tier naming migration
(`NAMING_SCHEME_EXECUTION_1`), but `src/RimMandrake/Utils/cast_to_xml.py`
(the one-way prose -> XML generator, `design/Jawa/bridge/INHABITED_CAST_*.md`
-> `CastRoster_*.xml`) still hardcoded the pre-migration element tag
`<Inhabited.CharacterDef>`. RimWorld's def-XML loader resolves an element
tag to a type by name, and the old bare-namespace tag no longer matches the
renamed class — every entry in every generated file silently failed def
resolution (not a config error the loader treats as fatal; it just drops the
def, per this project's own `<li>`-trap pattern of "wrong shape loads clean
and stays quiet").

`cast_to_xml.py`'s `OUT_DIR` was *also* stale (`src/Jawa/Inhabited/...`, a
dead path since the Jawa->RimMandrake reorg — the directory doesn't exist).
The live `CastRoster_*.xml` under `src/RimMandrake/Inhabited/Defs/` were
last regenerated 2026-08-23, before the C# rename; nobody re-ran the
generator after, so the drift was invisible until this load's log.

## Fixed (FOUNDRY, 2026-09-02, game-UP window)

- `cast_to_xml.py`: `OUT_DIR` corrected to
  `src/RimMandrake/Inhabited/Defs/CastRosters`; the two hardcoded tags
  changed to `<RimMandrake.Inhabited.CharacterDef>`.
- Regenerated against the fresh 593-mod dump
  (`2026-09-02T19-36-08Z`): 294 characters across 12 files, every trait and
  degree resolved clean, diff against the previous XML is *exactly* the tag
  rename (588 lines changed, symmetric open/close tags, nothing else moved).
- `harvest_log.py`'s "Inhabited ready" regex corrected to
  `\[RimMandrake\.Inhabited\] ready:` — confirms "present" against the
  current log now.
- Deployed the 12 regenerated XML files directly (`cp`, verified
  byte-identical repo-vs-deployed via `diff -q`) — `deploy_custom_mods.py
  --mod Inhabited --apply` itself failed on `Assemblies/Inhabited.dll`
  (`OSError: Invalid argument` — the game is UP and holds that DLL open;
  standard "can't write while it runs" lock, unrelated to this fix). The DLL
  also shows as drifted in the plan (`~ Assemblies/Inhabited.dll`) for a
  reason not yet investigated — pre-existing, not caused by this session's
  edits, needs the next game-DOWN window to deploy and diagnose if it's
  still drifted then.

## spec

Confirm at the next restart that `RimMandrake.Inhabited.CharacterDef`
entries actually resolve under RimWorld's def loader when
namespace-qualified with a tag that doesn't match the bare class name —
this exact resolution path (a mid-project C# namespace migration reflected
in a fully-qualified XML tag) has never been observed successfully loading
in this game; the regenerated XML on disk is unproven until a real load
reads it.

## verify

Next launch's Player.log:
- PASS: `[RimMandrake.Inhabited] ready: N patches, 294 characters, ...`
  (or the correct post-skills-discard count per
  `CAST_ROSTER_SKILLS_DISCARDED_1` if that item is still live) — NOT 0.
- FAIL: `Type ...CharacterDef is not a Def type` recurring, or any
  `Could not resolve cross-reference` naming an `Inhabited_*` defName.
- Also confirm `Assemblies/Inhabited.dll` deploys clean once the game is
  down (the blocked copy above) and check whether its drift was itself
  namespace-related or something else entirely.

## criteria

Next load's log shows a nonzero character count on the `[RimMandrake.Inhabited]
ready:` line and no `CharacterDef` resolution errors.
