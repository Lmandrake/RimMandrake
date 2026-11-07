---
name: using-rimflow
description: "Use before ANY rimflow / src/RimMandrake/rimflow/cli.py call — file, claim, start, close, drop, supersede, note, next, seat, sweep, bridge take/release/who — and before passing --owner-said, committing a ledger shard (infrastructure/state/ledger/events/<SEAT>.jsonl), or reading the ledger or queue/*.md projections. Covers the sharded ledger layout, exact verb syntax from --help, the close --sha literal-string and silent-HEAD-fallback traps, the four provenance flags (--owner-said / --by-card / --per-ruling / --why), --seat on the Mac laptop, ledger commits being local-only, merge-order projection, and the bridge lock."
---

# Using rimflow

## What rimflow is

rimflow is one master queue derived from an append-only ledger. 🔴 **The ledger
is SEVERAL files since 2026-09-23** (`EVENTS_JSONL_SHARDING_1`, landed
`2b5947555`): `infrastructure/state/ledger/events.jsonl` is frozen history that
nothing appends to any more, and every `file`/`claim`/`close`/etc. call appends
to the calling seat's own shard, `infrastructure/state/ledger/events/<SEAT>.jsonl`
— so two seats can never rebase-conflict in one git-tracked file. `model.read()`
with no path merges history + every shard; `model.read(model.EVENTS)` reads the
frozen history alone and is almost never what you want. No other file is the
source of truth. Item prose (spec, context, decisions) lives separately in
`infrastructure/state/items/<ID>.md` while the item is open; on close/drop/
supersede its prose file moves to `infrastructure/state/items/closed/`. IDs
are `SUBJECT_INTENT_TWIST` (`rimflow namecheck <NAME>`: 3–7 words, ≤ 44 chars; legacy `…_1` ids stay valid),
guessable cold — never a number. `rimflow
next --seat <SEAT>` is the one command you need to start work; everything
else (`show`, `why`, `render`, `reindex`) derives a view from the same ledger.

## Verbs

Every verb takes the per-verb (not global) flags, written AFTER the verb
(`cli.py bridge take --seat BENCH`; `cli.py --seat BENCH bridge take` is refused): `--seat`, `--target`, `--mode`,
`--owner-said`. Syntax below is exact, from `--help` — check `--help` again
before relying on flags not listed here; the CLI has more verbs
(`block`/`unblock`/`finding`/`spawn`/`needs`/`retarget`/`reassign`/`reclaim`/
`lint`/`artifact`/`render`/`reindex`/`game`/`capability`) not covered by this
skill.

```
rimflow file <ID> --for FOR --title TITLE [--kind K] [--row N]
             [--target-field v1|v2] [--needs offline|deploy|game-up|bridge|harvest|owner]
             [--spec PATH] [--caused-by ID] [--replaces ID]
             create work for ANY seat, including another's.
             --replaces ID supersedes ID in the same act (parent closes, names successor).

rimflow claim <ID>          take ownership; lands in `doing` under a live lease (was `ready` before the 2026-10 lease redesign)
rimflow start <ID>          begin work; never refused for missing prose

rimflow close <ID> --sha SHA | --no-code "<what>" [--reason REASON]
             close against a commit, any seat; --reason required in practice
             when the item is another seat's (see `close` is earned, below)

rimflow drop <ID> --reason REASON        this will not be done (reason required)
rimflow supersede <ID> --by ID [--reason REASON]   a better item replaces it

rimflow note <ID> --text TEXT            a line of context; prose belongs in items/<ID>.md

rimflow show <ID>           everything the ledger says about one item
rimflow next [--bench]      the one item to work now; --bench is the board-triage view

rimflow verify <ID> --result pass|fail|partial --config CONFIG
             [--evidence PATH] [--sha SHA]
             record a RUN. Immutable — a fail stands forever.

rimflow seat {ready,busy,idle} [--reason R] [--item ID] [--note NOTE]
             announce what this seat is doing; --note is what a handoff reads

rimflow bridge {take,release,who,give} [to] [--for PURPOSE] [--force]
             `who` only reads/repairs the mirror; `take`/`release`/`give` write the
             ledger. --force takes it from an awake other window (recorded).

rimflow sweep [--transient]    lists stale TRANSIENT_* files. LISTS ONLY, no ledger write.
```
- **`rimflow file` writes only the ledger event; it creates no `items/<ID>.md`, and `--spec PATH` records PATH verbatim without copying it.** Staging the imagined prose path dies on "pathspec did not match"; write the prose to `infrastructure/state/items/<ID>.md` yourself (or pass a repo path to `--spec`, never a session-scratch path that dies with the session, or the item reads "no spec"), and commit the shards. Never create `items/*.md` without a ledger row: it turns `selftest_items_glob_live` real_glob_is_clean red.
- **`rimflow file --needs game-up` prints a refusal-shaped warning ("A live check is owed only to a mechanism never once observed running...") but still files the item;** run `rimflow show <ID>` after a file call that looks bounced before assuming it did not file. `game-up` is the wrong tag for a pure offline roster diff; only flipping mods on and proving them needs the restart.
- **`rimflow implemented --none-owed` moves an item straight to DONE, which is terminal.** Helpers used it on two items whose live proof was still owed and they could not be reopened. Brief helpers to use `--criteria-file` with level-tagged owed checks, never `--none-owed`, unless nothing beyond L0 is genuinely owed.
- **`file --replaces X` supersedes X in the same act and there is no un-supersede.** A `--replaces` pasted onto the wrong line of a copy-pasted batch of file calls points the old item at the wrong successor for good (only a note corrects it). Write each file call with its own `--replaces` checked against the item it really replaces; never send a half-edited batch line.

