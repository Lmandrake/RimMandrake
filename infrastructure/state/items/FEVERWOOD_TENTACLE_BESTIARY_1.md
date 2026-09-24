# FEVERWOOD_TENTACLE_BESTIARY_1 — six limb types and the drive-off ladder

## ✅ Desktop answer — MEASURED from the decompiled engine (RimSage), 2026-09-23

**Q: does a hediff zeroing `Moving` pin a pawn mid-path without corrupting its job queue? NO — it DOWNS the pawn and clears its mind.**

- `Pawn_HealthTracker.ShouldBeDowned()` (Verse/Pawn_HealthTracker.cs:614-621) returns true the moment
  `!capacities.CapableOf(PawnCapacityDefOf.Moving)` (unless `RaceProps.doesntMove`). So Moving = 0 ⇒ downed.
- `MakeDowned` (:809-881) then calls `pawn.ClearMind_NewTemp(...)` (job + queue gone), `DropAndForbidEverything`,
  `stances.CancelBusyStanceSoft()`, undrafts, fires downed thoughts/tales and `Notify_PawnLost` on the lord.
  ⇒ It is the vanilla "incapacitated" path, not a snare. Nothing survives it.
- A hediff that only *slows* Moving does not pin either: `Pawn.TicksPerMove` (Verse/Pawn.cs:3221-3260) clamps at
  **450 ticks per cell** even at MoveSpeed 0 (`num3 = Mathf.Clamp(num3, 1f, 450f)`), i.e. 7.5 s a cell, still moving.

**What DOES pin a pawn in place with its job and path intact — two vanilla mechanisms, both engine-native:**

1. **Stun.** `pawn.stances.stunner.StunFor(int ticks, Thing instigator, bool addBattleLog = true, bool showMote = true,
   bool disableRotation = false)` (RimWorld/StunHandler.cs:176-185). `Pawn_StanceTracker.FullBodyBusy` is true
   while `stunner.Stunned` (Verse/Pawn_StanceTracker.cs:28-37), and `Pawn_PathFollower.PatherTick` returns early on
   `FullBodyBusy` (Verse/AI/Pawn_PathFollower.cs:217-365) with `curPath`, `destination` and `moving` untouched. `Pawn.Tick`
   still calls `jobs.JobTrackerTick()` (Verse/Pawn.cs:2796-2874), and no file under `Source/Verse/AI/` tests
   `stunner.Stunned` — so the job and its queue persist; only the body stops. Re-issue `StunFor` each interval to hold.
2. **A busy stance.** Any `Stance` whose `StanceBusy` is true (the `Stance_Cooldown`/`Stance_Warmup` family) has the same
   effect through the same `FullBodyBusy` gate, without the stun mote or battle-log line.

⇒ **Build the sink-mud, the snare's drag and F1's rescue window on `StunFor` (or a custom busy stance), not on a
Moving-zeroing hediff.** The "held by something" state is a hediff for *display and severity* only; the hold itself is
the stun. The one thing to test live, not from source: whether a stunned pawn being *carried* (the drag) keeps its job
— `MakeDowned` is the only path that clears it, and carrying does not down, so the expectation is YES.

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

🔑 **The species is NAMED: `RM_Sekkulaath`** — owner, 2026-09-23. The thing below is an adult
Sekkulaath; the juvenile is what the prison tank holds. ⛔ Do not invent another name for it, and
⛔ do not treat the tank's occupant as a different creature — §6m stage 3 (an escapee maturing
*"into the real thing"*) requires them to be one species. Ruling and its consequences:
`FEVERWOOD_DIANOGA_PRISON_1` → *tier — and the free-tier occupant is the SEKKULAATH*.

⚠️ **The built code's working name is "the Tenant", and two of its types carry the CAMPAIGN tier
prefix for what is franchise-free content** — `RUT_MapComponent_TheTenant` and
`RUT_TenantEmergenceSpawner` (F1/F4, shipped) against `RM_TenantTruceExtension`. Flagged, not
fixed; it is that item's `open`.

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
- ✅ **MEASURED 2026-09-23 (see the Desktop answer section): a hediff zeroing Moving DOWNS the pawn and clears its mind — use `StunFor` instead.** Original question: whether a hediff zeroing Moving pins a pawn mid-path
  without corrupting its job queue. RimSage has never connected on the Mac — do not assert
  it from there.
