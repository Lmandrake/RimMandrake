# ARTPIPE_FACING_COHERENCE_1 S4 backlog audit - 2026-10-09 (BENCH helper, offline)

Method: `Transient/facing_coherence_scan.py` (offline: sha/date from art ledger, N~E / N~S silhouette+luma clone test,
owner keep/redo by sha) + contact sheets (`Transient/facing_coherence_sheet.py`) that I LOOKED at. No LLM judge
(item 2026-09-20: it is not a gate), no codex meter touched, nothing filed or queued.

## Numbers
- Live multi-facing sets (N+S+E, src/**/Textures, masks excluded): **1716** (16 unreadable/empty facing).
- Donor-rooted mods (SWBestiary, StarWarsRaces, Droidworks, Armoury, StarWarsPatches, DesertVehicleReskin) are
  excluded as not-our-art; their pre-stamp/clone flags (~330 sets, mostly Armoury gear where N=S is legitimate) are UNJUDGED.
- Our-mod creature/pawn sets: 358. Pre-stamp (art-ledger date < 2026-09-14): 19 in our mods. Pre-stamp does NOT predict a
  violation: all 12 SeaBeasts (2026-09-02) look correct (N rear-from-above, S face, E profile).
- Looked at: 26 candidates (pre-stamp or clone flag) + 24 random post-stamp/pre-derive creature sets + top-12 N~E clones = ~60 sets.
  Base rate of real violations among random sample: ~0-2 of 24 (marginal only).

## Violators
1. **RM_Dredgel** (TheSump) - N, S, E are byte-identical front-facing images. Real violation.
   NOT a new debt: owner ruled **redo** 2026-10-06 ("I like the image, not make it go all the different directions properly"),
   and derived jobs `thesump_Dredgel_v2_north/south` are already DONE in artpipe `done/` (derive_from RM_Dredgel_south).
   Live files are still the old ones -> owed: install/review of the v2 pair, not a new regen.
2. Marginal, owner look (no keep ruling, no rows prepared - I would not call them violators):
   - `RM_Loomma` (Stillsand/neighbours) N~E~S all near-identical dome views (ne 0.85, ns 0.90).
   - `RM_Agaripod` (AA_Agaripod) N reads as a side/3-4 view like E.
   - `GR_Mantistanis` S is top-down (known since 2026-09-17).
   - `RM_Karrash` N shows eye-stalks from above; arguably fine.
3. Placeholder, KEEP-ruled: `RM_Murrelith`, `RM_Thavrik` (FeverWood birds) are flat solid-colour squares, N=S=E bytes.
   Owner keep ruling exists (trust=ruled) -> NOT queued; flagged for him in case keep was of the placeholder only.

## Clean / by design (not violations)
- N==S symmetric buildings: PyrinthBrazier, RSW_BactaTank(+Shell). Faceless radial body plans (Duumma, Dunejelly, Hessal,
  Ribbonwhip, LivingBolt, Titanoslime, Orruhmu, Gawpsack, Thollim, Karrimeth) show N~E/S similarity because no face exists.
- Pre-stamp sets with owner KEEP (sha match): ElderSando, SiltLamprey, RustNipper, GrippingTerror, Reefback, Gristle, AA_BloodShrimp.

## Rows
**None prepared.** The only definite violator already has done v2 renders; the rest are marginal and need his eyes first.
Contact sheets (scratch, regenerate with the scripts): sets listed above.
## Caveats
Art-ledger `date` is the first-seen date of those bytes, not necessarily generation time. Heuristic misses a N that is a
distinct image of a creature facing camera (face visible); only looking finds that, and only ~60 sets were looked at.
