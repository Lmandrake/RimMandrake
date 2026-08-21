🔴 **CLOSED BY THE OWNER, 2026-08-21, before it was worked. His words:**
> *"Let's just assume there will be no conflict. The user will know during gameplay if
> they're getting unresolvable massive negative moods. No further testing for Nomad issues
> at this time please."*

⇒ **`VME_Nomad` STAYS — on the Jawa tribes AND on the player ideo.** No Harmony patch, no
in-game verification, no further measurement. Options 1, 2 and 3 below are all dead; the
owner took option 1 and ruled the question shut.

⛔ **DO NOT REOPEN THIS ON THE EVIDENCE BELOW.** The −50 finding is real, confirmed against
Ludeon's own source, and **the owner has seen it and ruled anyway.** That is his call to
make and it is made. The measurements are kept here as the record of what he was told, not
as an argument still waiting for someone to act on it. If it bites in play, he will say so —
that is the mechanism he chose.

---

## spec
🔴 **OWNER, 2026-08-21: "But I like VME_Nomad!"** ✅ **Kept on the Jawa tribes — free, done**
(`NOMAD_MEME_RESTORED_TRIBES_1`; the harsh precept carries `enabledForNPCFactions: false`).
**This item is only about your own colony's ideo**, the one place it can actually fire.

### The mechanism, read out of the IL and verified against RimWorld source

`ThoughtWorker_Precept_PermanentBases.ShouldHaveThought` reads exactly **one** value:
`WorldComponent_TravellingAndTradingTracker.Instance.ticksWithoutAbandoning`. Not a
settlement founding tick, not `Map.generationTick`. It is a persistent world counter that:

- **+6000 every 6000 ticks** while you hold ≥1 map that is `IsPlayerHome && Parent is Settlement`
- **−6000 every 6000 ticks** while you hold none
- **zeroes ONLY** in `SetAbandonedTimeToZero`, a Harmony postfix on
  `RimWorld.Planet.SettlementAbandonUtility.Abandon`

Stages: nothing below 15 d · **−1** at 16 · **−3** at 20 · **−5** at 30 · **−20** at 40 ·
**−30** at 50 · **−40** at 60 · **−50** beyond.

### 🔴 A gravship launch does NOT reset it. Confirmed from Ludeon's own source.

```
RimWorld/GravshipUtility.cs:453        map.Parent.Abandon(wasGravshipLaunch: true)
RimWorld/Planet/SettlementAbandonUtility.cs:96-100
    private static void Abandon(MapParent settlement) { settlement.Abandon(wasGravshipLaunch: false); … }
```

VME patched the **private static wrapper**, which is reached only from `AbandonCommand` —
the player-clicked gizmo. The gravship calls the **virtual `MapParent.Abandon`** directly and
bypasses it. ⇒ **the postfix never fires on a launch.** Landing calls
`GravshipUtility.SettleTile` → `SettleUtility.AddNewHome`, so the new parent is a `Settlement`
and the counter resumes climbing at once. **A hop subtracts only the flight duration.**

⛔ **And the gizmo is not a usable workaround.** `TryAbandonWithColonyCheck` has no
last-colony guard, but abandoning a map your pawns are standing on runs
`PawnDiedOrDownedThoughtsUtility` with `Banished` and `Notify_LeftBehind` — you lose them.
Resetting would mean keeping a *second* settlement solely to abandon it.
⇒ **For a single-colony gravship campaign there is no practical reset. It climbs to −50 and
stays there.** That is the number, and it is the thing that was never verified until now.

### 🔑 The choice, and the third option is the one worth having

| | what you get |
|---|---|
| **(1) Keep it anyway** | −50 mood permanently, on top of everything else this clan is carrying. Survivable with enough buffers; arguably in character. Nothing to build |
| **(2) Tribes only** | Already done and free. Your own ideo drops the meme and keeps `Nomadic_Preferred`, whose reset IS proven — `GravshipUtility::ArriveNewMap` unconditionally stamps `lastResettledTick`, the only field its worker reads — plus **+0.3 caravan speed**. You lose the Nomadism symbol pack on YOUR faith; the tribes still carry it |
| ⭐ **(3) Patch it — ~6 lines** | A Harmony postfix on `MapParent.Abandon` that zeroes `ticksWithoutAbandoning` when `wasGravshipLaunch == true`. **This makes the meme do exactly what you thought it did: a gravship hop counts as moving.** You keep the meme, the symbol pack and the flavour, and the penalty becomes a real mechanic instead of a slow bleed |

**Option 3 is cheap and low-risk.** We already ship four mods with assemblies and a working
toolchain (`Inhabited`, `JawaIonWeapons`, `JawaPlantGrowth`, `DesertVehicleReskin`). The
target field is public on a public WorldComponent with a public static `Instance`. ⚠️ It needs
the game DOWN to deploy, so it batches into a shutdown window.
⚠️ Also worth knowing: VME ships a real bug here — `secondPeriod` is 720000 (12 d) where it
should be 1020000 (17 d), so its `< secondPeriod` test can never pass and the **−2 stage is
dead**, with −3 covering 16–20 days. Harmless, but it means the def's own table lies slightly.

## verify
Owner picks 1, 2 or 3. Whatever he picks, `The Salvation.rid` ends up **identical** in
`src/Jawa/ideoligion/` and in the game's `Ideos/` folder — they disagree today
(`DEPLOY_SALVATION_RID_1`), and an Ideo is fixed at world creation, so it must be settled
before the next remake.

## criteria
Option 3 only, and CHECK owes it: launch a gravship, land, and confirm no
`VME_PermanentBases_Despised` thought is present on any colonist afterwards.
