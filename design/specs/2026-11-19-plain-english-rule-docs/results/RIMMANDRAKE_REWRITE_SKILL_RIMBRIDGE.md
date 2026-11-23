# Result: `RIMMANDRAKE_REWRITE_SKILL_RIMBRIDGE`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimbridge/SKILL.md`. Run 2026-11-23.

Base: `2b0248fa7f`
Also: skills/rimbridge/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 29,187 | 31,355 |
| words in linted prose | 3,172 | 3,541 |
| STE violations per 100 words | 4.22 | 2.23 |
| sentences over 20 words | 65 | 32 |
| flagged lines (mechanical) | 56 | 47 |
| lines that a cold reader cannot act on (hand count, by the writer) | 11 | 0 that this run could resolve; 5 listed under "Could not determine" |

The 32 long sentences that stay: one holds a command list and a measurement (the VEF line, §3), one holds an engine quote
(`ResolvePawn`). The other 30 are two short sentences that the lint joined at a bold lead, a closing quote mark or an emoji.

The flags that stay are the 🔴, ⛔, ⚠️ and ✅ marks. ⚠️ stays everywhere because line 9 gives it a meaning (provisional).
The 🔑 and ⭐ marks are gone.

## What stays byte for byte

The front matter (`description` included) and every heading. Four table rows changed (see "Conflicts").

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "Those are the ones that have destroyed things" | which acts | "Those two acts …" |
| "this is the hazard" lines in the long §0b paragraph | which game each sentence is about | one bullet per game |
| "A refused claim … (75 held, 3 his hold, 2 could not look)" | that the numbers are exit codes | "Exit 75 is …" |
| "a testq lane", "an L3 evaluation" | what each is | short gloss; home file named for L3 |
| "An all-null `get_bridge_status` is this" | what "this" is | names the option and the unfocused game (`connect-and-claim.md`) |
| "in the game's menu (a `Prefs.xml` edit … is discarded)" | who discards it | names the game |
| "`build.py` refuses and names them" | what is refused | "refuses such a deploy and names the tools" |
| "a sealed room built from nothing …" as a clause | what to do | "build a sealed room …" |
| "Everything else changes one thing you named. This hands …" | what "this" is | "Unpausing hands …" |
| "Four … are one-way doors" over five bullets | which four | the later bullet stands apart |
| "§5's 'compose the sequence …'" | the line is not in §5 | §8 states the rule |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`, `solidThingDefs`, the 568 and the 65 | 1 lost (the id), exit 1. Check 1 did not see the other three. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 5 lost, exit 1 |
| check 1 | the final rewrite, with `--also` | 82 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 273 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work.py`, `selftest_guiding_prose.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | new text | PASS |

Names: Steam and Pilot are as often in the new text as in the old. VEF is named more often (the spawn rows). No person is
named in either text.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 24 items.

| finding | repair |
|---|---|
| `jawa/pawn_get` "each hediff": the code stops at 40 and does not tell left from right | says so |
| `T: Destroy`: "beside them" invented a position and lost that the pipes died | rewritten |
| §4 `Actions\Spawn Pawn...` "resolves" was weaker than "works" | "works", with the VEF limit |
| "A fifth thing fails silently" blurred the list | "One more thing in that area" |
| `--restore` "refuses any other state" was too strong; the chain rule had no refusal; the running game was missing | rewritten from `modset_builder.py` |
| history: the wrong commit for the md5 restore; an invented parenthesis | `7de700be43`, hardened by `0a63b2267e`; parenthesis gone |
| "Its load is seconds" was measured on the old tier | says so |
| §9 "add" had become an order | "you can add" |
| the all-null status needs an unfocused game too | added |
| four changes had no history record (fold-in note, `python.exe`, port scope, one-way doors, spawn row) | records added |

Not repaired, with the reason:

- The reader found no source for the testq gloss. The source is `skills/live-debugging-proof-harness/SKILL.md` ("runs proofs
  with no LLM (testq, SteveDesktop)").
- The reader notes that WSL judges a Windows holder by heartbeat, so "free at once" is not exact there. The line is root
  `CLAUDE.md`'s own.

The same reader then read each repair, the split of the fuel-tank line, and the edits of `connect-and-claim.md` and
`preflight.md`: OK or SAME, but for three. The writer repaired the three:

- the tier load time claimed a measurement: now "said of the old 3-mod tier; not re-measured at 10 entries";
- his quote "No more long runs." is the ledger's form; the history file now gives the transcript's form too;
- "check with the owner if it looks abandoned" had no history record: added.

No reader read those three last repairs. After the first landing, the prose check of `./publish` named 23 lines. The writer
repaired 22 in the same run: a noun for a pronoun (18), the L3 wording, one long sentence, the two debug actions that are the
"inhabited harness" (`DebugActions_Inhabited.cs`), and the file of `restore()`. No meaning reader read those; `keep` and the
prose check did. The term "deck" was not found: item `RIMMANDRAKE_DEFINE_DECK_IN_RIMBRIDGE_NOT_FOUND`.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| "45-minute staleness rule measures EVENT SILENCE" / a holder is a process | the process; 45 minutes only for his OWNER hold. Also corrected in `connect-and-claim.md` | 1: `cli.py` gives a live holder idle 0; `game_lock.py`; 3 |
| `claim a`, `launch b` / "do not write game a" | ArchBig, ArchSmall | 3 |
| `connect-and-claim.md` "wait for their release, or check with the owner" / take another free game | take another free game; wait only when no other game can take the work | 3: §There are several live games |
| "port 5174, stable" / ArchSmall 5175 | 5174 is ArchBig's | 1: `game_instance.py` `BASE_PORT` |
| `python` in the §1 command / "run `python.exe`" | `python.exe` | 5: the rule of the same section |
| "fold-in owed" (§0, `preflight.md`) / one list holds owed work | deleted in both: the pointer row is the form of that table | 3, 5 |
| `.rws` parse is "the only way to measure damage" / `jawa/pawn_get` | both routes | 1: `JawaBenchPawnTools.cs` |
| "spawn a pawn" by debug action / it NPEs on a VEF-loaded list | `jawa/spawn_pawn`; the debug action without VEF | 1: `traps/pawns-factions.md`, measured |
| "Long runs are risky" / "No more long runs" (both 2026-10-13) | allowed when the colony is safe (his card, 2026-11-23 9:55 AM PST) | `debug_process.md` §A long clock advance |
| "19-mod minimal list: 22 s" / 13-mod | the 13-mod list of 2026-08-19 | 1: as settled before |
| `--tier bridge` = 3 mods / every DLC is assumed | Core, every DLC, Harmony, RimBridgeServer and two helper mods | 1: plan run of 2026-11-23, 10 entries |
| `--restore` hands back the previous tier / md5-verified first before-copy | the second | 1: `modset_builder.py`, `7de700be43`, `0a63b2267e` |
| "restore ModsConfig BEFORE releasing the bridge" / no restore step | no restore; `--restore` still needs the bridge | 3; 1: `bridge_ok` |
| "15 of the companion's total", "all 91 `jawa/` tools" / "count it, never quote it" | counts deleted | 1: 16 tools in `JawaBenchMapTools.cs`; 4 |
| "full MIT source" in `vendor/` / no source folder | docs and tests; the folder is untracked | 1: 48 `.cs` files, all in Tests and Tools |
| "Four … one-way doors" over five bullets | four; the fifth bullet stands apart | 1: the bullet was added later (2026-09-23) |
| `B.until` / `B.watch` PLANNED / methods in `validation_core.py` | stays PLANNED | 1: the companion source has no `until` argument and no `jawa/cond_watch` |

Left as dated records: `design/RimMandrake/bridge_system.md` (2026-10-10, labelled history) and
`design/Jawa/worldbuilding/row8_build_order.md` cite line numbers of an old `SKILL.md`. The numbers were stale before this run.

## Could not determine

| line | question | who would know |
|---|---|---|
| "provisional findings ⚠️" | many ⚠️ lines are measured warnings, so the mark has two senses | the author of the skill head |
| "`saveName` … state-dependent" | which state decides it | a live run of `rimworld/save_game` |
| "`ResolvePawn` accepts player-controlled colonists only" | still true in today's RimBridgeServer; its source is not on this machine | a live call |
| "needs no save, no deck" | which deck (text of 2026-08-15) | item `RIMMANDRAKE_DEFINE_DECK_IN_RIMBRIDGE_NOT_FOUND` |
| "16.7 ms floor … cause of the spread is unknown" | the cause | `bridge_latency_bench.py` |

## What this run did not test

- No live game was driven. Each bridge claim of the old text stands as written.
- No measurement shows that an agent drives the game better with the new text.
- The trigger evals were not run, because the description did not change.
- The other files of `references/` were not read in full. Two of them changed: `connect-and-claim.md` (two paragraphs) and
  `preflight.md` (one line). The meaning reader read those edits.
