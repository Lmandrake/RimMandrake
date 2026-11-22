# RIMMANDRAKE_STOP_SEAT_DIRT_LANDING_STALE_COPY_OVER_NEWER_ORIGIN

## spec

`seat_dirt.py tidy` lands each safe-class path whole, in a temp index seeded from origin/main. On 2026-11-22 at
00:31 PST the seat clone `/home/mandrake/rm/bench` was 42 commits behind origin and held a dirty
`design/concepts/FlowWorks/ledger/DISPATCH.jsonl` (its old base plus 2 lines that were already on origin). The
FlowWorks concept folder read as settled, so tidy landed that copy as e7be98b0a4. The commit deleted 4 newer
ledger lines from origin (run.end and session.id of run-1795330730, lease.grant token 44 and run.start of
run-1795335550). After that, `selftest_modledger_tree.py` was red on origin (STALE_TOKEN, VIEW_STALE), and that
refused every `./publish`. 4b60b593d6 restored the 4 lines.

The fix: a safe-class path lands only when its landing replaces nothing newer on origin. That is true when origin
has no such path, or origin's copy is the clone's HEAD copy, or origin's copy is a byte prefix of the clone's copy
(an append-only file that origin has not passed). A conversation record (rewritten whole from its transcript) also
lands when the clone's copy changed after origin's last commit of the path. A concept folder with any path that
fails this does not land at all. That path is counted as dirt, so `disk.seat_dirt` names it. `tidy` fetches
before it classifies.

## verify

`python3 src/RimMandrake/Utils/selftest_seat_dirt.py` -> PASS. On the parent (4b60b593d6) it reads 5 FAIL
(watched 2026-11-22).

## criteria

- A concept file whose origin copy moved past the clone's base is not landable and is counted stale.
- An append-only file that extends origin's newer copy still lands.
- A conversation record older than origin's last commit of it does not land. A newer one lands.
- After tidy, origin keeps all its ledger lines and its newer conversation record.
