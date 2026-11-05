# art_eval run audit_20261105_g1

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Irqit__RM_Irqit_RM_Irqit_n | r3 | creature/walker | WEAK | regen | **ESCALATE** | 87.0 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'DESC_MISS']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'DESC_MISS']; still failing after 3 regen rounds — one line to the owner |
| RM_Siezer_n | r3 | creature/swimmer | WEAK | regen | **ESCALATE** | 81.3 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'F_TOPDOWN']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_INCONSISTENT', 'F_TOPDOWN']; still failing after 3 regen rounds — one line to the owner |
| RM_Sytheclaw__dessicated_n | r3 | creature/walker | WEAK | regen | **ESCALATE** | 82.8 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'OWNER_NOTE_IGNORED', 'F_TOPDOWN', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K3', 'K4'], own blocking ['F_INCONSISTENT', 'F_TOPDOWN', 'F_INCONSISTENT']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Irqit__RM_Irqit_RM_Irqit_n: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Siezer_n: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Sytheclaw__dessicated_n: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
