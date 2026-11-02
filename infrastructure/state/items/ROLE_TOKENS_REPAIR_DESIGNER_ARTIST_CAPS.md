# ROLE_TOKENS_REPAIR_DESIGNER_ARTIST_CAPS

selftest_role_tokens is RED on origin/main (seen 2026-11-02 at 580ccf5e5e, before and after BENCH's transfer edits,
which did not touch the roles rows): 4 failures in dispatcher_schedule.json roles rows.
- W5 Designer: _caps_why names the measured record and carries [A]
- W5 Artist: _caps_why names the measured record and carries [A]; per-run cap 300000 < measured x1.25; band-shrunk cap
  300000 lacks 15% headroom.
A regression: the same class was fixed in 1b78a2ad00 (SELFTESTS_MAIN_REPAIR_TWO_RED_AFTER_REWRITE). Find the commit that
re-broke it (git log -S on the Artist row), re-measure, and fix the caps or the why with the measured record.
Closing it touches dispatcher_schedule.json, so it needs --live.
## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_role_tokens GREEN.
