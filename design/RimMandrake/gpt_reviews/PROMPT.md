You review one mod of a RimWorld 1.6 campaign (RimMandrake). We attach its source bundle, in this order: kernels first, then components, patches, settings, defs summary, and its validation script.

Project facts:
- Assume that all DLCs are present.
- Harmony patches.
- Scribe save-compat matters.
- 'one kind of heat'.
- The ship is the only way to the sea floor.
- The owner wants superb Mod Settings and strong offline validation.
- Nobody has run any of this in game since a large refactor that extracted pure kernels.

What counts as a finding: a finding is significant when you measured it, or when you predict it with a concrete case (this input, this wrong result), to break something the mod promises the player or to cause a failure in ordinary play. A prediction with no concrete case is not significant. A rare failure that needs a second failure, or an input that nothing produces, is not significant.

Enough, and when to stop: one full read of the bundle. Report every significant finding and stop. Do not search for more to fill a part; an empty part is a complete answer.

The polish route: anything that is not significant (style, a minor nit, a stricter test, robustness against an input that nothing produces) is one line in a list headed POLISH at the end. Nobody works that list, and no ticket comes from it.

Produce a review in FOUR labelled parts, then the POLISH list. Put most effort on part 1.
1. DEBUGGING. Significant findings only. Look for these:
   - logic errors; save/load (Scribe) losses or renames; null/NRE paths;
   - tick-cadence and performance problems; Harmony patch fragility (target drift, ordering, double patch); thread-safety;
   - settings that do nothing or are not read; off-by-one and float/int rounding; defs that cannot load.
   For each finding, give: file:line, what is wrong, how it fails, the concrete case (this input, this wrong result), a minimal fix, severity (high/medium/low), and confidence.
2. LIKELY FUTURE COMPLICATIONS. What will bite when content is added, when other mods interact, when saves persist across versions, and at scale.
3. UNLEVERAGED OPPORTUNITIES. Things that the mod's machinery could do cheaply and does not do.
4. EXTENSIONS BEYOND THE MOD. Implications for, and reuse by, other mods or content in the campaign.
Parts 2, 3 and 4 are ideas for a human to read. They are not findings: no ticket comes from them.
Be specific; cite code. Do not praise. Do not restate the code. If something is unverifiable from the bundle, say UNVERIFIABLE rather than guessing.
