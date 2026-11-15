
## spec
maturation_now.py left a concept folder with stage.json but no version/VERSION.json off the map, table and cards. Now it is placed at its Designer stage, says "no Design Version named yet", says the lock is the owner's when stage.json is locked, counts in the chip, invents no version. A folder with neither file stays in the plain list.
Acceptance: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_now` (case 13, added). Watched failing on the base commit d20eb34ee3: 11 FAIL (113 PASS); after the fix ALL PASS (125).
Cross-check: maturation_dispatch status lists 7 mods; the page now shows 7. No other mod was missing (FlowWorks_Drawbridge has neither file, stays in the list).
