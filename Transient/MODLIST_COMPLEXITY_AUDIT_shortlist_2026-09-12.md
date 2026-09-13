# MODLIST_COMPLEXITY_AUDIT_1 — ranked keep-or-cut shortlist (beyond Giddy-Up)

Background analysis, 2026-09-12 (second pass). Ranked by risk-to-contribution,
worst first. Every claim about this machine is from disk; web-sourced background
is labeled. Giddy-Up/Run-and-Gun excluded (sibling item GIDDYUP_KEEP_OR_CUT_1).
`krkr.rule56` (CAI-5000) + `mlie.nwnrealfogofwar` excluded by standing owner
ruling (Route B fog pair — `infrastructure/state/items/FOG_REVIEW_SITTING_WITH_OWNER_1.md`:
dropping CAI removes no fog; the NWN switch is `onlyOutsideColony`). Not re-litigated.

Relationship to the earlier same-day report
(`Transient/modlist_keep_or_cut_shortlist_2026-09-12.md`, 19:10): this pass
carries its sound rows forward, CORRECTS its #1 (Caravan Adventures CUT is
stale — the owner ruled strip-stats-keep-quests on 2026-09-11, ledger:
"caravanadventures strip-stats-keep-quests (STAT_NORM_WAVE3_RETIRE_1)"), and
adds three families it missed (facial-animation pile, romance pile, caverns
mapgen spawner).

