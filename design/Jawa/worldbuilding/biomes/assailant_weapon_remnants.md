# The Assailant weapon remnants — the triptych's third panel (not a biome)

_Owner + BENCH, 2026-09-06. This doc holds what `HorrorWastes` and `AB_OcularForest`
would have been, after the owner ruled that **neither becomes a biome**: their content is
pillaged into a faction, injected dungeon content, and one named site._

## The triptych, stated once

The Assailant bioweapon, left alone too long with nature, met three ends:

| panel | sheet | what happened |
|---|---|---|
| **The Rot** | `the_rot.md` | nature won — the weapon was digested; only useful genes kept |
| **The Slime** | `the_slime.md` | the weapon won, and victory unmade it — a living archive |
| **The remnants** | *this doc* | **neither side won — the weapon is still fighting**, in two failure modes by energy regime |

The two failure modes are the grammar's own logic (one anomaly, two regimes):

- **Starved-cold patrol** — the deep nightside (Deadstone). Starved of energy and prey,
  the weapon has **degraded LESS than anywhere else**: slow, patient, cold-adapted,
  dormant in crysalises, surfacing to hunt and to *collect* (the BroodLord still takes
  victims alive — samples for a master who no longer exists). *"A semi-live version of the
  weapon slowly operating on the frozen darkside, showing its complex, alien, weaponized
  behavior far from the dayside"* (owner).
- **Overdrive-hot contagion** — the Overdrive (§ below): ambient heat and energy drove
  the weapon into **biological overdrive** — frenzy, mutation, infection of other
  lineages, burning itself out. Yet-another-failed-weapon-biology.

## 🔴 Rulings (owner, 2026-09-06)

1. **`HorrorWastes` leaves.** No sheet, no BiomeDef on the frozen world: its 1,711 tiles
   (MEASURED; Deadstone 1,457 + spills) **morph into their neighbors as usual** — the
   receiving def is ruled at the PropaneLakes sitting (Deadstone's other occupants:
   PropaneLakes 299, CrystalCaverns 194, IceSheet 49). Rides
   `HORRORWASTES_BIOME_DISSOLVE_1`.
2. **The Horrors become a RAIDING faction, not a settlement faction** — no bases, no
   settlements on the world. Players who land on the night side *encounter* them: the
   weapon on patrol comes out of the cold. Reach: a threat you walk toward, not one that
   finds you on the dayside (BENCH reading of the encounter framing; owner may widen).
   Rides `HORRORS_RAIDING_FACTION_1`.
3. **The Horror content goes into dungeons** — hives, dens, burrows, the sinkhole into
   the cave network, the molting crysalises, the mite-nest larders: injected onto
   nightside map tiles as Inhabited objects and dungeon templates (`fall_line.md`
   precedent: injection layer, no new BiomeDef). Same item.
4. **The Ocular Forest STAYS as a named site with a custom dungeon** — its 3 tiles in the
   Ashfall Range (MEASURED: lat −2..−0.7, lon 63..64, elev 2,177 m, 23 °C, dayside) are
   already a point feature. **Working name: the Overdrive.** It must be **woven into the
   plot more deeply**. Rides `OCULAR_OVERDRIVE_SITE_1`.
5. **The Rust Cathedral hates it** (owner): a mechanoid cathedral and a biological weapon
   in frenzy are natural enemies. ⚠️ MEASURED: the Overdrive sits **45.5° of arc** from
   the nearest Rust Cathedral tile — the enmity is written as *ideological and strategic*,
   not adjacency. If the owner wants them neighbors, that is a tile move to rule.

## What is pillaged, and from where

**From Horrors (Continued)** (`Mlie.Horrors`, ws 3535224844): the Horrors FactionDef
(re-shaped: raiding only), the six monster kinds (Visceral, Bulwark, Terrorworm, Harvester,
Prowler, BroodLord), the nest buildings (HorrorHive/Den/Burrow, MaggotNest, the collapsible
Sinkhole), the per-species crysalises (⭐ the cold-dormancy mechanic, free), the glowing
firefoam pustule, the horrorweb plant. Reskin toward cold-adapted forms.

**From Alpha Biomes' Ocular Forest** (+ Alpha Animals' patch): the **red fog** weather
(accuracy + mood, standing), the alien/red flora suite (alien tree, tentacular and globular
aberrations, blood bouquet, red grasses — note the earlier HorrorWastes flora pass already
borrowed half of these: the two were merging before anyone said so), and the **contagion
fauna**: Ocular Jelly (2.0), Red Spore, **Red Goo** (Green Goo corrupted — the weapon
infecting the Slime's own lineage), **Infected Aerofleet**. The motif is infection of other
lineages; lifeforms "not entirely alive"; ground that "fights against the neighbouring
lands."

## Hard bans (linter-checkable)

1. 🔴 **No Horrors settlement, base, or world-map holding** — a Horrors settlement def or
   settlement-generation weight above zero is a violation.
2. 🔴 **No `HorrorWastes` tiles on the frozen world** after `HORRORWASTES_BIOME_DISSOLVE_1`
   closes; no sheet is ever written for it.
3. 🔴 **The Overdrive stays a point** — Ocular content never spreads as terrain beyond its
   site; a biome-scale Ocular is a violation of the contagion-as-*site* ruling.
4. 🔴 **The war-legacy split holds**: this material never enters the Wasteland (its bans
   1–2), and the Rot/Slime stay the *disarmed* siblings.
5. 🔴 **The recognizability rule applies**; the icon carve-out protects mynock and neebray
   (legacy cast) wherever they re-home.

## Owed

- `HORRORWASTES_BIOME_DISSOLVE_1` — re-biome the tiles; receiving def ruled at the
  PropaneLakes sitting; legacy `cast_assignment.csv` rows (29, incl. mynock/neebray)
  re-home with them.
- `HORRORS_RAIDING_FACTION_1` — faction reshape (raid-only, nightside-gated encounters,
  reach rule), injection objects → dungeon templates, cold-adapted reskins, crysalis
  dormancy wired.
- `OCULAR_OVERDRIVE_SITE_1` — the named landmark, the custom dungeon, the plot weave
  (Rust Cathedral enmity; what the Overdrive is *for* in the campaign), a real name.
- Whether the Horrors' reach is nightside-only (BENCH reading) — owner's confirmation.
