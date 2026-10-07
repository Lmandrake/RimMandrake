# Tooke-trap plant

**defName**: `Plant_TookeTrap_Wild` (donor: Star Wars Animal Collection (Continued), `mlie.starwarsanimalcollection`).
It is cast in the Webwork (`RUT_Webwork`, 0.3) and the Greentide (`RUT_Greentide`, 0.5).
No owned `RSW_` port exists yet.

## Sourced text (Wookieepedia)
The plant has two articles. The canon one is thin and non-canon-tagged (LEGO). Most of the biology comes from the Legends one.

**Canon** (`Tooke-trap plant`, tagged non-canon: *LEGO Star Wars: The Skywalker Saga*, 2022). A carnivorous plant
native to Naboo, grown by Gungans. *"Tooke-trap plants were grown from seeds which would sprout into four-leafed
seedlings. Fully grown tooke-trap plants possessed a long stalk with a 'mouth' on the end, that protruded from a bush
that contained eight leaves. They would occasionally hiss."*

**Legends** (`Tooke-trap plant/Legends`, first appearance *Star Wars Episode I: The Gungan Frontier*; sources *The
Wildlife of Star Wars: A Field Guide*, *The Complete Star Wars Encyclopedia*). Native to the Gungan-occupied swamps
of Naboo. *"They were carnivorous plants that possessed between one and four stalks, each with a 'mouth' on the end,
that protruded from a leafy central bush. Though these plants could survive solely on water and sunlight like a
normal plant, tooke-traps also preyed on small rodents and small arthropods (especially insects). Their main prey was
the tooke, from which the species derived its common name. Because the fragrance it emitted was identical to that of
tooke mating pheromones, tookes found it irresistible. Gungans found the carnivorous plants to be excellent house
plants."*

Ecology, also Legends:
- It forms a symbiosis with **shiros**, known as the "shiro-trap" (see `../shirotrap/` and `../shiro/`). It grows in
  soil pockets between the shell ridges and gives the shiro camouflage against **saw-toothed granks**. The shiro gives
  it locomotion.
- It is eaten by **clodhoppers** (`../clodhopper/`).

## Visual brief
All three images agree on the body plan:
- a low **rosette of broad, pointed, veined leaves**, eight on the mature plant;
- one or more **long, thin, curving stalks** rising from the centre;
- each stalk ending in a **toothed "mouth" pod**, a hinged jaw lined with long, thin, inward-curving spines, like a
  Venus flytrap stretched into a tube;
- a **small cluster of round berry-like knobs** at the top of the mouth or where it meets the stalk. These are likely
  the lure or scent organs.

Colour:
- **Leaves:** pale sage/olive-green to cream, with **red-to-rose veins and edges**.
- **Stalk and mouth:** **brown-maroon to rust**; the mouth interior is darker.
- **Knobs:** dark red.

Size: a small plant, roughly knee-high to waist-high, judging by tooke prey and its use as a house plant.

The images:
- **Image 1** (Legends field-guide painting) is the strongest reference, with one stalk and mouth.
- **Image 2** (*Gungan Frontier* sprite) shows **two** stalks and mouths, which confirms the one-to-four-stalk range.
- **Image 3** (LEGO) shows the same plan in toy form. Use it only for confirmation, never for style.

## Must show
- [ ] Low rosette of broad, pointed leaves, sage/cream with red veins and edges
- [ ] At least one long, thin, curving stalk rising from the centre (one to four allowed)
- [ ] Each stalk ends in a toothed mouth pod with long, thin, inward-curving spines
- [ ] Stalk and mouth are brown-maroon/rust, distinct from the green leaves
- [ ] Small cluster of round dark-red knobs at the mouth
- [ ] Reads as a small plant (knee-to-waist height), not a tree

## Engine limits
- A plant is a single static sprite: the mouth cannot open or snap. Show it open and agape.
- "Preys on tooke and insects" and "lure fragrance" are behaviour. They are not representable in art. They would need
  a mechanic, for example a small-creature trap comp.

## Source URLs
- https://starwars.fandom.com/wiki/Tooke-trap_plant (canon/LEGO; text via MediaWiki API `action=parse`, 2026-10-07)
- https://starwars.fandom.com/wiki/Tooke-trap_plant/Legends (Legends; same API, 2026-10-07)
- File:Tooke-trap_plant.jpg (Legends infobox painting), File:TookeTrapPlant-TGF.jpg (*Gungan Frontier*),
  File:TookeTrapPlant-LEGOTSS.png (LEGO)

## Candidate images
- `tooke_trap_wookieepedia_1.png`: Legends field-guide painting. One stalk, a spined maroon mouth with dark-red knobs,
  and a cream/sage leaf rosette with red veins. **Primary reference.**
- `tooke_trap_wookieepedia_2.png`: *Gungan Frontier* in-game sprite. Two stalks and mouths over a pale leaf rosette.
  It confirms more than one stalk.
- `tooke_trap_wookieepedia_3_lego.png`: LEGO render. The same plan (rosette, curving stalk, toothed pod, knobs on top)
  in toy form. Use it to confirm the plan only.

## Webwork notes (for WEBWORK_FLORA_ROSTER_1)
- Canon home is a **swamp** on Naboo. In the Webwork it is a donor row (`Plant_TookeTrap_Wild`), so per the
  no-donor-art rule it needs our own render against this entry.
- Its canon ecology fits a predator-flora roster: it lures small prey with a fake mating scent, rides shiros, and is
  eaten by clodhoppers. Check which of tooke, shiro and clodhopper are cast in the Webwork before claiming the
  ecology in its description.
- Canon is thin. The main text is Legends, and the canon article is LEGO-tagged non-canon. Per Q11 it is a genuine
  Star Wars name, so an owned port routes through the Utinni or RimStarWars layer, never the free `RM_` tier.

## ruling
(empty — owner has not reviewed this entry)
