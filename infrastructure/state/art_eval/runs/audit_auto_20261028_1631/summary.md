# art_eval run audit_auto_20261028_1631

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ollathrix_n | r2 | creature/walker | WEAK | strong_accept | **ACCEPT** | 58.0 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Huldu_n | r2 | creature/swimmer | REALLY_BAD | - | **REGEN** | 44.1 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'OWNER_NOTE_IGNORED', 'F_SIZE_JUMP']; polish [] |
| RM_Murrin_ns | r2 | creature/swimmer | WEAK | regen | **REGEN** | 104.8 | opus band WEAK (model said good); blocking ['F_TOPDOWN', 'ALPHA_HALO', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K2', 'K3'], own blocking ['ALPHA_HALO', 'DEPARTURE_MISSING'] |
| RM_Skarrin_n | r2 | creature/swimmer | REALLY_BAD | - | **REGEN** | 54.7 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_TOPDOWN', 'OWNER_NOTE_IGNORED']; polish ['LEGIB_32'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
