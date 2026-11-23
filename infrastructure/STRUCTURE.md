# STRUCTURE.md — where things live, and why

_This file is the map of the repo. Read the map once to learn which tier a file belongs to. Then read
that tier's own `README.md`. The tier's `README.md` is authoritative about what belongs inside the tier._

**This file names homes.** A home is the folder or file where one kind of thing belongs.

- This file does not restate a tier's rules, and it carries no counts. A count copied out of `ls` drifts within hours
  and never announces that the count is wrong.
- On 2026-11-23 a run checked the paths below against the tree. The line of an absent path says that it is absent. A
  gitignored path can be absent from one clone and exist in another.
- If a path is dead, fix the path here in the same commit.

---

## Root

| Path | What it is |
|---|---|
| `CLAUDE.md` | Standing operating rules. **Pinned** (must stay at the root): Claude Code auto-loads the root copy and only the root copy. |
| `GLOBAL_CLAUDE.md` | Tracked mirror of `~/.claude/CLAUDE.md`, kept beside `CLAUDE.md` for the same reason. The mirror is out of date (`design/specs/2026-11-19-plain-english-rule-docs/census.md`). |
| `.gitignore` | The payload rules: which files git does not track. Read it before you add a binary. |
| `.claude/` | **Pinned by the harness.** Holds `hooks/` (for example `block_blanket_git_stage.py`, `set_session_title.py`), `settings.json`, `skills/` symlinks, and the gitignored `session_roles/`. |
| `skills/` | Skill sources. The directory *is* the skill. **Pinned**; see the warning below this table. |
| `design/` `src/` `deployed/` `observed/` `vendor/` `research/` `infrastructure/` | The seven tiers. |

This table is not complete. On 2026-11-23 the root also held `GUIDING_PRINCIPLES.md`, `PURPOSE.md`, `README.md`,
`LEXICON.md`, `world/`, `tickets/`, `conversations/`, `Transient/` and other entries. The other entries have no row here.

🔴 **The `skills/` pin is the dangerous one.**

- The entries in `.claude/skills/` are **relative symlinks** into `skills/`. Git stores a symlink as its literal target
  string. So a `git mv` does **not** update the symlinks.
- If someone moves `skills/`, the links break with **no error at all**. Then the harness silently stops offering those
  skills.
- A move of `skills/` needs the owner's word, or the Conductor's act with its ledger note (`design/RimMandrake/delegation_policy.md`
  §2). If it goes ahead, land the `git mv` and an `ln -sfn` for each entry in
  one commit.

---

## The seven tiers

Every tracked path is in exactly one tier, except the root entries outside the seven tiers. Each tier answers a
different question. The seven questions are the whole design: **intent, source, installed, measured, theirs, studied, ourselves.**

| Tier | Answers | Its rule lives in |
|---|---|---|
| `design/` | What do we *intend* to exist? | `design/README.md` |
| `src/` | What did we *write* for a machine to consume? | `src/README.md` |
| `deployed/` | What is the game actually *configured* with? | `deployed/README.md` |
| `observed/` | What did a *running game* actually do? | `observed/README.md` |
| `vendor/` | What did *someone else* write that we run? | `vendor/README.md` |
| `research/` | What did *someone else* write that we studied? | `research/README.md` |
| `infrastructure/` | How does the *project* run itself? | `infrastructure/agents/CHARTER.md` |

Agents cross these four boundaries by mistake:

- **`design/` vs `observed/`**: reasoning stays in `design/`. A *conclusion* that only a running game could settle is an
  observation.
- **`src/` vs `deployed/`**: we wrote the first; the second is installed. The two drift. The drift is why we track both.
- **`vendor/` vs `research/`**: the first is installed; the second is merely studied. A mod that we run is vendor. A mod
  that we read about and rejected is research.
- **`observed/` vs a script's own output**: map-synth PNGs and art-bench intermediates are artifacts of *our* tools. These
  artifacts are not a game's behaviour. The artifacts stay gitignored beside their generator in `src/`.

