# research/RimMandrake/inspiration/ — mod dossiers under consideration

_Two research dossiers written 2026-08-11, filed here 2026-08-11 with a local
installed-state audit added._

| file | covers |
|---|---|
| `weapon_effects_research.md` | spectacular weapon **effects**: beams, lock-on, chain lightning, plasma, sludge cones, muzzle/impact VFX layers |
| `gadget_and_utility_inspirations.md` | **non-weapon** Star Wars material culture: droids, restraint bolts, holoprojectors, tools, medpacs, doors, scanners, repair economies |

**Neither is an install list.** Both are explicitly "for consideration"; both say
to source-audit before adopting. This README adds the one thing they could not:
what is already on this machine.

---

## The audit — 53 cited Workshop items vs. this install

Run against `ModsConfig.xml` and the Workshop folder, 2026-08-11.

### Already installed AND active — 9

| mod | note |
|---|---|
| **Star Wars KotOR Resources and Materials** | far larger than the dossier assumes — see below |
| **Star Wars KotOR Weapons and Armor** | 137 weapons; already on our balance ladder |
| **Star Wars KotOR Droids** | 44 droid pawns, 28 droid apparel/utility |
| **Outer Rim — Droid Depot** | 38 droid pawns, incl. `OuterRim_DroidFactory` |
| **Outer Rim — Furniture & Decor** | 516 buildings incl. Aurebesh decals |
| **Ion Weaponry (Continued)** | already in the verb budget |
| **VFE — Security** | Tesla/railgun/shock-mine emplacements |
| **Extra Explosion Effects** | already supplying blast spectacle |
| **Gunplay** | ⚠️ see the warning below |

### Downloaded but NOT active — 4

These are free to try: no download, no Workshop trip, just a checkbox.

| mod | why it matters |
|---|---|
| **Muzzle Flash** | the dossier's highest-leverage VFX item — a *patchable* per-weapon-family firing signature |
| **Vanilla Weapons Expanded — Laser** | the beam family + the salvaged/unstable-laser concept |
| **RimTek DigiPal** | wearable datapad; better gadget donor than the music player |
| **Recon And Discovery (Continued)** | HoloDisk / personality-record concepts |

### Not on this machine — 40

Everything else, including all four of the weapon dossier's top teardown targets
(Dedicated Turrets, Laser Cannon, Volt Weaponry, Dubs Rimatomics).

---

## What we already own, measured

The gadget dossier asks "what non-weapon Star Wars material culture can we get?"
The answer is: **most of it, already installed.**

| source | contents |
|---|---|
| KotOR Resources & Materials | **455 items**, 173 apparel/utility, 157 buildings, **21 repair kits / medicines**, 7 materials, 6 ingestibles |
| Outer Rim Furniture & Decor | **516 buildings** |
| KotOR Droids | 44 droid pawns, 28 droid sensors/shields/generators |
| Outer Rim Droid Depot | 38 droid pawns, 80 droid parts/items |

Materials already present include **`KOTOR_IngotCortosis`, `KOTOR_IngotBeskar`,
`KOTOR_AlloyDurasteel`** — which the armour pass
(`design/Jawa/worldbuilding/setting_physics.md` L8) treats as quest-gated law-breakers, and
they exist as real craftable stuff *right now*.

**Implication: the gadget dossier's shopping list is largely a curation problem,
not an acquisition problem.** The scarce resource is attention, not content.

---

## Two live conflicts worth deciding

**1. `Gunplay` is ACTIVE, and its own dossier entry warns against it.** The entry
records reports of projectile trails persisting and causing *severe performance
degradation*, and recommends studying it rather than installing it. It is
installed. On a 580-mod stack with a 23-minute load, a performance regression is
expensive to diagnose — this is worth a deliberate keep/drop decision.

**2. `OuterRim_DroidFactory` is active, and it contradicts stated doctrine.**
The Jawa creed in the gadget dossier reads *"We give the second hand to what
others discarded; we do not breed new hands."* An unrestricted droid factory is
exactly the unlimited-manufacturing ladder the campaign is trying to avoid
(`balance_paradigm.md` Axis 18 — power arrives as shards, not tiers). Cherry
Picker or a recipe patch would keep the droids and remove the printing press.

**3. Two complete droid architectures are active simultaneously** — Droid Depot
(38) *and* KotOR Droids (44), 82 droid pawns between them. The dossier
explicitly asks for a crosswalk before running both. We are running both.

---

## Related project docs

`required_mods.md` · `forbidden_mods.md` · `armoury_keeplist.md` ·
`outer_rim_cherrypick_list.md` · `../worldbuilding/setting_physics.md` ·
`../worldbuilding/balance_paradigm.md`

---

## Decisions taken 2026-08-11

| item | decision |
|---|---|
| **Muzzle Flash** | ENABLE — already downloaded; the per-weapon-family firing signature layer |
| **VWE Laser** | ENABLE — beam family + the malfunction-prone salvaged-emitter concept |
| **Gunplay** | REMOVED, replaced by **Better Projectile Origin** |
| **Dedicated Turrets** | ADDED |
| **Laser Cannon** | ADDED — the primary ship gun |
| **EGI Holograms and Projectors** | ADDED |
| **Doors Expanded: SW Edition** | not adopted — redundant with existing Security doors |
| **Survival Tools Reborn** | atmospheric, NOT hardcore. A few tools act as **keys** to ship-repair gates |
| **Dubs Rimatomics** | **offline resource only** — not installed. See below |
| **Droid frameworks** | keep BOTH, assigned roles; trim later (see TODO) |

### Why Rimatomics stays offline

Its weapons are coupled to its own reactor/capacitor grid and research tab;
"take the guns, drop the tree" is unlikely to be clean, and its cooling-tower
industrial aesthetic reads RimWorld rather than Star Wars. Laser Cannon already
supplies the charged ship-beam that was the main attraction. Kept as a source of
ideas and implementation patterns.

### The droid factory — mechanism, and why the fix is a building removal

`OuterRim_DroidFactory` is **`Asimov.Building_AutoCrafter` with
`CompProperties_AutoCrafter`** — custom C# from the Asimov framework. It has
**zero `RecipeDef`s attached**, so droid creation is driven by the comp, not by
recipes. Consequences:

- You **cannot** suppress individual droid recipes by XML; there are none.
- The lever is the **building**: remove it (Cherry Picker) or make it
  unbuildable. Removing the factory does **not** remove the droid part items,
  which are ordinary ThingDefs.
- That is exactly the split we want (see `balance_paradigm.md` Axis 18b):
  **parts stay craftable, whole droids do not.**

Unverified: how parts are installed into a droid. Droids are pawns, so they
inherit every vanilla medical recipe (the 114 "recipes" on
`OuterRim_AstromechDroid` are mostly `Administer_*` and surgery, not part
fitting). The part-installation mechanism still needs confirming before the
patch is written.

### TODO — pare the droid roster with RimBridge

**41 droid pawns across two frameworks is far past Axis 17's attention budget**,
but evaluating them by clicking through menus is painful. When RimBridge is
working, use `rimworld/execute_debug_action` to spawn every droid in a labelled
grid for visual side-by-side judgement, then cut.

⚠️ Read the traps entry first: enumerating debug actions on this stack once
livelocked the game and cost a 23-minute load. Learn the action path on a
throwaway quick-test colony, then call the known path here.

The same grid technique applies to the animal roster (1,247) and would pair well
with `animal_contact_sheet.py`, which already solves the offline half.
