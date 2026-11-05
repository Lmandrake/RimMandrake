# art_eval run audit_20261105_h3

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Huldu_n | r3 | creature/swimmer | WEAK | regen | **ESCALATE** | 92.1 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING', 'ALPHA_HALO']; still failing after 3 regen rounds — one line to the owner |
| RM_Murrin_ns | r3 | creature/swimmer | WEAK | strong_accept | **ACCEPT** | 90.6 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Skarrin_n | r3 | creature/swimmer | WEAK | regen | **ESCALATE** | 83.9 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'OWNER_NOTE_IGNORED', 'FOOTPRINT']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_TOPDOWN', 'F_INCONSISTENT', 'FOOTPRINT']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Huldu_n: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Skarrin_n: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
