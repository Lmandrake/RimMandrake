# RIMMANDRAKE_CLASSIFY_VV_REDS_EDGE_SINKS_OFF_LEDGER_GAP

One source event: the rm-vv-matrix run of 2026-11-19 19:06 PST. Results:
D:\ClaudeWork\rimmandrake\build\VV_PILOT1_550eaa96_results\20261119T182941

## spec

The matrix's pre-declared criterion does not gate these reds: a red at a single-flag-off configuration is classified
in the report, and the SHIPPED suite is not gated. They were not that run's FAIL. That FAIL was a staging fault, fixed
under RIMMANDRAKE_INSTALL_VV_MATRIX_CLOCK_WRITTEN_NOT_RUNNING. Nobody has touched the mod.

For each case below, say which of two things it is:
- a kernel fault that a player reaches with his own settings (edgeSinksEnabled is a player setting); or
- a test pinned to the authored configuration that cannot hold when the configuration is forced.

The cases:
1. OFF_edgeSinksEnabled, kernel_fuzz: 142 of 2000 seeds red (rates.jsonl).
   - Seed 500029 (7x8, 8 pulses, limitless=True sinks=True visc=False): "pulse 6: sink drained 0, cells account for 1".
   - Seed 500031: "cells account for 0.7143".
2. Six suite tests red only at the forced SHIPPED configuration (suite_SHIPPED.stdout.txt):
   - Rain_pocket_sliced_equals_atomic_and_inert_dry ("sliced pocket rain differs from atomic")
   - StepPulse_shrink_end_state_pinned (digest)
   - ExcavationTick_exact_shortcuts_equal_reference ("scenes do not exercise both shortcuts")
   - ExcavationTick_sliced_pulse_equals_atomic
   - CsReview_exact_dry_square_skips_a_switched_off_source
   - CsReview_exact_dry_square_skips_an_unclaimable_source

## verify

Each case has a written class, backed by a test or a seed replay. A kernel fault gets a ticket of its own, with a
failing test. For a pinned test, name the configuration that it pins.
