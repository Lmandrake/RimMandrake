# Feverwood sheet: ruled art install (helper, 2026-10-07)
Source: Transient/biome_ffar/feverwood_sheet_2026-10-05.decisions.json (md5 ac9f834f..., copy in infrastructure/state/art_rulings/2026-10-07_feverwood_sheet_2026-10-05.decisions.json)

- ingest (art.py ingest --defer-redo-jobs): 77 rulings, 33 rejected-ingame records, 7 purges done, 0 purge refused (none live).
- Installed (via ledger ruling ids): RM_Claithe B (plant, FeverWood), Plant_JoganTree_Wild B (UtinniPatches swplants/JoganTree/JoganTreeA.png),
  RM_Skellick B (S/E/N, FeverWood), RM_Ollareth B and RM_Vaulm B (S/E/N set added; defs RM_SapSuckerGuild.xml graphicClass Graphic_Single -> Graphic_Multi, 3 life stages each; old single PNGs left in place, unused),
  VFEI2_Megathrips B (S/E/N, new donor-path override mod src/RimUtinni/MegathripsArtOverride, loadAfter oskarpotocki.vfe.insectoid2, ThermadonArtOverride pattern).
- Already current (his pick = art in game): Plant_HydenockTree_Wild A, RM_GiantLeaf, RM_Grolth, RM_Halquin, RM_Maulith, RM_Nubrith, RM_Ossagrel, RM_Plennith, RM_Seepril, RM_Silloch (all A). Fambaa D/E/F picks inside the redo row are already in game (SWBestiary).
- REFUSED / not done: RM_Chellow B (render has north+south only, no east; his note asks to add East) - regen job, not install.
  RM_Cistrel pick B (_byname) sits in a redo row - left to regen. Halquin/Maulith "picks _byname B" ruled as variant B kept, A stays live (decision A).
- Redo, hold, renames, descriptions, variants-only notes: not touched.
