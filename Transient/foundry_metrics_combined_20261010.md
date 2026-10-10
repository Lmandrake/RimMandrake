# Game-health metrics beyond TPS — combined Opus design + GPT review (2026-10-10)

Sources: `foundry_metrics_design_20261010.md` (Opus, 100 candidate metrics), `foundry_metrics_review_gpt_20261010.md` (GPT 6.1 Sol, high effort). Nothing is built or measured live.

## Where the two agree
- Tiered shape is right: cheap always-on, triggered/incident, on-demand deep profile, external observer.
- The companion only starts after cold load, so it cannot time a load from inside the game. Load timing must come from outside (log parse + external observer).
- No automatic "blame a mod" verdicts. Cost and attribution are separate questions.
- Nothing heavier goes always-on until the TPS full-list overhead test (MUST 17) passes.

## Where GPT changes the design
1. **Several proposed numbers would be confidently wrong.** Heap delta is not allocation rate; GC-count change during a gap is coincidence, not pause time; reserved-minus-used is not fragmentation; `totalTextureMemory` is not VRAM used; `PageFaultCount` is not hard faults; process at one core does not mean the main thread is spinning; `Root.Update` cadence is not displayed FPS; a frame split into scopes is not a partition.
2. **Unity release-player counters are counter-specific.** Total/GC memory, Draw Calls, Total Batches (the real name), SetPass are documented as available; GC allocated-in-frame and texture/mesh counts are not. Which actually work in RimWorld's build is UNKNOWN until probed once and recorded. A missing source must read "unavailable", never zero.
3. **Log cap is a blind spot.** After the cap the logger forwards nothing, so the threaded log event cannot count what was suppressed. The reader must say "emission suppressed; error activity unknown". Evidence conflict: the design says the cap is 10,000, `belt_watchdog.py` says 1,000. Resolve against the installed `Verse.Log` before encoding either.
4. **Cost estimates were optimistic.** Five timer pairs is at least ten timestamp reads. Profiler cost scales with ticks x maps x stages, not frames. Keep 0.1 ms/frame as a provisional budget, add p99 emission latency, max hitch, allocations and I/O. Measuring it on 600 mods is a multi-day counterbalanced experiment; an uncertain result is INCONCLUSIVE, not a pass.
5. **Hazards GPT sees in the current TPS code** (worth a ticket): global state in the tick/long-event hooks (re-entrancy), a foreign-thread check that runs after state is written, `WD.Beat()` outside the exception boundary, a profiler header still calling calibration a LOWER bound, and `belt_watchdog.py` pid-only CPU trend plus "above 0.7 cores = main-thread tight loop" attribution.
6. **Schema rules:** do not reset process-scoped counters at game change (that erases reload accumulation); never average window p99s, merge histograms; bulk artifacts go to separate capped files, not giant JSONL rows; keep each band's own interval.
7. **Missing metrics added:** main-thread CPU/wall ratio and other-thread CPU (external), bridge queue latency and main-thread occupancy (agent-induced load vs owner-only play), own background-queue ages, tick-duration histogram, tick-list/registration churn, per-map sim cost, Harmony topology/assembly growth across reloads, system commit headroom, log bytes per second, startup landmarks vs bridge readiness, reproduction identity (save/mod-content hashes), observer health, and a presentation-timing capture for displayed FPS.
8. **Dumps and early-load probe:** keep both unbuilt until a feasibility spike shows value on a known case. Verbose-load timing is a diagnostic load, only comparable with other verbose loads.

## Options

**F (GPT's recommendation, and mine): evidence-first, small steps.**
1. Persistent Windows-side observer: process/main-thread CPU, working/private memory, system memory and commit, log growth, startup milestones, its own heartbeat. No injected game code.
2. Minimal TPS-record extension: update-interval histogram on existing timestamps, log counts plus suppression state, bridge occupancy and queue delay, a read-only capability inventory.
3. Offline load-tree and save census from a verbose launch.
4. Later, only on proof: per-mod profiler, GC timing, early-load probe, dumps.

**A. Health line only.** Extend the TPS record with memory, frame, log and process fields. Cheapest to write. GPT: too broad to call low-risk; bundles unvalidated memory sources and private getters.

**B. Full tiered recorder.** Everything in the design. Most complete, but generic Harmony attribution, leak scanning and dumps each need their own feasibility work; likely to repeat the TPS rework cycle.

**C. Load and profile tools only.** Verbose-load parser plus on-demand profiler. Answers named optimisation questions; does not catch the owner's unobserved slow sessions.

**D. External observer only.** Best first forensic gain, zero in-game risk, but cannot see inside the game (log suppression, bridge load, frame histogram).

## First weekend, if F
Persistent observer; frame-interval histogram; log counts with suppression state; bridge occupancy markers; capability inventory; a combined timeline reader joined to TPS incidents.
