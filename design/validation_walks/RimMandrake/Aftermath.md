# RimMandrake: Aftermath — validation walk
subject: src/RimMandrake/Aftermath  (packageId `mandrake.rm.aftermath`)
deps: `mandrake.rm.ninefold` (RimMandrake Ninefold, this tier's own mod); `brrainz.harmony`
list: minimal+ninefold
status-hint: aftermath-hostilities engine — records whole-battle outcomes (REPELLED/ROUTED/STALEMATE/LOST) via a MapComponent, then a rule runner queues a delayed, telegraphed vanilla IncidentDef payload on a match, capped at one per faction / two total. This mod ships NO defs of its own (`RM_AftermathRuleDef` instances ship in `mandrake.rut.aftermath`, not built yet) — walk is built entirely from its own Harmony/C# log strings, per the anti-guessing rule for def-less mods.

## must be true
- On load, `AftermathMod` logs how many battle-recorder Harmony patches applied — a count of 0 is a load-time failure, not neutral.
- `MapComponent_BattleRecorder.OpenBattle` opens a record when `IncidentWorker_Raid.TryGenerateRaidInfo` returns true; the record closes and classifies (`BattleOutcome`: `Repelled`/`Routed`/`Stalemate`/`Lost`) when the raid's Lord is removed.
- The recorder calls Ninefold's own public `GameComponent_Ninefold.ApplyDelta` directly — it must NOT also patch `Pawn.Kill` a second time (Ninefold's `Patch_BattleResolved.cs` already owns that seam).
- `AftermathRuleRunner` reads closed records against `RM_AftermathRuleDef`s and, on a match, queues via `Find.Storyteller.incidentQueue.Add` with `parms.forced = true` — but since no `RM_AftermathRuleDef` ships in THIS mod, no rule can actually fire until `mandrake.rut.aftermath` (or an equivalent) supplies one; this walk can only prove the recorder half live.
- A missing/misnamed `payloadIncidentDefName` on a rule def logs a warning rather than crashing.

## the walk
1. [L] Player.log after load contains `"[RimMandrake.Aftermath] ready: "` followed by a non-zero patch count, and no "Config error in mandrake.rm.aftermath"   # load-time
2. [B] jawa/fire_raid `{points, faction=<a real hostile FactionDef defName from jawa/list_factions>, dryRun=false}` on a live colony map → expect Player.log line `"[RimMandrake.Aftermath] battle opened: <faction.Name> ..."`
3. [B] force the raid to resolve (kill/drive off the raiders via jawa/fire_incident or normal combat, or use `jawa/spawn_pawn`+damage to speed it) → expect Player.log line `"[RimMandrake.Aftermath] battle closed: <faction.Name> ..."` naming one of Repelled/Routed/Stalemate/Lost
4. [D] confirm via jawa/pawn_thoughts or Ninefold's own satiation state (see `Ninefold.md` step 3) that `GameComponent_Ninefold`'s mood vector moved as a side effect of step 3 closing — proves the direct `ApplyDelta` call fired, not a second independent patch
5. [L] with zero `RM_AftermathRuleDef` currently loaded (true today — defs ship in the not-yet-built `mandrake.rut.aftermath`), confirm Player.log shows NO `"[RimMandrake.Aftermath] queued ..."` line after step 3 — the rule-runner half is present in code but has nothing to match against yet, and the walk should say so rather than claim it fires

## anti-guessing notes
- No XML defs ship in this mod folder (`find src/RimMandrake/Aftermath -iname "*.xml"` returns only `About/About.xml`) — every check above is [L]/[B], never a [D] defName guess against this mod's own Defs/.
- No [S] line: this is a pure narrative/incident-timing system with no bespoke art.
