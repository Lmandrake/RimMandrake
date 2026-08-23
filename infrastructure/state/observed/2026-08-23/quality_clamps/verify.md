# forceWeaponQuality and the quality clamps — BUILD, 2026-08-23

The last of the four dead levers from `faction_equipment_clusters.md` PART 3 item 4. The
per-faction clamps were specified in `faction_equipment_guidance.md`'s table and never built.

## 🔴 THE DESIGN ASKS FOR MIN/MAX; THE FIELD DOES NOT DO THAT

`forceWeaponQuality` forces an **EXACT** quality — it is not a floor or a ceiling. Measured on
PawnKindDef, only 2 of 1737 kinds in the whole 578-mod set use it. The fields that DO clamp:

    itemQuality             1737 kinds   the centre of the gear roll (default Normal)
    forceNormalGearQuality  1737         hard-forces Normal
    minApparelQuality       1737         apparel floor
    maxApparelQuality       1737         apparel ceiling
    forceWeaponQuality         2         EXACT weapon quality

⇒ The design's *"min Excellent"* and *"max Poor→Normal"* were mapped onto what exists:
`forceWeaponQuality` for weapons where the faction's character is a single consistent
standard, `min/maxApparelQuality` for the apparel clamps, and `itemQuality` for the centre.

## applied, 32 kinds

| faction | weapons | apparel | why (from the design) |
|---|---|---|---|
| **Helix** | force **Excellent** | min Excellent | *"few and perfect. No waste, no spares, nothing improvised"* |
| **Wildsteam** | force **Good** | min Good | *"min Good — few weapons, each old and well-made"* |
| **Deepwater** | force **Good** | min Good | *"min Good"* — sealed suits, because failure drowns you |
| **Junkers** | force **Poor** | ⛔ **UNCLAMPED** | *"max Awful→Poor on weapons; armour unclamped"* |
| **Trade Moot** | force **Poor** | max Normal | *"max Poor→Normal"*, the tightest clamp of any faction |
| **Deep Desert** | — | max Normal | *"max Normal"*; no weapon clamp, a scavenged rifle is what they found |
| **Homestead** | — | max Good | *"max Good"* |
| **Empire** | already `forceNormalGearQuality` | — | *"uniformity is the point"* |
| **Hutt**, **Blackstar** | ⛔ **none, deliberately** | ⛔ none | *"wildly uneven by design"* / *"mismatched on purpose"* |

⭐ **The Junker asymmetry is the faction in two fields.** Weapons forced Poor, armour left
completely unclamped — *the armour was cut off a body and the gun was not.* Do not "finish"
the Junker row by adding an apparel clamp; its absence is the design.

⭐ **And the Geonosian row is its mirror**, already built: apparelMoney 60~240 against
weaponMoney up to 1800. The drone is the expendable part.

## ⚠️ what looked wrong and is NOT
Every faction reads MIXED on `itemQuality` because **the Leader carries a better value** —
Empire Leader Excellent, Hutt and Junkers Leaders Masterwork. That is correct: the clamp
describes the rank and file, and a boss is allowed better.

Two that specifically survive scrutiny:
- `Jawa_Junkers_Leader` itemQuality **Masterwork** looks like it contradicts the Junker clamp.
  It does not: `forceWeaponQuality Poor` still governs his WEAPON, and the design says his
  armour is unclamped. A Junker boss in the best-looted suit on the planet is the character.
- `Jawa_Empire_Leader` lacks `forceNormalGearQuality`. Also correct — uniformity is for the
  troops; the officer is the exception that makes the uniformity legible.

## all four dead levers are now built
`inventoryOptions` ✅ · `apparelColor` ✅ · `apparelDisallowTags` ✅ (Empire) · `forceWeaponQuality` ✅

⚠️ `apparelDisallowTags` exists only on the four Empire kinds, where the owner's stormtrooper
requirement demanded it. The design's wider taboo list — a Tusken never wearing Imperial
plate, for instance — is still unbuilt for the other eleven factions.
