# FEVERWOOD_TENTACLE_BESTIARY_1 — six limb types and the drive-off ladder

## spec

Authority: `design/Jawa/worldbuilding/biomes/fever_wood_deep_and_mud_2026-09-23.md`
§1, §2, §2a, §2b. 🔴 **Read §0 first** — this item exists because the owner's rulings of
2026-09-23 **superseded hard ban 1** of the frozen sheet. The thing below is now **ambient
and named**.

🔑 **The animal is never rendered.** It never enters the screen. Only **tentacles** are
ever drawn, and they behave as separate pseudo-species — *"different sizes and maybe types
of tentacles (act like different species, but they are all connected to the same great
elder being)"* (owner, verbatim).

Tier: **ours in the `RM_` tier, mapped to the dianoga when the campaign layer is active**
(owner, verbatim: *"we should just make up our own tentacled eldritch horror down there and
map it to the Dianoga when Utinni is active."*). Canon target for the campaign mapping:
`design/RimStarWars/canon_references/dianoga/description.md`, expanded 2026-09-23.

## the six limbs

feeler (thin, searches after noise) · snare (grabs and drags) · lash (barbed, ranged) ·
**porter** (🔴 *"more slender and delicate than the others"* — owner) · sentinel
(motionless; chorus silent while it is up) · bloom (vast, exposes the eye).

⚠️ Only the **porter**'s appearance is owner-ruled. The other five are BENCH's proposal.

## the drive-off ladder — owner ruled, verbatim in the spec §2b

| encounter | result |
|---|---|
| damage 1–2 emerged limbs | retreat, **reset within hours** |
| **severe** damage before withdrawal | limb **SEVERED** → ⭐ harvestable tentacle body + **one day** respite |
| rare set-piece: large pool, many limbs, **the eye** | attacking the eye is the goal |
| eye, moderate damage | all limbs driven off map-wide for **a day** |
| eye, severe damage before retreat | 🔴 **killed PERMANENTLY on this map** |
| foul water with poisons / radioactive material | **suppressed several days** as it diffuses |

## two consequences worth building deliberately

1. ⭐ **A severed tentacle is the only renewable source of the animal's body**, which is how
   the canon dianoga food line exists without killing it — pie from the meat, tea brewed
   from **spleen chemicals**, cream. Trade good and hazard are one creature.
2. **"Permanently on the map" is per-map, not per-world** — a colony can genuinely win its
   pools back while the species survives on the planet.

## reuse — do not rebuild

✅ `FEVER_WOOD_MECHANICS_1` F1 already built the **downed-pawn rescue countdown**
(`DamageUntilDowned` + a countdown cleared by `CarriedBy != null`). The snare's drag and the
**sink-mud** both ride that same mechanism.
✅ F1's `RUT_MapComponent_TheTenant` already scans the terrain grid for pool cells, and
`RUT_GenStep_ScatterPools` (order 226) already paints them.
⛔ F4's `RUT_TenantEmergenceSpawner` was built *referenced by nothing* to satisfy ban 1.
That rationale is **void** (§0) — but the **full emergence** is still plot-reserved. Ambient
play gets limbs; the whole animal rising is still the plot's to spend.

## 🔴 open, and rulings-shaped — do NOT guess

- **How often the rare set-piece arrives.** The single most important tuning number here:
  too rare and the permanent kill is unreachable, so players never learn the eye is the
  answer. Unset.
- **Which poisons and radioactive materials qualify.** The ruling names the category only.
  The seep-oils are the obvious local candidate and were **not** named by the owner.
- **Why anything lives down there at all.** The mechanism that would have answered it (a
  sap-sucker dropping into the pool) was offered and **declined** — ⛔ do not revive it.

## Watch out

- The **porter** must be recognisable *before* a player shoots it, because attacking it
  angers the pool **and** ends its treasure trickle permanently. That makes its distinct
  silhouette an art requirement, not flavour.
- ⚠️ **UNMEASURED, Desktop only:** whether a hediff zeroing Moving pins a pawn mid-path
  without corrupting its job queue. RimSage has never connected on the Mac — do not assert
  it from there.
