## spec
`TribalWarriorBase` asks for `weaponTags: NeolithicMeleeDecent`.
🔴 **In our 578-mod load set, NOTHING carries that tag.**
Scanned every file under the workshop, then narrowed to weapon defs that really
carry the tag rather than merely naming it: **exactly two defs in the world do.**
  `MeleeWeapon_Ikwa`   — vanilla Core, and it is in our **CUT** list
  `MPW_Bladelink_Ikwa` — kept, but it belongs to `Arquebus.MedievalPersonaWeapons`
                         which is **NOT in the active list**, and it is a persona
                         weapon besides.
⇒ the tag resolves to an empty set. **A pawnkind whose only weapon tag is empty
spawns bare-handed** — the same failure mode as B65's Autopistol.
⚠️ **The blast radius is every kind inheriting `TribalWarriorBase`**, which
includes vanilla tribal warriors AND our Deep Desert Tribes water raid (B42 uses
`Tribal_Hunter` · `Tribal_Archer` · `Tribal_Warrior`). The signature raid of a
faction arrives with no weapons.
🔴 **CORRECTION, 2026-08-19: `weaponTags` IS in the def dump** — 696 ThingDefs
and 414 PawnKindDefs carry it. The "invisible on every offline channel" line came
from B58's note and was repeated here without being measured. The dump is in fact
the BETTER instrument, being post-inheritance, post-patch and post-dedup, and the
owner has ruled it authoritative whenever its version matches the live mod list.
⚠️ The current dump is `modCount 579` against an active list of 578, so it does
NOT match and this census is PROVISIONAL. Re-derive it from the dump regenerated
after the full list is restored.

## verify
done offline: the scan output and the cut list. `MeleeWeapon_Ikwa` is present in
`observed/inventory/decisions_weapons.json` `cut`; `Arquebus.MedievalPersonaWeapons`
is absent from `ModsConfig.FULL.LATEST.xml`.

## criteria
spawn a `Tribal_Warrior` and a Deep Desert Tribes raid and look at their hands.
🔴 If they are armed, something supplies the tag that this scan did not see and
the finding is wrong — say so, because the fix below would then be unnecessary.
THE FIX IS A CONTENT CALL AND IS FILED TO DECIDE as
`the-tribal-melee-tag-is-empty-pick-the-weapon-4a72e8`: un-cut the ikwa, add the
tag to a kept neolithic melee weapon, or give our own kinds explicit weaponTags.
⭐ **AND THE HEADLINE IS TOO BROAD — corrected 2026-08-19 after the owner
said "I think we still have some kind of bow enabled actually." He is right.**
Six bows survive the cut, including `MA_CapryakScatterbow`, a real neolithic bow.
What was cut is the VANILLA set — `Bow_Short`, `Bow_Recurve`, `Bow_Great`,
`Flamebow` and the VWE longbow and crossbow.
🔑 A tag emptying is only fatal to a kind with NO surviving alternative, and the
per-kind census off the dump says **2 of 8 vanilla tribal kinds** are affected,
not all of them:
  `Tribal_Warrior`  `NeolithicMeleeDecent`  (0 left)  -> DISARMED
  `Tribal_Hunter`   `NeolithicRangedDecent` (0 left)  -> DISARMED
  `Tribal_Archer`   `NeolithicRangedBasic`  (1 left)  -> armed, with THROWING
                                                         KNIVES, not a bow
  the other five draw on ladders with 2-9 survivors each -> armed
Both broken ones list **exactly one tag**, read off Core's
`PawnKinds_Tribal.xml:85-87`. A kind with one tag has no fallback; the melee and
ranged ladders are otherwise healthy.
⇒ B42's water raid is `Tribal_Hunter 10 · Tribal_Archer 8 · Tribal_Warrior 4`, so
roughly two thirds of it arrives empty-handed and the rest throw knives.
🔴 TWO OF OUR OWN KINDS ARE IN THE SAME STATE: `Jawa_Tribal_Scavenger`
(`NeolithicMeleeDecent`) — which is C40(c) — and `Jawa_Gamorrean_Enforcer`
(`HC_gamorreanaxe`). 49 kinds are affected across the whole stack, `Mechanitor`
and `Mechanitor_Basic` on `Autopistol` among them, which independently confirms
B65's diagnosis.

## notes
**from:** BUILD, 2026-08-19. This is C40(a)'s missing check — the workshop-wide scan that
timed out twice on 2026-08-15 and was abandoned. It has now run to completion and
the suspicion is PROVEN.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

✅ DONE — the finding is REFUTED, 2026-08-20, on the criterion the item itself set.

**result:** The item said: "🔴 If they are armed, something supplies the tag that this scan
did not see and the finding is wrong — say so." **They are armed.** Spawned live
on the full 577-mod set and read back with `jawa/pawn_get`:
  Tribal_Warrior         BMT_FungalMantisClaw     ← predicted DISARMED
  Tribal_Hunter          NerveSpiker              ← predicted DISARMED
  Tribal_Archer          VWE_Throwing_Knives      (as predicted)
  Tribal_Berserker       MA_SivatheriumHorn
  Jawa_Tribal_Scavenger  GS_Gaffi                 ← C40(c), also armed
  Jawa_Gamorrean_Enforcer guy762_baton            ← predicted DISARMED
⇒ modded weapons carry `NeolithicMeleeDecent` and `NeolithicRangedDecent`; the
workshop scan missed them. **No fix is needed and the DECIDE item behind this
(`the-tribal-melee-tag-is-empty-pick-the-weapon-4a72e8`) is moot.** The offline
census was run against a dump whose modCount did not match the active list, which
the item flagged as PROVISIONAL — that caveat was the correct one.
🔑 THE GENERAL LESSON, worth more than the item: a tag census answers "does any
weapon carry this tag", and that was never the question. What disarms a pawn here
is `weaponMoney`, not an empty tag — see the item below, which this test found.
