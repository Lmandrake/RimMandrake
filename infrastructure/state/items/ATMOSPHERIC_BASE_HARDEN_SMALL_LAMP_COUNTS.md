# ATMOSPHERIC_BASE_HARDEN_SMALL_LAMP_COUNTS

Source: design/RimMandrake/atmospheric_base_review_package_2026-10-24.gpt_review.md (lines 9, 7, 10, 12, 19). GPT opinion. The accessibility finding (line 14) is VOID per owner; do not act on it.

## spec
GPT quotes:
- "Small populations break percentages. 4% of eleven lamps is 0.44. Flooring disables tremor; rounding up exceeds the cap. Likewise, max(1,10%) permits 100% flashers with one lamp. Define integer rules and test 0-25 fixtures."
- "After a hitch, replaying overdue transitions creates bursts; skipping them can erase tremors. Recompute current state once, discard obsolete transitions, and define maximum tolerated delay. Apply budgets to restores too."
- "Performance evidence omits the expensive consequence ... measure complete frames and subsequent regrids, allocations, maximum latency and synchronized bursts at 11/200/1,000 lamps."
- "Darkness ... section 4 L8 permits an unchanged ember forever, and 'one fixture per room' need not be visible. Require an observable traveling change with an empty-room fallback."

Build: amend the AtmosphericBase spec and code with explicit integer quota rules (state the chosen rounding and minimum), hitch-recompute behaviour with a max delay constant, and a travelling ember.

## verify
- Selftest sweeping fixture counts 0..25: quota never exceeds the stated cap and never silently zero where the spec says at least one.
- Hitch test: after a simulated long frame, one recompute, no burst of replayed transitions.
- Measurement file at 11/200/1000 lamps (frame time + regrid), path recorded.
- Ember test: position changes over time; empty-room fallback defined.
