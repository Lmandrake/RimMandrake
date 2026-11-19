# The Scald: what the rewrite chose, what it lost, and why

Companion to `design/concepts/TerminalBiomes/TheScald_design.md`, written 2026-11-18 by the same run. Its job is
to let the Scald's older files be deleted without fear: every distinct idea found in any source has a row saying
what became of it. Nothing has been deleted. The older files this design replaces are listed at the end.

**Why this page exists beside the combined one.** The same day's combined four-sea pass
(`design/concepts/TerminalBiomes/design.md` and `rewrite_choices.md`) said of itself that it was thinner than its
sources and not safe to delete on. For the Scald it had read the floor specification, the flora pass, the kit and
the steam specification by heading only, and had not opened the roster or the owner's card answers of
2026-11-10. This run read those to the end. What that changed is the next section.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge
ship on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply
be missed"*; the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the overriding
priority"*. The Scald needed almost no bending. Its floor was designed from the first for a party that comes down,
works and leaves, and on 2026-11-10 he answered three cards about it that describe a stop outright. Whose word
wins where sources disagree: his latest dated words; then a locked Designer sheet (the Scald has none); then the
cleanse of 2026-11-17, each line of which was checked against his answers dated before it.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed,
from and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and
this design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in 0.2.0 is listed under
Scope moves once and its row says only "0.2.0"); *folded into shared machinery*; *lost*. Where a lost, moved or
reshaped row leaves its last two cells empty, the reason is one already given in "The ones I would look at" or
"Scope moves".

## What reading in full changed, against the combined design

1. **His three card answers of 2026-11-10 are now the frame.** *"A thriving world inside the heat"*; *"Prepared
   crews finish a short job"*; *"A useful working visit... before withdrawing when cooling or supplies become
   inadequate."* The combined design did not have them. Neither did the cleanse, six days after he gave them.
2. **A whole floor he typed on 2026-09-25 had dropped out of sight.** The Mighty Vu'uul, the ullium swirl, the
   askirath guardians, the feen swarms, chimney fields in three heat zones, ore as nodules *"you simply gather"*,
   Mother-of-Scaldpearl, ancient machines on every floor, and the mineral-crusted Rakatan vessel in one hex.
   None of those four creature names appears anywhere in `src/` or in any later document (measured by search).
   The combined design carried one line of it. It is all in this design, almost all at 0.2.0.
3. **The elder sando is not the Scald's.** The combined design gave the Scald *"one to a sea if that, the elder
   sando."* On 2026-10-05 he moved both sandos to the Twilight Sea (*"it does not belong in the Scald"*) and
   renamed the elder the Gripping Terror. Source agrees: the Scald's roster has no sando.
4. **The floor is not an empty placeholder any more.** The combined design's one dependency was a 2026-10-02
   finding that a ship lands on *"an empty generic floor."* Source now has a Scald floor biome on the ship's
   layer with its own generator: walkable sediment, boiling and cool bands, a vent field, the manifold, a wreck
   field, fauna and plants. What is still owed is the live proof that the ship can fly there.
