# RIMMANDRAKE_FLUSH_PUBLISH_OUTPUT_SO_TAIL_SHOWS_REFUSAL

## spec

Found in the full-file review of publish.py (657a2a262a), 2026-11-16, after a real publish looked silent: publish
prints progress to stdout, block-buffered under a pipe, and REFUSED to stderr unbuffered, so `./publish ... 2>&1 |
tail -3` (the form agents are told to use) showed the progress lines last and hid the refusal. Fix: main() line-buffers
stdout.

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_publish_refusal_last selftest_publish` (2 tests).
selftest_publish_refusal_last watched FAIL on the base (last line "no change in the named paths ..."), PASS after.

## criteria

- With stdout and stderr in one pipe, REFUSED is the last line.
