# LONGSHADE_ART_AUDIT_GPT_UNKEPT_REDO_LIST

Sources: Transient/gpt_biome_art_review_2026-10-24.md (digest) and D:\ClaudeWork\rimmandrake\gpt_biome_review\LongShade.md (full review; raw answers in raw/). Everything below is GPT (gpt-6.1-sol) opinion; nothing was acted on.

Rows where GPT says redo/cut and the owner has NO keep on record. Filed as a FINDING, not queued: the art rule (memory 'Queue art only for NONE/PLACEHOLDER/DONOR') needs the destination state confirmed from the art ledger first, and that was not done here. Next step: confirm each row's state in the art ledger; NONE/PLACEHOLDER/DONOR may be queued, a live art-eval-pipeline redraw is shown to the owner after with a revert. Tile kinds: live = installed art, artpipe = candidate render.

## RSW_Clodhopper - art redo
- Reason: The live north is an undersized cartoon placeholder inconsistent with the painterly anatomy of south and east; the candidate east is successful.
- T017 (live) redo: Replace the tiny cartoon north placeholder with a complete painterly rear matching the size and four-legged anatomy of south and east.

## RM_Harrok - art redo
- Reason: The specified stilt legs and elevated narrow body are present, but the installed brown appearance loses essential forms against the ground. Check tint/material and restore the pale source treatment before replacing anatomy.
- T062 (live) redo: The live brown trunk and thin legs fade into the ground at normal play; restore the pale thumbnail values and readable edges, checking installed tint first.

## RM_Mirrak - art redo
- Reason: The conspicuous gold rim, scalloped outline and raised radial folds defeat the defining matte, wafer-flat false-shadow disguise across the facings.
- T084 (live) redo: Gold edging, radial pleats and raised folds undermine the false-shadow disguise; redraw a matte, wafer-flat dark oblong.

## RM_Pirrik - art redo
- Reason: The insect body and membrane wings omit the defining plumage and contradict bird identity. Rebuild an alien feathered bird, reduce display scale and simplify fine shapes for normal-play legibility.
- T093 (live) redo: Veined membrane wings, segmented body and multiple jointed legs conflict with the required plumaged bird; rebuild feathered anatomy and reduce palm-sized displa

## RSW_LongtailGorg - art redo
- Reason: The visible sets retain useful spots and flattened tail tips, but their dorsal front/rear constructions need consistent orthographic foreshortening; displayed size also warrants a separate polish check.
- T199 (live) redo: Retain tan spotting and the widened tail tip, but redraw the elongated dorsal south and north layouts with proper front and rear foreshortening.
- T200 (artpipe) redo: North reads as an overhead back-and-tail plan beside an elevated side profile; rebuild all facings with one camera angle and consistent body depth.
- T201 (artpipe) redo: North shows an almost unforeshortened dorsal body and south stacks the long tail above the face; correct perspective while retaining spots and the flattened tip
- T202 (artpipe) redo: Retain the spotted body and flattened tail tip, but replace overhead south/north views with proper front/rear views and broaden the narrow reptilian head.
- T203 (live) cut: Purple limbless tadpole placeholder lacks the frog head, four splayed limbs, clawed toes and widened tail tip.
- T204 (artpipe) redo: Spotted green colouring and expanded tail tip fit the brief, but north is an overhead spread-eagle view rather than the animal's rear.
- T205 (live) cut: Mint-and-purple cartoon tadpole placeholder lacks the spotted four-legged amphibian body and long spread toes.
- T206 (artpipe) cut: Broken facing set: south is an unrelated armoured arthropod while east and north depict a spotted amphibian.
- T207 (artpipe) cut: Repeats the mint-and-purple tadpole placeholder design, including its smooth wedge-shaped tail and vestigial limbs.
- T208 (live) cut: Cartoon tadpole placeholder lacks the defining spotted body, four developed limbs and horizontally expanded tail tip.
- T209 (artpipe) redo: Retain the spotted body and expanded tail tip, but replace dorsal south/north views with genuine front/rear swimming perspectives.

## RSW_Worrt - art redo
- Reason: No complete set passes. T214 lacks defining anatomy and uses flat cartoon treatment; T215 has promising front and rear views but a fundamentally inconsistent east view; T216 is a wrong-body placeholder. Use T215 south and north as the anatomical direction and rebuild a coherent set.
- T214 (live) redo: Recognisable worrt head, but the flat cartoon mound lacks the required long supporting forelimbs and splayed hands; an oval ground shadow also appears beneath i
- T215 (artpipe) redo: South and north approach the canon worrt, but east shows strapped-looking armour plates and clustered hooked claws instead of the same broad-headed, round-belli
- T216 (live) cut: Wrong-body placeholder: a smooth orange tailed tadpole/lizard rather than a squat, warty worrt with a broad mouth, heavy belly and long splayed forelimbs.

Cartoon placeholders for Eopie / LongtailGorg / Worrt are probably a STALE DEF DUMP in the sheet, not installed art; check before acting (see GIZKA_SHEET_FIX_ALTERNATE_SHOWN_AS_RENDER).

## Per-row outcome (FOUNDRY, 2026-10-24, delegated: GPT art triage)
Gate = regen_eligibility.Gate over every texPath of the def; pipeline = infrastructure/state/art_eval/runs/*/decisions.jsonl; PROTECTED = art.py status live slots. Queued directly: NONE (no redo slot is NONE/PLACEHOLDER/DONOR; dessicated slots that are DONOR are not what GPT flagged).

| def | gate | protected slots | art-eval runs so far | outcome |
|---|---|---|---|---|
| RSW_Clodhopper | REFUSED_REGEN | 1 | none | CANDIDATE: never judged; intake filed as GPTREDO_JUDGE_UNJUDGED_ROWS (art-eval run, not a direct regen). |
| RM_Harrok | REFUSED_REGEN | 0 | none | CANDIDATE: never judged; intake filed as GPTREDO_JUDGE_UNJUDGED_ROWS (art-eval run, not a direct regen). |
| RM_Mirrak | REFUSED_REGEN | 0 | none | CANDIDATE: never judged; intake filed as GPTREDO_JUDGE_UNJUDGED_ROWS (art-eval run, not a direct regen). |
| RM_Pirrik | REFUSED_REGEN | 0 | none | CANDIDATE: never judged; intake filed as GPTREDO_JUDGE_UNJUDGED_ROWS (art-eval run, not a direct regen). |
| RSW_LongtailGorg | REFUSED_REGEN | 12 | none | UNQUEUED: 39 ruled owner keep events, 12 protected slots - the "no owner keep" premise is false; GPT redo needs his word / revert record. Cartoon-placeholder tiles: the live files are ledger artpipe renders (REFUSED_REGEN), a stale-sheet-dump is plausible but unviewed. |
| RSW_Worrt | REFUSED_REGEN | 9 | none | UNQUEUED: 11 ruled owner keep events, 9 protected slots - the "no owner keep" premise is false; GPT redo needs his word / revert record. Cartoon-placeholder tiles: the live files are ledger artpipe renders (REFUSED_REGEN), a stale-sheet-dump is plausible but unviewed. |
