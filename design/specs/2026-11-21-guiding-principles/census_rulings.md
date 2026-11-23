# Census of written rulings that conflict with the universal-mechanics ruling (read-only helper, 2026-11-21)

Not a ruling. Each row is a pointer for review; the helper lists at its end where it did not look.

I found 41 written conflicts or ambiguities: 14 REVERSED, 17 AMBIGUOUS and 10 that are consistent but worded as confinement [measured: rows below]. Nothing was changed. Every file is under `/home/mandrake/rm/bench/`.

Three things about what I searched:
- **Items:** `infrastructure/state/items/` holds 896 item files, not 1,800. I grepped all of them for confinement phrases instead of picking by title.
- **Concepts:** the six `version/locked_bars.json` files hold only bar IDs. I read the bar texts from each mod's `tree.json` and `cleanse/bars.json`.
- **"Stillshade":** the word appears in no file except the concept draft. His description matches the Long Shade (long shadows) or the Stillsand (fixed sun).

## REVERSED by the new ruling

| # | File and line | Quote | His dated words behind it | Principle |
|---|---|---|---|---|
| R1 | `CLAUDE.md:219` (known) | "We promise biome mechanics only inside our own biomes." | 2026-10-15 | 1. The Forge haze commit cites this line. |
| R2 | `design/concepts/Contagion/design.md:153` and `:303` | "turns ordinary plants into flesh plants, in our biomes only" | none given | 1, 3 |
| R3 | `design/concepts/Contagion/tree.json`, leaf `flora_flesh` | "turn ordinary plants in owned biomes only". It counts "the haze runs on the temperate map too" as a false pass, and "none converted off-biome" is in the test. | none | 1, 3 |
| R4 | `design/concepts/Warscar/design.md:351` | "Broken turrets follow movement and never fire, on Warscar maps only." The check: "The other map's turrets do not turn." | none | 1 |
| R5 | `design/concepts/Greentide/cleanse/bars.json` rule R7 | "Direct Sun active on Greentide maps only" | none. This also breaks the Direct Sun ruling. | 1 |
| R6 | `design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md:228`, `:372` | "Our plants outside our biomes → `vanilla`, labelled unsupported" | card 2026-10-17: "OQ-10 outside our biomes → vanilla growth, labelled unsupported" | 1 |
| R7 | `infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md:5-8` | "Scope is Baroque Biomes' own biomes" | 2026-10-16: "It should only natively apply to plants within the Baroque Biomes" | 1 |
| R8 | `design/RimMandrake/biome_mod_architecture.md:485`, `:494-496` | "a biome-defName allowlist"; the default answer is "yes on `RM_X`, no elsewhere" | none | 1. The design itself is a biome check. |
| R9 | `design/RimMandrake/rot_warm_mat_portable_2026-10-22.md:143`, `:26` | "The exemption is decided by the map's biome (`RM_TheRotFront.IsRotBiome`)"; "No other Rot mechanic becomes cross-biome because of this." | 2026-10-22: "Rot doesn't require feeding due to sharing lore" | 1, 3. His outcome can stay; the biome check cannot. |
| R10 | `design/concepts/LanternDeeps/cleanse/bars.json` rules R0, R8 | "Custom host selection may widen the biome list, labelled unsupported outside shipped hosts" | none | 1. The temperature test alone should decide. |
| R11 | `design/concepts/Abyss/design.md:195` | "nothing outside the Abyss reads it, so today the pursuit is slowed by the biome alone" | His cover card of 2026-11-19 already made cover planet-wide. | 1 |
| R12 | `design/RimMandrake/gpt_review_findings_2026-10-22.md:211` | "spore cloud slider governs nothing off the Rot … Cross-biome is unsupported by ruling." | none | 1 |
| R13 | commit `d07e03a938` (known) | "vapour-column haze … on Forge maps only (pale ring round every geyser)" | His own words of 2026-11-21 reverse it. | 1, 5 |
| R14 | commit `675ab57651` (known) | The commit message says nothing about Pyrelands-only. The tree leaf `ashwallow_dives_unharmed` is not confined. | none | 1. I could not find the confinement in any written text. |

## AMBIGUOUS (needs his word)

