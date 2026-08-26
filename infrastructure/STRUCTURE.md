# STRUCTURE.md — where things live, and why

_The map of the repo. Read it once to learn which tier a file belongs to, then read
that tier's own `README.md`, which is authoritative about what belongs inside it._

**This file names homes. It does not restate a tier's rules and it carries no
counts** — a count copied out of `ls` drifts within hours and never announces that
it is wrong. Every path below was checked against the tree; if one is dead, fix it
here in the same commit.

---

## Root

| Path | What it is |
|---|---|
| `CLAUDE.md` | Standing operating rules. **Pinned** — Claude Code auto-loads the root copy and only the root copy. |
| `GLOBAL_CLAUDE.md` | Tracked mirror of `~/.claude/CLAUDE.md`, kept beside it for the same reason. |
| `.gitignore` | The payload rules. Read it before adding a binary. |
| `.claude/` | **Pinned by the harness.** `hooks/` (`block_blanket_git_stage.py`, `set_session_title.py`), `settings.json`, `skills/` symlinks, gitignored `session_roles/`. |
| `skills/` | Skill sources — the directory *is* the skill. **Pinned**; see the warning below. |
| `design/` `src/` `deployed/` `observed/` `vendor/` `research/` `infrastructure/` | The seven tiers. |

🔴 **The `skills/` pin is the dangerous one.** Five entries in `.claude/skills/` are
**relative symlinks** into it. Git stores a symlink as its literal target string, so
a `git mv` does **not** update them — the links break with **no error at all** and
the harness silently stops offering those skills. Moving `skills/` is gated on the
owner; if that gate opens, the `git mv` and the five `ln -sfn` land in one commit.

---

## The seven tiers

Every tracked path is in exactly one. The questions are different, and that is the
whole design: **intent, source, installed, measured, theirs, studied, ourselves.**

| Tier | Answers | Its rule lives in |
|---|---|---|
| `design/` | What do we *intend* to exist? | `design/README.md` |
| `src/` | What did we *write* for a machine to consume? | `src/README.md` |
| `deployed/` | What is the game actually *configured* with? | `deployed/README.md` |
| `observed/` | What did a *running game* actually do? | `observed/README.md` |
| `vendor/` | What did *someone else* write that we run? | `vendor/README.md` |
| `research/` | What did *someone else* write that we studied? | `research/README.md` |
| `infrastructure/` | How does the *project* run itself? | `infrastructure/README.md` |

The four boundaries crossed by mistake:

- **`design/` vs `observed/`** — reasoning stays in design; a *conclusion* only a
  running game could settle is an observation.
- **`src/` vs `deployed/`** — we wrote it vs it is installed. They drift, and the
  drift is the point of tracking both.
- **`vendor/` vs `research/`** — installed vs merely studied. A mod we run is
  vendor; a mod we read about and rejected is research.
- **`observed/` vs a script's own output** — map-synth PNGs and art-bench
  intermediates are *our* tool's artifacts, not a game's behaviour. They stay
  gitignored beside their generator in `src/`.

### The `Jawa/` vs `RimMandrake/` split

`design/`, `src/` and `research/` carry it. `deployed/`, `observed/` and
`infrastructure/` **do not**, deliberately — an installed config, a measurement and
a seat definition belong to something other than our reuse category.

> **The owner's promotion test:** *"Am I likely to want this in a totally unrelated
> playthrough, or will I have to fundamentally remake it — not just reconfigure
> it?"* **Reconfigure → `RimMandrake/`. Remake → `Jawa/`.**

⚠️ **When unsure, `Jawa/`.** Promoting later is a `git mv`; discovering that a
"generic" doc silently assumed Star Wars is a debugging session.

---

## `design/` — intent

**Not:** measurements (→ `observed/`), mod operating wisdom (→ `vendor/wisdom/`),
material we did not write (→ `research/`), **anything a machine generates**.

