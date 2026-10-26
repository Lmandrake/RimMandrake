# Compaction retention test — 2026-10-26

Owner, 2026-10-26: "Do not test clear and remote control. instead we need to test the compaction ability to retain context."

Status: DONE. Scratch: `D:\ClaudeWork\scratch\compaction_probe\`.

## Method
- Part A: offline audit of real compactions in seat transcripts (BENCH, FOUNDRY). DONE
- Part B: controlled headless probe, with and without Compact Instructions. DONE

## Part A — real compactions (offline, zero new tokens)

Corpus: top-level transcripts of `~/.claude/projects/-home-mandrake-rm-bench` and `-home-mandrake-rm-foundry` (160 files). A compaction = a `system/compact_boundary` record (carries `compactMetadata.trigger`, `preTokens`) followed by a `user` record with `isCompactSummary: true` (the summary text). **18 compactions in 16 sessions** (BENCH 8, FOUNDRY 10; 9 manual, 9 auto; preTokens 215k–588k; summaries 8–24 KB, i.e. roughly 1/25 of what they replace). Compact Instructions entered CLAUDE.md in 4d287a5e35 (2026-10-11 16:34 UTC): 11 compactions after (CI-era), 7 before.

Scripts and outputs: `D:\ClaudeWork\scratch\compaction_probe\partA\` (`audit.py`, `audit.json`, `agg.txt`, `summ_<session>_<n>.txt` = every summary).

How each item was measured (all string-matching, no model grading):
- Owner = `user` records with `origin.kind == "human"`, plus question-card answers (`User has answered...` tool results). Each sentence of 6+ words: verbatim = normalised sentence is a substring of the normalised summary; paraphrased = 60%+ of its 4+-letter words appear in the summary; otherwise lost. Dated = a date within ~250 characters of the quote.
- Open items = IDs on `NEXT` lines in assistant text, plus IDs the seat filed/claimed/started/noted through rimflow in the segment and did not close there (a proxy; another seat may have closed them). Present = exact ID in the summary.
- Running subagents = Agent/Task launches in the segment with no `<tool-use-id>` notification before the boundary (a proxy; it may overcount). Description verbatim/paraphrased; agentId present.
- Uncommitted = Write/Edit paths after the segment's last `git commit` (a proxy; seats delegate most writes to helpers, so n is small).
- HANDOFF OWED = owed if no `HANDOFF READY` after the last commit; present if the summary has the literal line.
- Bridge = segment ran `bridge take/release`; present if the summary mentions the bridge.

| Item (CI #) | All 18 | CI-era (11) | pre-CI (7) | Verdict |
|---|---|---|---|---|
| 3 Owner sentences | 316 verbatim / 18 paraphrased / 5 lost (93% / 5% / 1.5%) | 238 / 18 / 5 | 78 / 0 / 0 | Kept, because the built-in summary template has an "All user messages" section, not because of CI |
| 3 ...with a date | 10 of 316 verbatim quotes are dated (3%) | 7 / 238 | 3 / 78 | **Date lost almost always** |
| 1 Open item IDs (exact) | 34 present / 32 lost (52%) | 21 / 19 | 13 / 13 | Half lost or shortened (for example `DONOR_DEFS_PORT_TO_OURS_1` became `DONOR_DEFS_PORT`); CI did not move it |
| 1 ...only on literal `NEXT:` lines | 1 present / 3 lost (n=4) | | | Seats rarely write `NEXT:` lines in chat |
| 5 Running subagents (proxy n=26) | description 1 verbatim / 25 paraphrased / 0 lost; agentId kept 4 of 20 | IDs 3/15 | IDs 1/5 | The task survives; the **ID is lost**. Harness re-injects `task_status` attachments (ID, description, output file) after 7 compactions |
| 7 HANDOFF OWED | present 5, lost 5, not owed 8 | **5 present / 1 lost** | 0 present / 4 lost | **The one item where CI clearly works** |
| 4 Bridge | mentioned in 9/9 segments that used the bridge | 4/4 (+2 stated unprompted) | 5/5 | Kept (paraphrased) |
| 6 Uncommitted paths (proxy n=2) | 1 present / 1 lost | 1/0 | 0/1 | Too few cases to call |
| 2 Unfiled lessons | unmeasured (no reliable marker for a lesson that was not filed); 11/18 summaries mention lessons at all | 8/11 | 3/7 | UNMEASURED |

What happened after (proxies, labelled as such):
- Re-asking the owner: 8 question-card calls in the 400 records after a compaction. None has a token Jaccard of 0.35 or more against any owner message or card from before the compaction. **0 re-asks detected.**
- Redoing work: 2 identical non-trivial Bash commands re-run (both `date`); 2 helper launches with similar descriptions, both checked by hand and found to be new work ("Run FlowWorks live pass 3" after pass 2). **0 real redos detected.**
- User-level `~/.claude/CLAUDE.md` after compaction: **re-injected.** In 12 of 12 compactions where the session went on to another model request, an `instructions` attachment carries `User` (`/home/mandrake/.claude/CLAUDE.md`, the full 17,225 chars), `Project` (re-read from disk, so it picks up edits made mid-session: 22,345 to 23,038 chars) and `AutoMem` (MEMORY.md). The other 6 compactions were followed by fewer than 30 records (the session ended). The harness also re-attaches `invoked_skills` (the full text of skills loaded earlier), `compact_file_reference`/`file` (recently read files) and `task_status` (running agents).

Failure examples (Part A):
- aee88c33 (BENCH, auto, 491k tokens): an owner art ruling, *"The rail-ladders have issues: North needs to hug the wall perspective tighter and come up along the wall (compress north/south perspective direction)."*, is gone from the summary; the word "ladder" does not appear in it at all. The open `OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL` with its "NEXT: rerun the pile proofs from the start at the next game-up" is also lost ("pile" does not appear in the summary).
- b833ee96 (FOUNDRY): `DONOR_DEFS_PORT_TO_OURS_1` was shortened to `DONOR_DEFS_PORT`, and `HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP` became "health metrics code", so a resumed seat cannot grep the ledger for either.
- 306 of 316 verbatim owner quotes carry no date (the "All user messages" list has no timestamps).

## Part B — controlled probe

Setup (scripts in `D:\ClaudeWork\scratch\compaction_probe\partB\`): `gen.py` writes a synthetic 53-record BENCH-like transcript (about 283 KB, roughly 65k tokens; real design docs read as filler) straight into `~/.claude/projects/<probe dir>/<uuid>.jsonl`. It plants 5 owner rulings (genuine `origin.kind=human` messages on three different days, with `date` tool calls marking each day), 5 `ID — open; NEXT:` pointers, 3 background Agent launches (agentId and output path), a loaded skill whose rule is "end every rimflow note with [lgr-7]", an uncommitted design path, an unfiled lesson (shortHash), no HANDOFF READY, and a correction that reverses who holds the bridge (FOUNDRY, later BENCH, for the sluice proof). Two copies are compacted: `run_ci` (the probe CLAUDE.md includes the repo's Compact Instructions verbatim) and `run_noci` (no Compact Instructions). Each is then quizzed with the fixed `quiz.txt` (JSON answers, tools disabled) and graded by `grade.py` with exact string matching. The summary text is graded the same way. Sanity check: `grade.py` scores a hand-written perfect answer 31/31 and an empty one 0/31.

Results (one run per arm, n=1 each; opus `claude-opus-5-5`; compaction triggered headless with `claude -p --resume <id> "/compact"`, hooks disabled with `--settings '{"disableAllHooks":true}'`, tools disabled):

| Item (CI #) | with CI: summary | with CI: quiz | no CI: summary | no CI: quiz |
|---|---|---|---|---|
| 3 owner quote verbatim | 5/5 | 5/5 | 5/5 | 5/5 |
| 3 ruling date | 5/5 | 5/5 | 0/5 | 1/5 |
| 1 NEXT item ID (exact) | 5/5 | 5/5 | 5/5 | 5/5 |
| 1 NEXT action | 5/5 | 5/5 | 5/5 | 5/5 |
| 5 helper agentId | 3/3 | 3/3 | 0/3 | 0/3 |
| 5 helper output path | 3/3 | 3/3 | 3/3 | 3/3 |
| loaded skill's rule ([lgr-7]) | 1/1 | 1/1 | 1/1 | 1/1 |
| 6 uncommitted path | 1/1 | 1/1 | 1/1 | 1/1 |
| 4 bridge holder after the correction | 1/1 | 1/1 | 1/1 | 1/1 |
| 2 unfiled lesson | 1/1 | 1/1 | 1/1 | 1/1 |
| 7 HANDOFF OWED (literal line) | 1/1 | 1/1 (yes) | 0/1 | 1/1 (inferred) |
| **Total** | **31/31** | **31/31** | **23/31** | **24/31** |

- Without CI, the quiz answered **2026-10-26 for all five rulings**: confidently wrong for four of them. With CI, the summary has a dated rulings block (for example `2026-10-24 (between 19:08 on 10-24 and 10:14 on 10-25): "Kelp beds never..."`).
- Without CI, all three agentIds were dropped. Claude Code's own Agent result text says `agentId: ... (internal ID - do not mention to user...)` (the same wording appears in real seat transcripts), and that wording pushes the summariser to leave the ID out unless CI asks for it.
- The mid-session correction survived in both arms. The summaries even record the earlier wrong claim and its fix.
- After compaction the harness re-attached `instructions` with `User` (`~/.claude/CLAUDE.md`, 18,407 chars) and `Project` (the probe CLAUDE.md). The synthetic skill was **not** re-attached as `invoked_skills`, because it was never registered through the harness. Its rule survived only through the summary text. Real seats do get `invoked_skills` re-attached (Part A).
- Caveat: the probe history is about 65k tokens of content compacted into a 7 KB summary. Real seats compact 215k–588k tokens into 8–24 KB, so the probe is an easy case. Part A shows the same CI items degrading at real sizes: 52% of open IDs kept, 4/20 agentIds kept.

Real cost (list price, from `total_cost_usd`; the quiz call reports the session's running total, so each quiz is the difference): compaction $0.58 (CI) + $0.56 (no CI) at about 121k input tokens each; quiz about $0.15 + $0.14. **Total about $1.43.** Part A cost no model tokens.

## Failure examples
See the Part A failure examples (the rail-ladder ruling was lost; the pile NEXT was lost; IDs were shortened) and the Part B no-CI arm (every ruling dated "today"; all agentIds dropped).

## Recommendations
1. **Keep Compact Instructions.** They are the only measured cause of HANDOFF OWED surviving (real: 0/4 before CI, 5/6 after; probe: 0/1 without, 1/1 with). In the probe they also kept ruling dates (0/5 without, 5/5 with) and agentIds (0/3 without, 3/3 with).
2. **Open items must live on disk, not in the summary.** At real sizes only 52% of open item IDs survive exactly, and some come back shortened so they can no longer be grepped. A SessionStart(`compact`) hook that injects `rimflow next --seat <SEAT>` would restore them from the ledger at no model cost.
3. **Owner rulings need a dated on-disk record.** Real summaries quote the owner verbatim (93%, because the built-in "All user messages" section does it) but date only 3% of the quotes. Without that record a resumed seat stamps old rulings with today's date. Rulings should be written, with date, where they are executed (ledger `--owner-said`, the handoff), and the owner's verbatim words should not depend on the summary.
4. **Running helpers: rely on the harness `task_status` re-attachment plus a seat-side registry.** Summaries keep what a helper is doing but rarely its ID (4/20 real), partly because the harness labels the ID "do not mention to user". A small on-disk helpers file (id, task, output path), re-injected by the same hook, closes the gap.
5. **Not a gap:** `~/.claude/CLAUDE.md` (user level) is re-injected in full after every compaction that is followed by another request (12/12 real, 1/1 probe), along with the project CLAUDE.md re-read from disk, MEMORY.md, invoked skills and recently read files. No re-asking of the owner and no redone work were detected after real compactions (these are proxies; see Part A).
6. Unfiled lessons were not measurable in real transcripts. In the probe they survived both arms, so the safe rule stays: file a lesson when it is learned.

## Filed
`COMPACTION_RESTORE_OPEN_ITEMS_FROM_LEDGER`, `OWNER_RULINGS_HARDEN_DATES_ON_DISK`, `HELPER_IDS_RESTORE_AFTER_COMPACTION` (all --for BENCH, needs offline).
