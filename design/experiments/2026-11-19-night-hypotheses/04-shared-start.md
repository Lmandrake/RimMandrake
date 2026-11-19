# Experiment: do helpers launched from one fixed path share their starting context?

Item: `RIMMANDRAKE_TEST_SHARED_STARTING_CONTEXT_TWO_TINY_LAUNCHES`. Tests the hypothesis
`RIMMANDRAKE_SHARE_STARTING_CONTEXT_ACROSS_RUNS_EACH_REWRITES_IT` in `00-hypotheses.md`.

## For the owner (2026-11-19, 1:30 AM PST)

- The hypothesis is true, but the path is not the only cause.
- When the start of two runs is the same, byte for byte, the second run reads all of it from the cache. Call D
  read 59,445 tokens and wrote 0 [measured].
- A changed path stops the sharing. A changed git status line also stops it. Call B used the same path as call A,
  but one new line in the git status made B write 46,244 tokens again [measured].
- Today, two real helpers that start 29 seconds apart share only 11,266 tokens. The second one writes 50,612
  [measured]. Each helper brings four things that change: its clone path, the git status, its brief, and the
  hook and tool text.
- The smallest change has three parts: one fixed path for every helper (each helper still has its own clone),
  no git status block, and one fixed first prompt that tells the helper to read its brief from a file.
- With that change, about 74% of the start is shared [measured in call F]. I estimate a saving of about
  7 million weighted tokens a day, near 2% of detached spend [guess ~40%].
- The fixed path is the risk. Tools that find a helper by its path will break. I built nothing. The change is
  ticket `RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT`, with its acceptance test.
- Also found: a detached helper of seat BENCH gets the Conductor's identity file at start. That file tells it
  "do not do the work yourself". Ticket `RIMMANDRAKE_STRIP_CONDUCTOR_IDENTITY_HELPERS_TOLD_DELEGATE`.

## Written before running (2026-11-19, 1:14 AM PST)

- **Calls.** Four one-turn calls, `claude -p "Reply with the single word ok." --model claude-sonnet-5-5 --max-turns 1
  --output-format json`, each under `timeout 180`, in the foreground, with the environment this detached run has.
  A and B from this clone's root, one after the other. C from `D:\ClaudeWork\scratch\shared-start-C`, a
  `git clone --shared` of this clone at the same commit (same files, same branch, same recent commits, clean tree).
  D from this clone's root again, after C.
- **Reading.** The `usage` block of each call's JSON: `input_tokens`, `cache_creation_input_tokens`,
  `cache_read_input_tokens`. No usage block, or a non-zero exit: FAILED or UNMEASURED with the cause.
- **Counts FOR the hypothesis:** B reads at least 90% of its prompt from the cache (it writes under 10%), while C
  reads only about the 11,000 tokens every helper shares today and writes the rest; D again reads at least 90%.
- **Counts AGAINST:** B writes more than half its prompt new, as A did (then something other than the path differs
  between two runs from one path: a date, a session id, the hook text). Or C reads as much as B (then the path is
  not what breaks sharing, and the cause is elsewhere).
- **My guess before looking:** B and D read about 95% from cache [guess ~70%]; C reads about 11,000 to 14,000
  [guess ~60%, the same guess as in `00-hypotheses.md`].
- **Side effects to watch.** The repo's and the user's hooks fire on a `-p` session too (SessionStart,
  UserPromptSubmit, Stop, SessionEnd). After A, before B: this clone's `git status`, the Lodestar conversation
  records, and the session's own record are read. A hook that files, syncs or launches stops the experiment.

## Result (2026-11-19, 1:23 AM PST)

**Could the instrument see?** Yes. Every call exited 0, answered `ok` in one turn on `claude-sonnet-5-5`, and
printed a usage block. Each session transcript also records the request itself (`api-request-shape` for tools and
system prompt, `api-request-blob` for each message, `api-request` for the cache markers), so what differed between
two calls was read, not inferred. Calls E and F were added within the brief's six: E and F test whether
`CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` removes the git status block.

| call | path | what differed from the call before | uncached | cache write | cache read | read share |
|---|---|---|---|---|---|---|
| A | this clone | first call | 2 | 48,573 | 11,382 | 19% |
| B | this clone | git status gained A's conversation record; A's hook text had a "what changed" section B lacked | 2 | 46,244 | 13,201 | 22% |
| C | `D:\ClaudeWork\scratch\shared-start-C` (same commit, clean) | path | 2 | 47,886 | 11,382 | 19% |
| D | this clone | nothing: B's conversation record deleted so the git status equals B's | 2 | **0** | **59,445** | **100%** |
| E | this clone, git block off | git block gone; system prompt lost its git instructions | 2 | 47,439 | 11,129 | 19% |
| F | this clone, git block off | git status changed (a probe file added); the `rimsage` MCP server failed to connect (it connected for E) | 2 | 15,109 | 43,505 | 74% |

