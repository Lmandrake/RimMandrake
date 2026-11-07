# HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT

## spec
Two halves. (1) DONE: `handoff.py --wake` prints only the old window's last reply, the one-thing-to-carry, what-the-owner-should-see, what-is-half-done, the pointer lines with live ledger state, the game/bridge state, and the handoff's full path. Commits, closed/filed lists and the uncommitted list are dropped from the wake view; the handoff file itself stays whole. Measured on `BENCH_REBOOT_HANDOFF_202611071817.md`: 14141 bytes before, 9217 after.
(2) OWED: a one-screen state file generated from the ledger, holding open items, owner-pending items, live helpers and the NEXT lines, so a waking window reads ledger state rather than a narrated copy of it.

## verify
Half 2: a generator (rimflow verb or Utils script) writes the file; a selftest builds a test ledger (`RIMFLOW_LEDGER`) and checks each of the four sections, and that the output is at most one screen (about 50 lines). The wake pointer lines then name that file.

## criteria
The generated file is under 50 lines on the live ledger, regenerates without a human, and `--wake` points at it. Leave this item open until then.