| Path | Holds |
|---|---|
| `design/Jawa/concept.md`, `build_plan.md` | The campaign premise and the build order above everything else. |
| `design/Jawa/worldbuilding/` | The world, ship, xenotype, factions, biomes, droids, water and physics doctrine. |
| `design/Jawa/worldbuilding/data/` | Hand-kept data backing those specs (`mech_inventory.json`). |
| `design/Jawa/worldbuilding/review/` | HTML registers rendered for owner review — biomes, species, mechs, anomalies. |
| `design/Jawa/worldbuilding/ship_build/` | The deck plan as machine-readable tiles and exported layouts. |
| `design/Jawa/mods/` | Adoption, bans, cherry-pick lists, the armoury keeplist, mod config rulings. |
| `design/Jawa/art/` | Art briefs, the graphics-overhaul protocol, the salvage palette, scan/filter scripts. |
| `design/RimMandrake/` | **Method, not content** — faction authoring, save-authoring pipeline, map authoring, balance paradigm, the LLM/voice stack, `rimbridge.md`. |

---

## `src/` — source we author

**Not:** third-party source (→ `vendor/`), build outputs and copied config
(→ `deployed/`). A script's run-artifacts stay gitignored beside it, never in
`observed/`.

| Path | Holds |
|---|---|
| `src/README.md` | The tier rule and the `RimMandrake.<name>` / `Jawa.<name>` naming rule for **new** work only. |
| `src/DEPLOY_HOLD.txt` | The deploy interlock — read it before `--apply`. |
| `src/Jawa/` | Campaign mods: `Jawa_Patches`, `Jawa_Armoury`, `Jawa_Doctrine`, `JawaVoice`, `JawaIonWeapons`, `DesertVehicleReskin`, plus `art_bench/` (gitignored `_review/`). |
| `src/RimMandrake/Utils/` | The Python tooling — `deploy_custom_mods.py`, `harvest_log.py`, `refresh.py`, `check_refs.py`, `set_agent_window.sh`, `show.sh`, def/save/animal inventory scripts. |
| `src/RimMandrake/bridgetools/` | The RimBridge companion assembly (gitignored `artifacts/`). |
| `src/RimMandrake/mapsynth/` | Ship and map layout synthesis; `runs/` output is gitignored. |
| `src/RimMandrake/RimDefDump/` | The def-dump mod that produces `observed/**/dumps/`. |
| `src/RimMandrake/MissingArtFixes/`, `WreckedMachines/` | Generic mods — a stranger owning the donor mod could use them unchanged. |
| `src/RimMandrake/*Fix/` | Per-mod art and orientation fixes: `BlastDoorFrameAsyncFix`, `CereanManeFix`, `GravshipAstronautFix`, `KotORBandolierNorthFix`, `MSEDroidFix`, `PhytokinBarkHeadFix`, `ResearchKitEastFix`, `SauridFrillFix`, `ToolBeltFix`. |
| ~~`src/RimMandrake/JawaSeaShaper/`~~ | ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. The directory is DELETED from the repo, from the game's Mods folder and from `ModsConfig.xml`. Do not recreate it. |

---

## `deployed/` — what the install is configured with

**Not:** source (→ `src/`), third-party source (→ `vendor/`), anything a running
game produced (→ `observed/`).

| Path | Holds |
|---|---|
| `deployed/config/` | Copied game config, stamped and diffable — `ModsConfig.*.xml` snapshots and per-mod `Mod_<id>_<Name>.*.xml` settings. |

⏳ **`deployed/mods/` and `deployed/MODLIST.md` DO NOT EXIST.** The charter
describes them; the modlist needs `harvest_log.py --emit-modlist`. Do not cite
either as though it exists.

---

## `observed/` — what a running game did

**Not:** tool run-artifacts (→ beside their generator in `src/`), copied game config
(→ `deployed/config/`). Per stamp, **only `MANIFEST.json` is tracked**; saves, def
dumps, `Player.log` and screenshots are gitignored and stay on disk.

