# Card sitting agenda — 2026-09-12

Compiled for `MECHANICS_CARDS_SITTING_1`. Sections are ordered by how much
downstream work each decision unblocks — top of the list clears the most
other work. Read-only compilation: nothing here has been ruled, nothing
source has been edited.

**Correction applied:** `EXPLOSIVE_PLANT_GROWTH_1` and `FLOOD_WITNESS_EVENT_1`
are sourced from the committed 2026-09-10 designs
(`design/Jawa/worldbuilding/explosive_plant_growth_design.md` and
`design/Jawa/worldbuilding/flood_witness_event_design.md`), not the earlier
stale drafts under `design/Jawa/` — see the two "no open decisions" notes
below for why those items contribute zero cards to this agenda.

---

## Tier 1 — Foundational data integrity (blocks trusting the frozen artifacts at all)

### 1. Land the corrected planet census and declare one census source
**Unblocks:** every doc, dashboard, or design note that cites Ash'karr biome
counts, water totals, or sea sizes — currently three sources disagree
(546/557/604 for one biome alone).
**Question:** may the corrected, measured census numbers replace the stale
2026-08-23 ones in `canon.yml`, and can we declare the frozen tile CSV the
one true source of these counts from now on?
**Options:**
- **Yes, land it and declare the CSV the sole source.** Trade: closes the
  three-way disagreement everywhere in one stroke; every future count is
  cited to one file.
- **No, hold.** Trade: every doc keeps citing whichever of the three
  numbers it happened to use; nothing currently blocked by this gets
  unblocked.
**Source:** `infrastructure/state/items/CANON_PLANET_CENSUS_1.md` (spec +
2026-09-12 addendum).

### 2. Approve re-stamping the frozen region-CSV's freeze record
**Unblocks:** any tool or doc that reads the CSV's `region` column (809
tiles are currently stale, including a whole new region nobody's tooling
knows exists yet).
**Question:** can BENCH patch the frozen CSV's region names (five renames,
already prepared) and re-stamp its freeze fingerprint in the same change?
**Options:**
- **Yes, proceed.** Trade: the five renames land immediately (775 rows);
  the 34-tile "Abandoned Mines" region still can't land until its per-tile
  list is found (separate blocker, not this decision).
- **No, hold.** Trade: everything reading `region` off this CSV keeps
  citing five dead names.
**Source:** `infrastructure/state/items/CSV_REGION_SYNC_1.md`.

---

## Tier 2 — Cross-cutting mechanism rulings (each unblocks several biomes or systems)

### 3. Vapor emitters — Ancient*Vent family placement rule
**Unblocks:** `VAPOR_EMITTER_PLACEMENT_1` Part 4's live cleanup pass, and
every ruin/dungeon biome that carries these gas vents.
**Question:** should smoke/toxic/heat/cold-gas "Ancient Vent" props be
ruled as ruin decoration only, with no weather-style placement rule at all?
**Options:**
- **Ratify as proposed:** allowed only on tiles that already carry an
  ancient-ruin landmark, banned nowhere else. Trade: matches how they
  already sit on the map (ruin-clustered); no new placement work needed.
- No alternative option is drafted in the source.
**Source:** `design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md`,
Part 2.

### 4. Vapor emitters — magma vent biome lock
**Unblocks:** the same Part 4 cleanup; also flags 5 existing map tiles as
out-of-bounds and needing a fix once ruled.
**Question:** should magma vents stay locked to volcanic-crater biomes only,
never placed near mountains generally?
**Options:**
- **Ratify as proposed:** keep the existing lock to the two volcanic-crater
  biomes. Trade: simple, matches engine defaults; the 5 tiles currently
  sitting outside that lock become a known cleanup item, not a new rule.
- No alternative option is drafted in the source.
**Source:** `design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md`,
Part 2.

### 5. Vapor emitters — swamp/ruin gas family rule
**Unblocks:** the same Part 4 cleanup for four gas-vent types currently
placed by chance rather than by rule.
**Question:** should rotstink/toxic/smoke/deadlife gas vents be tied to
biome type (swamp gets rotstink, dead-machine ruins get toxic/deadlife)
instead of mountains?
**Options:**
- **Ratify as proposed:** lock each gas type to the biome family it's
  already clustering in. Trade: matches the map as it already looks;
  no distance/terminator rule needed for these.
- No alternative option is drafted in the source.
**Source:** `design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md`,
Part 2.

