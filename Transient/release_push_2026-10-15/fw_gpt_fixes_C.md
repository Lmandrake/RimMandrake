# FlowWorks GPT fixes — builder C (cross-cutting) — 2026-10-15

Source: `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md`. Status: TODO / FIXED <sha> / DROPPED (why).
Offline test: `src/RimMandrake/FlowWorks/selftest_flowworks_gpt_c.py` (one section per item).

| item | findings | status | sha | review |
|---|---|---|---|---|
| MAP_STATICS_PRUNE_GHOST_MAPS | C1-F2 C3-F2 C5-F3 C5-F4 | FIXED, closed | 94c41f6f40 df46b3e3a9 3ff85f6f0b (half rode in 72185cbc4c) | all CLEAN |
| FLOWWORKS_HOTPATH_MEASURE_EVERY_FRAME | C1-F6 C2-F8 C7a-F6 C7a-F7 C7a-F8 C7b-F7 | F7/F6/C2-F8 FIXED; C1-F6, C7a-F8, C7b-F7 not-a-bug (call frequency), closed | 72642d8cde | CLEAN |
| FLOWWORKS_PROBES_MEND_HOOK_HAZARDS | C8b-F1..F7 | all FIXED (+ProofLadder via SetRaised), closed | 7333aa53d5 24318d7583 | CLEAN |
| FLOWWORKS_TOGGLE_MEND_MIDGAME_LEFTOVERS | C4-F4 C6-F3 C6-F5 | FIXED, closed | ec3e21b942 (DLL 652e73c1b9) | LiquidHeat, RiverWorks, RiversSettings, Weir CLEAN; FlowWorksMod.cs pending |
| PLACEMENT_FAILURE_MEND_LOST_IN_POSTING | C1-F13 C2-F6 C5-F12 C6-F9 | FIXED, closed | 652e73c1b9 8fdc692b89 | all CLEAN except RM_DigDiscovery (pending MAP_STATICS) |

## Notes
- 652e73c1b9..: DLL commits carried other seats' WIP; final DLL rebuilt from a clean scratch clone at 8fb5afd51f.
- 72185cbc4c (builder A, C1-F5) swept in my uncommitted RM_LiquidNet.cs half of MAP_STATICS, with RM_MapComponent_FlowStatics wedged between RM_Patch_NetTopologySpawn and its Harmony attributes; HEAD did not compile until 94c41f6f40, attributes restored in df46b3e3a9 (selftest guards it).
- C# SelfTest: fixed two stale checks (river path cost shape after C6-F3; CurrentActive tick after builder B's 0377b63928). The HoseFuzz trail failure seen mid-session was another seat's WIP; at the end the targeted sweep (gpt_c, call_sites, rivers, hose_port, flowworks_stock C# SelfTest, settings_screens) is GREEN 6/6.
- Not fixed (out of scope, noted): RM_MapComponent_Hoses.Layered() builds a StringBuilder key over every reel every frame (small per-frame garbage); RM_LiquidSurface ForgetLook leaks the look's ripple textures on a dev Tune.
