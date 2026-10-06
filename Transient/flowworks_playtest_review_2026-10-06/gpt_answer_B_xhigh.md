I would make the primary deliverable **a ranked defect list and one short, prepared in-game review**. To produce it, I would move FlowWorks’ experiments into a dev-only runner inside the game, reuse the existing production C# checks, and reserve player-agent exploration for a few bounded tasks.

This is a change in where testing happens and what it produces—not another consolidation of Northstar’s Python scripts. Its first success criterion should be **more player-facing defects fixed and less work handed to the owner**, at approximately the current core run’s wall time.

All costs below are estimates, not measurements. “Agent-day” means a focused working day of implementation and debugging. Parallel authors can reduce elapsed development time; they cannot multiply the single game seat.

**1. The current method rewards proving the test apparatus more readily than improving the game.**

The evidence supports that diagnosis, but also shows that some older explanations are now stale:

| Evidence | What it establishes |
|---|---|
| October 1 time ledger: 84.7 minutes on setup-invalid runs plus 64.0 on lost/voided runs, out of 210 minutes | Historically, about **71%** of that cross-mod session was invalid work. This is not a current FlowWorks-only benchmark. |
| `latest_results_trimmed.md`, `validation_v2_result_20261006T040914`: **251.1 seconds, 11,510 ticks, 872 calls, 59 PASS** | FlowWorks’ current core already finishes in **4.2 minutes**. “The core is unbearably slow” is no longer the strongest diagnosis. |
| That run’s pits phase: 104 seconds; promoted checks: 80.99 seconds | Those two phases consume **74% of wall time** and approximately **91% of ticks**. Merely reducing bridge calls cannot remove all this time. |
| `flowworks_size_table.md`: 87 tooling-touching commits versus 74 mod-touching commits; 794 KB of Python | There is substantial tooling activity and complexity. Neither commits nor bytes measure labor; the Python total also includes the liquid generator and art tools. |
| `validation.py:ROW_SHOWS` maps state checks to appearance bars | Declared coverage can improve without improving visual detection. A loaded terrain def does not establish that an excavation *looks* obstructive. |
| `review_map_visuals.py` and the review key | The owner receives many fixtures and instructions to perform mechanical experiments, rather than only unresolved judgments. |

My inference is that the feedback loop has become:

**requirement → declaration → fixture → probe → evidence/status repair → further declarations**

The desired loop is:

**player action → observable consequence → defect → mod fix → short owner judgment**

The morning review correctly identified provenance and lost evidence as important problems. I disagree with making a broad evidence-system repair the next FlowWorks project. The latest L2 evidence already records matching loaded/repository assembly identity and shipped defaults. Also, the later checkout text and the morning report disagree about whether custom results are now ingested. Resolve that discrepancy with a short offline trace; do not spend another several days building a programme-wide scoreboard before fixing FlowWorks.

A second correction: **59/59 is a successful run of the current selection, not a complete playtest.** Pumps, prison behavior, doors, machinery and other shipped features cannot become optional coverage merely because they sit in `extensions.py`.

**2. There are three materially different architectures worth considering.**

**Approach A — an in-process gameplay scenario runner. This is my preferred approach.**

Put the runner in the dev companion assembly, for example a proposed `JawaBenchFlowWorksPlaytest.cs`. It references the exact FlowWorks DLL under test. It starts from an explicit test request after a map has finished initialization, executes on the main thread, and advances through resumable scenario states during normal game ticks.

The experiment itself needs no Northstar orchestration and no per-action bridge calls. A small Python launcher may select the deployment, launch/load the fixture and collect artifacts. RimBridge remains useful for intervention and diagnosis.

Do not make this a general scenario language. Write a small set of concrete C# scenario functions:

