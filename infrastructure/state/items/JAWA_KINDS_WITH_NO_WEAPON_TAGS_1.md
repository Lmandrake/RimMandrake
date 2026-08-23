## spec

🔴 **Fourteen Jawa pawnkinds carry `weaponTags: null` and therefore spawn unarmed every
time.** Measured live 2026-08-23 03:3x — five spawns of each of all 68 `Jawa_*` kinds,
equipment read back with `jawa/pawn_get`:

```
Jawa_Colonist          Jawa_Spawn_Lasat       Jawa_Spawn_Nelvaanian   Jawa_Spawn_Taung
Jawa_Spawn_Gand        Jawa_Spawn_Mimbanese   Jawa_Spawn_Ortolan      Jawa_Spawn_Yoder
Jawa_Spawn_Hutt        Jawa_Spawn_Muun        Jawa_Spawn_SithK        Jawa_Spawn_Zygerrian
Jawa_Spawn_Kubaz                              Jawa_Spawn_SithM
```

**5 of 5 bare, every one.** They account for **70 of the 73** bare pawns in a 340-pawn
census.

🔑 **This is structural, not a roll.** A kind with no `weaponTags` has no pool to draw
from, so `weaponMoney` is irrelevant — every one of these carries a `weaponMoney` range
and it can never be spent. ⛔ **No money change can fix this**, and reaching for one is
the trap `BARE_HANDS_REMEASURE_AFTER_LOAD_1` already refuted.

⭐ **Excluding them, the roster is healthy:** of the 54 kinds that DO carry tags, 270
spawns produced **3 bare — 1.1%** — and not one was bare 5/5, which is
`WEAPON_FLOOR_BOWS_KNIVES_1`'s stated PASS condition.

## The question this item is really asking

⚠️ **Some of these are probably CORRECT unarmed, and nobody has decided which.**
`Jawa_Colonist` is a colonist kind — colonists are not generated holding a rifle, and
`combatPower 30` fits a civilian. The thirteen `Jawa_Spawn_*` are species *enablers* from
`AlienSpawnEnablers.xml`, whose job is to make a species exist in the world, and they all
carry an identical `combatPower 40`.

⇒ **Two possibilities, and they need separating before anything is edited:**

- **Deliberate.** These are civilian/spawner kinds; unarmed is right; the only defect is
  that they carry a `weaponMoney` that misleads every future reader into thinking they
  should be armed. Fix: drop the dead `weaponMoney`.
- **An omission.** They were meant to inherit tags from a parent and do not. Fix: give
  them tags that match their faction's tech.

🔴 **Do not resolve this by copying tags onto all fourteen.** If a Hutt or an Ortolan
enabler starts spawning armed, raids change composition, and this project's own rule is
that an appearance change must not become a behavioural one by accident.

## verify

- Each of the fourteen is classified deliberate-unarmed or missing-tags, in writing.
- Any kind ruled deliberate-unarmed has no `weaponMoney`, so the def stops implying a
  weapon it can never draw.
- Any kind ruled missing-tags spawns armed 5/5 on a live re-census.

## criteria

`WEAPON_FLOOR_BOWS_KNIVES_1`'s "no kind is bare 5/5" is either true, or false only for
kinds a human has deliberately marked as unarmed.
