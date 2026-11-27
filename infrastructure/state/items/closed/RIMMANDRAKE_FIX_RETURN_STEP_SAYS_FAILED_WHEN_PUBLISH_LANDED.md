## spec
The return step of a detached run (`return_clone` in `src/RimMandrake/rimflow/detached_helper.py`) searches the last 400
characters of joined stdout+stderr of `./publish` for `PUBLISHED <sha>`. A push-lock line on stderr pushes the line out of
the window, so the step writes "publish note FAILED" for a publish that landed (49 lines in the Conductor log). Search the
whole stdout. Keep four answers apart: landed (sha), non-zero exit (FAILED, exit code, end of stderr), exit 0 with no
PUBLISHED line ("no PUBLISHED line", not FAILED), nothing to publish.

## refs
file: src/RimMandrake/rimflow/detached_helper.py

## verify
Acceptance test: the 4 cases of the brief `/mnt/d/ClaudeWork/rimmandrake/conductor/briefs/return_step_false_failed_20261127.md`,
in the selftest that covers `return_clone`, with a fake runner. The first case (stdout ends `PUBLISHED 0123456789ab`, a
600-character stderr line, exit 0) fails on the present code.

## criteria
- A return step says FAILED only for a failure.
- A landed publish shows its sha in the step text, whatever stderr holds.
