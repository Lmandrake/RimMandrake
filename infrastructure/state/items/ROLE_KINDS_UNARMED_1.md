## spec
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`.
**16 of the 48 `Jawa_*` role kinds spawn with NO weapon, 5/5 samples each.**
The `weaponTags` are HEALTHY — `ORDroidWeapon` 5 weapons, `Jawa_IonWeapon` 7,
`KotORBowcaster` 3. RimWorld then filters those by MarketValue against
`weaponMoney`, and not one weapon falls inside the range.
🔴 **CORRECTION 2026-08-20, read out of `PawnWeaponGenerator.TryGenerateWeaponFor`
after this item was filed. The rule is a CEILING, not a bracket.** The engine
rolls `weaponMoney.RandomInRange` once, then keeps every weapon pair whose
`Price` is **not greater than** that roll:
    `if (!(w.Price > randomInRange) && <tags match> && ...)`
⇒ **`min` is not a floor on eligibility.** It only shifts the roll. What empties
the pool is `max` sitting below the cheapest tagged weapon. So the fix is to
raise `max` above the cheapest candidate — raising `min` as well is a
separate, cosmetic choice about how rich the tier looks.
⚠️ And the engine compares `ThingStuffPair.Price`, which includes STUFF cost, not
the bare `MarketValue` the numbers below are taken from. Treat them as a floor:
the real price of a stuffed weapon is higher, never lower.
(a) RAISE `weaponMoney` (the `max` especially) to clear the real weapon values.
Measured off the
    577-mod dump, which MATCHES the live list, so these numbers are not
    provisional — `min` must be at or below the cheapest tagged weapon:
      Jawa_TradeMoot_Grunt        120-144    cheapest  800   (Jawa_IonWeaponLight/Jawa_IonWeapon, 800-2000)
      Jawa_TradeMoot_Leader       450-540    cheapest  800   (Jawa_IonWeapon, 800-2000)
      Jawa_Wildsteam_Grunt        200-240    cheapest 1250   (KotORBowcaster, 1250-13750)
      Jawa_Wildsteam_Leader       800-960    cheapest 1250   (KotORBowcaster, 1250-13750)
      Jawa_Wildsteam_Heavy        400-480    cheapest  550   (+SWKotORWeaponCategoryTag_heavyranged, 550-99999)
      Jawa_DeepDesert_Specialist  300-360    only     1977   (SaV_tusken)
      Jawa_Helix_Leader          2200-2640   cheapest 12000  (KotORRanged_legendary, 12000-80000)
      Jawa_Hutt_Leader           2500-3000   cheapest 12000  (KotORRanged_legendary/rare, 12000-80000)
    ⚠️ `Jawa_DeepDesert_Grunt` (90-108, ORTuskenMelee+ORMeleeBlunt),
    `Jawa_Empire_Grunt` (350-420, ORImperialStandard+ORImperialLight) and
    `Jawa_Empire_Heavy` (700-840, ORImperialHeavy+ORHeavyWeapon) are bare live,
    but their tagged weapons report NO `MarketValue` statBase in the dump —
    inherited from a parent it does not resolve. The VALUES ARE UNMEASURED;
    read them off the weapon defs directly rather than trusting a number here.
(b) `Jawa_Droid_Grunt` and `Jawa_Droid_Heavy` carry `weaponMoney 0-0`, which no
    weapon can ever satisfy. Give them a real range over `ORDroidWeapon`.
(c) `Jawa_Droid_Leader`, `Jawa_Droid_Specialist` and `Jawa_TradeMoot_Specialist`
    have **no `weaponTags` field at all**. They need a tag chosen, not a range
    widened — `ORDroidWeapon` for the two droids, an ion tag for the TradeMoot.
📌 Tier intent, so the numbers are not picked blind: Grunt = cheapest tier its
tag offers · Specialist/Heavy = mid · Leader = top. Widening `max` is harmless;
it is `min` sitting above every candidate that empties the pool.

## verify
offline, off the regenerated dump: for each of the 48 kinds, at least one
ThingDef carrying one of its `weaponTags` has a MarketValue inside `weaponMoney`.
A kind with no `weaponTags` fails this check by definition.

## criteria
spawn each of the 48 kinds 5x live and read `jawa/pawn_get` -> `pawns[0].equipment`.
          🔴 5/5 non-empty, for all 48. ONE SAMPLE IS NOT ENOUGH — `Jawa_Geonosian_Specialist`
          reached the suspect list on a single bare roll and is fine at 5/5.
          ⚠️ FALSE PASS: `jawa/pawn_gear` is a WRITER and answers a read with
          "Give a ThingDef." Reading equipment off it reports every pawn as bare.
🔴        **CONFIRMED BY THE GAME'S OWN VALIDATOR, in the 2026-08-20 session log
          (17:54, archived).** RimWorld validates this itself and its message settles the
          argument the item and I were having:
            `Config error in Jawa_Empire_Grunt: Cheapest weapon with one of my weaponTags`
            `costs 570 but weaponMoney MIN is 350, so could end up weaponless.`
            `Config error in Jawa_Empire_Heavy: ... costs 865 but weaponMoney min is 700 ...`
            `Config error in Jawa_TradeMoot_Specialist: weaponMoney is set but weaponTags is not.`
          ⇒ **The engine measures against `min`, not `max`** — the item's *"min must be at
          or below the cheapest tagged weapon"* is refuted by RimWorld in as many words.
          ⭐ **And it independently validates the affordability pass to within 0.5%:** the
          engine says Empire_Grunt 570 / Empire_Heavy 865; the tool computed **573** and
          **867.5**, having priced weapons that declare no MarketValue at all from their
          recipes. Three kinds flagged, and they are three of the nine I fixed.
          ⏳ All three errors were logged by a game that started at 07:59, BEFORE the fix
          deployed. **Next load they should be 0** — that is the cheapest possible check and
          `harvest_log.py`'s `Jawa_Patches ops` row (RED at 3, baseline 0) is where it shows.

## notes
**from:** CHECK, 2026-08-20. Measured live on the full 577-mod set, not inferred.
🔁 Filed to DECIDE first; the OWNER re-routed it here 2026-08-20 — BUILD
implements, the tiers are not a decision to wait on.

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20 (offline half). Table fixed in
`src/RimMandrake/Utils/gen_pawnkind_roster.py`, 48 defs regenerated into
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`, deployed.
verify output:
  `python3 src/RimMandrake/Utils/weapon_affordability.py`
  `always arms 48 · sometimes 0 · never 0 · no tags 0 · unmeasured 0`
  `validate_patch.py --defs` -> `OK - 0 errors, 0 warning(s)`
  48 PawnKindDefs · 48 with `weaponTags` · **0** with `weaponMoney 0~0`