| # | File and line | Quote | His dated words behind it | Principle |
|---|---|---|---|---|
| A1 | `design/RimMandrake/standing_rulings.md:178-185` (known) | "Biome mechanics are promised inside our own biomes only" | 2026-10-15 release words | 1. This is the draft's first open question: "universal" in how code is written, or also tested everywhere? |
| A2 | `src/RimMandrake/rimflow/concept_floor.json:26` | `biome_scope`, standing and not waivable: "promised inside our biomes only" | none | 1. A program enforces this one. |
| A3 | `src/RimMandrake/rimflow/roles/designer_write.md:81` | "Others are biomes in scope only" | none | 1 |
| A4 | `CLAUDE.md:184`, `standing_rulings.md:233`, `biome_rulings.md:210` (known) | "No biome has its own heat kind, number or exception, except one: the Scald" | card 2026-11-20: "hot water is not the same as hot air" | 1. Is this a biome exception, or physics of steam and hot water that applies anywhere? |
| A5 | `cleanse/bars.json` of Cauldron R13, Contagion R13, CrackedLands bars 0/2/3/6/7 and check 1, FeverWood R13, LongShade R5, Stillsand R13, TerminalBiomes R8, TheRot R10, RustCathedral R6, Miasma R9, TheSump bar 6, GelatinousSlime bar 8, LeaningScrub check 13 | "Existing unsupported cross-biome switches stay off" | 2026-10-15 | 1. These switches have nothing to switch under principle 1. |
| A6 | `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md:269`; `infrastructure/state/items/DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS.md:24`; `design/concepts/TerminalBiomes/cleanse/tickets.md:317` | "No new cross-biome switch is built"; "Unsupported: may work outside our biomes, not tested" | 2026-10-15 | 1 |
| A7 | `design/concepts/TerminalBiomes/TheChill_design.md:566`, `TwilightSea_design.md:508` | "Recommended for dropping, not yet his: the inert cross-biome switches" | none | 1. This is ready for his word. |
| A8 | `design/concepts/Contagion/cleanse/bars.json` bar 5 | "Off-biome ambient exposure is unsupported; existing contact behaviour must not be redesigned to test other biomes." | none | 1 |
| A9 | `design/concepts/Contagion/rewrite_choices.md:493`; `infrastructure/state/items/RIMMANDRAKE_BUILD_CONTAGION_REPULSOR_WARNING_NAMES_WHOLE_MAP.md:12` | "The Burn must never fire on another biome's map", kept as a build law | none | 1, 3. This is fine if the cause is the Bloom cloud, wrong if it is the biome. |
| A10 | `design/concepts/Wastes/design.md:379` | "The same food on another biome's map at the same temperature rots." | none | 1, 3. No physical reason is given. |
| A11 | `design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md` §6, setting A | "Vanilla crops in our biomes … need water nearby" | none | 1. Applied everywhere, this would change vanilla crops on the whole planet. |
| A12 | His two growth rulings disagree: `design/Jawa/worldbuilding/biomes/the_cracked_lands.md:273` against R7 | "the owner took it planet-wide" (2026-09-06) against "only natively apply to plants within the Baroque Biomes" (2026-10-16) | both dated | 1 |
| A13 | Pyrelands fire: `design/concepts/Pyrelands/tree.json` leaves 0-21 ("a running Pyrelands map with the biome's clocks"); the `pyrelandsEnabled` gates | Pyrelands cross-biome not picked | card 2026-10-15 (FIRE_ECOLOGY): "(Pyrelands cross-biome not picked)" | 1. This is the draft's question about mechanics that are dangerous everywhere. |
| A14 | `design/concepts/PyrelandsMechanics/tree.json` leaf 8 | "The player whose colony sets fires on a Pyrelands map … never sees a raid" | none | 1, 4. Is the Tribes rite biome data, or a mechanic? |
| A15 | `design/concepts/SleepingIce/design.md:44` | "the law of the place, from the sheet, which no other biome has: 'Sensing is thermal'" | none | 1, 2. Is heat-sensing physics everywhere, with the Sleeping Ice as its showcase? |
| A16 | `design/concepts/GelatinousSlime/tree.json` leaf 11 | "Arbitrary third-party biome retrofit is outside the adopted scope." | none | 1. This is the draft's question about vanilla and third-party biomes. |
| A17 | `design/concepts/TheRot/design.md:107`, `:353`; `design/RimMandrake/rot_warm_mat_portable_2026-10-22.md`; `design/RimMandrake/rot_northstar_bars_draft_2026-10-22.md:52` | His new ask "make it die in direct Sun exposure" | 2026-11-21 | 3. No file says it yet. |

