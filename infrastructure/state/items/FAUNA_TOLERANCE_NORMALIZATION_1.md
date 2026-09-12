# FAUNA_TOLERANCE_NORMALIZATION_1 — canonical graphs, now biome-aware

The owner, 2026-09-11, returning to the normalization loop: *"plotting certain
parameters vs. other parameters in canonical graphs... Animals should have wide
tolerances that let them survive easily in their domains of choice. And the
damages needed significant modification based on bodysize."* The fauna
assignment sitting (decisions_propagated.json) gives every animal a domain for
the first time — tolerance normalization can finally be judged per-biome.

## spec
1. **New law (Law 5?): temperature tolerance covers the domain, widely.** Each
   rostered animal's ComfortableTemperature range must comfortably envelop its
   ASSIGNED biome(s)' temperature envelope — wide margins, survival easy in its
   home. Domain truth = `round2/decisions_propagated.json` + `move_mapping_v2.md`
   (rosters lag until ROSTER_MOVE_APPLY_1 lands). The four normalization laws in
   `design/Jawa/worldbuilding/beast_normalization_spec.md` say NOTHING about
   temperature — this is new scope, add it to that spec, don't fork a second one.
2. **Law 3 extension: damage ≈ K×bodySize for the FULL rostered set**, not just
   the 161 SW beasts BEAST_DANGER_NORMALIZATION_1 already shipped
   (`BeastNorm_Law3.xml`). Same K 12-15, same sublinear-DPS shape, same
   manifest-driven execution; AA_/BMT_/GR_/DA_/vanilla-etc. kinds now in play.
3. **Products as a plotted axis** (meat, leather amounts vs bodySize) — plot
   first, rule after; no target curve is pre-agreed.
4. **The canonical graphs are the sitting instrument**: scatter plots
   (damage vs bodySize, DPS vs bodySize, temp-range vs biome envelope, products
   vs bodySize), outliers labeled by defName, one PNG set per axis pair, owner
   looks and rules, manifest freezes.

## RULED — owner, 2026-09-11 (phone card sitting, graphs artifact a7327077)

1. **Law 3 extension: K = 12–15 × bodySize for ALL 326 rostered animals.**
   One band, whole roster — grazers rise too. Supersedes nothing (the 161 SW
   beasts already sit in this band); AA_/BMT_/GR_/DA_/vanilla kinds now in play.
2. **Tolerance law (Law 5): domain envelope +15 °C on BOTH sides.** Every
   rostered animal's comfort range covers its assigned biome's temperature
   envelope plus 15 °C margin each way. Numeric, checkable. The 23 flagged
   narrows widen to meet it. Add to beast_normalization_spec.md, not a fork.
3. **Products: bodySize-proportional defaults NOW** (meat/leather ∝ bodySize);
   re-checked against live engine values when FAUNA_STATS_BRIDGE_TOOL_1 lands.
   Accepted trade: may be redone on real numbers.
4. **Above-band outliers come into the size band — no exemption list now.**
   Owner verbatim: *"We need to look at the art and eventual description to
   deduce whether a beast is particularly scary or harmless. Diversity is
   good. I am less interested in forcing everyone to a scaling and more that
   we allow huge things to terrify and tiny things to be harmless. So let's
   scale by size first. Then we can make a later round of diversification
   decision when we make the beast graphics and lore."* Size scaling is pass
   one (JOE_Nautilant at bs 8 comes down to the band); per-beast
   diversification is a LATER round tied to art+lore —
   FAUNA_LORE_DIVERSIFICATION_1. Does NOT change: bodySize itself, per the
   ceiling-fields lesson (each parameter its own law).

## OFFLINE PASS DONE (BENCH subagent, 2026-09-11)

- **Law 5 drafted linter-checkable** into `beast_normalization_spec.md` §2d
  (envelope = [p05,p95] of tile `temp_c` over the assigned biomes' painted
  defs, comfy range must reach envelope ±15 °C, widening-only, post-patch
  stats). §2e records the Law 3 full-roster extension and Law 6 products
  ruling in the same spec — no fork.
- **Violations census, MEASURED from mod XML** (`animal_inventory.py`,
  inheritance-resolved, LoadFolders-aware, PRE-patch):
  **196 of 279 measurable rostered animals VIOLATE** · 83 OK ·
  15 ENV_UNMEASURED (fall_line/the_lantern_deeps/wreck_fields have no painted
  tiles) · 3 XML_UNMEASURED (GR_Mantistanis, MA_Sporemole, VAEWaste_Hydra).
  Files: `design/Jawa/worldbuilding/fauna_tolerance_census_2026-09-11.csv`
  (297 rows, fingerprints in header) and
  `.../fauna_tolerance_violations_2026-09-11.md`. Roster derived live:
  decisions_propagated.json `in` rows + move_mapping_v2.md targets
  (+ GR_ParagonThrumbo's PLACED note) = 297 biome-assigned defNames — the
  ruling's "326" and "23 narrows" were graphs-artifact-era counts, superseded
  by this census.
- **Live harvest must confirm**: post-patch stat values (PatchOperations,
  gene/comp offsets, CherryPicker state — all invisible to base XML), the 3
  XML_UNMEASURED defs and the OuterRim droids, and realized seasonal extremes
  (tile temp_c is the map-gen mean). Harvest AFTER the restore, fingerprint-
  matched.
- **Plots for the owner's sitting ride the POST-restore harvest — out of
  scope for this offline pass.**

## traps
- 🔴 The offline def dump has NO statBases and drops fields — the census must
  come from mod XML or a live harvest, fingerprint-matched to the CURRENT mod
  set. `beast_census.csv` (fingerprint 1742630eb6253187) predates the culls and
  the 2026-09-11 CherryPicker restore — stale, do not trust without re-verify.
- Harvest AFTER the current batch restart completes and refresh.py reruns —
  the restore changes the live def set.
- bodySize ≠ melee damage in "scale all" passes (ceiling-fields lesson); each
  parameter gets its own law, never one multiplier.
- Cherry Picker cuts are invisible to the dump (commonality 0) — census the
  live set, not the mod folders.

## verify
- [ ] Every plot's data source states its fingerprint; MEASURED counts only.
- [ ] Owner has ruled the tolerance law's margins at the graph sitting.
- [ ] Patches validate --live and --defs; a patch that matches nothing logs
      nothing.

## criteria
- [ ] No rostered animal's comfort range excludes its assigned biome's envelope.
- [ ] The manifest (defName, old/new values, exemptions) is the decision record,
      committed.