### 6. Vapor emitters — helixien gas vent placement (unverified mechanism)
**Unblocks:** whether this gas vent type can be trusted for design work at
all before someone checks how it actually spawns.
**Question:** should we treat "volcanic and deep-desert tiles" as the
working placement rule for helixien gas vents until someone confirms how
the game actually places them?
**Options:**
- **Ratify as a placeholder rule, flagged for a follow-up check.** Trade:
  design work can proceed now; the actual game mechanism might turn out
  different and force a rewrite later.
- No alternative option is drafted in the source.
**Source:** `design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md`,
Part 1 gap + Part 2.

### 7. Vapor emitters — cold-gas vent rule for the planet's dark side
**Unblocks:** whoever eventually builds the not-yet-built cold-gas vent
(`RUT_GasVent`), and the propane-lake design it ties into.
**Question:** should the still-unbuilt cold-gas vent be barred from the
sunlit side of the planet entirely, only allowed once you're deep enough
into the cold zone?
**Options:**
- **Ratify as proposed:** allowed only past the propane-lake cold
  threshold; banned on the sunlit side. Trade: keeps this vent as a
  night-side-only signature; no work needed until the vent itself is built.
- No alternative option is drafted in the source.
**Source:** `design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md`,
Part 2.

### 8. Vapor emitters — how the Weeping Stones oasis gets its water
**Unblocks:** the oasis's water-source story, and settles whether a new
map-rule type needs to be built at all.
**Question:** should the hot-water oasis get its steam-vent feel by turning
up a biome-wide dial, or by building it a brand-new one-off rule?
**Options:**
- **Turn up the oasis biome's own geyser dial (preferred in the source).**
  Trade: no new content to build, but it applies evenly to every oasis
  tile — no fine control over individual tiles.
- **Build a bespoke rule just for this oasis.** Trade: lets each oasis
  tile be tuned individually, but it's new content that has to be built
  and maintained.
**Source:** `design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md`,
Part 2.

### 9. Contagion mutation deck — where do the "bad genes" come from?
**Unblocks:** building the Contagion exposure mechanism and the Unfinished's
random-limb spawner (both share this deck).
**Question:** when a mutation roll adds an unstable gene, should it reuse
the game's existing "genetic instability" genes, or should we design our
own custom one?
**Options:**
- **Reuse the vanilla genes as-is.** Trade: nothing new to build or tune.
- **Design a custom Utinni-flavored gene.** Trade: more work, but the
  mutation can carry campaign-specific flavor the vanilla genes don't.
**Source:** `research/mutation_systems_survey_2026-09-11.md`, "DRAFT — owner
rules the deck" → Open questions.

### 10. Contagion mutation deck — what happens if you try to remove a mutation?
**Unblocks:** the same mutation deck build.
**Question:** when a colonist tries to surgically remove a Contagion-added
body part, should it risk spawning a hostile creature (copying how the
game's other mutated-flesh parts behave), or something Contagion-themed
instead?
**Options:**
- **Copy the existing risk exactly** (spawns a hostile creature on a
  failed removal). Trade: no new content, proven mechanism.
- **Design a Contagion-flavored version** (e.g. spawns a local infection
  instead). Trade: fits the theme better, but is new work.
**Source:** `research/mutation_systems_survey_2026-09-11.md`, "DRAFT — owner
rules the deck" → Open questions.

### 11. Contagion mutation deck — should some rolls ever be pure bad luck?
**Unblocks:** the same mutation deck build; changes how scary/fair the
whole mechanic feels.
**Question:** should about 1 in 10 mutation rolls be pure downside with no
upside at all, or should every roll guarantee at least some benefit
(always taxed, never a pure loss)?
**Options:**
- **Keep a small pure-downside chance (current draft: ~10%).** Trade: adds
  real unlucky moments, at the cost of occasionally feeling unfair.
- **Remove it — every roll always pays out something.** Trade: feels
  fairer and matches the "large and random" lore framing better, but
  removes the rare gut-punch moment.
**Source:** `research/mutation_systems_survey_2026-09-11.md`, "DRAFT — owner
rules the deck" → Open questions.

### ⚠️ EXPLOSIVE_PLANT_GROWTH_1 — no open decisions found
The corrected, current design (`design/Jawa/worldbuilding/explosive_plant_growth_design.md`
§7, "Owner rulings, 2026-09-10 morning batch — all four answered") shows
every open question already ruled: the Burst's lethality is capped at
injury+knockdown, never death; the water-for-growth irrigation pump is
working as intended with no brake; the Fever Wood's Nectar Flush variant is
IN; and the shipping look is a stepped default with a smooth close-up cap
(perf gate still required before any density promise). The earlier
`design/Jawa/explosive_plant_growth_draft.md` and its six "Owner cards" are
a stale, superseded pre-ruling draft — nothing from it belongs on this
agenda.

---

## Tier 3 — Plot/reveal gating (unblocks quest and content authoring for major arcs)

### 12. The Rust Cathedral — does the Utinni already know it's alive?
**Unblocks:** `CATHEDRAL_PLAYER_CONCEALMENT_ARC_1`'s build (who can usher
the late-game reveal, what she says beforehand).
**Question:** when the Utinni vouches for the player with the Cathedral,
does she already know it's a living thing, or does she believe she's
following dead ritual and only learns the truth alongside the player?
**Options:**
- **(a) She knows, and is the one exception to "nobody knows."** Trade:
  makes her the natural guide for the late reveal.
