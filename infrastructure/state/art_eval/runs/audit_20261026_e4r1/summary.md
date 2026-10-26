# art_eval run audit_20261026_e4r1

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Skarrin_n | r1 | creature/swimmer | REALLY_BAD | - | **REGEN** | 54.2 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP', 'OWNER_NOTE_IGNORED']; polish ['LEGIB_32'] |
| RM_Vhakk_n | r1 | creature/walker | WEAK | regen | **REGEN** | 90.7 | opus band WEAK (model said weak); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'OWNER_NOTE_IGNORED', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_SIZE_JUMP', 'F_INCONSISTENT'] |
| RM_Vizhik_ns | r1 | creature/walker | WEAK | regen | **REGEN** | 102.7 | opus band WEAK (model said really_bad); blocking ['F_INCONSISTENT', 'OWNER_NOTE_IGNORED', 'DEPARTURE_MISSING']; polish ['F_TOPDOWN', 'LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
