# FlowWorks GPT fixes — builder C (cross-cutting) — 2026-10-15

Source: `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md`. Status: TODO / FIXED <sha> / DROPPED (why).
Offline test: `src/RimMandrake/FlowWorks/selftest_flowworks_gpt_c.py` (one section per item).

| item | findings | status | sha | review |
|---|---|---|---|---|
| MAP_STATICS_PRUNE_GHOST_MAPS | C1-F2 C3-F2 C5-F3 C5-F4 | TODO | | |
| FLOWWORKS_HOTPATH_MEASURE_EVERY_FRAME | C1-F6 C2-F8 C7a-F6 C7a-F7 C7a-F8 C7b-F7 | TODO | | |
| FLOWWORKS_PROBES_MEND_HOOK_HAZARDS | C8b-F1..F7 | TODO | | |
| FLOWWORKS_TOGGLE_MEND_MIDGAME_LEFTOVERS | C4-F4 C6-F3 C6-F5 | FIXED (source; DLL with next build) | see git log | LiquidHeat, RiverWorks, RiversSettings CLEAN; Weir+Mod pending |
| PLACEMENT_FAILURE_MEND_LOST_IN_POSTING | C1-F13 C2-F6 C5-F12 C6-F9 | TODO | | |

## Notes
