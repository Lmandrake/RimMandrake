# art_eval run fauna_auto_20261028_1131

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_FireHawk | r2 | creature/flyer | WEAK | strong_accept | **ACCEPT** | 57.6 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish ['FLYER_WINGS_GROUNDED']; gpt strong_accept: unsettled [], own blocking [] |
| RM_FireWasp | r2 | creature/flyer | WEAK | strong_accept | **ACCEPT** | 64.5 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP']; polish ['SCALE_WRONG', 'FLYER_WINGS_GROUNDED']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Flamefang | r3 | creature/walker | WEAK | regen | **ESCALATE** | 71.7 | opus band WEAK (model said weak); blocking ['ALPHA_HALO', 'STYLE_CARTOON']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['ALPHA_HALO']; still failing after 3 regen rounds — one line to the owner |
| RM_Surrik | s2r2 | creature/walker | WEAK | regen | **REGEN** | 104.9 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'F_SIZE_JUMP']; polish ['SCALE_WRONG', 'LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING'] |

## One line each for the owner
- RM_Flamefang: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
