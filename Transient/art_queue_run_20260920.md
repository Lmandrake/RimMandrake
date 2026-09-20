# Art queue run 2026-09-20

## State

STATUS 20260920 (live): not blocked. Just finished auditing 40/50 creature sets with the `claude -p` viewpoint check (results below, just written) — each call completes in ~10s so no long-lived process is visible between batches, that's expected, not a hang. Finishing the remaining 10 sets now, then queuing repair jobs into pending/ for confirmed OVERHEAD-FAIL sets, worst-first.

CONFIRMED: viewpoint check (`claude -p` vision call inside facing_set_audit.py) works and is fast (~10s/call). Not offline-only; genuinely judging each south PNG.
Scope: 65 FLAG sets from Transient/facing_set_sweep_20260920_postfringe.txt, of which 50 are creatures (the other 15 are buildings/vehicles/headgear where "face toward camera" doesn't apply the same way — PyrinthBrazier, WallPyrinthTorch, 3x AutomatedSmelter, 2x Bacta tanks, 5x DesertVehicleReskin, GravForge, AdvFungiponics, SpiderHelmet — SKIPPED, not creatures).
Ranked worst-first by (byte-identical*1000 + anchor-drift% + size-spread%) from the offline sweep. Running `facing_set_audit.py` WITH viewpoint check on all 50 creature sets.
Noted BENCH's new gate (commit 44518c266): jobs with `facing` + "top-down"/"overhead"/"N facings" in prompt body are refused. My repair prompts use surface language only ("front view, eyes toward viewer") so they pass clean.

## Viewpoint audit (CONFIRMED via `claude -p` vision call unless noted)

STAT-FLAG-ONLY = fails only an offline statistic (anchor drift/size spread/palette), south viewpoint judged fine — does NOT need a redraw.
OVERHEAD-FAIL = `claude -p` judged the south PNG as OVERHEAD (top-down), confirming the owner's named defect — NEEDS a south redraw.

1. cephalope — STAT-FLAG-ONLY (size spread 84.9%, no redraw needed for viewpoint)
2. dessicated_cephalope — OVERHEAD-FAIL
3. landopus/landopus — OVERHEAD-FAIL
4. swimming_cephalope — OVERHEAD-FAIL
5. swimming_landopus — OVERHEAD-FAIL
6. AA_Lockjaw2 — OVERHEAD-FAIL
7. AA_Lockjaw3 — OVERHEAD-FAIL
8. Sytheclaw — OVERHEAD-FAIL
9. swimming_nautilant — STAT-FLAG-ONLY
10. dessicated_landopus — OVERHEAD-FAIL
11. GR_ParagonRat — OVERHEAD-FAIL
12. GR_Molebear — OVERHEAD-FAIL
13. Ollopom — OVERHEAD-FAIL
14. Grank — OVERHEAD-FAIL
15. GreaterKraytDragon — OVERHEAD-FAIL
16. Wyyyschokk — OVERHEAD-FAIL
17. RUT_CathedralRoachCorpse — OVERHEAD-FAIL
18. Flamefang — OVERHEAD-FAIL
19. RUT_CathedralRoach — OVERHEAD-FAIL
20. Gizka — STAT-FLAG-ONLY
21. Orray — OVERHEAD-FAIL
22. Vornskyr — OVERHEAD-FAIL
23. Dewback — OVERHEAD-FAIL
24. AA_Thermadon — OVERHEAD-FAIL
25. Zakkeg — OVERHEAD-FAIL
26. FireWasp — STAT-FLAG-ONLY
27. Anooba_m — STAT-FLAG-ONLY
28. Insectomorph — OVERHEAD-FAIL
29. Kreetle — OVERHEAD-FAIL
30. Megatardi — OVERHEAD-FAIL
31. Dragonsnake — OVERHEAD-FAIL
32. nautilant — STAT-FLAG-ONLY
33. GR_Mantistanis — STAT-FLAG-ONLY
34. RUT_ScarRoach — OVERHEAD-FAIL
35. Horax — STAT-FLAG-ONLY
36. FurnaceBeast — STAT-FLAG-ONLY
37. Fambaa — STAT-FLAG-ONLY
38. AA_TarGuzzler — STAT-FLAG-ONLY
39. Whisperbird — OVERHEAD-FAIL
40. AA_Bumbledrone — STAT-FLAG-ONLY

(41-50 in progress: AA_AcanthamoebaGigantea, Kinrath, AA_Terramorph, GR_Spidercat, AA_Thunderox_male, GizkaW, Anooba_f, AA_BloodShrimp, Dalgo, AA_Agaripod)

Running tally so far: 24 OVERHEAD-FAIL / 16 STAT-FLAG-ONLY of 40 audited.

Full per-set raw output (offline stats + viewpoint verdict) logged at
`/mnt/d/Luke/dev/Rimworld/Transient/facing_viewpoint_audit_20260920.log`.

## Viewpoint audit — full result and a CRITICAL correction to the raw LLM verdict

All 50 creature sets audited. Raw tally: **33 OVERHEAD-FAIL / 17 STAT-FLAG-ONLY** by the `claude -p` judge alone.

🔴 **CONFIRMED by looking at all 33 OVERHEAD-FAIL south PNGs myself (Read tool, not just the LLM's one word):** the raw viewpoint judge over-flags a specific, otherwise-legitimate RimWorld art convention — a predator lunging/roaring straight at the camera, front legs splayed toward the viewer, face and teeth dominant, but with some dorsal spikes/back visible because the pose is dynamic (crouched, rearing, or mid-lunge). That pose reads as a genuine, acceptable FRONT view to a human, not an overhead one, and it is the same convention CLAUDE.md's own worked example (`rot_mycoidcolossus_v3_north` — "wide, low... splayed legs") uses successfully elsewhere. The LLM's calibration note in `facing_set_audit.py` itself warns of exactly this: *"high-angle crouches... sit near the boundary and may flag — that is a human-look flag, not a defect."*

Of 33 raw OVERHEAD-FAIL, only **12 are genuine** by my own look — the dominant visible surface is actually the back/shell/spine with little or no face, not a lunge pose:

**GENUINE (queued for repair):** Dewback, Ollopom, Wyyyschokk, GR_Molebear, GR_ParagonRat, RUT_CathedralRoach, RUT_CathedralRoachCorpse, RUT_ScarRoach, Flamefang, Orray, Kreetle, Megatardi.

**NOT queued — LLM said OVERHEAD, my own look says acceptable front-facing lunge/roar/dive pose (established convention, redrawing would waste quota the owner has rejected before for unneeded regens):** AA_Lockjaw2, AA_Lockjaw3, Sytheclaw, Vornskyr, Grank, GreaterKraytDragon, AA_Thermadon, Zakkeg, Insectomorph, Dragonsnake, Whisperbird (a diving owl — swoop-toward-camera is correct for a flyer), Kinrath, AA_Terramorph, GR_Spidercat, AA_BloodShrimp, AA_Agaripod.

**UNCERTAIN (not queued) — faceless blob/shell body plan, no eyes or head visible either way, so "front vs rear" cannot be judged by eye at all:** dessicated_cephalope, landopus, swimming_cephalope, dessicated_landopus, swimming_landopus. These need the owner or a body-plan ruling, not a redraw guess.

**17 STAT-FLAG-ONLY** (viewpoint judged EYELEVEL/fine, only an offline statistic like anchor drift or size spread flagged): cephalope, swimming_nautilant, Gizka, FireWasp, Anooba_m, nautilant, GR_Mantistanis, Horax, FurnaceBeast, Fambaa, AA_TarGuzzler, AA_Bumbledrone, AA_AcanthamoebaGigantea, AA_Thunderox_male, GizkaW, Anooba_f, Dalgo. None of these need a redraw for viewpoint; a drift/spread flag is a different repair (conform/re-anchor), out of this wave's scope.

Full per-set raw output logged at `/mnt/d/Luke/dev/Rimworld/Transient/facing_viewpoint_audit_20260920.log`.

## Queued

12 repair jobs written to `infrastructure/artpipe/pending/`, priority 90, `rimflow_item_id: ART_FACING_REPAIR_WAVE_1`, south-facing only, `reference: null`, verified to load cleanly through BENCH's new `common.load_job()` phrase gate (no "top-down"/"overhead"/"N facings" substrings — used positive surface language throughout: "seen from directly in front at eye level: eyes, face and chest toward the camera"):

Built from an existing artpipe job JSON (material/palette words reused verbatim, only the framing clause rewritten):
- `facingrepair_dewback_v1_south.json` (from dewback_v1_south)
- `facingrepair_ollopom_v1_south.json` (from ollopom_v1_south)
- `facingrepair_wyyyschokk_v1_south.json` (from wyyyschokk_v1_south)
- `facingrepair_orray_v1_south.json` (from pyrelands_orray_v2_south)
- `facingrepair_kreetle_v1_south.json` (from canon_kreetle_v1_south)
- `facingrepair_megatardi_v1_south.json` (from vaewaste_megatardi_v1_south)

Hand-authored (no prior job JSON existed for these — description written from my own look at the shipped PNG):
- `facingrepair_grmolebear_v1_south.json`
- `facingrepair_grparagonrat_v1_south.json`
- `facingrepair_rutcathedralroach_v1_south.json`
- `facingrepair_rutcathedralroachcorpse_v1_south.json`
- `facingrepair_rutscarroach_v1_south.json`
- `facingrepair_flamefang_v1_south.json`

All 12 pending as of this writing — the daemon has not yet picked any of them up (`infrastructure/artpipe/active/` was empty at last check, none in `done/` or `failed/` yet, 33 total jobs in `pending/` = 21 pre-existing + 12 mine). Per the owner's standing instruction not to idle-wait on quota, I am stopping here rather than polling; whoever picks this up next should check `infrastructure/artpipe/done/facingrepair_*.json` for completions.

Commit: `748a01731` (report + audit log + 12 queued jobs), pushed to `main`.

## Installed

(none yet — waiting on the daemon to render the 12 queued jobs)

## Failed or skipped

15 non-creature FLAG sets (buildings/vehicles/headgear) skipped entirely — "face toward camera" doesn't apply the same way and BENCH's brief scoped this to creature viewpoint: PyrinthBrazier, WallPyrinthTorch, 3x AutomatedSmelter (Kludged/Repaired/Wrecked — these are actually a FALSE FLAG per the audit script's own transposition-aware size check, see its comment on `AutomatedSmelter`), 2x Bacta tanks, 5x DesertVehicleReskin (Chariot/CoveredCarriage/DogSled/OxCart/WarChariot), GravForge, AdvFungiponics, SpiderHelmet.

21 creatures with genuine-looking OVERHEAD-FAIL by the raw LLM judge were deliberately NOT queued (see the correction above) — recorded, not silently dropped.

## Owed

- The 21 "boundary/acceptable pose" and 5 "faceless body plan" creatures above are UNMEASURED for viewpoint in any stronger sense than my own single look — a second human/Fable-tier look before fully closing them out would be good practice, but I judged them confidently enough not to spend quota on them.
- 17 STAT-FLAG-ONLY creatures still carry a real defect (anchor drift / size spread / palette distance) — not a viewpoint problem, so out of scope for `ART_FACING_REPAIR_WAVE_1`, but still open work for whoever owns the conform/re-anchor pass.
- Once the 12 queued jobs land in `done/`: zero alpha 1-16, downscale with premultiplied alpha to the target canvas, re-run `facing_set_audit.py` on the repaired set, install only if it improves, `deploy_custom_mods.py --mod <ModName>` plan then apply, commit+push per creature set. None of that has happened yet — nothing has landed from the daemon as of this writing.