- **(b) She believes it's dead protocol and learns at the reveal too.**
  Trade: the spec's own view is this makes the stronger scene, but it
  means writing her discovering the truth alongside the player.
**Source:** `design/Jawa/cathedral_concealment_arc_spec.md`, "Cards for the
owner" → A1.

### 13. The Rust Cathedral — how much does the late-game reveal explain?
**Unblocks:** same arc build; decides how much of the Cathedral's deep
lore is spoken aloud vs. held back.
**Question:** should the late-game reveal only show that the Cathedral is
alive and vast, or should it also explain more of what it's actually for
(the Assailants, its decline, its reserves)?
**Options:**
- **Reveal more now.** No trade stated in the source beyond the choice
  itself.
- **Hold purpose back for a later sitting.** No trade stated in the
  source beyond the choice itself.
**Source:** `design/Jawa/cathedral_concealment_arc_spec.md`, "Cards for the
owner" → A2.

### 14. The Rust Cathedral — can the Empire ever actually discover it?
**Unblocks:** same arc build; decides whether "exposure" is a real loss
condition or a pressure that never fully resolves.
**Question:** if the player carelessly draws Imperial attention to the
Cathedral, should full discovery be something that can actually happen and
end the relationship, or should it stay a mounting dread that's narrated
but never fully plays out?
**Options:**
- **(a) Make it a real, losable outcome.** No trade stated beyond the
  choice itself.
- **(b) Keep it asymptotic — pressure builds, narrated, never completes.**
  The spec's own draft assumes this for v1.
**Source:** `design/Jawa/cathedral_concealment_arc_spec.md`, "Cards for the
owner" → A3.

### 15. The Rust Cathedral — add the "misdirect the surveyors" quest beat?
**Unblocks:** same arc build; adds or drops one quest surface.
**Question:** should there be a quest where the player can actively feed a
snooping Imperial survey team boring, believable lies to protect the
Cathedral?
**Options:**
- **In.** Trade: it's the one place the player actively practices
  concealment rather than just abstaining from bad behavior — but it's a
  new quest to build.
- **Out.** Trade: less to build, but the arc stays purely about what the
  player doesn't do, never what they actively do to help.
**Source:** `design/Jawa/cathedral_concealment_arc_spec.md`, "Cards for the
owner" → A4.

### 16. The Rust Cathedral — when does selling its curiosities count as exposure?
**Unblocks:** same arc build; needed to price one of the standing-gain/loss
mechanics.
**Question:** the Cathedral's oddities (bolts, eel-catch) are safe to sell
to ordinary buyers — at what point does a buyer count as risky enough that
the sale hurts the Cathedral's cover instead?
**Options:** open question, no options drafted — the source asks for "one
sentence" ruling the line but proposes no candidate answers.
**Source:** `design/Jawa/cathedral_concealment_arc_spec.md`, "Cards for the
owner" → A5.

### 17. Ashfall Research Base — when does the reveal fire, and in what order?
**Unblocks:** the base's dungeon build and its quest weave (FOUNDRY is
waiting on this and the next three).
**Question:** should the player learn the base's role in the Contagion
story from its datafiles first, or should that wait until later story
beats (the Helix lineage reveal / the "flesh dungeon") have already
landed?
**Options:** open question, no options drafted.
**Source:** `infrastructure/state/items/OCULAR_OVERDRIVE_SITE_1.md`,
"Progress 2026-09-11"; also listed in `MECHANICS_CARDS_SITTING_1.md` under
`design/Jawa/worldbuilding/ashfall_research_base.md`.

