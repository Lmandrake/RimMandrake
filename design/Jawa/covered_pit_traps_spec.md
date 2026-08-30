<!-- status: draft — BENCH proposal for owner ruling, 2026-08-30. Item: COVERED_PIT_TRAPS_1. Parent: trap_renaissance_spec.md §4b -->
# Covered Pits — the earth that swallows (first-class mod spec)

_Owner's seed, verbatim anchor: 1x1/1x2/2x2 covered pit traps that trigger on
MASS and hold by BODYSIZE/HEALTH, plus a gated pit for prisoner holding — dug
fast by Jawa or droids, the canon holding pen. Expanded here into a standalone-
quality mod. Working name candidates: **Covered Pits** · **The Swallowing
Earth** · **Pitcraft**._

## 1. The fantasy

A thrumbo vanishes mid-stride. The sand simply takes it, and somewhere below it
is alive and furious and YOURS. Pits are the one trap the desert itself
co-authors: no steel, no glow, no tell — a hole, a lie of woven scrap laid over
it, and patience. This is Ishko's purest instrument (the earth hides), the
prisoner pipeline's intake (the bloodless take), and the most Jawa building
imaginable: it is not even a building. It is an absence, dressed as the world.

## 2. The pit lifecycle

`DIG (staged) → OPEN PIT (hazard/holder) → + COVER (armed trap) → SPRUNG
(occupant below, cover broken) → manage occupant → RE-COVER or REFILL`

