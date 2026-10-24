# art_eval run gearpack_redraw_20261024b

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Vhorrin | V2 | creature/swimmer | REALLY_BAD | - | **REGEN** | 47.0 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP']; polish ['SCALE_WRONG'] |
| RSW_KowakianMonkeyLizard | V2 | creature/walker | WEAK | regen | **REGEN** | 79.3 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish ['LEGIB_32', 'SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RM_Venomvine | c_V2 | plant/ground_cover | WEAK | regen | **REGEN** | 80.9 | opus band WEAK (model said good); blocking ['DESC_MISS', 'LUMP']; polish ['SCALE_WRONG']; unreadable ['VARIANTS']; gpt regen: unsettled ['K2', 'K3'], own blocking ['DESC_MISS'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
