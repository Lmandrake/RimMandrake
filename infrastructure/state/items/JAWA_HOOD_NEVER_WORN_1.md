# JAWA_HOOD_NEVER_WORN_1 — SOLVED. Inherited `apparelRequired` items win the head slot.

Observed live 2026-08-26 during C40, diagnosed the same day with the game down.
**16 of 16** `Jawa_Tribal_Scavenger` wear `guy762_Robes_jawa`. **0 of 16** wear `guy762_JawaHood`.
They wear `Apparel_WarVeil` instead — *despite `apparelMoney 0`*.

## 🔴 The game has been logging the cause on every load

```
Config error in Jawa_Tribal_Scavenger: required apparel can't be worn together (Apparel_WarVeil, guy762_JawaHood)
Config error in Jawa_Tribal_Elder:     required apparel can't be worn together (Apparel_TribalHeaddress, guy762_JawaHood)
Config error in Jawa_Tribal_Elder:     required apparel can't be worn together (Apparel_PlateArmor, guy762_Robes_jawa)
```

`PawnKindDef.ConfigErrors` (`Verse/PawnKindDef.cs:461-469`) runs `ApparelUtility.CanWearTogether`
over every pair in `apparelRequired` and yields exactly this string. Nobody had read it.

## The mechanism, from the source, not inferred

`apparelRequired` **inherits and APPENDS.** The effective lists, read out of the def dump:

```
Jawa_Tribal_Scavenger   [Apparel_WarVeil, guy762_Robes_jawa, guy762_JawaHood]
Jawa_Tribal_Elder       [Apparel_TribalHeaddress, Apparel_PlateArmor, guy762_Robes_jawa, guy762_JawaHood]
Jawa_Colonist           [guy762_Robes_jawa, guy762_JawaHood]        <- clean
Jawa_Tribal_Slinger     [guy762_Robes_jawa, guy762_JawaHood]        <- clean
```

`JawaColonistPawnKinds.xml` declares only the last two entries. The first ones come from
`ParentName="TribalWarriorBase"` — Core's `Tribal_Warrior` — and **the inherited items are FIRST in
the list.**

`PawnApparelGenerator.GenerateWorkingPossibleApparelSetFor` (`RimWorld/PawnApparelGenerator.cs:889`)
walks that list in order and takes an item only when
**`!workingSet.PairOverlapsAnything(pa)`**:

```csharp
for (i = 0; i < reqApparel.Count; i++)
    if (... allApparelPairs.Where(pa => pa.thing == reqApparel[i] && CanUseStuff(pawn, pa)
        && !workingSet.PairOverlapsAnything(pa)).TryRandomElementByWeight(...))
```

And the slots collide exactly:

| def | bodyPartGroups | layer |
|---|---|---|
| `Apparel_WarVeil` | **FullHead** | Overhead |
| `guy762_JawaHood` | **UpperHead, Mouth** | Overhead |
| `guy762_Robes_jawa` | Torso, Shoulders, Arms, Hands, Legs, Feet | Middle, OnSkin |

⇒ WarVeil is taken first, the hood overlaps it and is silently skipped, and the robe — a different
layer entirely — lands every time. **That is the whole of it, and it explains all 16 pawns.**

## ⚠️ It is worse than the hood: `Jawa_Tribal_Elder` also loses the ROBE

`Apparel_PlateArmor` is inherited ahead of `guy762_Robes_jawa` and overlaps it. Nobody has looked
at an Elder. **Untested prediction:** an Elder spawns in plate and a headdress with neither Jawa
piece; `Jawa_Colonist` and `Jawa_Tribal_Slinger`, whose lists are clean, wear both.

## The fix, and why the obvious one will not work

✅ **`<apparelRequired Inherit="False">` on `Jawa_Tribal_Scavenger` and `Jawa_Tribal_Elder`.**

⛔ A `PatchOperationRemove` on the inherited `<li>` will NOT work — the parent's items are not in the
child's XML to remove, and a patch that matches nothing logs nothing. This is the inherited-list
trap this project has already paid for once.

⚠️ **And the comment in `JawaColonistPawnKinds.xml` is half wrong, in the reassuring direction.**
It says *"apparelRequired is generated unconditionally - it ignores both `apparelTags` and
`apparelMoney`... so the robe and hood always land at any budget."* Money — yes. **Unconditional —
no.** Each item is skipped on a body-part overlap with anything already taken, which is precisely
what happened. That sentence is why nobody looked here. `src/**` is BUILD's, so the correction is
named here rather than edited in.

## How to prove the fix — the pawn wearing it, never the def

Spawn 8 of each of the four kinds and read `jawa/pawn_get` apparel back. Expect
`guy762_Robes_jawa` **and** `guy762_JawaHood` on all four kinds, and the three config-error lines
gone from `Player.log`. ⚠️ Presence of the defs in a dump proves nothing; both mods are active and
always were.

Evidence: `infrastructure/state/evidence/C40_jawa_fixes_2026-08-26_CHECK.md`
