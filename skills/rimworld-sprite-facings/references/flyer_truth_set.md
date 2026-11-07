# Flyer truth set: eight birds with the owner's verdicts (2026-11-07)

The human-labelled set for scoring any flyer check. He judged these animated, names hidden, at the game's frame rate. His eyes are the label. A new check should agree with this table, and it still counts for nothing until it has also been scored on a fresh sealed batch, because a check fitted on these birds has only passed its own test.

## The labels

| Bird | What it is | His words | Label |
|---|---|---|---|
| A | FireHawk frames at `af2991860e` | "North and south look good. East was built from a version with a static wing in the "down" position along the body, so as the wing flaps you see two wings ... There's also something wrong with the wing when it's pointed mostly at the camera ... strange static-like noise" | N, S good. E bad twice |
| B | A started one frame later | "nearly identical with the same problem, though the wings appear to beat more and that's better" | E bad. Beat better than A |
| C | A with the north right wing frozen on frame 5's pose | "North has an unflapping right wing though I can see some of the right wing peeking into its lower right quadrant, likely just a graphic mapping error" | N bad, E bad |
| D | FireHawk frames at `af2991860e^`, before the cut-out rebuild | "the body bobbing wildly and is quite silly, but I think maybe just adjusting it to keep the eyes level between shots might be the best fix we've got" | Body bad. Wings not faulted |
| E | Vanilla `Chicken_Flying_` from the game's assets | "a chicken that satisfies the requirements perfectly" | Good, all facings |
| F | A with the whole frame shifted by round(2 sin(2 pi k / 5)) px | "nearly identical to Bird A" | E bad. The 2 px bob went unmentioned |
| G | Live Porg frames at `5ee3fc2dc2` | "terrifying! The wings have been morphed away from the body incorrectly, so some of the white flesh appears to rip away from the body in a horrific sliced-off-cartoonish way" | Bad |
| H | A with the north left wing erased | "like Bird A except it is now missing any art in the upper left North facing, and shows the same east defect" | N bad, E bad |

## What each instrument read

Stabilize, lines, motion and frames-present are `flier_body_stabilize.py`, its `--lines`, `flyer_cutout.py motion` and the frames-present selftest. The judge is GPT on contact sheets and difference strips. The last four columns are `flyer_eye_checks.py audit`.

| Bird | Stabilize | Lines | Motion | Frames | Judge | HEAD span, worst facing | SIDES lowest ratio | SQUASH | HOLD on east |
|---|---|---|---|---|---|---|---|---|---|
| A | GREEN | GREEN | GREEN | GREEN | PASS | 0 | 0.95 | RED | mid-stroke |
| B | RED | RED | GREEN | GREEN | PASS | 0 | 0.94 | RED | extreme |
| C | GREEN | GREEN | GREEN | GREEN | FAIL, north only | 0 | **0.05** | RED | mid-stroke |
| D | UNMEASURED | UNMEASURED | GREEN | GREEN | FAIL | **57** | 0.96 | not a cut-out | extreme |
| E | BROKE | BROKE | GREEN | GREEN | PASS | 0 | 0.99 | not a cut-out | mid-stroke |
| F | RED | RED | GREEN | GREEN | FAIL | **4** | 0.97 | RED | mid-stroke |
| G | GREEN | GREEN | GREEN | GREEN | PASS | 0 | 0.95 | GREEN | mid-stroke |
| H | GREEN | GREEN | GREEN | GREEN | FAIL, north only | 0 | **0.05** | RED | mid-stroke |

## Reading it

- **Nothing here reads the east double wing or the Porg rip as a number.** Both show on `flyer_eye_checks.py parts`, which is a look: the FireHawk plate holds the folded wing, and the Porg plate is a straight-sided column with belly on the wing layers. A judge has to be shown that sheet to see them.
- **The body gates are wrong on both of his comparisons.** B is red and he prefers it. E is broken and he calls it perfect.
- **HOLD is one comparison, A against B.** E holds mid-stroke and he calls it perfect, so HOLD is advice, not a fault.
- **F is one observation with a louder defect beside it.** It is not a ruling that 2 px is fine. Loosening a bar is his.

Panel, gates and judge output: `D:\ClaudeWork\rimmandrake\firehawk_replay\`, with the key in `work\page_key.json` and the table with his causes checked in `OWNER_VERDICTS_2026-11-07.md`.
