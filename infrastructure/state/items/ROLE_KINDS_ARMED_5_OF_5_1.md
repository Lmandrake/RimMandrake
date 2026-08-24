## spec
Nine of the 48 could spawn bare. Fixed in the generator table and redeployed.
🔑 **The offline pass is now genuinely predictive rather than indicative**, because
it reproduces `StatWorker_MarketValue.CalculatedBaseMarketValue` for the Outer Rim
weapons, which declare no `MarketValue` and are priced from their recipe. Nothing
in the roster is UNMEASURED any more.
⚠️ **It is still a FLOOR.** The engine prices a `ThingStuffPair`, which adds STUFF
cost; the pass reads the unstuffed value. A stuffed weapon is dearer, never
cheaper, so a marginal kind fails in game before it fails offline. Every fixed
number was given headroom, but headroom is a judgement, not a proof.

## verify
spawn each of the 48 kinds **5 times** and read
`jawa/pawn_get` -> `pawns[0].equipment`.
🔴 **5/5 non-empty, for all 48. ONE SAMPLE IS NOT ENOUGH** —
`Jawa_Geonosian_Specialist` reached the original suspect list on a single bare
roll and is fine at 5/5.
⚠️ **FALSE PASS TO AVOID:** `jawa/pawn_gear` is a WRITER. It answers a read with
"Give a ThingDef.", and reading equipment off it reports every pawn as bare.

## criteria
no Jawa faction fields an unarmed raid.
🔴 **AND ONE THING TO ARGUE WITH RATHER THAN JUST VERIFY:** `combatPower` follows
the money by the generator's own rule, so the four **droid** kinds moved from
35/40/38/46 to **90/124/108/176**. Droid raids are now materially harder, because
the cheapest weapon their tag pool offers costs 982.5 and a kind that can hold it
is priced accordingly. That is the roster's stated intent, but it is a difficulty
change nobody explicitly asked for — **if it plays wrong, say so and DECIDE can
re-tier it; the fix is one number per row in the generator.**

## notes
**from:** BUILD, 2026-08-20. Offline half done; `weapon_affordability.py` reports
`always arms 48 · sometimes 0 · never 0 · no tags 0 · unmeasured 0`.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready

## MEASURED LIVE 2026-08-24 — true per kind, false per pawn
5 rolls each on the live map, all 49 roster kinds: **no kind is 0/5**, so the literal claim holds.
But **16 of 49 kinds roll bare at least once**, and **21 of 285 pawns spawned bare (7.4%)**.
Worst: `Jawa_Homestead_Heavy` **3 of 5 bare**; then `Jawa_Wildsteam_Grunt` and
`Jawa_Geonosian_Heavy` at 2 of 5.

🔑 Two causes, measured: **13 of the 21 carry a violence-disabling backstory**
(`EMPIRE_BLACKSTAR_ALWAYS_WILLING_1`) and **8 do not** (the `weaponMoney` roll). Fixing either alone
leaves bare pawns on the field. Evidence: `facts/roll_arm_harvest_2026-08-24.md` §1–2.
