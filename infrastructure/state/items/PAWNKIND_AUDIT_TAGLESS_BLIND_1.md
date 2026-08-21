## spec
`first_light.py`'s "Pawn kinds that cannot arm themselves" section reports, verbatim:

> *"Not counted: 291 with no weaponTags and 9 with weaponMoney.max 0 — both are how a
> civilian or a child is kept unarmed."*

That heuristic is **right in general and hides the case that matters**. A kind with no
`weaponTags` is usually a deliberate civilian. But a COMBAT role that has LOST its tags —
because a patch stopped emitting them, or the field was dropped in an edit — looks
identical, and is silently excluded from the count.

🔑 It is not hypothetical: `sixteen-authored-role-kinds-spawn-bare-handed-on-weaponmoney`
records three of our own authored kinds that once had **no `weaponTags` field at all**
(`Jawa_Droid_Leader`, `Jawa_Droid_Specialist`, `Jawa_TradeMoot_Specialist`). While that was
true, first_light would have reported them as intentionally-unarmed civilians.

⚠️ This is one of seven instruments caught returning a confident wrong number on
2026-08-21 — see `infrastructure/state/BUILDABLE.md`, "INSTRUMENTS THAT RETURN A CONFIDENT
WRONG ANSWER". It is the last one still unfixed and unfiled, which is why it is filed now.
✅ `weapon_tag_audit.py` does NOT have this blind spot and is the correct instrument for the
question today — this item is about the report the owner actually runs saying something
true, not about lacking any way to find out.

The fix is in the companion (`jawa/pawnkind_audit`), so it needs the game DOWN.

## verify
A kind with a combat role, `isFighter` true or a non-zero `combatPower`, and NO
`weaponTags` field is reported in its own line — something like "N kinds intend to fight
and carry no weaponTags at all" — rather than folded into the civilian exclusion.
⛔ Do not simply stop excluding tagless kinds: that would report 291 civilians as broken and
make the section useless, which is how the heuristic got there in the first place.

## criteria
Take a kind that currently has `weaponTags`, remove them in a scratch copy, and confirm
first_light names it rather than silently reclassifying it as a civilian.

## notes
Filed by BUILD 2026-08-21 on the owner's question: *"Did we fix all of these string issues
so we don't keep generating false negative results? This is very disturbing."* Three of the
seven were fixed in code, one was already filed, and this was the last one living only in a
ledger note.
