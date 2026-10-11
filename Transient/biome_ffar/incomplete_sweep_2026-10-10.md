# Incomplete renders / unfulfilled orders sweep — 2026-10-10

Status: DONE 2026-10-10 — 7 renders fixed and PASS; 11 still failed_canon after 2-3 rounds (generator limit, see Still open); all 27 sheets pass the gate

| sheet | incomplete renders | unfulfilled orders | action taken | still open |
|---|---|---|---|---|
| contagion (ruled) | Gawpsack E/N/S failed (failed_canon pink tint; master_failed) | redraw failed | | |
| deep_desert (ruled) | KraytDragon s3 south failed_canon; Drazzik/Qorrax swimming failed after 3 refiles | | | 4 conflicts (owner) |
| cauldron (prefill) | Silooth v5 east failed_canon | — (prefill) | | |
| miasma (prefill) | Blixus v2b south, v2 swim east, OpeeJuv v3 south failed_canon | — (prefill) | | |
| therot (prefill) | GreyLady immature failed_canon; violetwimple b v2 failed_canon | — | | 18 conflicts |
| weepingstones (prefill) | IvvolCatch N/S, KarrekCatch E/N/S failed | — | | |
| theforge (prefill) | enact refuses (no plumbing stamp) — expected for prefill | — | | |

Diagnosis (failed_canon root causes): catch jobs (Ivvol/Karrek) grade a non-visual workflow sentence ("generate AFTER the source is settled") that can never pass, plus no death cues in prompt; Drazzik/Qorrax swim jobs leave too much body above sand; Blixus/Opee tentacle/leg/antenna lengths; GreyLady immature reads as grown; VioletWimple glossy; Silooth only 3-4 legs visible in profile; Gawpsack residual pink; Krayt south lacks long neck. Dakkra gap jobs are already in done/ (resolved).

Action 1 (done): 18 failed jobs moved failed/ -> pending/ with prompts strengthened on exactly the failed check lines; manifests parked in _requeued_manifests/. canon_na (sanctioned per-job field) used only for unjudgeable lines: catch-job workflow sentence (the passing Ivvol east master already graded it n/a), Drazzik "match the source image" (grader never sees the master), Blixus east "two eyes" (far eye hidden in profile). No check line removed or loosened otherwise.

Placeholder sweep (placeholder_detect): 49 rows live on placeholder art (WeepingStones 20, FeverWood 18, Greentide 7, TwilightSea 2, Webwork 2). 44 already have finished candidate renders awaiting the owner's pick (prefill sheets — install is his call). No job by target_def: RM_Thavrik, RM_Skethral (FeverWood), RM_Gorrask, RM_Ivvol, RM_Karrek (WeepingStones) — checking with artpipe_state find.

All 49 placeholder rows have finished candidate renders (the 5 without a target_def match were found by artpipe_state find: feverwood_thavrik, feverwood_plant_skethral, weepingstones2_gorrask, weepingstones_ivvol, weepingstones_karrek). Nothing to queue.

Def halves of followed notes (description / size / rename / new-creature edits) on RULED sheets, not art, still open: abyss 7 (DuskProwler, Murkling, NightMule, Nightling, Septimum, Aveluthia, PaddleVine), blue_desert 1 (Thunderbeast: description + half size), desert 2 (Chorn 5 cells wide + description, Ultracactus), greysea 1 (Hessal), leaningscrub 1 (Chikka), thescald 2 (ScaldWalker rename "Iridesce", Thuum), thesump 1 (SumpMouse), twilightsea 2 (Dancing Skresh new creature from Hollu B). Not done here: def work in src/, needs a def-writing pass. Desert has 2 owner conflicts (GreatDevourer tier contradiction).

Round 1 results: done+PASS — Gawpsack E/N/S, KraytDragon s3 south, GreyLady immature, VioletWimple b v2. Failed again — Silooth (3/5), Blixus x2, OpeeJuv (3/7), catch jobs (still read alive; the reference is the live animal and the model copies its pose). Drazzik/Qorrax swim x3 still active.
Round 2 (9 jobs): hard requirements moved to the FRONT of the prompt ("FIRST AND MOST IMPORTANT ..."); catch jobs told explicitly not to copy the live pose.

Angel Moth / Crimson Cap (coordinator ask): renders exist and passed canon — rotrow_angelmoth_south_v1_south (south only), rotvar_crimsoncap_a_v1, rotvar_crimsoncap_b_v2 in done/. The Rot art sheet was stale (still showed failed crimsoncap_b_v1, no angelmoth row render); the naming sheet is a non-art sheet and shows no new art at all. Owner clarified he wants fresh realistic options; BENCH is queuing those — nothing queued here.

## Final (after round 2)
Fixed, done + canon PASS: Gawpsack E/N/S (contagion), KraytDragon s3 south + Drazzik swim north (deep_desert), Silooth v5 east (cauldron), GreyLady immature + VioletWimple b v2 (therot). GreyLady's PASS is vacuous (0/0 lines graded, its only line is provenance); looked at it myself: a closed-cap button with a few threads, reads young.
Rebuilt with refresh_sheets: cauldron, contagion, deep_desert, therot (contagion and therot servers restarted by the tool itself: NEW URL). remap_decisions dry run: 0 remapped, 0 orphaned on all 27, so no --apply. Gate: 27/27 PASS.

## Still open
- failed_canon after 3 tries, generator limit, not retried again: Qorrax swim E/S (deep_desert/desert; shell flank stays above sand), Blixus v2b south (4 legs show, not 6) and swim east (lowest tentacle short), OpeeJuv v3 south (legs stout, antennae short) (miasma); IvvolCatch N/S and KarrekCatch E (+N/S master_failed) (weepingstones; the model keeps the live pose). Next step: catch facings from a passing dead master (Ivvol east passed), and the owner decides whether the miasma/Qorrax canon art needs a new approach.
- Def halves of followed notes on ruled sheets (17 rows, listed above): def work, never done.
- Owner conflicts: deep_desert 4 (the swim jobs above), desert 2 (GreatDevourer tier), therot 18, greentide 3, wasteland 1. Awaiting-pick rows: many, his to rule.
- Angel Moth / Crimson Cap: BENCH is queuing new options (coordinator); nothing queued here.
