# Which source wrote each big Verse.Log rise, session ee0fbaa8 (2026-11-06)

Measured by `python3 src/RimMandrake/Utils/log_rise_census.py --session ee0fbaa8 --log <archived Player.log> --record <tps dir>`
(the alignment and its checks are in that file's header). The candidate on the item, Intimacy, was half the answer:
**Mood Chain Reaction wrote more, and wrote the largest rises alone.** Item: LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS.

| scan (Z) | count | rise | new errors (record) | written by | rise without the two mods |
|---|---|---|---|---|---|
| 20:08:04 | 693 → 1879 | 1186 | 10 | Intimacy 59.8%, Mood Chain 39.3% | 11 |
| 20:09:04 | 1879 → 3267 | 1388 | 0 | Intimacy 65.9%, Mood Chain 34.0% | 2 |
| 20:15:10 | 6077 → 7642 | 1565 | 1 | Mood Chain 71.7%, Intimacy 27.2% | 17 |
| 20:16:10 | 7642 → 9162 | 1520 | 0 | Mood Chain 63.8%, Intimacy 35.8% | 7 |
| 20:21:15 | 618 → 2860 | 2242 | 0 | Mood Chain 100% | 0 |
| 20:22:18 | 2860 → 4106 | 1246 | 31 | Mood Chain 95.0% | 62 |
| 20:26:20 | 4515 → 10000 | 5485 | 0 | Mood Chain 99.6% | 21 |
| 21:11:53 | 807 → 1904 | 1097 | 1009 | **not spam:** the load of `BENCH_leaf_scenes_20261026`, 84.4% save-load errors | 1097 |

The three earlier rises, 19:47Z to 19:49Z, are not the spam either: three loads of `RM_TestSite_calm_v2`, mostly
save-load and Beer policy errors, with Intimacy and Mood Chain at 33% of the last and less before it.

**Replay without the two mods.** The epoch from 19:46:59 reaches 8112 of the 10000 stop; the epoch from 20:05:03 reaches
121; the one from 20:19:14 reaches 168. Verse.Log stopped three times in this session and would have stopped in none.
Whole log: Mood Chain 17710 and Intimacy 8031 of 45024 lines. The item's "4691 'cannot currently do lovin' lines" is
every line holding "lovin"; the exact phrase is on 2623.

**The two switches, read from the DLLs.** Intimacy logs through `SexUtilities.HandNotesToEuterpe`, gated by its own
`IntimacySettings.logging`, which defaults to TRUE (constructor IL, and no override in the owner's config), so it spams
with Dev Mode off too. Mood Chain logs through `Hediff_MCRMoodChain.DebugLog`, gated by `Prefs.DevMode`, which every bridge
session has on. Both are now dropped by `src/RimMandrake/MandrakePatches/Source/LogSpamOff/LogSpamOff.cs`, default on, with
a Mod Settings checkbox.

**What this does not fix.** `log.errors_lower_bound` is sticky and is also set by a load's error burst: 21:11Z shows a
save load alone can pass the queue size. The two mods going quiet removes the in-play spam, not that.
