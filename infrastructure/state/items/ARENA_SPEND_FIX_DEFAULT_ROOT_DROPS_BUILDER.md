# ARENA_SPEND_FIX_DEFAULT_ROOT_DROPS_BUILDER

Can change a verdict: YES.

Replay clones live at `<RM_ARENA_ROOT>/replay/<arm>/<task>` and builder transcripts use that slug (live example: `/home/mandrake/rm/arena/sandbox/*/build/home/.claude/projects/-home-mandrake-rm-arena-replay-v3-...`). `spend_census.classify_slug` takes the first component under the root as the arm, so with the default root (no caller passes `--clones-root`) every builder call lands in arm `replay`.

`arena_spend.attribute` puts that bucket in `overhead` with a flag only, not in `blocking`. The arm is credited with tester spend alone, so an arm's efficiency omits its builders and arms with different builder/tester ratios compare wrongly. ZeroSpendRefused does not fire, because tester spend exists.

Proof (real arena_spend, scratch trail, stub transcripts rewritten with real cwd and slug, 28 calls):
- default root: 6 calls on v3, overhead {replay: 22}, flag only. `D:\ClaudeWork\rimmandrake\arena_readiness\logs\spend_default_root.json`
- `--clones-root <root>/replay`: all 28 on the right tasks, overhead empty. `D:\ClaudeWork\rimmandrake\arena_readiness\logs\spend3.json`

Fix direction: default the clones root to the replay dir, or classify `replay/<arm>`, and make a `replay` bucket blocking. Note that with `--clones-root <root>/replay` a missing arm directory reads `unlisted` (blocking), and the judge's HARNESS bucket sits outside that root: check both.
