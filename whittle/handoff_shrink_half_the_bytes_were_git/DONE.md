# Done claim

- true: Wake prints only next actions, open items and the last reply; then a one-screen state file generated from the ledger is done as `infrastructure/state/items/HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT.md` says, shown by fresh evidence. | evidence: `whittle/handoff_shrink_half_the_bytes_were_git/evidence/wake_BENCH_live.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/BENCH_STATE_NOW_live.md` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/wake_CLAUDE_ARCHMAGI_OFFLINE3_live.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/CLAUDE_ARCHMAGI_OFFLINE3_STATE_NOW_live.md` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/half1_bytes.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/regeneration.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/selftest_ledger_state.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/mutations.txt` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/staged_overtaken_next_STATE_NOW.md` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/fresh_reader_round1.md` `whittle/handoff_shrink_half_the_bytes_were_git/evidence/fresh_reader_round2.md`

How each part of the item reads in the evidence (all at eb4690e8ff, the last code change):
- Half 1: `half1_bytes.txt`. The wake's view of the live BENCH handoff keeps the one thing to carry, what the owner should
  see, what is half-done and game/bridge, and drops traps, closed, filed and commits (the file stays whole: 8531 bytes
  against 4335 viewed). The item's own measuring file re-measures at 12351 against 7403 bytes. The last reply is the top
  of `wake_BENCH_live.txt`; the pointer lines carry live ledger state; the handoff's full path is printed.
- Half 2, generator: `src/RimMandrake/Utils/ledger_state.py` writes `<state>/derived/state_now/<SEAT>_STATE_NOW.md`
  (gitignored) beside the ledger in use.
- Half 2, the four sections: open items (this seat's), owner-pending (owner_queue's answer, every seat), live helpers
  (unexpired leases, every seat), NEXT lines (the newest `NEXT:` in a ledger note per open item, with its standing, date,
  writer and a ⚠ when the ledger has moved since). See `BENCH_STATE_NOW_live.md`.
- Selftest on a `RIMFLOW_LEDGER` test ledger written by the real CLI checks each section for what must and must not be
  there and the one-screen bound: `selftest_ledger_state.txt`, 31 checks, 0 failures, plus `run_selftests.py --only` GREEN. Twelve
  deliberate breaks each fail it: `mutations.txt`.
- Criteria: under 50 lines on the live ledger (BENCH, the busiest seat with 1819 open items: 45 lines, at most 120 columns;
  a worker seat: 27). It regenerates without a human: every `handoff.py --wake` writes it (`regeneration.txt`, two
  ordinary wakes around a real ledger write, so the second shows the new NEXT). `--wake` points at it: the
  `LEDGER STATE NOW …: <path>` line under the pointer block, with a `now:` line giving game and bridge as the ledger has
  them.

## What I'm least sure about
- "One screen" assumes a 120x50 terminal. On 80 columns the long rows wrap and the file runs past a screen.
- A NEXT is the action as its writer put it. The file marks a cut action (…) and a NEXT the ledger has moved past (⚠),
  but it cannot tell whether the action still holds. Both fresh readers handled that correctly, by opening the item.
- "Live helpers" is unexpired leases. A worker that died with its lease still shows until the lease lapses (45 min).
  The heading says so.
- The header's `bridge` is the Archmagi bridge (the ledger's default host); a SteveDesktop game's bridge is not in it.
- Owner-pending reads the Relentless store and Designer turns as well as the ledger, as the status board does, so it
  agrees with the board. If the Designer store cannot be read, owner_queue adds a `DESIGNER_TURNS_UNMEASURED` row rather
  than staying silent. With no Relentless store, its holds filter nothing. Neither case is tested here.
- `code_review_status.py` still marks the four files DIRTY. One full review found seven issues, all fixed and each now a
  selftest check. Nobody has done a second, clean review pass that would mark them clean.

## What I did not test
- A wake on SteveDesktop or the Mac (another `agent storage`, another TZ): the TZ case is tested in the selftest; the
  machine is not.
- The Windows Terminal profile's own wake prompt launching `handoff.py --wake` in `/home/mandrake/rm/bench`. I ran the
  same command in this clone on the same live ledger, but not from that profile.
- A ledger read failing mid-wake. The code prints `LEDGER STATE NOW: UNMEASURED (<error>)`, but no test forces that path.
