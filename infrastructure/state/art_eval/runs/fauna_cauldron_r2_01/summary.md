# art_eval run fauna_cauldron_r2_01

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_DecayDrake | r2 | creature/walker | WEAK | regen | **REGEN** | 118.4 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'ALPHA_HALO', 'F_SIZE_JUMP']; polish []; gpt regen: unsettled ['K3'], own blocking ['F_SIZE_JUMP'] |
| RM_Mullgoth | r3 | creature/walker | WEAK | regen | **ESCALATE** | 89.4 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'STYLE_CARTOON', 'DUPLICATE']; polish []; gpt regen: unsettled [], own blocking ['STYLE_OFF', 'F_SIZE_JUMP']; still failing after 3 regen rounds — one line to the owner |
| RM_Rhossak | r2 | creature/walker | WEAK | strong_accept | **ACCEPT** | 50.2 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |

## One line each for the owner
- RM_Mullgoth: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
