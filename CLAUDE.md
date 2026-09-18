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
- **A cold load is ~15 minutes on the full list; a quicktest map is ~90 s.** Never
  "restart and see". *(MEASURED 2026-09-07: launch 15:12 → `Bridge token:` 15:27 on
  **599** active mods. Supersedes the long-standing ~25 min figure. Caveat: that was
  the second launch of a session, so a first launch after a reboot may run slower.)*
- **`ModsConfig.xml` is the live mod list**, at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
  Read it for the active count, never a number written in a doc.
- **Never guess a defName, field, or namespace.** RimSage (`mcp__rimsage__*`), the
  def, the About.xml, or `measure` — and 🔴 **a number about a large artifact comes
  from `measure`, never from a scan** (`grep`/`strings`/`wc` return plausible wrong
  counts; `.claude/hooks/block_blind_scan.py` refuses and names the instrument).
  `0` means measured zero; ignorance answers `UNMEASURED`. The skill lives at
  `~/.claude/skills/measuring-large-artifacts`.
- 🔴 **RimSage answers on the Windows Desktop ONLY — on the Mac laptop it has never
  connected** (MEASURED 2026-09-16: five timed-out session logs 2026-09-02→09-16,
  `mcp.rimsage.com` TCP-dead while general egress is fine, no `mcp__rimsage__*` tool in
  the toolset at all, no cached decompiled tree). So on the laptop an **engine-internals
  question is UNMEASURABLE** — say so rather than reasoning from a doc, and never brief a
  subagent to "use RimSage" there: it costs a whole run to rediscover. Still fine offline
  on either machine: the def dump (`measure`, `refresh.py`) for DEFS, and reading our own
  source. ⚠️ **Several docs assert engine facts that trace to an earlier agent's prose,
  not a decompiler** — `About.xml`'s "vanilla ignition already works on any flammable
  terrain", and `Flood.noPossibleCell` being private with no accessor. Do not launder
  those into measurements.
- 🔴 **A backgrounded `Agent` dies at 600 s of silence and leaves NOTHING on disk.** Three died
  that way 2026-09-17, all mid-read before their first write, all leaving a clean tree — so each
  cost a whole run rather than being truncated; the two that survived streamed output at 385 s
  and 575 s. **Brief every writing subagent to create its output file as a skeleton FIRST and
  fill it section by section** — a file write emits progress and persists partial work. A long
  read-then-write brief is the shape that trips it.
- 🔴 **`northstar.parse()` returns a DICT.** `getattr(w, "must_show")` yields `None` → `len()` 0,
  so all four VALIDATED walks read as "0 bars" — an alarming wrong number that looks like a
  catastrophic finding. Use `w["must_show"]`. 🔑 A count that is conveniently *or* alarmingly
  round is a query bug until proven otherwise, and the alarming direction is the one you will
  believe without checking.
- 🔴 **Never scan `ModsConfig.xml`.** `grep -c '<li>'` returns **48** where the real active count
  is **631** — it counts lines containing the tag, and that file puts many elements on one line.
  Parse it (`ET.parse(p).find("activeMods")`). Snapshots are in
  `infrastructure/state/modlists/`; the live file is a Windows path **unreachable from the Mac**,
  so a laptop claim about the LIVE list is UNMEASURABLE and must say so (2026-09-17).
- 🔴 **`handoff.py` cannot tell two BENCH windows apart.** It REFUSES on "BRIDGE still held by
  BENCH" even when the hold belongs to the *other* window's live session, because both sign as
  `BENCH`. ⛔ Do not release it to satisfy the gate — that breaks a live game. `--force` records
  it as open, which is the correct exit, and the handoff must name whose hold it was.
- 🔴 **An existence test is not an identity test, and a fixed line number is not a field.**
  `[ -e src/RimMandrake/Pits ]` passes while that folder holds only `__pycache__` — the mod
  merged into FlowWorks at `cade628c1`, yet its checklist is **VALIDATED with 12 binding bars**
  against nothing. Test `$dir/About/About.xml`. Likewise a sweep reading `subject:` from **line
  2** reported zero failures across 78 walks while missing the only file still broken, because
  `AtmosphericBase.md` carries it on line 3. Read the first matching line, never an index. Both
  checkers returned a confident clean bill of health (2026-09-17).
