# Four research access classes — mechanism scoping, one class BLOCKED

🔴 **PARTIALLY BLOCKED.** Three of the four classes (common, jawa-special,
ship-only) have a proven, pure-data vanilla mechanism — no new C#/Harmony
needed for any of them. The fourth, **faction-held**, needs the owner to name
which of the twelve campaign factions are "tech-aligned" and to which research
domains before any row can be assigned — no such mapping exists in any design
doc today, and this file does not invent one, same pattern as
`DROID_DONOR_PATCH_GATE_1` staying blocked on `DROID_SYSTEM_BUILD_1`.
No CSV rows were touched by this pass (see "what was NOT written" below) — the
manifest's `source_gate` column is untouched beyond the 3 `memory_core` rows
`RESEARCH_MANIFEST_DRAFT_1` already wrote.

## spec
Source: `infrastructure/state/canon.yml` `research_tree.tech_gating_ruled`
(owner, 2026-08-31, verbatim quoted there) — four access classes: common /
faction-held (techprints from a tech-aligned faction) / jawa-special (known
at colony start) / ship-only (Utinni memory core). Owner's own hunch: "it
could be as simple as who holds the tech prints." This item investigates the
mechanism for each class against RimSage's vendored RimWorld 1.6 decompile
and the vendored Research Reinvented source (`petetimessix.researchreinvented`
— confirmed ACTIVE in the live `ModsConfig.xml`, 586 mods), and against the
campaign's own design docs for a faction/tech alignment.

## findings

### 1. common — nothing to build
Confirmed: the manifest's `source_gate` column (schema in
`research_tree_taxonomy.md` §3) is already empty-by-default for every row not
otherwise gated — `research_manifest_draft.csv` has 521 data rows, 3 carry
`memory_core`, **518 are blank**. Blank IS common; the taxonomy doc says so
explicitly ("Source gates are flags, not tiers"). No column, no code, no
scenario part — common is what happens when nothing else applies. Nothing to
implement.

