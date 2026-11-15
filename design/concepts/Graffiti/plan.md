# Graffiti: plan (Designer, stage 3)

Graffiti is built. The plan is proof, not construction, plus one new behaviour: the raider pressure he picked by card.

## structure and reuse
- Existing proof entry points reused as acceptance scenes: `validation.py` (spree_wall, spree_variety, wall_closeup, gallery,
  beauty_pair, breach_bias_toggle_flips) and `graffiti_v1_live_proof.py` clauses A2 to A7 (raid exit tags, sigil,
  going-over, hostile thought, scrub protection, player orders).
- The twelve validated must-show lines no component claims get their scenes from
  RIMMANDRAKE_CLAIM_GRAFFITI_MUST_SHOWS_TWELVE_LEFT_BARE (art_skill, own_fun, rereads, mockery, tribute and memorial, answer
  the wall, raid retaken, visitors, fights, temperament, settings, lived-in soak). Each scene names it as entry_point_item.
- New entry points outside those twelve: RIMMANDRAKE_SCRIPT_GRAFFITI_CORRIDOR_WALK_AND_WALL_LOSS_SCENES (his flagship
  corridor, wall loss, the walk).
- Start assertion "all 8 settings at shipped defaults": RIMMANDRAKE_CHECK_GRAFFITI_SITE_SETTINGS_SIX_OF_EIGHT (preflight
  checks 6 today; its acceptance test fails on the base).
- The one new behaviour: RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL (a per-faction record of standing
  raider marks, a letter naming faction and mark, raid points or timing pushed by a setting, lifted when the last mark goes).

## order
1. The site preflight (cheap, offline, unblocks every scene's start assertion).
2. The twelve claims, so modcheck stops refusing every Graffiti run and SteveDesktop stops recording INVALID jobs.
3. Raider pressure, with its offline kernel test and live scene together.
4. The corridor, wall loss and walk scenes; the walk needs the lived-in save from
   RIMMANDRAKE_WALK_GRAFFITI_LIVED_IN_WALL_WEEKS_NOT_MINUTES and step 3.
No instrument leaf: every leaf is measured by existing bridge reads (marks, thoughts, opinions, goodwill, letters, raid
points); the soak's mood sum is a read over those.

## risks
- The soak (stories_not_tax) is the one long live run; compressed at top speed, three in-game weeks. If it cannot finish
  on the full list, it is decomposed into a mark-count rate and a thought-sum per colonist, and says so.
- Raider pressure on raid size alone may be invisible: the letter carries the trace, so its look-target is asserted.
- Art-reading leaves (reads_at_play_zoom, punk_register, no_english, not_dirt, ugliness_visible) need a judge that did not
  make the art; each control plants a known-bad texture so the judge is shown able to refuse.

## the showcase set
1. spree_corridor, his pick (OWNER:1794728091811038301), revisit cheaply if it does not read.
2. social_wall: mockery, answer, temperament, visitors, own fun.
3. after_the_raid: exit tags, going-over, retaking the wall, the pressure and its lifting by scrub or weather.
4. devout_wall: sigils, scrub protection, paint dying with its wall.
Breach bias, the settings sweep and standing alone are covered by ordinary scripted checks (coverage_rest).
