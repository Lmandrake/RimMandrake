<!-- status: design brief — nothing here is built -->
# The vhessk — GOO_BOOM_COMMISSION_1, the one boom creature that replaces the family

_Design brief, 2026-09-10, Fable pass (backgrounded from BENCH per
`infrastructure/agents/Agent_Policy.md`: design is drafted by Fable, never in-window).
This doc **specifies**; it writes no ThingDef, no PawnKindDef, no C#, no texture. Whoever
builds it next should be able to follow it mechanically. Every defName, field, worker
class, path and number below was read from the file it cites — nothing is guessed._

**The commission, verbatim (owner, 2026-09-10):** *"Keep one big reskin boom creature for
the assailant dungeon, but redo it to be fleshy-based with sacks of explosive goo, and be
done with them."*

**What it replaces:** the 15-creature boom family cut by `BOOM_FAMILY_CUT_1` the same day
(`Boomalope`, `Boomrat`, `VFEI2_Boomtick`, and the 12 Vanilla Genetics Expanded `GR_*`
boom hybrids — record in `infrastructure/state/items/BOOM_FAMILY_CUT_1.md`). The
Boomalope's own review row was the seed: *"Convert to a twisted thing the Assailants make
in their dungeons"* (`review/round2/reserved_groups_draft.md` §9). This is that convert.

---

## 0. The three rules this brief obeys

1. **It is Assailant-made, so it lives in the Assailant dungeon and nowhere else.** The
   dungeon-guardians roster (`reserved_groups_draft.md` §1, Assailant rows) is its only
   home. ⛔ Never a `wildAnimals` entry in any biome. See §4.
2. **It is a sibling of the flesh-mutant register already on that roster** —
   `GR_AberrantFleshbeast`, `GR_FleshGrowth`, `GR_FleshMonstrosity` (VGE
   `Races_Animal_Failures.xml`) and `VQEA_Spliceling/-hulk/-fiend/-toot` (VQE Ancients
   `Races_Animal_Mutants.xml`). Same body-horror visual register, comparable size class.
   It is NOT "Boomalope but fleshy" — no hump-backed cow silhouette, no milking, no
   chemfuel economy, no farm-animal cuteness.
3. **The register guard holds** (`ANCIENTS_AS_RAKATA_SPEC.md` "the dark half",
   `reconciled_lore/03_deep_history.md`): the Assailant is never named, never
   sympathetic, and nothing in a label or tooltip states Assailant capabilities as
   narrator-fact. The description below is written in the salvager's voice — what a Jawa
   crew *calls* it and what they *saw*, not what it *is*.

---

## 1. Name and flavor

