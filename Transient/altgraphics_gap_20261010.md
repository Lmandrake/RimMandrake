# altgraphics gap sweep 2026-10-10 (FOUNDRY helper, offline)

Method: for every art_fold_manifest row with a donor, parse the donor's PawnKindDefs (workshop + Mods via /mnt/c) that name a folded texPath and list every other texPath (alternateGraphics, stages, male/female, dessicated, swimming).

## Gaps found and fixed (alternateGraphics, same shape as Dewback/DewbackW)
- Tauntaun: six alternateGraphics rows (chance 0.8) at swanimals/Tauntaun/Tauntaun were not reached by the index-based stage patch -> value op added to Tauntaun_CanonArt.xml; new manifest row.
- BloodShrimp (AA_BloodShrimp2/3), Frostmite (AA_FrostMite2/3), RaptorShrimp (AA_RaptorShrimp2/3): colour-variant alternates, repointed to the painted main set.
- Lockjaw: alternate AA_Lockjaw (1 of 3, chance 1) was donor art; repointed to painted AA_Lockjaw2 (no painted AA_Lockjaw exists; owner may want a dedicated one).

## Clean
- Behemoth: all four stage slots (m, f, dessicated) covered by BehemothArtUpres; no alternateGraphics. Pack overlay art is still the donor 256px extraction (noted in that patch).
- Gualaar: only Gualaar + Dessicated; covered.

## Not fixable: no painted art
- Reek and IthorianReek (donor races): adult swanimals/Reek/Reek and swanimals/IthorianReek/IthorianReek have NO painted art. The "4 / 3 bound" ledger hits are the donor's own Reek_j (calf) textures extracted into SWBestiary, not paintings. Only IridonianReek is painted, and it already sits at the donor's own path. Nothing to wire.

## Left as is (not alternateGraphics, no painted counterpart)
Baby/juvenile and swimming stages: Silooth_j, Fambaa_j/_Swimming/_j_Swimming, Kreetle_j, Dragonsnake_Swimming, Ollopom_Swimming, ShadowCharger/Thunderox _baby and _female, Rimclaw BabyRimclaw, Visceral/Bulwark. Dessicated corpses everywhere. These were never painted by the old override mods; repointing a calf to adult art would be wrong.