- **Excavation:** use `Designator_DigCanal` and the fill-in designation, let ordinary WorkGivers select jobs, and observe completed terrain/grid changes, material use and reservations.
- **Hydraulics:** invoke the production pulse path for numerous inexpensive state cases, then use short normal-scheduler windows to establish that the game actually invokes it.
- **Prison:** walk a pawn into a sufficiently wide D4 cut, attempt escape, add/remove a ladder, form a prison room, capture from the lip, and run actual feeding, tending and social jobs.
- **Machinery:** run real `Building_LiquidPump`, tank, hose and converter components; observe their inputs and outputs rather than their “running” flags.
- **Fire:** create an actual vanilla Fire or explosion and exercise the Harmony triggers in `RM_LiquidFire.cs`; inspect fuel consumption, propagation and extinguishing.
- **Rivers:** exercise `RM_MapComponent_RiverCurrent` through normal scan/process cadence as well as deterministic `StepOne` cases.
- **Persistence:** save a shared checkpoint, continue, reload that checkpoint, repeat the continuation and compare consequences.

Reuse `RM_NorthstarProofs`, `RM_RiverWorksProof`, `RM_RiverWorksProofWorks`, `RM_FluidIdentityProof`, the existing pulse implementation and existing pure C# math. But classify those methods correctly: `ProofPump` can change mode, `ProofWallFaces` regenerates geometry, and `ProofResetRect` changes excavation state. They are not uniformly passive observers.

Use a fixed, settled fixture with exact pawns and a genuine river. Protect the river from plot repainting. Separate independent sites spatially; serialize tests that change global weather or settings. Most plots must be outside the ten-cell sink band.

The runner should write each completed result immediately. Its result record needs only build identity, fixture identity, scenario outcome, expected/observed effects, timing and artifact references. A missing result is incomplete, never green. Use the existing record adapter if useful; do not invent another registry.

Keep runner state outside the save. Static dev state plus an external continuation record avoids introducing a test MapComponent or GameComponent into the owner’s save.

**Cost:** a useful two-day pilot; approximately **5–7 agent-days** for coverage of the owner’s listed concerns, assuming substantial reuse. Covering every capability in the 45-feature sheet could take longer. Target **3–6 warm live minutes** for mechanics and persistence, plus **1–3 minutes** to publish the selected review stations and save. Add the measured 22-second minimal restart and actual fixture-load cost; budget 90 seconds when creating a fresh quicktest.

Those are targets to falsify. Moving code into C# does not make genuine pawn labor or save/load instantaneous.

**Failure modes:** direct calls bypassing the behavior being claimed; observers agreeing with the same defective predicate; global-state interference; a runner blocking the main thread; an expanding generic test framework. Counter these with normal-job sentinels, effect-based observations, a few production mutations and hard build/run budgets.

**Reuse:** existing C# proofs, pure selftests, fixture geometry, labels, screenshot capture and decisions storage.

**Retire after migration:** Python orchestration in `validation_v2.py`, duplicated plot experiments in `extensions.py`, and the golden-site setup/preflight stack for migrated scenarios. Preserve their useful predicates and regression cases before deleting their execution paths.

---

**Approach B — extract the actual liquid/state kernel and test it offline.**

This abandons live-game testing as the main search mechanism.

Expand `Source/SelfTest/Program.cs`, linking the actual production math files: `RM_StockMath`, `RM_PitTrapMath`, `RM_FireMath`, `RM_PumpMath`, `RM_ConversionMath`, `RM_DigDiscoveryMath`, `RM_RiverMath`, `RM_WallFaceMath` and related helpers.

The important additional work is extracting the real flow calculation—component resolution, donor selection, displacement and body accounting—from `RM_MapComponent_Excavation` and `RM_LiquidStock` into a small production kernel, such as a proposed `RM_FlowKernel.cs`. Its inputs are grids, body IDs, fluid properties and explicit external contributions. Verse adapters continue handling terrain, jobs, rendering and Scribe.

Test that same kernel with generated **action sequences**, not another Python implementation:

- Dig, fill, drain, deepen, fill in, pump, burn, refill and reconnect.
- Enforce depth/fill bounds and finite stocks.
- Account separately for each fluid.
- Include declared rain/refill/limitless inputs and sink/burn/overflow/consumption outputs.
- Check converter input/output vectors against the authored recipe.
- Preserve and shrink failing seeds into small reproducers.

Do not assume arbitrary rotational or construction-order equality where the design permits tie-breaking. State precisely which transformations should preserve results.

