## spec
✅ **OWNER'S RULING, 2026-08-22 11:00, to DECIDE: retag the orphaned vanilla kinds onto
surviving Star Wars weapons.** Verbatim option he chose: *"A vanilla mercenary draws a
surviving blaster instead of nothing. Keeps your cut, keeps the kinds."*

⛔ **The two rejected options are dead — do not revisit them.** He declined *"cut the kinds
too"* (thins who can show up) and *"leave them unarmed"* (a third of every vanilla-kind raid
arrives as a punching bag). **The kinds STAY and they get armed.**

## the work is already scoped kind-by-kind — 29 of 711
`jawa/pawnkind_audit`, no filter, 711 tool-using kinds. **29 intend to arm and cannot.**
(291 with no `weaponTags` and 9 with `weaponMoney.max 0` are civilians and children — not
these.) The ruling routes the two halves differently:

### A · the 12 with an EMPTY pool — retag; money cannot help them
`Mech_Pikeman` · `Drone_Sentry` · `Tribal_Archer_Fire` · `VEE_Hunter` · `VEE_TribalHunter` ·
`VFEP_Footsoldier` · `BS_Crossbowman` · `BS_CrossbowDvergr` · `BS_DvergrTraditionalist` ·
`DP_ArtilleryPirate` · `DP_RocketPirate` · `OuterRim_ImperialTrader`

⭐ Already covered: `MECH_WEAPONS_UNCUT_1` un-cut `Gun_Needle` and `Gun_Scattergun`, fixing
the **pikeman** and **sentry drone** on the next cold load. `VEE_HUNTERS_GET_WEAPONS_1`
covers the two `VEE_*`. `Bow_Great` is still cut, so **`Tribal_Archer_Fire` is NOT fixed** —
see `FIRE_ARCHER_SPEC_STILL_WRONG_1`.

### B · the 17 that CANNOT AFFORD — raise `weaponMoney.max`, and the audit says by how much
Not a retag at all; the pool survives and only expensive things are left in it. The audit
gives the exact figure per kind, e.g. `Mercenary_Sniper` +2 variants: tag `SniperRifle`,
budget 600, cheapest survivor `guy762_brifle_dmr` at 760 ⇒ **raise max to 760**.
`Town_Trader`/`Town_Councilman` +5 clones: tag `Gun`, budget 200, cheapest
`Gun_IncendiaryLauncher` 340 ⇒ **340**.

## 🔑 DECIDE's one scope constraint — check reachability BEFORE spending a patch
⚠️ **The audit does not know which factions generate.** `OnlyOurFactions.xml` zeroes
`startingCountAtWorldCreation` on **48** factions, and a kind fielded only by a zeroed
faction can never reach Ash'karr. A previous sweep narrowed 9 flagged kinds to **2 real**
this way.

⇒ **For each of the 29, confirm at least one faction that (a) generates on Ash'karr and
(b) fields it, before patching.** A kind that cannot arrive is not a defect and must not
cost a patch. **Report the ones you drop and why** — a silent skip reads as coverage.

⛔ **Do not raise a budget above the cheapest SURVIVING weapon in the pool.** The point is
that they arrive armed, not that they arrive rich.

## verify
Re-run `jawa/pawnkind_audit` with no filter: `emptyTagPool` and `cannotAfford` both **zero**
among kinds reachable on Ash'karr. Then spawn 5 each of `Mercenary_Sniper`, `Scavenger` and
`Town_Guard` — the three carrying all 13 of the measured 40 bare vanilla rolls — and confirm
none is bare.

## criteria
Zero reachable vanilla kinds bare-handed; the unreachable ones listed with their reason.

## watch out
⚠️ Baseline to beat: vanilla combat kinds ran **13 bare of 40 rolls = 32.5%**, all of it in
`Mercenary_Sniper` (5/5), `Scavenger` (5/5) and `Town_Guard` (3/5).
⚠️ This is NOT the authored-roster problem. Our 48 kinds are handled by
`BLACKSTAR_DEEPDESERT_POOLS_EMPTY_1` and `EMPIRE_BLACKSTAR_ALWAYS_WILLING_1`.
