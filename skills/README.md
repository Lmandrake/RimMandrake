# Skills

A registered skill loads itself when its `description` matches the task. An unregistered skill does not load itself: you
read it by path (§Not registered (read by path)). Read a skill when you are about to do the thing that it names. Do not
read it before.

## 🔴 A skill is INVISIBLE until it is wired — and `skills/` is not where Claude looks

You write a skill in `skills/<name>/SKILL.md`. **Claude Code finds a skill only at `.claude/skills/<name>`.** That entry
is a symlink to `skills/<name>`. A skill is wired, or registered, when that symlink works.

If a skill has no symlink, the skill loads for nobody and triggers on nothing. The missing symlink has no symptom. The
work that the skill holds never happens.

```
ln -s ../../skills/<name> .claude/skills/<name>            # a skill in THIS repo
ln -s /mnt/d/Luke/dev/<name> .claude/skills/<name>         # one that lives OUTSIDE it
```

- **Link a skill outside this repo by ABSOLUTE path.** A relative path resolves inside the checkout. So the link dangles
  (points at nothing) as soon as the skill is not there.
- **Enforced since 2026-08-22** by the hook `.claude/hooks/warn_skill_unwired.py`. The hook warns when you write or commit
  a `SKILL.md` that has no symlink that works. The hook never blocks. The hook prints the first command above for that skill.
- A symlink that dangles is as invisible as no symlink. The hook treats the two the same.
- Each skill in the table "Not registered (read by path)" below is unwired on purpose. The hook stays quiet for it.
- `python3 src/RimMandrake/Utils/selftest_skills_registered_or_listed.py` checks the set. Each skill folder is either
  linked or in that table, never both, never neither.
- `python3 skills/validate_skills.py` checks the content of each skill folder (front matter, pointers to reference files,
  `jawa/` tool names). This tool does not check the links.

## Editing a skill

- **To edit `skills/<name>/` IS to install the skill.** For a wired skill, the symlink means that the next session loads
  the new text.
- Edit skills only in fresh-context curation sessions. Such a session starts new, for the edit of a skill. Never edit a
  skill at the end of a session's context.
- Until such a session, each lesson goes in its own file in `infrastructure/state/lessons/`
  (`src/RimMandrake/Utils/lessons.py add`).
- Any window maintains any skill.
- `package_skill.py` builds a `.skill` zip (gitignored). Build the zip only to upload the skill to claude.ai. Claude Code
  does not load skills from the zip.

## Lessons stay; evidence moves to a history file

The active files of a skill are all its files except its history file. If its repo uses a record folder instead, the
files in that folder are not active files.
The active files hold the lessons, in plain words. Each lesson stays as strong as it was given. Four things leave the
active files: narration, incident stories, dates and repeated copies. Owner, 2026-11-07: *"move evidence into pointer
history files while keeping the lessons themselves in the active files. Provenance is for git."* One convention applies
everywhere:

- Put evidence that still matters in `references/history.md` beside the skill. For a project-level fact file, put such
  evidence in `infrastructure/state/facts/history/<topic>.md`. If the skill's repo keeps its own record folder, use that
  folder instead.
- The active file points at the history file once. Everything else is in git.
- **Every learned fact stays in an active file.** "Nothing learned is dropped for space" still holds.
- Before you remove a *claim* as redundant, prove that another claim implies it or repeats it. If you are in doubt, use
  the two-blind-arms method in `efficient-subagents`.
- A skill's `description` fires the skill. Change a `description` only with `skill-creator`'s trigger evals.
- Ask if a lesson of a project skill stays true with RimWorld removed. If yes, the lesson belongs in MandrakeWorkflows,
  with a thin layer here.

## Skills that live OUTSIDE this repo