A failing seed becomes a small live replay recipe, rather than a request to rerun an entire golden map.

**Cost:** a **two-day extraction spike**; **7–12 agent-days** for a useful production kernel and sequence tests. Math-only additions could be useful in 1–2 days. If extraction requires rewriting large Verse adapters, stop the spike.

**Per run:** **zero live-game minutes** for the main suite; target seconds to a minute offline. Candidate validation still needs approximately **5–10 live minutes** of adapter/persistence checks and a prepared visual save. Offline tests cannot replace those.

**Failure modes:** constructing a fake RimWorld; testing a copied algorithm instead of production; spending a week refactoring while known game defects wait; “save tests” that only serialize a DTO.

**Reuse:** the linked C# selftest project, existing regression geometries and independent physical invariants. Keep the Python oracle temporarily as a differential diagnostic.

**Retire:** duplicate simulation logic in `fakegame.py` and Python flow models once equivalent useful coverage exists. Keep small transport/schema fault tests; they serve a different purpose.

This is attractive for long-term hydraulic reliability. It is a weaker first-week answer to the current backlog of jobs, prison behavior and rendering.

---

**Approach C — a bounded agent that actually plays three player tasks.**

This changes the search strategy rather than the simulation boundary.

Give the agent goals such as:

1. Build and operate a defensive canal.
2. Capture and maintain a prisoner in a pit.
3. Establish a liquid production chain and safe river crossing.

After fixture preparation, it uses Architect designations, normal work priorities, bills, float-menu orders and gizmos. It does not call `Deepen`, `ProofIgnite`, raw stock setters, forced RM jobs or teleports to make its goal succeed.

Use ordinary UI interaction for a small number of important discovery paths. Semantic bridge actions can handle repetitive commands, but the report must distinguish “the command worked” from “a player could find and use it.”

Read-only bridge observations record job progress, refusals, reservations, inventories, pawn locations and relevant health/guest state. The agent reports a timestamped action trace, repeated attempts, interventions and a few screenshots or short clips.

Hostile behavior must also be staged correctly: spawning a hostile pawn without an appropriate lord does not establish that an assault or escape scenario works.

**Cost:** **3–5 agent-days** for a three-task pilot; **6–10** for broader use. Allow **20–40 live minutes** per useful episode, including agent deliberation, with a hard stop.

**Failure modes:** agent incompetence reported as game friction; dev interventions hiding broken gameplay; tool-building during an episode; repeating the same happy path; narrative findings without reproducible actions.

Freeze the tool set during episodes. After three unsuccessful attempts, classify the cause as game behavior, agent limitation or transport limitation. Only the first is a mod defect.

**Reuse:** RimBridge client, cached tool descriptions, parameter guards, background execution, fresh screenshots and the fixture/save machinery.

**Retire from this path:** god-mode showroom operations and scripted proof calls masquerading as gameplay. Keep the showroom separately for appearance judgment.

This is useful exploration, but too expensive and unreliable to be the primary gate.

The coverage distinctions are important:

