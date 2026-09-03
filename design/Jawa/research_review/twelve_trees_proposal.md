<!-- status: PROPOSAL — RESEARCH_TREE_NORMALIZATION_1 vision pass v2, Fable design agent
     2026-09-03, on the owner's directive of the same day ("around 12 trees, rebalance,
     aggressive thematic filtering, weapons by physics, ritual-tech, Royalty question").
     Nothing here is ruled. Companion artifacts: restructured_model_v2.json (all 522 rows
     accounted), build_tree_visual_v2.py → research_trees_visual_v2.html (the review visual).
     Supersedes nothing; v1 (six trees, restructured_model.json) remains the last ruled-on state. -->

# Thirteen trees — research restructure, vision pass v2

> 🔴 **A CUT REMOVES A `ResearchProjectDef` AND NOTHING ELSE** — owner,
> 2026-09-03: *"I did not cut the anomaly content. I only cut the players
> ability to research that tech tree."* Every ThingDef, PawnKindDef, building,
> creature and piece of map content stays in the game for the campaign's own
> repurposing. Where this document reads as though cut content is gone, it is
> wrong and this line governs. `research_tree_taxonomy.md` migration rule 5.


**What changed from v1:** six trees → thirteen; 30 new cuts (each with a
recover line); tier now DERIVES from the ruled cost band (`tier = band(cost)`),
which makes band conformance real and turns every felt-tier disagreement into an
explicit re-cost proposal (28 of them); weapons regrouped by the physics of how
they kill; droids split into two branches along the Ohm/Oomo fault; THE SHIP
re-armed as the exotic payoff tree; one NEW tree (The Rites) proposed from
whole cloth. All 522 rows accounted: 84 v1-cut + 6 merge + 30 new-cut + 402
placed.

## 1. The roster

Read left to right as the ambition gradient. Counts are survivors placed today.

| # | tree | theme — in the clan's own taxonomy | rows |
|---|---|---|---|
| 1 | **Scavenger** | the pride-free floor: fire, water, food, hide, door, trap | 44 |
| 2 | **The Hearth** | comfort and culture: cooking, brew, furniture, art, music, games, cloth | 49 |
| 3 | **The Refinery** | what sand and wreck become: fuels, chems, drugs, ores, synthetics | 52 |
| 4 | **The Workshop** | making and mending: smithing, machining, electronics, fabrication, vehicles, power | 54 |
| 5 | **Powder & Slug** | things that kill by MASS: guns, cannon, mortars, blades, blast doors, the Watch | 36 |
| 6 | **Blasterworks** | things that kill by HEAT: the blaster spine, plasma, beam, disruptor, tibanna | 16 |
| 7 | **The Strange Schools** | things that kill by STRANGER physics: ion/EMP, sonic, vibro, gravitic relics, cloak, saber | 11 |
| 8 | **The Shell** | not dying: armors, shields, warcaskets, worn gear, the maker doctrines | 39 |
| 9 | **Droidsmith** | Ohm's hands: labor/utility/protocol droids, parts, mechtech, drones | 29 |
| 10 | **The Waking Mind** | the flashpoint: war droids, the AI ladder, positronic minds | 27 |
| 11 | **THE SHIP** | the Utinni herself: gravtech, her systems, her guns, her memory | 29 |
| 12 | **The Reach** | the trap: flesh, genes, bionics, archotech — priced brutally | 16 |
| 13 | **The Rites** | NEW — the liturgy: researching how to speak to the gods (§5) | 0 + 5 proposed |

Weapon physics honors `setting_physics.md`'s forms of harm and the turret
register's families: **mass / heat / strange**, with armor split out because the
clan files "not dying" under its own god (Rekko keeps you whole; Ozzik gets you
shot). The three weapon trees plus The Shell replace the single 106-row Armory.

