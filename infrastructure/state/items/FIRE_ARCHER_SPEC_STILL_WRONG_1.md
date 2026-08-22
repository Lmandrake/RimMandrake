## spec
`infrastructure/state/items/FIRE_ARCHERS_GET_BOWS_1.md` is closed and what shipped
(`d82c5cb`) is correct — but its spec text still asserts both facts that
`CUT_TABLE_PAIRED_WRONG_1` ruled dead, and it is the file a reader arrives at.

Two lines to correct, both near the head:

| line | says | truth |
|---|---|---|
| ~3–4 | ``NeolithicRangedFlame`` is "the only ranged tag on `Tribal_Archer_Fire` and `Tribal_Hunter_Fire`. **Both spawn bare-handed.**" | ⛔ `Tribal_Hunter_Fire` was never disarmed. It resolves to `['NeolithicRangedDecent','NeolithicRangedFlame']` and `weapon_tag_audit.py` does not list it |
| ~14–15 | "**APPEND** the vanilla tag `NeolithicRanged`" | ⛔ **zero carriers.** What shipped is `NeolithicRangedBasic` (5 carriers), which `Tribal_Archer` already carries at the same `weaponMoney` 80~80 |

🔑 **Why it matters that the item is closed.** A closed item reads as settled, so its spec
is exactly what a later reader copies. `NeolithicRanged` would apply cleanly, match its
xpath, log nothing, and leave the kind bare-handed with the item closed green — the
silent-success class this project keeps paying for.

🔴 **Why DECIDE filed this instead of fixing it.** DECIDE wrote the correction, and the
`queue_lint` hook refused the commit: the file belongs to BUILD. That is the same guard
that stopped BUILD committing `CUT_DISARMED_VANILLA_KINDS_1.md`, which DECIDE owns and
has now committed (`9c9bd61b`). The guard is right both times — it just means each
correction has to be made by the seat that owns the file.

⚠️ Do not restate the mechanism from memory. It is published once, in
`infrastructure/state/BUILDABLE.md` 9 and 10: **losing a tag's sole carrier disarms a kind
ONLY if that kind also blocks inheritance.** `Tribal_Archer_Fire` carries
`<weaponTags Inherit="False">`; `Tribal_Hunter_Fire` does not, so it appends to
`Tribal_Hunter`'s live tag. Cite it, do not re-derive it.

## verify
- `grep -n "NeolithicRanged\b" infrastructure/state/items/FIRE_ARCHERS_GET_BOWS_1.md`
  returns nothing that is not inside a strikethrough or a correction note.
- The file no longer asserts that `Tribal_Hunter_Fire` spawns bare-handed.
- No code changes. `d82c5cb` shipped the right patch and must not be touched.

## criteria
A reader arriving cold at the closed fire-archer item cannot re-derive either dead fact.
