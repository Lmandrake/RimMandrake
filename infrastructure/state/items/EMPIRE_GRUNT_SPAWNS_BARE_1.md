## spec

**`Jawa_Empire_Grunt` is the only kind still fielding a bare-handed pawn.** Measured
live 2026-08-23 02:4x on the full 578 list, ten spawns of each of the seven kinds
`BARE_HANDS_REMEASURE_AFTER_LOAD_1` names worst:

| kind | bare / spawned |
|---|---|
| **`Jawa_Empire_Grunt`** | **2 / 10** |
| `Jawa_Blackstar_Grunt` | 0 / 10 |
| `Jawa_Deepwater_Heavy` | 0 / 10 |
| `Jawa_Droid_Specialist` | 0 / 10 |
| `Jawa_Hutt_Leader` | 0 / 10 |
| `Jawa_Junkers_Grunt` | 0 / 10 |
| `Jawa_TradeMoot_Grunt` | 0 / 10 |

**70 spawns, 2 bare.** Six of seven kinds are clean, so whatever is left is specific to
this kind rather than general to the roster.

⭐ **The eight that ARE armed draw sensibly** — `OuterRim_DE10Blaster` ×4,
`OuterRim_EC17Blaster` ×2, `OuterRim_SE14RBlaster` ×1 — so the kind's weapon tags reach
a real pool and it is not falling back to one item. Whatever fails, fails intermittently.

⛔ **Do NOT reach for `weaponMoney.min`.** `BARE_HANDS_REMEASURE_AFTER_LOAD_1` refuted
that diagnosis offline — this kind's `min` already sits **above** its cheapest eligible
weapon (650 against 573.0), so a low roll cannot be the cause and raising the floor
changes nothing. That is the trap this item exists to keep closed.

## What has NOT been done

⚠️ **The cause is unknown and I did not guess at it.** Candidates worth separating
before anyone edits a def: an `apparelRequired`-style channel being bypassed by the same
thing `JAWA_ROBES_NEVER_WORN_1` describes; a `MayRequire`d weapon that resolves for some
rolls and not others; or a tag whose surviving pool is smaller than it looks after the
Cherry Picker neutering — the post-cut census in `WEAPON_FLOOR_BOWS_KNIVES_1` shows the
vanilla industrial tags at or near zero survivors.

⚠️ **Sample size.** 2/10 bounds the rate loosely. Re-run with 40+ before treating the
proportion as meaningful; what is established is that it happens, not how often.

## verify

- 40 `Jawa_Empire_Grunt` spawned through `jawa/spawn_pawn`, read with `jawa/pawn_get`:
  **zero** carry an empty `equipment` list.
- The other six kinds stay at zero on the same run.

## criteria

An Empire grunt arrives with a weapon every time, and the reason the two did not is
written down rather than fixed by moving a number until the symptom stops.


---

## 🔴 CORRECTION — BUILD, 2026-08-23. Cause identified, fix deployed, and the evidence here CONFIRMS it.

**This item measured the PRE-FIX defs.** The game loaded at 00:12; the fix landed at 02:08
(`992e1038`), and RimWorld parses defs only at startup.

### what the RUNNING game held during this test

    Jawa_Empire_Grunt   weaponTags  ['ORImperialStandard', 'ORImperialLight']
                        weaponMoney 650~780

### and here is why that produces exactly what was observed

Every rifle in `ORImperialStandard` costs **906** — E-11, DLT-20A and E-22 alike — against a
**780** ceiling. The rifles were unreachable by construction, so the roll fell through to
`ORImperialLight`, which is **entirely sidearms**.

⭐ **This item's own evidence is the proof.** The eight armed pawns drew
`OuterRim_DE10Blaster` ×4, `OuterRim_EC17Blaster` ×2, `OuterRim_SE14RBlaster` ×1 — **all four
of those are tagged `ORPistol`**, and not one of the three rifles appeared in ten spawns.
That is not a coincidence; it is the budget.

✅ **FIXED at `992e1038`:** `weaponMoney` → **950~1150** and `ORImperialLight` dropped, leaving
the three canon rifles, all now affordable (3 of 3).

⚠️ **The 2-of-10 bare is a SEPARATE and still-open question.** The budget explains why they
carried pistols; it does not obviously explain why two carried nothing, since the pistols at
573-592 sat well inside the old 650-780 band. Re-measure after the next cold load: if the
bare rate goes to 0 the budget was the whole story, and if it does not, this item still has
something to find.

⛔ **The item is right that `weaponMoney.min` is not the answer** — that trap stays closed.
The defect was the **ceiling**, not the floor.

## ⚠️ MEASURED LIVE 2026-08-24 — the premise is wrong
`Jawa_Empire_Grunt` rolled **5 of 5 ARMED**. It is **not** "the only kind still spawning
bare-handed": 16 of 49 roster kinds roll bare, and the worst is `Jawa_Homestead_Heavy` at 3 of 5.
(A single earlier probe spawn of Empire_Grunt did come up bare — which is the point: this is a ROLL,
and one sample cannot tell a broken kind from an unlucky one.)
⇒ Retarget or supersede this item; the real shape is in `facts/roll_arm_harvest_2026-08-24.md` §1–2.

---

## ✅ SETTLED 2026-08-27, BUILD — the premise is dead and the real cause is elsewhere

`Jawa_Empire_Grunt` measured live across two runs today: **0 bare of 16**, and **0 bare of 16**
again in the guarded cohort (`EMPIRE_BLACKSTAR_ALWAYS_WILLING_1`, 142 pawns, 0 bare across all
eight Empire and Blackstar kinds).

⇒ **It is not "the only kind still spawning bare-handed", and it is not spawning bare at all.**
The `requiredWorkTags: Violent` guard shipped at `92679d9b` removed the one cause that applied
to it.

🔑 **The whole bare-hands cohort is now explained and this item's framing was wrong.** 150
spawns censusing requested-vs-actual kind resolved every bare pawn into exactly two causes —
a violence-disabling backstory, or a silently substituted vanilla kind
(`SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1`). **There is no `weaponMoney` defect**: the corrected
`weapon_affordability.py` reports `always arms 49 · sometimes 0 · never 0 · unmeasured 0`.

⭐ **The trap this item existed to keep closed stayed closed and was right.** `weaponMoney.min`
was never the answer. ⚠️ The 2026-08-23 correction inside it — that the *ceiling* was the defect,
every `ORImperialStandard` rifle costing 906 against a 780 ceiling — was correct and is what the
`950~1150` fix addressed.

⛔ **Do not re-open on a single bare Empire pawn.** One sample cannot tell a broken kind from an
unlucky roll; that mistake is what produced this item's headline.
