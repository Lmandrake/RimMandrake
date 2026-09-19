# Two pre-existing selftest failures, not rename fallout — both repaired

## spec
Two independent selftests were red: `selftest_check_canon.py` (9/36 cases) and
`selftest_frozen_dumps.py` (1/32 cases). Diagnose each from the actual current
state — not a stale memory of what should be true — and fix the real cause.

## verify

### `selftest_check_canon.py` — the selftest was stale, not canon or the checker
Root cause: `check_canon.py` gained `suspend_planet_rules()` on 2026-08-22
(commit `3dc322c1`) — while `canon.yml > planet.status` reads anything but
`frozen`, every planet-derived rule (water, tiles, settlements, axis, lake,
seas, named_regions, rivers, habitable_ring, start_tile) downgrades from a
hard contradiction (exit 1) to an advisory print (exit 0). The selftest's
`CASES` table was last touched 2026-08-20, two days before that feature
existed, and every planet-derived case still asserted the old hard-fail
behaviour.

`canon.yml > planet.status` is legitimately `remaking` right now — owner,
2026-08-22/23: the freeze is a SAVEGAME (map ported through the live bridge,
factions/leaders/ideoligions correct at initiation, then saved), and that
sequence has not completed (`infrastructure/state/V1.md`, still current as of
its 2026-08-23 edit: *"planet.status STAYS remaking, and that is
deliberate"*). So neither canon.yml nor the world-facts source is stale —
only the selftest was, because 9 of its cases were entangled with a live,
intentionally-mutable status flag instead of testing the rule-matching logic
in isolation.

Fix: `src/RimMandrake/Utils/selftest_check_canon.py` now builds two throwaway
`canon.yml` fixtures (via `CLAUDE_PROJECT_DIR` override) — one with
`planet.status` forced `frozen`, one forced `remaking` — and runs the
pre-existing `CASES` against the `frozen` fixture, decoupled from whatever the
live flag says on any given day. A new dedicated case,
`planet.status=remaking downgrades a planet-derived hit to advisory`, runs
against the `remaking` fixture and locks in the suspend feature itself, so a
future flip of the live flag can never silently break this file again in
either direction. **37/37 passing.**

### `selftest_frozen_dumps.py` — the selftest fingerprinted the wrong capture
Root cause: `t_no_registry_entry_carries_an_unreproducible_sha` called
`refresh.dump_fingerprint()` with no argument. That defaults to `D_DUMP`,
which resolves to `game_paths.newest_capture()` — whatever is newest on disk
*today*. The active frozen entry, `OFFICIAL-2026-08-29` (capture
`2026-08-29T13-30-02Z`, `modlist_sha 1742630eb6253187`), was frozen before a
later ordinary game load produced a newer capture (`2026-08-31T04-57-37Z`) —
exactly the "our own mods change the count constantly" drift the frozen-dump
immunity exists to shrug off. The test compared the frozen sha against the
*current* capture's fingerprint instead of the *named* capture's, so it read
FABRICATED when the claim was reproducible all along.

Verified directly (per `~/.claude/skills/measuring-large-artifacts`
discipline — fingerprint, never a scan):
`refresh.dump_fingerprint(".../DefDump/captures/2026-08-29T13-30-02Z")` →
`1742630eb6253187`, `modCount 584` — an exact match to the registry entry.

Fix: the test now reads `active.get("capture")` off the registry entry and
fingerprints `<DUMP_ROOT>/captures/<that id>` (falling back to the flat root
for a pre-migration entry with no `capture` field), matching how
`refresh.frozen_entry()` resolves the same entry elsewhere in this file.
**32/32 passing.**

## criteria
- [x] `selftest_check_canon.py` diagnosed from actual current state (not
      guessed) and repaired: 37/37 passing.
- [x] `selftest_frozen_dumps.py` diagnosed from actual current state (fingerprint
      re-measured, not assumed) and repaired: 32/32 passing.
- [x] Neither fix landed on an explanation that is rename fallout — confirmed:
      one is a feature (`suspend_planet_rules`) added without a matching
      selftest update, the other is a wrong-argument bug in a fingerprint call.
- [x] No canon/data ruling needed — `canon.yml` and the frozen registry entry
      are both correct as they stand; only the two selftests were wrong.

## notes
Files touched: `src/RimMandrake/Utils/selftest_check_canon.py`,
`src/RimMandrake/Utils/selftest_frozen_dumps.py`. Neither `check_canon.py`,
`canon.yml`, nor `refresh.py`/`REGISTRY.jsonl` needed a change — both defects
were in the tests, not the systems under test.
