# RIMMANDRAKE_FREE_DEAD_OWNER_DRIVER_LOCK_BLOCKS_EVERY_TAKE

## spec
Measured 2026-11-16 06:55 PST on Archmagi. The Conductor took the bridge in the owner's name for his Gimme Some
Slack review-map walk (OWNER driver lock, wsl pid 2227933, gen 1479). He said "ok, I'm done"; the hold was
released twice (`rimflow bridge release --owner-said "ok, I'm done"`, the second with --force). Then:
- `bridge who`: `driver lock: STALE OWNER 2227933 gen 1479 (holder process pid 2227933 gone)` and `bridge FREE`;
- `bridge take --idle-ok` refuses: "the OWNER holds the driver lock", takeable only 45 min after his last
  interaction (which keeps moving while he chats); --force does not override it;
- `bridge release`: "only the holder releases it" - the driver lock stays.

Cause: `_bridge_release_write` frees the driver lock only when this process holds it, and the driver-lock owner
gate (`cli._driver_owner_gate`, `host_guard._owner_gate`) knows only the 45-min clock, not his deliberate release
("45 minutes after my last interaction, or I deliberately release it", owner by card 2026-10-30).

## criteria
(a) An OWNER driver lock whose holder process is gone, with an OWNER bridge `released` event carrying his words
(ownerSaid / byCard, or his own hands) written after the lock was acquired, does not refuse a take (cli and
host_guard). (b) `bridge release` with his words clears an OWNER driver lock whose holder is dead. (c) Unchanged and
still tested: an OWNER hold he has not released, or one whose holder process lives, refuses a take and --force until
45 min after his last deliberate interaction.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_owner_hold selftest_bridge_lock_owner_holes` plus the
new cases; live: the real lock 2227933 gen 1479 cleared by the fixed release, `rimflow bridge idle --for check`
reads takeable.

## refs
file: src/RimMandrake/rimflow/cli.py
file: src/RimMandrake/rimflow/host_guard.py
file: src/RimMandrake/rimflow/owner_interaction.py
