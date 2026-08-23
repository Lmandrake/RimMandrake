# Jawa wear robes and hoods, and Jawa exist in two places only
# BUILD, 2026-08-23, on the owner's two rulings

Owner 01:43: "I must insist that Jawa spawn entirely wearing robes and hoods. They can
have all the variants on those keywords you want, but please stick with that."
Owner 01:47: "Let's take the Jawa out of any faction except player and Trade Moot then..."

## 1. every Jawa-generating PawnKindDef now REQUIRES robe + hood
   ✅ Jawa_Colonist                  required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['IndustrialBasic']
   ✅ Jawa_Tribal_Scavenger          required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']
   ✅ Jawa_Tribal_Slinger            required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']
   ✅ Jawa_Tribal_Elder              required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']
   ✅ RimMandrakeJawa_Kind           required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']
   ✅ RimMandrake_JawaTribal         required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']
   ✅ Jawa_TradeMoot_Grunt           required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']
   ✅ Jawa_TradeMoot_Heavy           required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']
   ✅ Jawa_TradeMoot_Specialist      required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']
   ✅ Jawa_TradeMoot_Leader          required=['guy762_Robes_jawa', 'guy762_JawaHood']
      variants: ['SaV_apparel_jawa', 'ORHermit', 'KotORClothing_civilian_hooded']

## what was replaced, so it can be objected to
   Jawa_Tribal_Elder      had Apparel_TribalHeaddress + Apparel_PlateArmor (per the live
                          capture; the repo def carried none, so a patch was adding them)
   Jawa_Tribal_Scavenger  had Apparel_WarVeil
   RimMandrakeJawa_Kind   had apparelTags IndustrialBasic and NO required — this is the
                          def that could put a Jawa in jeans, and it is the player one
   Jawa_TradeMoot_*       required the robe but NOT the hood, all four

## 2. Jawa now exist in exactly two places
   Jawa_IndigenousTribes (the Trade Moot)  MandrakeJawa 1.0   KEPT
   PlayerColony / PlayerTribe kinds        MandrakeJawa       KEPT
   Jawa_HuttCartel                         MandrakeJawa 0.014 REMOVED

   Measured: those were the ONLY two FactionDefs in the whole 578-mod load set whose
   xenotypeChances named MandrakeJawa. No other faction ever generated one.

## the Jawa_Tribal_* kinds are Trade Moot kinds, NOT Deep Desert
   Their defaultFactionDef reads TribeCivil, which is a FALLBACK and misleading.
   Measured against pawnGroupMakers: all three are fielded by Jawa_IndigenousTribes
   (Combat comm 100, Peaceful comm 100, Trader comm 100) and by nothing else.
   ⇒ They stay Jawa. Removing them would have emptied the Trade Moot's own roster.