| Owner concern | A: in-process scenarios | B: offline production kernel | C: player agent |
|---|---|---|---|
| Flooding, canal flow, source exhaustion, liquid types | Automatic engine effects, including `Flood_FlowWorks` temporary-terrain restoration | Automatic kernel/accounting; misses actual terrain-layer integration | Selected ordinary-use outcomes; misses systematic boundaries |
| Designating canals/pits, pawn jobs, building, filling in | Automatic normal designations, WorkGivers and completed jobs | Math and eligibility only; misses job machinery | Strong exploration of discovery, priorities, reservations and carrying |
| Quarry, sluice, terrain creation/embedding | Automatic authored legality, actual finds and hardware behavior | Rules/data only | Selected usable paths; human judges usefulness |
| Pumps, pipes, tanks, converters | Automatic real transfers; dependency-specific adapters need their tier | Automatic transfer/conversion accounting; misses third-party integration | Production-chain friction; incomplete adapter coverage |
| Trapping, prisoners, ladders, inability to escape | Automatic movement, reachability and actual prison jobs; human judges readability/balance | Width/rule calculations; misses Harmony, rooms and AI | Finds practical escapes and awkward interactions, without exhaustive proof |
| Flame ignition, eligible fluids, extinguishing | Automatic actual Fire/explosion triggers, consumption and negatives | Fire arithmetic and sequence invariants; misses triggers/effects | Selected gameplay outcomes and warning/readability problems |
| Differing viscosities | Automatic fronts at equal elapsed time; human judges feel | Automatic propagation/rate rules | Screens whether differences matter during play |
| River force pushing | Automatic cadence, displacement, exemptions and edge cases; human judges force/balance | Automatic river math; misses game movement/pathing | Crossing and ferry friction; weak statistical coverage |
| Two fluids interacting | Automatic contact/boundary/transfer rules; human judges legibility and intended interaction | Strong generated contact and identity checks | Selected encounters; misses rare arrangements |
| Varying depth/fill, refill, shallow/deep behavior | Automatic independent D/F states, consequences and refill; human judges appearance | Strong bounds/rates; misses embodied consequences | Selected depth and refill experiences |
| Art, perspective, layering, clipping, pawn versus edge | Structural rendering checks plus staged human comparisons | Geometry calculations only; needs a live gallery | Screens visible trouble; cannot certify appearance |
| Saving/loading | Actual Scribe and continuation comparison | State-kernel round trips only; not a RimWorld save test | Selected continued play after reload |
| Performance | Component, rendering and whole-game measurements separated | Kernel scaling only | Notices stalls; poor attribution and repeatability |

Every architecture leaves judgment to the owner. B also leaves substantial engine correctness untested; C leaves substantial systematic coverage untested.

Several **specific production tests should precede any generic framework work**:

- **Unlike natural liquids touching:** `RM_LiquidStock.FormBody` traverses neighboring source cells without the shown same-fluid restriction. Test water/tar contact, diagonal contact and reversed first-touch order. The omission is visible in source; its gameplay consequence still needs confirmation.
- **Scarce supply across reload:** `DoPulse` uses an excavation set whose ordering differs between session construction and load reconstruction. Give two separate outlets one payable increment; compare uninterrupted versus reloaded allocation. Do not normalize away a changed outcome.
- **Stone excavation through the player route:** the initial `Designator_DigCanal` soil restriction differs from directly calling `Deepen` on `Granite_Rough`. A stone gallery proves that synthetic state renders; it does not prove players can create it.
- **Mesh invalidation:** `RM_NorthstarProofs.ProofWallFaces` calls `Regenerate`. It can repair the stale mesh it should detect.
- **Sluice intent:** older ruling/key text describes retaining liquid and opening to flood a pit; the unified model and `Flood_FlowWorks.CanFloodInto` describe flow doors passing liquid while closed. Record the implemented behavior and resolve this intent conflict before claiming a successful sluice demonstration.
- **Detonation fuel consumption:** `RM_LiquidFire.AdvanceFront` produces explosions, while `BurnPulse` applies gradual consumption. Test the specified immediate-consumption consequence, not just the presence of a blast.

For two-fluid interactions, a differently colored pair is insufficient. Test the actual contact rule. If the intended requirement includes chemical reactions beyond the authored rules, that remains a design/content gap.

**3. Evaluate the four possible owner outputs by the work they remove.**

| Output | What it catches or enables | Cost and prerequisite | Worth it here? |
|---|---|---|---|
| **(a) Ranked breakages + one prepared “walk this” save** | Separates mechanical failures from appearance, feel and balance; makes the owner’s sitting productive | Approximately 0.5–1 agent-day to adapt existing publishing/navigation; 1–3 warm minutes beyond testing; needs A, or B plus live adapters | **Required and highest value. Make this the product of the system.** |
| **(b) Player agent reporting friction** | Missing/unclear commands, awkward workflows, job interference, practical exploits and surprises | C; 20–40 live minutes per episode; objective observations needed to distinguish agent failures | Worth a rationed weekly/candidate episode after basic mechanics are reliable |
| **(c) Pass/fail on every build** | Fast regressions in production math/data; live gates catch adapters, triggers and persistence | Existing C# selftests offline; A for live integration | Worth doing offline on every build. A complete live checkout on every build is poor use of this seat |
| **(d) All three layered** | Regression protection, exploratory discovery and owner judgment | All three, with different cadences | Worth it **only with asymmetric scheduling** |

