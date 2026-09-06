# Retirement checklist — four mods, 2026-09-05

The owner ruled these four out on 2026-09-05: *"Agreed mythic ages is gone. Take
what we need from beasts of the rim and retire it and free seaswaterline. Drop
megafauna after taking what we need and clean up any references. Same for
Jurassic… Let's just add our own jerba."*

Authority for what each mod actually ships, and what depends on it:
`design/Jawa/worldbuilding/mod_retirement_audit.md`. **Nothing in the repo depends
on any of the four any more** — the repo side of this is DONE and is listed below
the line. What is left is the owner's, because it is the live mod list.

---

## 🔴 Before unticking ANY mod, check retirement ORDER — not just this doc's four

This rule outlives the four mods named above; it applies to every future
retirement, not only the 2026-09-05 batch.

A `PatchOperationFindMod` can add or remove a node when a donor mod is
absent. It **cannot** make a `ParentName` resolve. If a def anywhere in the
live mod set (ours or a donor's) inherits from an abstract `Name=` owned by a
different mod, and that owning mod retires first, the child def is silently
discarded — no Config error, no log line — and takes every def built on it
down with it. `DROID_RETIREMENT_ORDER_ASSERT_1` found this live:
`guy762_KotORDroidBase` (in kotorcore's `_DroidsBase` folder, loaded only
while `guy762.KotORDroids` is active) carries
`ParentName="ABF_Thing_Synstruct_HumanlikeBase"`, an ABF-owned abstract — so
`guy762.kotordroids` must retire no later than ABF/SynCore, or 12 downstream
droid ThingDefs vanish with nothing to connect the loss to this cause.

**Run this before touching `ModsConfig.xml`:**

```
python3 src/RimMandrake/Utils/retirement_order.py
```

It reads every known ordering constraint from
`infrastructure/state/facts/retirement_order.json` against the live mod list
and exits non-zero, naming the violation, if the mod you are about to untick
would break one. `src/RimMandrake/Utils/selftest_retirement_order.py` proves
the check actually fails on the bad state (a fixture, not the live file), and
runs automatically with every selftest pass.

**When a retirement sweep finds another absorbed-content `ParentName`
crossing into a donor scheduled to retire, add a row to
`retirement_order.json` — never a hardcoded pair of strings in a script.**
A full sweep of `src/` on 2026-09-06 (`DROID_RETIREMENT_ORDER_ASSERT_1`)
found this is the only such crossing today: no other def anywhere under
`src/` inherits via `ParentName` from an abstract owned by Asimov
(`neronix17.asimov`) or Outer Rim Droid Depot
(`neronix17.outerrim.droiddepot`), the two other donor mods currently
scheduled to retire per `design/Jawa/droids/DROID_PROGRAM_STATE_2026-09-06.md`.

---

## 🔴 What the owner does

⛔ Nothing here was done for you: `ModsConfig.xml` and the Steam subscriptions are
the owner's, by standing rule.

### 1. Enable one mod of ours FIRST — it holds the absorbed content

**`mandrake.rsw.swbestiary`** ("RimMandrake: SW — Bestiary") is **not in the
601-mod list today** and it is now where the absorbed creatures and the jerba
live. Deploy it and tick it on, or the eight absorbed creatures and `RSW_Jerba`
are simply absent.

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod SWBestiary          # dry run
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod SWBestiary --apply
```

Position it anywhere after Core; it declares no dependency on any of the four.
Then redeploy the mods whose patches changed:

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod SeasWaterline --mod Doctrine \
    --mod UtinniPatches --mod Armoury --mod StarWarsPatches --mod PawnFlavor --mod BeastLairs --apply
```

### 2. Untick the four, in this order

Order matters only in that the blocked one goes after the mod that blocked it.

| # | untick | packageId | why this position |
|---|---|---|---|
| 1 | Mythic Ages: Megafauna Bestiary | `veterano.mythicages.megafaunabestiary` | the clean kill — zero dependents, nothing absorbed |
| 2 | Megafauna | `Spino.Megafauna` | cleanup-only; every reference was conditional and is now deleted |
| 3 | Jurassic Rimworld - Dinosaurs Only (Continued) | `Mlie.JurassicRimworldDinosaursOnly` | only after SWBestiary is live, or the eight absorbed creatures have no home |
| 4 | Beasts of the Rim (Continued) | `Mlie.BeastsoftheRim` | last: it was the one with a HARD dependency declared against it (now removed) |

Use RimSort, per `skills/rimworld-start-prep`: Refresh, untick, **Save** — closing
the window writes nothing. Unsubscribing in Steam is optional and separate; it
changes disk folders, not the mod list.

### 3. Cherry Picker

The four mods' defNames are still in the live Cherry Picker cut list (1,291 cut
ThingDefs, 2026-09-04). Cuts naming a def that no longer exists are inert, so
this is tidying, not a blocker — but the next `cherrypicker.py` census will
over-count until they go.