- 🔴 **`modcheck run <Mod>` REWRITES the live `ModsConfig.xml`** — it calls `modlist_swap` and
  swaps to MINIMAL. It reads like a query verb and is a Charter expensive-list action. On the
  Mac it dies on the Windows path; on the Desktop it swaps his list unasked (2026-09-17).
- 🔴 **A texture glob on `*south*` reads the MASK as often as the art.** `X_southm.png` is the
  colour mask, saturated across ~99% of its pixels by convention (MEASURED 259,344 of 262,144),
  so `glob(...)[0]` in filesystem order decides whether a head appears to carry baked colour —
  it inverted 4 of 7 decisions in one pass, and the tell was male vs female Cathar reading 253
  vs 0 on structurally identical files. **Measure `_south.png` alone** (2026-09-17).
- 🔴 **The north-star system cannot GREEN anything: `shows=` appears in 0 of 54 mod
  `validation.py` files** (RE-MEASURED 2026-09-17), so every VALIDATED mod's must-show bars are
  bound-and-uncovered and a `modcheck run` against one returns REFUSED before the game is
  consulted. Authoring more bars adds refusals, not coverage; `NORTH_STAR_PIT_PILOT_1` is the
  falsification test and has never run. 🔴 **And the 81 walk findings are NOT rot:**
  `doctor` derives a walk's mod from the walk's BASENAME, never from its `subject:` line, so its
  24 ORPHAN_WALKs and 10 SUBJECT_COLLISIONs are ONE phenomenon — **34 of 78 walks are deliberate
  per-feature walks sharing a live mod's subject** (MEASURED 2026-09-18). Of the 33 failing
  walks, 25 have a fully live subject and the defect is a stale id inside a STEP, and **0 are
  genuinely orphaned**. ⛔ Never "fix" a walk on an ORPHAN_WALK finding alone, and ⛔ do not
  rebuild the 43-row decision sheet: the owner ruled it was never his to adjudicate
  (*"this doesnt feel like a sheet I should be asked"*) and its data was wrong besides — a walk's
  subject packageId is backticked in 28 walks, BARE in 34 and absent in 16, so a backtick-only
  regex reads None for 50 of 78. `DETERMINISM_ASSESSMENT.md` §11a is the account; the walk-model
  ruling (`feature:` key vs collapsing 34 walks into 10) is still OWED BY HIM. ✅ **The "modcheck status reads a stored field" bug is
  FIXED** (`fa27e1cab`, `status.check_or_orphaned` + `doctor.py`, same day as the claim above was
  first written) — live-checked 2026-09-17: `modcheck status` now correctly prints `FlowWorks
  STALE   [stored: GREEN]` and `Pits ORPHANED (no such mod folder)   [stored: GREEN]`, re-deriving
  every row rather than trusting the stored field. The dead `FluidCanals` key is gone too
  (`b110a7a2d`, `rename-key`/`forget-key`). Don't re-open this as a live defect without
  re-measuring; the stored field only ever appears now as a `[stored: ...]` drift annotation.
- **A doc can describe defects that were fixed before the doc was written.**
  `liquids_framework_design.md` (2026-09-13) blocked all engine work on three flood
  defects fixed 2026-09-02 and closed at `747b0025`, and an open item was still telling
  FOUNDRY to re-fix them. Check the code and the ledger before believing any doc's
  "engine status" — and check whether an open item is asking for work already done.
- 🔴 **A gate cited by NAME outlives the item it names — check the item's state.**
  `NAMING_SCHEME_EXECUTION_1` closed **2026-08-31** at `54a8e28d` on the owner's word,
  yet ~20 live docs still said "do not rename ahead of it" 16 days later, which is why
  FlowWorks (named by ruling 20) still ships as `fluidcanals`. Owner: *"That file may be
  VERY old… do not accept stale info."* Sweep: `STALE_RENAME_GATE_SWEEP_1`.