| field | value |
|---|---|
| **defName** (ThingDef and PawnKindDef) | `RUT_Vhessk` |
| **label** | `vhessk` |
| **nickname (description only)** | "lampgut" — salvager slang, carries the warning per `Alien_Bestiary.md` §1 rule 4 |
| tier | RimUtinni (campaign content; `design/NAMING_SCHEME_PLAN.md`: `RUT_` prefix, packageId `mandrake.rut.<modname>`, C# namespace `RimMandrake.Utinni.<Mod>` if any C# is ever written) |

**Why this name.** `Alien_Bestiary.md` §1: one or two syllables, hard stop, doubled
consonants, sibilant `ss-`/`-ssh` for the venom/heat clade, `vh-` initial for the things
"people whisper" — and the name never describes the mechanic; the nickname does. `vhessk`
is opaque, apex-coded, sibilant, and shares no morpheme with the cut family (no "boom", no
"-alope"). The English flesh-mutant labels beside it (fleshbeast, splicehulk) are donor
labels; ours follows the campaign's own naming rule, which is what will eventually rename
those too.

**Description (in-fiction, player-facing — 4 sentences, salvager register):**

> A low, wide slab of wet muscle that walks on too many short legs, its back and flanks
> hung with translucent sacs that swell and slacken as it breathes. The stuff inside the
> sacs glows faintly and stinks of fuel; salvage crews who have seen one burst call the
> thing a lampgut, and they say it from a long way off. It was found in the flesh-galleries
> of the deep nightside, standing guard over things that are older than it is, and it does
> not leave them. Nobody has kept one alive long enough to learn whether it eats.

**Register check:** no "Assailant", no "Rakata", no bioweapon claim, no tyranny leak —
only what a crew saw. "Older than it is" hints at the Forsaken works it guards without
saying whose. ✅ Pre-reveal safe.

---

## 2. Silhouette and size

### 2a. Body plan (what the art pass draws)

A **low, broad, ground-hugging slab** — wider than it is tall, roughly 2 : 1 length to
width from above, the way `GR_AberrantFleshbeast` reads as a lumpy mass rather than an
animal with a neck. No head worth the name: a frontal cleft with a ring of teeth, no eyes,
no ears, no face. **Six to eight short thick legs** in an irregular row down each flank
(asymmetry is the register — `the_contagion.md` §9: "creatures that read as drafts").

**The sacs are the point of the silhouette.** Five to seven **translucent, taut,
membranous sacs** of clearly different sizes, budding from the dorsal ridge and the upper
flanks — the largest one or two on the back (each ~⅓ of body width), smaller ones
crowding the shoulders and rump. They should read as **inflated bladders under thin
skin**: a visible bright specular highlight on each, a darker meniscus where the goo
pools at the bottom of the sac, thin dark veins branching across the membrane. One sac
should be visibly *over*-taut — the one that will go first. From above (the south facing)
the sacs must break the body outline so the creature is recognisable as "the one with the
bladders" at 3 cells on a dark dungeon floor.

Compare the three donor sprites the art pass should have open as references
(all loose PNGs, all readable off disk):

| reference | path (under `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2801160906/Textures/Things/Pawn/Animal/Failures/`) | canvas | what to take from it |
|---|---|---|---|
| aberrant fleshbeast | `AberrantFleshbeast/Fleshbeast_south.png` | 256×256 | the lumpy, faceless mass; the low, wide stance |
| flesh monstrosity | `FleshMonstrosity/FleshMonstrosity_south.png` | 384×384 | the tendril/leg fringe; near-black outline weight |
| flesh growth | `Fleshgrowth/FleshgrowthA.png` | 256×256 | the salmon-on-maroon highlight scheme; membrane sheen |

### 2b. Numbers (proposed — see §6 for which are open)

Anchors read from the roster siblings: VGE flesh mutants `baseBodySize 5`,
`baseHealthScale 13`, `drawSize 3.0`, `combatPower 250` (Fleshbeast is `combatPower 50`);
VQEA Splicefiend `baseBodySize 4`, `baseHealthScale 5`, `drawSize 3`, `combatPower 420`;
Boomalope `baseBodySize 2.0`, `baseHealthScale 0.65` (Core `Races_Animal_CowGroup.xml`).

| field | proposed | grounding |
|---|---|---|
| `drawSize` (all life stages) | **3.0** | = 3 m body length, literal per `creature_normalization_doctrine.md` ruling 1; matches the flesh-mutant siblings' render so it sits beside them on the dungeon floor at the same visual weight |
| `baseBodySize` | **3.0** | engine scale (Law 2 ruled: 60 kg/bs kept) → ~180 kg. Cube check `(3/1.5)³ = 8` disagrees; **stated shape reason:** a hollow, sac-filled body — gas/gel-filled register, light for its length (the doctrine's own "gas-filled" exemption). Big enough to be "one big creature" (owner) and shrug bullet stagger vs most small arms; not a leviathan |
| `baseHealthScale` | **2.0** | health ∝ mass (doctrine ruling 3) would say ~3; deliberately BELOW that because the design wants it *poppable from range* — the counterplay is "shoot it before it reaches you" (the same counterplay Boomalope's 0.65 encodes, scaled up to guardian class). ⚠️ open, §6 |
| `body` | `QuadrupedAnimalWithHoovesAndHump` | Boomalope's own body (Core). Reused for one reason: it already carries a **Hump** part, which gives the sacs a hittable body part for injury flavour without a new BodyDef. Cosmetic labels ("hoof") only surface in health-tab injury text — accept, or file a BodyDef later (§6) |
| `combatPower` | **200** | between Fleshbeast 50 and FleshMonstrosity/Splicehulk 240–250; it is a one-shot hazard, not a sustained fighter |
| `MoveSpeed` | **2.6** | slower than Boomalope 3.4: a slab on short legs. Slow is the counterplay's other half |
| `Wildness` | 1.0; `trainability None`; `canBePredatorPrey false`; `herdAnimal false`; `manhunterOnDamageChance 1.0` | untameable guardian, always turns on what hurts it |
| `foodType` / `baseHungerRate` | `OmnivoreAnimal`, low (0.2) | it must not starve to death (and detonate) inside a sealed gallery before the player arrives — set hunger low; or better, place it via a symbol that spawns on activation (§4) |
| `lifeExpectancy` | 30 | irrelevant in play; prevents old-age death in a dormant complex |
| meat / leather | `MeatAmount` explicit **0** or a `useMeatFrom` on an existing inedible; `leatherDef` none | nothing of value comes off it — no boomalope-milk economy returns through the back door. ⚠️ open whether butchering yields a goo item, §6 |
| `tradeTags` | none | never traded |

**Melee tools** (Law 3, `beast_normalization_spec.md`: best hit ≈ 12–15 × bodySize for
bs ≥ 1, DPS sublinear via 3–4 s cooldowns; K = 15 shipped):

| tool | capacity | power | cooldown | linked group | note |
|---|---|---|---|---|---|
| body slam | Blunt | **40** | 3.5 | `HeadAttackTool` + `ensureLinkedBodyPartsGroupAlwaysUsable true` | 13.3 × bs — inside the ruled 12–15 band, below the K=15 ceiling of 45. Linked group is Boomalope's own head-tool pattern (61 uses across Core races; no vanilla animal tool links a torso group, so none is invented here) |
| maw | Bite | 14 | 2.0 | `Teeth` | the chip damage between slams |

---

## 3. Mechanic — what happens when it dies

### 3a. The real mechanism (read from Core source via RimSage)

Boomalope: `race.deathAction.workerClass = DeathActionWorker_BigExplosion`
(Core `Races_Animal_CowGroup.xml`). Boomrat: `DeathActionWorker_SmallExplosion`
(`Races_Animal_SquirrelGroup.xml`). The workers (`RimWorld/DeathActionWorker_BigExplosion.cs`,
`_SmallExplosion.cs`):

```
BigExplosion:   radius 1.9 (life-stage index 0) / 2.9 (index 1) / 4.9 (index ≥ 2),
                damType Flame, GenExplosion.DoExplosion(...), DangerousInMelee = true,
                DeathRules = Transition_DiedExplosive
SmallExplosion: radius 1.9, Flame
```

`Flame` (`Core/Defs/DamageDefs/Damages_Environmental.xml`): `defaultDamage 10`,
`defaultArmorPenetration 0`. `DoExplosion` with `damAmount = -1` uses the DamageDef's
default. `DeathActionProperties` (`Verse/DeathActionProperties.cs`) carries **only**
`workerClass` — there is no XML knob for radius, damage or damage type on the vanilla
workers. The complete vanilla worker set is `Simple`, `Vanish`, `Divide`, `BigExplosion`,
`SmallExplosion`, `ToxCloud` (ToxCloud: `ToxGas`, radius 0.9/1.9/2.9, Biotech-gated).

### 3b. 🔴 The trap the build must not fall into

**`DeathActionWorker_BigExplosion` picks its radius by LIFE-STAGE INDEX, not by adulthood.**
A def with a single `lifeStageAges` entry (the natural thing to write for a guardian that
is never born) has `CurLifeStageIndex == 0` and detonates at the **baby radius 1.9**, not
4.9 — silently, with no error. The Boomalope only gets 4.9 because it has three stages.

⇒ **Build rule:** either (a) declare three `lifeStageAges` (`AnimalBaby` minAge 0,
`AnimalJuvenile` 0.01, `AnimalAdult` 0.02 — every spawn older than a week is adult, and
the placement symbol can pin age anyway), or (b) write the custom worker in §3c, which
does not read the life stage. Whichever is chosen, **the verify step is a quicktest kill
and a count of the scorched cells** — a 4.9 radius is ~75 cells, a 1.9 is ~12; you cannot
mistake them by LOOKING.

### 3c. The spec'd behaviour — v1, zero C#

**Detonation on death**: `deathAction.workerClass = DeathActionWorker_BigExplosion`,
three life stages per §3b. Adult radius **4.9**, `Flame` 10 dmg, fires start across the
blast — the vanilla Boomalope blast, unchanged. In a flesh-gallery full of fleshmass and
`VFEI2_Infested*` set-pieces (the dungeon's fabric per `dungeons_arc_spec.md` §2) a fire
blast is the *right* flavour: the goo is fuel, the room burns, and the other guardians
(all flesh) burn with it. That is a genuine guardian threat — the player who kills it
badly loses the gallery, the loot in it, and anyone standing close.

**Why not ToxCloud / a goo cloud for v1:** `DeathActionWorker_ToxCloud` is Biotech-gated
and its radius caps at 2.9; it reads as a Toxalope, which is already on the roster with
that exact mechanic. The commission says *explosive*; keep the explosion.

**Provocation**: `manhunterOnDamageChance 1.0` + `DangerousInMelee` (the worker sets it)
means: it charges whatever hurts it, and vanilla hunting AI already keeps hunters at
range from it. No custom aggro logic needed.

### 3d. v2 option — only if the build seat wants the goo to be visible (needs C#)

A ~15-line worker `RimMandrake.Utinni.<Mod>.DeathActionWorker_GooBurst : DeathActionWorker`
mirroring `BigExplosion` but calling `GenExplosion.DoExplosion` with named args
(`Verse/GenExplosion.cs`): `damType Bomb` (Core `Damages_Misc.xml`: `defaultDamage 50`,
`defaultArmorPenetration 0.10`, `isExplosive true`) at radius 3.9, `chanceToStartFire 0.6`,
`postExplosionSpawnThingDef` = a filth def (a goo splatter), `postExplosionSpawnChance 0.5`,
`screenShakeFactor 1.5`, and a fixed radius that ignores life stage. This is a real
mechanical difference (Bomb 50 kills what Flame 10 only burns) — **it is not the default;
the owner picks it or not (§6)**.

---

## 4. Placement — dungeon-guardian only, stated plainly

- **Roster:** added to `design/Jawa/worldbuilding/review/round2/reserved_groups_draft.md`
  §1 dungeon-guardians as an **Assailant** row (this pass, same table style as the four
  VQEA Splice rows), under the 2026-09-10 ruling "ONE roster with a dungeon-owner column".
- **Where it spawns:** inside the Assailant complex only — `ASSAILANT_DUNGEON_BUILD_1`
  (`dungeons_arc_spec.md` §2: the first-impact complex, deep Umbra, thaw-gated). It is
  placed by that dungeon's layout generator as a **pawn symbol**, the way
  `gen_vault_layouts.py` registers `PAWN_SYMBOLS` for the Forsaken vaults (the pattern
  `BOOM_FAMILY_CUT_1` removed `RUT_Symbol_Boomsnake` from). Because the complex is inert
  until the power core thaws it, the guardian should spawn **on activation** where the
  build allows, not sit for years in a sealed room (see the hunger note in §2b).
  Preferred rooms: the interior digested-works galleries and the approach to the core —
  anywhere the blast can cost the player something.
- ⛔ **Never:** `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`,
  `design/Jawa/fauna/BiomeCast_Ashkarr.xml`, `design/Jawa/fauna/cast_assignment.csv`, any
  `design/Jawa/worldbuilding/biomes/rosters/*.json` wildAnimals list, any trader stock,
  any manhunter/incident pool. Give the PawnKindDef no `wildSpawn`-eligible biome tags
  and keep the ThingDef out of every biome's `wildAnimals`. `canMakeRandomly`-style
  exposure is not a field on animals, so the guarantee is *absence from every cast*,
  which the roster JSON validator (`rosters/_validate.py`) can be taught to assert.
- The Forsaken **vaults** are NOT covered — `VAULT_DUNGEON_CONCEPT_1`'s Anomaly
  exclusion and the vault/Assailant split (`dungeons_arc_spec.md` §1) keep Assailant flesh
  out of Rakatan vaults. The Boomsnake slot the cut vacated in the Type-2 vault garrison
  stays vacated.

---

## 5. Art direction — the brief for the sprite pass

Follow `skills/generating-rimworld-sprites/SKILL.md` end to end (chroma-key → alpha →
conform → validator). This section supplies only what that skill needs told.

**Canvas.** `drawSize 3.0` → `creature_size_model.md` §4: `3.0 × 128 = 384` → round up to
**512 × 512**, generated at 512 (achieved ~170 px/cell; record it in the PLAN.md). Three
facings — `_south`, `_east`, `_north` (west is the mirrored east by default; the donor
flesh mutants ship exactly these three). A `Dessicated_` corpse variant is optional; the
donor register has one per creature, and a burst lampgut corpse is a good place to show
the emptied, flapping sacs — **if made, it is the same canvas.**

**texPath** (proposed, RimUtinni mod folder): `Things/Pawn/Animal/Vhessk/Vhessk` with the
three facing suffixes. Texture binds by texPath, not defName (memory:
`texture-binds-by-texpath-not-defname`) — the PawnKindDef `lifeStages` entries must all
point at it.

**Camera and silhouette.** Top-down RimWorld animal camera, subject filling ~80 % of the
canvas width in the south facing, centred, no ground shadow baked in, hard near-black
outline (the donor register's outline weight, ~2 % of canvas width). The body plan of
§2a: low broad slab, six-to-eight short legs in an uneven row, frontal toothed cleft, no
eyes. **Five to seven taut translucent sacs of unequal size on the back and upper flanks,
the two largest dorsal, one visibly over-inflated.** Every sac carries a specular
highlight and a darker fluid line at its base.

**Palette — measured, not invented.** The flesh-mutant register sampled from the three
donor sprites (dominant opaque colours, quantised to 16 levels):

| role | value | source |
|---|---|---|
| outline / deepest shadow | `#000000`–`#201010` | 12–17 % of every donor sprite |
| body, main flesh | `#402020`, `#503030`, `#604040`, `#705050` | Fleshgrowth/Fleshbeast body mass |
| body, lit flesh | `#805050`, `#902020` | Fleshbeast/Monstrosity highlights |
| raw-flesh highlight | `#c06060`, `#d09080` | Fleshgrowth's salmon tips |

Use that for the **body**, so it sits beside the GR/VQEA mutants as one family. For the
**sacs**, take the campaign's own established goo palette rather than the donors':
`the_slime.md` §"artistic theme" — *"translucent greens and ambers, membrane pinks"* — and
`the_contagion.md` §9 — *"pink-and-blue aberrations, the grey-white of husks"*. So: sac
membrane in a desaturated membrane-pink (`#c08080` family) over a **sick amber-green
fill** (chemfuel-amber toward bile-green; it must read *fuel*, not water), with a small
near-white specular. **Value rule:** the sacs must be visibly LIGHTER than the body so
they read at 3 cells on a dark floor — that is the whole recognisability of the creature.
⛔ No desert tans, no scavenger rust: this is dungeon content, not Jawa kit. ⛔ No visible
Earth-animal cue (no cow/goat head, no hooves drawn as hooves) — `creature_recognizability_rule.md`,
and size amplifies the penalty (amendment 2).

**Prompt (paste-ready for the generator; keep the invariants every iteration):**

> Top-down game sprite of an alien flesh creature, RimWorld art style, flat matte shading
> with a hard near-black outline, plain white background. A low, wide slab of wet dark-maroon
> muscle (colours #402020 to #705050 with salmon #c06060 highlights) seen from directly
> above, longer than wide, with six to eight short thick uneven legs along each flank and a
> lipless toothed cleft at the front, no eyes, no face. Along its back and upper flanks bud
> five to seven taut translucent bladder-like sacs of different sizes, the two largest on the
> spine, one over-inflated; each sac is a pale membrane-pink skin over a glowing sick
> amber-green fluid with a bright specular highlight and darker fluid pooled at its base,
> thin dark veins across the membrane. Sacs lighter than the body. Asymmetric, diseased,
> organic-wrong; nothing that resembles a cow, goat or any Earth animal. Centered, filling
> most of the frame, no shadow, no text.

Then the east facing ("seen from its right side, walking to the right, same creature, same
sacs") and the north ("seen from directly above with the head away from the viewer"); state
the silhouette, canvas and palette invariants in every iteration (SKILL.md's rule).

**Acceptance (the validator says shippable; only these say good):** at 3 cells on the
review sheet, a viewer who has never read this doc should say "the one with the bladders";
it must not be nameable as an Earth animal; it must sit beside `GR_FleshGrowth` on the
same sheet and read as the same family.

---

## 6. What this brief explicitly does NOT decide

Left open for the owner / BENCH, with the default that ships if nobody rules:

| open call | default in this brief | why it is open |
|---|---|---|
| **v1 vanilla worker vs v2 goo-burst C#** (§3c vs §3d) | v1, zero C# — Flame 10 at radius 4.9 | v2 is a real lethality change (Bomb 50) and a new DLL; owner's call whether the visible goo is worth it |
| `baseHealthScale` 2.0 | 2.0 | deliberately below the doctrine's health-∝-mass reading (~3) to keep "pop it from range" as counterplay; the owner may want it tougher |
| body slam 40 / bite 14 | as proposed | inside Law 3's ruled band; not quicktested |
| `MarketValue` | none set (it is never traded) | if the owner wants a corpse/goo item to be worth something, that is an economy call |
| butchery yield | 0 meat, no leather | whether a "vhessk sac" goo item exists (fuel? a crafting reagent?) is new economy, not this commission |
| a real BodyDef | reuse `QuadrupedAnimalWithHoovesAndHump` for its Hump part | a bespoke body with "sac" parts is cleaner but is its own small build |
| glow | none — the glow is painted into the sprite only | a `CompProperties_Glower` on a pawn is a mod-pattern question, not confirmed here |
| spawn-on-activation vs pre-placed | prefer on-activation | depends on how `ASSAILANT_DUNGEON_BUILD_1`'s thaw-gate is actually wired (itself HELD FOR OWNER) |
| directory | this file lives at `design/Jawa/worldbuilding/creatures/` (new) | the only prior single-commission brief (`fish_bestiary_commission_2026-09-10.md`) sits flat in `worldbuilding/`; BENCH may prefer to move this beside it |

---

## 7. Sources read for this brief (so the next reader need not re-derive)

- `infrastructure/state/items/BOOM_FAMILY_CUT_1.md`, `ASSAILANT_FLESH_DUNGEON_1.md`, `ASSAILANT_DUNGEON_BUILD_1.md`
- `design/Jawa/worldbuilding/review/round2/reserved_groups_draft.md` §1, §9, rulings 2026-09-10
- `src/RimUtinni/UtinniPatches/Patches/AncientsAreRakata.xml` header; `ANCIENTS_AS_RAKATA_SPEC.md`; `reconciled_lore/03_deep_history.md`; `infrastructure/state/canon.yml` `assailant_reveal_arc`, `anomaly_content`; `dungeons_arc_spec.md` §1–2; `biomes/assailant_weapon_remnants.md`, `the_contagion.md` §9, `the_slime.md` palette line
- `design/NAMING_SCHEME_PLAN.md`; `Alien_Bestiary.md` §1; `creature_names_ashkarr.md`; `creature_recognizability_rule.md`; `creature_normalization_doctrine.md`; `creature_size_model.md` §1, §4; `beast_normalization_spec.md` Law 3
- Core `Races_Animal_CowGroup.xml` (Boomalope), `Races_Animal_SquirrelGroup.xml` (Boomrat), `DamageDefs/Damages_Environmental.xml` (Flame), `Damages_Misc.xml` (Bomb); Biotech `Damages_Misc.xml` (ToxGas)
- RimSage: `DeathActionWorker_BigExplosion`, `_SmallExplosion`, `_ToxCloud`, `DeathActionProperties`, `GenExplosion.DoExplosion`, and the worker-class sweep
- VGE (ws 2801160906) `1.6/Defs/ThingDefs_Races/Races_Animal_Failures.xml` and `Races_Animal_BoomHybrids.xml`; the three flesh-mutant PNGs (viewed and colour-sampled); VQE Ancients (ws 3618306875) `1.6/Defs/ThingDefs_Races/Races_Animal_Mutants.xml`
- `skills/generating-rimworld-sprites/SKILL.md` (canvas, facings, validator)