### The `Jawa/` vs `RimMandrake/` split

- `design/`, `src/` and `research/` carry the split. In `src/`, new work uses the three naming tiers
  (`design/NAMING_SCHEME_PLAN.md`): `src/RimMandrake/`, `src/RimStarWars/` and `src/RimUtinni/`.
- `deployed/`, `observed/` and `infrastructure/` **do not** carry the split, deliberately. An installed config, a
  measurement and a seat definition belong to something other than our reuse category.

Which tier a new thing takes: `design/NAMING_SCHEME_PLAN.md` (the owner's earlier two-way test is in
`design/RimMandrake/CLAUDE.history.md`). `design/Jawa/` and `research/Jawa/` keep their old folder name: "Jawa" is lore
text only, and no new mod folder takes it.

To promote a file later costs only a `git mv`. If a "generic" doc silently assumed Star Wars, the cost is a debugging
session.

---

## `design/` — intent

**Not here:** measurements (→ `observed/`), mod operating wisdom (→ `vendor/wisdom/`),
material we did not write (→ `research/`), **anything a machine generates**.

| Path | Holds |
|---|---|
| `design/Jawa/concept.md`, `build_plan.md` | The campaign premise, and the build order above everything else. |
| `design/Jawa/worldbuilding/` | The world, ship, xenotype, factions, biomes, droids, water and physics doctrine. |
| `design/Jawa/worldbuilding/data/` | Hand-kept data that backs those specs (`mech_inventory.json`). |
| `design/Jawa/worldbuilding/review/` | HTML registers rendered for owner review: biomes, species, mechs, anomalies. |
| `design/Jawa/worldbuilding/ship_build/` | The deck plan as machine-readable tiles, and exported layouts. |
| `design/Jawa/mods/` | Adoption, bans, cherry-pick lists, the armoury keeplist, mod config rulings. |
| `design/Jawa/art/` | Art briefs, the graphics-overhaul protocol, the salvage palette, scan and filter scripts. |
| `design/RimMandrake/` | **Method, not content**: faction authoring, save-authoring pipeline, map authoring, balance paradigm, the LLM and voice stack, `rimbridge.md`. |

---

## `src/` — source we author

**Not here:** third-party source (→ `vendor/`), build outputs and copied config
(→ `deployed/`). A script's run-artifacts stay gitignored beside the script, never in
`observed/`.

| Path | Holds |
|---|---|
| `src/README.md` | The tier rule, and the `RimMandrake.<name>` / `Jawa.<name>` naming rule for **new** work only. For a new name, `CLAUDE.md` now names `design/NAMING_SCHEME_PLAN.md`. |
| `src/DEPLOY_HOLD.txt` | The deploy interlock: the files that are held back from a deploy on purpose. Read it before `--apply`. |
| `src/Jawa/` | The old home of the campaign mods `Jawa_Patches`, `Jawa_Armoury`, `Jawa_Doctrine`, `JawaVoice`, `JawaIonWeapons`, `DesertVehicleReskin`. None of the six is here now (2026-11-23). `Jawa_Armoury` is now `src/RimStarWars/Armoury/`, and `Jawa_Doctrine` is now `src/RimUtinni/Doctrine/`. `JawaVoice`, `JawaIonWeapons` and `DesertVehicleReskin` are in `src/RimStarWars/`. `src/Jawa/` still holds `art_bench/` (gitignored `_review/`). |
| `src/RimMandrake/Utils/` | The Python tools: `deploy_custom_mods.py`, `harvest_log.py`, `refresh.py`, `check_refs.py`, `set_agent_window.sh`, `show.sh`, and the def, save and animal inventory scripts. |
| `src/RimMandrake/bridgetools/` | The RimBridge companion assembly (gitignored `artifacts/`). |
| `src/RimMandrake/mapsynth/` | Ship and map layout synthesis. The `runs/` output is gitignored. |
| `src/RimMandrake/RimDefDump/` | The def-dump mod that produces `observed/**/dumps/`. |
| `src/RimMandrake/MissingArtFixes/`, `WreckedMachines/` | Generic mods: a stranger who owns the donor mod could use them unchanged. `MissingArtFixes/` is absent (2026-11-23): commit `78b6c1fb23` retired it. |
| `src/RimMandrake/*Fix/` | Per-mod art and orientation fixes: `BlastDoorFrameAsyncFix`, `CereanManeFix`, `GravshipAstronautFix`, `KotORBandolierNorthFix`, `PhytokinBarkHeadFix`, `ResearchKitEastFix`, `SauridFrillFix`, `ToolBeltFix`. No `*Fix/` folder is here now (2026-11-23). `BlastDoorFrameAsyncFix` and `CereanManeFix` are in `src/RimStarWars/StarWarsPatches/Source/`. `KotORBandolierNorthFix` is in `src/RimStarWars/`. `GravshipAstronautFix`, `PhytokinBarkHeadFix`, `ResearchKitEastFix` and `ToolBeltFix` are in `src/RimMandrake/MandrakePatches/Source/`. `SauridFrillFix` has no folder in `src/`. |
| ~~`src/RimMandrake/JawaSeaShaper/`~~ | ⛔ DEAD. Owner ruled 2026-08-19: all in-game worldgen hooks are stripped. The route is the live bridge; see `ASHKARR_WORLD_DEFINITION.md` §12. The directory is DELETED from the repo, from the game's Mods folder and from `ModsConfig.xml`. Do not recreate it. |

