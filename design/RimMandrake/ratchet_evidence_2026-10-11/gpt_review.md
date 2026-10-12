**1. SKEPTICAL REVIEW**

1. **Sharpest objection: the plan responds to failed tool adoption by building another control plane before proving one complete convergence cycle.** R1–R12 total roughly **41 agent-hours**, excluding migration, integration, biome work and repairs. The evidence supports a small adoption experiment; it does not support launching this infrastructure programme alongside six biome completions.

2. **The ratchet is not monotonic.** Its rungs explicitly drop. Historical accomplishments can be monotonic; confidence in the current edited build cannot. Preventing legitimate regression would make the board falsely reassuring.

3. **The ladder conflates independent dimensions.** Specification, art coverage, behaviour, human judgement and compatibility form a dependency graph, not seven naturally ordered steps. Requiring art completion before behavioural proof unnecessarily blocks useful testing. “Owner-seen” also does not mean owner-approved.

4. **Input globs are an unsound foundation as written.** Dependencies include shared code, generated assemblies, check/oracle versions, resolved defs, mod order, settings and saves. “A texture edit never reopens R3” is unsupported: textures can affect loading or rendering checks. One weekly sampled rung neither establishes dependency completeness nor protects this burst.

5. **The evidence establishes dysfunction more convincingly than its causes.** Review debt increased partly because scope expanded; missing owner timestamps do not prove absent owner decisions; repeated sheet snapshots inflate entry counts. Historical GREEN, current GREEN and STALE are mixed across different denominators. Commit churn measures neither agent cost nor lost delivery time; the health timer already costs little and stopped committing its output.

6. **The validation economics are overstated.** There is no results join, so “189 bridge-hours / ~15 changes” combines bridge occupancy with modcheck status changes without attribution. Identical PASS outputs do not establish identical inputs or useless execution. Regression, nondeterminism and integration checks can legitimately reconfirm.

7. **The ~70-hour burst is not a credible capacity forecast.** Elapsed time is not available compute. Token totals do not establish Max quota consumption, remaining allowance or helper overhead. The lane table permits roughly **18 agents before TRIAGE**, contradicting the stated 6–9 peak. Adding agents because usage trails elapsed time ignores the game and human bottlenecks.

8. **The critical path contains uncommissioned machinery.** No biome has the proposed `proof_all`; artboard has never run live; provenance is broken; shared harness faults remain open. R4 explicitly requires the game, contrary to the budget argument that it needs neither game nor human. Monday lunch’s output also depends on Sunday overnight commissioning succeeding.

9. **Biome ordering measures visible paperwork, not remaining difficulty.** Small walks and few named items can reflect weak specification. NightsideIce has two uncovered lines, no plan and zero reviewed files. DivingInteraction spans six biomes and substantial code; “re-run only” is not established by stored GREEN.

10. **Silence-as-default can conceal the bottleneck.** Reversibility does not make an unnoticed change cheap to discover, review or undo. Expiry can resolve records without resolving judgement. Likewise, “80% resolved during a sitting” says little if arrivals exceed service capacity or difficult items accumulate.

11. **The pre-review evidence cannot support an order-of-magnitude reduction yet.** Catching four known clamp rows is a useful regression test, not an independent calibration. A 5% audit of 147 auto-resolved rows is about seven rows; zero disagreements gives weak assurance. Pixel validity, visual quality and in-game suitability are different questions.

12. **The clone proposal removes shared indexes, not shared coordination.** INFRA and biome lanes overlap on ratchet files; helpers within a lane still need writer ownership. `land.sh` ends in synchronization that can refuse, and hooks inspect local HEAD. Deployments, game configuration and capture outputs remain shared mutable resources. The clone system has one recorded trial.

13. **Several recommendations create fresh churn.** New inbox records, glob declarations, expiry processing, method attribution, existence-claim enforcement, lesson expiry, alarms and reapers all require maintenance. A sweep of 850 items is especially poorly timed: it can lower the count through disposal while consuming the burst and hiding unfinished work.

**2. IMPROVEMENTS — ranked**

14. **First: complete one pilot before expanding.** Use GSS to repair the known sheet/provenance incident, then take NightsideIce through offline checks, live proof and one owner sitting. Require published code, deployed build identity, inspectable evidence and recorded disposition. Add a second biome only after this cycle works without bespoke rescue.