The droid split is the theology made legible: **Droidsmith** is the branch Ohm
loves and Oomo tolerates (metal that serves); **The Waking Mind** is the branch
they war over (metal that thinks, metal that kills). RimAI's three AI levels
spread T2→T3→T4 by re-cost so the ladder climbs instead of stacking; the
Positronic Brain (10,000) and the ultra-mech capstones live at its top.

**THE SHIP re-armed.** Everything that was ruled to couple in is now actually
in: the gravtech spine, all seven VGE systems, the GravTech exotics (grav
forge, tuning, black hole, big cannons), ShipReactor, the MiningCo drill-laser
pair (the ancient "solid beam" tech, ruled), VFE_Manufacturing, the Core
starflight cluster (Johnson-Tanaka drive, sensors, vacuum cryptosleep, machine
persuasion — the ship's own mind), shuttles, orbital tech, and the Memory Core
ship-design trio. The junk that sat next to it (deathrest, gene labs, low-tier
installations) is gone or re-homed. VGE rows priced 100–400 are re-costed to
3,200–4,200: her systems are the endgame grind, not loose change.

## 2. New cuts — 30 rows, each with a recover line

Full per-row list with reasons in the visual and `restructured_model_v2.json`
(`fate2: cut`, `reason2`, `recover`). By group:

- **KotOR hero/companion relic catalogs — 18** (`guy762_ResearchKotOR_bastila`
  … `_bigZ`, + `_uncraftable`): every one priced 100,000,000 by its author,
  i.e. flagged unreachable; named heroes 4,000 years off era. *Recover:* the
  items stay in the world as loot; the best belong to Memory-Core quest
  rewards and trade finds, not the bench.
- **VGE genetics — 6** (`GR_*`): the gene-splicing laboratory register the
  owner named. *Recover:* the creature-crafting gameplay could return v2 as an
  **Oomo-sanctioned beast-breeding rite** — hatchery, not laboratory.
- **Deathrest — 1**: the vampire type case. *Recover:* v2 "long-sleep cradle"
  ship structure if the dormancy gameplay is ever wanted.
- **Torment Master — 2** (oil-pour cage, cranial pin): torture-dungeon
  register. *Recover:* dead.
- **Dark Ages crypts — 2** (bloodflame, catacombs): gothic register on a
  desert world. *Recover:* the mass-interment gameplay could return as
  sand-tomb vaults in the clan idiom.
- **RimFridge dev row — 1**: cost 0, unlocks nothing, the dump's one measured
  self-loop. *Recover:* dead.

Kept but FLAGGED for the owner (not cut, trade-offs §6): lightsabers (4 rows,
kept as the Strange Schools' deep temptation at re-costed prices), warcaskets
(7 rows, scavenged power armor reads as salvage), Space Worms xenobiology
(sarlacc-adjacent), insectoid hivetech (desert creature-keeping).

⚠️ **Consistency debt the v1 Anomaly cut created:** taxonomy §1 kept Anomaly
researchable *for the sarlacc/Assailant exception*; the owner's cut removes
that route. The exception content needs a non-research access (jawa-special
class item grant, or a Memory-Core event) before the cut ships. Carried as an
execution note, not re-litigated here.

## 3. Tier = cost band, and the 28 re-costs

v1 carried tier from techLevel, so "Light Installations" (1,000) sat in T4 and
VGE ship systems (100) sat in T3. v2 derives tier from the ruled bands
(T0 ≤600 < T1 ≤1,600 < T2 ≤3,000 < T3 ≤5,000 < T4). Consequences:

- **Felt-tier fixes come free**: Light/Medium/Heavy Installations land T1/T2/T3;
  holograms land T2.
- **Every remaining disagreement is now an explicit price change** — the
  28-row `RECOST` table in `classify_v2.py`, rendered in the visual. Headline
  groups: the RimAI spread (2,500/4,000/8,000), the SHIP re-pricing (VGE +
  GravTech + gravtech spine up to 3,200–9,000, Black Hole at the crown), the
  Alpha-Mechs ultra capstones (500 → 5,500 — priced as typos, spent as
  capstones), two measured KotOR inversions (basic upgrading 8,000 → 1,600
  under expert 6,000; simple droids 7,500 → 2,500 under adv. 2,500), and the
  lightsaber chain priced as hubris (6,000/8,000).
- Research Reinvented's techprint economy multiplies on top of every number
  here; these are BASE costs. The validator's band check becomes meaningful
  for the first time.

## 4. Royalty's inspiration — does tech gate the world?

**No — and the campaign already ruled the stronger inversion: the world gates
tech.** The sitting's four access classes (common / faction-held via
techprints / jawa-special / ship-only) are precisely the Royalty idea worth
keeping — progression bound to *standing and place* rather than points —
without its literal mechanics. Faction-held techprints are permits: the high
tree ends up gated on who you trade with, raid, or befriend
(TECHPRINT_FACTION_GATING_1 is already filed to execute this). Ship-only is
the title: the Utinni is the throne room, and her memory decides what you may
know next.

The Dungeon Pack cut set the boundary from the other side: research must never
unlock a *place*. Places unlock RESEARCH — the Memory Core reveal, a vault's
schematics, a hulk's salvaged prototype — which is research-as-revelation and
already canon. Recommendation: adopt no new world gate; write the four classes
into the manifest as a `access` column so the gate is data, and let
TECHPRINT_FACTION_GATING_1 carry the Royalty inheritance.

## 5. The Rites — researching the liturgy

The owner's question: *could Jawa rituals become a sort of tech — researching
better shipwide rituals, more ideologically active and powerful, as they
"learn" from their shipboard gods?* Yes — and most of it needs no C#.

**Mechanism facts (per the ideoligion skill + engine source):**
- The ideo BAKES at world creation; XML cannot add precepts/rituals to a live
  ideo, and MaxRituals is 6. [VERIFIED — skill §1, §2]
- Ritual outcome quality is computed by `RitualOutcomeComp_Quality` comps,
  including `RitualOutcomeComp_RoomStat` (room stats, e.g. impressiveness) and
  `RitualOutcomeComp_BuildingsPresent` (named buildings in the ritual room) —
  both engine classes read from the outcome def's data. [VERIFIED —
  `Source/RimWorld/RitualOutcomeComp_*.cs`]
