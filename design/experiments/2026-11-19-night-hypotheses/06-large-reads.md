# Replay: how much of a large file read does a session use later?

Item: `RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS`. Tests the hypothesis
`RIMMANDRAKE_DIGEST_BIG_READS_WHOLE_FILES_FILL_HALF` in `00-hypotheses.md`: large file reads are about half of
all tool text brought into helpers' contexts, and much of it is never used.

## For the owner

(PENDING: written after the counts.)

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
