## PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS

Owner card 2026-10-16: "Draw a few shared packs" (decided PACK_SPRITES_DECIDE_HAULERS_LOADED). Draw 3-4 generic
loaded-pack overlays shared across the packAnimal races, instead of one set per species (report:
`Transient/swanimals_pack_texture_report.md`: 79 missing `<bodyTexPath>Pack` paths, 3 facings each).

### Mechanism (from the report)
The engine derives `<body texPath>+"Pack"` (Graphic_Multi: north, east, south; no west) for every `packAnimal` race and
draws it only while the animal carries load. No def field names it, so a shared overlay is installed as a COPY of the
group's overlay at each missing path (or the pack node is patched per race; copies need no code). The overlay is drawn at
the body's own size, so each group's overlay must be a transparent canvas with the bags placed at the back/flank for that
body shape, readable at the group's smallest and largest drawSize.

### Survey (packAnimal=true, measured from src/ XML 2026-10-16: 54 race defs; 48 are the SWBestiary races)
Grouped by body shape (BodyDef leg/wing/shell parts):

- **A four-legged side-view quadruped, 39:** RSW_Bolotaur, RM_Aurrok, RM_Chorn, RM_Gennok, RM_Vaalok, RM_Vellak, RSW_Dalgo,
  RSW_Ronto, RSW_TelluroxRace, RM_Aveluthia, RSW_Bantha, RSW_Bordok, RSW_Gualaar, RSW_Jerba, RSW_Mudhorn, RSW_Nerf,
  RSW_Runyip, RM_Tirbak, RSW_Falumpaset, RSW_Jamel, RSW_TeeMuss, RSW_Maxolotl, RSW_Narglatch, RSW_TuskCat, RSW_Behemoth,
  RSW_Dactillion, RSW_Uvak (4 legs + wings), RSW_CorellianHound, RSW_Dewback, RSW_Fambaa, RSW_Eopie, RSW_KellDragon,
  RSW_Mastmot, RSW_Orray, RSW_IthorianReek, RSW_Reek, RSW_Shaak, RSW_Skalder, RSW_Varactyl.
  Sub-variants worth one pack if it does not fit: humped/hooved (Jamel, Tirbak, Falumpaset, TeeMuss) vs low long-bodied
  (CorellianHound, TuskCat, Narglatch, Maxolotl).
- **B biped, upright or striding, 6:** RSW_Blurrg, RSW_Brezak (winged), RSW_Kaadu, RSW_Kybuck, RSW_Tauntaun, RSW_Thranta (winged).
- **C six-legged shelled insect, 7:** RSW_HarvesterBeetle, RM_Moravatha, RSW_FoundryBeetle, RSW_Holcorobeus, RSW_RoyalRhino,
  RSW_LavaFlea, VAEWaste_Megatardi.
- **D low long body (larva/slug), 2:** RSW_Gelagrub, RSW_Sacapillar.

So 4 overlays: A (the bulk, 39), B, C, D. Missing paths per group: see the report's table (race -> path).
Existing Pack art that needs no new work: Behemoth, Ronto, Holcorobeus, Bantha `BanthaW_j`; Bantha Pack source copy for
BanthaR/V_* variants is a free copy (report section (a)).

### Order of work
1. Overlay A (quadruped saddlebags) first, then B, C, D. Canon-neutral generic gear: leather saddlebags and a roll, no
   franchise marks.
2. Show each overlay on a review sheet over 2-3 real bodies at true scale (sheet via `art_sheet.py --subjects ... --jobs`).
3. After his pick, install via `art install` to every missing path of the group (3 facings each); `*_Swimming` and `_j`
   juvenile bodies may be waived (not pack-eligible in practice).

Filed 2026-10-16 (design/RimMandrake/pack_overlays_commission_2026-10-16.json): artpipe jobs `packoverlay_quadruped_v1_{east,south,north}` (overlay A, quadruped).

NEXT: when `packoverlay_quadruped_v1` lands, check it, then commission overlays B, C, D (add rows to the same json) and build a review sheet over Bantha, Dewback and Reek bodies.
