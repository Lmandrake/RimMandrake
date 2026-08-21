## spec
`TribalWarriorBase` asks for `weaponTags: NeolithicMeleeDecent` and **nothing in
the 578-mod load set carries it.** Vanilla's `MeleeWeapon_Ikwa` is the only Core
weapon with the tag and it is in our CUT list; the one other def in the entire
workshop that carries it belongs to a mod we do not run. An empty weapon tag
spawns pawns bare-handed.
⇒ every kind inheriting `TribalWarriorBase` is unarmed, including the Deep Desert
Tribes water raid — B42's signature raid, and the reason B42 exists.
THE CHOICES, all one line of XML:
(a) **Un-cut `MeleeWeapon_Ikwa`.** Smallest change, restores vanilla behaviour
    everywhere at once, and the ikwa is a plausible desert-tribal weapon. ⚠️ it
    was cut deliberately; this reverses that.
(b) **Add `NeolithicMeleeDecent` to a kept neolithic melee weapon** via a patch —
    spear, club, mace, whatever survived. Keeps the cut and fills the tag. Needs
    a pick, which is why this is here.
(c) **Give our own kinds explicit `weaponTags`** and leave vanilla tribals
    unarmed. Narrowest blast radius, but it leaves a known-broken vanilla
    inheritance in a campaign we are freezing.
🔑 Whichever is chosen, the same trap applies to B53's 48 pawn kinds, which are
about to be authored with `weaponTags`: **a tag is only real if a SURVIVING
weapon carries it.** BUILD is building the tag -> surviving-weapon index now and
will refuse to write a tag that resolves to nothing.
⭐ **NARROWED 2026-08-19, twice, and the fix got cheaper both times.**
(i) The owner: *"I think we still have some kind of bow enabled actually."* Correct
    — six bows survive, including `MA_CapryakScatterbow` on
    `NeolithicRangedAdvanced`. Only the VANILLA bow set was cut.
(ii) Re-measured off the def dump rather than raw XML — post-inheritance and
    post-patch, per the owner's ruling on which instrument to trust — the damage
    is **kinds that list exactly ONE tag**, not a whole tier. Two vanilla tribal
    kinds qualify (`Tribal_Warrior`, `Tribal_Hunter`) and two of ours
    (`Jawa_Tribal_Scavenger`, `Jawa_Gamorrean_Enforcer`); 49 across the stack.
⇒ 🔑 **NEW OPTION (d), and it is now the cheapest and least invasive: give each
single-tag kind a SECOND tag that already resolves.** `NeolithicMeleeAdvanced`
(8 survivors) for the warrior and scavenger, `NeolithicRangedAdvanced` (the
scatterbow) or `NeolithicRangedHeavy` (3) for the hunter. One patch, no cut
reversed, no vanilla weapon restored, and the ladder does the rest.
⛔ (a) un-cutting the ikwa is no longer recommended — it fixes one rung of one
ladder and reverses a deliberate decision to do it.
⚠️ The census is PROVISIONAL until the dump matches the mod list: the current
dump is `modCount 579` against 578 active. Re-run after the restore and load.

## verify
n/a — a ruling.

## criteria
n/a

## notes
**from:** BUILD, 2026-08-19, off the completed C40(a) scan. Measured, not suspected.

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

✅ CLOSED 2026-08-20 — **ALREADY FIXED BY BUILD. Verified, not assumed.**
BUILD took choice **(b)**: `src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`
grants `NeolithicMeleeDecent` to kept weapons — `AG_ForsakenSpear`,
`AlphaThrumboHorn` and others — and it is **DEPLOYED** to
`...\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Patches\`, stamped
2026-08-20 00:04. `MeleeWeapon_Ikwa` remains cut, correctly; (a) was not needed.
⭐ **And BUILD used `PatchOperationConditional`**, so it works whether or not the
target def already has a `weaponTags` node — the silent-no-op failure a plain
`PatchOperationAdd` would have hit on any weapon lacking it.
⚠️ **CHECK's queue still lists `Tribal_Warrior → NeolithicMeleeDecent (0 left) →
DISARMED`.** That line is stale; the measurement predates the patch.
