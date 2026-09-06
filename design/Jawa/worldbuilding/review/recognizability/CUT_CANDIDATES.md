# CUT candidates — LIVE creatures that are too recognizable

Judged by LOOKING at every sprite on 49 labelled contact sheets (`sheets/`), against
`design/Jawa/worldbuilding/creature_recognizability_rule.md`. **OBVIOUS = a player names
the species, or a famous type, on sight.** 216 live creatures scored OBVIOUS; the full
list is in `recognizability.json` (filter `cut:false, verdict:"OBVIOUS", scope:"creature"`).

Ranked by how instantly nameable, presence on the planet as tie-break (`b=` biomes it
spawns in, `c=` top commonality).

| # | name | mod | read as | why it fails |
|---|---|---|---|---|
| 1 | brown rat | Core | rat | textbook rat; the single commonest animal on the map (c=3.0, b=23) |
| 2 | wild boar | Core | wild boar | tusked pig, named on sight, b=23 |
| 3 | raccoon | Core | raccoon | mask and ringed tail, unmistakable, b=20 |
| 4 | squirrel | Core | squirrel | bushy tail, named instantly, b=19 |
| 5 | deer | Core | deer | antlered deer; also caribou and elk, b=17 |
| 6 | hare / snowhare | Core | hare | long ears; c=2.0 across 22 biomes |
| 7 | horse | Core | horse | the plainest Earth silhouette in the set, b=16 |
| 8 | cougar | Core | cougar | big cat, instant, b=22 |
| 9 | timber wolf / arctic wolf | Core | wolf | canine, instant, b=20 |
| 10 | rhinoceros | Core | rhinoceros | horn and bulk, instant, b=13 |
| 11 | elephant | Core | elephant | trunk and ears, instant, b=10 |
| 12 | red fox / arctic fox / fennec fox | Core | fox | instant, b=15 |
| 13 | grizzly bear / polar bear | Core | bear | instant, b=19 |
| 14 | turkey | Core | turkey | wattle and fan tail, instant, b=15 |
| 15 | Colorful cobra | GRiNDTerra Biomes | snake | hooded cobra, instant; c=1.3 over 11 biomes |

Close behind, all live and all instantly named: **ibex, caribou, elk, iguana, chinchilla,
monkey, dromedary (camel), bison, alpaca, duck, goat, lynx, yak, panther, megasloth
(reads sloth/anteater), donkey, guinea pig**.

Farm block — nameable but not wild-spawning (b=0), so they only appear via colony/trade:
**cow, pig, chicken, sheep, goose**. Cut them only if farm stock is in scope.

Non-Core, live and instantly named — these are the block-level bargains:
- **Biomes! Caverns** (35 live OBVIOUS): brown bat, bioluminescent bat, megabat, woolly bat,
  cave spider, fleece spider, frostweaver (spider), giant slug, glowslug, acid slug, giant
  snail, chem snail, metallosnail, mole, truffle mole, molebear, cave cricket, cave lemming,
  pillbug, silver sheep, bearded yak, jewel/bovine/rhino beetles, fire salamander, dark
  axolotl, goeto toad, imperial toad, sonar rabbit, hoarfrost mastodon (mammoth).
- **Biomes! Polluted Lands** (13): gastro toad, carrion vulture, bloodletter petrel, smog moth,
  megaphorid (fly), tainted turtle, tox-wool sheep, fenrid stoat, maligoat, mucklurker catfish,
  three tumorfish (plain fish).
- **Alpha Animals** (27, though its best work is alien): bumbledrone x3 (wasp/bee), fire wasp,
  two butterflies + three caterpillars, fission mouse x3, shock goat, chameleon yak, radyak,
  Grey-Coated Mouflon, decay drake (dragon), erin (crocodile), giant crowned silkie (cassowary),
  four "ave" birds, plasmorph (slug), crescendo anole (lizard), rough-plated monitor, groundrunner.
- **Megafauna** (11): arthropleura (millipede), pulmonoscorpius (scorpion), meganeura (dragonfly),
  sivatherium (giraffe), dinocrocuta (hyena), uintatherium, megaloceros (elk), titanis, zygolophodon
  (elephant), morrak (walrus).
- **Jurassic (live, 14)**: the ones a player names are **Euoplocephalus (ankylosaur),
  Bagaceratops (triceratops-type), Pteranodon + vhazh + Nyctosaurus (pterodactyl),
  Dilophosaurus (Jurassic Park famous), Beelzebufo (frog), Pulmonoscorpius (scorpion),
  Macrelcana (wasp), Meganeura (dragonfly), Euphoberia + Arthropleura (millipede),
  Manipulator (praying mantis), Bernicia (snail)**. The rest of the live Jurassic set reads
  as "some dinosaur", which is BORDERLINE, not instant.
- **Star Wars Animal Collection**: only 7 live OBVIOUS, and they are the Earth-shaped ones —
  **loth-cat (cat), loth-wolf (wolf), Boar-wolf (boar), bordok (donkey/ox), convor (owl),
  strill (rat), porg (puffin)**. Everything else in that mod reads alien and should stay.
