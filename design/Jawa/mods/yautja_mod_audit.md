<!-- status: live -->
# yautja_mod_audit.md — what `[AB] Xenotype: Yautja` actually brings

DECIDE owns this. Written 2026-08-15 to answer the owner's question at the
Configure Factions screen: *"We still need to know if we need any of its unusual
genes or items."*

**Owner's ruling, 2026-08-15:** the four Predator factions are **NOT unticked at
worldgen**. Configuring them away would mean either an extensive cherrypick or
deprecating the mod, and neither is decided — so the factions stay, and the real
choice is made later against this audit. Keeping is the recoverable direction: a
faction present at world creation can be emptied afterwards, and one that is
absent can never be added.

`biotechrace.yautja.alleyballey`, workshop `3536839586`. Loads `1.6` and `Common`,
216 XML files. **Nothing in it is currently cut** — it survived the weapons and
apparel reviews intact.

| def type | count |
|---|---|
| GeneDef | 431 (**54** in `ABYautjaCategory`; the rest are HAR/head/hair plumbing) |
| ThingDef | 146 — **36 weapons**, **26 apparel**, 9 buildings, 75 other |
| HediffDef · RecipeDef | 75 each |
| PawnKindDef | 40 |
| HeadTypeDef · HairDef | 102 · 191 |

---

## The genes: 14 are mechanical, ~40 are Predator cosmetics

**This is the split that matters.** Roughly three quarters of the Yautja gene
category is appearance — tendril hair in four variants, crest patterns, X-ray
skulls, translucent head lines, visible blood vessels. Those are Predator's
*look*, they are useless to us, and they are the bulk of the count.

The ones that carry a mechanic, and are unusual enough to be worth wanting:

| gene | why it is interesting here |
|---|---|
| **`ABYautja_HeatPits`** — heat pits | Infrared sensing. Nothing else in the stack does this, and a heat-sensing species on a tidally locked world is a genuinely good idea |
| **`ABYautja_Ambush`** — predatory ambush | 🔴 **The only gene in the set that grants an ABILITY** (`ABYautja_Ambush`). Everything else is passive. That makes it the single hardest thing to reproduce |
| **`ABYautjaMonocolorVision`** | Vision restricted to one colour band. Pairs with heat pits as a sensory trade |
| **`ABYautjaKeenSenses`** — hunter's keen senses | Straightforward perception gene |
| **`ABYautja_BreedingSeason`** — seasonal breeding | A reproduction *rhythm* rather than a rate. Unusual, and it would suit an egg-laying clan |
| **`ABYautjaExtra_Terrestrial`** — space faring | Off-world origin as a gene |
| **`ABYautjaAdvancedTechnologically`** — alien intelligence | Research/tech aptitude |
| **`ABYautjaClaws`** · **`ABYautjaLeatherySkin`** | Natural weapon and natural armour. Common patterns, cheaply replaced |
| **`ABYautja_GreenBlood`** — yautja blood | Changes blood filth and its colour |
| **`ABYautjaMenacingApperance`** · **`ABYautjaWarriorsMindset`** · **`ABYautjaSharpShooter`** | Social and combat modifiers. Ordinary; other mods supply equivalents |
| **`ABYautjaTwoToed`** | Cosmetic-adjacent, listed for completeness |

⚠️ **Do not judge these from this table alone before committing.** The labels are
read off the defs; the actual stat and hediff payloads were not measured. If any
one of them becomes load-bearing for a xenotype, read it first.

## The items: the shoulder mounts are the real find

**Four utility-slot weapons.** This is the mechanic worth taking, and it is rare:

```
ABYautja_Utility_PlasmaCaster    shoulder plasmacaster
ABYautja_Utility_PlasmaNetGun    shoulder plasma-net gun
ABYautja_Utility_NetGun          shoulder net gun
ABYautja_Utility_Blazer          shoulder blazer
```

A ranged weapon that occupies the **utility slot instead of the hands** is close
to unheard of elsewhere in this stack, and it reskins onto Star Wars fiction
almost without effort — a droid's shoulder blaster, a bounty hunter's rig, a
Jawa's scavenged arm-mount. **The mechanic is the asset; the Predator art is not.**

**Capture-alive gear**, which suits a scavenger clan and a slaver economy:
`ABYautja_Gun_HandheldNetGun` · `ABYautja_Gun_HandheldPlasmaNetGun` ·
`ABYautja_Ranged_CinchingBola` · `ABYautja_Ranged_ElectroshockBola`.

**Thrown and returning weapons**, with no obvious equivalent kept elsewhere:
`ABYautja_Gun_SmartDisc` · `ABYautja_Gun_PoliNanoDisc` · `ABYautja_Gun_Shuriken` ·
`ABYautja_Gun_SpinningBlade` · `ABYautja_Gun_PlasmaSpinningBlade`.

**Thermal mesh** — `ABYautja_Apparel_ThermalMesh`,
`ABYautja_Apparel_AdvancedThermalMesh`, plus child versions. Heat-management
apparel on a world with a scorched dayside is thematically free.

**14 melee weapons** (combistaff, glaive, war-axe, elder sword, hand scythe…) —
competent but not scarce. BUILD's B24 uses the Yautja blade as its mid-tier
reference at AP 0.60; that is the one dependency the rest of the project has on
this mod today.

**The rest** — 11 bio-masks and armour pieces — are Predator silhouettes. Good art,
strongly branded, expensive to launder.

## What this means for the eventual decision

**Deprecating the mod costs more than the faction untick would have.** It is a
game-down window, it risks `Could not resolve cross-reference`, and B24 loses its
reference weapon. Against that, the mod is the only source of a utility-slot
ranged weapon and of an ability-granting sensory gene.

⇒ **The recommendation is an extensive cherrypick, not deprecation**: keep the
four utility mounts, the net guns and bolas, the discs, the thermal mesh, and the
dozen mechanical genes; cut the ~40 cosmetic genes, the bio-masks and the
Predator-branded armour. That leaves the mod earning its slot on mechanics we
cannot get elsewhere, with almost none of its fiction visible.

**Unresolved and owed to the owner:** whether the Predator *pawns* appear at all
once the factions are settled. This audit is about the parts, not the people.
