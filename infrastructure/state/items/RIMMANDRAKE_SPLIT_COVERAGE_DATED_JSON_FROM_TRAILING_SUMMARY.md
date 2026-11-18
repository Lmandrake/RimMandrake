# RIMMANDRAKE_SPLIT_COVERAGE_DATED_JSON_FROM_TRAILING_SUMMARY

## spec
`python3 src/RimMandrake/Utils/testq/coverage.py dated --json` prints its human summary line ("N of M wired mods hold a dated DONE testq result...") on stdout AFTER the JSON document, so any JSON parser of stdout rejects it. Found by Codex review during RIMMANDRAKE_CLAIM_WIRED_MUST_SHOWS_THREE_MODS_BARE (2026-11-18).

## fix
In --json mode the summary goes to stderr; exit code unchanged (1 names a wired mod with no DONE result).

## verify
    python3 src/RimMandrake/Utils/testq/selftest_testq_coverage.py

Acceptance test: the case "dated --json stdout parses as JSON, the summary is on stderr" in that selftest; watched FAIL on base 9782bf6563 (stdout ends with the summary line); expected 1 new PASS.

## criteria

`coverage.py dated --json` stdout is exactly one JSON document; the summary line is on stderr; the exit code is unchanged.

## refs

file: src/RimMandrake/Utils/testq/coverage.py
