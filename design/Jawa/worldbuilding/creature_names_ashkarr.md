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

## ⚠️ Four names are RESERVE, not live — and this is a drift the doc caused

**`Protovermes` → ssik · `Compsognathus` → sskek · `dinornis` → kessik · `sivatherium` → obbakar.**

~~All four **exist in the dump**. They are not broken defs.~~

> 🔴 **CORRECTED 2026-08-23, DECIDE — two of the four do NOT exist.** Measured against the
> live capture `2026-08-23T07-12-04Z` *and* the 2026-08-21 database, both empty:
>
> | name | exists? | ruling |
> |---|---|---|
> | `Protovermes` → **ssik** | 🔴 **NO — absent from both dumps.** Its mod is not installed | ⛔ **DEAD.** Not a reserve; there is nothing to hold a name for |
> | `Compsognathus` → **sskek** | 🔴 **NO — absent from both dumps** | ⛔ **DEAD** |
> | `dinornis` → **kessik** | ✅ yes, Megafauna | ⏸️ **RESERVE**, and the reason is below |
> | `sivatherium` → **obbakar** | ✅ yes, Megafauna | ⏸️ **RESERVE**, and the reason is below |
>
> ⚠️ **"Reserve" and "dead" are different states and the doc merged them.** A reserve name is
> waiting for a creature that exists; a dead one names nothing at all. `ssik` and `sskek` are
> free to be re-used by any future creature — nothing holds them.

### ⏸️ Why the two live ones stay OUT of the cast — DECIDE, 2026-08-23

⛔ **Neither is cast, and the cast is NOT being re-opened for them.** Measured:

| | `Dinornis` | `Sivatherium` |
|---|---|---|
| bodySize | 5 | **8** — SUPER-class (the 24 cast SUPERs median 8.2) |
| sprite | 2,851 px | 2,526 px |
| its band's weak line | 2,884 (huge) | 3,311 (SUPER) |
| comfy temperature | −30 … **40** | −20 … **40** |
| biomes on Ash'karr where its own mod gives it commonality > 0 | 4, all at **0.004 – 0.01** | 🔴 **none** |

- **`Sivatherium` fails on all three counts.** No native reach on this planet at all; `ComfyTemperatureMax 40` excludes the hot desert that is 35% of the ground; and at bodySize 8 with a 2,526 px sprite it would enter the cast as an immediate shrink candidate under `CREATURE_RESIZE_PATCH_1`.
- **`Dinornis` is closer but not close enough.** Its native reach is real but vanishing (0.004 in `AB_MiasmicMangrove`), and its sprite sits *below* its own band's weak line.
- 🔑 **And the cast is settled.** The owner approved creature sizes against it on 2026-08-23; re-opening it to add two marginal animals would invalidate a decision hours old for no gain the world can see.

✅ **Both names stand as reserve, in-clade and ready.** `obbakar` in particular is the
bestiary's own elder-form of `obbak`, and **`Diprotodon` — the creature that carries `obbak` —
IS cast**, so the pairing is waiting if a later re-cast wants it.

⚠️ **TWO DEFS ARE CALLED SIVATHERIUM.** `Sivatherium` (Megafauna, bodySize 8) and
`MA_Sivatherium` (Mythic Ages: Megafauna Bestiary, bodySize 3.3). **This row means the
Megafauna one.** A generator matching on label would pick either.
⚠️ **`Sivatherium`'s label carries a trailing space in the dump** — `'sivatherium '`. Anything
matching on label must strip it; anything renaming it fixes it for free.

🔑 **The names stand as reserve.** If either live one returns to a cast, its name is already
coined and in-clade. ⛔ **Do not read an empty rename as a missing def** — `gen_name_patch.py`
now says so out loud when the list is non-empty.
⚠️ **The lesson: this doc is authored against a SNAPSHOT of the cast.** Re-run the generator
after any re-cast, and read its warning.

## What this does NOT change
⛔ **No `defName` is touched.** A rename is `<label>` and `<description>` only. defNames are
referenced by quests, incidents and other mods' patches, and changing one breaks them
silently.
⚠️ The **descriptions** still read as Earth palaeontology and are NOT rewritten here. That is
a second pass and a larger one; the label is what a player sees in the wild.
