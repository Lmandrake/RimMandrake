# Skills by kind of work: the SKILL.md paths to read first

Owner, 2026-11-19: *"since we're not seeming enamored of auto firing skills at the moment, it might be very important
to pass relevant debug skills to the subagents we assign to do related work, yes?"*

- Most project skills are no longer registered (`skills/README.md`, table "Not registered (read by path)"). So a helper
  never sees their descriptions. A helper reads such a skill only when its brief names the skill's path.
- **Every brief names the SKILL.md paths for its kind of work, taken from this page**
  (`src/RimMandrake/rimflow/roles/conductor.md`).
- `detached_helper.py launch` prints a WARNING for a brief that names none.
- Read a skill when you are about to do the work, not before.
- Paths in this repo are relative to the clone root (on the mirror: `D:\Luke\dev\RimMandrake\skills\...`).
- Paths that start with `~/dev/` are skills outside this repo (`D:\Luke\dev\...`). Read them by path too. Most of them
  are not registered machine-wide. `~/dev/Lodestar/claude/skills.md` says which are. A machine can also hold a link that
  `skills.md` does not declare (Archmagi does).
- The table at the end gives the registration of each skill of this repo.
- `src/RimMandrake/Utils/selftest_skills_by_work.py` refuses a skill folder that this page does not name. The selftest
  also refuses a registration column that disagrees with `.claude/skills/`.

## Live debugging and proofs
- `skills/live-debugging-proof-harness/SKILL.md`: write, run and read a live proof (`proof_all`, `validation_v2`,
  `LogTap`).
- `skills/rimworld-debug-testing/SKILL.md`: test in a throwaway quicktest colony. The skill says what a quicktest can and
  cannot prove.
- `skills/northstar-validation/SKILL.md`: run a mod's north-star suites live (the bland world, and the situational envelope of
  `modcheck run --situational`).
- `skills/telemetry/SKILL.md`: recorded history. Query the history before you measure the game, the bridge, the disks or
  the art pipeline again.
- `~/dev/MandrakeWorkflows/skills/test-pilot-sitting/SKILL.md`: the Test Pilot's method (write theories first; make
  one change at a time).

## Driving the live game over the bridge
- `skills/rimbridge/SKILL.md`: drive the live game (planet, map, pawns, weather, raids). Use it also when a call
  "succeeded" but moved nothing.
- `skills/rimbridge-companion/SKILL.md`: add a new `[Tool]` method to the JawaBench companion DLL when the bridge cannot
  do a thing.
- `skills/rimworld-live-review/SKILL.md`: stage a scene and capture it for a human to look at.
- `skills/rimworld-world-editing/SKILL.md`: edit the planet (tiles, biomes, rivers, landmarks) from the bridge.

## Deploying to the game
- `skills/rimworld-deploy/SKILL.md`: the repo is not the game's Mods folder. Plan, apply and validate a deploy.
- `skills/rimworld-start-prep/SKILL.md`: set the mod list and the load order before the game launches.

## Load rounds (a cold load, a restart)
- `skills/rimworld-load-round/SKILL.md`: spend a cold load well, or avoid it with the minimal list (13 mods on 2026-08-19,
  larger now).
- `skills/rimworld-start-prep/SKILL.md`: the three writers of the mod list (RimWorld, RimSort and Steam).

## Savegames
- `skills/rimworld-savegame/SKILL.md`: read, grep and edit a `.rws` (map grids, shortHashes, fogGrid).
- `skills/gravship-layout/SKILL.md`: gravship layouts as XML (`ShipLayoutDefV2`), with no live game.

## Modding and patches
- `skills/rimworld-modding/SKILL.md`: Defs, XML patches, C#/Harmony, inheritance, Player.log triage.
- `skills/rimworld-deploy/SKILL.md`: a file that you write is not yet deployed.
- `skills/rimbridge-companion/SKILL.md`: read it when the change is a bridge tool.

## Game content by kind
- `skills/rimworld-quests/SKILL.md`: `QuestScriptDef`s and their silent signal bugs (signal bugs that show no error).
- `skills/rimworld-custom-incidents/SKILL.md`: `IncidentDef`s, `IncidentWorker`s and storyteller pace.
- `skills/rimworld-crew-and-nemesis-events/SKILL.md`: events about who joins a small crew, whom someone takes, and
  who comes back.