- **North stars: `FlowWorks`, `Graffiti`, `Pits` and `WreckedMachines` are VALIDATED** —
  MEASURED 2026-09-17 through the parser: 13+3 / 8+2 / 11+1 / 12+2 = **44 bars**, every
  recorded hash MATCHing. ⛔ Do not casually edit their `## north star` sections: the hash
  covers the **whole section including explanatory prose**, so correcting a stale caveat
  reverts the checklist to DRAFT and the mod quietly stops being refused (hit live
  2026-09-16). 🔴 **Owner ruled 2026-09-17 that this stays as it is** — verbatim: *"Change
  no code — you just re-validate when prose is corrected."* Bar-scoped hashing is
  **declined, not deferred** (`NORTHSTAR_HASH_SCOPE_1` dropped), so the remedy for false
  text in a hashed section is: correct it, then re-validate on his word, same sitting.
  ⛔ Never leave false text standing to protect a hash — that trade is now ruled against.
  🔑 Therefore **write only state-independent prose inside that section** — never "binds
  nothing until validated", which is false the moment it is. And `modcheck/cli.py
  validate <Mod>` refuses unless BOTH `state:` and `validated-hash:` header lines exist
  (blank is fine), and since 2026-09-17 refuses a section parsing to **zero bars** — a
  misformatted section used to record VALIDATED against an empty checklist, binding
  nothing; omit `--owner-said` for a dry run that writes nothing.
- **A number you brief a subagent with will come back to you.** A census reported "2 of
  137 canon entries ruled"; the real figure is **25**. Two later agents measured 25 and
  both explicitly refused to adjust to the briefed figure — the correct behaviour. When
  two subagents disagree on a number, measure it yourself before it becomes a fact.
- **A patch that matches nothing logs nothing.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match.
- **Dumps and harvests decay** (owner, 2026-08-27): trust one only after its
  fingerprint matches the live mod set; the frozen `official` dump is the sole
  design target (`GAME_STATE_WORKFLOW.md`).

## In-game LLM access is the Claude Code CLI, never a hosted API key — owner, 2026-09-05

Every mod that calls out to an LLM (the Oracle, the raid-redesigner, any future
consumer) does it by shelling out to **`claude -p "<prompt>"`** (Claude Code in
non-interactive mode) as a subprocess, not by making an HTTP call to an
OpenAI-compatible endpoint. Owner, verbatim: *"Claude Code in non-interactive
mode (`claude -p "..."`) authenticates via your claude.ai login and can be
called from a shell script without any API key."*

- ⛔ **Supersedes `OracleClient`'s original HTTP/OpenAI-compatible design**
  (`design/RimMandrake/llm_ingame_wiring_spec.md` §1, `src/RimMandrake/Oracle`'s
  `OracleHttpClient`) — no base URL, no model string, no API key field, no local
  Ollama fallback. The two laws in that spec (text/menu authority only; the
  game is whole with the LLM absent) and the async/timeout/kill-switch
  threading shape are UNCHANGED — only the transport (HTTP → subprocess) moves.
- The game process (Mono/Unity on the owner's Windows machine) launches `claude
  -p` via `System.Diagnostics.Process`, same off-tick `Task`-based async
  pattern already built, reading stdout instead of an HTTP response body.
  Whoever rebuilds `OracleHttpClient` against this: verify the exact
  invocation and output shape against a real local `claude -p` call before
  wiring it — do not assume flags or JSON structure from this note.
- **New environment dependency this creates**: the owner's machine must have
  Claude Code installed and logged in for any consumer to work at all — this
  is now a fact about his machine, not a config value in Mod Settings.
- Affects `ORACLE_EXPERIMENT_SPIKE_1` (client rewrite owed) and
  `PLOT_MECHANISM_MODS_WAVE_1` Part 1 (the raid-redesigner's Oracle calls ride
  whatever `OracleClient` becomes).

## A pit is a SUPERDEEP cell, not a building — owner, 2026-09-17

*"I'm not really sure a pit is any different than a deep canal."* Ruled and fully
specified, **nothing built**: `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`.
A pit is depth 4 on the D/F primitive rulings 18/19 already established, so the
fitting concept collapses to **spikes alone** (oil and poison are FluidDefs; the
oubliette is CUT), an enclosed superdeep area is a room that becomes a prison room
once a bed is in it, `capture down`/`convert down` happen from the lip because
nobody who enters can leave, and TEMPERATURE is the softening mechanism.

🔴 **The ITEM is the authority, not the spec.**
`design/RimMandrake/pit_superdeep_collapse_spec.md` (1127 lines) was written BEFORE
three rounds of rulings that changed ten of its answers; the item lists the revisions
it is owed. ⛔ Do not read the spec and act on it without reading the item first —
you would build the version he rejected. Door family is its own item,
`FLOWWORKS_DOOR_FAMILY_1`: **two** stuffable defs, never the three he described and
then talked himself out of.

## Shipping names are three-tier — owner, 2026-08-30

Every NEW packageId, defName, C# namespace and mod folder uses the tier
grammar in `design/NAMING_SCHEME_PLAN.md`: **RimMandrake** (any RimWorld game) /
**RimStarWars** (any Star Wars scenario) / **RimUtinni** (this campaign) —
packageId `mandrake.<tier>.<modname>`, prefixes `RM_`/`RSW_`/`RUT_`,
C# namespaces nested `RimMandrake[.StarWars|.Utinni].<Mod>` (never bare
`RimStarWars`/`RimUtinni`). "Jawa" is lore text only. Dev tooling is exempt.

🔴 **The migration is DONE — there is no rename gate any more.**
`NAMING_SCHEME_EXECUTION_1` closed **2026-08-31** at `54a8e28d` on the owner's
own word (*"Deploy the full rename."*), which is why the mod set already carries
`mandrake.rm.*` / `mandrake.rsw.*`. So when a mod is RENAMED after that date, the
rename is simply owed work — execute it, do not defer it to a closed item. Three
live docs were still citing that item as a reason to wait 16 days after it
closed, which is how `FlowWorks` (named by ruling 20, 2026-09-16) kept shipping
as `fluidcanals`. If you find another such citation, delete it.

## Every mod ships superb Mod Settings — owner, 2026-09-12

Every mod we ship carries a real settings screen: on/off per major
feature/mechanic, tuning where a number is the experience, defaults = shipped
behavior, all-off degrades gracefully, and worldgen-affecting toggles labeled
as such. Biome-kit mechanics are feature-gated so they can be enabled in other
biomes without the biome. Spec + retrofit of existing mods:
`MOD_OPTIONS_RETROFIT_1`. Applies to every future mod, no exceptions.

## Queue items are NAMED, not numbered — owner, 2026-08-20

`THREE_UPPER_SNAKE_WORDS_#`, guessable cold: `SANDSTORM_WEATHER_TUNING_1`. No new
`B*`/`C*`/`D*`/`W*` IDs; legacy IDs are never renamed and are always cited with
their title attached — `B58 (the dead Jawa pawnkind)`, never bare.