---

## `deployed/` — what the install is configured with

**Not here:** source (→ `src/`), third-party source (→ `vendor/`), anything a running
game produced (→ `observed/`).

| Path | Holds |
|---|---|
| `deployed/config/` | Copied game config, stamped and diffable: `ModsConfig.*.xml` snapshots and per-mod `Mod_<id>_<Name>.*.xml` settings. |

⏳ **`deployed/mods/` and `deployed/MODLIST.md` DO NOT EXIST.**

- The charter of the folder (`deployed/README.md`) describes the two.
- The modlist needs `harvest_log.py --emit-modlist`.
- Do not cite either one as though it exists.

---

## `observed/` — what a running game did

**Not here:** tool run-artifacts (→ beside their generator in `src/`), copied game config
(→ `deployed/config/`).

- Small records and READMEs of a stamp (dated folder) are tracked.
- Saves, def dumps, `Player.log` and screenshots are gitignored and stay on disk.

| Path | Holds |
|---|---|
| `observed/2026-08-13/dumps/` | 🔴 **The current generated-data home, not a snapshot.** The def-name and mod manifests every offline validator joins against. This path is absent from the tree and from the bench clone (2026-11-23). `CLAUDE.md` names `observed/inventory/DefDump_OFFICIAL/` as the only design target; that path is gitignored, and is not in this clone or the bench clone either. |
| `observed/<date>/<subject>/` | Captures of one experiment: a `README.md`, and the artefacts that one run produced. |
| `observed/LIVE.md` | Facts you would otherwise need a running game to learn. Published by CHECK, a retired seat. |

⚠️ **Judge a directory here by its inbound references, never by how old its stamp looks.**

- An audit on the date alone deletes live data.

---

## `vendor/` — Steam content that is not ours

**Not here:** our patches against their mods (→ `src/`), candidates we have not adopted
(→ `research/`). We track *that* we have a payload, and which version. We never track the bytes.

| Path | Holds |
|---|---|
| `vendor/mod_sources/` | Third-party mod source. **Gitignored, and it stays that way.** |
| `vendor/salvage/` | Salvaged stray game assemblies, stamped by date. |
| `vendor/wisdom/` | Ours, but *about their mod*: `benign_log_errors.md` (read §0 first), `def_override_clusters.md`, `Factory_lore.md`, `cqf_quest_types_explainer.md`. |

---

## `research/` — material we did not author

**Not here:** content installed in the game (→ `vendor/`), what *we* intend (→ `design/`).
Payloads are gitignored; **the teardown is the work product.** A teardown is our written study of the payload.

