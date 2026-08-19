# THE ONE MAP — Ash'karr, hand-authored once

**🔴 Owner's ruling, 2026-08-18:**

> *"We aren't trying to make random generators that produce alternative planet maps…
> that's way out of scope and produces unacceptably unreal solutions. I just want ONE
> planetary map that is as realistic as possible, following the guidelines I told you
> from design and discussion."*

> *"Make the rivers wind and fan out into salty deltas. Coat the rivers in jungles.
> Be free. You don't need to make Python that does this… just do it directly. See how
> far that gets you through iteration."*

- ⛔ **No generator.** Nothing that can produce a *second* planet: no seed sweep, no
  "roll N and pick", no exposed parameters, no worldgen step. A knob that could roll
  a different world is out of scope even if we would only ever turn it once.
- ✅ **One planet, authored.** Direct edits to `world/WORLDMAP_ashkarr.rws`, judged on
  **realism first** — does it read as a photograph of a real world — then against the
  design docs below.
- 🔑 **The loop is LOOK, not measure.** `worldview.py` renders the save; change,
  render, look, change again. The old pipeline's numbers all passed while the picture
  showed compass-drawn circles, comb-toothed rivers and rectangular roads. **The
  picture is the acceptance test.**

---

## What "realistic" means here — read off the owner's reference images

All in `D:\Luke\dev\Rimworld\research\Jawa\`.

| reference | what it is binding for |
|---|---|
| `planet_map_tidal_lock_inspiration.webp` | ⭐ **THE TARGET.** Whole-globe: a hot ochre dayside, a ragged **dark water crescent lying near — not on — the terminator**, green only where the water is, and a pale ice nightside. Water is torn and elongated, never a ring, never round. |
| `planet_inspiration_tidal_lock2.webp` | The same read from orbit: brown day face, blue-green terminator, white night cap. Confirms the colour story reads at globe scale. |
| `desert_map_inspiration2.jpg` | ⭐ **THE RIVERS.** Dark braided channels in red rock, **branching at acute angles**, tributaries converging downstream, never a straight run, never perpendicular teeth. |
| `desert_tilemap_inspiration2.jpg` | Canyon country: parallel dissected mesas, drainage cutting *back into* a massif. |
| `desert_tilemap_inspiration3.jpg` | Dune sheet — the **vast unbroken tract** with almost no feature in it. Emptiness is a texture, and most of the dayside should be this. |
| `desert_tilemap_inspiration4.jpg` | ⭐ **THE DELTAS / ALLUVIAL FANS.** Where drainage leaves the highland it spreads into a pale fan and dies. |
| `desert_zoomin_inspiration.jpg` | Salt pans and playas — irregular pale sheets with dark rock islands, no straight edge anywhere. |
| `spinning_inspirational_generic_desert_planet.gif` | Motion reference for the globe as a whole. |

**Five defects the references rule out**, all present in the 2026-08-18 painter output
and all visible in the first `worldview.py` render:

1. ⛔ **Circular seas.** Ash'karr had four discs and one literal annulus.
2. ⛔ **Comb rivers** — straight trunks with regular perpendicular teeth.
3. ⛔ **Rectangular roads** — closed boxes and ruler-straight diagonals.
4. ⛔ **Concentric biome rings** about the substellar point — a bullseye, so every
   direction out of the hot pole looks like every other.
5. ⛔ **Inherited names.** The regions were still the vanilla source world's
   (Josephine's Pride Mountains, Isle Ballerrei…). Ash'karr must name itself.

---

## 🔑 THE GEOMETRY, MEASURED — the tidal lock is a POINT, not a latitude band

`design/Jawa/worldbuilding/tidally_locked_world.md` states the mod remaps temperature
onto **latitude** — "low latitude is the burning dayside… the poles are the nightside".
**That is not what the world does.** Measured 2026-08-18 with `worldview.py` on both the
painted world and the untouched vanilla source it was built from:

```
                    corr(T, |lat|)   corr(T, angle from substellar)
WORLDMAP_ashkarr        +0.105              -0.979
WORLDMAP_sub7b_source   -0.097              -0.958
```

**Substellar point = latitude 0.0, longitude 0.0**, on both worlds, and temperature
falls with **angular distance from that point** — not with latitude. Latitude explains
essentially nothing (|r| ≈ 0.1).

⇒ **Every spec written in "normalised latitude" must be read as normalised ANGULAR
DISTANCE from (0°, 0°)**, where `θ = 0°` is the substellar point, **`θ = 90°` is the
terminator**, `θ = 180°` is the antistellar point. The sea band "normalised latitude
0.35–0.65" therefore means **θ between 63° and 117°**, which is exactly the terminator
band the same doc asks for — so the intent survives the correction, only the axis moves.

⚠️ This has not been reconciled with the mod's own `TidallyLocked` PlanetTypeDef, which
may still key on latitude at runtime. **Flagged for the owner; not silently resolved.**

---

## The binding constraints this map must satisfy

Pulled from `worldgen_sea_spec.md`, `tidally_locked_world.md`, `desert_world_design.md`,
`hydrology_and_fire_ecology.md`, `water_doctrine.md`. Numbers are theirs, not mine.

**Sea** — ~25% of tiles water, accept **22–28%**. **Exactly three** connected bodies, no
strays. Perimeter²/area **≥ 25** (a circle is 4π ≈ 12.6). Two centroids in the
terminator band, **one deliberately out near the antistellar point**, frozen. Elongated
and torn, ⛔ **never a ring**, ⛔ never smoothed. Hypersaline — the sea is food and mass,
not drink. Every water tile `elevation ≤ 0`; every land tile `elevation > 0`.

**Rivers** — few, **short**, and every one **born on a high peak**, because rain only
condenses at altitude. They run **dayside only**; ⛔ nothing feeds the nightside. Some
reach a sea, the rest die in evaporative sinks. Winding and branching at acute angles.

**Green** — a **narrow, fierce** ribbon on the water margin and nowhere else.
`AB_OcularForest` sits on or beside Mountainous terrain at the river heads and bleeds
the streams outward. Everything else is desert, and the deep desert kills by absence.

**Fire** — ONE clustered volcanic region (Pyroclastic Conflagration + Volcano + Lava
Fields + Tar Pits packed together). The rest of the planet is comparatively quiet.
⛔ Not one mountain spine — **many ranges, dotted with volcanoes**.

**Night** — terminator → poison forest → dark margin (`HorrorWastes`, `AB_PropaneLakes`)
→ deep night (`AB_RockyCrags`, common) → `Glowforest` as isolated points. ⛔ The
nightside must never become farmable. ⛔ No gelatinous-superorganism band — patches only.

**One-of-a-kind** — a single hand-seeded `AB_MechanoidIntrusion` cluster, the Shipyards.

---

## Status

Written 2026-08-18 as the standing brief for the repaint. The paint recipe itself is
`src/RimMandrake/Utils/ashkarr_paint.py` — a one-off script for THIS planet, not a
generator, and it is finished when the picture is right, not when a test passes.