For (c), consider an illustrative 20 C# builds per day. A minimal restart, fresh quicktest and 3–6 minute integration run would consume roughly **100–160 game-seat minutes**, before review preparation. That is an estimate, not the project’s measured build frequency.

Use these cadences:

- **Every build:** production C# selftests and inexpensive data checks.
- **Every deployed batch:** affected in-process scenarios; a candidate gets the complete owner-list checkout.
- **When relevant appearance/behavior changes:** publish the changed review stops.
- **Weekly or before a release:** one bounded player episode.
- **On a selected candidate:** one full-list load and smoke run, with additional targeted dependency tiers where relevant.

An offline-passed build awaiting integration must say so. A minimal-tier pass must not imply canonical-list compatibility. A visual model’s uncertain assessment must not become PASS.

The full list still matters. Minimal tests identify FlowWorks faults efficiently; a single candidate run on the real list checks whether that evidence survives the actual environment. Add the measured **15-minute cold load** explicitly. DBH is absent from today’s live list, so its patch must not be presented as live-proven there.

**4. Machines can judge rendering contracts; they cannot establish that the result looks right.**

Use three levels of visual evidence.

**Deterministic structural checks can fail automatically:**

- Expected material/texture/shader exists and is actually used.
- Required shader properties are supported and applied—not merely present in `surfaceLook` data.
- Vertices and UVs are finite; bounds and generated geometry obey the intended footprint.
- Pawn draw offsets change with depth as specified.
- Occlusion geometry covers the intended portion of an isolated pawn, without covering a surface bystander.
- Liquid state remains inside its sanctioned cells.
- A change dirties and updates the visible section without camera movement or forced regeneration.
- Cover, scorch and wall geometry appears/disappears in the specified states.

These establish contracts, not aesthetic quality. Correct vertex count and draw altitude do not establish correct final layering.

**Screenshots can establish constrained pixel facts**, when the capture is controlled:

- A subject or expected region is missing.
- A known isolated pawn region remains exposed where an approved mask requires occlusion.
- An unrelated surface pawn/item disappears after the occluder is introduced.
- A before/after transition leaves the visible frame unchanged despite a required visible change.
- An approved appearance regresses substantially under the same scene/camera conditions.

Each capture needs the scene, camera, frame and timing identity. An identical image hash alone is not proof of a stale screenshot. Conversely, a successful capture response is not proof of a new frame.

Keep the camera fixed through a mutation. Capture first; only then reframe or regenerate. If reframing repairs the result, report an invalidation defect.

`RM_LiquidSurface` uses real-time animation, so pausing ticks does not necessarily freeze its appearance. Compare controlled animation phases or tolerate expected surface motion. Do not turn shimmer differences into regression failures.

**The human must judge:**

- Whether the cut reads as excavation rather than gravel or a building.
- Whether perspective, wall height and material treatment fit RimWorld.
- Whether shallow liquid looks shallow and deep liquid looks deep.
- Whether tar, oil and slime look like distinct liquids.
- Whether edge crossing and trapping look physically convincing.
- Whether fluid fronts, river force, refill and lethality feel useful and balanced.

A visual model can rank suspicious frames. Initially, it should not certify those judgments.

The existing 34-station visual matrix needs revision. Its liquid fill is mostly `max(1, depth - 1)`: it changes depth and fill together. That cannot isolate their contributions.

Instead, stage:

- **D4 with F0–F4**, side by side.
- **F1 with D1–D4**, side by side.
- Vanilla shallow/deep water beside FlowWorks equivalents.
- Matched water/tar/slime channels captured after equal elapsed time.
- North/south/east/west lip crossings, with a surface pawn or item beside the crossing.
- Representative small/large bodies and relevant facings.
- Cover, ladder, spikes and scorch before/after pairs.

This directly targets `RM_PitLipOcclusion`’s transition behavior and its documented risk to neighboring surface subjects. A stationary pawn in a pit cannot demonstrate clean walking across its edge.

