# Load errors triage 2026-10-09

(a) cross-refs: pending
(b) patch failures: pending
(c) ConfigErrors: pending
(d) missing art: pending
(e) SettingsOpenSmoke: pending
(a)(b) landed c73b7e7 61e9b33 63933e4 f8f2418; (c) in progress: menushell id, RUT_Tree_Hearth coords, RM_FE_* burnedDef, FoundrySalvageCache, RM_Illisk
(c) landed: SalvageCache move 41a77e8, Illisk 58c34c7, menushell rename; skipped (accepted by owner 2026-09-03): RM_FE_* burnedDef x4. RUT_Tree_Hearth coords: next
(d) skeleton graphicClass fixed 37c11ed; Swarmling/ZakkroEgg pending
(e) RM_SettingsOpenSmoke landed 2afb054 (unrun in game); MenuShell rename blocked by art guard, reverted

## Result
Fixed: c73b7e7 Thrumbungus resize retarget (sequence was aborting), 61e9b33 GreyLady, 63933e4 GravForge Copy recipe, f8f2418 Creep holds lifted, 41a77e8 SalvageCache move, 58c34c7 Illisk, 37c11ed skeleton graphicClass, 99b1b94 ZakkroEgg art, 2afb054 SettingsOpenSmoke.
Not ours / accepted: RM_FE_* burnedDef x4 (owner accepted 2026-09-03); research coord collisions (final dump values distinct, engine saw pre-relocation values, donor projects); menushell defName (RimThemes donor builds it from folder name with a space; rename blocked by art guard).
Needs owner/live: Rot AA_Swarmling art (purged 2026-10-08 greentide redo, no replacement approved); needs deploy of all above + deleting old UtinniPatches RUT_FoundrySalvageCache.xml; SettingsOpenSmoke live run; UtinniPatches loads before mandrake.rm.biomes in live order (contradicts its loadAfter).
Silent no-ops noted, not touched: ~45 BMT_* targets in MegafaunaYield.xml (retired donor).
