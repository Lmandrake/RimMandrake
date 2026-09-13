# Keep-or-cut shortlist beyond Giddy-Up — MODLIST_COMPLEXITY_AUDIT_1

BENCH background analysis, 2026-09-12 (AFK). Ranked by risk-to-value, worst
first. Every claim about this machine is from disk (items, ledger, Cherry
Picker config, cast CSV, mod folders); nothing executes without an owner card.
Giddy-Up itself: sibling analysis `Transient/giddyup_keep_or_cut_2026-09-12.md`
(GIDDYUP_KEEP_OR_CUT_1). Excluded by standing ruling: `krkr.rule56` (CAI-5000)
+ `mlie.nwnrealfogofwar` — the owner-ruled Route B fog pair
(FOW_ROUTE_B_INTEGRATION_1, cai_fog_deep_dive_2026-08-31.md); not re-litigated.

Context number: Cherry Picker currently carries **2,286 cut entries** (config
read 2026-09-12). Many belong to mods ALREADY retired (AM_/AEXP_/Isekai_/BS_
samples resolve to nothing live) — the config is residue-heavy and not by
itself proof a mod is active-but-hollow.

## The shortlist

1. **iforgotmysocks.caravanadventures** — Caravan Adventures
   - Gives: caravan QoL, companion thoughts, its own "ancient machines" story arc.
   - Risks/costs: THREE separate local defect trails — runtime faction injection
     (`StoryUtility.cs` adds sacrilegHunters/mechanoids, EMPIRE_WHITELIST_OVERRIDDEN_1);
     save-compat GC that trips on retired donors regardless of use
     (`CaravanAdventures.InitGC` packUpFilter, DROID_DONOR_SAVE_COMPAT_REGRESSION_1);
     `ThoughtDef::TravelCompanions` in PAWN_FLAVOR_SILENT_NONAPPLY_1. Its story arc
     COMPETES with our own Rakata campaign on a gravship (not caravan) scenario.
   - Disposition option: **CUT**. Trade: lose caravan QoL and companion mood
     content the campaign barely uses; shed a proven repeat confounder whose
     signature story duplicates ours.

2. **dubwise.dubsperformanceanalyzer.steam** — a PROFILER in the play stack
   - Gives: performance analysis when someone is actually profiling.
   - Risks/costs: a Harmony-patching dev instrument riding every load of the
     shipping list; nonzero overhead and patch surface for zero play content.
   - Disposition option: **CUT from the standing list, enable on demand** (it is
     a toggleable dev tool, not content; re-enable takes one ModsConfig line
     when a perf session needs it). Trade: one extra restart when profiling.

3. **mlie.jurassicrimworlddinosaursonly** — dinosaurs on a Star Wars world
   - Gives: nothing the campaign uses that disk shows — **0 cast rows** in
     cast_assignment.csv; BEAST_DANGER_NORMALIZATION_1 explicitly lists
     "Jurassic herbivores" as non-SW offenders out of scope; More Vanilla
     Biomes ships a Jurassic patch file that is live pure overhead
     (BIOME_DUPLICATES_STILL_LIVE_1).
   - Caveat: donor-art/retexture use UNMEASURED — retextures bind by texPath
     and a naive grep lies; run the reachability check before the cut lands.
   - Disposition option: **CUT after a texPath/donor check**. Trade: lose a
     dino pool nobody cast; shed defs, patches and spawn-table noise.