All six readings [measured], `usage` of each call's JSON, kept in `/tmp/shared-start/{A..F}.json` (a program's
copy; the transcripts under `~/.claude/projects/` are the record). D ran 7 minutes after B: the cache was warm.
A real pair for comparison: two Opus 5.5 detached helpers started 29 s apart at 12:41 AM PST
(`...PROVE-TWO-COVERAGE-JUDGE...` then `...WRITE-REVIEW-BRIEF-CALIBRATE...`): the second read 11,266 and wrote
50,612, a share of 18% [measured: `tools/first_request_share.py`].

**Against the written lines.** B wrote far more than half its prompt new, so the line "B reads at least 90%" is
**against**; but D shows why: B's start was not byte-identical to A's, and D's was identical to B's and read all of
it. C read 11,382, exactly the global part every Claude Code session shares: **for** "the path breaks sharing". So
the hypothesis holds in the strong form "an identical start is read from cache" [measured, D], and the guess that
the path is *the* cause is wrong: the path is one of four causes. My guess "B reads about 95%" was wrong.

**The brief's figure of 68,000 tokens is high.** A helper's whole first prompt is 59,000 to 62,000 tokens
[measured: A–F, and the real pair at 61,880]; 11,000 to 13,000 of it is already shared.

## How a helper's first request is built (Claude Code 2.1.311, read from the transcripts)

In prompt order, with the cache markers (`cacheControl`) the request carries. Sizes: system to the end of block 2
is 13,201 and message 0 about 30,300 and message 1 about 15,100 [measured: B, F]; the split inside message 0 is
[guess ~70%] from character counts.

| part | size | marker | changes between two helpers today |
|---|---|---|---|
| tools (13) and system blocks 0–1 | ~11,400 tokens | `scope: global` | no: read from cache by every session |
| system block 2: style rules and the **memory folder path**, which holds the cwd | ~1,800 | yes | **the clone path** (`<ITEM>.det`) |
| message 0, block 0: both CLAUDE.md files; the project one is headed `Contents of <cwd>/CLAUDE.md` | ~20,000 | no | **the clone path**; the text, when the clones sit at different commits |
| message 0, block 1: email and **git status** (branch, dirty files, last 5 commits) | ~400 | no | **the last 5 commits**: origin/main takes a ledger commit every few minutes; any dirty file |
| message 0, blocks 2–3: attribution, then **the prompt: the brief and its footer** | 1,000–5,000 | no | **always**: item, clone path, task |
| message 1 (role system): SessionStart hook text (identity file, a "what changed while you were away" section keyed to the clone's own sync marker), environment (cwd, model), deferred tool list including which MCP servers connected, MCP instructions, skills list, date | ~15,000 | yes, at its last block | **the cwd**; the "what changed" section; MCP connection luck (`rimsage` connected for E, failed for F, 17 s apart); the date, daily |

Not in the context, so not a cause: the unit name, `--name`, `--settings`, the environment variables the unit sets.
Outside the prompt but deciding sharing: **the model** (a cache entry serves one model; Opus, Fable and Sonnet
starts never share) and **the account** (entries are kept per organisation [guess ~85%]: the three Claude accounts
do not share). The cache life is 1 hour.

A cache read happens only where an earlier request left an entry. The explicit markers are at the end of system
block 2 and the end of message 1. F also read at the boundary between message 0 and message 1 (43,505 tokens) when
message 0 was identical and message 1 was not [measured]; B did not read at any boundary inside message 0 when
message 0 differed in block 1. So: **message 0 must be identical from its first byte for its 30,000 tokens to be
read; message 1 is the 15,000-token tail.** Why F's boundary held an entry is not known [guess ~50%: the server
keeps entries at message boundaries of earlier requests].

**What breaks sharing today, in prompt order:** the clone path (system block 2, the first change, at ~13,000
tokens), then the git status, then the brief, then the message-1 text. Everything after the first change is written
new, so fixing the later causes alone saves nothing.

## The smallest change that lets real helpers share

Ticket `RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT` (filed, not built). All three parts are needed
for message 0 to match; none is useful alone:

1. **One fixed path, one tree per helper.** Each unit runs claude in its own private mount namespace in which its
   own clone is bind-mounted at one fixed path (for example `/home/mandrake/rm/helper`): `unshare --user --mount
   --map-current-user` and `mount --bind <clone> <fixed>`, or the unit's `BindPaths=` if the user manager allows it.
   Untested here: whether the WSL2 kernel and the user manager allow either [guess ~70% that `unshare` works].
2. **No git status block:** `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` on the unit [measured: E's request has no git
   block]. It also drops Claude Code's built-in commit and PR instructions; helpers land with `./publish`, so
   nothing a helper needs is lost [guess ~80%].
3. **One fixed first prompt.** The prompt names a file: "Read your brief at `$RM_BRIEF` and do it." The brief and
   its footer go into that file, so they arrive as a tool result after the shared start.