## Inaccurate material is DELETED, not superseded-in-place — owner, 2026-09-09

*"Simply remove offending inaccurate material, don't leave it in and supersede
it."* Wrong or dead content is removed outright — git is the provenance — and
every inbound reference is fixed in the same change. A one-line successor
pointer at the top is only for content that MOVED somewhere else (owner,
2026-08-30); it is never a banner over wrong content left in place. Entries
state what IS, never what used to be. "Not my file" does not discharge it.
Single-source only what a generator can enforce; where only discipline enforces
a duplicate, write a pointer instead.

## Git

Explicit paths, never `git add -A`/`.`/`-a` (hook-enforced). Push immediately after
committing; rejected push → `git pull --rebase`, never `--force`. Never a file over
~50 MB.

🔴 **The pathspec goes on the `commit`, not just the `add`** — `git commit <paths> -F -`
(hook-enforced). Four threads share this working tree *and* its index, so a bare
`git commit -m` sweeps a peer's staged files into your commit under your message.
⚠️ The hook is `PreToolUse`, so it refuses a **compound** command whole: if you chain a
file write to a commit, the write never happens either. Keep writes and commits separate.

🔴 **A subagent that runs `git reset --hard HEAD` destroys THIS window's staged work** — one
tree, one index. It ate 3 staged files 2026-09-18. Recovery: `git add` writes blobs before any
commit, so `git fsck --unreachable` + `git cat-file -p <sha>` restores them byte-exact. Brief
every subagent that `reset --hard`, `checkout --` and `stash` on shared paths are FORBIDDEN and
that a conflict is reported back, never cleared — "leave those files alone" reads as licence to
clear them another way.

🔴 **`git rebase --continue` saying "You must edit all merge conflicts" while `git status` says
all conflicts are fixed means the WORKTREE is dirty, not that a conflict remains.** Usually
self-inflicted: `code_review_status.py`'s `_trigger_health_rebuild` spawns the health publisher,
so every `prune`/`list` re-dirties 5 tracked artifacts. Commit them and the rebase finishes
(MIN_INTERVAL is 900 s, so it holds long enough).

