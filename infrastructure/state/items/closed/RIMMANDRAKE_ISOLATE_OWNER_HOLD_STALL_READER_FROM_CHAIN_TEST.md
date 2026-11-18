# RIMMANDRAKE_ISOLATE_OWNER_HOLD_STALL_READER_FROM_CHAIN_TEST

## spec
`selftest_mod_owner_hold.py` is red on origin/main 0a46880422 (publish door: PRE-EXISTING RED): `test_stall_reader
raised FileNotFoundError: .../selftest_dispatcher_XXXX/state/state.json`. Measured: `test_stall_reader` passes alone;
run after `test_designer_chain` (which runs selftest_designer_chain's fixture and leaves `RM_DISPATCHER_STATE` naming a
temp dir it removed), `ops_watch._q_designer`'s `chain_capped` opens `$RM_DISPATCHER_STATE/state.json` and raises.
The reader is right to raise on an unreadable state (blind, not calm); the test is not isolated.

Fix: `test_stall_reader` gives `_q_designer` its own `state_file` (a temp dispatcher state with an empty roles
object). Its assertion is unchanged.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_mod_owner_hold.py` exits 0 (watched failing on base
7420c5bb76: "1 FAIL", the FileNotFoundError above).

## criteria
- The whole file passes; test_stall_reader's check is unchanged.

## refs
file: src/RimMandrake/rimflow/selftest_mod_owner_hold.py
