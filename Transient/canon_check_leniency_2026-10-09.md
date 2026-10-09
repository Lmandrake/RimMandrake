# canon_check leniency diagnosis — 2026-10-09 (diagnosis only; no grader or canon text changed)

## How the grader works (`src/RimMandrake/Utils/artpipe/canon_check.py`)
- One codex vision call (gpt-6.1-sol, effort high). Image 1 = render; images 2..5 = up to 4 canon images. So it DOES see canon
  (hawkbat: only 1 image attached, `wookieepedia_legends_infobox.jpg`).
- Prompt: "strict art director", grade EACH `## Must show` line pass/fail/na with a one-line reason. Verdict = FAIL iff any line fails.
- Lenience built into the prompt: "Do NOT fail a line for art style, medium, scale or level of detail"; brief + job prompt included as context;
  owner note wins over canon. No holistic "does the whole animal match the reference" question exists; a render is never compared to the
  canon image as a whole, only line-by-line against text.
- Parsing is strict (missing line / bad verdict raises). No default-pass in the parser. The leniency is in WHAT is asked, not parsing.

## Root cause 1 — the hawkbat Must-show lines are loose and the entry's own brief describes a wyvern
Must show: "violet-purple dorsal fading to cream", "small horn", "hooked beak", "LONG TAIL present", "ribbed wing membrane ... clawed wingtips",
"reads as a PTEROSAUR-LIKE reptavian". Visual brief: "pterosaur-like silhouette ... long tail". A wyvern with whip tail satisfies every line
(each manifest reason cites exactly that). Nothing says body-is-the-wing, no standing legs, purple as a central stripe with tan cross-bars,
no finger-spar fan, no crest. The lines are also contradicting the owner's "NOT a bird" vs "hooked beak" prompt (noted in redraw note).
So the checklist itself, not the vision model, is what passes it. Colour line passes on "violet ribs and dorsal areas".

## Root cause 2 — checklist structure makes PASS cheap
- Mean 3.2 graded lines per job; 806 of 1374 graded jobs have <=3 lines. Owner-note jobs (868 of 875) average 1-3 sentences.
- All-lines-must-pass sounds strict, but each line is a presence test ("tail present", "ribbed membrane present"), which is the easiest kind to satisfy.
- Overall PASS rate 1364/1374 = 99.3%. A gate that passes 99.3% is not discriminating.

## Measured agreement (MEASURED 2026-10-09, python; join = owner ruling `target.shas` / `rejected.sha` to sha256 of each manifest's graded render)
Instrument: graded manifests in `_artpipe/done/*.manifest.json` with `canon_check.status==graded`: 1374, all with render file present.
Owner rulings from `infrastructure/state/art/events/{BENCH,FOUNDRY}.jsonl` (`by=owner`, trust ruled/flawed-sheet, verdict keep|redo|reject, plus `rejected` events).
Labelled renders N=559 (sha-joined):

| owner \ canon_check | PASS | FAIL |
|---|---|---|
| rejected / redo (23) | 23 | 0 |
| kept (536) | 528 | 8 |

- Owner-rejected renders PASSED: 23 of 23 (100%) — ~13 distinct subjects (eopie, gorg, iriaz, longtailgorg, skalder, worrt, pekopeko flyer,
  skennet, brimlock, kessaroth, pellareth, varrisk). Catch rate of owner rejections = 0/23.
- Owner-kept renders that canon_check FAILED: 8 of 536 (bluedesert Vrisk/Thunderbeast/Dovvik, Destroyer, Vhaulk...) — mostly the vague line
  "It must look like nothing terrestrial: no recognisable Earth ..." and, for bantha, a fine detail (mouth width, horn size).
- Net: the grader fails on subjective/vague lines and fine details, passes gross body-plan misses. Direction of agreement with the owner is
  about chance-or-worse (negative signal: its 10 FAILs hit 8 kept renders and 0 rejected renders).
- Caveats: only 23 rejected shas joined (735 `rejected` events exist, most are unrenders from non-artpipe shas); labels are per-sheet column
  keep/redo, so a kept column may be a lesser-evil choice; hawkbat renders themselves are not in this set (rejected by card, no sha ruling).
  Sanity probe: join found 559 labelled and 10 FAILs overall, so the join can see both classes; the 23/23 is not a join artifact (rejects join
  at all, and FAILs do exist elsewhere).

## Proposed fixes, cheapest first (not implemented)
1. (cheap, per entry, wording) Rewrite Must show as negatives + body-plan lines that a wrong animal cannot satisfy. Hawkbat: "NO separate
   body/legs/whip tail: the wing membrane IS the body, two trailing points", "wing = narrow kite membrane with dense transverse ribs, NOT
   radiating finger spars", "broad violet stripe down the centre of each wing crossed by tan bars", "no crest/feathers; two swept-back horn-stalks".
   Also fix the brief's "pterosaur-like ... long tail" which licenses the wyvern.
2. (cheap, code) Add two generic gate lines to every canon job in build_prompt: "OVERALL BODY PLAN: could a stranger shown only the render and
   canon image 2 call them the same animal? (silhouette, limb count, tail, wing/body structure)" and "COLOUR LAYOUT matches the canon image,
   where the colour sits, not just which colours exist". Tell the grader that presence-of-a-feature is not enough; list what is WRONG.
3. (medium) Two-pass: first ask the vision model to describe render and canon image independently (no checklist), then diff the descriptions
   against the Must-show; this removes anchoring on the checklist wording. Plus a calibration set (the 23 rejected + 8 kept FAILs above) run
   before trusting a prompt change; require it to FAIL >=80% of the rejected and <=10% of the kept.
4. (higher) Attach all canon images, side-by-side composite (render | canon) as one image to force a visual comparison; exclude boilerplate
   "nothing terrestrial" lines from the verdict or make them advisory.
