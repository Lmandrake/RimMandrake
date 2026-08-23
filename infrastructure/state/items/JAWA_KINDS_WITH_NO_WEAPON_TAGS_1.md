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

## ✅ DECIDE'S RULING, 2026-08-23 — all fourteen are DELIBERATE-UNARMED. Nothing to edit.

**And two of this item's premises are wrong. Both corrections matter more than the ruling.**

### ⛔ Correction 1: `weaponMoney` is ALREADY `0..0` on all fourteen — there is nothing dead to drop

This item proposes *"drop the dead `weaponMoney`"* so the def stops implying a weapon it can
never draw. Measured off the live capture: **every one of the fourteen carries
`weaponMoney {min: 0, max: 0}`.** That is not a misleading leftover — it is the def **already
saying, correctly, that this kind buys no weapon.** The suggested edit would remove a field
that is doing its job. ⇒ **No def change on any of the fourteen.**

### ⛔ Correction 2: thirteen of the fourteen are fielded by NOTHING AT ALL

Searched every `FactionDef`, `PawnGroupMakerDef`, `ScenarioDef`, `QuestScriptDef` and
`RaidStrategyDef` for an exact-quoted reference:

| kind | referenced by |
|---|---|
| `Jawa_Spawn_Gand` · `Kubaz` · `Taung` · `Mimbanese` · `Zygerrian` · `Lasat` · `Muun` · `Ortolan` · `Nelvaanian` · `SithK` · `SithM` · `Yoder` | 🔴 **nothing** |
| `Jawa_Colonist` | nothing in defs — a colonist takes its gear from the **scenario**, and unarmed is how vanilla colonists generate |
| `Jawa_Spawn_Hutt` | `Jawa_HuttCartel` → `pawnGroupMakers[1]` (**Trader**) → **`guards`**, selectionWeight **1** against Gamorrean Guard 6 and Enforcer 2 |

⇒ **Twelve species enablers never enter a raid, a trade caravan or a settlement.** Their whole
job is to make a species exist in the world. An enabler nobody fields cannot spawn bare in play,
so `combatPower 40` on them is inert too.

### ⭐ And the fourteenth is not a defect either — it is the best detail in the file

`Jawa_Spawn_Hutt` appears **once**, as a rare **trade-caravan guard**. 🔑 **A Hutt is not a
guard — a Hutt is what guards are FOR.** An unarmed Hutt arriving with a caravan, at weight 1
in 9, behind two Gamorreans who do carry weapons, is the crime lord riding along with his own
muscle. That reads exactly right, and arming it would break it. **Leave it.**

## criteria — answered
`WEAPON_FLOOR_BOWS_KNIVES_1`'s *"no kind is bare 5/5"* stands, with these **fourteen named as
deliberately unarmed**. Its PASS condition should read: *no kind is bare 5/5 except the fourteen
on the deliberate list.* ⭐ Excluding them the roster is healthy — 270 spawns across the 54
tagged kinds produced **3 bare, 1.1%**, none of them 5/5.
⛔ **Do not re-file this as a bare-hands defect.** Two items have now reached for `weaponMoney`
as the cause; it is 0–0 on purpose, and the 70 bare pawns are twelve enablers nothing fields,
one colonist, and one Hutt being a Hutt.