- Buildings gate on research via `researchPrerequisites`; outcome defs are
  patchable XML. [VERIFIED — vanilla-standard]
- `The Salvation.rid` carries no `<fluid>` flag — the campaign ideo is NOT
  fluid today; development-point mechanics would need that conversion ruled.
  [VERIFIED — grep of the shipped .rid]

**Option A — the liturgy infrastructure ladder (XML-only). RECOMMENDED for v1.**
Five new `RUT_` research projects (below) unlock ritual buildings; a
PatchOperation adds `BuildingsPresent`/`RoomStat` quality comps for them to the
campaign rituals' outcome defs. Research then *measurably* improves every
ritual outcome through the vanilla quality table — better moods, better
rewards, fewer disasters — with zero new mechanics and zero coupling (theology
stays decoupled per canon §6.3). The proposed tree:

| tier | project (RUT_ defs, naming grammar) | cost | unlocks |
|---|---|---|---|
| T0 | **The Scrap Shrine** `RUT_Rites_ScrapShrine` | 400 | a salvage-built ritual focus; the first ritual room |
| T1 | **Conduit Choir** `RUT_Rites_ConduitChoir` | 1,200 | powered shrine tier — the gods hear better through live current |
| T2 | **God-Speaker Array** `RUT_Rites_GodSpeakerArray` | 2,600 | speaker masts + vox/drum stations; big-congregation quality |
| T3 | **Liturgy of the Hull** `RUT_Rites_HullLiturgy` | 4,000 | rites held against the Utinni's hull; ship-only access class |
| T4 | **The Gods Speak Back** `RUT_Rites_GodsSpeakBack` | 8,000 | the capstone — see Option B; memory-core gated |

