# SacredGraffiti — validation walk
subject: src/RimMandrake/SacredGraffiti  (packageId mandrake.rm.sacredgraffiti)
deps: mandrake.rm.graffiti (hard modDependency, "RimMandrake: Graffiti Framework" — supplies `RM_BaseGraffiti`, the ParentName every sacred mark inherits from)
list: minimal+graffiti
status-hint: sacred devotional wall-marks, one per Salvation god (one shipped: Ishko), built on `mandrake.rm.graffiti`'s filth infrastructure; placement mechanism is ready but genuinely unwired — no real ritual references it yet.

## must be true
- `ThingDef RM_SacredMark_Ishko` (`ParentName="RM_BaseGraffiti"`) resolves, with `graphicClass Graphic_Single`, `texPath Things/Filth/SacredMark/SacredMark_Ishko`, and `statBases` `Flammability 0`, `Beauty 6` (positive — devotional, not vandalism), `Cleanliness -2` (`SacredGraffiti/Defs/SacredMarks.xml:38-50`).
- Its `ModExtension_Graffiti` carries `category=Sacred`, `supportsQuality=false`, `hasSubject=false`, `godSatiationHook=Ishko` (`SacredMarks.xml:62-69`).
- `RitualOutcomeEffectDef RM_Ishko_RitualOutcome_PlaceSacredMark` resolves, `workerClass RimMandrake.SacredGraffiti.RitualOutcomeEffectWorker_PlaceSacredMark`, `filthDefToSpawn RM_SacredMark_Ishko`, `filthCountToSpawn 1~1`, `startingQuality 0.5` (`SacredGraffiti/Defs/RitualOutcomeEffects.xml:28-49`).
- `RitualOutcomeEffectWorker_PlaceSacredMark.ApplyExtraOutcome` only spawns the mark on a POSITIVE outcome (`if (!outcome.Positive) return;`), and only if `def.filthDefToSpawn` is set; it spawns via `FilthMaker.TryMakeFilth` at the ritual's target cell, falling back to a present participant's position if the target carried no cell (`SacredGraffiti/Source/SacredGraffiti.cs:55-79`).
- 🔴 As of this walk, `RM_Ishko_RitualOutcome_PlaceSacredMark` is NOT referenced by any real `RitualDef`/`PreceptDef` — the Salvation Matrix's boons/curses are design prose only (About.xml, Defs/RitualOutcomeEffects.xml header). The mechanism is real and inert; do not expect it to fire from ordinary play.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.sacredgraffiti" and no XML error naming SacredGraffiti's About.xml or Defs   # load-time; also proves ParentName RM_BaseGraffiti resolved from mandrake.rm.graffiti
2. [D] def read-back: `ThingDef RM_SacredMark_Ishko` exists; `statBases.Beauty` = 6; `modExtensions[ModExtension_Graffiti].godSatiationHook` = "Ishko"
3. [D] def read-back: `RitualOutcomeEffectDef RM_Ishko_RitualOutcome_PlaceSacredMark` exists; `workerClass` = "RimMandrake.SacredGraffiti.RitualOutcomeEffectWorker_PlaceSacredMark"; `filthDefToSpawn` = "RM_SacredMark_Ishko"
4. [B] `jawa/spawn_thing {defName: "RM_SacredMark_Ishko", count: 1}` → success, then `jawa/list_things` confirms it exists on the map with the expected texPath/Beauty — proves the def itself is game-ready even though no ritual can reach it yet (per must-be-true's 🔴 note, this bypasses the worker entirely and is a def-sanity check, not an end-to-end ritual test)
X. [S] (human pass) with the mark spawned, confirm the "pair of glowing orange eyes" art actually renders (positive Beauty in the inspect pane) rather than a placeholder/magenta texture — deferred to MOD_HUMAN_EXPLORATION_PASS_1