⭐ **THE "AFFORDABILITY PASS" THE GENERATOR TELLS YOU TO RUN DID NOT EXIST.**
`gen_pawnkind_roster.py:55` said *"Re-check with the affordability pass whenever
a tag or a price changes"* and there was no such tool in the repo. Built it:
`src/RimMandrake/Utils/weapon_affordability.py`. It reads the roster table out of
the generator itself, so it cannot drift from the thing it checks.

🔴 **THE ITEM'S OWN CORRECTION IS STILL HALF WRONG, AND THE HALF THAT IS WRONG
IS THE ONE THAT DECIDES THE 5/5 CRITERION.** It says *"`min` must be at or below
the cheapest tagged weapon"*. Read out of `TryGenerateWeaponFor`: the engine
rolls `weaponMoney.RandomInRange` **once**, keeps every weapon priced at or below
that roll, and if the pool is empty **the pawn gets nothing**. So:
  `max >= cheapest`  ->  the kind CAN arm
  `min >= cheapest`  ->  the kind ALWAYS arms
A `min` *below* the cheapest weapon means every roll under that price arms
nobody. ⇒ **for 5/5, `min` must be at or ABOVE the cheapest**, not below.
The pass reports the middle case as `ARMS ONLY SOMETIMES` with its odds rather
than as a pass — `Jawa_Wildsteam_Specialist` was armed on 62% of rolls.

⭐ **AND THE 9 "UNMEASURED" KINDS ARE NOW MEASURED — the item's advice to "read
them off the weapon defs directly" could not have worked.** Every Outer Rim
weapon declares MaxHitPoints, Flammability, DeteriorationRate and Beauty and **no
`MarketValue` at all**; there is nothing on the def to read. The engine computes
it via `StatWorker_MarketValue.CalculatedBaseMarketValue` from the recipe, and
the pass now reproduces that formula from `costList` + `WorkToMake`:
  `OuterRim_DroidWeapon_BlasterCannon` = **982.5**, which is why
  `weaponMoney 0~0` on the two droid kinds was never the whole story — even 900
  would have armed nobody.
⚠️ **This also corrected MY OWN first run.** Before computed pricing, five kinds
were reported as NEVER ARMS purely because their cheaper weapons had no declared
price and were excluded from the minimum. `Jawa_Homestead_Specialist`,
`Jawa_Deepwater_Leader`, `Jawa_Helix_Specialist`, `Jawa_Blackstar_Specialist` and
`Jawa_Blackstar_Leader` are all fine and needed no change.

WHAT CHANGED, 9 kinds:
  `Empire_Grunt` 350->650 · `Empire_Heavy` 700->1000 · `DeepDesert_Grunt` 90->150
  `Wildsteam_Specialist` 500->620
  `Droid_Grunt` 0->1100 · `Droid_Heavy` 0->1400   (cheapest droid weapon 982.5)
  `Droid_Specialist` 0->1200 + `ORDroidWeapon` · `Droid_Leader` 0->1800 +
  `ORDroidWeapon` · `TradeMoot_Specialist` 300->900 + `Jawa_IonWeapon`,
  `KotORRanged_ion`
⚠️ **`combatPower` moved with the money, by the generator's own rule** — the four
droid kinds went 35/40/38/46 to 90/124/108/176. That is the roster's intent (a
kind is as dangerous as its kit) but it IS a difficulty change to droid raids,
and it is the one thing here somebody may want to argue with.
⏳ Live half is CHECK's: `ROLE_KINDS_ARMED_5_OF_5_1` in `queue/CHECK.md`.
