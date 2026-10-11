# Standing owner rulings and process detail — full text

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

## North-star validation state

- 🔴 **Validation state is never written as prose: `modcheck floor --all` measures it.** 🔴 **And the 81 walk findings are NOT rot:**
  `doctor` derives a walk's mod from the walk's BASENAME, never from its `subject:` line, so its
  24 ORPHAN_WALKs and 10 SUBJECT_COLLISIONs are ONE phenomenon — **34 of 78 walks are deliberate
  per-feature walks sharing a live mod's subject** (MEASURED 2026-09-18). Of the 33 failing
  walks, 25 have a fully live subject and the defect is a stale id inside a STEP, and **0 are
  genuinely orphaned**. ⛔ Never "fix" a walk on an ORPHAN_WALK finding alone, and ⛔ do not
  rebuild the 43-row decision sheet: the owner ruled it was never his to adjudicate
  (*"this doesnt feel like a sheet I should be asked"*) and its data was wrong besides — a walk's
  subject packageId is backticked in 28 walks, BARE in 34 and absent in 16, so a backtick-only
  regex reads None for 50 of 78. `DETERMINISM_ASSESSMENT.md` §11a is the account; the walk-model
  ruling landed 2026-09-18 (owner card): **per-feature walks are first-class via a `feature:`
  key** (`WALK_FEATURE_KEY_1`, done). ✅ **The "modcheck status reads a stored field" bug is
  FIXED** (`fa27e1cab`, `status.check_or_orphaned` + `doctor.py`, same day as the claim above was
  first written) — live-checked 2026-09-17: `modcheck status` now correctly prints `FlowWorks
  STALE   [stored: GREEN]` and `Pits ORPHANED (no such mod folder)   [stored: GREEN]`, re-deriving
  every row rather than trusting the stored field. The dead `FluidCanals` key is gone too
  (`b110a7a2d`, `rename-key`/`forget-key`). Don't re-open this as a live defect without
  re-measuring; the stored field only ever appears now as a `[stored: ...]` drift annotation.
- ⛔ Do not casually edit their
  `## north star` sections: the hash
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
- Affects `PLOT_MECHANISM_MODS_WAVE_1` Part 1 (the raid-redesigner's Oracle calls ride
  whatever `OracleClient` becomes).

## A pit is a SUPERDEEP cell, not a building — owner, 2026-09-17

*"I'm not really sure a pit is any different than a deep canal."* Ruled and fully
specified, build in progress: `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`.
A pit is depth 4 on the D/F primitive rulings 18/19 already established, so the
fitting concept collapses to **spikes alone** (oil and poison are FluidDefs; the
oubliette is CUT), an enclosed superdeep area is a room that becomes a prison room
once a bed is in it, `capture down`/`convert down` happen from the lip because
nobody who enters can leave, and TEMPERATURE is the softening mechanism.

🔴 **The ITEM is the authority, not the spec.**
`design/RimMandrake/pit_superdeep_collapse_spec.md` (1127 lines) was written BEFORE
three rounds of rulings that changed ten of its answers; the item lists the revisions
it is owed. ⛔ Do not read the spec and act on it without reading the item first —
you would build the version he rejected. Door family shipped as
`FLOWWORKS_DOOR_FAMILY_1` (done): **two** stuffable defs, never the three he described and
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

## Every DLC is assumed — owner, 2026-09-19/25/26

🔑 **Design assumes every DLC is present** — owner, 2026-09-25, verbatim: *"Always assume all
the dlcs."* No standalone-without-expansion fallback tier is owed (asked about the free mods'
deluxe gear without Odyssey). `MayRequire` guards stay for load safety, not as a design axis.

🔴 **And that assumption covers the PLAYER, not just us** — owner, 2026-09-26: *"it is assumed
that future players will have all the Rimworld DLC's currently installed."* ⇒ **Every DLC is a
hard prerequisite of shipping, exactly like the base game.** Royalty, Ideology, Biotech, Anomaly
and Odyssey content may be depended on outright in anything we ship — a mechanic, a def, a
biome roster, a quest, a scenario.
- ⛔ **Do not design, build or file a DLC-less degradation path**, and do not raise "what if the
  player lacks X" as a defect, a risk or an open question. It is answered: they have it.
- ⛔ **Do not spend a review, a test tier or a load round on proving a DLC-absent configuration.**
  There is no such supported configuration.
- ✅ `MayRequire` still goes on **mod** guards for load safety. On a DLC it is harmless but
  decides nothing, so never read one as evidence that a DLC-absent case is supported.

