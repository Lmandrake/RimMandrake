# VANILLA_COUNT_PSEUDO_DEF_1

Split off KOTOR_HEADBAND_DANGLING_REFS_1's crossref bucket (2026-09-03 big-dump
harvest): alongside the 23 guy762_Headband_* dangling refs (root cause found
and fixed separately — an accidental file deletion in 8c946ec9, restored),
the same harvest logged unresolved crossrefs to `MealSimple10`, `Chemfuel60`,
`Steel75`, `Silver120`, `ComponentIndustrial12` — none of which are real
defNames in vanilla or any def dump. Shape strongly suggests some mod wrote
`<li>MealSimple10</li>`-style entries meaning "10x MealSimple" where the
schema actually wants a `<def>`/`<count>` pair or a `Thing count=N` structure,
and the literal concatenated string got treated as a defName reference.

grep across `src/` for these five literal tokens returns zero hits, so the
offending file is in a third-party donor mod (live Mods folder or a
vendor/mod_sources snapshot), not our own authored content — this needs the
live crossref/dangling-ref report (or a fresh harvest) to name the source
file, not a repo grep.

## spec

Identify which mod/file emits these five (or more — the harvest only sampled)
count-suffixed pseudo-defNames, and confirm whether it's fixable on our side
(a patch we own referencing it wrong) or purely third-party donor content
(then it's just noted, not ours to fix).

## verify

Re-run the same dangling-crossref harvest that KOTOR_HEADBAND_DANGLING_REFS_1
came from; these five entries should either resolve to a named, findable
source file, or be confirmed third-party/unfixable.

## criteria

Source file named. If ours: fixed and the crossref count drops. If
third-party: recorded here as such and left alone.
