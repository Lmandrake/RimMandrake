> HISTORY: retired era, see design/RimMandrake/retired_eras_index_2026-11-18.md. This file's mentions of Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 are history (that machinery no longer runs); the rest is as current as its own status says.

# Replay: how much of a large file read does a session use later?

Item: `RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS`. Tests the hypothesis
`RIMMANDRAKE_DIGEST_BIG_READS_WHOLE_FILES_FILL_HALF` in `00-hypotheses.md`: large file reads are about half of
all tool text brought into helpers' contexts, and much of it is never used.

## For the owner (2026-11-19, 3:06 AM PST)

- Large file reads are not half of all tool text. They are 36% [measured].
- The earlier "half" was a counting fault. A copy of each request repeats its tool results. The old count
  took 9.6 million characters twice. I fixed the tool and the three files that used the number.
- Later turns quote, edit or name only 13% of the lines in a large read [measured]. So most of it is never
  quoted. But a reader can use a line without quoting it, and my test cannot see that.
- Second readers make 94% of the large reads. You ordered them to read whole files. I do not recommend a change.
- All other helpers made only 25 large reads in 25 hours. They cost at most about 3.4 million weighted tokens,
  about 1% of helper spend.
- Reading by part would not help much. The lines that a session uses are spread through the file. Blocks of 100
  lines that hold them make up 82% of the file.
- My recommendation: make no rule about large reads. The saving is too small, and the risk sits with second readers.

## Written before measuring (2026-11-19, 2:48 AM PST)

- **Population.** The same transcripts the earlier run read: helper sessions under
  `~/.claude/projects/*-rm-relentless-clones-*-det/`, last written between 2026-11-18 00:00 PST and 2026-11-19
  00:50 PST. Sidechain (subagent) lines are left out, as before. A tool result is counted once by its id, so a
  resumed session's copied history is not counted twice. Sanity probe: the population must give back the earlier
  figures (106 sessions, 923 `Read` results, 50.1 million tool-result characters) within 2%, or it is a different
  population and I say so.
- **A large read** is a `Read` result over 20,000 characters (the line the earlier run used).
- **Used.** A line of the read counts as used if a later assistant block in the same session (its text, or the
  input of any tool call it makes: an edit's old text, a command, a search pattern, a file it writes) contains 30
  characters of that line in a row, or the whole line when the line is 15 to 29 characters long. A line also counts
  as used if it holds a name (an identifier of 8 or more characters with `_`, `.`, `/` or a capital inside it) that
  appears nowhere in the session before the read and does appear in a later assistant block. Lines under 15
  characters, and lines that repeat in the same file, are not testable and are left out of both sides.
- **Reported:** the share of testable characters used, over all large reads; the share of large reads with no used
  line at all; and the share a read by part would have brought in (the 100-line blocks that hold every used
  line), as a ceiling on what reading by part could save.
- **A separate class:** reads by a second reader, that is, a session whose brief tells it to read files in full,
  to the end, or as a second or fresh reader. The owner ordered those reads whole. They are counted apart and are
  not a candidate for trimming, whatever their share.
- **FOR the hypothesis:** large reads are at least 40% of tool-result characters, and under 30% of their testable
  characters are used later.
- **AGAINST:** large reads are under 30% of tool-result characters, or over 60% of their testable characters are
  used.
- **Between those lines** I report the numbers and claim neither.

## Two instrument faults, found and fixed before the counts

1. **The earlier figure counted 9.6 million characters twice.** The sanity probe failed first: this population
   gave 104 sessions, 581 `Read` results and 40.5 million characters, against the earlier 106, 923 and 50.1
   million. Counting the earlier way (every transcript line that holds a tool result, any line type) gives exactly
   50.1 million and 923 [measured]. The gap is the `api-request-blob` lines: they repeat tool results already in
   the session, 9.6 million characters in all. Counted once by `tool_use_id`, `Read` carries 40.5% of tool text,
   not 49.4%, and `Bash` carries 59.3%. I fixed `tools/what_fills_context.py` (each result once, and an `--until`
   bound) and corrected the figure in `00-hypotheses.md`, `01-context-rent.md` and `99-morning.md`. I did not
   trace why this run counts 104 sessions and the earlier one 106.
2. **A shared phrase made every line "used".** A planted session (`tools/selftest_large_reads.py`) gave 400 of
   400 lines used where 2 were. Its lines shared a 30-character phrase that a later quote held. A 30-character
   run now counts only if no other line of the same read holds it. The planted test then passes 4 of 4: a quote
   and a new name are found; a quote made before the read, a name seen before the read, and no later use are not.
   On the real data the used share fell from 16.5% to 13.0%. I also left out lines with fewer than 10 letters or
   digits (table rules like `|---|---|`, which matched by chance).

## Method

- **Population.** Helper transcripts under `~/.claude/projects/*-rm-relentless-clones-*-det/`, last written on
  or after 2026-11-18 00:00 PST, with every line stamped after 2026-11-19 00:50 PST left out (the earlier run's
  cut). 104 sessions. Sidechain lines and `api-request-blob` lines are skipped; each tool result counts once.
- **Large read:** a `Read` result over 20,000 characters. 393 of them, 14.5 million characters. 71 of the 393
  already used `offset` or `limit`.
- **Used:** as written before measuring, with the two fixes above. The match runs over the session's later
  assistant blocks: text, and every string in a tool call's input (an edit's old text, a command, a pattern, a
  written file). A "quote-only" figure leaves out the name rule.
