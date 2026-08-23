# Gear audit, pass 2 — BUILD, 2026-08-23

Owner's tiers: Empire and Helix VERY wealthy · Hutts and Deepwater intermediate · Jawa and
Junkers only rich enough for their characteristic gear · heavy Junkers required in warcaskets.

## ✅ APPLIED

**Empire — apparel budgets were the THINNEST of any faction, for the richest power.**
Grunt 500~600 → 900~1100 · Heavy 700~840 → 1100~1300 · Specialist 700~840 → 1000~1200 ·
Leader 1200~1440 → 2000~2400.

**Helix — the Grunt was poorer than an Empire grunt and the ladder was a cliff.**
Grunt 600~720 → 1400~1700 · Heavy 1100~1320 → 2000~2400 · Specialist 1400~1680 → 2600~3100.

**Junkers — could afford 25 to 44 apparel options. That is a wardrobe, not a characteristic.**
Grunt 400~480 → 250~300 · Heavy 700~840 → 600~720 · Specialist 900~1080 → 700~850 ·
Leader 1400~1680 → 1000~1200.

**🔴 Junkers Heavy required the warcasket HELMET ONLY — a cased head over ordinary clothes.**
Added `VFEP_Warcasket_Warcasket` (body, 341) and `VFEP_WarcasketShoulders_Warcasket` (81).
Junkers Leader had NO required apparel at all and is now cased too. Base Warcasket tier
deliberately, not a veteran suit: Junkers are not rich, they are merely armoured, and that
is the whole character of the faction.

## 🔴 THE MISTAKE I MADE, AND THE RULE THAT COMES OUT OF IT

I cut four budgets that "looked absurd" and **created four bare-handed kinds** — the exact
defect I had spent the night fixing elsewhere. All four were reverted:

    Jawa_DeepDesert_Specialist  cut 2000~2400 -> 400~500    SaV_tusken holds 2 weapons,
                                                            both the Tusken slugrifle at 1977
    Jawa_Wildsteam_Grunt        cut 1300~1560 -> 500~600    KotORBowcaster's cheapest is 1250
    Jawa_Helix_Leader           cut 12500~15000 -> 4000     KotORRanged_legendary starts at 12000
    Jawa_Hutt_Leader            cut 13000~15600 -> 3000     same tier, same floor

🔑 **A weaponMoney that looks absurd is usually LOAD-BEARING.** It has been sized to the
faction's SIGNATURE weapon, and cutting it toward a tidy-looking tier strands the kind below
its own gear. **Read the pool's price floor before touching any budget** — the number is a
consequence of the tag, not a free parameter.

⚠️ The Hutt case is the subtle one: the FACTION is intermediate — its Grunts run 200~240 —
but a crime boss carrying one ostentatious 12,000-credit blaster is the character, not a
contradiction. Tier the ROSTER, not every row of it.

## ⚠️ MY LADDER CHECK WAS WRONG, and the data was right
Empire, Droid and Wildsteam read "not ascending" because the **Specialist** sits below the
Heavy. That is correct: a Specialist is a SUPPORT role, not a rung — an Imperial officer
carries a sidearm, and should. A roster is role-shaped, not linear. The check was rewritten
to stop reporting it.

## FINAL STATE
**0 kinds have priced options they cannot afford**, weapons or apparel, across all 52.
validate_patch.py 0 errors. Deployed, VERIFIED in sync.

## still open, and named rather than assumed
- `forceWeaponQuality` clamps are specified per faction in the design and remain unbuilt —
  they would make a Helix agent's gear visibly better than a Junker's, which budget alone
  does not do.
- `apparelColor` per faction: unbuilt.
- 226 of 758 weapons and many apparel items are runtime-priced; the estimator reproduces
  RimWorld's own costList method but is an ESTIMATE, and quality multipliers sit on top of it.