### 4. What you will notice in play

- **The seas lose Megasquid.** Its Lake 0.38 / Ocean 0.2 was re-homed onto
  `DA_LeviathanCrab` (Dark Ages: Beasts and Monsters), which was at 0.12 / 0.06.
  The cast is 13 creatures, not 14, and the big offshore silhouette is now a crab.
- **`VEE_TribalHunter` loses the top of its weapon roll.** `MA_CapryakScatterbow`
  (520) was the bow at the top of that pool; the floor — the thing that decides
  whether the kind arms at all — is unchanged at 25 (`VFET_Throwspikes`).
- **`CreatureNames_Ashkarr.xml` is now empty.** All 37 of its Star Wars renames
  targeted Jurassic (20) and Megafauna (17) creatures. The file is kept because
  its generator owns it; give `gen_name_patch.py` new targets in
  `creature_names_ashkarr.md` if the pass is wanted again.
- **BoneAmount doctrine is not applied to the eight absorbed creatures.**
  `MeatAmount` was baked into their defs; `BoneAmount` is a modded StatDef and
  belongs in the generated patch. Add them to
  `src/RimUtinni/Doctrine/Source/gen_megafauna_yield.py`'s source list and re-run
  it when convenient.
- **`AnimalBiomeDuplicates_Fix.xml` needs regenerating from a fresh capture.**
  Seven of its operations went with the retired defNames; the Armadillo and
  Penguin ones could not go by name, because those defNames are vanilla AND
  redefined by Beasts of the Rim. With that mod gone the vanilla defs carry no
  `wildBiomes` at all, so those conditionals match nothing — dead, not harmful.
  `src/RimMandrake/Utils/biome_animal_conflicts.py` needs a LIVE dump, so run it
  after the mods are actually unticked rather than guessing now.
- **Four of the eight absorbed creatures were never cast on Ash'karr** —
  Segnosaurus, Holcorobeus, Termitotron, Baseopsis were on the CUT pile and are
  preserved, not placed. They keep their donor wildBiomes, which name biomes
  Ash'karr does not have, so they will not spawn wild until a cast pass places
  them. That is deliberate: absorbing is not the same as casting.

---

## ✅ What was already done in the repo

### Mythic Ages: Megafauna Bestiary — `veterano.mythicages.megafaunabestiary`
Nothing absorbed (0 of its 21 creatures survive the recognizability rule; its 61
thoughts, 37 recipes and 6 incidents exist only to service those creatures).
Removed: its `PatchOperationFindMod` group in `MegafaunaYield.xml`, its group in
`PawnFlavorPhase2_ThoughtDef.xml`, its group in `Armour_Leather.xml`, its group
plus 8 loose `MA_*` weapon operations in `WeaponTags_Renormalise.xml`, its
`MA_CapryakScatterbow` operation in `AncientArsenal_Ashkarr.xml`, its `MA_*`
entries in `BiomeCast_Ashkarr.xml`, `AnimalTolerances_Ashkarr.xml`,
`CreatureResize_Ashkarr.xml`, `AnimalBiomeDuplicates_Fix.xml` and
`AnimalBiomeDuplicates_Generated.xml`, and its `loadAfter` line in Doctrine's
About.xml. `MA_HarpeagleNest` survives only as a named influence in BeastLairs'
prose, marked as retired.

### Beasts of the Rim (Continued) — `Mlie.BeastsoftheRim`
🔴 **The blocker is cleared.** `src/RimStarWars/SeasWaterline/About/About.xml` no
longer declares `mlie.beastsoftherim` in `<modDependencies>` or `<loadAfter>`, and
its description no longer advertises Megasquid. The two Megasquid operations in
`Waterline_Lane1.xml` are gone and `seas_waterline_manifest.csv` matches. Its
groups and entries were removed from the same set of files as above, and its
`loadAfter` line dropped from Doctrine's About.xml. **Replacement built:**
`RSW_Jerba`.

