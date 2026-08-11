# armoury_keeplist.md — the proposed weapon roster

_Drafted 2026-08-10 from the live post-patch dump (674 weapons across 60 mods).
Decisions follow `worldbuilding/setting_physics.md` and
`worldbuilding/balance_paradigm.md`. **Proposal for review — nothing cut yet.**_

**The test each weapon must pass:** does it look like it belongs in this galaxy,
and does it hold a rung on the ladder or a verb no one else has? A weapon that is
an Earth firearm with a new name fails both.

**Current state:** 674 weapons. **Proposed: ~330 in, ~344 out.**

---

## IN — the roster

### Backbone (the Star Wars armoury) — 230

| mod | n | what it carries |
|---|---|---|
| **Star Wars KotOR Weapons and Armor** | 137 | the core. Blasters, **slugthrowers**, ion/sonic/disruptor pistols, vibro melee |
| **Outer Rim — Core** | 40 | blasters, turbolasers, ion cannon, **28 mines**, grenades |
| **[JDS] StarWars — Armory** | 33 | vibroblade/sword/axe, missile launcher, ECD grenade |
| **Star Wars : The Force — Lightsaber** | 15 | every lightsaber |
| **Outer Rim — Droid Depot** | 5 | droid-mounted weapons |

This is the whole ladder in one place, and it already contains the verbs.

### Utility & the strange — 28

| mod | n | why |
|---|---|---|
| **Ion Weaponry (Continued)** | 7 | dedicated ion — the salvage-intact verb (L4/L17) |
| **Alpha Mechs** | 21 | tesla, acid spewer — alien, non-Earth silhouettes |

### Creature weapons and harvested parts — ~60

Natural attacks and the trophies cut from them: thrumbo horn, gallatross horn,
insectoid stingers. These *are* the "every creature leaves something behind"
principle already implemented (Axis 7), and none of them read as Earth.

Star Wars Animal Collection (10) · Mythic Ages: Megafauna (17) · Biomes! Caverns
(11) · Alpha Genes (9) · Megafauna (6) · Alpha Animals (4) · VFE Insectoids 2 (3)
· Biomes! Polluted Lands (3) · Dark Ages: Beasts (2) · Horrors (2)

### Traps, mines and IEDs — ~35 — **the Jawa specialty**

| mod | n | why |
|---|---|---|
| **Custom Gas Types** | 20 | literally `CGT_TrapIED_*` — tear gas, N2O, and friends |
| **Outer Rim mines** | *(within the 40)* | frag, cryoban |
| **Vanilla Furniture Expanded — Security** | 12 of 21 | landmine, shockmine, bear trap |

**Mines and emplaced traps are the premier anti-shield weapon** (L13a) and the
prepared-ground answer a poor colony has to rich infantry. This is a keep-and-
*expand* category, not a keep-as-is one.

### Scavenger tier — 5

**Vanilla Weapons Expanded — Makeshift** (5). Pipe guns and improvised trash.
Cut on the "no Earth guns" rule, kept on the Jawa rule: this is what you build
from a wrecked speeder, and it is the visual bottom of the ladder.

---

## OUT — and why

| mod | n | reason |
|---|---|---|
| **Ancient urban ruins** | 35 | **literal Earth firearms** — AK, M700, MK18, SR25, TKB. The single worst offender for breaking the setting |
| **Vanilla Weapons Expanded** | 61 | Earth analogues: trench gun, sawn-off, HMG, battle rifle, longbow, crossbow |
| **Core** | ~45 of 51 | vanilla rifles/pistols/shotguns. Keep only what is needed as "ancient salvage" |
| **Fortifications — Industrial** | 11 | modern military autocannon/MG |
| **Destiny Exotic Weapons** | 9 | strong art, wrong universe |
| **Dungeon Pack** | 10 | fantasy (Thor hammer) |
| **Vanilla Brewing Expanded** | 6 | joke melee |
| **Metal Pipe / ModularWeapons 2** | 7 | redundant with the Makeshift tier |
| **Biotech / Odyssey / Royalty** | ~30 | case-by-case; Royalty persona melee may be worth **reskinning** rather than cutting |
| **Big and Small — Weapons** | 14 | keep only if oversized xenotypes stay |

