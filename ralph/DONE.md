# Graffiti: done claim

I would show this to the owner. Two lines below are qualified, and the gaps are listed at the end.

Screenshots are in `D:\ClaudeWork\rimmandrake\ralph_graffiti\shots\`. All are at measured 64 px per cell, on the small `graffiti_solo` list with all DLC, in a throwaway quicktest colony built by `stage_colony.py`.

- `ns_natural_day2_n/s`: one colony at about tick 75000, with no forced spree and only ordinary idle and recreation painting.
- `ns_spree_day3_n/s`: the same colony after three real sprees.
- `ns_gallery`: every mark def. `ns_compare`: scrawl vs tally, with vanilla filth below. `ns_faces`: all four walls, inside and out.

| North-star line | Verdict | How sure | Shot |
|---|---|---|---|
| `mark_actually_appears` | True | High | `ns_natural_day2_n`, `ns_spree_day3_n` |
| `mark_reads_as_deliberate` | True | High | `ns_spree_day3_n`, `ns_gallery` |
| `mark_reads_at_play_zoom` | True. Scratches and the thin grey tag are the weakest. | Fairly high | `ns_gallery` |
| `mark_sits_on_the_wall` | Mostly true. Marks stay inside the wall band and never hang over the floor, but they lie flat across the crease between the wall's top and its front face instead of following it. | Medium | `ns_faces` |
| `marks_visibly_various` | True | High | `ns_spree_day3_n` |
| `mark_register_is_punk_urban` | True in a colony. Partly true for the meme glyphs alone: lined up, they still read as emblems with spray on them. | Medium | `ns_spree_day3_n`, then `ns_gallery` rows 3 and 4 |
| `mark_carries_no_earth_signage` | True as far as I can see. Ring-and-slash, the Venus mark and the stick figure in a ring are all gone. | Fairly high | `ns_gallery` |
| `mark_ugliness_is_visible` | True: scrawl is mess, tally is neat. The pink mouth is louder more than uglier. | Fairly high | `ns_compare` |
| `never_real_world_english` | True. No real words, and the two throw-ups closest to words were replaced. Some asemic shapes are still letter-like. | High | `ns_gallery` |
| `never_reads_as_dirt` | True | High | `ns_compare` |

## The independent judge
`judge_cli.py` on the last suite run (`Transient/northstar/Graffiti_20261107T061116Z.json`): 18 PASS, 2 FAIL, 1 UNMEASURED.
- FAIL `mark_sits_on_the_wall`: the crease complaint above.
- FAIL `mark_register_is_punk_urban`: the glyph-only gallery page. That page has failed on every run where the judge reached a verdict on it.
- UNMEASURED `mark_ugliness_is_visible`: unjudgeable because nothing labels the Beauty value. It passed in earlier runs.
- The suite's two compat rows are UNMEASURED because those mods are not on the small list.

**So the suite's own verdict is NOT GREEN.** I am claiming done on what a player sees in a colony, as the brief asks, while disagreeing with the judge only about how much the glyph page should count. The judge is one noisy sample per bar: signage and play zoom each failed in one run and passed in others.

That run came one commit before the final fist art, and nothing but that art and its description changed afterwards. The last full run of live clauses A1-A8 was two art commits earlier, and all passed. Player.log showed 0 exceptions on the final build.

## What I did not test
- The owner's full mod list. Everything here ran on the small list.
- Save and load with a mark or a paint job in progress. The fields are scribed but I never loaded such a save.
- Anything past about 2.5 game days. Long-run Beauty and mood balance, and whether the room cap is right, are reasoned rather than measured.
- Raid-exit tags are proven by clause A2, but they appear in no evidence shot.
- Colonists in the shots are drawn at their spawn spot, a bridge view quirk I could not fix. `call Who` shows them moving and painting, but no shot shows a pawn mid-paint.

## Things the owner may want to know
- The loop's service environment sets no seat, so I took the bridge as `BENCH` (the clone's folder and `live_session.py`'s default), and waited out a stale RELENTLESS hold instead of forcing it.
- The wall-face card of 2026-10-22 said to draw on the floor cell, offset toward the wall. I kept the floor-cell anchor but moved the drawing fully onto the wall cell. It also says a mark stays if its wall goes: that hung paint in the air, so paint now goes with its wall.
- Launching the game went through Steam, as `live_session.py` does. I did not fullscreen or focus it deliberately, but cannot rule out Windows raising the window at launch.
