
## spec
🔴 **This is a SCOPE question and it is DECIDE's, which is why it is filed rather than built.**

`EMPIRE_BLACKSTAR_ALWAYS_WILLING_1` carries an explicit DECIDE ruling of 2026-08-22:

> ⛔ **Do not apply this to the other ten factions.** DECIDE ruled their pacifist rolls are
> wanted texture; narrowing them is a regression, not a bonus.

The live harvest of 2026-08-24 (`facts/roll_arm_harvest_2026-08-24.md` §2, 285 pawns) measured
something that ruling could not have known:

| cohort | distinct backstories | of which disable `Violent` |
|---|---|---|
| bare (21 pawns) | 32 | **10** |
| armed (264 pawns) | 256 | **0** |

**Zero overlap.** A violence-disabling backstory is *sufficient* to produce a bare pawn — not one
of 264 armed pawns carried one. And the 13 pacifist rolls landed on **Droid ×3, Wildsteam ×2,
Geonosian ×2, TradeMoot ×2, Homestead, Hutt, Gamorrean and Empire ×1**. Blackstar rolled none.

⇒ The guard (`requiredWorkTags Violent`, shipped at `92679d9b` on eight kinds) is on the two
factions that turned out **least** affected, and off the eight that were.

## The question only DECIDE can answer
**Is a bare-handed pawn the price of the "wanted texture", or was the texture ruled in before
anyone knew it cost the pawn its weapon?** Those are different rulings and the 2026-08-22 one was
made without the second half.

⛔ **BUILD did not widen the guard**, because widening it is exactly what that ruling forbids, and
"the measurement suggests it" is not a reversal. The mechanism is trivial either way —
`requiredWorkTags: Violent` on whichever combat kinds are named — so this item costs one line to
implement once the scope is settled.

## Watch out
⚠️ **A pacifist backstory is SUFFICIENT but NOT NECESSARY.** The other **8 of 21** bare pawns can
do violence and rolled bare anyway. ⇒ Whatever is ruled here, it closes at most 13/21 of the bare
problem and **must not be reported as closing the bare-hands defect**.
⚠️ Violence-disabling **traits** were never measured — the dump reports 0 `TraitDef`s with `Violent`
in `degreeDatas`, which is a dump blind spot rather than a proven zero.
🔑 The remaining 8 are NOT the weaponMoney band: `weapon_affordability.py`, corrected 2026-08-27 to
read the emitted XML instead of the generator's stale shadow table, reports **always arms 49 ·
sometimes 0 · never 0 · unmeasured 0**. The band is not the cause; the leading remaining candidate
is that the tool's prices are unstuffed `MarketValue` while the engine compares
`ThingStuffPair.Price`, and 11 kinds pass on under 25% headroom.

---

## ⭐ STRENGTHENED 2026-08-27 by live measurement — this guard is now the LARGER half of the fix

150 spawns, seat BUILD. Evidence: `infrastructure/state/evidence/bridge_session_2026-08-27_BUILD.md`.

Of 70 pawns spawned across 7 roster kinds, **5 arrived bare and all 5 carry a
violence-disabling backstory — zero unexplained.** The pacifist set is the 59 `BackstoryDef`s
carrying `Violent` in `workDisables`, measured from the capture.

⇒ The item this was split from assumed the backstory guard closed *at most* 13 of 21 bare
pawns, with 8 left to a `weaponMoney` defect. **That defect does not exist** — the other cause
is `SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1`. ⇒ **Ruling on which factions the guard covers now
decides most of the bare-hands problem, not part of it.**

⛔ **Still not BUILD's to widen.** The 2026-08-22 ruling stands until DECIDE moves it; this
note raises the stakes of the question, it does not answer it.