**Note on Core:** cutting vanilla weapons wholesale is risky — they are
referenced by scenarios, raid loadouts, trader stock and quest rewards. Prefer
**Cherry Picker removal** or making them non-craftable salvage, over deletion.

---

## Missiles — cut the launchers, keep the torpedoes

**21 missile/rocket weapons exist. 18 are not Star Wars** — vanilla's rocket,
triple-rocket, doomsday and grenade launchers, VWE's charge missile launcher,
Yayo's anti-armour rocket, Big and Small's Warmech launchers. All were already
on the cut list, so removing the hypersonic missile costs almost nothing.

The three Star Wars ones stay, **reframed as slow torpedoes** (L13c/L13d):

| def | mod | new role |
|---|---|---|
| `OuterRim_DroidWeapon_WristRocket` | Outer Rim | the Mandalorian wrist rocket — iconic, personal, rare |
| `JDSA_E-60R_Missile_Launcher` | [JDS] Armory | shoulder torpedo, anti-emplacement |
| `guy762_rocketrifle` | KotOR | specialist launcher |

The reframe, not a nerf: make them **slow**. A slow warhead passes deflector
screens (L6), can be seen and dodged, and is therefore only worth firing at
something that cannot move — an emplacement, a vehicle, a shield generator, a
VAST creature. That makes them the **ranged** anti-shield weapon where mines are
the **emplaced** one, and it is exactly the proton-torpedo-down-the-trench image.

Better still, give them **verb warheads** rather than blast: ion (disables *and*
leaves salvage), buzz droid, net, gas. Then a torpedo is the only way to put an
effect somewhere you cannot reach — a role nothing else in the armoury fills.

## The gaps — where a new mod might be needed

The keep-list covers the ladder better than expected. Three genuine holes:

1. **Ship-scale weaponry (L9) does not exist.** The heaviest thing in the game
   is an 80-damage turbolaser. We need something two orders up, or we author it.
   Likely ours to build rather than to find.
2. **Vehicle-mounted / emplaced heavy weapons** are thin. Vehicle Framework is
   installed; whether it brings weapons is unchecked.
3. **More non-damage verbs.** We have ion, EMP, sonic, stun, disruptor, acid,
   flame. Missing and desirable: **entangle/net**, **adhesive**, **blind**,
   **carbonite/freeze** (Cryoban is close), **tractor/displace**.

**Not a gap:** slugthrowers. `guy762_slugrifle`, **Tusken Cycler**, *Verpine
Shatter Gun*, *Kaleesh Battle Rifle*, *Cinnagaran Battle Rifle*, *Trandoshan Mass
Driver* and `OuterRim_CyclerRifle` already exist with real Star Wars identity.
They are all pinned at damage 10 (Cycler 28), so the range must be **created by
retuning**, not by adding a mod. Under L11 these become the correct answer to
desert megafauna, which gives the whole family a permanent role.

---

## Why the Jawa are trap-layers and gunsmiths

Falls out of the physics rather than being decided:

- **L17** — this civilisation runs enormous power through minimal containment, so
  every discarded power cell, spent blaster and dead droid is *already a bomb*.
  A scavenger culture sitting on a mountain of failing hardware does not have to
  manufacture explosives. **It has to decide where to put them.**
- **L18** — everything wears out, so the Jawa's obsessive repair work is
  preservation practised inside a consumerist, replacement-centric Imperial
  culture. They are not tinkering for fun; they are refusing to let power decay
  (Axis 18d).
- **L13a** — mines and emplaced charges are the premier anti-shield weapon, so
  the poorest faction on the planet holds the hardest counter to the richest.

That is a faction identity derived entirely from the physical laws, and it is
the kind of coherence these documents exist to produce.
