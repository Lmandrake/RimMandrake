# Donor pack-animal art (2026-10-10, FOUNDRY helper, offline)

## Dewback verification (donor mlie.starwarsanimalcollection, workshop 3497316713, Races_Animal_SW.xml)
- Donor PawnKindDef Dewback: lifeStages bodyGraphicData texPath `swanimals/Dewback/Dewback` (what Dewback_ArtFold.xml repointed: VERIFIED real, value-matched).
- GAP FOUND: `alternateGraphicChance 0.8` with six alternateGraphics at `swanimals/Dewback/DewbackW` (donor art, in the AssetBundle, never overridden by the old mod). 80 percent of donor dewbacks, and of our own RSW_Dewback (it copies the same six rows), drew donor art. That is the cartoon Mookee.
- FIX: Dewback_ArtFold.xml gets a second value-matched op DewbackW -> painted set; RSW_Dewback.xml edited in place; manifest row gets a second group. art_fold_check: 60 creatures, 0 red. donor_plain_ports_check: 7 ports, 0 failures.
- Unverified (needs game): that the painted set's blank mask leaves the six tint colours inert.

## Census of the 16 donor pack races with no RSW_ port (per MOOKEE item)
Painted art / patch exists: Gualaar (ArtFold already), Tauntaun (Tauntaun_CanonArt.xml, lifeStages only), Behemoth (BehemothArtUpres patch, 512px redraw).
Ledger-bound variants only (not wired): IthorianReek (3), Reek (4).
No painted art anywhere (artpipe_state find, 0 bound): Aiwha, Bordok, Brezak, CorellianHound, HarvesterBeetle, Kaadu, KellDragon, Mastmot, Narglatch, Thranta, TuskCat.
No art queued: it is not shown that any of these are trader stock, and the item says no art before the species is known. Tauntaun/Behemoth alternateGraphics were not audited for the same donor-path gap as Dewback.
