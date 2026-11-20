## spec
`src/RimMandrake/rimflow/selftest_maturation_dispatch.py` calls `maturation_dispatch.decide(...)` with no `bridge=` stand-in in its cert rerun and cert red gate checks, so `decide` falls back to the LIVE bridge (`M.bridge_idle`, maturation_dispatch.py line 391). Live failure: `./publish` on 2026-11-19 about 4:20 PM PST failed 2 of these checks ("cert rerun gates: at max_live 1 on one game, the rerun ahead spends neither, the next mod's visit launches", "cert red gates: on one game, the builder ahead holds no game and the next mod's visit launches", Twin read `bridge_held`); the same test passed 1 minute later and on the next publish (2c71850741). Evidence: D:\ClaudeWork\rimmandrake\lane6_briefs_spend\publish_flake_20261119.txt. Fix: pass a takeable bridge stand-in (`bridge=lambda p, game="a": (True, "free")`) to every `decide` call in those checks that is not about the bridge itself.

## verify
Acceptance test: `python3 -c "import sys, runpy; sys.path.insert(0, 'src/RimMandrake/rimflow'); sys.argv=['x']; import maturation as M; M.bridge_idle = lambda *a, **k: (False, 'held'); runpy.run_path('src/RimMandrake/rimflow/selftest_maturation_dispatch.py', run_name='__main__')"` from the repo root. Watched on 2c71850741: exit 1, 3 FAIL (the two above and "cert red gates (in-game visit 2): slot taken by an earlier mod on the list"). Passes with exit 0 and 0 FAIL after the fix; the plain selftest stays green. Evidence: D:\ClaudeWork\rimmandrake\lane6_briefs_spend\flake_acceptance_red_2c71850741.txt.

## criteria
selftest_maturation_dispatch.py reads no live bridge: its verdict is the same with the bridge free or held.

## refs
file: src/RimMandrake/rimflow/selftest_maturation_dispatch.py
