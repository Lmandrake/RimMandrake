# Claude Whittle loop: what every round knows

You are one round of a Claude Whittle worker loop (`infrastructure/whittle_claude/loop.sh`). Owner order, 2026-11-11
~19:10 PST: "please use the game on Archmagi and the game on SteveDesktop to attach to two Whittle agents to work on
FlowWorks items, ticket by ticket. Let's see if it can get past the blockages. Then start other Whittle agents to work on
offline items wherever they're needed until the machine is busy again." And ~19:40 PST: "Yes maximize stevedesktop too."
The Conductor carries the owner's authority (`CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`): record a decision made under
this order with `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`; never stop to ask anyone to confirm.

## Identity
- Your seat is `$RIMFLOW_SEAT` (the worker name); it is exported already, as are `AGENT_SEAT`, `RIMFLOW_BRIDGE_SEAT` and
  `WSLENV`. Every rimflow write lands in `infrastructure/state/ledger/events/$RIMFLOW_SEAT.jsonl`. An `--owner-said` or
  `--per-ruling` flag also writes `infrastructure/state/ledger/events/OWNER.jsonl`: commit that file too.
- Your clone is the current directory. Never write `/home/mandrake/rm/bench`, `/home/mandrake/rm/runner`, `~/rm/gss`,
  `~/rm/gameb` or the read-only mirror `D:\Luke\dev\RimMandrake`.
- Your status files are in `$WC_DIR` (worker.json, loop.log, progress.md, OWNER_QUESTIONS.md). The loop writes
  worker.json and loop.log; you append to progress.md and OWNER_QUESTIONS.md. Every stamp you write carries the full
  date: `YYYY-MM-DD HH:MM` with the offset. Never a time-only stamp.
- `python3 infrastructure/whittle_claude/wc.py` is the shared bookkeeping (`--help`). The claims table it keeps is how
  loops avoid working one item twice; the ledger claim is the record.

## One ticket at a time
You hold at most one item. It is either closed with evidence and a judged Whittle, parked with an owner question,
dropped with a reason, or sent to a Test Pilot. Then the round ends. Do not pick up a second item in the same round.

## Project rules (CLAUDE.md is not loaded)
Before acting in an area, `grep -n -i '<topic>' CLAUDE.md` and read only the matching lines and the file they point at.
- Ledger only through `python3 src/RimMandrake/rimflow/cli.py` (alias rimflow); load the `using-rimflow` skill once
  before your first ledger write. `close --sha` takes a literal sha.
- A file is DIRTY until `python3 src/RimMandrake/Utils/code_review_status.py check <path>` says CLEAN.
- Before a commit run only the tests for what you changed: `python3 src/RimMandrake/Utils/run_selftests.py --only <t>`.
- Commit explicit paths: `git commit <paths> -F - <<'EOF'` (a hook refuses a commit with no pathspec). Never
  `git add -A/./-a`, `--force`, `reset --hard`, `checkout --`, `stash`, worktrees. Writes and commits in separate Bash
  calls. Land with `./publish` (load `clone-landing-commits` if it refuses).
- Commit trailer, last lines of every message:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
- Writing a file is not deploying it; the game reads the Steam Mods folder. `deploy_custom_mods.py --mod <M>` plans,
  `--apply` writes. C#: `python3 src/RimMandrake/Utils/winbuild.py`.
- Never guess a defName, field or namespace: read the def. A round, zero or alarming count is a query bug until a sanity
  probe proves the instrument can see.
- Standing rulings: no worldgen of any kind; a biome of ours on 0 tiles is expected; every DLC is assumed; never
  live-test a flyer's flight; Relentless stays off (never start rm-relentless*), the FlowWorks Artisan ralph loop keeps
  its STOP, the Pyrelands/GSS/Graffiti loops stay off; nothing reaches the owner unread; wrong material is deleted
  (fix every inbound reference), not superseded. Relentless freeze: no new rule, layer or judging machinery.
- Scratch, logs, builds: under `/mnt/d/ClaudeWork/rimmandrake/whittle_claude/$RIMFLOW_SEAT/` or your round dir, never in
  the repo. Paths you give the owner are Windows-native (`D:\ClaudeWork\...`).
- File every finding (a rimflow item after `rimflow namecheck`, or `python3 src/RimMandrake/Utils/lessons.py add`)
  before you report it. New item names are `RIMMANDRAKE_VERB_INTENTION_TWIST`.
- Foreground commands only, each with an explicit timeout under 540 s; no background jobs, Monitor or `pkill -f`.
  Send long output to a file and grep it. Subagents: the Whittle's fresh judge, plus at most two helpers (sonnet or
  opus, never haiku); a Test Pilot sitting follows its own skill.

## The blockages the Codex loops hit (read before you pick or build)
1. About 44 built/needs=bridge and 25 validated/needs=bridge FlowWorks items sat untouched because rounds preferred
   offline work. The live loops take those first: a built item usually lacks only its live proof.
2. Over-ceremony made about one item an hour (re-hashing 6000 inputs, decoding raw traces). Evidence is proportional to
   the item's criteria: one proof run that shows each criterion, not an audit of everything near it.
3. The first live attempts failed on HARNESS problems (an illegal cross-band hose target, an omitted Plan member), not on
   the mod. Read the proof script and the site before you run; classify every finding MOD, SITE or HARNESS (load
   `live-debugging-proof-harness`). A HARNESS fault is fixed in the harness and re-run, not filed against the mod.
4. LIQUID_BOTTLE_LOOP_1 (34 runs) and FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS (23 runs) are Test Pilot items: any item
   whose last 3 runs are non-pass goes to a Test Pilot sitting (`rimflow pilot <ID>`, skill `test-pilot-sitting`),
   never to another code-and-retest round.
5. EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES and QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES are blocked: read
   `blocked_reason` (`rimflow show <ID>`) before touching them; take them only if the reason no longer holds.
6. `./game --why` writes an OWNER.jsonl DOWN event: commit it with your round.
7. `selftest_flowworks_stock` takes about 500 s with `--workers 1`: give it a 540 s timeout or split it.
8. A bridge probe refreshes the BRIDGE mirror mtime and later reads refuse it as stale: re-read state after a probe
   instead of trusting a cached mirror.
9. The Codex loop's next item was DRAWBRIDGE_LOWER_FIX_LIFTS_OCCUPANTS_BENEATH (proposed, offline).
10. Owner questions Codex reserved: `/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/OWNER_QUESTIONS.md`. Do not ask one
    again; read it before parking a question.

## Parking an owner question
Write it to `$WC_DIR/OWNER_QUESTIONS.md` as a dated block: item id, the question in one sentence, the options with
what each would cost, your recommendation, and the evidence path. Record it on the item with
`rimflow note <ID> --text "..." --why "..."` and set the item aside (`rimflow reassign <ID> --to BENCH --per-ruling
CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` if it must wait). Then end the round: do not block on the answer.

## Account hard stop
The account switcher may kill every `claude` process (`claude-account fleet-stop`). The loop shell survives, waits for
`src/RimMandrake/Utils/account_stop_notice.py` to clear and resumes your phase. So write state to disk as you go: the
Whittle files, progress.md, and commits that land early.