### Megafauna — `Spino.Megafauna`
Nothing absorbed. Its `MegafaunaYield.xml` group, its four Ash'karr patch entry
sets, its `Armour_Leather.xml` group and its Doctrine `loadAfter` line are gone.

### Jurassic Rimworld (Dinosaurs Only) — `Mlie.JurassicRimworldDinosaursOnly`
**Eight creatures absorbed** into `src/RimStarWars/SWBestiary/` as `RSW_`-prefixed
ThingDef/PawnKindDef pairs, each with a provenance header saying exactly what
changed and why:

| absorbed | why it survives |
|---|---|
| `RSW_Segnosaurus` | the owner's own type-case; RESTORE_CANDIDATES.md #1, and the sprite that carries the therizinosaur silhouette where `JRWTherizinosaurus`'s own art does not |
| `RSW_Holcorobeus` | RESTORE_CANDIDATES.md #2 — reads as an alien armoured thing, not a rhinoceros |
| `RSW_Termitotron` | RESTORE_CANDIDATES.md #5 — machine-insect, in register for Star Wars |
| `RSW_Baseopsis` | live, STRANGE — segmented tube creature |
| `RSW_Diplocaulus` | live, STRANGE — flame-finned amphibian |
| `RSW_Platyhystrix` | live, STRANGE — sail-backed amphibian |
| `RSW_Protosolpuga` | live, STRANGE — unplaceable arthropod |
| `RSW_Protovermes` | live, STRANGE — red slug-blob; the only one already cast on Ash'karr |

The other two RESTORE candidates, **hydrazoa** and **jellybird**, are from
Primordial Geysers (`IronScruff.PrimordialGeysers`), a mod nobody is retiring —
they are out of scope here.

Absorbed with them: 16 egg items (`RSW_*EggFertilized` / `EggUnFertilized`), so
the creatures still breed rather than being silently converted to live-bearers;
27 creature textures plus 3 egg textures pulled out of the donor's AssetBundle
via `observed/inventory/bundle_textures/`. Every donor-only dependency was
replaced with a vanilla equivalent — the `AnimalDinoThingBase` abstract inlined,
`Leather_SmallDino`/`MediumDino` → `Leather_Lizard`,
`ExtraButcheringProducts.CompProperties_SpecialButcherChance` + `DinoChitin`
dropped (that comp class lives in the donor's DLL and would throw), the
`Pawn_Carnotaurus_*` SoundDefs → vanilla `Pawn_Thrumbo_*`, the
`Spooky/*Dessicated` corpses → vanilla corpses, `CarnivoreDinosaur` /
`HerbivoreDinosaur` trade tags → `AnimalUncommon`. The donor's 228 SoundDefs ship
their clips inside its AssetBundle rather than as loose `.ogg`, so they could not
be absorbed; every sound these eight now name is vanilla.

### The jerba
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Jerba.xml` — **new content,
not a port.** Beasts of the Rim's `Jerbal` was an After Man speculative "large
kangaroo-like gerbil" and never a Star Wars jerba. This is the real one: a
shaggy, horned, placid Tatooine pack-and-milk beast, bodySize 1.4, `packAnimal`,
`herdAnimal`, milkable, Advanced trainability, banded −12…60 °C and given
Desert / ExtremeDesert / AridShrubland commonality animal-side only (the
biome-side duplicate is the `CommonalityOfAnimal` crash that
`AnimalBiomeDuplicates_Fix.xml` exists for). Jerba is an **iconic Star Wars
creature**, so `creature_recognizability_rule.md`'s icon carve-out applies and its
being instantly nameable is the point.

**Art: reused, nothing generated.** It draws the already-absorbed **unwooled
bantha** sprite (`swanimals/Bantha/Bantha`, from Star Wars Animal Collection via
MLIE_FAUNA_ABSORPTION_1) at roughly a third of `RSW_Bantha`'s draw size in a pale
dun palette, with `BanthaPack_*` carrying the loaded-pack render. `RSW_Bantha`
uses the *wooled* `BanthaW` set in dark browns, so the two do not read as the same
animal. Plain `Cutout`, not `CutoutComplex` — only the wooled set ships masks.

### Verification run
- `python3 src/RimMandrake/Utils/run_selftests.py` — **38/38 passed**, 2 skipped
  (both skip by design: an art check needing a human `--reference`, and a package
  module needing its own venv).
- `validate_patch.py` on all ten touched patch files — **0 errors**.
- Every def, sound, leather, body, egg and parent the new files name resolves to
  vanilla or to this mod; every non-vanilla `texPath` they name exists on disk.
