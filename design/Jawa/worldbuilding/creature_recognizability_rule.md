# The recognizability rule — the actual keep/cut criterion

_Owner, 2026-09-05, verbatim:_

> "We should be careful letting cut things back in as one of the main reasons to
> cut was familiarity in terrestrial forms. The 'no stegosaurs' rule. But many
> dinos are so strange that they work well. We should keep to that rule.
> **Generally you can ask yourself if you recognize what the creature is supposed
> to be. If it's obvious and easy, we shouldn't use it.**"

## The test

Look at the creature. **Can you immediately name what it is meant to be?**

- **Obvious and easy → CUT.** "That's a stegosaurus." "That's a rhino." "That's a
  housecat." Recognition is the disqualifier, however good the art is.
- **Strange enough that you cannot place it → KEEP.** Many dinosaurs pass: a
  therizinosaurus or a dunkleosteus reads as an alien thing to most eyes, where a
  stegosaurus or a T-rex is instantly named.

🔑 This is a test of the VIEWER's recognition, not of taxonomy. The question is not
"is this a real Earth animal" — it is "will a player instantly know what it is."
A real animal nobody can name still works; an invented creature drawn as an obvious
horse does not.

## Why this matters more than art quality

Every review sheet states plainly that its pre-fill ranks **art quality at display
size** and CANNOT rank **worth**. This rule IS the worth criterion. It outranks
polish in both directions, exactly as the owner has ruled before:
- weak art KEPT for an alien silhouette,
- good art CUT for being recognisably from Earth.

## How it applies to restoration

The cut pile is not a restore pool. It was cut largely FOR familiarity, so most of
it must stay cut. Restore only where the creature is genuinely strange — and judge
that by the test above, not by the mod it came from and not by whether the biome
needs stocking. **A starved biome is not a reason to admit a recognisable animal.**

---

## AMENDMENTS, 2026-09-05 (owner) — recognizability is necessary, not sufficient

The rule above says what to CUT. These say when NOT to, and what to do instead.

### 1. 🔴 Mechanical value outranks a bad sprite — REGENERATE, don't cut
> "Alpha creatures tend to have cool powers. I would rather regenerate their
> graphics to save them than just cut them because they boringly made a blue
> butterfly... if there are extenuating reasons to keep a beast such as custom
> attacks or code or functions (such as the genetic freak hybrids)."

⇒ The decision is not `recognizable → cut`. It is:

