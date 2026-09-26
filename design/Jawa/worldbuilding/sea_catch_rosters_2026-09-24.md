# Sea catch rosters — four seas, seven-plus catches each

**Status:** DESIGN for the owner's reading (2026-09-24). Feeds `SEA_FLOOR_AND_CATCH_PASS_1`.
Extends `fish_bestiary_commission_2026-09-10.md` (its §0 rules and §1 registers apply to every row here).

## The owner's brief, verbatim (2026-09-24, at the bench)

> "Let's do them now. Grey sea should be timorous, sickly, extrkophile, or alien saline creatures often with crusty bits and shell. Twilight sea tends towards glowing bits and somewhat elegant designs. Propane lake has some documented crystalline life already mentioned. If not, make some. Scald has some defined. Please flesh all of these out to make each of them hold at least seven varied and interesting catches that make sense. Some fish. Some eels. Some crustaceans. Some alien who knows what. Revisit all fishing tables of the seas at this time."

("extrkophile" = extremophile.) This is the ruling for every table below: **each of the four seas holds at least seven varied catches.** Where it overrides an earlier no-fish ruling, that ruling is quoted in `## Superseded rulings` with this sentence as the authority.

## How to read the tables

- **Rules inherited from the commission (§0):** a `fishTypes` entry is an item def (`ParentName="FishBase"`, `MayRequire="Ludeon.RimWorld.Odyssey"`), never a race def; anti-exponential (Nutrition ≤ 0.25, MarketValue ≤ 6.5 except where the register row sets its own baseline); recognizability (only the shoal register may look like a fish); soft vowel-led names for the drifting and soft-bodied, `karr-`/`-rrik`/`-ik`/`-ek` roots for the armoured and quick. Register stat envelope (nutrition / market / mass / rot): shoal .25/6.5/.5/2d · crustacean .20/7/.6/3d · squid .25/6/.4/1.5d · octopus .25/8/.5/2d · eel = shoal · floater .10/3/.2/1d · jellyfish .08/4/.3/1d + raw poison .05 · cucumber .20/5/.5/4d. Two registers are added here because the owner asked for them by kind: **shellfish** (.15 / 5 / .7 / 5d — shell keeps longest, heaviest to haul) and **alien** (no fixed envelope; each entry states its own numbers inside the anti-exponential cap).
- **`defName`** keeps the sibling files' `RUT_` prefix. Retiering to `RM_` is the TERMINALBIOMES sitting's job (Q12, `biome_mod_architecture.md` §7) — not decided here.
- **`band`** is the `fishTypes` bucket. Which pair a sea *canonically* uses is stated under each table; `mandrake.rm.seashores` falls back salt↔fresh when a pair is empty (`RM_SeaShoreUtility.BandFor`), so a wrong-pair table still serves, but the canonical pair is what the build writes.
- **`floor pairing`** follows `SEA_FLOOR_AND_CATCH_PASS_1`'s rule: every catch species gets a floor animal; a shoal gets ONE swarm creature; megafauna stay floor-only. `owed: single` / `owed: swarm` means no race def exists yet; a named def means the animal is already built.
- **`art`**: MEASURED 2026-09-23 — `infrastructure/artpipe/done/` and `_artsrc/` hold **no** art for any of the 13 built catch items (sanity probe `Cindermite` 15 hits; every fish name 0), so every row here is NEW icon owed; the built rows carry the SandSwimmer-convention placeholder texPaths named in their files.
- **Names:** all invented, swept 2026-09-23 word-bounded across `design/ src/ infrastructure/state/ skills/` (probes `karrash` 6, `niim` 4, `hollu` 3) and against the Wookieepedia search API (probe `Tessek` → exact hit; every name below → no exact title). Four first drafts were renamed on hits: *Sheel* (canon Sheel Odala + our Tusken cast), *Yuun* (canon Gand), *Wesh* and *Oleen* (our Hutt cast-roster pawn names). No reused canon creature name anywhere in this doc.

## The Grey Sea (`RUT_GreySea` · `WaterOceanDeep` · saltwater)

