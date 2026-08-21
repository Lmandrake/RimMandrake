## spec
`first_light.py` reports 17 pawn kinds that "cannot afford the cheapest weapon their tags
allow", and proposes a fix per row:

    Town_Trader      money max 200, cheapest Gun_IncendiaryLauncher at 340 -> raise max to 340
    Town_Councilman  money max 200, cheapest Gun_IncendiaryLauncher at 340 -> raise max to 340
    Hunter           money max 250, cheapest Gun_IncendiaryLauncher at 340 -> raise max to 340
    Scavenger        money max 300, cheapest Gun_IncendiaryLauncher at 340 -> raise max to 340
    Mercenary_Sniper money max 600, cheapest guy762_brifle_dmr    at 760 -> raise max to 760

🔴 **Arming a town trader with an incendiary launcher is not a fix, it is a symptom.** The
number is right and the conclusion drawn from it is not: a hunter carrying an incendiary
launcher is a worse outcome than a hunter carrying nothing, and "raise the budget" is the
answer only if the POOL is sane.

### What is established offline, from the 2026-08-21 dump

✅ Those kinds carry the tag **`Gun`** and budgets of 140–300 (`Mercenary_Sniper` carries
`SniperRifle` at 600).

🔴 **Every vanilla gun in the dump reads `weaponTags: []`** — `Gun_Revolver`,
`Gun_BoltActionRifle`, `Gun_Autopistol`, `Gun_PumpShotgun`, `Gun_MachinePistol`,
`Gun_HeavySMG`, `Gun_AssaultRifle`, `Gun_SniperRifle`. Meanwhile
`Gun_IncendiaryLauncher` keeps `['Gun', 'GunHeavy', 'IndustrialGunAdvanced']`.

⇒ If that is true at runtime, **the cheap end of the `Gun` pool has been emptied**, and the
cheapest thing a `Gun`-tagged kind can reach really is a heavy launcher. That is the defect,
and raising the budget would bake it in.

⚠️ **UNCERTAIN, and it matters:** whether the dump is telling the truth here. Core still
reports 23 of its 51 weapon-tag-carrying defs as non-empty, so the dumper is not simply
dropping vanilla tags wholesale. But every vanilla gun also reads `MarketValue: 0.0`, which
is not a plausible price for a revolver, so at least one of the two fields is being reported
badly. ⛔ **Do not act on the dump alone.**

⭐ Corroboration that is NOT from the dump: `first_light` derived `Gun_IncendiaryLauncher` at
340 from the **live game's own weapon-pair table**, and independently reached the same
conclusion — that the cheapest `Gun` a trader can buy is a launcher. Two instruments, one
answer, one of them live.

## verify
Live, on the next load — this is the instrument that cannot drift, because it is the engine's
own eligibility test:

    jawa/pawnkind_audit  (no filter, includeHealthy=true)

For each of the five kinds above, read the reported `cheapest eligible weapon`. Then read
`Gun_Revolver`'s runtime `weaponTags` off the live game.

- revolver HAS `Gun` at runtime ⇒ the dump lied, the pool is fine, and the 17 rows are a
  budget question after all
- revolver has NO `Gun` at runtime ⇒ the pool really is emptied, and the fix is to restore
  the tag rather than raise the money

## criteria
- the runtime tags of at least three vanilla cheap guns are recorded
- the cause is named as **pool** or **budget**, with the evidence for the call
- ⛔ no `weaponMoney` is raised on any kind until that call is made
- 🔑 and if it is the pool: find WHAT stripped the tags. The content-moderation skill's
  standing trap is that cutting the last weapon carrying a tag silently disarms every kind
  whose tags all went to zero — Cherry Picker is the owner's cutting mechanism and is the
  first place to look

## notes
Filed for CHECK 2026-08-21. ⚠️ I got this wrong once on the way in: my first pass read
`statBases` as a dict, found no `MarketValue` anywhere, and concluded the dump could not
price weapons at all. It is a LIST of `StatModifier` objects. The corrected read is what
produced the finding above — and the wrong read would have produced a confident,
completely different story.
