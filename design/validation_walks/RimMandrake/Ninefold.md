# RimMandrake Ninefold (M0 — safe core) — validation walk
subject: src/RimMandrake/Ninefold  (packageId `mandrake.rm.ninefold`)
deps: none (Ludeon.RimWorld, brrainz.harmony only)
list: minimal
status-hint: nine-god satiation/mood vector (Ishko, Ohm, Oomo, MobUnloo, Rekko, TaBaa, Zizzik, Shkaar, Ozzik), a band ladder (Wrathful/Slighted/Neutral/Content/Exalted), a per-god Mood random walk, and five Harmony hooks (research completed, mental break started, birth outcome, building deconstructed, building repaired) that call `ApplyDelta`. This mod ships NO XML defs (`find src/RimMandrake/Ninefold -iname "*.xml"` returns only About.xml) — walk built from its own log strings, per the anti-guessing rule for def-less mods.

## must be true
- On load, `NinefoldMod` logs how many event-hook patches applied — 0 is a load failure, not neutral.
- `GameComponent_Ninefold` persists a satiation value AND a mood value per one of the 9 `God` enum members, and both survive a save/load round-trip (its own log warns if a saved list's count does not match `GodExtensions.Count` = 9).
- Each of the five wired events (research completed, mental break started, birth outcome, building deconstructed, building repaired) moves at least one god's satiation/mood by a measurable, non-zero delta when it fires — `ApplyDelta`'s effect is logged per-call: `"[Ninefold] <god> satiation ..."`.
- `God` enum member ORDER must not be relied on for save compatibility — `God.cs` itself calls out `NINEFOLD_ENUM_ORDER_SAVE_TRAP_1` as a live hazard; a check should confirm the save format keys by god NAME, not ordinal.

## the walk
1. [L] Player.log after load contains `"[RimMandrake.Ninefold] ready: "` followed by a non-zero patch count, and no "Config error in mandrake.rm.ninefold"   # load-time
2. [B] jawa/research_finish_project on any real ResearchProjectDef → expect Player.log line `"[Ninefold] <god> satiation ..."` naming the god the research-completed hook is wired to
3. [B] jawa/pawn_force_mental_break on a colonist → expect a second `"[Ninefold] <god> satiation ..."` line for the mental-break-started hook's god
4. [D] before/after each of steps 2-3, read the live satiation/mood value for the affected god (whatever accessor `GameComponent_Ninefold` exposes — confirm the read path with `mcp__rimsage__read_csharp_symbol GameComponent_Ninefold` before writing the concrete call) and assert the delta is non-zero and moves the band ladder consistently (e.g. Neutral -> Content, not backwards)
5. [B] save the game and reload (or use a bridge save/load round-trip if one exists) → re-read the same god's satiation/mood and confirm it matches the pre-save value, with no `"[Ninefold] saved satiation list has ..."` or `"saved mood list has ..."` warning in Player.log

## anti-guessing notes
- `Log.Error("[Ninefold] NINEFOLD_ENUM_ORDER_SAVE_TRAP_1: God." + ...)` in `God.cs:59` is a live self-check the mod already runs; its ABSENCE from Player.log after step 5 is itself part of the pass condition, not just its presence proving a bug.
- No [S] line: satiation/mood is an internal number this pass, with no bespoke UI or art surfacing it yet (per the mod's own "the wiring itself is not built yet" note about downstream consumers).