- **By part:** the 100-line blocks of the read that hold at least one used line, as a share of the read's
  characters. That is the least a read by part could have brought in, if the session had known where to look.
- **Second reader:** the session's brief matches `second reader`, `fresh read`, `read in full`, `read it whole`
  or `READ_IN_FULL` (28 sessions with a large read; the matched phrases are in the tool).
- **Tokens [model].** A read's entry cost is the next request's cache write, shared among what entered since
  the last request by characters, weighed at the 1-hour write price. Its rent is that many tokens re-read at the
  cache-read price on every later request, until the context drops by half (a compaction). Each request is read
  once, so resumed sessions count once. The entry figure is an upper bound: it comes to 0.45 tokens per
  character, while requests that took in one large read and nothing else show 0.42 at the median and 0.36 at the
  lowest tenth [measured, 169 requests]. The write also carries the previous turn's thinking.

## Counts [measured; tokens are the model above]

| class | large reads | characters | lines used later | quote only | reads with nothing used | 100-line blocks needed | entry + rent |
|---|---|---|---|---|---|---|---|
| all | 393 | 14.5M | 13.0% | 10.7% | 7 (2%) | 82% | 25.6M + 17.1M weighted |
| second-reader sessions | 368 | 13.6M | 12.0% | 10.0% | 7 | 82% | 24.4M + 14.9M |
| other sessions | 25 | 0.9M | 27.2% | 20.9% | 0 | 87% | 1.2M + 2.2M |
| other, design files | 9 | 0.3M | 14.1% | 9.3% | 0 | 81% | 0.6M + 0.8M |
| other, not design | 16 | 0.6M | 35.6% | 28.4% | 0 | 90% | 0.7M + 1.4M |

All tool text was 40.5 million characters, so large reads are 35.7% of it. Detached helper spend in the same
window was 310 million weighted tokens (`01-context-rent.md`). Large reads cost at most 42.7 million of that
(14%), and 39.3 million of it is second readers' reads.

**Against the lines written before measuring.** FOR needed a share of 40% or more and under 30% used. AGAINST
needed a share under 30% or over 60% used. The share is 35.7% and the used part is 13.0%, so the result falls
between the lines, and I claim neither. The second half of the claim ("much of it is never used") is supported
by the quote test. The first half ("about half of all tool text") is not.

## Blind spots

- **Use without quoting is invisible.** A reader who reads a design to judge it, or reads code to understand
  a call, uses lines it never repeats. This is the main job of a second reader. Their 12% is a floor, not a
  measure of waste. The same holds for the 0% and 3% reads of design specs in other sessions.
- **Thinking is not in the transcripts.** Thinking blocks are stored empty, so a line named only in thinking
  counts as unused.
- **Paraphrase is missed.** A session that restates a line in its own words does not match.
- **A false match is still possible** when a 30-character run of a line happens to occur later for another
  reason. The uniqueness rule cuts this. I did not measure the rate on real data.
- **"By part" assumes the session knew where to look.** Finding the parts costs a search, which this does not count.
- **One day.** 25 hours, 104 sessions, and a night in which second readers were a large share of the work. Another
  week's mix may differ.

## What I would and would not do

- **Would not** limit large reads by second readers. He ordered whole reads. He has already caught trimmed
  readings (`RIMMANDRAKE_CHECK_RESUMED_READERS_PAGES_FOR_TRIMMED_READING`), and my test cannot see their use.
- **Would not** build a digest step or a size rule for other helpers. Their large reads cost at most about 1% of
  spend. Reading by part would still bring in about 87% of it.
- **Would** count tool text once by `tool_use_id` in every future measure of context. The earlier double count
  moved a headline from 36% to "half".
- **Would** look next at `Bash` output, if anything. It is 59% of tool text, and 15% of it sits in results over
  20,000 characters. I did not measure how much of it is used.

## Files

- `tools/large_reads.py`: the replay. `tools/selftest_large_reads.py`: its planted test (4 of 4; seen red before
  the uniqueness fix).
- `tools/what_fills_context.py`: fixed to count each tool result once.
- Scratch, not committed: `D:\ClaudeWork\scratch\replay_two_hypotheses_20261119\large_reads.json` (one row per
  `Read`) and `large_reads.txt` (the printed table).
