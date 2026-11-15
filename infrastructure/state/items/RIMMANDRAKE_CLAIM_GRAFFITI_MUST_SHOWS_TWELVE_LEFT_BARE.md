# RIMMANDRAKE_CLAIM_GRAFFITI_MUST_SHOWS_TWELVE_LEFT_BARE

Graffiti's validated north star (`design/validation_walks/RimMandrake/Graffiti.md`) has 12 must-show lines that no
validation component claims (`shows=`), so modcheck refuses every Graffiti run on its visual floor. The lines came in
with commit b967d9e9cb (2026-11-08, "Graffiti: land the Artisan loop's mod (ralph/graffiti fd650c5589)"). The filler
sent the refused selection to SteveDesktop 3 times (J20261113T174408Z-b5a782, J20261114T052458Z-bcacdc,
J20261114T160304Z-c97383), each dying INVALID after a deploy. Class (a), the test itself
(RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED census). Graffiti is unwired from the filler
(`src/RimMandrake/Utils/testq/wired_mods.json`) until this closes; re-wire it in the same change.

Unclaimed: art_skill_goes_into_the_art, each_takes_it_like_themselves, fights_have_people_and_reasons,
making_a_mark_is_its_own_fun, mockery_changes_regard, pawns_answer_the_wall, raid_mark_troubles_until_retaken,
rereads_affect_at_most_daily, stands_alone_and_obeys_settings, stories_not_a_tax, tribute_and_memorial_mean_it,
visitors_read_without_recharging.

## fix

Give each line a component in `src/RimMandrake/Graffiti/validation.py` that really tests it (`shows=<id>`). Removing or
un-validating a must-show line is loosening a north-star bar: the owner's call, never this item's.

## acceptance test

    python3 src/RimMandrake/Utils/modcheck/cli.py run Graffiti --chains forced_paint_job,mental_break_spree,spree_wall --preview

exits 0 (today: exit 2, `REFUSED: validated must-show lines no component claims: ...`, watched failing 2026-11-14), and
`python3 src/RimMandrake/Utils/testq/coverage.py check` passes with Graffiti wired again.