### 18. Ashfall Research Base — amend canon.yml's Helix lineage entry
**Unblocks:** same dungeon/quest work; canon.yml needs to state the Helix's
actual motive and outcome once ruled.
**Question:** what should canon.yml say about why the Helix spliced
themselves into the Rakatan bloodline (motive) and what it cost them
(outcome)?
**Options:** open question, no options drafted.
**Source:** `infrastructure/state/items/OCULAR_OVERDRIVE_SITE_1.md`,
"Progress 2026-09-11"; also `MECHANICS_CARDS_SITTING_1.md`.

### 19. Ashfall Research Base — pick the landmark's display name
**Unblocks:** placing the landmark on the live world map.
**Question:** what should this site be called on the world map?
**Options:** open question, no options drafted.
**Source:** `infrastructure/state/items/OCULAR_OVERDRIVE_SITE_1.md`,
"Progress 2026-09-11"; also `MECHANICS_CARDS_SITTING_1.md`.

### 20. Ashfall Research Base — what does it do for the campaign?
**Unblocks:** same dungeon/quest work; decides whether it's worth building
as a quest destination, a lootable prize, or a ticking threat.
**Question:** should the base function as a quest line, a one-time prize
site, or a threat clock that escalates over time?
**Options:** open question, no options drafted.
**Source:** `infrastructure/state/items/OCULAR_OVERDRIVE_SITE_1.md`,
"Progress 2026-09-11"; also `MECHANICS_CARDS_SITTING_1.md`.

### ⚠️ FLOOD_WITNESS_EVENT_1 — no open decisions found
The corrected, current design (`design/Jawa/worldbuilding/flood_witness_event_design.md`
§5, "Owner rulings, 2026-09-10 morning batch — all four answered") shows
every open question already ruled: lethality is capped at injury+knockdown
(shared with the growth item's ruling above, for both the first flood and
later natural floods); the site is one canonical, fixed authored Cracked
Lands tile (no floating site, no tile-picker); the offer voice is a
Moisture Farmer invitation; and the trigger beat is the player's first
gravship landing within range of the Cracked Lands. The earlier
`design/Jawa/flood_witness_event_draft.md` and its five "Owner cards" are a
stale, superseded pre-ruling draft — nothing from it belongs on this
agenda.

---

## Tier 4 — Biome kit cards (each unblocks its own kit's build; a couple interlock)

### 21. Miasma kit — the fever-forged "strange" tier
**Question / options:** open question, no options drafted; the source
names only the topic.
**Unblocks:** `miasma_kit_spec.md`'s build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/miasma_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 22. Miasma kit — surge behavior vs. player-held ground
**Question / options:** open question, no options drafted.
**Unblocks:** same kit build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/miasma_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 23. Miasma kit — scope of creche despoiling
**Question / options:** open question, no options drafted.
**Unblocks:** same kit build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/miasma_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 24. Fever Wood kit — hidden plumbing factions vs. the ban on §6.2
**Question / options:** open question, no options drafted; the source
flags a possible conflict with an existing ban but doesn't propose a
resolution.
**Unblocks:** `fever_wood_kit_spec.md`'s build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/fever_wood_kit_spec.md`,
per `MECHANICS_CARDS_SITTING_1.md`.

### 25. Fever Wood kit — Tenant behavior vs. player pawns
**Question / options:** open question, no options drafted.
**Unblocks:** same kit build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/fever_wood_kit_spec.md`,
per `MECHANICS_CARDS_SITTING_1.md`.

### 26. Fever Wood kit — scope of thornbug fear behavior
**Question / options:** open question, no options drafted.
**Unblocks:** same kit build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/fever_wood_kit_spec.md`,
per `MECHANICS_CARDS_SITTING_1.md`.

