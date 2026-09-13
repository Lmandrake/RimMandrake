<!-- status: live -->
# CAMPAIGN ARC — the gather (Phase A of CAMPAIGN_STORY_SITTING_1)

_An INDEX + EXTRACT, never a rewrite. Every entry is a quote (or a paraphrase
marked ¶) with a source path and a status tag. Gaps say `GAP`; nothing here is
invented. Entry ids (G1…) are stable — Phase B cards cite them. Built
2026-09-12 by BENCH (AFK pass); the two-blind-arms confirmation of every
`STATUS-DOUBT` row is still owed before a SUPERSEDED verdict lands on any of
them._

Status tags: `RULED (date, where)` · `DRAFTED (by whom, agreed?)` ·
`MENTIONED-UNUSED` · `CONTRADICTED-BY <path>` · `SUPERSEDED-BY <ruling>` ·
`STATUS-DOUBT` · `INFERRED (names both fragments)`.

---

## 1. The spine — what the campaign IS, in the order a player could live it

**G1 — the premise and the opening moment.** `RULED (canon; reconciled_lore)`
> "A Jawa scavenger clan on the desert world **Ash'karr** breaks into the oldest hulk in a Hutt discard yard — a Rakatan vessel … and wakes it by pressing a Jawa-patterned mind into its empty ancient core. The ship was the **Kolyska**, 'Cradle', one of the initiator vessels that terraformed this world … The campaign opens the moment the stolen ship sets down and the hatch opens: the ship is home, the Hutts are furious, the Empire watches from orbit, and the flight hardware is missing. **Getting it off the ground is the campaign.**" — `design/Jawa/reconciled_lore/01_campaign.md`

**G2 — the start place.** `RULED (2026-09-08, owner card on PLAYER_START_SITE_1)`
> "The junkyard anchors at the Zeddo's Toll cluster (candidate start tile **17007**, alternates 1621/17011 …). Ships are the real terrain (Fall Line Barrens); the old megastructures arrive by structure injection." — `infrastructure/state/items/PLAYER_START_SITE_1.md`
¶ Note: "Fall Line Barrens" was renamed **The Breaks** 2026-09-12 (G81). The canonical start save is `CANONICAL_ASHKARR_START_2026-09-12.rws`; ship landed at 17007 (`infrastructure/state/canon.yml` planet block).

**G3 — the loop.** `RULED (01_campaign)`
> "Land → choose objectives → temporary camp → explore → gather → improve the ship → enemy pressure rises → **decide what to leave behind** → launch → repeat. The permanent colony lives aboard; planetary camps are disposable." — `design/Jawa/reconciled_lore/01_campaign.md`

**G4 — the three pressures that force motion.** `RULED (owner 2026-08-05/06; 01_campaign)`
> "**The Empire** — the singular escalating military pursuer, orbital-first. Its detection timer forces exit from any open-sky tile in under one growing season … **The Hutt ledger** — economic/criminal pressure; they want the ship back and they want paying … **Ta'Baa's clock** — the theological pressure to move." — `design/Jawa/reconciled_lore/01_campaign.md`

**G5 — flight hardware is a mid-game earn.** `RULED (2026-08-14, "do not 'fix' this")`
> "**Flight capability is v1; flight HARDWARE ships unbuilt** — no thruster, tank or console. Mobility is earned mid-game." — `design/Jawa/reconciled_lore/01_campaign.md`

**G6 — the Antiquities ladder is the campaign's deepest progression.** `RULED (2026-09-04, antiquities_design ruled by card sitting)`
> "the campaign's deepest progression is the clan **reading the world back into existence**: language, then religion, then culture, then maps, then a voice that the last living ancients will actually answer … read aloud to a ship that is slowly realizing the encryption is *its own*." — `design/Jawa/antiquities_design.md` §0

**G7 — the Cathedral relationship arc (WARY → TOLERATED → VOUCHED → REVEALED).** `RULED (canon §7b 2026-09-10) + DRAFTED (spec 2026-09-11, cards A1–A5 RULED 2026-09-12)`
> "**The player's Rakatan gravship flying around agitating the Empire is exactly the danger it fears — so it dislikes the player at first and hides from them for a long while.**" — `design/Jawa/worldbuilding/biomes/the_rust_cathedral.md` §7b amendment 2026-09-10
> Stage table (0 WARY / 1 TOLERATED / 2 VOUCHED / 3 REVEALED) — `design/Jawa/cathedral_concealment_arc_spec.md` §1.

