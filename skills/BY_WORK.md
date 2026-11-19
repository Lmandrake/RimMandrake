# Skills by kind of work: the SKILL.md paths to read first

Owner, 2026-11-19: *"since we're not seeming enamored of auto firing skills at the moment, it might be very important
to pass relevant debug skills to the subagents we assign to do related work, yes?"* Most project skills are no longer
registered (`skills/README.md`, table "Not registered (read by path)"), so a helper never sees their descriptions. A
helper reads a skill only when its brief names the skill's path. **Every brief names the SKILL.md paths for its kind
of work, taken from this page** (`src/RimMandrake/rimflow/roles/conductor.md`); `detached_helper.py launch` prints a
WARNING for a brief that names none.

Paths in this repo are relative to the clone root (on the mirror: `D:\Luke\dev\RimMandrake\skills\...`). Paths starting
`~/dev/` are skills outside this repo (`D:\Luke\dev\...`); most are not registered machine-wide either
(`~/dev/Lodestar/claude/skills.md` says which), so they too are read by path. Read the skill
when you are about to do the work, not before. Whether each one is registered is the table at the end.
`src/RimMandrake/Utils/selftest_skills_by_work.py` refuses a skill folder missing from this page, and a registration
column that disagrees with `.claude/skills/`.

## Live debugging and proofs
- `skills/live-debugging-proof-harness/SKILL.md`: write, run and read a live proof (proof_all, validation_v2, LogTap).
- `skills/rimworld-debug-testing/SKILL.md`: throwaway quicktest colonies; what a quicktest can and cannot prove.
- `skills/northstar-validation/SKILL.md`: a mod's north-star suites live (bland world, situational envelope).
- `skills/telemetry/SKILL.md`: recorded history before re-measuring the game, bridge, disks or art pipeline.
- `~/dev/MandrakeWorkflows/skills/test-pilot-sitting/SKILL.md`: the Test Pilot's method (theories, one change at a time).

## Driving the live game over the bridge
- `skills/rimbridge/SKILL.md`: drive the running game (planet, map, pawns, weather, raids); a call that "succeeded" but
  moved nothing.
- `skills/rimbridge-companion/SKILL.md`: add a new [Tool] to the JawaBench companion DLL when the bridge cannot do it.
- `skills/rimworld-live-review/SKILL.md`: stage a scene and capture it for a human to look at.
- `skills/rimworld-world-editing/SKILL.md`: edit the planet (tiles, biomes, rivers, landmarks) from the bridge.

## Deploying to the game
- `skills/rimworld-deploy/SKILL.md`: the repo is not the game's Mods folder; plan, apply, validate.
- `skills/rimworld-start-prep/SKILL.md`: the mod list and load order before the game launches.

## Load rounds (a cold load, a restart)
- `skills/rimworld-load-round/SKILL.md`: spend a cold load well, or avoid it (the 13-mod minimal list).
- `skills/rimworld-start-prep/SKILL.md`: the three writers of the mod list.

## Savegames
- `skills/rimworld-savegame/SKILL.md`: read, grep and edit a `.rws` (map grids, shortHashes, fogGrid).
- `skills/gravship-layout/SKILL.md`: gravship layouts as XML (ShipLayoutDefV2), with no game running.

## Modding and patches
- `skills/rimworld-modding/SKILL.md`: Defs, XML patches, C#/Harmony, inheritance, Player.log triage.
- `skills/rimworld-deploy/SKILL.md`: writing a file is not deploying it.
- `skills/rimbridge-companion/SKILL.md`: when the change is a bridge tool.

## Game content by kind
- `skills/rimworld-quests/SKILL.md`: QuestScriptDefs and their silent signal bugs.
- `skills/rimworld-custom-incidents/SKILL.md`: IncidentDefs, IncidentWorkers, storyteller pacing.
- `skills/rimworld-crew-and-nemesis-events/SKILL.md`: who joins, is taken or comes back to a small crew.
- `skills/rimworld-ideoligion/SKILL.md`: ideoligions (IdeoPresetDef, the FactionDef ideo block).
- `skills/rimworld-xenotypes/SKILL.md`: xenotypes and the genes that give them a face.
- `skills/rimworld-scenario-building/SKILL.md`: scenarios, game-creation settings, storyteller.
- `skills/rimworld-content-moderation/SKILL.md`: which content from a large mod stack stays.

## Maps, structures and scenes
- `skills/rimworld-layout-layers/SKILL.md`: a structure by its power, pipe, roof and floor layers.
- `skills/rimworld-scene-composition/SKILL.md`: a scattered site that reads as one authored place.
- `skills/gravship-layout/SKILL.md`: gravship designs.
- `skills/rimworld-world-editing/SKILL.md`: the planet.

