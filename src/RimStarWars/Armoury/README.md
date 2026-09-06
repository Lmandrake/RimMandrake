# Jawa Armoury Rebalance

_First pass at the weapon retune, 2026-08-10/11. Derived from
`design/Jawa/worldbuilding/setting_physics.md` (the 18 laws) and
`design/RimMandrake/balance_paradigm.md` (why we change any value)._

**Status: built, validated, NOT YET ENABLED.** It has never run in game.

---

## Why

Measured on the live post-patch dump of this exact 562-mod stack:

- **Median ranged damage was 12.** Against a ~40 HP torso, four in five weapons
  needed **three or more hits** to drop an *unarmoured* person.
- **Median blaster damage was 10 — a human fist does 8.2.** A stormtrooper was
  22% more effective than a colonist punching you.
- **Melee beat ranged across the board**: lightsaber 28, vibro 24, conventional
  melee 22, versus blaster 10. **A wooden club outperformed a blaster rifle.**
- **`OuterRim_Gun_HeavyTurbolaser` did 80** — 1.45x a vanilla sniper turret,
  where L9 asks for two orders of magnitude.
- Everything from fist to capital battery lived inside a **10x range**. The
  problem was never any single number; it was **compression**.

## What it does

| rung | before (median) | after | shots to kill (40 HP torso) |
|---|---|---|---|
| slugthrower | 10 | **27** (18–36) | 4.0 → **1.5** |
| blaster | 10 | **25** (24–34) | 4.0 → **1.6** |
| vibro | 24 | **44** (35–52) | 1.7 → **0.9** |
| lightsaber | 28 | **35** (see KNOWN DEFECTS #2 correction — "99" below was this pass's original, unshipped number) | 1.4 → **0.5** |
| turbolaser | 80 | **1400** (800–2000) | 0.5 → 0.03 |
| ion / stun / EMP / sonic | 8 | **8 — untouched** | — |
| explosives | — | **untouched** | — |
| torpedo *speed* | 50 | **12–18** | — |

**What is deliberately NOT changed:**

- **Verb weapons** (ion, stun, EMP, sonic, disruptor) keep near-zero damage. The
  verb IS the weapon (L4/L16) — an ion gun that kills is just a worse blaster.
- **Blast values.** Explosions stay devastating against every form of protection
  (L13); scarcity is the only thing balancing them. What was wrong with missiles
  was the *delivery*, not the warhead.
- **Conventional melee, and every non-Star-Wars weapon.** Out of scope for pass 1.

**Relative order inside every family is preserved.** This restretches the
ladder; it does not flatten it.

## Torpedoes (L13c)

Missiles travelled at **speed 50 — the exact speed of a blaster bolt**, and the
median of all 537 projectiles. A warhead indistinguishable from a bullet is the
hypersonic missile this setting says was never built.

Slowing them to 12 (heavy, blast >= 2.5) or 18 (personal) makes them fit:
they pass deflector screens because screens stop *fast* things (L6), and they can
be seen and dodged, which is the counterplay that makes a no-hard-counter weapon
tolerable. A colonist moves ~4.6 cells/sec: at speed 50 a warhead crosses 20
cells in 0.4 s (no reaction possible); at 12 it takes 1.4 s and the target covers
~6 cells. **That is the difference between a cutscene and a decision.**

Anything already at or below speed 26 was left alone — `KotORMissile_seeker` and
`_whistlingbird` were already right, and there is no reason to overwrite good
work.

---

## KNOWN DEFECTS — read before trusting the numbers

### 1. The heavy-blaster tier did not separate

**Median "heavy" is 25, the same as standard.** The patch classifies
*projectiles*, but "heavy" appears in *weapon* names: `guy762_hvyrepeater` and
friends fire `KotORBlasterBolt_default`, the same bolt as every pistol. A
projectile-level patch cannot tell them apart.

Fix: give a handful of iconic heavies their own projectile defs, or accept the
mod authors' verdict that a heavy repeater is a faster-firing standard bolt.

### 2. All 15 lightsabers are now identical at 99 — STALE, see correction below

A direct consequence of patching the declarer. They share one base
(`Force_LightsaberBase`), so **one node means one value** — the generator
computed an 80–120 spread and then wrote a single number. Not wrong, but not a
spread.

Fix: `PatchOperationAdd` a `tools` block per saber, so Anakin's blade can differ
from a training foil.

**Correction, 2026-09-06 (`ARMOURY_MELEEPOWER_STALE_1`):** the "99" above is
from this section's original 2026-08-10/11 pass and is not what ships. KotOR
Weapons injects its own `<tools Inherit="False">` onto 8 of the 15 sabers
(`LIGHTSABER_MELEE_PATCH_FAIL_1`, 2026-09-01), so only the other 7 are actually
reachable through `Force_LightsaberBase` — and `gen_armoury_patch.py`'s
declarer-vs-live-label comparison (`self_supplied_tools_defnames()`,
`b5da9f9b`) now writes those 7 at **hilt 12→15, point/edge 28→35**, not 99. A
fresh regen against a near-current (596/598-mod) dump reproduces this section
of `Armoury_MeleePower.xml` byte-for-byte, so the shipped 15/35/35 is current,
not stale — only this paragraph's "99" was.

### 3. Vibro out-damages blasters, 44 vs 25

Intentional under L14 (vibro shears ablative armour), but it means melee still
beats ranged on raw damage — the original complaint about the armoury. The
physics answer is that blasters win at *range* and armour is where the real
differentiation lives: vibro shreds ablative, blasters bounce off it. **Armour is
unpatched, so that half of the contract does not exist yet.** Decide deliberately
rather than discovering it in a firefight.

### 4. The generator cannot currently touch the absorbed KotOR/JDS melee weapons at all

`guy762_v*` (KotOR vibro-blades) and `RSW_JDSA_*` (JDS Armory vibro-blades) are
absorbed, retired-donor content (`ARMOURY_SWMODS_DONOR_GAP_1`, 2026-09-05):
their ThingDefs now live under `mandrake.rsw.armoury`'s own
`Absorbed_AdditionalMods` patches, so the live dump reports their `modName` as
**"Jawa Armoury Rebalance"** — our own mod's display name, not one of the
retired donor strings (`Star Wars KotOR Weapons and Armor`, `[JDS] StarWars -
Armory`) still hardcoded in `gen_armoury_patch.py`'s `SW_MODS` tuple. A regen
right now silently **drops** these 33 melee ops entirely rather than producing
wrong numbers — checked 2026-09-06 by running the generator to a scratch
output dir against a near-current (596/598-mod) dump. The 33 ops currently in
`Armoury_MeleePower.xml` are hand-preserved and NOT reproducible until
`SW_MODS` (or a `retired_mods`-style rename map) recognizes "Jawa Armoury
Rebalance" — and doing that pulls in 173 total weapon defs (most of them
ranged), so it is a separate, larger item, not a one-line fix here.

