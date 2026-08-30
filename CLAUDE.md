# RimWorld 1.6 — Jawa scavenger clan on a desert world

**Read `infrastructure/agents/CHARTER.md`** — the whole process rulebook — and your
own window file: `infrastructure/agents/BENCH.md` (with the owner) or
`infrastructure/agents/FOUNDRY.md` (autonomous queue). Model ladder:
`infrastructure/agents/Agent_Policy.md`. Game cycle:
`infrastructure/GAME_STATE_WORKFLOW.md`. *(The four-seat POLICY.md system was
superseded 2026-08-27 — redesign #4, `Fable_Review/`.)*

## 🔴 There is no worldgen feature, in any version — owner, 2026-08-15

- **OUT, permanently:** any automated or programmatic worldgen; worldgen as a
  player-facing capability. ⛔ v2 is not a parking space for it — mark such work
  dead, never deferred.
- 🔑 **Players never generate anything. They receive a savegame holding the fixed
  world** — one hand-made world, frozen, shipped. A faction, ideoligion or setting
  absent when it freezes is absent from every player's game forever.
- ⛔ **Do not build anything that produces ALTERNATIVE planets** (owner, 2026-08-18).
  No seed sweeps, no variants, no knobs that could roll a second world. ✅ Author
  THE map, judged by realism first, iterated by LOOKING (`worldview.py`); target and
  references: `design/Jawa/worldbuilding/the_one_map.md`.

## Facts you cannot guess

- **The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`,
  never this repo.** Writing a file is not deploying it.
- **A cold load is ~25 minutes; a quicktest map is ~90 s.** Never "restart and see".
- **`ModsConfig.xml` is the live mod list**, at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
  Read it for the active count, never a number written in a doc.
- **Never guess a defName, field, or namespace.** RimSage (`mcp__rimsage__*`), the
  def, the About.xml, or `measure` — and 🔴 **a number about a large artifact comes
  from `measure`, never from a scan** (`grep`/`strings`/`wc` return plausible wrong
  counts; `.claude/hooks/block_blind_scan.py` refuses and names the instrument).
  `0` means measured zero; ignorance answers `UNMEASURED`. The skill lives at
  `~/.claude/skills/measuring-large-artifacts`.
- **A patch that matches nothing logs nothing.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match.
- **Dumps and harvests decay** (owner, 2026-08-27): trust one only after its
  fingerprint matches the live mod set; the frozen `official` dump is the sole
  design target (`GAME_STATE_WORKFLOW.md`).

## Shipping names are three-tier — owner, 2026-08-30

Every NEW packageId, defName, C# namespace and mod folder uses the tier
grammar in `design/NAMING_SCHEME_PLAN.md`: **RimMandrake** (any RimWorld game) /
**RimStarWars** (any Star Wars scenario) / **RimUtinni** (this campaign) —
packageId `mandrake.<tier>.<modname>`, prefixes `RM_`/`RSW_`/`RUT_`,
C# namespaces nested `RimMandrake[.StarWars|.Utinni].<Mod>` (never bare
`RimStarWars`/`RimUtinni`). "Jawa" is lore text only. Dev tooling is exempt.
Old names migrate under NAMING_SCHEME_EXECUTION_1 — do not rename ahead of it.

## Queue items are NAMED, not numbered — owner, 2026-08-20

`THREE_UPPER_SNAKE_WORDS_#`, guessable cold: `SANDSTORM_WEATHER_TUNING_1`. No new
`B*`/`C*`/`D*`/`W*` IDs; legacy IDs are never renamed and are always cited with
their title attached — `B58 (the dead Jawa pawnkind)`, never bare.

## Superseding a doc means writing INTO the doc you superseded

One line at the top of the superseded file naming the successor — nobody reads
backwards, and provenance lives in git, nowhere else (owner, 2026-08-30):
entries state what IS, never what used to be. "Not my file" does not discharge
it. Single-source only what a generator can enforce; where only discipline
enforces a duplicate, write a pointer instead.

## Git

Explicit paths, never `git add -A`/`.`/`-a` (hook-enforced). Push immediately after
committing; rejected push → `git pull --rebase`, never `--force`. Never a file over
~50 MB.

## What is where

```
src/                    mods, defs, C#, art            FOUNDRY owns
design/                 campaign specs (Utinni)        the owner's, via BENCH
skills/                 tooling + how-to               curated in fresh-context passes
infrastructure/state/   ledger, items, facts/, V1.md   written only through rimflow
Transient/              output to LOOK AT, then bin    untracked, ~14 days
```

**Transient rule** (owner, 2026-08-27): a human reads it once → `Transient/`;
a program reads it → `/tmp`, never the repo; anyone-later → the repo, committed.
Never the only copy of anything in `Transient/`, and never a committed doc citing a
file inside it. `rimflow sweep --transient` lists by age; it never deletes.

## Tools

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name>   dry run; --apply writes
python3 src/RimMandrake/Utils/refresh.py            rebuild the offline def dump
measure count <DefType>                             one line; never a bare number
python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs ...
./src/RimMandrake/Utils/show.sh <path>              open it in Explorer
./game --said "<his words>" up|down|loading         the moment he says it; bare ./game measures
python3 src/RimMandrake/rimflow/cli.py …            the ledger: file/claim/close/drop/verify
node --check <file.js>                              Node 22 is installed user-local
```

`broadcast.py` is the owner's tool; the game-state relay above is its only carve-out.
🔴 Run commands yourself — a `!`-prefixed paste handed to the owner is the defect
(hook-enforced on Stop); anything he must LOOK at comes with the complete native path.

## Skills

Roster: `skills/README.md`. Most reached for: `rimworld-modding` · `rimworld-deploy`
· `rimworld-load-round` · `rimbridge` · `efficient-subagents` ·
`generating-rimworld-sprites`. Lessons go to
`infrastructure/state/LESSONS_INBOX.md` (one line); skills are edited only in
fresh-context curation sessions.