## Art and sprites
- `skills/generating-rimworld-sprites/SKILL.md`: game-ready sprites matching a reference (canvas, alpha, footprint).
- `skills/rimworld-sprite-facings/SKILL.md`: north/south/east/west facings, mirrors, flip-books.
- `~/dev/MandrakeWorkflows/skills/generating-images/SKILL.md`: a new raster image through Codex $imagegen.
- `~/dev/MandrakeWorkflows/skills/editing-images/SKILL.md`: editing an existing image through Codex $imagegen.
- `skills/reading-rimworld-graphics/SKILL.md`: finding a texture on disk or in an AssetBundle.

## Judging art
- `skills/rimworld-art-evaluation/SKILL.md`: the art judging pipeline (Opus first, GPT second look).
- `skills/rimworld-sprite-facings/SKILL.md`: whether each facing is right.
- `skills/rimworld-canon-references/SKILL.md`: Star Wars work graded against the canon library.

## Review sheets (a human keeps, cuts or ranks many items)
- `skills/rimworld-review-sheets/SKILL.md`: RimMandrake sheets, true scale, `art.py enact`.
- `~/dev/MandrakeWorkflows/skills/review-sheets/SKILL.md`: the general layer under it.
- `skills/rimworld-content-moderation/SKILL.md`: contact sheets for keep/cut calls on a mod stack.

## Landing commits
- `skills/clone-landing-commits/SKILL.md`: `./publish`, `./sync`, a clone that reads ahead and behind.

## The ledger (rimflow) and the accounts
- `skills/using-rimflow/SKILL.md`: every rimflow verb, the shards, the provenance flags, the bridge lock.
- `skills/rimflow-operations/SKILL.md`: the Claude accounts' quota, switching plan, standing windows down and up.

## Measuring large files
- `~/dev/MandrakeWorkflows/skills/measuring-large-artifacts/SKILL.md`: numbers from files too big to read.
- `~/dev/MandrakeWorkflows/skills/confident-wrong-numbers/SKILL.md`: a round, zero or alarming count.
- `skills/rimworld-savegame/SKILL.md`: when the large file is a save.
- `skills/telemetry/SKILL.md`: when the answer is already recorded.

## Design orders (three options with tradeoffs, a GPT skeptical teardown, a merge)
- `~/dev/MandrakeWorkflows/skills/deep-design-3x2/SKILL.md`: his usual design order, run as one workflow (three real
  solutions, GPT blind then critiquing, a re-measure, one merge, decisions back to him).
- `~/dev/Dispatch/skills/chatgpt-consult/SKILL.md`: how to reach GPT for the second pass.

## Writing a helper's brief
- `~/dev/MandrakeWorkflows/skills/efficient-subagents/SKILL.md`: scope, feed and bound a helper.
- This page: name the paths for the helper's kind of work.

## Writing a checker (a selftest, a gate, a judge)
- `~/dev/MandrakeWorkflows/skills/mutate-your-checker/SKILL.md`: watch it go red on a planted fault first.

## Every skill folder in this repo, and whether it is registered

`yes` = linked under `.claude/skills/`, so its description loads by itself; `no` = read by path only.

| skill | registered |
|---|---|
| `clone-landing-commits` | yes |
| `generating-rimworld-sprites` | yes |
| `gravship-layout` | no |
| `live-debugging-proof-harness` | yes |
| `northstar-validation` | no |
| `reading-rimworld-graphics` | no |
| `rimbridge` | yes |
| `rimbridge-companion` | yes |
| `rimflow-operations` | yes |
| `rimworld-art-evaluation` | no |
| `rimworld-canon-references` | no |
| `rimworld-content-moderation` | no |
| `rimworld-crew-and-nemesis-events` | no |
| `rimworld-custom-incidents` | no |
| `rimworld-debug-testing` | no |
| `rimworld-deploy` | yes |
| `rimworld-ideoligion` | no |
| `rimworld-layout-layers` | no |
| `rimworld-live-review` | yes |
| `rimworld-load-round` | yes |
| `rimworld-modding` | no |
| `rimworld-quests` | no |
| `rimworld-review-sheets` | yes |
| `rimworld-savegame` | no |
| `rimworld-scenario-building` | no |
| `rimworld-scene-composition` | no |
| `rimworld-sprite-facings` | no |
| `rimworld-start-prep` | no |
| `rimworld-world-editing` | no |
| `rimworld-xenotypes` | no |
| `telemetry` | no |
| `using-rimflow` | yes |