🔑 **ALL TEST MOD LISTS include ALL FIVE EXPANSIONS — no exceptions right
now.** Owner ruling, 2026-09-19, verbatim: *"Was Odyssey even loaded for this
test? ALL TEST MOD LISTS should include ALL THE EXPANSIONS; we're not trying
to ablate expansions out of our list at this time."* `modset_builder.py`'s
`bridge`/`pits`/`graffiti`/`oracle` tiers built Core-only before this ruling;
all tiers now set `dlc: True`. A tier's `want` list may still narrow which
*mods* load for isolation — it may no longer narrow which *DLC* loads.

## Correctness outranks seat ownership — owner, 2026-09-19

*"It is WORSE to leave incorrect information that belongs to another seat than it is
to violate seats... ok? I keep saying this. MAKE IT SO EVERYWHERE."*

🔴 **A false statement in another seat's file is yours to fix, on sight.** Item prose,
spec, design doc — no correction ticket, no note, no waiting. A wrong sentence left
standing is believed by everyone who reads it next; the seat boundary was never
supposed to protect one.

- **Commit it at once, explicit paths.** The danger was always the UNCOMMITTED fix in
  an uncommitted change is erased by the next checkout, nobody told. Committing is
  the safeguard, not the risk.
- **The commit says what was WRONG**, not merely what changed.
- ⛔ **Correcting is not redirecting.** Their scope, priorities and open decisions stay
  theirs — fix what is false, `rimflow file --for <them>` anything that is a judgement.
- Enforced, not exhorted: `.claude/hooks/queue_lint.py` WARNS on a cross-seat item
  edit and never blocks it. Pair with the deletion rule directly below — remove wrong
  content, don't annotate it.

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

**Operating doc: `design/RimMandrake/GIT_WORKFLOW.md`** — read it before touching git.

