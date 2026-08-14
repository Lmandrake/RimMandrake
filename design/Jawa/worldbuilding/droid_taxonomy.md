# The three droid families, and what each is FOR

_VISION, 2026-08-13. Measured across all 57 droids in the three active droid
mods. **The headline finding contradicts a belief this project has been designing
against.**_

---

## 🔴 CORRECTED — the explosion tier is OUR DESIGN, not a claim about the mods

⚠️ **My first version of this section said "the self-destruct belief is wrong".
That was unfair and it misread our own paperwork.** `design/Jawa/droid_ruling.md`
§6 *specifies* an explosion tier that we intend to author — it is a ruling, not a
misremembered fact:

> *"Explosions remain about **energy density**: only droids with large shielding…
> cannot explode. POWER DENSITY explodes, not the fact it's a machine."*

It assigns `explodeOnKilled` to **shield-generator units, heavy weapons platforms
and reactor/battery units**, with `chanceNeverExplodeFromDamage: 1`, and
explicitly rules that ion-blasted droids must NOT explode.

**So the design stands. What the measurement corrects is narrower:**

`droid_ruling.md`'s heading *"JDS droids blow up, and that is the point"* reads
as describing the mod. It does not. **Measured: that mod contains no `deathAction`, no
`CompExplosive` and no DLL at all.** Grepped across all three mods, **exactly one
droid self-destructs** — `guy762_DroidRace_KX12APD`, the K-X12 assassin probe,
via `DeathActionWorker_BigExplosion` at `AlienRace_KX12probe.xml:479`.

**The real JDS mechanism is different and much better for us.** They use
`fleshType Mechanoid`, so vanilla forces `deathOnDownedChance = 1.0` — **killed
instead of downed, never a prisoner.** But the wreck is ordinary salvage, and the
mod ships its own repair recipes (`JDSCIS_ResurrectDroid_Light` / `_Heavy`,
1 corpse + 150 steel) that rebuild it into a working droid.

⇒ **Two separate facts, both true:**
1. **As shipped**, exactly one droid explodes. Nothing we would have to *remove*.
2. **By our design**, an explosion tier gets *added* — to energy-dense units
   only, on death and never on downing.

⭐ **And the two fit together perfectly.** `explodeOnKilled` fires on
`KillFinalize`; **a downed pawn has not died, so it does not explode.** The Jawa
fantasy — down it, drag it home, repair it — survives the explosion tier
completely intact. **The tier costs the player nothing except the units they
choose to kill outright.**

## ⭐ The three families are three different relationships with machines

**They do not overlap, and that is the argument for keeping all three.**

| family | what it is to the clan | alive | dead |
|---|---|---|---|
| **KotOR rogue droids** (22) | ⭐ **the enemy you can convert.** A real hostile faction with seven raid compositions and boss units — and every single one is capturable and reprogrammable | **capturable** — universal reprogram surgery | salvageable corpse |
| **JDS Separatists** (16) | ⭐ **the enemy you can only scavenge.** Pure hostile army, no trade, no peace, never taken alive — but every wreck rebuilds | **never** — force-killed on downing | **repairable** back into a working droid |
| **Outer Rim Depot** (19) | **the workforce you buy and build.** No hostile faction at all — its "rogue droid colony" is a *player* faction for a scenario start. **Nobody fields these against you** | capturable | butcherable — droid brain, durasteel, hypertech components |

⭐ **Three registers, no redundancy: convert · scavenge · purchase.** That is a
complete machine economy for a scavenger clan, and it arrived without anyone
designing it.

## What this means for the campaign

- **KotOR is the spine.** It is the only mod supplying enemy, loot and workforce
  at once — and *taking a raider apart and putting it to work* is the purest
  expression of the Jawa fantasy the stack can produce.
- **JDS is the wreck economy.** You cannot take a Separatist alive; you take its
  parts. **That is a different verb from capture and it deserves to stay
  different.**
- **Outer Rim is the catalogue.** Player-side only, and it is where the
  restraining-bolt question actually bites, because these are the droids the clan
  owns in bulk.

⚠️ **Outer Rim's combat/utility split is the soft one.** That mod ships **no
weapon tags, no `pawnGroupMakers`, and a sentinel `combatPower`** (40 for every
humanlike, 99999 for every animal-race droid — including the mouse droid). Its
classification rests on automaton comp flags and authored skills alone. **If a
build decision turns on it, check it live first.**

## Filed, not fixed

**`design/Jawa/droid_ruling.md` needs its mechanism corrected** — the ruling it
reaches (JDS uncapturable, do not bother ion-stunning them) still holds, but the
stated reason is wrong. **Not my file.** The correction is the paragraph above.
