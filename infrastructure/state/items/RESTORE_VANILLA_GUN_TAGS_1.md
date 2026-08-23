## 🔴 CORRECTED 2026-08-21 ~17:35 — DO NOT RESTORE ANYTHING. THIS ITEM WAS FILED WRONG.

**The cause is Cherry Picker, and Cherry Picker is the owner's own curation.** The 26
weapons are not victims of a mystery mod — **they are on the kill list, deliberately.**
Correspondence checked defName-for-defName against the list the running game loaded
(`Config/Mod_3521312241_Mod_CherryPicker.xml.bak-20260821-mechuncut`):

    weapons measured stripped and present on the loaded kill list:  27 of 27
    weapons measured intact and absent from it:                     2 of 2
                                                (Gun_IncendiaryLauncher, Gun_ChargeRifle)

No exceptions in either direction. ⛔ **The original title — "restore the vanilla gun
tags" — describes undoing a decision the owner made on purpose.** Nobody is to act on it.

**How Cherry Picker does it:** it is C#/Harmony, not XML. There is no PatchOperation to
find — an exhaustive sweep of 1437 XML files mentioning `weaponTags` across 1254 workshop
mods found nothing targeting these defs. At load it walks its `keys` list and **neuters**
each named def instead of deleting it (deleting would break cross-references), and part of
neutering a weapon is **emptying its `weaponTags`** so no PawnKindDef, ThingSetMaker or
trader can roll it. The def survives with `weaponTags = []` — exactly the observed state in
both runtime and the dump.

🔑 **So a Cherry Picker cut is invisible to every XML-shaped search.** Anyone hunting a
def's missing field should read the kill list FIRST.

## what IS a defect, and it is a consequence rather than the cut
`skills/rimworld-content-moderation` names this exact trap: **cutting the last weapon
carrying a tag silently disarms every pawn kind whose tags ALL went to zero.** That is
what happened, and it is measured:

    Mercenary_Sniper   bare 5/5      Scavenger    bare 5/5      Town_Guard  bare 3/5
    vanilla combat kinds overall     13 of 40 = 32.5% unarmed

The whole-game audit puts a number on it: **29 of 711 tool-using kinds intend to arm and
cannot** — 12 whose tag pool is genuinely empty, 17 whose pool survives but now holds only
expensive weapons. The cut was intended; **disarmed raiders were probably not.**

⚠️ Correcting an earlier line in this file's evidence: `Mercenary_Sniper` is **not** bare
because its pool is empty. It holds a 760-silver DMR and the kind has 600 to spend. Every
cheap `Gun`-tagged weapon was cut, so the cheapest survivor wearing `Gun` is the incendiary
launcher at 340.

⇒ The work is **not** un-cutting weapons. It is one of:
1. **Retag the orphaned kinds** onto surviving weapons, so a vanilla kind draws a Star Wars
   gun instead of nothing.
2. **Cut the kinds too**, if no vanilla kind should be fielding pawns on Ash'karr at all.
3. **Accept it** — some factions arrive with melee-only or unarmed pawns.

That is a scope call. Filed as `ORPHANED_KINDS_AFTER_GUN_CUT_1` for DECIDE.

## ⚠️ live-config drift, worth knowing before the next load
The current kill list was edited **today at 16:22** and differs from the loaded one by
exactly two entries: **`Gun_Needle` and `Gun_Scattergun` were REMOVED** — BUILD's
`MECH_WEAPONS_UNCUT_1` repair. It is real and correct; it simply has not taken, because the
running game loaded the pre-edit list. **On the next cold load those two — and only those
two — come back tagged**, which should arm `Mech_Pikeman` and `Drone_Sentry`.
🔑 `Bow_Great` is still on the list, so `Tribal_Archer_Fire` will still spawn bare.

## the rebuilt criteria
Measured after the next cold load, not now:
- `Gun_Needle` and `Gun_Scattergun` read non-empty `weaponTags`
- `Mech_Pikeman` and `Drone_Sentry` spawn **5/5 armed**
- every other def on the kill list still reads `[]` — **that is the pass condition, not a
  failure**

Evidence: `infrastructure/state/observed/2026-08-21/armed_sweep_48/`.


---

## 🔴 CORRECTION — BUILD, 2026-08-23, against capture `2026-08-23T07-12-04Z`

**The offline half is MET; two of its statements are dead.**

✅ Measured: `Gun_Needle` = `['MechanoidGunLongRange']` MarketValue 1400; `Gun_Scattergun` =
`['SentryDroneGunShortRange']` MarketValue 1000 — both were `[]` / 0. Of 1,289 kill-listed
ThingDefs, 1,162 are present and all 1,162 correctly read `weaponTags: []`.

⛔ **STRUCK:** *"`Bow_Great` is still on the list, so `Tribal_Archer_Fire` will still spawn
bare."* It does not. That kind carries `NeolithicRangedBasic`, and `Flamebow` — uncut on the
owner's 2026-08-22 01:05 ruling — is the sole live carrier of `NeolithicRangedFlame`.

What remains is only the live 5-of-5 spawn confirmation, which no dump can give.