| Path | Holds |
|---|---|
| `research/Jawa/` | Star Wars reference: the visual dossier and species scale atlas (PDF), the ingredients inventory. |
| `research/RimMandrake/hand_authored_maps/` | Downloaded study maps. The `.rws`/`.zip`/binaries are gitignored; the teardown is committed. |
| `research/RimMandrake/reference/`, `inspiration/` | Format and technique references, visual inspiration. |
| `research/RimMandrake/samuel_streamer_study/` | Another creator's campaign, torn down for technique. |
| `research/RimMandrake/installed_packageids.json` | The packageId index that the tools join against. |

---

## `infrastructure/` — how the project runs itself

**Not here:** anything about the campaign (→ `design/`), findings about the game
(→ `observed/`). **No `Jawa/`/`RimMandrake/` split**: coordination is singular.

### Slow-moving rules

| Path | Holds |
|---|---|
| `infrastructure/STRUCTURE.md` | This file. |
| `infrastructure/agents/CHARTER.md` | The whole process rulebook since 2026-08-27 (redesign #4: the fourth redesign of the seats. The first three each removed a coordination channel: peer chat, queue hand-edits, the CHECK seat's re-read loop). `POLICY.md` is a supersession stub. |
| `infrastructure/agents/<WINDOW>.md` | One charter per window: `CONDUCTOR.md`. The workshop file was folded into it on 2026-11-04. The retired seat files are stubs. |
| `infrastructure/REFRESH.md` | What to re-run after the mod list changes. |
| `infrastructure/archive/` | Superseded narrative kept only for *why*: `context.md`. Never current state. `context.md` is absent (2026-11-23). |
| `infrastructure/output/` | Reports **still being read**: audits, options papers, plans. Evidence, never doctrine. |

### The live-state spine — `infrastructure/state/`

`infrastructure/state/` is the moving half. Test each file with this question: *would a reader be wrong tomorrow if
they trusted this?*

- A rule is durable.
- A queue is meant to be consumed.

| Path | Holds |
|---|---|
| `infrastructure/state/V1_CHAIN.md` | 🔴 A record of what v1 was planned to hold, in the order that the engine forces. It is not a gate. Open work is in the mod's folder or on the one list (`CLAUDE.md` §Mods keep their own state). |
| `infrastructure/state/items/` | Live item prose. `items/closed/` holds terminal items (done, dropped or superseded). `infrastructure/state/handoffs/` holds reboot handoffs (2026-09-19). |
| `infrastructure/state/items/COLD_LOAD_RUN_SHEET_*.md` | The run sheet for the next game load, a normal queue item since 2026-08-27. The two hand-kept run-sheet files are deleted. The open folder holds none now; four are in `items/closed/` (2026-11-23). |
| `infrastructure/state/OWNER_DECISIONS.md` | Every question only the owner can answer, and their rulings. |
| `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` | A record of the Configure Factions page when the one fixed world was set up by hand. No worldgen feature exists (`CLAUDE.md`). |
| `design/V2_DREAMS.md` | Deferred `[v2]` bodies, kept intact. Append-only; every seat may write to it directly. |
| `infrastructure/state/TEST_PLAN.md` | How deployed material gets proved in-game. A retired seat wrote it. `load_session.py` still cites it. |
| game state | One `game` event on the ledger, measured or owner-announced (`./game`). The old `status/game.json` stamp and its directory are gone. |
| `infrastructure/state/queue/<SEAT>.md` | Rendered views of a seat's queue (gitignored; `rimflow queue <SEAT>` renders one on read), plus the hand-written `HUMAN`. File work with `rimflow file --for <SEAT>`. |

### The Conductor's window and the helpers it launches — since 2026-11-13

- **The Conductor (seat key `BENCH`).** The first retired split is the 2026-08-14 names. The next is the four seats
  DECIDE/BUILD/CHECK/REP.
- The last retired split is BENCH · FOUNDRY (2026-08-27 to 2026-11-02).
- Legacy items keep their old owners in the ledger.
- The Windows Terminal profiles set the window. The manual path is
  `./src/RimMandrake/Utils/set_agent_window.sh <WINDOW>`, which refuses the retired FOUNDRY.

| Who | Role | Its question |
|---|---|---|
| `BENCH` | the Conductor, with the owner | what does he need done, decided, or seen right now? |
| helpers | launched by the Conductor in the Maturation Pipeline (`src/RimMandrake/rimflow/detached_helper.py`) | does it exist, does it pass, and is it closed? |

---

## `skills/` — loadable procedure

**Charter: `skills/README.md`.** The charter holds these rules:

- how a skill is wired and edited, where its lessons and evidence go, and which skills are registered;
- the `SKILL.md` / `references/` / `scripts/` split;
- the enforced caps (500-line body, 1024-char description).

Archives are gitignored build outputs. At hand-off, rebuild them with
`python3 src/RimMandrake/Utils/package_skill.py --all`.

The directory is the source. The `<name>.skill` zips beside it are untracked packaging artifacts.

**Which skill to load when:** `skills/BY_WORK.md` and `skills/README.md`, not this file.

`efficient-subagents` ·
`generating-rimworld-sprites` · `gravship-layout` · `rimbridge` ·
`rimworld-debug-testing` · `rimworld-deploy` · `rimworld-load-round` ·
`rimworld-modding` · `rimworld-savegame` · `rimworld-start-prep`

These ten are not the whole roster. The roster is `skills/README.md`. `efficient-subagents` moved to MandrakeWorkflows
(commit `41eebdb659`).

The index of earned lessons is `skills/rimworld-modding/references/traps.md`. The index routes to
topic files. Open the topic file that matches what you are about to do.

---

## Three cross-tier rules you will hit today

**Writing a file in `src/` is not deploying it.**

- The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>`. Nothing syncs that folder from
  this tree.
- First plan with `src/RimMandrake/Utils/deploy_custom_mods.py`. Then run `--apply --mod <Name>`.
- A bare `--apply` pushes every mod in the tree, another seat's half-finished work included.
- The procedure is in `skills/rimworld-deploy/SKILL.md`.

**Track the manifest, never the payload.**

- Payloads are saves, def dumps, `Player.log`, screenshots, downloaded `.rws` maps, `vendor/mod_sources/`. All are
  gitignored, and all are still on disk.
- **Git never forgets, so the rule is about refusing the *next* payload**, not about the last one.
- Never delete a payload "for size". Such a delete buys nothing.
- Never commit a file over ~50 MB. One oversized file blocks every seat's push.

**One working tree, five seats.**

- An older layout had five seats in one tree. Now each seat has its own clone, and a helper works in the clone that its
  brief names (`CLAUDE.md` §Git).
- A window and its subagents still share one working tree. So the rules below stay.

- Before you edit a shared doc, `git status` it.
- Commit **explicit paths only**. Never use `git add -A`, `git add .`, or `git commit -a`.
- Before you commit, read `git diff --cached --stat`.
- The hook `.claude/hooks/block_blanket_git_stage.py` enforces the explicit paths.
- ⚠️ `git commit <path>` records the **working tree** at that path, not your index. A peer's uncommitted edit to the
  same file rides along.

---

## Keeping this file true

**A manifest is the one document that cannot be maintained by reading documents.**

Diff this file against the tree. The diff takes about a minute:

```bash
find /mnt/d/Luke/dev/RimMandrake -maxdepth 2 -type d -not -path '*/.git*'
ls /mnt/d/Luke/dev/RimMandrake/*/README.md    # every tier states its own rule
```

**A new top-level directory, a new root file, or a new `infrastructure/state/`
entry belongs here in the same commit.**

- Everything else in the repo announces itself. A missing entry on a map does not.
- A tier's deeper internals are the problem of that tier's own README. Do not mirror those internals here. If you do,
  the copy drifts. Then this file starts to lie about the tree that it exists to describe.
