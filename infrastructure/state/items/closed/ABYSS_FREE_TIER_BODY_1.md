# ABYSS_FREE_TIER_BODY_1 — the Abyss's free-tier body: our own labels, the donor cast wired to finished art, flora guarded or owned

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §5 #12 (the movement-4 pre-ticket, "owed whatever the volley rules") and §1. Cast bible: `design/Jawa/worldbuilding/biomes/abyss_cast_bible_2026-10-01.md` §1 and §4E. Sitting: `BLACKCRAGS_BEDAZZLE_SITTING_1`. Rule: every mod ships Mod Settings; the free `RM_` tier must be rich enough to stand alone (Q11a).

## spec

The ticket-out audit found these §5 #12 pre-ticket lines carried by no item. This is the Abyss's slice of them. The port machinery itself (how a donor def becomes ours) belongs to `DONOR_DEFS_PORT_TO_OURS_1`; do not fork it, use it.

1. **Free-tier labels.** The label patch `Abyss_Rename.xml` is Utinni-only, so free players see the donor's English names (nightling, darkbeast...). Give the free tier the same invented labels (vrakk, ulkhorr, kessik, ...) in `mandrake.rm.biomes`, either on our ported defs or by a free-tier label patch gated per def.
2. **Wire the 12 finished donor-cast art sets** (`crags_<label>_{south,east,north}` in `infrastructure/artpipe/done/` + `_artsrc/`: vrakk, dhukk, hulggarok, zekkra, kessik, brekkugar, korrag, bhoruk, gruzz, shekkur, ulkhorr, thrizzik) onto the Abyss's ported defs as `DONOR_DEFS_PORT_TO_OURS_1` lands them. Not `crags_ghorrumak_*`/`crags_zhurrakor_*`: those two are superseded by fresh art under `ABYSS_DONOR_BEASTS_FREED_1` (owner: fully regenerate).
3. **The dusk rat's art redo** (owner "replace" ruling, `port_alphaanimals_2026-09-20.decisions.json`): its job is on the Abyss art list (commission waits for the owner); wire it when it lands.
4. **The 8 flora rows** (`AB_GlowingGrass`, `AB_ToxicGamma`, `AB_GiantGamma`, `AB_WildRadagast`, `AG_Gamma`, `AB_GiantStikehr`, `AG_Septimum`, `AB_GiantSeptimum`) carry no `MayRequire`. Guard them now (a `<li>`-free shorthand row takes `MayRequire` on the element), then own them through the port; finished redraws exist (`giantgamma_v1`, `giantstikehr_v1`, `septimum_v1`, `giantseptimum_v1` and siblings in `done/`, owner "replace with our own def and our own art", `port_tail_2026-09-20.decisions.json`).
5. **Weather labels.** Etchfall and Witchfire are names on donor weathers (`AB_ForsakenRainyNight`, `AB_ForsakenThunderstorm`). The free tier owes its own WeatherDefs or labels for them, because `ABYSS_DARK_BUILD_1` (storm call) and `ABYSS_ETCHFALL_BUILD_1` key on them.
6. **About.xml** still says the Forsakens "are campaign plot content and stay in Utinni entirely" (around line 42). The cryptid is now the Nhaleth in every tier (`ABYSS_FREE_CRYPTID_1`); correct the line.
7. **Paint list.** Add `RM_Abyss` to the paint list for `BIOME_PAINT_ONCE_AT_THE_END_1`. Its 0 tiles is the expected state, not a defect.

## criteria

- A free-tier game shows our invented label on every Abyss creature; no donor English name remains player-visible.
- The 12 done `crags_*` sets render on their ported defs; no new art job spent on any of them.
- Every flora row is guarded or owned; none unguarded on a donor.
- Etchfall and Witchfire exist as names the free tier owns.
- About.xml carries no Forsakens line for the cryptid.

## verify

Offline build + selftests + `validate_patch.py`; a live look is a joint session.
