# BLACKCRAGS_BEDAZZLE_SITTING_1 — the Abyss (asked as Black Crags; was Forsaken Crags) bedazzle sitting

Row 11 of `BAROQUE_BEDAZZLE_PROGRAM_1` — the last row. Opening authorized by
question card 2026-09-30 22:45 PDT (decision taken by question card). The
rename Forsaken Crags → Black Crags was owner-typed 2026-09-27 (program row 11)
and executes at this sitting, gated by the tile check.

Biome: `src/RimMandrake/Abyss/` (`RM_Abyss`), frozen twin `RUT_Abyss`, sheet
`design/Jawa/worldbuilding/biomes/abyss.md`, roster
`design/Jawa/worldbuilding/biomes/rosters/abyss.json`.

## Report (movements 1–2, done 2026-09-30)

`design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` —
what is there, rename census + tile gate, nine-mark scorecard (free 0/2/7),
roster fill (gharrek, durrgak, krizzak, etchcap), the turn-1 slate, and the
owner's first volley card (§6). GPT consult:
`Transient/bedazzle_gpt_enrich_2026-09-30/blackcrags.{prompt.md,md}`.

Findings that stand regardless of the volley:
- Tile gate (offline decode of the canonical save, dump 2026-10-01T01-12-26Z,
  probe RM_FloodedCanyon 44): `RM_ForsakenCrags` 0, `RUT_ForsakenCrags` 1,135 (old def names, as measured on the save),
  `AB_RockyCrags` 0. Live world UNMEASURED (game down). Same block shape as
  Cauldron's `RUT_PoisonForest`.
- `EMPIRE_PURSUIT_SURVEY_SHADOW_1`'s `surveyShadowBiomes` names only the donor
  `AB_RockyCrags`; exact `List<BiomeDef>.Contains` — the sensor shadow likely
  never fires on the campaign world. Correctness fix owed.
- `AA_Behemoth` (ghorrumak, the giant) and `GR_Nighthrumbo` (zhurrakor) are
  rostered here but wired into neither BiomeDef.
- `RSW_Cindermare`/`RSW_Skarnix` are invented (0 Wookieepedia hits), so Q11a
  puts them in `RM_` — card.

## spec

The four movements of the program item, applied to this biome:
1. Review — done (report above).
2. Roster fill — proposed (report §4); owner admits at the card.
3. Volley — four turns, fixed shape; ledger-note every ruling as it lands.
4. Ticket + commission — `BLACKCRAGS_RULED_CONTENT_1` +
   `BLACKCRAGS_MECHANICS_BUILD_1` for FOUNDRY, a `BLACKCRAGS_FULL_RENAME_1`
   (CAULDRON_FULL_RENAME_1 shape: tile gate recorded first), and artpipe jobs
   after checking `artpipe/done/` (12 `crags_*` creature facings and 7 flora
   `*_v1` are already done and unwired).

## criteria

- Review doc committed and pushed. ✅
- Volley completed (two full exchanges), every ruling on the ledger.
- Build items + rename ticket filed for FOUNDRY; art jobs queued.
- Sitting closes at ticket-out; art review stays on the art items.

## verify

`rimflow show BLACKCRAGS_BEDAZZLE_SITTING_1` lists the owner's volley rulings as
notes; the three child items exist; the review doc's §6 card is answered.

## Turn 1 rulings (2026-09-30)

See report §7. Rename to **the Abyss** (typed), executed by `ABYSS_FULL_RENAME_1`; spine = the Dark in full -> `ABYSS_DARK_BUILD_1`; hidden ship yes with probe droids -> `ABYSS_HIDDEN_SHIP_PROBES_1`; all four new creatures admitted -> `ABYSS_{GHARREK,DURRGAK,KRIZZAK,ETCHCAP}_BUILD_1`. The pursuit shadow list now names `RUT_Abyss` and `RM_Abyss`. Turn 2 owes card items 5-7.