- **Work in your seat clone** — `/home/mandrake/rm/bench` or `/home/mandrake/rm/foundry`, ext4, one writer each. `D:\Luke\dev\RimMandrake` is a **read-only mirror** of origin/main (no `.git`, refreshed every 5 min); never write it. Windows tools read it.
- **Land with the wrappers:** `./publish -m "subject" path…` or `land.sh <sha> <paths>` (each prints `PUBLISHED <sha>`; pass that to `rimflow close --sha`), and `./sync` to realign the clone — never `git pull --rebase` (it refuses on any dirty file) and never a stash (`GIT_WORKFLOW.md`). Pathspec on the `commit` (`git commit <paths> -F -`), never `git add -A`/`.`/`-a` (hook-enforced), never `--force`, never a file over ~50 MB.
- Committed *and pushed* is the only durable state: commit each finished unit and push at once. Proof of publication is `git merge-base --is-ancestor <sha> origin/main`, not an empty `git log origin/main..HEAD`.
- The pre-push and PreToolUse hooks refuse a compound command whole: keep file writes and commits in separate Bash calls.
- 🔴 **Worktrees are OFF** (owner, 2026-10-02, by card): never `isolation: "worktree"`, never `git worktree add` (`block_worktrees.py` refuses both). Writing helpers edit in the window's clone, one at a time when paths could overlap; the window commits explicit paths. Brief helpers that `reset --hard`, `checkout --` and `stash` are forbidden and a conflict is reported, never cleared.
- **Per-writer state, nothing shared:** ledger shards `ledger/events/<SEAT>.jsonl` (`merge=union`, `ledger_lint.py`; never `checkout --ours/--theirs` one); queue views are rendered on read (`rimflow queue <SEAT>`); lessons are one file each under `infrastructure/state/lessons/`; review status records under `infrastructure/state/code_review/`; artpipe state is outside git at `D:\Luke\dev\_artpipe\`.
- **Windows-side tools:** builds go through `winbuild.py <Mod|csproj>`; `codex.exe` needs `D:\Luke\dev\_rmscratch\codex\` staging (`gpt_consult.py`, `codex_image.py` do it). 🔴 A committed mod DLL carries a `.srchash` and is pushed with it (hook `block_dll_source_mismatch.py`, on push); after a merge touching a mod's `Source/`, rebuild — never pick a side's DLL.
- Drained historical work lives in `archive/*` tags on origin.
- Origin is SSH (`git@github.com:Lmandrake/RimMandrake.git`); a push that falls back to https can use a one-shot token header (`gh auth token`).
- ⚠️ A `cd` in one Bash call persists into later calls (`modcheck` needs `python3 -m modcheck.cli <verb>` from `src/RimMandrake/Utils`); use absolute paths or `cd` back.

## Code isn't clean until a review says so

**Every file in this repo is dirty by default — including files nobody has
touched today.** The only way a file is CLEAN is a clean
record in `infrastructure/state/code_review/<SEAT>.jsonl` (append-only, last
record per path wins; owned by `code_review_status.py`, never hand-edited) whose recorded content hash is
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
`design/RimStarWars/canon_references/` holds the canon entries (creatures, species, droid
chassis; count it, never cite a number) — each with sourced canon, a visual brief written against real reference images, a
`## Must show` checklist and `## Engine limits`. **An empty `## ruling` means canon stands
unopposed, not that the entry is unusable**; he rules only on ambiguity, deliberate
departures and contested regens. `AGENT_BRIEF.md` there is the operating doc. 🔴 Keep the
three defect classes apart — a **missing gene** is edited in the def, an **engine limit**
needs new art or more mask channels, and a **rig limit** (Ithorian neck, Kaminoan
proportions, Muun body, Lasat legs) cannot be fixed at all, so art chasing it is waste.
⛔ **Cosmetic changes need his permission first** — they can break animated faces.
🔑 **Every art review sheet shows the canon reference images and the entry's `## Must show`
beside each row whenever the subject has a canon entry** (owner, 2026-10-04); a row without one
says so. Since 2026-10-04 art goes through the art ledger and its `art install` only
(`design/RimMandrake/art_ledger_design_2026-10-04.md`), and his rulings live in
`infrastructure/state/art_rulings/`, never only in `Transient/`.

```
src/                    mods, defs, C#, art            FOUNDRY owns
design/                 campaign specs (Utinni)        the owner's, via BENCH
skills/                 tooling + how-to               curated in fresh-context passes
infrastructure/state/   ledger, items, facts/, V1.md   written only through rimflow
  items/<ID>.md         LIVE item prose only — this glob is the live set
  items/closed/         prose of done/dropped/superseded items (moved on close)
  handoffs/             reboot handoffs — NOT queue items, never greppable queue state
Transient/              output to LOOK AT, then bin    tracked+pushed, ~14 days
```

**Transient rule**: a human reads it once → `Transient/`; a program reads it →
`/tmp`, never the repo; anyone-later → the repo, committed outside `Transient/`.
Tracked and pushed so the owner can review it from another machine (his ruling
2026-09-01, recorded in `.gitignore`), but shelf life is ~14 days: never the
only copy of anything, and never a committed doc citing a file inside it.
`rimflow sweep --transient` lists by age; it never deletes.

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

## Check for existing regenerated art before queuing more — owner, 2026-09-20

Before filing any `fill_queue.py` job (or otherwise deciding art is "owed"),
check whether art for that subject was **already generated and already ruled
on** — the artpipe daemon runs continuously and its output regularly sits
unused for days because the def/roster work that would wire it in hasn't
happened yet.

- **Search the artpipe state dir by subject/defName first** —
  `python3 src/RimMandrake/Utils/artpipe/artpipe_state.py find <term>…` covers `done/`, `_artsrc/`,
  `registry.jsonl` and `art_status.json` in `D:\Luke\dev\_artpipe` (outside git since 2026-10-02) and
  refuses rather than report 0 when that dir is absent — not just by job-id guesswork.
  A finished job's `rimflow_item_id` and `style_notes` often name the exact
  roster row or item it was generated for.
- **Check for a review sheet's `.decisions.json`** (`Transient/*.decisions.json`,
  a `port_tail_*`/`bulk_art_*` sheet, or similar) — if the owner already ruled
  on that art (kept/replace/improve), queuing a fresh regen throws that
  ruling away and spends a job for nothing.
- 🔑 **Caught live, 2026-09-20 (`BMT_FLORA_ABSORPTION_1`):** three plants
  (giant leaf, fire lavender, heatsink fungus) were about to get a fresh
  `fill_queue.py` job each. All three already had finished, validated art
  sitting in `_artsrc/` since 2026-09-12/13 — one traced straight to the
  exact roster row being fixed — found only because the owner said *"I
  actually already saw beautiful art for giant leaf somewhere in a review
  sheet"* and asked for a check across the rest of the missing set. Nothing
  in the workflow up to that point had prompted the check on its own.
- **How to apply:** whenever a def/item is "missing art" or "owed new art",
  search first, generate only what the search comes up empty on.

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

🔴 **Holding the bridge is blanket authorization — never ask what to do with it** (owner,
2026-09-19, verbatim: *"Never ask that. If you have bridge, you may start steam, launch
game, anything you need."*). Once `bridge who`/`bridge take` says it's yours, starting
Steam, launching the game, running a cold load, anything the session needs — none of it
needs a question first. This supersedes asking-first instincts elsewhere in this file for
anything gated only on "do you have the bridge."

`src/RimMandrake/Utils/broadcast.py` is the owner's tool; the game-state relay above is its
only carve-out, and since 2026-09-29 that relay is STAMP-ONLY — a seat running it writes the
ledger event and messages no window (owner: game-state broadcasts between agents *"burn tokens
unnecessarily and rarely inform"*; `rimflow next` measures the game itself).
🔴 Run commands yourself — a `!`-prefixed paste handed to the owner is the defect
(hook-enforced on Stop); anything he must LOOK at comes with the complete native path.