Ruled after this census was written (2026-11-21 5:34 PM PST). A11 (his card, 2026-11-21 5:34 PM PST): vanilla crops need water nearby wherever the ground is dry and hot, a condition, not 'in our biomes'. Temperate maps are untouched. 'Dry and hot' is defined as a measurable condition when Explosive Growth next advances. A12 (the Conductor's call under his cards of 2026-11-21): no conflict is left. Explosive growth belongs to the plant species and acts wherever those plants and water are. The Baroque biomes are where the plants are native (biome data). A14 (the Conductor's call under his cards of 2026-11-21): the Tribes rite follows a burn front where the Tribes are present. The front's schedule is the biome's weather odds (data). The code names no biome.

I did not read the sentence at `design/RimMandrake/sprinklers_design_2026-10-16.md:112` in context: "the 2026-10-15 rule keeps us out of other biomes" (principle 1).

## CONSISTENT, but worded as confinement (rewording only)

| # | File and line | Quote | What makes it consistent |
|---|---|---|---|
| C1 | `design/concepts/Warscar/design.md:353`, `:400`, `:424` | "gives nightmares only here" / "only while on this ground" | Principle 1 holds if the poisoned ground is the cause, not the biome. |
| C2 | `design/concepts/TerminalBiomes/TheChill_design.md:434` | "The same stove on any other map lights." | Lack of oxygen is the real reason. |
| C3 | `design/concepts/Greentide/design.md:468`; `design/RimMandrake/special_mechanics_review_2026-10-22.md:303` | "Churnmud seeded on other biomes (kept off and labelled unsupported)" | Seeding terrain is biome data (principle 4). |
| C4 | `design/concepts/Warscar/design.md:480`; `infrastructure/state/items/DEAD_OR_INERT_SETTINGS_1.md:11`, `:22`; `design/RimMandrake/fluff_cuts_2026-10-23.md:186` | cross-biome spread and wreck-lichen seeding settings | biome data (principle 4) |
| C5 | `design/concepts/Stillsand/cleanse/bars.json` bar 1 | "Tree-heavy other biomes … are dependency scope, not new Stillsand promises" | consistent |
| C6 | `design/RimMandrake/rot_warm_mat_portable_2026-10-22.md:20-21` | no upkeep inside the Rot, needs food outside | Matches his 2026-11-21 words. The mechanism is the problem, in R9. |
| C7 | Pyrelands `populations_are_the_biomes_own`, no foreign arrivals, "never sees ordinary rain" (`design/concepts/Pyrelands/tree.json`, `record.json`) | the biome's own roster and weather | biome data (principle 4) |
| C8 | `infrastructure/state/items/RUST_CATHEDRAL_MECHANICS_1.md:360`, `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1.md:70`, `FORGE_MECHANICS_1.md:449` | infestation off "on Cathedral maps only"; borehulk "on any other biome's map: none"; a hard-coded Forge biome check | Incident and placement odds are data (principle 4), even though they are built as biome checks. |
| C9 | `design/Jawa/worldbuilding/biomes/the_webwork.md:180`; `design/Jawa/worldbuilding/biomes/the_propane_lakes.md:180` | "No hyperweave from any source but the Webwork"; ban #8 "binds the biome map only" | The Webwork as the source (principle 2); a roster ban (principle 4). |
| C10 | `design/RimMandrake/biome_rulings.md:217` | "natives should drink their own environmental water" | 2026-11-01. This is biome data, worded by biome. |

