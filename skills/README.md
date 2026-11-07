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
it the same. `python3 skills/validate_skills.py` re-measures the set (2026-10-11: 35 skill
dirs; 34 wired into this repo plus `review-sheets` linked in from outside it).

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
  `infrastructure/state/facts/history/<topic>.md`. A skill whose repo keeps a record folder (`artisan/`, `relentless/` in
  MandrakeWorkflows) uses that instead.
- The active file points at it once. Everything else is in git.
- **Every learned fact stays in an active file.** "Nothing learned is dropped for space" still holds. Before removing a *claim*
  as redundant, prove it implied or duplicated, by the two-blind-arms method in `efficient-subagents` if doubtful.
- A skill's `description` fires it. Change one only with `skill-creator`'s trigger evals.
- When a project skill's lesson would be true with RimWorld removed, it belongs in MandrakeWorkflows, with a thin layer here.

## Skills that live OUTSIDE this repo

General skills live in `~/dev/MandrakeWorkflows/skills/` (`D:\Luke\dev\MandrakeWorkflows\skills\`) or their own repos, linked
into `~/.claude/skills/` for every project; `~/dev/Lodestar/claude/skills.md` is the cross-machine table. These include
`efficient-subagents`, `deciding-and-superseding`, `frozen-artifacts`, `verify-before-you-escalate`, `agent-fanout-research`,
`calibrating-binary-formats`, `artisan`, `artisan-head`, `artisan-judge`, `relentless-pipeline`, `measuring-large-artifacts`,
`review-sheets` and `confident-wrong-numbers`. The roster below reads `skills/` and **cannot see them**; fix one in its own repo
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
| `relentless` | Operate, read, stop, debug or work inside the Relentless Pipeline (src/RimMandrake/rimflow/relentless.py, rm-relentless.timer… |
| `rimbridge` | Drive a live RimWorld from outside via the RimBridgeServer GABP bridge and its JawaBench companion - author the planet, author… |
| `rimbridge-companion` | Write, build, deploy and prove new [Tool] methods in the JawaBench companion DLL so the RimBridge bridge can do something it… |
| `rimflow-operations` | Operate the multi-account Claude quota system - check each account's level (weekly vs 5-hour cap, percent left, reset time… |
| `rimworld-art-evaluation` | Automated evaluation of RimMandrake game art — creatures (walkers, swimmers, flyers, catch items), plants, and machines with… |
| `rimworld-artisan` | The RimMandrake facts on top of the general artisan, artisan-head and artisan-judge skills, for Artisan loops on a RimWorld mod |
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
