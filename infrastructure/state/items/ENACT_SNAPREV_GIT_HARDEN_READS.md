## spec
Minor findings from the review of 93d799120b (enact.py `snapshot_revisions` / stale slot keys):
1. The `git show <h>:<rel>` loop does not catch `subprocess.TimeoutExpired` or `UnicodeDecodeError` (or a JSON error on a
   mangled revision), so one bad revision crashes the whole enact (loud, not silent, but it blocks every row).
2. It reads EVERY revision eagerly: 0.33 s for 40 revisions on ext4; on drvfs D: it will be several times that per sheet.
   It could stop at the first revision built at or before the click (git log is newest first).
3. The real git path is untested: selftest_enact_stale_lane.py replaces `E.snapshot_revisions` with a lambda and never
   restores it.
4. When a snapshot row has no `graphic_of` (`lanes_now` empty; 54 of 3202 rows) a stale slot key is not checked at all and
   installs at the old key as before 93d799120b.
Safe already: shallow or missing history and a renamed snapshot file (no --follow) both end in a refusal.

## failing test (sketch)
- Make a temp git repo with a snapshot committed twice, the second revision truncated JSON; call the REAL
  `E.snapshot_revisions(path)`; assert it returns the good revisions and does not raise. Today: json/decoding error escapes.
- A row with columns but no graphic_of, slot key "oldfolder/Kite/Kite" that ships one of our files: assert a conflict.
  Today: installs under the old key.

## verify
Wrap each revision read in try/except (skip it, count it, print one note); stop early; restore the monkeypatch in the
selftest and add one test that runs the real function on a scratch repo.
