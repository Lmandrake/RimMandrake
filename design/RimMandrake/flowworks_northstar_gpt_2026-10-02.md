# GPT recommendation: FlowWorks northstar v2 (2026-10-02)

- **Model:** `gpt-6.1-sol`, the highest model listed in `C:\Users\Mandrake\.codex\models_cache.json` (priority 1). Effort: `ultra`, its highest.
- **Route:** `src/RimMandrake/Utils/gpt_consult.py` (codex.exe). A probe confirmed the model answers on this install today; `codex_image.py`'s note that it "fails" did not reproduce.
- **Inlined files:** the interrogation, the plan, `validation.py`, the walk `FlowWorks.md`, and `validation_v2_DRAFT.py`.
- **Status:** a hypothesis, not a verdict (debug_process §5). The plan's last section records which points I tested and adopted.

Verbatim answer:

---

My recommendation is to make v2 a small set of tests against the loaded C#, with independent behavioral assertions and a few real scheduler/job checks. Keep the Python oracle as a diagnostic model.

The oscillation hypothesis is persuasive under the stated equal-depth rules. However, the draft currently contains both a guaranteed premature failure and several false-pass paths.

I reviewed all five inlined files. I did not inspect the underlying C# or raw live trace, so source-dependent conclusions below remain hypotheses.

**Top 10 recommendations, ranked by tick savings and false-pass prevention**

| Rank | Recommendation | Value |
|---:|---|---|
| 1 | Invoke the loaded C# pulse for transition tests; retain a short scheduled replay. | Removes most E2-E5 game time without substituting another simulation. |
| 2 | Replace S7's `cap is None` acceptance with exact holder membership and alive state. | Prevents the central capture false pass; almost no extra ticks. |
| 3 | Replace E2 with mirrored three-cell channels and five pulses. Separate oracle agreement from eventual-fill acceptance. | Smaller discriminator; fixes the premature south-control failure. |
| 4 | Replace E3's long channel with several short outlets; read stock and fill deltas. | Exhaustion in 2-3 pulses, with a budget that actually binds. |
| 5 | Probe actual designator/WorkGiver gates, then complete one real dig and one real fill-in job. | Prevents another bridge-bypass test while avoiding duplicate job waits. |
| 6 | Test displacement with spare recipient capacity, plus a separate overflow case. | Makes ON/OFF distinguishable; arithmetic can cost zero ticks. |
| 7 | Read forbidden surrounding ground, excluding the authored reservoir. | Fixes the old ring failure and v2's missing confinement assertion. |
| 8 | Restore original settings in a suite-level `finally`; remove fixture pawns promptly. | Prevents contamination across scenes and reloads. |
| 9 | Require actual rain/fire stimuli and typed successful reads before interpreting negatives. | Prevents E6/T2 from passing because nothing happened. |
| 10 | Keep visual bars separately unmet; use canonical state comparisons and scoped logs. | Prevents regex promotions, `shows=` wiring, and oracle matches from becoming false green. |

**A. Verdicts I would dispute or narrow**

- **`canal_holds_only_channel`: PROVES should be downgraded.** Its ring includes the source cell immediately west of the inlet. The channel begins at `x0+10`; water occupies through `x0+9`. That legitimate reservoir cell reports D=4/F=4 and fails `_expect_dry_ring`. Your audit identifies this in `confinement_on`, but the bar component has the same defect. Exclude the authored reservoir footprint, then test the remaining ground.

- **`dig_to_depth_on` proves a primitive operation, not the toggle.** If `Deepen` bypasses the setting, reaching D=3 cannot establish that `digToDepthEnabled` works. I would not include this among toggle proofs.

- **`superdeep_capture_on` is not even a clean partial capture proof.** Failed spawning, failed listing, death, or unrelated despawning can satisfy its absent-pawn assertion. The same applies to `pit_captures_hostile`.

- **`own_faction_default_off` is vacuous unless arrival is established.** Remaining in `list_pawns` somewhere does not show that the pawn stood on D=4 and was exempted.

- **`fillInEnabled` OFF is useful paired evidence, but “clean proof” is too strong.** Unchanged D also follows from failed designation, unavailable work, or an interrupted worker. Verify accepted designation and worker eligibility under both setting states.

