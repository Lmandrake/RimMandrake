# WORLDMAP_FINAL_REVIEW_1 — the studio review: is this THE map?

Owner, 2026-09-08 worldmap sitting, verbatim charge: *"a final review of the worldmap.
Not just the biome sheets... the map itself. You can start with the csv, but I want you
to screenshot the whole thing in segments. really STARE at it and perform a completely
thorough review... a serious game-dev company-style review. Is this map going to be THE
map?"* Positive and negative both wanted, **earned with evidence**; every critique gets
a corrective, every compliment gets a leverage brainstorm.

Seat: BENCH (Fable), in-sitting. Bridge held. Baseline: **V27** (`WORLDMAP_V27_cs_icons_scoped_2026-09-09`),
canon CSV drift zero as of `9656a389`.

## spec — the review plan (phases; evidence class named per lane)

**Phase 0 — fresh instruments (all layers re-exported LIVE, nothing trusted from disk):**
tiles, links (roads+rivers), mutators (whole planet), landmarks (2,880), world objects/
settlements, features (71). Plus in-engine `world_lint` and `world_mutators_audit` runs.
Everything lands in `Transient/final_review/` with a manifest.

**Phase 1 — measured audits (scripted, MEASURED verdicts):**
- **Rivers**: full graph diagnostics — uphill flow, orphan segments, riverDist
  consistency, mouth/source census; 🔴 the R1 ruling test: rivers must READ as leaving
  the Scald (engine draws it as a basin — test the graph, not the elevation); river/biome
  harmony (allowRivers hidden links).
- **Roads**: settlement connectivity components, orphan stubs, roads crossing
  allowRoads=false biomes (stored-but-invisible), dead-ends that serve nothing.
- **Mutators**: per-biome density + variety, gate violations (needs-river/coast/hilliness
  written illegally), the never-used census vs placed, stacking extremes.
- **Landmarks**: density per biome/region, stacked-on-settlement violations, icon
  coverage vs density (the Rust Cathedral lesson), name quality sample.
- **Settlements & factions**: roster per faction vs `faction_world_spec.md`, biome fit
  post-rejigger, spacing/clustering stats, unreachable-by-road settlements.
- **Biome distribution**: adjacency seam audit (every biome-pair border length vs the
  sheets' declared neighbors/cross-flows), dryland-ladder monotonicity (arc vs temp),
  water bodies vs `the_seas.md`.
- **Landforms**: hilliness composition per biome vs sheet claims, elevation profiles of
  named massifs (Scald rim, the Forge, Rimewall), basin/ridge sanity.

**Phase 2 — the STARE (bridge `world_view` + screenshots, judged in-window by Fable):**
- ~18 global segments: substellar, 4 dayside (arc≈45), 8 terminator ring (arc≈90), 4
  nightside (arc≈135), antistellar — overlapping, `clear_ui` + dialogs closed each shot.
- ~12 named-site closeups: the Scald + rim, Rust Cathedral, Umbra + the lake, Dune Sea,
  the Greentide/delta country, Cracked Lands, Fall Line, the two seas, the Forge,
  Pyrelands, the Ashfall Range, road-network wide shots.
- Per segment: landform readability, composition/color, label fit, icon clutter or
  barrenness, coastline quality, anything that snags the eye — positive snags included.

**Phase 3 — text & lore (Fable judgment):**
- Every player-visible string the world screen serves: biome labels/descriptions
  (BiomeNames_Ashkarr + our defs), landmark descriptions, feature names, settlement
  names, scenario text items. 🔴 **Plot-leak check**: text describes what IS — no
  past-why (Rakatan reveal ladder, the war lab, terramanufacture) and no not-yet-happened
  story; the §P/§GM partitions in scarlands/rust-cathedral sheets are the rule source.
- Qualitative lore-vs-map comparison: each sheet's landform prose (canyons, rims, discs,
  arcs) checked against what Phase 1/2 actually found.

**Phase 4 — the report:**
One comprehensive document: per-domain findings (each tagged MEASURED / SEEN / JUDGED,
with the evidence), critiques each carrying a corrective, compliments each carrying a
leverage brainstorm, and the verdict on THE map with whatever punch list stands between
here and it. Screenshots referenced by full native path.

## execution shape
BENCH orchestrates: Phase 1 audit scripts run as backgrounded subagents (sonnet) writing
findings files; Phase 2 staring and Phase 3 judgment are done in-window (Fable, per the
L3 Fable-evaluation carve-out — the owner asked *me* to stare); Phase 4 synthesis
in-window. Read-only against the world unless the owner rules otherwise per finding.

## verify
- Every numeric claim in the report traces to a Phase-0 export or an in-engine audit run.
- Every visual claim names its screenshot (full native path).
- Plot-leak verdicts quote the offending string verbatim.

## criteria
The owner reads one report and can answer "is this THE map?" — with a punch list whose
items are each: the finding, the evidence, the corrective, the cost.

## 2026-09-09 (BENCH, AFK): deliberately NOT started despite bridge-free
The paint is mid-churn: BIOME_OWNERSHIP_WAVE_1 is being executed live by the other
window (RUT_BlueDesert already repainted; RUT_Sump/TheForge/TheRot/Umbra/… defs
authored and switching). A FINAL review measured now audits a moving target and its
verdicts decay within hours; the STARE half needs the owner besides. Run it after
the ownership switches settle — its Phase-0 fresh exports will then measure the map
the owner is actually judging.