| art | mechanics | verdict |
|---|---|---|
| recognizable | ordinary | **CUT** |
| recognizable | **unique** (custom attack, ability, C#, hybrid function) | **REGENERATE ART + RENAME** |
| strange | anything | keep |

Alpha Animals and Vanilla Genetics Expanded are the two mods this protects: their
*inventiveness is the asset*, and a boring blue butterfly is an art defect, not a
design defect. **Check for unique mechanics before cutting anything.**

### 2. 🔴 Size amplifies the penalty
> "I am very serious about making truly huge creatures everywhere, so even more
> risk if they aren't alien."

A huge creature dominates the screen, so a recognizable *large* animal is a worse
offence than a recognizable small one. **Scale the strictness with drawn size** —
the renormalization will make this sharper, not softer.

### 3. The dinosaur ruling: take the DEEPER cut
> "If we can afford the deeper Dino cut it is safer as I don't really want the
> world to feel like a Walking with Dinosaurs episode."

⇒ Strict reading applies: **"reads as a dinosaur at all" counts as OBVIOUS**, not
just the famous silhouettes. Generic theropods and ornithopods are cut too.

### 4. Boomalope and thrumbo are deliberate in-jokes
Kept as RimWorld references — but **reskinned**, with descriptions that reference
them only distantly and punningly. They are an exception granted on purpose, not a
failure of the rule.

### 5. Restoration path: art + name redo
A cut creature may return if art AND name are redone enough to **sever it from its
terrestrial-hybrid past**. The bar is the same test applied to the NEW art.

### 6. ⭐ Retire whole mods where little survives
> "We should also watch for the opportunity to retire entire mods if we're barely
> keeping their content and reskinning what they got... Less mod mod conflict,
> easier maintenance."

Absorb the few survivors into our own mods (the `Absorbed_*` pattern already in
`RimStarWars/Armoury`) and drop the dependency. **Measured survival under the
strict rule (STRANGE only), live creatures:**

| mod | live | survive | % | note |
|---|---|---|---|---|
| Megafauna | 15 | **0** | 0% | retire — nothing to absorb |
| Mythic Ages: Megafauna Bestiary | 10 | **0** | 0% | retire |
| Beasts of the Rim (Continued) | 10 | **0** | 0% | retire |
| GRiNDTerra Biomes | 9 | **0** | 0% | ⚠️ also ships biomes |
| Biomes! Caverns | 89 | 9 | 10% | ⚠️ also ships biomes |
| Jurassic (Dinosaurs Only) | 28 | 5 | 18% | owner named it; absorb Segnosaurus + 4 |
| Biomes! Polluted Lands | 37 | 9 | 24% | ⚠️ also ships biomes |
| Vanilla Genetics Expanded | 93 | 33 | 35% | 🔴 PROTECTED by rule 1 (hybrid functions) |
| Alpha Animals | 135 | 73 | 54% | 🔴 PROTECTED by rule 1 (powers) — regenerate, don't cut |
| Star Wars Animal Collection | 160 | 89 | 56% | cleanest large mod in the set |
| VFE-Insectoids 2 / Anomaly / Ideology / Horrors / Alpha Memes | 58 | 58 | 100% | keep entire |

🔴 **Before retiring ANY of these, audit what else the mod ships.** Several are
biome mods — Biomes! Caverns, Polluted Lands and GRiNDTerra supply terrain, plants
and biomes we may want to keep even when their fauna is worthless. Creature
survival alone is NOT a retirement decision.

### 🔴 CORRECTION to the retirement table above (mod_retirement_audit.md, 2026-09-05)

The §6 table lists four mods at 0% survival **as if that made four retirements. It
makes one and a half.** Creature survival was never why three of them were installed:

| mod | real verdict | why |
|---|---|---|
| Mythic Ages: Megafauna Bestiary | ✅ **RETIRE — the clean kill** | fauna-and-nothing-else, zero dependents, zero absorption |
| Beasts of the Rim | ✅ retire after ONE edit | **our own** `SeasWaterline/About.xml` hard-depends on it; re-home its Megasquid lane |
| Megafauna | ✅ retire, cleanup only | dead groups in `MegafaunaYield.xml` + 4 patches + a loadAfter; every reference is conditional so nothing breaks if cleanup slips |
| GRiNDTerra Biomes | 🔴 **KEEP** | ships **15 biomes, 123 terrains, 117 plants**, and its DLL holds 15 `BiomeWorker_*` subclasses (one per biome, wired by bare `<workerClass>`) — there is no XML-only version of it |
| Biomes! Caverns | 🔴 **KEEP, decisively** | **1,003 planet tiles** sit on its biomes, and `The Salvation.rid` — our shipped ideoligion — holds its precept `BMT_FungusEating_DontCare`. Not fixable by removal. |
| Biomes! Polluted Lands | **KEEP** | 40 plants, 18 genes, a faction, and our own SeasWaterline fish |
| Jurassic (Dinosaurs Only) | ⏳ retire after absorbing 5 | Segnosaurus + 4; no world content at stake |

🔑 **No other mod in the 601-mod list declares a hard dependency on any of the seven** —
every third-party coupling found is an inert `loadAfter` ordering hint. The only hard
dependencies are **ours**.

⇒ Lesson for future retirement calls: **a fauna count is not a retirement decision.**
Ask what the mod generates (biomes, terrain, genes, GenSteps, world tiles) and what
OUR content already leans on, before counting creatures.


---

## 🔴 THE STAR WARS ICON CARVE-OUT (owner ruling, 2026-09-05)

> "Iconic Star Wars status protects completely."

The rule disqualifies **terrestrial** recognizability, never **in-universe**
recognizability. A bantha that reads as a bantha, a dewback that reads as a
dewback, an astromech that reads as an astromech — **that is the campaign
working.** Iconic Star Wars creatures and droids are exempt outright, and their
recognizability is an ASSET to seek rather than a defect to correct.

This settles the five Outer Rim droids the mechanics scan flagged: **not cut, not
even regenerate — protected.**

⇒ Corollary, and it inverts the usual direction of this work: where an iconic
creature is MISSING from the game, that is an opportunity to reskin or recreate
something into it. Being instantly nameable is the goal there.
See `design/Jawa/worldbuilding/starwars_iconic_creatures.md` (research pending).
