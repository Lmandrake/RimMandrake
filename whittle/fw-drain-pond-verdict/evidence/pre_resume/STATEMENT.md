# Pond shallowing acceptance must actually show a partial stage

The pond-depth proof should distinguish shallowing from an unchanged deep-water picture.

- When the pond surface falls and its census still contains only deep water, pond_depth_verdict returns FAIL/MOD rather than accepting a partial-depth stage.
- Genuine chest-deep, shallow or thin stages remain acceptable when the existing stable-wet-count and falling-surface conditions hold; a mixed deep/partial census is also valid.
- Existing no-pump, nonapplicable-body, insufficient-reading and shrinking-from-the-rim classifications remain intact, and focused regression checks execute the production predicate and fail against the original false-safe implementation.