- General skills live in `~/dev/MandrakeWorkflows/skills/` (`D:\Luke\dev\MandrakeWorkflows\skills\`) or in their own
  repos.
- `~/dev/Lodestar/claude/skills.md` is the cross-machine table. The table declares which of these skills have a link in
  `~/.claude/skills/`. A skill with a link there loads for every project, unless the settings of that project hide the
  skill.
- A machine can also hold a link that the table does not declare. Archmagi holds many. So a skill that loads here can be
  absent on another machine.
- The general skills include `efficient-subagents`, `deciding-and-superseding`, `frozen-artifacts`,
  `verify-before-you-escalate`, `agent-fanout-research`, `calibrating-binary-formats`, `measuring-large-artifacts`,
  `review-sheets` and `confident-wrong-numbers`.
- The loop skills `artisan`, `artisan-head`, `artisan-judge`, `whittle` and `relentless-pipeline` are retired here.
  `.claude/settings.json` hides them.
- The roster below reads `skills/` and **cannot see the general skills**.
- Fix a general skill in its own repo, and push there. A queue item here never reaches that repo.

<!-- doc_roster:BEGIN — generated, do not hand-edit -->
| skill | when it loads |
|---|---|
| _(generated from each skill's own `description` — the text that actually decides when it loads, so no second copy can disagree)_ | |
| `clone-landing-commits` | How to get a commit from a RimMandrake seat clone (/home/mandrake/rm/bench) onto origin/main and keep the clone level afterwards… |
| `generating-rimworld-sprites` | Produces RimWorld-ready sprite art that matches an existing reference asset — correct canvas, real alpha, silhouette inside the… |
| `gravship-layout` | Author, save and load RimWorld gravship layouts (ShipLayoutDefV2) as XML — write a ship directly with no map, no build and no… |
| `live-debugging-proof-harness` | Write, run and read a LIVE proof of a RimWorld mod through the bridge — proof_all.py, proof_hose.py, a northstar/ runner… |
| `northstar-validation` | Run a mod's north-star suites live without the harness eating the sitting — the bland world (generated per game, or the saved… |
| `reading-rimworld-graphics` | Finding and reading RimWorld texture assets from disk — loose PNGs, Unity AssetBundles, and the base game's resources.assets — so… |
| `rimbridge` | Drive a live RimWorld from outside via the RimBridgeServer GABP bridge and its JawaBench companion - author the planet, author… |
| `rimbridge-companion` | Write, build, deploy and prove new [Tool] methods in the JawaBench companion DLL so the RimBridge bridge can do something it… |
| `rimflow-operations` | Operate the multi-account Claude quota system - check each account's level (weekly vs 5-hour cap, percent left, reset time… |
| `rimworld-art-evaluation` | Automated evaluation of RimMandrake game art — creatures (walkers, swimmers, flyers, catch items), plants, and machines with… |
| `rimworld-canon-references` | Grade Star Wars creature, species and droid work against design/RimStarWars/canon_references/ — 137 entries whose sourced canon… |
| `rimworld-content-moderation` | Deciding what content stays in a RimWorld campaign out of a large mod stack — building contact sheets of real sprites straight… |
| `rimworld-crew-and-nemesis-events` | Design and build RimWorld 1.6 events about PEOPLE for a small fixed crew — who may join (a stranger, a castaway, a relative, a… |
| `rimworld-custom-incidents` | Build our own RimWorld 1.6 incidents and storyteller pacing — an IncidentDef plus IncidentWorker, a follow-up through the… |
| `rimworld-debug-testing` | Testing anything in RimWorld without spending a cold load — starting and destroying throwaway dev quicktest colonies through the… |
| `rimworld-deploy` | Writing a file is not deploying it — RimWorld loads C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>, never… |
| `rimworld-ideoligion` | Design, author, validate and judge RimWorld ideoligions |
| `rimworld-layout-layers` | Assess a RimWorld structure on its INDEPENDENT LAYERS - power circuits, mod pipe networks (Helixien gas, chemfuel, deepchem… |
| `rimworld-live-review` | Stage a live RimWorld scene through the bridge so a human can LOOK at it and judge it — a biome's plant density and colour, a… |
| `rimworld-load-round` | How to spend a RimWorld cold load — and how to stop needing one |
| `rimworld-modding` | Author, patch, validate and debug RimWorld mods — XML PatchOperations, custom Defs, C#/Harmony assemblies, def inheritance that… |
| `rimworld-quests` | Design, author, validate and debug RimWorld quests |
| `rimworld-review-sheets` | Use before building, serving, refreshing, enacting or retiring any RimMandrake review sheet, and before showing the owner ANY… |
| `rimworld-savegame` | Reading, grepping and editing a RimWorld `.rws` savegame — plain XML plus base64/raw-DEFLATE map grids of 2-byte def shortHashes |
| `rimworld-scenario-building` | Authoring a RimWorld scenario and the game-creation settings around it — ScenarioDefs, .rsc scenario files, ScenParts, Custom… |
| `rimworld-scene-composition` | Make a scattered/scenic site (a ruin, a bone field, a wreck, a camp) read as ONE authored place at a glance instead of a props… |
| `rimworld-sprite-facings` | The facing half of generating-rimworld-sprites |
| `rimworld-start-prep` | Getting the mod list and load order into the state you actually intend BEFORE RimWorld launches — the three uncoordinated writers… |
| `rimworld-world-editing` | Author RimWorld's PLANET from the bridge - tiles, biomes, elevation, rivers, roads, mutators, landmarks, named regions and… |
| `rimworld-xenotypes` | Authoring, moving, spawning and debugging RimWorld xenotypes and the genes that give them a face |
| `telemetry` | Query recorded history before re-measuring anything about the game, a live test, the bridge, host memory, disks or the art… |
| `using-rimflow` | Use before ANY rimflow / src/RimMandrake/rimflow/cli.py call — file, claim, start, close, drop, supersede, note, next, seat… |
<!-- doc_roster:END -->

## Not registered (read by path)

Owner, 2026-11-19: *"most of the time I invoke things quite manually in my text when I want a skill (hence they don't need to be registered... it knows where to look already)"*.

- When we made this table, nobody had invoked these skills in 30 days. So this project does not load their
  descriptions into every session. Each skill folder stays.
- **Read a skill's SKILL.md by path when you are about to do what its line says.**
- `skills/BY_WORK.md` says which skills go with which kind of work. Use that page when you write a brief.
- To undo one row, run the command in its last column. Then delete the row here, and set the skill to `yes` in
  `skills/BY_WORK.md`. The selftests refuse a half-done undo.
- To undo the `review-sheets` row (a skill outside this repo), run its command and delete the row only. No selftest
  checks that undo.

| skill | SKILL.md | read it when | undo |
|---|---|---|---|
| `gravship-layout` | `D:\Luke\dev\RimMandrake\skills\gravship-layout\SKILL.md` | writing, saving, loading or inspecting a gravship layout (ShipLayoutDefV2) as XML | `ln -s ../../skills/gravship-layout .claude/skills/gravship-layout` |
| `reading-rimworld-graphics` | `D:\Luke\dev\RimMandrake\skills\reading-rimworld-graphics\SKILL.md` | finding or extracting a RimWorld texture on disk or in an AssetBundle | `ln -s ../../skills/reading-rimworld-graphics .claude/skills/reading-rimworld-graphics` |
| `review-sheets` | `D:\Luke\dev\MandrakeWorkflows\skills\review-sheets\SKILL.md` | building an HTML sheet where a human keeps, cuts or ranks many items (this row is about the project link only: a machine-wide link in `~/.claude/skills/` loads this description in every session) | `ln -s /mnt/d/Luke/dev/MandrakeWorkflows/skills/review-sheets .claude/skills/review-sheets` |
| `rimworld-art-evaluation` | `D:\Luke\dev\RimMandrake\skills\rimworld-art-evaluation\SKILL.md` | judging game art or a regen before it reaches the owner | `ln -s ../../skills/rimworld-art-evaluation .claude/skills/rimworld-art-evaluation` |
| `rimworld-canon-references` | `D:\Luke\dev\RimMandrake\skills\rimworld-canon-references\SKILL.md` | grading Star Wars creature, species or droid work against the canon library | `ln -s ../../skills/rimworld-canon-references .claude/skills/rimworld-canon-references` |
| `rimworld-content-moderation` | `D:\Luke\dev\RimMandrake\skills\rimworld-content-moderation\SKILL.md` | deciding which content from a large mod stack stays in the campaign | `ln -s ../../skills/rimworld-content-moderation .claude/skills/rimworld-content-moderation` |
| `rimworld-crew-and-nemesis-events` | `D:\Luke\dev\RimMandrake\skills\rimworld-crew-and-nemesis-events\SKILL.md` | designing events about who joins, is taken or returns to a fixed crew | `ln -s ../../skills/rimworld-crew-and-nemesis-events .claude/skills/rimworld-crew-and-nemesis-events` |
| `rimworld-custom-incidents` | `D:\Luke\dev\RimMandrake\skills\rimworld-custom-incidents\SKILL.md` | building an IncidentDef, IncidentWorker or storyteller pacing | `ln -s ../../skills/rimworld-custom-incidents .claude/skills/rimworld-custom-incidents` |
| `rimworld-debug-testing` | `D:\Luke\dev\RimMandrake\skills\rimworld-debug-testing\SKILL.md` | testing through a throwaway quicktest colony instead of a cold load | `ln -s ../../skills/rimworld-debug-testing .claude/skills/rimworld-debug-testing` |
| `rimworld-ideoligion` | `D:\Luke\dev\RimMandrake\skills\rimworld-ideoligion\SKILL.md` | designing or authoring ideoligions (IdeoPresetDef, FactionDef ideo block) | `ln -s ../../skills/rimworld-ideoligion .claude/skills/rimworld-ideoligion` |
| `rimworld-layout-layers` | `D:\Luke\dev\RimMandrake\skills\rimworld-layout-layers\SKILL.md` | assessing a structure by power, pipe, roof and floor layers | `ln -s ../../skills/rimworld-layout-layers .claude/skills/rimworld-layout-layers` |
| `rimworld-modding` | `D:\Luke\dev\RimMandrake\skills\rimworld-modding\SKILL.md` | authoring, patching or debugging any mod Def, XML patch, C# or Harmony, or reading Player.log | `ln -s ../../skills/rimworld-modding .claude/skills/rimworld-modding` |
| `rimworld-quests` | `D:\Luke\dev\RimMandrake\skills\rimworld-quests\SKILL.md` | designing or debugging a QuestScriptDef | `ln -s ../../skills/rimworld-quests .claude/skills/rimworld-quests` |
| `rimworld-savegame` | `D:\Luke\dev\RimMandrake\skills\rimworld-savegame\SKILL.md` | reading, grepping or editing a .rws savegame | `ln -s ../../skills/rimworld-savegame .claude/skills/rimworld-savegame` |
| `rimworld-scenario-building` | `D:\Luke\dev\RimMandrake\skills\rimworld-scenario-building\SKILL.md` | authoring a scenario, game-creation settings or storyteller | `ln -s ../../skills/rimworld-scenario-building .claude/skills/rimworld-scenario-building` |
| `rimworld-scene-composition` | `D:\Luke\dev\RimMandrake\skills\rimworld-scene-composition\SKILL.md` | making a scattered site (ruin, camp, wreck) read as one authored place | `ln -s ../../skills/rimworld-scene-composition .claude/skills/rimworld-scene-composition` |
| `rimworld-sprite-facings` | `D:\Luke\dev\RimMandrake\skills\rimworld-sprite-facings\SKILL.md` | any north/south/east/west facing, mirror or flip-book question on sprites | `ln -s ../../skills/rimworld-sprite-facings .claude/skills/rimworld-sprite-facings` |
| `rimworld-start-prep` | `D:\Luke\dev\RimMandrake\skills\rimworld-start-prep\SKILL.md` | getting the mod list and load order right before RimWorld launches | `ln -s ../../skills/rimworld-start-prep .claude/skills/rimworld-start-prep` |
| `rimworld-world-editing` | `D:\Luke\dev\RimMandrake\skills\rimworld-world-editing\SKILL.md` | editing the planet (tiles, biomes, rivers, roads, landmarks) from the bridge | `ln -s ../../skills/rimworld-world-editing .claude/skills/rimworld-world-editing` |
| `rimworld-xenotypes` | `D:\Luke\dev\RimMandrake\skills\rimworld-xenotypes\SKILL.md` | authoring, spawning or debugging xenotypes and genes | `ln -s ../../skills/rimworld-xenotypes .claude/skills/rimworld-xenotypes` |
| `northstar-validation` | `D:\Luke\dev\RimMandrake\skills\northstar-validation\SKILL.md` | running a mod's north-star suites live, so that the test harness does not use up the sitting (was never linked) | `ln -s ../../skills/northstar-validation .claude/skills/northstar-validation` |
| `telemetry` | `D:\Luke\dev\RimMandrake\skills\telemetry\SKILL.md` | querying recorded history before re-measuring the game, bridge, disks or art pipeline | `ln -s ../../skills/telemetry .claude/skills/telemetry` |
