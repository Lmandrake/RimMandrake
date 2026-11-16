# RIMMANDRAKE_LOCK_PYRELANDS_TWO_LEAVES_THE_TABLE_MAKER_REFUSES

## spec

A question for the Conductor (a bar-set call; builders may not change bars). design/concepts/Pyrelands/tree.json holds
two experience leaves that are not in version/locked_bars.json (42 ids, locked from 237b79116781) nor in bars.md:
`firehawk_hunt_rewards` and `ullai_cross_the_map_as_vanilla_herds`. Both came in with the locked change 91a7c61989
(2026-11-15, "fix the coverage judge's 12 Problem gaps", his card OWNER:1794748469904049550). tree.json plus record.json
now hold 44 bars, so the table's own maker (version/pilot_throwaway/make_test_table.py) stops at its guard
`bar set differs from bars.md` and the test table cannot be remade. Found by RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_BARS_LEFT
(journal, 2026-11-16) and again by RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_LEFT; filed now so it is not found a third time.

The obvious answer, with its evidence: they are 0.1.0 bars, because a locked change he carded added them (the same
road as `inv_firehawk_hunt_rewards`, bar-added 2026-11-14). Then: record them with `maturation.py lock-bars`, list
them in bars.md, give each its deciders in make_test_table.py's B list (and its 42 count), and remake the table.
Against it: `firehawk_hunt_rewards` may duplicate the inventory bar `inv_firehawk_hunt_rewards`, in which case the
leaf is coverage of that bar, not a new one, and the maker should map it rather than count it.

## Acceptance test

`python3 design/concepts/Pyrelands/version/pilot_throwaway/make_test_table.py` exits 0 and `python3
src/RimMandrake/rimflow/maturation.py next Pyrelands` still reads 0 bars not runnable. Watched fail at filing:
AssertionError 'bar set differs from bars.md' (44 bars in tree.json + record.json, 42 locked).