4. **The urban-ruins family** — `xmb.ancienturbanruins.mo`,
   `meteores.ancienturbanruinsalldeconstructible.aurad`,
   `meteores.ancienturbanruinsvanillaloot.aurvl`, `mlie.dungeonpack`, `gmmp.dungeon`
   - Gives: ruin/dungeon structures — earth-flavored ("crashed 21st-century
     motorway", FASCINATING_WORLD_JUNK_1's own words).
   - Risks/costs: five mods of mapgen/structure content already marked as the
     donor pool FASCINATING_WORLD_JUNK_1 Phase 2 mines "before we throw away".
   - Disposition option: **CONFIRM retirement timeline** — mine (Phase 2), then
     cut the family. Trade: none once mining lands; cutting early loses the
     idea pool.

5. **mlie.moevents** — Mo'Events
   - Gives: 8 event mechanics the campaign wants — which is exactly why
     RUT_SCAVENGEREVENTS_BUILD_1 (in flight, blocked) is porting them as our
     own workers, then "retire mlie.moevents BEFORE save freeze".
   - Disposition option: **KEEP until the port lands, then CUT (already
     planned)**; interim: zero all MO_ baseChances via its own settings, as the
     item specifies. Trade: none — this card just ratifies the existing plan.

6. **vanillaexpanded.vgeneticse** — Vanilla Genetics Expanded
   - Gives: some cast biome animals (GR_ hybrids appear in BiomeCast) and the
     genetics-lab mechanic (off-theme for a scavenger clan; usage UNMEASURED).
   - Risks/costs: **91 GR_ hybrids Cherry-Picked out** (config, 2026-09-12);
     today's GIDDYUP_NULLKEY_CRASH_1 traced to its LoadFolders-gated Megafauna
     subfolder (our data bug, but the mod's conditional-def shape is a standing
     trap); a large C# mod carrying mostly-cut content.
   - Disposition option: **CENSUS then card** — count what the cast and save
     actually use from it (measured, not grepped); if it is a handful of
     animals, port them RSW_ (the MLIE/BMT absorption pattern) and cut. Trade:
     porting work vs a big fragile donor gone.

7. **mlie.yayoscombat3** — Yayo's Combat 3 beside CAI-5000 + melee animation
   - Gives: combat animation/mechanic overhaul (aim/dodge/reload ammo optional).
   - Risks/costs: broad combat Harmony surface stacked on CAI-5000 (ruled in)
     AND co.uk.epicguru.meleeanimation AND fuu.bloodanimations — four mods
     patching the same fight; classic confounder pile; one local mention only
     (no crash trail yet).
   - Disposition option: **TRIM the stack by one** — card asks which of
     yayoscombat3 / meleeanimation the owner actually sees and wants. Trade:
     visual flair vs untangling the next combat bug across four patchers.

8. **Tree retexture redundancy** — `maal.bettertreesmod` +
   `qux.comigo.bettertreesmod` + `chaoticenrico.bettertrees`
   - Three tree-visual mods at once; whichever wins is texPath-binding order
     luck. Disposition option: **keep one, cut two** (owner picks by
     screenshot). Trade: none visible if the kept one covers the biomes shown.

9. **arkymn.slowerpawntickrate** — tick-rate toucher
   - Gives: perf via slower pawn ticks; overlaps taranchuk.performanceoptimizer.
   - Risks/costs: changes sim timing under every other mod; subtle,
     unattributable behavior shifts (the worst kind of confounder).
   - Disposition option: **CARD** — keep exactly one perf-timing mod. Trade:
     some perf vs attributability of every future timing bug.

10. **zal.betterinfestations** — historic breaker class
    - No local incident on disk; reputation risk only; infestations barely
      feature on Ash'karr surface (caverns mods present though).
    - Disposition option: **KEEP, watch** — cut only on first local incident.

11. **mlie.horrors** — KEEP (nightside raiding faction is designed-in,
    HORRORS_RAIDING_FACTION_1) — listed so the audit shows it was weighed; its
    own storyteller/mapgen hooks must stay gated per that item's spec.

12. **sr.modrimworld.factionalwarcontinued** — old faction-war event mod, no
    local defect trail; **watch**, revisit at the next audit.

## The three cards I would serve first
1. **Caravan Adventures CUT** — the only candidate with three independent local
   defect trails AND a story that competes with the campaign's own arc.
2. **Profiler out of the play stack** — zero-content risk reduction, one line.
3. **Jurassic dinos CUT (after the texPath check)** — measured-zero cast usage,
   named non-SW offender, and its removal also kills a live MVB patch file.