15. **Make completed versions monotonic; make current validity explicit.** Certify an immutable candidate containing code, dependency and environment identities. Keep that candidate available while edits create a new candidate. The board shows “last accepted version” and “current candidate: valid/stale/failed.” Freeze accepted scope during the burst. Never imply that old evidence certifies new edits.

16. **Replace handwritten globs with conservative dependency closure.** Start by hashing whole mod roots plus their shared dependencies, checker/oracle code, build configuration and relevant runtime fixtures. Include directory membership so additions and deletions invalidate. Derive narrower sets from build dependencies, manifests and observed reads; treat those observations as supporting evidence, not completeness proof. Unknown changes invalidate broadly. Narrow only where measured rerun savings justify it.

17. **Use independent evidence facets and explicit prerequisites.** Track offline validity, behavioural proof, art coverage, human acceptance and compatibility separately. Each PASS includes executed check IDs and their manifest version; unexecuted checks remain unknown. “Ship-ready” is a conjunction over a specific candidate. Have one writer derive status from results rather than multiple lanes editing rung state.

18. **Bound the human queue by minutes and actual arrivals.** Initially serve at most **three decisions in a ten-minute window**, reserving two minutes for context and saving. Permit at most **two prepared biome review packs** awaiting the owner. Price preparation, game setup and follow-up repairs into evening sessions. If backlog exceeds the next day’s review budget, stop producing review-dependent work. Calibrate estimates from the first two sittings.

19. **Default to preserving the accepted state.** Skipped new art or mechanics stay staged; skipped necessary judgement stays pending. Allow automatic acceptance only for categories the owner explicitly preauthorizes, with visible consequences and cheap rollback. Store `owner-approved`, `policy-defaulted` and `deferred` separately. A default must never advance “owner-seen.”

20. **Use private clones plus one integration writer.** Give each concurrent writer a clone; serialize writing helpers within that clone. Workers submit an explicit patch/commit, base identity, owned paths and evidence. One integrator lands against fresh main, refuses overlapping changes, verifies publication, then checks the integrated result. Exercise simultaneous submissions and stale hooks on two lanes before increasing N. Separate clone indexes alone are insufficient.

21. **Give the live runner exclusive ownership of the entire game environment.** It alone deploys, changes mod lists/settings, launches, captures defs and manages review saves. Jobs identify immutable candidates; suspend further candidate edits during execution. Schedule owner sessions first and reserve recovery time. Nobody edits deployed files underneath a running proof.

22. **Rebudget around observed capacity.** Start with one infrastructure writer, one biome writer and one live runner, using read-only helpers selectively. Allocate against *remaining* account allowance, retaining headroom for failures. Measure one pilot’s quota consumption, integration cost and game occupancy. Treat **two proven biomes and one owner-accepted biome** as provisional planning scope; six/three is stretch scope until measured otherwise.

23. **Cache only well-defined questions.** Keys must include checker/oracle version, candidate dependencies and relevant environment. Deterministic offline PASS can be reused; live evidence needs an explicit policy for seeds, repetitions and environment changes. Fail fast on prerequisite failures, but continue independent cheap checks when they save another load. Reject missing or malformed result files even when the process exits zero.

24. **Commission pre-review as assisted triage first.** Run one live GSS capture; have the owner inspect both flagged rows and a deliberately varied sample of machine passes. Keep machine dispositions provisional until performance is understood. Initially omit automatic fixes: a classifier-driven fix loop can consume the sole game and introduce new regressions.

25. **Extend Part 3 for research uncertainty.** Record hypotheses as supported, contradicted or inconclusive under stated conditions; distinguish harness failure from hypothesis failure. Version algorithms, datasets, baselines, seeds and evaluation protocols together. Separate exploratory tuning from held-out confirmation. Preserve negative results with their scope and limitations; include replication and uncertainty checks even when they change no status. Evolving questions require new evidence versions, not forced ascent on an old ladder.

26. **Measure useful delivery, not rung activity.** For the pilot, record accepted candidates, owner minutes including rework, end-to-end elapsed time and escaped defects. Keep compatibility coverage as a requirement even when it finds few bugs. Drop runs-per-rung targets: splitting rungs or narrowing checks can improve that metric without improving the mod.

27. **Cut the burst to adoption essentials.** Keep sheet purpose/filter/provenance fixes, conservative evidence identities, one live queue and a generated text summary using existing tools. Defer the new hub tab, inbox CLI, lane wrapper/reaper, fine-grained globs, method-yield backfill, global decision migration, 850-item sweep, lesson-expiry machinery and existence-claim policing. Draft the portable method only after the pilot reveals what actually worked.