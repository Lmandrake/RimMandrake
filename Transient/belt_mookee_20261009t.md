# Mookee trade animal identify (2026-10-09)

Game: UP on the owner's colony map (tile 80070, biome RM_TheRot, tick 84998, 1 map). Not a throwaway map.

## Mookee
- Pawn `Dewback211868`, name "Mookee", race defName `Dewback` (donor: mlie.starwarsanimalcollection, NOT our RSW_Dewback), kindDef `Dewback`, faction PlayerColony, cell (64,175).
- Donor art. Pawn-level graphic reads BadTexture (pawns render via render tree, thing_graphic is uninformative); donor texPath family `swanimals/Dewback/...` (RSW_Dewback copy uses `swanimals/Dewback/DewbackW`).
- It sits in a hand-staged lineup at z=175/184, x=64..94: donor/RSW pairs, all PlayerColony-owned (not a trader caravan). No trader caravans/visitors exist on the map.

## Pack/trade animals present (id, name, race=kindDef)
z=175: Dewback211868 Mookee Dewback; RSW_Dewback211869 Wanga; Ronto211870 Achuta Ronto; RSW_Ronto211871 Buyer Beware; Nuna211872 Mynock Nuna; RSW_Nuna211873 Majority Shareholder.
z=184: GR_Spidercat Jailbird; AA_Thunderox Herman; VFEI2_Megathrips Yulian; Dalgo Malastare; Iriaz Bargon; RSW_Kreetle Known Issue.
Elsewhere (z~40-47, x128-157): Dewback Chopper, RSW_Dewback Only Driven Once, Ronto Deetoo, RSW_Ronto Threepio, Nuna Luggabeast, RSW_Nuna Head Of Security.
Names are from Jawa_PetNames.xml; unprefixed Dewback/Ronto/Nuna/Dalgo/Iriaz are donor defs.

## Verdict
"Mookee" is a Dewback with the donor def (not RSW_), i.e. donor art. Fix is wiring/replacing donor-def trade animals with RSW_ twins, not renaming. Screenshot read: painterly pack animals visible; no cartoon seen at that crop (RSW art), donor ones were not individually framed.
Screenshot: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\mookee_lineup__cell_rect.png`
