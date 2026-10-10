# WEEPINGSTONES_SETTLED_FOLLOWUPS_1 — Weeping Stones work that waits on a creature being settled

Source: owner's rulings on `Transient/biome_ffar/weepingstones_sheet_2026-10-05.decisions.json` (2026-10-10).
Each line below fires once the named creature's redraw is PICKED by him (a letter on a review sheet, or its render live).

## Vellak description (his note, verbatim: "Redo description after art to conform.")
- RM_Vellak redraw `enact_3df263b9_vellak_v2_*` (based on his (b), pending). NEXT: once he picks a Vellak render, rewrite
  RM_Vellak's description to match the picked art ("more alien ... furred snake for a neck/head. Sometimes used for pack
  animals"), then `art.py enact <decisions> --mark-done RM_Vellak --evidence <sha>`.

## Catches (his note: "Make it look like a dead one of these. Of course generate AFTER the source is settled, blocking until")
`art.py enact` now files these itself once the creature is settled (catch rows wait; the source's picked picture is
attached as reference). Early renders were withdrawn to `D:\Luke\dev\_artpipe\_withdrawn\`.
- RM_HulduCatch — waits on RM_Huldu (`enact_huldu_from_c_v2_*` done, awaiting his pick).
- RM_LoomuCatch — waits on RM_Loomu (`enact_34cbe6a2_loomu_v2_*` pending).
- RM_MurrinCatch — waits on RM_Murrin (`enact_e6d931f4_murrin_v2_*` pending).
- RM_SkarrinCatch — waits on RM_Skarrin (`enact_3c182127_skarrin_v1_*` done, awaiting his pick).
- RM_VizhikCatch (fan eel catch) — waits on RM_Vizhik (`enact_aff7b795_vizhik_v2_*` pending).
- RM_IvvolCatch, RM_KarrekCatch — creatures settled (his pick C); re-filed with that art as reference
  (`enact_5dc38971_ivvolcatch_v1_*`, `enact_ef0ad81f_karrekcatch_v1_*`).
NEXT: after each creature pick, run `art.py enact <decisions> --apply` — it files the waiting catch.

## Huldu fur (his note: "Very beautiful fur that is a trading commodity")
Decision taken by question card 2026-10-10: "add it". DONE at `0de0868678a2`: `RM_Leather_Huldu` ("huldu fur",
MarketValue 9, LeatherBase) in `WeepingStones/Defs/ThingDefs_Items/RM_HulduFur.xml`, set as RM_Huldu's `leatherDef`.
Uses the shared vanilla leather texture tinted brown for now. Icon job `rm_huldufur_icon_v1` queued (reference: the
huldu render), target texPath `Things/Item/Resource/RM_LeatherHuldu`. NEXT: when it is done, install it and add the
`<texPath>` to RM_Leather_Huldu's graphicData.

## Agent-added scopes: owner KEPT all three
Decision taken by question card 2026-10-10: the new RM_Colossia creature, the "korrim" spice + recipe change, and the
global vanilla reeds repoint all STAND as the agent added them.