**5. The owner’s sitting should begin with the game already loaded and framed.**

Deliver four linked artifacts:

1. **A one-page ranked findings list.** Deduplicate by likely cause. Rank severity, exposure and confidence. Show expected versus observed behavior and whether it was fixed, remains broken or needs an intent decision.
2. **One keeper save.** Include only functioning demonstrations with unresolved appearance, feel or balance questions.
3. **A plain-language key**, using the same stable station numbers as the map.
4. **Short clips/contact sheets**, so transient events do not require repeated staging.

Do not put a known broken pump, empty placeholder pad or probabilistic quarry hunt in the owner’s walk. Agents should resolve those mechanically. Do not ask him to dig fourteen cells, ignite a scene or wait several days to discover whether a feature works.

Reuse `JawaBenchReviewLabels` and the existing `--goto` behavior, but expose **Next/Back** in the review UI. Vanilla letters with station look targets can provide durable bookmarks. Re-pin process-only labels automatically after loading; labels stay outside the subject and can be hidden while judging. No owner CLI commands.

Use approximately **8–12 stops**:

- Depth/fill readability and shallow/deep controls.
- Dirt/stone perspective.
- Liquid identities and viscosity.
- Edge crossing and occlusion.
- Trapped occupant, ladder, cover and spikes.
- Prison interactions from the lip.
- Burning and scorched appearance.
- Pump/hose/sluice state readability.
- River force and safe crossing.
- A stocked free area for a few balance experiments.

Keep mechanical verification behind details. Each stop asks one clear judgment and provides **Accept / Change / Cannot judge**, plus an optional note.

Target **15–20 minutes for the first sitting**, then **5–10 minutes for changed stops**. These are proposed budgets to measure, not established timings.

The map should be calm, paused, clear and in daylight. Remove ambient interference without destroying subjects needed by the scenarios. Use bulk destruction rather than explosive killing. Turn screenshot mode off before handoff. God mode can support the free area; it must not be the basis of conclusions about ordinary jobs or balance.

Reuse the existing decisions sidecar and serving machinery. Persist verdicts immediately with station/question ID, relevant build/art identity and evidence identity. Preserve the owner’s exact notes. Agents then:

- Turn “Change” into a deduplicated mod task.
- Improve staging for “Cannot judge.”
- Run affected mechanical checks after a fix.
- Re-present only materially changed judgments.

Do not collapse mechanical PASS and human approval into “Works in game.” The supplied review README currently derives that label from mapped live rows; that can overstate both experience and completeness.

**6. The first week should prove that this produces game improvement.**

| Day | Work | Falsifiable success test |
|---|---|---|
| **1** | Build the smallest in-process runner and fixed fixture. Add touching-fluid and scarce-source/reload reproducers. Retain current identity checks and incremental results. | Both experiments execute without per-step bridge orchestration. A deliberately interrupted run preserves completed evidence and is incomplete. Findings identify consequences rather than only probe responses. |
| **2** | Run player-route digging, filling in, representative terrain legality, construction and quarry behavior. Fix confirmed mod faults. | Making a real job effect a no-op turns its test red even if its selection predicate still succeeds. Synthetic granite excavation cannot count as proof of player designation. At least one confirmed defect is fixed, or an existing shipped-change regression is demonstrated. |
| **3** | Add trapping/escape, ladder transitions, prison-room formation, capture and actual lip-service jobs. | A held pawn fails an actual escape attempt; the intended ladder/fill-in transition releases it; a warden completes a real job while staying out of D4. A no-op completion is detected. |
| **4** | Add pump/tank/hose/converter effects, real ignition/explosion triggers, extinguishing, refill and two-fluid contact. | Resource deltas balance under declared conversions and external inputs. Flame ignites eligible fluid; a non-igniting control does not. Sluice behavior is reported against the resolved intent, not the old key’s promise. |
| **5** | Add actual save/load continuation, component/performance measurements and fixed-camera visual checks. | A dropped saved field or suppressed mesh invalidation is detected. Three warm mechanics runs have median ≤6 minutes and maximum ≤8. Every owner-list item has automatic evidence, a human stop, or an explicit unresolved gap. |
| **6** | Publish and conduct the first owner walk. Immediately fix actionable findings. | The owner begins judging without setup or commands, finishes within 20 minutes, and verdicts persist automatically. No station requires him to perform a functional QA experiment. |
| **7** | Freeze a candidate; run the real list once and relevant dependency smoke checks. Publish the final findings/save pair. | Results identify the actual candidate and list. Ordinary untested mechanics remain visibly incomplete. The week has produced mod fixes and recorded judgments, not merely more declared checks. |