Mod count source: live ModsConfig at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`
currently holds the FULL list (read 2026-09-12). Exact active count: UNMEASURED
in this pass (single-line XML; no `measure` run) — "~594" is the working figure.

## Shortlist (worst risk-to-contribution first)

1. **dubwise.dubsperformanceanalyzer.steam** (Dubs Performance Analyzer)
   - Gives: profiling, when someone is actually profiling. Zero play content.
   - Risks: a Harmony-patching dev instrument riding every load of the shipping list.
   - Evidence: present in live ModsConfig; no content reference anywhere in
     `src/RimMandrake/` or `design/Jawa/`.
   - Disposition: **CUT from the standing list, re-enable on demand** (one
     ModsConfig line when a perf session needs it).
   - Trade: one extra restart when profiling, versus a patcher gone from every play load.

2. **mlie.jurassicrimworlddinosaursonly** (Jurassic Rimworld — Dinosaurs Only)
   - Gives: a dino pool with **0 cast rows** (prior report, measured against
     cast_assignment.csv); non-SW on a Star Wars world.
   - Risks: none new — it is ALREADY RETIRED by owner ruling 2026-09-05
     (`infrastructure/state/facts/retired_mods.json`: "eight creatures absorbed
     into mandrake.rsw.swbestiary") **yet still sits in the live ModsConfig**.
     A generator or dump consumer can resurrect its content any day it stays.
   - Disposition: **EXECUTE the existing retirement** — after the
     texPath/donor-art reachability check the prior report flagged (retextures
     bind by texPath; a naive grep lies).
   - Trade: none — the ruling is already made; this closes the gap between ruling and disk.

3. **Facial-animation pile (5 mods)** — `nals.facialanimation`,
   `nals.facialanimationexperimentals`, `danzinagri.facialanimationcompatabilityproject`,
   `reel.facialanims` (+ `sd.fa.reelsadjustments`), `vanillaexpanded.vtexe.facialanims`
   - Gives: animated pawn faces — pure visual flair, no mechanics.
   - Risks: per-pawn-draw render patching times five cooperating mods; a
     compat-project mod existing at all is evidence the base mod conflicts
     widely (that inference, not disk). Local trail is thin: one
     `FacialAnimationPatch` frame in
     `Transient/Player_log_582_recovery_reset_diagnosis_2026-09-09.log` (weak,
     presence not culpability) and one ledger mention.
   - Disposition: **TRIM via card** — keep `nals.facialanimation` + the compat
     project if he likes the faces; the experimentals and add-on layers are the
     cut candidates.
   - Trade: slightly plainer faces versus three fewer render patchers when the next draw-loop bug lands.

4. **Combat-animation pile** — `mlie.yayoscombat3` +
   `co.uk.epicguru.meleeanimation` + `fuu.bloodanimations`, stacked on CAI-5000
   - Gives: combat visual flair and (Yayo) optional mechanics.
   - Risks: four mods patching the same fight (CAI ruled in, so three
     discretionary); classic confounder pile — the next combat bug is a
     four-way attribution job. No crash trail yet (one ledger mention).
   - Disposition: **TRIM by one via card** — ask which of yayoscombat3 /
     meleeanimation he actually notices in play.
   - Trade: visual flair versus untangling future combat bugs across four patchers.

5. **arkymn.slowerpawntickrate** vs **taranchuk.performanceoptimizer**
   - Gives: performance, twice, by different timing hacks.
   - Risks: slowerpawntickrate changes sim timing under every other mod —
     subtle, unattributable behavior shifts; two timing mods doubles it.
     Evidence: both in live ModsConfig; ledger mentions only (no defect yet).
   - Disposition: **CARD — keep exactly one** (performanceoptimizer is the
     broader, better-known one; web-sourced characterization, labeled as such).
   - Trade: some perf versus attributability of every future timing bug.

6. **Romance/intimacy pile (8 mods)** — `mianreplicate.romanceandintimacyontherim`,
   `telardo.romanceontherim`, `divinederivative.romance`,
   `lovelydovey.sex.witheuterpe`, `lovelydovey.sex.withrosaline`,
   `lovelydovey.recreation.witheuterpe`, `udon.masslovein`, `gulmadred.breedingritual`
   - Gives: social/romance depth. One IS load-bearing: ledger records "(Romance
     On The Rim) has 476 instances on the live Ash'karr colony map".
   - Risks: eight mods in one domain, all patching pawn interaction/thought
     systems; overlap invites double-firing thoughts and attribution swamps.
   - Disposition: **CARD — keep the load-bearing core (telardo + one framework),
     name each of the rest for keep/cut**.
   - Trade: niche interaction content versus a five-mod reduction in social-system patch surface.

7. **vanillaexpanded.vgeneticse** (Vanilla Genetics Expanded)
   - Gives: a few cast biome animals (GR_ hybrids in BiomeCast); the genetics
     lab is off-theme for a scavenger clan.
   - Risks: **91 GR_ hybrids Cherry-Picked out** (prior report, config read
     2026-09-12); GIDDYUP_NULLKEY_CRASH_1's null key was `GR_Mantistanis` (a
     dead ref from this family, ledger); a large C# mod carrying mostly-cut content.
   - Disposition: **CENSUS then card** — measure what cast + save actually use;
     if a handful, port RSW_ (the MLIE absorption pattern) and cut.
   - Trade: porting work versus a big, mostly-hollow donor gone.

8. **biomesteam.biomescaverns** (Biomes! Caverns, Caveworld_Flora_Unleashed)
   - Gives: cavern content — on a campaign whose world is surface desert
     (Ash'karr; local features doctrine).
   - Risks: its `MapComponent_CaveFungus.MapGenerated` mycelium spawner is in
     the quicktest crash stack
     (`Transient/Player_log_C1_run2_clean_then_quicktest_crash_2026-09-08.log`,
     tail: Caveworld_Flora_Unleashed.SpawnNewMyceliumAt → GenSpawn.Spawn →
     Vehicles.Patch_Construction). Presence in the fatal stack, shared with VF —
     culprit not proven, but it runs code at every mapgen.
   - Disposition: **CARD — justify caverns on a desert world or cut the family**
     (check `biomesteam.biomespollutedlands` and `biomesteam.biomesfossils` in
     the same sitting).
   - Trade: underground variety the frozen world may never show versus a mapgen-time spawner out of every map roll.

9. **Urban-ruins family (5 mods)** — `xmb.ancienturbanruins.mo`,
   `meteores.ancienturbanruinsalldeconstructible.aurad`,
   `meteores.ancienturbanruinsvanillaloot.aurvl`, `mlie.dungeonpack`, `gmmp.dungeon`
   - Earth-flavored ruins already marked as a donor pool to mine
     (FASCINATING_WORLD_JUNK_1 Phase 2, per prior report).
   - Disposition: **CONFIRM the timeline — mine, then cut the family.**
   - Trade: none once mining lands; cutting early loses the idea pool.

10. **mlie.moevents** (Mo'Events)
    - Its 8 event mechanics are being ported as our own workers
      (RUT_SCAVENGEREVENTS_BUILD_1; `mandrake.rut.scavengerevents` is already
      in the live list); the plan already says retire it before save freeze.
    - Disposition: **KEEP until the port lands, then CUT (ratify existing plan);
      interim: zero MO_ baseChances via its settings.**
    - Trade: none — the card ratifies what is already planned.

11. **Tree retexture trio** — `maal.bettertreesmod`, `qux.comigo.bettertreesmod`,
    `chaoticenrico.bettertrees`
    - Three tree-visual mods; the winner is texPath-binding order luck.
    - Disposition: **keep one, cut two — owner picks by screenshot.**
    - Trade: none visible if the kept one covers the biomes shown.

12. **iforgotmysocks.caravanadventures** (Caravan Adventures) — **ALREADY RULED**
    - Owner, 2026-09-11 (ledger, Wave 3): strip-stats-keep-quests
      (STAT_NORM_WAVE3_RETIRE_1) — counter-patch its stat edits to neutral,
      keep the quest layer. The earlier report's CUT card is superseded by
      this ruling and must not be re-served.
    - Its three local defect trails (Empire whitelist injection, InitGC
      save-compat regression, TravelCompanions non-apply) stand on record:
      first NEW incident after the counter-patch reopens the cut question.
    - Disposition: **execute the existing ruling; watch.**

13. **zal.betterinfestations** — historic breaker class (web reputation,
    labeled); no local incident on disk; infestations barely feature on
    Ash'karr surface. Disposition: **KEEP, cut on first local incident.**

## Weighed and NOT shortlisted (so the audit shows its work)
- **smashphil.vehicleframework** + vehicle family: the single largest local
  defect family (a dozen VEHICLE_* ledger items; also in the quicktest crash
  stack via Patch_Construction) — but the campaign is heavily invested
  (mandrake.rsw.desertvehiclereskin, VEHICLE_ION_TIER_1, fuel doctrine).
  Contribution matches the risk. KEEP; it is the maintenance budget, not a cut.
- **mlie.beastsoftherim**: retired by ruling, absorption in flight
  (BMT_FAUNA_ABSORPTION_1) — still-active is expected mid-execution, not a defect.
- **mlie.horrors**: nightside raiding faction is designed-in
  (HORRORS_RAIDING_FACTION_1). KEEP, gated per that item.
- **Dubs family** (bad hygiene lite+thirst, rimefeller, mint menus/minimap,
  paintshop, break mod): each carries used content or UI the owner touches;
  no local defect trail found. Not shortlisted this pass.

## Cards to serve first
1. Profiler out of the play stack (zero-content risk reduction, one line).
2. Execute the Jurassic retirement already ruled (after the texPath check).
3. Facial-animation pile trim (biggest discretionary render surface).
