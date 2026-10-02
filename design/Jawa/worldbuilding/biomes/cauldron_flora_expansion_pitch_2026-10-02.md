# The Cauldron — flora expansion pitch (2026-10-02)

**Item:** `BEDAZZLE_FLORA_EXPANSION_1` (Cauldron sitting only — one biome at a time).
**Asked:** owner, 2026-09-29, on the Cauldron art sheet: *"Needs more color in palette and
more plants."* **Status:** pitches only — nothing admitted, nothing built, nothing queued.

## Context read

- Frozen sheet `design/Jawa/worldbuilding/biomes/cauldron.md` — §5 always-true (every plant
  surface wet or crystalline; ore lives in organisms; no potable water), §6 hard bans (no
  green, no leaves/needles/broadleaf crowns, no sunlight cues, no lush flora, no
  Earth-nameable organisms, no heat/volcanism), §9 palette (wet black/slate, bone-pale
  trunks, crystal in **bruised blue and sulfur yellow**, red-purple films, no warm light).
- Cast bible `cauldron_bedazzle_cast_2026-09-28.md` — name accent (glass and acid: thin
  front vowels, ts/sk/x/ss clusters, -ix/-iss/-eth endings); ruling that nothing here
  explodes ("too many exploding giant beasts" — honoured below: no flora detonates).