The week does not need a generalized Northstar service, comprehensive fuzzing platform or new capability dashboard.

Use two stopping rules:

- **Pilot kill:** if after two days the new runner cannot execute two meaningful production regressions, stop extending it. Use the existing 251-second core plus a few batched C# cases and the shortened owner walk.
- **Growth kill:** after bootstrap, track agent effort and live minutes. Freeze new tooling if, over three days, tooling consumes more effort than mod changes; or if two successive candidates add tooling without producing a fix or actionable finding; or if more than 10% of the last five runs’ live time is invalidated by setup/instruments.

On a freeze, spend the next 48 hours fixing the three highest-impact mod problems with existing tools. Permit a tooling change only when it addresses a named present defect or demonstrates a measurable reduction in owner/live time.

The lead measures should be **player-facing faults fixed, recurrence prevented, owner judgments completed per sitting, and invalid live minutes**. “Required checks proven per minute” remains useful diagnostically, but still rewards manufacturing more checks.

**7. Stop these practices now.**

- **Stop expanding programme-wide reporting before FlowWorks experiments work.** Repair the current result join in a bounded offline task. The morning review’s proposed shared-harness extraction is not the next prerequisite.
- **Stop counting `shows=` claims as appearance proof.** `validation.py:ROW_SHOWS` is a mapping. The October 1 38/38 floor demonstrated declaration completeness, not acceptable rendering.
- **Stop placing ordinary shipped mechanics behind “on request.”** Move their useful cases into the candidate checkout. Keep compatibility/removal separately scoped; toggles do not justify missing functional coverage.
- **Stop the owner’s exhaustive showroom assignment.** Cut the default 51-station gallery, automatic claims and unbuilt pads to unresolved judgments. Retain optional reference material outside the walk.
- **Stop per-cell review construction over RPC.** From `review_map_visuals.station_ops`, the 34 visual stations require approximately **700 bridge calls** before extra verification/navigation: 408 digs, 216 fluid fills, 34 terrain operations, 34 pawn spawns and eight scorch calls. Build the recipe in-process or with a dedicated batch operation.
- **Stop treating painting and destruction as a reset.** `ProofResetRect` improves depth reset, but does not establish that body records, pending actions and other state are clean. `extension_proof.py`’s “rivers first” rule already records one contamination failure. Use verified fixture reloads and a small explicit reset contract.
- **Stop forced refresh before judging update correctness.** `ProofWallFaces.Regenerate()` belongs in a geometry diagnostic, not the stale-render test.
- **Stop letting old key prose define current behavior.** Correct the sluice conflict and terrain-route claims. Also, `runsheet.py` treats “conservation exception” as universally fatal while sanctioned overflow can emit that phrase; inspect the event and amount rather than failing on the substring.
- **Stop requiring a universal implication proof before deleting low-value checks.** The densification rule that another row must fail whenever the removed row fails is too absolute to establish generally. Preserve named defect classes with representative production mutations; archive redundant orchestration.
- **Stop “keep the bridge busy” as an objective.** An idle seat while agents fix mod code can be productive. A busy seat rebuilding fixtures is not.
- **Stop inheriting hazardous historical recipes.** No debug-menu search/execute calls in suites—the hang runbook documents why. No explosive cleanup. No assumption that a minimal-load timing describes the full list.

Keep the strongest assets: the production math selftests, known regression scenes, one serialized game executor, loaded-build identity, incremental evidence, real save/load, and the prepared in-game review. Put the next substantial effort into making an ordinary pawn action expose an ordinary game defect.