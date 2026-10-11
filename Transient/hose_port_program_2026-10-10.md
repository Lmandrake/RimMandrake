# GSS build-out → hose port into FlowWorks — program tracker (2026-10-10 night)

Owner order (typed, 2026-10-10 ~23:40 PDT): stop validating GSS; fully build it; full design pass porting GSS's
flexible hose + reels into FlowWorks; independent agent review; GPT combined review with all of FlowWorks; merge the
design; fully port; offline tests; independent offline review; THEN validate GSS (hose-free) and FlowWorks.
BENCH orchestrates, ≤3 subagents.

| # | stage | state | output | sha |
|---|---|---|---|---|
| 1 | GSS build-out (non-hose features) | running | Transient/gss_buildout_2026-10-10.md | |
| 2 | Hose-port design pass | running | design/RimMandrake/hose_port_to_flowworks_design_2026-10-10.md | |
| 3 | Independent design review | waiting on 2 | | |
| 4 | GPT combined review (design + all FlowWorks) | waiting on 3 | | |
| 5 | Merged final design | waiting on 4 | | |
| 6 | Full port + offline tests | waiting on 5 | | |
| 7 | Independent offline review of the port | waiting on 6 | | |
| 8 | Validate GSS (hose-free) + FlowWorks live | waiting on 7 | | |