⚠️ **A `cd` in one Bash call PERSISTS into later calls.** `modcheck` needs
`python3 -m modcheck.cli <verb>` from `src/RimMandrake/Utils`, and after that `cd` a git query
or a glob makes `infrastructure/` look DELETED. Use absolute paths, or `cd` back.

## Code isn't clean until a review says so

**Every file in this repo is dirty by default — including files nobody has
touched today.** The only way a file is CLEAN is a recorded entry in
`infrastructure/state/CODE_REVIEW_STATUS.json` (owned by
`code_review_status.py`, never hand-edited) whose recorded content hash is
byte-identical to the file on disk. No entry, or any byte changed — DIRTY.
(Content-based, not commit-based: a rewrite reverted to identical bytes is
CLEAN; a path moved by `git mv` has no entry at the new path — review 2026-09-06.)

```
python3 src/RimMandrake/Utils/code_review_status.py check <path>...   CLEAN/DIRTY, with the reason if dirty
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

**Art is judged against the canon library, and canon is the target** (owner, 2026-09-15).
`design/RimStarWars/canon_references/` holds 137 entries — 45 creatures, 69 species, 23 droid
chassis — each with sourced canon, a visual brief written against real reference images, a
`## Must show` checklist and `## Engine limits`. **An empty `## ruling` means canon stands
unopposed, not that the entry is unusable**; he rules only on ambiguity, deliberate
departures and contested regens. `AGENT_BRIEF.md` there is the operating doc. 🔴 Keep the
three defect classes apart — a **missing gene** is edited in the def, an **engine limit**
needs new art or more mask channels, and a **rig limit** (Ithorian neck, Kaminoan
proportions, Muun body, Lasat legs) cannot be fixed at all, so art chasing it is waste.
⛔ **Cosmetic changes need his permission first** — they can break animated faces.

```
src/                    mods, defs, C#, art            FOUNDRY owns
design/                 campaign specs (Utinni)        the owner's, via BENCH
skills/                 tooling + how-to               curated in fresh-context passes
infrastructure/state/   ledger, items, facts/, V1.md   written only through rimflow
Transient/              output to LOOK AT, then bin    tracked+pushed, ~14 days
```

**Transient rule**: a human reads it once → `Transient/`; a program reads it →
`/tmp`, never the repo; anyone-later → the repo, committed outside `Transient/`.
Tracked and pushed so the owner can review it from another machine (his ruling
2026-09-01, recorded in `.gitignore`), but shelf life is ~14 days: never the
only copy of anything, and never a committed doc citing a file inside it.
`rimflow sweep --transient` lists by age; it never deletes.

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
python3 src/RimMandrake/Utils/run_selftests.py      run every selftest before a commit — parallel,
                                                     explicit N/N, never silently truncated
python3 src/RimMandrake/Utils/system_screenshot.py <out.bmp>   OS-level desktop capture (ctypes,
                                                     DPI-aware) — not the game's own F10/bridge
                                                     screenshot. Owner ruling 2026-09-09: always
                                                     OK to take one when in doubt of live state —
                                                     no asking first. Convert with PIL if needed.
python3 src/RimMandrake/Utils/system_click.py <x> <y>          OS-level click at real screen
                                                     coordinates (from a system_screenshot.py
                                                     capture, scaled to its actual resolution) —
                                                     for a Windows dialog a bridge call can't
                                                     reach (UAC/firewall prompts, native error
                                                     boxes). Same DPI-awareness as above.
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
  `rimworld/save_game` has silently written the CURRENT slot instead of `saveName`.
  Confirm a NEW file appeared and no existing one changed size — never trust the
  path it hands back.
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

`src/RimMandrake/Utils/broadcast.py` is the owner's tool; the game-state relay above is its only carve-out.
🔴 Run commands yourself — a `!`-prefixed paste handed to the owner is the defect
(hook-enforced on Stop); anything he must LOOK at comes with the complete native path.

## Skills

Roster: `skills/README.md`. Most reached for: `rimworld-modding` · `rimworld-deploy`
· `rimworld-load-round` · `rimbridge` · `efficient-subagents` ·
`generating-rimworld-sprites`. Lessons go to
`infrastructure/state/LESSONS_INBOX.md` (one line); skills are edited only in
fresh-context curation sessions.
