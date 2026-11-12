# Code review rounds on src/RimMandrake/Utils/ship_contributions.py (fresh opus reviewers, read-only), 2026-11-11

| round | findings that could give a wrong verdict | acted on |
|---|---|---|
| 1 | texPath / ingredient filters / `costList Inherit=` counted as material sources; EXEMPT accepted any quote mark; recipeMaker trusted one level; unshipped mods and test harnesses in scope; patches ignored; duplicate keys silent; merge dropped duplicate-tag children, ignored IsNull; parse failures silent | all fixed; scope = FULL test mod list + Baroque Biomes members |
| 2 | blacklist still leaked (descriptionHyperlinks, defaultStuff, affordance tags, disallow patches, C# lookup table); patches only warned | source test rewritten as a WHITELIST of hand-out contexts; placement-editing patches FAIL |
| 3 | MultiDef trader lines missed; `thingToSpawn` missed; patch test used a text window | fixed; per-operation patch judging |
| 4 | an EXEMPT row could borrow its gift's owner date (reproduced false PASS); ancestor-targeted patches unseen | fixed (citation must sit in the EXEMPT text); ancestor `@Name`/`@ParentName` and contains/starts-with/ends-with selectors matched |
| 5 | wildcard xpath selectors, ParentName attribute rewrites | cheap styles fixed; the rest is a stated limit (xpath is pattern-matched, not evaluated; the patched tree is effective_def_lint.py's job) |

| 6 | the caching edit indented the patch check under a `continue`, so it never ran (no wrong verdict today: the 4 patches it should report are label/comp edits) | dedented; selftest now proves the check runs on real patches and flags a synthetic placeWorkers patch |
| 7 | see the result appended below | |

Real-data effects found along the way: `RM_CloudRepulsorShip` had no source at all (fixed in the Helix trader);
`RM_SunSphere`'s seed fuel is fished (Odyssey `fishTypes`), which the checker now reads. Each review's fixes are covered
by the selftest (`selftest_ship_contributions.txt`: unit checks on real data and synthetic XML, 12 mutated lists).

