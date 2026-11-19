## spec
DESIGN DECISION 2026-11-18 (on RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY): `design/concepts/<Mod>/stage.json` stays the Designer stage machine's own state store. It is not archived and not turned into a generated view; the mod ledger reads it.
- `modledger.packet(root, mod)` adds one line to the packet's head, `Designer step: <0-5> (<status>)`, plus `blocked_on` text when the Designer is blocked, read from stage.json when the packet is made. It never calls the Designer's step a "stage": the pipeline stage is the ledger's.
- The four answers stay apart: a step read · `none (no stage.json)` · `UNMEASURED (<cause>)` for a file that does not parse, is not an object, or has no step 0-5.
- `acceptance/modledger_cutover_accept.py`: `OLD` drops `stage.json` (expected count becomes 3 mods x 3 checks + 1 writer check = 10). This edit is authorized here by the Conductor's delegate; make it after RIMMANDRAKE_NARROW_CUTOVER_WRITER_CHECK_EIGHT_OF_THIRTEEN_READ lands, in the same file.
- Not in this ticket: designer_stage.py's storage. No ledger event is added per stage.json write.

## refs
file: src/RimMandrake/rimflow/modledger.py
file: src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py

## criteria
- The acceptance test passes 15 of 15; `modledger.py lint` stays clean on the three pilot mods; designer_stage.py is unchanged.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_designer_state_accept.py` (15 checks; on b28e0d697, watched: 14 red, 1 green, "making a packet does not write stage.json"). Covers: locked, step 0, blocked with its reason, no file, five unreadable shapes, the head never saying "stage N" for the step, the three real pilot mods, and the cutover test's OLD list.
