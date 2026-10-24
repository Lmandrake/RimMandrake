# art_eval run fauna_cauldron_r3_00

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_BedBug | r3 | creature/walker | WEAK | regen | **ESCALATE** | 77.2 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K3'], own blocking ['F_TOPDOWN', 'F_INCONSISTENT']; still failing after 3 regen rounds — one line to the owner |
| RM_Bileworm | r3 | creature/walker | WEAK | strong_accept | **ACCEPT** | 101.1 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_CrystalMit | r3 | creature/walker | WEAK | strong_accept | **ACCEPT** | 61.9 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish []; gpt strong_accept: unsettled [], own blocking [] |

## One line each for the owner
- RM_BedBug: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