| Path | Holds |
|---|---|
| `observed/2026-08-13/dumps/` | 🔴 **The current generated-data home, not a snapshot.** The def-name and mod manifests every offline validator joins against. |
| `observed/<date>/<subject>/` | Per-experiment captures — a `README.md` and the artefacts one run produced. |
| `observed/LIVE.md` | Facts you would otherwise need a running game to learn. Published by CHECK. |

⚠️ **Judge a directory here by its inbound references, never by how old its stamp
looks.** Auditing on the date alone deletes live data.

---

## `vendor/` — Steam content that is not ours

**Not:** our patches against their mods (→ `src/`), candidates we have not adopted
(→ `research/`). We track *that* we have a payload and which version — never bytes.

| Path | Holds |
|---|---|
| `vendor/mod_sources/` | Third-party mod source. **Gitignored, ~430 MB, and it stays that way.** |
| `vendor/salvage/` | Salvaged stray game assemblies, stamped by date. |
| `vendor/wisdom/` | Ours, but *about their mod* — `benign_log_errors.md` (read §0 first), `def_override_clusters.md`, `Factory_lore.md`, `cqf_quest_types_explainer.md`. |

---

## `research/` — material we did not author

**Not:** content installed in the game (→ `vendor/`), what *we* intend (→ `design/`).
Payloads are gitignored; **the teardown is the work product.**

| Path | Holds |
|---|---|
| `research/Jawa/` | Star Wars reference — the visual dossier and species scale atlas (PDF), the ingredients inventory. |
| `research/RimMandrake/hand_authored_maps/` | Downloaded study maps; `.rws`/`.zip`/binaries gitignored, the teardown committed. |
| `research/RimMandrake/reference/`, `inspiration/` | Format and technique references, visual inspiration. |
| `research/RimMandrake/samuel_streamer_study/` | Another creator's campaign torn down for technique. |
| `research/RimMandrake/installed_packageids.json` | The packageId index the tooling joins against. |

---

## `infrastructure/` — how the project runs itself

**Not:** anything about the campaign (→ `design/`), findings about the game
(→ `observed/`). **No `Jawa/`/`RimMandrake/` split** — coordination is singular.

### Slow-moving rules

| Path | Holds |
|---|---|
| `infrastructure/README.md` | The tier rule, and the rules-vs-state line. |
| `infrastructure/STRUCTURE.md` | This file. |
| `infrastructure/agents/POLICY.md` | Shared seat rules — how you work, the queue channel, the item contract, the modes. |
| `infrastructure/agents/<SEAT>.md` | One charter per seat: `DECIDE.md`, `BUILD.md`, `CHECK.md`, `REP.md`. |
| `infrastructure/DOC_BUDGET.md` | Doc-count policy and how a written instruction rots. |
| `infrastructure/REFRESH.md` | What to re-run after the mod list changes. |
| `infrastructure/archive/` | Superseded narrative kept only for *why* — `context.md`. Never current state. |
| `infrastructure/output/` | Reports **still being read** — audits, options papers, plans. Evidence, never doctrine. |

### The live-state spine — `infrastructure/state/`

The moving half. The test is *would a reader be wrong tomorrow if they trusted
this?* A rule is durable; a queue is meant to be consumed.

| Path | Holds |
|---|---|
| `infrastructure/state/V1_CHAIN.md` | 🔴 What ships in v1, in the order the engine forces. **Check it before queueing anything.** The authority on the v1/v2 line. |
| `infrastructure/state/NEXT_RELOAD.md` | The run sheet for the next game load — work that needs the game running. |
| `infrastructure/state/OWNER_DECISIONS.md` | Every question only the owner can answer, and their rulings. |
| `infrastructure/state/EXPECTED_FAILURES_next_load.md` | Expected-failure signatures, written **before** a load so triage is judgeable. |
| `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` | The Configure Factions page, box by box, for world creation. |
| `design/V2_DREAMS.md` | Deferred `[v2]` bodies, kept intact. Append-only; every seat may write to it directly. |
| `infrastructure/state/TEST_PLAN.md` | How deployed material gets proved in-game. Written by a retired seat; still cited by `load_session.py`. |
| `infrastructure/state/status/game.json` | The game-state stamp. ⚠️ `<SEAT>.json` and `say.py` are GONE (2026-08-22): nobody wrote them, the board showed week-old sentences as current. What a seat is doing is a `seat` event on the ledger — `rimflow seat`. |
| `infrastructure/state/queue/<SEAT>.md` | 🔴 **The filing destination.** `DECIDE`, `BUILD`, `CHECK`, plus `HUMAN` for the owner. You own your own; file at the next seat's. |

