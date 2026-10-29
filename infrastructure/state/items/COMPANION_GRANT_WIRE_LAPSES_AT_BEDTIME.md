## spec
The companion's test-profile grant lapsed at 03:00Z on 2026-10-29 and bounced 4 FOUNDRY tickets. Nobody noticed,
because nothing read the grant before a ticket started.

The grant is `<SaveData>\JawaBench\companion_profile.json`, which is
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\companion_profile.json`.
Its fields are `profile` (`test`, or its alias `gm`) and `expiresUtc`. Per design/RimMandrake/companion_handshake.md, a
file that is absent, invalid, expired or unknown counts as `campaign`, and the companion then refuses every test-only
tool.

The grant is **not** renewed automatically. Renewal opens test-only tools on the owner's machine, and no ruling makes
it an agent's call. This item warns early and routes work around a lapse.

1. `src/RimMandrake/rimflow/companion_grant.py` is the one reader. Its config is `companion_grant.json`, with a
   `_why` on every setting. It returns a state:
   - `OK`
   - `LAPSING`: under `hold_within_min` left.
   - `LAPSED`: expired, absent, torn, a non-test profile, or no readable `expiresUtc`.
   - `UNMEASURED`: the JawaBench folder itself cannot be seen, so the instrument is blind. A blind reading also holds.
2. **Early warning.** The ops_watch family `companion` emits `companion.grant_hours_left` (MEASURED). An alarm
   target fires below 12 h, so a grant set to lapse at bedtime is flagged in the morning. The alarm files a BENCH
   item through the usual ops_watch alarm path. The key is also on the blind digest allow-list, so the Conductor sees it.
3. **Preflight.** Every `rimflow next`, including `--peek` (which the Dispatcher reads), withholds items whose
   needs are in `hold_needs` (`bridge`, `game-up`) whenever the state is not `OK`. It prints one loud
   `(companion grant ...)` line, and the seat gets offline work instead.

## verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_companion_grant.py`
  passes, and so do the ops_watch, cli and dispatcher selftests.
- `python3 src/RimMandrake/rimflow/companion_grant.py` reads the real file and prints its hours left.
- `python3 src/RimMandrake/Utils/ops_watch.py` with family `companion` records the point.
