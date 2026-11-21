# RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES

## What the card said

<!-- answered 2026-11-21T21:09:33Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Form first. A census just read our shipped mod code: about 66 places in about 25 mods switch a mechanic on only in its own biome, and six mods carry an 'Enable outside this biome' switch that is off by default and labelled unsupported. Your Stillshade sun and the Rot's living floor are both gated this way today. So your ruling reverses how nearly every biome mod is built. A 'biome check' is code that asks which biome the map is. 'Biome data' is what a biome contains: its plants, animals, terrain, weather odds and map generation. (Hard to read? Type STE, Binding or Both for a rewrite.) What should 'universal' mean as a rule for the code?
**Picked:** Conditions, never the place (Recommended)
**Its description:** Why: it is your Stillshade example made exact. A mechanic reads only physical conditions (sun angle, heat, water, fire, ground, roof) and never which biome it is in; a biome keeps only its data. Buys one clear test a program can enforce. Costs converting all 66 gates over time. Recommended: the only form a tool can check.
**Other options:** Universal unless a reason is written · Only the elements are universal

## What the card said

<!-- answered 2026-11-21T21:09:33Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** On October 15 you released the requirement that biome mechanics work in other biomes: 'That is too much of a lift... we are not going to validate that at this time.' Today's ruling says they are universal. Both can stand if 'universal' is how the code is written and testing stays limited, or the October ruling can be reversed. How much do we test a mechanic away from its home biome?
**Picked:** Home only, as ruled in October
**Its description:** Why: testing everywhere was already judged too heavy. The code is written universal; only the home biome is tested. Buys no new test cost. Costs truth: mechanics will silently break on foreign maps, which is what the 'unsupported' label admits today.
**Other options:** Home, plus one foreign map (Recommended) · Every mechanic on every biome

## What the card said

<!-- answered 2026-11-21T21:09:33Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** The conversion is large: about 66 gates in about 25 mods. Six biome mods are under your hold, and Pyrelands is the only biome mod advancing; it alone has 13 gates. Its first version is two real faults away from your walk. When should existing mods be converted?
**Picked:** New work now; old mods as they advance (Recommended)
**Its description:** Why: no mod pays twice. The principle binds all new design and code from today; each existing mod converts when it next advances, as a planned change for its next version. Buys steady progress and keeps Pyrelands's first version on course. Costs months of mixed state. Recommended: least disruption for the same end.
**Other options:** Pyrelands converts now · One campaign across all mods now

## What the card said

<!-- answered 2026-11-21T22:35:31Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** You ruled today that a mechanic reads only physical conditions, never which biome it is in. Six mods have a Mod Settings switch named 'Enable outside this biome', off by default and labelled unsupported. Under your ruling the mechanic already works anywhere, so the switch has no job as written. Our Mod Settings rule also says each major feature has an on/off switch. (Hard to read? Type STE, Binding or Both for a rewrite.) What becomes of the six 'Enable outside this biome' switches?
**Picked:** Turn each into a plain on/off (Recommended)
**Its description:** Why: one switch per mechanic, no biome in it. When a mod converts, its switch becomes 'this mechanic: on/off', default on. Buys a player escape from any mechanic. Costs a settings change in six mods at their next version. Recommended: it fits both rulings.
**Other options:** Delete the switches · Keep them, flip the default to on

## What the card said

<!-- answered 2026-11-21T22:35:31Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Some mechanics hurt a colony: Pyrelands fire walks across dry grass, and the Rot spreads. Written as conditions, they will act on any map where the conditions hold (dry grass, heat, no rain), not only at home. You chose to test in game only on the home biome, so behaviour on other maps is untested. Are dangerous mechanics on by default on every map?
**Picked:** On everywhere; conditions decide (Recommended)
**Its description:** Why: this is the ruling taken at its word. Fire walks wherever the grass is dry. Buys one consistent world. Costs surprise deaths on maps we never tested, and a heavier load of threats on every map. Recommended: a default-off list would be a biome check under a new name.
**Other options:** On everywhere, with a danger dial · On at home, off elsewhere until tested

## What the card said

<!-- answered 2026-11-21T22:35:31Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** The Scald is the hot-spring biome. Today it is our one written heat exception: it keeps its own steam clock, and its water harms faster than its steam. Every other biome uses one sun-heat rule. Under 'conditions, never the place', is the Scald's hot water still an exception?
**Picked:** Physics: hot water scalds anywhere (Recommended)
**Its description:** Why: the harm comes from the water's heat, not the map. Any water that hot, on any map, harms the same way; the Scald is simply where it is common. Buys a rule with no exception. Costs a rewrite of the Scald's clock at its next version. Recommended: it removes the last named exception.
**Other options:** Keep it as the one exception · Decide when the Scald next advances
