# KotORBandolierNorthFix — validation walk
subject: src/RimStarWars/KotORBandolierNorthFix  (packageId: mandrake.rsw.kotorbandoliernorthfix)
deps: guy762.MM.KotORCore (Star Wars KotOR Resources and Materials) — required, and this mod must loadAfter it (loose-file override race)
list: minimal+guy762.MM.KotORCore
status-hint: ships the missing north/northm worn-art for bandolier_chewbacca and bandolier_traveler (20 loose PNGs) so KotORCore's Graphic_Multi stops falling back to a 180°-mirrored south with the chest pouches drawn on the pawn's back.

## must be true
- Ships exactly 20 loose PNGs under Textures/SWApparel/Accessories/{bandolier_chewbacca,bandolier_traveler}/Apparel_{Male,Female,Thin,Fat,Hulk}_{north,northm}.png — no Defs, no Assemblies; the fix is pure art riding the donor's own wornGraphicPath.
- Declares loadAfter guy762.MM.KotORCore (About.xml) — required because the donor ships its textures loose too, and between two loose files at the same path RimWorld resolves by load order; placed earlier this mod would be invisibly overwritten.
- The two donor ThingDefs that use these paths are guy762_Accessory_chewiebandolier (texPath/wornGraphicPath SWApparel/Accessories/bandolier_chewbacca/Apparel) and guy762_Accessory_travelerbag (SWApparel/Accessories/bandolier_traveler/Apparel), both apparel.drawData.dataNorth.layer = 65 — read from the donor's own Apparel_SWAccessories.xml (workshop id 3254370945), not guessed.
- Each shipped `_north.png` has the same canvas size as the donor's matching `_south.png` and the same opaque-pixel count (alpha_count) — the build gate in Source/build_north.py refuses to write a file that fails either check, so a shipped file failing them on disk would mean the deployed copy diverged from what the gate approved.
- Each shipped `_north.png` carries at least one fully-opaque pixel (alpha channel max == 255) and each `_northm.png` is a solid (255,0,0,255) field at the donor's canvas size — the mask-tint convention Source/build_north.py enforces.
- No log line is possible for this defect class ("Failed to find any textures at" only fires when EVERY facing of a set is missing, and both sets already ship east+south) — so the only automatable proof is the file-level parity above, not a load-time message.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.kotorbandoliernorthfix" and no "Failed to find any textures at" naming bandolier_chewbacca or bandolier_traveler   # load-time; a hit here would mean the donor's own art broke, not this mod
2. [D] asset check: script (PIL) opens the deployed C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\KotORBandolierNorthFix\Textures\SWApparel\Accessories\bandolier_chewbacca\Apparel_Male_north.png against the donor's Apparel_Male_south.png at the same relative path (guy762.MM.KotORCore's own Textures folder) — confirms canvas size equal, alpha_count(north) == alpha_count(south), north alpha max == 255
3. [D] repeat check 2 for the remaining 8 body/set combinations (Female, Thin, Fat, Hulk × chewbacca, traveler) — 10 pairs total including Male
4. [D] asset check: each of the 10 `_northm.png` files is uniform (255,0,0,255) across its full canvas and matches its `_north.png` sibling's size
5. [B] jawa/get_def {defType: "ThingDef", defName: "guy762_Accessory_chewiebandolier"} → apparel.wornGraphicPath still reads SWApparel/Accessories/bandolier_chewbacca/Apparel and apparel.drawData.dataNorth.layer still reads 65 — confirms the donor def this mod targets hasn't drifted since About.xml was written
6. [B] jawa/get_def {defType: "ThingDef", defName: "guy762_Accessory_travelerbag"} → same check for wornGraphicPath SWApparel/Accessories/bandolier_traveler/Apparel
X. [S] (human pass) spawn a pawn wearing guy762_Accessory_chewiebandolier (or _travelerbag), rotate to face north, and confirm bare leather renders on the back instead of the chest pouches
