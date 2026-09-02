# BRIDGE_OVERRIDE_ATTRIBUTION_GAP_1 — the ledger loses WHO/WHY on an owner give or a forced/stale take

## Where this came from
`/code-review high 7865b643` (FOUNDRY, 2026-09-02) against the bridge-handoff
commit. Two findings fixed already (`c850ad81`): the `write_bridge_file`
race, and CHARTER.md/GAME_STATE_WORKFLOW.md/`./bridge --help` all stating
stale doctrine. These four are left — all in `cmd_bridge`
(`src/RimMandrake/rimflow/cli.py`), all about the SAME root gap: `write_
bridge_file`'s `note=` parameter carries real provenance into the
disposable `infrastructure/state/BRIDGE` mirror that never reaches the
`_emit()` call building the PERMANENT ledger event.

## spec

**1. `bridge give` never marks the ledger event as an owner override.**
`cmd_bridge`'s `give` branch (~line 1214): `ev = {"seat": to, "event":
"bridge", "state": "taken"}` — `seat` is the TARGET window (BENCH/
FOUNDRY), byte-identical in shape to that window taking the bridge itself.
`model.write_bridge_file(to, "OWNER", args.purpose, None, note="handed
over by the owner")` puts the real story only in the mirror, which the
very next `bridge` call overwrites. Compare `DROID_TILES_SOURED_TERRAIN_1`'s
own history (`rimflow show`) — an existing `OWNER unblock`/`OWNER block`
event convention already stamps `override=...`/`ownerSaid=...` on the
ledger event itself when the owner overrides another seat's item. `bridge
give` doesn't follow that convention; it should.

**2. A forced or staleness-triggered `take` has the same gap.** ~line 1254:
`why` ("forced", or "`<holder>` went quiet for N min") is computed, then
only reaches `write_bridge_file`'s `note=`, never the `ev` dict that gets
emitted. `rimflow bridge take --force` while another seat's hold is still
fresh produces a ledger line indistinguishable from an ordinary
uncontested take — a year later, nothing in `events.jsonl` (this module's
own stated sole source of truth) shows that take crossed an active holder.

**3. The `to` positional silently no-ops for `take`/`release`/`who`.**
`s.add_argument("to", nargs="?", help="give only: ...")` — accepted by
argparse for every `bridge` action, only read inside the `give` branch.
`rimflow bridge take BOGUS --for x` exits 0, prints success, and `BOGUS`
vanishes with no error. Argparse's own `choices=`/subparser-per-action
mechanism (already used elsewhere in this file) would make this a real
error instead of a silent no-op.

**4. `_idle_seconds` (line ~1173) reimplements `_epoch` (line ~406) with
different, incompatible failure semantics.** `_epoch` slices `ts[:19]`
against `"%Y-%m-%dT%H:%M:%S"` and returns `0.0` on a parse failure.
`_idle_seconds` requires the full string with a trailing `Z` against
`"%Y-%m-%dT%H:%M:%SZ"` and returns `None` on failure — `None` and `0.0`
are read differently downstream (`_idle_seconds is None` currently reads
as "unparseable -> treat the holder as stale enough to take"). Two parsers
for one timestamp format can silently drift: a future change to the
ledger's timestamp format fixed in one and not the other changes staleness
behavior with no line anywhere near the actual edit.

## verify
- 1 & 2: after fixing, `rimflow show` (or a direct ledger read) on a
  `give`'d or force-taken bridge event shows the override/force fact ON
  THE EVENT, not just in a `rimflow bridge who` printout or the mirror
  file. Confirm the existing `override=`/`ownerSaid=` convention (see
  `DROID_TILES_SOURED_TERRAIN_1`'s history) is the one followed, not a new
  third shape.
- 3: `rimflow bridge take BOGUS --for x` exits non-zero with an argparse-
  style error, not a silent success.
- 4: pick one parser (probably `_epoch`, already used elsewhere) and make
  `_idle_seconds` call it, or document precisely why the two need
  different tolerance/failure values if they genuinely do.

## criteria
`events.jsonl` alone — no mirror file, no stdout capture — is enough to
answer "was this bridge action normal, or an override, and by whom" for
every bridge event past or future, matching this module's own "the ledger
is the truth" design principle.
