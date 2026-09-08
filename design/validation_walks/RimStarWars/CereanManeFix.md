# CereanManeFix — validation walk
subject: src/RimStarWars/CereanManeFix  (packageId: mandrake.rsw.cereanmanefix)
deps: Neronix17.OuterRim.GalacticDiversity (Outer Rim - Galactic Diversity) — required
list: minimal+Neronix17.OuterRim.GalacticDiversity
status-hint: replaces the fully-transparent OuterRim/Hairs/Cerean/CereanMane_south.png so Ceans wearing HairDef OuterRim_CereanMane stop rendering bald from the front (south) view.

## must be true
- Ships exactly one loose PNG at Textures/OuterRim/Hairs/Cerean/CereanMane_south.png, no Defs, no code.
- Declares no loadAfter (deliberate — on 1.6 the donor serves this art from an AssetBundle via LoadFolders.xml's Common/ folder, and a loose file always wins over a bundled asset regardless of load order).
- The shipped PNG is 512x512 and carries non-zero alpha (the donor's file at the same path, inside its AssetBundle, is 512x512 with alpha maximum 0).
- HairDef OuterRim_CereanMane (owned by Outer Rim - Galactic Diversity, Hairs_Cerean.xml line 37) still resolves with texPath OuterRim/Hairs/Cerean/CereanMane.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.cereanmanefix"   # load-time
2. [D] asset check: script (PIL, same pattern as Source/draw_mane_south.py) opens the deployed .../CereanManeFix/Textures/OuterRim/Hairs/Cerean/CereanMane_south.png; confirms canvas 512x512 and max alpha > 0
3. [B] jawa/get_def {defType: "HairDef", defName: "OuterRim_CereanMane"} resolves and its texPath field reads OuterRim/Hairs/Cerean/CereanMane — confirms the donor mod that owns this def is present and its path is unchanged
X. [S] (human pass) put a Cerean pawn wearing the Cerean mane hairstyle on the map, view from the south/front, and confirm the crest renders instead of a bald scalp