5. **Most of the 2026-10-02 sitting is built, and the combined design called it "later".** The Walking Pasture
   (with a trample he ruled by card on 2026-10-09), the Sail Forecast, the Immersion Berth and the Return
   Gallery are all in `src/RimMandrake/DivingInteraction/`. The cleanse could not see that folder (*"their
   implementations are not in this checkout"*) and marked the floor "unknown".
6. **The floor is dark.** His card of 2026-09-25 (*"Visibility = light-based only"*) and his typed words of
   2026-09-26 (*"dark on the bottom"*). The combined design had the ship dropping *"into cyan light"*.
7. **Three built creatures have different names on screen** than the documents use: the walker is labelled
   *iridesce*, the muddal *iridai*, the thuum *shimmer eel*. The first is asked under `NEEDS HIM`.
8. **One on-screen moment in the combined design had no source** (*"The ground beside the salvage party gets up.
   It was a bottom-walker's back"*). It is not carried over. The karrash's line does the same job and is quoted.
9. **Hull wear needed no proposal.** The Scald's is ruled (card, 2026-10-02) and in source. Reading the shield
   rulings in full added two things the combined design lacked: his own description of a thermal veil under
   which *"the temperature slowly climbs anyway"*, and *"nothing 'holds out water'"*.
10. **Who is nearby.** The world definition seats the Compact *"two on the Scald despite the Empire"*, the
    Wildsteam on its jungles, a Helix outpost on its shore, and one of the Empire's three ground holdings at the
    Scald Gate. The combined design had only the two faiths.

## The ones I would look at

1. **The guardians, at 0.2.0.** *"Big leggy things like brittlestars gone wild. They think they're defending the
   Walker."* His typed words, unbuilt, and the best close-range animal encounter this sea has: a threat that is
   wrong about the crew, switches off when the crew steps back, and teaches a radius. I put them at 0.2.0 only
   because every pilot design put unbuilt creatures there. If one thing comes forward into 0.1.0, it is this
   (one creature, one think node, three sprites).
2. **The steam clock, moved into 0.1.0 against the cleanse.** The cleanse switched it off, reading the one-sun
   ruling as forbidding it. But he asked for steam *"deadly without protective gear"*, folded its protection into
   ordinary heat armour by card, and tuned the rind coat against it on 2026-11-06, after the one-sun ruling. I
   took his later card. It is `NEEDS HIM` 2, and reverting is one scope line and one promise row.
3. **Nodules, at 0.2.0.** *"Ore is NODULES you simply gather"*: lumps of gold on a sea floor, for a crew that has
   never mined and always scavenged. Under his "very Jawa" test nothing here scores higher, and it is cheap
   (items, a scatter, six sprites). It could come forward.
4. **The Return Gallery, at 0.2.0 though it is built.** A Jawa with a gauge reading a pipe older than the
   Republic is the right picture, and it was his card (*"Both at once"*). I held it back to keep 0.1.0's list
   provable; the mechanics review of 2026-10-22 had it at "ask". What its locker actually pays out I did not
   verify in source.
5. **The Rakatan vessel.** *"I love the idea of a crashed ancient Rakatan vessel, encrusted in minerals, with a
   few goodies still left."* A turret for the hull, batteries, a shield emitter, an archive: salvage for the
   ship itself, once per world. It is 0.2.0 and campaign layer here because it is a whole unbuilt mod with its
   own sitting owed. Nobody had mentioned it since September.
6. **The two-faith shore.** *"The margins hurt and heal simultaneously, and both faiths claim it as proof of
   their own reading... two churches, one shore, no concession."* Campaign layer and rites, one line in the
   design. The most beautiful thing in the sheet that a stop does not show.
7. **"The planet's water purification runs through the weapon: the Contagion is the filter stage of the
   distillery. Nobody planned it. It works anyway."** World lore, lost from a design about a stop. It belongs in
   a world document and should not be deleted with the sheet.
8. **The rivers.** The sources disagree on whether rivers leave the Scald, and both sides are his words
   (`NEEDS HIM` 4). The cleanse picked "terminal" from the amended world definition without weighing his typed
   *"the rivers flow OUT of the Scald... and you know this!"* of 2026-09-12 or his line of 2026-10-20.
9. **The dive clock, at 0.2.0.** His two-axis gear ruling is typed and detailed, and none of it is built. In
   0.1.0 a crew member outside the hull pays for heat and pools only; nothing represents breath. That is honest
   to what exists, and a player may find it odd.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17 (or against the combined
design, where said). Revert by moving the line in the design's Scope section.

- **Steam exposure clock and its clothing:** next version → 0.1.0, on the beach. See above.
- **Immersion Berth:** not in the cleanse census → 0.1.0. His card of 2026-10-02 and his hull ruling of
  2026-11-18. (The combined design made the same move.)
- **The herd's grazing, the following job and the trample:** not in the cleanse census (it saw the walker only
  as a roster animal) → 0.1.0. Combined design: "later" → 0.1.0.
- **The vent cycle and the sails' gathering:** the cleanse deferred "staged bubble-sail appearances" → the
  forecast is 0.1.0 (his answer of 2026-11-10 is about exactly this); the beach's sail scatter stays 0.2.0.
  Combined design: "later" → 0.1.0.
- **Cool ring on the floor:** the cleanse ruled the margin beach-only → kept on the floor as built (it is where
  the build put the floor's fishable water and it gives the bathing thought at the ship). Marked in the design
  as the build's choice.
- **Cleanse's new floor substrate ticket:** kept as a build question, not a scope item. Source already lays
  walkable sediment as the base; whether pools should sit only at vents is the ticket's remaining point.
- **Steam-catch and distilled water; steam devils; vent flashes; walker sighting; sail scatter; sponge on
  wrecks:** next version → 0.2.0.
- **Return Gallery:** not in the cleanse census → 0.2.0. Combined design: "later" → 0.2.0.
- **His 2026-09-25 floor (zones, guardians, swarms, swirl, nodules, pearl, machines, vessel, layers):** in no
  census → 0.2.0.
- **Dive clock and local dive gear:** in no census → 0.2.0.
- **Sando passage:** dropped (his move of 2026-10-05).
- **Forty colonists on a floor and the whole-sea season model:** first version → later (as the combined design).
- **New, not in any source:** stating cover from orbit for the two places; the still-day question; reading the
  Cathedral's hidden heat as support for the cover; reading stolen steam-water as the crew's trade good; the
  Empire's Scald Gate set beside the pursuit; the open question of how the Empire reaches a floor.

## Every idea, row by row

Source names. In `design/Jawa/worldbuilding/biomes/`: *sheet* = `the_scald.md`; *agenda* =
`the_scald_floor_sitting_agenda_2026-10-02.md`; *consult* = `the_scald_floor_gpt_consult_2026-10-02.md`; *bath
rite* = `the_scald_margin_bath_rite_2026-10-03.md`; *flora pass* = `the_scald_underwater_flora_pass_2026-09-27.md`;
*kit* = `kits/scald_kit_spec.md`; *roster* = `rosters/the_scald.json`; *cast proposal* =
`terminal_seas_cast_proposal_2026-09-25.md`; *history draft* =
`the_rust_cathedral_SCALD_HISTORY_amendment_draft.md`; *twilight danger* =
`the_twilight_deep_danger_pass_2026-09-27.md`. In `design/RimMandrake/`: *steam spec* =
`scald_steam_and_hazards_spec.md`; *dive spec* = `sea_dive_maps_spec.md`; *gear matrix* =
`exposure_gear_matrix_spec.md`; *answers* = `designer_codex_2026-11-09/TheScaldFloor/ANSWERS_OWNER.md`; *mechanics
review* = `special_mechanics_review_2026-10-22.md`; *floor census* = `sea_floor_census_2026-10-29.md`;
*experiences* = `biome_experiences_2026-10-20.md`; *liquid types* = `RM_liquid_types_mod.md`; *deepfire spec* =
`deepfire_luminous_pigment_spec.md`; *sun design* = `unified_direct_sun_heat_2026-10-19.md`; *minerals design* =
`minerals_where_they_belong_design_2026-10-02.md`; *wreckage design* =
`salvage_wreckage_everywhere_design_2026-10-02.md`; *surface removal* = `sea_surface_removal_2026-11-01.md`;
*rulings* = `biome_rulings.md`. Elsewhere in `design/`: *cleanse* = `design/concepts/TerminalBiomes/cleanse/`;
*combined design* = `design/concepts/TerminalBiomes/design.md` and `rewrite_choices.md`; *walk* =
`design/validation_walks/RimMandrake/TerminalBiomes.md`; *catch rosters* =
`design/Jawa/worldbuilding/sea_catch_rosters_2026-09-24.md`; *world definition* =
`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md`; *shield design* =
`design/Jawa/proposals/ship_shields_deep_design.md`; *campaign* = `design/Jawa/campaign/CAMPAIGN_ARC_GATHER.md` and
`design/Jawa/reconciled_lore/01_campaign.md`; *boiling-lift spec* = `design/Jawa/mods/REGROWTH_BOILING_LIFT_SPEC.md`.
In `infrastructure/state/items/`: *mechanics item* = `SCALD_MECHANICS_1.md`; *small items* = the Scald's other
item files, named in the row; *sea items* = `SEA_FLOOR_AND_CATCH_PASS_1.md`, `SEABED_DESCENT_ASCENT_1.md`,
`closed/HAZARD_NATIVE_TAG_1.md`, `closed/TERMINALBIOMES_RM_MOD_BUILD_1.md`. *ledger* = his words and cards as
recorded on ledger events, read with `src/RimMandrake/rimflow/owner_rulings.py --grep`. *source* = `src/`,
read only for what exists and for the comments that quote his cards.

### The place and its law

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The kettle at the centre of the world: every river starts here, boiling. Life here is cooked and proud of it." | experiences; walk | kept, quoted, first | His line, by card 2026-10-20. | |
| "A crater sea that boils... a place of roiling wonder" | sheet §1 | kept, quoted | | |
| "A sea of fire's making, fouled at heart, whose clean breath waters the world" | sheet header | kept as the reason the water is never drink | | |
| Two places only: the beach and the sea floor; nothing "on" the boil | ledger (2026-11-01); sheet ban 4; surface removal | kept, quoted; the design is written for both | | |
| Ship or nothing; the ship flies to its own layer; the hatch is a leftover | rulings; dive spec; sea items | kept, quoted | | |
| Three seas are three biomes; nothing shared with the Twilight or the Grey | sheet; roster | kept as a build fact | | |
| The terminator seas' law (one giant, no schools) does not bind the Scald; herds are legal | roster; cast proposal | kept | | |
| Fouled heart, clean breath; the water chain through the Contagion, "Nobody planned it. It works anyway." | sheet §3 | lost; flagged above | World lore. | A world document. |
| Volcanic heat keeps it boiling; "the sun merely helps" | sheet §3 | kept as one clause | | |
| Eight rivers in, none out; a terminal pan | sheet §0, §3; world definition; cleanse ambiguity 3 | kept, reshaped: stated as an open disagreement | His typed words of 2026-09-12 say the opposite. | `NEEDS HIM` 4. |
| "The rivers flow OUT of the Scald... and you know this!"; freshwater bucket | liquid types (card 1, 2026-09-12); roster; kit | kept as the other side of the same question | | |
| Renumbering river distance so the Scald end is the source | small items (`SCALD_RIVER_REPAINT_1`) | lost | World painting; nothing a stop shows. | |
| Tile count, crater centre, arc, measured depth and temperatures | sheet §0; world definition | lost | The planet is painted at the end. | |
| Placement: the Scald stays where it was, at about arc 35; fix the sheet and the temperature | ledger (2026-10-23) | kept as a fact behind "high sun on the beach" | | |
| The Scald's mutator layers: the Boil, the Nine Mouths, the Brine Ladder, the dead heart | world definition §13.5 | lost | World authoring on the frozen map. | |
| "Hypersaline basin"; life only at the river mouths | world definition §13.5 | lost | Superseded by the sheet's thriving floor and his answer of 2026-11-10. | |
| Never potable; "fouled, not toxic" | sheet ban 1; kit; cleanse | kept, quoted | | |
| The drink tag removed from the boil and moved to the margin | mechanics item; kit | kept as build history; the cleanse's "margin is not drink either" is kept | The later reading wins and matches the ban. | |
| No boiling-immune traversal for free; gear never reaches zero | sheet ban 3; steam spec | kept | | |
| No native land predator hunts the water | sheet ban 3 | kept, quoted; it is why 0.1.0 has no hunter | | |
| "No macro-life in the boil" and its withdrawal | sheet ban 4; ledger (2026-11-01); kit; catch rosters | kept as withdrawn | | |
| No drained, cooled or tamed Scald; the still day is "a pause in the breath, never in the boil" | sheet ban 5; steam spec | kept, quoted | | |
| No vanilla-Earth flora or fauna | sheet ban 6 | kept | | |
| The admission test: "thrives in heat that kills everything else, and joins the dung-and-mat economy" | sheet §4 | kept as the rule behind the cast | | |
| "The mats coat, the walkers mow, the dung feeds, the silver darts, the sails ride: one economy, wholly submerged" | sheet §5 | kept, quoted | | |
| "A thriving world inside the heat... wonder and understanding the herds worthwhile beyond extraction" | answers | kept, quoted, as the frame | His card, 2026-11-10. | |
| "A useful working visit... withdrawing when cooling or supplies become inadequate" | answers | kept, quoted; it sets what ends a stop | | |
| A sea visit: arrival, safe edge, temptation, bad choice, recovery | cleanse definition | kept as the shape of the first day | | |
| One signature for the whole mod (the Twilight's current); the Scald gets land and life only | cleanse owner pages | kept, reshaped: the Scald has its own 0.1.0 (herd, vents, the warm ship) | His hull ruling and his 2026-11-10 answers. | The cleanse's way: a Scald that is scenery in its first version. |
| "Cyan glow under white steam — the sea that is also a forge" | sheet §9 | kept, quoted, for the beach | | |
| Art direction: light, palette, silhouettes, motion, sound | sheet §9 | kept as art direction | | |
| "A bottom-walker's back breaking the surface at the deep center, rare and enormous" | sheet §9; kit S5 | kept, reshaped: seen from the beach at the deep-water edge | His card of 2026-11-01. | |
| The floor is dark; visibility is light-based only | dive spec §7a-13, §8.5; twilight danger (his words, 2026-09-26) | kept in 0.1.0; whether built is unmeasured | | |
| Light draws things on a dark floor: redirected from the Twilight to the Grey and the Scald | twilight danger | moved (no bucket → 0.2.0); no design exists yet | His typed redirect. | |
| Steam belongs to the beach map; the floor stays calm | ledger (card, 2026-10-23); mechanics item; cleanse | kept | | |
| Bubbles as the floor's weather | ledger (2026-11-01) | kept in 0.2.0 as filed, unwritten | | |
| The four experience lines of the four seas | experiences; combined design | kept (the Scald's) | | |

### The floor: ground, vents and heat

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| At depth "the boil gentles to mere heat" | sheet §4; consult | kept, quoted | | |
| The floor as it is in source: walkable sediment, a boiling band, a cool margin band, 55 °C | mechanics item (2026-10-22); kit S3 | kept as 0.1.0's ground | Found in source, not in the cleanse. | |
| A new hot mineral substrate, with boiling pools only beside vents and a pool-free way from the hull | cleanse (ticket T49, bar B4, rule R6) | kept, reshaped: the walkable ground exists; pools at vents and the clear route are kept as the promise | | |
| The margin is beach-only | cleanse ambiguity 5 | lost; the built floor ring stays | See Scope moves. | Beach-only: the floor loses its bathing ring and its fishable water. |
| The whole floor burning a worker without end is a failure | cleanse review | kept as a control in the promises | | |
| The old hatch pocket map and its hot-spring patches | agenda §1.4; dive spec §2 | lost | The hatch is a leftover. | |
| The floor found empty on 2026-10-02 | agenda; combined design | lost as a present fact; the live proof it asked for is still owed | Source has moved on. | |
| Three heat zones painted as terrain: plain, chimney field, core | dive spec §8.1 | moved (no bucket → 0.2.0) | Unbuilt; his card ("heat as zones"). | |
| Chimney fields: "large fields of boiling cloudy water, rich in life and ore, at temperatures that threaten even protected divers" | dive spec §7a-10 | moved (→ 0.2.0); the built vent fields are their first form | His typed words. | |
| Chimneys as lit smoker columns | dive spec §8.1 | moved (→ 0.2.0) | | |
| The heat gate is soft: zones burn, gear decides how long you last, no wall | dive spec §7b-17 | kept as a rule for the 0.2.0 zones | | |
| Vent fields generated on the floor | agenda ruling 3; mechanics item | kept in 0.1.0 | In source. | |
| The Sail Forecast: sails gather over a vent before it goes | consult idea 2; agenda ruling 3; answers | kept in 0.1.0, quoted | His answer of 2026-11-10 is about it. | |
| A discharge "pushes loose objects" | consult | lost for now (not built: damage and interruption only) | | Build it: small; it would show the event on cargo. |
| "Decide whether the forecast is needed beyond a letter" | mechanics review S3 | lost | His answer of 2026-11-10 settles it: the learning is the point. | |
| Vents go off near a parked ship | agenda decision 3 | kept as an `UNSETTLED` note on landing sites | | |
| Geysers on the shore; "the vapor law's second densest ground" | sheet §8; kit S4 | kept at the beach | | |
| The geyser mutator applied before a map exists | kit S4; mechanics item | lost | World authoring detail. | |
| Marine snow; the shimmer band at a field's edge | dive spec §7b-22, §8.5 | moved (→ 0.2.0) | | |
| The floor persists between visits; floors are 100 by 100 | dive spec §7 | kept as build facts | | |
| Nodule regrowth out of sight between visits | dive spec §8.3 | kept with the nodules, 0.2.0 | | |
| "No raids" on the floor (a pocket-map fact) | dive spec §1 | lost as a claim | The floor is no longer a pocket map; what the Empire does is `NEEDS HIM` 1. | |
| What happens to a party if the ship leaves; whether a ship can hold station over a sea | dive spec §1 | kept as unmeasured | | |

### The floor: the herd

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Bottom-walkers: "armored, slow, pastoral", herds mowing the mats | sheet §4 | kept, quoted | | |
| "Their feces are the food" | sheet §4 | kept as the economy's line | | |
| The centrepiece: huge, sea-urchin-like, very alien, living off temperature gradients; they never attack | dive spec §7a-7 | kept, quoted | His typed words. | |
| "The Mighty Vu'uul" | dive spec §7b-16; ledger (2026-09-25); deepfire spec | kept in the prose; `NEEDS HIM` 3 | Source labels it iridesce. | |
| The built walker, labelled iridesce: "a hundred short thick legs... has somewhere to be" | small items (`SCALD_SHEET_REDOS_1`); floor census | kept, quoted | | |
| Walkers PRODUCE the mats as they pass; the trail is the mat source | dive spec §7a-7, §8.2; deepfire spec | moved (no bucket → 0.2.0); the built herd mows | Both are his; mowing is what exists. | Laying only: mats appear behind herds and nowhere else; a rebuild of the built grazing. |
| Walkers graze the boundary of a heat field | dive spec §8.1 | moved with the zones (→ 0.2.0) | | |
| The walker as a message only; as a surfacing incident | kit S5; agenda §1.3 | lost | Superseded by the pawn. | |
| The Walking Pasture: a plain herd first, then the crew follows it to harvest what grazing exposes | consult idea 1; agenda ruling 1 | kept in 0.1.0 | In source; his card. | |
| A walker too close "tramples the colonist and deals damage (not push-aside)", with a warning | source (the trample kernel's header, quoting his card of 2026-10-09) | kept in 0.1.0, quoted | | |
| "Swept aside by an animal that scarcely notices people" | consult | lost | Replaced by his trample card. | |
| A grazing walker is safe to work beside; back off when two lanes converge | consult; source headers | kept | | |
| The walker surfacing as a beach sighting, with a real pawn at the deep-water edge that leaves unless harassed | ledger (card, 2026-11-01); mechanics item | moved (cleanse next version → 0.2.0) | The pawn is unbuilt. | |
| The ullium: a glowing swirl that follows a herd and lights it | dive spec §7b-16, §8.2 | moved (→ 0.2.0) | His name. | |
| The askirath: guardians that "think they're defending the Walker" | dive spec §7a-8, §8.2 | moved (→ 0.2.0); flagged above | | 0.1.0: one creature and its art. |
| The feen: scalding swarms that defend a chimney; nests that can be cleared | dive spec §7a-8, §8.2 | moved (→ 0.2.0) | | |
| Walkers as "herds" needing a herd flag | roster | lost | Settled by the built herd. | |
| Hunting or communing with the deep by a pawn dive | small items (`SCALD_DIVING_MOD_1`); kit card 3 | lost | Ship or nothing. | |
| Walker chitin as a material | small items (`SCALD_DIVING_MOD_1`); steam spec | kept as a thing to take away; how it is now obtained is `UNSETTLED` | Its only source was the retired dive hunt. | |
| The Immersion Berth mistaken for a soak-and-commune rite | mechanics review S6 | lost | A misdescription in the review; the Berth is the ship's rooms heating. | |
| The steam and devils scalding the walker on its own floor; one native tag | sea items (`HAZARD_NATIVE_TAG_1`) | kept as fixed | | |

### The floor: the rest of the cast and the catch

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The silver shoals on the dung-fall, "the strangest entry the fish roster will ever take" | sheet §4 | kept | | |
| The bubble-sailors, "like little solar sails"; "the biome's signature silhouette and kindest resident" | sheet §4 | kept, quoted | | |
| "Pilgrims read their traffic the way sailors read gulls" | sheet §4 | kept, reshaped: it became the forecast | | |
| Saal: creature and catch share one name; "noohm" retires | agenda ruling 5; walk | kept | His typed word. | |
| The built cast, each written from its catch: eesh, doss, shulla, muddal, thuum, karrash, ekkel, bladderboil | agenda §1.2; catch rosters | kept, quoted | | |
| On-screen labels iridai (muddal) and shimmer eel (thuum) | small items (`SCALD_SHEET_REDOS_1`) | kept as built | | |
| Every catch has a living body on the floor; two instruments agree on zero gaps | floor census; rulings | kept as a promise | | |
| The floor biome copies the sea's catch, so the floor's cool rings are fishable | mechanics item (2026-10-22) | kept as built; marked as the build's choice | | The dive spec's "nothing is fished on the floor". |
| Seven or more catches per sea; the Scald's rare table | catch rosters | kept | | |
| The Scald fishes as freshwater | liquid types; catch rosters | kept as a build fact | | |
| Margin fishing on the beach needs a sealed cove, never placed | kit S3; mechanics item; sea items | kept as an owed placement | Map painting is the end pass. | |
| Elder sando and sando aqua monster on the Scald | agenda §3; dive spec §7a-9; sea items | lost: moved to the Twilight Sea by him | His words, 2026-10-05, in the roster. | |
| The sando passage: a shadow sliding over the floor | dive spec §8.2, §8.5 | lost with them | | Ask him whether the shadow alone may stay: one incident. |
| Sandos made non-predators to fit the pastoral floor | roster | lost | Moot. | |
| Mee and faa on the Scald | agenda decision 6; roster | lost: *"Put them in the twilight sea instead."* | | |
| Imports ruled onto the Scald in September: atispec, ray hound, nautilant, colo claw fish, thornback colo | roster; sea items | lost from this design; left to the roster's own sitting | Evictions are stopped; no pass edits a roster. | |
| The free tier's cast must stand alone; the names proposed for the holes | cast proposal | kept (done) | | |
| The eesh "lives in the boiling column itself" against the old ban | agenda §3 | lost | The ban is withdrawn. | |
| The Scaldhide's spare art as a new Contagion creature | small items (`SCALDHIDE_R1_DESIGN_NEW_CREATURE`) | lost from here | Not the Scald's; a name match only. | |

### The floor: plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "It should not be barren": a density and "strange little underwater plants... all with alien twists" | flora pass (his commission, 2026-09-26) | kept | | |
| Crowncarpet mats: rainbow, "oddly fuzzy", banded by heat, "the oldest truth" | sheet §4 | kept, quoted | | |
| Each plant's survival trick is its twist, and no two repeat | flora pass | kept as the garden's rule | | |
| Simmerlace, kettlewick, vekkfan, thurlsponge, foamgorse, seepcandle, threshreed | flora pass; cleanse census | kept in 0.1.0, quoted in part | In source. | |
| Glasskelle and pulsebead at the vents; "the applause" | flora pass | kept | In source. | |
| Chillbrace, a cold plant | flora pass | lost: *"No, this is silly. No cold."* | | |
| Thurlsponge yields real steel | flora pass ruling 5 | kept as a thing to take away, quoted | | |
| Thurlsponge colonising wrecks as its own placement | flora pass; cleanse | 0.2.0 | | |
| Simmerlace knots become ekkel, as fishermen's lore | flora pass; agenda ruling 7; walk | kept as built | | |
| Kettlewick's collar and seepcandle's wax: what they yield | flora pass (open) | kept as open; the wax is the design's one fuel scrap | | |
| Foamgorse as the saal nursery; fans and sponges as the cleanup crew | flora pass | kept as lore | | |
| Threshreed marks where the fishermen set their nets | flora pass | kept as lore | | |
| Plant density 0.30 ratified | agenda ruling 7; small items (`SCALD_PLANTDENSITY_UNSET_1`) | kept as a build fact, not a bar | A bar pins no number. | |
| Routes for placing plants; glass forests re-rolling between visits | flora pass | kept as build facts | | |
| Pigment: the mats as "the artistic economy's raw color" | sheet §7 | kept as the pigment mat | | |
| Deepfire is its own mod, required by the Scald mod; fresh mat dies in a day | deepfire spec; ledger (2026-09-25) | kept as a thing to take away, quoted; the craft chain is later | | |

### The floor: things to find

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Wrecks, "cooked clean", "salvage priced in burns" | sheet §8; kit S6; wreckage design | kept in 0.1.0, floor and beach | In source. | |
| Wreck loot as a separate table | kit S6; wreckage design | lost (never built; ordinary salvage only) | | |
| Wreck shadows that match each silhouette | small items (`SCALD_WATER_AGITATION_FLECKS_1`) | kept as built | | |
| Other wreckage scattered on every floor "is a must" | dive spec §7a-14 | kept | | |
| Ore is nodules you simply gather | dive spec §7a-11; minerals design | moved (→ 0.2.0); flagged above | His typed words; unbuilt. | 0.1.0: items, a scatter, six sprites. |
| Gold, silver, uranium; Chimney Iron that smelts to steel only; magnetite and uraninite | dive spec §7a-12, §7b-18, §8.3 | moved (→ 0.2.0) | | |
| Mother-of-Scaldpearl on the chimney flanks; jewellery, not a pigment catalyst | dive spec §7b-23 | moved (→ 0.2.0) | | |
| Seep Salt and Pyrinth on the floor | dive spec §8.3 | moved (→ 0.2.0) | | |
| Gem clusters and Star Wars gas seeps | dive spec §7a-12 | lost (declined by card, 2026-09-25) | | |
| Plasteel stays plasteel | dive spec §7a-15 | lost from here | Another design's. | |
| Unbranded ancient machines on every floor, never hostile | dive spec §7b-19, §8.4 | moved (→ 0.2.0) | | |
| The Return Gallery: a broken coolant manifold to trace | consult idea 4; agenda ruling 3; mechanics review S7 | moved (cleanse: absent → 0.2.0); flagged above | In source. | 0.1.0: it is built. |
| The Scald Wrecked Rakatan Vessel in one hex; hidden until the first visit, then a named landmark | dive spec §7a-14, §7b-20, §8.4 | moved (→ 0.2.0, campaign layer); flagged above | | |
| Its goods: a turret for the ship, batteries, a degraded shield emitter, a sealed archive | dive spec §7a-14, §7b-21 | kept with the vessel, quoted | | |
| A navigation core in the wreck | dive spec §8.4 | lost (declined by card) | | `NEEDS HIM` 5. |
| Dormant droids on the floor, not in the ship; era-plausible chassis only | dive spec §7a-14, §7b-19 | kept with the vessel | | |
| The wreck's hold as an air pocket where the dive clock heals | dive spec §8.4 | kept with the vessel | | |
| The campaign's own ship is a Rakatan vessel | campaign | kept as the reason the wreck's parts fit | | |

### Gear and the cost of being outside

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| 55 °C on the floor as ordinary heat | dive spec §4; cleanse | kept in 0.1.0 | | |
| The dive clock: deep exposure that only shelter heals | dive spec §4; gear matrix | moved (→ 0.2.0); flagged above | Unbuilt. | |
| Gear is a two-axis matrix: no air, and heat or cold; cheap, moderate, deluxe; "Locals make their own" | dive spec §7b-24; gear matrix | moved (→ 0.2.0), quoted | His typed ruling. | |
| The air bladder and the rebreather; one dive stat for all four seas | gear matrix | moved (→ 0.2.0) | | |
| Flight suits patched to protect divers | gear matrix ruling 5 | kept in "later" | | |
| The scald wrap and the boil-suit | steam spec §5 | kept in 0.1.0 with the steam clock | In source. | |
| Boil-suit research is Industrial; vacsuits protect too | steam spec rulings 3, 4; ledger (2026-09-25) | kept; vacsuits later | | |
| The Royal Rind coat: Neolithic, extreme heat and cold, near-immune to steam on a tiny floor | steam spec §5a; ledger (card, 2026-11-06) | kept in "later" | Waits on the Greentide's fruit. | |
| Scald protection folds into ordinary heat armour | small items (`SCALD_FOLD_INTO_HEAT_1`) | kept; it is why no second heat exists | His card, 2026-10-08. | |
| No drink, salve or bath lowers exposure; no building clears the steam | steam spec §5 | kept | | |
| A humanlike native would need a gene; none planned | steam spec ruling 10 | lost | Nothing to build. | |

### The beach

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Steam weather "really beautiful and interesting (and deadly without protective gear)" | steam spec §0; ledger (2026-09-25) | kept, quoted | | |
| Standing steam with still days | kit S1; mechanics item; steam spec §3.2 | kept in 0.1.0 | In source. | |
| "A still day that shows the wrecks" | sheet §9; kit | kept, quoted, as an on-screen moment | | |
| The steam exposure clock, its stages, "dead in under two days" | steam spec §3.3, ruling 1 | moved (cleanse next version → 0.1.0); `NEEDS HIM` 2 | | The cleanse's way: hot air only. |
| "Clean steam" means pure, not harmless | steam spec §1; cleanse ambiguity 4 | kept | | |
| No private steam-health currency | cleanse rule R5, check K6 | kept, reshaped: the clock stays because it reads ordinary heat armour | | |
| The Scald's own "ambient +15 °C" heat is to become plain air temperature | sun design | kept as owed work | The one-sun ruling. | |
| Steam's look: the overlay, sky colours, steam off the water, the breath sound | steam spec §3.1 | kept as art and sound direction | | |
| Steam costs accuracy and caps range | steam spec §3.3; kit S1 | kept as a fight fact; the numbers are tuning | | |
| Vent flashes | steam spec §3.1; cleanse | 0.2.0 | | |
| Steam devils | steam spec §2, §6; cleanse; mechanics review S9 | 0.2.0 | | |
| Boiling water burns on traversal; deep burns harder | sheet §0; steam spec §4, ruling 9 | kept, quoted | | |
| A setting to stop the lake burning, default on | steam spec ruling 5 | kept | | |
| The water "hurts nicely": burn and comfort in one step | sheet §0, §5 | kept, quoted | | |
| Margin calm, shallow lightly agitated, deep constantly agitated | small items (`SCALD_WATER_AGITATION_FLECKS_1`) | kept, as his description | | |
| Natives immune to the water, the steam and the devils | steam spec §6; ledger (2026-09-25) | kept | | |
| Natives drink their own water | rulings (2026-11-01) | kept | | |
| The steam-catch: "the tap of the world" | sheet §7; kit S2; mechanics item | moved (cleanse next version → 0.2.0) | | |
| Item water by default, a pipe network behind a setting | kit card 2 | kept with it; the pipe form later | | |
| Catch-rights: "whoever holds catch-rights holds the monopoly's source" | sheet §7 | kept, quoted, under who is here | | |
| The sail scatter at beach vents | kit S5; cleanse | 0.2.0 | | |
| The baths: "the planet's one sacred spa" | sheet §7 | kept in "later", with the rite | | |
| The Margin Bath rite for Ta'Baa; the bathing-stone; "the sea burns, the margin forgives" | bath rite; agenda ruling 4 | kept in "later" | His ruling of 2026-10-23: every taught rite is second version. | |
| The Unanswered Wound rite | consult idea 5; agenda decision 4 | lost (not chosen) | | |
| The boiling-lift | sheet §7; boiling-lift spec | kept in "later" | Its own ruled spec. | |
| Geothermal power on shore geysers | kit S4 | kept as one line | | |
| The Greentide's twin groves on the flanks | sheet §8 | kept as where the Wildsteam sit | | |
| The ocular forest and one Helix outpost on the mountainous shore | world definition §7c | kept as one line | | |
| The dark tower is the Spire, in the mountains, seen from the lake | sheet §8; small items (`SCALD_DARK_TOWER_1`); campaign | kept as one line; lost from here otherwise | Another design's. | |

### The ship

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The Immersion Berth: "a parked ship's rooms slowly heat; doors never seal, launch never blocked" | consult idea 3; agenda ruling 2 | kept in 0.1.0, quoted | His card; in source. | |
| Heat by outside hull faces only | source (the Berth component's header; ledger title `SCALD_BERTH_HULL_FACES_1`) | kept as a promise's control | | |
| "Uses ordinary room heat, power and equipment, not a special colonist heat system" | answers | kept, quoted | | |
| New floor refrigeration exchangers | consult | lost | Ordinary coolers do it, by his answer. | |
| "Tune for a meaningful power burden, not mandatory reconstruction" | consult | kept as the reason no rate is a bar | | |
| Kettle scale on the hull | agenda decision 2 | lost (not picked) | | `NEEDS HIM` 5. |
| Steam and sound only | agenda decision 2 | lost (not picked) | | |
| The thermal veil: heat out, heat in, "the temperature slowly climbs anyway" | shield design | kept, quoted, as a campaign-layer answer | | |
| "Slow pressing things move through all shields... nothing 'holds out water'" | shield design | kept, quoted | | |
| No hard landing gate; the ship advises "but no more than that" | shield design | kept, quoted | | |
| A landing reserves its hull and a way out, clear of hazards | cleanse definition | kept, for pools and vents | | |
| The Cathedral dumps its heat in the Scald so nobody sees it | history draft; sheet §8 | kept, quoted, beside cover from orbit | | |
| The Scald as the intended coolant reservoir; two coolant systems; Rustwave a captured river | history draft | lost | Cathedral lore. | |
| The Cathedral fears the player's ship drawing the Empire | history draft (his resolution 3) | kept, quoted, as a campaign hook | | |
| "Many paths to fuel"; helixien gas on volcanic tiles | campaign | kept, quoted, as the rim's fuel, not this sea's | | |

### Who is here

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The two-faith shore | sheet §8 | kept in the campaign layer, one line; flagged above | | |
| The Deepwater Compact, "two on the Scald despite the Empire" | world definition | kept, quoted | | |
| The Wildsteam's two jungle seats | world definition; sheet §8 | kept, quoted | | |
| The Empire's ground holding at the Scald Gate | world definition | kept as an `UNSETTLED` neighbour | | |
| The steam-catch works, condenser lines, the Compact's watch | sheet §8 | kept in the campaign layer | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's land and life rows for the Scald | cleanse census | kept | | |
| The cleanse's switch-off tickets for the Scald | cleanse tickets, next-version list | kept as they stand, except where a feature moved | | |
| The beach steam wiring may point at a background sea | cleanse ticket T45 | kept as an unmeasured build risk | | |
| The Scald's bar: pools burn, ground does not, nothing is drink | cleanse bars | kept as one of the twelve promises | | |
| The mod's description still says perched and spilling | cleanse ticket T48 | kept as owed text work, pending `NEEDS HIM` 4 | | |
| Forty colonists and a whole-sea season | cleanse definition | moved (first version → later) | Colony scale. | |
| The inert cross-biome switch | cleanse; walk | lost (recommended for dropping; his to confirm) | | |
| Settings for each Scald feature | walk; mechanics item; steam spec §7 | kept | | |
| The walk's intended-function lines for the Scald, all unrun | walk | kept | | |
| The mechanics review's ten Scald rows and their keep, simplify and ask marks | mechanics review | kept as history; answered by scope here | | |
| The combined design's Scald section and its rows | combined design | kept, reshaped: corrected as listed at the top of this page | | |
| The kit's six mechanics and three classes | kit; mechanics item | kept as build history | | |
| The free-tier mod split and the frozen campaign twin | sea items (`TERMINALBIOMES_RM_MOD_BUILD_1`); floor census | kept as build facts | | |
| Two consult jobs run at once crossed their answers | agenda §4 | lost | A tooling note, not design. | |
| Saallen (a Sleeping Ice organism) and the acid immersion defect | small items (`SAALLEN_BUILD_BLISTERS_ON_CUE`, `IMMERSION_DAMAGE_WIRE_NEVER_APPLIED`) | lost from here | Name matches only; neither is the Scald's. | |

## Sources read, and the count

Measured after writing by a script that counts the table rows above and the first words of each "what happened"
cell, and checks that every source name defined above appears in a row (the check and its probe are recorded in
`design/RimMandrake/biome_rewrite_scald_row_check_2026-11-18.txt`): **209 rows** over **35 named sources**, of
which **38 lost**, **28 record a move** (24 that say "moved" and 4 cleanse deferrals that say only "0.2.0"),
**7 kept, reshaped** and 0 folded into shared machinery. Every named source is in at least one row. The same
record holds a second check: every quoted phrase in both files was compared with the repository text.

**Read to the end (31 files):** `the_scald.md`; the floor agenda; the consult; the bath rite; the flora pass; the
kit; the roster; the history draft; the steam spec; the dive spec; `SCALD_MECHANICS_1.md`; ten smaller item files
(`SCALD_FOLD_INTO_HEAT_1`, `SCALD_DIVING_MOD_1`, `SCALD_WATER_AGITATION_FLECKS_1`, `SCALD_DARK_TOWER_1`,
`SCALD_RIVER_REPAINT_1`, `SCALD_SHEET_REDOS_1`, `SCALD_PLANTDENSITY_UNSET_1`, `SCALDHIDE_R1_DESIGN_NEW_CREATURE`,
`SAALLEN_BUILD_BLISTERS_ON_CUE`, `IMMERSION_DAMAGE_WIRE_NEVER_APPLIED`); the owner answers of 2026-11-10; the
cleanse's `definition.md`, `owner_pages.md`, `ambiguities.md` and `next_version.md`; the floor census; the walk;
the experiences table; and the combined `design.md` and `rewrite_choices.md`. Read to the end as references, not
sources: `design/concepts/Greentide/design.md` and `design/RimMandrake/biome_shared_machinery_2026-11-18.md`.

**Read in part, and where a second reader should look:**
- The cleanse's `tickets.md`: its opening, tickets T1 to T6, T45, T48 and T49 whole; every other ticket by heading.
- The cleanse's `census.json`, `bars.json`, `converge.json`, `fixes.json` and `review.json`: every record that
  mentions the Scald, steam, boil, vent, walker, sail, berth, condenser, margin, sponge or wreck, cut at 1,400
  characters each; `models.md` by the same words, line by line; `result.json` and `run.json` by their keys only.
- The cast proposal: its headings and every Scald passage.
- The mechanics review: the Scald table whole; nothing else.
- The gear matrix: every line naming the Scald, a bladder, a rebreather or a dive, cut at 600 characters.
- The shield design: the rulings table whole and the thermal veil section; the rest by search.
- The world definition: the Scald's passages (the lakes table, the water-source ruling, the faction seats, the
  ocular forest, the mutator layers); the rest of its 111 KB not at all.
- By search for the Scald, lines cut short: the catch rosters, the deepfire spec, the liquid types design, the
  minerals design, the wreckage design, the boiling-lift spec, the sun design, the two campaign documents, the
  rulings file, the surface removal record, the Twilight danger pass (its cut and redirect only), and the item
  files `SEA_FLOOR_AND_CATCH_PASS_1`, `closed/TERMINALBIOMES_RM_MOD_BUILD_1`, `closed/HAZARD_NATIVE_TAG_1`,
  `SEABED_DESCENT_ASCENT_1` (its first sixty lines) and `SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR`.
- Source, for what exists: the Scald's biome, race, plant, apparel and floor-generator defs by parse; the header
  comments of seven floor classes; two constants in the shield and berth code. No class was read whole.
- The ledger, for his words: `owner_rulings.py --grep` on twenty-one words. Items with no file were read as their
  one-line ledger title only (`SCALD_WALKING_PASTURE_1`, `SCALD_IMMERSION_BERTH_1`, `SCALD_RETURN_GALLERY_1`,
  `SCALD_FLOOR_VENT_FIELDS_1`, `SCALD_BATHING_RITE_1`, `SCALD_FLOOR_PASS_1`, `SCALD_UNDERWATER_FLORA_1`,
  `SEABED_PER_SEA_FLOORS_1`, `SCALD_BERTH_HULL_FACES_1`, and the four filed on 2026-11-01).

**Not read:** `terminator_sea.md` (the roster rules that its law does not bind the Scald); the fish bestiary
commission and build item; the river ledger and graph data; `LIQUID_BIOMES_MAP_1_RECONCILIATION.md`; the freeze
review and freeze rulings files; `FORGE_MECHANICS_1` and the Forge, Greentide and Webwork kit specs that mention
the Scald; the art lists, regeneration job files, mineral and fauna tables. A search on 2026-11-18 found the word
"scald" in 541 files under `design/` and `infrastructure/state/items/`; this page accounts for roughly seventy of
them (not counted), and most of the rest are data tables and other biomes' use of the word as a verb.

## The older files this design replaces, ready to delete on his word

For the Scald, all in `design/Jawa/worldbuilding/biomes/`: `the_scald.md`,
`the_scald_floor_sitting_agenda_2026-10-02.md`, `the_scald_floor_gpt_consult_2026-10-02.md`.

Hold, because each is the only specification of something this design defers or leaves to another layer:
`design/RimMandrake/sea_dive_maps_spec.md` (his whole 2026-09-25 floor, the Rakatan vessel, and the other three
seas' floors); `design/RimMandrake/scald_steam_and_hazards_spec.md` and
`design/RimMandrake/exposure_gear_matrix_spec.md` (built numbers and unbuilt gear);
`the_scald_underwater_flora_pass_2026-09-27.md` (def and art specification for built plants);
`the_scald_margin_bath_rite_2026-10-03.md` (second-version rite); `kits/scald_kit_spec.md` (engine findings the
build still leans on); `rosters/the_scald.json` (his eviction words and the unsettled imports);
`the_rust_cathedral_SCALD_HISTORY_amendment_draft.md` (the Cathedral's, not the Scald's);
`terminal_seas_cast_proposal_2026-09-25.md` (three other seas).

Not for deletion: the cleanse folder (superseded for the Scald by this design, never applied; it should be re-run,
not applied); `designer_codex_2026-11-09/TheScaldFloor/ANSWERS_OWNER.md` (his answers); the validation walk; every
ledger item.

Before deleting `the_scald.md`: it is frozen by `BIOME_FREEZE_FABLE_REVIEW_1`, other sheets cite it by section,
and the water chain and the two-faith shore (rows above, flagged) need a home in a world document first.