- **Dug, not built.** A dig designation (construction/mining hybrid job); Jawa
  dig FAST (species work bonus), **droids dig** (ties the droid-labor layer).
  Ground only — never on ship substructure: pits are the LANDED clan's craft,
  and the sacred hull has no holes. (Ishko's ground game; the ship is Ta'Baa's.)
- **Depth tiers by staged digging** (each stage = more work, spoil hauled out):
  - **Shallow** (1 stage): holds bodysize ≤1 (human-and-down).
  - **Deep** (2 stages): holds bodysize ≤2.5.
  - **Chasm** (3 stages, needs shoring materials): holds megafauna.
- **Terrain digs differently, and this is the loop's soul:** soft sand digs
  fastest but **unshored pits silt back up over time** (sandstorms refill open
  pits — maintenance/ambience in one rule); packed earth/clay digs slower,
  stays; rock takes mining proper and never silts. The desert is the best and
  worst pit country at once.

## 3. Covers & camouflage — the cover IS the local terrain (owner's idea)

The cover's graphic is **sampled from the terrain it is placed on** — a custom
Graphic class reads the cell's TerrainDef texture and renders the cover as a
patch of that ground (slight seam/discoloration at high zoom for the player's
own eye; the F9 signature of the building). Lay it on sand, it is sand; on
rough stone, it is rough stone. Mechanization options:

- **Option A — pure visual — ✅ RULED v1 (owner, 2026-08-30)**: camouflage is
  cosmetic + flat enemy-avoidance rules. Cheap, robust, always looks right.
- **Option B — camo-quality stat**: v2 candidate only (match% vs surrounding
  cells drives detection). Not in v1.
- Either way: **Jawa trap-sense sees all pits** (their own always; enemy pits
  per trap_renaissance_spec §2 Option C, RULED), allies/visitors do NOT — the
  §6 comedy/Zizzik feed applies.

**Cover tiers set the TRIGGER (mass rating)** — the player's targeting knob:
- **Woven scrap** (rating ~40kg): everything humansized-and-up falls; wildlife
  hunting and raider work.
- **Plank & lattice** (~120kg): humans walk over… heavies, mechs, big game
  fall. Let the raiders escort their centipede onto it.
- **Reinforced frame** (~220kg, revised 2026-08-30 — 400kg measured unreachable
  by any single vanilla creature, 240kg ceiling): only the monsters and
  vehicles go through.
Below rating: walks across safely. At/above: the floor lies. **Load sums** — a
tight raider knot can overload a plank cover together; a spread line crosses.
(Squad-breaking emergent play: they learn to spread, you learn to funnel.)

## 4. Hold & escape — bodysize/health as struggle, not stat-check

Fall deals mass-scaled blunt damage + a **Pinned-in-Pit** state. Escape is a
**struggle clock**, not a coin flip: each interval the occupant attempts a
climb; odds scale with (bodysize − pit depth tier), health %, and manipulation;
each failed attempt costs a little health/stamina (thrashing). So: a healthy
thrumbo in a shallow pit is out in seconds and ANGRY; a wounded raider in a
deep pit is yours; anything in a chasm stays until hauled. The escape window is
the drama — dart it, net it, talk to it, or watch it climb out while your
pawns scatter. Occupants below can still shoot upward at pawns on the rim
(grenades out of a pit end poorly for everyone — `▲Zizzik`).

## 5. The variants (one framework, five faces)

_Floor fittings ✅ RULED expanded (owner, 2026-08-30): "Spikes, flammable oil,
poison, water (can't climb out at all perhaps if deep)."_

| Variant | Floor/fitting | What it is |
|---|---|---|
| **Bare pit** | nothing | capture; the bloodless take — `↑Mob'Unloo` `↑Ishko`, no Sh'kaar feed |
| **Spiked pit** | scrap spikes | lethal fall; cheap kill-zone — feeds `▲Sh'kaar` (blood in the earth), `↓Oomo` faint |
| **Oiled pit** | flammable oil pooled below | occupants soaked on impact; **ignitable at will or by tripwire** — a lit oil pit is Sh'kaar's altar (`▲Sh'kaar` large); doubles as a firebreak-fed area-denial horror |
| **Poison pit** | toxin-slicked floor (CGT gas / toxin liquor) | slow capture-then-fade: occupant weakens over time instead of dying on impact — the patient hunter's kill or the softening pre-capture; `▲Zizzik` faint (the creeping wrongness) |
| **Deep water pit** | flooded chasm | **no climbing out at all** — swimming things tread until exhausted; air-breathers drown if left. The drowning cell and the perfect indefinite hold in one. Oomo's domain both ways: holding in his waters is his patient jail, *drowning* a captive is life spilled through waters — `↓Oomo` + `▲Zizzik` on a death, neutral on a hold. |
| **The oubliette** | ion mine / EMP charge at the bottom | mechs & droids drop in and switch OFF — **disable-and-take chamber**: Ozzik's favorite room, feeds the salvage loop |
| **Baited pit** | bait slot on the cover (HAZN loop pattern) | draws predators/game to the lie — passive hunting; `↑Ishko` `↑Oomo` (game provides) |
| **Pit cell** | gate cover + ladder | the prisoner pit, §6 |

## 6. The pit cell — the gated prisoner pit (the canon holding pen)

A scavenger clan digs a hole; it does not build locked barracks on the sacred
ship. The old "prisoner pit" mod's failure was fighting RimWorld's room/bed
prisoner logic. **We don't fight it — we use the Anomaly holding-platform
pattern**: the pit cell is a *holding building* (CompHoldingPlatformTarget
family precedent — modern, shipped, save-stable), not a room. Prisoners are
ASSIGNED to the pit, held by the same struggle rules (§4), fed through the
gate (a feeding job at the rim), visible below on the open-gate graphic.
- ✅ **RULED severity (owner, 2026-08-30): the COVER is the mercy.** Gated/
  covered pit cell = grim-but-usable — real mood/weather penalties, real Oomo
  stakes, but a fed and tended pit is a legitimate long-term hold (the
  hole-then-hearth conversion story works). **Uncovered = actively harsh: the
  unsetting sun beats straight down into the hole — gruesome by design.** A
  captive left open to the sky degrades fast (heatstroke, burn, despair), and
  **an occupied pit left open to the sun FEEDS `▲Sh'kaar`** — the Searer
  gorging on the one who cannot hide. Closing the gate is thus both cruelty's
  limit and Ishko's small kindness (the captive, too, is hidden).
- Gate open = interaction (feed, recruit-talk from the rim, hoist out);
  Oomo watches how you keep them (**tending/feeding pit captives = his
  nursing credit; letting one waste away in the hole = his wrath and
  Zizzik's snack**).
- Recruit from the pit at a penalty (who loves the hole?) — but emancipation
  OUT of the pit into the clan is exactly the §8b emancipation rite, and the
  contrast (the hole, then the hearth) is the conversion story itself.
- Capacity by footprint: 1x2 holds one; 2x2 holds two (or one big).

## 7. Weather, terrain, ambience

Open pits silt up in sandstorms (sand country); collect water in rain (a
slighted Oomo's standing water — disease risk in an occupied pit); a cover
buried by a storm becomes MORE hidden (the desert re-arms your lies). Fog and
night mute the seam tell. The world keeps co-authoring the trap after you dig
it — that's the "first-class" feel: the mod converses with weather, terrain,
and time instead of sitting inert like a spike board.

## 8. Theology wiring (rows for §8b/matrix on ruling)

- Pit capture (bloodless) → `↑Mob'Unloo` (value taken whole), `↑Ishko` (the
  earth hid your hand), `↑Oomo` when kept fed.
- Spiked kill → `▲Sh'kaar` small, `↑Ta'Baa` nil (a pit is not a door).
- Own pawn/animal falls in own pit → `▲Zizzik` (delicious), colony mood
  comedy thought.
- Oubliette droid-take → `↑Ozzik` (large) `↑Ohm` (a hand recovered intact).
- A captive dies forgotten in the pit → `↓Oomo` (large), `▲Zizzik`,
  `↓Mob'Unloo` (an asset wasted).
- Digging itself → honest Rekko-neutral labor; droid-dug pits please Ohm
  (his hands shaping the earth).

## 9. Layering & compatibility (first-class means standalone)

✅ **RULED naming (owner, 2026-08-30): the RimMandrake moniker, never "Jawa",
on everything that ships** — mod name, packageId, defName prefixes
(`RimMandrake_Pits` / `RM_*`). "Jawa" stays inside lore text and campaign
docs only.

- **Core mod: `RimMandrake Pits`** — species-agnostic framework, no campaign
  references: dig stages, covers, mass trigger, struggle escape, holding
  cell, terrain-sampled graphics. Works on any colony, any modded creature
  (bodysize and mass are universal stats — modded megafauna Just Works).
- **Campaign layer (RimMandrake, patches on top)**: species dig-speed bonus,
  trap-sense integration, theology rows, droid dig jobs, oubliette recipe,
  art pass.
- **Stretch, flagged not promised:** Vehicle Framework masses triggering
  covers (a speeder nose-down in a chasm is too good to not want) — gated on
  VEHICLE_ION_TIER_1 learnings; insect/infestation interactions.
- Settings: trigger-mass tuning, escape difficulty, silt-up on/off.

## 10. C# skeleton & in-stack precedents

`Building_PitCover` (trigger; Building_Trap subclass, mass-sum check) ·
`Building_OpenPit` (holder; struggle ticker, occupant render at depth offset) ·
terrain-sampled `Graphic_TerrainMimic` (reads cell TerrainDef at spawn;
re-samples if terrain changes) · pit cell via the Anomaly holding-platform
pattern · precedents already in the stack: `QE_CaptureNet`
(CustomTrap_Capture), Odyssey `Building_TrapRelease*`, HAZN bait/refuel loop.
Build route per rimbridge-companion/modding skills when the owner calls it;
quicktest plan: spawn-mass matrix (squirrel/human/thrumbo/centipede ×
cover tiers) on the 22-second minimal list.

## 11. Rulings ledger (owner cards, 2026-08-30) — all four answered

1. Camouflage → **pure visual v1** (§3); camo-quality is a v2 candidate.
2. Lethality → **full fitting family in v1**: spikes, flammable oil, poison,
   deep water (§5).
3. Pit cell severity → **the cover is the mercy**: covered grim-but-usable,
   uncovered actively harsh under the unsetting sun, `▲Sh'kaar` fed by an
   open occupied pit (§6).
4. Structure → core + campaign layer, **RimMandrake moniker on everything
   that ships** (§9).

Remaining open: none blocking. Build files when the owner calls it; the
spawn-mass quicktest matrix (§10) is the first build step.