- **`sourceBudgetEnabled` ON is especially weak.** Under the supplied rules, an isolated east-running 30-cell D=1 channel saturates at 16 filled cells. A 20-unit budget therefore never binds: `wet <= 20` passes with stock remaining, and OFF cannot reach `wet > 20`. This is more than stale-body contamination.

- **Not every staging read-back is vacuous.** `Deepen` followed by independent D/terrain reads establishes a narrow synchronous engine contract. Fill clamping is also useful. Neither establishes natural flow, player work, or visual legibility. I would label plot B/H assertions “state/driver contract” rather than evidence-free.

- **The corner-cell recession assertion is brittle, rather than inherently meaningless.** A verified source cell becoming non-source is evidence of recession if competing causes are excluded. The weakness is assuming that particular corner must recede. `recededCount` improves the functional test, but still does not establish the owner's *far shoreline* visual claim.

- **`fill_fluid_distinct` is not proven UNBUILT merely by one `activeFluid` field.** The bar asks about distinguishable appearances, not explicitly per-body fluid simulation. `_restore_water` also says existing fill terrain retains its old fluid when the override is used. Reconcile those statements before concluding that staging different appearances is impossible.

I agree with the principal WRONG findings: the pathCost payload check, joint-depth framing, tank adjacency assumption, broad TrapSpikeArmed scan, and legacy-trigger attribution.

A screenshot-only component can also be a valid visual test despite having no Python predicate. “Vacuous functional predicate” and “vacuous visual test” need separate labels.

**B. Oscillation: strong conditional hypothesis, with a smaller discriminator**

For isolated, initially dry, straight D=1 channels with one inlet, the described rules give this hand-derived trace. Vectors run inlet to tail:

| Pulse | East/north, three cells | West/south, three cells |
|---:|---|---|
| 0 | `[0,0,0]` | `[0,0,0]` |
| 1 | `[0,0,1]` | `[1,0,0]` |
| 2 | `[1,1,0]` | `[0,1,0]` |
| 3 | `[1,0,1]` | `[1,0,1]` |
| 4 | `[1,1,0]` | `[0,1,1]` |
| 5 | `[1,0,1]` | `[1,1,1]` |

The mechanism is sound: the ascending-index inlet becomes full and leaves subsequent recipient snapshots. It consequently stops replenishing the unit that later redistribution moves away.

Two corrections matter:

- East/north channels of length one or two fill. “East/north channels never fill” needs geometry and initial-state qualifications.
- Under these rules, west/south length four fills at pulse seven; length six at pulse eleven. The draft checks its south length-four control after **six** pulses, when it is `[0,1,1,1]`. Your audit's six-cell `<=8` claim also needs reconciliation.

The cheapest useful live discriminator is:

1. Use two isolated interior one-cell water sources, each with capacity five.
2. Attach one three-cell east channel and one three-cell west channel.
3. Disable rain, refill, recession and sinks for this diagnosis.
4. Verify initial vectors, source identities, depths and sink flags.
5. Execute five **actual loaded-C# pulses**, capturing every vector and stock debit.
6. Replay the same fixture through ordinary scheduled pulses.

No 64-cell edge source is needed.

Matching the trace in both paths strongly supports an implementation liveness defect. A mismatch identifies a concrete port, fixture, or scheduling assumption to investigate. Twin equality and conservation alone cannot allocate blame: a deterministic defect can conserve perfectly.

For an even cheaper preliminary check, two source-free D=1 cells seeded `[1,0]` should alternate `[0,1]`, `[1,0]`. That checks equal-depth shuttling in two pulses, but does not establish inlet starvation.

There is also a separate oracle discrepancy worth testing: `_pick` permits a non-brimming donor when **donor depth is less than recipient depth**, while your prose says “deeper or brimming.” Use two mixed-depth cells to resolve that comparison. Equal-depth oscillation does not depend on this discrepancy.

**C. What I would cut, repair, and add**

Cut from the default functional run:

- The automatic second full run. Replay the small native transition fixtures; reserve `--twice` for diagnosing nondeterminism.
- E2's duplicate east channel once the minimal directional discriminator is established.
- Long E3 exhaustion/front waits.
- Repeated worker jobs for arithmetic/toggle cases.
- Per-run keeper construction and visual framing. Keep an explicit visual/keeper mode.
- Setter-only peripheral toggle checks. Report those as uncovered behavior.
- Regex-based “UNBUILT proofs” as acceptance tests.

