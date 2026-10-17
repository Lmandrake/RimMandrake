# FlowWorks review + pre-existing selftest reds (BENCH AFK helper, 2026-10-17)

## Status
DONE. All four touched files full-read and marked clean; 4/4 FlowWorks selftests green.

## Task 1: full-file reviews
- generate_liquid_suite.py: full read; logic clean, generator reproduces every committed output byte for byte (checked into scratch). Fixed stale prose only: slime rows said no bottled/thirstQuality; registry header omitted coloured waters + living slime; three places (incl. the generated RM_LiquidBottles.xml header) said buckets/barrels are never drunk (RM_DrinkFromContainer drinks them now); ingestible note said icy water has no thirstQuality (it is Potable). Regenerated: only the two headers changed.
- review_map_coverage.py: full read, no logic defects (washedAwayM..Days regex intentional: Min/Max). Added the RM_WaterThin.png tex row (task 2).
- RM_LiquidBottles_Base.xml: full read, all cross-references resolve; fixed the module comment that said buckets/barrels are not drunk (stale since fa4101455e).

## Task 2: selftest reds
- selftest_hose_port P9: CHECKER STALE, mod right. Production has 21 credit calls; the Python mirror listed 20 and lacked `credit site: sprinkler draw` (RM_Sprinkle.cs:114, inside `if (RM_LiquidTransfer.Move(...) == r.need)`), which C# TransferChecks.CreditTags already has (added by 799336e671). Added the row; the bath was never the problem (its row in the failure is the planted can-fail case). PASS.
- selftest_review_map RM_WaterThin.png: MOD side (coverage rules table) missing a row; the gate is right. Texture installed 1e1d12f2e1 with no tex rule. Added tex rule -> flow_shrinks (where its TerrainDef is already shown).

## Task 3: selftests run
run_selftests.py --only selftest_hose_port selftest_review_map selftest_liquid_look_tune selftest_flowworks_fuel_moat: PASS 4/4.

## Owed
- COVERAGE.md (northstar/review/map) not re-planned: review_map.py --plan also rewrites KEYSHEET files another agent has uncommitted edits in.
- FlowWorks deploy already owed (comment-only XML changes here add nothing live).
