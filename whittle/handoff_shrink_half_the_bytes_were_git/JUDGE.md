# Judge: HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT (fresh blind judge, 2026-11-12 00:05 PST, at e4da6e13f6)

Read: STATEMENT.md, NOTES.md, the item file `infrastructure/state/items/HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT.md`
(spec/verify/criteria), and every file in `evidence/`. Did not read DONE.md, BROADEN.md, STALLED.md or PROMPT.md.
I also ran the work myself; outputs are in /tmp/judge2/.

## Statement line 1: "done as the item file says, shown by fresh evidence" — TRUE

Each requirement in the item file, with what shows it:

- **Half 1, the wake prints only the listed parts** (last reply, one thing to carry, what the owner should see, half-done,
  pointer lines with live ledger state, game/bridge state, full path), and drops commits, closed/filed and uncommitted
  while the file stays whole. I ran `RIMFLOW_SEAT=BENCH handoff.py --wake` (/tmp/judge2/wake.txt, 71 lines, exit 0). Its
  only sections are those four plus the last reply and the POINTER STATUS block. A "Left out of this view" line gives
  the full path and lists Traps / Closed / Filed / Commits / uncommitted as dropped. A grep for commit or uncommitted
  sections finds none. `half1_bytes.txt` shows the file is untouched on disk (8531 B whole, 3717 B shown).
- **Half 2, a generator writes a one-screen file holding open items, owner-pending items, live helpers and NEXT.**
  `ledger_state.py` writes `infrastructure/state/derived/state_now/<SEAT>_STATE_NOW.md` (gitignored by .gitignore:227).
  I regenerated it: 41 lines, widest 120 columns, the four sections in order. It matches the evidence copy except for
  the generation stamp.
- **Its numbers are real; I checked each one against another instrument:**
  - Open items: 1826 for BENCH. `rimflow queue BENCH` lists exactly 1826 distinct item headings, and the state counts
    add up to 1826.
  - Owner-pending: 17, plus 10 answered. `owner_queue.py` gives "17 truly his" and "10 answered", and the 7 rows shown
    plus "9 more" make the 16 topics.
  - Live helpers: 0. A zero needed a probe, so I wrote my own `model.replay` lease check (/tmp/judge2/probe_leases.py).
    It found 41 lapsed and 8 released leases. The newest expired at 07:01Z, and the time now is 08:01Z. The selftest
    also shows the section can see live leases (2 shown, and a released one excluded).
  - NEXT: I spot-checked `HARNESS_REPAIR_CAUSE_C1B99C19` with `rimflow show`. Its newest NEXT is at 06:19Z, followed by
    two later events (a reassign and a note). That matches "⚠ 2 later events".
  - The game-up stamp: a read-only Windows process list shows the game process running, so the stamp is true.
- **Verify: the selftest builds a test ledger (`RIMFLOW_LEDGER`), checks each section, and checks the 50-line limit.**
  `selftest_ledger_state.py` writes its ledger through the real CLI with `RIMFLOW_LEDGER` set to a temp dir (line 40).
  Its checks cover all four sections and one screen (34 lines; a 400-item stress ledger gives 42 lines).
  `run_selftests.py --only selftest_handoff selftest_ledger_state` gave PASS 2/2, GREEN (/tmp/judge2/selftests.txt).
  `mutations.txt` lists 31 deliberate breakages, and the tests catch every one, so the checks can see what they claim
  to see.
- **Criteria: under 50 lines on the live ledger, regenerates without a human, and `--wake` points at it.** It is 41
  lines on the live ledger. My own wake rewrote the file: its generated stamp moved from 23:58 to 00:01 with no other
  step. The last line of the wake's pointer block names the absolute path of the file. Wake callers include
  `rimflow/seat_restart.py`, so a restart regenerates it without anyone asking.
- **The code is reviewed and landed.** `code_review_status.py check` says CLEAN for handoff.py, ledger_state.py and
  both selftests. HEAD e4da6e13f6 is an ancestor of origin/main, and src/ has no uncommitted changes.

## Where the evidence is tidy or weaker than it looks (none of it changes the verdict)
- `CLAUDE_ARCHMAGI_OFFLINE3_STATE_NOW_live.md` is an idle subject: the seat has 1 open item and 1 NEXT. The BENCH file
  (1826 items) and the 400-item stress ledger are the real tests of the one-screen limit, and both hold.
- `regeneration.txt`: the ledger write between its two wakes re-wrote the same NEXT text ("fresh blind judge"). Only the
  stamps changed, so it proves the file is rewritten, not that new content appears. The selftest's "regenerated from
  the ledger as it is at the wake" check and my own run cover that gap.
- `fresh_reader_round1-3.md` were read at older commits (round 3 at d7ff8762de), not at HEAD. They show the view is
  usable. They are not evidence about the final code.
- Half 1's byte figures do not match the item's. The item recorded 14141 B before and 9217 B after for
  BENCH_REBOOT_HANDOFF_202611071817.md. That file has only ever been committed at 12351 B (one commit, 0bcd731141),
  and its view now measures 6785 B. The evidence states this mismatch openly. Half 1 was already marked DONE in the
  owner's spec, so this is a note, not a defect.
- The live state file stamps the game and bridge as up and held by CLAUDE_ARCHMAGI_FWLIVE, while the handoff in the
  same wake says NOT RUNNING. The wake labels the handoff's section "as at the handoff", and the live stamp is true
  now, so this is correct.

would show: yes