"Learning from the shipboard gods" is carried by the access classes: T3/T4 are
ship-only/memory-gated — the deep liturgy is *revealed*, not derived, which is
the research-as-revelation principle applied to worship.

**Option B — the gods answer (small C#).** A GameComponent that, on completing
each Rites project, grants ideo development points so the player reforms in
new rituals/precepts — research literally funds doctrinal growth.
Requires ruling The Salvation FLUID (a real campaign decision: fluid ideos can
drift). Small, save-safe, sits on top of A.

**Option C — ranked rites (big C#).** Per-ritual rank in a WorldComponent,
Harmony postfix scaling outcomes by rank, research raises rank. Most powerful,
most coupling; defer to v2 unless A+B under-deliver.

**Recommendation: A now, B behind a one-line owner ruling on fluidity, C
parked.** A alone gives the tree teeth: five projects, five buildings, every
ritual in the campaign visibly better for researching them.

## 6. Trade-offs for the owner's later review

1. **Thirteen tabs vs six.** Thirteen `ResearchTabDef`s render as a wider tab
   strip in the research screen (wraps at small UI scale). Cost: crowding.
   Benefit: each tree is a guild with a readable identity. Middle option: 9
   (fold the three weapon trees into two — mass vs energy — and Rites into
   Reach). Recommended: thirteen; the strip fits at 100% UI scale.
2. **Tier = cost band, enforced.** 28 real price changes vs keeping techLevel
   tiers and the felt-wrongness (Light Installations in T4). Recommended: enforce.
3. **VGE genetics: cut wholesale vs keep a small Flesh tree.** Cut loses real
   creature-content gameplay; keeping it keeps the lab register the owner
   rejected. Recommended: cut, recover v2 as Oomo beast-breeding rites.
4. **KotOR hero catalogs: cut vs Memory-Core relic-hunt chain.** The relic
   hunt is genuinely attractive design (quest rewards for named artifacts) but
   is quest work, not research rows. Recommended: cut now, relic hunt as a
   quest-layer item later.
5. **Lightsabers: kept (re-costed as endgame hubris) vs cut as non-Jawa.**
   Kept version is a deliberate temptation — a Jawa clan building a Jedi's
   weapon is peak Ozzik. Owner's call; I kept them.
6. **Maker doctrines (Czerka/Mando/Hutt/… equipment catalogs): Shell
   sub-chain vs a 14th tree.** As a sub-chain they read as "we learn each
   maker's ways" — very scavenger. As a tree they'd be the clearest guild of
   all but push the count to 14. Recommended: sub-chain.
7. **Ritual mechanism size:** A / A+B / C — see §5. Recommended A, B behind a
   fluidity ruling.
8. **Warcaskets: kept vs cut.** Salvaged power-armor shells fit the register;
   the pirate flavor text does not. Keep + reflavor pass. Recommended: keep.
9. **Droid Depot's flat catalog.** Sixteen OuterRim droid rows all cost 2,000,
   so they all land T2 — a wall, not a ladder. Option: re-cost into a
   1,600→5,000 ladder (touches 16 more rows). Recommended: do it at manifest
   draft, not here.
10. **The Anomaly-exception debt** (§2 ⚠️): the sarlacc/Assailant content needs
    a non-research route once the 42-row cut ships. Must be resolved before
    execution, not after.

## 7. What execution needs from this (unchanged contracts)

No defName renames. Cuts via Cherry Picker; cherrypicker.py remains the
reader. Merges re-point unlocks before the loser dies. The manifest gains
columns `tab2/tier2/cost2/access/recover`; coverage-or-refuse stays the law
(522 in, 522 accounted — asserted by `classify_v2.py` at every run). All
validation against the RESOLVED post-RR dump, fingerprint-matched.