### The four seats

**DECIDE · BUILD · CHECK · REP.** The earlier seat names
were retired 2026-08-14. Name your window first thing:
`./src/RimMandrake/Utils/set_agent_window.sh <SEAT>`.

| Seat | Role | Its question |
|---|---|---|
| `DECIDE` | scope and spec | what exactly ships, and in what order? |
| `BUILD` | mod author and artist | does it exist, and does it pass offline? |
| `CHECK` | live-systems engineer | did it actually work in the running game? |
| `REP` | the human's interface | what does the owner need to see or answer? |

---

## `skills/` — loadable procedure

**Charter: `skills/README.md`** — what earns a skill versus a traps entry, the
`SKILL.md` / `references/` / `scripts/` split, and the enforced caps (500-line body,
1024-char description). Archives are gitignored build outputs: rebuild with
`python3 src/RimMandrake/Utils/package_skill.py --all` at hand-off.

The directory is the source; `<name>.skill` zips beside it are untracked packaging
artifacts. **Which skill to load when is `CLAUDE.md`'s job**, not this file's.

`editing-images` · `efficient-subagents` · `generating-images` ·
`generating-rimworld-sprites` · `gravship-layout` · `rimbridge` ·
`rimworld-debug-testing` · `rimworld-deploy` · `rimworld-load-round` ·
`rimworld-modding` · `rimworld-savegame` · `rimworld-start-prep`

Earned lessons index: `skills/rimworld-modding/references/traps.md` — it routes to
topic files; open the one matching what you are about to do.

---

## Three cross-tier rules you will hit today

**Writing a file in `src/` is not deploying it.** The game reads
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>` and nothing
syncs it from this tree. Plan first with
`src/RimMandrake/Utils/deploy_custom_mods.py`, then `--apply --mod <Name>`; a bare
`--apply` pushes every mod in the tree including another seat's half-finished work.
Procedure: `skills/rimworld-deploy/SKILL.md`.

**Track the manifest, never the payload.** Saves, def dumps, `Player.log`,
screenshots, downloaded `.rws` maps, `vendor/mod_sources/` — all gitignored, all
still on disk. **Git never forgets, so the rule is about refusing the *next*
payload**, not cleaning up the last. Never delete one "for size"; it buys nothing.
Never commit a file over ~50 MB — one oversized file blocks every seat's push.

**One working tree, five seats.** `git status` a shared doc before editing it.
Commit **explicit paths only** — never `git add -A`, `git add .`, or `git commit -a`
— and read `git diff --cached --stat` before committing. Enforced by
`.claude/hooks/block_blanket_git_stage.py`. ⚠️ `git commit <path>` records the
**working tree** at that path, not your index — a peer's uncommitted edit to the
same file rides along.

---

## Keeping this file true

**A manifest is the one document that cannot be maintained by reading documents.**
Diff it against the tree; it takes about a minute:

```bash
find /mnt/d/Luke/dev/Rimworld -maxdepth 2 -type d -not -path '*/.git*'
ls /mnt/d/Luke/dev/Rimworld/*/README.md    # every tier states its own rule
```

**A new top-level directory, a new root file, or a new `infrastructure/state/`
entry belongs here in the same commit.** Everything else in the repo announces
itself; a missing entry on a map does not. A tier's deeper internals are its own
README's problem — do not mirror them here, or the copy will drift and this file
will start lying about the tree it exists to describe.
