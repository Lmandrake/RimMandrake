# RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST

## spec

Pyrelands 0.1.0: the four things only he can give, all at his Pyrelands walk (act 3) or as his art act (act 2). Merged by
the ticket sweep of 2026-11-22 (RIMMANDRAKE_SWEEP_PYRELANDS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE) from the items
named under each part; each part is done when he has looked or picked and the pick is carried out.

1. **Ullai at play zoom (his kept art).** From RIMMANDRAKE_JUDGE_PYRE_ULLAI_HERD_READS_AS_GREY_RUBBLE and
   RIMMANDRAKE_CARD_ULLAI_REDRAW_KEPT_ART_FAILS_AT_DEFAULT_ZOOM. Visit 5 (ArchBig, 2026-11-22) saw the herd as small grey
   blobs and sticks at play zoom; evidence `design/concepts/Pyrelands/version/in_game/visit_5/screenshots/herd_look__ullai_lying_crop.jpg`,
   `herd_look__rimbridge_20261122_064207__cell_rect.jpg`, `design/concepts/Pyrelands/version/evidence/ullai_readability/`.
   Options from the judge run: (a) redraw wider north and south views, (b) raise drawSize, (c) keep.
   Owner, recorded 2026-11-22 about 1:00 PM PST (OWNER note 21:09Z): "he wants the in-game look at the ullai herd before
   the card. Stage the ullai station from PYRELANDS_0.1.0_VISIT5_WALK_FULL on ArchBig after his FlowWorks and Gimme Some
   Slack walks; card after he has looked."
2. **Fire-hawk east view S (his kept art).** From RIMMASTER_INSTALL_FIREHAWK_S_EAST_WAITS_ON_HIS_LOOK. Flip-book S (A's
   north and south, east rebuilt from D with eyes level and one belly edit), a naive judge passed it after two fixes; page
   `D:\ClaudeWork\rimmandrake\firehawk_replay\page2\index.html`, frames `D:\ClaudeWork\rimmandrake\firehawk_replay\fix2\cand\S`.
   Install only after his look, through `art.py install` (it refuses kept art). Flight is never shown live without him.
3. **Ash footprints and the hover label.** From RIMMASTER_FIX_ASH_FOOTPRINTS_AND_SAND_LABEL_AFTER_CLOSE. He saw live on
   2026-11-08 about 11:00 AM PST that footprints never showed in ash and the hover read 'Windswept sand'. Fixed in
   38d347bfc2 (landed on main in 8fb9f7f2b6): darker ash prints, buryDepth 0.3, hover "Ash"; offline check T_TRACKS
   (`src/RimMandrake/Utils/selftest_pyrelands_track_contrast.py`) PASS. Owner, 2026-11-08 (OWNER note 2026-11-09T03:44Z):
   "We can check the Pyrelands footprints on Wednesday." Show him one walked path in ash and the hover at the walk.
4. **The flamefang danger.** From RIMMANDRAKE_CARD_FLAMEFANG_ONE_BITE_KILLS_UNTENDED_HIS_DANGER_CALL (a card promised to him
   at 12:19 PM PST 2026-11-21) and RIMMANDRAKE_WEIGH_PYRE_TWO_FLAMEFANG_BITES_KILL_UNTENDED. Visit 3 saw one untended bite
   kill a healthy colonist by day 2. Since 11fca75b4bd1 (RIMMANDRAKE_TUNE_PYRE_FLAMEFANG_BITE_KILLS_BEFORE_IMMUNITY) one
   untended bite peaks at 0.64 of lethal (worst 0.79) and two untended bites can still kill; sc_flamefang_venom PASS in
   visit 5. The card asks: is that the danger he wants (one bite survivable untended, two not)? Bring it after his walk.

## Acceptance test

none, each part is his look or pick (five acts 2 and 3).
