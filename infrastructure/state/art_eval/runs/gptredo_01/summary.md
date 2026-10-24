# art_eval run gptredo_01

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_Mynock | live | creature/flyer | REALLY_BAD | - | **REGEN** | 58.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'CANON_MISS', 'F_TOPDOWN']; polish ['FLYER_WINGS_GROUNDED', 'LEGIB_32'] |
| RSW_Gizka | live | creature/walker | WEAK | regen | **REGEN** | 115.8 | opus band WEAK (model said good); blocking ['STYLE_CARTOON', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['STYLE_OFF']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RSW_Clodhopper | live | creature/walker | REALLY_BAD | - | **REGEN** | 56.6 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'PLACEHOLDER', 'STYLE_CARTOON', 'F_SIZE_JUMP', 'F_TOPDOWN', 'F_NORTH_FACE', 'CANON_MISS', 'OWNER_NOTE_IGNORED', 'DONOR']; polish ['SCALE_WRONG']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`

## VOID row
RSW_Mynock in this run is VOID: it was judged on _east/_north files that the game never draws, because the def is Graphic_Single. Its delegated record was deleted. The re-judgement is gptredo_01b (RSW_Mynock__live_single.json). See ART_EVAL_SPEC_FIX_GRAPHIC_SINGLE_FACINGS.
