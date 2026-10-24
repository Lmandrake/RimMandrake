The first gate should be live Phases 1–4 validation. The package establishes offline behaviour; it does not establish perceptibility, frame cost, compatibility or comfort. Findings below reference the inlined package, not independently inspected source.

**DEBUG**

- **Several “clarifications” change design.** §4’s RGB-distance requirement, fixture movement quotas, rotating tremor winners and fixed 10 Hz sampling are proposals requiring approval. RGB distance ≥60 establishes neither visibility nor gentleness. Judge rendered floor illumination against actual substrates, zoom and surrounding light.
- **Time needs a persistence contract.** §§2.1, 3.3, 4 use process uptime, which resets between sessions. Specify whether save/load preserves phase, gesture duration and tremor slots. Persist an epoch/offset using a monotonic double clock; converting an already rounded float to double cannot recover precision. Float uptime spacing reaches 0.125 seconds around twelve days. Test long uptime, restart, pause, backgrounding and two maps.
- **Skipped samples need defined behaviour.** §6B cannot guarantee a 0.8-second visible duration at arbitrary fps. After a hitch, replaying overdue transitions creates bursts; skipping them can erase tremors. Recompute current state once, discard obsolete transitions, and define maximum tolerated delay. Apply budgets to restores too.
- **Ownership lifecycle is incomplete.** §§1, 3.2 need live cases for destruction, minify/reinstall, transport, landing, map removal, unlit release and reload before consumers re-register. Specify tie-breaking, duplicate pushes, invalid ranks, group overlap and disjoint groups. Union allocation must not give a god fixtures outside its permitted group.
- **Small populations break percentages.** §§1, 4: 4% of eleven lamps is 0.44. Flooring disables tremor; rounding up exceeds the cap. Likewise, `max(1,10%)` permits 100% flashers with one lamp. Define integer rules and test 0–25 fixtures.
- **Performance evidence omits the expensive consequence.** §§2.3 K7, 3.3, 6: measure complete frames and subsequent regrids, allocations, maximum latency and synchronized bursts at 11/200/1,000 lamps. B’s average event count hides whole-room changes. Lazy heap invalidation needs bounded storage; direct list indices become stale after removal.
- **Other light mods need arbitration.** §§2.1, 6C: “no Harmony” does not prevent competing writes. Detect external ownership changes; choose exclusive ownership or relinquishment. Restoring the takeover snapshot can overwrite a later user/mod setting. Test both update orders, coloured lamps and variable-radius glowers.
- **Darkness and Narrator rules conflict internally.** §4 L8 permits an unchanged ember forever, and “one fixture per room” need not be visible. Require an observable traveling change with an empty-room fallback. §§4–5 promise fades while prohibiting mixed colours: author discrete ramp entries or explicitly permit bounded interpolation. Define nested letters, cancellation and restore after ownership changes.
- **Proofs need adversarial boundaries.** §§3.1–3.3: “changes per step” depends on sampling interval; screenshots cannot establish motion. Test discontinuities ±epsilon, hitches, collisions and geometry edits. Separate sparse-map functional tests from visual-site requirements. Add live engine colour overlap and regrid measurements.
- **Accessibility is missing.** §§3–5: identity needs slow rhythm/spatial signatures plus an optional text legend for colour-blind players. D3’s changes/minute and 4% fixture cap do not bound screen-area flashes. Test combined effects at every zoom. Offer reduced motion and disable flashes/white wash. Use ≤3 flashes in every rolling second as a conservative ceiling, accounting for luminance and saturated red; this is not a safety guarantee. [W3C guidance](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html)

**PROPOSALS**

- **A:** Strongest fix: weighted architectural distances, stable tie-breaking, quota-preserving allocation and hysteresis. Fixed distance ordering plus an oscillating threshold changes shares and can leave outer fixtures permanently owned. Equal room distances can flip whole rooms together. Invalidate on topology changes, not merely membership changes. Worst failure: stationary territories interrupted by room-wide jumps.
- **B:** Strongest fix: analytical deadlines plus current-state recomputation, bounded heap compaction, stable handles and a global frame budget. Worst failure: stale events or deferred restores leave lamps stuck. Preserve an independent evaluator as the oracle; brute-force sampling alone misses exact boundaries.
- **C:** Strongest fix: prototype fixture-local embers, render through a verified draw callback, and measure batching. Property blocks alone guarantee neither instancing nor one draw call. Alpha blending changes perceived colours despite palette membership. Worst failure: detached luminous paint, obscured combat information and a large white flash.
- **Better hybrid:** first cache membership and eliminate allocations/linear lookups; then use B for deadlines and A for ownership. Keep real glowers expressive. Gate C behind a separate visual prototype.

**FIVE NOVELTIES**

1. **Grammar:** slow approach–pause–withdraw sequences distinguish invitation from warning. Cost: authoring/test matrix; risk: ambiguous meanings.
2. **Territory scars:** retain a faint previous-owner rhythm briefly after transfer. Cost: short history buffer; risk: muddled ownership.
3. **Listening hush:** a room slowly settles when a witnessed deed matters. Cost: witness integration; risk: implying knowledge nobody observed.
4. **Architectural call-and-response:** one wing breathes; another answers seconds later. Cost: graph routing; risk: conspicuous synchronization.
5. **Dark procession:** one dim ember travels between existing fixtures, with overlapping handoffs. Cost: path cache; risk: sparse lamps suggest outages.

**OWNER CARDS, ranked by build impact**

1. **Missing—accessibility contract:** reduced-motion default (lower intensity, weaker language); gentle motion plus independent suppression controls (expressive, more variants).
2. **Q4 medium:** grid only (coherent, limited writhe); bounded overlay (flexible, renderer complexity); main overlay (expressive, greatest intent drift).
3. **Q1 takeover:** manual (predictable, hidden); map-wide opt-in (discoverable, extra action); automatic (immediate, compatibility surprise).
4. **Missing—ownership arbitration:** exclusive takeover (simple, blocks edits); relinquish on external edit (cooperative, may unexpectedly stop).
5. **Missing—reload semantics:** preserve phase (continuity, serialization); restart gently (simple, changes mood timing).
6. **Q2 territory:** wedge (robust, mechanical); architectural tides (situated, topology work); god-specific shapes (language, authoring burden).
7. **Q7 sequence:** live baseline then optimization (measured, delays novelty); Phase 5 first (visible progress, uncertain foundation).
8. **Q3 palette:** retain (restrained, possibly invisible); widen fixed palette (legible, illumination changes); quantized substrate variants (compatible, larger validation matrix).
9. **Q5 white:** HSV region (simple, blunt); perceptual exclusion around reserved white (targeted, requires rendered calibration).
10. **Q6 anger:** include manual switching (consistent, punitive); exclude it (usable, exploitable). Avoid removing vanilla controls.
11. **Q8 sound:** retain non-gating listening notes (preserves intent, maintenance); move them into Phase 6 (cleaner scope, less visibility).