## Item hygiene

🔴 **An item's prose must not be the only copy of its inputs.** `NORTHSTAR_PROCESS_RETRO_1` named a `Transient/` notes
file as a first input; Transient is untracked, and the file was gone from every clone when the item came up. Pin the
file (`transient_pin.py add`) or copy what matters into the item. The same item's helper list had gone stale in the
meantime (two of six were built under other names), so `grep` the tree before building from an old list.

🔴 **An item filed alongside a finished analysis must cite the report path.**
Two items carried specs but no pointer to the prior window's `Transient/`
report, so the next window re-ran both analyses blind.

⚠️ **An item's "NEXT:" note can be DISCHARGED by a later item** — acting on a
note without checking cost a whole redundant review sheet once, when a later
item filed the same day recorded that the noted work had already been served
and ruled. Before acting on any note, list items filed AFTER it that name the
same subject: `ls -t infrastructure/state/items/` is enough.

🔴 **`infrastructure/state/MODE` has no CLI setter — it is a plain file
`cli.py` only reads, and it can go stale.** A FOUNDRY window once read `afk`
from a prior session while the owner was live saying "go go go"; `rimflow why`
silently suppressed a fully-specified `needs=owner` item under that stale
mode with no warning that mode gating was the reason. If the owner is
actively present but items keep reading "needs owner, afk suppressed", check
this file before assuming the item is genuinely blocked.

🔴 **`rimflow unblock` refuses another seat's in-flight item, and names the
right move itself:** correct the false prose in their item file, commit by
explicit path, and use `note` to nudge. Do not force the state.