- Review `cauldron_bedazzle_review_2026-09-28.md` — roster gaps; slate B ("assay the
  trees", metal from old trunks) is a tree mechanic, so no pitch here duplicates it.
- **Live roster**, parsed from the shorthand `<DefName>commonality</DefName>` form:
  `src/RimMandrake/Cauldron/Defs/BiomeDefs/RM_Cauldron.xml` carries **11** wildPlants —
  TwistingThornwood 0.6, CrystalFlower 0.5, TreeMartyr 0.5, BloodBouquet 0.4, RavenNettle
  0.4, GiantAgariTox 0.3, RedBugloss 0.3, Xithess 0.35, DarkCrust 0.25, KeeningCordax 0.2,
  GiantToxicFlower 0.08 (all now `RM_`-owned in
  `src/RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml`). The frozen twin
  `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Cauldron.xml` carries 10; no
  `UtinniPatches` WildPlants patch targets either Cauldron BiomeDef
  (`BiomeFlora_Ashkarr.xml` lists RUT_Cauldron as "authored in its own def").
- **Palette of what ships today:** grey/bone trunks, black (nettle), crimson/red
  (bouquet, bugloss, crust), purple-green (agaritox), toxic green (giant toxic flower),
  clear crystal. ⇒ **Missing entirely: sulfur yellow, cobalt blue, amber-orange, fuchsia,
  violet-lavender, and interference/iridescent colour.** Each pitch below takes one.
- **Built-already search:** `CompContactVenom` (generic plant contact-scratch comp,
  `src/RimMandrake/EnvironmentalHazards/Source/CompContactVenom.cs`, "any later thorn plant
  reuses this") and vanilla `CompProperties_GasOnDamage` (already used in our race defs)
  are reused below instead of inventing mechanisms. `RM_CompPlantAlarm` /
  `RM_CompPlantPredator` exist but no pitch needs them.

## Collision sweep

Instrument: python over every `.xml .md .cs .csv .json .txt .py .html .yaml` under `src/`
and `design/` (5,560 files; this file excluded) — case-insensitive substring of the whole
file text, plus near-miss (difflib ratio ≥ 0.75) against 16,688 tokens drawn from every
`<defName>` (CamelCase-split, tier prefix stripped) and every `<label>`/`<description>` word,
plus the Cauldron's own invented names (vexxiss, zisska, eskith, xithess, vexxith, tsekkit).

**Sanity probe: `korrum` → 48 files** (instrument proven able to see; src+design only, so
lower than the cast bible's 65, which also searched `infrastructure/state/`).

| name | substring files | near-miss | verdict |
|---|---|---|---|
| tsevrix | 0 | none | CLEAR |
| ixalith | 0 | none | CLEAR |
| fexxil | 0 | none | CLEAR |
| sessarix | 0 | none | CLEAR |
| kissaveth | 0 | none | CLEAR |
| selvix | 0 | none | CLEAR |

**Dropped on the sweep (collisions found):** *ketsareth* (near `kessaroth`, a Webwork
plant), *vissaleth* (near `vissler`, a Leaning Scrub creature), *skeshix* (near `keshig`),
*pessith* (near the Cauldron's own `eskith`), *tsirrel* (near `shirrel`/`squirrel`),
*issavex* (clean, but a third `vex-` name beside vexxiss/vexxith would blur at a glance).

## Pitches

All six: one home (the Cauldron), `RM_` tier, invented names, no green, nothing explodes,
nothing glows warm. Numbers are proposals for FOUNDRY to calibrate.

### 1. Tsevrix — FOOD — sulfur yellow

**Look:** a low cluster of fist-sized waxy bladders, **sulfur-yellow** with **cinnabar-red
veining**, clustered at the base of stones like a spill of wet lanterns that give no light.
Condensate beads on the wax; the tops are dimpled where the gas escapes. No leaves.

**Grows/behaves:** ground-level, clustered near vent ground and xithess stands (both feed
on the same exhaled gas). Commonality ~0.3. Slow (the biome's "nothing hurries" law).

**Harvest/yield:** raw tsevrix pulp — starchy, filling, and **toxic raw** (the bladders hold
dissolved vent volatiles). Roasting drives the volatiles off: one recipe at a campfire or
stove turns it into safe food. The only plant food in a biome whose meat is all poison.

**Why here:** it is a chemosynthetic store — the plant banks vent gas as starch, and the
gas is what makes it dangerous. Sulfur yellow is named in §9's palette and appears nowhere
in today's roster.

**Mechanism + cost:** vanilla only — PlantDef (`harvestedThingDef`), a raw-food ThingDef
whose `ingestible.outcomeDoers` gives `ToxicBuildup` (vanilla `IngestionOutcomeDoer_GiveHediff`),
one RecipeDef for the roasted form. **S.**

**Collision:** CLEAR (0 substring, no near-miss).

### 2. Ixalith — BEAUTY — oil-slick iridescence

**Look:** a stand of thin **black wire-stalks** with translucent films stretched between
them like soap skins, every film showing **oil-slick interference colour** — magenta,
gold, peacock-blue bands that slide as the fog moves. Beaded condensate on the wires.

**Grows/behaves:** sparse, solitary, in still pockets between trunks. Commonality ~0.12.
Fragile — low hit points; a fire or a careless pawn ends it.

**Harvest/yield:** none; it is a beauty plant. High Beauty stat — the one place in the
Cauldron a colonist's mood goes up for looking at something.

**Why here:** the films are the forest's chemistry made visible — vapour condensing into
thin skins, not pigment. Interference colour is exactly the "alien, varied colour" the owner
asked for, and it needs no light source, so it obeys the no-warm-light law.

**Mechanism + cost:** vanilla PlantDef (`statBases/Beauty`, `harvestYield 0`, low
`MaxHitPoints`). **S.** (Optional later: films "pop" off during a vent bloom — needs a comp,
M; not required.)

**Collision:** CLEAR.

### 3. Fexxil — HAZARD — cobalt blue

**Look:** a knee-high thicket of **cobalt-blue glass burrs** — branching spines tipped with
tiny hooked crystals, deep blue at the core going **pale ice-blue** at the tips, every hook
holding a bead of condensate. Reads as broken bottle-glass grown into a shrub.

**Grows/behaves:** dense patches along trails and trunk bases. Commonality ~0.25. High path
cost. Pawns walking through take a periodic scratch that carries a dose of the forest's
metal (toxic buildup); animals route around it.

**Harvest/yield:** a small yield of glass shards (or nothing — FOUNDRY's call); the point
is the hazard, and clearing it is real work.

**Why here:** the crystal fans the trees sweat (§1) — but grown as its own plant. "Bruised
blue" crystal is in §9's palette and today only the clear crystal flower carries crystal.

**Mechanism + cost:** reuses the **already-built** generic `CompContactVenom`
(`src/RimMandrake/EnvironmentalHazards/Source/CompContactVenom.cs`) + one new DamageDef whose
`additionalHediffs` gives `ToxicBuildup`; vanilla `pathCost`. **S** (no new C#; adds an
EnvironmentalHazards dependency to the Cauldron mod).

**Collision:** CLEAR.

### 4. Sessarix — MATERIAL — amber-orange

**Look:** glossy **amber-orange resin boils** welling out of cracked stone and slag, with a
**tar-black core** visible through the translucent skin; thin threads of resin drip and
harden into glass-like drips. No stalk, no leaf: a weeping blister.

**Grows/behaves:** on rock and old ruin footings, never on soil. Commonality ~0.15. Very slow
regrowth.

**Harvest/yield:** **chemfuel** directly — the resin is vent chemistry already refined by the
plant. Small yield per boil.

**Why here:** §7 lists "vent gas for chemistry" as one of the biome's three unique goods and
nothing in the roster yields it; this makes the scavenger clan's reason to come here visible.

**Mechanism + cost:** vanilla PlantDef with `harvestedThingDef Chemfuel`. **S.** *Trade-off
risk:* a free fuel tap if commonality or yield is lazy — keep it rare.

**Collision:** CLEAR.

### 5. Kissaveth — HAZARD — violet-lavender

**Look:** a clump of **pale lavender gas-bladders** on short stalks, skins thin enough to show
**deep violet** fluid sloshing inside, ringed at the base with white mineral crust. Swollen,
taut, and visibly full.

**Grows/behaves:** scattered through the understory. Commonality ~0.2. When damaged —
shot, burned, trampled by a fight — the bladders **split and sigh out a puff of tox gas**.
Not an explosion: a leak, a hiss, a lilac haze that drifts.

**Harvest/yield:** none safe; cutting it near your base is the mistake it teaches.

**Why here:** the ground exhales; this plant bottles the exhalation and lets it go when hurt.
The hiss belongs to the ruled "loud ground" soundscape.

**Mechanism + cost:** vanilla `CompProperties_GasOnDamage` (`type ToxGas`), already used on
our race defs. **S** if damage-only. ⚠️ UNMEASURED: whether vanilla's cut/harvest path applies
damage to a plant (it may not, so a plain "cut" might not trigger the puff); a release-on-cut
comp would make it **M**.

**Collision:** CLEAR.

### 6. Selvix — MATERIAL (medicine) — fuchsia

**Look:** a flat star-shaped rosette of thick, wet **fuchsia-pink** fleshy arms, each rimmed
with a **frost of white crystal** where it sweats out the metal it cannot keep. Low, hugging
the stone, with a dark wine-red heart.

**Grows/behaves:** in rings on stained ground. Commonality ~0.2. Sweats its metal outward, so
its flesh is the cleanest thing in the forest.

**Harvest/yield:** herbal medicine. The healers' secret: the plant strips toxins out of
itself, and what it keeps inside is safe.

**Why here:** the §4 logic in reverse — the trees plate themselves in waste, the selvix
crusts it off its skin. Fuchsia is new to the palette.

**Mechanism + cost:** vanilla PlantDef with `harvestedThingDef MedicineHerbal`. **S.**
(Optional later: a small toxic-buildup-reducing effect on ingestion — vanilla outcome doer
on a new item, S–M.)

**Collision:** CLEAR.

## Card draft

1. **Tsevrix** — sulfur-yellow bladder cluster; food that's poisonous raw and safe once roasted. Gives a meal here, but only to a camp with a fire.
2. **Ixalith** — oil-slick colour films on black wires; pure beauty for mood. Lovely and cheap, but gives no yield and burns easily.
3. **Fexxil** — cobalt glass-burr thicket that scratches and poisons passers-by. A real hazard, but clearing paths becomes ongoing chore work.
4. **Sessarix** — amber resin blisters on stone that yield fuel. Useful reason to visit, but risks a free-fuel faucet if too common.
5. **Kissaveth** — lavender gas-bladders that leak poison gas when hurt. Great tension, but cutting near camp may need extra code.
6. **Selvix** — fuchsia crystal-rimmed rosette that yields herbal medicine. Fills a gap colourfully, but overlaps medicine other biomes already give.
