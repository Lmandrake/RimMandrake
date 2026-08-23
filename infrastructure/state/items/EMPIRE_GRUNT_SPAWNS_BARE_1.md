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