## (a) Biomes whose text treats a mechanic as special to them
- **Long Shade** (`design/concepts/LongShade/design.md:42`): "every rock and scarp throws a shadow four times its own height". Line 354 already says the one sun "runs on every day-side map; this is the biome built on it."
- **Stillsand** (`design/concepts/Stillsand/design.md:374`): "Every dayside biome uses the geometry; only here is there never anything else."
- **The Rot** (`design/concepts/TheRot/design.md:107`): "The floor is the heater. Living mat warms a room built over it." Nothing says it dies in direct sun.
- **Sleeping Ice:** thermal sensing (A15). **Warscar:** the mark's nightmares (C1). **Contagion:** the zhool haze (R2). **The Forge:** the geyser haze (R13). **The Scald:** the steam clock and the water (A4).
- **Webwork** (`design/Jawa/worldbuilding/biomes/the_webwork.md:206`): the light-moat is "the only base-defense of its kind on the planet".
- **Twilight Deep** (`design/Jawa/worldbuilding/biomes/the_twilight_deep_content_2026-09-26.md:757`): "nowhere else on the planet do you rent light".
- **Wreck fields** (`design/Jawa/worldbuilding/biomes/wreck_fields.md:161`): "Life is in circles around live wrecks, and nowhere else."

## (b) Rulings that already state the universal idea (precedents)
- **Direct Sun:**
  - `CLAUDE.md` §"One Direct Sun, a pure function of geometry"
  - `design/RimMandrake/standing_rulings.md` §Direct Sun, 2026-10-19: "a pure function of geometry, NOT biome"
  - `design/RimMandrake/biome_rulings.md` §No biome-specific sun or heat
  - `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md:166`: "no per-biome opt-in"
  - Tree shade, 2026-10-19: "direct sun works the same everywhere on the day side"
- **Shade-seeking**, 2026-11-10: "This mechanic should be true everywhere in the biomes … It's the beasts that should act specially since they're evolved to do so." This is principle 2's showcase idea almost word for word. The card of 2026-11-19 (`biome_rulings.md` §5) repeats it: "one shared rule for every day-side biome".
- **Rot warm mat**, 2026-10-22: "Make it work anywhere … Would grow in other biomes if tended with food." This is principles 2 and 3 in one sentence.
- **Explosive growth**, 2026-09-06 (`design/Jawa/worldbuilding/biomes/the_cracked_lands.md:273`): "a WORLD mechanic, born here".
- **Seas**, 2026-11-20: "underocean rivers should be commonplace in all the oceans, so this isn't even special for Twilight".
- **Cover card**, 2026-11-19: "where you land is a real choice everywhere".
- **Other dated words:** anima trees blocked "on ALL biomes" (2026-10-11); "Rites are allowed everywhere" (2026-10-01).
- **The design pattern** in the biome designs: "Featured here / Merely active here", for example Greentide `:358` "Growth runs on every wet map; only here is it the thing the player fights", FeverWood `:381` "this is its home", TheSump `:434`, LeaningScrub `:420`, CrackedLands `:122` "nothing special to this".
- **Know-how items:** "learned here, works anywhere" (Cauldron `:246`, Greentide `:315`, Abyss `:391`).
- **Slime:** `design/RimMandrake/RM_gelatinous_slime_mod.md:170`: "the cure geography is data, not code".

## Where I did not look, or only grepped
- `cleanse/census.json` and `review.json` files: not read. They have the highest keyword counts (Miasma 50, Stillsand 25, TheRot 22).
- `record.json` files: only Pyrelands was read.
- `rewrite_choices.md` and the biome sheets: phrase grep only.
- `design/Jawa/worldbuilding/the_one_map.md`: grep only. Its hits were data and showed no conflict.
- `LEXICON.md` and `design/RimMandrake/delegation_policy.md`: no conflicting text in the grep. I read neither in full.

## Summary
- REVERSED: 14 [measured: rows R1 to R14]. AMBIGUOUS: 17 [measured: rows A1 to A17], plus one sentence I did not read in context. CONSISTENT-but-worded: 10 [measured].
- Ambiguity 1: what "universal" means. Is it a rule for how code is written, or also a promise to test everywhere? This decides A1, A2 (a program enforces it), A3 and A16, and whether R1 is reworded or deleted.
- Ambiguity 2: the cross-biome switches and the dangerous mechanics. Do the switches go, and does Pyrelands fire ecology (A13), with growth (R6, A11, A12), become on by default everywhere?
- Ambiguity 3: is the Scald's steam clock and hot water a biome exception, or physics that applies anywhere (A4)? The same physical-reason question decides A9, A10 and A15.
- Fast fixes once he rules: R2 to R5 and R8 to R11 are design texts that gate a mechanic on the map's biome. Each can be rewritten to name a physical condition.
