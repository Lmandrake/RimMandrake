# JAWA_HOOD_NEVER_WORN_1 — the hood is in the apparel list and never on the pawn

Observed live, 2026-08-26, seat CHECK, full 582-mod list, during C40.

**16 of 16** `Jawa_Tribal_Scavenger` spawned in `Jawa_IndigenousTribes` wear
`guy762_Robes_jawa`. **0 of 16** wear `guy762_JawaHood`. The only other apparel any of
them carries is `Apparel_WarVeil`.

⇒ The robe half of the starting-gear patch (`5bb9f5c`, B58 — the dead Jawa pawnkind) is
landing and the hood half is not. C40 passed on the robe, which is what its criteria named;
this is the remainder.

**Where to look, in order.** `guy762_JawaHood` is from KotOR Weapons, which IS active — so
the def exists and this is not the `OuterRim_Jawa` class of defect. Candidates: the hood is
not in `apparelRequired`/`apparelTags` at all; it is in `apparelTags` but loses the roll to
`Apparel_WarVeil` on the same body-part group (both are head/overhead); or a `apparelMoney`
ceiling excludes it. `jawa/pawnkind_audit` only audits WEAPONS, so it cannot see this.

**How to prove the fix:** spawn 8 and read `jawa/pawn_get` apparel back. Presence of the def
in a dump proves nothing — the pawn wearing it is the only evidence.

Evidence: `infrastructure/state/evidence/C40_jawa_fixes_2026-08-26_CHECK.md`
