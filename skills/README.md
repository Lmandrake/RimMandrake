# Skills

Each loads itself when its `description` matches the task. Read one when you are
about to do the thing it names — not before.

## 🔴 A skill is INVISIBLE until it is wired — and `skills/` is not where Claude looks

Authoring is `skills/<name>/SKILL.md`. **Discovery is `.claude/skills/<name>`, a symlink
back into it.** A skill with no symlink loads for nobody, triggers on nothing, and has no
symptom — the work it encodes simply never happens.

```
ln -s ../../skills/<name> .claude/skills/<name>            # a skill in THIS repo
ln -s /mnt/d/Luke/dev/<name> .claude/skills/<name>         # one that lives OUTSIDE it
```

⚠️ **A skill outside this repo must be linked by ABSOLUTE path.** The relative form
resolves inside the checkout and dangles the moment the skill is not there.

✅ **Enforced since 2026-08-22**: `.claude/hooks/warn_skill_unwired.py` warns (never
blocks) when a `SKILL.md` is written or committed with no working symlink, and hands over
that exact command. ⚠️ A **dangling** symlink is as invisible as none, and the hook treats
it the same. A skill listed in the "Not registered (read by path)" table below is unwired on purpose
(the hook stays quiet for it). `python3 skills/validate_skills.py` re-measures the set.

## Editing a skill

**Editing `skills/<name>/` IS installing it** — the symlink means the next session loads
the new text. Skills are edited only in fresh-context curation sessions; lessons land one
file each in `infrastructure/state/lessons/` (`src/RimMandrake/Utils/lessons.py add`) until
then. Any window maintains any skill. `package_skill.py` builds a `.skill` zip
(gitignored) only for uploading to claude.ai — it is not how Claude Code loads skills.

## Lessons stay; evidence moves to a history file

A skill's active files hold the lessons, in plain words, each as strong as it was given. What leaves them is narration,
incident stories, dates and repeated copies (owner, 2026-11-07: *"move evidence into pointer history files while keeping
the lessons themselves in the active files. Provenance is for git."*). One convention everywhere:

- Evidence that still matters goes to `references/history.md` beside the skill. For a project-level fact file it goes to
  `infrastructure/state/facts/history/<topic>.md`. A skill whose repo keeps its own record folder uses that instead.
- The active file points at it once. Everything else is in git.
- **Every learned fact stays in an active file.** "Nothing learned is dropped for space" still holds. Before removing a *claim*
  as redundant, prove it implied or duplicated, by the two-blind-arms method in `efficient-subagents` if doubtful.
- A skill's `description` fires it. Change one only with `skill-creator`'s trigger evals.
- When a project skill's lesson would be true with RimWorld removed, it belongs in MandrakeWorkflows, with a thin layer here.

## Skills that live OUTSIDE this repo

General skills live in `~/dev/MandrakeWorkflows/skills/` (`D:\Luke\dev\MandrakeWorkflows\skills\`) or their own repos, linked
into `~/.claude/skills/` for every project; `~/dev/Lodestar/claude/skills.md` is the cross-machine table. These include
`efficient-subagents`, `deciding-and-superseding`, `frozen-artifacts`, `verify-before-you-escalate`, `agent-fanout-research`,
`calibrating-binary-formats`, `measuring-large-artifacts`, `review-sheets` and `confident-wrong-numbers` (the loop
skills `artisan`, `artisan-head`, `artisan-judge`, `whittle` and `relentless-pipeline` are retired here, hidden by `.claude/settings.json`). The roster below reads `skills/` and **cannot see them**; fix one in its own repo
and push there — a queue item here never reaches it.

<!-- doc_roster:BEGIN — generated, do not hand-edit -->
| skill | when it loads |
|---|---|
| _(generated from each skill's own `description` — the text that actually decides when it loads, so no second copy can disagree)_ | |
| `clone-landing-commits` | How to get a commit from a RimMandrake seat clone (/home/mandrake/rm/bench) onto origin/main and keep the clone level afterwards… |
| `editing-images` | Modifies an existing image with a text prompt by attaching it to Codex's built-in $imagegen tool, then verifies what actually… |
| `generating-images` | Generates raster images from a text prompt by driving the Codex CLI's built-in $imagegen tool, then retrieves, inspects and… |
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

Owner, 2026-11-19: *"most of the time I invoke things quite manually in my text when I want a skill (hence they don't need to be registered... it knows where to look already)"*. Each skill below is never-invoked in 30 days, so its `description` is not loaded into every session; the folder stays. **Read its SKILL.md by path when you are about to do what the line says.** Which skills go with which kind of work, for a brief: `skills/BY_WORK.md`. Undo for one: the command in the last column.

| skill | SKILL.md | read it when | undo |
|---|---|---|---|
| `editing-images` | `D:\Luke\dev\RimMandrake\skills\editing-images\SKILL.md` | editing an existing image with Codex $imagegen and checking what changed | `ln -s ../../skills/editing-images .claude/skills/editing-images` |
| `generating-images` | `D:\Luke\dev\RimMandrake\skills\generating-images\SKILL.md` | making a new raster image or transparent PNG with Codex $imagegen | `ln -s ../../skills/generating-images .claude/skills/generating-images` |
| `gravship-layout` | `D:\Luke\dev\RimMandrake\skills\gravship-layout\SKILL.md` | writing, saving, loading or inspecting a gravship layout (ShipLayoutDefV2) as XML | `ln -s ../../skills/gravship-layout .claude/skills/gravship-layout` |
| `reading-rimworld-graphics` | `D:\Luke\dev\RimMandrake\skills\reading-rimworld-graphics\SKILL.md` | finding or extracting a RimWorld texture on disk or in an AssetBundle | `ln -s ../../skills/reading-rimworld-graphics .claude/skills/reading-rimworld-graphics` |
| `review-sheets` | `D:\Luke\dev\MandrakeWorkflows\skills\review-sheets\SKILL.md` | building an HTML sheet where a human keeps, cuts or ranks many items | `ln -s /mnt/d/Luke/dev/MandrakeWorkflows/skills/review-sheets .claude/skills/review-sheets` |
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
| `northstar-validation` | `D:\Luke\dev\RimMandrake\skills\northstar-validation\SKILL.md` | running a mod's north-star suites live without the harness eating the sitting (was never linked) | `ln -s ../../skills/northstar-validation .claude/skills/northstar-validation` |
| `telemetry` | `D:\Luke\dev\RimMandrake\skills\telemetry\SKILL.md` | querying recorded history before re-measuring the game, bridge, disks or art pipeline | `ln -s ../../skills/telemetry .claude/skills/telemetry` |
