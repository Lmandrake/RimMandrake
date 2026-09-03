# RimWorld 1.6 — Jawa scavenger clan on a desert world

**Read `infrastructure/agents/CHARTER.md`** — the whole process rulebook — and your
own window file: `infrastructure/agents/BENCH.md` (with the owner) or
`infrastructure/agents/FOUNDRY.md` (autonomous queue). Game cycle:
`infrastructure/GAME_STATE_WORKFLOW.md`. *(The four-seat POLICY.md system was
superseded 2026-08-27 — redesign #4, `Fable_Review/`.)*

**Models — owner, 2026-09-02: BENCH orchestrates on Opus, backgrounds DESIGN work
to a Fable subagent, and steps every other subagent down to the cheapest tier that
still has a catcher.** The ladder lives in `infrastructure/agents/Agent_Policy.md`
and nowhere else; never restate a model choice outside it.

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

## Code isn't clean until a review says so

**Every file in this repo is dirty by default — including files nobody has
touched today.** The only way a file is CLEAN is a recorded entry in
`infrastructure/state/CODE_REVIEW_STATUS.json` (owned by
`code_review_status.py`, never hand-edited) with zero commits against that
path since the recorded commit. No entry, or any commit since — DIRTY.

```
python3 src/RimMandrake/Utils/code_review_status.py check <path>...   CLEAN/DIRTY, with the commits since if dirty
python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path>  only after a full-file review finds nothing — refuses on uncommitted changes
python3 src/RimMandrake/Utils/code_review_status.py list               every recorded entry and its current state
```

- **Fixing a finding does not clean a file.** Only a full-file review returning
  zero significant findings does, recorded with `mark-clean`.
- **Diff-scoped (incremental) review is only valid once a file is CLEAN.** Before
  that first clean mark, review the whole file — never just the diff.
- A single edit after `mark-clean` makes the file DIRTY again — `check` will say
  so and name the commits.
- **Before spending a review on a file, check it is still reachable** — owner,
  2026-09-03: old scripts sit around long after they stop mattering. A Python
  file with no importer, no `python3 <it>` in any doc/hook/script, and no CLI
  entry point is a DEAD-FILE candidate; a `.cs` file dropped from the `.csproj`
  or with no live caller (reflection-registered bridge tools included — grep
  the tool-name string, not just C# call sites) is the same. Say what you
  checked. **Don't delete on a grep alone — verify, then file it** (or drop
  it, if it's plainly gone) rather than spending a full review on code nobody
  runs. A file only a human runs by hand can look unused to a naive grep and
  not be.

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
                                                     🔴 a REBOOT is yours to call, no asking
                                                     (owner 2026-09-02) — bridge free first,
                                                     then GAME_STATE_WORKFLOW.md's gates
./bridge [bench|foundry|free]                       OWNER ONLY — bare ./bridge says who has it
python3 src/RimMandrake/rimflow/cli.py …            the ledger: file/claim/close/drop/verify
node --check <file.js>                              Node 22 is installed user-local
for f in $(find src -name selftest_\*.py); do python3 "$f" || echo "FAIL $f"; done
                                                     run every fast offline selftest before a commit
```

## Options he must LOOK at ship as a savegame — owner, 2026-09-02

*"Save user review options as save games."* A screenshot shows one angle of one
thing; a save lets him walk it, zoom it, and read the tooltips. So when a pass
produces options for him to judge in-world — structures, layouts, creatures,
gear on a pawn — **build them and save the game.**

- **One map, all options** (his ruling by card), laid out on a grid with enough
  pitch that nothing overlaps, plus an item file giving the **grid key**: which
  option is at which cell.
- **Saves stay until he says delete.** Not auto-purged, not overwritten by the
  next review.
- 🔴 **Back up the Saves folder's keepers first and stat it afterwards.**
  `rimworld/save_game` honoured `saveName` on 2026-09-02 and silently wrote the
  CURRENT slot instead on 2026-08-24. Confirm a NEW file appeared and no
  existing one changed size — do not trust the path it hands back.
- ⚠️ Verify each option is actually THERE (`jawa/list_things` per slot) before
  calling it a review. A placement log's `thingsSpawned` is a NET count and goes
  negative when a build clears plants.

## The bridge is passed through one file

One window drives the live game at a time — not for ownership, for attributability.
Who holds it is in **`infrastructure/state/BRIDGE`**, one glanceable line written by
`rimflow bridge` and never by hand. It mirrors the ledger; `bridge who` re-derives it.

```
rimflow bridge who                        is it free? (also repairs the mirror)
rimflow bridge take --for "<what for>"    request it — say what for, the other window reads it
rimflow bridge release                    the moment you stop. Not at the end of the session
```

🔑 **It errs toward ALLOWING, never toward mutual lockout** (owner, 2026-09-02).
A take is refused only while the holder is provably alive — an event within 45
minutes; after that the lock is stale and the next window simply takes it, saying so.
`take --force` always works and is recorded. **Nobody is coming to tell you it freed:
if you want it, look again.** ⚠️ Do not message the other window — that channel is off.

⭐ **The owner overrides both of you with `./bridge bench|foundry|free`**, and his word
lands in the same file you already read.

`broadcast.py` is the owner's tool; the game-state relay above is its only carve-out.
🔴 Run commands yourself — a `!`-prefixed paste handed to the owner is the defect
(hook-enforced on Stop); anything he must LOOK at comes with the complete native path.

## Skills

Roster: `skills/README.md`. Most reached for: `rimworld-modding` · `rimworld-deploy`
· `rimworld-load-round` · `rimbridge` · `efficient-subagents` ·
`generating-rimworld-sprites`. Lessons go to
`infrastructure/state/LESSONS_INBOX.md` (one line); skills are edited only in
fresh-context curation sessions.