**G8 — the Spire is the Key (main-line beat).** `RULED (2026-09-12 plot sitting, owner verbatim; commit 919d5c155)`
> "This is the Key that opens the frozen War Base beneath the Propane Lake on the antipodal node. The Dark Spire was the command center for the Rakatan surface level machine, so the command codes are the only way into the base after it's revealed by the melting event." … "The command codes CANNOT be granted by the cathedral. They are on an isolated system within the command center (dark spire) and were never ceeded to the cathedral." — `design/Jawa/worldbuilding/ashfall_research_base.md` §6

**G9 — the crater event (the lake's ending).** `RULED (ANCIENT_WAR_LAB_1 rulings + amendment 2026-09-12)`
> "the lake becomes **a massive fresh crater and a ripped-open ancient lab, shielding intact, amazingly** — on a frozen world that is otherwise never allowed to change." … "There will be multiple ways for the player to cause it. And if they fail to do so, there may be automated ways for it to occur too. Either way, no one will miss it. We will effectively have a 'cut scene.'" — `design/Jawa/worldbuilding/biomes/the_propane_lakes.md` §8

**G10 — the war lab is a two-key dungeon.** `RULED (2026-09-12 amendment)`
> "The war lab is a two-key dungeon: the lake's ending opens the ground; the Spire's codes open the door." — `design/Jawa/worldbuilding/biomes/the_propane_lakes.md` §8 amendment

**G11 — the dungeons arc (Assailant complex + six vaults) and its learning chain.** `RULED (2026-08-30 + 2026-09-01 cards)`
> "earn droid trust → earn Cathedral trust → Cathedral reveals 'Where the infection started... and remains to this day' … → thaw-gate strike → the Cathedral wants the Cradle as its pyrrhic surgical strike against the Assailant → releasing that knowledge to the Hutts requires a deal protecting the Cathedral's 'beautiful young children,' the droids." — `design/Jawa/worldbuilding/dungeons_arc_spec.md` §2.6 (canon.yml `assailant_reveal_arc`)

**G12 — the Reclamation (late game).** `RULED (2026-09-04, canon.yml rakata.reclamation)`
> "late game, one concentrated event: every ancient the player ever woke, united, tries to take the Utinni back — in local collaboration with the Helix, who turn hostile (ending the Ascendant Ladder boon economy: a price the player should see coming). Survive it and the ancients become permanently neutral — dominated." — `design/Jawa/reconciled_lore/09_arcs_dungeons_quests.md` §2b

**G13 — the tibanna embargo clock (the Forge, both ends ruled).** `RULED (CARD T2, 2026-09-12)`
> "The player can BREAK THE METER (assault/heist chain on the station; monopoly ends, gas floods, Heat maxes, Act III early — the garrison must be beatable), and if the player never intervenes THE EMPIRE WINS THE CLOCK (the drought completes; resistance factions go quiet …)." — `design/Jawa/tibanna_embargo_plot_spec.md` Cards

**G14 — victory: v1 is open-ended.** `RULED (owner 2026-08-30)`
> "v1 is OPEN-ENDED: the arcs provide climaxes, nothing rolls credits. The pressure systems … give the late game its shape; authored endings (the god-map roads) are v2." — `design/Jawa/reconciled_lore/01_campaign.md` §Victory

**G15 — the other designed arcs riding alongside.** `RULED (09_arcs list)`
¶ The nine-claimant ship (which god wins the Body); the succession clock (Nekko Vok); the love-gate (Yeku/Wim); the droid-theft heist (Griz, one-time unlock); the god-mapped win paths (v2 per G14). — `design/Jawa/reconciled_lore/09_arcs_dungeons_quests.md` §§3–7

**G16 — spine ORDER caveats.** `INFERRED / GAP`
- The item's own beat order ("the yard → the theft → getting it off the ground → the pressures → the Antiquities ladder → the Cathedral thaw → the Spire/the Key → the crater event → the war lab → the Reclamation → the open end") is the sitting brief's phrasing, not a ruled sequence — `infrastructure/state/items/CAMPAIGN_STORY_SITTING_1.md`.
- Cathedral-arc vs Spire order: **no stated dependency** — the codes explicitly do NOT ride the Cathedral relationship (G8), and no ruling says the thaw must precede or follow the Spire. `GAP`.
- Crater-event timing vs the Reclamation: no stated order. `GAP`.
- Reclamation trigger: vault_thaw build expresses "late-ness … as a 45-day chain delay rather than a VOICE gate" — flagged there as **PROPOSED, not canon** — `design/Jawa/worldbuilding/vault_thaw_quest_family.md` §0.
- INFERRED: the war lab is the campaign's antipodal ENDGAME — from "This makes the Base a **main-line beat**: the campaign's antipodal endgame passes through the Spire's core" (`ashfall_research_base.md` §6) + the two-key gate (G10). What the player finds/does INSIDE the war lab: `GAP` (no source states its interior, prize, or consequence beyond "where the Assailants were first contained and studied").

---

## 2. Places with purposes

**G20 — Zeddo's Salvage Yard (the start).** `RULED (2026-09-08 + rename 2026-09-12)`
> "a Hutt junkyard — 'The Hutts keep a mountain of the galaxy's discards out here' — with the dead Rakatan hull (the gravship), Gamorrean guards, and the clan sneaking in." — `infrastructure/state/items/PLAYER_START_SITE_1.md`

**G21 — The Spire / Ashfall Research Base (Helix "Overdrive").** `RULED (2026-09-06 name; 2026-09-12 function)`
> "a mysterious thin black needle of a building with a disc landing near the top, visible only occasionally due to the atmospheric turbulence over the Scald's mountains." — `design/Jawa/worldbuilding/ashfall_research_base.md` §6. Purpose: the Helix–Assailant reveal datafiles (encrypted, ladder-gated) + the Rakatan command codes (G8). Dungeon sitting + live placement still owed (§6 "Still owed").

**G22 — the ancient war lab (under the propane lake, antipode).** `RULED (siting + gate; interior GAP)`
> "**beneath the propane lake's surface, directly over the Impact Site where the first infection occurred** — where the Assailants were first contained and studied … the study subjects here are **live, trapped, and being studied**." — `design/Jawa/worldbuilding/biomes/the_propane_lakes.md` §8. PURPOSE beyond entry: `GAP` (G16).

**G23 — the Rust Cathedral / Archon.** `RULED (frozen sheet + 2026-09-12 name amendment)`
> "It was called Archon by them … So Rakatan systems will refer to it as Archon. It greatly dislikes the name Rust Cathedral and sees that as what has become of its surface only." — `design/Jawa/worldbuilding/biomes/the_rust_cathedral.md` §1 amendment. Purpose: the concealment arc (G7), the reveal descent (spec §5), the Assailant learning chain (G11), gravtech boons, the shard-reconstruction compute partnership (G44).

**G24 — the six Forsaken vaults V1–V6.** `RULED (siting table, types, 325×325, concentric grammar)`
> V1 678 Rust Cathedral ① · V2 4000 Scorch ① · V3 9167 Fall Line ① · V4 17461 Deadstone ② · V5 37 Slough ② · V6 20853 Umbra ③ ("the rare emotional scene"). — `design/Jawa/worldbuilding/dungeons_arc_spec.md` §3.2. Quests built as XML (`vault_thaw_quest_family.md` §0 table); bridge placement + hand-finish owed.

**G25 — the Assailant flesh complex.** `RULED (site family; adjacency to V6)`
> "**The Assailant's first-impact point** … A HUGE frozen complex, inert and dormant since the fall … *the* site, the one place the whole war traces back to." — `dungeons_arc_spec.md` §2.1. Purpose: the tyranny reveal (register guard: "the Rakata tyranny surfaces HERE, nowhere earlier" — `09_arcs` §Dungeons); thaw-gate = deliver `AIPersonaCore`.

**G26 — the Forge + the Imperial gas station.** `RULED (the_forge.md §8 via tibanna spec)`
> "a garrisoned gas-mining station working the beldon herds, metering the one thing every blaster needs, 'watching their ammunition slowly run out with a smart grin.'" — `design/Jawa/tibanna_embargo_plot_spec.md` §law. Purpose: the embargo clock (G13).

**G27 — the Fall Line (The Breaks).** `RULED (frozen sheet)`
> "the Fall Line's wreckage is **fresh** — 'Nothing here is old' — renewable, Empire-claimed salvage rights." — `infrastructure/state/items/PLAYER_START_SITE_1.md` citing `design/Jawa/worldbuilding/fall_line.md` (FROZEN). Purpose: the salvage economy's deposition belt; V3 sits on the Empire's Ashgarrison chokepoint (`dungeons_arc_spec.md` §3.2).

**G28 — the Scald's dark tower.** `RULED (nature); dungeon owed`
> "The dark tower in the crater lake — the Rakatan ground-based high command, and the Scald's engineered geometry with it." — `design/Jawa/worldbuilding/rakatan_legacy_index.md` row 4 (`SCALD_DARK_TOWER_1`). Campaign-beat purpose: `GAP` (no source ties it into the spine order).

**G29 — the Helix settlements (renamed 2026-09-12).** `RULED (WORLD_NAME_FIXES_1)`
> Site Aurek (was Specimen Hall) · Farside Station (was The Revision) · Site Cresh (was The Fair Copy) · Cold Stores (was Cold Archive, tile 17901). — `infrastructure/state/items/WORLD_NAME_FIXES_1.md`. Bridge rename pass NOT yet run (item open); purpose: the Helix's faction ground (04_factions §9); V4 sits 15° from Site Aurek (`dungeons_arc_spec.md` §3.2, pre-rename name).

**G30 — the Free Droid Enclaves' holy city.** `RULED (frozen sheet)`
> "eight of twelve seats (*Cell Seven, No Master, Vent Forty, Vent Twelve, The Cracking Yard, No Owner, Second Speaker* and kin); only *No Master* kept a road out." — `the_rust_cathedral.md` §8. Purpose: sacrilege economy; the trust chain's first rung (G11); Coldfire + The Cracking Station are "the last waypoint, rumor carriers" to the Assailant complex (`dungeons_arc_spec.md` §2.2).

**G31 — the Geonosian hive.** `RULED (arc beat)`
> "the **Geonosian Alliance** (a protected base for ship/urn tech, until the Empire erases them — `04_factions.md` §8)." — `design/Jawa/reconciled_lore/09_arcs_dungeons_quests.md` §2a

**G32 — the Sump.** `RULED (sheet); campaign purpose GAP`
> "**The stations** — Junker derricks, holding ponds, barrel yards, wick-gardens …" — `design/Jawa/worldbuilding/biomes/the_sump.md` §8. Fuel redundancy: tar pits are one of the "many paths to fuel" (`01_campaign.md` §Fuel). Spine-beat purpose: `GAP`.

**G33 — the Fever Wood's "Tenant".** `RULED (2026-09-07, ratified per README_BIOME_GRAMMAR.md row)`
> "**The Tenant**" is the deep thing's internal working name" … "## F1. The Tenant — one aquifer, one entity, never seen (§4, §6.1)" — `design/Jawa/worldbuilding/biomes/kits/fever_wood_kit_spec.md` (lines 9, 44). The biome SHEET carries no "Tenant" (its §8 names Sporefall); the KIT spec is the Tenant's home. Doubt resolved 2026-09-12 (BENCH follow-up, direct read of the kit spec). Campaign-beat purpose beyond the kit: `GAP`.

**G34 — the Miasma's warden-mothers.** `RULED (sheet); campaign purpose GAP`
> "**The warden mothers.** The adults that stay: brine-broken elders too old …" and "its mother is the reason ships sink." — `design/Jawa/worldbuilding/biomes/the_miasma.md`. Spine-beat purpose: `GAP`.

**G35 — the Deeps (three seas).** `DRAFTED (concept + v1 build spec); campaign wiring GAP`
> "**Because the map already paid for it.** Three seas were hand-authored into a fixed world and currently hold nothing. This mod is the reason they exist." — `design/Jawa/worldbuilding/depths_concept.md` §8. Purposes stated there: sunken colonization-age fleet salvage, leviathan materials, sea-floor quest vaults, Oomo's pilgrimage, the bolt-hole "the one refuge orbital power cannot audit." v1 slice: `RM_Seafloor_WreckField` (`depths_build_spec_v1.md`). No spine beat cites the Deeps: `GAP`.

**G36 — the island, tile 5873.** `RULED (2026-09-08 review sitting)`
> "ruled a place, not an accident: the reading is the lab's access standing above the fuel. Landmark + name owed at build." — `the_propane_lakes.md` §8

**G37 — Hutt sites.** `RULED (roster)`
¶ Zeddo's Toll (tile 17006), Gorga the Immense's Palace (tile 3638), Hurgo's Kennels (21230) — `PLAYER_START_SITE_1.md` candidates section. Purpose beyond the start/ledger pressure: `GAP` per-site.

**G38 — the Contagion + its observation posts.** `RULED (sheet + ashfall doc)`
> "The Contagion now paints **24 Ashfall Range tiles** among its 179; the base sits on one of them." — `ashfall_research_base.md` §3. The "Ocular" of `OCULAR_OVERDRIVE_SITE_1` IS this site (item renamed by the biome flip — `ashfall_research_base.md` header).

---

## 3. Mentioned-but-unused threads

**G40 — orbital towers / sky ladder → repulsor spires (v2, all of it).** `SUPERSEDED-BY the 2026-09-02 sheet ruling; v2`
> Original: "The space towers were owned by the Galactic Empire — how they land and access the surface — so they get VERY angry about it. And that's the whole point the Hutts were after." — `design/Jawa/worldbuilding/orbital_towers_and_the_sky_ladder.md` (banner: SUPERSEDED, premise replaced by repulsorlift spires).
> Successor: "these are going to have to be very high altitude stations with a tapering tower beneath them, Bespin style technology using repulsorlifts. This one should likely actually be over the Rust Cathedral, an old research station turned into a cargo redistribution center … Each one has a ship handed upon it with weapons capable of shooting anyone leaving the planet or approaching." — `design/Jawa/proposals/skyhook_deep_design.md` (RULED name "Repulsor Spires"; "Everything here is **v2** — no spire content ships in v1"; 6 of 9 sheet rows CUT, crash-salvage kept as v2).
¶ Nothing on the map or in an active mod points at a spire today; the Space Tower mod (`hailuan.spacetower`) is "the only absent piece" per `design/V2_DREAMS.md` (v2 parking).

**G41 — the asteroid belt.** `MENTIONED-UNUSED`
> "brought metal down from the asteroids" and "the Forsakens' asteroid-fed factory complexes, ground to a rusty halt" — `design/Jawa/reconciled_lore/03_deep_history.md`. These are the only mechanism-bearing mentions (the sitting brief says so too). No map object, no mod, no beat: `GAP` — it exists as the Cathedral's origin story only.

**G42 — orbital platforms / floating station(s).** `MENTIONED-UNUSED`
¶ Odyssey's own orbital sites exist as engine content (`OpportunitySite_Satellite`, noted in a def census — `design/V2_DREAMS.md`), and the Empire "watches from orbit" (G1), but no authored campaign object is a floating station in v1; the first spire (G40) is the designed one, v2. `GAP`.

**G43 — moons and moonlight · Force powers · water-bottle currency · carbonite trophies · the five Ortolan siblings · GREAT_NAMESPACE_RENAME.** `MENTIONED-UNUSED (v2 list)`
> "Named v2 mechanics with specs already written: Water bottles as currency … Force powers in their entirety (VPE returns in v2) … moons and moonlight …" — `design/Jawa/reconciled_lore/FUTURE_VECTORS.md`

**G44 — the faction semi-permanent bases seed.** `DRAFTED (seed; its own pass owed)`
> "the faction semi-permanent bases concept (`design/Jawa/faction_semipermanent_bases_seed.md`) wants its own design pass; Antiquities touches it twice (urn sanctum at the Rust Cathedral, the shard-reconstruction compute partnership)." — `design/Jawa/antiquities_design.md` §10

**G45 — the Sarlacc + They! ant nests (living-location dungeons).** `RULED v2`
> "v2 gravity wells: **the Sarlacc** (Anomaly pit-gate rebrand — confirmed buildable, v1 does not attempt it) and the **They! giant-ant nests** … ⚠️ their faction must be ticked at world creation or v2 ants need a new world." — `design/Jawa/reconciled_lore/09_arcs_dungeons_quests.md` §Dungeons

**G46 — ship-footprint concern (very large maps / off-ship storage).** `MENTIONED-UNUSED (flag, no ruling)`
> "the owner flags the gravship may be too big for standard maps; very large maps or off-ship storage (the bases) are the two compensators named so far." — `design/Jawa/antiquities_design.md` §10

---

## 4. Reveal moments — in the order the player could hit them

**G50 — the ladder orders the reveals.** `RULED (2026-09-04 antiquities; 2026-09-12 Ashfall gating)`
> LANGUAGE: "ancient sites get true-name labels" · RELIGION: "Shrine sites revealed on the world map" · CULTURE: "War children become *identifiable*" · CARTOGRAPHY: "Vault sites revealed … each with its *access phrase*" · VOICE: "how to *address* an ancient. Enables the Call-Out." — `design/Jawa/antiquities_design.md` §3.
> "**Reveal gating — RULED: encrypted, the antiquities literacy ladder unlocks.** … so the truth lands in ladder order and can never front-run the Reclamation or the flesh dungeon." — `ashfall_research_base.md` §6

**G51 — the register guard (the one hard ordering law).** `RULED (canon.yml rakata.victims_and_tyrants)`
> "the Rakata tyranny surfaces at the Assailant flesh dungeon, nowhere earlier." — `ashfall_research_base.md` §5; same law in `dungeons_arc_spec.md` §1.

**G52 — the reversal staged INTO the urn corpus.** `RULED (reintegration plan ruled 2026-09-04)`
> "**CULTURE is where the reading turns**: civic registers start rendering as census-of-property — and some of the property has names … By VOICE the player addresses the ancients *knowing both halves* … The flesh dungeon remains the visceral reveal and keeps primacy (the urns corroborate in text what the dungeon shows in meat; whichever the player hits first, the other confirms)." — `design/Jawa/canon_reintegration_plan.md` §B3

**G53 — the Helix–Assailant reveal (the Ashfall datafiles).** `RULED (intent + gating); text owed`
> "how the Helix 'adopted' Rakatan genetics to adopt *themselves* into that family line, in an attempt to control the old technology in the Cathedral — a failure that gave them intelligence and cruelty in equal parts." — `ashfall_research_base.md` §2. Datafile text: owed (§6 "Still owed"). Trigger: seizable any time, readable per G50.

**G54 — the Cathedral reveal (stage 3).** `RULED scope (A2); trigger discipline drafted`
> "The reveal shows SCALE and ALIVENESS; purpose stays in the dark it prefers." — `cathedral_concealment_arc_spec.md` §5, CARD A2 RULED 2026-09-12. Tone: the descent is specified ("halls the size of canyons, a production line a mile long …"). The knowledge-gate exception: the Utinni already knows — "She knows, because she can 'feel' (receive) the Ratakan transponder working on frequencies no longer used" (CARD A1, owner verbatim).

**G55 — V6 WAKE: the woken commander.** `DRAFTED (2026-09-11, owner "good for now" — provisional)`
> "Rakata do not thank tools. Stand aside — report: what year, what front, who holds the sky? … And that hull outside. That is a colonizer ship of the Rakata. What, exactly, is it doing under *your* feet?" — `dungeons_arc_spec.md` §3.10. Opens the ship-claim thread (continuation HELD FOR OWNER, §3.9).

**G56 — the witness at the Assailant core + memory surfacing.** `DRAFTED (2026-09-11, AGREED provisional)`
> "Here are the works of my makers' masters — glyph and girder, first-rank and pitiless — and here is what became of them: swallowed slowly, without malice …" — `dungeons_arc_spec.md` §2.8. "loot recovered here triggers ship memory-surfacings — the dungeon feeds the ship its own past" (canon.yml `assailant_reveal_arc`, quoted there).

**G57 — the Empire urn-hunt + the Shattered Vault + the turn.** `RULED (2026-09-04 beats)`
> "one revealed vault site, visited, is found ALREADY RAIDED … the floor carpeted with **shattered urn shards**. The gut punch is the point. And then the turn: … Gathering ALL the fragments opens a reconstruction job that the clan cannot do alone — it needs the **droids' computing resources, in partnership with the Rust Cathedral**." — `design/Jawa/antiquities_design.md` §8.1

**G58 — the Call-Out and the Testament (VOICE).** `RULED (2026-09-04)`
> "the **Call-Out** at VOICE (called-out ancients stand down and LEAVE — a literate custodian outranks an illiterate heir); the **Testament** (the first Call-Out ends with a fresh urn at the map edge — ambivalent: gratitude without warmth)." — `design/Jawa/reconciled_lore/09_arcs_dungeons_quests.md` §2a

**G59 — the crater event (planet-wide, unmissable).** `RULED (2026-09-12 amendment)` — see G9. What the cut-scene SHOWS and its text: `GAP` (build rides `ANCIENT_WAR_LAB_1`).

**G60 — the Reclamation's two after-scenes.** `RULED (2026-09-04, verbatim)`
> the Helix's true heart: "If you will not share your wisdom and power, then I will learn from what destroyed you" · the Rakatans refused by the Rust Cathedral: "I am bound to an Empire that no longer reigns, not their mongrel offspring who managed to lose the war that broke me." — `design/Jawa/reconciled_lore/09_arcs_dungeons_quests.md` §2b

**G61 — the Archon-name tell.** `RULED (2026-09-12)`
> "in-fiction Rakatan text (datafiles, ship systems, the Utinni's transponder band) says Archon; everyone alive says the Rust Cathedral; and the mind's dislike of the placename is a usable tell." — `the_rust_cathedral.md` §1 amendment

**G62 — reveal moments with no specified trigger/place/tone.** `GAP list`
- What the war lab reveals inside (fact + tone): `GAP` (G16, G22).
- The Spire's codes seizure as a MOMENT (fact ruled; trigger = dungeon core; tone): `TONE: GAP`.
- How the player learns the crater event opened something (the lab "revealed by the melting event" — presentation beyond the cut-scene: `GAP`).
- The Narrator's lore-reveal channel exists (canon.yml `narrator` — "free to reference history the player has not yet learned"), but which spine beats get narrator reveals is unstated: `GAP`.

---

## 5. Transitions — the tone/experience each is supposed to have

**G70 — the flood witness (Cracked Lands).** `RULED (design 2026-09-10; restructured 2026-09-12)`
> "the flood mostly won't happen while the player is in the canyons, so the plot organizes an event where they witness it at least once." · Ruled: "lethality has an injury+knockdown ceiling (no outright deaths), and the witness route is the declinable Moisture Farmer INVITATION with a re-offering scheduler." — `infrastructure/state/items/FLOOD_WITNESS_EVENT_1.md`. Tone: "disaster and fertilizer; death, then soil, then the bloom."

**G71 — the crater event.** `RULED` — "no one will miss it. We will effectively have a 'cut scene.' It's big enough that everyone on the planet will notice in some way." (G9). Experience beyond scale: `TONE: GAP`.

**G72 — the Reclamation.** `RULED` — "a price the player should see coming" (G12). The Helix flip ends the boon economy; the two after-scenes (G60) carry the exit tone.

**G73 — the Testament.** `RULED` — "ambivalent: gratitude without warmth" (G58).

**G74 — V6 and the vault rings.** `DRAFTED (provisional, owner "good for now")` — the ring letters and V6 arrival/casket-hall/WAKE/LOOT/LEAVE units, all under the three-voice law — `dungeons_arc_spec.md` §3.10.

**G75 — the embargo resolution.** `RULED (T2)` — two ends, both authored (G13). The gun-runner register: "arming the local resistance buys them time, never victory — no uprising, no Rebellion, no liberation event" — `tibanna_embargo_plot_spec.md` §6.6.

**G76 — Cathedral exposure completing.** `RULED (A3)`
> "challenged, probed, and forced to defend itself or self destruct... a losing battle" (§GM register, quoted in `cathedral_concealment_arc_spec.md` §6.1); "full Imperial discovery is buildable and ends the relationship in the §GM catastrophe register." — CARD A3.

**G77 — transitions with TONE: GAP.**
- First launch (getting it off the ground achieved): `TONE: GAP` — no source states the moment's experience.
- Entering the war lab (post-crater, codes in hand): `TONE: GAP`.
- Antiquities stage completions: theology register stated ("Rekko-tagged, pride-neutral — reading what was always written is restoration, not transcendence" — `antiquities_design.md` §3) but no per-stage MOMENT authored: `GAP`.
- The droid-theft heist's payoff and the succession clock's crisis: no authored tone found this pass: `TONE: GAP` (`STATUS-DOUBT` — deeper sources may exist in `08_droids.md` / `05_the_clan.md`, not deep-read this pass).

---

## 6. Contradictions — listed, sourced, NOT resolved

**G80 — the Spire prep's four shapes vs the Key ruling.** `SUPERSEDED-BY ashfall §6 (2026-09-12, commit 919d5c155); still on disk`
> `design/Jawa/spire_plot_discussion_prep.md` header still says: "He ruled 2026-09-12 … function NOT ruled, deliberately — 'Not ready to resolve this yet, need a whole plot discussion first (TBD)'" and offers four candidate shapes (Third Clock / Archive Heist / Cathedral's Errand / Standing Wound) — while `ashfall_research_base.md` §6 now carries "Campaign function — RULED at the plot sitting, 2026-09-12. The Base is THE KEY." Delete-don't-supersede has not yet been applied to the prep doc.

**G81 — pre-rename place names across the corpus.** `CONTRADICTED-BY infrastructure/state/items/WORLD_NAME_FIXES_1.md (RULED renames, bridge pass + doc fix not yet run)`
¶ Files still carrying an old name (Specimen Hall / Fall Line Barrens / The Revision / Fair Copy / Cold Archive / Scald Spine), found by grep this pass: `world_rename_proposals.md` (the proposals doc itself, fine), `ASHKARR_WORLD_DEFINITION.md`, `contagion_placement_candidates.md`, `dungeons_arc_spec.md` (V4 row: "Specimen Hall"), `vapor_emitter_inventory.md`, `vapor_emitter_review_2026-09-12.md`, `vault_siting_prep.md`, `worldgen_interactive_def.md`, `biomes/the_contagion.md`, `biomes/the_greentide.md`, `biomes/_freeze_rulings_2026-09-07.md`, `biomes/weeping_stones.md`, plus `PLAYER_START_SITE_1.md` ("Fall Line Barrens"). The renames are ruled; the propagation is the open half of WORLD_NAME_FIXES_1.

**G82 — the seed document's ending vs open-ended victory.** `SUPERSEDED-BY the victory ruling (owner 2026-08-30, 01_campaign.md §Victory)`
> Seed: "End with a major destination, mechhive confrontation, or other final objective rather than indefinite wandering." — `design/Jawa/worldbuilding/Gravship_Campaign_Planning_Discussion_2026-08-02.md` §3. Still on disk as historical conversation (doc is the SEED record; no banner).

**G83 — victory open-ended vs the god-mapped win paths.** `RESOLVED ON PAPER — flag only`
¶ `09_arcs` §7 lists three win paths with no version marker; `01_campaign.md` §Victory says "authored endings (the god-map roads) are v2." Not a live contradiction, but a reader of 09_arcs alone would ship v1 endings. Cite both on any Phase B card touching endings.

**G84 — three canon layers at three speeds.** `CONTRADICTED-BY itself (structural)`
> "the campaign now has THREE canon layers moving at three speeds — canon.yml (days), reconciled_lore (frozen 2026-08-29), and the design docs (hours) — and the newest rulings live only in the fastest layer." — `design/Jawa/canon_reintegration_plan.md` §A. ¶ Verified still true this pass: `01_campaign.md`/`09_arcs` know nothing of the Spire-Key, Archon, T2, A1–A5 (all 2026-09-12). CANON_DRAIN_1 is the scheduled fix; the sitting's output (CAMPAIGN_ARC.md) must not fork a FOURTH layer — storage per `design/CANON_STORAGE_ARCHITECTURE_options.md` Phase 0+1 (certainty tiers + claim index, ADOPTED 2026-09-12).

**G85 — the concealment spec's asymptotic-v1 line.** `SUPERSEDED-BY CARD A3 — propagation claimed done, verify`
¶ CARD A3's text says "SUPERSEDES this spec's own asymptotic-v1 assumption everywhere it appears (§6.1 amended in the same change)". §6.1 as read this pass does carry the A3 ruling. Residual check for Phase B: no other doc found this pass still asserts exposure-cannot-complete; `STATUS-DOUBT` only for docs not deep-read (kyber spec).

**G86 — ECONOMY_TRADE_SWEEP_1 exists in the ledger; its item FILE is missing.** `RULED (2026-09-10, ledger event, owner-said)`
> "having them show up in trader inventories or as loot is very fun. It should be expensive indeed. Please make a ticket now to do a full economic sweep or what is sold where and when at the end of the world sweeps." — `infrastructure/state/ledger/events.jsonl` (OWNER file event, 2026-09-10T07:45:43Z, caused_by CRYSTAL_MODS_INGEST_1, for BENCH). No `items/ECONOMY_TRADE_SWEEP_1.md` exists — the known missing-file failure mode (`rimflow-item-files-live-under-state-items` memory), not a phantom item. Doubt resolved 2026-09-12 (BENCH follow-up). Owed: write the item file.

**G87 — "campaign function TBD" docs ruled since.** `RESOLVED (sweep run 2026-09-12, BENCH follow-up)`
¶ Corpus-wide grep of `design/Jawa/**/*.md` for TBD / "not ruled" / "not yet ruled": ONE today-ruled contradiction found — `spire_plot_discussion_prep.md:6-7` ("function NOT ruled, deliberately … (TBD)"), which is exactly G80. Every other hit (pawn_flavor ceilings, research_tree roster, setup_checklist storage ratio, arid_shrubland candidates, the_forgotten_war numbers, required_mods build notes) is a genuinely still-open TBD, not stale against a ruling.

---

## STATUS-DOUBT ledger (two-blind-arms these before any SUPERSEDED verdict)

- ~~G33~~ — RESOLVED 2026-09-12: the Tenant is ruled, home = `biomes/kits/fever_wood_kit_spec.md` §F1.
- **G77 (partial)** — heist/succession tone: `08_droids.md`, `05_the_clan.md` not deep-read this pass.
- **G85** — kyber spec not re-read for surviving asymptotic-exposure language.
- ~~G86~~ — RESOLVED 2026-09-12: real ledger item (owner, 2026-09-10); only its item file is missing.
- ~~G87~~ — RESOLVED 2026-09-12: sweep run; sole today-ruled hit is G80.