### 2. jawa-special — real vanilla mechanism, no rows chosen yet
`Source/RimWorld/ScenPart_StartingResearch.cs` (RimSage decompile) is a
stock vanilla `ScenPart` subclass: one instance per project, holding a single
`<project>ResearchProjectDefName</project>` field, calling
`Find.ResearchManager.FinishProject(project, ...)` from `PostGameStart()`.
Pure XML, no C#: add one `<li Class="ScenPart_StartingResearch"><def>...
</def><project>SomeDefName</project></li>` per jawa-special row into
`Scenario_Utinni.xml`'s `<parts>` list
(`src/SPLIT_Phase3/Jawa_Patches/Defs/ScenarioDefs/Scenario_Utinni.xml`,
read in full — currently 4 parts, no research part yet, structurally trivial
to add a 5th+).
- **Not wired**: no manifest row is currently flagged jawa-special (the
  column only distinguishes `memory_core` from blank today), and no design
  doc names WHICH projects the clan should start knowing. Unlike ship-only
  (which had the ship-design trio named in canon already), nothing names
  jawa-special candidates — picking rows is itself a content call this item
  does not make, for the same reason it does not make faction picks.
- A secondary vanilla field, `FactionDef.startingResearchTags` +
  `ResearchProjectTagDef` (e.g. `ClassicStartTechprints`), only filters which
  projects `ScenPart_StartingResearch.Randomize()` offers in the scenario
  EDITOR — irrelevant here since the def is authored, not randomized in-game.

### 3. ship-only/memory_core — the mechanism is NOT actually wired yet
The 3 rows in `research_manifest_draft.csv` (`MM_Research_AncientShipDesigns`
→ `_CWShipDesigns` → `_EmpireShipDesigns`, lines 520–522) carry
`source_gate=memory_core`, but **this is a manifest label only — nothing in
the repo currently hides or reveals them.** Checked directly: none of the
three rows' live defs (nor any patch in `src/`) set `hiddenPrerequisites`,
and no quest/incident/event exists anywhere in `src/` or `design/` that calls
`ResearchManager.FinishProject` or otherwise reveals a gated project.
`research_normalization_principles.md` §2 item 4 names the INTENDED
mechanism — `hiddenPrerequisites` (real vanilla `ResearchProjectDef` field,
pure XML) plus "event-driven reveal" — but that second half has no proven
data-only implementation:
- Searched RimWorld source for a vanilla QuestNode that finishes/reveals a
  specific research project by defName: none exists. The closest vanilla
  primitive is `CompUseEffect_FinishRandomResearchProject` (a ThingComp an
  item can carry, usable to finish a RANDOM eligible project) — not a
  targeted reveal of one named row, and not currently used anywhere in this
  campaign's mods.
- **Verdict: the reveal/trigger half genuinely may need a small
  QuestNode or Harmony patch** (call `Find.ResearchManager.FinishProject` on
  a named hidden gate-project when a specific in-fiction event fires) — this
  is the one piece of the whole item where "no new C#" is NOT confirmed.
  Flagged as a follow-on build item, not built here per the brief's "do not
  write C# without being certain it's required."

### 4. faction-held — the hard one, genuinely BLOCKED
`ROComp_RequiresFaction` / `OF_Factions` (Research Reinvented, vendored
source at `vendor/mod_sources/ResearchReinvented-main/…/OpportunityComps/`,
`…/Managers/OpportunityFactories/OF_Factions.cs`) turned out to be the WRONG
mechanism: RR generates a "learn from any faction roughly your tech level"
opportunity automatically for EVERY project × EVERY live faction, weighted by
a techLevel-difference table — it is not configurable per-project-per-faction
and does not express "faction X holds project Y" at all.

**The right mechanism is vanilla, not RR, and it is exactly what the owner
guessed**: `ResearchProjectDef.heldByFactionCategoryTags` (`Source/Verse/
ResearchProjectDef.cs:51`) — a list of `FactionDef.categoryTag` strings.
`TechprintUtility.GetResearchProjectsNeedingTechprintsNow()` filters
techprint generation to only the factions whose `categoryTag` is in a
project's list, and vanilla's own `StockGenerator_Techprints` (a real,
already-shipping `StockGenerator` subclass usable in any `TraderKindDef`'s
`stockGenerators`) draws from that filtered pool by weighted commonality.
Royalty already uses this precedent live: `ResearchProjects_Implants.xml`
gates several projects with `<heldByFactionCategoryTags><li>Empire</li>
</heldByFactionCategoryTags>`, and `MainTabWindow_Research` displays "held by
faction" to the player from this same field. **This confirms the owner's
"could be as simple as who holds the techprints" — it is, and it is 100%
pure Def-field data, zero C#.**

What's still missing before any row can use it:
1. **None of the 12 campaign `FactionDef`s currently set `categoryTag`**
   (checked `src/RimStarWars` — zero hits). Adding one is trivial XML per
   faction, but which factions get which tag(s) is exactly the "tech-aligned
   strongly" call the owner referenced.
2. **No design doc maps a faction to a tech DOMAIN in the sense this gate
   needs.** Searched `design/Jawa/worldbuilding/FACTION_SPEC.md` (948 lines),
   `faction_roster_v2.md` (2847 lines), `faction_equipment_clusters.md`,
   `faction_equipment_guidance.md`: no hits for "techprint" tied to a
   faction, no "faction X holds research Y" table. The closest analog is
   `faction_equipment_clusters.md`'s Part 2 faction × weapon-cluster matrix
   (a retired seat's 2026-08-14 proposal, itself flagged unsettled in its own
   doc — "R6" notes contest even its own one-cluster-per-faction premise):
   e.g. Free Droid Enclaves = ionic+charge, Jawa Trade Moot = ion (their only
   weapon), Deep Desert Tribes = kinetic with energy weapons as SACRILEGE,
   Ascendant Helix = charge+EMP (their "wealthy research enclaves" line in
   `FACTION_SPEC.md:443` is suggestive). This is equipment-loadout design,
   not a ruled research-tech alignment, and it does not cover all Armory
   schools/tabs (nothing maps to Sonic, Gravitic-personal, or most of Trade &
   Craft/The Reach). **Using it as a stand-in mapping would be inventing the
   assignment the brief said not to invent.**
3. Even with tags assigned, each faction needs `StockGenerator_Techprints`
   added to at least one of its `TraderKindDef`s (pure XML,
   `maxTechLevelBuy` + `countChances`) for the techprint to actually appear
   for sale — none of the campaign factions currently carry this generator
   either (not checked exhaustively here, flagged for the build pass).

**This class stays BLOCKED on the owner naming which factions are
tech-aligned and to what.** No per-row faction assignment was guessed across
the ~521 rows.

## what was NOT written
No CSV rows touched — `source_gate` in `infrastructure/output/
research_manifest_draft.csv` is exactly as `RESEARCH_MANIFEST_DRAFT_1` left
it (518 blank + 3 `memory_core`). No `fate`/`tab`/`tier`/`cost` columns
touched. No C#/Harmony written. No `FactionDef` XML edited (`categoryTag` is
a real, confirmed-needed change but assigning it per faction is the blocked
design call). `ModsConfig.xml` untouched, nothing deployed, no `rimflow`
commands run, nothing committed/pushed — left for the owner to review.

## verify (once unblocked)
1. Common: nothing to verify — it's the CSV's existing default.
2. Jawa-special: once the owner names candidate rows, add
   `ScenPart_StartingResearch` entries to `Scenario_Utinni.xml`, cold-load a
   quicktest colony, confirm the projects show `IsFinished` at tick 0 via the
   research tab.
3. Ship-only: build the thin reveal trigger (QuestNode or Harmony patch,
   scoped by a follow-on item) before claiming this class works; add
   `hiddenPrerequisites` to the 3 memory_core rows (and any future ones)
   pointing at a dedicated hidden gate project per chain link.
4. Faction-held: once the owner rules the tech-alignment map, add
   `categoryTag` per aligned `FactionDef`, `heldByFactionCategoryTags` per
   assigned research row, `StockGenerator_Techprints` on that faction's
   trader(s); validate with `research_manifest_validate.py` (extend it with
   an 8th check reading `source_gate` values against a live
   `heldByFactionCategoryTags`/`categoryTag` cross-reference) and a quicktest
   trade with that faction to confirm the techprint actually appears in
   stock.

## criteria
- [x] Common confirmed as the existing default — no implementation needed.
- [x] Jawa-special mechanism identified and confirmed pure-XML
      (`ScenPart_StartingResearch`), no rows assigned (none named in any doc).
- [x] Ship-only/memory_core mechanism investigated: `hiddenPrerequisites`
      half confirmed pure-data; reveal/trigger half confirmed NOT yet
      implemented anywhere and NOT confirmed achievable without a thin
      QuestNode/Harmony patch — flagged, not built.
- [x] Faction-held mechanism identified and confirmed pure-XML
      (`heldByFactionCategoryTags` + `StockGenerator_Techprints`), proven via
      a live Royalty precedent (`ResearchProjects_Implants.xml`); Research
      Reinvented's own faction system investigated and ruled OUT as the
      mechanism (it's an automatic per-faction "learn from anyone" system,
      not a per-project holder assignment).
- [x] Faction-tech alignment doc search: none found; the closest artifact
      (`faction_equipment_clusters.md`'s weapon-cluster matrix) is named,
      quoted, and explicitly NOT used as a substitute mapping.
- [ ] BLOCKED — owner rules which factions are tech-aligned and to which
      research domains/tabs, by name, before any faction-held row is
      assigned in the manifest.
- [ ] Follow-on build item needed for the ship-only reveal trigger
      (QuestNode or Harmony patch) before that class can be called "working"
      rather than "labeled."
