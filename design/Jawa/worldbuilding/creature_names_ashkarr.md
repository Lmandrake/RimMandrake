# Creature names for Ash'karr — killing the Latin

_DECIDE, 2026-08-22. Closes the naming half of `CREATURE_NAMES_MADE_LOCAL_1`._

**Owner:** *"we'll scan their names and find better Star Wars-style animal reskins for them
instead of latin dinosaur names (particularly terrible)."*

## What is renamed, and what deliberately is not

Measured against the cast (`design/Jawa/fauna/cast_assignment.csv`, 633 creatures):

| mod | in the cast | renamed |
|---|---|---|
| **Jurassic Rimworld** | 22 | ✅ all — the worst offenders, pure Latin binomials |
| **Megafauna** | 19 | ✅ all — `castoroides`, `andrewsarchus`, `josephoartigasia` |
| Mythic Ages: Megafauna | 18 | ⛔ **no** |
| Insectoids 2 / Alpha Animals / Biomes! | 9 | ⛔ **no** |

⛔ **Mythic Ages and the English compounds stay, on the bestiary's own rule.**
`Alien_Bestiary.md` §1: *"Avoid English compounds ('sandstalker') except as **nicknames** —
those read as spacer slang, which is a different register and useful for contrast."*
`dunbear`, `duskhorn`, `manehound`, `hellboar`, `sporemole` are exactly that register. They
are not Latin and they are not broken. **Renaming them would flatten the contrast the
bestiary is deliberately building.**

## The rules applied — `Alien_Bestiary.md` §1

1. One or two syllables, hard stop at the end.
2. Doubled consonants; terminal `-k` / `-ak` / `-ik` / `-rr`.
3. Apostrophes rare and load-bearing — reserved for Sith/ancient things. **None used here.**
4. **The name never describes the mechanic.** The nickname carries the warning.

**Clade roots**, so the ecosystem reads as evolved rather than assembled:
`ss-`/`-ssh`/`-zh` reptiles · `-ak`/`-rak`/`-dar` ursine heavies · `-ik`/`-ek`/`-ka` small
quick things · `karr-`/`-rrik` insectoid · `-kir`/`-bak` mounts · `dh-`/`vh-`/`kr-` apex.

⭐ **The elder-form rule is used where the mod gave us a size ladder.** A `ssvek` and a
`ssvarrak` are visibly the same animal eighty years apart, and the player works that out
without a codex.

## Jurassic Rimworld — the reptile clade, `ss-`

| was | becomes | band | why |
|---|---|---|---|
| Protovermes | **ssik** | tiny | `ss-` reptile + `-ik` small-quick. The clade's smallest. |
| Compsognathus | **sskek** | small | sibling of `ssik`, one rung up |
| Coelophysis | **sslek** | med | same ladder |
| Hypsilophodon | **ssvek** | med | pairs with `ssvarrak` below — elder form |
| Microceratus | **ssbik** | med | |
| Zephyrosaurus | **sszhal** | med | `-zh` reptile, faster read |
| Archaeopteryx | **zhikka** | med | feathered: `zh-` reptile, `-ka` small-quick |
| Cyclosphaeroma | **karrik** | med | not a reptile — an isopod. `karr-` insectoid root |
| Hynerpeton | **sslugg** | med | amphibian; doubled consonant, wetter sound |
| dinilysia | **sserrik** | med | snake |
| wonambi | **ssorrak** | med | snake, heavier |
| yurlunggur | **sshaggan** | med | snake, largest of the three |
| Agilisaurus | **sskarr** | large | |
| Dryosaurus | **ssdarr** | large | |
| Kileskus | **krissh** | large | `kr-` apex initial — this one hunts |
| Geosternbergia | **vhazh** | large | flier, `vh-` apex initial |
| Rhamphorhynchus | **vhikk** | large | smaller flier, same `vh-` family |
| Brachiosaurus | **ssorrbantha** | huge | `-bantha` muffalo line: a herd colossus, domesticable in principle |
| Ouranosaurus | **ssvarrak** | huge | ⭐ elder form of `ssvek` |
| Estemmenosuchus | **ssgrondak** | huge | shares `grond-` with the bestiary's `grondar` line |
| Dimetrodon | **sszhakar** | huge | |
| Torosaurus | **ssborrak** | huge | horned charger |

## Megafauna — mammals, by clade

| was | becomes | band | clade |
|---|---|---|---|
| castoroides | **grondik** | large | rodent-burrower; `grond-` line, `-ik` small |
| dinopithecus | **vekka** | large | quick climber, `-ka` |
| palaeeudyptes | **korrik** | large | cold-water diver |
| smilodon | **dhakar** | large | `dh-` apex feline — the ones people whisper about |
| Short-faced bear | **rannak** | huge | ursine `-ak`; sibling of the bestiary's `rannok` |
| andrewsarchus | **krondar** | huge | `kr-` apex + `-dar` heavy |
| daeodon | **borrak** | huge | ursine heavy |
| dinornis | **kessik** | huge | flightless runner; shares `kess-` with `kessorak` |
| diprotodon | **obbak** | huge | ⭐ the bestiary already coins `obbak` for the muffalohorse line |
| enhydriodon | **lussik** | huge | otter-kin, wet sibilant |
| gomphotaria | **morrak** | huge | tusked heavy |
| josephoartigasia | **grondrak** | huge | ⭐ bestiary's own elder-form of `grondar` |
| procoptodon | **jakkir** | huge | leaper; `-kir` mount root — it can be ridden |
| quinkana | **sskorrak** | huge | land crocodile — reptile `ss-` + heavy `-ak` |
| woolly mammoth | **vhorbantha** | huge | ⭐ bestiary's own name for the dunemother line |
| gigantophis | **sserrakoth** | SUPER | elder form of `sserrik` |
| purussaurus | **sskorrath** | SUPER | elder form of `sskorrak` |
| sivatherium | **obbakar** | SUPER | ⭐ bestiary's own elder-form of `obbak` |
| titanoboa | **ssorrakoth** | SUPER | elder form of `ssorrak` |

## What this does NOT change
⛔ **No `defName` is touched.** A rename is `<label>` and `<description>` only. defNames are
referenced by quests, incidents and other mods' patches, and changing one breaks them
silently.
⚠️ The **descriptions** still read as Earth palaeontology and are NOT rewritten here. That is
a second pass and a larger one; the label is what a player sees in the wild.
