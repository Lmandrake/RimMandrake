<!-- status: evidence for a BENCH sitting — no rulings made here, per the item's own scope -->
# Outgrown-mod audit — 2026-08-30

`MOD_LIST_OUTGROWN_AUDIT_2`. Prepares evidence only; **rulings are the
owner's**, via a BENCH sitting. `ModsConfig.xml` was not touched.

Full 585-row data: `design/Jawa/mods/outgrown_audit_2026-08-30.csv`
(packageId, verdict, note — one row per active mod, count MEASURED to match
`ModsConfig.FULL.LATEST.xml`'s 585 `<activeMods>` exactly).

## Method

1. **The three named leads** (owner, verbatim, filed on the item) got a real
   look: About.xml, Defs folder contents, and cross-read against
   `reconciled_lore/` and `FUTURE_VECTORS.md`. Full write-ups below.
2. **The rest of the 585**, triaged in three cheap passes rather than one
   expensive one per mod:
   - Already assessed: the 23 mods in `sw_ownership_survey.md`, and 120 more
     whose packageId appears literally in an existing design doc or
     `canon.yml` — both read as "already has a documented reason," not
     re-derived here.
   - **416 mods carry no content-bearing Defs folder** (no ThingDefs,
     PawnKindDefs, RecipeDefs, IncidentDefs, FactionDefs, HediffDefs,
     TraitDefs, QuestDefs, ResearchProjectDefs, WorldObjectDefs, GeneDefs,
     BiomeDefs, TerrainDefs or SoundDefs folder) AND are not mentioned
     anywhere in our docs — almost certainly frameworks, libraries, or
     patch-only dependencies. **Not individually opened this pass** — see
     the honesty note below.
   - **25 mods are genuinely content-bearing and have never once been
     referenced in any design doc** — these got an actual look (folder
     listing + About.xml description) and a real one-line verdict. Three of
     these are the named leads; the other 22 are below.

⚠️ **Honesty note on the 416 "framework" bucket**: the classifier only
checked for XML content-def folders. A mod that does everything through pure
C# (a Harmony-patched mechanic, a UI change, a QoL behavior) with zero XML
Defs would be misclassified into this bucket and NOT individually examined.
This is a real, acknowledged gap in a "quick" pass, not a claim that all 416
are harmless — if a specific one is ever suspected of doing something live,
open it directly rather than trusting this bucket.

## The three named leads

### 1. They! (Giant Ants) — `sapiently.theyatomicmonsters`
**Verdict: keep for parts, not for its own mechanic.**

The mod is almost entirely a **FactionDef + raid mechanic** ("Giant Ants to
raid your colony and eat your food!") — one `FactionDef`, one
`PawnKindDef` set, one building def (`They_CarapaceWall`, a themed wall, not
a nest structure). That faction/raid mechanic is dead: `09_arcs_dungeons_
quests.md` already records "their faction must be ticked at world creation
or v2 ants need a new world," and this project's world is permanently frozen
(no worldgen, ever — CLAUDE.md). There is no future tick to wait for.

But `FUTURE_VECTORS.md` already plans to use **the ants as authored dungeon
content** ("the They! giant-ant nests slot in behind [the Sarlacc] as
living-location dungeons"), which only needs the race/pawnkind to be
spawnable via the bridge at a specific site — no faction registration
required. The mod's remaining value is exactly that: source material
(pawnkind, race, wall texture) for a v2 authored ant-nest dungeon, not the
mod's own mechanic.

### 2. ISEKAI RPG LEVELING — `jellycreative.isekaileveling`
**Verdict: keep — the "grant items" framing undersold it.**

`ISEKAI_GRANT_EXCLUSION_1` only touched one narrow interaction (Jawa_ traits
leaking into ISEKAI's grant-item pools). The mod itself is a **full RPG
leveling system**: `Defs/PassiveTrees`, `Defs/RuneDefs` (implied by folder
names), `Defs/QuestDefs`, `Defs/WorldObjectDefs`, `Defs/IncidentDefs`,
`Defs/StatDefs`, `Defs/TraitDefs`, `Defs/ThoughtDefs`, a RimHUD integration,
and its own C# source. None of our own systems (Droidworks, weapons
absorption, turret doctrine) touch skill-tree/leveling/rune progression at
all — this is a whole layer nothing else owns. Recommend: keep, and treat
`ISEKAI_GRANT_EXCLUSION_1` as the narrow compatibility fix it is, not a
signal to re-examine the whole mod.

### 3. Faction Territories and Vassalage — `jaeger972.factionterritories`
**Verdict: keep — real mechanism, not just a map overlay.**

The About.xml undersells it too ("Adds a mode that draws territory regions
around settlements") — its `Defs/` folder is `CaravanIncidents.xml`,
`Invasions.xml`, `Regions.xml`, `VassalOutposts.xml`. `Invasions.xml` defines
`FactionTerritories.Invasions.Invasion` and
`FactionTerritories.Expansion.SettlementConstruction` — factions dynamically
**expand their territory by building new settlements** and **invade rivals**
based on that territory, plus a vassalage/outpost layer. This is a genuine,
live mechanism tying raid/invasion frequency to settlement count, exactly
the "custom raids in proportion to settlements" the owner named — and a
strong candidate mechanism for `VAULT_DUNGEON_CONCEPT_1` point 4
(vault-access conflicts inside faction territory).

## The other 22 never-referenced content mods

| mod | verdict | why |
|---|---|---|
| `unlimitedhugs.allowtool` | keep | Essential QoL utility (mass designations) — no examination needed |
| `asp.halituisamaricanous` | **examine** | Cosmetic astronomy style/terrain pack — check it's actually visible against the desert palette, or drop as dead weight |
| `kshtantrumsounds.mod` | keep | Sound-only flavor, trivial |
| `businburg.businfeatures` | **examine** | TraitDefs under a vague name ("Betures") — open it before ruling |
| `costel.customroomnames` | keep | Trivial QoL |
| `darkestdungeon.incidentsounds` | keep | Sound-only flavor, trivial |
| `clown.dedicatedturrets` | **examine** | New turret mechanics — direct overlap risk with the ratified turret-normalization doctrine in `canon.yml`; check before keeping both |
| `dorbo.watersfx` | keep | Sound-only flavor, trivial |
| `flangopink.metalpipe` / `metalpipehorseshoe` | keep | Decorative items + sounds, trivial |
| `radzerp.naturalpaths` | keep | Terrain path decor, fits desert terrain work |
| `tug.minotaur` | **examine** | A full Biotech xenotype (genes/abilities/achievements) — thematic fit for this campaign is questionable, likely unused |
| `usgiyi.slaveoutfits` | keep | Slave apparel — directly on-theme for the enslave-not-recruit doctrine |
| `amoruch.rimworldstealingmod` | **examine** | New stealing job/thought/trait mechanic — thematically apt for scavenger Jawa, but check anti-exponential/balance concerns |
| `gerrymon.stylizedslavecollar` | keep | Slave collar/headgear — directly on-theme |
| `ucp.tabletopdecorations` | keep | Decor, trivial |
| `propickelz.tinkerbench` | keep | Tinkering Bench / Biohacking Station — strong thematic fit, Jawa are canon droid-tinkerers; a positive find, not a removal risk |
| `titans.fl` | **examine** | New giant-scale race — check power/scale level against the anti-exponential discipline |
| `error277.tunneler.expanded` | keep | Tunneling terrain/building/drug content — directly on-theme for the clan's Nomad+Tunneler ideology memes |
| `addvans.wasdedpawn` | **examine** | Single hediff, purpose unclear from the name alone — needs an actual open-and-look |
| `mrhydralisk.voeadditionaloutposts` | keep | Additional outposts for the already-adopted Vanilla Outposts Expanded framework |
| `legator.prisonerrealism` | **examine** | Prisoner mechanics overhaul — thematically apt for the slavery-heavy campaign, but check overlap with our own enslave-not-recruit doctrine before endorsing wholesale |

**7 of 25 are genuine "examine" candidates** for the BENCH sitting; the rest
resolve to "keep" on inspection (mostly trivial flavor, or — `propickelz.
tinkerbench` and `error277.tunneler.expanded` especially — turn out to be
unexpectedly strong thematic fits nobody had written down yet).

## Examine candidates — three ruled, 2026-08-31 (owner sitting)

### `clown.dedicatedturrets` — KEEP, already folded into our own doctrine

Not a conflict — it's **already claimed by the turret-normalization roster**.
`turret_register.json` lists all four of its turrets (Atomiser, Vaporiser,
Sludger, Zapper) as canon entries assigned to the Junkers faction (owner
ruling: "the makeshift look"), each with a computed `scaleTarget`/
`scaleAnchor` awaiting the same rescale pass every other turret got. The
mod is purely additive (no vanilla/other-mod turret defs touched) and
ships real C# mechanics beyond a flat damage number (Atomiser: 3-stage
ramping beam; Vaporiser: instant line-of-sight beam; Sludger: cone-spray
slow/accuracy debuff; Zapper: chain-lightning stun) — the outstanding work
is executing the register's already-decided rescale on these four, which
needs bespoke `DamageScalingExtension`/`ControlProjectileExtension` edits
(their output isn't a flat `damageAmountBase`), not a keep/cut call.

### `titans.fl` — RETIRE, design extracted first

Owner: it read genuinely scary, unlike most RimWorld creatures, but "it's
not Star Wars canon." Full mechanical extraction:
`design/Jawa/mods/titans_design_extraction.md`. Short version: the
scariness is NOT raw stat inflation (its per-hit damage is actually below
Thrumbo's, and vanilla's own `combatPower` rates it lower) — it's five
ordinary knobs stacked at once: zero-armor pure-HP tanking (a different
survivability shape than armor-deflection), near-total pain immunity
(0.95, defeats "wound it into submission"), an opening-hit hard stun on
its melee tools, active unprovoked predation up to 2x its own size, and
pack spawning (1-8) that compounds all of the above across multiple
bodies. All plain XML fields, zero C#/Harmony dependency, fully portable
to a Star Wars apex creature. Removed from `ModsConfig.xml` (takes effect
next restart — the in-flight one at ruling time had already read the old
list).

### `legator.prisonerrealism` — KEEP, one setting toggled

Already adopted as the prisoner-handling backbone
(`required_mods.md:1281`, workshop `3760196312`) — a large, mostly
complementary system (institutionalization, riots, force-feed, contraband,
lockpicking, recidivism, etc.) sitting entirely upstream of the
recruit/enslave choice; grepped its full `Source/` tree for
`GuestTracker`/`resistance`/`.will`/`SlaveOf`/`IsSlave`/`InteractionMode` —
zero hits, it never touches enslavement mechanics. **One real, narrow
conflict**: its `RecruitOffer` feature (`Source/Features/RecruitOffer/`)
periodically letters an offer to recruit an institutionalized prisoner
outright, calling `RecruitUtility.Recruit` directly on Accept — the exact
action `jawa_society.md` §4.1's enslave-not-recruit doctrine bans. Fully
containable: `enableRecruitOffer` is a per-feature mod setting (default
**true**) — turn it off, keep everything else. Doctrine op, not a
ModsConfig change.

## Summary

| bucket | count | action |
|---|---|---|
| Named leads (real look, above) | 3 | ruled above, ready for the sitting |
| Already in `sw_ownership_survey.md` | 23 | no re-examination — that survey stands |
| Already referenced in a design doc / `canon.yml` | 120 | no re-examination — has a documented reason |
| No content-bearing Defs, never referenced | 416 | not individually opened — acknowledged gap, see honesty note |
| Content-bearing, never referenced, examined | 22 | 7 flagged **examine**, 15 resolve to keep |
| Our own mod | 1 (`mandrake.inhabited`) | not an audit target |
| **Total** | **585** | matches `ModsConfig.FULL.LATEST.xml` exactly |
