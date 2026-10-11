# GSS build-out → hose port into FlowWorks — program tracker (2026-10-10 night)

Owner order (typed, 2026-10-10 ~23:40 PDT): stop validating GSS; fully build it; full design pass porting GSS's
flexible hose + reels into FlowWorks; independent agent review; GPT combined review with all of FlowWorks; merge the
design; fully port; offline tests; independent offline review; THEN validate GSS (hose-free) and FlowWorks.
BENCH orchestrates, ≤3 subagents.

| # | stage | state | output | sha |
|---|---|---|---|---|
| 1 | GSS build-out (non-hose features) | running | Transient/gss_buildout_2026-10-10.md | |
| 2 | Hose-port design pass | DONE | design/RimMandrake/hose_port_to_flowworks_design_2026-10-10.md | 7db8d8288 |
| 3 | Independent design review | DONE (9 must, 12 should; v2 written) | design/RimMandrake/hose_port_to_flowworks_review_2026-10-10.md + _design_v2_ | 068edd3af |
| 4 | GPT combined review (design + all FlowWorks) | running | design/RimMandrake/hose_port_gpt_review_2026-10-10/ | |
| 5 | Merged final design | running (same agent) | design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md | |
| 6 | Full port + offline tests | waiting on 5 | | |
| 7 | Independent offline review of the port | waiting on 6 | | |
| 8 | Validate GSS (hose-free) + FlowWorks live | waiting on 7 | | |

## Owner questions from stage 2 (recommended default proceeds; reversible)
1. Rename RM_LiquidHose to universal pipe — rec: yes
2. Hoses switched off also carry nothing — rec: yes
3. Open nozzle in liquid acts as pump intake — rec: yes, later, behind a switch
4. Move the 40 hose images byte-for-byte during the art pause — rec: allowed (no redraw); FlowWorks gets its own default-look setting
5. Reel build tab — rec: Production
6. Show liquid flow direction — rec: not now
