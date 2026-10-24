# art_eval run fauna_contagion_r3_01

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Fleshsop | r3 | creature/walker | WEAK | regen | **ESCALATE** | 69.0 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING']; still failing after 3 regen rounds — one line to the owner |
| RM_Gawpsack | r3 | creature/walker | WEAK | regen | **ESCALATE** | 76.9 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; still failing after 3 regen rounds — one line to the owner |
| RM_Gorekite | r3 | creature/flyer | WEAK | strong_accept | **ACCEPT** | 105.0 | opus band WEAK (model said good); blocking ['STYLE_EARTHLY', 'DUPLICATE']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |

## One line each for the owner
- RM_Fleshsop: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Gawpsack: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
