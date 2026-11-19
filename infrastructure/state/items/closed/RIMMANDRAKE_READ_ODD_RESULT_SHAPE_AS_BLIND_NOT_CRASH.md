## spec
infrastructure/stevedesktop/worker.py Attempt.kept_game_unmappable (ab3cb4372d) takes read_json's value as a dict.
A result.json that parses but is a list or number, or whose note is not a string, RAISES (AttributeError/TypeError)
instead of reading as a record it cannot use; measured here, 3 of 3. Found by the Codex review of ab3cb4372d
(D:\ClaudeWork\rimmandrake\conductor\remote_landings_20261118\codex\ab3cb4372d.review.md, must-fix 1). Its other must-fixes were judged not to need action: the 32M-char log cap is a
documented rule; no PASS row text containing "readiness 'mapData'" exists in src [measured, grep]; an unreadable
newest attempt costs one cold start, never a job. 🔴 Do NOT land a worker.py change while the SteveDesktop 72 h soak
runs (started 2026-11-18): the host may pull it mid-soak.

## verify
python3 src/RimMandrake/rimflow/acceptance/worker_result_shape_accept.py   # exit 0
Watched failing on c32e228e91: rc 1, all three shapes RAISE. Positive control: a (None, path) record passes it. Expected: 1 pass.

## criteria
- An odd result shape keeps the game and writes the blindness to worker.log by name; nothing raises.
