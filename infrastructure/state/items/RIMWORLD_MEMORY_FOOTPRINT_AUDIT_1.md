# RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1 — why the game runs 18GB+ and sometimes crashes for memory reasons

Owner, 2026-09-07 (verbatim in intent): *"Please add a ticket to do a deep-dive on why
the game is 18GB or more in memory footprint. It sometimes seems to crash for memory
reasons, and it might be worth examining things like compression or other approaches
that might reduce that. Worth a deep Opus analysis on how to reduce Rimworld memory
consumption, the worst mod offenders, etc."*

## spec
- **Measure first**: current live memory footprint (RSS of the RimWorld process) at a
  cold load on the full mod list (599 active mods per `ModsConfig.xml` as of
  2026-09-07 — re-read it, it drifts) and again after a long play session, since
  "18GB or more" may be steady-state, a leak, or a peak during a specific operation
  (worldgen, a big map, a save). Distinguish these three before attributing cause.
- **Worst-offender census**: per-mod memory contribution is not directly measurable
  without profiling, but proxy signals are: texture/AssetBundle size on disk per mod
  (`du` per workshop folder — a real MEASURED figure, not a guess), asset resolution
  and count (many biome/animal/weapon-pack mods ship large texture atlases), and
  whether a mod ships an AssetBundle vs loose PNGs (RimWorld keeps loaded textures in
  memory differently depending on path). Rank the top N mods by on-disk asset weight
  as a starting hypothesis, then check whether Player.log or a memory profiler
  corroborates that ranking — a big mod folder is not proof it dominates RAM.
- **Crash correlation**: check whether existing crash reports/Player.log captures
  (several already sit in `Transient/`, e.g. `crash_report_20260905_225503*.md`,
  `crash_report_20260906_055852.md`, `rimworld_mem_watch_2026-09-05.log`) show an
  OutOfMemory pattern, a specific mod's stack trace, or a specific operation (map
  gen, world gen, save/load) at the moment of the crash — read what's already been
  captured before generating new crash data.
- **Reduction approaches to evaluate** (owner's own suggestion, "compression or other
  approaches"): texture compression settings/formats already in use vs available,
  whether any active mod ships uncompressed or oversized textures that could be
  re-encoded without visible quality loss, RimWorld's own texture streaming/quality
  settings, mod-level opportunities (retexturing a bloated donor mod's assets is
  already a pattern this project uses via Cherry Picker/absorption — cross-reference
  `WEAPONS_DONOR_RETIREMENT_1`-style absorption work for precedent), and whether
  trimming unused content from an already-absorbed mod (dead defs, dropped textures)
  meaningfully helps.
- 🔴 **This is diagnostic and analytical, not a rebuild** — the deliverable is a
  report: the actual measured footprint, the ranked list of worst offenders with
  real numbers (never a guess dressed as a finding — `measuring-large-artifacts`
  applies to any large-file/mod-folder size claim), and a set of concrete,
  owner-decidable reduction options with their expected savings and trade-offs
  (visual quality, load time, compatibility). Building any actual fix is separate,
  owner-ruled follow-up work once the report lands.
- Owner asked for this to ride a **deep Opus-tier analysis pass** — size the model
  accordingly per `infrastructure/agents/Agent_Policy.md` rather than defaulting to
  a cheap fan-out for the synthesis step; cheap models are fine for the mechanical
  measurement/census legwork feeding into it.

## verify
A written report (Transient/ for the human-readable version, cited from this item)
with: measured RSS at cold-load and after extended play, a ranked worst-offender
list backed by real per-mod measurements, crash-log correlation findings (or
"UNMEASURED, no OOM pattern found in captured logs"), and 3-5 concrete reduction
options with estimated impact, presented as owner-decidable choices, not a
unilateral fix.