⚠️ **A gate citing an item by name should be treated as suspect the moment
that item's own state changes, not just after weeks.** `rimflow lint
--citations`' STALE_GATE sweep has found items describing another item as
"still open/blocked" that closed the SAME calendar day, one within the same
session that closed it — a doc can go stale within hours, not just weeks.
- **Before building, claiming or re-briefing an item, check the code and git first.** `git log -S <symbol the finding names>` and `git log --grep=<ITEM_ID>` (a design doc's "not changed yet" lines go stale; 4 of 7 "unworked" pieces and 8 of 10 "proposed" candidates were already built), `rimflow show <ID>` history, and a `git fetch` plus grep of origin for the deliverable's files at the start and at each milestone (a ~800-line helper was built twice). If it is built, record `implemented` with the DLL/commit sha instead of rebuilding. After building, append a `## Built` section to `infrastructure/state/items/<ID>.md`: a build recorded only in a ledger note gets re-briefed as new work. When a brief says "these uncommitted edits finish items X and Y", mark an item implemented only when `git show --stat <sha>` lists THAT item's files.
- **A closed item cannot be restarted, and `done` is terminal (no `done` -> `dropped`).** Never `close` a standing-loop item; file a continuation instead. A fixture or trial item that was closed by mistake is retired with `rimflow verify --result fail` plus a note saying so, and the false close stays visible in close statistics; prefer fixtures that never reach the shared ledger.
- **An item found "already built" is closed or marked `implemented`, never left with only a ledger note.** Two `*_RM_MOD_BUILD_1` items sat `proposed` after notes and kept being re-offered to later windows.
- **A failed or partial live-verify step is grounds to retry or block, never to close.** A build agent whose `## verify` needs a live quicktest and that closes on deploy-sync alone while "documenting the gap honestly" has not verified; brief build agents explicitly, and send such a close back.
- **Before carding, routing or asking the owner anything, read the item's whole ledger history, not the latest block reason or a prose harvest.** Grep the ledger shards and sibling items for each question (`rimflow show <ID>`, the caused/causing items, `design/RimMandrake/delegation_policy.md` §1/§2): a prose-only harvest re-asked 4 already-ruled questions, and of 6 items routed as needs-owner none needed him (a ruling he had already given, classes the delegations hand to agents, a list answered by later rulings).
- **A closed item can be true for one twin def and false for its frozen twin.** Check both the `RM_` and `RUT_` side before closing a per-biome numeric fix (`RM_PropaneLake` got `animalDensity`, the live save's `RUT_PropaneLake` did not).
- **A note saying UNBLOCKED is not an unblock.** The BLOCKED event stands and rimflow keeps rendering the item BLOCKED; when work resumes on a blocked item run `rimflow unblock` in the same act, and have sweeps grep notes for "unblock" on BLOCKED items.
- **When you record the owner's answer on an item that is `needs=owner`, move `needs` in the same sitting** (`rimflow needs <ID> --to offline|bridge`); 8 of 13 "to rule" rows had been answered after the needs event and nobody moved it. `needs=owner` names no addressee and `--for` names the seat that works the item, so RimPulse shows a ledger ask only when it is addressed to him (filed/asked by OWNER, a provenance flag, `--for OWNER`, only L4 owed, or "owner decides") and is a thing to view or a fresh ruling; everything else is one dim "N not shown" line. Start the reason with `owner:` (or `agent:` for a question to a seat/judge), and re-ask with `needs --to owner` to bring a stale one back.
- **Copy an owner-ruled table or decision into `infrastructure/state/items/<ITEM>.md` the day it is ruled;** Transient decays and later specs cite only items. A spec that could not see the ruling (an owner-ruled Rot fauna table living only in a Transient draft and a ledger note) contradicted it. Likewise, before building from a design-doc section, grep the item's ledger notes for owner card rulings: a doc can still say the opposite of a later card (the mineral registry design said "unregistered minerals suppressed by default" after the card ruled the reverse); propagate the ruling into the doc.
- **A claim sha is often a lesson-only or ledger commit, not the work.** A verifier must `git show --stat` the cited sha and find the real code commits by file log before testing. Claims whose sha is a ledger or lesson commit, with no verify text and no code-review mark, cannot leave UNRESOLVED however often they are re-judged (67 carried through four Arbiter batches): close-time sha and review marks move them, not more batches.
- **Put a proof on its item in the moment it is seen** (`rimflow note` or `verify`). A proof that lands only in a diag file or a lane's resume reason (a wake-on-LAN success sat in a diag file with no note on its item) does not survive a handoff, and the owner had to say it again.
- **An item is a claim about the past; read it to its END.** Writers ship work without touching the item file, notes never expire, and prose keeps "open question" text after the ruling lands. `rimflow next` quotes only the opening `## spec`; the answer is usually under a later dated heading. Then run `git log --oneline -5` on the files and keywords it names; silence in the item file proves nothing. Before acting on a `NEXT:`/"owed" note, list items filed after it on the same subject (`ls -t infrastructure/state/items/`): the newest item outranks an older note. Before carding a harvested "open question", grep `infrastructure/state/ledger/events/*.jsonl` and sibling items for its topic (owner: "You had asked me those questions before."), and brief harvesters to do this per question. When you solve an item, fix both its `needs:` and its stale opening section, or the next window is handed your dead theory as top-priority work. Classify items by their `state:`, never by a name list.
- **Any seat closes dead items.** (owner) "when any queue item is found to have been completed, totally invalidated or superceded, or otherwise rendered into something no longer worthy of being considered for activity, ANY SEAT may denote this in its log, record which seat ruled this, and CLOSE it completely." `close`/`drop`/`supersede` are `who: "any"`; pass `--reason` with the proof and no owner-quote flag. Done means proven; a subagent's verdict is not the proof.
- **An item's detail writeup lives at `infrastructure/state/items/<ID>.md`, never `infrastructure/state/queue/items/`.** The latter sits next to `queue/BENCH.md` and looks plausible, but `rimflow show <ID>` does not read it: it prints "(absent or has no ## sections)" for a real writeup, and the ledger `spec=` can point at the wrong path with no error. When `rimflow show` reports no sections, check `queue/items/<ID>.md` before assuming the detail was never written. Before moving or deleting a misplaced file check the owning seat (`rimflow show <ID>`): a cross-seat-ownership hook refuses a commit touching another seat's item file even for a pure path fix, so leave it flagged for the owner.
- **Ledger-note every accepted ruling, name map or register the moment it lands.** A ruling that exists only in conversation is stranded by a reboot or by a background agent that never saw it. Quote the owner's words verbatim in the note. Search a biome or subject under ALL its names (program-table name and campaign label differ) before concluding its design record is missing.
- **A closed item's `## verify` can be silently unmet, and offline-green is not done for anything the running game touches.** Before trusting a closed item's "zero X remain" claim, grep the actual deployed or hand-authored XML, not the design-layer source: a generator (`biome_flora.py --write` to `Patches/BiomeFlora_*.xml`) only overwrites at load and never edits the base `Defs/BiomeDefs/RUT_*.xml`, so its `--check` (roster vs `FAMILIES`) cannot see a stale base file. The same roster/generator-layer fix never reaching the hand-authored layer recurred four times. Defects found only by a live load: a generator overwriting hand-authored `wildPlants`, a stale `CreatureBehaviors.dll` missing three types, a mod absent from the owner's stored FULL list so its plants could never spawn, and a missing-suffix bug in the texture-absorption generator dropping worn graphics for 123 apparel defs (1,560 PNGs). Do not close a build item on "compiles + validates" when its criteria say live.
- **Read the roster, not a "still absent" item's own census, before authoring flora or fauna.** A census that grepped only `RSW_` names claimed 14 flora defs had no replacement; 11 already had `RUT_` ports in `design/Jawa/worldbuilding/biomes/rosters/*.json` and `RUT_*Flora.xml`. The rosters (not the generated `BiomeFlora_*.xml`/`PlantTolerances_*.xml`, which go stale after a roster edit) are the source for `design/Jawa/mods/biome_flora.py --write`, and that script's hardcoded `FAMILIES` dict is a third copy that must be hand-synced or `--write` silently emits the old names. Before queuing `fill_queue.py`, search `infrastructure/artpipe/done/` and `_artsrc/` by subject: finished validated art had sat unused for weeks. Scan patched-in tables too (e.g. `Patches/BiomeFishTypes_*.xml`), since scanning BiomeDefs alone misses them.

## `close` is earned (RO3, ruling D1(b), 2026-11-01)

`close` needs `--sha <published sha>` or `--no-code "<what>"`; HEAD is never assumed, and a sha that does not resolve
here or touches only the ledger is refused. Then, each refused with its reason and nothing changed:

- **owed:** a criterion still outstanding. No word lifts it; verify it or drop the item.
- **unchecked:** no level-tagged pass on that sha. Record one first:
  `rimflow verify <ID> --sha <sha> --level L0 --result pass --config <what ran> --evidence <path>`. A pass on another sha does not count.
- **fail:** the newest deciding run is a fail. A pass on that sha after it clears it.
- A sha touching none of the paths the item cites needs `--why`.

`--owner-said`, `--by-card` or `--per-ruling` on the close lifts **fail** only. `--why` lifts neither.

A `verify` now moves state both ways. A fail on the built sha takes `validated` to `built` and owes the criterion again;
a fail on a closed sha, or on a later commit that contains it, REOPENS the same item (`done` -> `ready`). A pass on any sha
but the built one counts for nothing. A run before
`model.EARNED_FROM` replays as it was written.
- **A criterion's level L1 is not "selftest":** most FlowWorks L1 criteria read "in game ...". Read the criterion text before recording a selftest as its verify; a selftest pass on a live criterion is a note, not a verify. When tightening a live clause, REPLACE its line in `infrastructure/state/live_proofs/<ID>.criteria` (never append a second `A1 L1:` line): `rimflow implemented` refuses "criterion A1 is listed twice" and the game phase dies after a green offline proof.

## Done means running: `--live`

A commit touching a hook, a systemd unit, `dispatcher_schedule.json` or `ops_watch_rules.json`, an Operations alarm
(`OPS_*`, `LIVE_RESTORE_*`) and any item already holding a promise closes only with a line that holds right now:

    --live "unit=rm-foo.timer reading=<path> max_age=6h"     the reading must be newer than the commit
    --live "unit=rm-foo.timer max_age=6h"                    the timer's own last firing
    --live "hook=block_foo.py"
    --live "role=Operations max_age=2d"
    --live "once: <why this is a real one-off>"              the visible escape; never swept

`close` and `implemented` take it alike; a refusal changes nothing. `rm-deadman.timer` (no AI, every 15 min, from the
dispatch clone) rechecks every line on the ledger and `src/RimMandrake/rimflow/live_baseline.txt`. A dead promise
reopens the SAME item through the RUNNER-only `live` verb, the one way out of `done`; recovery puts it back. A promise
with no item files `LIVE_RESTORE_<NAME>`, a fixed id, so a return counts on one item: repeat 2 reads NEEDS FOLD in
`show`, and Operations owns that. Remove a promise by retiring its item or its baseline line by hand. The last pass
is `D:\ClaudeWork\rimmandrake\ops_watch\live_sweep.json`.

## Provenance: `--owner-said`, `--by-card`, `--per-ruling`, `--why`

Owner rulings by question card, 2026-10-11 (the transcript-proof guards were deleted that
day: 0 forgeries found, 95% of refusals were his real words). One field per kind of
authority, so nothing lands in `ownerSaid` by mistake:

| flag | event field | acts as OWNER? | what goes in it |
|---|---|---|---|
| `--owner-said "…"` | `ownerSaid` | yes | **his words.** Light tidying is fine — typo fixes, joining two of his own sentences — if the meaning is unchanged. Never your words. |
| `--by-card ["question → picked option"]` | `byCard` | yes | a decision he took by clicking a question-card option. The label is OUR text, so it never goes in `--owner-said`; anything he TYPED into the card's notes/Other may. |
| `--per-ruling <item-id\|event>` | `perRuling` | yes | a standing ruling of his, cited by its item id or ledger event (e.g. `OWNER.jsonl:<tsn>`) instead of re-quoting it. **A ruling stands until he changes it.** Refused if it has spaces (that is a quote, not a reference). |
| `--why "…"` | `why` | **no** | your own reason in your own words (a self-initiated restart, an investigation note). Grants nothing; combine with any of the above. |

- **A delegated decision** (`design/RimMandrake/delegation_policy.md`, owner 2026-10-22) is
  `--why "delegated: <class>"` — ours, not his. ⛔ Never `--per-ruling` the delegation
  item to make it read as OWNER: the ruling authorises the class, not the call.
- rimflow still checks the quote's **shape** only: a question or bare assent ("yes") is
  refused as `--owner-said` — quote the instruction, or use `--by-card`.
- `note --owner-said` stamps the WHOLE event as OWNER-authored; use bare `note` (plus
  `--why` if useful) for your own writeups.
- `rimflow show <ID>` prints each field labelled (`owner said “…”`, `decided by card:`,
  `per standing ruling`, `agent's reason:`).
- `./game` takes the same four flags (`--said` is its spelling of `--owner-said`); a
  restart you call yourself is `./game --why "<your reason>" <state>`.
- **`--owner-said` rejects a quote ending in a question mark (read as a question) and a string stitched from several separate card answers.** Quote each answer in its own note and cut before any trailing question.
- **A provenance flag switches the acting seat.** `--per-ruling`, `--owner-said` or `--by-card` on ANY verb (`note`, `claim`, `start`, `reassign`) writes the event into `OWNER.jsonl` as seat OWNER, even with `--seat`/`RIMFLOW_SEAT`, and on a claim/start it moves the item's ownership to OWNER; `reassign --per-ruling` reads as the owner overriding, not you acting under a ruling. A builder's own progress or result note takes `--why`; use a provenance flag only where the owner's authority is the point (a ruling, a close lifting a fail). The Conductor (BENCH) may still verify and close OWNER-owned items.
- **An OWNER-seat note's `text=` field is an agent's gloss of a card option, not his words;** only the `ownerSaid` / `byCard` fields are verbatim. Quote those and label `text=` as "option text recorded with it". A card ruling with no doc write-back is invisible to every doc grep, so write the ruling into the item file.
- **`--owner-said` (and `art.py install/purge`, which uses the same guard) only sees the owner's ORDINARY typed turns** - never a message he sends mid-turn, never the current turn's text via `block_forged_owner_said`, and never a subagent's session. Record a volley ruling as a bare `note` quoting him verbatim (the guard's prescribed exit). To displace owner-kept art, collect the list and ask him for one plain message while idle; that message authorises the whole batch.
- **`./game --said` is STAMP-ONLY by owner ruling.** It writes the ledger and messages no window (broadcast.py skips delivery on purpose). A peer window that seems deaf to a game-state change is the design, not a regression: `rimflow next` measures the game itself. Do not "fix" the silent delivery.

