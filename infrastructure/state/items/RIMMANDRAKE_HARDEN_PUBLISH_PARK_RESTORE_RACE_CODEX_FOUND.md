## spec
seat_sync park (84ca416f3a). Codex reported (D:\ClaudeWork\rimmandrake\conductor\remote_landings_20261118\codex\84ca416f3a.review.md), confirmed here by reading seat_sync.py
~176-215, not run: (1) _unpark_added checks os.path.lexists(dst) then os.rename(park/u, dst), so a save landing in
between is silently overwritten (os.rename replaces); (2) the park dir is rm-...-<YYYYmmdd_HHMMSS>-<pid>, so two parks
in one process in one second share it and the second overwrites a retained first; (3) the rollback test
(selftest_publish.py ~830) never asserts the file was parked before the injected refusal. The ticket's own case is
kept: selftest_publish 56/56 here, 52/56 on the parent with the new test.

## verify
Acceptance test: none yet, the race needs an injected writer between the check and the rename; the builder writes the failing cases first (restore refuses an existing destination; distinct park dirs; the rollback test asserts the park).

## criteria
- No restore overwrites a file it did not park; a retained park is never reused; the rollback test fails if nothing was parked.