- `skills/rimworld-ideoligion/SKILL.md`: ideoligions (`IdeoPresetDef`, the `FactionDef` ideo block).
- `skills/rimworld-xenotypes/SKILL.md`: xenotypes and the genes that give them a face.
- `skills/rimworld-scenario-building/SKILL.md`: scenarios, game-creation settings, storyteller.
- `skills/rimworld-content-moderation/SKILL.md`: decide which content from a large mod stack stays.

## Maps, structures and scenes
- `skills/rimworld-layout-layers/SKILL.md`: assess a structure by its power, pipe, roof and floor layers.
- `skills/rimworld-scene-composition/SKILL.md`: make a scattered site read as one authored place.
- `skills/gravship-layout/SKILL.md`: design a gravship.
- `skills/rimworld-world-editing/SKILL.md`: edit the planet.

## Art and sprites
- `skills/generating-rimworld-sprites/SKILL.md`: make game-ready sprites that match a reference (canvas, alpha,
  footprint).
- `skills/rimworld-sprite-facings/SKILL.md`: north/south/east/west facings, mirrors and flip-books.
- `~/dev/MandrakeWorkflows/skills/generating-images/SKILL.md`: make a new raster image through Codex `$imagegen`.
- `~/dev/MandrakeWorkflows/skills/editing-images/SKILL.md`: change an existing image through Codex `$imagegen`.
- `skills/reading-rimworld-graphics/SKILL.md`: find a texture on disk or in an AssetBundle.

## Judging art
- `skills/rimworld-art-evaluation/SKILL.md`: the pipeline that judges art. Opus scores first. GPT takes a second look at a
  weak score.
- `skills/rimworld-sprite-facings/SKILL.md`: decide whether each facing is right.
- `skills/rimworld-canon-references/SKILL.md`: grade Star Wars work against the canon library.

## Review sheets (a human keeps, cuts or ranks many items)
- `skills/rimworld-review-sheets/SKILL.md`: RimMandrake review sheets: pictures at true scale, and `art.py enact`.
- `~/dev/MandrakeWorkflows/skills/review-sheets/SKILL.md`: the general layer under `rimworld-review-sheets`.
- `skills/rimworld-content-moderation/SKILL.md`: make contact sheets for keep/cut calls on a mod stack.

## Landing commits
- `skills/clone-landing-commits/SKILL.md`: `./publish`, `./sync`, and a clone that reads both ahead and behind.

## The ledger (rimflow) and the accounts
- `skills/using-rimflow/SKILL.md`: every rimflow verb, the ledger shards, the provenance flags and the bridge lock.
- `skills/rimflow-operations/SKILL.md`: the quota of the Claude accounts and the plan for an account switch. The
  skill also says how to stand windows down and up.

## Measuring large files
- `~/dev/MandrakeWorkflows/skills/measuring-large-artifacts/SKILL.md`: get numbers from files that are too big to
  read.
- `~/dev/MandrakeWorkflows/skills/confident-wrong-numbers/SKILL.md`: check a count that is round, zero or alarming.
- `skills/rimworld-savegame/SKILL.md`: read it when the large file is a save.
- `skills/telemetry/SKILL.md`: when the answer is already in a record.

## Design orders (three options with tradeoffs, a GPT skeptical teardown, a merge)
- `~/dev/MandrakeWorkflows/skills/deep-design-3x2/SKILL.md`: the owner's usual design order, as one workflow. The
  steps are three real solutions, a blind GPT answer, a GPT critique, a re-measure and one merge. Then the decisions go
  back to the owner.
- `~/dev/Dispatch/skills/chatgpt-consult/SKILL.md`: how to reach GPT for the second pass.

## Writing a helper's brief
- `~/dev/MandrakeWorkflows/skills/efficient-subagents/SKILL.md`: set a helper's scope, its inputs and its bounds.
- This page. Name in the brief the paths for the helper's kind of work.

## Writing a checker (a selftest, a gate, a judge)
- `~/dev/MandrakeWorkflows/skills/mutate-your-checker/SKILL.md`: watch the checker go red on a planted fault
  first.

## Every skill folder in this repo, and whether it is registered

`yes` means that the skill has a link under `.claude/skills/`, so its description loads by itself. `no` means that you
read the skill by path only.

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