Optional, for the last 15,000 tokens: a fixed MCP set for helpers (`--strict-mcp-config`, so connection luck
cannot change the text) and no "what changed" section when `RM_ROLE_UNIT` is set.

**What it would save** [guess ~40%; range 4 to 10 million]. The ceiling is measured: first-request cache writes are
14.7 million weighted tokens a day, 4.8% of 309.6 million detached spend (`01-context-rent.md`; that total is from
transcripts, so a resumed run is counted once, not the log's inflated 373.6 million). The three parts make message 0
shared, 74% of a start [measured, F]. A start saves only when a run on the same model and account started in the
hour before: about 70% of starts on a busy night [guess ~60%; Opus starts about 2.7 an hour, Fable about 1.3].
0.74 × 0.70 × 14.4 million = about 7.5 million a day; less about 0.3 million for the extra request that reads the
brief. **About 7 million weighted tokens a day, near 2.3% of detached spend.** With the optional parts, about
10 million. Per start: an Opus helper writes about 50,000 tokens at weight 2.0 (100,000 weighted) and would read
them at 0.05 (2,500); a Fable helper, 200,000 against 2,500 (`MODEL_PRICES`).

## What it risks

**Sharing a prefix is not sharing a tree.** The rule against two helpers in one working tree is about writes: two
agents editing, staging and committing one set of files. Under part 1 each helper still has its own clone and its
own index; only the *name* of the directory is the same, and each name points at a different tree inside a
different mount namespace. No file is shared. Sharing would break that rule only if the fixed path were a real
shared directory, which is the rejected design: a cwd in one common checkout with the work done elsewhere by absolute
paths, where every hook writes through `CLAUDE_PROJECT_DIR` into the common tree.

What the fixed path does break, each to be handled by the ticket:
- `~/.claude/projects/<cwd>/` becomes **one folder for every helper**: transcripts mix (the session id still
  separates them), and the auto-memory folder is shared, so one helper's memory reaches all of them. Today every
  clone's memory folder is its own and empty.
- Every tool that finds a run's transcript or clone by the clone's name: `tools/context_rent.py`,
  `tools/log_runs.py`, `conversations_land.py`, the conversation records (keyed by cwd), `detached_helper`'s
  transcript lookup.
- `scratch_clone.clone_in_use` and `detached_helper.clone_busy` read processes' cwd; inside a namespace the cwd reads
  as the fixed path, so a helper may look absent from its clone and the clone could be reused under it.
- Anything that prints the cwd to the owner shows the fixed path, not the item.
- A failed bind mount must stop the run before claude starts, never fall back to the real path silently (that would
  run two helpers at one real path).

## Side finding: a BENCH helper is told it is the Conductor

The SessionStart hook (`.claude/hooks/set_session_title.py`) injects `infrastructure/agents/CONDUCTOR.md` into every
session whose seat is BENCH, detached helpers included: this run got it, and so did every test call [measured:
message 1 begins `# CONDUCTOR`]. That file says "do not do the work yourself (a subagent does)", the opposite of a
helper's brief. Ticket `RIMMANDRAKE_STRIP_CONDUCTOR_IDENTITY_HELPERS_TOLD_DELEGATE`.

## Tickets and their acceptance tests

**`RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT`.** Acceptance test: launch two one-turn helpers on
the same model through the real launcher, from two different item clones, within 10 minutes, then run
`python3 design/experiments/2026-11-19-night-hypotheses/tools/first_request_share.py <first.jsonl> <second.jsonl>
--min-share 0.7`; pass is exit 0. Seen on today's base: the real Opus pair above exits 1 (share 0.182); A then B
exits 1 (0.222); B then C exits 1 (0.192); B then D, the identical start, exits 0 (1.000); a missing transcript
exits 3; an empty transcript exits 4. (0.7, not 0.9: message 1 is not required to match.) Plus a unit test that a
failed bind mount ends the unit before claude starts.

**`RIMMANDRAKE_STRIP_CONDUCTOR_IDENTITY_HELPERS_TOLD_DELEGATE`.** Acceptance test, run in a clone with
`RM_ROLE_UNIT` and `AGENT_SEAT=BENCH` set as a detached unit sets them:
`echo '{"session_id":"probe-identity-0001","hook_event_name":"SessionStart","source":"startup","cwd":"'$PWD'"}' |
CLAUDE_CODE_SESSION_ID=probe-identity-0001 python3 .claude/hooks/set_session_title.py | grep -c "# CONDUCTOR"`
prints `0` (pass); then `rm -f .claude/session_roles/probe-identity-0001*`. Seen on today's base: prints `1`. The
Conductor's own window (no `RM_ROLE_UNIT`) must still print `1`.

## Side effects of the calls

The hooks did not file, sync or launch anything. Each call left a conversation record in the clone
(`conversations/*.md`, deleted), a role marker in `.claude/session_roles/` (ignored by git) and touched the
`run_end_wake` lock without arming it (only the Conductor window arms). Copy C was deleted after its call.
