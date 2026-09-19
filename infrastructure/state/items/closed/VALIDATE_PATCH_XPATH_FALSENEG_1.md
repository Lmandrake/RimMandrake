## spec
Found during standing dirty-code-review wave (2026-09-05), reviewing
`src/RimStarWars/StarWarsPatches/Patches/EggLayersLayEggs.xml`.
`validate_patch.py`'s xpath hit-count check reported 0 matches for a guard
xpath of the shape `genes/li="Outland_EggLayer"` (a nested double-quoted
predicate) against the live def dump — the reviewing subagent independently
confirmed via direct `lxml` evaluation against the real root element that
this xpath correctly matches all 19 real xenotype targets. The tool's
primary engine is `lxml` (full XPath 1.0) per its own startup banner, but it
also carries an `ElementTree` fallback path for when `lxml` is unavailable —
the false-negative traces to that fallback's translation of this specific
nested-predicate shape, not to the primary lxml path (the subagent's
independent lxml check is what proved the patch itself correct).

## why this matters
This is exactly the class of instrument this project has been burned by
repeatedly ("instruments that lie with a number") — a "0 matches" report
from the tool that CLAUDE.md's own doctrine treats as strong evidence of a
silently-broken patch. If the ElementTree fallback path is what's actually
running in some environment (not confirmed which — needs investigation),
future reviews could wrongly "fix" a correct patch based on this false
signal, or ship an actually-broken patch that this same fallback happens to
report a false positive for the same way in reverse.

## criteria
- Reproduce the false negative directly: run `validate_patch.py` against
  `EggLayersLayEggs.xml` and confirm which xpath engine (lxml vs
  ElementTree) actually ran, and under what condition the ElementTree
  fallback triggers (missing `lxml` install? a specific xpath shape it
  can't translate?).
- Fix the translation for nested double-quoted-predicate xpaths in the
  ElementTree fallback, or if `lxml` is effectively always available in
  this environment, consider whether the fallback path is worth keeping at
  all (a silently-wrong fallback is worse than an explicit hard dependency).
- Add a regression test: a plan/patch with this exact xpath shape, asserting
  a nonzero hit count under whichever engine actually runs in CI/local dev.