**The water:** the planet's chemical works. Hypersaline, shrinking, one crystal-binding monoculture (the pillar-mason) building bone-pale columns toward light that never arrives; everything soluble concentrates downward; the dead are jacketed in mineral where they sank and never rot (`the_grey_deep.md` §4–§6). **Bans respected:** no glow of any kind below (ban 4 — the giant's mate-mark is the only light, so nothing in this table is bioluminescent, which is exactly why the Twilight got the glow instead); no schools or swarms (the Grey Deep roster note, 2026-09-10: *"Schools and swarms stay out of the Grey — anything that schools lives in the Twilight Deep"*), so **there is no shoal register here and no swarm pairing** — every catch is a solitary, and every floor pairing is a single animal; no Earth organism by name or read (ban 6); no decay of the encased (ban 5 — the rare table's cameo is that law made portable). **Palette:** every grey, bone-pale, crystal white, the murk's green cast. **Register:** timorous, sickly, extremophile, alien saline — crusty bits and shell on nearly everything.

Canonical band pair: **saltwater_\*** (`WaterOceanDeep` and the shore's `WaterOceanShallow` both declare `Saltwater`; terminator_sea ban: no freshwater organisms). `maxFishPopulation` **120** — a chemistry, not a fishery, but seven kinds need room: below the Twilight's 700 by a long way, above the Scald's 30.

| defName | label | kind | band | commonality | exists? | floor pairing | art |
|---|---|---|---|---|---|---|---|
| `RUT_Sallik` | sallik | crustacean | saltwater_Common | 1.2 | NEW | owed: single | NEW icon |
| `RUT_Karrud` | karrud | fish | saltwater_Common | 1.0 | NEW | owed: single | NEW icon |
| `RUT_Hessal` | hessal | shellfish | saltwater_Common | 1.0 | NEW | owed: single (sessile — a floor "animal" that does not move; see note) | NEW icon |
| `RUT_Oomal` | oomal | eel | saltwater_Common | 0.6 | NEW | owed: single | NEW icon |
| `RUT_Maalu` | maalu | alien (jellyfish-analog) | saltwater_Uncommon | 1.0 | NEW | owed: single | NEW icon |
| `RUT_Immu` | immu | fish | saltwater_Uncommon | 0.7 | NEW | owed: single | NEW icon |
| `RUT_Haarn` | haarn | alien | saltwater_Uncommon | 0.4 | NEW | owed: single | NEW icon |
| — | rare | — | `rareCatchesSetMaker` → `RUT_RareGreyCatches` | — | NEW | — | see `## Rare-catch tables` |

Kinds: 2 fish, 1 eel, 1 crustacean, 1 shellfish, 2 alien. Seven catches, all new.

**sallik** — crustacean, common. *salt-hermit.*
> A thumb-sized crab-thing that never grew a shell of its own: it excretes the salt it cannot keep out and wears the crust, layer on layer, until it is a walking lump of the sea's own mineral with legs underneath. Touch the water and every sallik within reach pulls its legs in and becomes a pebble. Cracked open there is very little in it, and that little is salt-sweet and good. The crusts are kept by the shore-folk, who say no two are alike.

Stats: crustacean envelope, Nutrition 0.15 (below the register — mostly crust), MarketValue 7, Mass 0.6, rot 3 d. Sensory hook: crust, timorous. `-ik` small-quick root.

**karrud** — fish, common. *crust-back.*
> A slab-flat, palm-wide fish-thing that has given up swimming for lying still. The upper face grows a plate of pillar-mineral — the sea builds on anything that holds still long enough, and the karrud holds very still — so from above it is a chip of grey stone with a mouth-slit underneath. It moves only when the brine at the bottom gets too strong even for it, sliding uphill along the pillar bases a hand's width at a time. Beneath the plate the flesh is pale and soft and tastes faintly of rock.

Stats: shoal envelope (Nutrition 0.25 / MarketValue 6.5 / Mass 0.5 / rot 2 d). Sensory hook: extremophile, crusty. `karr-` chitin root deliberately on a fish — it wears armour it did not grow. ⚑ Allowed to be fish-shaped? No — it is a plate with a mouth; the art brief is *a stone chip*, no fins drawn.

**hessal** — shellfish, common. *the sealed.*
> A bivalve-thing whose two shells are grown from the sea's crystal rather than from anything living, so a hessal bed reads as a patch of frost on the floor. It seals itself for years at a stretch when the brine thickens and reopens when the fog-season thins it, and nobody has seen one open. Prised apart it holds a knot of grey meat that keeps for a week in its own salt and tastes of nothing but the sea. The Homestead sites on the margin live on them.

Stats: shellfish envelope (Nutrition 0.15 / MarketValue 5 / Mass 0.7 / rot 5 d). Sensory hook: shell, extremophile (halophile that seals). Floor pairing note: the hessal is sessile; its "floor animal" is a non-moving creature def (`moveSpeed` near 0, no wander — the `RUT_GreatboleCore`-style marker shape is the wrong tool; a real Pawn with no movement is the right one) so a diver sees the beds the catch descriptions promise. ⚑ If a motionless pawn misbehaves in the engine, fall back to a bed as *floor terrain/scatter* and record hessal as "catch-only, reason: sessile".

**oomal** — eel, common (0.6). *the pallid.*
> A blind, arm-long brine-eel the colour of boiled paper, so translucent the salt-crust it has swallowed shows as a grey line down the middle of it. It lives in the silt at the pillar feet and does not come up; the shore-nets take it when the bottom-brine surges. It is always sick — every oomal carries lesions where the salt has got in — and it is never fast. Shore-folk eat it and say it is better than it looks, which is not a high bar.

Stats: eel envelope (vanilla FishBase, rot 2 d). Sensory hook: sickly, pale, timorous. Nothing to do with the Weeping Stones' warm-throat *ozhu* — different water, different root.

**maalu** — alien (jellyfish-analog), uncommon. *sick-bell.*
> A bell of grey jelly the size of two hands that has half turned to stone: the sea's crystal grows into it from the rim inward, and a maalu drifts with the weight of its own mineral edge pulling it down, sagging, tilting, never quite sinking. It is not luminous — nothing down here is — and it is not dangerous; it is barely alive. Netted, the crystal rim crumbles and the jelly inside is a mouthful of salt water. Some pilgrims eat it for the rim, which they say tastes of the pillars.

Stats: jellyfish envelope (Nutrition 0.08 / MarketValue 4 / Mass 0.3 / rot 1 d / raw poison 0.05). Sensory hook: sickly, crusty edge, no glow (ban 4 held explicitly).

**immu** — fish, uncommon (0.7). *the lodger.*
> A finger-long, soft, eyeless fish-thing that lives inside the shells of dead hessal — it never grew any armour of its own and borrows the sea's. Lift a shell and it is there, curled, and it will not leave: shore-folk carry the shell home and shake it out over the pan. It is the most timid thing in the Grey and the only one with any colour, a faint sick pink under the skin. Sweet, small, and mostly bones.

Stats: shoal envelope, MarketValue 6, Mass 0.3. Sensory hook: timorous, shell (borrowed). ⚑ The one colour note in the table is a *pink under skin*, not a saturated mark — the giant's mate-mark stays the Grey's one saturated colour (`terminator_sea.md` §4).

**haarn** — alien, uncommon (0.4). *the encased.*
> Nobody agrees what a haarn is. It is a jacket of pillar-mineral the size of a helmet, closed all round, that moves — slowly, along the floor, from pillar to pillar, leaving a scrape-line in the silt like a very small version of the giant's. Cut open there is a soft thing inside with no eyes and a great many small hooks, and it dies at once in open air. It is the Grey's only true extremophile: it lives in the strongest brine at the bottom, where nothing else survives, and it has plainly been doing so for a very long time. Divers who find one do not report it, on the grounds that it seems to have been minding its own business.

Stats: alien — Nutrition 0.20, MarketValue 8 (the jacket sells as a curiosity), Mass 0.8, rot 4 d, `Beauty 1`. Sensory hook: crust as the whole body, extremophile, alien. Its scrape-line is a deliberate echo of the crusted giant's tell (`the_grey_deep.md` §4) at toy scale — a diver learns the small scrape before meeting the big one.

## The Twilight Sea (`RUT_TwilightSea` · `WaterOceanDeep` · saltwater)

**The water:** the mat-roof sea — one mold organism shore to shore, light columns through the skylights the gardener keeps open, kelp forests under them, ceiling gardens dripping detritus, mud channels, the shoals, the one true predator (`the_twilight_deep.md` §4). The only water on the planet that populates *generously* by ruling (*"yes, and another"*). **Bans respected:** nothing crowds above the roof (ban 1 — the catch is served at the shore by `mandrake.rm.seashores`, and "Just make the surface fishable" (owner, 2026-09-20) is what put the table on the def at all); no Earth organism by name or read (ban 6); no roof without the gardener (the rare table never touches `RSW_Lanternwhale`). **Palette:** deep greens, kelp bronze, mat-pale ceiling, silver shoal-flash, lamp gold. **Register (owner, 2026-09-24):** glowing bits, elegant lines.

**What is built (MEASURED — `RUT_TwilightFish_Niim.xml` + `BiomeFishTypes_TwilightDeep.xml`):** eight catch items and the binding, `maxFishPopulation` 700, `RUT_RareTwilightCatches` with three options. The eight stand as written; every weight is kept. **The revisit is two things:** (1) the eight were designed before the "glowing bits" brief, and only two of them glow — so each existing row below carries a one-line *glow note* that becomes the art brief and, where the description is silent, a phrase the def build may add to the description (the description text itself is not reopened otherwise); (2) two NEW catches are added to bring the glow-and-elegance register up to the owner's read of the water, one common and one uncommon, and to give the Twilight a **shellfish** (the one kind the eight lack).

Canonical band pair: **saltwater_\*** (already built that way; `WaterOceanDeep`/`WaterOceanShallow` are Saltwater). `maxFishPopulation` 700 stands (the built value, "against the Greentide's 720 as the ceiling").

| defName | label | kind | band | commonality | exists? | floor pairing | art |
|---|---|---|---|---|---|---|---|
| `RUT_Niim` | niim | fish (shoal) | saltwater_Common | 1.5 | BUILT `RUT_TwilightFish_Niim.xml` | **owed: swarm** (the one swarm creature this sea gets — `SeaBeasts_Swarm.xml` is the file to grow) | NEW icon (placeholder `swplants/Bloddle/BloddleA`) |
| `RUT_Pallu` | pallu | floater | saltwater_Common | 1.0 | BUILT | owed: single | NEW icon (placeholder `AloeVeraB`) |
| `RUT_Tikkarr` | tikkarr | crustacean | saltwater_Common | 0.8 | BUILT | owed: single | NEW icon (placeholder `PincushionPlantB`) |
| `RUT_Nuudal` | nuudal | cucumber | saltwater_Common | 0.6 | BUILT | owed: single | NEW icon (placeholder `SweetheartPlantB`) |
| `RUT_Aluun` | aluun | shellfish | saltwater_Common | 0.6 | NEW | owed: single (sessile, same shape as the Grey's hessal) | NEW icon |
| `RUT_Kellu` | kellu | squid | saltwater_Uncommon | 1.0 | BUILT | owed: single | NEW icon (placeholder `SnakePlantB`) |
| `RUT_Murrol` | murrol | eel | saltwater_Uncommon | 0.8 | BUILT | owed: single | NEW icon (placeholder `SchlumbergeraB`) |
| `RUT_Hollu` | hollu | jellyfish | saltwater_Uncommon | 0.8 | BUILT | owed: single | NEW icon (placeholder `JadePlantB`) |
| `RUT_Liiru` | liiru | eel | saltwater_Uncommon | 0.5 | NEW | owed: single | NEW icon |
| `RUT_Oobo` | oobo | octopus | saltwater_Uncommon | 0.4 | BUILT | owed: single | NEW icon (placeholder `EcheveriaB`) |
| — | rare | — | `rareCatchesSetMaker` → `RUT_RareTwilightCatches` | — | BUILT (3 options) | — | — |

Kinds: 1 shoal fish, 2 eels, 1 crustacean, 1 shellfish, 1 squid, 1 octopus, 1 floater, 1 jellyfish, 1 cucumber. Ten catches: 8 built, 2 new.

**Glow notes on the built eight** (art brief; the bracketed phrase may be appended to the description at build time where noted):
- **niim** — already glows: "a dot-line of cold light along the flank." Art: the dot-line is the icon's one bright element; a shoal *flash* in the stack art.
- **pallu** — the green symbiont mat on its upper face **glows faintly in the dark between columns** [add: *"and in the dark between columns a sinking pallu is a small green lamp going out."*]. Elegant: a saucer, a disc, a face turned to the light.
- **tikkarr** — no glow (it is the pest, kelp-coloured, clinging); elegant only in the length of leg. Art: long-limbed, the kelp bronze of the palette. The one deliberately dull entry — a table needs one.
- **nuudal** — no glow; mottled. Art: soft, long, cattle-plain. The second dull entry; the floor is where the light does not reach.
- **kellu** — **ink-black with a single cold-blue line down each arm** [add: *"a line of blue light runs each arm, and the kelp squid hunts by putting it out."*]. Elegant: the arms, the taper.
- **murrol** — no glow; blunt and fat by design ("the fat slow thing"). Art: mud-brown, comfortable. Dull entry three; three of ten is the ceiling.
- **hollu** — already glows by implication (pulsing bell falling through a column); make it explicit in art: a **soft gold pulse** in the bell, lamp gold from the palette. [add: *"It lights as it falls."*]
- **oobo** — **the underside of the arms carries a ring of pale points** [add: *"the underside of every arm is ringed in pale light, which is the last thing the thing below it sees."*]. Elegant: wide, slow, a dropped veil.

**aluun** — shellfish, common (0.6). *the lamp-shell.*
> A fan-shaped shell-thing that grows on the kelp stems in the light columns, two thin translucent valves held open to the fall of detritus, and inside them a mantle that lights — a steady pale gold, the colour of the palette's lamps, bright enough that a kelp tower hung with aluun reads from the shore as a column of small windows. The Compact harvests them by the stem. The meat is a coin of sweet white flesh; the valves, dried, are the lantern-panes in every deep dock.

Stats: shellfish envelope (Nutrition 0.15 / MarketValue 5 / Mass 0.7 / rot 5 d). Sensory hook: glow, elegant lines (a fan), the palette's lamp gold made literal. Sessile: same floor-pairing shape as the Grey's hessal. Name: soft register.

**liiru** — eel, uncommon (0.5). *the ribbon.*
> The Twilight's elegant thing: a ribbon-eel as long as an arm and no wider than a finger, that swims upright through the light columns in slow vertical S-curves, and carries along its whole length a single unbroken line of blue-white light. A column with liiru in it looks, from the bank, as if someone had drawn on the water. It eats what falls, it is eaten by the kellu, and it is not fast; it does not need to be, because nothing wants the trouble of a mouthful of ribbon. Netted, it is a long thin excellent meal and a light that takes a minute to go out.

Stats: eel envelope (vanilla FishBase tier), MarketValue 7 (a little prized, for the look), rot 2 d. Sensory hook: glow as a line, elegance as a curve. ⚑ Relationship to the built niim: both blue-white; the art must separate them — niim a *dotted* line on a fish body, liiru a *continuous* line on a ribbon with no fish silhouette at all.

**Twilight note on the roster JSON:** `rosters/the_twilight_sea.json` lists floor fauna the live def does not carry (`RSW_OpeeSeaKiller`, `RSW_AbyssalColo`, `RSW_CrimsonOpee`, `RSW_Starmaw`, `RSW_StormSando`, `Yobshrimp`, the tumorfish trio, `StoneCrab`) — those are the *floor* half's inputs for the TERMINALBIOMES sitting, not catches, and this doc does not move them. ⚠️ `RSW_ColoClawFish`'s corpse is the built rare table's third option here, while `the_scald.json` rosters the live creature in the Scald; that is a multi-homing row for the Scald's own sitting (`BIOME_SPECIFIC_FAUNA_LAW_1` — annotate, never cut), not a defect in this table.

## The Propane Lake (`RUT_PropaneLake` · `AB_PropaneLake` · not water)

**The liquid:** Umbra — the planet's fuel tank. Liquid propane at cryogenic cold under the brightest aurora on the planet, ringed by a crust of the same compound frozen solid; it snows fuel (hydrocarbon and ammonia precipitation), and the crystal flora — crystal horn, frost leaf, ⭐ rime nodules with their euphoric sacs — is *partially inorganic and regrows overnight from what falls* (`the_propane_lakes.md` §0, §4, §4b). Ammonia is the polar solvent here and builds the Flats' life; propane is the medium that lets the nightside's butane/pentane biochemistry *get big*. The sea's own exotics are ruled: the V-wake creature and its kin, propane-native, agitated by pumping. **Bans respected:** no icy dayside analog (ban 1 — nothing here is a cold-water fish; every entry is hydrocarbon- or ammonia-metabolic); 🔴 **none of it is kyber** (ban 2 — the crystal here is frozen hydrocarbon and mineral, never a lightsaber part, and the rare table says so in its def comment); no ignition by fiat (ban 4 — the catches are *flammable*, they do not ignite anything); no transportable natives (ban 6 — the items are dead; the floor animals carry the R-H10 no-transport read). **Palette:** black mirror, aurora green/violet, crystal-clear and frost-white, blue running flame.

**What "fishing" pulls out, and why it is worth pulling.** Nothing here is a water fish. What a line or net brings up from the fuel is **crystalline life** — organisms that build their bodies from the fuel snow, half organic and half frozen hydrocarbon lattice, cold enough to burn the hand that lands them. They are edible only barely and only cooked (the hydrocarbon fraction boils off in the pan — every entry is RawBad with a raw poison chance, and their Nutrition is the lowest of any sea), and what makes them a catch worth the cold is that **every one of them is fuel**: `Flammability 1.0` on every item, and the rare table pays out in `Chemfuel`. A Propane Lake shore is fished for the stove and the tank as much as for the plate — the one sea on the planet where the catch is worth more burned than eaten. The sole exception is the euphoric: the *oddu* is kin to the rime nodule and carries the same mild joy, which is why the Flats' scrapers fish at all.

Canonical band pair: **saltwater_\***, and this is a build decision, not a default. 🔴 **MEASURED against the engine (RimSage, 2026-09-23):** `WaterBodyTracker` forms a water body only where the terrain's `waterBodyType != None` (`WaterBodyTracker.cs:50, :81, :178`), `Designator_ZoneAdd_Fishing` refuses a cell whose type is `None` **or whose terrain is Impassable** (`Designator_ZoneAdd_Fishing.cs:65`), and `FishingUtility` returns nothing for a `None` body (`FishingUtility.cs:138`). The donor `AB_PropaneLake` is `waterBodyType None`, Impassable (`RUT_PropaneLake.xml` header, read off the live dump) — so **as shipped, no propane cell can ever hold a fishing zone, whatever the table says.** ⇒ The build owes a FlowWorks' `RM_PropaneShallow` (owner card 2026-09-24: the shore uses FlowWorks' own propane suite, `RM_PropaneShallow`/`RM_PropaneDeep`, whose row in `generate_liquid_suite.py` now carries `waterBodyType Saltwater`; a duplicate FlowWorks' `RM_PropaneShallow` was shipped and then deleted the same day) laid by the seashores extension's `shallowTerrain` (today `AB_SolidPropane`, which is solid ground and not a water body either): passable, `waterBodyType Saltwater`, `tags Water`. *Saltwater* rather than Freshwater because DBH and every drink-from-terrain mechanism read Freshwater as potable, and the def header's reason for `None` was exactly "correctly not recognised as drinkable water"; Saltwater keeps that property and is fishable. The table is authored under `saltwater_*` to match. `providesCatch` on the Propane Lake's `RM_SeaShoreExtension` flips from `false` to `true` — its comment ("whether fishing is even the right verb for a lake of fuel is an open design question") is answered by the owner's brief above. `maxFishPopulation` **60** — sparse; a fuel tank is not a fishery.

| defName | label | kind | band | commonality | exists? | floor pairing | art |
|---|---|---|---|---|---|---|---|
| `RUT_Fessu` | fessu | fish | saltwater_Common | 1.2 | NEW | owed: single | NEW icon |
| `RUT_Krellik` | krellik | crustacean | saltwater_Common | 1.0 | NEW | owed: single | NEW icon |
| `RUT_Oddu` | oddu | shellfish | saltwater_Common | 0.8 | NEW | owed: single (sessile) | NEW icon |
| `RUT_Oovu` | oovu | floater (jellyfish-analog) | saltwater_Common | 0.6 | NEW | owed: single | NEW icon |
| `RUT_Iliss` | iliss | eel | saltwater_Uncommon | 1.0 | NEW | owed: single | NEW icon |
| `RUT_Tarnn` | tarnn | alien | saltwater_Uncommon | 0.6 | NEW | owed: single (sessile colony) | NEW icon |
| `RUT_Zhiil` | zhiil | alien | saltwater_Uncommon | 0.4 | NEW | **the V-wake exotic** (owed creature, `the_propane_lakes.json` new_defs) — a life stage, per the owner's carve-out | NEW icon |
| — | rare | — | `rareCatchesSetMaker` → `RUT_RarePropaneCatches` | — | NEW | — | see `## Rare-catch tables` |

Kinds: 1 fish, 1 eel, 1 crustacean, 1 shellfish, 1 floater, 2 alien. Seven catches, all new. Common to all: `Flammability 1.0`, `preferability RawBad`, `FoodPoisonChanceFixedHuman` 0.08 raw (cooking removes it, as vanilla), and a `description` that says it burns.

**fessu** — fish, common (1.2). *the flake.*
> A hand-wide, paper-thin fish-thing that is more crystal than flesh: a translucent lattice of frozen hydrocarbon grown around a thread of something alive, flat as a snowflake, drifting edge-on through the fuel where the snow falls thickest. It feeds by growing — each night's fall adds a rim to it, and an old fessu is a plate. Landed it steams in the cold, and it is so light it can be held up to the aurora and read through. Cooked it is a thin bitter wafer that burns blue if you leave it in the pan.

Stats: Nutrition 0.10, MarketValue 6, Mass 0.2, rot 3 d. Sensory hook: crystalline, snow-fed. ⚑ The one fish-*kind* entry here is a snowflake, not a fish silhouette — the recognizability rule holds.

**krellik** — crustacean, common. *rime-crab.*
> A crab-thing plated in hydrocarbon frost, each plate a clear crystal grown from the fuel snow and shed and regrown nightly, so a krellik is always half new. It walks the solid propane at the lake's edge and the floor beneath, picking at the crystal flora's fallen fragments, and it is the one thing on the shore the Frostmite will not eat — the shell is too cold even for that. Cracked, the plates ring like glass. The meat inside is dense and oily and takes fire the moment it dries.

Stats: crustacean envelope (Nutrition 0.20 / MarketValue 7 / Mass 0.6 / rot 3 d). Sensory hook: crystal plates, regrown overnight (the flora's rule on an animal). `-ik` root.

**oddu** — shellfish, common (0.8). *the sac.*
> Kin to the rime nodule and the reason anyone fishes this shore: a fist-sized shell-thing that sits in the fuel and does what the nodule does on land — draws propane out of its surroundings into a sac of clear jelly that is, eaten, a very mild euphoric. The shell is frost-white and closes when the aurora fades. Raised from the lake it is cold enough to burn, and the scrapers of the Flats carry them home in mittens to eat by the tap-wire, which is as close to a good evening as the nightside offers.

Stats: shellfish envelope (Nutrition 0.15 / MarketValue 9 / Mass 0.7 / rot 5 d) — MarketValue above the register for the drug, still under the octopus/drazz ceiling. ⚑ Optional, drazz-precedent: `outcomeDoers` → a small joy/euphoria hediff on ingestion (whatever `AB_RimeNodules`'s harvested product already uses; if the donor ships a hediff, reuse it under `MayRequire`, never invent a second euphoric). Sensory hook: the documented crystalline life, made a catch.

**oovu** — floater (jellyfish-analog), common (0.6). *frost-bell.*
> A bell of frozen hydrocarbon jelly that rides at the surface of the fuel where the snow lands, catching it — a floating cup with a crystal rim, tipping and righting, faintly green under the aurora because the aurora is the only light. It has no sting; it has almost nothing. Netted it is a bell of propane with a frost crust, and the shore-folk keep them for the lamp, not the pot: an oovu on a wire burns steadily for an hour.

Stats: floater envelope (Nutrition 0.10 / MarketValue 3 / Mass 0.2 / rot 1 d). Sensory hook: the fuel-snow catcher; the only "glow" here is reflected aurora, never bioluminescence (that is the Twilight's).

**iliss** — eel, uncommon. *wire-eel.*
> A wire-thin eel the length of a forearm, black, with a spine of conductive mineral that the auroral ground currents run through — it lives along the bed of the lake where the electrojet's currents cross, and on a reconnection night the whole floor of a bay hums with them. It hunts nothing; it feeds on the charge, or on what the charge kills. Landed on a wet line it bites with a shock that has knocked scrapers down. Cooked, it is a good oily eel. Raw, it is still live in a sense that matters.

Stats: eel envelope, MarketValue 7, Mass 0.4, rot 2 d. ⚑ Optional, drazz-precedent: `outcomeDoers` → the same short "shock" hediff `RUT_Drazz` ships (§4.3 of the commission, ruled in for v1) on RAW ingestion — reuse, never a second def. Sensory hook: the electrojet made animal (`the_propane_lakes.md` §7 tap).

**tarnn** — alien, uncommon (0.6). *the lattice.*
> A colony, not a creature — or a creature that grew like a colony. A branching lattice of clear crystal the size of a bucket, half of it frozen hydrocarbon and half of it something alive threaded through the crystal, growing a hand's width every night from the fuel snow and fracturing back when the aurora is weak. It is the sea's version of the crystal flora on the shore, and nobody has decided which side of the line it stands on. A net brings up a piece of it. The piece keeps growing on the shore for a day, then stops. Chipped and boiled it is bitter and it is barely food; dried it is the best kindling on the nightside.

Stats: alien — Nutrition 0.08, MarketValue 8 (crystal curiosity), Mass 0.8, rot 6 d, `Beauty 2`. Sensory hook: the crystalline life, partially inorganic, the 1-day regrow rule on a catch. 🔴 Not kyber; the def comment says so.

**zhiil** — alien, uncommon (0.4). *wake-fry.*
> The young of the thing that makes the V-wake. Hand-long, black, ridged, a body built of the same propane-native chemistry as its parent and already agitated by anything that moves in the fuel — a zhiil in a net thrashes until it freezes solid, and then it is a spiny black icicle that thaws back to thrashing on the fire. Scrapers who have fished up a zhiil pull the line and leave, because the parent is a thing that attacks pipe on sight and has a fairly clear idea of where its young went.

Stats: alien — Nutrition 0.15, MarketValue 5, Mass 0.4, rot 2 d. Floor pairing: **the V-wake exotic** (an owed creature by the sheet, `the_propane_lakes.json` new_defs row 2) is the adult; this is the life-stage carve-out the owner named (*"young versions that grow ... then migrate"*) used the right way round — the catch is the young, the floor animal is the adult, one species, two defs, and the fiction links them. `zh-` sibilant root for a reptile-adjacent thing.

## The Scald (`RUT_TheScald` · `RUT_ScaldWaterOceanDeep` · boiling brine)

**The water:** the roiling wonder. Boiling, fouled mineral brine — never potable (ban 1), fouled not toxic; rainbow welcome-blanket mats banded by temperature; armoured bottom-walker herds mowing the mats at depth where the boil gentles to mere heat; their dung is the water column's whole budget; the silver shoals work the dung-fall; the bubble-sailors ride the boil (`the_scald.md` §4). **Bans respected:** no macro-life in the boil itself (ban 4 — every entry lives at the margin, at depth, or on the vents, and comes up *already cooked* at the surface); no native land predator hunts the water (ban 3); no Earth organism (ban 6); never the terminator seas' biome (ban 2 — nothing here is shared with the Twilight or Grey tables). **Palette:** boiling white, scald cyan, thermophile rainbow, basalt black. **Register:** thermophile margin harvest — "water that burns and comforts in the same step" (§7).

**What is built (MEASURED — `RUT_ScaldFish.xml`, the def's own `fishTypes`, `RUT_RareScaldCatches.xml`):** five catch items on `freshwater_Common/Uncommon`, `maxFishPopulation` 30, one rare option. All five stand with their weights; the eesh/muddal/karrash/saal/bladderboil descriptions are final (owner ruling 5, 2026-09-18: nicknames are the shipped names). **Three NEW** catches bring the table to eight and add the two kinds it lacks (an eel, an alien) plus a second crustacean so the dung-fall economy has a small consumer beside the shoal.

Canonical band pair: **freshwater_\*** — and the reason is worth stating once so nobody "fixes" it. The Scald's *inland* fishing water (`waterDeepTerrain`/`waterShallowTerrain`/`waterMovingShallowTerrain`/`waterMovingChestDeepTerrain` → `RUT_ScaldWaterDeep/Shallow/MovingShallow/MovingChestDeep`) inherits **Freshwater** from Core's `WaterDeepBase`/`WaterShallowBase` parents (measured in `RUT_ScaldFish.xml`'s header), so vanilla's own path serves `freshwater_*` on any Scald-biome river or pool. The sea tile's `RUT_ScaldWaterOceanDeep` and the seashores' `RUT_ScaldWaterOceanShallow` declare **Saltwater** — and `mandrake.rm.seashores` falls back to the freshwater pair on a Saltwater shore when the saltwater pair is empty (`RM_SeaShoresHarmony.cs:141`). One table, both routes, no duplication. ⛔ Do not copy the table into `saltwater_*` "for correctness": two copies drift. (Fiction-wise the Scald is brine and "salt" is the truer word; the engine-wise answer is the one that keeps one table.) `maxFishPopulation` **40** — up from 30 for eight kinds; still the smallest fishery on the planet, a margin harvest.

| defName | label | kind | band | commonality | exists? | floor pairing | art |
|---|---|---|---|---|---|---|---|
| `RUT_Eesh` | eesh | fish (shoal) | freshwater_Common | 1.5 | BUILT `RUT_ScaldFish.xml` | **owed: swarm** (the silver shoal creature — `the_scald.json` new_defs row 3, the sea's one swarm) | NEW icon (placeholder `ToxicMeat_a`) |
| `RUT_Muddal` | muddal | cucumber | freshwater_Common | 0.8 | BUILT | owed: single | NEW icon (placeholder `ToxicMeat_b`) |
| `RUT_Doss` | doss | crustacean | freshwater_Common | 0.7 | NEW | owed: single | NEW icon |
| `RUT_Thuum` | thuum | eel | freshwater_Common | 0.5 | NEW | owed: single | NEW icon |
| `RUT_Karrash` | karrash | crustacean | freshwater_Uncommon | 1.0 | BUILT | owed: single | NEW icon (placeholder `ToxicMeat_c`) |
| `RUT_Saal` | saal | jellyfish | freshwater_Uncommon | 0.5 | BUILT | **the bubble-sailor creature** (`the_scald.json` new_defs row 2 — owed, C# bubble-line locomotion) | NEW icon (placeholder `JawaClaimRumour`) |
| `RUT_BladderboilCatch` | bladderboil | floater | freshwater_Uncommon | 0.5 | BUILT | **`RUT_Bladderboil`** pawn (owed by `RUT_hydrocarbon_ecology_commission.md` §10c — two defs by that doc's design) | NEW icon (placeholder `RUT_Greenwood`) |
| `RUT_Ekkel` | ekkel | alien | freshwater_Uncommon | 0.4 | NEW | owed: single | NEW icon |
| — | rare | — | `rareCatchesSetMaker` → `RUT_RareScaldCatches` | — | BUILT (1 option) — **extended**, see `## Rare-catch tables` | — | — |

Kinds: 1 shoal fish, 1 eel, 2 crustaceans, 1 jellyfish, 1 floater, 1 cucumber, 1 alien. Eight catches: 5 built, 3 new.

**doss** — crustacean, common (0.7). *dung-shrimp.*
> The eesh's small competitor: a finger-length, hunch-backed shrimp-thing, boiled pink from birth, that works the dung-fall from below where the shoals work it from above — picking over what settles on the mats before the muddal get to it. It is everywhere at the margins in the warm season and it is the pilgrims' snack, gathered with a cloth and eaten from the hand, already cooked like everything here. There is very little to one. There are always more.

Stats: crustacean envelope, Nutrition 0.15, MarketValue 5 (the cheap catch), Mass 0.4, rot 3 d; `preferability RawTasty` (comes up cooked — the muddal's register-break, justified by the same water). Sensory hook: thermophile, the dung economy at hand scale. ⚑ Not a swarm creature on the floor: single pairing; the *eesh* is this sea's one swarm.

**thuum** — eel, common (0.5). *blanket-eel.*
> An eel that lives *under* the crowncarpet mats — between the rainbow mat and the rock, in the thin hot film where the mat is thickest — and takes the pigment into its skin the way the muddal does, so a thuum is banded down its whole length in the mat's own colours, and a pilgrim who lifts a mat-edge at the baths sometimes finds one lying there like a strip of the Scald's oldest truth that has learned to move. It comes up cooked, and it is the margin's best eating after the eesh — richer, and the bands hold in the pan.

Stats: eel envelope (vanilla FishBase tier), rot 1 d (cooked flesh, keeps worse — the eesh's precedent), `preferability RawTasty`. Sensory hook: the thermophile rainbow on an animal; the pigment harvest's living neighbour.

**ekkel** — alien, uncommon (0.4). *the tumbler.*
> Nobody knows which way up an ekkel goes. A fist-sized knot of stiff, heat-mirror filaments — the eesh's skin grown into a tangle — that lives on the vent walls beside the karrash and rolls: it lets go, tumbles down the chimney in the boil-current flashing like a dropped handful of needles, catches, climbs, and lets go again. It is feeding, somehow, on the mat. Netted it is a ball of hot wire with a soft thing at the centre that is already cooked and tastes of the vents, which is to say of metal and something older. Rim-pilgrims keep the filament-knots; they stay bright for years.

Stats: alien — Nutrition 0.12, MarketValue 8 (the knot sells), Mass 0.3, rot 2 d, `Beauty 2`, `preferability RawTasty`. Sensory hook: the heat-mirror register (eesh's) on a thing that is not a fish at all; the vent chimneys as the karrash's neighbourhood.

## Rare-catch tables

Template: `src/RimUtinni/UtinniPatches/Defs/ThingSetMakerDefs/RUT_RareScaldCatches.xml` — `ThingSetMakerDef ParentName="RareFishingCatchesBase"`, `root Class="ThingSetMaker_RandomOption"`, each option a `weight` + `ThingSetMaker_StackCount` with a `thingDefs` filter and a `countRange`. ⛔ No corpse option in the Grey or Propane tables — neither water has a predator that would leave one and the Grey's dead do not rot (ban 5).

| sea | defName | options (weight · thing · count) |
|---|---|---|
| Grey Sea | `RUT_RareGreyCatches` (NEW) | 4 · **`RUT_SaltCameo`** ×1 — NEW prize item, `ResourceBase`/ExoticMisc like `RUT_SeepStone`: a small creature jacketed in pillar-mineral, the statuary made portable; MarketValue ~30, Beauty 4, never rots (ban 5 in a stat) · 2 · `RUT_Hessal` ×4–6 — "a bed of the sealed came up whole" · 1 · `Silver` ×5–15 — "somebody's ring, still in its jacket, chiselled out on the shore" (one thing per option in this template) |
| Twilight Sea | `RUT_RareTwilightCatches` (BUILT, 3 options) | stands: 4 · `RUT_LampBlack` ×1–2 · 2 · `RUT_Niim` ×8–12 · 1 · `RSW_ColoClawFish` corpse ×1. **+1 option:** 1 · `RUT_Aluun` ×6–10 — "a whole stem of lamp-shells, still lit" |
| Propane Lake | `RUT_RarePropaneCatches` (NEW) | 4 · `Chemfuel` ×10–20 — "a sac of pooled fuel, frozen round the line" (vanilla def; the tank's own catch) · 2 · **`RUT_AuroraGlass`** ×1 — NEW prize item, ExoticMisc, MarketValue ~30, Beauty 4, `Flammability 0`: a fist of clear hydrocarbon-mineral crystal grown in the lake bed, aurora-green when lit from behind. 🔴 Def comment: *not kyber, carries no lightsaber property, never will* (ban 2) · 1 · `RUT_Oddu` ×4–6 — "a good evening's worth" |
| Scald | `RUT_RareScaldCatches` (BUILT, 1 option) | stands: 3 · `RUT_Karrash` ×2. **+2 options** to reach the template's ≥2: 2 · `RUT_Ekkel` ×2–3 — "a whole tumble, caught mid-fall" · 1 · the rainbow-pigment scrap the commission §2E.rare already names (2–4 of whatever pigment product the welcome-blanket flora entry ships; **omitted, not invented, if none exists at build time** — that instruction stands verbatim) |

## Superseded rulings

Each of these is overridden by the owner's sentence *"Please flesh all of these out to make each of them hold at least seven varied and interesting catches that make sense"* (2026-09-24, above). Nothing else in those documents is reopened.

1. **`fish_bestiary_commission_2026-09-10.md` §3**, restating `rosters/_fish_assignment_proposal.md` §3: *"the_grey_sea — surface AND Grey Deep … saturated brine, monoculture, planetary no-schools ban; three-resident cap; 'its water is a chemistry, not a fishery'; no analogs owed."* — **superseded** for the catch table only. The no-schools part is *kept* (no shoal register, no swarm pairing in the Grey); the three-resident cap was already released 2026-09-10 (`the_grey_deep.md` §4 note).
2. **Same §3:** *"the_propane_lakes — liquid propane at ~−79 °C; the sea's life is the propane-native exotics — CREATURES owed as new defs, never fishTypes."* — **superseded**: the Propane Lake now carries a `fishTypes` table. The creatures remain owed (the V-wake exotic is now also the zhiil's floor pairing).
3. **`RUT_PropaneLake.xml`'s `RM_SeaShoreExtension` comment** (`SEA_FLOOR_AND_CATCH_PASS_1`, 2026-09-23): *"providesCatch is FALSE on purpose: whether 'fishing' is even the right verb for a lake of fuel is an open design question, and this file must not answer it by default."* — **answered**: `providesCatch` → `true` at build. Likewise that item's spec step 5 (*"whether 'fishing' is even the right verb there is a design question, not a default. Ask rather than assume"*) is discharged by the brief.
4. **`fish_bestiary_commission_2026-09-10.md` §1 / §3's Twilight-*surface* no-fish line** was already superseded by *"Just make the surface fishable"* (owner, 2026-09-20, recorded in `BiomeFishTypes_TwilightDeep.xml`); nothing here reopens it — recorded so nobody re-derives the surface/deep split from this doc.
5. **`the_grey_deep.md` ban 2** (*"No schools, swarms, or added kinds — three residents; a fourth is a violation"*) — the *added kinds* clause is dead twice over (cap released 2026-09-10; seven catches ruled 2026-09-24) and the sheet still carries it: the biome sitting deletes the clause and keeps "no schools, swarms" (`deciding-and-superseding`: remove, do not annotate). Same for `terminator_sea.md` §6 *"No high species count … a rich fauna list is a violation"* as it applies to the two seas' **catch** tables — the floor/megafauna reading of it is untouched.

Not superseded, and the doc obeys them: Scald ban 4 (no macro-life in the boil), Grey Deep ban 4 (no glow), Propane ban 2 (no kyber), the anti-exponential law, the recognizability rule, and `the_scald.md` ban 2 (three seas, three defs — no shared species).

## Owed after this

Everything below is build work for `SEA_FLOOR_AND_CATCH_PASS_1` / `TERMINALBIOMES_RM_MOD_BUILD_1`; nothing in this doc writes XML.

**Defs (catch items) — 19 new `FishBase` items + 2 prize items + 2 new ThingSetMakerDefs + 2 extended:**
- Grey: `RUT_Sallik`, `RUT_Karrud`, `RUT_Hessal`, `RUT_Oomal`, `RUT_Maalu`, `RUT_Immu`, `RUT_Haarn`; `RUT_SaltCameo`; `RUT_RareGreyCatches`; `fishTypes` + `maxFishPopulation 120` on `RUT_GreySea` (on the def, per the seashores design — the catch is served from the SEA def).
- Twilight: `RUT_Aluun`, `RUT_Liiru`; patch `BiomeFishTypes_TwilightDeep.xml` adds the two rows; `RUT_RareTwilightCatches` +1 option; the four bracketed glow phrases appended to pallu/kellu/hollu/oobo descriptions.
- Propane: `RUT_Fessu`, `RUT_Krellik`, `RUT_Oddu`, `RUT_Oovu`, `RUT_Iliss`, `RUT_Tarnn`, `RUT_Zhiil`; `RUT_AuroraGlass`; `RUT_RarePropaneCatches`; `fishTypes` (saltwater_\*) + `maxFishPopulation 60` on `RUT_PropaneLake`; 🔴 **FlowWorks' `RM_PropaneShallow` (owner card 2026-09-24: the shore uses FlowWorks' own propane suite, `RM_PropaneShallow`/`RM_PropaneDeep`, whose row in `generate_liquid_suite.py` now carries `waterBodyType Saltwater`; a duplicate FlowWorks' `RM_PropaneShallow` was shipped and then deleted the same day)** (passable, `waterBodyType Saltwater`, `tags Water`, the donor's propane look) and the extension's `shallowTerrain` repointed to it, `providesCatch true`. Without the terrain the table is dead XML (engine read above).
- Scald: `RUT_Doss`, `RUT_Thuum`, `RUT_Ekkel`; `maxFishPopulation` 30 → 40; `RUT_RareScaldCatches` +2 options.
- Optional hediff reuse (drazz precedent, ruled in for v1 there): iliss raw shock = `RUT_Drazz`'s hediff; oddu euphoria = the rime-nodule product's hediff under `MayRequire`, if the donor ships one.

**Floor animals (the pairing rule) — 26 pairings, of which 2 are swarms, 4 are already-owed creatures, 20 are new singles:**
- Swarms (one per sea that has a shoal): the **niim** shoal creature (Twilight), the **eesh** silver-shoal creature (Scald). Grow `SeaBeasts_Swarm.xml` (that item's own instruction). The Grey and the Propane Lake get **no** swarm.
- Already owed elsewhere, now doubly owed: the bubble-sailor (saal), `RUT_Bladderboil` (bladderboil), the V-wake exotic (zhiil's adult).
- New single floor animals: Grey 7 (three sessile/near-sessile: hessal, haarn crawls, karrud lies still), Twilight 9 (aluun sessile), Propane 6 (oddu and tarnn sessile), Scald 6. ⚠️ Whether `<wildAnimals>` spawn at all on an `impassable=true` biome is still the Desktop's question (`SEA_FLOOR_AND_CATCH_PASS_1` Watch out) — settle it before authoring 20 pawns. ⚠️ `the_grey_deep.md` ban 1 (*no survivable brine-pool entry*) is in the same position the Scald's ban 4 was: superseded only as far as the DEEP/diving interaction by the owner's 2026-09-21 floor ruling; the Grey sitting annotates it the way the Scald's was.
- Megafauna stay floor-only, untouched: `RSW_Reefback`, `RSW_Lanternwhale`, `RSW_SandoAquaMonster`, `RSW_ElderSando`, and the roster JSONs' listed giants.

**Art — 34 NEW item icons**: every catch row above (Grey 7 + Twilight 10 + Propane 7 + Scald 8 = 32, of which 13 are built on placeholders and 19 are new) plus `RUT_SaltCameo` and `RUT_AuroraGlass`; none exists in the artpipe (measured above). Per §0's art law no placeholder may be a fish silhouette and no two entries in one table may share one. Direction per sea is in each section's palette line and each entry's sensory hook; the Twilight glow notes are the art brief for the built eight. Check `infrastructure/artpipe/done/` again by defName before queuing — the daemon runs continuously.

**Docs:** `the_grey_deep.md` §6 ban 2 and `terminator_sea.md` §6 species-count clause corrected (Superseded 5); `rosters/the_grey_sea.json`, `the_propane_lakes.json`, `the_twilight_sea.json`, `the_scald.json` `fish` arrays filled from these tables (the `fish ruling` strings in the first two say no-fish and are now false); `fish_bestiary_commission_2026-09-10.md` §1 gains four rows (or a pointer to this doc — pointer preferred, single-source); `SEA_FLOOR_AND_CATCH_PASS_1` step 5 marked designed.

**Tier:** every `RUT_` above is retiered to `RM_` at the TERMINALBIOMES sitting per Q12 — invented names are not IP (Q11a). This doc does not pre-empt that.

## Questions for the owner — ANSWERED 2026-09-24 (decisions taken by question card)

1. **Twilight glow: art only.** The eight built descriptions stay exactly as ruled final on 2026-09-18; the glow lives in the icon briefs.
2. **Propane catches as fuel: a MECHANIC.** `RUT_Make_ChemfuelFromPropaneCatch` on the vanilla `BiofuelRefinery` renders 10 catches into 35 chemfuel at 1200 work (`src/RimUtinni/UtinniPatches/Defs/RecipeDefs/RUT_PropaneCatch_Refining.xml`). The shore is a second fuel source beside the pipe; ban 5 (tankers) is untouched.
3. **The plain entries stay plain** (tikkarr, nuudal, murrol, oomal, hessal) — the ground the strange ones stand out from.

