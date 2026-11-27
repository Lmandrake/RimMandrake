# BOUNDARY: the return step of a detached run names a publish by what it did, Design Version 0.1.0

Code: `detached_helper.publish_step` and its two calls in `detached_helper.return_clone` (the steps "publish" and
"publish note") in `src/RimMandrake/rimflow/detached_helper.py`. Item
`RIMMANDRAKE_FIX_RETURN_STEP_SAYS_FAILED_WHEN_PUBLISH_LANDED`, written 2026-11-27. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_detached_helper.py`.

Why: the return step searched the last 400 characters of stdout and stderr joined for `PUBLISHED <sha>`. When `./publish`
waits for the push lock, it writes a long line to stderr, which comes after stdout, and the search missed a publish that
had landed. The Conductor log holds 49 lines "publish note FAILED" for publishes that landed (exit 0).

## ACCEPTS (the only inputs this is built for)

- **a-finished-publish-run.** The exit code, the stdout and the stderr of one `./publish` run, whatever their length.

## DOES NOT SURVIVE (not promised)

- **a-published-line-in-stdout-of-a-failed-publish.** A run that exits non-zero after it printed `PUBLISHED <sha>` is
  written as landed, because the line is the proof of the landing.

## PROMISES (each one is owed a test of the same name)

- **a-return-step-says-failed-only-for-a-failure.** The step text of a publish keeps four answers apart:
  - the publish landed (a `PUBLISHED <sha>` line anywhere in stdout): the text holds the sha, whatever stderr holds;
  - exit code not 0: the text reads FAILED with the exit code and the end of stderr;
  - exit code 0 and no `PUBLISHED` line: the text reads "no PUBLISHED line" and never FAILED;
  - nothing to publish (no dirty shard): the text reads "nothing to publish".
  Red on the base: a 600-character stderr line turned a landed publish into FAILED.