Keep the owner's bound visual bars unmet until observed. Moving them out of the functional clock budget must not make them green.

The main repairs are:

| Row/component | Problem | Proposed test |
|---|---|---|
| `S7_capture_on_cell` | Explicitly accepts `cap is None`. | Successful holder read contains the exact pawn ID; pawn alive and unspawned. |
| `E2_channel_vs_oracle` | Claims confinement without reading surrounding ground. | Read the authored forbidden-ground ring after flow. |
| `E2_channels_fill` | South control checked one pulse early. | Three-cell controls, five pulses; independent eventual-fill assertion. |
| `E3_budget_exhaustion` | Stable sum is treated as stopped front. | Assert no additional source input separately from front position. |
| E3 OFF tail | Exhausted one-cell pond is also required to recede. | Test budget with recession OFF; test recession separately. |
| S6 | `designate_batch` may directly insert designations. | Invoke actual designator acceptance and WorkGiver eligibility gates. |
| E7 plan | `[2,2,2]` leaves no displacement capacity. | Use `[0,2,2]` for transfer, plus a full-neighbor overflow case. |
| E6 | `RainRate > 0.01` does not guarantee one unit in two pulses. | Compute accumulation from the actual rule/rate, or invoke native pulses until the known threshold. |
| T2 | No proof the adjacent fire survives until ignition evaluates. | Verify the stimulus immediately before evaluation and identify resulting fire on tar. |
| `U_unbuilt_register` | A substring flip immediately PASSes a visual bar. | Report “needs scene/review”; never PASS from the flip. |

E3 has another likely failure: if its sole source cell recedes to non-water terrain, disabling budgeting cannot make that cell supply again. A budget-OFF twin must retain a valid donor.

The draft implements substantially less than the plan: L0-L3, S6/S8/S9, E1/E5-E10, the tar tier, full environment checks, and pulse restoration are absent. Its claimed complete bar wiring is also absent. Treat the budget as a proposed design, not the budget of the supplied executable draft.

Offline checks are narrower too: O1 omits several promised def facts; O2 omits float Scribe defaults and class binding; O5 has no 100-seed exercise; O6 is absent. The XML regex does not resolve inheritance or patches.

For basic functionality, I would require these additions:

- One real designation -> WorkGiver -> JobDriver -> depth change.
- One real fill-in job, including restoration to D=0 and appropriate terrain/holder cleanup.
- Actual displacement transfer and exact destroyed-overflow accounting.
- Alive capture into the correct holder, plus own-faction ON/OFF and capture-disabled behavior.
- Exit eligibility with a ladder in the pit cell.
- Save/load of D/F, fluid, body stock **and a captured occupant**.
- Shipped-interval scheduling, engine-disable behavior, and a scoped unexpected-error gate.
- MBT2/3/5 legacy flood behavior if that path still ships under this walk.

Legacy expiry need not consume its entire duration: test the real expiry condition immediately before and at its boundary using a controlled fixture, then retain a short ordinary ticking check.

I would also explicitly account for irrigation's functional coverage. The absence of a visual bar does not remove the claimed yield behavior. If a production evaluator exists, compare wet-adjacent and dry controls directly instead of growing crops for days.

**D. A tighter budget**

Shrink demand geometry before shrinking timeouts.

For E3, one capacity-five source with four separated adjacent D=2 recipients has eight units of demand. At one unit per recipient per pulse, it can exhaust in two pulses. Two opposing D=3 recipients exhaust in three. Keep refill/recession OFF for accounting.

For E5, prefill isolated sink and interior cells. One pulse establishes drainage and its exact counter delta. A second fixture tests sinks OFF.

My proposed budget is:

| Work | Native transition profile | Real scheduler profile |
|---|---:|---:|
| Dig/fill mapping, classification, gate probes | 0 | 0 |
| Direction, budget, sinks, displacement arithmetic | 0 | Small representative replay |
| Capture reconciliation | Direct checks plus 2-4 ticks | 2-4 ticks |
| Shipped cadence and pulse calibration | — | Roughly 250-500 |
| Ignition | 0 if the correct native evaluator is exposed | Up to one verified evaluation interval |
| One normal dig and one normal fill-in | — | `J_dig + J_fill` |
| Save/load and batch reads | 0 | 0 |

