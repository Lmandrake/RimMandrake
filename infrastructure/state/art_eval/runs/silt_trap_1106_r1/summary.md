# art_eval run silt_trap_1106_r1

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_SiltTrap_Modern |  | machine/structure | WEAK | regen | **REGEN** | 79.2 | opus band WEAK (model said good); blocking ['OWNER_NOTE_IGNORED', 'CAM_WRONG', 'ALPHA_HALO']; polish ['LEGIB_32']; gpt regen: unsettled ['K3'], own blocking ['ALPHA_HALO'] |
| RM_SiltTrap_Industrial |  | machine/structure | GOOD | - | **ACCEPT** | 42.2 | opus band GOOD (model said good); blocking []; polish ['LEGIB_32'] |

Models reported: UNMEASURED, claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+machine@v4#d24b10`
