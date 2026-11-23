You review one mod of a RimWorld 1.6 campaign (RimMandrake). We attach its source bundle, in this order: kernels first, then components, patches, settings, defs summary, and its validation script.

Project facts:
- Assume that all DLCs are present.
- Harmony patches.
- Scribe save-compat matters.
- 'one kind of heat'.
- The ship is the only way to the sea floor.
- The owner wants superb Mod Settings and strong offline validation.
- Nobody has run any of this in game since a large refactor that extracted pure kernels.

Produce a review in FOUR labelled parts. Put most effort on part 1.
1. DEBUGGING. Concrete defects and unspotted issues. Look for these:
   - logic errors; save/load (Scribe) losses or renames; null/NRE paths;
   - tick-cadence and performance problems; Harmony patch fragility (target drift, ordering, double patch); thread-safety;
   - settings that do nothing or are not read; off-by-one and float/int rounding; defs that cannot load.
   For each finding, give: file:line, what is wrong, how it fails, a minimal fix, severity (high/medium/low), and confidence.
2. LIKELY FUTURE COMPLICATIONS. What will bite when content is added, when other mods interact, when saves persist across versions, and at scale.
3. UNLEVERAGED OPPORTUNITIES. Things that the mod's machinery could do cheaply and does not do.
4. EXTENSIONS BEYOND THE MOD. Implications for, and reuse by, other mods or content in the campaign.
Be specific; cite code. Do not praise. Do not restate the code. If something is unverifiable from the bundle, say UNVERIFIABLE rather than guessing.