## Seat identity

`--seat` is beaten by `RIMFLOW_SEAT` and refused if unresolvable. On the Mac
laptop neither rimflow nor `handoff.py` can derive the seat at all — no seat
profile, `CLAUDE_CODE_SESSION_ID` unset, and `set_agent_window.sh` only does
the window half — so every ledger call there needs an **explicit `--seat`**,
or a whole sitting's ledger trail lands mis-seated. Also: subcommand targets
take `--to` (e.g. `reassign --to FOUNDRY`, `needs --to bridge`); bare
positionals for a target are refused.
- **`rimflow next --seat <OTHER SEAT>` takes a real lease as that seat in YOUR clone** (a diagnostic `next --seat FOUNDRY` wrote a lease into the local `FOUNDRY.jsonl` and then blocked `./publish`). For a read-only look use `next --seat X --peek` (what the Dispatcher uses), `blind_view.py queue <SEAT>`, `rimflow why` or `rimflow show`, and run it in THAT seat's clone: the Dispatcher peeks there and a seat's local reconciles are not on origin.
- **`handoff.py` refuses "cannot tell which agent identity is handing off" when the corpus holds several seats.** Set the seat explicitly (`HANDOFF_SEAT=MACBENCH python3 ~/dev/Lodestar/bin/handoff.py` on the Mac laptop, whose seat is `MACBENCH`, not the Desktop's `BENCH`); guessing files your reboot under the other window's name and hands it your unfinished work.
- **`python.exe` has no seat env unless `RIMFLOW_SEAT` is set explicitly;** rimflow/ledger calls from `python.exe` fail or mis-attribute without it.

## Committing ledger writes

rimflow writes this seat's shard, `infrastructure/state/ledger/events/<SEAT>.jsonl`,
to disk immediately on every `claim`/`start`/`close`/`note`/etc. call — but it
has **no git integration at all**. Committing it is entirely on the calling seat, and it
is easy to miss: CLAUDE.md's "explicit paths, never `git add -A`" means a
commit that stages only the specific code/content files a fix touched will
never pick up the ledger delta as a side effect. A full session's queue
history can sit uncommitted — already-lost territory if the machine goes
down — until caught by accident.

Commit your seat's shard `infrastructure/state/ledger/events/<SEAT>.jsonl` by **explicit
path** (the rendered `queue/BENCH.md`/`FOUNDRY.md` are gitignored since 2026-10-02 —
never commit them; read them with `rimflow queue <SEAT>`, which renders first), with
each close or at least once per work wave — not only at session end. Prefer
a dedicated "ledger sync" commit over folding it silently into a code
commit's file list; it keeps the code commit's message focused and makes the
ledger's own commit history legible.

⚠️ **A stale or dirty clone cannot push its own shard.** The pre-push
`ledger_lint` hook checks the LOCAL HEAD, so events written in a clone that is
behind origin are refused as `NOT_APPEND` against other seats' shards.
`src/RimMandrake/Utils/ledger_sync.py` rescues them onto origin/main — run it
before any recovery of a stale clone, or the events are lost with it.

🔴 **A torn/invalid line in ANY ledger file breaks `rimflow`/`./game` entirely
for every seat** — a torn line has no admin-event fix, because rimflow can't
finish reading the file to append one. This has happened from a botched `git
stash pop` landing unresolved conflict markers straight into the file. Since
the sharding a torn line is far likelier in a shard than in the frozen head.
`src/RimMandrake/Utils/repair_torn_ledger.py` is the fix: dry-run by default,
`--apply --owner-said "…"` to write, and `--seat <SEAT>` to target that seat's
shard (a seat name, never a path); it removes only lines that fail to
parse (keeping a whole event glued onto a torn fragment), backs up to
`D:\ClaudeWork\rimmandrake\ledger_repair\` first, and sanity-caps at 25 bad lines.
- **`--owner-said`, `--by-card`, `--per-ruling` and `./game --why/--said` write `infrastructure/state/ledger/events/OWNER.jsonl`, not your seat shard.** Commit `OWNER.jsonl` by explicit path too (a commit of only `<SEAT>.jsonl` silently publishes nothing of the ruling), and a helper that restarts the game must commit it with its work: an uncommitted OWNER.jsonl makes `./publish`'s `reset --keep` refuse for every helper in the clone once origin's OWNER shard moves.
- **A ledger or `code_review` shard left uncommitted in the worktree while peers' rebases move HEAD goes older than origin (or ends up mid-file).** Committing it by path then silently deletes upstream lines and fails `ledger_lint` NOT_APPEND, and `./publish` retries forever. Fix forward: rebuild the file as origin's content plus your extra lines appended (`grep -qxF` to add only the new ones), commit. Prevention: the seat commits its shard promptly instead of helpers working around foreign lines.
- **`./publish` rebases your local commits onto origin, so a sha taken before publishing never reaches main.** `rimflow close --sha`, `verify --sha`, notes and commit-message references must use the sha `./publish` prints (`PUBLISHED <sha>`), so publish first and close after; a closed item cannot be re-closed, so correct a dead sha with `rimflow note`. A clone fed those commits by bundle then diverges ('ahead 10, behind 27'); bring it back with `git rebase origin/main`, which drops the already-applied duplicates. `code_review_status.py mark-clean` records the current local HEAD the same way: rebase first and then mark, or pass `--sha` with a published commit.
- **A hook refuses a commit that stages the ledger shard together with other paths.** Commit `infrastructure/state/ledger/events/<SEAT>.jsonl` (and `OWNER.jsonl`) alone, in its own commit.
- **`./publish` can REFUSE (a foreign dirty file blocks `reset --keep`); the commit then stays local and a later publish by any seat rebases it to a new sha.** Hold the close until it publishes. Its closing hint `close with: rimflow close <ID> --sha X` names the TIP of main after the rebase, which in a shared clone can be a peer's commit that landed after yours: take the sha from `git log --oneline` for YOUR subject line. A wrong close cannot be repeated (a second close is refused), so a pushed wrong close needs a note or a new item. Separately, `winbuild` compiles the working tree, so in a shared clone another seat's dirty `.cs` is baked into the DLL you commit (srchash shows it): build from `git archive HEAD` plus your files when anyone else has dirty source.
- **`rimflow append()` does not check the shard ends in a newline,** so a write torn at the tail gets the NEXT good event glued onto the same physical line; a repair that deletes every unparseable line deletes that good event too. `repair_torn_ledger.py` keeps a trailing complete event (keys event/seat/ts) and drops only the fragment.

## Reading projections

Every ledger file is append-only, and since 2026-10-02 the shards merge with
`merge=union` (`.gitattributes`), so **file position means nothing**: union keeps
duplicate lines and interleaves two clones' appends arbitrarily. `model.read()` with
no path is the one reader that is correct under that — it collapses identical
events and orders by `(ts, subject, model.VERB_RANK, seat, content)`, never by file.
**Never re-sort on `(ts, event)` yourself** — same-second `start`+`close` pairs get
their alphabetical tiebreak inverted by an `event`-name sort, which once turned 61
real "doing" items into a reported 102; `VERB_RANK` exists to prevent exactly that.
If you derive your own view (rather than `rimflow show`/`next`/`queue <SEAT>`), call
`model.read()` rather than merging by hand. A concurrent claim of one item by two
windows resolves earliest-ts-wins; `rimflow next` prints a CONTESTED CLAIM notice
naming both timestamps so the later window stands down. `ledger_lint.py` (selftests +
a push guard) refuses torn lines, missing newlines and any non-append edit.

🔴 **A view is only as current as the clone it renders from.** `rimflow queue`
in a clone behind origin replays a behind-origin ledger and shows closed or
changed items as open. A RECONCILE or decay sweep re-checks each item in a
fresh origin clone (`git fetch` and compare, or `scratch_clone.py`), never from
a stale seat clone's view.

🔴 **Never re-derive item state from raw events by hand — fold through
`model.replay(events, observe=cb)`.** A reader that knew only the `needs` verb
missed `implemented` and `file --needs owner`, so the old RimPulse board hid 29 owner items
and listed one item 9.5 h after it moved (2026-10-11). `observe(ev, world, ok)`
is called after every folded event, so it tells you which event moved a field
without re-implementing the verbs.
- **`rimflow queue` renders from the clone's own ledger, so a clone behind origin shows closed or changed items as open.** A reconcile or decay sweep must `./sync` first (or re-check each item in a fresh origin clone) and never trust the stale seat clone's queue view.
- **`rimflow show` lists only OWED criteria and truncates event text.** To prove a criterion was reworded to L0, grep the latest `implemented criteria=` history line, not the owes block.
- **A stale clone reads like an empty queue.** Before trusting `rimflow next`/`show` cold, `git fetch` and compare `git diff --stat HEAD origin/main` both ways; a clone ten commits behind answered from an old base while origin held shipped work. `./sync` realigns a clone (see `clone-landing-commits`).

## Bridge lock

`rimflow bridge` decides who drives the live game — not for ownership, for
attributability. `take --for "<what for>"` says what you're driving it for so
the other window can judge whether to wait; `release` the moment you stop
driving, not at session end. It errs toward **allowing, never toward mutual
lockout**: a `take` is refused only while the holder is provably alive — an
event within the last 45 minutes; after that the lock is stale (event
silence, not game activity — the game can sit idle for hours while the
holder is still working) and the next window simply takes it, saying so.
`--force` works on any seat's hold and is recorded. 🔴 **His OWNER hold is the exception** (owner, by card
2026-10-30: *"45 minutes after my last interaction, or I deliberately release it"*): no take, `--force` or
release by a seat until 45 min after his last deliberate interaction (OWNER ledger event, `./bridge`, `./game`,
his chat prompt to any seat); an unmeasured signal refuses (`rimflow/owner_interaction.py`). Nothing announces a release,
so if you want the bridge, check `bridge
who` again rather than waiting to be told.
- **Bridge idle time counts ledger events only (take/release/note), never GABP calls.** A subagent making 90+ live calls can show "idle 58 min", and a seat's live scripts (sprinkler_live, thirst_live, load_walk) call the bridge with no seat field so they never refresh the hold: `driver lock: FREE + hold idle 2h` is not proof the bridge is free. Check `D:\ClaudeWork\rimmandrake\scratch\bridge_calls.jsonl` for calls in the last ~10 minutes (or the Player.log) before taking it, and before calling a session stalled.
- **While the owner walks a save, do not touch the bridge at all, reads included** (`get_camera_state`/`get_ui_state` polling every 30 s coincided with his "someone automated is moving around the map"). Wait on `rimflow bridge who`, not on the game.
- **`rimflow bridge take --idle-ok` refuses any `--for` text containing the word "flyers", even negated ("no flyers")** ("flyer flight is never delegated"). Leave flyers out of the purpose string.
- **A bridge gate written as `rimflow bridge idle --for x | head -1 && <kill>` does not gate:** the pipeline's exit is `head`'s (0), so the kill ran on NOT TAKEABLE (a game was closed this way). Test the verdict text (`grep -q '^TAKEABLE'`) before any game close. Likewise a read-only "can I?" check must call what the action's own refusal calls: `bridge idle` once read the seat alone and said TAKEABLE while `take` refused on the process-keyed driver lock, so a tick spent 17 deploy plans and a ModsConfig write before each refused take.
- **Never assume the bridge or game is unavailable; check.** Run `rimflow bridge who` and `rimflow game` before any brief says "no live verification this pass". "Never assume you can't have Bridge. Always check for it before assuming you can't." (owner) The only real blocker is often the game being down, which a seat may fix by rebooting it.
