# Warden mother art, 2026-10-03
- Searched: artpipe find warden/wardenmother (0 hits for her; Thrummel/Mireflit wardens unrelated), CSV rows existed, no Textures dir in Miasma.
- Queued via fill_queue (subset CSV of rows 1-2): RM_WardenMother_{south,east,north}, RM_WardenMother_Aged_{south,east,north} (pending/).
- Def edit: RM_WardenMother.xml gained LifeStageDef RM_WardenMotherElder (minAge 38 of lifeExpectancy 45) + 4th lifeStage with texPath .../WardenMother/WardenMotherAged.
- Not done: wiring PNGs (daemon not run yet; collect to Miasma/Textures/Things/Pawn/Animal/Miasma/WardenMother/WardenMother_{south,east,north}.png and WardenMotherAged_*), succession code reading the age.