A defensible target is **roughly 300-800 non-job ticks, plus the measured duration of two jobs**. A total around **1,000-2,000 ticks** is plausible if the pinned worker's work constants permit it. The attachments do not justify a guaranteed numeric job cap.

Do not replace 2,000/2,500 with arbitrary smaller timeout numbers. Derive the cap from required work, worker stats, approach distance and scheduler delay.

Reflection validates the actual C# transition on a real map, but bypasses cadence, ticker registration, competing components and time progression. Refill/recession are only equivalent at zero ticks if their dependencies actually use the supplied interval rather than timestamps or cached tick state.

`run_lua` reduces round trips, not frame-bound game ticks. Upstream documents both the frame-bound stepping contract and Lua's restricted subset; dry-compile and discover the installed surface first. [RimBridgeServer documentation](https://github.com/pardeike/RimBridgeServer/blob/master/README.md)

Also, pinning 60 may leave the existing 250-tick deadline intact. Budget from observed `nextPulseTick`, not “five pulses equals exactly 300 ticks.”

**E. Bland-world interference I would additionally pin**

- **Future event producers.** Emptying today's queue does not disable storyteller or quest producers. Store a quiet scenario with no active quest effects and record that configuration.
- **Anomaly mode.** Set it explicitly to Disabled. Removing the monolith is insufficient in Ambient horror mode. [Official Anomaly settings](https://ludeon.com/blog/2024/05/new-ambient-horror-setting-and-tribal-anomaly-support/)
- **Odyssey terrain systems.** Check actual source terrain layers, ice and active flood producers. Clear weather and one centre temperature do not establish those conditions. [Official Odyssey terrain/weather description](https://ludeon.com/blog/2025/06/odyssey-preview-1-map-features-landmarks-and-biomes/)
- **Worker identity.** Use saved healthy adult baseliners with no royal titles, specialist restrictions, special needs or active rituals. Verify capacities and work eligibility. Ideology roles and Biotech age/genes can change worker behavior. [Ideology roles](https://ludeon.com/blog/2021/07/ideology-adds-social-roles-and-rituals/), [Biotech systems](https://ludeon.com/blog/2022/10/biotech-preview-3-reproduction-children-genetic-modification-release-date/)
- **Residual map state.** Soil painting does not establish absence of roofs, snow, pollution, temporary terrain, designations, reservations or map-component state.
- **Harness interventions.** Feeding, rescue actions, modal handling and focus changes are part of the experiment. Prefer full initial needs and an observe-only watch during measured scenes.
- **Test-owned threats.** Detectors must distinguish intentionally spawned hostiles/fires from unexpected interference.

Record game build, DLC identities, active mod order, companion identity and resolved def identity. A FlowWorks DLL hash alone cannot establish the whole tested deployment.

**F. Most likely live flakes and guards**

The highest risks are fixture lifetime, worker scheduling and pulse boundaries.

S7 leaves an uncaptured hostile and colonist near each other for later scenes. Remove fixture pawns immediately after assertions. Redraft workers after E7/E8.

Before either worker job, verify work settings, schedule, needs, capacities, allowed area, reservations and approach cells. Poll job identity and failure reason alongside D. A timeout is unresolved evidence; it is not automatically SITE rather than MOD.

Guard `_step_pulses` against overdue/negative deadlines and confirm exactly one pulse executed. Do not assume `nextPulseTick` must freeze when disabled unless scheduling semantics require that; the essential assertion is no flow.

Read E6's roof and actual rain rate after the measured interval as well as before it. A collapsed roof or weather transition is a fixture failure.

Require successful typed payloads everywhere. Missing fields must become instrument failure, never empty lists, zero counters or absent pawns.

Finally, compare canonical state in repeat runs: ordered D/F vectors, stock deltas, holder relationships and relevant flags. Exclude incidental IDs, timestamps, wall timings and log cursors. Use log cursors and verify DevMode before relying on conservation warnings.

The decisive separation is between “the loaded engine matches this model” and “the engine satisfies this behavior.” E2 and E3 need both assertions.