---

## THREE BUGS THIS MOD ENCODES

All three were found by reading output, not by reasoning. This is the argument
for generating patches rather than hand-writing them — a hand-written version
would have shipped all three silently.

**1. Projectiles are shared.** The first generator ranked *weapons* and wrote the
result onto their projectiles. `KotORBlasterBolt_default` backs most of the KotOR
line, so one heavy rifle dragged the whole family to 66 — and independent ranking
inverted `RSW_Low_Blue_Blaster_Bolt` (11→66) *above* `High_Blue` (25→34). Ranged
damage is a property of the projectile, so the **projectile** is the unit of work.

**2. Patches hit raw XML, before inheritance.** All 15 lightsabers inherit tools
from abstract `Force_LightsaberBase` and declare none of their own, so xpaths
naming a concrete saber matched **zero nodes** and would have thrown a red error
every launch. The validator caught 33 of these. Aiming at the declaring ancestor
fixed it and collapsed 15 operations into 1 — which is also *why* every
lightsaber had identical stats to begin with.

**3. Explosives are not a damage rung.** A grenade at damage −1 was assigned 24,
and the missile launcher was *nerfed* 100→72. Projectiles with damage ≤ 0 are
effect-driven; rewriting `damageAmountBase` on one does nothing useful and can
silently disarm it.

---

## Layout and regeneration

```
About/About.xml
Patches/Armoury_RangedDamage.xml    30 ops   generated
Patches/Armoury_MeleePower.xml      52 ops   generated (19 declarers)
Patches/Armoury_TorpedoSpeed.xml    17 ops   generated
Source/gen_armoury_patch.py         damage + melee power
Source/gen_torpedo_speed.py         warhead speed
Source/compare_ladder.py            before/after verification
```

**Do not hand-edit the XML.** Re-run the generators:

```bash
python src/RimStarWars/Armoury/Source/gen_armoury_patch.py
python src/RimStarWars/Armoury/Source/gen_torpedo_speed.py
python skills/rimworld-modding/scripts/validate_patch.py src/RimStarWars/Armoury/Patches \
   --defs ".../workshop/content/294100" --defs ".../RimWorld/Mods" --defs ".../RimWorld/Data"
```

The generators read **both** layers: the live dump (`RimDefDump`) for
post-patch truth, and `src/RimMandrake/Utils/def_inventory.py` for who *declares* each node —
because a patch must aim at the declarer, not the inheritor.

`compare_ladder.py` reads the new values back **out of the generated XML**
rather than recomputing them, so it measures what will actually ship.

## Every operation is guarded

Wrapped in `PatchOperationFindMod`. Unguarded, a `Replace` whose target mod is
absent logs a red error on every launch — and this mod must stay droppable.
Validation: **3 files, 0 errors, 0 warnings**, down from 163 warnings on the
first attempt.

## Enabled — this text was stale

This section used to say `mandrake.rsw.armoury` was not in `ModsConfig.xml`.
**That is no longer true.** Measured 2026-09-05: it IS active in the live
595-mod `ModsConfig.xml`, and the ledger (`ARMOURY_LIGHTSABER_FINDMOD_1`,
`ARMOURY_SOUND_PATHS_RSW_PREFIX_1`, `LIGHTSABER_RECIPE_GATE_1`) shows BENCH and
FOUNDRY deploying and live-verifying Armoury fixes against the full campaign
list across multiple 2026-09-04/05 sessions. Do not trust this doc's enabled/
disabled claims without checking `ModsConfig.xml` yourself — this file drifted
out of sync with reality without anyone updating it.