### 27. Sump kit — does only the moat trigger the command mechanism?
**Question / options:** open question, no options drafted.
**Unblocks:** `sump_kit_spec.md`'s build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/sump_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 28. Sump kit — can era traps be disarmed?
**Question / options:** open question, no options drafted.
**Unblocks:** same kit build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/sump_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 29. Sump kit — what ends a woken beast?
**Question / options:** open question, no options drafted.
**Unblocks:** same kit build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/sump_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 30. Forge kit — how deep does the tower go in v1?
**Question / options:** open question, no options drafted.
**Unblocks:** `forge_kit_spec.md`'s build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/forge_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 31. Forge kit — how lethal is the boiling rain?
**Question / options:** open question, no options drafted.
**Unblocks:** same kit build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/forge_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 32. Forge kit — penned beldons vs. the tibanna embargo (rule with #38-39)
**Question / options:** open question, no options drafted. The source
notes this interacts with the tibanna embargo cards below and should be
ruled together with them.
**Unblocks:** same kit build, and the tibanna embargo resolution (#38-39).
**Source:** `design/Jawa/worldbuilding/biomes/kits/forge_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 33. Scald kit — what does the steam-catch produce?
**Question:** should the steam-catch mechanic output a plain water item, a
pipe-based water system, or both?
**Options:**
- **Item water.** No trade stated in the source.
- **Pipe-based (`dbh_water`) system.** No trade stated in the source.
- **Both.** No trade stated in the source.
Note: this shares its salinity question with the liquid-types mod's card
#35 below — one ruling covers both.
**Unblocks:** `scald_kit_spec.md`'s build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 34. Scald kit — bottom-walker creatures: scenery or interactive?
**Question:** should the Scald's "bottom-walker" creatures stay pure
background visuals forever, or should the design leave room for a player
to eventually interact with them at depth?
**Options:**
- **Visual forever.** No trade stated in the source.
- **Eventual depth-pawn interaction.** No trade stated in the source.
**Unblocks:** same kit build.
**Source:** `design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 35. Liquid types mod — Scald basin salinity (shared with card #33)
**Question / options:** open question, no options drafted; tied to card
#33's steam-catch output question — one ruling settles both.
**Unblocks:** `RM_liquid_types_mod.md`'s build and the Scald kit's build.
**Source:** `design/RimMandrake/RM_liquid_types_mod.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 36. Liquid types mod — coolant fishing bucket
**Question / options:** open question, no options drafted.
**Unblocks:** same mod build.
**Source:** `design/RimMandrake/RM_liquid_types_mod.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 37. Liquid types mod — is a sediment/film system in v1?
**Question:** should a sediment/film build-up system ship in the first
version of the liquid-types mod, or be deferred?
**Options:**
- **In v1.** No trade stated in the source.
- **Deferred.** No trade stated in the source.
**Unblocks:** same mod build.
**Source:** `design/RimMandrake/RM_liquid_types_mod.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 38. Tibanna embargo — cut, gate, or relax the mining contradiction (rule with #32)
**Question:** other active mods currently let players mine tibanna gas
directly, which contradicts the campaign rule that beldons are the only
source. Should that mining ability be cut, locked behind research, or
should the campaign rule be relaxed instead?
**Options:**
- **Cut it.** The spec's draft assumes this option. No trade stated
  beyond that.
- **Research-gate it.** No trade stated in the source.
- **Relax the beldons-only rule instead.** No trade stated in the source.
Note: rule together with card #32 (penned beldons vs. this same embargo).
**Unblocks:** `tibanna_embargo_plot_spec.md`'s build and the Forge kit's
build.
**Source:** `design/Jawa/tibanna_embargo_plot_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 39. Tibanna embargo — how does it resolve?
**Question:** how should the tibanna embargo plot end — does it break, does
it bleed out slowly, or does the Empire win it outright?
**Options:**
- **Break.** No trade stated in the source.
- **Bleed.** No trade stated in the source.
- **Empire wins.** No trade stated in the source.
**Unblocks:** same plot build.
**Source:** `design/Jawa/tibanna_embargo_plot_spec.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

### 40. Poison Forest — ratify the four drafted weather names
**Question:** should the four drafted weather names for Poison Forest
(scatter-dusk, vent bloom, vapour bank, dewfall) be ratified as-is, the
same way the sibling biomes' weather tables were?
**Options:** open question beyond ratify/reject — no alternative names or
trades are drafted in the source.
**Unblocks:** any def work on Poison Forest weather beyond the one spore
weather type already built.
**Source:** `design/Jawa/worldbuilding/biomes/poison_forest.md` §4b, per
`MECHANICS_CARDS_SITTING_1.md`.

### 41. Fauna tolerance — how do "injection-layer" animals get their climate range?
**Question:** twelve animals live in layers (fall-line, lantern-deeps,
wreck-fields) that were never painted onto the map directly — should their
allowed climate range be inherited from the union of their host biomes'
ranges, or should each one get a hand-set range instead?
**Options:**
- **Inherit the host biomes' combined range.** No trade stated in the
  source.
- **Hand-set ranges per animal.** No trade stated in the source.
**Unblocks:** closing out `fauna_tolerance_violations_2026-09-11.md`'s one
remaining undecided case.
**Source:**
`design/Jawa/worldbuilding/fauna_tolerance_violations_2026-09-11.md`, per
`MECHANICS_CARDS_SITTING_1.md`.

---

## Tier 5 — Gizka ship-pest (self-contained; unblocks only its own build)

### 42. Gizka pest — how mean should the escalation curve be?
**Unblocks:** `GIZKA_TRIBBLE_ADAPTATION_1`'s build.
**Question:** how fast should a stowaway gizka go from "cute" to "chewing
your wiring" — over a season, over about a week, or should it just ship
tunable with a slow default?
**Options:**
- **(a) Slow burn (about a season).** Trade: more warning and more time to
  get attached (culling hurts more) — but some players may never see the
  problem at all.
- **(b) One bad decision, fast (about a week of neglect).** Trade: the
  joke lands reliably — but less time to fall in love with them first.
- **(c) Tunable, ship the slow default.** Trade: friendliest to later
  tweaking — but whichever default ships becomes the "real" experience
  everyone remembers.
**Source:** `design/Jawa/gizka_ship_pest_draft.md`, "Owner cards" → Card 1.

### 43. Gizka pest — what should a gizka sell for?
**Unblocks:** same build; needed before the trade/economy piece can ship.
**Question:** the donor mod prices a gizka at 100 silver, which turns a
breeding swarm into a money printer — how far down should we cut that
price?
**Options:**
- **(a) About 15 silver** (muffalo-calf territory). Trade: selling still
  feels like the scam working; culling a big swarm nets real pocket
  change.
- **(b) About 5 silver** (chicken territory). Trade: the purest fix —
  selling becomes mood-management rather than income, barely worth the
  trip.
- **(c) Leave it at 100, rely on the population cap instead.** Trade: no
  price patch needed, but even a capped swarm of 20 is worth 2,000 silver
  standing around — the draft's own view is this is the weakest option.
**Source:** `design/Jawa/gizka_ship_pest_draft.md`, "Owner cards" → Card 2.

### 44. Gizka pest — does culling need an extra guilt penalty?
**Unblocks:** same build.
**Question:** on top of the game's normal "you killed a named pet" guilt,
should culling any gizka (even un-bonded ones, because they're cute) carry
a small extra mood penalty?
**Options:**
- **(a) Vanilla only, no new penalty.** Trade: nothing new to build, but
  culling a swarm becomes almost free once they're not bonded.
- **(b) Add a small "culled the gizka" guilt for anyone who watches.**
  Trade: one new item to build, but it makes selling/baiting/freezing them
  out genuinely competitive with just killing them.
**Source:** `design/Jawa/gizka_ship_pest_draft.md`, "Owner cards" → Card 3.

### 45. Gizka pest — ship without the gravship-hold trigger, or wait for it?
**Unblocks:** same build; decides the launch scope.
**Question:** the "found one in your ship's hold" trigger is the flagship
version of this feature, but nobody's confirmed the exact game hook for it
yet — should we ship without it and add it later, or hold the whole
feature until that hook is found?
**Options:**
- **(a) Ship without it, add later.** Trade: the feature ships sooner, but
  its signature moment arrives late.
- **(b) Hold the whole feature for the hook.** Trade: launches complete,
  but the whole feature waits on one uncertain technical detail.
**Source:** `design/Jawa/gizka_ship_pest_draft.md`, "Owner cards" → Card 4.

### 46. Gizka pest — include the quest-reward "free gift" gag in v1?
**Unblocks:** same build; smallest-scope decision in this set.
**Question:** should a gizka be able to show up as a "free gift" in a quest
reward (a classic scam joke), in the first version?
**Options:**
- **In v1.** No trade stated beyond "touches the quest system for one
  gag."
- **Deferred.** Trade (per the source): cheap to put off; nothing else
  depends on it.
**Source:** `design/Jawa/gizka_ship_pest_draft.md`, "Owner cards" → Card 5.

---

## Count

**46 decisions pending.**
