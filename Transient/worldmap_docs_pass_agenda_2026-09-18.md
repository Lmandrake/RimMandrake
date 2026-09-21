# Worldmap Docs Pass — Walk Agenda (prep 2026-09-18)

Read-only prep for the owner's file-by-file ruling sitting on the canonical
worldbuilding docs. Ground truth used throughout: no worldgen feature ever
(fixed savegame only); authored so far = roads, mines, seas, settlements;
three Wildsteam Clan settlements (incl. Sporefall, "in the Fever Wood on the
road") have no roads; F6 Rust Cathedral lozenge improved but 42 single-tile
AridShrubland islands remain; one 118-tile LargeRiver system reaches no sea
(violates trunk-river rule); naming migration DONE (mandrake.<tier>.*,
NAMING_SCHEME_EXECUTION_1 closed 2026-08-31); FlowWorks = fluidcanals renamed;
proposals suite fully ruled 2026-09-02; liquids framework ruled 2026-09-13
(LiquidDef registry canon); pit = SUPERDEEP cell not a building (2026-09-17);
local features not repaints (Ash'karr stays desert).

STATUS: complete. All 7 input files read; 41 stale/contradicted-directive rows
identified across them (max 10 per doc, per the brief); walk order and unknowns below.

---

## 1. ASHKARR_WORLD_DEFINITION.md

**1. STATUS:** "The single source of truth for the planet" — the big canonical spec
(1,613 lines). Header `status: live`. Extremely actively self-correcting: dozens of
inline "SUPERSEDED"/"CORRECTED"/"RE-MEASURED" blocks spanning 2026-08-18 through
2026-08-26, each dated. This doc mostly polices its own staleness already — the rows
below are places it either still disagrees with itself, disagrees with a sibling doc,
or doesn't yet reflect ground truth handed to this sitting.

**2. LIVE DIRECTIVES that look stale or contradicted:**

| line | quote | why suspect |
|---|---|---|
| 556-567 | §7 header: "this section said 72. The map has **120**"..."the LIVE roster is canon and smaller than this table — **95** NPC settlements measured on V27" | 🔴 **the doc itself carries THREE settlement counts (72 → 120 → 95), and none of the sibling docs read here cite 95** — `WORLD_REDRAFT.md` still says 72 (the *most* stale of the three), `FACTION_SPEC.md`'s per-faction weights sum to ~96 (close to 95, i.e. roughly consistent with the LATEST number, not the 72 everyone else assumes) |
| 584 | Wildsteam Clan — "***Sporefall* in the Fever Wood on the road** (owner, 2026-08-24)" | ground truth: three Wildsteam Clan settlements including Sporefall currently have **no roads** — this doc's own settlement table asserts the opposite for Sporefall specifically; may have been pruned by a later road-thinning pass (§7e "Grey Sea thinning," or the Tusken road-pruning at line 579) and never restored |
| 245-252 | §4 rule 6: "**RIVERS DO NOT CONNECT THE BASINS**... they should peter out into salt flats" — Twilight Sea, Grey Sea and the Scald are hydrologically **separate**; termini are the design | ground truth reports a 118-tile LargeRiver system reaching no sea as a **violation of a "trunk-river rule"** — this doc's stated doctrine treats a river dying short of the sea as correct and intended; no distinction here between ordinary rivers (may die in salt flats) and a LargeRiver-class trunk (may be required to reach the sea) |
| 1391 | "Water came out at **6.46%** (1,412 tiles), not the **8.14%** this file and `the_one_map.md` both carried... the DOCS were stale." | this doc already flags itself as stale on its own headline water number (§3, cited repeatedly as 8.14% from `canon.yml`) — unclear whether `canon.yml > planet.water_pct` was ever corrected to 6.46% after this measurement, since every earlier section still asserts 8.14% |
| 765-766, 825-827 | "**The player start is unsited.** ⛔ REOPENED 2026-08-24" | still open at this doc's latest edit (§10 open questions, §11 handoff) — no later doc in this input set confirms a landing tile was ever chosen |
| 1415-1435 | "The magenta tiles are missing MOD art... five sarlacc landmarks" — `sw_DeadSarlacc`/`sw_Sarlacc` textures do not exist in the shipping mod | unresolved art defect as of this doc: "drop the 5 landmarks, or draw the two textures" — no resolution recorded |
| 617-651 | §7d Rust Cathedral — "All **236 tiles** are `Flat`" (levelled 2026-08-24), no islands mentioned | ground truth's "F6 Rust Cathedral lozenge improved but 42 single-tile AridShrubland islands remain" is not addressed anywhere in this section — looks like a later-introduced or separately-tracked defect this doc doesn't yet know about |
| 1411-1413 | "This is **NOT persisted in the bundle**... a re-import re-breaks it" (feature label rescale) | operational trap for anyone re-running the importer described in §12 — worth restating at the sitting since a redraft (per `WORLD_REDRAFT.md`) would silently reintroduce it |

**3. OWNER QUESTIONS:**
1. 🔴 Which settlement count is now authoritative — 72, 120, or 95? This doc's own "live roster is canon" note (2026-09-08) points to 95, but no other doc in this set has been updated to match, and `WORLD_REDRAFT.md`'s "done" bar still checks for 72.
2. Does Sporefall (and the other two roadless Wildsteam settlements) still belong "on the road" per this doc's line 584, or was the road correctly removed by a later pass and this doc's text just never updated?
3. Is there a "trunk river must reach a sea" rule distinct from this doc's general "rivers die in salt flats" doctrine — because as written, a dead-ending 118-tile LargeRiver reads as this doc working as designed, not as a defect.

---

## 2. REGIONS_THAT_LIE.md

**1. STATUS:** Audit (not a spec/gate) — swept all 71 named regions for name/tile
mismatch; dated **2026-08-23**, header `status: live`. 13 regions flagged, 4 more
already fixed same night and delisted.

**2. LIVE DIRECTIVES that look stale or contradicted:**

| line | quote | why suspect |
|---|---|---|
| 4-6 | "Swept all 71 named regions... 13 fail." | dated 2026-08-23, **before** current authoring wave (roads/mines/seas/settlements per ground truth) — tile composition and even region boundaries may have moved since; no re-audit citation anywhere else in the input set |
| 15 | "**Deadstone** ... 0% hilliness>=4 and 10% rocky biome" | INCOHERENT/name-mismatch findings are computed against a snapshot; unclear if still true post-authoring |
| 16,17,18,20,23,24 | "INCOHERENT: N different biomes" (Dune Sea, Nightspill, Twilight Sea, Gray Crags, Dew Belt, Anvil) | 6 of 13 findings are the same class (biome incoherence); doc never says whether incoherence is itself a defect requiring a fix or an accepted feature of a hand-authored desert world with local variety |
| 36 | "Judgement, not a defect list. `Cinderdark` at −29°C may be deliberate... Read each one before changing it." | doc explicitly disclaims its own list as action items — so every row above is a candidate for discussion, not a queued fix, and the owner has apparently never ruled on any of the 13 |

**3. OWNER QUESTIONS:**
1. This audit is unranked and unruled — of the 13 flagged regions, which are genuine defects to fix now vs. accepted lore (e.g. Cinderdark's cold ash, Deadstone's HorrorWastes)? The doc asks this question of itself and never answers it.
2. Given roads/mines/seas/settlements authoring has continued since 2026-08-23, should this audit be re-run before being acted on, since the current table cannot be trusted as current tile truth?
3. Do the 6 "INCOHERENT" (8+ biome) regions need boundary redraws, or is biome variety within one named region acceptable for this world?

---

## 3. WORLD_REDRAFT.md

**1. STATUS:** Redraft procedure (a DECIDE record, not a generator) — "Rebuilding the
keeper world, by hand". Dated 2026-08-21, corrections through 2026-08-23. Explicitly
"THIS IS A REDRAFT PROCEDURE, NOT A GENERATOR" and "documentation for later," deliberately
not scheduled to run next as of its own writing.

**2. LIVE DIRECTIVES that look stale or contradicted:**

| line | quote | why suspect |
|---|---|---|
| 43 | "The artifact this produces: `world/WORLDMAP_gen.rws`, ~5.1 MB, world-only." | Transient/ now holds `CANONICAL_ASHKARR_2026-09-09.rws.bak-...` and MEMORY names `CANONICAL_ASHKARR_START_2026-09-12.rws` as the current phase's start save — different filename convention; unclear if `WORLDMAP_gen.rws` is still the produced artifact name or superseded |
| 53 | "mod list \| **578**, the owner's full stack" | current facts / MEMORY put the mod count at 593 (phase doc) and CLAUDE.md notes a 599-mod load and a 631-active-count trap; the 578 figure is explicitly timestamped "2026-08-21" in-doc but the procedure has no update noting which count applies if run again |
| 165 | "settlements — ⛔ **all 72 or none**" | ground truth: three Wildsteam Clan settlements (incl. Sporefall) currently have no roads — an apparent authoring gap post-dating this doc; unclear whether 72 is still the target count or whether settlement count/definition has moved since 2026-08-21 |
| 211 | "stage 5 reported **72 of 72** settlements, not 68" | same — this "done" criterion is a hardcoded count from the original run; no later doc in this set re-confirms 72 is current |
| 25-32 | "This procedure does NOT run next... documentation for later again" | if the 2026-09-12 canonical start save (per MEMORY) resulted from actually running this procedure, the doc's framing ("does not run next") is now historical, not a standing instruction |
| 106-109 | in-doc self-correction on Tribal Furniture mod-list ruling | resolved within the doc itself, not a live contradiction — noted only for completeness |

**3. OWNER QUESTIONS:**
1. Did this exact procedure produce the 2026-09-12 canonical start save? If so, should the doc's "documentation for later, does not run next" framing be replaced with a record of the actual run (mod list used, settlement count achieved, any deviations)?
2. The three Wildsteam Clan settlements without roads (incl. Sporefall, canon "on the road") — is this a paint-CSV gap (stage 2 rivers/roads vs. stage 5 settlements ordering) that a future redraft would fix, or a live authoring TODO independent of any redraft?
3. Is 72 still the authoritative settlement count, or has continued map authoring since 2026-08-21 changed how many settlements Ash'karr carries?

---

## 4. PRE_WORLDGEN_GATE.md

**1. STATUS:** Gate/DECIDE record — closes `D-CRIT`, header `status: live`, body dated
2026-08-21 through 2026-08-23 (multiple in-place corrections). Concerns the **one-time
world-creation click** (factions + ideoligions baked at that moment), not the ongoing
map-authoring pass — its "worldgen" is the single manual click event, consistent with
"no worldgen feature" ground truth, not a contradiction of it.

**2. LIVE DIRECTIVES that look stale or contradicted:**

| line | quote | why suspect |
|---|---|---|
| 1-27 | whole doc frames itself as "**Before** the owner generates the world — what is actually owed" | 🔴 **MEMORY records a `CANONICAL_ASHKARR_START_2026-09-12.rws` start save already exists** ("ship at 17007; 593 mods") — dated ~3 weeks after this doc's latest correction. If the world-creation click already happened 2026-09-12, this entire gate is retrospective history, not a live pre-condition, and its "owed" framing is false-as-written |
| 68 | "override all twelve on the IDEO, in the same session as world creation, before the save" — filed as `LEADER_TITLES_ON_THE_IDEO_1` | if the click already happened 2026-09-12, this item either got done in that session or the save already shipped without it — no doc in this set confirms which |
| 87-94 | describes `WORLDGEN_FACTION_CHECKLIST.md` as "one screen the owner ticks during the run" (future tense) | same click-already-happened question — is this checklist still a future action or a historical record of the 2026-09-12 run? |
| 153 | "Nobody tells the owner the world is ready to make until §2 is empty and deployed." | gatekeeping language for an event that (per MEMORY) may be three weeks in the past |

**3. OWNER QUESTIONS:**
1. 🔴 **Top question for the whole sitting:** did the 2026-09-12 canonical start save represent the actual worldgen click this file gates? If yes, this entire document is dead-in-place history (per the "inaccurate material is deleted" rule) and should be archived/deleted rather than walked as a live gate.
2. If the click already happened, did `LEADER_TITLES_ON_THE_IDEO_1` (the one item this doc says "genuinely still owed") actually get applied before that save, or did it ship with the `Awoken Cheese`/`Ethical Thug` override-defect intact?
3. If the click has NOT happened yet and 2026-09-12 was something else (a test/interim save), what is the current state of the single item in §2 — still open?

---

## 5. FACTION_SPEC.md

**1. STATUS:** Buildable faction-layer spec — "DECIDE owns this file. It is what BUILD
executes." Header `status: live`. Heavily revised in place; rulings dated across
2026-08-14 through 2026-08-29 (most recent: the Wildsteam Clan name clarification).
Primarily about FactionDefs/pawn groups/ideo, but specs per-faction settlement counts
and siting, which bears directly on the map.

**2. LIVE DIRECTIVES that look stale or contradicted:**

| line | quote | why suspect |
|---|---|---|
| 106-108, 128-372 (per-faction weight rows) | "`settlementGenerationWeight` is scaled so **7 settlements = 1.0**" + per-faction counts (19+13+9+12+4+5+5+7+4+7+8+3 = **~96**) | 🔴 sums to roughly **96 settlements**, but `WORLD_REDRAFT.md`'s "done" criterion says stage 5 must report **"72 of 72"** — a direct numeric contradiction between two docs in this same input set |
| 199-201 | Free Droid Enclaves — "12; sited AWAY FROM ORGANICS... Cathedral ground, volcanic terrain, and quiet dark-side seats (2026-08-24)" | dated AFTER the 2026-08-17 ruling below (line 932) that the Free Droid Enclaves also need "a presence on the plateau" beside the Rust Cathedral — this later siting note doesn't say whether that plateau presence is already folded into the "12" |
| 264 | Geonosian Foundry Hive — "settlementGenerationWeight 0.7 -- 5, mountains/caves/ancient factories" | 2026-08-17 ruling (line 888-919) established **TWO** settlement clusters for this faction (Ore Seams + the Plateau beside the Rust Cathedral) — unclear if "5" already covers both or predates the split |
| 328-330 | "the 2026-08-21 world showed **four** Blackstar Companies with three divergent 'the Contract' ideos, and that contradiction is unexplained. Carried by `BLACKSTAR_NAME_MUST_NOT_LEAK_1`" | open/unexplained defect as of this doc, no resolution recorded here |
| 426-431 | "leaderTitle ON THE DEF IS NOT WHAT THE PLAYER READS... `ideoOverrodeDefCount: 36` of 37" | cross-references `PRE_WORLDGEN_GATE.md`'s still-open `LEADER_TITLES_ON_THE_IDEO_1` — if the 2026-09-12 canonical save already happened (per MEMORY), did this get fixed before it, or did the save ship with `Awoken Cheese`/`Ethical Thug`? |
| 521-524 | "ZERO Star Wars faction namers... measured against the **585**-mod set; the list is now **575**... re-run it against the fresh dump before relying on the zero" | mod counts (585/575) are stale relative to current ~593-631 range noted in ground truth; doc flags its own number as needing a re-check that evidently never happened in this set |
| 205-206 | Free Droid ideoName — "the religions spec flags this may not run if the droid race is not Humanlike. Settle that before authoring the ideo block." | explicit open conditional, no resolution recorded |
| 933-935 | "Unresolved: whether the volcanic enclaves and the plateau enclaves are one faction or a split." | explicit open item flagged by the doc itself |

**3. OWNER QUESTIONS:**
1. 🔴 Per-faction settlement targets here sum to roughly 96; `WORLD_REDRAFT.md` says exactly 72. Which number is authoritative, and does the currently-authored map (roads/mines/seas/settlements) match either?
2. Are the Free Droid Enclaves' volcanic-mountain settlements and the Geonosian Foundry Hive's new plateau outpost (beside the Rust Cathedral) meant to be one faction each with two site clusters, or should the plateau communities become distinct factions? (flagged unresolved 2026-08-17, never closed in this set)
3. Given a canonical start save may already exist (2026-09-12), did `LEADER_TITLES_ON_THE_IDEO_1` actually get applied before that save, and were the four divergent Blackstar Company instances (`BLACKSTAR_NAME_MUST_NOT_LEAK_1`) ever explained/fixed?

---

## 6. SCENARIO_SPEC.md

**1. STATUS:** Campaign-start spec — "how the campaign starts", chain step 12, DECIDE
owns it. Header `status: live`. Rulings dated 2026-08-14 through 2026-08-22; several
items marked ✅ CLOSED in place. Mostly pawns/ship/starting-stock, but the landing
tile's biome and fuel-source geography tie it to the map.

**2. LIVE DIRECTIVES that look stale or contradicted:**

| line | quote | why suspect |
|---|---|---|
| 135 | "**map** \| the tile the owner picks... Desert / ExtremeDesert / AridShrubland" | ground truth: 42 single-tile AridShrubland islands remain near F6 Rust Cathedral (named in this same doc, line 369, as the landing region's mega-structure) — since the starting tile is a permanent, irreversible choice ("fixed map"), whether it risks landing on one of the malformed single-tile islands is worth confirming before the sitting |
| 55-58 | "the campaign-start save is the one artifact v1 actually ships, so it is committed... Commit the finished start, not every iteration." | `WORLD_REDRAFT.md` line 201 notes `*.rws` is gitignored and needs `git add -f`; no committed campaign-start `.rws` is visible in the current git status snapshot (only an untracked `Transient/...bak` for a differently-named `CANONICAL_ASHKARR_2026-09-09.rws`) — unclear whether the actual ruled-committed save exists under this or another name |
| 17-22, 32-44 | "the owner starts his campaign from it"; "Every FactionDef and ideo block must be deployed BEFORE the owner makes the world" | 🔴 same open question as `PRE_WORLDGEN_GATE.md`/`WORLD_REDRAFT.md`: if the 2026-09-12 canonical start save already exists, has this whole "who does what" sequence already executed, making this doc historical rather than a live pre-condition? |
| 332-357 | "The planet currently offers three [fuel paths], ruled separately and now confirmed as a set... helixien gas pockets · propane lakes · tar pits" | ruled 2026-08-15, **before** the liquids framework ruling of 2026-09-13 (LiquidDef registry canon) — unclear whether these three fuel sources now need representing as LiquidDefs or are otherwise unaffected |
| 21 | queue item cited as `the-scenariodef-part-list-and-what-a-jawa-may-never-do-8d4c07` | this lowercase-dash-plus-hex ID format predates and violates the 2026-08-20 naming rule (`THREE_UPPER_SNAKE_WORDS_#`) — likely a dead/renamed reference; worth confirming the item still exists under a current name |

**3. OWNER QUESTIONS:**
1. Has "Flight of the Utinni" already been started (cf. the 2026-09-12 canonical start save in MEMORY)? If so, did the ship, the six founders and starting stock ship exactly as specced here, and should this doc be rewritten as a historical record rather than a forward gate?
2. Is the chosen/intended landing tile clear of the 42 single-tile AridShrubland islands near F6 Rust Cathedral — has anyone actually checked this irreversible choice against that known map defect?
3. Do the three ruled fuel paths (helixien gas, propane lakes, tar pits) need reconciling with the 2026-09-13 liquids framework ruling (LiquidDef registry canon), or do they stand as-is?

---

## 7. biomes/README_BIOME_GRAMMAR.md

**1. STATUS:** Grammar/spec doc for biome definition sheets — "Owner + BENCH,
2026-09-05". Progress table updated through 2026-09-07, ending in a banner:
"THE CAMPAIGN IS COMPLETE — every biome on Ash'karr has a ratified sheet."

**2. LIVE DIRECTIVES that look stale or contradicted:**

| line | quote | why suspect |
|---|---|---|
| 166-167 | "**Arid shrubland** = where the shade economy *ends*... That is the proposed hinge, put to the owner 2026-09-05 and **not yet ruled**." | doc's own text flags this as an open, unruled proposal — a direct candidate for the sitting |
| 139 | `the_rust_cathedral.md` \| `AB_MechanoidIntrusion` ("the Rust Cathedral"; 236 tiles MEASURED, one region, 211 flat...) | ground truth: "F6 Rust Cathedral lozenge improved but 42 single-tile AridShrubland islands remain" — this sheet's tile/region description does not mention or account for that island defect; unclear if same region and whether the sheet needs a revision note |
| 12-13 | "Concentric biome rings about the substellar point are **FORBIDDEN**. A bullseye planet is explicitly ruled out." | 42 single-tile AridShrubland islands (scattered single-tile fragments) could read as a ring-adjacent artifact near F6; worth checking against this hard ban |
| 118 | "`terminator_sea.md` \| Twilight Sea + Grey Sea... this row previously said 'the three seas' — the Scald is the third and has NO biome sheet" | doc already self-flags one gap (Scald has no dedicated sheet, only comparison-foil mentions) — still true as of this doc's freeze; unclear if closed since |
| 148 | "**THE CAMPAIGN IS COMPLETE**... Every biome... has a ratified sheet (2026-09-05 → 2026-09-07)." | liquids framework was ruled 2026-09-13 (LiquidDef registry canon), **after** this banner — unclear whether that ruling touched any of the sea/sea-bottom biome sheets listed here (the_scald, the_grey_deep, the_twilight_deep) |
| 186 | "actual animals wait for the full plant-and-animal assignment pass" | status of that pass is outside this input set — flagged as an open dependency, not verified here |

**3. OWNER QUESTIONS:**
1. Is "Arid shrubland = where the shade economy ends" (sun 9.2°, 16% insolation) ruled as the dryland-ladder hinge, or still open as this doc states?
2. Do the 42 single-tile AridShrubland islands near F6 Rust Cathedral violate this doc's hard "no bullseye/no concentric rings" ban, and if so, is the fix a sheet-level rule or a paint-level cleanup?
3. Does the Scald still lack its own biome sheet (using `terminator_sea.md` only as a foil), and if so, is a dedicated sheet still owed, or was it deliberately merged elsewhere (`the_scald.md` under `RUT_TheScald` appears later in the same table, line 145 — possible internal contradiction to reconcile with line 118's "no biome sheet" claim)?

---

## WALK ORDER

1. **`ASHKARR_WORLD_DEFINITION.md`** — the declared single source of truth; walk it
   first because it carries the settlement-count ambiguity (72→120→95) and the
   still-open player-start-site question that every other doc downstream inherits.
2. **`FACTION_SPEC.md`** — its per-faction settlement weights and two open siting
   questions (Free Droid/Geonosian plateau split, Blackstar containment) can only be
   ruled once #1's settlement-count question is settled.
3. **`WORLD_REDRAFT.md`** — a procedure whose "done" bar (72 settlements, 578 mods)
   is now doubly stale against #1 and needs updating regardless of whether it has
   already run once (2026-09-12).
4. **`PRE_WORLDGEN_GATE.md`** — shares the same "has the one-time click already
   happened" question as #3; best rendered right after so the owner rules it once
   for both docs together.
5. **`SCENARIO_SPEC.md`** — depends on #4's answer (has the campaign started) and
   on #1's still-unsited landing tile / the AridShrubland-island risk near it.
6. **`biomes/README_BIOME_GRAMMAR.md`** — mostly self-contained biome design
   grammar; one still-open ruling (the arid-shrubland hinge) and one internal
   date inconsistency (the Scald's biome-sheet status), lower stakes than the
   settlement/click questions above.
7. **`REGIONS_THAT_LIE.md`** — smallest and explicitly self-described as
   "judgement, not a defect list"; walk last since it predates the current
   authoring wave and every row needs re-verification before it can be actioned.

---

## UNKNOWN

- Whether the 2026-09-12 `CANONICAL_ASHKARR_START_2026-09-12.rws` (per MEMORY)
  is in fact the product of the one-time worldgen click that `PRE_WORLDGEN_GATE.md`,
  `WORLD_REDRAFT.md` and `SCENARIO_SPEC.md` all gate — could not confirm from the
  six files read; this is the single biggest open fact for the sitting.
- The **current** live settlement count on the actual map today — `ASHKARR_WORLD_DEFINITION.md`
  records 95 as of a 2026-09-08 measurement, but ground truth says authoring
  (roads/mines/seas/settlements) has continued since, so even 95 may be stale.
- Whether `infrastructure/state/canon.yml > planet.water_pct` was ever updated from
  8.14% to the measured-live 6.46% — `canon.yml` is under `infrastructure/`, out of
  scope for this read-only pass.
- Whether the 42 single-tile AridShrubland islands and the 118-tile dangling
  LargeRiver (both given as ground truth for this sitting) are recorded in any
  `infrastructure/state/items/` file, and under what item name — could not check,
  out of scope.
- The identity of the other two roadless Wildsteam Clan settlements beyond
  Sporefall — `ASHKARR_WORLD_DEFINITION.md` names three settlements added
  2026-08-26 (Bitterleaf, Oilpalm, Warthorn) with no road mentioned for any of
  them, but this is circumstantial, not confirmed.
- Whether the five magenta sarlacc-landmark tiles were ever resolved (dropped or
  given real textures) — no later reference found in this input set.
- Any resolution recorded in the ~108 other worldbuilding files explicitly out of
  scope for this pass (`the_one_map.md`, `faction_roster_v2.md`, the individual
  biome sheets, `SCENARIO_SETTINGS_SPEC.md`, etc.) — several of the rows above cite
  those files as the place an answer might already exist.
- The current live active mod count — ground truth gives a range (593/599/631
  across different recent measurements); did not independently re-measure.
